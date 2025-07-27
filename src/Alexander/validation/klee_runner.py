#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import subprocess
import platform
import re
import shutil

def find_klee_executable():
    """Find KLEE executable in PATH"""
    klee_paths = ["klee", "/usr/local/bin/klee", "/opt/klee/bin/klee"]
    
    for path in klee_paths:
        try:
            result = subprocess.run([path, "--version"], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  universal_newlines=True, timeout=5)
            if result.returncode == 0:
                print(f"Found KLEE at: {path}")
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return None

def find_ktest_tool():
    """Find ktest-tool executable"""
    ktest_paths = ["ktest-tool", "/usr/local/bin/ktest-tool", "/opt/klee/bin/ktest-tool"]
    
    for path in ktest_paths:
        try:
            result = subprocess.run([path, "--help"], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True, timeout=5)
            if result.returncode == 0:
                print(f"Found ktest-tool at: {path}")
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return None

def compile_to_llvm_bc(source_file, temp_dir):
    """Compile C source to LLVM bitcode in temporary directory"""
    base_name = os.path.splitext(os.path.basename(source_file))[0]
    bc_file = os.path.join(temp_dir, f"{base_name}.bc")
    
    # Check if bitcode file is up-to-date
    if os.path.exists(bc_file):
        source_mtime = os.path.getmtime(source_file)
        bc_mtime = os.path.getmtime(bc_file)
        
        if source_mtime <= bc_mtime:
            print(f"Using existing bitcode: {bc_file}")
            return bc_file
    
    # Compile to LLVM bitcode
    compile_cmd = [
        "clang", "-I", "/usr/local/include", "-emit-llvm", 
        "-c", "-g", "-O0", "-Xclang", "-disable-O0-optnone",
        source_file, "-o", bc_file
    ]
    
    print(f"Compiling to LLVM bitcode: {' '.join(compile_cmd)}")
    
    try:
        subprocess.run(compile_cmd, check=True)
        print(f"Successfully compiled bitcode: {bc_file}")
        return bc_file
    except subprocess.CalledProcessError as e:
        print(f"Error compiling to bitcode: {str(e)}")
        return None
    except FileNotFoundError:
        print("Error: clang compiler not found. Make sure LLVM/Clang is installed.")
        return None

def link_with_qsort(driver_bc_file, qsort_bc_file, temp_dir):
    """Link driver bitcode with qsort.c bitcode using llvm-link"""
    base_name = os.path.splitext(os.path.basename(driver_bc_file))[0]
    linked_bc_file = os.path.join(temp_dir, f"{base_name}_linked.bc")
    
    # llvm-link command
    link_cmd = ["llvm-link", driver_bc_file, qsort_bc_file, "-o", linked_bc_file]
    
    print(f"Linking with qsort.c: {' '.join(link_cmd)}")
    
    try:
        subprocess.run(link_cmd, check=True)
        print(f"Successfully linked: {linked_bc_file}")
        return linked_bc_file
    except subprocess.CalledProcessError as e:
        print(f"Error linking bitcode: {str(e)}")
        return None
    except FileNotFoundError:
        print("Error: llvm-link not found. Make sure LLVM tools are installed.")
        return None

def run_klee_analysis(bc_file, temp_dir, klee_path, max_time=300):
    """Run KLEE symbolic execution"""
    base_name = os.path.splitext(os.path.basename(bc_file))[0]
    klee_output_dir = os.path.join(temp_dir, f"klee-out-{base_name}")
    
    # Remove existing output directory
    if os.path.exists(klee_output_dir):
        shutil.rmtree(klee_output_dir)
    
    # KLEE command - removed --only-output-states-covering-new to get all test cases
    klee_cmd = [
        klee_path,
        "--output-dir", klee_output_dir,
        "--max-time", str(max_time),
        "--write-kqueries",
        "--write-cov",
        "--write-test-info",
        "--optimize",
        "--libc=uclibc",
        "--posix-runtime",
        bc_file
    ]
    
    print(f"Running KLEE analysis: {' '.join(klee_cmd)}")
    
    try:
        result = subprocess.run(klee_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                              universal_newlines=True, timeout=max_time + 60)
        
        print("KLEE stdout:")
        print(result.stdout)
        
        if result.stderr:
            print("KLEE stderr:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"KLEE returned non-zero exit code: {result.returncode}")
        
        return klee_output_dir
        
    except subprocess.TimeoutExpired:
        print("KLEE analysis timed out")
        return klee_output_dir
    except Exception as e:
        print(f"Error running KLEE: {str(e)}")
        return None

def parse_ktest_txt_to_json(txt_content):
    """Parse ktest txt content to JSON format"""
    data = {}
    lines = txt_content.split('\n')
    
    current_object = None
    current_name = None
    current_data = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse object number and extract info
        if line.startswith('object ') and ': name:' in line:
            # Extract object number and name
            match = re.match(r'object\s+(\d+):\s+name:\s+\'([^\']+)\'', line)
            if match:
                current_object = int(match.group(1))
                current_name = match.group(2)
                
        elif line.startswith('object ') and ': data:' in line:
            # Extract data
            match = re.match(r'object\s+(\d+):\s+data:\s+(.+)', line)
            if match and int(match.group(1)) == current_object:
                current_data = match.group(2).strip()
                
                # Process the object if we have all info and it's not model_version
                if current_name and current_name != 'model_version' and current_data:
                    # Keep the data in b'...' format
                    data[current_name] = current_data
                
                # Reset for next object
                current_object = None
                current_name = None
                current_data = None
    
    return data

def extract_ktest_files_to_json(klee_output_dir, ktest_tool_path, func_name):
    """Extract .ktest files to JSON format directly in function directory"""
    if not os.path.exists(klee_output_dir):
        print(f"KLEE output directory not found: {klee_output_dir}")
        return []
    
    # Create function directory
    func_dir = f"data_out_{func_name}"
    if not os.path.exists(func_dir):
        os.makedirs(func_dir)
    
    # Find all .ktest files
    ktest_files = []
    for root, dirs, files in os.walk(klee_output_dir):
        for file in files:
            if file.endswith('.ktest'):
                ktest_files.append(os.path.join(root, file))
    
    if not ktest_files:
        print("No .ktest files found")
        return []
    
    print(f"Found {len(ktest_files)} .ktest files")
    
    # Extract each .ktest file directly to JSON in function directory
    json_files = []
    for i, ktest_file in enumerate(ktest_files):
        # Create JSON filename with format test000001.json
        json_filename = f"test{i+1:06d}.json"
        json_file = os.path.join(func_dir, json_filename)
        
        # Run ktest-tool
        extract_cmd = [ktest_tool_path, ktest_file]
        
        try:
            result = subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
            
            if result.returncode == 0:
                # Parse the txt output to JSON
                data = parse_ktest_txt_to_json(result.stdout)
                
                if data:
                    # Write JSON file in function directory
                    with open(json_file, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    json_files.append(json_file)
                    print(f"Created JSON: {json_file}")
                else:
                    print(f"No valid data extracted from {ktest_file}")
            else:
                print(f"Error extracting {ktest_file}: {result.stderr}")
                
        except Exception as e:
            print(f"Error running ktest-tool on {ktest_file}: {str(e)}")
    
    return json_files

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 klee_runner.py <qsort.c> <klee_driver_files...>")
        print("Example: python3 klee_runner.py qsort.c klee_partition.c klee_quickSort.c klee_swap.c")
        sys.exit(1)
    
    qsort_file = sys.argv[1]
    driver_files = sys.argv[2:]
    
    # Check if qsort.c exists
    if not os.path.exists(qsort_file):
        print(f"Error: qsort.c file '{qsort_file}' not found")
        sys.exit(1)
    
    # Check if driver files exist
    for driver_file in driver_files:
        if not os.path.exists(driver_file):
            print(f"Error: Driver file '{driver_file}' not found")
            sys.exit(1)
    
    # Find KLEE and ktest-tool
    klee_path = find_klee_executable()
    if not klee_path:
        print("Error: KLEE not found. Please install KLEE and ensure it's in PATH.")
        sys.exit(1)
    
    ktest_tool_path = find_ktest_tool()
    if not ktest_tool_path:
        print("Error: ktest-tool not found. Please ensure KLEE tools are in PATH.")
        sys.exit(1)
    
    # Create temporary directory for intermediate files
    temp_dir = "temp_klee_build"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Compile qsort.c to bitcode
    print(f"\n{'='*60}")
    print(f"Compiling qsort.c: {qsort_file}")
    print('='*60)
    
    qsort_bc_file = compile_to_llvm_bc(qsort_file, temp_dir)
    if not qsort_bc_file:
        print(f"Failed to compile {qsort_file}")
        sys.exit(1)
    
    successful_drivers = []
    function_dirs = {}
    total_json_count = 0
    
    # Process each driver file
    for driver_file in driver_files:
        print(f"\n{'='*60}")
        print(f"Processing: {driver_file}")
        print('='*60)
        
        # Extract function name from driver filename
        base_name = os.path.splitext(os.path.basename(driver_file))[0]
        if base_name.startswith('klee_'):
            func_name = base_name[5:]  # Remove 'klee_' prefix
        else:
            func_name = base_name
        
        # Step 1: Compile driver to LLVM bitcode
        driver_bc_file = compile_to_llvm_bc(driver_file, temp_dir)
        if not driver_bc_file:
            print(f"Failed to compile {driver_file}")
            continue
        
        # Step 2: Link with qsort.c
        linked_bc_file = link_with_qsort(driver_bc_file, qsort_bc_file, temp_dir)
        if not linked_bc_file:
            print(f"Failed to link {driver_file} with qsort.c")
            continue
        
        # Step 3: Run KLEE analysis on linked bitcode
        klee_output_dir = run_klee_analysis(linked_bc_file, temp_dir, klee_path)
        if not klee_output_dir:
            print(f"Failed to run KLEE on {driver_file}")
            continue
        
        # Step 4: Extract .ktest files to JSON directly in function directory
        json_files = extract_ktest_files_to_json(klee_output_dir, ktest_tool_path, func_name)
        if not json_files:
            print(f"No test cases generated for {driver_file}")
            continue
        
        successful_drivers.append(driver_file)
        function_dirs[func_name] = f"data_out_{func_name}"
        total_json_count += len(json_files)
        print(f"Generated {len(json_files)} JSON test cases for {driver_file} in data_out_{func_name}")
    
    # Clean up temporary directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temporary directory: {temp_dir}")
    
    # Print summary
    if successful_drivers:
        print(f"\n{'='*60}")
        print("Analysis completed successfully!")
        print('='*60)
        
        print(f"\nSummary:")
        print(f"Total JSON files generated: {total_json_count}")
        print(f"Functions analyzed: {list(function_dirs.keys())}")
        
        for func_name, func_dir in function_dirs.items():
            if os.path.exists(func_dir):
                file_count = len([f for f in os.listdir(func_dir) if f.endswith('.json')])
                print(f"  {func_name}: {file_count} test cases in {func_dir}")
    else:
        print("No test cases were generated.")
    
    print("\nKLEE analysis completed!")

if __name__ == "__main__":
    main()
