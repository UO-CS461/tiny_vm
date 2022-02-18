# Tests IsADuck with is_instance test
.class DuckCheck:Obj
.method $constructor
.local  duck
    enter
    const "Getting my ducks in a row ...\n"
    call String:print
    pop
    new IsADuck
    call IsADuck:$constructor
    store duck
    const "One duck constructed\n"
    call String:print
    pop
    load duck
    is_instance IsADuck
    jump_if  it_is
    const "It should have been a duck!\n"
    call String:print
    pop
    return 0
it_is:
    const "It is a proper duck, as expected!\n"
    call String:print
    pop
    load duck
    is_instance String
    jump_ifnot  not_a_string
    const "A box that holds a String is not a String!\n"
    call String:print
    pop
    return 0
not_a_string:
    const "You can tell ducks from strings by their beaks.\n"
    call String:print
    pop
    load duck
    call  IsADuck:print
    pop
    const "Ducks have been checked.\n"
    call String:print
    return 0
