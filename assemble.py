"""An assembler for the tiny virtual machine.
(Initial, stripped down version.)

This is a single-pass assembler with back-patching resolution.
There are two approaches to "resolving" labels:
(a) Two pass resolution: Run through the source code once to determine
    addresses, then run through a second time to actually produce
    object code with resolved addresses.  The simple assembler we use
    in CIS 211 for the Duck Machine uses two pass resolution.
(b) One pass assembly with back-patching.  We keep track of all the
    references to labels and "patch them up" at the end.
"""

import re
import sys
import json
from pathlib import Path
import argparse
import configparser
from typing import Dict, List,  Optional, Tuple

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Configuration:
    def __init__(self):
        config = configparser.ConfigParser()
        try:
            config.read("asm.conf")
            self.tvmlib = Path(config["DEFAULT"]["TVMLIB"])
        except FileExistsError:
            # If no configuration file is present, we will look in ./OBJ
            self.tvmlib = Path("./OBJ")

CONFIG = Configuration()  # Visible from any code


def cli() -> object:
    parser = argparse.ArgumentParser(
        description="Assemble tiny virtual machine module"
                    "into JSON-formatted object code"
    )
    parser.add_argument("source", type=argparse.FileType("r"))
    parser.add_argument("target", type=argparse.FileType("w"),
                        nargs="?", default=sys.stdout)
    return parser.parse_args()

# ----------------
#  Imported modules:  What we need to know is
#    - Slot numbers for methods, e.g., "print" is
#      the second slot.
#    - Field numbers for load and store operations
#

class ImportedModule:
    """Imported module uses information from
    json file
    """
    def __init__(self, path: Path):
        with open(path, "r") as source:
            self.json = json.load(source)
        # Dict from name to position would be faster, but
        # number of lookups is very small
        self.methods: List[str] = self.json["methods"]
        self.fields:  List[str] = self.json["fields"]

    def method_slot(self, name: str) -> int:
        return self.methods.index(name)

    def n_methods(self) -> int:
        return len(self.methods)

    def field_slot(self, name: str) -> int:
        return self.fields.index(name)




IMPORTS: Dict[str, ImportedModule] = {}
def import_module(module: str) -> ImportedModule:
    if module not in IMPORTS:
        path = CONFIG.tvmlib.joinpath(module).with_suffix(".json")
        IMPORTS[module] = ImportedModule(path)
    return IMPORTS[module]

def resolve_call(full_name: str) -> int:
    """Resolve "Class:method" to slot number"""
    class_name, method_name = full_name.split(":")
    module_record = import_module(class_name)
    method_slot = module_record.method_slot(method_name)
    return method_slot

# ----------------
#  The instruction set of the machine and the numeric
#  encoding of instructions must be consistent between
#  assembler and loader, so it is derived from a common
#  text file, opdefs.txt.  The assembler constructs an
#  internal representation for translation.
#
#  There is one ugly hack in this scheme:  We need to
#  know that constants are re-encoded in the loader, because
#  constant offsets in the run-time constant pool depend on
#  all loaded modules (non-local information).
#

class InstructionDef:
    def __init__(self, name: str, code: int, ops: int):
        self.name = name
        self.code = code
        self.ops = ops

    def size(self) -> int:
        """An instruction without an operand
        takes 1 word; with operand, 2 words.
        """
        return 1 + self.ops

    def __str__(self):
        if self.ops:
            suffix = "  <op>"
        else:
            suffix = ""
        return f"{self.code} ({self.name}){suffix}"


class InstructionSet:
    """A dict-like structure
    mapping instruction names to InstructionCode objects
    """
    def __init__(self, path: str):
        self.ops: Dict[str, InstructionDef] = {}
        """Instruction set initialized from text table"""
        opcode = 0
        with open(path, "r") as f:
            for line in f:
                # Strip comments, discard empty lines
                line = line.split("#")[0].strip()
                if not line:
                    continue
                # What remains should be an instruction definition
                parts = line.split(",")
                name, code, ops = parts
                instr = InstructionDef(name, opcode, ops)
                self.ops[name] = instr
                opcode += 1

    def __getitem__(self, name: str):
        return self.ops[name]


# FIXME: Operands to be resolved
# First just for constants; then add
#   - Labels
#   - Classes
#   - Class.method   (Done)
#   - Class.field
# with all the class things depending on reading
# OTHER json files.  (So we get separate compilation
# after all).  Create stub symbol files for built-ins.
# So assembler does a lot of the symbolic -> numeric resolution. 

# Instruction set is a global
INSTRS = InstructionSet("opdefs.txt")


class Instruction:
    """Object code instruction, including operand if any."""
    def __init__(self, label: Optional[str],
                 operation: InstructionDef,
                 operand: Optional[str]):
        self.label = label
        self.operation = operation
        self.operand = operand
        if operation.ops == '0':
            assert operand is None
        else:
            assert operand is not None

    def __str__(self) -> str:
        if self.label:
            label = f"{self.label}: "
        else:
            label = "  "
        if self.operand:
            operand = f"    {self.operand}"
        else:
            operand = ""
        return f"{label} {self.operation.name} {operand}"


# ----------------
# Our object file will be a JSON structure with
# constants, code, and other information.  We'll build
# it up in an object and then dump it all at once.
#
class ObjectCode:
    def __init__(self):
        # The following are initialized in declare_class
        self.class_name: str = ""
        self.super_name: str = ""
        self.method_list: List[str] = []
        self.field_list: List[str] = []
        # Constant pool
        self.constants: List[Tuple[str, int]] = []
        # Method code (instructions)
        self.code = []  # Will expand to code per method
        # For each method defined here, we want its
        # name, its slot# (position in vtable), and
        # its code.
        self.method_code: List[dict] = []
        # Things to be resolved
        # Labels resolve to addresses within the code
        # of a method.
        # label -> address
        self.labels: Dict[str, int] = {}
        # address -> unresolved label
        self.label_patch: Dict[int, str] = {}
        # Later: method slots, class references

    def declare_class(self, name: str, super_name: str):
        self.class_name = name
        self.super_name = super_name
        super_module = import_module(super_name)
        # Methods and field list are initially those
        # we inherit, but may be extended elsewhere
        # in the assembly code
        self.method_list = super_module.methods
        self.n_inherited = len(super_module.methods)
        self.field_list = super_module.fields

    def begin_method(self, method_name: str):
        if method_name not in self.method_list:
            self.method_list.append(method_name)
        method_slot = self.method_list.index(method_name)
        # Initialize code block
        self.code = []  # We will append instructions to this list
        self.method_code.append({"name": method_name, "slot": method_slot,
                                 "code": self.code })

    def resolve(self):
        """Patch up references to code labels"""
        for (patch_loc, patch_label) in self.label_patch.items():
            try:
                self.code[patch_loc] = self.labels[patch_label]
            except IndexError:
                log.error(f"Unresolved label '{patch_label}'")


    def add_int_constant(self, literal: str) -> int:
        literal_index = len(self.int_constants)
        self.int_constants.append(literal)
        return literal_index

    def add_str_constant(self, literal: str) -> int:
        literal_index = len(self.str_constants)
        self.str_constants.append(literal)
        return literal_index

    def add_instruction(self, instr: Instruction):
        if instr.label:
            # Address of next instruction
            self.labels[instr.label] = len(self.code)
        self.code.append(instr.operation.code)
        if instr.operand:
            # Many operands require interpretation
            # that depends on the operation
            op_value = self.encode_operand(instr)
            self.code.append(op_value)

    def encode_operand(self, instr: Instruction):
        """Each operand type is idiosyncratic"""
        op: str = instr.operation.name
        operand: str = instr.operand
        if op == "const":
            # We have integer constants and string
            # constants.  They reside in the same
            # runtime table, but are initialized
            # by different vm operations.  We need to
            # keep them together in one list to give them
            # consistent internal numbers that can be remapped
            # in the loader.
            if re.match("[0-9]+", operand):
                kind = "i"
            elif re.match('["][^"]*["]', operand):
                kind = "s"
                operand = operand.strip("\"").\
                    encode("utf-8").decode("unicode_escape")
            else:
                log.error(f"Could not type operand '{operand}'")
            self.constants.append({"kind": kind, "value": operand})
            return len(self.constants) - 1
        if op == "call":
            slot = resolve_call(operand)
            return slot
        if op in ["return", "load", "store"]:
            # These operations have integer operands that should be
            # resolved by the compiler
            return int(operand)
        # Match should be exhaustive
        log.error(f"Unhandled operand type for {instr}")

    def json(self) -> str:
        struct = {
            "class_name": self.class_name,
            "super": self.super_name,
            "methods": self.method_list,
            "fields": self.field_list,
            # It's just simpler to count fields and methods
            # in the assembler than in the loader, so we'll add
            # some redundant information here.
            "n_fields": len(self.field_list),
            "n_methods": len(self.method_list),
            "n_inherited": self.n_inherited,
            "constants": self.constants,
            "code": self.method_code
        }
        return json.dumps(struct, indent=4)

    def __str__(self) -> str:
        return self.json()

# ----------------
#  Assembly code is line-oriented and can be parsed
#  with regular expressions.  We strip away comments
#  and then scan for label, operation, and operand fields.
#

def strip_comments(line: str) -> str:
    return line.split("#")[0].strip()
    # Note comment lines will now be empty,
    # as will blank lines.


# Instruction pattern (single operation of vm)
INSTR_PAT = re.compile(r"""
    ((?P<label> \w+):)?   # Optional label
    \s*
    (?P<opname> \w+)      # Operation name is required
    (\s+ (?P<operand>     # Operands are integers, quoted strings, or names
         [0-9]+           # Integers are strings of digits
       |
         ["](             # String begins and ends with quote 
           ([\\].)  |           # Anything escaped
           [^"\\]               # Anything but a quote or escape
         )*["]
       |
         (\w|[:])+         # name, which may be part:part
         ))?               # Operand is optional
   \s*
    """, re.VERBOSE)

# Directive:  Name this class
CLASS_DECL_PAT = re.compile(r"""
[.]class \s+ 
(?P<class_name> \w+ )[:](?P<super_name> \w+)
\s*
""", re.VERBOSE)

# Directive: Name this method
#   (Starts a new method entry in the code object)
METHOD_DECL_PAT = re.compile(r"""
[.]method \s+
(?P<method_name> [$]?\w+ )
\s*
""", re.VERBOSE)


def translate(lines: List[str]) -> ObjectCode:
    code = ObjectCode()
    for line in lines:
        line = strip_comments(line)
        if not line:
            continue
        match = CLASS_DECL_PAT.match(line)
        if match:
            class_name = match.groupdict()["class_name"]
            superclass_name = match.groupdict()["super_name"]
            code.declare_class(class_name, superclass_name)
            continue
        match = METHOD_DECL_PAT.match(line)
        if match:
            method_name = match.groupdict()["method_name"]
            code.begin_method(method_name)
            continue
        match = INSTR_PAT.match(line)
        if not match:
            log.error(f"NO MATCH on '{line}'")
            continue
        parts = match.groupdict()
        label = parts["label"]
        opname = parts["opname"]
        operand = parts["operand"]
        instruction = Instruction(label, INSTRS[opname], operand)
        code.add_instruction(instruction)
    code.resolve()
    return code

def main():
    """Assemble one file into object code in json format"""
    args = cli()
    instructions = InstructionSet("opdefs.txt")
    source = [line for line in args.source]
    # lines = read_source("unit_tests/sample_2.asm")
    objcode = translate(source)
    print(objcode.json(), file=args.target)


if __name__ == "__main__":
    main()
