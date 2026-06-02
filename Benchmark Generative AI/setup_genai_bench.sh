#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VENV_DIR:-$SCRIPT_DIR/.venv-genai-bench}"

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install genai-bench
python3 "$SCRIPT_DIR/patch_genai_bench.py" "$VENV_DIR"

echo "Installed genai-bench into: $VENV_DIR"
echo "Use:"
echo "  export GENAI_BENCH_BIN=\"$VENV_DIR/bin/genai-bench\""
