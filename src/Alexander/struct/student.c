#include "student.h"

// Global tracking variables
volatile int age_invalid = 0;
volatile int grades_invalid = 0;
volatile float grade_sum = 0.0f;
extern volatile int path_tracker; // From main.c

void processStudent(struct Student s) {
    // Age check with side effect
    if(s.age < 0 || s.age > 120) {
        age_invalid = 1;
        path_tracker |= 1;  // Set flag bit 0
    }
    
    // Grade processing
    for(int i = 0; i < 5; i++) {
        if(s.grades[i] < 0.0) {
            grades_invalid = 1;
            path_tracker |= (1 << (i+1));  // Set bits 1-5
        }
        grade_sum += s.grades[i];
    }
}
