#!/bin/bash
set -u

OUTPUT_FILE="./tool_results/clang_tidy_results.txt"
mkdir -p tool_results

echo "====== clang-tidy Results ======" > "$OUTPUT_FILE"

for SRC in testcases/*.c testcases/safe_programs/*.c; do
	[ -f "$SRC" ] || continue
	PROG=$(basename "$SRC" .c)
	echo "--- $PROG ---" >> "$OUTPUT_FILE"
	clang-tidy "$SRC" --checks="clang-analyzer-*,bugprone-*,cert-*,misc-*" -- -std=c11 >> "$OUTPUT_FILE" 2>&1
	echo "" >> "$OUTPUT_FILE"
done

echo "clang-tidy results saved to $OUTPUT_FILE"
