#!/bin/bash

name=$2
if [ "$name" == "" ]; then
    name="Main"
fi

python3 translator.py "$1" "${name}.asm"
python3 assemble.py "${name}.asm" "OBJ/${name}.json"