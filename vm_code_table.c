
/**
 * GENERATED CODE, DO NOT EDIT
 * 
 * Integer encoding of VM operations ---
 * Map those integer encodings to function pointers (for executing)
 * and to strings (for debugging and assembling).
 */
 
#include "vm_code_table.h"
op_tbl_entry vm_op_bytecodes[] = {

	 { "halt", vm_op_halt, 0 }, //0
	 { "const", vm_op_const, 1 }, //1
	 { "call", vm_op_methodcall, 1 }, //2
	 { "call_native", vm_op_call_native, 1 }, //3
	 { "new", vm_op_new, 1 }, //4

};

