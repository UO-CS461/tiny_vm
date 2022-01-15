/*
 * vm_core is mostly just for shared declarations,
 * but it seems like the best place to put debugging
 * support as well.
 */
#include "vm_core.h"
#include "logger.h"
#include <assert.h>

void check_health_class(class_ref c) {
    assert(c->header.healthy_class_tag == HEALTHY);
}

void check_health_object(obj_ref v) {
    assert(v->header.tag == GOOD_OBJ_TAG);
    assert(v->header.clazz->header.healthy_class_tag == HEALTHY);
}
