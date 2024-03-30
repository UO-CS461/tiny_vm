/**
 * Core operations codes of the virtual machine
 * (distinct from the methods of built-in classes in builtins.c)
 */
#include "vm_ops.h"
#include "vm_state.h"
#include "builtins.h"  // For literals lit_true, lit_false, nothing
#include "logger.h"
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>

/*  Push inline constant (by constant table index).
 *  The constant is not CREATED here; it is REFERENCED here.
 *
 * vm_op_const(i): [] -> [ obj_ref ]
 */
void vm_op_const(void) {
    int inline_const_index = vm_fetch_next().intval;
    obj_ref the_constant = get_const_value(inline_const_index);
    check_health_object(the_constant);
    vm_eval_push(the_constant);
    return;
}

/* Halt the virtual machine */
void vm_op_halt(void) {
    vm_run_state = VM_HALTED;
}

/* =======  Control Flow  =========== */

/* Control flow is always relative to the
 * program counter.
 */

/* Jump always */
extern void vm_op_jump() {
    int span = vm_fetch_next().intval;
    log_debug("Unconditional jump %d", span);
    vm_relative_jump(span);
}

/* Jump if true */
extern void vm_op_jump_if() {
    int span = vm_fetch_next().intval;
    obj_ref cond = vm_frame_pop_word().obj;
    assert_is_type(cond, the_class_Boolean);
    if (cond == lit_true) {
        vm_relative_jump(span);
    }
};

/* Jump if false */
extern void vm_op_jump_ifnot() {
    int span = vm_fetch_next().intval;
    obj_ref cond = vm_frame_pop_word().obj;
    assert_is_type(cond, the_class_Boolean);
    if (cond == lit_false) {
        vm_relative_jump(span);
    }
}

/* ========  Linkage instructions =========== */

/* Call a method on an object; the object
 * should be on the eval stack, and the
 * next word in the instruction stream should
 * be the index of the method in the vtable.
 */
extern void vm_op_methodcall(void) {
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
    obj_ref receiver = (*vm_fp).obj;
    check_health_object(receiver);
    class_ref clazz = receiver->header.clazz;
    check_health_class(clazz);
    vm_addr method_addr = clazz->vtable[method_index];
    vm_pc = method_addr;
    return;
}

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
extern void vm_op_call_native(void) {
    log_debug("Making native call\n");
    vm_Native m = vm_fetch_next().native;
    obj_ref result = m(*vm_fp);
    check_health_object(result);
    assert(result->header.tag == GOOD_OBJ_TAG);
    log_debug("Native method returned %s\n",
           result->header.clazz->header.class_name);
    vm_Word word = {.obj = result};
    vm_frame_push_word(word);
}


extern void vm_op_enter() {
    // Currently does nothing
    log_debug("Function entered\n");
    stack_dump(10);
}



extern void vm_op_return() {
    // Needs arity to reclaim arguments correctly
    int arity = vm_fetch_next().intval;
    assert(0 <= arity);   // Sanity check -- arity is non-negative
    assert(10 >= arity);  // Sanity check --- arity at most 10
    vm_Word return_value = vm_frame_pop_word();
    check_health_object(return_value.obj);
    vm_sp = vm_fp + 2;
    vm_fp = vm_frame_pop_word().frame_addr;
    vm_pc = vm_frame_pop_word().code_addr;
    vm_sp -= arity;
    *vm_sp = return_value;
    return;
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
    check_health_class(clazz);
    log_debug("Allocating a new object of type %s\n", clazz->header.class_name);
    obj_ref new_thing = (obj_ref) malloc(clazz->header.object_size);
    new_thing->header.clazz = clazz;
    new_thing->header.tag = GOOD_OBJ_TAG;
    for (int i=0; i < clazz->header.n_fields; ++i) {
        new_thing->fields[i] = nothing;
    }
    return new_thing;
}

/* The "new" operation first allocates space for a new, uninitialized
 * object of the right size, then calls the constructor to initialize it.
 * One operand, a class reference.
 * [ ] -> [ object ]
 */
extern void vm_op_new(void) {
    class_ref clazz = vm_fetch_next().clazz;
    check_health_class(clazz);
    obj_ref new_thing = vm_new_obj(clazz);
    check_health_object(new_thing);
    vm_eval_push(new_thing);
    return;
}

/* Is thing an instance of clazz?
 * FIXME:  Refactor to reduce duplication with assert_is_type
 */
int is_instance(obj_ref thing, class_ref clazz) {
    if (thing->header.tag != GOOD_OBJ_TAG) {
        fprintf(stderr, "Type check failure: %p is Not on object!\n", thing);
        assert(0);
    }
    assert(clazz->header.healthy_class_tag == HEALTHY);
    class_ref thing_class = thing->header.clazz;
    while (1) {
        if (thing_class == clazz) {
            return 1; // True, is an instance
        }
        if (thing_class == the_class_Obj) {
            return 0;  // Not an instance
        }
        thing_class = thing_class->header.super;
        assert(thing_class->header.healthy_class_tag == HEALTHY);
    }
 }

 /* is_instance operation:
  * [ obj, class ] -> [ bool ]
  */
extern void vm_op_is_instance(void) {
    class_ref clazz = vm_fetch_next().clazz;
    check_health_class(clazz);
    if (is_instance(vm_frame_pop_word().obj, clazz)) {
        vm_frame_push_word((vm_Word) lit_true);
    } else {
        vm_frame_push_word((vm_Word) lit_false);
    }
}


/*
 * Stack and local variable manipulation
 */

/* Discard top element
 * [x] -> []
 */
extern void vm_op_pop(void) {
    obj_ref trash = vm_frame_pop_word().obj;
    return;
}

/* Roll the stack:
 * roll 2: [ob x y] -> [x y ob]
 * roll 1: [ob x] -> [x ob]
 * (used to put the receiver object at the
 * stack pointer in preparation for method call)
 */
void vm_op_roll(void) {
    int k = vm_fetch_next().intval;
    vm_roll(k);
}


/* Push element loaded from local variable
 * (ref) [] -> [x]
 * FIXME: Refactor stack access into vm_state ?
 */
extern void vm_op_load() {
    int variable_frame_index = vm_fetch_next().intval;
    obj_ref value = (vm_fp + variable_frame_index)->obj;
    check_health_object(value);
    vm_eval_push(value);
    return;
}


/* Pop top element and store into local variable
 * [x] -> []
 */
extern void vm_op_store() {
    int variable_frame_index = vm_fetch_next().intval;
    obj_ref value = vm_eval_pop();
    check_health_object(value);
    (vm_fp + variable_frame_index)->obj =  value;
    return;
}

/* Allocate stack space for local variables.
 * (i) [] -> [ n1, n2, ..., ni ]   (As many nothing objects as allocated)
 */
extern void vm_op_alloc() {
    int alloc_how_much = vm_fetch_next().intval;
    for (int i=0; i < alloc_how_much; ++i) {
        vm_frame_push_word((vm_Word) {.obj = nothing});
    }
}

/* Load/store to fields of an object.
 */

/* For load, object should be at top of stack.
 * (i) [obj] -> [field]
 */
extern void vm_op_load_field() {
    int field_slot = vm_fetch_next().intval;
    obj_ref the_obj = vm_frame_pop_word().obj;
    check_health_object(the_obj);
    log_debug("Loading field %d from %s object\n", field_slot,
              the_obj->header.clazz->header.class_name);
    obj_ref val = the_obj->fields[field_slot];
    check_health_object(val);
    vm_frame_push_word((vm_Word) {.obj=val});
}

/* For store, push object to be stored into first,
 * then calculate value to store into it.
 * The vm_op_store_field operation consumes both the value
 * and the object, which can be inefficient if we want to
 * store into several fields of the same object, but it's
 * the simplest and most consistent approach for code generation.
 * (i) [val obj] -> []
 */
extern void vm_op_store_field() {
    // push_log_level(DEBUG);
    int field_slot = vm_fetch_next().intval;
    obj_ref target_obj = vm_frame_pop_word().obj;
    check_health_object(target_obj);
    obj_ref value = vm_frame_pop_word().obj;
    check_health_object(value);
    assert(target_obj->header.clazz->header.n_fields > field_slot);
    // If you crash on the assertion above, consider whether target
    // and value are in the right order on the stack.
    log_debug("Storing value of class %s into field %d of type %s",
              value->header.clazz->header.class_name,
              field_slot,
              target_obj->header.clazz->header.class_name);
    target_obj->fields[field_slot] = value;
    // pop_log_level();
}
