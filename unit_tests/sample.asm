# Sample assembly code
# (augment as the assember and loader are built out)
.class Sample:Obj

.method $constructor
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
    const "I added a method!\n"
    return 0

