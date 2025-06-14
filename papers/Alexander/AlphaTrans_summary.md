# AlphaTrans: Code Translation Framework

## Core Method
AlphaTrans combines static program analysis with LLM-based code synthesis to translate an entire repository (both application and test code) from one language to another. It:
1. **Refactors PL-specific constructs** (e.g., overloaded constructors)
2. **Decomposes code** into fine-grained fragments (fields, methods, test fragments) with dependency metadata
3. **Builds a "skeleton"** of the target project by mapping
4. **Iteratively translates** each fragment in reverse call order, validating via:
   - Syntax checks
   - GraalVM-based in-isolation execution of original tests
   - Execution of translated test fragments
   - Automated feedback loops on failures

## Pros & Cons

### Pros
- **Scalability & Coverage**: Successfully translated 17,874 fragments across ten real-world Java projects, with:
  - 96.4% syntactic correctness
  - 27% functional validation via source tests
- **Practical Validation**: Leverages GraalVM’s polyglot API to execute Python translations in isolation against existing Java tests, avoiding "test translation coupling" and localizing errors.
- **PL-Agnostic Pipeline**: Although implemented for Java→Python, the neuro-symbolic pipeline (decomposition, skeleton construction, fragment-wise LLM prompting, multi-level validation) can generalize to other language pairs (e.g., D to Rust).

### Cons / Limitations
- **Language Interop Constraints**: GraalVM validation can’t handle all data types (e.g., certain library types), leading to "Graal Error" for ~15% of covered methods.
- **Resource & Time**: End-to-end translation of a medium project takes on average **34 hours** and incurs LLM costs (≈$14/project with GPT-4o).
- **LLM Dependence**: Quality hinges on LLM capabilities; weaker models yield lower semantic equivalence.

## Innovations

### Method
- **Neuro-Symbolic Fragmentation**: Breaks down large codebases into AST-driven fragments (fields, methods, test blocks) to fit within LLM context limits.
- **PL-Specific Refactoring**: Automates semantics-preserving refactoring of overloaded constructors/methods before translation.
- **Reverse Call Translation**: Orders fragment translation bottom-up via call graph topological sorting to ensure dependencies are met.
- **Feedback-Driven Prompts**: Iteratively reprompts the LLM based on parse, compilation, or test failures, with an adaptive reprompt budget.

### Validation
- **Syntactic & Type Checks**: Ensures generated code parses and type annotations compile.
- **In-Isolation GraalVM Execution**: Executes translated fragments in Python within a Java test harness via GraalVM’s Polyglot API, validating each method in isolation against original unit tests.
- **Test Decomposition & Recomposition**: Splits original tests into incremental fragments to localize failures and validate translated code paths before full test execution.
- **Recomposition Loop**: Gradually stitches translated fragments into the target skeleton and re-runs eligible translated tests for integrated validation.

## Phase 1 Applicability
- ✅ **Reusable**: Cross-language test decomposition and migration framework can be adapted to generate C unit tests automatically (e.g., by analyzing C code fragments, creating skeletons, and prompting an LLM to synthesize tests).
- ⚠️ **Limitation**: Does not handle pointer aliasing or low-level memory semantics, so tests involving complex pointer interactions may require manual annotations or domain-specific extensions.