#!/bin/bash
if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "Error: Input file '$1' not found"
    exit 1
fi

python3 transformer.py -f "$1"

if [ $? -ne 0 ]; then
    echo "Error: transformer.py failed"
    exit 1
fi

python3 assemble.py Main.asm ./bin/OBJ/Main.json
