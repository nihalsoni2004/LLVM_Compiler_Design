// Safe Program: Bounds-checked array access
#include <stdio.h>

int get_element_safe(const int arr[], int size, int index, int *out) {
	if (index < 0 || index >= size) {
		return -1;
	}
	*out = arr[index];
	return 0;
}

int main(void) {
	int data[5] = {1, 2, 3, 4, 5};
	int value = 0;
	if (get_element_safe(data, 5, 3, &value) == 0) {
		printf("value = %d\n", value);
	}
	return 0;
}
