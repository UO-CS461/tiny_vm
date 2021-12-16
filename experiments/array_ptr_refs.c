/**
 * A little experiment to make sure I understand how pointer references
 * are related to array indexing in C.
 */
#include <stdio.h>

typedef struct _thing {
    int first;
    int second;
} thing;

typedef struct _thing* thingptr;

thing things[100];

int main(int argc, char **argv) {
    things[0].first = 42;
    things[1].second = 84;
    things[2].first = 77;
    thingptr p = things;
    printf("Expecting 42: %d\n",  p->first);
    printf("Expecting 84: %d\n", (p+1)->second);
    printf("Expecting 77: %d\n", (p+2)->first);
    (p+1)->first = 99;
    printf("Modified (p+1)->first\n");
    printf("Expecting 42: %d\n",  p->first);
    printf("Expecting 99: %d\n", (p+1)->first);
    printf("Expecting 84: %d\n", (p+1)->second);
    printf("Expecting 77: %d\n", (p+2)->first);
    printf("Whew!\n");
}

