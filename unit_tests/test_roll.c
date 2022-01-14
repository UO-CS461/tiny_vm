//
// Created by Michal Young on 1/12/22.
// Simple isolated unit test for the new 'roll' operation
//
#include "vm_state.h"
#include "builtins.h"
#include "logger.h"
#include <stdio.h>

int main(int argc, char **argv) {
    set_log_level(DEBUG);
    fprintf(stderr, "Testing the 'roll' operation\n");
    vm_frame_push_word((vm_Word) {.intval = 44});
    vm_frame_push_word((vm_Word) {.intval = 43});
    vm_frame_push_word((vm_Word) {.intval = 42});
    vm_frame_push_word((vm_Word) {.intval = 41});
    vm_frame_push_word((vm_Word) {.intval = 40});
    stack_dump(5);
    fprintf(stderr, "Expected:  44 43 42 41 40\n");
    vm_roll(3);
    stack_dump(5);
    fprintf(stderr, "Expected: 43 40 41 42 44\n");
    fprintf(stderr, "Finished testing the 'roll' operation.\n");
    return 0;
}
