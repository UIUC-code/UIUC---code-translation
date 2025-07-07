import os
import json
import re
import subprocess
import shutil
import sys
from pathlib import Path

# Setup directories
SRC_DIR = Path("src")
MODIFIED_SRC_DIR = Path("modified_src")
TARGETS_FILE = "targets.json"
KLEE_HEADER = "#include <klee/klee.h>"

def add_klee_header(content):
    """Ensure content includes KLEE header"""
    if not re.search(r'#\s*include\s*<klee/klee\.h>', content):
        return KLEE_HEADER + "\n" + content
    return content

def transform_main(body):
    """
    Transform main function body:
    - Only convert variables with // KLEE_INPUT annotation
    - Remove initializers and add klee_make_symbolic calls
    """
    # This will find declarations with KLEE_INPUT annotation
    annotations = re.finditer(
        r'((?:(?:const\s+)?[a-zA-Z_][\w\s*]*)\s*[a-zA-Z_]\w*\s*(\[\d*\]\s*)?)\s*=\s*[^;]+)\s*;\s*(?://\s*KLEE_INPUT|/\*\s*KLEE_INPUT\s*\*/)',
        body
    )
    
    replacements = []
    for ann in annotations:
        full_decl = ann.group(1).strip()
        var_decl = ann.group(1).split('=')[0].strip()
        array_dim = ann.group(2).strip() if ann.group(2) else ""
        
        # Extract base variable name
        match = re.search(r'(\w+)\s*$', var_decl)
        if match:
            var_name = match.group(1)
            
            # For array declarations
            if array_dim:
                replacement = f"{var_decl};\n    klee_make_symbolic({var_name}, sizeof({var_name}), \"{var_name}\");"
            else:  # Scalar/pointer declarations
                replacement = f"{var_decl};\n    klee_make_symbolic(&{var_name}, sizeof({var_name}), \"{var_name}\");"
            
            # Add to replacements list
            replacements.append((full_decl + ';', replacement))
    
    # Apply replacements in reverse order
    for original, new in reversed(replacements):
        body = body.replace(original, new)
    
    return body

def preprocess_file(file_path, modified_dir):
    """Preprocess single C file"""
    print(f"Processing {file_path.name}...")
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Add KLEE header if missing
    content = add_klee_header(content)
    
    # Extract main function body if exists
    main_match = re.search(
        r'(int\s+main\s*\([^{]*?\)\s*\{)([\s\S]*?)(\})', 
        content
    )
    
    if main_match:
        prefix = main_match.group(1)
        main_body = main_match.group(2)
        suffix = main_match.group(3)
        
        # Transform annotated variables
        transformed_body = transform_main(main_body)
        
        # Reconstruct content
        content = content.replace(main_body, transformed_body, 1)
    
    # Save modified source file
    modified_path = modified_dir / file_path.name
    with open(modified_path, "w") as f:
        f.write(content)
    
    # Extract target functions
    targets = []
    for match in re.finditer(r'/\*\s*KLEE_TARGET:\s*(\w+)', content):
        targets.append(match.group(1))
    
    return targets, modified_path

def install_ctags():
    """Install ctags tool if missing"""
    if shutil.which("ctags"):
        return True
    
    print("Installing ctags...")
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "universal-ctags"], check=True)
        return True
    except Exception as e:
        print(f"Failed to install ctags: {e}")
        return False

def preprocess_all():
    """Preprocess all source files"""
    os.makedirs(MODIFIED_SRC_DIR, exist_ok=True)
    
    # Install ctags if needed
    if not install_ctags():
        print("Warning: ctags not available")
    
    all_targets = []
    file_mapping = {}
    
    for file in SRC_DIR.glob("*.c"):
        try:
            targets, modified_path = preprocess_file(file, MODIFIED_SRC_DIR)
            all_targets.extend(targets)
            file_mapping[file.name] = modified_path
            print(f"  Processed {file.name}, found {len(targets)} targets")
        except Exception as e:
            print(f"Error processing {file.name}: {e}")
    
    # Save target function list
    with open(TARGETS_FILE, "w") as f:
        json.dump({
            "targets": all_targets,
            "file_mapping": {k: str(v) for k, v in file_mapping.items()}
        }, f, indent=2)
    
    print(f"Preprocessing completed. Processed {len(file_mapping)} files.")
    print(f"Generated {len(all_targets)} test targets.")

if __name__ == "__main__":
    try:
        preprocess_all()
    except Exception as e:
        print(f"Fatal error during preprocessing: {e}")
        sys.exit(1)
