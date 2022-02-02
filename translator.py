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


quack_grammar = """

?start: program         // Ignore the first starting node.
    
    program: statement
        | program statement
        
    statement: rexp ";" 
        | assignment

    assignment: lexp (":" NAME)? "=" rexp ";"

    ?rexp: sum

    methodcall: atom "." NAME "(" args ")"
    
    args: rexp? ("," rexp)*
    
    lexp: NAME              -> var
        | atom "." NAME     -> member_access
    
    ?sum: product
        | sum "+" product   -> mc_plus
        | sum "-" product   -> mc_sub
        
    ?product: atom
        | product "*" atom  -> mc_mult
        | product "/" atom  -> mc_div
        | "-" atom          -> mc_neg
        
        
    ?atom: "(" sum ")"
         | methodcall
         | lexp
         | const     

    !const: INT
         | STRING
         | "true"
         | "false"
         | "none"



    %import common.CNAME -> NAME
    %import common.INT
    %import common.WS
    %import python.STRING
    %ignore WS
"""



# The asm code to generate a new line
end_line = """  const "\\n"
  call  String:print
  pop"""


# These methods need to be "de-sugared" and create a different kind of method call in the tree.
builtin_methods = ["mc_plus", "mc_sub", "mc_div", "mc_mult", "mc_neg"]


constant_types = {
    "INT": "Int",
    "STRING": "String",
    "TRUE": "Boolean",
    "FALSE": "Boolean",
    "NONE": "Nothing",
    "OBJ": "Obj"
}


local_vars = {}
local_instructs = []

# Right, post-order traversal of the tree prints the
# instructions in the correct order for arithmetic
# expressions. Useful for parsing right-hand expression
# by adding instructions in the correct order for a stack machine.
def rt_post_recur_print(tree):
    if isinstance(tree, Tree):
        for i in range(len(tree.children) - 1, -1, -1):
            rt_post_recur_print(tree.children[i])

        if tree.data == "const":
            local_instructs.append(f"  const {tree.children[0]}")
        elif tree.data == "var":
            local_instructs.append(f"  load {tree.children[0]}")
        elif tree.data == "methodcall":
            call_method(tree)
        elif tree.data in builtin_methods:
            call_method_builtins(tree)
        elif tree.data == "args":   # args are already pushed onto the stack.
            pass
        else:
            print(tree)
            raise Exception()


"""
Assumes the tree is an assignment node.
"""
def assign(tree):
    name = tree.children[0].children[0]  # the name of the variable
    type = tree.children[1]
    local_vars.update( {name: type} )

    # Evaluarte the right hand side of the assignment.
    rt_post_recur_print(tree.children[2])


    #local_instructs.append(f"  new {type}")
    #local_instructs.append(f"  call {type}:$constructor")
    #local_instructs.append(f"  pop")

    # ASM instructions to create new Integer variable and assign the value on the stack.
    local_instructs.append(f"  store {name}")


def call_method_builtins(tree):
    if tree.children[0].data == "var":
        type = local_vars[tree.children[0].children[0]]
    elif tree.children[0].data == "const":
        type = constant_types[tree.children[0].children[0].type]

    elif tree.children[0].data in  builtin_methods:
        type = infer_type(tree.children[0])
    else:
        print(tree)
        raise Exception()

    local_instructs.append(f"  call {type}:{tree.data[3:]}")


# Gets the type of an input tree by following the children
# until the child is a token or the child is a variable.
def infer_type(tree):
    tmp = tree
    while not isinstance(tmp, Token) and tmp.data != "var":
        tmp = tmp.children[0]

    type = None

    if isinstance(tmp, Tree) and tmp.data == "var":
        type = local_vars[tmp.children[0].value]
    elif tmp.type in constant_types.keys():
        type = constant_types[tmp.type]

    # if there is not a type then something went wrong
    if type is None:
        raise Exception()

    return type


def call_method(tree):
    # Get the type of the reciever object.
    recv = tree.children[0]
    method = tree.children[1]

    if recv.data == "var":
        type = local_vars[recv.children[0]]

        local_instructs.append(f"  call {type}:{method}")
    elif recv.data == "const":

        type = constant_types[recv.children[0].type]
        local_instructs.append(f"  call {type}:{method}")

    elif recv.data in builtin_methods:
        # Get the type for the current method call.
        type = infer_type(recv)
        local_instructs.append(f"  call {type}:{method}")
    else:
        print(recv)
        raise Exception()

    # Pop the nothing object from the stack returned by the print method.
    if method == "print":
        local_instructs.append("  pop")


# Parses the following statements:
#       - assignment
#       - method calls
def parse_statement(tree):
    if tree.children[0].data == "assignment":
        assign(tree.children[0])

    elif tree.children[0].data == "methodcall":
        rt_post_recur_print(tree.children[0])
    elif tree.children[0].data in builtin_methods:  # Ignore de-sugared calls that do not have an effect.
        pass
    elif isinstance(tree.children[0].data, Token): # Just a token that does not have an effect.
        pass
    else:
        print(tree.children[0])
        raise Exception()


# Parses the Quack grammar tree returned by the call to Lark.
def parse_quack(tree: Tree):
    if isinstance(tree, Tree):
        # The children of a program node can be another program and statement
        # or only a statement.
        if tree.children[0].data == "statement":
            parse_statement(tree.children[0])
        else:
            parse_quack(tree.children[0])
            parse_statement(tree.children[1])



def printLocalVars():
    if len(local_vars) > 0:
        print(f".local ", end="")

        names = list(local_vars.keys())
        for i in range(len(names) - 1):
            print(f"{names[i]}", end=",")

        print(f"{names[-1]}")


def main():
    # Open and read the expressions from the source file.
    try:
        f_name = argv[1]
        with open(f_name, "r") as fp:
            quack_input = fp.read()

    except IndexError:
        print("usage: python3 translator.py <source-file>\n")
        return
    except FileNotFoundError:
        print(f"File not found: {f_name}")
        return


    quack_parser = Lark(quack_grammar, parser='lalr')

    # Genereate the parse tree using the lark interface.
    tree = quack_parser.parse(quack_input)
    parse_quack(tree)
    #print(tree.pretty())

    print(f".class Main:Obj")
    print(".method $constructor")

    # Print the local variables stored in local_vars
    printLocalVars()
    print("  enter")

    # Exit program
    local_instructs.append(end_line)
    local_instructs.append("  const none")
    local_instructs.append("  return 0")

    for instr in local_instructs:
        print(instr)



if __name__ == "__main__":
    main()
