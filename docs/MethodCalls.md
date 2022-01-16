# Method Calls in the tiny vm

The tiny virtual machine supports a dynamic dispatch method
that is closely modeled on dispatch in C++, Java, and other
commonly used programming languages.  It is like calling a 
"virtual function" in C++, or a method of a class (not interface)
in Java, and probably in several other programming languages. 

## Dynamic dispatch and class hierarchy

The *dynamic* part of *dynamic dispatch* is that the same 
call may invoke different methods through *overriding*. 
Suppose `x` is a variable of class `T`.  The value of 
`x` may be an object `o` of class `R`, where `R` is a subclass
of `T`.  `T` may have a method `m`, and `R` may override that 
method.  Then, when we call `x.m`, we will invoke `R.m` rather
than `T.m`.

Languages like C++ and Java achieve this dynamic dispatch through
a "virtual function table" mechanism. 

## "Virtual function" tables (vtables)

Each object contains a reference to a class descriptor structure.
The class descriptor contains a "vtable", which is an array holding
function pointers.  Each method supported by the class is represented
by one function pointer in the vtable. 

The key trick is that the vtable of a subclass must be aligned
with all the vtables of its ancestors in the class hierarchy. 
In the example above, let's suppose method `m` is a function pointer
in slot 2 of class `T`.  Method `m` of class `R` must then also 
be in slot 2 of class `R`, whether it is the same method (inherited)
or a different method (overriding).  We make the call by indexing
into the table, not knowing whether we are calling a method of 
class `T` or one of its descendants in the class hierarchy. 

![Vtables must align](img/vtable.png)

We can see this dispatch in the `methodcall` operation of 
the tiny vm, implemented by function `vm_op_methodcall`:

```c
extern void vm_op_methodcall(void) {
    int method_index = vm_fetch_next().intval;
    // New "this" will be receiver object
    vm_addr new_fp = vm_sp;
    // Save program counter for return
    vm_frame_push_word((vm_Word) {.code_addr = vm_pc});
    // Save caller's frame pointer
    vm_frame_push_word((vm_Word) {.frame_addr = vm_fp});
    vm_fp = new_fp;
    // Address of code for called method, found in the
    // class vtable.
    struct class_struct *clazz = (*vm_fp).obj->header.clazz;
    vm_addr method_addr = clazz->vtable[method_index];
    vm_pc = method_addr;
    return;
}
```

The crucial line is 

```c
    vm_addr method_addr = clazz->vtable[method_index];
```

which obtains the new program counter address (like a function pointer)
by indexing the vtable of the class of the receiver object.

## Variations

You might note that this simple dynamic dispatch scheme will not
work for everything.  It won't work for multiple inheritance
(too hard to line up the vtables with multiple superclasses), 
and similarly it won't work for Java interfaces.  In fact the 
Java virtual machine has two different method call operations, 
`invokevirtual` (use the vtable) and `invokeinterface` (use a 
separate hash table).  When the static type of a variable is 
an interface rather than a class, Java uses `invokeinterface`
(which is typically slightly slower). 

Python uses a `dict` structure rather than a `list`, which allows
for all sorts of wacky things like dynamically adding methods
to a class. 

There is another family of languages that use a different 
mechanism, called *delegation*.  In an OO langauge with delegation,
a class "knows" only about its own methods.  It may have a superclass, 
but it does not actually "inherit" methods from the superclass. 
Instead, when it receives a method call, it first checks its own
methods and then, if it does not have a corresponding method, it
"delegates" the call to its superclass.   Languages with a delegation
model tend to look a little different from languages with a
class hierarchy and inheritance. For example, some languages do
not distinguish between classes and objects at all --- an object
can inherit from (or rather, dispatch to) another object
(typically called a "prototype") rather than
a class.  The delegation model tends to create compact but slow
code. NewtonScript, the language shipped on an early hand-held
computer, used the delegation model because it can produce very compact
object code.  I do not know JavaScript well, but I believe JavaScript
also uses delegation.  

The Kotlin language (a successor to Java) has a mechanism called 
"delegation", but I don't believe it is the same mechanism
as delegation in NewtonScript, Self, and related delegation-based
object oriented languages. 
