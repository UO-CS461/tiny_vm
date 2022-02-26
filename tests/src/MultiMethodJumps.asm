# Bug fix check --- labels and jumps in multiple methods
# should not interfere with each other.
#
.class MultiMethodJumps:Obj
.method foo forward
.method bar forward

.method $constructor
.local x,y
    enter
    const 5
    store x
    const 6
    store y
    load x
    load y
    call Int:equals
    jump_if same
    const "Five is not six.\n"
    call String:print
    pop
    jump out
same:
    const "Five and size are actually the same\n"
        call String:print
        pop
out:
    # This may not be legal in Quack ...
    load $
    call $:foo
    return 0

.method foo
    enter
    const 42
    const 42
    call Int:equals
    jump_if  same2
    const "42 is not 42, that is weird\n"
    call String:print
    pop
    jump out2
same2:
    const "42 is 42.  That is reassuring.\n"
    call String:print
    pop
out2:
    load $
    call $:bar
    return 0

.method bar
    # Reuse some labels here ... ok?
       const 84
       const 84
       call Int:equals
       jump_if  same2
       const "84 is not 84, that is weird\n"
       call String:print
       pop
       jump out2
   same2:
       const "84 is 84.  That is reassuring.\n"
       call String:print
       pop
   out2:
       const nothing
       return 0
