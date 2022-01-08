# Minimal example that creates and uses a class with
# two fields (both Int), with an internal method
#
.class Pair:Obj
.field x
.field y

.method $constructor
    load 0  # The "this" object
    const 2
    store_field $:x
    load 0
    const 4
    store_field $:y
    load 0
    load_field $:x
    call Int:print
    return 0
