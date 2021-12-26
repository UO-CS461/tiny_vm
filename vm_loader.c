/* Linking loader for user code */

#include "vm_loader.h"
#include "vm_state.h"
#include "builtins.h" // For constants
#include "vm_code_table.h" // opcode -> instruction
#include <cjson/cJSON.h>
#include <stdio.h>
#include <assert.h>

// Address to load to (pushed forward by each load)
//
int vm_load_address = 0;

// Capacity limit:  For simplicity we read into a fixed
// buffer of 20k bytes.
//
#define FILE_BUFFER_CAPACITY (1024 * 100 * sizeof(char))
char file_buffer[FILE_BUFFER_CAPACITY];


/* read_file_fd
 * returns 0 (failure) or 1 (success)
 */
int read_file_fd(FILE *fd) {
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
    tree = cJSON_Parse(buf);
    if (tree == NULL) {
        perror("Failed to parse buffer");
        return 0;
    }
    // Constants in user code are numbered from 0
    // in the order they appear, but may have different
    // identifiers in the VM.
    int constant_renumber_map[30];
    int next_local_const = 0;
    val = cJSON_GetObjectItemCaseSensitive(tree,
                                           "const_ints");
    if (val == NULL) {
        perror("Missing 'const_ints' element in json");
        return 0;
    }
    int literal_count = 0;
    cJSON_ArrayForEach(el, val) {
        char *literal = el->valuestring;
        int internal = int_literal_const(literal);
        constant_renumber_map[literal_count] = internal;
        printf("Literal %s internal %d remapped to %d\n",
               literal, literal_count, internal);
        ++literal_count;
    }
    // FIXME: Add string literals in the same way

    // Translating code.  Constants are an ugly
    // special case.  Is there any way around that?
    cJSON *ops = cJSON_GetObjectItemCaseSensitive(tree,
        "instructions");
    assert (cJSON_IsArray(ops));
    el = ops->child;
    while (el) {
        assert(cJSON_IsNumber(el));
        int opcode = el->valueint;
        printf("Op: %d (%s)\n",
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
    return 1;
}

/* Load an "object" file, which should be in JSON format.
 * Return 1 = success, 0 = failure.
 */
int vm_load_from_file(FILE *fd) {
    int ok;
    ok = read_file_fd(fd);
    if (ok) {
        cJSON *jobj = cJSON_Parse(file_buffer);
        ok = (jobj != NULL);
    }
    return ok;
}


int vm_load_from_path(char *path) {
    FILE *fd = fopen(path, "r");
    if (! fd) {
        perror("Failed to open file");
        return 0;
    }
    int status = vm_load_from_file(fd);
    assert(status);
    status = load_json(file_buffer);
    fclose(fd);
    return status;
}
