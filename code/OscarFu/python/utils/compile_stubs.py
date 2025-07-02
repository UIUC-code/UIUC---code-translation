import subprocess
import sys
import os
from tqdm import tqdm

if len(sys.argv) != 5:
    print("Usage: python3 compile_stubs.py <INCLUDE_DIR> <RAW_C_DIR> <SRC_C_DIR> <OUT_BC_DIR>")
    sys.exit(1)

include_dir = sys.argv[1]
raw_c_dir = os.path.abspath(sys.argv[2])
src_c_dir = os.path.abspath(sys.argv[3])
out_dir = os.path.abspath(sys.argv[4])

os.makedirs(out_dir, exist_ok=True)

def compile_c_to_bc(src_path, bc_path, include_dir):
    print(f"[+] Compiling {src_path} → {bc_path}")
    cmd = ["clang", "-I", include_dir, "-emit-llvm", "-c", src_path, "-o", bc_path]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"[!] Compilation failed for {src_path}")
        sys.exit(1)

# 1. complile sample.c
sample_c_path = os.path.join(raw_c_dir, "sample.c")
sample_bc_path = os.path.join(out_dir, "sample.bc")
if os.path.exists(sample_c_path):
    compile_c_to_bc(sample_c_path, sample_bc_path, include_dir)
else:
    print(f"[!] sample.c not found in {raw_c_dir}")

# 2. compile klee_builtin_stubs.c
builtin_stub_c_path = os.path.join(raw_c_dir, "klee_builtin_stub.c")
builtin_stub_bc_path = os.path.join(out_dir, "klee_builtin_stub.bc")
if os.path.exists(builtin_stub_c_path):
    compile_c_to_bc(builtin_stub_c_path, builtin_stub_bc_path, include_dir)
else:
    print(f"[!] klee_builtin_stub.c not found in {raw_c_dir}")

# 3. compile all *_klee_stub.c
stub_files = [f for f in os.listdir(src_c_dir) if f.endswith("_klee_stub.c")]
stub_files = [os.path.join(src_c_dir, f) for f in stub_files]

for src in tqdm(stub_files, desc="Compiling stubs"):
    base_name = os.path.basename(src)[:-2]  # strip '.c'
    out = os.path.join(out_dir, base_name + ".bc")
    compile_c_to_bc(src, out, include_dir)

print(f"✅ All stubs, sample.c, and builtin stubs compiled successfully into {out_dir}.")
