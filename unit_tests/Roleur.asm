# A simple unit test for the new 'roll n' operation
# Expected output 41 42 43 44
.class Roleur:Obj
.method $constructor
    const 44
    const 41
    const 43
    const 42
    roll 2
    call Int:print
    pop
    call Int:print
    pop
    call Int:print
    pop
    call Int:print
    pop
    const 0
    return 0
