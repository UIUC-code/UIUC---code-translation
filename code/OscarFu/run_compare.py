import os
import subprocess

# Your symbolic string pool
options = [
    "hello",
    "world",
    "today is a good day",
    "openAI creates amazing tools",
    "klee helps find bugs",
    "symbolic execution rocks",
    "rust is safe and fast",
    "testing is important"
]

def parse_ktest_tool_output(output):
    """Extract idx_a and idx_b values from ktest-tool CLI output."""
    idx_a = None
    idx_b = None
    current_name = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("object 0: name:") or line.startswith("object 1: name:"):
            current_name = line.split("'")[1]
        elif "int :" in line and current_name in ("idx_a", "idx_b"):
            val = int(line.split(":", 2)[2].strip())
            if current_name == "idx_a":
                idx_a = val
            elif current_name == "idx_b":
                idx_b = val
            current_name = None
    return idx_a, idx_b

def run_runner(executable, arg1, arg2):
    """Run a binary (e.g., c_runner or rust_runner) with two string arguments."""
    try:
        result = subprocess.run(
            [f"./{executable}", arg1, arg2],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def compare_c_rust(idx_a, idx_b):
    """Compare the output of C and Rust runners for given string indices."""
    if not (0 <= idx_a < len(options)) or not (0 <= idx_b < len(options)):
        return f"INVALID INDICES: idx_a={idx_a}, idx_b={idx_b}", "INVALID", "INVALID", "SKIP"

    a_str = options[idx_a]
    b_str = options[idx_b]

    c_output = run_runner("c_runner", a_str, b_str)
    rust_output = run_runner("rust_runner", a_str, b_str)

    status = "MATCH" if c_output == rust_output else "MISMATCH"
    return f"a='{a_str}', b='{b_str}' | C: {c_output} | Rust: {rust_output} => {status}", c_output, rust_output, status

def main():
    klee_dir = "klee-last"
    mismatches = 0

    for filename in sorted(os.listdir(klee_dir)):
        if not filename.endswith(".ktest"):
            continue

        path = os.path.join(klee_dir, filename)

        try:
            result = subprocess.run(
                ["ktest-tool", path], capture_output=True, text=True, check=True
            )
        except Exception as e:
            print(f"Failed to run ktest-tool on {filename}: {e}")
            continue

        idx_a, idx_b = parse_ktest_tool_output(result.stdout)

        if idx_a is None or idx_b is None:
            print(f"{filename}: Failed to extract idx_a/idx_b")
            continue

        result_str, c_out, rust_out, status = compare_c_rust(idx_a, idx_b)
        print(f"{filename}: {result_str}")

        if status == "MISMATCH":
            mismatches += 1

    print(f"\n=== Summary ===")
    print(f"Total mismatches: {mismatches}")

if __name__ == "__main__":
    main()
