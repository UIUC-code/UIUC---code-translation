import os
import subprocess
from pathlib import Path

MODIFIED_SRC_DIR = Path("modified_src")
BC_DIR = Path("bitcode")

def compile_to_bitcode():
    """编译修改后的源文件为LLVM Bitcode"""
    os.makedirs(BC_DIR, exist_ok=True)
    
    compilers = ["clang-14", "clang-13", "clang-12", "clang-11", "clang", "cc", "gcc"]
    clang_cmd = None
    
    for compiler in compilers:
        if subprocess.run(["which", compiler], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            clang_cmd = compiler
            print(f"Using compiler: {clang_cmd}")
            break
    
    if not clang_cmd:
        print("Error: No C compiler found")
        exit(1)
    
    for src_file in MODIFIED_SRC_DIR.glob("*.c"):
        print(f"Compiling {src_file.name} to bitcode...")
        bc_file = BC_DIR / (src_file.stem + ".bc")
        
        cmd = [
            clang_cmd,
            "-I", "src",
            "-c", "-g", "-O0", "-emit-llvm",
            str(src_file),
            "-o", str(bc_file)
        ]
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed: {e}")
            print("Trying with simpler options...")
            
            simple_cmd = [
                clang_cmd,
                "-I", "src",
                "-c", "-g",
                str(src_file),
                "-o", str(bc_file)
            ]
            subprocess.run(simple_cmd, check=True)

if __name__ == "__main__":
    compile_to_bitcode()
