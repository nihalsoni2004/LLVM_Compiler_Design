#!/bin/bash
# scripts/run_clang_warnings.sh

OUTPUT_FILE="./tool_results/clang_warnings.txt"
mkdir -p tool_results
echo "====== Clang Static Warnings ======" > "$OUTPUT_FILE"

for SRC in testcases/*.c testcases/safe_programs/*.c; do
    if [ ! -f "$SRC" ]; then
        continue
    fi
    PROG=$(basename "$SRC" .c)
    echo "--- $PROG ---" >> "$OUTPUT_FILE"
    clang -Wall -Wextra -Weverything -Wno-padded \
          -fsyntax-only "$SRC" 2>> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done

echo "Clang warnings saved to $OUTPUT_FILE"
