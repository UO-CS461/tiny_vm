//
// Created by Michal Young on 12/30/21.
//

#include "logger.h"
#include <stdio.h>
#include <stdarg.h>

enum LOG_LEVEL LOGGING = INFO;

#define MAX_LEVELS 20
enum LOG_LEVEL prior_levels[MAX_LEVELS];
int level_stack_depth = 0;


void set_log_level(enum LOG_LEVEL level) {
    LOGGING = level;
}


void push_log_level(enum LOG_LEVEL level) {
    if (level_stack_depth >= MAX_LEVELS) {
        fprintf(stderr, "*** Log levels stacked too deep\n");
        return;
    }
    prior_levels[level_stack_depth] = LOGGING;
    ++level_stack_depth;
    LOGGING = level;
}


void pop_log_level() {
    if (level_stack_depth == 0) {
        fprintf(stderr, "*** Log levels stack underflow\n");
        return;
    }
    --level_stack_depth;
    LOGGING = prior_levels[level_stack_depth];
}


void log_debug(const char *fmt, ...) {
    if (LOGGING > DEBUG) return;
    va_list args;
    va_start(args, fmt);
    fprintf(stderr, "*DEBUG* : ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "\n");
}

void log_info(const char *fmt, ...) {
    if (LOGGING > INFO) return;
    va_list args;
    va_start(args, fmt);
    fprintf(stderr, "*INFO* : ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "\n");
}

void log_warn(const char *fmt, ...) {
    if (LOGGING > WARN) return;
    va_list args;
    va_start(args, fmt);
    fprintf(stderr, "*WARN* : ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "\n");

}
void log_error(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    fprintf(stderr, "*ERROR* : ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "\n");

}


