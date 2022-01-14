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
    store pair1
    const 3
    load pair1
    store_field Pair:x
    const 4
    load pair1
    store_field Pair:y
    const "Expect 3,4: "
    call String:print
    pop
    load pair1
    call Pair:print
    pop
    const "\n"
    call String:print
    pop

    new Pair
    store pair2
    const 8
    load pair2
    store_field Pair:x
    const 11
    load pair2
    store_field Pair:y
    const "Expect 8, 11: "
    call String:print
    pop
    load pair2
    call Pair:print
    pop
    const "\n"
    call String:print
    pop

    const "Now bumping the y value by 20\n"
    call String:print
    pop

    const 20
    load pair2
    call  Pair:bumpy
    pop
    load pair2
    call Pair:print
    pop
    const "\n"
    call String:print
    pop
    const 0
    return 0
