from lark import Lark, Transformer, v_args 
import lark.tree as t
import sys
import os
import ASTutils
import staticsemantics as ss
# From Lark Example calculator Grammar

calc_grammar = """
    ?start: codeblock
    
    codeblock: statement+
    
    ?statement: assignment
        | method_call
        | flow
    
    ?condition: value evaluator value -> conditional
        | value -> boolean

    ?evaluator: ">" -> gt
        | "<" -> lt
        | "==" -> equals
        | "!=" -> nequals
        | "and"
        | "or"
        | "not"
        
    ?flow: ifstmt
        | elifstmt
        | whilestmt
        
    ?ifstmt: "if" condition "{" start* "}" elsestmt -> ifcall
    
    ?elifstmt: "elif" condition "{" start* "}" -> ifcall
    
    ?elsestmt: "else" "{" start* "}" -> elsecall
        | -> codeblock
    
    ?whilestmt: "while" condition "{" start* "}" -> whilecall
    
    ?assignment: NAME "=" value ";" -> assign_var

    ?method_call: value "." NAME "(" argument_list? ")" ";" -> call_method
    
    argument_list: value ("," value)*
    
    ?value: sum
        | TRUE -> tf
        | FALSE -> tf
        
    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | STRING -> string
         | NAME             -> var
         | "(" sum ")"
    TRUE: "true"
    FALSE: "false"
    STRING: /"[^"]*"/
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""
# Parse -> AST -> ASM
@v_args(inline=True)
class ASTGenerator(Transformer):
    # Extending the Lark Transformer class to generate an AST instead of directly translating
    def __init__(self):
        self.vars = set()
        self.symboltable = {}
        # this is really hacky and bad
        self.if_counter = 0
        self.while_counter = 0
    
    def assign_var(self, name, value):
        self.vars.add(name)
        node = ASTutils.Assignment(name, value)
        node.infer(self.symboltable)
        return node
    
    def call_method(self, obj, method, args=None):
        node = ASTutils.Methods(obj,method,args)
        node.infer(self.symboltable)
        return node
    
    def argument_list(self, *args):
        return list(args)
    
    def conditional(self, left, operator, right):
        # I could abuse the Binary Operation node for now...
        # but that will fall apart when I have to add and, or and not
        node = ASTutils.Conditional(left,operator,right)
        node.infer(self.symboltable)
        return node
    
    def ifcall(self, conditional, body, elsepart=None):
        node = ASTutils.IfStatement(conditional,body,elsepart)
        node.infer(self.symboltable)
        return node
    
    def whilecall(self,conditional, body):
        node = ASTutils.WhileStatement(conditional,body)
        node.infer(self.symboltable)
        return node
    
    # EVALUATORS
    
    def gt(self):
        return ">"
    def lt(self):
        return "<"
    def equals(self):
        return "=="
    def nequals(self):
        return "!="
    
    # BIN OPS
    
    def boolean(self, value):
        node = ASTutils.SoloCond(value)
        node.infer(self.symboltable)
        return node
        
    def add(self, left, right):
        node = ASTutils.BinaryOperation(left, '+', right)
        node.infer(self.symboltable)
        return node

    def sub(self, left, right):
        node = ASTutils.BinaryOperation(left, '-', right)
        node.infer(self.symboltable)
        return node

    def mul(self, left, right):
        node = ASTutils.BinaryOperation(left, '*', right)
        node.infer(self.symboltable)
        return node

    def div(self, left, right):
        node = ASTutils.BinaryOperation(left, '/', right)
        node.infer(self.symboltable)
        return node

    # TERMINALS
    
    def number(self, value):
        node = ASTutils.Constant(value)
        node.infer(self.symboltable)
        return node
        
    def string(self, value):
        node = ASTutils.Constant(value)
        node.infer(self.symboltable)
        return node

    def tf(self, value):
        node = ASTutils.Constant(value)
        node.infer(self.symboltable)
        return node
    
    def var(self, name):
        node = ASTutils.Variable(name)
        node.infer(self.symboltable)
        return node
    
    # VISITORS
    
    def print_ast(self, node=None, indent=0):
        if node is None:
            return
        
        if isinstance(node,t.Tree):
            for statement in node.children:
                self.print_ast(statement)
        if isinstance(node, ASTutils.Assignment):
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
            print(' ' * indent, 'Method Call:', node.method)
            self.print_ast(node.obj, indent + 4)
            if node.args is not None:
                for arg in node.args:
                    self.print_ast(arg, indent + 8)
        elif isinstance(node, ASTutils.IfStatement):
            print(' ' * indent, 'If Statement:')
            self.print_ast(node.condition, indent + 4)
            self.print_ast(node.body, indent + 4)
            if node.elsebody is not None:
                print(' ' * indent, 'Else:')
                self.print_ast(node.elsebody, indent + 4)
        elif isinstance(node, ASTutils.WhileStatement):
            print(' ' * indent, 'While Loop:')
            self.print_ast(node.condition, indent + 4)
            self.print_ast(node.body, indent + 4)
        elif isinstance(node, ASTutils.Conditional):
            print(' ' * indent, 'Conditional:')
            self.print_ast(node.left, indent + 4)
            print(' ' * (indent + 4), 'Operator:', node.operator)
            self.print_ast(node.right, indent + 4)
        elif isinstance(node, ASTutils.SoloCond):
            print(' ' * indent, 'Solo Conditional:')
            self.print_ast(node.value, indent + 4)

    def typecheck(self, checker, node=None ):
        if node is None:
            return ''
        if isinstance(node,t.Tree):
            for statement in node.children:
                checker(statement)
            
    def generate_asm(self, node=None):
        if node is None:
            return ''
        if isinstance(node,t.Tree):
            asm = ""
            for statement in node.children:
                asm+= self.generate_asm(statement) + "\n"
            return asm
        
        if isinstance(node, ASTutils.Assignment):
            asm = self.generate_asm(node.value)
            return f"{asm}\nstore {node.name}"
        
        elif isinstance(node,ASTutils.IfStatement):
            ifasm = ""
            condition_asm = self.generate_asm(node.condition)
            then_asm = self.generate_asm(node.body)
            thenlabel = f"then_{self.if_counter}"
            elselabel = f"else_{self.if_counter}"
            endiflabel = f"endif_{self.if_counter}"
            self.if_counter += 1
            ifasm += f"{condition_asm}\n"
            ifasm += f"jump_ifnot {elselabel}\n"
            ifasm += f"jump {thenlabel}\n"
            ifasm += f"{thenlabel}:\n{then_asm}\njump {endiflabel}\n"
            if node.elsebody != None:
                else_asm = self.generate_asm(node.elsebody)
                ifasm+=f"{elselabel}:\n"
                ifasm+= f"{else_asm}"
            ifasm += f"{endiflabel}:\n"
            return ifasm
        
        elif isinstance(node, ASTutils.WhileStatement):
            while_asm = ""
            condition_asm = self.generate_asm(node.condition)
            body_asm = self.generate_asm(node.body)
            whilelabel = f"while_{self.while_counter}"
            endlabel = f"endwhile_{self.while_counter}"
            self.while_counter += 1
            while_asm += f"{whilelabel}:\n"
            while_asm += f"{condition_asm}\n"
            while_asm += f"jump_ifnot {endlabel}\n"
            while_asm += f"{body_asm}\n"
            while_asm += f"jump {whilelabel}\n"
            while_asm += f"{endlabel}:\n"
            return while_asm
            
        elif isinstance(node,ASTutils.Conditional):
            left_asm = self.generate_asm(node.left)
            right_asm = self.generate_asm(node.right)
            if node.operator == '>':
                return f"{left_asm}\n{right_asm}\ncall {self.symboltable[node.identifier]}:less"
            elif node.operator == '<':
                return f"{right_asm}\n{left_asm}\ncall {self.symboltable[node.identifier]}:less"
            elif node.operator == '==':
                return f"{right_asm}\n{left_asm}\ncall {self.symboltable[node.identifier]}:equals"            
        elif isinstance(node,ASTutils.SoloCond):
            s_cond_asm = self.generate_asm(node.value)
            return f"{s_cond_asm}"
                   
        elif isinstance(node, ASTutils.Methods):
            asm = self.generate_asm(node.obj)
            if isinstance(node.obj, ASTutils.Constant):
                nodekey = node.obj.value
            else:
                nodekey = node.obj.name
            if(node.args != None):
                # uhh, do something with the args,
                # probably something like load them I think...
                # I don't think we need this for mini quack right now though
                # since we're only doing <= >= == < > which aren't called like methods
                # like print, which I think is the only "legitimate" method
                pass
            
            call = f"{asm}\ncall {self.symboltable[nodekey]}:{node.method}"
            
            if (node.method == "print"):
                call += "\npop"
            return call
        
        elif isinstance(node, ASTutils.BinaryOperation):
            left_asm = self.generate_asm(node.left)
            right_asm = self.generate_asm(node.right)
            if node.operator == '+':
                return f"{right_asm}\n{left_asm}\ncall {self.symboltable[node.identifier]}:plus"
            elif node.operator == '-':
                return f"{right_asm}\n{left_asm}\ncall {self.symboltable[node.identifier]}:minus"
            elif node.operator == '*':
                return f"{right_asm}\n{left_asm}\ncall {self.symboltable[node.identifier]}:mult"
            elif node.operator == '/':
                return f"{right_asm}\n{left_asm}\ncall {self.symboltable[node.identifier]}:div"
            
        elif isinstance(node, ASTutils.Constant):
            return f"const {node.value}"
        
        elif isinstance(node, ASTutils.Variable):
            return f"load {node.name}"
        return ""
            

def main():
    debug = open('debug', 'w', encoding="utf-8")
    file = False
    asm = ""
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
                content = file_stream.read().replace("\n","")
                tree = calc(content)
                checker = ss.Checker(transformer.symboltable)
                # print(tree.pretty("     "))
                # transformer.print_ast(tree)
                transformer.typecheck(checker.check,tree)
                asm = transformer.generate_asm(tree)
  
        except FileNotFoundError:
            print("File not found:", path)
        except IOError:
            print("Error opening file:", path)
        
        main = open('Main.asm', 'w+', encoding="utf-8")
        print(f".class Main:Obj\n.method $constructor",file=main)
        print('.local',','.join(transformer.vars),file=main)
        print(asm,file=main)
        print(f"return 0\n",file=main)
        # print(transformer.symboltable)
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

