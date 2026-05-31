# Evaluation

This document defines metrics, test cases, and the comparison methodology used in this project.

## Metrics
- Detection Rate: fraction of UB cases correctly identified (per tool / LLM).
- False Positives: cases reported as UB but are safe.
- False Negatives: UB cases missed.
- Precision / Recall / F1 for binary UB detection.
- Explanation quality (qualitative) for LLM: correctness, completeness, and helpfulness.

## Testcases
- All benchmark programs are in `benchmarks/` (or `testcases/` after syncing). Each file targets a single UB class.

## Comparison methodology
1. Run static analyzers (`clang-tidy`, `cppcheck`) over all testcases and collect warnings.
2. Run sanitizers (UBSan/ASan) over compiled binaries to collect runtime detections.
3. Query LLM with a fixed prompt template and collect predictions.
4. Compare all outputs against ground truth (manually labeled expected UB per test case) and generate a CSV of results.

## Producing the comparison table
- `python scripts/compare_results.py` ingests `tool_results/*` and `llm_results/*` and writes `results/comparison_table.csv` and `comparison_table.md`.
