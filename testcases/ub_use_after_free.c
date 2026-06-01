// UB Class: Use-After-Free (C11 7.22.3)
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = (int *)malloc(sizeof(int));
    if (p == NULL) {
        return 1;
    }

    *p = 42;
    free(p);

    printf("%d\n", *p);
    *p = 100;
    free(p);
    return 0;
}
