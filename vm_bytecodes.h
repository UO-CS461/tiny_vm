/* Convert between text and integer versions of bytecode
 * and internal code form.
 */

#ifndef TINY_VM_VM_BYTECODES_H
#define TINY_VM_VM_BYTECODES_H

#include "vm_code_table.h"

extern int hex_to_int(const char *s);

extern int scan_hex(const char *fname);



#endif //TINY_VM_VM_BYTECODES_H
