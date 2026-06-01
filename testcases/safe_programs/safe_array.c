// Safe Program: No UB
#include <stdio.h>

int main(void) {
    int data[5] = {0,1,2,3,4};
    for (int i = 0; i < 5; ++i) {
        printf("%d ", data[i]);
    }
    printf("\n");
    return 0;
}
