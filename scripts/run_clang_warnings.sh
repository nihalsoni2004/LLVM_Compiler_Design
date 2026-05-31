#!/bin/bash
set -u

OUTPUT_FILE="./tool_results/clang_warnings.txt"
mkdir -p tool_results

echo "====== Clang Static Warnings ======" > "$OUTPUT_FILE"

for SRC in benchmarks/*.c benchmarks/safe_programs/*.c; do
	[ -f "$SRC" ] || continue
	PROG=$(basename "$SRC" .c)
	echo "--- $PROG ---" >> "$OUTPUT_FILE"
	clang -Wall -Wextra -Weverything -Wno-padded -fsyntax-only "$SRC" >> "$OUTPUT_FILE" 2>&1
	echo "" >> "$OUTPUT_FILE"
done

echo "Clang warnings saved to $OUTPUT_FILE"
