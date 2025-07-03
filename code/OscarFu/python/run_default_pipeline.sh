#!/bin/bash
set -e  # Exit on error

# === Configuration: change these paths as needed ===
RAW_C_DIR="raw_c"
SAMPLE_C_FILE="$RAW_C_DIR/sample.c"
INCLUDE_DIR="include"
GENERATED_HEADER="$INCLUDE_DIR/generated_funcs.h"
FUNCTIONS_JSON="functions.json"

KLEE_STUBS_DIR="klee_stubs"
STUB_SRC_DIR="$KLEE_STUBS_DIR/src_c"
LLVM_BC_DIR="$KLEE_STUBS_DIR/llvm_bc"
LLVM_BC_LINKED_DIR="$KLEE_STUBS_DIR/llvm_bc_linked"

KLEE_OUTPUT_DIR="klee-out"

# === Script steps ===

echo "[1/5] Extract functions JSON from sample.c"
python3 utils/extract_funcs.py "$SAMPLE_C_FILE" "$FUNCTIONS_JSON"

echo "[2/5] Generate KLEE stubs (.c) from functions.json"
mkdir -p "$STUB_SRC_DIR"
python3 utils/gen_klee_stubs.py "$FUNCTIONS_JSON" "$STUB_SRC_DIR"

echo "[3/5] Generate header file from sample.c"
mkdir -p "$INCLUDE_DIR"
python3 utils/gen_headers.py "$SAMPLE_C_FILE" "$GENERATED_HEADER"

echo "[4/5] Compile stubs and sample C to LLVM bitcode"
mkdir -p "$LLVM_BC_DIR"
python3 utils/compile_stubs.py "$INCLUDE_DIR" "$RAW_C_DIR" "$STUB_SRC_DIR" "$LLVM_BC_DIR"

echo "[5/5] Run KLEE on linked bitcode"
mkdir -p "$LLVM_BC_LINKED_DIR" "$KLEE_OUTPUT_DIR"
python3 utils/run_klee_all.py "$LLVM_BC_DIR" "$LLVM_BC_LINKED_DIR" "$KLEE_OUTPUT_DIR"
