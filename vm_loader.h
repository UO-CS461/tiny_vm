/* Linking loader for user code */

#ifndef TINY_VM_VM_LOADER_H
#define TINY_VM_VM_LOADER_H

#include "vm_core.h"

/* Loading normally starts at address 0,
 * but may be controlled through vm_load_address.
 */
extern int vm_load_address;

/* Initialize loader (loads built-in classes)
 */
extern void vm_loader_init();

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

#endif //TINY_VM_VM_LOADER_H
