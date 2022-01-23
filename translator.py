#!/usr/bin/python3

import lark
import argparse
import sys

#this grammar is taken from the example in Lark's documentation,
#with some removals to fit the spec of the current compiler
calc_grammar = """
    ?start: sum

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "(" sum ")"

    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""

quack_grammar = """
    ?start: program

    ?program: statement
            | program statement

    ?statement: r_exp ";"
              | assignment ";"

    ?assignment: l_exp ":" type "=" r_exp

    ?type: NAME

    ?l_exp: NAME

    ?r_exp: sum

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | l_exp            -> var
         | "(" sum ")"

    %import common.NUMBER
    %import common.CNAME -> NAME
    %import common.WS_INLINE
    %import common.WS

    %ignore WS_INLINE
    %ignore WS
"""

def quack_main():
    parser = argparse.ArgumentParser(prog='translate')
    parser.add_argument('source', type=argparse.FileType('r'))
    parser.add_argument('target', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()
    quack_parser = lark.Lark(quack_grammar, parser='lalr')
    code = args.source.read()
    tree = quack_parser.parse(code)
    print(tree.pretty())

#operates on the tree as it is created
@lark.v_args(inline=True)
class CalculateTree(lark.Transformer):
    def __init__(self, target):
        #store the target file/stdout where commands are printed
        self.target = target
    def number(self, token):
        #if a number is found, output a "push constant" command
        print('\tconst %s' % token, file=self.target)
    def add(self, a, b):
        #output a call to the builtin addition function
        print('\tcall Int:plus', file=self.target)
    def sub(self, a, b):
        #output a call to the builtin subtraction function
        print('\tcall Int:sub', file=self.target)
    def mul(self, a, b):
        #output a call to the builtin multiplication function
        print('\tcall Int:mult', file=self.target)
    def div(self, a, b):
        #output a call to the builtin division function
        print('\tcall Int:div', file=self.target)
    def neg(self, a): #
        #output a call to the builtin negation function
        print('\tcall Int:neg', file=self.target)

#read an input and output file from the command line arguments
def cli_parser():
    parser = argparse.ArgumentParser(prog='translate')
    parser.add_argument('source', type=argparse.FileType('r'))
    parser.add_argument('target', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout)
    return parser.parse_args()

#same for all programs - Sample is hardcoded in the tiny_vm
assembly_header = """\
.class Sample:Obj

.method $constructor\
"""

def main():
    args = cli_parser()
    parser = lark.Lark(calc_grammar, parser='lalr',
                       transformer=CalculateTree(args.target))
    def gen(s): #convenience method for printing to target file
        print(s, file=args.target)
    gen(assembly_header) #output header of assembly file
    #iterate through arithmetic expressions
    for line in args.source:
        line = line.strip() #remove extraneous whitespace
        if not line: #ignore blank lines
            continue
        #output command to print raw expression
        gen('\tconst "%s = "' % line)
        gen('\tcall String:print')
        gen('\tpop')
        try:
            #attempt to parse expression
            tree = parser.parse(line)
        except lark.exceptions.LarkError:
            #output to stderr on failed parse
            print('Invalid line: "%s"' % line, file=sys.stderr)
        else:
            #if no exception was found, output command to print result
            gen('\tcall Int:print')
            gen('\tpop')
            #print newline after each expression
            gen('\tconst "\\n"')
            gen('\tcall String:print')
            gen('\tpop')
    #end of method
    gen('\treturn 0')

if __name__ == '__main__' and not sys.flags.interactive:
    #main()
    quack_main()
