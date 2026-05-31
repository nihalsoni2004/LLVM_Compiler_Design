// UB Class: Modifying String Literal (C11 6.4.5)
#include <stdio.h>

int main(void) {
    char *str = "hello";
    str[0] = 'H';
    printf("%s\n", str);
    return 0;
}
