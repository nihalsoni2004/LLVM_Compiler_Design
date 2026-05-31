# Final Presentation Outline

## Slide 1: Title
- Assignment 13: AI for Undefined Behaviour Detection in C/C++
- Course: Compiler Design Lab
- Team details

## Slide 2: Problem Statement
- UB is legal optimization fuel in C/C++
- Same source may behave differently under optimization
- Question: can LLM detect UB effectively?

## Slide 3: What is UB?
- Examples: signed overflow, null deref, OOB, invalid shift, UAF
- Why dangerous: unpredictable runtime + optimizer assumptions

## Slide 4: Project Objectives
- Detect UB patterns
- Explain UB per language semantics
- Predict LLVM optimization implications
- Compare LLM vs existing tools

## Slide 5: Benchmark Suite
- 10 UB programs + 3 safe programs
- One primary UB class per UB benchmark

## Slide 6: LLVM Experiment Method
- O0 and O2 IR generation
- O0 and O2 assembly generation
- Diff-based analysis

## Slide 7: Key LLVM Demo (Signed Overflow)
- Source snippet: overflow check
- O0 vs O2 behavior difference
- Why optimization is legal under UB assumptions

## Slide 8: Tools Used
- UBSan
- Clang warnings
- clang-tidy
- cppcheck
- LLM (Gemini 2.5 Flash)

## Slide 9: Results Table
- Present main comparison table
- Highlight detector coverage percentages

## Slide 10: Findings
- LLM detection coverage was highest on this benchmark
- UBSan/cppcheck also strong, but not complete
- Clang warnings weakest coverage among tested tools

## Slide 11: Strengths and Weaknesses
- LLM strengths: semantic reasoning, explanation quality on many cases
- LLM weaknesses: inconsistent explanations on some samples
- Traditional tools: stable but incomplete coverage

## Slide 12: Hybrid Pipeline Proposal
1. Static pre-filter (clang warnings + cppcheck)
2. Deep static analysis (clang-tidy)
3. LLM semantic triage and fix suggestions
4. UBSan runtime confirmation

## Slide 13: Conclusion
- No single tool solves UB detection completely
- Hybrid approach provides best practical outcome

## Slide 14: Future Work
- Larger benchmark corpus
- More compilers and optimization levels
- LLM calibration and confidence scoring

## Slide 15: Q&A
- Keep a backup slide with extra logs and IR diffs

## Demo Commands (optional backup slide)
```bash
clang -O0 -o test_O0 benchmarks/ub_signed_overflow.c
clang -O2 -o test_O2 benchmarks/ub_signed_overflow.c
./test_O0
./test_O2
```

## Export Notes
- Convert this outline into PPTX manually in PowerPoint/Google Slides
- Add screenshots from:
  - llvm_experiments/results/*_diff.txt
  - tool_results/*.txt
  - results/comparison_table.md
