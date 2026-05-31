#!/bin/bash
set -u

BENCHMARKS_DIR="./benchmarks"
OUTPUT_FILE="./tool_results/ubsan_results.txt"
mkdir -p tool_results

echo "====== UBSan Results ======" > "$OUTPUT_FILE"
echo "Date: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

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
	BIN="/tmp/${PROG}_ubsan"

	if [ ! -f "$SRC" ]; then
		echo "--- $PROG ---" >> "$OUTPUT_FILE"
		echo "Missing source: $SRC" >> "$OUTPUT_FILE"
		echo "" >> "$OUTPUT_FILE"
		continue
	fi

	echo "--- $PROG ---" >> "$OUTPUT_FILE"

	clang -fsanitize=undefined,address -fno-omit-frame-pointer -g -O1 "$SRC" -o "$BIN" >> "$OUTPUT_FILE" 2>&1
	timeout 5 "$BIN" >> "$OUTPUT_FILE" 2>&1
	EXIT_CODE=$?

	if [ $EXIT_CODE -ne 0 ]; then
		echo "Exit code: $EXIT_CODE (crash or sanitizer trigger)" >> "$OUTPUT_FILE"
	else
		echo "Exit code: 0 (no runtime UB detected by UBSan)" >> "$OUTPUT_FILE"
	fi
	echo "" >> "$OUTPUT_FILE"
done

echo "UBSan results saved to $OUTPUT_FILE"
