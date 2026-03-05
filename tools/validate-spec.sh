#!/bin/bash
# OpenSpec Validation Script
# Quick validation entry point

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_ROOT="${1:-spec}"

echo "=== OpenSpec Quick Validation ==="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Run linter
echo "Running spec linter..."
python3 "$SCRIPT_DIR/spec-linter.py" "$SPEC_ROOT"

echo ""
echo "Validation complete!"
