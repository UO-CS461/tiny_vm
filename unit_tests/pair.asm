# Minimal example that creates and uses a class with
# two fields (both Int), with an internal method
#
.class Pair:Obj
.field x
.field y

.method $constructor
    enter
    load $  # The "this" object
    const 2
    store_field $:x
    load $
    const 4
    store_field $:y
    load $
    load_field $:x
    call Int:print
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
