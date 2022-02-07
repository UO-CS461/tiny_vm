.class Sample:Obj
.method $constructor
.local yes,no
    const true
    call Bool:print
    pop
    const "\n"
    call String:print
    pop
    const false
    call Bool:string
    call String:print
    pop
    const "\n"
    call String:print
    pop
    const nothing
    return 0
