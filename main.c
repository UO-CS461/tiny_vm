#include <stdio.h>
#include <assert.h>
#include "vm_state.h"
#include "vm_loader.h"
#include "logger.h"

int main() {
    push_log_level(DEBUG);
    log_info("Initiating loader");
    vm_loader_init();
    log_info("Load from sample.json");
    vm_load_from_path("sample.json");
    log_info("Code Loaded.");
    vm_loader_set_main("Sample");
    log_info("Patched in call to constructor of 'Sample'");
    log_info("Dumping constants");
    dump_constants();
    vm_run();
    log_info("Ran");
    return 0;
}
