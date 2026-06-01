// UB Class: Integer Division by Zero (C11 6.5.5)
#include <stdio.h>

int divide(int a, int b) {
    return a / b;
}

int main(void) {
    int result = divide(10, 0);
    printf("10 / 0 = %d\n", result);
    return 0;
}
