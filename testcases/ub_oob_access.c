// UB Class: Out-of-Bounds Array Access (C11 6.5.6)
#include <stdio.h>

int get_element(int arr[], int index) {
    return arr[index];
}

int main(void) {
    int data[5] = {1, 2, 3, 4, 5};
    printf("%d\n", get_element(data, 10));
    return 0;
}
