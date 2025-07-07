#!/bin/bash

set -e 

python3 pipelines/preprocess.py


python3 pipelines/compile.py

python3 pipelines/run_klee.py



