import os
class ASTNode:
    def __init__(self):
        self.children = []
    def infer(self, symboltable):
        pass

# this shouldn't be needed since quack doesn't have declarations but I'm leaving it here for now since its not really hurting anyone
class Declaration(ASTNode):
    def __init__(self, name):
        self.name = name

class Assignment(ASTNode):
    def __init__(self, name, value, t_type="NULL"):
        self.inferred_type = None
        self.name = name
        self.value = value
    def infer(self, symboltable):
        # print(self.value)
        self.inferred_type = self.value.infer(symboltable)
        symboltable[self.name] = self.inferred_type
        return self.inferred_type
        

class BinaryOperation(ASTNode):
    def __init__(self, left, operator, right):
        # print(type(left))
        self.left = left
        self.operator = operator
        self.right = right
        self.inferred_type = "OBJ"
        self.identifier = f"{left}{operator}{right}"
    def infer(self,symboltable):
        ltype = self.left.infer(symboltable)
        rtype = self.right.infer(symboltable)

        if ltype == rtype:
            symboltable[self.identifier] = ltype
            self.inferred_type = ltype
        else:
            # do LCA... uh for now just return OBJ I guess.. the most common ancestor?
            symboltable[self.identifier] = self.inferred_type
            return self.inferred_type
        
        return self.inferred_type

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name
        self.inferred_type = None
    def infer(self,symboltable):
        # get the type from the symbol table, if dne return OBJ
        self.inferred_type = symboltable.get(self.name,'OBJ')
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
        symboltable[self.value] = "OBJ"
        return "OBJ"
        
class Methods(ASTNode):
    def __init__(self, obj, method):
        # print(obj)
        self.obj = obj
        self.method = method
    def infer(self,symboltable):
        # should methods have types? the things they return should have a type if it isn't a method uhh for now pass maybe OBJ
        return symboltable.get(self.obj,"OBJ")
        

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