# A set of tests for use of local variables,
#   (motivated by an error in a compiled Quack program)
# Should produce a sequence of 42
#
.class Locals:Obj
.method $constructor
.local x,y
enter

# Printing with Int:print
#
const "\nShoudl be 42, from Int:print: "
call String:print
pop
const 42
call Int:print
pop

# Printing with Obj:print
#
const "\nShoudl be 42, from Obj:print: "
call String:print
pop
const 42
call Obj:print
pop

# Print after store and load from local
#
const "\nShould be 42, after store and load: "
call String:print
pop
const 42
store x
load x
call Int:print
pop

# Print after store, load, add
#
const "\nShould be 42, after store and load: "
call String:print
pop
const 0
store y
load x
load y
call Int:plus
call Int:print
pop

const "\n"
call String:print
pop

const nothing
return 0
