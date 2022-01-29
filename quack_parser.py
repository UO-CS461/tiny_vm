"""
Quack Parser
================
Variable Assignment, Typed Method calls, adding functionality to REPL calculator
"""
from lark import Lark, Transformer, v_args
import sys
import argparse

parser = argparse.ArgumentParser(description=
                                 'Compile quack into assembly')

parser.add_argument('-i', '--input', default=None,
                    help="Specify input file name")
parser.add_argument('-o', '--output', default=None,
                    help="Specify output file name")
args = parser.parse_args()



try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass


calc_grammar = """
    ?start: program -> end

    ?program: statement*

    statement: rexpr ";"
      | assignment ";"

    assignment: lexpr ":" type "=" rexpr -> assign

    ?type: NAME

    ?lexpr: NAME

    ?rexpr: sum
      | methodcall
    
    methodcall: rexpr "." methodname "(" methodargs ")" -> methodcall
    
    ?methodname : NAME
    ?methodargs: (rexpr ("," rexpr)* )? -> methodargs

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> const_number
         | "-" atom         -> neg
         | lexpr            -> var
         | "(" sum ")"
         | "true" -> const_true
         | "false" -> const_false
         | "nothing" -> const_nothing
         | string -> const_string

    ?string: ESCAPED_STRING

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.ESCAPED_STRING
    %import common.WS_INLINE
    %import common.WS

    %ignore WS_INLINE
    %ignore WS
"""


@v_args(inline=True)    # Affects the signatures of the methods
class MakeAsm(Transformer):

    def __init__(self):
        self.vars = {}
        self.codes=['.class Main:Obj','.method $constructor']
        self.stackheight=0
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

    def assign(self,name,typename,value):
        self.vars[name]=typename
        self.codes.append(f"store {name}")
        self.stackheight-=1
    def var(self, name):
        assert name in self.vars, f"Variable {name} not assigned"
        self.stackheight+=1

        self.codes.append(f"load {name}")
        return name
    def add(self,left,right):
        self.stackheight-=1

        self.codes.extend(["roll 1",f"call {self.gettype(left)}:plus"])
        return left
    def sub(self,left,right):
        self.stackheight-=1
        self.codes.extend(["roll 1",f"call {self.gettype(left)}:sub"])
        return left
    def mul(self,left,right):
        self.stackheight-=1
        self.codes.extend(["roll 1",f"call {self.gettype(left)}:mul"])
        return left
    def div(self,left,right):
        self.stackheight-=1
        self.codes.extend(["roll 1",f"call {self.gettype(left)}:div"])
        return left
    def neg(self,right):
        self.codes.append(f"call {self.gettype(right)}:neg")
        return right
    def methodargs(self,*args):
        return args
    def methodcall(self,caller,methodname,methodargs):
        if methodname== 'print':
            self.stackheight-=1
        self.codes.append(f"call {self.gettype(caller)}:{methodname} {''.join(methodargs)}")
    def const_number(self,val):
        self.stackheight+=1
        self.codes.append("const "+val)
        return val
    def const_true(self):
        self.stackheight+=1
        self.codes.append("const true")
        return "true"
    def const_false(self):
        self.stackheight+=1
        self.codes.append("const false")
        return "false"
    def const_nothing(self):
        self.stackheight+=1
        self.codes.append("const nothing")
        return "nothing"
    def const_string(self,val):
        self.stackheight+=1
        self.codes.append("const "+val)
        return val
    def end(self,right):
        assert self.stackheight >=0, "negative stack height!!"
        self.codes= self.codes[:2]+[".local "+','.join(self.vars.keys())]+self.codes[2:]
        self.codes+=["pop"]*self.stackheight
        self.codes.extend(["const nothing","return 0"])
        return self.codes


calc_parser1 = Lark(calc_grammar, parser='lalr',transformer=MakeAsm())
calc1 = calc_parser1.parse
calc_test=Lark(calc_grammar, parser='lalr')
calc = calc_test.parse

def main():
    arguments = vars(args)
    f_input = arguments["input"]
    f_output = arguments["output"]
    s = ""
    with open(f_input, 'r', encoding='utf-8') as f:
        s=f.read()
    

    with open(f_output, 'w', encoding='utf-8') as f:
        #print tree for debug
        #print(calc(s).pretty(),flush=True)
        f.write('\n\t'+'\n\t'.join(calc1(s)))

    

def test():
    print(calc("a = 1+2"))
    print(calc("1+a*-3"))


if __name__ == '__main__':
    # test()
    main()
