#include <stdio.h>
#include <assert.h>
#include "vm_state.h"
#include "vm_loader.h"
#include "logger.h"

int main() {
    push_log_level(WARN);
    log_info("Initiating loader");
    vm_loader_init();
    log_info("Load from sample.json");
    vm_load_from_path("sample.json");
    log_info("Code Loaded.");
    vm_run();
    log_info("Ran");
    return 0;
}
