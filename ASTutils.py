import os
class ASTNode:
    pass

class Declaration(ASTNode):
    def __init__(self, name, t_type):
        self.name = name
        self.t_type = t_type

class Assignment(ASTNode):
    def __init__(self, name, value, t_type="OBJ"):
        self.name = name
        self.t_type = t_type
        self.value = value

class BinaryOperation(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

class Constant(ASTNode):
    def __init__(self, value):
        self.value = value
        
class Methods(ASTNode):
    def __init__(self, obj, method):
        self.obj = obj
        self.method = method
        

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