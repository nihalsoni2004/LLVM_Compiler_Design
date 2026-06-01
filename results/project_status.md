# Project Completion Status (Against README)

## Overall
- Status: **Mostly complete**
- Completed phases: 1 to 6
- Remaining phases: 7 (report finalization), 8 (presentation finalization)

## Phase-by-Phase Audit

### Phase 1: Understanding UB
- Covered UB classes in benchmark suite.
- Status: Done

### Phase 2: Benchmark C/C++ Programs
- UB programs present:
  - ub_signed_overflow
  - ub_null_deref
  - ub_oob_access
  - ub_invalid_shift
  - ub_use_after_free
  - ub_uninitialized
  - ub_div_zero
  - ub_type_punning
  - ub_double_free
  - ub_string_literal
- Safe programs present:
  - safe_arithmetic
  - safe_array
  - safe_pointers
- Status: Done

### Phase 3: LLVM/Clang Optimization Experiments
- O0/O2 LLVM IR and assembly generated for UB programs.
- Diff files generated.
- Status: Done

### Phase 4: Existing Tools
- Generated outputs:
  - ubsan_results.txt
  - clang_warnings.txt
  - clang_tidy_results.txt
  - cppcheck_results.txt
- Status: Done

### Phase 5: LLM Evaluation
- LLM output files generated for all benchmark and safe programs.
- Gemini 2.5 Flash model used with API key fallback and retry logic.
- Status: Done

### Phase 6: Comparison Table
- CSV and Markdown table generated.
- Summary statistics generated.
- Status: Done

### Phase 7: Report Writing
- Report draft created in report/report.md.
- Pending: convert to final PDF format and polish wording/screenshots.
- Status: In progress

### Phase 8: Hybrid Pipeline + Final Presentation
- Slide outline created in presentation/slides_outline.md.
- Pending: convert outline into actual PPTX and add visuals.
- Status: In progress

## Submission-Ready Checklist
- [x] Benchmarks created
- [x] LLVM experiments run
- [x] Static/runtime tool results collected
- [x] LLM results collected
- [x] Comparison table generated
- [ ] Report exported as PDF
- [ ] Presentation exported as PPTX
