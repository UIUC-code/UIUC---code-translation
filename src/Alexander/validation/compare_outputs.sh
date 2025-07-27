#!/bin/bash

# Run the executables and capture outputs
echo "Running qsort_test_c..."
./qsort_test_c > output_c.txt 2>&1
c_status=$?

echo "Running qsort_test_r..."
./qsort_test_r > output_r.txt 2>&1
r_status=$?

# Check if both executed successfully
if [ $c_status -ne 0 ] || [ $r_status -ne 0 ]; then
    echo -e "\nError: One or both executables failed to run:"
    echo "qsort_test_c exit status: $c_status"
    echo "qsort_test_r exit status: $r_status"
    echo "Check output files for details:"
    echo "  C output:   output_c.txt"
    echo "  Rust output: output_r.txt"
    exit 1
fi

# Compare outputs
echo -e "\nComparing outputs..."
if diff -q output_c.txt output_r.txt > /dev/null; then
    echo "SUCCESS: Outputs are identical"
    # Clean up
    rm output_c.txt output_r.txt
else
    echo "DIFFERENCES FOUND:"
    diff --color -u output_c.txt output_r.txt
    echo -e "\nOutput files preserved:"
    echo "  C output:   output_c.txt"
    echo "  Rust output: output_r.txt"
    echo "Use 'diff output_c.txt output_r.txt' to review differences"
fi