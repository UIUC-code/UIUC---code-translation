#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include "qsort.c"
// External function from qsort.c
extern void swap(int *a, int *b);

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
    const char *dir_path = "data_out_swap";
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
        
        char *a_str = extract_value(content, "a");
        char *b_str = extract_value(content, "b");
        
        if (!a_str || !b_str) {
            fprintf(stderr, "JSON extraction failed in %s\n", filepath);
            free(a_str);
            free(b_str);
            free(content);
            continue;
        }
        
        size_t a_bytes, b_bytes;
        unsigned char *a_bytes_arr = parse_bytes(a_str, &a_bytes);
        unsigned char *b_bytes_arr = parse_bytes(b_str, &b_bytes);
        
        free(a_str);
        free(b_str);
        free(content);
        
        if (!a_bytes_arr || !b_bytes_arr) {
            fprintf(stderr, "Byte parsing failed in %s\n", filepath);
            free(a_bytes_arr);
            free(b_bytes_arr);
            continue;
        }

        // Convert byte arrays to integer arrays (little-endian)
        // For swap, we expect each to be an integer array
        if (a_bytes % sizeof(int) != 0 || b_bytes % sizeof(int) != 0) {
            fprintf(stderr, "Invalid byte size: a=%zu, b=%zu (not divisible by %zu)\n", 
                    a_bytes, b_bytes, sizeof(int));
            free(a_bytes_arr);
            free(b_bytes_arr);
            continue;
        }
        
        int a_len = a_bytes / sizeof(int);
        int b_len = b_bytes / sizeof(int);
        int *a_arr = (int *)a_bytes_arr;
        int *b_arr = (int *)b_bytes_arr;
        
        printf("Input a: [");
        for (int i = 0; i < a_len; i++) {
            printf("%d%s", a_arr[i], (i < a_len - 1) ? ", " : "");
        }
        printf("]\n");
        
        printf("Input b: [");
        for (int i = 0; i < b_len; i++) {
            printf("%d%s", b_arr[i], (i < b_len - 1) ? ", " : "");
        }
        printf("]\n");
        
        // Call swap on each corresponding pair of elements
        int min_len = (a_len < b_len) ? a_len : b_len;
        for (int i = 0; i < min_len; i++) {
            swap(&a_arr[i], &b_arr[i]);
        }
        
        printf("Output a: [");
        for (int i = 0; i < a_len; i++) {
            printf("%d%s", a_arr[i], (i < a_len - 1) ? ", " : "");
        }
        printf("]\n");
        
        printf("Output b: [");
        for (int i = 0; i < b_len; i++) {
            printf("%d%s", b_arr[i], (i < b_len - 1) ? ", " : "");
        }
        printf("]\n");
        
        free(a_bytes_arr);
        free(b_bytes_arr);
    }
    
    closedir(dir);
    return EXIT_SUCCESS;
}
