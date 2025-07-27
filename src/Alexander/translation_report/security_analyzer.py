#!/usr/bin/env python3

import re
import subprocess
import sys
import json
import os
from collections import defaultdict

def analyze_c_code(file_path):
    with open(file_path, 'r') as f:
        code = f.read()
    
    code = re.sub(r'//.*?\n', '\n', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    
    pointer_dangling = len(re.findall(r'return\s*&[a-zA-Z_]+\s*;', code))
    pointer_arithmetic = len(re.findall(r'[\w]+(\+\+|\-\-|\+|\-)\d', code))
    
    malloc_count = len(re.findall(r'\bmalloc\b', code))
    calloc_count = len(re.findall(r'\bcalloc\b', code))
    realloc_count = len(re.findall(r'\brealloc\b', code))
    free_count = len(re.findall(r'\bfree\b', code))
    
    memleak_potential = (malloc_count + calloc_count + realloc_count) - free_count
    
    unsafe_calls = {
        "strcpy": len(re.findall(r'\bstrcpy\b', code)),
        "strcat": len(re.findall(r'\bstrcat\b', code)),
        "sprintf": len(re.findall(r'\bsprintf\b', code)),
        "gets": len(re.findall(r'\bgets\b', code)),
        "scanf": len(re.findall(r'\bscanf\b', code))
    }
    
    null_deref = len(re.findall(r'\*[a-zA-Z_]+(?!\s*= NULL)', code))
    
    return {
        "dangling_pointers": pointer_dangling,
        "pointer_arithmetic": pointer_arithmetic,
        "memory_leak_risk": max(0, memleak_potential),
        "buffer_overflow_risk": sum(unsafe_calls.values()),
        "null_dereference_risk": null_deref,
        "memory_operations": {
            "allocations": malloc_count + calloc_count + realloc_count,
            "deallocations": free_count,
            "unsafe_functions": unsafe_calls
        }
    }

def analyze_rust_code(file_path):
    with open(file_path, 'r') as f:
        code = f.read()
    
    code = re.sub(r'//.*?\n', '\n', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    
    ownership_transfers = len(re.findall(r'let\s+\w+\s*=\s*\w+\s*;', code))
    borrows = len(re.findall(r'&\w+', code))
    mutable_borrows = len(re.findall(r'&mut\s+\w+', code))
    lifetimes = len(re.findall(r'<.*?\>', code))
    
    safe_allocations = len(re.findall(r'\bBox::new\b', code))
    safe_containers = len(re.findall(r'\bVec::\b|\bArc::\b|\bRc::\b', code))
    
    option_usage = len(re.findall(r'\bOption<', code))
    result_usage = len(re.findall(r'\bResult<', code))
    unwrap_calls = len(re.findall(r'\.unwrap\(\)', code))
    expect_calls = len(re.findall(r'\.expect\(\)', code))
    
    slice_access = len(re.findall(r'\[\d+\.\.\d+\]', code))
    iter_usage = len(re.findall(r'\.iter\(\)', code))
    
    return {
        "ownership_system": {
            "transfers": ownership_transfers,
            "borrows": borrows,
            "mutable_borrows": mutable_borrows,
            "lifetimes": lifetimes
        },
        "memory_management": {
            "safe_allocations": safe_allocations,
            "safe_containers": safe_containers
        },
        "error_handling": {
            "option_usage": option_usage,
            "result_usage": result_usage,
            "unwrap_calls": unwrap_calls,
            "expect_calls": expect_calls
        },
        "boundary_safety": {
            "slice_access": slice_access,
            "iter_usage": iter_usage
        }
    }

def capture_rust_errors(file_path):
    try:
        result = subprocess.run(
            ['rustc', '--edition=2021', file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        errors = []
        security_errors = defaultdict(int)
        
        if result.stderr:
            for line in result.stderr.splitlines():
                if "error" in line:
                    errors.append(line)
                    
                    security_keywords = [
                        "use after move", "borrow of moved value", 
                        "borrowed data escapes", "dropped while borrowed",
                        "cannot borrow as mutable", "cannot borrow as immutable",
                        "dereference of raw pointer", "memory safety"
                    ]
                    
                    for keyword in security_keywords:
                        if keyword in line.lower():
                            security_errors[keyword] += 1
        
        return {
            "error_count": len(errors),
            "errors": errors,
            "security_errors": dict(security_errors)
        }
    except subprocess.TimeoutExpired:
        return {"error_count": 0, "errors": [], "security_errors": {}}

def generate_comparison(c_data, rust_data, rust_errors):
    c_risks = {
        "dangling_pointers": c_data["dangling_pointers"],
        "pointer_arithmetic": c_data["pointer_arithmetic"],
        "memory_leak_risk": c_data["memory_leak_risk"],
        "buffer_overflow_risk": c_data["buffer_overflow_risk"],
        "null_dereference_risk": c_data["null_dereference_risk"]
    }
    total_c_risks = sum(c_risks.values())
    
    rust_features = {
        "ownership": rust_data["ownership_system"]["transfers"] + 
                    rust_data["ownership_system"]["borrows"],
        "memory_safety": rust_data["memory_management"]["safe_allocations"] +
                         rust_data["memory_management"]["safe_containers"],
        "error_handling": rust_data["error_handling"]["option_usage"] +
                          rust_data["error_handling"]["result_usage"],
        "boundary_safety": rust_data["boundary_safety"]["slice_access"] +
                           rust_data["boundary_safety"]["iter_usage"]
    }
    total_rust_features = sum(rust_features.values())
    
    memory_comparison = {
        "c_manual_allocations": c_data["memory_operations"]["allocations"],
        "c_manual_deallocations": c_data["memory_operations"]["deallocations"],
        "rust_auto_allocations": rust_data["memory_management"]["safe_allocations"],
        "rust_auto_containers": rust_data["memory_management"]["safe_containers"]
    }
    
    intercepted_errors = sum(rust_errors["security_errors"].values())
    
    return {
        "total_c_risks": total_c_risks,
        "total_rust_features": total_rust_features,
        "c_risk_breakdown": c_risks,
        "rust_feature_breakdown": rust_features,
        "memory_comparison": memory_comparison,
        "intercepted_errors": intercepted_errors,
        "rust_error_details": rust_errors
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python security_analyzer.py <c_file> <rust_file>")
        sys.exit(1)
    
    c_file = sys.argv[1]
    rust_file = sys.argv[2]
    
    if not os.path.exists(c_file):
        print(f"Error: C file '{c_file}' does not exist")
        sys.exit(1)
    
    if not os.path.exists(rust_file):
        print(f"Error: Rust file '{rust_file}' does not exist")
        sys.exit(1)
    
    print(f"Analyzing C file: {c_file}")
    c_data = analyze_c_code(c_file)
    
    print(f"Analyzing Rust file: {rust_file}")
    rust_data = analyze_rust_code(rust_file)
    
    print("Capturing Rust compiler errors...")
    rust_errors = capture_rust_errors(rust_file)
    
    print("Generating security comparison data...")
    comparison = generate_comparison(c_data, rust_data, rust_errors)
    
    result = {
        "c_analysis": c_data,
        "rust_analysis": rust_data,
        "rust_compiler_errors": rust_errors,
        "security_comparison": comparison
    }
    
    output_file = "security_data.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Security analysis completed! Results saved to {output_file}")
    
    print("\n=== Security Summary ===")
    print(f"Total C risks: {comparison['total_c_risks']}")
    print(f"Total Rust security features: {comparison['total_rust_features']}")
    print(f"Security errors intercepted by compiler: {comparison['intercepted_errors']}")
    print(f"Memory operations: C manual allocations {comparison['memory_comparison']['c_manual_allocations']}")
    print(f"                      Rust automatic allocations {comparison['memory_comparison']['rust_auto_allocations']}")

if __name__ == "__main__":
    main()