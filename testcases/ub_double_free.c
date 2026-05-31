// UB Class: Double Free (C11 7.22.3.3)
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = (int *)malloc(sizeof(int));
    if (p == NULL) {
        return 1;
    }

    *p = 10;
    printf("value: %d\n", *p);

    free(p);
    free(p);
    return 0;
}
