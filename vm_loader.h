/* Linking loader for user code */

#ifndef TINY_VM_VM_LOADER_H
#define TINY_VM_VM_LOADER_H

#include "vm_core.h"

/* Loading normally starts at address 0,
 * but may be controlled through vm_code_index.
 */
extern int vm_code_index;

/* Initialize loader (loads built-in classes)
 */
extern void vm_loader_init(char *load_path_prefix);

/* When everything is loaded, we can patch in a call to the
 * constructor of the main class.
 */
void vm_loader_set_main(char *main_class_name);

/* Get loaded class reference by class name,
 * or return 0 indicating class is not loaded.
 */
extern class_ref find_loaded(char *name);

/* Load an "object" file (json format) from
 * a class name.
 */
extern int vm_load_class(char *classname);

/* Load an "object" file, which should be in JSON format.
 * Return 1 = success, 0 = failure.
 */
extern int vm_load_from_path(char *path);

/* Constants in method bytecode will be small non-negative
 * integers corresponding to the "constants" list in the
 * object code json, or chosen from this fixed set of
 * negative integers, each denoting a named literal.
 *
 * NOTE:  These constants MUST be consistent between
 * the loader (here) and the assembler (assemble.py).
 */
#define CODE_NOTHING  (-1)
#define CODE_FALSE (-2)
#define CODE_TRUE (-3)

#endif //TINY_VM_VM_LOADER_H
