# Sample assembly code
# (augment as the assember and loader are built out)
    const 1
    call  Int:print
    halt
    const "Integers"
    call  String:print
    const   42   # Should also trigger a literal constant for 42
    call    Int:print    # Method call
    pop
    const  42
    const 58
    call Int:plus
    call Int:print
    pop
    halt
