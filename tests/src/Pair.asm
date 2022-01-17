# Minimal example that creates and uses a class with
# two fields (both Int), with an internal method
#
.class Pair:Obj
.field x
.field y

.method $constructor
    enter
    const 2
    load $  # The "this" object
    store_field $:x
    const 4
    load $
    store_field $:y
    const "Next line should be 2, the 'x' field of (2, 4)\n"
    call String:print
    pop
    load $
    load_field $:x
    call Int:print
    const "\n Next line should be 2, 4\n"
    call String:print
    pop
    load $
    call $:print
    pop
    const "\n"
    call String:print
    return 0

# It would be better to inherit "print" and redefine "string",
# but string doesn't have concatenation yet.
.method print
    enter
    load $
    load_field $:x
    call Int:print
    pop
    const ", "
    call String:print
    pop
    load $
    load_field $:y
    call Int:print
    return 0

.method bumpy   # Add an Int to the y field
.args    increment
    load increment
    load $
    load_field    $:y
    call Int:plus
    load $
    store_field  $:y
    const nothing
    return 1
