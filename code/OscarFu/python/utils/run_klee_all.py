import os
import shutil
import subprocess

def clear_klee_outputs(klee_output_base):
    if os.path.exists(klee_output_base):
        for entry in os.listdir(klee_output_base):
            path = os.path.join(klee_output_base, entry)
            if os.path.isdir(path):
                print(f"[-] Removing old output directory: {path}")
                shutil.rmtree(path)

def link_stub_with_sample(llvm_bc_path, sample_bc_path, builtin_bc_path, linked_bc_path):
    os.makedirs(os.path.dirname(linked_bc_path), exist_ok=True)
    print(f"[+] Linking {llvm_bc_path} + {sample_bc_path} + {builtin_bc_path} -> {linked_bc_path}")
    subprocess.run(
        ["llvm-link", sample_bc_path, llvm_bc_path, builtin_bc_path, "-o", linked_bc_path],
        check=True
    )

def run_klee_on_bc_files(llvm_bc_dir, sample_bc_path, builtin_bc_path, linked_bc_out_dir, klee_output_base="klee-out"):
    llvm_bc_files = [f for f in os.listdir(llvm_bc_dir) if f.endswith(".bc")]
    src_idx = 0
    for i, llvm_bc_file in enumerate(llvm_bc_files):
        llvm_bc_path = os.path.join(llvm_bc_dir, llvm_bc_file)
        linked_bc_path = os.path.join(linked_bc_out_dir, f"{llvm_bc_file[:-3]}_linked.bc")
        
        print(f"[{i+1}/{len(llvm_bc_files)}] Processing {llvm_bc_file}...")
        
        # Step 1: link
        if os.path.basename(llvm_bc_path) == os.path.basename(sample_bc_path) or os.path.basename(llvm_bc_path) == os.path.basename(builtin_bc_path):
            print(f"[!] Skipping self-link: {llvm_bc_file}")
            continue
        try:
            link_stub_with_sample(llvm_bc_path, sample_bc_path, builtin_bc_path, linked_bc_path)
        except subprocess.CalledProcessError as e:
            print(f"[!] Linking failed for {llvm_bc_file}: {e}")
            continue

        # Step 2: run KLEE
        output_dir = os.path.join(klee_output_base, f"{src_idx:03d}_{llvm_bc_file[:-3]}")
        print(f"[+] Running KLEE on {linked_bc_path} -> Output: {output_dir}")
        try:
            subprocess.run(
                ["klee", "-output-dir=" + output_dir, linked_bc_path],
                check=True
            )
            src_idx += 1
        except subprocess.CalledProcessError as e:
            print(f"[!] KLEE failed on {llvm_bc_file}: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python3 utils/run_klee_all.py <llvm_bc_directory> <linked_bc_output_dir> <klee_output_base>")
        sys.exit(1)

    llvm_bc_directory = os.path.abspath(sys.argv[1])
    linked_bc_output_dir = os.path.abspath(sys.argv[2])
    klee_output_base = os.path.abspath(sys.argv[3])
    linked_bc_output_dir = os.path.abspath(sys.argv[2])
    klee_output_base = os.path.abspath(sys.argv[3])

    os.makedirs(linked_bc_output_dir, exist_ok=True)
    os.makedirs(klee_output_base, exist_ok=True)

    # clear old KLEE outputs
    clear_klee_outputs(klee_output_base)


    # run KLEE on all stub.bc files
    run_klee_on_bc_files(
        llvm_bc_dir=llvm_bc_directory,
        sample_bc_path=os.path.join(llvm_bc_directory, "sample.bc"),
        builtin_bc_path=os.path.join(llvm_bc_directory, "klee_builtin_stub.bc"),
        linked_bc_out_dir=linked_bc_output_dir,
        klee_output_base=klee_output_base
    )
