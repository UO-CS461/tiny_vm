.class ModTest:Obj
.method $constructor
.local m,modObj,i,x
    enter
    const 7
    store m
    load m
    new Mod
    call Mod:$constructor
    store modObj
    const 1
    store i
    jump whilecond_3
whileloop_3:
    load i
    load modObj
    call Mod:mod
    store x
    load i
    call Int:print
    pop
    const " mod "
    call String:print
    pop
    load m
    call Int:print
    pop
    const " = "
    call String:print
    pop
    load x
    call Int:print
    pop
    const "\n"
    call String:print
    pop
    const 1
    load i
    call Int:plus
    store i
whilecond_3:
    const 14
    load i
    call Int:less
    jump_if whileloop_3
whileend_3:
    load $
    return 0
