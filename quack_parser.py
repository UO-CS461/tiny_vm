"""
Quack Parser
================
Variable Assignment, Typed Method calls, adding functionality to REPL calculator
"""
from pydoc import classname
from lark import Lark, Transformer, v_args,exceptions,tree
import sys
import argparse
from quack_grammar import *
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



@v_args(inline=True)    # Affects the signatures of the methods
class MakeAsm(Transformer):

    def __init__(self, class_name='Main'):
        self.vars = {}
        self.codes=[f'.class {class_name}:Obj','.method $constructor']
    def gettype(self,left):
        receivertype="Object"
        if left in self.vars:
            receivertype=self.vars[left]
        if left in ("true","false"):
            receivertype= "Bool"
        if left == "nothing":
            receivertype= "Nothing"
        if left[0] == '"':
            receivertype= "String"
        if str.isdigit(left):
            receivertype = "Int"
        return receivertype
    def returntype(self,methodname,caller):
        X=dict(print='nothing')
        return X.get(methodname,caller)
    def solo_statement(self,soloexpr):
        self.codes.append('pop')

    def assign(self,name,typename,value):
        self.vars[name]=typename
        self.codes.append(f"store {name}")
    def var(self, name):
        assert name in self.vars, f"Variable {name} not assigned"
        self.codes.append(f"load {name}")
        return name
    def add(self,left,right):
        self.codes.extend(["roll 1",f"call {self.gettype(left)}:plus"])
        return left
    def sub(self,left,right):
        self.codes.extend(["roll 1",f"call {self.gettype(left)}:sub"])
        return left
    def mul(self,left,right):
        self.codes.extend(["roll 1",f"call {self.gettype(left)}:mul"])
        return left
    def div(self,left,right):
        self.codes.extend(["roll 1",f"call {self.gettype(left)}:div"])
        return left
    def neg(self,right):
        return right
    def methodargs(self,*args):
        return args
    def methodcall(self,caller,methodname,methodargs):
        self.codes.append(f"call {self.gettype(caller)}:{methodname}")
        return self.returntype(methodname,caller)
    def const_number(self,val):
        self.codes.append("const "+val)
        return val
    def const_true(self):
        self.codes.append("const true")
        return "true"
    def const_false(self):
        self.codes.append("const false")
        return "false"
    def const_nothing(self):
        self.codes.append("const nothing")
        return "nothing"
    def const_string(self,val):
        self.codes.append("const "+val)
        return val
    def end(self,right):
        self.codes= self.codes[:2]+([".local "+','.join(self.vars.keys())] if self.vars  else [])+self.codes[2:]
        self.codes.extend(["const nothing","return 0"])
        return self.codes


calc_test=Lark(calc_grammar, parser='lalr',lexer="basic")
calc = calc_test.parse
def main():
    arguments = vars(args)
    f_input = arguments["input"]
    f_output = arguments["output"]
    f_name = arguments["classname"]
    s = ""
    with open(f_input, 'r', encoding='utf-8') as f:
        s=f.read()
    calc_parser1 = Lark(calc_grammar, parser='lalr',transformer=MakeAsm(class_name=f_name),lexer="basic")
    calc1 = calc_parser1.parse

    

    with open(f_output, 'w', encoding='utf-8') as f:
        #print tree for debug
        #print(calc(s).pretty(),flush=True)
        try:
            f.write('\n\t'+'\n\t'.join(calc1(s)))
            tree.pydot__tree_to_png( calc(s), './parser.png')

        except exceptions.UnexpectedToken as ex:
            print(calc(s).choices(),flush=True)
            tree.pydot__tree_to_png( calc1(s), './parser.png')


            
    

def test():
    print(calc("a = 1+2"))
    print(calc("1+a*-3"))


if __name__ == '__main__':
    # test()
    main()
