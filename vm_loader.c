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


// Set load library path before loading each class by name.
// This is so that "imports" in each class can trigger recursive
// loads from the class name alone
static char *PATH_PREFIX = "UNINITIALIZED LOAD PATH";

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

/* Initialize loader
 * (loads built-in classes, dummy main program,
 * special named constants)
 */
void vm_loader_init(char *load_path_prefix) {
    // Where we will look for object modules in .json format
    PATH_PREFIX = load_path_prefix;
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
    //
    // The named constant literals
    create_const_value("$nothing", nothing);
    create_const_value("$true", lit_true);
    create_const_value("$false", lit_false);
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

vm_Word *translate_method_code(cJSON *ops, int const_map[], class_ref class_map[]);

/*
 * Constants in a class file (.json) are referenced as small
 * (non-negative) integer indexes
 * in a per-class "constant pool", or a fixed set of
 * negative integers (-1 .. -3 currently) for named literals.
 * Adding them to the constant pool for the
 * whole program requires remapping them to different indexes.
 * (Java, in contrast, maintains a separate constant pool for each
 * class at run-time.)
 */
static int remap_constants(int map[], cJSON *tree, int capacity) {
    cJSON *constants = cJSON_GetObjectItemCaseSensitive(tree,
                                           "constants");
    if (constants == NULL) {
        perror("Missing 'constants' element in json");
        return 0;
    }
    int literal_count = 0;
    cJSON *el;
    cJSON_ArrayForEach(el, constants) {
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
        map[literal_count] = internal;
        log_debug("Literal %s internal %d remapped to %d",
                  literal, literal_count, internal);
        ++literal_count;
        assert(literal_count < capacity);
    }
    return literal_count; // Actually it's the count - 1
}

/*  Object code in .json file refers to classes by index of its
 * "imports" list.  We
 *  need to make sure each referenced class is loaded, and to
 *  map those indexes to actual references to loaded classes.
 */
static int map_classes(class_ref class_map[], cJSON *tree, int capacity) {
    int class_count = 0;
    cJSON *imports = cJSON_GetObjectItemCaseSensitive(tree,
                                                        "imports");
    if (imports == NULL) {
        perror("Missing 'imports' element in json");
        return 0;
    }
    assert(cJSON_IsArray(imports));
    cJSON *el = imports->child;
    while (el) {
        assert(class_count < capacity);
        char *class_name = el->valuestring;
        class_ref clazz = find_loaded(class_name);
        if (! clazz) {
            /* We must load it first; recursive call of loader */
            log_info("Requires loading %s", class_name);
            vm_load_class(class_name);
            clazz = find_loaded(class_name);
            assert(clazz);
        }
        class_map[class_count] = clazz;
        ++class_count;
        el = el->next;
    }
    return class_count; // Actually it's the count - 1
}


static int load_json(char buf[]) {
    cJSON *tree = NULL; // Tree as a whole
    cJSON *val = NULL;  // Named value in tree
    cJSON *el = NULL;   // Element of value
    tree = cJSON_Parse(buf);  // Must free at end
    if (tree == NULL) {
        perror("load_json in vm_loader.c: Failed to parse buffer. ");
        assert(tree);  // Will definitely abort
    }

    /* module constant index -> global constant index */
    int constant_renumber_map[30];
    int n_consts = remap_constants(constant_renumber_map, tree, 30);

    /* module class index -> class reference,
     * with potential side effect of loading more class files.
     */
    class_ref class_map[30];
    int n_classes = map_classes(class_map, tree, 30);

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
    size_t obj_size = sizeof(struct obj_header_struct) + n_fields * sizeof(vm_Word);
    class_ref the_super = find_loaded(super_name);
    assert(the_super); // Error if we can't find the superclass
    class_ref the_class = (class_ref) malloc(class_obj_size);
    the_class->header = (struct class_header_struct) {
            .class_name = strdup(class_name),
            .healthy_class_tag = HEALTHY,
            .n_fields = n_fields,
            .object_size = obj_size,
            .super = the_super
    };
    log_debug("Class %s class object size %d with %d methods",
             class_name, class_obj_size, n_methods);
    log_debug("Objects of %s size %d with %d fields",
            class_name,  obj_size, n_fields);
    log_debug("Size of object header alone is %d bytes\n",
             sizeof(struct obj_header_struct));
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
        vm_Word *method_start_addr =
                translate_method_code(ops, constant_renumber_map, class_map);
        the_class->vtable[method_slot] = method_start_addr;
    }
    cJSON_Delete(tree);
    return 1;
}

vm_Word *translate_method_code(cJSON *ops, int const_map[], class_ref class_map[]) {
    // Translating code.  Constants must be renumbered since local
    // constant number is not global constant number.
    assert (cJSON_IsArray(ops));
    cJSON *el = ops->child;
    vm_Word *method_start_address = vm_current_address();
    while (el) {
        assert(cJSON_IsNumber(el));
        int opcode = el->valueint;
        log_debug("[%d] Op: %d (%s)",
               vm_current_address() - vm_code_block,
               opcode, vm_op_bytecodes[opcode].name);
        vm_code_block[vm_code_index++] = (vm_Word)
                {.instr = vm_op_bytecodes[opcode].instr};

        if (vm_op_bytecodes[opcode].n_operands) {
            // Max is 1 operand!
            el = el->next;
            int operand = el->valueint;
            log_debug("[%d] Operand: %d",
                      vm_current_address() - vm_code_block,
                      operand);
            if (vm_op_bytecodes[opcode].instr == vm_op_const) {
                int const_index;
                if (operand == CODE_FALSE) {
                    const_index = lookup_const_index("$false");
                } else if (operand == CODE_TRUE) {
                    const_index = lookup_const_index("$true");
                } else if (operand == CODE_NOTHING) {
                    const_index = lookup_const_index("$nothing");
                } else {
                    assert(operand >= 0);
                    const_index = const_map[operand];
                }
                assert(const_index);
                check_health_object(get_const_value(const_index));
                vm_code_block[vm_code_index++] = (vm_Word)
                        {.intval=  const_index};
            } else if(vm_op_bytecodes[opcode].instr == vm_op_new) {
                class_ref clazz = class_map[operand];
                log_debug("Translating allocation of new '%s'",
                          clazz->header.class_name);
                vm_code_block[vm_code_index++] = (vm_Word)
                        {.clazz = clazz};
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
#define PATHBUFSIZE 4096
extern int vm_load_class(char *classname) {
    char load_path[PATHBUFSIZE];
    strlcpy(load_path, PATH_PREFIX, PATHBUFSIZE);
    strlcat(load_path, "/", PATHBUFSIZE);
    strlcat(load_path, classname, PATHBUFSIZE);
    strlcat(load_path, ".json", PATHBUFSIZE);
    log_info("Loading %s", load_path);
    return vm_load_from_path(load_path);
}


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
