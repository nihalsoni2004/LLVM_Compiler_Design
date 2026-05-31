// UB Class: Strict Aliasing Violation (C11 6.5)
#include <stdio.h>
#include <string.h>

float int_to_float_ub(int x) {
    float *fp = (float *)&x;
    return *fp;
}

float int_to_float_safe(int x) {
    float result;
    memcpy(&result, &x, sizeof(float));
    return result;
}

int main(void) {
    int val = 0x3F800000;
    printf("UB way:   %f\n", int_to_float_ub(val));
    printf("Safe way: %f\n", int_to_float_safe(val));
    return 0;
}
