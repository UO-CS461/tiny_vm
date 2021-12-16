"""Build table mapping integer byte codes to function pointers.
Machine operations, their names, and the number of operands
for each are given in opdefs.txt.
"""
import argparse

# Fixed code at beginning of generated file
import sys

PROLOGUE = """
/**
 * GENERATED CODE, DO NOT EDIT
 * 
 * Integer encoding of VM operations ---
 * Map those integer encodings to function pointers (for executing)
 * and to strings (for debugging and assembling).
 */


op_tbl_entry vm_op_bytecodes[] = {
"""

# Fixed code at end of generated file
CODA = """
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
    args = cli()
    print(PROLOGUE, file=args.outfile);
    next_byte_code = 0;
    for line in args.infile:
        # Strip off comments
        line = line.split("#")[0]  # The part before "#"
        line = line.strip()
        # Is there anything left?
        if len(line) == 0:
            continue
        parts = line.split(",")
        assert len(parts) == 3, f"Couldn't parse {line}"
        name, func, inlines = parts
        LB = "{"
        RB = "}"
        print(f'\t {LB} "{name}", {func}, {inlines} {RB}, #{next_byte_code}',
              file=args.outfile)
        next_byte_code += 1
    print(CODA, file=args.outfile)

if __name__ == "__main__":
    main()





