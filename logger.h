//
// Created by Michal Young on 12/30/21.
//

#ifndef TINY_VM_LOGGER_H
#define TINY_VM_LOGGER_H

enum LOG_LEVEL { DEBUG, INFO, WARN, ERROR };

extern enum LOG_LEVEL LOGGING;

extern void set_log_level(enum LOG_LEVEL level);
extern void push_log_level(enum LOG_LEVEL level);
extern void pop_log_level(void);

extern void log_debug(const char *fmt, ...);
extern void log_info(const char *fmt, ...);
extern void log_warn(const char *fmt, ...);
extern void log_error(const char *fmt, ...);


#endif //TINY_VM_LOGGER_H
