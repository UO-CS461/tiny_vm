"""Simple test script for Ori (tiny vm) asm files.
(Extend later to work with Quack compilation)

FIXME: There must be better ways to handle file dependencies
"""
import subprocess
import pathlib
import shutil
import filecmp
import csv

import logging
import sys

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# The following might differ from system to system,
# and should be configurable
PY = "python3"
ROOT = ".."
ASM = f"{ROOT}/assemble.py"
VM = f"{ROOT}/bin/tiny_vm"
BUILTINS = ["Bool.json", "Int.json", "Nothing.json", "Obj.json", "String.json"]
ASMREQS = ["asm.conf", "opdefs.txt"]

def install_prereqs():
    """Copy pre-requisite files.
    It would be cleaner to do this in Cmake, probably.
    """
    for objfile in BUILTINS:
        origin = pathlib.Path("../OBJ/" + objfile)
        copied = pathlib.Path("./OBJ/" + objfile)
        log.debug(f"Copying {origin} to {copied}")
        shutil.copyfile(origin, copied)
    for asmreq in ASMREQS:
        origin = pathlib.Path("../" + asmreq)
        copied = pathlib.Path("./" + asmreq)
        log.debug(f"Copying {origin} to {copied}")
        shutil.copyfile(origin, copied)

def assemble(class_name: str) -> bool:
    """Translate src/Class.asm to OBJ/Class.json.
    Separated because some classes (e.g., Counter) cannot
    be run as main programs.  (Main program class constructors
    cannot have arguments.)
    """
    src = pathlib.Path("./src/" + class_name + ".asm")
    obj = pathlib.Path("./OBJ/" + class_name + ".json")
    try:
        proc = subprocess.run([PY, ASM, src, obj], text=True)
        proc.check_returncode() # May throw CalledProcessError
    except subprocess.CalledProcessError:
        log.warning(f"Assembler crashed on {src}")
        return False
    return True


def test_class(class_name: str) -> bool:
    """Assemble, run, and check a single test case
    for a class C, in src/C.asm, with expected output
    in expect/C_stdout.txt.  Returns True iff test case
    has expected outcome.
    """
    ok = True
    observed_stdout = pathlib.Path("out/" + class_name + "_stdout.txt")
    observed_stderr = pathlib.Path("out/" + class_name + "_stderr.txt")
    expect_stdout = pathlib.Path("expect/" + class_name + "_stdout.txt")
    if not assemble(class_name):
        return False
    try:
        std_out = open(observed_stdout, "w")
        std_err = open(observed_stderr, "w")
        proc = subprocess.run([VM, class_name], text=True,
                              stdout=std_out, stderr=std_err)
        proc.check_returncode() # May throw CalledProcessError
        if filecmp.cmp(observed_stdout, expect_stdout):
            log.info(f"OK: {class_name} produced expected output")
        else:
            log.info(f"{class_name} output did not match expectation")
            ok = False
    except subprocess.CalledProcessError:
        log.warning(f"Crashed: {proc.args}")
        ok = False
    return ok


def main():
    """Stub"""
    install_prereqs()
    with open("src/TESTS.csv") as cases:
        case_reader = csv.DictReader(cases)
        for case in case_reader:
            class_name = case["Class"]
            action = case["Action"]
            if action == "assemble":
                # Assemble but do not execute
                log.info(f"Class '{class_name} -- assemble only")
                ok = assemble(class_name)
            elif action == "run":
                log.info(f"Class '{class_name} -- assemble and run")
                ok = test_class(class_name)
            else:
                log.error(f"Unrecognized action '{action}' for class {class_name}")
            if not ok:
                print(f"*** Failed test case: {action} {class_name}", file=sys.stderr)
    # FIXME: Add a check for omitted source files
    print("Testing complete")


if __name__ == "__main__":
    main()
