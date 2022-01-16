# Sample assembly code
# (augment as the assember and loader are built out)
.class Sample:Obj
.field x   # This is in addition to inherited fields
.field y
.method added forward

.method $constructor
    enter
    call $:added
    const "Scrabble: The game\n"
    call  String:print
    pop
     const 418
     const 383
    call Int:plus
     call Int:print
     pop
    const "\n"
    call  String:print
    pop
    const "That was our best game ever\n"
    call String:print
    pop
    return 0

.method added
    load_field $:x
    store_field $:y
    return 0
