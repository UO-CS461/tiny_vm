#  Allocating a new object of the current class
#  Class wraps a single Int
.class NewThis:Obj
.field x
.method $constructor
.args  initial
    enter
    load initial
    load $
    store_field $:x
    const "Creating a NewThis object, value "
    call String:print
    pop
    load $
    load_field $:x
    call Int:print
    pop
    const "\n"
    call String:print
    pop
    load $
    return 1

.method next
    enter
    const 1
    load $
    load_field $:x
    call Int:plus
    new $
    call $:$constructor
    return 0
