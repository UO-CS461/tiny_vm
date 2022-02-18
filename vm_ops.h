//
// Created by Michal Young on 6/24/21.
//

#ifndef TINY_VM_VM_OPS_H
#define TINY_VM_VM_OPS_H

#include "vm_core.h"

/* Push value of inline constant onto the eval stack.
 * The next word is index of constant.
 *
 * vm_op_const(index): [] -> [ const[index] ]
 */
extern void vm_op_const(void);

/* Halt the virtual machine */
extern void vm_op_halt(void);

/* Call a method (virtual function) indirectly
 * through the vtable of an object's class.
 * Next word should be method index.
 *
 * vm_op_methodcall(m_index): [arg, arg, ...,  receiver] -> [result]
 */
extern void vm_op_methodcall(void);

/* Trampoline to a native method.
 * Wrap this inside an interpreted method
 * to handle the frame layout properly.
 *
 * The native method is parameterless, but has
 * access to the virtual machine state including
 * the "this" object at fp and the contents of
 * the stack.  The native method returns a value
 * which will be pushed onto the stack by the
 * trampoline.
 *
 * vm_op_call_native(native_function): [] -> [result]
*/
extern void vm_op_call_native(void);

/* The object allocator should be called just before
 * a call to the constructor. It creates an object with the
 * class pointer, but without initializing fields.  The
 * partially initialized object is left on the stack, where
 * the constructor can operate it.  Therefore we usually
 * want to push constructor arguments, invoke the allocator,
 * then invoke the constructor.
 *
 * new(class): [ ] -> [ instance ]
 */
 extern void vm_op_new(void);

 /* is_instance is the other op that takes a class as operand */
 extern void vm_op_is_instance(void);


 /* The interpreter may also create an object from within a
  * built-in method, without executing a VM instruction.
  */
 extern obj_ref vm_new_obj(class_ref clazz);

 /*  Control flow:
  * conditional and unconditional jumps
  * (always relative to program counter)
  *
  * Note: Relative jumps must consider that
  * program counter has already advanced past
  * end of instruction.  For example, relative jump
  * of -2 is jump to same jump instruction.
  *
  */
 extern void vm_op_jump();          // unconditional jump
 extern void vm_op_jump_if();       // conditional jump
 extern void vm_op_jump_ifnot();    // conditional jump

/*
 * The vm calling convention pushes and
 * pops whole activation records.
 *
 * vm_op_call:  What the calling procedure does to make
 *    the call.
 * vm_op_enter:  What the called procedure does initially,
 *     including allocation of local variables in the frame.
 * vm_opreturn: What the called procedure does to resume
 *     execution in the calling procedure.
 */

extern void vm_op_call();   // Args and receiver are on stack; method index follows
extern void vm_op_enter();  // Currently a no-op
extern void vm_op_return(); // Expects arity next in code, to pop args

/*
 * Stack  manipulation
 */
extern void vm_op_pop();    // Discard top of operand stack
extern void vm_op_alloc();  // Allocate empty stack space for local variables
extern void vm_op_roll();  // Roll suffix of stack

/* Local variables */
extern void vm_op_store();  // Store into local variable at fp+n
extern void vm_op_load();   // Load from local variable at fp+n

/* Fields of objects */
extern void vm_op_load_field();  // Load from field of object
// store_field n: [value target] -> [], target.fields[n] = value
extern void vm_op_store_field(); // Store into field of object


#endif //TINY_VM_VM_OPS_H
