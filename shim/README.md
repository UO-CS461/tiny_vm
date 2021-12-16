# Shim code (not in use)

OBSOLETE

These built-in classes have been used for linking with generated C code.
They provide strongly-typed methods in the classes, which can be useful
for debugging the code generator.  Their built-in methods are written
in C.  

We are taking a somewhat different tack for the VM byte code interpreter,
in which a built-in method is interpreted code (a sequence of byte-code
instructions) and native code is invoked by a special VM instruction.  
