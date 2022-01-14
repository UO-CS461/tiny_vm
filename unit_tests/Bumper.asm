# Unit test of modifying a field of an object.
# Class "Pair" has a method "bumpy" which should add
# an Int to the y field of a pair.  We want to call
# that method and the print method to see if we can
# call methods to update fields.
.class Bumper:Obj
.method $constructor
    .local pair
    const "\n===Pair 7,11 should appear below===\n"
    call String:print
    pop
    new Pair
    store pair
    const 7
    load pair
    store_field Pair:x
    const 11
    load pair
    store_field Pair:y
    load pair
    call Pair:print
    pop
    const "\n===Pair 7,11 should appear above===\n"
    call String:print
    pop
    const 10
    load pair
    call Pair:bumpy
    pop
    load pair
    call Pair:print
    pop
    const nothing
    return 0
