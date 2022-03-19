"""
Quack Parser
================
Variable Assignment, Typed Method calls, adding functionality to REPL calculator
"""
from calendar import c
from lark import Lark, Transformer, UnexpectedCharacters, Visitor, v_args,exceptions,Tree,tree,Token
from lark.visitors import Interpreter,Transformer_InPlaceRecursive
from itertools import count
import argparse
from quack_grammar import calc_grammar,methodlist,commontype,commontypelist,clsname_hierarchy as hierarchy
import quackpydot as qpd
import logging
from functools import partialmethod
from itertools import chain
logging.basicConfig(filename = "log.txt", level = logging.INFO)

log = logging.getLogger('quack_parser')
log.setLevel(logging.DEBUG)
parser = argparse.ArgumentParser(description=
                                 'Compile quack into assembly')

parser.add_argument('-i', '--input', default=None,
                    help="Specify input file name")
parser.add_argument('-cn', '--classname', default=None,
                    help="Specify program class name")


args = parser.parse_args()

try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass

def getclass(self):
    if hasattr(self,'classname'):
        return self.classname
    assert hasattr(self,'parent')
    self.classname = self.parent.getclass()
    return self.classname
def getmethod(self):
    if hasattr(self,'methodname'):
        return self.methodname
    assert hasattr(self,'parent')
    self.methodname = self.parent.getmethod()
    return self.methodname
def getifcons(self):
    if hasattr(self,'ifcons'):
        return self.ifcons
    if hasattr(self,'parent'):
        self.ifcons = self.parent.getifcons()
        return self.ifcons
    return False
def getwhilecons(self):
    if hasattr(self,'whilecons'):
        return self.whilecons
    if hasattr(self,'parent'):
        self.whilecons = self.parent.getwhilecons()
        return self.whilecons
    return False

def in_constructor(self):
    if hasattr(self,'_in_constructor'):
        return self._in_constructor
    if hasattr(self,'parent'):
        self._in_constructor = self.parent.in_constructor()
        return self._in_constructor
    return False

Tree.getclass= getclass
Tree.getmethod= getmethod
Tree.getifcons= getifcons
Tree.getwhilecons= getwhilecons
Tree.in_constructor= in_constructor
class Quack_Interpreter(Interpreter):

    def __init__(self,class_name='Main') -> None:
        super().__init__()
        self.vars={} 
        self.allvars={}
        self.classargs={i:{} for i in methodlist}
        self.methodargs={}
        self.classparent = {}
        self.fields={i:{} for i in methodlist}
        labelcounts={i:count() for i in ['if','elif','else','while','endif','endwhile','and_false','and_end','or_true','or_end']}
        self.label= lambda i:f'{i}{next(labelcounts[i])}' 
        self.code = {}
        self.class_name=class_name
        self.fields_assigned=set()
        # python hacks! 
        Tree.CODE = property(lambda t: self.code[t.getclass()],
                    lambda t,val: (self.code[t.getclass()].clear(),self.code[t.getclass()].extend(val)))
        Tree.visit = partialmethod(self.visit)
        Tree.visit_children = partialmethod(self.visit_children)


    def class_signature(self,t):
        classname,formalargs,superclass = t.children
        if superclass is None:
            methodlist[classname]=methodlist['Obj'].copy() 
            hierarchy[classname]='Obj'
            superclass = 'Obj'
        else:
            methodlist[classname]=methodlist[superclass].copy()
            hierarchy[classname]=superclass
        self.classargs[classname]={}
        self.methodargs[classname]={}
        self.code[classname]=[]
        for formalarg in formalargs.children:
            varname,vartype = formalarg.children
            self.classargs[classname][varname]=vartype
        self.classparent[classname] = superclass
        t.parent.classname = t.classname = classname
    
    def formalargs(self,t):
        for arg in t.children:
            _,vartype= arg.children
            assert vartype in methodlist, f"{vartype} not defined"
    
    def constructor(self,t):
        t._in_constructor = True
        t.methodname=Token('NAME',"$constructor")
        classname=t.getclass()
        self.fields[classname]=self.fields.get(self.classparent[classname],{}).copy()
        while True:
            before_code = t.CODE[:]
            before_allvars= self.allvars.copy()
            t.CODE = []
            t.visit_children()
            
            t.CODE= [f'.class {classname}:{self.classparent[classname]}']+\
                    [f'.field {fieldname}' for fieldname in self.fields[classname] if fieldname not in self.fields.get(self.classparent[classname],{})]+\
                    [f'.method $constructor'] +\
                    ([".args "+','.join(self.classargs[classname].keys())] if self.classargs[classname]  else []) +\
                    ([".local "+','.join(self.allvars.keys())] if self.allvars  else []) +\
                    ['enter'] +\
                    t.CODE +\
                    ['load $',f'return {len(self.classargs[classname])}']
            after_allvars=self.allvars.copy()
            if before_allvars == after_allvars:
                break
            t.CODE= before_code
        self.vars.clear()
        self.allvars.clear()   

    def assign_infertype(self,t):
        name,rhs= t.children
        rhs.visit()
        if name in self.vars:
            if rhs.type != self.vars[name]:
                self.vars[name]=commontype(self.vars[name],rhs.type)
        else:
            self.vars[name]= rhs.type
        t.CODE.append(f'store {name}')
        self.allvars.update(self.vars)

    def assign_field(self,t):
        objname,fieldname,rhs= t.children
        rhs.visit()
        objname.visit()
        assert fieldname in self.fields[objname.type], f"{objname.type} has no field {fieldname}"
        assert rhs.type == self.fields[objname.type][fieldname], f"{objname.type}:{fieldname} is not of type {rhs.type} "
        resolved_type = objname.type if objname.type != t.getclass() else '$'
        t.CODE.append(f'store_field {resolved_type}:{fieldname}')

    def assign_this_field(self,t):
        fieldname,typename,rhs= t.children
        rhs.visit()
        if t.in_constructor():
            if fieldname in self.fields[t.getclass()] and fieldname in self.fields[self.classparent[t.getclass()]]:
                if typename is None:
                    assert self.fields[t.getclass()][fieldname] == commontype(self.fields[t.classname][fieldname],rhs.type)
                else:
                    assert self.fields[t.getclass()][fieldname] == typename and typename == commontype(typename,rhs.type) 
            elif fieldname in self.fields[t.getclass()]:
                if typename is None:
                    self.fields[t.getclass()][fieldname] = commontype(self.fields[t.classname][fieldname],rhs.type)
                else:
                    self.fields[t.getclass()][fieldname] = typename = typename = commontype(typename,rhs.type) 
            elif typename is None and not t.getwhilecons():
                self.fields[t.getclass()][fieldname] = rhs.type 
            elif not t.getwhilecons():
                self.fields[t.getclass()][fieldname] = commontype(typename,rhs.type)
            else:
                raise AssertionError('Cannot initialize new field within while loop')
            if t.getifcons():
                self.fields_assigned.add(fieldname)   
             
        else:
            assert fieldname in self.fields[t.getclass()], f"field {fieldname} not present in class {t.getclass()}"
            assert commontype(rhs.type,self.fields[t.getclass()][fieldname]) == self.fields[t.getclass()][fieldname],\
                                            f"field {fieldname} does not accept objects of type {rhs.type}"
            
        t.CODE.extend(['load $',f'store_field $:{fieldname}'])
        

    def assign(self,t):
        name,typename,rhs= t.children
        if name in self.vars:
            if typename != self.vars[name]:
                typename = commontype(self.vars[name],typename)
        self.vars[name]=typename
        rhs.visit()
        if rhs.type != typename:
            self.vars[name] = commontype(typename,rhs.type)
        t.CODE.append(f'store {name}')
        self.allvars.update(self.vars)
    
    def solo_statement(self,t):
        t.visit_children()
        t.CODE.append('pop')
    def if_handler(self,t):
        t.ifcons=False
        old_fields_assigned=self.fields_assigned.copy()
        old_fields=set(self.fields[t.getclass()].items())
        if t.in_constructor():
            t.ifcons=True
            self.fields_assigned = set()
        ifc,*elifcs,elsec = t.children
        f_if,f_elifs,f_else=set(),[],set()
        t.else_present = elsec is not None
        ifcond,ifbody = ifc.children
        ifcond.visit()
        iflabel = self.label('if')
        endlabel= self.label('endif')
        t.CODE.append(f'jump_if {iflabel}')
        eliflabels = []
        for elifc in elifcs:
            elifcond,elifbody = elifc.children
            elifcond.visit()
            eliflabels.append(self.label('elif'))
            t.CODE.append(f'jump_if {eliflabels[-1]}')
        if t.else_present:
            elsebody,*_ = elsec.children
            elsebody.visit()
            f_else.update(self.fields_assigned)
            self.fields_assigned=set()
        t.CODE.append(f'jump {endlabel}')
        t.CODE.append(f'{iflabel}:')
        ifbody.visit()
        f_if.update(self.fields_assigned)
        self.fields_assigned=set()
        t.CODE.append(f'jump {endlabel}')
        for elifc,eliflabel in zip(elifcs,eliflabels):
            elifcond,elifbody = elifc.children
            t.CODE.append(f'{eliflabel}:')
            elifbody.visit()
            f_elifs.append(self.fields_assigned.copy())
            self.fields_assigned=set()
            t.CODE.append(f'jump {endlabel}')
        t.CODE.append(f'{endlabel}:')
        if t.ifcons:
            allsets=[f_if,*f_elifs,f_else]
            allsets=[fset.difference(old_fields) for fset in allsets]
            assert allsets[1:]==allsets[:-1], f'{allsets} must be equal'
        self.fields_assigned=old_fields_assigned
    def while_handler(self,t):
        if t.in_constructor():
            t.whilecons = True 
        whilecond, whilebody = t.children
        looplabel= self.label('while')
        endlabel= self.label('endwhile')
        t.CODE.append(f'{looplabel}:')
        whilecond.visit()
        t.CODE.append(f'jump_ifnot {endlabel}')
        whilebody.visit()
        t.CODE.append(f'jump {looplabel}')
        t.CODE.append(f'{endlabel}:')
        t.whilecons= False

    def statement_block(self,t):
        old_vars = self.vars.copy()
        t.visit_children()
        self.vars = {i:self.vars[i] for i in old_vars}
                       
    def var(self,t):
        name,*_ = t.children
        assert name in self.allvars or (t.in_constructor() and name in self.classargs[t.getclass()]) or name in self.methodargs[t.getclass()][t.getmethod()] , f'Variable {name} not assigned'
        assert name in self.vars or (t.in_constructor() and name in self.classargs[t.getclass()]) or  name in self.methodargs[t.getclass()][t.getmethod()], f'Variable {name} not assigned in current scope'
        if name in self.vars:
            t.type = self.vars[name]
        elif t.in_constructor() and name in self.classargs[t.getclass()]:
            t.type = self.classargs[t.getclass()][name]
        elif name in self.methodargs[t.getclass()][t.getmethod()]:
            t.type = self.methodargs[t.getclass()][t.getmethod()][name]
        t.CODE.append(f'load {name}')
    
    def load_this_field(self,t):
        fieldname,*_= t.children
        assert fieldname in self.fields[t.getclass()], f"No field {fieldname} in class {t.getclass()}"
        t.CODE.extend(['load $',f'load_field $:{fieldname}'])
        t.type = self.fields[t.getclass()][fieldname]

    def load_field(self,t):
        objname,fieldname= t.children
        objname.visit()
        assert fieldname in self.fields[objname.type], f"{fieldname} not in {objname.type}:{self.fields[objname.type]}"
        resolved_type = objname.type if objname.type != t.getclass() else '$'

        t.CODE.append(f'load_field {resolved_type}:{fieldname}')
        t.type = self.fields[objname.type][fieldname]
    
    def method_def(self,t):
        name,args,rtype,body = t.children
        t.methodname = name
        args.visit()
        classname =t.getclass()
        self.methodargs[classname][name]=dict(arg.children for arg in args.children)
        assert rtype in methodlist
        if name in methodlist[classname]:
            assert commontype(methodlist[classname][name][1],rtype)==methodlist[classname][name][1]
        methodlist[classname][name]=[[*self.methodargs[classname][name].values()],rtype]
        while True:
            before_code = t.CODE[:]
            before_locals = self.allvars.copy()
            t.CODE = []
            body.visit()

            t.CODE= before_code +\
                    [f'.method {name}'] +\
                    ([".args "+','.join(self.methodargs[classname][name].keys())] if self.methodargs[classname][name] else []) +\
                    ([".local "+','.join(self.allvars.keys())] if self.allvars  else []) +\
                    ['enter'] +\
                    t.CODE
            
            assert self.check_return(body,rtype), f"{name} does not have return type {rtype}"
            if f'{rtype}' == 'Nothing':
                t.CODE.extend(['const nothing',f"return {len(methodlist[classname][name][0])}"])
            
            after_locals= self.allvars.copy()
            if before_locals == after_locals:
                break
            t.CODE = before_code
        self.vars.clear()
        self.allvars.clear()
        
    def check_return(self,t,rtype):
        *statements,return_stmt= t.children
        returnlist=[True]
        if return_stmt is None:
            if  f'{rtype}' != 'Nothing':
                last_stmt=statements[-1]
                if last_stmt.data == 'if_handler' and last_stmt.else_present:
                    for _,block in last_stmt.children:
                        returnlist.append(self.check_return(block,rtype))
                else:
                    return False
            else:
                return True        
        return all(returnlist)

    def constructorcall(self,t):
        classname,args = t.children
        args.type=[]
        assert classname in self.classargs
        for arg in args.children:
            arg.visit()
            args.type += ([arg.type] if arg.type is not None else [])
        assert list(self.classargs[classname].values()) == args.type
        resolved_type = classname if classname != t.getclass() else '$'

        t.CODE.extend([f'new {resolved_type}',f'call {resolved_type}:$constructor'])
        t.type = classname


    def methodcall(self,t):
        caller,name,args = t.children
        name = name.value
        args.type=[]
        for arg in args.children:
            arg.visit()
            args.type += ([arg.type] if arg.type is not None else [])
        args.type = args.type
        caller.visit()
        assert name in methodlist[caller.type] , f'no method {name} for class {caller.type}'
        assert commontypelist(methodlist[caller.type][name][0],args.type) == methodlist[caller.type][name][0], f'method {caller.type}:{name} does not have argtypes {args.type},  {methodlist[caller.type][name]}'
        resolved_type = caller.type if caller.type != t.getclass() else '$'

        t.CODE.append(f'call {resolved_type}:{name}')
        t.type=methodlist[caller.type][name][1]
        
    def return_handler(self,t):
        rhs,*_ = t.children
        classname,methodname= t.getclass(),t.getmethod()
        rhs.visit()
        assert rhs.type == commontype(rhs.type,methodlist[classname][methodname][1]), f'{rhs.type!r} is not the same as {commontype(rhs.type,methodlist[classname][methodname][1])!r}'
        t.CODE.append(f"return {len(methodlist[classname][methodname][0])}")
    def _and(self,t):
        left,right = t.children
        andlabel = self.label('and_false')
        endlabel = self.label('and_end')
        left.visit()
        t.CODE.append(f'jump_ifnot {andlabel}')
        right.visit()
        t.CODE.extend([f'jump_ifnot {andlabel}',
                            'const true',
                            f'jump {endlabel}',
                            f'{andlabel}: const false',
                            f'{endlabel}:'])
        t.type = 'Bool'

    def _or(self,t):
        left,right = t.children
        orlabel = self.label('or_true')
        endlabel = self.label('or_end')
        left.visit()
        t.CODE.append(f'jump_if {orlabel}')
        right.visit()
        t.CODE.extend([f'jump_if {orlabel}',
                            'const false',
                            f'jump {endlabel}',
                            f'{orlabel}: const true',
                            f'{endlabel}:'])
        t.type = 'Bool'
    
    def end(self,t):
        t.classname= self.class_name
        t.methodname= Token('NAME',"$constructor")
        t._in_constructor = True
        self.classparent[t.classname]='Obj'
        self.code[t.classname]=[]
        self.classargs[t.classname]={}
        self.fields[t.classname]={}
        self.methodargs[t.classname]={}
        while True:
            before_locals = self.allvars.copy()
            t.CODE=[]
            t.visit_children()
            t.CODE = ([f'.class {t.classname}:{self.classparent[t.classname]}','.method $constructor']+
            ([".local "+','.join(self.allvars.keys())] if self.allvars  else [])) + t.CODE + ["const nothing","return 0"]
            after_locals= self.allvars.copy()
            # log.debug(after_locals)
            # log.debug(t.CODE)
            # log.debug(methodlist)
            # log.debug(hierarchy)
            if before_locals == after_locals:
                break
        self.allvars.clear()
        self.vars.clear()
    def const_number(self,t):
        t.type= 'Int'
        val, *_ = t.children
        t.CODE.append(f'const {val}')
    def const_true(self,t):
        t.type= 'Bool'
        t.CODE.append(f'const true')
    def const_false(self,t):
        t.type= 'Bool'
        t.CODE.append(f'const false')
    def const_string(self,t):
        t.type= 'String'
        val, *_ = t.children
        t.CODE.append(f'const {val}')
    def const_nothing(self,t):
        t.type= 'Nothing'
        t.CODE.append(f'const nothing')

def methodcall_tree(caller,methodname,*args):
    return Tree('methodcall',
                [   caller,
                    Token('NAME',methodname),
                    Tree('methodargs',args)
                ])



class AttachParent(Visitor):
    def __default__(self, tree):
        for subtree in tree.children:
            if isinstance(subtree, Tree):
                subtree.parent = tree
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
        return Tree(data,children,meta)

calc_test=Lark(calc_grammar, parser='lalr',lexer="basic",debug=True)
calc = calc_test.parse
calcin= calc_test.parse_interactive
def main():
    arguments = vars(args)
    f_input = arguments["input"]
    f_name = arguments["classname"]
    s = ""
    with open(f_input, 'r', encoding='utf-8') as f:
        s=f.read()
    
    parsetree = calc(s)
    # tree.pydot__tree_to_png(parsetree, './Tree1.png')
    DesugarTransformer().transform(parsetree)
    # tree.pydot__tree_to_png( parsetree, './sugar.png')
    AttachParent().visit(parsetree)
    res=Quack_Interpreter(f_name)
    res.visit(parsetree)
    classcodes=res.code.values()
    outputfiles=["0_"+classname+".asm" for classname in res.code]
    qpd.draw_png(parsetree,'./typedtree.png')   
    for fname,fcode in zip(outputfiles,classcodes):
        with open(fname, 'w', encoding='utf-8') as f:
            f.write('\n\t'+'\n\t'.join(fcode))

    print(*res.code)
if __name__ == '__main__':
    main()
