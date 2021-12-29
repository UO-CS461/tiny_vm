#include <stdio.h>
#include <assert.h>
#include "vm_state.h"
#include "vm_ops.h"
#include "vm_loader.h"
#include "builtins.h"

int main() {
    printf("Load from sample.json\n");
    vm_load_from_path("sample.json");
    printf("Code Loaded.\n");
    vm_run();
    printf("Ran\n");
    return 0;
}
