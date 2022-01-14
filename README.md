# tiny_calculator
Thomas Renn

# How to run
```
$ python3 translator.py <soruce-file> > sample.asm
```
The source-file is a file containing arithmetic expressions.
There is an example file unit_tests/exps_hard.txt that contains some
difficult expressions. The program translator prints to standard
input, so the output needs to be redirected to a file to run with
the assembler.


```
$ python3 assembler.py sample.asm sample.json
```

Once the tiny_vm executable has been built, it can be run
and outputs the answer to the expressions specified in the 
source-file.

```
$ ./tiny_vm
```