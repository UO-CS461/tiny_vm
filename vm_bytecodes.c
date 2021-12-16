//
// Created by Michal Young on 6/24/21.
//

#include "vm_bytecodes.h"
#include <stdio.h>
#include <assert.h>
#include <errno.h>

extern int hex_to_int(const char *s) {
    return 0; // FIXME
}

extern int scan_hex(const char *fname) {
    FILE *fp;
    fp = fopen(fname, "r");
    if (fp == NULL) {
        int err = errno;
        printf("Error opening file, fp is null: %d\n", err);
    }
    assert(fp);
    int hexval;
    while(fscanf(fp, "%x ", &hexval) != EOF) {
        printf("Read value: %d\n", hexval);
    }
    return 0;
}
