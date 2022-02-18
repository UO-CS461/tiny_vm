# Will the loader recursively load the superclass of the superclass?
# We need two levels of derived class to find out.  This is level 1
#
.class RecursiveLoadSuper:Obj
.method $constructor
    enter
    const "This is RecursiveLoadSuper's constructor\n"
    call String:print
    load $
    return 0

.method shout
    enter
    const "This is RecursiveLoadSuper's shout method\n"
    call String:print
    # Leave 'none' on the stack
    return 0
