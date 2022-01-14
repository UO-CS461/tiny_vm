#!/usr/bin/python3

import lark
import argparse
import sys

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

@lark.v_args(inline=True)
class CalculateTree(lark.Transformer):
    def number(self, token):
        print('\tconst %s' % token)
    def add(self, a, b):
        print('\tcall Int:plus')
    def sub(self, a, b):
        print('\tcall Int:sub')
    def mul(self, a, b):
        print('\tcall Int:mult')
    def div(self, a, b):
        print('\tcall Int:div')
    def neg(self, a):
        print('\tcall Int:neg')

calc_parser = lark.Lark(calc_grammar, parser='lalr', transformer=CalculateTree())
calc = calc_parser.parse

def cli_parser():
    parser = argparse.ArgumentParser(prog='translate')
    parser.add_argument('source', type=argparse.FileType('r'))
    parser.add_argument('target', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout)
    return parser.parse_args()

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()

def main():
    args = cli_parser()
    output = []
    for line in args.source:
        line = line.strip()
        if not line:
            continue
        try:
            tree = calc(line)
        except lark.exceptions.LarkError:
            print('Invalid line: "%s"' % line)
        else:
            pass

if __name__ == '__main__' and not sys.flags.interactive:
    main()
