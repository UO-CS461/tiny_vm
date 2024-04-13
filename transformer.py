from lark import Lark, Transformer, v_args

# From Lark Example calculator Grammar
calc_grammar = """
    ?start: sum
          | NAME "=" sum    -> assign_var

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
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

@v_args(inline=True)
class AssemblyCodeGenerator(Transformer):
    # Got my lefts and rights swapped
    # working now
    def __init__(self):
        self.vars = {}

    # I don't think this requires storing or loading variables right now
    # but i'm going to leave this here even if its incorrect
    
    
    def assign_var(self, name, value):
        # Handle variable assignment
        self.vars[name] = value
        # should probably have it grab the name from the dictionary
        # and if it's not there make a .local {name} declaration
        return f"const {value}\nstore {name}"

    def var(self, name):
        # Handle variable usage
        return f"load {name}"

    # Lark example used from operators, defining these by hand for our language

    def add(self, left, right):
        # Handle addition operation
        return f"{right}\n{left}\ncall Int:plus"

    def sub(self, left, right):
        # Handle subtraction operation
        return f"{right}\n{left}\ncall Int:minus"

    def mul(self, left, right):
        # Handle multiplication operation
        return f"{right}\n{left}\ncall Int:mult"

    def div(self, left, right):
        # Handle division operation
        return f"{right}\n{left}\ncall Int:div"

    def number(self, value):
        # Handle constants
        return f"const {value}"


    # I don't think I need this but I might be wrong
    # def sum_in_parentheses(self, expr):
    #     # Handle expressions within parentheses
    #     return expr

    # Recursive handling
    
    def sum(self, left, op, right):
        # Handle sum (addition or subtraction) with recursion for nested expressions
        return f"{self.transform(left)}\n{self.transform(right)}\ncall Int:{op}"

    def product(self, left, op, right):
        # Handle product (multiplication or division) with recursion for nested expressions
        return f"{self.transform(left)}\n{self.transform(right)}\ncall Int:{op}"


# parser and transformer could seperate out into 2 different parts but according to lark this is faster
calc_parser = Lark(calc_grammar, parser='lalr', transformer=AssemblyCodeGenerator())
calc = calc_parser.parse

def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        
        # Generate the asm code
        asm = calc(s)
        print("Parse tree (concrete syntax):")
        print(asm)

if __name__ == '__main__':
    main()
