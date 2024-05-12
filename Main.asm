.class Main:Obj
.method $constructor
.local a,z,b,x
const 2
store x
const 10
store z
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

load z
store a
load x
store b
while_1:
load z
load x
call Int:less
jump_ifnot endwhile_1
while_0:
load a
load b
call Int:less
jump_ifnot endwhile_0
const "inside of second while a:"
call String:print
pop
load a
call Int:print
pop
const "\n"
call String:print
pop
const 1
load a
call Int:minus
store a

jump while_0
endwhile_0:

const 1
load x
call Int:plus
store x
const "x:"
call String:print
pop
load x
call Obj:print
pop
const "\n"
call String:print
pop

jump while_1
endwhile_1:

const "this should throw error\n"
store x
load x
call Obj:print
pop
load x
load z
call Obj:plus
store x
load x
call Obj:print
pop
const "\nthis really shouldn't happen"
call String:print
pop

return 0

