// Safe Program: Null-check before dereference
#include <stddef.h>
#include <stdio.h>

void process_safe(const int *p) {
	if (p == NULL) {
		printf("null pointer\n");
		return;
	}
	printf("value: %d\n", *p);
}

int main(void) {
	int value = 42;
	process_safe(&value);
	process_safe(NULL);
	return 0;
}
