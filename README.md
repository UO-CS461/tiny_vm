# tiny_calculator
Thomas Renn

# How to run
```
$ python3 translator.py <soruce-file> > Main.asm
```
The source-file is a file containing assignment expressions and method calls.
There is an example file unit_tests/tests.txt that contains some
examples. The program translator prints to standard
input, so the output needs to be redirected to a file to run with
the assembler.


```
$ python3 assemble.py Main.asm OBJ/Main.json
```

Once the tiny_vm executable has been built, the nano 
quack program can be run


```
$ ./bin/tiny_vm -L OBJ Main
```
