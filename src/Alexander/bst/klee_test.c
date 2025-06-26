// klee_test.c - Modified to use standard assert
#include "bst.h"  // Include header instead of bst.c
#include <klee/klee.h>
#include <assert.h>
#include <stdlib.h>

// Configurable test sequence
#define MAX_OPS 4
#define MAX_KEY 6

int main() {
    struct node* root = NULL;
    int keyTracker[MAX_OPS] = {0};
    int keyCount = 0;
    
    // Make operation types and keys symbolic upfront
    int operations[MAX_OPS];
    int keys[MAX_OPS];
    
    klee_make_symbolic(operations, sizeof(operations), "operations");
    klee_make_symbolic(keys, sizeof(keys), "keys");
    
    for (int i = 0; i < MAX_OPS; i++) {
        klee_assume(operations[i] >= 0 && operations[i] <= 4);
        klee_assume(keys[i] >= 0 && keys[i] <= MAX_KEY);
    }
    
    // Symbolic operation sequence
    for (int i = 0; i < MAX_OPS; i++) {
        int op_type = operations[i];
        
        switch (op_type) {
            case 0:  // Insert
                if (keyCount < MAX_OPS) {
                    keyTracker[keyCount++] = keys[i];
                    root = insert(root, keys[i]);
                }
                break;
                
            case 1:  // Delete
                if (keyCount > 0) {
                    for (int j = 0; j < keyCount; j++) {
                        if (keyTracker[j] == keys[i]) {
                            keyTracker[j] = keyTracker[--keyCount];
                            break;
                        }
                    }
                    root = deleteNode(root, keys[i]);
                }
                break;
                
            case 2: { // Search
                int found = search(root, keys[i]);
                int expected = 0;
                for (int j = 0; j < keyCount; j++) {
                    if (keyTracker[j] == keys[i]) {
                        expected = 1;
                        break;
                    }
                }
                assert(found == expected);
                break;
            }
                
            case 3: { // Min
                struct node* min = minValueNode(root);
                if (keyCount > 0) {
                    int expected_min = keyTracker[0];
                    for (int j = 1; j < keyCount; j++) {
                        if (keyTracker[j] < expected_min)
                            expected_min = keyTracker[j];
                    }
                    assert(min != NULL && min->key == expected_min);
                } else {
                    assert(min == NULL);
                }
                break;
            }
                
            case 4: { // Max
                struct node* max = maxValueNode(root);
                if (keyCount > 0) {
                    int expected_max = keyTracker[0];
                    for (int j = 1; j < keyCount; j++) {
                        if (keyTracker[j] > expected_max)
                            expected_max = keyTracker[j];
                    }
                    assert(max != NULL && max->key == expected_max);
                } else {
                    assert(max == NULL);
                }
                break;
            }
        }
        
        // Validate BST invariants after every operation
        assert(isValidBST(root));
    }
    
    freeTree(root);
    return 0;
}
