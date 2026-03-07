#!/bin/bash
# DevSpec Development Loop Entry Point

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_ROOT="${1:-spec}"

echo "Starting DevSpec AI Development Loop..."
echo ""

# Run the AI dev loop
python3 "$SCRIPT_DIR/ai-dev-loop.py" "$SPEC_ROOT"
