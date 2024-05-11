.class $Main:Obj
.method $constructor
.local 
const 3
store a
const 3
const 3
call Int:plus
store x
const 4
const 2
const 13
call Int:plus
call Int:mult
store z
load z
load x
call Int:mult
store thisisalongname
const "Below this is nonsense"
store b
const "t:Int = f*7; -> this will fail because f is not defined"
store c
load b
load c
call String:plus
store d
call String:print
pop
load c
load c
call String:plus
store x
call String:print
pop
const "hello\n"
call String:print
pop
return 0

