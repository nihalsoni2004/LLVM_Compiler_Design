#!/bin/bash
set -euo pipefail

# Sync benchmarks/ -> testcases/ (safe copy) to satisfy repo naming requirements
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT_DIR/benchmarks"
DST="$ROOT_DIR/testcases"

if [ ! -d "$SRC" ]; then
    echo "No benchmarks/ directory found at $SRC"
    exit 1
fi

echo "Copying $SRC -> $DST"
rm -rf "$DST"
cp -r "$SRC" "$DST"
echo "Done. testcases/ is ready."
