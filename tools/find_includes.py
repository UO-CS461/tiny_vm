"""
Scan #include references in C/C++ code
"""

import argparse
import pathlib
import logging
import re
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

C_SUFFIXES = ["h", "c"]  # FIXME: Need comprehensive suffix list

def cli() -> object:
    """Command line arguments"""
    parser = argparse.ArgumentParser("Scan C/C++ for #include relation")
    parser.add_argument("dirs", help="Directories to scan; defaults to .",
                        nargs="?", default=["."])
    args = parser.parse_args()
    return args

def scan_includes(p: pathlib.Path):
    """Emits an "f -> g" line for each #include "g"  """
    f_name = p.name
    with open(p, "r") as f:
        #print()
        for line in f:
            matched = re.match(r"""#include\s*["](?P<included>.*)["].*""",
                               line)
            if matched:
                log.debug(f"Matched line '{line.strip()}'")
                included = matched.groupdict()["included"]
                log.debug(f"Included '{included}'")
                print(f"{f_name}\t->\t{included}")


def main():
    print("digraph depends {")
    args = cli()
    for d in args.dirs:
        p = pathlib.Path(d)
        log.debug(f"Scanning directory {p}")
        for f in p.iterdir():
            log.debug(f"Considering file {f}")
            suffix = f.name.split(".")[-1]
            if suffix in C_SUFFIXES:
                log.debug(f"{f.name} appears to be a C source file")
                scan_includes(f)
    print("}")

if __name__ == "__main__":
    main()









