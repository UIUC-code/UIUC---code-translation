#include <stdio.h>
#include <string.h>

int my_strcmp(const char* a, const char* b) {
    return strcmp(a, b);
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s string1 string2\n", argv[0]);
        return 1;
    }
    const char *a = argv[1];
    const char *b = argv[2];

    int result = my_strcmp(a, b);
    printf("%d\n", result);

    return 0;
}
