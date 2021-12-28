#include <stdio.h>
#include <assert.h>
#include "vm_state.h"
#include "vm_ops.h"
#include "vm_bytecodes.h"
#include "vm_loader.h"
#include "builtins.h"

int main() {
    // Testing constant renumbering ...
    int everything = int_literal_const("99");
    int even_more = int_literal_const("98");
    printf("Load from sample.json\n");
    vm_load_from_path("sample.json");
    printf("Code Loaded.\n");
    vm_run();
    printf("Ran\n");
    return 0;
}

int junk() {
    printf("Creating constants\n");
    int everything = int_literal_const("42");
    int even_more = int_literal_const("58");
    printf("Initializing code block\n");
    vm_code_block[0] = (vm_Word) { .instr = vm_op_const };
    vm_code_block[1] = (vm_Word) { .intval = everything };
    // Method call:  Slot 2 is "print"
    vm_code_block[2] = (vm_Word) { .instr = vm_op_methodcall };
    vm_code_block[3] = (vm_Word) { .intval = 2 };
    vm_code_block[4] = (vm_Word) { .instr = vm_op_const };
    vm_code_block[5] = (vm_Word) { .intval = everything };
    vm_code_block[6] = (vm_Word) { .instr = vm_op_const };
    vm_code_block[7] = (vm_Word) { .intval = even_more};
    vm_code_block[8] = (vm_Word) { .instr = vm_op_methodcall};
    vm_code_block[9] = (vm_Word) { .intval =  5}; // Plus
    vm_code_block[10] = (vm_Word) { .instr = vm_op_methodcall};
    vm_code_block[11] = (vm_Word) { .intval = 2}; // Print
    vm_code_block[12] = (vm_Word) { .instr = vm_op_halt };
    printf("Code loaded.\n");
    vm_run();
}