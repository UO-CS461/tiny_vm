# tiny_vm
A tiny virtual machine interpreter for Quack programs

## How to use

To compile and run a Quack program, run the following sequence of commands:
```
python translator.py <source_file> out.asm
python assemble.py out.asm sample.json
./tiny_vm
```

## Work in progress

This is intended to become the core of an interpreter for the Winter 2022
offering of CIS 461/561 compiler construction course at University of Oregon, 
if I can ready it in time. 

