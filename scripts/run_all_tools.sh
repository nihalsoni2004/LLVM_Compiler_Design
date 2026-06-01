#!/bin/bash
# scripts/run_all_tools.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running all tools..."
bash "$SCRIPT_DIR/run_ubsan.sh"
bash "$SCRIPT_DIR/run_clang_warnings.sh"
bash "$SCRIPT_DIR/run_clang_tidy.sh"
bash "$SCRIPT_DIR/run_cppcheck.sh"
echo "All tools complete. Results in tool_results/"
