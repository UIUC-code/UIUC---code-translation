import sys
import json

from clang.cindex import Config
Config.set_library_file("/usr/lib/llvm-14/lib/libclang.so")

from clang import cindex


def extract_functions(source_file, clang_args=None):
    if clang_args is None:
        clang_args = ['-x', 'c', '-std=c11']

    index = cindex.Index.create()

    try:
        tu = index.parse(source_file, args=clang_args)
    except cindex.TranslationUnitLoadError as e:
        print(f"[Error] Failed to parse source file '{source_file}': {e}", file=sys.stderr)
        sys.exit(1)

    functions = []

    def visit(node):
        if node.kind == cindex.CursorKind.FUNCTION_DECL:
            # skip static functions（not global scope）
            if node.storage_class == cindex.StorageClass.STATIC:
                return
            
            # only include functions with definitions (not just declarations)
            if not node.is_definition():
                return

            func = {
                "name": node.spelling,
                "return_type": node.result_type.spelling,
                "parameters": [],
                "location": f"{node.location.file}:{node.location.line}"
            }

            for c in node.get_children():
                if c.kind == cindex.CursorKind.PARM_DECL:
                    func["parameters"].append({
                        "name": c.spelling,
                        "type": c.type.spelling
                    })

            functions.append(func)

        # recursively visit child nodes
        for child in node.get_children():
            visit(child)

    visit(tu.cursor)
    return functions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_funcs.py <source_file.c>")
        sys.exit(1)

    source_path = sys.argv[1]
    functions = extract_functions(source_path)
    json_path = sys.argv[2]
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(functions, f, indent=2, ensure_ascii=False)

    print(f"[+] Extracted {len(functions)} functions to {json_path}")
