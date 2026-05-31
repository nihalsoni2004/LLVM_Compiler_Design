#!/bin/bash
set -e

echo "Running all tools..."
bash scripts/run_ubsan.sh
bash scripts/run_clang_warnings.sh
bash scripts/run_clang_tidy.sh
bash scripts/run_cppcheck.sh
echo "All tools complete. Results in tool_results/"
