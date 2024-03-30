# Tiny VM assembly language and instruction set

The Tiny Virtual Machine is an interpreter engine with the following
characteristics:

- It is _pedagogical_. The Tiny VM is designed to illustrate an 
  interpretation mechanism.  It is designed to be understandable, as 
  well as being useful in student projects. 
- It is designed for implementing an object-oriented language with 
  implementation inheritance (vtables).
- In order to illustrate realistic interpretation mechanisms, it 
  uses a _threaded code_ approach, in which VM instructions are 
  represented as pointers to C functions that implement those 
  instructions. 
- It is stack oriented, because generating stack oriented expression 
  evaluation is simpler than performing register allocation.
- It exposes a stack of activation records, including an explicit 
  frame pointer and stack pointer, more like the runtime 
  organization of native code than like a typical VM. The evaluation 
  stack is on the stack of activation records, not separate.  In 
  this way it is quite different than the JVM, the Python virtual 
  machine, etc. 

## Invoking the assembler

The assembler is a Python script, `assemble.py`.  It is invoked as 
follows to translate an assembly language module `source.asm` into
object code stored in `object.json`:

```cli 
python3 asssemble.py source.asm  object.json
```

If no object code file path is given in the command, object code (in 
JSON format) will be emitted to standard output.

In addition to the source file, the assembler may access object code 
of other modules.

## The Assembly Language

Lines in the assembly language file may be

- Comments or blank lines
- Class declarations (normally followed by methods and fields)
- Field declarations
- Method declarations
- Argument declarations
- Instructions

The following example (part of `unit_tests/Counter.asm`) includes 
each of those kinds of line: 

```
.# Counter: Wraps an integer, can be incremented
.class Counter:Obj
.field i
# Constructor takes a single argument, an
# Int object
.method $constructor
.args   n
    enter
    load n
    load $
    store_field $:i
    load $  # Return the initialized object
    return 1

.method inc
    enter
    const 1
    load $
    load_field $:i
    call Int:plus
    load $
    store_field $:i
    const nothing
    return 0
```

Declarations of various kinds (classes, fields, methods, arguments) 
are recognizable by the leading dot ('`.`'), e.g., `.class`. 
Line-ending comments are introduced by '`#`' or '`;`'.  Other lines 
may be prefixed by a label like '`lab: `' (not illustrated here) and 
then consist of a an instruction (like `load` or `const`) and then 
zero or one operands (like `Int:plus` or `1`). 

### The Declarations

A class is introduced by a `.class` declaration, followed by the 
name of the class.  Class names have two parts, like `Counter:Obj`. 
which declares that we are creating a class _Counter_ which is a 
subclass of class _Obj_.  To implement inheritance, the assembler 
will find and load the object file for class `Obj`, so subclass 
`Counter` will have the fields and methods of `Obj`, which it may 
override with its own method declarations. 

A class declaration may be followed by one or more `.field` 
declarations, which allocate instance variables in objects of the 
class.  These are in addition to any fields inherited from the 
superclass (e.g., fields that `Counter` might inherit from `Obj`).  
Fields may not be overridden. 

A method declaration has the form `.method name` where `name` is the 
name of the method.  It may override a method in the superclass, or 
it may be an additional method that is not in the superclass. 

Methods must be declared before they can be referenced.  To enable 
recursion, a method may be declared "forward", to be fully defined 
later in the source code, like this: 

``` 
.method   name   forward
```

Except "forward" declaration, method declaration is normally followed 
by a method _definition_ as a sequence of 
instructions.   Methods `$constructor` and `inc` in the example 
above are definitions which consist of the method declaration 
followed by a method body. 

Some instructions have no operands, like `pop`.  
Other instructions, like `const` and `call`, have a single operand. 
Operands are of three kinds: 

- An integer constant (in decimal notation)
- A quoted string  (only for the `const` instruction)
- A name, which may refer to a class, method, field, local variable, 
  or label.

Special names include `$` for the "self" object. 

## The instruction set

The tiny virtual machine has, as implied by its name, a small 
instruction set.  This instruction set does _not_ include 
implementation of operations like multiplying two integers; those 
operations are instead implemented as built-in methods, and invoked 
through method calls. They are implemented in `builtins.c`.  Most of 
the instructions of the tiny virtual 
machine manage creation of objects and method call and return. 

The instruction and their names are declared in `opdefs.txt` and 
implemented in `vm_ops.c`. 

| Instruction | Operands | C function        | Description                                                          |
|-------------|----------|-------------------|----------------------------------------------------------------------|
| halt        | 0        | vm_op_halt        | Stops the processor.                                                 |
| const       | 1        | vm_op_const       | Push constant  (operand is constant to push)                         |
| call        | 1        | vm_op_methodcall  | Call an interpreted method                                           |
| call_native | 1        | vm_op_call_native | Trampoline to native method (cannot be written in assembly language) |
| enter       | 0        | vm_op_enter       | Prologue of called method                                            |
| return      | 1        | vm_op_return      | Return from method, reclaiming locals                                |
| new         | 1        | vm_op_new         | Allocate a new object instance                                       |
| pop         | 0        | vm_op_pop         | Discard top of stack                                                 |
| alloc       | 1        | vm_op_alloc       | Allocate stack space for locals                                      |
| load        | 1        | vm_op_load        | Load (push) a local variable onto stack                              |
| store       | 1        | vm_op_store       | Store (pop) top of stack to local variable                           |
| load_field  | 1        | vm_op_load_field  | Load from object field                                               |
| store_field | 1        | vm_op_store_field | Store to object field                                                |
| roll        | 1        | vm_op_roll        | rotate top of stack  [obj arg1 ... argn] -> [arg1 ... argn obj]      |
| jump        | 1        | vm_op_jump        | Unconditional relative jump                                          |
| jump_if     | 1        | vm_op_jump_if,1   | Conditional relative jump, if true                                   |
| jump_ifnot  | 1        | vm_op_jump_ifnot  | Conditional relative jump, if false                                  |
| is_instance | 1        | vm_op_is_instance | Test membership in class (for typecase)                              |                                                                 |

### Linkage: Method call and return 

When we call method _m_ of object _o_ with an instruction like 

```
  call   T:m
```

_o_ is called the "receiver 
object", and must be a subtype (subclass) of T. T is the
_static type_ of _o_, but _o_ may be a subtype (subclass).  
Within _m_, _o_ will be the _self_ object. 

Method arguments, including the receiver object,
are passed on the stack of activation records.  For 
example, the following sequence pushes a reference to a string 
constant onto the stack and then calls the print method of class 
`String` to print it: 

``` 
    const "Example"
    call String:print
```

Note that the method called must be _compatible_ with the receiver
object, but might not be the same. The type given in 
the operand is the _static type_ of the object, but the method 
actually called is taken from the _dynamic type_ of the object.
This is called _dynamic dispatch_, which is implemented using a 
_vtable_ or _virtual function table_. 

Supposing instead 
of the literal string "Example", we had pushed an object of some 
subclass `SpecialString` with its own `print` method.  The `call` 
instruction could still reference `String:print`, but the method 
actually called would be `SpecialString:print`. 

The _receiver object_ is always the _top_ argument on the
stack. Sometimes this will require using the `roll` instruction to
move it from lower in the stack. 

The called method must declare arguments, except the `self` argument 
which is implicit.  For example, the constructor of class `Counter` 
takes one additional argument, an integer, which it stores into 
field `i`:

```
.class Counter:Obj
.field i
# Constructor takes a single argument, an
# Int object
.method $constructor
.args   n
    enter
    load n      ; Pushes a copy of argument n
    load $      ; Pushes a reference to the self object
    store_field $:i    ; Pops value of n and stores it in field i
    load $             ; Returns the initialized self object
    return 1    ;  Pops one argument before returning
```

### Native methods

It can't be turtles all the way down. 
In addition to the operations of the tiny vm itself, the built-in 
classes (Int, String, etc) have some methods that cannot be 
implemented through sequences of other virtual machine instructions. 
These are instead implemented in C, which is the "native code" of 
the tiny virtual machine.  

While `call_native` is an operation code of the virtual machine, it 
is impossible to write its operand, a reference to a C function, in 
assembly language.   The _trampoline_ code which bridges from 
interpreted code to native code must instead be specified in a C 
struct and compiled by a C compiler which has access to the address 
of the implementation function.

Consider the method `Equals` of class `Int`.  The `Int` class wraps 
a native C integer, so the `Equals` method must access that native C 
integer and use the C equality to compare it to the native C integer 
wrapped in another object.  The `Int:Equals` method is implemented 
as a sequence of tiny vm operations that includes a `call_native` 
instruction to the C implementation.  The sequence of vm 
instructions is held in the following C struct in `builtins.c`: 

```c
vm_Word method_Int_equals[] = {
        {.instr = vm_op_enter},
        {.instr = vm_op_call_native},
        {.native = native_Int_equals},
        {.instr = vm_op_return},
        {.intval = 1}
};
```

The `native` element of the `vm_Word` union is a reference to a C 
function, in this case `native_Int_equals`.  T

```c
obj_ref native_Int_equals(void ) {
    obj_ref this = vm_fp->obj;
    assert_is_type(this, the_class_Int);
    obj_Int this_int = (obj_Int) this;
    obj_ref other = (vm_fp - 1)->obj;
    assert_is_type(other, the_class_Int);
    obj_Int other_int = (obj_Int) other;
    log_debug("Comparing integer values for equality: %d == %d",
           this_int->value, other_int->value);
    if (this_int->value == other_int->value) {
        return lit_true;
    } else {
        return lit_false;
    }
}
```

Note that `native_Int_equals` takes no arguments, but is aware of 
the layout of the activation record including the receiver object
`this` at the top of the stack (the frame pointer `fp`) and the 
other operand just below it.

FIXME: why is it at fp and not at sp? Why does it leave them on the 
stack? 
