#!/bin/bash

# 主KLEE测试用例生成流水线

set -e  # 任何步骤失败则退出
echo "========== [1] 预处理 =========="
python3 pipelines/preprocess.py

echo "========== [2] 编译为LLVM Bitcode =========="
python3 pipelines/compile.py
echo "========== [3] 运行KLEE =========="
python3 pipelines/run_klee.py

echo "========== [4] 处理测试用例 =========="
python3 pipelines/process_tests.py

echo "========== 流水线完成 =========="

