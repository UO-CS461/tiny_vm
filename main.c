#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include "vm_state.h"
#include "vm_loader.h"
#include "logger.h"

#define PATHBUFSIZE 1000
int main(int argc, char *argv[]) {
    set_log_level(INFO);
    log_info("This is the tiny VM\n");
    int opt;
    char *main_class = "";
    char load_path[PATHBUFSIZE];
    int ok = 1;
    char *load_library = "./OBJ";
    while ((opt = getopt(argc, argv, ":DL:")) != -1) {
        switch (opt) {
            case 'L':
                load_library = optarg;
                fprintf(stderr, "Look in '%s' for object modules\n", optarg);
                break;
            case 'D':
                fprintf(stderr, "Noisy debugging selected with -%c\n", opt);
                set_log_level(DEBUG);
                vm_logging = DEBUG;
                break;
            case ':':
                fprintf(stderr, "Option %s requires a value\n", optarg);
                ok = 0;
                break;
            case '?':
                fprintf(stderr, "Unknown option '%s' \n", optarg);
                ok = 0;
                break;
        }
    }
    log_debug("Finished options, load library is %s\n", load_library);
    if (ok && optind < argc) {
        log_debug("There is at least one non-option argument\n");
        vm_loader_init(load_library);
        for (; ok && optind < argc; ++optind) {
            log_debug("Processing command line argument %d\n", optind);
            main_class = argv[optind];
            ok = vm_load_class(main_class);
        }
        vm_loader_set_main(main_class);
    }
    if (ok) {
        log_info("Executing %s\n", main_class);
        vm_run();
        log_info("Ran");
    } else {
        fprintf(stderr, "Errors, will not run\n");
    }
    return 0;
}
