# Counter: Wraps an integer, can be incremented
.class Counter:Obj
.field i
# Constructor takes a single argument, an
# Int object
.method $constructor
.args   n
    enter
    load n
    load $
    store_field $:i
    load $  # Return the initialized object
    return 1

.method inc
    enter
    const 1
    load $
    load_field $:i
    call Int:plus
    load $
    store_field $:i
    const nothing
    return 0

# check if counter has reached value; return Boolean
.method check
.args value
    load value
    load $
    load_field $:i
    call Int:equals
    return 1

.method print
    enter
    load $
    load_field $:i
    call Int:print
    return 0
