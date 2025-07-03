#include <stddef.h>

// Define standard library functions as stubs
double sqrt(double x) { return 0.0; }
char* strcpy(char* dest, const char* src) { return dest; }
size_t strlen(const char* s) { return 0; }

// Self-defined functions
int max(int a, int b) {
    if (a > b) return a; 
    else return b;
}
