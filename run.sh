#!/bin/bash
set -euo pipefail

# Top-level run script: sync testcases, run experiments and analysis, then compare
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Ensuring testcases directory exists..."
if [ ! -d "$ROOT_DIR/testcases" ]; then
    echo "Creating testcases/ by copying benchmarks/ (if present)..."
    if [ -d "$ROOT_DIR/benchmarks" ]; then
        cp -r "$ROOT_DIR/benchmarks" "$ROOT_DIR/testcases"
    else
        mkdir -p "$ROOT_DIR/testcases"
    fi
fi

echo "Running LLVM experiments..."
bash scripts/run_experiments.sh || echo "run_experiments.sh failed"

echo "Running all analysis tools..."
bash scripts/run_all_tools.sh || echo "run_all_tools.sh failed"

echo "Querying LLM (if configured)..."
if [ -f scripts/llm_query.py ]; then
    python scripts/llm_query.py || echo "llm_query.py failed"
fi

echo "Comparing results..."
if [ -f scripts/compare_results.py ]; then
    python scripts/compare_results.py || echo "compare_results.py failed"
fi

echo "Run complete. Results in tool_results/, llvm_experiments/results/, llm_results/, results/"
