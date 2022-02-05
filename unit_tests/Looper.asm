# Loop a counter from 1 to 10, printing each value
.class Looper:Obj
.method $constructor
.local  n
    enter
    const 1
    new Counter
    call Counter:$constructor
    store n

loop:  const "\nHead of loop\n"
    call String:print
    pop
    const 10
    load n
    call Counter:check
    jump_if  done

    const "Body of loop\n"
    call String:print
    pop
    load n
    load_field Counter:i
    call Int:print
    pop
    const "\nCounter value just above\n"
    call String:print
    pop

    load n
    call Counter:inc
    pop
    jump loop

done:  const "Exit loop\n"
    call String:print
    return 0
