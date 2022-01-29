# tiny_vm
A tiny virtual machine interpreter for Quack programs

## Work in progress

Instructions


For Nano-quack:

build 
```
cmake -S . -B ./build
cd build
make
cd ..
```

generate ASM:
```
python quack_parser.py -i quacksample.qck -o test.asm
```
generate object code
``` 
python assemble.py test.asm OBJ/Main.json
```
execute
```
./bin/tiny_vm -L OBJ Main
```
