/*
 * Table associating byte codes (table positions) with operation
 * names and implementing functions.  The table contents in
 * vm_code_table.c are generated automatically from opdefs.txt,
 * and that file should not be edited manually.
 */

#ifndef TINY_VM_VM_CODE_TABLE_H
#define TINY_VM_VM_CODE_TABLE_H

#include "vm_state.h"
#include "vm_ops.h"

typedef struct {
    char *name;
    vm_Instr instr;
    int n_operands;
} op_tbl_entry;

extern op_tbl_entry vm_op_bytecodes[];

#endif //TINY_VM_VM_CODE_TABLE_H
