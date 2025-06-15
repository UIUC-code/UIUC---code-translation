# Translating C to Safer Rust

## Summary  
This work examines the safety gaps in Rust code produced by the rule‑based C2Rust transpiler and then tries to resolve one of the largest sources of unsafety—raw pointer usage—through an automated, compiler‑guided rewrite. First, the authors perform an empirical analysis over 17 diverse C programs, identifying seven distinct unsafe constructs (e.g., raw dereferences, global variables, casts) by using Rust’s High‑level Intermediate Representation and call graphs. They then focus on raw pointer dereferences and present a two‑phase repair pipeline:

1. **ResolveImports** cleans up module boundaries, deduping types and stripping unnecessary `unsafe`/`mut` annotations to prepare for pointer rewriting.  
2. **ResolveLifetimes** optimistically replaces raw pointers with borrowed references (`&`/`&mut`), then repeatedly invokes the Rust compiler’s borrow checker. Each compilation error is parsed to refine lifetime annotations or ownership decisions until the program type‑checks as safe Rust .

---

## Key Findings  
- **Quantitative Taxonomy**: Raw pointers constitute the majority of unsafe annotations in transpiled Rust, with 83 % of functions marked unsafe solely due to lifetime issues .  
- **High Repair Rate**: The pipeline removes roughly 83 % of lifetime‑related raw pointer occurrences, transforming those functions into fully safe Rust without manual intervention.  
- **Compiler‑as‑Oracle**: By leveraging the existing borrow‑checker error messages, the approach sidesteps the need for heavy custom analyses and scales to real‑world codebases.

---

## Phase 1 Applicability  
- **Skeleton Test Synthesis**  
  - Prompt an LLM to generate initial C unit-test templates for each function using its signature and doc comments.  
- **Compile‑And‑Refine Loop**  
  - Compile each skeleton test immediately. Capture compiler diagnostics (missing includes, type mismatches) and runtime failures, then automatically reprompt the LLM to refine test code until it compiles and runs.  
- **Diagnostic‑Driven Feedback**  
  - Parse compiler and test-run error messages to pinpoint assertion gaps or incorrect input generation; feed these back into the LLM to strengthen test assertions and input coverage.  
- **Function‑Level Slicing**  
  - Use call‑graph analysis to extract individual functions for test targeting, enabling parallel test generation and validation among team members.  
- **Progress Metrics**  
  - Monitor the percentage of functions with at least one passing test, compile-error resolution rate, and average time to first passing test to ensure on‑track completion within three weeks.  
