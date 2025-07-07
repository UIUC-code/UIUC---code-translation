from pathlib import Path
import os
import subprocess
import shutil

BC_DIR = Path("bitcode")
KLEE_RESULTS = Path("klee_results")
REPORTS = Path("reports")

def clean_output_dir(output_dir):
    """Remove output directory if it exists"""
    if output_dir.exists():
        shutil.rmtree(output_dir, ignore_errors=True)

def print_log_tail(log_file):
    """Print last 10 lines of log file for debugging"""
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            n = min(10, len(lines))
            print(f"  Last {n} lines of log:")
            for line in lines[-n:]:
                print(line, end='')
    except Exception as e:
        print(f"  Error reading log file: {e}")

def run_klee():
    """Run KLEE on all bitcode files in BC_DIR"""
    os.makedirs(KLEE_RESULTS, exist_ok=True)
    os.makedirs(REPORTS, exist_ok=True)

    for bc_file in BC_DIR.glob("*.bc"):
        print(f"Running KLEE on {bc_file.name}...")
        test_name = bc_file.stem
        output_dir = KLEE_RESULTS / test_name
        log_file = REPORTS / f"{test_name}_klee.log"

        # Clean output directory before first attempt
        clean_output_dir(output_dir)

        # First attempt with basic options
        cmd = [
            "klee",
            "--output-dir", str(output_dir),
            str(bc_file)
        ]

        try:
            with open(log_file, 'w') as log:
                subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
            print(f"  KLEE run completed for {bc_file.name}")
        except subprocess.CalledProcessError as e:
            print(f"  First run failed: {e}")
            print_log_tail(log_file)
            
            # Clean again before simpler attempt
            clean_output_dir(output_dir)
            print("  Trying with simpler options...")
            
            # Second attempt with simpler options
            simple_cmd = [
                "klee",
                "--output-dir", str(output_dir),
                "--libc=klee",
                "--optimize",
                str(bc_file)
            ]
            
            try:
                with open(log_file, 'a') as log:
                    log.write("\n\n======= SIMPLER OPTIONS =======\n")
                    subprocess.run(simple_cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
                print(f"  KLEE run completed with simpler options")
            except subprocess.CalledProcessError as e2:
                print(f"  Simpler options failed: {e2}")
                with open(log_file, 'a') as log:
                    log.write("\n\n======= SIMPLER OPTIONS FAILED =======\n")
                print_log_tail(log_file)
            except Exception as e:
                print(f"  Unexpected error in simpler run: {e}")
        except Exception as e:
            print(f"  Unexpected error: {e}")

if __name__ == "__main__":
    run_klee()
