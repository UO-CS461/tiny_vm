"""Build table mapping integer byte codes to function pointers.
Machine operations, their names, and the number of operands
for each are given in opdefs.txt.
"""
import argparse
import datetime

# Fixed code at beginning of generated file
import sys
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

LB = "{"
RB = "}"

PROLOGUE = f"""
/**
 * GENERATED CODE, DO NOT EDIT
 * Generated {datetime.datetime.now()} by build_bytecode_table.py
 * 
 * Integer encoding of VM operations ---
 * Map those integer encodings to function pointers (for executing)
 * and to strings (for debugging and assembling).
 */
 
#include "vm_code_table.h"
op_tbl_entry vm_op_bytecodes[] = {LB}
"""

# Fixed code at end of generated file
CODA = """
    { 0, 0, 0}  // SENTRY
};
"""

def cli() -> object:
    """Command line interface"""
    parser = argparse.ArgumentParser(prog=__name__,
                     description="Build bytecode table")
    parser.add_argument("infile", type=argparse.FileType("r"),
                        nargs="?", default=sys.stdin,
                        help="Textual table of operations")
    parser.add_argument("outfile", type=argparse.FileType("w"),
                        nargs="?", default=sys.stdout,
                        help="Put C header file here")
    args = parser.parse_args()
    return args


def main():
    log.info("Bytecode table generation")
    args = cli()
    print(PROLOGUE, file=args.outfile)
    next_byte_code = 0;
    for line in args.infile:
        line = line.strip()
        # Strip off comments
        parts = line.split("#")
        comment = ""
        if len(parts) > 1:
            comment = "#".join(parts[1:])
        line = parts[0].strip()
        # Is there anything left?
        if len(line) == 0:
            continue
        parts = line.split(",")
        assert len(parts) == 3, f"Couldn't parse {line}"
        name, func, inlines = parts
        print(f'\t {LB} "{name}", {func}, {inlines} {RB}, //{next_byte_code} {comment}',
              file=args.outfile)
        next_byte_code += 1
    print(CODA, file=args.outfile)
    log.info("Finished bytecode table generation")

if __name__ == "__main__":
    main()





