.class Main:Obj
.method $constructor
.local thisisalongname,c,x,b,z
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
load x
call Int:print
pop
const "Below this is nonsense"
store b
const "t:Int = f*7; -> this will fail because f is not defined"
store c
const "\nhello\n"
call String:print
pop
load z
load x
call Int:less
jump_ifnot else_0
jump then_0
then_0:
const "hello x is less than z\n"
call String:print
pop

jump endif_0
else_0:
const "hello x is not less than z\n"
call String:print
pop
load z
load x
call Int:less
jump_ifnot else_1
jump then_1
then_1:
const "x is greater than z\n"
call String:print
pop

jump endif_1
else_1:
endif_1:


endif_0:


return 0

