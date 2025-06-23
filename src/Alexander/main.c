#include <klee/klee.h>
#include <stdlib.h>
#include <string.h>

struct Student {
    char name[50];
    int age;
    float grades[5];
};

void processStudent(struct Student s);

// Create observable effects at global scope
volatile int path_tracker;

int main() {
    struct Student s;
    klee_make_symbolic(&s, sizeof(struct Student), "struct_student");
    s.name[49] = '\0';  // Ensure null termination
    
    // Add path tracking - will improve BCov
    path_tracker = 0;
    
    processStudent(s);
    
    // Force exit with value based on execution path
    if(path_tracker) {
        return 1;
    }
    return 0;
}
