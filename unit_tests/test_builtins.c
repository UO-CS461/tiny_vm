/* Test cases for builtins.{c,h} */
#include "../builtins.h"
#include <assert.h>

void test_Int() {
    obj_ref i = new_int(42);
    assert(i->fields);
}

int main(int argc, char* argv[]) {
    test_Int();
}