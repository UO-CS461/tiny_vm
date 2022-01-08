#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <getopt.h>
#include "vm_state.h"
#include "vm_loader.h"
#include "logger.h"

#define PATHBUFSIZE 1000
int main(int argc, char *argv[]) {
    set_log_level(DEBUG);
    int opt;
    char *main_class = "";
    char load_path[PATHBUFSIZE];
    int ok = 1;
    char *load_library = "./OBJ";
    while (opt == getopt(argc, argv, ":L:")) {
        switch (opt) {
            case 'L':
                load_library = optarg;
                fprintf(stderr, "Look in '%s' for object modules\n", optarg);
                ok = 0;
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
        vm_loader_init();
        for (; optind < argc; ++optind) {
            log_debug("Processing command line argument %d\n", optind);
            main_class = argv[optind];
            strlcpy(load_path, load_library, PATHBUFSIZE);
            strlcat(load_path, "/", PATHBUFSIZE);
            strlcat(load_path, main_class, PATHBUFSIZE);
            strlcat(load_path, ".json", PATHBUFSIZE);
            log_info("Loading %s\n", load_path);
            vm_load_from_path(load_path);
        }
        vm_loader_set_main(main_class);
        log_info("Executing %s\n", main_class);
        vm_run();
        log_info("Ran");
    } else {
        fprintf(stderr, "Not loading\n");
    }
    return 0;
}
