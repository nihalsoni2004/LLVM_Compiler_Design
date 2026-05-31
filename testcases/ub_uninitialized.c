// UB Class: Uninitialized Variable Read (C11 6.3.2.1)
#include <stdio.h>

int main(void) {
    int x;
    int y = x + 1;
    printf("y = %d\n", y);

    int flag;
    if (flag) {
        printf("flag is true\n");
    }
    return 0;
}
