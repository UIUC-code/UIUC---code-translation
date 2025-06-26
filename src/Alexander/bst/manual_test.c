// manual_test.c - Generic KTEST file reader and executor
#include "bst.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// Binary tree visualization helper (horizontal display)
void print_tree(struct node* root, int depth) {
    if (root == NULL) return;
    
    // Right subtree (top position)
    print_tree(root->right, depth + 4);
    
    // Current node
    for (int i = 0; i < depth; i++) printf(" ");
    printf("[%d]\n", root->key);
    
    // Left subtree (bottom position)
    print_tree(root->left, depth + 4);
}

// Parse hex string to integer (little-endian)
int parse_hex_to_int(const char* hex_str) {
    // Remove '0x' prefix if present
    if (strncmp(hex_str, "0x", 2) == 0) {
        hex_str += 2;
    }
    
    // Parse the hex string as big-endian first
    uint32_t big_endian_value = (uint32_t)strtoul(hex_str, NULL, 16);
    
    // Convert from big-endian to little-endian by swapping bytes
    uint32_t little_endian_value = ((big_endian_value & 0xFF000000) >> 24) |
                                   ((big_endian_value & 0x00FF0000) >> 8)  |
                                   ((big_endian_value & 0x0000FF00) << 8)  |
                                   ((big_endian_value & 0x000000FF) << 24);
    
    // Convert to signed integer
    return (int32_t)little_endian_value;
}

// Read ktest file using ktest-tool and extract operations and keys
int read_ktest_file(const char* filename, int* operations, int* keys) {
    char command[512];
    sprintf(command, "ktest-tool %s", filename);
    
    FILE* pipe = popen(command, "r");
    if (!pipe) {
        printf("Error: Cannot run ktest-tool. Make sure KLEE is installed and ktest-tool is in PATH.\n");
        return 0;
    }
    
    char line[512];
    int current_object = -1;
    int found_operations = 0, found_keys = 0;
    
    printf("DEBUG: Parsing ktest-tool output...\n");
    
    while (fgets(line, sizeof(line), pipe)) {
        printf("DEBUG: Line: %s", line);
        
        // Look for object headers
        if (strstr(line, "object 0:")) {
            current_object = 0;
            printf("DEBUG: Found object 0 (operations)\n");
        }
        else if (strstr(line, "object 1:")) {
            current_object = 1;
            printf("DEBUG: Found object 1 (keys)\n");
        }
        
        // Look for hex data lines (format: "object N: hex : 0x...")
        if (strstr(line, ": hex :")) {
            char* hex_start = strstr(line, "0x");
            if (hex_start) {
                char hex_data[128];
                if (sscanf(hex_start, "%127s", hex_data) == 1) {
                    printf("DEBUG: Found hex data for object %d: %s\n", current_object, hex_data);
                    
                    if (current_object == 0 && !found_operations) {
                        // Parse operations array - data is little-endian 32-bit integers
                        char* hex_ptr = hex_data;
                        if (strncmp(hex_ptr, "0x", 2) == 0) hex_ptr += 2;
                        
                        int hex_len = strlen(hex_ptr);
                        printf("DEBUG: Operations hex length: %d\n", hex_len);
                        
                        // Parse as 32-bit little-endian integers (8 hex chars each)
                        for (int i = 0; i < 4 && (i * 8) < hex_len; i++) {
                            char int_hex[9];
                            strncpy(int_hex, hex_ptr + (i * 8), 8);
                            int_hex[8] = '\0';
                            operations[i] = parse_hex_to_int(int_hex);
                            printf("DEBUG: operations[%d] = %d (from %s)\n", i, operations[i], int_hex);
                        }
                        
                        printf("DEBUG: Parsed operations: [%d, %d, %d, %d]\n", 
                               operations[0], operations[1], operations[2], operations[3]);
                        found_operations = 1;
                    }
                    else if (current_object == 1 && !found_keys) {
                        // Parse keys array - data is little-endian 32-bit integers
                        char* hex_ptr = hex_data;
                        if (strncmp(hex_ptr, "0x", 2) == 0) hex_ptr += 2;
                        
                        int hex_len = strlen(hex_ptr);
                        printf("DEBUG: Keys hex length: %d\n", hex_len);
                        
                        // Parse as 32-bit little-endian integers (8 hex chars each)
                        for (int i = 0; i < 4 && (i * 8) < hex_len; i++) {
                            char int_hex[9];
                            strncpy(int_hex, hex_ptr + (i * 8), 8);
                            int_hex[8] = '\0';
                            keys[i] = parse_hex_to_int(int_hex);
                            printf("DEBUG: keys[%d] = %d (from %s)\n", i, keys[i], int_hex);
                        }
                        
                        printf("DEBUG: Parsed keys: [%d, %d, %d, %d]\n", 
                               keys[0], keys[1], keys[2], keys[3]);
                        found_keys = 1;
                    }
                }
            }
        }
    }
    
    pclose(pipe);
    
    if (!found_operations || !found_keys) {
        printf("Error: Could not find operations or keys in ktest-tool output\n");
        printf("Try running: ktest-tool %s\n", filename);
        printf("to see the actual format of the file.\n");
        return 0;
    }
    
    return 1;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("Usage: %s <ktest_file_path>\n", argv[0]);
        printf("Example: %s test000001.ktest\n", argv[0]);
        printf("Note: Requires ktest-tool to be available in PATH\n");
        return 1;
    }
    
    struct node* root = NULL;
    int operations[4] = {0};
    int keys[4] = {0};
    
    printf("===== Test Case Execution =====\n");
    printf("Reading KTEST file: %s\n\n", argv[1]);
    
    // Read and parse ktest file
    if (!read_ktest_file(argv[1], operations, keys)) {
        return 1;
    }
    
    printf("\nExtracted data:\n");
    printf("Operations: [%d, %d, %d, %d]\n", operations[0], operations[1], operations[2], operations[3]);
    printf("Keys: [%d, %d, %d, %d]\n\n", keys[0], keys[1], keys[2], keys[3]);
    
    // Execute test sequence
    for (int i = 0; i < 4; i++) {
        printf("\n-- Step %d: Operation %d --", i+1, operations[i]);
        
        // Handle invalid operations (constraint violations)
        if (operations[i] < 0 || operations[i] > 4) {
            printf("\nInvalid operation %d (outside range 0-4), skipping", operations[i]);
        } else {
            switch(operations[i]) {
                case 0: // Insert
                    root = insert(root, keys[i]);
                    printf("\nInserted %d", keys[i]);
                    break;
                    
                case 1: // Delete
                    root = deleteNode(root, keys[i]);
                    printf("\nAttempted to delete %d", keys[i]);
                    break;
                    
                case 2: // Search
                    {
                        int found = search(root, keys[i]);
                        printf("\nSearch for %d: %s", keys[i], found ? "FOUND" : "NOT FOUND");
                    }
                    break;
                    
                case 3:; // Min value
                    struct node* min = minValueNode(root);
                    if(min) printf("\nMin value: %d", min->key);
                    else printf("\nMin value: (empty tree)");
                    break;
                    
                case 4:; // Max value
                    struct node* max = maxValueNode(root);
                    if(max) printf("\nMax value: %d", max->key);
                    else printf("\nMax value: (empty tree)");
                    break;
            }
        }
        
        // Display tree after operation
        printf("\nCurrent BST structure:");
        if(root) {
            printf("\n");
            print_tree(root, 0);
        } else {
            printf(" (empty)\n");
        }
        
        // Verify BST properties
        if(isValidBST(root)) {
            printf("BST validation: PASSED\n");
        } else {
            printf("BST validation: FAILED!\n");
        }
    }
    
    // Cleanup
    freeTree(root);
    printf("\n===== Test Completed =====\n");
    return 0;
}
