# Simple test for the Counter class
.class TestCounter:Obj

.method $constructor
.local counter
    enter
    const 5
    new Counter
    call Counter:$constructor
    store counter

    const "Expecting '5' on next line\n"
    call String:print
    pop
    load counter
    call Counter:print
    pop
    # Increment should bump it to 6
    load counter
    call Counter:inc
    pop
    const "\nExpecting '6' on next line\n"
    call String:print
    pop
    load counter
    call Counter:print
    pop

    const "Counter is seven?\n"
    call String:print
    pop
    const 7
    load counter
    call Counter:check
    call Obj:print
    pop

    const "\nCounter is six?\n"
    call String:print
    pop
    const 6
    load counter
    call Counter:check
    call Obj:print
    pop

    const "\nEnd of test\n"
    call String:print
    pop

    load $
    return 0
