"""
Translates arithmetic expressions located in a source text file
to tiny vm assembly code and prints to standard output.

usage: python3 translator.py <source-file>

To use with the assembler:
    - Redirect stdout of this program to a *.asm file. This generated file will be the
      source for the assembler program.

    source-file: Contains lines of arithmetic expressions.

    Thomas Renn
"""

# ---------------------------------------
# ---------------------------------------
# ---------------------------------------
# calc_grammar copied from the example script at:
# https://lark-parser.readthedocs.io/en/latest/examples/calc.html#sphx-glr-examples-calc-py

from lark import Lark, Token, Tree
from sys import argv

calc_grammar = """
    ?start: sum
          | NAME "=" sum    -> assign_var

    ?sum: product
        | sum "+" product   -> plus
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mult
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME             -> var
         | "(" sum ")"

    
    
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""


calc_parser = Lark(calc_grammar, parser='lalr')
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

# The ams code to generate a new line
end_line = """  const "\\n"
  call  String:print
  pop"""



# Right, post-order traversal of the tree prints the
# instructions in the correct order for arithmetic
# expressions.
def recur_print(tree):
    if isinstance(tree, Tree):
        for i in range(len(tree.children) - 1, -1, -1):
            recur_print(tree.children[i])

        if tree.data == "number":
            print(f"  const {tree.children[0]}")
        else:
            print(f"  call Int:{tree.data}")


def main():
    # Open and read the expressions from the source file.
    try:
        f_name = argv[1]
        with open(f_name, "r") as fp:
            expressions = fp.readlines()

    except IndexError:
        print("usage: python3 translator.py <source-file>\n")
        return
    except FileNotFoundError:
        print(f"File not found: {f_name}")
        return

    print(".class Sample:Obj")
    print(".method $constructor")

    # Read in the expressions from the source file and
    # generate the instructions to execute the expression
    # using the tiny_vm.
    for exp in expressions:

        # Instruction to print the expression from the source file.
        tmp = exp.rstrip('\n')
        print(f"  const \"{tmp} = \"")
        print("  call  String:print")
        print("  pop")

        # Genereate the parse tree using the lark interface.
        tree = calc_parser.parse(tmp)

        # Print out the instructions in the correct order.
        recur_print(tree)

        # Instruction to print the value of the expression.
        print(f"  call Int:print")
        print("  pop")
        print(end_line)

    print("  return 0")

if __name__ == "__main__":
    main()
