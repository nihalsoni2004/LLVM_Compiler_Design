#!/bin/bash
# scripts/run_experiments.sh
# Generates O0 and O2 LLVM IR for all benchmark programs

BENCHMARKS_DIR="./testcases"
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
