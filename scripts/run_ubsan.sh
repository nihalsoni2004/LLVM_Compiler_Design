#!/bin/bash
# scripts/run_ubsan.sh

BENCHMARKS_DIR="./testcases"
OUTPUT_FILE="./tool_results/ubsan_results.txt"
mkdir -p tool_results

echo "====== UBSan Results ======" > "$OUTPUT_FILE"
echo "Date: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

PROGRAMS=(
    "ub_signed_overflow" "ub_null_deref" "ub_oob_access"
    "ub_invalid_shift" "ub_use_after_free" "ub_uninitialized"
    "ub_div_zero" "ub_type_punning" "ub_double_free" "ub_string_literal"
    "safe_programs/safe_arithmetic" "safe_programs/safe_array" "safe_programs/safe_pointers"
)

for PROG in "${PROGRAMS[@]}"; do
    SRC="${BENCHMARKS_DIR}/${PROG}.c"
    PROG_NAME=$(basename "$PROG")
    echo "--- $PROG_NAME ---" >> "$OUTPUT_FILE"

    if [ ! -f "$SRC" ]; then
        echo "WARNING: $SRC not found, skipping."
        continue
    fi

    # Compile with UBSan + AddressSanitizer
    clang -fsanitize=undefined,address -fno-omit-frame-pointer \
          -g -O1 "$SRC" -o "/tmp/${PROG_NAME}_ubsan" 2>> "$OUTPUT_FILE"

    # Run and capture output + sanitizer messages
    timeout 5 "/tmp/${PROG_NAME}_ubsan" >> "$OUTPUT_FILE" 2>&1
    EXIT_CODE=$?

    if [ $EXIT_CODE -ne 0 ]; then
        echo "Exit code: $EXIT_CODE (crash or sanitizer trigger)" >> "$OUTPUT_FILE"
    else
        echo "Exit code: 0 (no runtime UB detected by UBSan)" >> "$OUTPUT_FILE"
    fi

    echo "" >> "$OUTPUT_FILE"
done

echo "UBSan results saved to $OUTPUT_FILE"
