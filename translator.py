#!/usr/bin/python3

from lark import Lark
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

calc_parser = Lark(calc_grammar, parser='lalr')
calc = calc_parser.parse

def postorder(tree):
    tokens = []
    _postorder(tree, tokens)
    return tokens

def _postorder(tree, tokens):
    if tree.data in ('add', 'sub', 'mul', 'div', 'neg'):
        for child in tree.children:
            _postorder(child, tokens)
        tokens.append(tree.data)
    elif tree.data == 'number':
        tokens.append(str(tree.children[0]))

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
            post = postorder(tree)
            print(' '.join(post), file=args.target)

if __name__ == '__main__' and not sys.flags.interactive:
    main()
