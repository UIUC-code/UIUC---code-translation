# C2SAFERRUST: Transforming C Projects into Safer Rust with NeuroSymbolic Techniques

## Core Method
C2SAFERRUST uses a neuro‑symbolic pipeline to convert C code into idiomatic, memory‑safe Rust by:
1. **Rule‑based transpilation**: Runs C2Rust to produce an initial, unsafe Rust code.
2. **Static analysis & slicing**: Breaks the code into small translation units (functions or code chunk that has less than 150 lines of code) via call‐graph and data‐flow analyses.
3. **LLM‐driven refinement**: Invokes an LLM on each slice to rewrite it into safe, idiomatic Rust.
4. **Iterative validation loop**:
   - Compile the hybrid Rust code
   - Run existing test suite
   - Feed compiler/runtime errors back to the LLM for repair

## Pros & Cons

### Pros
- **Hybrid Safety**: Combines deterministic C2Rust output with LLM creativity to eliminate many unsafe patterns.
- **Scalability**: Handles large codebases by operating at the slice level.
- **Semantic Correctness**: Continuous compile‑and‑test feedback ensures behavioral equivalence to the original C.

### Cons / Limitations
- **Test Suite Dependence**: Cannot generate new tests; requires a comprehensive existing harness.
- **Residual Unsafe Code**: Leaves unsafe blocks for foreign function in
terfaces and low‑level struct definitions.
- **Chunking Overhead**: Very long functions may need extra slicing to fit within LLM context limits.

## Innovations

### Method
- **Neuro‑Symbolic Fragmentation**: AST‐driven slicing of code into LLM‑friendly units.
- **Rule‑plus‑LLM Integration**: Uses C2Rust’s rule‑based transpiler to produce intermediate representations of unsafe Rust code, then applies LLM refinements.
- **Static Analysis Orchestration**: Leverages call‐graph and data‐flow analyses to order translation units.

### Validation
- **Compile & Test Loop**: Differential testing at each step—compile hybrid code and run system tests.
- **Error‐Driven Reprompting**: Automatically reprompts the LLM on parse, compile, or runtime failures.
- **End‑to‑End Feedback**: Combines compiler errors and failed test outputs to guide iterative repairs.

## Phase 1 Applicability
- ✅ **Reusable Framework**: The compile‑and‑test feedback loop can validate generated unit tests for C functions, filtering effective tests automatically.
- ⚠️ **Gap in Test Generation**: Since C2SAFERRUST doesn’t produce tests, Phase 1 requires a dedicated unit‑test synthesis component (e.g., LLM prompts to generate new C tests) before applying this validation pipeline.
