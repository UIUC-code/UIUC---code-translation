#include <klee/klee.h>

int my_strcmp(const char *a, const char *b) {
    while (*a && (*a == *b)) {
        a++;
        b++;
    }
    return (unsigned char)*a - (unsigned char)*b;
}

int main() {
    const char* options[] = {
        "hello",
        "world",
        "today is a good day",
        "openAI creates amazing tools",
        "klee helps find bugs",
        "symbolic execution rocks",
        "rust is safe and fast",
        "testing is important"
    };
    int idx_a, idx_b;

    klee_make_symbolic(&idx_a, sizeof(idx_a), "idx_a");
    klee_make_symbolic(&idx_b, sizeof(idx_b), "idx_b");

    klee_assume(idx_a >= 0);
    klee_assume(idx_a < 8);
    klee_assume(idx_b >= 0);
    klee_assume(idx_b < 8);

    const char* a = options[idx_a];
    const char* b = options[idx_b];

    int result = my_strcmp(a, b);

    return result;
}
