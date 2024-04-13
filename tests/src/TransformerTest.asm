.class TransformerTest:Obj
.method $constructor
    enter
    const 5
    const 4
    call Int:minus
    const 3
    const 2
    call Int:plus
    call Int:mult
    call Int:print
    const "\n"
    call String:print
    pop
    return 0