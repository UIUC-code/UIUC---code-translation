import os
import subprocess

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

def main():
    klee_dir = "klee-last"
    for filename in sorted(os.listdir(klee_dir)):
        if not filename.endswith(".ktest"):
            continue
        path = os.path.join(klee_dir, filename)
        try:
            result = subprocess.run(
                ["ktest-tool", path], capture_output=True, text=True, check=True
            )
            idx_a, idx_b = parse_ktest_tool_output(result.stdout)
            a_str = options[idx_a] if idx_a is not None and 0 <= idx_a < len(options) else f"INVALID({idx_a})"
            b_str = options[idx_b] if idx_b is not None and 0 <= idx_b < len(options) else f"INVALID({idx_b})"
            print(f"{filename}: idx_a={idx_a} -> '{a_str}', idx_b={idx_b} -> '{b_str}'")
        
        except Exception as e:
            print(f"Failed to parse {filename}: {e}")

if __name__ == "__main__":
    main()
