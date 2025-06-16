# Ownership guided C to Rust translation

## Summary  
Rust’s memory‑safety guarantees hinge on its ownership model, but rule‑based C→Rust transpilers (e.g., C2Rust) generate `unsafe` code that merely mirrors C pointers. This paper introduces **Crown**, a tool that:

1. **Infers ownership** of C pointers via a static, field‑ and flow‑sensitive analysis—strengthened by an “ownership monotonicity” assumption to avoid expensive aliasing checks  
2. **Retypes pointers** in the AST to safe Rust equivalents (`Box<T>`, `Option<Box<T>>`, `&mut T`) based on the inferred ownership  
3. **Rewrites pointer uses** (e.g., `as_deref_mut().unwrap()`, `take()`, `Box::from_raw`) to match the new types  
4. **Scales to large codebases** (up to 500000 lines of code in < 10 s) and achieves a high conversion rate compared to prior work :contentReference[oaicite:0]{index=0}.

## Key Findings  
- **Scalability & Precision**: Crown’s ownership analysis handles nested pointers and inductively defined data structures in half‑million‑line codebases in under 10 seconds :contentReference[oaicite:1]{index=1}.  
- **High Reduction of Unsafe Code**: On a benchmark suite of 20 programs, Crown reduces mutable, non‑array raw pointer **declarations** by a median of 37.3 % and **uses** by 62.1 %, outperforming prior tools like Laertes in most cases :contentReference[oaicite:2]{index=2}.  
- **Semantic Preservation**: All translated benchmarks compile cleanly, and for those with available test suites (e.g., `libtree`, `rgba`, `quadtree`), Crown–generated Rust passes every test, ensuring behavioral equivalence :contentReference[oaicite:3]{index=3}.

## Phase 1 Applicability  

- **Ownership‑Driven Test Slicing**  
  - Use Crown’s ownership analysis to decompose a C codebase into function‑level units along ownership boundaries (e.g., where pointers transfer ownership). Generating tests per slice ensures each unit’s memory‑management invariants are exercised.  
- **Memory‑Safety Assertions**  
  - Leverage ownership monotonicity constraints to automatically insert assertions for correct allocation/use/free patterns. Tests can check that functions obey the inferred ownership discipline (no double‑free, no leaks).  
- **Feedback‑Guided Refinement**  
  - Compile skeleton tests against the C code; on memory‑error diagnostics (e.g., from Valgrind or AddressSanitizer), use ownership constraints to pinpoint violating functions and regenerate or strengthen test inputs.  
- **Parallel Test Generation**  
  - Assign disjoint ownership slices to team members—since Crown identifies unique ownership regions, tests for different pointer‑owning units won’t overlap, enabling concurrent development and faster coverage.
