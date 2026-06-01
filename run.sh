#!/bin/bash
# run.sh
# Run full pipeline (experiments, tools, LLM queries, comparison)

echo "=== Starting LLVM Compiler Design Project Pipeline ==="

# Check virtual environment
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "WARNING: .venv directory not found. Running with global python if available."
fi

# 1. Run LLVM experiments
echo ""
echo "--- Phase 3: Generating LLVM IR Optimization Experiments ---"
bash scripts/run_experiments.sh

# 2. Run static/dynamic tools
echo ""
echo "--- Phase 4: Running Existing Tools (UBSan, Clang Warnings, clang-tidy, cppcheck) ---"
bash scripts/run_all_tools.sh

# 3. Query LLM
echo ""
echo "--- Phase 5: Querying LLM (Gemini) for UB Analysis ---"
if [ -n "$GEMINI_API_KEY_1" ] || [ -n "$GEMINI_API_KEY_2" ] || [ -n "$GEMINI_API_KEY_3" ]; then
    python scripts/llm_query.py
else
    echo "Skipping automated LLM query because GEMINI_API_KEY_1, GEMINI_API_KEY_2, or GEMINI_API_KEY_3 is not set."
    echo "To run LLM querying automatically, set your API key, e.g.:"
    echo "  export GEMINI_API_KEY_1=\"AIzaSy...\""
fi

# 4. Generate Comparison Table
echo ""
echo "--- Phase 6: Generating Comparison Tables ---"
python scripts/compare_results.py

echo ""
echo "=== Pipeline Completed! ==="
echo "You can now run the Streamlit UI to view the 5-way comparison table:"
echo "  streamlit run ui/comparison_ui.py"
