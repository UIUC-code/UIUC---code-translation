#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "qsort.h"

void print_array(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int is_sorted(int arr[], int size) {
    for (int i = 0; i < size - 1; i++) {
        if (arr[i] > arr[i + 1]) return 0;
    }
    return 1;
}

int parse_ktest_with_tool(const char* filename, int operations[], int max_ops) {
    char command[512];
    snprintf(command, sizeof(command), "ktest-tool %s", filename);
    
    FILE* pipe = popen(command, "r");
    if (!pipe) return -1;
    
    char line[1024];
    
    while (fgets(line, sizeof(line), pipe)) {
        if (strstr(line, "hex") && strstr(line, "0x")) {
            char* hex_start = strstr(line, "0x");
            if (hex_start) {
                char hex_data[256];
                if (sscanf(hex_start, "%255s", hex_data) == 1) {
                    // Skip "0x" prefix
                    char* hex_ptr = hex_data + 2;
                    int hex_len = strlen(hex_ptr);
                    
                    // Parse hex as little-endian 32-bit integers
                    int num_ops = 0;
                    for (int i = 0; i < max_ops && (i * 8) < hex_len; i++) {
                        char int_hex[9] = {0};
                        int chars = (hex_len - (i * 8) >= 8) ? 8 : hex_len - (i * 8);
                        strncpy(int_hex, hex_ptr + (i * 8), chars);
                        
                        uint32_t value = 0;
                        // Parse little-endian: reverse byte order
                        for (int j = 0; j < chars; j += 2) {
                            char byte_str[3] = {int_hex[j], int_hex[j+1], 0};
                            uint32_t byte_val = strtoul(byte_str, NULL, 16);
                            value |= (byte_val << ((j/2) * 8));
                        }
                        
                        operations[i] = (int)value;
                        num_ops++;
                    }
                    
                    pclose(pipe);
                    return num_ops;
                }
            }
        }
    }
    
    pclose(pipe);
    return -1;
}

int parse_ktest_binary(const char* filename, int operations[], int max_ops) {
    FILE *f = fopen(filename, "rb");
    if (!f) return -1;

    uint32_t magic, version, num_args, num_objects;
    
    if (fread(&magic, sizeof(uint32_t), 1, f) != 1 ||
        fread(&version, sizeof(uint32_t), 1, f) != 1 ||
        fread(&num_args, sizeof(uint32_t), 1, f) != 1 ||
        fread(&num_objects, sizeof(uint32_t), 1, f) != 1) {
        fclose(f);
        return -1;
    }

    // Skip arguments
    for (uint32_t i = 0; i < num_args; i++) {
        uint32_t arg_len;
        if (fread(&arg_len, sizeof(uint32_t), 1, f) != 1) {
            fclose(f);
            return -1;
        }
        fseek(f, arg_len, SEEK_CUR);
    }

    // Read first object
    if (num_objects > 0) {
        uint32_t name_len;
        if (fread(&name_len, sizeof(uint32_t), 1, f) != 1) {
            fclose(f);
            return -1;
        }
        fseek(f, name_len, SEEK_CUR);

        uint32_t obj_size;
        if (fread(&obj_size, sizeof(uint32_t), 1, f) != 1) {
            fclose(f);
            return -1;
        }

        if (obj_size % sizeof(int) == 0) {
            int count = obj_size / sizeof(int);
            int actual_count = (count > max_ops) ? max_ops : count;
            
            if (fread(operations, sizeof(int), actual_count, f) == actual_count) {
                fclose(f);
                return actual_count;
            }
        }
    }

    fclose(f);
    return -1;
}

void process_ktest(const char *filename) {
    int operations[10];
    int num_ops;
    
    // Try binary parsing first
    num_ops = parse_ktest_binary(filename, operations, 10);
    
    // If binary fails, try ktest-tool
    if (num_ops <= 0) {
        num_ops = parse_ktest_with_tool(filename, operations, 10);
    }
    
    if (num_ops > 0) {
        printf("Input:  ");
        print_array(operations, num_ops);
        
        int *sorted_arr = malloc(num_ops * sizeof(int));
        memcpy(sorted_arr, operations, num_ops * sizeof(int));
        
        quickSort(sorted_arr, 0, num_ops - 1);
        
        printf("Output: ");
        print_array(sorted_arr, num_ops);
        
        printf("Result: %s\n", is_sorted(sorted_arr, num_ops) ? "PASS" : "FAIL");
        printf("\n");
        
        free(sorted_arr);
    } else {
        printf("Failed to parse ktest file\n");
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <path_to.ktest>\n", argv[0]);
        return 1;
    }
    
    process_ktest(argv[1]);
    return 0;
}
