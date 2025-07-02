import json
import sys
import os
import re

type_size_map = {
    "int": 4,
    "unsigned int": 4,
    "char": 1,
    "char*": 8,
    "const char*": 8,
    "float": 4,
    "double": 8,
    "long": 8,
    "short": 2,
    "vector": 64,
}

def declare_symbolic_variable(ptype: str, pname: str, handlers_info: list[dict]) -> list[str]:
    """Declare a symbolic variable for KLEE.

    Args:
        ptype (str): The type of the variable.
        pname (str): The name of the variable.
        handlers_info (list[dict]): Information about function handlers.

    Returns:
        list[str]: The lines of code to declare the symbolic variable.
    """
    lines = []

    # Handle function pointer types, e.g. void (*)(int)
    match_func_ptr = re.match(r'(\w[\w\s\*]+)\s*\(\s*\*\s*\)\s*\(([^)]*)\)', ptype)
    if match_func_ptr:
        ret_type = match_func_ptr.group(1).strip()
        arg_types_str = match_func_ptr.group(2).strip()
        arg_types = [a.strip() for a in arg_types_str.split(',')] if arg_types_str else []

        # Store function pointer info for generating handlers and dispatch
        handlers_info.append({
            "pname": pname,
            "ret_type": ret_type,
            "arg_types": arg_types,
        })
        
        # No direct variable declaration here; will declare selector & dispatch in main
        return []

    # char[N] pattern
    match_char_array = re.match(r'char\[(\d+)\]', ptype)

    if ptype.endswith('[]'):
        base_type = ptype[:-2].strip()
        size = type_size_map.get(base_type, 64)
        lines.append(f'  {base_type} {pname}[{size}];')
        lines.append(f'  klee_make_symbolic({pname}, sizeof({pname}), "{pname}");')
    elif match_char_array:
        size = match_char_array.group(1)
        lines.append(f'  char {pname}[{size}];')
        lines.append(f'  klee_make_symbolic({pname}, sizeof({pname}), "{pname}");')
    elif '*' in ptype:
        base_type = ptype.replace('*', '').strip()
        size = type_size_map.get(base_type, 64)
        lines.append(f'  {base_type} {pname}[{size}];')
        lines.append(f'  klee_make_symbolic({pname}, sizeof({pname}), "{pname}");')
    else:
        lines.append(f'  {ptype} {pname};')
        lines.append(f'  klee_make_symbolic(&{pname}, sizeof({pname}), "{pname}");')
    return lines

def generate_handlers_code(handlers_info):
    """Generate KLEE handler functions and symbolic dispatch code.

    Args:
        handlers_info (list[dict]): Information about function handlers.

    Returns:
        tuple[str, str]: The generated handler functions and selector code.
    """

    if handlers_info is None or len(handlers_info) == 0:
        return None, None
    
    handler_funcs = []
    selector_code = []

    for idx, info in enumerate(handlers_info):
        pname = info["pname"]
        ret_type = info["ret_type"]
        arg_types = info["arg_types"]

        # Create two empty handler functions
        handler_name_0 = f"{pname}_handler0"
        handler_name_1 = f"{pname}_handler1"
        args_str = ", ".join(arg_types) if arg_types and arg_types[0] != '' else "void"
        handler_funcs.append(f"{ret_type} {handler_name_0}({args_str}) {{}}")
        handler_funcs.append(f"{ret_type} {handler_name_1}({args_str}) {{}}")

        # Declare symbolic selector variable and constrain it to [0,1]
        selector_var = f"{pname}_selector"
        selector_code.append(f"  int {selector_var};")
        selector_code.append(f"  klee_make_symbolic(&{selector_var}, sizeof({selector_var}), \"{selector_var}\");")
        selector_code.append(f"  klee_assume({selector_var} >= 0);")
        selector_code.append(f"  klee_assume({selector_var} < 2);")

        # Dispatch function pointer using ternary operator based on selector
        dispatch_line = f"  {ret_type} (*{pname})({args_str}) = {selector_var} == 0 ? {handler_name_0} : {handler_name_1};"
        selector_code.append(dispatch_line)

    return "\n".join(handler_funcs), "\n".join(selector_code)

def generate_klee_stub(func):
    func_name = func["name"]
    params = func["parameters"]

    header_file = "generated_funcs.h"
    
    handlers_info = []

    lines = []
    lines.append('#include <klee/klee.h>')
    lines.append(f'#include "{header_file}"')
    lines.append('')
    lines.append('int main() {')

    used_names = set()
    var_names = []

    # Declare symbolic vars
    for p in params:
        ptype = p["type"]
        pname = p["name"] or "param"
        base_name = pname
        idx = 1
        while pname in used_names:
            pname = f"{base_name}{idx}"
            idx += 1
        used_names.add(pname)
        var_names.append(pname)
        lines.extend(declare_symbolic_variable(ptype, pname, handlers_info))

    # Add assumptions (example for size)
    for p in params:
        pname = p["name"]
        if pname and "size" in pname.lower():
            lines.append(f'  klee_assume({pname} >= 0);')
            matched_array = next((v for v in var_names if isinstance(v, str) and '[' in v or 'arr' in v or 'array' in v), None)
            if matched_array:
                lines.append(f'  klee_assume({pname} <= sizeof({matched_array}) / sizeof({matched_array}[0]));')
            # else:
            #     lines.append(f'  klee_assume({pname} <= 64);  // fallback max')


    # Generate handler functions & symbolic dispatch for function pointers
    handler_code, selector_code = generate_handlers_code(handlers_info)
    
    if handler_code is not None and selector_code is not None:
        # Insert handlers before main
        lines.insert(2, handler_code)
        # Insert selector code after variable declarations in main
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip() == 'int main() {':
                insert_pos = i + 1
                break
        lines = lines[:insert_pos] + [selector_code] + lines[insert_pos:]
    
    call_params = ', '.join(var_names)
    lines.append(f'  {func_name}({call_params});')
    lines.append('  return 0;')
    lines.append('}')

    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 gen_klee_stubs.py functions.json klee_stubs_dir")
        sys.exit(1)

    json_path = sys.argv[1]
    output_dir = sys.argv[2]

    os.makedirs(output_dir, exist_ok=True)

    with open(json_path, 'r', encoding='utf-8') as f:
        functions = json.load(f)

    for func in functions:
        stub_code = generate_klee_stub(func)
        filename = os.path.join(output_dir, f"{func['name']}_klee_stub.c")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(stub_code)

    print(f"KLEE stubs generated in directory: {output_dir}")
