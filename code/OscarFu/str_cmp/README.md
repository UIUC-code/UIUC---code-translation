
## Environment Setup

### Build the image
```bash
docker-compose build
```
### Start the container
```bash
docker-compose up -d
```
### Get a shell inside it
```bash
docker-compose exec dev-environment bash
```
Now you’ll be inside your dev environment, with your `./src` code mounted at `/home/researcher/project`.

```bash
docker pull klee/klee:3.0
docker run --rm -ti --ulimit='stack=-1:-1' -v <loca-path-to-UIUC-code-translation>/code:/code klee/klee 
```

### Run the dockerfile.klee-c2rust
```bash
docker build -t klee-c2rust -f Dockerfile.klee-c2rust .
```

## Run the code

### Translate to LLVM bitcode:
```
clang -I /path/to/klee/include -emit-llvm -c -g strcmp_sample.c -o strcmp_sample.bc

klee strcmp_sample.bc

ktest-tool klee-last/test000001.ktest
```
Results:
```
KLEE: done: total instructions = 33
KLEE: done: completed paths = 1
KLEE: done: partially completed paths = 0
KLEE: done: generated tests = 1
```


### Generate LLVM IR (C2Rust requires it)
```bash
clang -emit-llvm -S -g -c c_runner.c -o c_runner.ll
```
This produces `c_runner.ll`, a human-readable LLVM intermediate representation.