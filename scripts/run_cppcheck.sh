#!/bin/bash
# scripts/run_cppcheck.sh

OUTPUT_FILE="./tool_results/cppcheck_results.txt"
mkdir -p tool_results
echo "====== cppcheck Results ======" > "$OUTPUT_FILE"

cppcheck --enable=all \
         --std=c11 \
         --verbose \
         --suppress=missingIncludeSystem \
         testcases/ >> "$OUTPUT_FILE" 2>&1

echo "cppcheck results saved to $OUTPUT_FILE"
