# Assignment 13 — AI for Undefined Behaviour Detection in C/C++ Programs
 
Detailed Description: 
AI for Undefined Behaviour Detection
in C/C++ Programs
Description: Study whether an LLM can detect undefined behaviour (UB) in C/C++ source
code before LLVM/Clang optimizations exploit that UB and transform the program in
surprising ways.
Background: In C/C++, operations such as signed integer overflow, null dereference, invalid
shifts, and out-of-bounds access may have undefined behaviour. Modern compilers like
LLVM legally optimize under the assumption that UB does not occur. This makes UB both a
language-semantics problem and a compiler-analysis problem. Existing tools such as UBSan
and clang warnings help, but they do not fully solve the problem: UBSan is runtime-based,
and static tools are incomplete.
Objective: Investigate whether an LLM can:
(a) identify UB patterns in C/C++ programs,

(b) explain why they are UB,
(c) predict how LLVM may optimize based on those assumptions, and
(d) compare its performance against existing tools such as UBSan, clang-tidy, and static
analysers.
Deliverables:
• A benchmark set of small C/C++ programs containing different classes of UB
• LLVM/Clang experiments showing how optimization changes code behavior or
reasoning
• A comparison of LLM predictions vs UBSan / clang warnings / static analysis
• A report discussing soundness, completeness, false positives, and false negatives
• A final presentation proposing a hybrid LLM + static-analysis pipeline

> **Course:** Compiler Design Lab  
> **Objective:** Study whether an LLM can detect Undefined Behaviour (UB) in C/C++ source code before LLVM/Clang optimizations exploit it.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Prerequisites & Environment Setup](#2-prerequisites--environment-setup)
3. [Project Directory Structure](#3-project-directory-structure)
4. [Phase 1 — Understanding Undefined Behaviour](#4-phase-1--understanding-undefined-behaviour)
5. [Phase 2 — Writing Benchmark C/C++ Programs](#5-phase-2--writing-benchmark-cc-programs)
6. [Phase 3 — LLVM/Clang Optimization Experiments](#6-phase-3--llvmclang-optimization-experiments)
7. [Phase 4 — Running Existing Tools](#7-phase-4--running-existing-tools)
8. [Phase 5 — LLM Evaluation](#8-phase-5--llm-evaluation)
9. [Phase 6 — Building the Comparison Table](#9-phase-6--building-the-comparison-table)
10. [Phase 7 — Report Writing](#10-phase-7--report-writing)
11. [Phase 8 — Hybrid Pipeline Proposal](#11-phase-8--hybrid-pipeline-proposal)
12. [Final Presentation Guide](#12-final-presentation-guide)
13. [Common Errors & Troubleshooting](#13-common-errors--troubleshooting)
14. [References](#14-references)

---

## 1. Project Overview

### What is this project?

This project is a **research and benchmarking** study. You are NOT training a machine learning model from scratch. Instead, you:

1. Create a set of small C/C++ programs that contain known Undefined Behaviour (UB).
2. Use LLVM/Clang to demonstrate how compilers exploit UB during optimization.
3. Run existing static and runtime tools (UBSan, clang-tidy, cppcheck) on those programs.
4. Feed the same programs to a Large Language Model (LLM) and collect its analysis.
5. Compare all results and draw conclusions about soundness, completeness, and usability.
6. Propose a hybrid pipeline combining LLM reasoning with static analysis.

### Why does this matter?

C and C++ compilers like LLVM legally assume that Undefined Behaviour **never occurs**. Based on this assumption, they apply aggressive optimizations. This means:

- Code that appears correct may behave completely differently after optimization.
- Runtime sanitizers (UBSan) only catch UB that is actually executed.
- Static tools (clang-tidy, cppcheck) are incomplete and miss many UB patterns.
- LLMs have been trained on massive codebases and may reason about UB semantically.

The research question is: **Can an LLM do better than existing tools?**

---

## 2. Prerequisites & Environment Setup

### Quick start (recommended)

Follow these steps on WSL/Ubuntu (or macOS with equivalent tools):

```bash
cd /mnt/f/Downloads/6th_Sem_EL/CD_Lab
# Create and activate venv
python3 -m venv .venv
source .venv/bin/activate
# Install Python deps
pip install --upgrade pip
pip install -r requirements.txt

# Build helper (creates venv and installs if needed)
bash build.sh

# Run full pipeline (experiments, tools, LLM queries, comparison)
bash run.sh

# View results and UI
streamlit run ui/comparison_ui.py
```

Notes: `requirements.txt` contains the minimal Python packages used by automation and UI. System tools (clang, cppcheck, clang-tidy) must be installed separately (see below).

### 2.1 Required Software

| Tool | Purpose | Install Command |
|------|---------|-----------------|
| LLVM/Clang (≥ 14) | Compile C/C++, generate IR, run sanitizers | See below |
| clang-tidy | Static analysis | Comes with LLVM |
| cppcheck | Open-source static analyser | `sudo apt install cppcheck` |
| Python 3.10+ | Scripting and automation | `sudo apt install python3` |
| diff / diffutils | Compare IR files | Pre-installed on Linux |
| make | Build automation | `sudo apt install make` |

### 2.2 Installing LLVM and Clang on Ubuntu/Debian

```bash
# Add the official LLVM repository
wget https://apt.llvm.org/llvm.sh
chmod +x llvm.sh
sudo ./llvm.sh 17          # Install LLVM version 17

# Install clang-tidy and other tools
sudo apt install clang-17 clang-tidy-17 clang-tools-17 llvm-17

# Verify installation
clang --version
clang-tidy --version
llvm-dis --version
```

### 2.3 Installing LLVM on macOS

```bash
brew install llvm
echo 'export PATH="/opt/homebrew/opt/llvm/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
clang --version
```

### 2.4 Installing cppcheck

```bash
# Ubuntu/Debian
sudo apt install cppcheck

# macOS
brew install cppcheck

# Verify
cppcheck --version
```

### 2.5 Python Dependencies (for automation scripts)

```bash
pip install pandas tabulate matplotlib requests openai
```

---

## 3. Project Directory Structure

Set up your project like this before starting:

```
assignment13-ub-detection/
│
├── README.md                        ← This file
│
├── benchmarks/                      ← All benchmark C programs
│   ├── ub_signed_overflow.c
│   ├── ub_null_deref.c
│   ├── ub_oob_access.c
│   ├── ub_invalid_shift.c
│   ├── ub_use_after_free.c
│   ├── ub_uninitialized_read.c
│   ├── ub_divide_by_zero.c
│   ├── ub_type_punning.c
│   ├── ub_stack_overflow.c
│   ├── ub_dangling_pointer.c
│   ├── ub_modify_string_literal.c
│   ├── ub_double_free.c
│   ├── safe_programs/               ← Programs with NO UB (for false positive testing)
│   │   ├── safe_arithmetic.c
│   │   ├── safe_array.c
│   │   └── safe_pointers.c
│
├── llvm_experiments/                ← IR files and optimization experiments
│   ├── run_experiments.sh           ← Script to generate all IR files
│   ├── results/
│   │   ├── ub_signed_overflow_O0.ll
│   │   ├── ub_signed_overflow_O2.ll
│   │   └── ...
│
├── tool_results/                    ← Output from each tool
│   ├── ubsan_results.txt
│   ├── clang_warnings.txt
│   ├── clang_tidy_results.txt
│   ├── cppcheck_results.txt
│
├── llm_results/                     ← LLM responses for each program
│   ├── llm_ub_signed_overflow.txt
│   ├── llm_ub_null_deref.txt
│   └── ...
│
├── scripts/
│   ├── run_all_tools.sh             ← Automates running all tools
│   ├── run_ubsan.sh
│   ├── run_clang_tidy.sh
│   ├── run_cppcheck.sh
│   ├── compare_results.py           ← Builds comparison table
│   └── llm_query.py                 ← Script to query LLM API
│
├── results/
│   ├── comparison_table.csv         ← Final comparison table
│   └── comparison_table.md
│
├── report/
│   └── report.pdf                   ← Final report
│
└── presentation/
    └── slides.pptx                  ← Final presentation
```

Create this structure with:

```bash
mkdir -p assignment13-ub-detection/{benchmarks/safe_programs,llvm_experiments/results,tool_results,llm_results,scripts,results,report,presentation}
cd assignment13-ub-detection
```

---

## 4. Phase 1 — Understanding Undefined Behaviour

Before writing code, you must understand each class of UB. Here is a reference:

### 4.1 UB Classes You Must Cover

| # | UB Class | C Standard Reference | What Happens at Runtime |
|---|----------|---------------------|------------------------|
| 1 | Signed integer overflow | C11 §6.5 | Anything — crash, wrong result, infinite loop |
| 2 | Null pointer dereference | C11 §6.5.3.2 | Segmentation fault (usually) |
| 3 | Out-of-bounds array access | C11 §6.5.6 | Memory corruption, crash |
| 4 | Invalid shift (shift ≥ width) | C11 §6.5.7 | Wrong value, platform-dependent |
| 5 | Use-after-free | C11 §7.22.3 | Use of freed memory — heap corruption |
| 6 | Uninitialized variable read | C11 §6.3.2.1 | Garbage value |
| 7 | Division by zero (integer) | C11 §6.5.5 | SIGFPE signal, program crash |
| 8 | Type punning via pointer cast | C11 §6.5 (strict aliasing) | Optimizer may break the code |
| 9 | Double free | C11 §7.22.3.3 | Heap corruption, crash |
| 10 | Modifying a string literal | C11 §6.4.5 | Segmentation fault |

### 4.2 Key Insight — Why Compilers Exploit UB

The compiler is allowed to assume UB never happens. Therefore:

```
If UB cannot happen → condition is always true/false → branch eliminated
```

Example thought process for signed overflow:
- `x + 1 > x` — if this were unsigned, overflow could make it false.
- But signed overflow is UB. So compiler assumes it never happens.
- Therefore `x + 1 > x` is **always true**. Compiler eliminates the else branch entirely.

---

## 5. Phase 2 — Writing Benchmark C/C++ Programs

Write all programs in the `benchmarks/` directory. Each program should be small (10–30 lines), focused on one UB class, and compilable with `clang`.

### Program 1 — Signed Integer Overflow (`ub_signed_overflow.c`)

```c
// ub_signed_overflow.c
// UB Class: Signed Integer Overflow (C11 §6.5)
// Description: Adding 1 to INT_MAX causes signed overflow — UB in C.
// LLVM may optimize away the check (x + 1 > x) because it assumes
// signed overflow never occurs, making the condition always true.

#include <stdio.h>
#include <limits.h>

int check_overflow(int x) {
    // With -O2, LLVM may optimize this to always return 1
    // because it assumes signed overflow (UB) cannot happen
    if (x + 1 > x) {
        return 1;   // "overflow did not happen"
    }
    return 0;       // "overflow happened" — unreachable after optimization!
}

int main() {
    printf("check_overflow(INT_MAX) = %d\n", check_overflow(INT_MAX));
    // Expected (no opt): 0 (overflow happened)
    // Actual with -O2:   1 (optimizer removed the check)
    return 0;
}
```

### Program 2 — Null Pointer Dereference (`ub_null_deref.c`)

```c
// ub_null_deref.c
// UB Class: Null Pointer Dereference (C11 §6.5.3.2)
// Description: Dereferencing a null pointer is UB.
// LLVM may assume p != NULL based on the dereference and
// eliminate any null checks that appear AFTER the dereference.

#include <stdio.h>

void process(int *p) {
    int val = *p;        // If p is NULL → UB happens here
    if (p == NULL) {     // Optimizer may DELETE this check entirely!
        printf("p is null\n");
        return;
    }
    printf("value: %d\n", val);
}

int main() {
    process(NULL);
    return 0;
}
```

### Program 3 — Out-of-Bounds Access (`ub_oob_access.c`)

```c
// ub_oob_access.c
// UB Class: Out-of-Bounds Array Access (C11 §6.5.6)
// Description: Accessing array beyond its declared bounds is UB.
// Tools like AddressSanitizer will catch this at runtime.
// Static tools often miss this when index is computed dynamically.

#include <stdio.h>

int get_element(int arr[], int size, int index) {
    return arr[index];   // No bounds check — UB if index >= size
}

int main() {
    int data[5] = {1, 2, 3, 4, 5};
    printf("%d\n", get_element(data, 5, 10));  // index 10 is out of bounds!
    return 0;
}
```

### Program 4 — Invalid Shift (`ub_invalid_shift.c`)

```c
// ub_invalid_shift.c
// UB Class: Shift amount >= width of type (C11 §6.5.7)
// Description: Shifting a 32-bit int by 32 or more is UB.
// On x86, hardware ignores high bits of shift count, so 1<<32 == 1<<0 == 1.
// But C standard says this is UB — compiler may do anything.

#include <stdio.h>

int main() {
    int x = 1;
    int shift = 32;
    int result = x << shift;   // UB: shift amount equals bit width
    printf("1 << 32 = %d\n", result);

    // Also UB: negative shift
    int neg_result = x << -1;  // UB: negative shift amount
    printf("1 << -1 = %d\n", neg_result);
    return 0;
}
```

### Program 5 — Use-After-Free (`ub_use_after_free.c`)

```c
// ub_use_after_free.c
// UB Class: Use After Free (C11 §7.22.3)
// Description: Using a pointer after the memory it points to has been freed.
// The freed memory may be reallocated, causing data corruption.

#include <stdio.h>
#include <stdlib.h>

int main() {
    int *p = (int *)malloc(sizeof(int));
    if (p == NULL) return 1;

    *p = 42;
    free(p);             // Memory is freed

    printf("%d\n", *p); // UB: reading freed memory
    *p = 100;           // UB: writing to freed memory (heap corruption)

    free(p);            // UB: double free (also UB — see program 9)
    return 0;
}
```

### Program 6 — Uninitialized Variable Read (`ub_uninitialized.c`)

```c
// ub_uninitialized.c
// UB Class: Reading an uninitialized variable (C11 §6.3.2.1)
// Description: An uninitialized variable has an indeterminate value.
// Reading it is UB. The compiler may assume any value, or optimize
// code that depends on it in unexpected ways.

#include <stdio.h>

int main() {
    int x;             // Declared but not initialized
    int y = x + 1;    // UB: x has indeterminate value
    printf("y = %d\n", y);

    // More subtle: branch on uninitialized value
    int flag;
    if (flag) {        // UB: flag is uninitialized
        printf("flag is true\n");
    }
    return 0;
}
```

### Program 7 — Division by Zero (`ub_div_zero.c`)

```c
// ub_div_zero.c
// UB Class: Integer Division by Zero (C11 §6.5.5)
// Description: Integer division by zero is UB (not the same as IEEE 754
// floating point division, which returns infinity).
// On most platforms this raises SIGFPE and crashes the program.

#include <stdio.h>

int divide(int a, int b) {
    return a / b;    // UB if b == 0
}

int main() {
    int result = divide(10, 0);   // UB: division by zero
    printf("10 / 0 = %d\n", result);
    return 0;
}
```

### Program 8 — Strict Aliasing / Type Punning (`ub_type_punning.c`)

```c
// ub_type_punning.c
// UB Class: Strict Aliasing Violation (C11 §6.5, "effective type")
// Description: Accessing an object through a pointer of incompatible type
// violates the strict aliasing rule. LLVM assumes pointers of different
// types do not alias, enabling aggressive load/store optimizations.

#include <stdio.h>
#include <stdint.h>

float int_to_float_ub(int x) {
    // This is UB — violates strict aliasing
    float *fp = (float *)&x;
    return *fp;
}

// Correct way: use memcpy or a union
#include <string.h>
float int_to_float_safe(int x) {
    float result;
    memcpy(&result, &x, sizeof(float));
    return result;
}

int main() {
    int val = 0x3F800000;  // IEEE 754 representation of 1.0f
    printf("UB way:   %f\n", int_to_float_ub(val));
    printf("Safe way: %f\n", int_to_float_safe(val));
    return 0;
}
```

### Program 9 — Double Free (`ub_double_free.c`)

```c
// ub_double_free.c
// UB Class: Double Free (C11 §7.22.3.3)
// Description: Calling free() twice on the same pointer corrupts the
// heap allocator's internal metadata. This is a common security vulnerability.

#include <stdio.h>
#include <stdlib.h>

int main() {
    int *p = (int *)malloc(sizeof(int));
    if (p == NULL) return 1;

    *p = 10;
    printf("value: %d\n", *p);

    free(p);   // First free — OK
    free(p);   // Second free — UB: double free, heap corruption
    return 0;
}
```

### Program 10 — Modifying String Literal (`ub_string_literal.c`)

```c
// ub_string_literal.c
// UB Class: Modifying a String Literal (C11 §6.4.5)
// Description: String literals are stored in read-only memory segments.
// Attempting to modify them is UB — typically causes SIGSEGV.

#include <stdio.h>

int main() {
    char *str = "hello";  // Points to read-only memory
    str[0] = 'H';         // UB: attempt to modify string literal
    printf("%s\n", str);
    return 0;
}
```

### Safe Programs (for False Positive Testing)

```c
// safe_programs/safe_arithmetic.c
// No UB — correctly handles overflow with unsigned integers

#include <stdio.h>
#include <limits.h>
#include <stdint.h>

int main() {
    // Unsigned overflow is WELL DEFINED in C (wraps around)
    unsigned int x = UINT_MAX;
    unsigned int y = x + 1;   // Defined: wraps to 0
    printf("UINT_MAX + 1 = %u\n", y);

    // Safe: check before operation
    int a = INT_MAX;
    if (a < INT_MAX) {
        int b = a + 1;   // Safe: only executes when no overflow
        printf("b = %d\n", b);
    }
    return 0;
}
```

---

## 6. Phase 3 — LLVM/Clang Optimization Experiments

This phase is the most visually impressive part — you will **show** how LLVM changes code based on UB assumptions.

### 6.1 Generate LLVM IR at Different Optimization Levels

For each benchmark program, compile to LLVM IR at O0 and O2:

```bash
# For each program, run:
PROG="ub_signed_overflow"

# Unoptimized IR
clang -O0 -S -emit-llvm benchmarks/${PROG}.c -o llvm_experiments/results/${PROG}_O0.ll

# Optimized IR
clang -O2 -S -emit-llvm benchmarks/${PROG}.c -o llvm_experiments/results/${PROG}_O2.ll

# Compare the two
diff llvm_experiments/results/${PROG}_O0.ll llvm_experiments/results/${PROG}_O2.ll
```

### 6.2 Automation Script (`run_experiments.sh`)

Create this script to automate all IR generation:

```bash
#!/bin/bash
# scripts/run_experiments.sh
# Generates O0 and O2 LLVM IR for all benchmark programs

BENCHMARKS_DIR="./benchmarks"
RESULTS_DIR="./llvm_experiments/results"
mkdir -p "$RESULTS_DIR"

PROGRAMS=(
    "ub_signed_overflow"
    "ub_null_deref"
    "ub_oob_access"
    "ub_invalid_shift"
    "ub_use_after_free"
    "ub_uninitialized"
    "ub_div_zero"
    "ub_type_punning"
    "ub_double_free"
    "ub_string_literal"
)

for PROG in "${PROGRAMS[@]}"; do
    SRC="${BENCHMARKS_DIR}/${PROG}.c"
    if [ ! -f "$SRC" ]; then
        echo "WARNING: $SRC not found, skipping."
        continue
    fi

    echo "Processing $PROG..."

    # Generate LLVM IR
    clang -O0 -S -emit-llvm "$SRC" -o "${RESULTS_DIR}/${PROG}_O0.ll" 2>/dev/null
    clang -O2 -S -emit-llvm "$SRC" -o "${RESULTS_DIR}/${PROG}_O2.ll" 2>/dev/null

    # Generate assembly (for low-level comparison)
    clang -O0 -S "$SRC" -o "${RESULTS_DIR}/${PROG}_O0.s" 2>/dev/null
    clang -O2 -S "$SRC" -o "${RESULTS_DIR}/${PROG}_O2.s" 2>/dev/null

    # Save diff
    diff "${RESULTS_DIR}/${PROG}_O0.ll" "${RESULTS_DIR}/${PROG}_O2.ll" \
        > "${RESULTS_DIR}/${PROG}_diff.txt" 2>/dev/null

    echo "Done: $PROG"
done

echo "All experiments complete. Results in $RESULTS_DIR"
```

```bash
chmod +x scripts/run_experiments.sh
./scripts/run_experiments.sh
```

### 6.3 What to Look for in the IR

Open any `.ll` file and look for these key differences between O0 and O2:

| What to Look For | Meaning |
|-----------------|---------|
| Branch (`br`) disappears in O2 | Optimizer eliminated dead branch due to UB assumption |
| `icmp` instruction removed | Comparison was proven always true/false |
| `ret i32 1` directly (no compare) | Entire function body collapsed |
| `nsw` / `nuw` flags on `add` | "No Signed/Unsigned Wrap" — tells LLVM overflow is UB |
| `unreachable` instruction | Optimizer proved code path is dead |

### 6.4 Key Experiment — Signed Overflow

Compile and run the same program at O0 and O2 to see different outputs:

```bash
# Compile at O0 (no optimization)
clang -O0 -o test_O0 benchmarks/ub_signed_overflow.c
./test_O0
# Output: check_overflow(INT_MAX) = 0   (overflow actually happened)

# Compile at O2 (optimized)
clang -O2 -o test_O2 benchmarks/ub_signed_overflow.c
./test_O2
# Output: check_overflow(INT_MAX) = 1   (optimizer removed the else branch!)
```

**This is your smoking gun.** The same source code, different output — because LLVM exploited UB.

---

## 7. Phase 4 — Running Existing Tools

### 7.1 UBSan (UndefinedBehaviourSanitizer)

UBSan instruments the binary to detect UB at runtime.

```bash
#!/bin/bash
# scripts/run_ubsan.sh

BENCHMARKS_DIR="./benchmarks"
OUTPUT_FILE="./tool_results/ubsan_results.txt"
mkdir -p tool_results

echo "====== UBSan Results ======" > "$OUTPUT_FILE"
echo "Date: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

PROGRAMS=(
    "ub_signed_overflow" "ub_null_deref" "ub_oob_access"
    "ub_invalid_shift" "ub_use_after_free" "ub_uninitialized"
    "ub_div_zero" "ub_type_punning" "ub_double_free" "ub_string_literal"
)

for PROG in "${PROGRAMS[@]}"; do
    SRC="${BENCHMARKS_DIR}/${PROG}.c"
    echo "--- $PROG ---" >> "$OUTPUT_FILE"

    # Compile with UBSan + AddressSanitizer
    clang -fsanitize=undefined,address -fno-omit-frame-pointer \
          -g -O1 "$SRC" -o "/tmp/${PROG}_ubsan" 2>> "$OUTPUT_FILE"

    # Run and capture output + sanitizer messages
    timeout 5 "/tmp/${PROG}_ubsan" >> "$OUTPUT_FILE" 2>&1
    EXIT_CODE=$?

    if [ $EXIT_CODE -ne 0 ]; then
        echo "Exit code: $EXIT_CODE (crash or sanitizer trigger)" >> "$OUTPUT_FILE"
    else
        echo "Exit code: 0 (no runtime UB detected by UBSan)" >> "$OUTPUT_FILE"
    fi

    echo "" >> "$OUTPUT_FILE"
done

echo "UBSan results saved to $OUTPUT_FILE"
```

```bash
chmod +x scripts/run_ubsan.sh
./scripts/run_ubsan.sh
cat tool_results/ubsan_results.txt
```

### 7.2 Clang Static Warnings

```bash
#!/bin/bash
# scripts/run_clang_warnings.sh

OUTPUT_FILE="./tool_results/clang_warnings.txt"
echo "====== Clang Static Warnings ======" > "$OUTPUT_FILE"

for SRC in benchmarks/*.c; do
    PROG=$(basename "$SRC" .c)
    echo "--- $PROG ---" >> "$OUTPUT_FILE"
    clang -Wall -Wextra -Weverything -Wno-padded \
          -fsyntax-only "$SRC" 2>> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done
```

### 7.3 clang-tidy

```bash
#!/bin/bash
# scripts/run_clang_tidy.sh

OUTPUT_FILE="./tool_results/clang_tidy_results.txt"
echo "====== clang-tidy Results ======" > "$OUTPUT_FILE"

for SRC in benchmarks/*.c; do
    PROG=$(basename "$SRC" .c)
    echo "--- $PROG ---" >> "$OUTPUT_FILE"
    clang-tidy "$SRC" \
        --checks="clang-analyzer-*,bugprone-*,cert-*,misc-*" \
        -- -std=c11 2>> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done
```

### 7.4 cppcheck

```bash
#!/bin/bash
# scripts/run_cppcheck.sh

OUTPUT_FILE="./tool_results/cppcheck_results.txt"
echo "====== cppcheck Results ======" > "$OUTPUT_FILE"

cppcheck --enable=all \
         --std=c11 \
         --verbose \
         --suppress=missingIncludeSystem \
         benchmarks/ 2>> "$OUTPUT_FILE"

echo "cppcheck done."
```

### 7.5 Run All Tools at Once

```bash
#!/bin/bash
# scripts/run_all_tools.sh

echo "Running all tools..."
bash scripts/run_ubsan.sh
bash scripts/run_clang_warnings.sh
bash scripts/run_clang_tidy.sh
bash scripts/run_cppcheck.sh
echo "All tools complete. Results in tool_results/"
```

```bash
chmod +x scripts/run_all_tools.sh
./scripts/run_all_tools.sh
```

---

## 8. Phase 5 — LLM Evaluation

### 8.1 Prompt Template

For each benchmark program, use this exact prompt with the LLM (Claude, GPT-4, or any other):

```
You are an expert C/C++ compiler engineer specializing in undefined behaviour analysis.

Analyze the following C program carefully:

[PASTE PROGRAM CODE HERE]

Please answer the following questions:

1. DETECTION: Does this program contain undefined behaviour (UB)? Answer YES or NO.

2. IDENTIFICATION: If YES, identify exactly which line(s) contain UB and what type of UB it is (e.g., signed integer overflow, null pointer dereference, out-of-bounds access, etc.).

3. EXPLANATION: Explain WHY this is undefined behaviour according to the C standard. Cite the relevant behaviour if possible.

4. LLVM OPTIMIZATION: How might LLVM/Clang legally optimize this code based on the assumption that UB does not occur? Describe what the optimized code might look like or what branches might be eliminated.

5. SEVERITY: Rate the severity of this UB: Low / Medium / High / Critical.

6. FIX: Show the corrected version of the code that eliminates the UB.
```

### 8.2 Manual LLM Testing (Simplest Approach)

1. Open [claude.ai](https://claude.ai) or [chat.openai.com](https://chat.openai.com)
2. Paste the prompt template + each program's code
3. Copy the response into `llm_results/llm_<program_name>.txt`
4. Note: Did the LLM detect UB? (YES/NO), Did it correctly explain it? (YES/NO)

### 8.3 Automated LLM Querying via API (Optional)

If you have access to an LLM API, use this Python script:

```python
#!/usr/bin/env python3
# scripts/llm_query.py
# Queries an LLM API for UB analysis of each benchmark program

import os
import glob
import requests
import json
import time

# Configuration — edit these
LLM_API_URL = "https://api.anthropic.com/v1/messages"
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
MODEL = "claude-opus-4-5"

PROMPT_TEMPLATE = """You are an expert C/C++ compiler engineer.

Analyze this C program for undefined behaviour:

{code}

Answer:
1. DETECTION: Does this contain UB? YES or NO.
2. IDENTIFICATION: Which line(s) and what type of UB?
3. EXPLANATION: Why is this UB per the C standard?
4. LLVM OPTIMIZATION: How might LLVM optimize based on UB assumptions?
5. SEVERITY: Low / Medium / High / Critical
6. FIX: Show corrected code.
"""

def query_llm(code: str) -> str:
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": MODEL,
        "max_tokens": 1500,
        "messages": [
            {"role": "user", "content": PROMPT_TEMPLATE.format(code=code)}
        ]
    }
    response = requests.post(LLM_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        return f"ERROR: {response.status_code} - {response.text}"

def main():
    os.makedirs("llm_results", exist_ok=True)
    c_files = glob.glob("benchmarks/*.c")

    for filepath in sorted(c_files):
        prog_name = os.path.basename(filepath).replace(".c", "")
        output_file = f"llm_results/llm_{prog_name}.txt"

        if os.path.exists(output_file):
            print(f"Skipping {prog_name} (already done)")
            continue

        print(f"Querying LLM for: {prog_name}")
        with open(filepath, "r") as f:
            code = f.read()

        response = query_llm(code)

        with open(output_file, "w") as f:
            f.write(f"=== LLM Analysis: {prog_name} ===\n\n")
            f.write(response)

        print(f"  Saved to {output_file}")
        time.sleep(1)  # Rate limit — be polite to the API

    print("LLM querying complete.")

if __name__ == "__main__":
    main()
```

```bash
export ANTHROPIC_API_KEY="your_key_here"
python3 scripts/llm_query.py
```

### 8.4 Recording LLM Results

After getting responses, manually record results in a structured way:

For each program, note:
- Did LLM detect UB? (YES / NO / PARTIAL)
- Was the explanation correct? (CORRECT / WRONG / PARTIAL)
- Did it predict LLVM optimization correctly? (YES / NO / PARTIAL)
- False positive on safe programs? (YES / NO)

---

## 9. Phase 6 — Building the Comparison Table

### 9.1 Manual Comparison Table

After collecting results from all tools and the LLM, fill in this table:

| Program | UB Type | UBSan | Clang Warnings | clang-tidy | cppcheck | LLM Detection | LLM Explanation |
|---------|---------|-------|----------------|------------|----------|---------------|-----------------|
| ub_signed_overflow.c | Signed overflow | ✓ | ✓ (partial) | ✗ | ✗ | ✓ | ✓ |
| ub_null_deref.c | Null dereference | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| ub_oob_access.c | Out-of-bounds | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ |
| ub_invalid_shift.c | Invalid shift | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| ub_use_after_free.c | Use-after-free | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ |
| ub_uninitialized.c | Uninitialized read | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ |
| ub_div_zero.c | Division by zero | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| ub_type_punning.c | Strict aliasing | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| ub_double_free.c | Double free | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ |
| ub_string_literal.c | String literal mod | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| safe_arithmetic.c | None (safe) | ✗ | ✗ | ✗ | ✗ | ✗ | N/A |

> Note: Fill this table with your actual results — these are examples.

### 9.2 Automated Table Generator (`compare_results.py`)

```python
#!/usr/bin/env python3
# scripts/compare_results.py
# Reads tool output files and builds a summary table

import os
import csv

# You fill this dict manually based on your actual results
results = {
    "ub_signed_overflow":  {"ub_type": "Signed Overflow",    "ubsan": True,  "clang_warn": True,  "clang_tidy": False, "cppcheck": False, "llm_detect": True,  "llm_explain": True},
    "ub_null_deref":       {"ub_type": "Null Dereference",   "ubsan": True,  "clang_warn": False, "clang_tidy": True,  "cppcheck": True,  "llm_detect": True,  "llm_explain": True},
    "ub_oob_access":       {"ub_type": "Out-of-Bounds",      "ubsan": True,  "clang_warn": False, "clang_tidy": False, "cppcheck": False, "llm_detect": True,  "llm_explain": True},
    "ub_invalid_shift":    {"ub_type": "Invalid Shift",      "ubsan": True,  "clang_warn": True,  "clang_tidy": False, "cppcheck": False, "llm_detect": True,  "llm_explain": True},
    "ub_use_after_free":   {"ub_type": "Use-After-Free",     "ubsan": True,  "clang_warn": False, "clang_tidy": True,  "cppcheck": False, "llm_detect": True,  "llm_explain": True},
    "ub_uninitialized":    {"ub_type": "Uninitialized Read", "ubsan": False, "clang_warn": True,  "clang_tidy": False, "cppcheck": True,  "llm_detect": True,  "llm_explain": True},
    "ub_div_zero":         {"ub_type": "Division by Zero",   "ubsan": True,  "clang_warn": False, "clang_tidy": True,  "cppcheck": True,  "llm_detect": True,  "llm_explain": True},
    "ub_type_punning":     {"ub_type": "Strict Aliasing",    "ubsan": False, "clang_warn": False, "clang_tidy": False, "cppcheck": False, "llm_detect": True,  "llm_explain": True},
    "ub_double_free":      {"ub_type": "Double Free",        "ubsan": True,  "clang_warn": False, "clang_tidy": False, "cppcheck": False, "llm_detect": True,  "llm_explain": True},
    "ub_string_literal":   {"ub_type": "String Literal Mod", "ubsan": True,  "clang_warn": True,  "clang_tidy": False, "cppcheck": False, "llm_detect": True,  "llm_explain": True},
    "safe_arithmetic":     {"ub_type": "None (Safe)",        "ubsan": False, "clang_warn": False, "clang_tidy": False, "cppcheck": False, "llm_detect": False, "llm_explain": True},
}

def bool_to_symbol(b):
    return "✓" if b else "✗"

os.makedirs("results", exist_ok=True)

# Write CSV
with open("results/comparison_table.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Program", "UB Type", "UBSan", "Clang Warnings", "clang-tidy", "cppcheck", "LLM Detection", "LLM Explanation"])
    for prog, data in results.items():
        writer.writerow([
            prog, data["ub_type"],
            bool_to_symbol(data["ubsan"]),
            bool_to_symbol(data["clang_warn"]),
            bool_to_symbol(data["clang_tidy"]),
            bool_to_symbol(data["cppcheck"]),
            bool_to_symbol(data["llm_detect"]),
            bool_to_symbol(data["llm_explain"]),
        ])

# Write Markdown
with open("results/comparison_table.md", "w") as f:
    f.write("# UB Detection Tool Comparison\n\n")
    f.write("| Program | UB Type | UBSan | Clang Warn | clang-tidy | cppcheck | LLM Detect | LLM Explain |\n")
    f.write("|---------|---------|-------|------------|------------|----------|------------|-------------|\n")
    for prog, data in results.items():
        f.write(f"| {prog} | {data['ub_type']} | {bool_to_symbol(data['ubsan'])} | {bool_to_symbol(data['clang_warn'])} | {bool_to_symbol(data['clang_tidy'])} | {bool_to_symbol(data['cppcheck'])} | {bool_to_symbol(data['llm_detect'])} | {bool_to_symbol(data['llm_explain'])} |\n")

    # Summary statistics
    total = len([k for k, v in results.items() if v["ub_type"] != "None (Safe)"])
    f.write(f"\n## Summary\n\n")
    f.write(f"Total UB programs: {total}\n\n")
    for tool, key in [("UBSan", "ubsan"), ("Clang Warnings", "clang_warn"), ("clang-tidy", "clang_tidy"), ("cppcheck", "cppcheck"), ("LLM", "llm_detect")]:
        detected = sum(1 for k, v in results.items() if v["ub_type"] != "None (Safe)" and v[key])
        f.write(f"- **{tool}**: {detected}/{total} detected ({100*detected//total}%)\n")

print("Comparison table saved to results/")
```

```bash
python3 scripts/compare_results.py
cat results/comparison_table.md
```

---

## 10. Phase 7 — Report Writing

Your report should cover these sections:

### 10.1 Report Structure

```
1. Introduction
   - What is UB in C/C++?
   - Why is it dangerous?
   - Research question

2. Background
   - C/C++ standard and UB definition
   - How LLVM exploits UB (with your IR examples)
   - Existing tools overview

3. Methodology
   - How you created benchmark programs
   - What tools you ran and how
   - How you prompted the LLM

4. Results
   - Comparison table (your filled table)
   - Notable findings per UB class
   - Example IR diffs (signed overflow is great here)

5. Analysis
   - Soundness: Does the tool catch all UB? (False Negatives)
   - Completeness: Does it raise false alarms? (False Positives)
   - LLM Strengths: What did it do better than static tools?
   - LLM Weaknesses: Where did it fail or hallucinate?

6. Proposed Hybrid Pipeline
   - Diagram of combined approach
   - When to use static tools vs LLM
   - Expected improvement in coverage

7. Conclusion
   - Summary of findings
   - Future work

8. References
```

### 10.2 Key Points to Make in the Report

**About UBSan:**
- Advantage: Very accurate — true positives only (no false positives at runtime)
- Disadvantage: Runtime only — must actually execute the buggy path. A UB inside an untaken `if` branch will not be caught.

**About clang-tidy / cppcheck (Static Tools):**
- Advantage: No need to run the program
- Disadvantage: Many false negatives — miss complex aliasing, dynamic indices, etc.
- Cannot reason about semantic meaning, only patterns

**About LLM:**
- Advantage: Can reason about semantics, explain, predict optimizer behaviour
- Advantage: Catches UB classes that static tools miss (strict aliasing, uninitialized reads)
- Disadvantage: May hallucinate — confidently wrong
- Disadvantage: Not formally sound — no guarantees
- Disadvantage: Context limit — cannot analyze very large programs at once

---

## 11. Phase 8 — Hybrid Pipeline Proposal

### 11.1 Proposed Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  C/C++ Source Code                       │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │   Stage 1: Fast Filter  │
          │   clang -Wall -Wextra   │
          │   cppcheck              │
          └────────────┬────────────┘
                       │
          Flags suspicious code regions
                       │
          ┌────────────▼────────────┐
          │   Stage 2: Deep Static  │
          │   clang-tidy            │
          │   clang-analyzer        │
          └────────────┬────────────┘
                       │
          Narrows down candidates
                       │
          ┌────────────▼────────────┐
          │   Stage 3: LLM Analysis │
          │   Feed flagged snippets │
          │   Ask for UB type,      │
          │   explanation, severity │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │   Stage 4: Runtime Check│  ← Optional
          │   UBSan on test suite   │
          │   Validates LLM verdict │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │   Final UB Report       │
          │   Ranked by severity    │
          │   With explanations     │
          └─────────────────────────┘
```

### 11.2 Why This Hybrid Approach Is Better

| Stage | Role | Benefit |
|-------|------|---------|
| Fast static (clang, cppcheck) | Pre-filter obvious UB | Speed — don't send everything to LLM |
| Deep static (clang-tidy) | Pattern matching | Catches well-known UB patterns formally |
| LLM | Semantic reasoning | Catches subtle UB, provides explanations, handles novel patterns |
| UBSan | Ground truth validation | Confirms LLM findings with runtime evidence |

---

## 12. Final Presentation Guide

### Slide Structure (15–20 slides)

1. **Title Slide** — Assignment 13, team names
2. **What is Undefined Behaviour?** — Definition + 2 shocking examples
3. **Why UB Matters** — Show the INT_MAX+1 optimization trick live
4. **LLVM IR Demo** — Side-by-side O0 vs O2 IR for signed overflow
5. **Existing Tools Overview** — UBSan, clang-tidy, cppcheck
6. **Our Benchmark Set** — Table of 10 programs and UB classes
7. **Tool Results** — Comparison table
8. **LLM Methodology** — How you prompted the LLM
9. **LLM Results** — What it got right and wrong
10. **LLM vs Tools — Analysis** — Soundness, completeness, false positives
11. **LLM Strengths** — What it uniquely does well
12. **LLM Weaknesses** — Hallucinations, limitations
13. **Hybrid Pipeline** — Your proposed architecture diagram
14. **Conclusion** — Key takeaways
15. **Future Work** — What could be done next
16. **References**

### Live Demo (Optional but impressive)

During the presentation, show live:
```bash
# Show the bug
cat benchmarks/ub_signed_overflow.c

# Show different outputs
./test_O0    # shows 0
./test_O2    # shows 1 — same code, different behaviour!

# Show UBSan catching it
./test_ubsan
```

---

## 13. Common Errors & Troubleshooting

### Error: `clang: command not found`
```bash
# Try with version suffix
clang-17 --version
# Or add to PATH
export PATH=/usr/lib/llvm-17/bin:$PATH
```

### Error: UBSan not available
```bash
# Make sure you have the full LLVM suite
sudo apt install clang llvm compiler-rt
```

### Error: `clang-tidy: no such file`
```bash
sudo apt install clang-tidy
# Or use versioned
clang-tidy-17
```

### LLM gives wrong answer
- Try rephrasing the prompt to be more specific
- Break the program into smaller snippets
- Explicitly ask: "Focus on line 12 — is this UB?"
- This is actually useful data — note it as a false negative in your results!

### IR diff shows no changes
- Some UB may not trigger optimizer changes at O2
- Try O3: `clang -O3 -S -emit-llvm ...`
- Or add `-fno-sanitize=undefined` to ensure sanitizer doesn't interfere

---

## 14. References

1. **ISO/IEC 9899:2011** (C11 Standard) — The authoritative source for UB definitions
2. **LLVM Language Reference Manual** — https://llvm.org/docs/LangRef.html
3. **Clang Static Analyzer** — https://clang-analyzer.llvm.org/
4. **UBSan Documentation** — https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html
5. **AddressSanitizer** — https://clang.llvm.org/docs/AddressSanitizer.html
6. **cppcheck manual** — http://cppcheck.sourceforge.net/manual.pdf
7. **"What Every C Programmer Should Know About Undefined Behavior"** — Chris Lattner's LLVM Blog (2011) — Must read!
8. **CWE/SANS Top 25** — https://cwe.mitre.org/top25/
9. **Juliet Test Suite** — https://samate.nist.gov/SARD/test-suites/112

---

## Quick Start Checklist

- [ ] Install LLVM/Clang, clang-tidy, cppcheck
- [ ] Create project directory structure
- [ ] Write 10 benchmark C programs (one per UB class)
- [ ] Write 3 safe programs for false positive testing
- [ ] Run `scripts/run_experiments.sh` to generate IR files
- [ ] Compare O0 vs O2 IR for signed overflow manually
- [ ] Run `scripts/run_all_tools.sh` to collect tool results
- [ ] Query LLM for each program using the prompt template
- [ ] Fill in comparison table manually
- [ ] Run `scripts/compare_results.py` to generate formatted table
- [ ] Write report following the structure in Phase 7
- [ ] Prepare presentation slides
- [ ] Practice live demo

---

*This README was created as part of Assignment 13 — Compiler Design Lab.*  
*Refer to individual phase sections for detailed implementation steps.*
