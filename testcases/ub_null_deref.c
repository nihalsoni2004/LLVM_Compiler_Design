// UB Class: Null Pointer Dereference (C11 6.5.3.2)
#include <stddef.h>
#include <stdio.h>

void process(int *p) {
    int val = *p;
    if (p == NULL) {
        printf("p is null\n");
        return;
    }
    printf("value: %d\n", val);
}

int main(void) {
    process(NULL);
    return 0;
}
