# Testcases / Benchmarks

This directory contains the canonical benchmark C programs used for the UB experiments.

Purpose
- Provide one small, focused C program per UB class (and a few safe programs for false-positive checks).

Contents (each file targets a single UB class)
- `ub_signed_overflow.c` — signed integer overflow
- `ub_null_deref.c` — null pointer dereference
- `ub_oob_access.c` — out-of-bounds array access
- `ub_invalid_shift.c` — invalid shift amounts
- `ub_use_after_free.c` — use-after-free
- `ub_uninitialized.c` — reading uninitialized variables
- `ub_div_zero.c` — integer division by zero
- `ub_type_punning.c` — strict aliasing / type punning
- `ub_double_free.c` — double free
- `ub_string_literal.c` — modifying string literal

Safe programs (for false-positive validation)
- `safe_programs/safe_arithmetic.c`
- `safe_programs/safe_array.c`
- `safe_programs/safe_pointers.c`

How to run a single testcase

1. Create and activate the venv (see top-level README):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Compile with Clang and run with UBSan/ASan:

```bash
clang -fsanitize=undefined,address -fno-omit-frame-pointer -g -O1 testcases/ub_signed_overflow.c -o /tmp/ub_signed_overflow
/tmp/ub_signed_overflow
```

3. Generate LLVM IR at O0/O2 for comparison:

```bash
clang -O0 -S -emit-llvm testcases/ub_signed_overflow.c -o llvm_experiments/results/ub_signed_overflow_O0.ll
clang -O2 -S -emit-llvm testcases/ub_signed_overflow.c -o llvm_experiments/results/ub_signed_overflow_O2.ll
diff llvm_experiments/results/ub_signed_overflow_O0.ll llvm_experiments/results/ub_signed_overflow_O2.ll
```

Why `testcases/` exists
- This is the canonical folder used by all automation scripts. Do not keep duplicates (like `benchmarks/`) — all test sources must live here.

