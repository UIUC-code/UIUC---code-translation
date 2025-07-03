import sys
from pycparser import c_ast, parse_file
import pycparser_fake_libc

class FuncAndTypeExtractor(c_ast.NodeVisitor):
    def __init__(self):
        # Store collected typedefs and functions
        self.typedefs = []
        self.functions = []
        self.enum_forward_decls = set()
        self.enum_defs = {}

    def visit_Typedef(self, node):
        # Collect typedefs of structs: typedef struct { ... } Name;
        if isinstance(node.type, c_ast.TypeDecl) and isinstance(node.type.type, c_ast.Struct):
            self.typedefs.append(node)

    def visit_FuncDef(self, node):
        # Extract function return type and name
        ret_type = self._get_type(node.decl.type.type)
        func_name = node.decl.name
        params = []
        param_list = node.decl.type.args

        if param_list:
            # For each parameter, get the full type string including parameter name
            for param in param_list.params:
                # Pass param.name to properly format function pointers with names
                ptype = self._get_type(param.type, param.name)
                params.append(ptype)
        self.functions.append((ret_type, func_name, params))
        
    def visit_Enum(self, node):
        if node.name and node.values:  # avoid externs
            self.enum_defs[node.name] = node

    def _get_type(self, node, name=None):
        """
        Recursively construct type string from AST node.
        For function pointer types, inserts the parameter name correctly,
        e.g. int (*func)(int)
        
        Args:
            node: AST node representing the type
            name: optional parameter name to include in the declaration
            
        Returns:
            A string representing the type, including pointer/function pointer syntax
        """

        if isinstance(node, c_ast.TypeDecl):
            # Drill down to the base type, pass down the name
            return self._get_type(node.type, name)

        elif isinstance(node, c_ast.IdentifierType):
            base = ' '.join(node.names)
            # Append the name if provided
            return base if name is None else f"{base} {name}"

        elif isinstance(node, c_ast.PtrDecl):
            # For pointer types:
            # If inner node is FuncDecl, pass name down so that the (*)name
            # syntax is correctly placed for function pointers
            if isinstance(node.type, c_ast.FuncDecl):
                # For function pointers, the name goes inside (*name)
                return self._get_type(node.type, name)
            else:
                # For normal pointers, append '*'
                inner = self._get_type(node.type)
                return f"{inner} *" if name is None else f"{inner} * {name}"

        elif isinstance(node, c_ast.ArrayDecl):
            # Array: append array size after the variable name
            # But name must come before []
            arr_size = ''
            if node.dim:
                if isinstance(node.dim, c_ast.Constant):
                    arr_size = f"[{node.dim.value}]"
                else:
                    arr_size = "[]"
            else:
                arr_size = "[]"
            # Here name must be before [], so we append arr_size to name
            # and recurse to base type
            new_name = f"{name}{arr_size}" if name else arr_size
            return self._get_type(node.type, new_name)

        elif isinstance(node, c_ast.FuncDecl):
            # Function pointer:
            ret = self._get_type(node.type)  # return type without name
            params = []
            if node.args:
                for p in node.args.params:
                    ptype = self._get_type(p.type)
                    params.append(ptype)
            param_list = ", ".join(params) if params else "void"
            if name:
                # Insert parameter name inside (*name)
                return f"{ret} (*{name})({param_list})"
            else:
                # Anonymous function pointer type (no name)
                return f"{ret} (*)({param_list})"

        elif isinstance(node, c_ast.Enum):
            # enum with optional name
            if node.name:
                self.enum_forward_decls.add(node.name)
                return f"enum {node.name}" if name is None else f"enum {node.name} {name}"
            else:
                return "enum" if name is None else f"enum {name}"

        elif isinstance(node, c_ast.Typedef):
            # typedef with optional name
            if node.name:
                return node.name if name is None else f"{node.name} {name}"
            else:
                return "typedef" if name is None else f"typedef {name}"

        elif isinstance(node, c_ast.Struct):
            # struct with optional name
            if node.name:
                return f"struct {node.name}" if name is None else f"struct {node.name} {name}"
            else:
                return "struct" if name is None else f"struct {name}"

        else:
            # fallback
            return "UNKNOWN" if name is None else f"UNKNOWN {name}"


def generate_header(source_path, out_path):
    # Parse C source file using pycparser with fake libc includes
    ast = parse_file(source_path, use_cpp=True,
                     cpp_args=[
                         '-E',
                         f'-I{pycparser_fake_libc.directory}'
                     ])

    extractor = FuncAndTypeExtractor()
    extractor.visit(ast)

    with open(out_path, 'w', encoding='utf-8') as f:
        # Write include guards and standard headers
        f.write("#ifndef GENERATED_FUNCS_H\n#define GENERATED_FUNCS_H\n\n")
        f.write("#include <stddef.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <stdarg.h>\n#include <wchar.h>\n\n")

        # Write all typedef struct definitions
        for td in extractor.typedefs:
            # Skip known system typedefs to avoid conflicts
            if td.name in ("atomic_flag", "atomic_bool"):
                continue
            name = td.name
            struct_decl = td.type.type
            members = []
            if struct_decl.decls:
                for decl in struct_decl.decls:
                    mtype = extractor._get_type(decl.type)
                    mname = decl.name
                    members.append(f"    {mtype} {mname};")
            f.write(f"typedef struct {{\n" + "\n".join(members) + f"\n}} {name};\n\n")

        # Write enum definitions
        for enum_name, enum_node in extractor.enum_defs.items():
            f.write(f"enum {enum_name} {{\n")
            for enumerator in enum_node.values.enumerators:
                f.write(f"    {enumerator.name}")
                if enumerator.value:
                    f.write(f" = {extractor._get_enum_const_value(enumerator.value)}")
                f.write(",\n")
            f.write("};\n\n")

        # Write all function prototypes
        for ret_type, name, params in extractor.functions:
            param_list = ", ".join(params) if params else "void"
            f.write(f"{ret_type} {name}({param_list});\n")

        f.write("\n#endif\n")

    print(f"[+] Header generated at {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 gen_headers.py sample.c include/generated_funcs.h")
        sys.exit(1)

    src_path = sys.argv[1]
    out_path = sys.argv[2]

    generate_header(src_path, out_path)
