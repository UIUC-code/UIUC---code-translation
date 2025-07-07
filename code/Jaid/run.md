# KLEE RUNNING COMMANDS:
## MySQL:

1. python3 klee_transformer.py test_code.c -o processed.c -c config.txt -v
2. clang -I /media/goat/Projects/Work/Jobs/UIUC/klee/include \
      -emit-llvm -c -g -O0 \
      -Xclang -disable-O0-optnone \
      -DKLEE_ANALYSIS \
      processed.c -o processed.bc
3. VIO_SYM_CONFIGS="autocommit,flush_at_trx_commit" \
/media/goat/Projects/Work/Jobs/UIUC/klee/build/bin/klee processed.bc


## BUBBLE_SORT:

1. python3 klee_transformer.py bubble_sort.c -o processed.c -c bubble_config.txt -v
2. clang -I /media/goat/Projects/Work/Jobs/UIUC/klee/include \
      -emit-llvm -c -g -O0 \
      -Xclang -disable-O0-optnone \
      -DKLEE_ANALYSIS \
      processed.c -o processed.bc
3. VIO_SYM_CONFIGS="value1,value3" \
/media/goat/Projects/Work/Jobs/UIUC/klee/build/bin/klee processed.bc



## Basic C Running Command
gcc bubble_sort.c -o bubble_sort
./bubble_sort



## Handles #include directives and removes comments
gcc -E test_code.c -o source_preprocessed.c
python ast_generator.py source_preprocessed.c
python ast_generator.py test_code.c