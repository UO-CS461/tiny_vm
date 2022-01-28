# A simple unit test for the new 'roll n' operation
# Expected output 41 42 43 44
.class Roleur:Obj
.method $constructor
    const 44
    const 41
    const 43
    const 42
    roll 2
    # The "roll 2" should move 41 into the top position
    # and leave 42, 43, 44 above it

    const "Expect 41: "
    call String:print
    pop
    call Int:print
    pop

    const "\nExpect 42: "
    call String:print
    pop
    call Int:print
    pop

    const "\nExpect 43: "
    call String:print
    pop
    call Int:print
    pop

    const "\nExpect 44: "
    call String:print
    pop
    call Int:print
    pop

    const "\n"
    call String:print
    pop
    const nothing
    return 0
