
#include "klee/klee.h"
#include <stdlib.h>
#include <assert.h>
#include "../qsort.h"  
extern void swap(int *, int *);

int main() {
    #define MAX_ARRAY_SIZE 4  
    #define MAX_VALUE 1000      
    int *a = (int *)malloc(sizeof(int) * MAX_ARRAY_SIZE);
    klee_make_symbolic(a, sizeof(int) * MAX_ARRAY_SIZE, "a");
    

    for (int i = 0; i < MAX_ARRAY_SIZE; i++) {
        klee_assume(a[i] >= 0);
        klee_assume(a[i] < MAX_VALUE);
    }

    int *b = (int *)malloc(sizeof(int) * MAX_ARRAY_SIZE);
    klee_make_symbolic(b, sizeof(int) * MAX_ARRAY_SIZE, "b");
    

    for (int i = 0; i < MAX_ARRAY_SIZE; i++) {
        klee_assume(b[i] >= 0);
        klee_assume(b[i] < MAX_VALUE);
    }
    
    swap(a, b);
    
    return 0;
}