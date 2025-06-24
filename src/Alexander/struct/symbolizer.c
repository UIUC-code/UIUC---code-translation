#include "complex_struct.h"  // Include struct definitions first
#include "symbolizer.h"
#include <string.h>

void __symbolize_struct_internal(void* ptr, const char* type_name) {
    if (strcmp(type_name, "DeviceState") == 0) {
        DeviceState* ds = (DeviceState*)ptr;

        // Make entire struct symbolic at once
        klee_make_symbolic(ds, sizeof(DeviceState), "DeviceState");

        // Constrain reading_count to valid range
        klee_assume(ds->reading_count <= 5);

        // Don't re-symbolize the readings array since it's already part of the struct
        // The array elements are already symbolic from the struct symbolization above
        
        // Set function pointer to concrete value after symbolization
        ds->calibration_func = NULL;
    }
}
