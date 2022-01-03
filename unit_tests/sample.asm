# Sample assembly code
# (augment as the assember and loader are built out)
.class Sample:Obj

.method $constructor
    const "A string\n"
    call  String:print
    pop
     const 1
     const 2
    call Int:plus
     const 3
     call Int:equals
     call Bool:print
    pop
    const "\n"
    call  String:print
    pop
    const "oops\n\"I did it again\"\n"
    call String:print
    pop
    halt

.method added
    const "I added a method!\n"
    return 0

