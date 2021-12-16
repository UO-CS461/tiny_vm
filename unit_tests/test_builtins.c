/* Test cases for builtins.{c,h} */
#include "../builtins.h"
#include <assert.h>

void test_Int() {
    obj_ref i = int_literal(42);
    assert(i->fields)
}

