#ifndef SYMBOLIZER_H
#define SYMBOLIZER_H

#include <klee/klee.h>

#define SYMBOLIZE_STRUCT(obj, type) do { \
    __symbolize_struct_internal(&(obj), #type); \
} while (0)

void __symbolize_struct_internal(void* ptr, const char* type_name);

#endif // SYMBOLIZER_H
