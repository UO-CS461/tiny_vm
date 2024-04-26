.class Main:Obj
.method $constructor
.local x,z,thisisalongname,b,c
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
call String:print
pop
return 0

