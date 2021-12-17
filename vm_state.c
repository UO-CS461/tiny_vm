//
// Created by Michal Young on 6/23/21.
//

#include "vm_state.h"
#include "vm_code_table.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

/* The concrete data structures live here */

vm_Word vm_code_block[CODE_CAPACITY];
vm_addr vm_pc =   &vm_code_block[0];
int vm_run_state = VM_RUNNING;

/* --------- Program code -------------- */
/* Fetch next word from code block,
 * advancing the program counter.
 */
vm_Word vm_fetch_next(void) {
    vm_Word cur = (*vm_pc);
    printf("Fetched %p\n", cur);
    vm_pc ++;
    return cur;
}


/* ----------Activation records (frames) -----------
 *
 * Upward growing stack (real stacks grow downward).
 */
vm_Word vm_frame_stack[FRAME_CAPACITY];

vm_Word *vm_fp = vm_frame_stack;    // Frame pointer, points to "this" object
vm_Word *vm_sp = vm_frame_stack;    // Stack pointer, points to top item
/* Evaluation stack is at end of activation record. */


/* Push a single word on the frame stack */
void vm_frame_push_word(vm_Word val) {
    ++ vm_sp;
    *vm_sp = val;
}

/* Pop a single word from the frame stack */
vm_Word vm_frame_pop_word() {
    vm_Word value = *vm_sp;
    -- vm_sp;
    return value;
}

/* Get top word without removing it */
vm_Word vm_frame_top_word() {
    vm_Word value = *vm_sp;
    return value;
}

/* While many higher level VMs (e.g., the Java virtual machine) keep
 * a separate stack for expression evaluation, we will integrate the
 * evaluation stack with the procedure call stack.  This is closer to
 * how a stack would be used in native code, although native code would
 * typically be register-oriented and make less use of an evaluation stack.
 */
void vm_eval_push(obj_ref v) {
    vm_frame_push_word((vm_Word) {.obj = v});
}

obj_ref vm_eval_pop() {
    vm_Word w = vm_frame_pop_word();
    return w.obj;
}


// FIXME:  Add load/store relative to fp

/* -------------  Call / Return protocol ----------- */

/* The vm calling convention pushes and
 * pops whole activation records.
 *
 * vm_call:  What the calling procedure does to make
 *           the call.
 * vm_enter:  What the called procedure does initially,
 *            including allocation of local variables in the frame.
 * vm_return: What the called procedure does to resume
 *            execution in the calling procedure.
 *
 *            FIXME:  Allow arguments on the stack
 */

extern void vm_call() {
    int method_index = vm_fetch_next().intval;
    // New "this" will be receiver object
    vm_addr new_fp = vm_sp;
    // Save program counter for return
    vm_frame_push_word((vm_Word) {.code_addr = vm_pc});
    // Save caller's frame pointer
    vm_frame_push_word((vm_Word) {.frame_addr = vm_fp});
    vm_fp = new_fp;
    // Address of code for called method, found in the
    // class vtable.
    struct class_struct *clazz = (*vm_fp).obj->header.clazz;
    vm_addr method_addr = clazz->vtable[method_index];
    vm_pc = method_addr;
    return;
}


extern void vm_enter() {
    // Currently does nothing
    printf("Function entered\n");
}


extern void vm_return() {
    // Needs arity to reclaim arguments correctly
    int arity = vm_fetch_next().intval;
    assert(0 <= arity);   // Sanity check -- arity is non-negative
    assert(10 >= arity);  // Sanity check --- arity at most 10
    vm_Word return_value = vm_frame_pop_word();
    vm_sp = vm_fp + 2;
    vm_fp = vm_frame_pop_word().frame_addr;
    vm_pc = vm_frame_pop_word().code_addr;
    vm_sp -= arity;
    *vm_fp = return_value;
    return;
}


/* --------------------- Constant pool --------------- */

struct constant_pool_entry {
    char* name;
    obj_ref const_object;
};

static struct constant_pool_entry vm_constant_pool[CONST_POOL_CAPACITY];
static int vm_next_const = 1; // Skip index 0 so that it can be failure signal

/* lookup_const_index("literal string") returns index
 * OR zero to indicate not present
 */
extern int lookup_const_index(char *literal) {
    // We start with index 1, not 0, so that we can use 0 as failure
    for (int i=1; i < vm_next_const; ++i) {
        if (strcmp(literal, vm_constant_pool[i].name) == 0) {
            return i;
        }
    }
    // Not present in constant table
    return 0;
}

/* create_const_value returns a positive index of the
 * entry the new constant object will have in the constant pool.
 */
extern int create_const_value(char *literal, obj_ref value) {
    int const_index = vm_next_const;
    vm_next_const += 1;
    vm_constant_pool[const_index].name = strdup(literal);
    vm_constant_pool[const_index].const_object = value;
    return const_index;
}

/* get_const_value returns an object reference corresponding
 * to the provided index.
 */
extern obj_ref get_const_value(int index) {
    assert(index > 0 && index < vm_next_const);
    return vm_constant_pool[index].const_object;
}


/* Does execution belong here?
 * Maybe for now.
 */

/* Debugging/tracing support */
char *op_name(vm_Instr op) {
    static char buff[100];
    /* Is it an instruction? */
    for (int i=0; vm_op_bytecodes[i].name; ++i) {
        if (vm_op_bytecodes[i].instr == op) {
            return vm_op_bytecodes[i].name;
        }
    }
    // Not an instruction ... what else could it be?
    sprintf(buff, "%p",  op);
    return buff;
}

/* One execution step, at current PC */
void vm_step() {
    vm_Instr instr = vm_fetch_next().instr;
    printf("Step:  %s\n", op_name(instr));
    (*instr)();
}

void vm_run() {
    vm_run_state = VM_RUNNING;
    while (vm_run_state == VM_RUNNING) {
        vm_step();
    }
}
