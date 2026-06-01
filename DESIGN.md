# Design

## Goal
Provide a clear approach for detecting and demonstrating Undefined Behaviour (UB) in small C programs, compare LLM predictions vs existing tools, and propose a hybrid workflow.

## High-level approach
- Benchmarks: small, focused C programs (one UB per file).
- Tooling: use LLVM/Clang to generate IR at different optimization levels (O0 vs O2), run sanitizers (UBSan), and static analysers (clang-tidy, cppcheck).
- LLM evaluation: send benchmark sources to an LLM, collect structured responses, and compare detection/diagnosis with tools.

## Architecture
- `testcases/` (benchmarks) — one C file per UB class.
- `scripts/` — automation for generating IR, running tools, querying LLM, and comparing results.
- `llvm_experiments/` — generated IR and diffs for O0/O2.
- `tool_results/`, `llm_results/`, `results/` — outputs and comparison tables.

## Alternatives considered
- Replace LLM queries with an ensemble of static analyzers — higher coverage but still incomplete.
- Use fuzzing and sanitizer-driven test generation to expose UB dynamically — stronger runtime evidence but requires harnesses and more compute.

## Trade-offs
- LLMs provide semantic reasoning and natural-language explanations but may hallucinate details; combine with static/runtime tools to improve precision.
