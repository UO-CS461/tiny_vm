# Simple smoke test: Twopair incorporates two instances of Pair,
# and must import the Pair class (so it tests the recursive loading
# as well as reference to methods and fields in another class).
#
.class TwoPair:Obj
.field thing_one
.field thing_two

.method sum forward

.method $constructor
.local  pair1,pair2
    enter
    load $  # this
    new Pair
    store pair1  # Is this the right place?
    load pair1
    const 3
    store_field Pair:x
    load pair1
    const 4
    store_field Pair:y
    new Pair
    store pair2
    load pair2
    const 8
    store_field Pair:x
    load pair2
    const 11
    store_field Pair:y
    load pair1
    call Pair:print
    pop
    const "\n"
    call String:print
    pop
    load pair2
    call Pair:print
    return 0
