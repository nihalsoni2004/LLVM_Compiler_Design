// Safe Program: No UB
#include <limits.h>
#include <stdio.h>

int main(void) {
    unsigned int x = UINT_MAX;
    unsigned int y = x + 1;
    printf("UINT_MAX + 1 = %u\n", y);

    int a = INT_MAX;
    if (a < INT_MAX) {
        int b = a + 1;
        printf("b = %d\n", b);
    }
    return 0;
}
