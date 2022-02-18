# Will the loader recursively load the superclass of the superclass?
# We need two levels of derived class to find out.  This is level 2
#
.class RecursiveLoadSuperDuper:RecursiveLoadSuper
.method yell forward
.method $constructor
    enter
    const "This is RecursiveLoadSuperDuper's constructor\n"
    call String:print
    load $
    call $:yell
    return 0

.method yell
    enter
    load $
    call $:shout
    return 0
