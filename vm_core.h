/*  The types that must be visible to both
 * vm_state and builtins
 * (so they do not circularly reference each other)
 */

#ifndef TINY_VM_VM_CORE_H
#define TINY_VM_VM_CORE_H

/**
 * VM core structures.  See docs/notes.md.
 *   The order of declarations below is constrained
 *   by C language rules about declaration before use.
 */

struct obj_struct;
struct class_struct;

typedef struct obj_struct*
obj_ref;

typedef struct class_struct*
class_ref;

struct obj_header_struct {
    class_ref clazz;
    int tag; // Validation tag for test & debug
    // To do:  garbage collector metadata would go here.
};


struct obj_struct {
    struct obj_header_struct header;
    obj_ref fields[];
};

/* A class contains its name (only for debugging),
 * a pointer to its superclass (for isinstance or typecase),
 * and a table of method pointers ("virtual functions"
 * in C++ terminology).  Method pointers are addresses of
 * instruction sequences.
 */
struct class_header_struct {
    char *class_name;
    int healthy_class_tag;
    class_ref super;  // Needed for typecase
    int n_fields;     // Redundant but convenient for debugging
    int object_size;  // Malloc this much before calling constructor
};


/* Virtual machine instructions */
typedef int vm_Intval;          // Native integers only for method slot indexes
typedef void (*vm_Instr)();     // VM instructions are pointers to their implementations
typedef obj_ref (*vm_Native)(); // Native methods return a value to be pushed


typedef union u_Word *vm_addr;

/* Memory is untyped.  All these things can be stored in memory words. */
typedef union u_Word {
    vm_Instr  instr;         // A virtual machine instruction
    // Some instructions are followed immediately by an operand
    // which may be ...
    vm_Intval intval;        // Only for method slot indexes; these are not Int objects
    vm_Native native;        // A native method
    // The following things appear in the activation record stack
    obj_ref obj;            // Reference (pointer) to an object
    class_ref clazz;        // A class to be instantiated
    vm_addr code_addr;      // Saved program counter
    vm_addr frame_addr;    // Saved stack or frame pointer;
} vm_Word;


/* In the class hierarchy, if C.vtable[7] is method "foo",
 * and D is a subclass of C, then D.vtable[7] is
 * either the same method "foo"  (inheritance)
 * or a compatible method "foo"  (overriding).
 * This allows us to treat D as a C even though D
 * might override some methods and add others (only at
 * the end of the vtable).
 */
struct class_struct {
    struct class_header_struct header;
    /* The vtable is an array of pointers to
     * code blocks.
     */
    vm_Word* vtable[];
};

/* Self-check debugging support */
/* A validation tag is an arbitrary number,
 * but should be unlikely to appear by chance.
 * The health checking functions just crash the
 * interpreter if given an unhealthy value. They
 * could be redefined as macros if we wanted to
 * eliminate the run-time cost.
 */
#define HEALTHY 1234
extern void check_health_class(class_ref c);
#define GOOD_OBJ_TAG 0xceed
// == 52973 decimal
extern void check_health_object(obj_ref v);


#endif //TINY_VM_VM_CORE_H
