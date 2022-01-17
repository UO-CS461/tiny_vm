/*  The core state of the virtual machine
 *  including the code page and the stack
 *  (but not the heap, for now).
 */

#include "vm_state.h"
#include "vm_code_table.h"
#include "logger.h"
#include "builtins.h"  // For debugging only
#include <assert.h>
#include <stdio.h>
#include <string.h>

/* The concrete data structures live here */

vm_Word vm_code_block[CODE_CAPACITY];
vm_addr vm_pc =   &vm_code_block[0];
int vm_run_state = VM_RUNNING;
enum LOG_LEVEL vm_logging = INFO;

char *guess_description(vm_Word w);

/* --------- Program code -------------- */
/* Fetch next word from code block,
 * advancing the program counter.
 */
vm_Word vm_fetch_next(void) {
    vm_Word cur = (*vm_pc);
    if (vm_pc >= vm_code_block && vm_pc < vm_code_block + CODE_CAPACITY) {
        // Looks like we are executing an instruction in the main
        // code memory
        int word_number = vm_pc - vm_code_block;
        log_debug("Fetched [%d] (%p : %s)", word_number, cur.native,
                  guess_description(cur));
    } else {
        log_debug("Fetched %p (%s)", cur.native, guess_description(cur));
    }
    vm_pc ++;
    return cur;
}

/* A jump is an adjustment (+/- n instruction words)
 * to program counter.  A jump of 0 would continue
 * to next instruction. A jump of -2 would repeat
 * the jump instruction.
 */
extern void vm_relative_jump(int n) {
    log_debug("vm_state, Jumping (adjusted) %d from %p", n, vm_pc);
    vm_pc += n;
    log_debug("New program counter is %p", vm_pc);
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
    assert(v->header.tag == GOOD_OBJ_TAG);
    vm_frame_push_word((vm_Word) {.obj = v});
}

obj_ref vm_eval_pop() {
    vm_Word w = vm_frame_pop_word();
    assert(w.obj->header.tag == GOOD_OBJ_TAG);
    return w.obj;
}

/* Roll the stack:
 * roll 2: [ob x y] -> [x y ob]
 * roll 1: [ob x] -> [x ob]
 * (used to put the receiver object at the
 * stack pointer in preparation for method call)
 */
void vm_roll(int n) {
    vm_Word ob = *(vm_sp - n);
    for (int i=n; i > 0; --i) {
        *(vm_sp - i) = *(vm_sp + 1 - i);
    }
    *(vm_sp) = ob;
}


/* --------------------- Constant pool --------------- */

struct constant_pool_entry {
    char* name;
    obj_ref const_object;
};

/* There is a GLOBAL constant pool in the VM, shared by
 * all loaded modules. Each module has its own LOCAL
 * constants, because it doesn't know about the others.
 * Local constants are consolidated into the global pool
 * when a module is loaded into the VM, and constant
 * indexes are remapped while the module is loaded.
 */

/* The global pool */
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

/* Debugging support */
extern void dump_constants(void) {
    for (int i=1; i < vm_next_const; ++i) {
        obj_ref thing = vm_constant_pool[i].const_object;
        class_ref clazz = thing->header.clazz;
        log_debug("Constant %d: %s", i,
                  clazz->header.class_name);
        if (clazz == the_class_String) {
            struct obj_String_struct *s = (struct obj_String_struct *) thing;
            log_debug("Value: |%s|", s->text);
        } else if (clazz == the_class_Int) {
            struct obj_Int_struct *v = (struct obj_Int_struct *) thing;
            log_debug("Value: %d", v->value);
        }  else if (thing == lit_true) {
            log_debug("the literal true");
        }  else if (thing == lit_false) {
            log_debug("the literal false");
        } else if (thing == nothing) {
            log_debug("the value nothing");
        } else {
            log_debug("Maybe a user-defined value");
        }
    }
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
            char *name = vm_op_bytecodes[i].name;
            return name;
        }
    }
    // Not an instruction ... what else could it be?
    sprintf(buff, "%p",  op);
    return buff;
}

char *guess_description(vm_Word w) {
    static char buff[500];
    /* Is it an instruction? */
    for (int i=0; vm_op_bytecodes[i].name; ++i) {
        if (vm_op_bytecodes[i].instr == w.instr) {
            char *name = vm_op_bytecodes[i].name;
            return name;
        }
    }
    /*  A small integer constant? */
    if (w.intval >= -1000 && w.intval <= 1000) {
        sprintf(buff, "(int) %d", w.intval);
        return buff;
    }
    /* The remaining checks all assume it is
     * a valid (readable) memory address.
     * I really need exception handling for the
     * cases when it is not.
     */

    /* An object? */
    if (w.obj->header.tag == GOOD_OBJ_TAG) {
        sprintf(buff, "(%s object) %p",
                w.obj->header.clazz->header.class_name,
                w.obj);
        return buff;
    }
    /* An address on the stack? */
    long stack_base =  (long) &vm_frame_stack[0];
    long stack_limit = (long) &vm_frame_stack[FRAME_CAPACITY];
    long as_frame = (long) w.frame_addr;
    if (stack_base <= as_frame && as_frame < stack_limit) {
        int frame_num = w.frame_addr - vm_frame_stack;
        sprintf(buff, "(stack ptr) %d", frame_num);
        return buff;
    }
    /* We can't currently distinguish class objects
     * from other things.
     */
    sprintf(buff, "Unknown thing: %p",  w.instr);
    return buff;
}

void stack_dump(int n_words) {
    const char* fp_ind = "-fp->";
    const char* not_fp = "     ";
    log_debug("===");
    vm_addr top = vm_sp;
    int depth = top - vm_frame_stack;
    /* Start up to n_words below the top */
    vm_addr cur_cell;
    if (depth > n_words) {
        cur_cell = top - n_words;
    } else {
        cur_cell = vm_frame_stack;
    }
    while (cur_cell <= top) {
        const char *indic;
        if (vm_fp == cur_cell) {
            indic = fp_ind;
        } else {
            indic = not_fp;
        }
        int frame_num = cur_cell - vm_frame_stack;
        log_debug("%s %d : %s", indic, frame_num,
               guess_description(*cur_cell));
        cur_cell += 1;
    }
    log_debug("===");
}

/* One execution step, at current PC */
void vm_step() {
    vm_Instr instr = vm_fetch_next().instr;
    char *name = guess_description((vm_Word) instr);
    log_debug("Step:  %s",name );
    (*instr)();
    health_check_builtins();
    stack_dump(8);
}


void vm_run() {
    vm_run_state = VM_RUNNING;
    // push_log_level(DEBUG);
    while (vm_run_state == VM_RUNNING) {
        vm_step();
    }
    // pop_log_level();
}
