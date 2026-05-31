// UB Class: Invalid Shift (C11 6.5.7)
#include <stdio.h>

int main(void) {
    int x = 1;
    int shift = 32;
    int result = x << shift;
    printf("1 << 32 = %d\n", result);

    int neg_result = x << -1;
    printf("1 << -1 = %d\n", neg_result);
    return 0;
}
