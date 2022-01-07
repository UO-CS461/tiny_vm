/* Linking loader for user code */

#include "vm_loader.h"
#include "vm_state.h"
#include "builtins.h" // For constants
#include "vm_code_table.h" // opcode -> instruction
#include "logger.h"
#include <cjson/cJSON.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>


// Address to load to (pushed forward by each load)
// Note this is changed in vm_loader_init
int vm_code_index = 0;  // This actually index, not address
// And we need the address for methods, so ...
vm_addr vm_current_address() {
    return &vm_code_block[vm_code_index];
}



/* Table of already loaded classes.
 * Note that since each class header contains its name, a simple
 * list of classes references will do; we can look them up by checking
 * the ref->header.name
 */
#define MAX_CLASSES 100   // And we will behave very badly if you have more
class_ref loaded_classes[MAX_CLASSES];
static int n_classes_loaded;

/* Add a class reference to the table of loaded classes.
 */
static void set_loaded(class_ref c) {
    int slot = n_classes_loaded++;
    assert(n_classes_loaded < MAX_CLASSES);
    loaded_classes[slot] = c;
    return;
}

/* Initialize loader (loads built-in classes)
 */
void vm_loader_init() {
    // The built-in classes are available from the start,
    // and don't go through the usual class-loading translation process.
    set_loaded(the_class_Obj);
    set_loaded(the_class_String);
    set_loaded(the_class_Boolean);
    set_loaded(the_class_Int);
    set_loaded(the_class_Nothing);
    // We'll leave a little room for a "main" code sequence
    // at the beginning
    vm_code_index = 16;
    // And place a dummy sequence there for now ...
    int no_main = str_literal_const("No main program loaded!\n");
    vm_code_block[0] = (vm_Word) {.instr = vm_op_const};
    vm_code_block[1] = (vm_Word) {.intval = no_main};
    vm_code_block[2] = (vm_Word) {.instr = vm_op_methodcall};
    vm_code_block[3] = (vm_Word) {.intval = 2}; // "print" method
    vm_code_block[4] = (vm_Word) {.instr = vm_op_halt};
}

/* When everything is loaded, we can patch in a call to the
 * constructor of the main class (which should not have anything
 * except a constructor).
 */
void vm_loader_set_main(char *main_class_name) {
    class_ref main_class = find_loaded(main_class_name);
    assert(main_class);
    vm_code_block[0] = (vm_Word) {.instr = vm_op_new};
    vm_code_block[1] = (vm_Word) {.clazz = main_class};
    vm_code_block[2] = (vm_Word) {.instr = vm_op_methodcall};
    vm_code_block[3] = (vm_Word) {.intval = 0}; // Constructor method slot
    vm_code_block[4] = (vm_Word) {.instr = vm_op_pop};
    vm_code_block[5] = (vm_Word) {.instr = vm_op_halt};
}


/* Get loaded class reference by class name,
 * or return 0 indicating class is not loaded.
 */
class_ref find_loaded(char *name) {
    for (int i=0; i < n_classes_loaded; ++i) {
        if (strcmp(loaded_classes[i]->header.class_name, name) == 0) {
            return loaded_classes[i];
        }
    }
    return 0;
}


// Capacity limit:  For simplicity we read into a
// buffer of 20k bytes.
//
#define FILE_BUFFER_CAPACITY (1024 * 100 * sizeof(char))


/* read_file_fd
 * returns 0 (failure) or 1 (success)
 */
int read_file_fd(FILE *fd, char *file_buffer) {
    int pos = 0;
    char ch;
    /* Simple, not efficient. */
    while (1) {
        ch = fgetc(fd);
        if (feof(fd)) {
            break;
        } else if (ferror(fd)) {
            perror("Error reading file");
            break;
        }
        file_buffer[pos++] = ch;
    }
    // Do we need to add the null byte?  Maybe.
    file_buffer[pos] = 0;
    return 1;
}

vm_Word *translate_method_code(cJSON *ops, int const_map[]);

static int load_json(char buf[]) {
    cJSON *tree = NULL; // Tree as a whole
    cJSON *val = NULL;  // Named value in tree
    cJSON *el = NULL;   // Element of value
    tree = cJSON_Parse(buf);  // Must free at end
    if (tree == NULL) {
        perror("load_json in vm_loader.c: Failed to parse buffer. ");
        assert(tree);  // Will definitely abort
    }

    // Constants in user code are numbered from 0
    // in the order they appear, but may have different
    // identifiers in the VM.
    int constant_renumber_map[30];
    int next_local_const = 0;
    val = cJSON_GetObjectItemCaseSensitive(tree,
                                           "constants");
    if (val == NULL) {
        perror("Missing 'constants' element in json");
        return 0;
    }
    int literal_count = 0;
    cJSON_ArrayForEach(el, val) {
        cJSON *kind_el = cJSON_GetObjectItemCaseSensitive(el, "kind");
        cJSON *value_el = cJSON_GetObjectItemCaseSensitive(el, "value");
        char *kind = kind_el->valuestring;
        char *literal = value_el->valuestring;
        int internal;
        if (kind[0] == 'i') {
            internal = int_literal_const(literal);
        } else if (kind[0] == 's') {
            internal = str_literal_const(strdup(literal));
        } else {
            perror("Constant of unknown type");
        }
        constant_renumber_map[literal_count] = internal;
        log_debug("Literal %s internal %d remapped to %d",
                  literal, literal_count, internal);
        ++literal_count;
    }

    // Create and initialize a class object
    // push_log_level(DEBUG);
    char *class_name = cJSON_GetStringValue(
            cJSON_GetObjectItemCaseSensitive(tree, "class_name"));
    char *super_name = cJSON_GetStringValue(
            cJSON_GetObjectItemCaseSensitive(tree, "super"));
    log_info("Class %s extends %s", class_name, super_name);
    // Counts of methods and fields; I'm letting the assembler do the work here.
    int n_fields = (int) cJSON_GetNumberValue(
            cJSON_GetObjectItemCaseSensitive(tree, "n_fields"));
    int n_methods = (int) cJSON_GetNumberValue(
            cJSON_GetObjectItemCaseSensitive(tree, "n_methods"));
    log_info("Class %s has %d methods and %d fields",
             class_name, n_methods, n_fields);
    size_t class_obj_size =
            sizeof(struct class_header_struct)
            + n_methods * sizeof(vm_Word);
    class_ref the_super = find_loaded(super_name);
    assert(the_super); // Error if we can't find the superclass
    class_ref the_class = (class_ref) malloc(class_obj_size);
    the_class->header = (struct class_header_struct) {
            .class_name = strdup(class_name),
            .object_size = n_fields * sizeof(vm_Word),
            .super = the_super
    };
    // Copy inherited method pointers into vtable
    int n_inherited = (int) cJSON_GetNumberValue(
            cJSON_GetObjectItemCaseSensitive(tree, "n_inherited"));
    for (int i = 0; i < n_inherited; ++i) {
        the_class->vtable[i] = the_super->vtable[i];
    }
    //pop_log_level();

    set_loaded(the_class);
    // We want the class in the "loaded classes" table before loading
    // methods, because the methods might have references to the current class.

    cJSON *code_table = cJSON_GetObjectItemCaseSensitive(tree, "code");
    assert(code_table);  // Abort if it wasn't present
    assert(cJSON_IsArray(code_table));  // Should be an array of methods
    cJSON_ArrayForEach(el, code_table) {
        char *method_name = cJSON_GetStringValue(
                cJSON_GetObjectItemCaseSensitive(el, "name"));
        int method_slot = (int) cJSON_GetNumberValue(
                cJSON_GetObjectItemCaseSensitive(el, "slot"));
        cJSON *ops = cJSON_GetObjectItemCaseSensitive(el, "code");
        vm_Word *method_start_addr = translate_method_code(ops, constant_renumber_map);
        the_class->vtable[method_slot] = method_start_addr;
    }
    cJSON_Delete(tree);
    return 1;
}

vm_Word *translate_method_code(cJSON *ops, int const_map[]) {
    // Translating code.  Constants must be renumbered since local
    // constant number is not global constant number.
    assert (cJSON_IsArray(ops));
    cJSON *el = ops->child;
    vm_Word *method_start_address = vm_current_address();
    while (el) {
        assert(cJSON_IsNumber(el));
        int opcode = el->valueint;
        log_debug("Op: %d (%s)",
               opcode, vm_op_bytecodes[opcode].name);
        vm_code_block[vm_code_index++] = (vm_Word)
                {.instr = vm_op_bytecodes[opcode].instr};

        if (vm_op_bytecodes[opcode].n_operands) {
            // Max is 1 operand!
            el = el->next;
            int operand = el->valueint;
            // FIXME: Are constants the only things we need to renumber?
            // Probably classes too when we implement the "new" operation
            if (vm_op_bytecodes[opcode].instr == vm_op_const) {
                vm_code_block[vm_code_index++] = (vm_Word)
                        {.intval=  const_map[operand]};
            } else {
                vm_code_block[vm_code_index++] = (vm_Word)
                        {.intval = operand};
            }
        }
        el = el->next;
    }
    return method_start_address;
}



/* Load an "object" file (json format) from
 * a class name.
 */
extern int vm_load_class(char *classname);


int vm_load_from_path(char *path) {
    char file_buffer[FILE_BUFFER_CAPACITY];
    FILE *fd = fopen(path, "r");
    if (! fd) {
        perror("Failed to open file");
        return 0;
    }
    int ok;
    ok = read_file_fd(fd, file_buffer);
    if (ok) {
        cJSON *jobj = cJSON_Parse(file_buffer);
        ok = (jobj != NULL);
    }
    assert(ok);
    ok = load_json(file_buffer);
    fclose(fd);
    return ok;
}
