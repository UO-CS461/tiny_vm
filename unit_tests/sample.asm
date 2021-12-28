# Sample assembly code
# (augment as the assember and loader are built out)
    const   42   # Should also trigger a literal constant for 42
    call    Int:print    # Method call
    const  42
    const 58
    call Int:plus
    call Int:print
    halt
