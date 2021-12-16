//
// Created by Michal Young on 6/24/21.
//

#ifndef TINY_VM_VM_OPS_H
#define TINY_VM_VM_OPS_H

#include "vm_core.h"

/* Add top two eval stack elements (as integers) */
extern void vm_op_add(void);

/* Push inline constant onto the eval stack.
 * The next word should be an object reference.
 * FIXME: Use constant pool instead
 *
 * vm_op_const(ref): [] -> [ref]
 */
extern void vm_op_const(void);

/* Halt the virtual machine */
extern void vm_op_halt(void);

/* Trampoline to a native method.
 * Wrap this inside an interpreted method
 * to handle the frame layout properly.
 *
 * The object should be on the stack, and the
 * next word in the instruction stream should
 * be the index of the native_method in the vtable.
 * The result of the native method call replaces
 * the "this" object on the stack.
 *
 * vm_op_call_native(native_function): [this] -> [result]
 */
extern void vm_op_call_native(void);

/* Call a method (virtual function) indirectly
 * through the vtable of an object's class.
 * Next word should be method index.
 *
 * vm_op_methodcall(m_index): [arg, arg, ...,  receiver] -> [result]
 */
extern void vm_op_methodcall(void);

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

 /* The interpreter may also create an object from within a
  * built-in method, without executing a VM instruction.
  */
 extern obj_ref vm_new_obj(class_ref clazz);


#endif //TINY_VM_VM_OPS_H
