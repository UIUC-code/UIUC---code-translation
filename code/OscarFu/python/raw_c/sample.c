#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    double x;
    double y;
} Vector2;

enum Status {
    OK,
    ERROR
};

// Forward declaration
int multiply(int a, int b);

// Function with struct and enum return
enum Status normalize_vector(Vector2* vec);

// Inline function
inline int max(int a, int b) {
    return (a > b) ? a : b;
}

// Global variables
char global_buffer[1024];
static int internal_state = 0;

// Function with array parameter
void fill_array(int arr[], int size, int value) {
    for (int i = 0; i < size; ++i) {
        arr[i] = value;
    }
}

// Function returning a pointer
char* duplicate_string(const char* input) {
    size_t len = strlen(input);
    char* copy = (char*)malloc(len + 1);
    if (copy) {
        strcpy(copy, input);
    }
    return copy;
}

// Function with function pointer as argument
void for_each(int* array, int size, void (*func)(int)) {
    for (int i = 0; i < size; ++i) {
        func(array[i]);
    }
}

// Static helper
static void log_message(const char* msg) {
    printf("[log] %s\n", msg);
}

// Actual definition of multiply
int multiply(int a, int b) {
    return a * b;
}

// Using enum and modifying struct
enum Status normalize_vector(Vector2* vec) {
    double mag = sqrt(vec->x * vec->x + vec->y * vec->y);
    if (mag == 0.0) return ERROR;
    vec->x /= mag;
    vec->y /= mag;
    return OK;
}
