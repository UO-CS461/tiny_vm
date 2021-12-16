#include <stdio.h>
#include <assert.h>
#include "vm_state.h"
#include "vm_ops.h"
#include "vm_bytecodes.h"
#include "builtins.h"

int main() {
    printf("Creating constants\n");
    obj_ref everything = int_literal(42);
    int where_is_everything = create_const_value("everything", everything);
    printf("Initializing code block\n");
    vm_code_block[0] = (vm_Word) { .instr = vm_op_const };
    vm_code_block[1] = (vm_Word) { .intval = where_is_everything };
    // Method call:  Slot 2 is "print"
    vm_code_block[2] = (vm_Word) { .intval = 2 };
    vm_code_block[4] = (vm_Word) { .instr = vm_op_methodcall };
    vm_code_block[5] = (vm_Word) { .instr = vm_op_halt };
    printf("Code initialized.\n");
    vm_run();
    printf("Ran\n");
    return 0;
}
