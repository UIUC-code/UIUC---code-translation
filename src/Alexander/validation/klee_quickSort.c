
#include "klee/klee.h"
#include <stdlib.h>
#include <assert.h>
#include "qsort.h"  
extern void quickSort(int [], int, int);

int main() {
    #define MAX_ARRAY_SIZE 4  
    #define MAX_VALUE 1000    
    

    int *arr = (int *)malloc(sizeof(int) * MAX_ARRAY_SIZE);
    klee_make_symbolic(arr, sizeof(int) * MAX_ARRAY_SIZE, "arr");
    
    for (int i = 0; i < MAX_ARRAY_SIZE; i++) {
        klee_assume(arr[i] >= 0);
        klee_assume(arr[i] < MAX_VALUE);
    }

    int low;
    klee_make_symbolic(&low, sizeof(low), "low");
    
    klee_assume(low >= 0);
    klee_assume(low < MAX_VALUE);
    int high;
    klee_make_symbolic(&high, sizeof(high), "high");
    
    klee_assume(high >= 0);
    klee_assume(high < MAX_VALUE);
    
    klee_assume(low >= 0);
    klee_assume(low < MAX_ARRAY_SIZE);
    klee_assume(high >= 0);
    klee_assume(high < MAX_ARRAY_SIZE);
    klee_assume(low <= high);
    
    quickSort(arr, low, high);
    
    return 0;
}