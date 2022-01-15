
	.class Sample:Obj
	.method $constructor
	const 2
	call Int:neg
	const 3
	call Int:mul
	const 1
	const 4
	call Int:neg
	call Int:mul
	call Int:plus
	call Int:print
	pop
	return 0