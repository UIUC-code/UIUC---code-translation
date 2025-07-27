
# Automated Validation for C-to-Rust Translation of qsort

## Intro

Manually validating low-level functions like quicksort components is time-consuming and often fails to cover critical edge cases. This pipeline provides end-to-end validation for Rust translations of core qsort components (swap, partition, and quicksort) against their original C implementations. By using KLEE, the workflow can generate comprehensive test cases covering edge conditions and program paths, then verify semantic equivalence between the implementations.

## Workflow

1. Write klee test case generation code for each functions 

2. Generate Test Cases with KLEE

```bash
python3 klee_runner.py qsort.c klee_partition.c klee_quickSort.c klee_swap.c
```

This will first generate .ktest test cases. Then, using ktest-tool to convert these binary files into human-readable .txt. Then transformation them to structured JSON inputs:

example:
```txt
{
  "arr": [3, 1, 4, 1, 5],
  "low": 0,
  "high": 4
}
```

3. Write test code to take generated test cases as input and produce outputs (quicksort.c, partition.c, swap.c)

4. Translate test code to rust (quicksort.rs, partition.rs, swap.rs)

5. Run compare_outputs.sh to compare the outputs of C version of test code and Rust version of test code. If the output matches, the translation is correct. Otherwise, it means the translation has some errors.


## Conclusion

This automated solution uses KLEE‑generated test cases to catch edge case tests and remove tedious manual testing, ensuring reliable C‑to‑Rust validation with minimal effort.