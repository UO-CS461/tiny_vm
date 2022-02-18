# Test for "is_instance" operation
.class IsADuck:Obj
.field box
.method $constructor
    enter
    const "Constructing a Duck\n"
    call String:print
    pop
    const "Quack quack\n"
    load $
    store_field $:box
    load $
    return 0

.method string
    enter
    load $
    load_field $:box
    return 0

.method is_it
.args   x
    enter
    const "Checking my duck\n"
    call String:print
    pop
    load x
    is_instance $
    return 1
