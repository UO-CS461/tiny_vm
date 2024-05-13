import ASTutils as a
import lark.tree as t
import sys
class Checker:
    
    def __init__(self, symboltable):
        self.symboltable = symboltable
        self.warnings = []
        self.methods = {
            '+':["String","Int"],
            '*':["Int"],
            "-":["Int"],
            "/":["Int"],
            '<':["String","Int"],
            '>':["String","Int"],
            '==':["String","Int"],
            '!=':["String","Int"],
        }
        
    def check(self, node):
         
        if isinstance(node, a.Assignment):
            self.check_assignment(node)
        elif isinstance(node,a.BinaryOperation):
            self.check_binops(node)
        elif isinstance(node, a.Conditional):
            self.check_cond(node)
        elif isinstance(node, a.SoloCond):
            self.check_cond(node)
        elif isinstance(node, a.IfStatement):
            self.check_if(node)
        elif isinstance(node, a.WhileStatement):
            self.check_while(node)
    
    def check_assignment(self, node):
        if node.value.infer(self.symboltable) != node.inferred_type :
            self.warnings.append(f"Type mismatch in assignment:{node.name}")

    def check_if(self, node):
        error = self.check_cond(node.condition)
        if error != None:
            sys.tracebacklimit = 0
            raise TypeError(f"\n{error[0]} if {error[1]}")
        if isinstance(node.body, t.Tree):
            for statement in node.body.children:
                if isinstance(statement, a.ASTNode):
                    self.check(statement)
        elif isinstance(node.body, a.ASTNode):
            self.check(node.body)
            
        if isinstance(node.elsebody, t.Tree):
            for statement in node.body.children:
                if isinstance(statement, a.ASTNode):
                    self.check(statement)
        elif isinstance(node.elsebody, a.ASTNode):
            self.check(node.elsebody)
            
    def check_while(self, node):
        error = self.check_cond(node.condition)
        if error != None:
            sys.tracebacklimit = 0
            raise TypeError(f"\n{error[0]} while {error[1]}")
        if isinstance(node.body, t.Tree):
            for statement in node.body.children:
                if isinstance(statement, a.ASTNode):
                    self.check(statement)
        elif isinstance(node.body, a.ASTNode):
            self.check(node.body)
              
    def check_cond(self, node):
        if isinstance(node,a.Conditional):
            cond_type = node.infer(self.symboltable)
            eval = f"{node.left.inferred_type} {node.operator} {node.right.inferred_type} evaluates to {cond_type}\nType {cond_type} does not have method '{node.operator}' and can not return a 'Bool' "
            if cond_type != "Bool":
                return f"Compilation failed\nCondition expression in",f"statement must evaluate to boolean type\n{eval}"
        elif isinstance(node, a.SoloCond):
            cond_type = node.infer(self.symboltable)
            # print(node.value)
            eval = f"{cond_type}\nType {cond_type} is not a 'Bool' "
            if cond_type != "Bool":
                return f"Compilation failed\nCondition expression in",f"statement must evaluate to boolean type\n{eval}"
        return None
    
    def check_binops(self, node):
        if isinstance(node.left,a.Variable):
            left_key = node.left.name
        else:
            left_key = node.left.value
            
        if isinstance(node.right,a.Variable):
            right_key = node.right.name
        else:
            right_key = node.right.value
            
        if node.operator == '+' and node.inferred_type not in self.methods['+']:
            sys.tracebacklimit = 0
            raise TypeError(f"Compilation failed \nat {left_key}+{right_key}\nType {node.inferred_type} does not have method '+' ")
        if node.operator == '-' and node.inferred_type not in self.methods['-']:
            sys.tracebacklimit = 0
            raise TypeError(f"Compilation failed \nat {left_key}-{right_key}\nType {node.inferred_type} does not have method '-' ") 
        if node.operator == '*' and node.inferred_type not in self.methods['*']:
            sys.tracebacklimit = 0
            raise TypeError(f"Compilation failed \nat {left_key}*{right_key}\nType {node.inferred_type} does not have method '*' ")  
        if node.operator == '/' and node.inferred_type not in self.methods['/']:
            sys.tracebacklimit = 0
            raise TypeError(f"Compilation failed \nat {left_key}/{right_key}\nType {node.inferred_type} does not have method '/' ") 
        