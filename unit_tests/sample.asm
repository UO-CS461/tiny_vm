# Sample assembly code
# (augment as the assember and loader are built out)
     const 1
     const 2
#    call Int:equals
#    call  Bool:print
#    call  Nothing:print
#    pop
#    const 1
#    const 1
     call Int:plus
     const 3
     call Int:equals
     call Bool:print
    pop
    const "oops"
    call String:print
    pop
    halt
