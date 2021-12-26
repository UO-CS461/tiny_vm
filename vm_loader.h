/* Linking loader for user code */

#ifndef TINY_VM_VM_LOADER_H
#define TINY_VM_VM_LOADER_H

/* Loading normally starts at address 0,
 * but may be controlled through vm_load_address.
 */
extern int vm_load_address;

/* Load an "object" file, which should be in JSON format.
 * Return 1 = success, 0 = failure.
 */
extern int vm_load_from_path(char *path);

#endif //TINY_VM_VM_LOADER_H
