// UB Class: Signed Integer Overflow (C11 6.5)
#include <limits.h>
#include <stdio.h>

int check_overflow(int x) {
	if (x + 1 > x) {
		return 1;
	}
	return 0;
}

int main(void) {
	printf("check_overflow(INT_MAX) = %d\n", check_overflow(INT_MAX));
	return 0;
}
