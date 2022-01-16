//
// The state of the virtual machine, as a shared
// structure (global variables).
//
// Each operation of the virtual machine may
// inspect and modify this state.  Common
// operations such obtaining the next instruction
// word and advancing the instruction pointer are
// provided by vm_state.
//
//

#ifndef TINY_VM_VM_STATE_H
#define TINY_VM_VM_STATE_H

#define CODE_CAPACITY    1024  // Max # instruction words
#define FRAME_CAPACITY   1024    // Procedure call stack words
#define CONST_POOL_CAPACITY 128  // Constant objects, created during loading

/* Core definitions shared with
 * builtins.h
 */
#include "vm_core.h"
#include "logger.h"

/* Code block, a sequence of pointers to functions
 * that implement virtual machine instructions.
 * We represent the program counter (pc) as a pointer
 * rather than an index so that we can create blocks code
 * outside the vm_code_block, which is convenient for
 * creating native methods with trampolines.
 * Program counter always points at next instruction
 * word (not currently executing word).
 */
extern vm_Word vm_code_block[];
extern vm_addr vm_pc;

/* Fetch word at program counter, and advance
 * pc to point to next instruction.
 */
extern vm_Word vm_fetch_next(void);


/* A jump is an adjustment (+/- n instruction words)
 * to program counter.  A jump of 0 would continue
 * to next instruction. A jump of -2 would repeat
 * the jump instruction.
 */
extern void vm_relative_jump(int n);


/* Execution run state - running or halted
 */
#define VM_RUNNING 1
#define VM_HALTED 0
#define VM_SINGLE_STEP 2
extern int vm_run_state;
extern  enum LOG_LEVEL vm_logging;

/* Evaluation stack, separate from activation record
 * stack.  For now we just keep integers as values.
 */

/* While many higher level VMs (e.g., the Java virtual machine) keep
 * a separate stack for expression evaluation, we will integrate the
 * evaluation stack with the procedure call stack.  This is closer to
 * how a stack would be used in native code, although native code would
 * typically be register-oriented and make less use of an evaluation stack.
 */
extern void vm_eval_push(obj_ref v);
extern obj_ref vm_eval_pop();


/* Frame (activation record) stack.
 */
extern vm_Word vm_frame_stack[FRAME_CAPACITY];
extern vm_addr vm_sp;   // Stack pointer  (next free location on stack)
extern vm_addr vm_fp;   // Frame pointer  (locals and return address are relative to this)

/* Single word push/pop */
extern void vm_frame_push_word(vm_Word val);
extern vm_Word vm_frame_pop_word();
extern vm_Word vm_frame_top_word();  // Without popping
/*  roll 2: [ob x y] -> [x y ob] */
extern void vm_roll(int n);

/* Debugging */
void stack_dump(int n_words);
extern void dump_constants(void);
extern char *guess_description(vm_Word w);

/* ---------------- Constant Pool --------------------- */
/* We keep a table of constants corresponding to
 * literal values found in the program. This is similar to
 * the constant pool in a Java class file.  In a C or C++ program,
 * this would be a value computed at compile time and kept in a
 * known memory location.
 *
 * Constant values are object references.
 */

/* lookup_const_index("literal string") returns index
 * OR zero to indicate not present
 */
extern int lookup_const_index(char *literal);

/* create_const_value returns a positive index of the
 * entry the new constant object will have in the constant pool.
 */
extern int create_const_value(char *literal, obj_ref value);

/* get_const_value returns an object reference corresponding
 * to the provided index.
 */
extern obj_ref get_const_value(int index);


/* Execution control */
void vm_run();

#endif //TINY_VM_VM_STATE_H
