.class TestBuiltins:Obj
.method $constructor
    .local n,m
    enter
    
    const 5
    store n
    const 2
    store m

    const "\nchecking mult... 5*2 -> 10\n"
    call String:print
    pop

    load m
    load n
    call Int:mult
    call Int:print

    const "\nchecking div... 5/2 -> 2\n" 
    call String:print
    pop

    load m
    load n
    call Int:div
    call Int:print

    const "\nchecking minus... 5-2 -> 3\n"
    call String:print
    pop

    load m
    load n
    call Int:minus
    call Int:print
    
    const "\ndone \n\n"
    call String:print
    pop

    return 0


