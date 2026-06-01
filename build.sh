#!/bin/bash
# build.sh
# Build helper (creates venv and installs python dependencies)

echo "=== Building Environment ==="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed. Please install it first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "Virtual environment (.venv) already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing python packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "WARNING: requirements.txt not found."
fi

echo "=== Environment Build Complete! ==="
