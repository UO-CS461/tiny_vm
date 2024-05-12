import os
import lark.tree as t
class ASTNode:
    def __init__(self):
        self.children = []
    def infer(self, symboltable):
        pass

class Conditional(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
        self.inferred_type = "Obj"
        self.identifier = f"{left}{operator}{right}"
        
    def infer(self, symboltable):
        ltype = self.left.infer(symboltable)
        rtype = self.right.infer(symboltable)
        if ltype != rtype:
            # same thing as binary ops, do lca
            raise ValueError("Types of left and right expressions in conditional must match")
        # for now if the two types match return a bool
        symboltable[self.identifier] = ltype
        self.inferred_type = "Bool"
        return self.inferred_type

class IfStatement(ASTNode):
    def __init__(self, condition, body, elsebody=None):
        self.condition = condition
        self.elsebody = elsebody
        self.body = body
          
    def infer(self, symboltable):
        condition_type = self.condition.infer(symboltable)
        if condition_type != "Bool":
            raise ValueError("Condition expression in if statement must evaluate to boolean type")
        # print(self.body)
        # print(self.elsebody.children)
        if isinstance(self.body, t.Tree):
            for statement in self.body.children:
                if isinstance(statement, ASTNode):
                    statement.infer(symboltable)
        elif isinstance(self.body, ASTNode):
            self.body.infer(symboltable)

        if isinstance(self.elsebody, t.Tree):
            for statement in self.elsebody.children:
                if isinstance(statement, ASTNode):
                    statement.infer(symboltable)
        elif isinstance(self.elsebody, ASTNode):
            self.elsebody.infer(symboltable)
        
class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def infer(self, symboltable):
        condition_type = self.condition.infer(symboltable)
        if condition_type != "Bool":
            raise ValueError("Condition expression in while loop must evaluate to boolean type")
        
        if isinstance(self.body, t.Tree):
            for statement in self.body.children:
                if isinstance(statement, ASTNode):
                    statement.infer(symboltable)
                    
        elif isinstance(self.body, ASTNode):
            self.body.infer(symboltable)
                     
class Assignment(ASTNode):
    def __init__(self, name, value, t_type="NULL"):
        self.inferred_type = None
        self.name = name
        self.value = value
    def infer(self, symboltable):
        # print(self.value)
        self.inferred_type = self.value.infer(symboltable)
        # check if name is alreadyin table
        if self.name in symboltable:
            # do LCA
            existing_type = symboltable[self.name]
            # print("existing type:",existing_type)
            if (existing_type != self.inferred_type):
                # for now just assume LCA is Obj since thats really the only ancestor for all types right now
                print("we got here")
                self.inferred_type = "Obj"
                                 
        symboltable[self.name] = self.inferred_type
        # print("final type:",self.inferred_type)
        # print("symbol table var value:", symboltable[self.name])
        return self.inferred_type
        
class BinaryOperation(ASTNode):
    def __init__(self, left, operator, right):
        # print(left)
        self.left = left
        self.operator = operator
        self.right = right
        # kinda hacky 
        self.inferred_type = "Obj"
        self.identifier = f"{left}{operator}{right}"
    def infer(self,symboltable):
        ltype = self.left.infer(symboltable)
        rtype = self.right.infer(symboltable)

        if ltype == rtype:
            symboltable[self.identifier] = ltype
            self.inferred_type = ltype
        else:
            # do LCA... uh for now just return Obj I guess.. the most common ancestor?
            symboltable[self.identifier] = self.inferred_type
            return self.inferred_type
        
        return self.inferred_type

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name
        self.inferred_type = None
    def infer(self,symboltable):
        # get the type from the symbol table, if dne return Obj
        self.inferred_type = symboltable.get(self.name,'Obj')
        return self.inferred_type
        
class Constant(ASTNode):
    def __init__(self, value):
        # so value in this case is a lark lexed token, if I want to do type inference logic here I gotta be able to tell what's a string and whats an int 
        self.value = value
        self.inferred_type = None
    def infer(self, symboltable):
        # this feels kind of hacky but since consts can only be strings or ints this should work
        # especially since the grammar won't allow strings that don't start with and end with quotes
        if(self.value.startswith("\"")):
            self.inferred_type = "String"
            symboltable[self.value] = self.inferred_type
            return "String"
        else:
            self.inferred_type = "Int"
            symboltable[self.value] = self.inferred_type
            return "Int"
        symboltable[self.value] = "Obj"
        return "Obj"
        
class Methods(ASTNode):
    def __init__(self, obj, method, args=None):
        # print(obj)
        self.obj = obj
        self.method = method
        self.args = args
        
    def infer(self,symboltable):
        # should methods have types? the things they return should have a type if it isn't a method uhh for now pass maybe Obj
        return symboltable.get(self.obj,"Obj")
        

def find_file(start_dir, target_file):
    # Iterate over all files and directories in the start directory
    for root, dirs, files in os.walk(start_dir):
        # Check if the target file exists in the current directory
        if target_file in files:
            # Construct the full path to the target file
            file_path = os.path.join(root, target_file)
            return file_path  # Return the path to the file

    # If the file is not found in any directory
    return None