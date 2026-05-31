# Implementation Details

This document describes practical implementation details and LLVM-specific observations.

## LLVM/Clang workflow
- Generate LLVM IR at O0 and O2 to observe optimizer-driven differences:
  - `clang -O0 -S -emit-llvm file.c -o file_O0.ll`
  - `clang -O2 -S -emit-llvm file.c -o file_O2.ll`
- Check for `nsw`/`nuw` flags on arithmetic ops (indicates assumed no-wrap). 
- Look for `unreachable` and eliminated `br`/`icmp` sequences — signs optimizer exploited UB.

## Automation
- `scripts/run_experiments.sh` automates IR/assembly generation and diffs.
- `scripts/run_ubsan.sh`, `scripts/run_clang_tidy.sh`, `scripts/run_cppcheck.sh` run tools and store outputs under `tool_results/`.
- `scripts/llm_query.py` queries an LLM and writes responses to `llm_results/`.
- `scripts/compare_results.py` builds `results/comparison_table.csv` and `comparison_table.md` from tool and LLM outputs.

## Notes on flags and sanitizer usage
- Use `-fsanitize=undefined,address` (UBSan + ASan) when running dynamic checks.
- Compile tests with `-g -O1` for better sanitizer diagnostics and stack traces.
