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
    def __init__(self, target):
        self.target = target
    def number(self, token):
        print('\tconst %s' % token, file=self.target)
    def add(self, a, b):
        print('\tcall Int:plus', file=self.target)
    def sub(self, a, b):
        print('\tcall Int:sub', file=self.target)
    def mul(self, a, b):
        print('\tcall Int:mult', file=self.target)
    def div(self, a, b):
        print('\tcall Int:div', file=self.target)
    def neg(self, a):
        print('\tcall Int:neg', file=self.target)

def cli_parser():
    parser = argparse.ArgumentParser(prog='translate')
    parser.add_argument('source', type=argparse.FileType('r'))
    parser.add_argument('target', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout)
    return parser.parse_args()

assembly_header = """\
.class Sample:Obj

.method $constructor\
"""

def main():
    args = cli_parser()
    parser = lark.Lark(calc_grammar, parser='lalr',
                       transformer=CalculateTree(args.target))
    def gen(s):
        print(s, file=args.target)
    gen(assembly_header)
    for line in args.source:
        line = line.strip()
        if not line:
            continue
        gen('\tconst "%s = "' % line)
        gen('\tcall String:print')
        gen('\tpop')
        try:
            tree = parser.parse(line)
        except lark.exceptions.LarkError:
            print('Invalid line: "%s"' % line, file=sys.stderr)
        else:
            gen('\tcall Int:print')
            gen('\tpop')
            gen('\tconst "\\n"')
            gen('\tcall String:print')
            gen('\tpop')
    gen('\treturn 0')

if __name__ == '__main__' and not sys.flags.interactive:
    main()
