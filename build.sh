#!/bin/bash
set -euo pipefail

# Build/setup helper: create venv and install Python deps
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

echo "Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    pip install requests pandas tabulate matplotlib streamlit python-pptx
fi

echo "Build/setup complete. Activate with: source $VENV_DIR/bin/activate"
