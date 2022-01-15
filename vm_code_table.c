
/**
 * GENERATED CODE, DO NOT EDIT
 * Generated 2022-01-14 23:39:21.323650 by build_bytecode_table.py
 * 
 * Integer encoding of VM operations ---
 * Map those integer encodings to function pointers (for executing)
 * and to strings (for debugging and assembling).
 */
 
#include "vm_code_table.h"
op_tbl_entry vm_op_bytecodes[] = {

	 { "halt", vm_op_halt, 0 }, //0  Stops the processor.
	 { "const", vm_op_const, 1 }, //1  Push constant; constant value follows
	 { "call", vm_op_methodcall, 1 }, //2  Call an interpreted method
	 { "call_native", vm_op_call_native, 1 }, //3  Trampoline to native method
	 { "enter", vm_op_enter, 0 }, //4  Prologue of called method
	 { "return", vm_op_return, 1 }, //5  Return from method, reclaiming locals
	 { "new", vm_op_new, 1 }, //6  Allocate a new object instance
	 { "pop", vm_op_pop, 0 }, //7  Discard top of stack
	 { "load", vm_op_load, 1 }, //8  Load (push) a local variable onto stack
	 { "store", vm_op_store, 1 }, //9  Store (pop) top of stack to local variable

    { 0, 0, 0}  // SENTRY
};

