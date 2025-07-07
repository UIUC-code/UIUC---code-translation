"""
KLEE C Code Transformer
Automatically transforms C source code to be compatible with KLEE symbolic execution.
Focuses on making configuration parameters symbolic.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ParamType(Enum):
    BOOL = "BOOL"
    INT = "INT"
    STRING = "STRING"


@dataclass
class ConfigParameter:
    name: str
    type: ParamType
    default_value: str
    min_constraint: Optional[int] = None
    max_constraint: Optional[int] = None
    string_options: Optional[List[str]] = None


@dataclass
class CodeStructure:
    includes: List[str]
    structs: List[str]
    enums: List[str]
    global_vars: List[str]
    functions: Dict[str, str]
    main_function: str
    config_parsing_function: Optional[str]
    config_usage_points: List[Tuple[str, str]]  # (function_name, config_param)


class KLEETransformer:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.config_params: Dict[str, ConfigParameter] = {}
        self.code_structure: Optional[CodeStructure] = None

    def log(self, message):
        if self.verbose:
            print(f"[TRANSFORMER] {message}")

    def parse_config_file(self, config_path: str) -> Dict[str, ConfigParameter]:
        """Parse config.txt to extract parameter definitions."""
        self.log(f"Parsing config file: {config_path}")
        config_params = {}

        try:
            with open(config_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Infer parameter type
                        param_type = self._infer_type(value)

                        # Create parameter with constraints
                        param = ConfigParameter(
                            name=key, type=param_type, default_value=value
                        )

                        # Set type-specific constraints
                        if param_type == ParamType.INT:
                            if key == "query_cache_size":
                                param.min_constraint = 0
                                param.max_constraint = 65536
                            else:
                                param.min_constraint = 0
                                param.max_constraint = 100000
                        elif param_type == ParamType.BOOL:
                            param.min_constraint = 0
                            param.max_constraint = 1
                        elif param_type == ParamType.STRING:
                            # For known string parameters, set options
                            if key == "binlog_format":
                                param.string_options = [
                                    "ROW",
                                    "STATEMENT",
                                    "MIXED",
                                    "OTHER",
                                ]

                        config_params[key] = param
                        self.log(f"Found config parameter: {key} ({param_type.value})")

        except FileNotFoundError:
            self.log(f"Config file not found: {config_path}")

        self.config_params = config_params
        return config_params

    def _infer_type(self, value: str) -> ParamType:
        """Infer parameter type from its value."""
        # Check for boolean
        if value.lower() in ["true", "false", "0", "1"]:
            return ParamType.BOOL

        # Check for integer
        try:
            int(value)
            return ParamType.INT
        except ValueError:
            pass

        # Default to string
        return ParamType.STRING

    def analyze_c_code(self, c_file_path: str) -> CodeStructure:
        """Analyze C code structure and extract components."""
        self.log(f"Analyzing C code: {c_file_path}")

        with open(c_file_path, "r") as f:
            content = f.read()

        structure = CodeStructure(
            includes=self._extract_includes(content),
            structs=self._extract_structs(content),
            enums=self._extract_enums(content),
            global_vars=self._extract_global_vars(content),
            functions=self._extract_functions(content),
            main_function=self._extract_main(content),
            config_parsing_function=self._find_config_parser(content),
            config_usage_points=self._find_config_usage(content),
        )

        self.code_structure = structure
        return structure

    def _extract_includes(self, content: str) -> List[str]:
        """Extract #include statements."""
        pattern = r'#include\s*[<"][^>"]+[>"]'
        includes = re.findall(pattern, content)
        return includes

    def _extract_structs(self, content: str) -> List[str]:
        """Extract struct definitions."""
        # Simplified struct extraction
        pattern = r"typedef\s+struct[^{]*\{[^}]+\}[^;]*;"
        structs = re.findall(pattern, content, re.DOTALL)
        return structs

    def _extract_enums(self, content: str) -> List[str]:
        """Extract enum definitions."""
        pattern = r"typedef\s+enum[^{]*\{[^}]+\}[^;]*;"
        enums = re.findall(pattern, content, re.DOTALL)
        return enums

    def _extract_global_vars(self, content: str) -> List[str]:
        """Extract global variable declarations."""
        # Look for variables declared outside functions
        pattern = (
            r"^(?!.*\bstatic\b)(?!.*\btypedef\b)(?!.*\#).*\b\w+\s+\*?\w+\s*(?:=.*)?;"
        )

        # Remove function bodies to focus on globals
        content_no_funcs = re.sub(r"\{[^{}]*\}", "", content)

        globals_list = []
        for line in content_no_funcs.split("\n"):
            if re.match(pattern, line.strip()) and not line.strip().startswith("//"):
                globals_list.append(line.strip())

        return globals_list

    def _extract_functions(self, content: str) -> Dict[str, str]:
        """Extract function definitions."""
        functions = {}

        # Pattern to match function definitions
        pattern = r"(\w+\s+\*?\w+\s*\([^)]*\)\s*\{)"

        # Find all function starts
        for match in re.finditer(pattern, content):
            func_start = match.start()
            func_signature = match.group(1)

            # Extract function name
            func_name_match = re.search(r"(\w+)\s*\(", func_signature)
            if func_name_match:
                func_name = func_name_match.group(1)

                # Find the matching closing brace
                brace_count = 1
                pos = match.end()

                while brace_count > 0 and pos < len(content):
                    if content[pos] == "{":
                        brace_count += 1
                    elif content[pos] == "}":
                        brace_count -= 1
                    pos += 1

                # Extract complete function
                func_body = content[func_start:pos]
                functions[func_name] = func_body

        return functions

    def _extract_main(self, content: str) -> str:
        """Extract main function."""
        functions = self._extract_functions(content)
        return functions.get("main", "")

    def _find_config_parser(self, content: str) -> Optional[str]:
        """Find the function that parses config file."""
        # Look for functions that open config files
        for func_name, func_body in self._extract_functions(content).items():
            if "fopen" in func_body and (
                "config" in func_name.lower() or "parse" in func_name.lower()
            ):
                return func_name
        return None

    def _find_config_usage(self, content: str) -> List[Tuple[str, str]]:
        """Find where config parameters are used."""
        usage_points = []

        # Look for get_config_var calls
        pattern = r'get_config_var\s*\(\s*"([^"]+)"\s*\)'

        for func_name, func_body in self._extract_functions(content).items():
            for match in re.finditer(pattern, func_body):
                config_name = match.group(1)
                usage_points.append((func_name, config_name))

        return usage_points

    def generate_processed_code(self) -> str:
        """Generate the processed.c file with KLEE integration."""
        self.log("Generating processed C code")

        if not self.code_structure:
            raise ValueError("No code structure analyzed yet")

        # Generate the complete processed.c file
        processed_code = self._generate_header()
        processed_code += self._generate_includes()
        processed_code += self._generate_klee_includes()
        processed_code += self._generate_data_structures()
        # **CHANGE**: Consolidated all injected code generation
        processed_code += self._generate_injected_code()
        processed_code += self._generate_application_functions()
        processed_code += self._generate_main_with_hooks()

        return processed_code

    def _generate_header(self) -> str:
        """Generate file header."""
        return """/*
 * Auto-generated processed.c for KLEE symbolic execution
 * Generated by KLEE Transformer
 * 
 * This file contains the original application logic with VIOLET hooks
 * for making configuration parameters symbolic.
 */

"""

    def _generate_includes(self) -> str:
        """Generate include statements."""
        includes = ["#include <stdio.h>", "#include <stdlib.h>", "#include <string.h>"]

        # Add original includes that aren't duplicates
        for inc in self.code_structure.includes:
            if inc not in includes:
                includes.append(inc)

        return "\n".join(includes) + "\n\n"

    def _generate_klee_includes(self) -> str:
        """Generate KLEE-specific includes."""
        return """#ifdef KLEE_ANALYSIS
#include <klee/klee.h>
#endif

"""

    def _has_param_type_enum(self) -> bool:
        """Check if ParamType enum is already defined in the source code."""
        for enum in self.code_structure.enums:
            if "ParamType" in enum:
                return True
        return False

    def _generate_data_structures(self) -> str:
        """Generate data structures with KLEE extensions."""
        code = "/* ========== Data Structures ========== */\n\n"

        if not self._has_param_type_enum():
            code += """typedef enum {
    INT,
    BOOL,
    STRING
} ParamType;

"""

        for enum in self.code_structure.enums:
            code += enum + "\n\n"

        code += """typedef struct ConfigVar {
    const char *name;
    ParamType type;
    union {
        int int_val;
        int bool_val;
        char *str_val;
    } value;
    struct ConfigVar *next;
#ifdef KLEE_ANALYSIS
    int min_val;
    int max_val;
    void (*make_symbolic)(struct ConfigVar *);
#endif
} ConfigVar;

"""

        # Add global variables
        code += "/* Global Variables */\n"
        code += "ConfigVar *all_sys_vars = NULL;\n\n"

        return code

    def _generate_injected_code(self) -> str:
        """Generates all self-contained, KLEE-aware code to be injected."""

        code = "/* ========== Injected KLEE-Aware Utilities ========== */\n\n"
        code += """
/* A KLEE-aware implementation of strdup.
 * Uses malloc, which KLEE can intercept, to allocate memory within
 * KLEE's symbolic heap. This ensures pointers are valid for KLEE functions.
 */
static char *strdup_internal(const char *s) {
    if (!s) return NULL;
    size_t len = strlen(s) + 1;
    char *new_s = malloc(len);
    if (new_s == NULL) return NULL;
    memcpy(new_s, s, len);
    return new_s;
}

"""

        code += "/* ========== Injected Helper Functions ========== */\n\n"
        code += """ConfigVar *create_var(const char *name, ParamType type, void *value)
{
    ConfigVar *var = (ConfigVar *)malloc(sizeof(ConfigVar));
    if (!var)
    {
        perror("Failed to allocate memory for new variable");
        exit(EXIT_FAILURE);
    }

    var->name = strdup_internal(name); // Use KLEE-aware strdup
    var->type = type;
    switch (type)
    {
    case INT:
        var->value.int_val = *(int *)value;
        break;
    case BOOL:
        var->value.bool_val = *(int *)value;
        break;
    case STRING:
        var->value.str_val = strdup_internal((char *)value); // Use KLEE-aware strdup
        break;
    }
    var->next = NULL;
    return var;
}

ConfigVar *get_config_var(const char *name)
{
    ConfigVar *current = all_sys_vars;
    while (current != NULL)
    {
        if (strcmp(current->name, name) == 0)
        {
            return current;
        }
        current = current->next;
    }
    return NULL; 
}

"""

        code += """/* ========== VIOLET Hooks Implementation ========== */

#ifdef KLEE_ANALYSIS

#define MAX_SYM_CONFIGS 20
static char *target_configs[MAX_SYM_CONFIGS];
static int num_target_configs = 0;

/* Make a configuration variable symbolic */
static void make_config_var_symbolic(ConfigVar *var) {
    if (var == NULL) return;
    
    printf("[VIOLET] Making '%s' symbolic.\\n", var->name);
    
    switch (var->type) {
    case INT: {
        int tmp = var->value.int_val;
        klee_make_symbolic(&tmp, sizeof(tmp), var->name);
        klee_assume(tmp >= var->min_val);
        klee_assume(tmp <= var->max_val);
        var->value.int_val = tmp;
        break;
    }
    case BOOL: {
        int tmp = var->value.bool_val;
        klee_make_symbolic(&tmp, sizeof(tmp), var->name);
        klee_assume(tmp == 0 || tmp == 1);
        var->value.bool_val = tmp;
        break;
    }
    case STRING: {
"""

        for param_name, param in self.config_params.items():
            if param.type == ParamType.STRING and param.string_options:
                code += f"""        if (strcmp(var->name, "{param_name}") == 0) {{
            int choice;
            klee_make_symbolic(&choice, sizeof(choice), "{param_name}_choice");
            klee_assume(choice >= 0 && choice < {len(param.string_options)});
            switch (choice) {{
"""
                for i, option in enumerate(param.string_options):
                    code += f"""            case {i}: free(var->value.str_val); var->value.str_val = strdup_internal("{option}"); break;
"""
                code += """            }
        }
"""
        code += """        break;
    }
    }
}

/* Initialize hooks by assigning function pointers */
void violet_initialize_hooks(void) {
    ConfigVar *current = all_sys_vars;
    while (current != NULL) {
        current->make_symbolic = make_config_var_symbolic;
"""

        for param_name, param in self.config_params.items():
            if param.type in [ParamType.INT, ParamType.BOOL]:
                code += f"""        if (strcmp(current->name, "{param_name}") == 0) {{
            current->min_val = {param.min_constraint};
            current->max_val = {param.max_constraint};
        }}
"""
        code += """        current = current->next;
    }
}

/* Parse environment variable for target configs */
void violet_parse_config_targets(void) {
    const char *targets_str = getenv("VIO_SYM_CONFIGS");
    if (targets_str == NULL) {
        printf("[VIOLET] VIO_SYM_CONFIGS not set. No variables will be made symbolic.\\n");
        return;
    }
    
    printf("[VIOLET] Checking for target configs: %s\\n", targets_str);
    
    /* Check for each discovered config parameter using substring search */
"""
        for param_name in self.config_params.keys():
            code += f"""    if (strstr(targets_str, "{param_name}")) {{
        target_configs[num_target_configs++] = "{param_name}";
    }}
"""
        code += """}

/* Check if a config is targeted for symbolic execution */
static int is_target(const char *name) {
    for (int i = 0; i < num_target_configs; i++) {
        if (strcmp(name, target_configs[i]) == 0) {
            return 1;
        }
    }
    return 0;
}

/* Make target configs symbolic */
void violet_make_target_configs_symbolic(void) {
    printf("[VIOLET] Searching for target configs to make symbolic...\\n");
    ConfigVar *current = all_sys_vars;
    while (current != NULL) {
        if (is_target(current->name)) {
            if (current->make_symbolic) {
                current->make_symbolic(current);
            }
        }
        current = current->next;
    }
}

#else

/* Stub implementations for non-KLEE builds */
void violet_initialize_hooks(void) {}
void violet_parse_config_targets(void) {}
void violet_make_target_configs_symbolic(void) {}

#endif /* KLEE_ANALYSIS */

"""
        return code

    def _generate_application_functions(self) -> str:
        """Generate application functions, filtering out injected helpers."""
        code = "/* ========== Application Functions ========== */\n\n"

        injected_helpers = ["create_var", "get_config_var", "strdup_internal"]

        for func_name, func_body in self.code_structure.functions.items():
            if (
                func_name not in ["main", self.code_structure.config_parsing_function]
                and func_name not in injected_helpers
            ):
                code += func_body + "\n\n"

        code += self._generate_modified_config_parser()

        return code

    def _generate_modified_config_parser(self) -> str:
        """Generate a modified config parser that works with defaults."""
        code = "/* Modified config parser with default value support */\n"
        code += f"static void load_config_with_defaults(const char *config_path) {{\n"
        code += "    /* Default values based on config.txt */\n"

        for param_name, param in self.config_params.items():
            if param.type == ParamType.INT:
                code += f"    int default_{param_name} = {param.default_value};\n"
            elif param.type == ParamType.BOOL:
                code += f"    int default_{param_name} = {param.default_value};\n"
            elif param.type == ParamType.STRING:
                code += f'    char *default_{param_name} = "{param.default_value}";\n'

        has_string_param = any(
            p.type == ParamType.STRING for p in self.config_params.values()
        )
        if has_string_param:
            code += "\n    /* Temporary buffers for parsed string values */\n"
            for param_name, param in self.config_params.items():
                if param.type == ParamType.STRING:
                    code += f"    char parsed_val_{param_name}[256];\n"

        code += "\n"
        code += "    /* Try to load from file, use defaults if not found */\n"
        code += '    FILE *f = fopen(config_path, "r");\n'
        code += "    if (!f) {\n"
        code += '        printf("[VIOLET] Using default configuration values\\n");\n'
        code += "    } else {\n"
        code += "        /* Parse config file */\n"
        code += "        char line[256];\n"
        code += "        while (fgets(line, sizeof(line), f)) {\n"
        code += "            if (line[0] == '#' || line[0] == '\\n') continue;\n"
        code += "            \n"
        code += "            char *eq = strchr(line, '=');\n"
        code += "            if (!eq) continue;\n"
        code += "            \n"
        code += "            *eq = '\\0';\n"
        code += "            char *key = line;\n"
        code += "            char *val = eq + 1;\n"
        code += "            \n"
        code += "            /* Trim whitespace */\n"
        code += "            while (*key && (*key == ' ' || *key == '\\t')) key++;\n"
        code += "            while (*val && (*val == ' ' || *val == '\\t')) val++;\n"
        code += '            val[strcspn(val, "\\n\\r")] = 0;\n'
        code += "            \n"
        code += "            /* Update defaults based on file content */\n"

        for param_name, param in self.config_params.items():
            if param.type == ParamType.STRING:
                code += f'            if (strcmp(key, "{param_name}") == 0) {{\n'
                code += f"                strncpy(parsed_val_{param_name}, val, sizeof(parsed_val_{param_name}) - 1);\n"
                code += f"                parsed_val_{param_name}[sizeof(parsed_val_{param_name}) - 1] = '\\0';\n"
                code += (
                    f"                default_{param_name} = parsed_val_{param_name};\n"
                )
                code += "            }\n"
            else:
                code += f'            if (strcmp(key, "{param_name}") == 0) {{\n'
                code += f"                default_{param_name} = atoi(val);\n"
                code += "            }\n"

        code += "        }\n"
        code += "        fclose(f);\n"
        code += "    }\n"
        code += "    \n"
        code += "    /* Create configuration variables with values */\n"

        params = list(self.config_params.items())
        if params:
            first_param_name, first_param_obj = params[0]
            if first_param_obj.type == ParamType.STRING:
                code += f'    all_sys_vars = create_var("{first_param_name}", {first_param_obj.type.value}, default_{first_param_name});\n'
            else:
                code += f'    all_sys_vars = create_var("{first_param_name}", {first_param_obj.type.value}, &default_{first_param_name});\n'

            if len(params) > 1:
                code += "    ConfigVar *temp = all_sys_vars;\n"
                for param_name, param in params[1:]:
                    if param.type == ParamType.STRING:
                        code += f'    temp->next = create_var("{param_name}", {param.type.value}, default_{param_name});\n'
                    else:
                        code += f'    temp->next = create_var("{param_name}", {param.type.value}, &default_{param_name});\n'
                    code += "    temp = temp->next;\n"

        code += "}\n\n"
        return code

    def _generate_main_with_hooks(self) -> str:
        """Generate main function with VIOLET hooks."""
        code = """/* ========== Main Function with KLEE Integration ========== */

int main(int argc, char *argv[]) {
    printf("=== Starting KLEE-instrumented application ===\\n");
    
    /* Load configuration with defaults */
    const char *config_path = (argc > 1) ? argv[1] : "config.txt";
    load_config_with_defaults(config_path);
    
    printf("Configuration loaded.\\n");
    
#ifdef KLEE_ANALYSIS
    /* VIOLET Hook Point - Right after config parsing */
    violet_initialize_hooks();
    violet_parse_config_targets();
    violet_make_target_configs_symbolic();
#endif
    
    printf("\\n--- Running Application Logic ---\\n");
    
"""
        if any(
            "write_row_to_log" in u for u in self.code_structure.config_usage_points
        ):
            code += "    write_row_to_log();\n"
        if any(
            "query_cache_size" in u for u in self.code_structure.config_usage_points
        ):
            code += "    setup_query_cache();\n"

        code += """
    printf("\\n--- Application Logic Finished ---\\n");

    /* 
     * Correctly free all allocated memory for the configuration list.
     * This is disabled during KLEE analysis, as KLEE manages its own heap
     * and freeing memory can sometimes interfere with its analysis.
     */
#ifndef KLEE_ANALYSIS
    ConfigVar *cur = all_sys_vars;
    while (cur)
    {
        ConfigVar *next = cur->next;
        free((void *)cur->name); // Free the duplicated name
        if (cur->type == STRING && cur->value.str_val) {
            free(cur->value.str_val); // Free the duplicated string value
        }
        free(cur); // Free the struct itself
        cur = next;
    }
#endif /* !KLEE_ANALYSIS */

    return 0;
}
"""
        return code

    def transform_file(
        self, input_file: str, output_file: str, config_file: str = "config.txt"
    ):
        """Main transformation function."""
        self.log(f"Starting transformation: {input_file} -> {output_file}")
        self.parse_config_file(config_file)
        self.analyze_c_code(input_file)
        processed_code = self.generate_processed_code()
        with open(output_file, "w") as f:
            f.write(processed_code)
        self.log(f"Transformation complete: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Transform C code for KLEE symbolic execution"
    )
    parser.add_argument("input", help="Input C source file")
    parser.add_argument(
        "-o", "--output", default="processed.c", help="Output file name"
    )
    parser.add_argument(
        "-c", "--config", default="config.txt", help="Configuration file"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()
    transformer = KLEETransformer(verbose=args.verbose)
    try:
        output_file = transformer.transform_file(args.input, args.output, args.config)
        print(f"Success! Generated: {output_file}")
        print("\nNext steps:")
        print(f"1. Compile to LLVM bitcode:")
        print(
            f"   clang -I /path/to/klee/include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone -DKLEE_ANALYSIS {output_file} -o processed.bc"
        )
        print("\n2. (Optional but Recommended) Link with klee-libc:")
        print(
            f"   llvm-link processed.bc /path/to/klee/build/lib/klee-libc.bca -o processed.linked.bc"
        )

        print(f"\n3. Run KLEE with symbolic configs:")
        print(
            f"   VIO_SYM_CONFIGS=autocommit,flush_at_trx_commit klee processed.bc (or processed.linked.bc)"
        )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
