# KLEE Symbolic Execution with C Function Extractor in Python (2025.07.02)
This code space contains tools and scripts for symbolic execution testing of C code using KLEE. The workflow includes extracting function signatures, generating KLEE stubs, compiling to LLVM bitcode, and running KLEE for automated testing.

---

## 🐳 Docker Setup

I provided a Docker environment with Clang, KLEE, and Python dependencies pre-installed for easy and consistent setup.

### 1. Build the Docker Image

Run this command in the repository root where your `Dockerfile.klee-clang` is located:

```bash
docker build -t klee-clang -f Dockerfile.klee-clang .
```

### 2. Run the Docker Container

```bash
docker run --rm -it --ulimit stack=-1:-1 -v <path-to-your-code-folder>:/workspace klee-clang bash
```

>Replace <path-to-your-code-folder> with the full path to your source code directory on your host machine.

Inside the container, your code will be available at /workspace

### 3. Setup Inside Container
Once inside the container shell:

Install Python dependencies required by utility scripts:

```bash
pip install -r requirements.txt
```
## End-to-End Workflow
>You can run the whole default pipeline with the following command:

```bash
bash run_default_pipeline.sh 
```
---

## Step-by-step Workflow

>Or execute these commands in order to prepare and run KLEE tests:

1. **Extract function information from your C source:**

```bash
python3 utils/extract_funcs.py raw_c/sample.c functions.json
```

This step uses Clang AST (`clang.cindex`) to extract function declarations, parameter types, and pointers. The output is saved as `functions.json`.

2. **Generate KLEE stub C files from the extracted functions:**

```bash
python3 utils/gen_klee_stubs.py functions.json klee_stubs/src_c
```

This creates stub source files under `klee_stubs/src_c`, one for each extracted function. Each stub includes symbolic initialization of function arguments and intelligent handling of complex types such as arrays and function pointers.

e.g. Function Pointer Handling

For functions that accept a function pointer (e.g., `void for_each(int* arr, int size`, `void (*func)(int));`), the system automatically:

Generates multiple candidate callback stubs:

```c
void func_handler0(int x) {}
void func_handler1(int x) {}
```

Adds a symbolic selector with constraints:

```c
int func_selector;
klee_make_symbolic(&func_selector, sizeof(func_selector), "func_selector");
klee_assume(func_selector >= 0);
klee_assume(func_selector < 2);
```

Assigns the callback using a symbolic dispatch:

```c
void (*func)(int) = func_selector == 0 ? func_handler0 : func_handler1;
```

3. **Generate the header file with function declarations:**

```bash
python3 utils/gen_headers.py raw_c/sample.c include/generated_funcs.h
```

>Currently implemented using `pycparser`. Consider replacing it with a Clang-based header generator for consistency with `utils/extract_funcs.py`.

This generates `generated_funcs.h` for KLEE stubs and compilation.

4. **Compile stubs and source files to LLVM bitcode:**

```bash
python3 utils/compile_stubs.py ./include/ ./raw_c/ ./klee_stubs/src_c/ ./klee_stubs/llvm_bc
```

This compiles and places `.bc` files into `klee_stubs/llvm_bc`.

5. **Run KLEE on linked LLVM bitcode files and collect outputs:**

```bash
python3 utils/run_klee_all.py klee_stubs/llvm_bc/ klee_stubs/llvm_bc_linked/ klee-out/
```

This links the bitcode files, runs KLEE, and stores test outputs under `klee-out/`.

---

## 📁 Directory Structure Overview

```
.
├── raw_c/
│   ├── sample.c            # Your original C source files
│   └── klee_builtin_stub.c # Standard lib/self-defined lib definitions
├── include/
│   └── generated_funcs.h   # Auto-generated header with function declarations
├── klee_stubs/
│   ├── src_c/              # Generated KLEE stub C files
│   ├── llvm_bc/            # Compiled LLVM bitcode files (.bc)
│   └── llvm_bc_linked/     # Linked LLVM bitcode files ready for KLEE
├── klee-out/               # KLEE symbolic execution output and tests
├── functions.json          # Extracted functions info file
├── requirements.txt        # Python dependencies
└── utils/                  # Utility scripts for extraction, stub generation, compiling, running
```

---

## Additional notes

In this code, I've encountered some problems like:

* **Undefined reference warnings:** May occur for standard library functions like `sqrt`, `strcpy`. Consider providing simple stub implementations like `klee_builtin_stub.c` manually if necessary.
* **Memory errors:** Check your symbolic variable sizes and array bounds in stubs and assumptions. Sometimes might be hard-coded.
* **Function pointer errors:** Ensure symbolic function pointer handling is correctly stubbed and constrained.
