#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include "qsort.c"
// External function declarations - these are defined in your qsort.c
extern void swap(int *a, int *b);
extern int partition(int arr[], int low, int high);
extern void quickSort(int arr[], int low, int high);

char* extract_value(const char *json, const char *key) {
    char key_pattern[128];
    // Handle both quoted and unquoted keys, and potential whitespace
    snprintf(key_pattern, sizeof(key_pattern), "\"%s\"", key);
    
    const char *key_pos = strstr(json, key_pattern);
    if (!key_pos) {
        // Try without quotes around the key
        key_pos = strstr(json, key);
        if (!key_pos) return NULL;
        key_pos += strlen(key);
    } else {
        key_pos += strlen(key_pattern);
    }
    
    // Skip whitespace and colon
    while (*key_pos && (isspace(*key_pos) || *key_pos == ':')) {
        key_pos++;
    }
    
    // Expect opening quote
    if (*key_pos != '"') return NULL;
    key_pos++; // Skip opening quote
    
    const char *val_start = key_pos;
    const char *val_end = strchr(val_start, '"');
    if (!val_end) return NULL;
    
    size_t len = val_end - val_start;
    char *result = malloc(len + 1);
    if (!result) return NULL;
    
    memcpy(result, val_start, len);
    result[len] = '\0';
    return result;
}

unsigned char* parse_bytes(const char *str, size_t *byte_count) {
    // Handle format: "b'\\x00\\x01...'"
    const char *ptr = str;
    
    if (strncmp(ptr, "b'", 2) == 0 && ptr[strlen(ptr)-1] == '\'') {
        ptr += 2;  // Skip "b'"
    }
    
    // Count how many \x sequences we have
    size_t count = 0;
    const char *temp = ptr;
    while (*temp && *temp != '\'') {
        if (*temp == '\\' && *(temp + 1) == 'x') {
            count++;
            temp += 4;  // Skip \xHH
        } else {
            temp++;
        }
    }
    
    *byte_count = count;
    unsigned char *bytes = malloc(*byte_count);
    if (!bytes) return NULL;
    
    size_t i = 0;
    while (*ptr && *ptr != '\'' && i < count) {
        if (*ptr == '\\' && *(ptr + 1) == 'x') {
            // Parse hex digits
            char hex_str[3] = {ptr[2], ptr[3], '\0'};
            char *endptr;
            bytes[i] = (unsigned char)strtoul(hex_str, &endptr, 16);
            
            if (*endptr != '\0') {
                fprintf(stderr, "Invalid hex digits: %s\n", hex_str);
                free(bytes);
                return NULL;
            }
            i++;
            ptr += 4;  // Skip \xHH
        } else {
            ptr++;
        }
    }
    
    return bytes;
}

int main() {
    const char *dir_path = "data_out_partition";
    DIR *dir = opendir(dir_path);
    if (!dir) {
        fprintf(stderr, "Error opening directory '%s': %s\n", dir_path, strerror(errno));
        return EXIT_FAILURE;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
            continue;
            
        char filepath[1024];
        snprintf(filepath, sizeof(filepath), "%s/%s", dir_path, entry->d_name);
        
        FILE *f = fopen(filepath, "r");
        if (!f) {
            fprintf(stderr, "Error opening file '%s': %s\n", filepath, strerror(errno));
            continue;
        }

        fseek(f, 0, SEEK_END);
        long size = ftell(f);
        fseek(f, 0, SEEK_SET);
        
        char *content = malloc(size + 1);
        if (!content) {
            fclose(f);
            continue;
        }
        
        fread(content, 1, size, f);
        fclose(f);
        content[size] = '\0';
        
        char *arr_str = extract_value(content, "arr");
        char *low_str = extract_value(content, "low");
        char *high_str = extract_value(content, "high");
        
        if (!arr_str || !low_str || !high_str) {
            fprintf(stderr, "JSON extraction failed in %s\n", filepath);
            free(arr_str);
            free(low_str);
            free(high_str);
            free(content);
            continue;
        }
        
        size_t arr_bytes, low_bytes, high_bytes;
        unsigned char *arr_bytes_arr = parse_bytes(arr_str, &arr_bytes);
        unsigned char *low_bytes_arr = parse_bytes(low_str, &low_bytes);
        unsigned char *high_bytes_arr = parse_bytes(high_str, &high_bytes);
        

        
        free(arr_str);
        free(low_str);
        free(high_str);
        free(content);
        
        if (!arr_bytes_arr || !low_bytes_arr || !high_bytes_arr) {
            fprintf(stderr, "Byte parsing failed in %s\n", filepath);
            free(arr_bytes_arr);
            free(low_bytes_arr);
            free(high_bytes_arr);
            continue;
        }

        // Convert byte arrays to integers (little-endian)
        int low = 0, high = 0;
        for (size_t i = 0; i < low_bytes; i++)
            low |= (low_bytes_arr[i] << (i * 8));
        for (size_t i = 0; i < high_bytes; i++)
            high |= (high_bytes_arr[i] << (i * 8));
            
        // Convert byte array to integer array
        if (arr_bytes % sizeof(int) != 0) {
            fprintf(stderr, "Invalid array size: %zu bytes\n", arr_bytes);
            free(arr_bytes_arr);
            free(low_bytes_arr);
            free(high_bytes_arr);
            continue;
        }
        
        int arr_len = arr_bytes / sizeof(int);
        int *arr = (int *)arr_bytes_arr;
        
        printf("Input array: [");
        for (int i = 0; i < arr_len; i++) {
            printf("%d%s", arr[i], (i < arr_len - 1) ? ", " : "");
        }
        printf("]\n");
        
        printf("Sorting range: low=%d, high=%d\n", low, high);
        
        // Validate bounds
        if (low < 0 || high >= arr_len || low > high) {
            fprintf(stderr, "Invalid bounds: low=%d, high=%d, arr_len=%d\n", low, high, arr_len);
            free(arr_bytes_arr);
            free(low_bytes_arr);
            free(high_bytes_arr);
            continue;
        }
        
        // Call your partition function from qsort.c
        int pivot_index = partition(arr, low, high);
        
        printf("Pivot index: %d\n", pivot_index);
        printf("\n");
        
        free(arr_bytes_arr);
        free(low_bytes_arr);
        free(high_bytes_arr);
    }
    
    closedir(dir);
    return EXIT_SUCCESS;
}
