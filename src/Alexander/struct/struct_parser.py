import clang.cindex
import sys
import re

def parse_array_type(field_type):
    """Parse array type and return base type and dimensions"""
    # Handle cases like "char [50]", "float [5]", etc.
    array_match = re.match(r'(.+?)\s*\[([^\]]+)\]', field_type)
    if array_match:
        base_type = array_match.group(1).strip()
        array_size = array_match.group(2).strip()
        return base_type, f"[{array_size}]", array_size
    return field_type, "", None

def get_type_size(base_type):
    """Get the size of a basic type in bytes"""
    type_sizes = {
        'char': 1,
        'signed char': 1,
        'unsigned char': 1,
        'short': 2,
        'short int': 2,
        'unsigned short': 2,
        'unsigned short int': 2,
        'int': 4,
        'unsigned int': 4,
        'long': 8,
        'long int': 8,
        'unsigned long': 8,
        'unsigned long int': 8,
        'long long': 8,
        'long long int': 8,
        'unsigned long long': 8,
        'unsigned long long int': 8,
        'float': 4,
        'double': 8,
        'long double': 16,
    }
    
    # Clean up the type name
    clean_type = base_type.strip()
    return type_sizes.get(clean_type, 4)  # Default to 4 bytes if unknown

def generate_klee_main(source_file, target_function, output_file):
    # Set the library path for clang
    clang.cindex.Config.set_library_path("/usr/lib/llvm-11/lib/")
    index = clang.cindex.Index.create()
    
    # Parse with better error handling
    try:
        tu = index.parse(source_file, args=['-x', 'c'])
    except Exception as e:
        print(f"Error parsing source file: {e}")
        return
    
    # Check for parsing errors
    for diag in tu.diagnostics:
        if diag.severity >= 3:  # Error level
            print(f"Parse error: {diag.spelling}")
    
    struct_map = {}
    target_param_type = None
    struct_name = None
    
    # Walk through the AST
    for cursor in tu.cursor.walk_preorder():
        if cursor.kind == clang.cindex.CursorKind.STRUCT_DECL:
            current_struct = cursor.spelling
            fields = []
            for child in cursor.get_children():
                if child.kind == clang.cindex.CursorKind.FIELD_DECL:
                    field_type = child.type.spelling
                    field_name = child.spelling
                    fields.append((field_name, field_type))
            if current_struct:
                struct_map[current_struct] = fields
        
        elif (cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL and 
              cursor.spelling == target_function):
            for child in cursor.get_children():
                if child.kind == clang.cindex.CursorKind.PARM_DECL:
                    target_param_type = child.type.spelling
                    # Extract struct name more carefully
                    if 'struct' in target_param_type:
                        # Handle cases like "struct Student *", "struct Student", etc.
                        match = re.search(r'struct\s+(\w+)', target_param_type)
                        if match:
                            struct_name = match.group(1)
                    break
    
    if not struct_name:
        print(f"Error: Could not find struct parameter for function {target_function}")
        print(f"Available structs: {list(struct_map.keys())}")
        return
    
    if struct_name not in struct_map:
        print(f"Error: Struct {struct_name} not found in parsed structs")
        print(f"Available structs: {list(struct_map.keys())}")
        return
    
    fields = struct_map[struct_name]
    if not fields:
        print(f"Error: No fields found for struct {struct_name}")
        return
    
    print(f"Found struct {struct_name} with {len(fields)} fields")
    
    # Generate the KLEE main file
    with open(output_file, 'w') as f:
        f.write("#include <klee/klee.h>\n")
        f.write("#include <stdlib.h>\n")
        f.write("#include <string.h>\n\n")
        
        # Write struct definition with correct syntax
        f.write(f"struct {struct_name} {{\n")
        
        for field_name, field_type in fields:
            base_type, array_dims, _ = parse_array_type(field_type)
            f.write(f"    {base_type} {field_name}{array_dims};\n")
        
        f.write("};\n\n")
        
        # Function declaration
        if '*' in target_param_type:
            f.write(f"void {target_function}(struct {struct_name}* s);\n\n")
        else:
            f.write(f"void {target_function}(struct {struct_name} s);\n\n")
        
        # Main function
        f.write("int main() {\n")
        f.write(f"    struct {struct_name} s;\n\n")
        
        # Write two approaches - whole struct (recommended) and individual fields
        f.write("    // Method 1: Make the entire struct symbolic (recommended)\n")
        f.write(f"    klee_make_symbolic(&s, sizeof(struct {struct_name}), \"struct_{struct_name.lower()}\");\n\n")
        
        # Add null terminator for char arrays
        for field_name, field_type in fields:
            base_type, array_dims, array_size = parse_array_type(field_type)
            if array_dims and 'char' in base_type and array_size and array_size.isdigit():
                array_size_int = int(array_size)
                f.write(f"    s.{field_name}[{array_size_int - 1}] = '\\0';  // Ensure null termination\n")
        
        f.write("\n    /* Alternative: Individual field approach\n")
        f.write("    // Clear the struct first\n")
        f.write("    // memset(&s, 0, sizeof(s));\n\n")
        
        # Generate individual field approach as comments
        for field_name, field_type in fields:
            base_type, array_dims, array_size = parse_array_type(field_type)
            
            if array_dims:  # Array field
                if array_size and array_size.isdigit():
                    element_size = get_type_size(base_type)
                    total_size = int(array_size) * element_size
                    f.write(f"    // klee_make_symbolic(s.{field_name}, {total_size}, \"{field_name}\");\n")
                else:
                    f.write(f"    // klee_make_symbolic(s.{field_name}, sizeof(s.{field_name}), \"{field_name}\");\n")
            
            elif '*' in field_type:  # Pointer field
                f.write(f"    // s.{field_name} = NULL;  // Pointer field\n")
            
            else:  # Regular field
                type_size = get_type_size(base_type)
                f.write(f"    // klee_make_symbolic(&s.{field_name}, {type_size}, \"{field_name}\");\n")
        
        f.write("    */\n\n")
        
        # Call the target function
        if '*' in target_param_type:
            f.write(f"    {target_function}(&s);\n")
        else:
            f.write(f"    {target_function}(s);\n")
        
        f.write("    return 0;\n")
        f.write("}\n")
    
    print(f"Successfully generated {output_file}")

def create_sample_input():
    """Create a sample input file for testing"""
    sample_code = """#include <stdio.h>

struct Student {
    char name[50];
    int age;
    float grades[5];
};

void process_student(struct Student s) {
    printf("Processing student: %s\\n", s.name);
    printf("Age: %d\\n", s.age);
    for (int i = 0; i < 5; i++) {
        printf("Grade %d: %.2f\\n", i+1, s.grades[i]);
    }
}
"""
    
    with open("sample_student.c", "w") as f:
        f.write(sample_code)
    print("Created sample_student.c for testing")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python struct_parser.py <source_file> <target_function> <output_file>")
        print("Example: python struct_parser.py sample_student.c process_student klee_main.c")
        
        # Create sample file if none provided
        create_sample_input()
        print("\\nTry: python struct_parser.py sample_student.c process_student klee_main.c")
        sys.exit(1)
    
    generate_klee_main(sys.argv[1], sys.argv[2], sys.argv[3])
