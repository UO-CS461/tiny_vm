.class Mod:Obj
.field modulus
.method mod forward
.method printModulus forward
.method $constructor
.args modulus
    enter
    load modulus
    load $
    store_field $:modulus
    load $
    return 1
.method mod
.args x
.local y
    enter
    load $
    load_field $:modulus
    store y
    jump whilecond_1
whileloop_1:
    load y
    load x
    call Int:minus
    store x
whilecond_1:
    load y
    load x
    call Int:atleast
    jump_if whileloop_1
whileend_1:
    jump whilecond_2
whileloop_2:
    load y
    load x
    call Int:plus
    store x
whilecond_2:
    const 0
    load x
    call Int:less
    jump_if whileloop_2
whileend_2:
    load x
    return 1
.method printModulus
    enter
    load $
    load_field $:modulus
    call Int:print
    pop
    const none
    return 0
