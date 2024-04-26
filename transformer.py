from lark import Lark, Transformer, v_args
import sys
import os
import ASTutils
# From Lark Example calculator Grammar

calc_grammar = """
    ?start: declaration
        | assignment
        | method_call
    
    ?declaration: NAME ":" TYPE ";" -> declare_var
    ?assignment: NAME ":" TYPE "=" value ";" -> assign_var
        | NAME "=" value ";" -> assign_var_notype

    ?method_call: NAME "." NAME "(" ")" ";" -> call_method
    
    ?value: sum
    
    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | NAME             -> var
         | "(" sum ")"
         | NAME ":" TYPE ";" -> declare_var
         | STRING -> number

    TYPE: "Int" 
         | "String"
         | "OBJ"
         
    STRING: /"[^"]*"/
    
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""
# Single pass / direct translator
@v_args(inline=True)
class AssemblyCodeGenerator(Transformer):
    # Got my lefts and rights swapped
    # working now
    def __init__(self):
        self.vars = {}
        self.types = {}
    # I don't think this requires storing or loading variables right now
    # but i'm going to leave this here even if its incorrect
    def declare_var(self, name, t_type):
        if name not in self.vars:
            if t_type == "String":
                self.vars[name] = ""

            else:
                self.vars[name] = 0
            self.types[name] = t_type
            return f".local {name}"
        else:
            # maybe throw and error since you declared the var twice
            return ""
    
    # this is very silly but i'm not as familiar with overloading in python as I am in c likes
    # I very much dislike this though.
    # maybe in the future figure out how to change the order lark passes args
    def assign_var(self, name, t_type, value):
        # Handle variable assignment
        
        # print to a debug file for easier reading
        print(f"t_type:{t_type}\n name:{name}\n value:\n{value}\n",file=debug)
        if name not in self.vars:
            self.vars[name] = value
            return f".local {name}\n{value}\nstore {name}"
        return f"{value}\nstore {name}"
    
    # how to write a polymorphic function in python should be simple ...
    def assign_var_notype(self, name, value):
        # Handle variable assignment
        if name not in self.vars:
            self.vars[name] = value
            return f".local {name}\n{value}\nstore {name}"
        return f"{value}\nstore {name}"

    def var(self, name):
        # Handle variable usage
        if name not in self.vars:
            raise ValueError(f"Variable '{name}' is not defined.")
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
    
    def string(self,value):
        return f"const {value}"
    
    # def type_print(self,t_type,value)

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

# Parse -> AST -> ASM
@v_args(inline=True)
class ASTGenerator(Transformer):
    # Extending the Lark Transformer class to generate an AST instead of directly translating
    def __init__(self):
        self.vars = {}
        self.types = {}
        self.asm_code = []
        self.asm_code.append(f".class Main:Obj\n.method $constructor")
        
    
    def declare_var(self, name, t_type):
        self.types[name] = t_type
        if(t_type == "String"):
            self.vars[name] = ""
            
        elif (t_type == "Int"):
            self.vars[name] = 0
            
        elif (t_type == "Bool"):
            self.vars[name] = True
            
        else:
            self.vars[name] = None
            
        return Declaration(name,t_type)

    def assign_var(self, name, t_type, value):
        self.vars[name] = value
        self.types[name] = t_type
        return ASTutils.Assignment(name, value, t_type)
    
    def call_method(self, obj, method):
        return ASTutils.Methods(obj,method)
    
    def assign_var_notype(self, name, value):
        return ASTutils.Assignment(name, value)
    
    def add(self, left, right):
        return ASTutils.BinaryOperation(left, '+', right)

    def sub(self, left, right):
        return ASTutils.BinaryOperation(left, '-', right)

    def mul(self, left, right):
        return ASTutils.BinaryOperation(left, '*', right)

    def div(self, left, right):
        return ASTutils.BinaryOperation(left, '/', right)

    def number(self, value):
        return ASTutils.Constant(value)

    def string(self, value):
        return ASTutils.Constant(value)

    def var(self, name):
        return ASTutils.Variable(name)
    
    def print_ast(self, node=None, indent=0):
        if node is None:
            return

        if isinstance(node, ASTutils.Declaration):
            print(' ' * indent, 'Declaration:', node.name, node.t_type)
        elif isinstance(node, ASTutils.Assignment):
            print(' ' * indent, 'Assignment:', node.name)
            self.print_ast(node.value, indent + 4)
        elif isinstance(node, ASTutils.BinaryOperation):
            print(' ' * indent, 'Binary Operation:', node.operator)
            self.print_ast(node.left, indent + 4)
            self.print_ast(node.right, indent + 4)
        elif isinstance(node, ASTutils.Constant):
            print(' ' * indent, 'Constant:', node.value)
        elif isinstance(node, ASTutils.Variable):
            print(' ' * indent, 'Variable:', node.name)
        elif isinstance(node, ASTutils.Methods):
            print(' ' * indent, 'Method Call:', node.obj,":",f"{self.types[node.obj]}, {node.method}")

    def generate_asm(self, node=None):
        if node is None:
            return ''
        if isinstance(node, ASTutils.Declaration):
            return ''
        elif isinstance(node, ASTutils.Assignment):
            asm = self.generate_asm(node.value)
            return f"{asm}\nstore {node.name}"
        elif isinstance(node, ASTutils.Methods):
            assert node.obj in self.types.keys()
            call = f"call {self.types[node.obj]}:{node.method}"
            if (node.method == "print"):
                call += "\npop"
            return call
        elif isinstance(node, ASTutils.BinaryOperation):
            left_asm = self.generate_asm(node.left)
            right_asm = self.generate_asm(node.right)
            if node.operator == '+':
                return f"{right_asm}\n{left_asm}\ncall Int:plus"
            elif node.operator == '-':
                return f"{right_asm}\n{left_asm}\ncall Int:minus"
            elif node.operator == '*':
                return f"{right_asm}\n{left_asm}\ncall Int:mult"
            elif node.operator == '/':
                return f"{right_asm}\n{left_asm}\ncall Int:div"
        elif isinstance(node, ASTutils.Constant):
            return f"const {node.value}"
        elif isinstance(node, ASTutils.Variable):
            return f"load {node.name}"
            
# probably need to generate the asm file this time instead of just generating the code and printing it out
def main():
    debug = open('debug', 'w', encoding="utf-8")
    file = False
    asm = []
    transformer = ASTGenerator()
    calc_parser_ptree = Lark(calc_grammar, parser='lalr')
    calc_parser = Lark(calc_grammar, parser='lalr', transformer=transformer)
    calc = calc_parser.parse
    calcp = calc_parser_ptree.parse
    for index, arg in enumerate(sys.argv[1:]):
        if arg == "-f":
            if index + 1 <len(sys.argv[1:]):
                filename = sys.argv[index+2]
                file = True
            else:
                print(f"Error: requires filename after -f")
                return
    if file:
        path = ASTutils.find_file(os.getcwd(),filename)
        if path:
            print(f"Found {filename} at:{path}")
        else:
            print(f"File {filename} not found in:{os.getcwd()}")
            return
        try:
            # Open the file in read mode as a stream
            with open(path, 'r') as file_stream:
                # Process the file stream (e.g., read lines, parse data)
                for line in file_stream:
                    # skip new lines
                    if line != "\n":
                        asm.append(calc(line.strip()))
  
        except FileNotFoundError:
            print("File not found:", path)
        except IOError:
            print("Error opening file:", path)
        
        main = open('$Main.asm', 'w+', encoding="utf-8")
        print(f".class $Main:Obj\n.method $constructor",file=main)
        print('.local',','.join(transformer.vars.keys()),file=main)
        for i in range(len(asm)):
            print(transformer.generate_asm(asm[i]),file=main)
        print(f"return 0\n",file=main)
    else:
        while True:
            try:
                s = input('> ')
            except EOFError:
                break
            # Generate the asm code
            AST = calc(s.strip())
            ptree = calcp(s.strip())
            print("Parse Tree:")
            tree = ptree.pretty('   ')
            print(tree)
            print("AST:")
            transformer.print_ast(AST)
            print("ASM:")
            print(transformer.generate_asm(AST))
            
    debug.close()
            
if __name__ == '__main__':
    main()

