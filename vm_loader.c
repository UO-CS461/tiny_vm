/* Linking loader for user code */

#include "vm_loader.h"
#include "vm_state.h"
#include "builtins.h" // For constants
#include "vm_code_table.h" // opcode -> instruction
#include "logger.h"
#include <cjson/cJSON.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>


// Address to load to (pushed forward by each load)
//
int vm_load_address = 0;

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
    set_loaded(the_class_Obj);
    set_loaded(the_class_String);
    set_loaded(the_class_Boolean);
    set_loaded(the_class_Int);
    set_loaded(the_class_Nothing);
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

    /* Some literal constants are always present.  These include
     * "$false" and "$true", which represent the corresponding
     * boolean constants.  The "$" is to make confusion with
     * string literals less likely. (This should be improved to
     * make collisions impossible --- FIXME.)
     */


    cJSON_ArrayForEach(el, val) {
        cJSON *kind_el = cJSON_GetObjectItemCaseSensitive(el, "kind");
        cJSON *value_el = cJSON_GetObjectItemCaseSensitive(el, "value");
        char *kind = kind_el->valuestring;
        char *literal = value_el->valuestring;
        int internal;
        if (kind[0] == 'i') {
            internal = int_literal_const(literal);
        } else if (kind[0] == 's') {
            internal = str_literal_const(literal);
        } else {
            perror("Constant of unknown type");
        }
        constant_renumber_map[literal_count] = internal;
        log_debug("Literal %s internal %d remapped to %d",
               literal, literal_count, internal);
        ++literal_count;
    }


    // Translating code.  Constants are an ugly
    // special case.  Is there any way around that?
    cJSON *ops = cJSON_GetObjectItemCaseSensitive(tree,
        "instructions");
    assert (cJSON_IsArray(ops));
    el = ops->child;
    while (el) {
        assert(cJSON_IsNumber(el));
        int opcode = el->valueint;
        log_debug("Op: %d (%s)",
               opcode, vm_op_bytecodes[opcode].name);
        vm_code_block[vm_load_address++] = (vm_Word)
                {.instr = vm_op_bytecodes[opcode].instr};

        if (vm_op_bytecodes[opcode].n_operands) {
            // Max is 1 operand!
            el = el->next;
            int operand = el->valueint;
            // FIXME: What a hack!
            if (vm_op_bytecodes[opcode].instr == vm_op_const) {
                vm_code_block[vm_load_address++] = (vm_Word)
                        {.intval=  constant_renumber_map[operand]};
            } else {
                vm_code_block[vm_load_address++] = (vm_Word)
                        {.intval = operand};
            }
        }
        el = el->next;
    }
    cJSON_Delete(tree);
    return 1;
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
