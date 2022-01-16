/*
 * The built-in classes.  These may have "hidden" fields
 * that are not objects (e.g., a String object has a
 * char* value field, an Int object has an int value field).
 * Their methods are "native code", i.e., pointers to C
 * functions.
 *
 * We need the following built-ins:
 * Obj:  root of the class hierarchy.
 * Nothing: a singleton, like 'None' in Python,
 *     or something like 'void' or 'NULL' in C.
 * Boolean:  has only two values, true and false.
 * Int:  holds a native integer.
 * String: holds a char*
 *
 * 2022 revision:  All methods return obj_ref, not more specific
 * classes.  The C type system, lacking a notion of subtype / subclass,
 * is just too unhelpful and tedious for more specific typing in a class
 * hierarchy.  Instead of leveraging the C type system, we will make
 * extensive use of dynamic type checks.
 *
 * All method functions take a single argument, "this".  Methods
 * with additional arguments (e.g., EQUALS) obtain their remaining
 * arguments from the virtual machine stack.
 *
 */
#ifndef TINY_VM_BUILTINS_H
#define TINY_VM_BUILTINS_H

/* Things we share with vm_state.h */
#include "vm_core.h"

/* Naming conventions:
 * (Simplified)
 */

extern const class_ref the_class_Obj;
extern class_ref the_class_String;
extern class_ref the_class_Boolean;
extern class_ref the_class_Int;
extern class_ref the_class_Nothing;

/* Literal constants.  */
extern obj_ref nothing;                 // token: nothing
extern obj_ref str_literal(char *s);    // token: "text"
extern obj_ref lit_false;               // token: false
extern obj_ref lit_true;                // token: true
extern obj_ref int_literal(char *n);      // token: [0-9]+, e.g., 17

/* ===============================
 * Make all the methods we might
 * inherit visible to user code.  (Needed?)
 * For VM this will likely be replaced by placing
 * inheritable native methods in a global pool
 * with a symbol table so that the loader can
 * access them.
 *================================
 */


/* While we make all methods return obj_ref, a specific
 * object structure for each class is used for a constructor
 * and for accessing fields after a cast.  We do not use
 * the C static type system to check the validity of field
 * and method references (tried that; too messy).  Instead,
 * function assert_is_type provides a dynamic type check,
 * similar to Python's isinstance.
 */

extern void assert_is_type(obj_ref thing, class_ref expected);

/* ==============
 * Obj
 * Fields: None
 * Methods:
 *    Constructor  (called after allocation)
 *    STRING
 *    PRINT
 *    EQUALS
 *
 * ==============
 */

struct class_Obj_struct;
typedef struct class_Obj_struct* class_Obj;

typedef struct obj_Obj_struct {
    struct obj_header_struct header;
    // No fields.
} * obj_Obj;

struct class_Obj_struct {
    struct class_header_struct header;
    /* Method table */
    vm_addr m_constructor;
    vm_addr m_string;
    vm_addr m_print;
    vm_addr m_equals;
};

extern  const class_ref the_class_Obj; /* Initialized in builtins.c */


/* ================
 * String
 * Fields:
 *    One hidden field, holding char*
 * Methods:
 *    Those of Obj, plus ordering, concatenation
 *    FIXME: (Incomplete for now.)
 * ==================
 */
struct class_String_struct;
typedef struct class_String_struct* class_String;

typedef struct obj_String_struct {
    struct obj_header_struct header;
    char *text;  // Hidden field
} * obj_String;

struct class_String_struct {
    struct class_header_struct header;
    /* Method table: Inherited or overridden */
    vm_addr constructor;
    vm_addr m_string;
    vm_addr m_print;
    vm_addr m_equals;
    /* Added method */
    vm_addr m_less;
};

extern class_ref the_class_String;

/* Construct an object from a string literal.
 * This is not available to the Quack programmer, but
 * is used by the compiler to create a literal string
 * from a Quack literal string.
 */
extern obj_ref str_literal(char *s);


/* ================
 * Boolean
 * Fields:
 *    One hidden field, an int (0 for False, -1 for True)
 * Methods:
 *
 * =================
 */

struct class_Boolean_struct;
typedef struct class_Boolean_struct* class_Boolean;

typedef struct obj_Boolean_struct {
    struct obj_header_struct header;
    int value;
} * obj_Boolean;

struct class_Boolean_struct {
    struct class_header_struct header;
    /* Method table: Inherited or overridden */
    vm_addr constructor;
    vm_addr m_string;
    vm_addr m_print;
    vm_addr m_equals;
};

extern class_ref the_class_Boolean;

/* There are only two instances of Boolean,
 * lit_true and lit_false
 * (i.e., the values of the literals true and false)
 * The constructor should return one of them;
 * maybe lit_false.
 */
extern obj_ref lit_false;
extern obj_ref lit_true;


/* ==============
 * Nothing (really just a singleton Obj)
 * Fields: None
 * Methods:
 *    Constructor  (called after allocation)
 *    STRING
 *    PRINT
 *    EQUALS
 *
 * ==============
 */
struct class_Nothing_struct;
typedef struct class_Nothing_struct* class_Nothing;

typedef struct obj_Nothing_struct {
    struct obj_header_struct header;
} * obj_Nothing;

/* I don't THINK we can ever call a method on Nothing,
 * but we'll give it a real method table just in case.
 */
struct class_Nothing_struct {
    struct class_header_struct header;
    /* Method table */
    vm_addr constructor;
    vm_addr m_string;
    vm_addr m_print;
    vm_addr m_equals;
};

extern class_ref the_class_Nothing;

/* There is a single instance of Nothing,
 * called nothing
 */
extern obj_ref nothing;


/* ================
 * Int
 * Fields:
 *    One hidden field, an int
 * Methods:
 *    STRING  (override)
 *    PRINT   (inherit)
 *    EQUALS  (override)
 *    and introducing
 *    LESS
 *    PLUS
 *    (add more later)
 * =================
 */

struct class_Int_struct;
typedef struct class_Int_struct* class_Int;

typedef struct obj_Int_struct {
    struct obj_header_struct header;
    int value;  // Hidden field
} * obj_Int;

struct class_Int_struct {
    /* Method table: Inherited or overridden */
    vm_addr constructor;
    vm_addr m_string;
    vm_addr m_print;
    vm_addr m_equals;
    /* Added methods */
    vm_addr m_less;
    vm_addr m_plus;
};

extern class_ref the_class_Int;

/* Integer and String objects may be created by built-in methods,
 * and literals may be created by the loader.
 */
extern int int_literal_const(char *n_lit);  // Index to constants table
extern obj_ref new_int(int n);  // An object reference, not a literal

extern int str_literal_const(char *s_lit); // Index to constants table
extern obj_ref new_string(char *s);  // An object reference, not a literal

/* Debugging - health checks */
extern void class_health_check(class_ref clazz);

/* Purely debugging ... stop when we corrupt a built-in class structure */
extern void health_check_builtins();

#endif //TINY_VM_BUILTINS_H
