# Class to use NewThis
.class UseThis:Obj
.method $constructor
    enter
    const "\n*** Use This ***\n"
    call String:print
    pop
    const 42
    new NewThis
    call NewThis:$constructor
    call NewThis:next
    load_field NewThis:x
    call Int:print
    pop
    const "\n *** end of use this ***\n"
    call Int:print
    pop
    load $
    return 0
