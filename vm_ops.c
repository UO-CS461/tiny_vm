/**
 * Core operations codes of the virtual machine
 * (distinct from the methods of built-in classes in builtins.c)
 */
#include "vm_ops.h"
#include "vm_state.h"
#include <stdlib.h>
#include <stdio.h>

void vm_op_add(void) {
    // FIXME
    obj_ref op_right = vm_eval_pop();
    obj_ref op_left = vm_eval_pop();
    vm_eval_push(op_left);  // STUB
}

// For now we'll consider in-line constants.
// To be reconsidered; we could have objects
// in a VM heap or on the VM frame stack.
//

/*  Push inline constant (by constant table index).
 *  The constant is not CREATED here; it is REFERENCED here.
 *
 * vm_op_const(i): [] -> [ obj_ref ]
 */
void vm_op_const(void) {
    int inline_const_index = vm_fetch_next().intval;
    obj_ref the_constant = get_const_value(inline_const_index);
    vm_eval_push(the_constant);
    return;
}

/* Halt the virtual machine */
void vm_op_halt(void) {
    vm_run_state = VM_HALTED;
}


/* Call a method on an object; the object
 * should be on the eval stack, and the
 * next word in the instruction stream should
 * be the index of the native_method in the vtable.
 */
extern void vm_op_methodcall(void) {
    vm_call();
//    int method_index = vm_fetch_next().intval;
//    printf("Method call to method slot %d\n", method_index);
//    obj_ref this = vm_eval_pop();
//    class_ref its_class = this->header.clazz;
//    vm_addr m = its_class->vtable[method_index];
//    FIXME
}

/* Call a native_method on an object; the object
 * should be on the eval stack, and the
 * next word in the instruction stream should
 * be the address of the native_method.
 * The result of the native method call replaces
 * the "this" object on the stack.
 * vm_op_call_native(native_function): [this] -> [result]
 */
extern void vm_op_call_native(void) {
    printf("Making native call\n");
    obj_ref this = vm_eval_pop();
    vm_Native m = vm_fetch_next().native;
    obj_ref result = m(this);
    vm_Word word = {.obj = result};
    vm_frame_push_word(word);
}

/* The object allocator should be called just before
 * a call to the constructor. It creates an object with the
 * class pointer, but without initializing fields.  The
 * partially initialized object is left on the stack, where
 * the constructor can operate it.  Therefore we usually
 * want to push constructor arguments, invoke the allocator,
 * then invoke the constructor.
 *
 * The vm_new_obj function can be used for creating
 * literal constants, without the interpreter.
 *
 * vm_op_new(class): [ ] -> [ instance ]
 *
 */
extern obj_ref vm_new_obj(class_ref clazz) {
    printf("Allocating a new object of type %s\n", clazz->header.class_name);
    obj_ref new_thing = (obj_ref) malloc(clazz->header.object_size);
    new_thing->header.clazz = clazz;
    return new_thing;
}

extern void vm_op_new(void) {
    class_ref clazz = vm_fetch_next().clazz;
    obj_ref new_thing = vm_new_obj(clazz);
    vm_eval_push(new_thing);
    return;
}