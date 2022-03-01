"""
Quack Parser
================
Variable Assignment, Typed Method calls, adding functionality to REPL calculator
"""
from calendar import c
from lark import Lark, Transformer, v_args,exceptions,Tree,tree,Token
from lark.visitors import Interpreter,Transformer_InPlaceRecursive
from itertools import count
import argparse
from quack_grammar import calc_grammar,methodlist,commontype
import quackpydot as qpd
import logging
logging.basicConfig(filename = "log.txt", level = logging.INFO)

log = logging.getLogger('quack_parser')
log.setLevel(logging.DEBUG)
parser = argparse.ArgumentParser(description=
                                 'Compile quack into assembly')

parser.add_argument('-i', '--input', default=None,
                    help="Specify input file name")
parser.add_argument('-o', '--output', default=None,
                    help="Specify output file name")
parser.add_argument('-cn', '--classname', default=None,
                    help="Specify program class name")


args = parser.parse_args()

try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass

class TTree(Tree):
    def __init__(self, data, children, meta= None) -> None:
        super().__init__(data, children, meta)
        self.type=None
    def __repr__(self):
        return 'TTree[%r](%r, %r)' % (self.type,self.data, self.children)


class Quack_Interpreter(Interpreter):

    def __init__(self,class_name='Main') -> None:
        super().__init__()
        self.vars={} 
        self.allvars={}
        labelcounts={i:count() for i in ['if','elif','else','while','endif','endwhile','and_false','and_end','or_true','or_end']}
        self.label= lambda i:f'{i}{next(labelcounts[i])}' 
        self.code =[]
        self.class_name=class_name

    def assign_infertype(self,t):
        name,rhs= t.children
        self.visit(rhs)
        if name in self.vars:
            if rhs.type != self.vars[name]:
                self.vars[name]=commontype(self.vars[name],rhs.type)
        else:
            self.vars[name]= rhs.type
        self.code.append(f'store {name}')
        self.allvars.update(self.vars)


    def assign(self,t):
        name,typename,rhs= t.children
        if name in self.vars:
            assert typename == self.vars[name],f"Conflicting type declarations '{typename}' and '{self.vars[name]}' for variable '{name}'"
        self.vars[name]=typename
        self.visit(rhs)
        assert rhs.type == typename, f"Conflicting type declarations '{typename}' and '{rhs.type}' for variable '{name}'"
        self.code.append(f'store {name}')
        self.allvars.update(self.vars)
    
    def solo_statement(self,t):
        self.visit_children(t)
        self.code.append('pop')
    def if_handler(self,t):
        ifc,*elifcs,elsec = t.children
        else_present = elsec is not None
        ifcond,ifbody = ifc.children
        self.visit(ifcond)
        iflabel = self.label('if')
        endlabel= self.label('endif')
        self.code.append(f'jump_if {iflabel}')
        eliflabels = []
        for elifc in elifcs:
            elifcond,elifbody = elifc.children
            self.visit(elifcond)
            eliflabels.append(self.label('elif'))
            self.code.append(f'jump_if {eliflabels[-1]}')
        if else_present:
            elsebody,*_ = elsec.children
            self.visit(elsebody)
        self.code.append(f'jump {endlabel}')
        self.code.append(f'{iflabel}:')
        self.visit(ifbody)
        self.code.append(f'jump {endlabel}')
        for elifc,eliflabel in zip(elifcs,eliflabels):
            elifcond,elifbody = elifc.children
            self.code.append(f'{eliflabel}:')
            self.visit(elifbody)
            self.code.append(f'jump {endlabel}')
        self.code.append(f'{endlabel}:')
       

    def while_handler(self,t):
        whilecond, whilebody = t.children
        looplabel= self.label('while')
        endlabel= self.label('endwhile')
        self.code.append(f'{looplabel}:')
        self.visit(whilecond)
        self.code.append(f'jump_ifnot {endlabel}')
        self.visit(whilebody)
        self.code.append(f'jump {looplabel}')
        self.code.append(f'{endlabel}:')

    def statement_block(self,t):
        old_vars = self.vars.copy()
        self.visit_children(t)
        self.vars = {i:self.vars[i] for i in old_vars}
                       
    def var(self,t):
        name,*_ = t.children
        assert name in self.allvars, f'Variable {name} not assigned'
        assert name in self.vars, f'Variable {name} not assigned in current scope'
        t.type = self.vars[name]
        self.code.append(f'load {name}')

    def methodcall(self,t):
        caller,name,args = t.children
        name = name.value
        args.type=[]
        for arg in args.children[::-1]:
            self.visit(arg)
            args.type += ([arg.type] if arg.type is not None else [])
        args.type = args.type[::-1]
        self.visit(caller)
        assert name in methodlist[caller.type] , f'no method {name} for class {caller.type}'
        assert methodlist[caller.type][name][0] == args.type, f'method {caller.type}:{name} does not have argtypes {args.type}'
        self.code.append(f'call {caller.type}:{name}')
        t.type=methodlist[caller.type][name][1]
        
    def _and(self,t):
        left,right = t.children
        andlabel = self.label('and_false')
        endlabel = self.label('and_end')
        self.visit(left)
        self.code.append(f'jump_ifnot {andlabel}')
        self.visit(right)
        self.code.extend([f'jump_ifnot {andlabel}',
                            'const true',
                            f'jump {endlabel}',
                            f'{andlabel}: const false',
                            f'{endlabel}:'])
        t.type = 'Bool'

    def _or(self,t):
        left,right = t.children
        orlabel = self.label('or_true')
        endlabel = self.label('or_end')
        self.visit(left)
        self.code.append(f'jump_if {orlabel}')
        self.visit(right)
        self.code.extend([f'jump_if {orlabel}',
                            'const false',
                            f'jump {endlabel}',
                            f'{orlabel}: const true',
                            f'{endlabel}:'])
        t.type = 'Bool'
    
    def end(self,t):
        self.visit_children(t)
        self.code = ([f'.class {self.class_name}:Obj','.method $constructor']+
        ([".local "+','.join(self.allvars.keys())] if self.allvars  else [])) + self.code + ["const nothing","return 0"]

    def const_number(self,t):
        t.type= 'Int'
        val, *_ = t.children
        self.code.append(f'const {val}')
    def const_true(self,t):
        t.type= 'Bool'
        self.code.append(f'const true')
    def const_false(self,t):
        t.type= 'Bool'
        self.code.append(f'const false')
    def const_string(self,t):
        t.type= 'String'
        val, *_ = t.children
        self.code.append(f'const {val}')
    def const_nothing(self,t):
        t.type= 'Nothing'
        self.code.append(f'const nothing')

def methodcall_tree(caller,methodname,*args):
    return TTree('methodcall',
                [   caller,
                    Token('NAME',methodname),
                    TTree('methodargs',args)
                ])
class DesugarTransformer(Transformer_InPlaceRecursive):
    def add(self,t):
        left,right= t
        return methodcall_tree(left,'plus',right)
    def sub(self,t):
        left,right= t
        return methodcall_tree(left,'sub',right)
    def mul(self,t):
        left,right= t
        return methodcall_tree(left,'mul',right)
    def div(self,t):
        left,right= t
        return methodcall_tree(left,'div',right)
    def neg(self,t):
        right,*_ = t
        return methodcall_tree(right,'neg')
    def less(self,t):
        left,right= t
        return methodcall_tree(left,'less',right)
    def more(self,t):
        left,right= t
        return methodcall_tree(left,'more',right)
    def atleast(self,t):
        left,right= t
        return methodcall_tree(left,'atleast',right)
    def atmost(self,t):
        left,right= t
        return methodcall_tree(left,'atmost',right)
    def equals(self,t):
        left,right= t
        return methodcall_tree(left,'equals',right)
    def _not(self,t):
        right,*_= t
        return methodcall_tree(right,'not')

    def __default__(self,data,children,meta):
        return TTree(data,children,meta)

calc_test=Lark(calc_grammar, parser='lalr',lexer="basic",tree_class= TTree)
calc = calc_test.parse
def main():
    arguments = vars(args)
    f_input = arguments["input"]
    f_output = arguments["output"]
    f_name = arguments["classname"]
    s = ""
    with open(f_input, 'r', encoding='utf-8') as f:
        s=f.read()
    parsetree = calc(s)
    # tree.pydot__tree_to_png(parsetree, './TTree1.png')
    DesugarTransformer().transform(parsetree)
    # tree.pydot__tree_to_png( parsetree, './sugar.png')

    res=Quack_Interpreter()
    res.visit(parsetree)
    # qpd.draw_png(parsetree,'./typedtree.png')   
    with open(f_output, 'w', encoding='utf-8') as f:
        f.write('\n\t'+'\n\t'.join(res.code))

if __name__ == '__main__':
    main()
