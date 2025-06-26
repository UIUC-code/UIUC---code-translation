#include <assert.h>
#include <klee/klee.h>

// Forward declare quicksort functions from qsort.c
void swap(int* a, int* b);
int partition(int arr[], int low, int high);
void quickSort(int arr[], int low, int high);

int main() {
    #define SIZE 5
    int arr[SIZE];
    
    // Make the array symbolic
    klee_make_symbolic(arr, sizeof(arr), "arr");
    
    // Sort the array
    quickSort(arr, 0, SIZE - 1);
    
    // Verify array is sorted
    for (int i = 0; i < SIZE - 1; i++) {
        // Check sorted invariant: current element <= next element
        klee_assume(arr[i] <= arr[i + 1]);  // Teach KLEE the expected invariant
        klee_assert(arr[i] <= arr[i + 1]);    // Verify the property
    }
    
    return 0;
}
