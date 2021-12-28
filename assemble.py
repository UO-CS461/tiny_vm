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
from typing import Dict, List,  Optional

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


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
        self.methods: Dict[str, int] = {}
        for slot, name in enumerate(self.json["methods"]):
            self.methods[name] = slot
        self.fields: Dict[str, int] = {}
        for slot, name in enumerate(self.json["fields"]):
            self.fields[name] = slot

    def method_slot(self, name: str) -> int:
        return self.methods[name]

    def field_slot(self, name: str) -> int:
        return self.fields[name]

IMPORT_PATH = Path("unit_tests")  # FIXME: Temporary hack
IMPORTS: Dict[str, ImportedModule] = {}
def import_module(module: str) -> ImportedModule:
    if module not in IMPORTS:
        path = IMPORT_PATH.joinpath(module).with_suffix(".json")
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
        # Constant pool
        self.int_constants = []
        self.str_constants = []
        # Method code (instructions)
        self.code = []  # Will expand to code per method
        # Things to be resolved
        # Labels resolve to addresses within the code
        # of a method.
        # label -> address
        self.labels: Dict[str, int] = {}
        # address -> unresolved label
        self.label_patch: Dict[int, str] = {}
        # Later: method slots, class references

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
            # by different vm operations.
            if re.match("[0-9]+", operand):
                if operand in self.int_constants:
                    return self.int_constants.index(operand)
                else:
                    self.int_constants.append(operand)
                    return len(self.int_constants) - 1
            else:
                if operand in self.str_constants:
                    return self.str_constants.index(operand)
                else:
                    return len(self.str_constants) - 1
        if op == "call":
            slot = resolve_call(operand)
            return slot
        # Match should be exhaustive
        log.error(f"Unhandled operand type for {instr}")

    def json(self) -> str:
        struct = {
            "const_ints": self.int_constants,
            "const_strings": self.str_constants,
            "instructions": self.code
        }
        return json.dumps(struct)

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
    (\s+ (?P<operand> (\w|:)+))?
    """, re.VERBOSE)


def translate(lines: List[str]) -> ObjectCode:
    code = ObjectCode()
    for line in lines:
        line = strip_comments(line)
        if not line:
            continue
        match = INSTR_PAT.match(line)
        if not match:
            log.error(f"NO MATCH on '{line}'", file=sys.stderr)
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
    # lines = read_source("unit_tests/sample.asm")
    objcode = translate(source)
    print(objcode.json(), file=args.target)


if __name__ == "__main__":
    main()
