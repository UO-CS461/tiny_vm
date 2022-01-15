"""
Basic calculator
================

A simple example of a REPL calculator

This example shows how to write a basic calculator with variables.
"""
from lark import Lark, Transformer, v_args


try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass


calc_grammar = """
    ?start: sum             -> end

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "(" sum ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""


@v_args(inline=True)    # Affects the signatures of the methods
class MakeAsm(Transformer):

    def __init__(self):
        self.vars = {}
        self.codes=['.class Sample:Obj','.method $constructor']

    def add(self,left,right):
        self.codes.append("call Int:plus")
    def sub(self,left,right):
        self.codes.append("call Int:sub")
    def mul(self,left,right):
        self.codes.append("call Int:mul")
    def div(self,left,right):
        self.codes.append("call Int:div")
    def neg(self,right):
        self.codes.append("call Int:neg")
    def number(self,const):
        self.codes.append("const "+const)
    def end(self,right):
        self.codes.extend(["call Int:print","pop","return 0"])
        return self.codes


calc_parser = Lark(calc_grammar, parser='lalr')
calc = calc_parser.parse
calc_parser1 = Lark(calc_grammar, parser='lalr',transformer=MakeAsm())
calc1 = calc_parser1.parse


def main():
    with open ('test.asm', 'w') as f:
        s = input('> ')

        f.write('\n\t'+'\n\t'.join(calc1(s)))

    

def test():
    print(calc("a = 1+2"))
    print(calc("1+a*-3"))


if __name__ == '__main__':
    # test()
    main()
