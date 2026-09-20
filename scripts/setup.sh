#!/usr/bin/env bash
# ==============================================================================
# scripts/setup.sh - Unix/macOS Bash Setup Wrapper
# ==============================================================================
# Usage:
#   ./scripts/setup.sh [--dry-run] [--check] [--finalize]
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=================================================================="
echo " GitHub Repository Template Initialization (Bash) "
echo "=================================================================="

PYTHON_CMD="python3"
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    PYTHON_CMD="python"
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        echo "[ERROR] Python 3 is required but could not be located in PATH." >&2
        exit 1
    fi
fi

if [[ "$*" == *"--check"* ]]; then
    echo ""
    echo "[*] Validating file naming conventions..."
    "$PYTHON_CMD" "${SCRIPT_DIR}/validate-filenames.py"
    echo ""
    echo "[*] Checking unresolved template placeholders..."
    "$PYTHON_CMD" "${SCRIPT_DIR}/apply-template.py" "--check"
    exit 0
fi

"$PYTHON_CMD" "${SCRIPT_DIR}/apply-template.py" "$@"

if [[ "$*" != *"--dry-run"* ]]; then
    echo ""
    echo "[*] Configuring Git Hooks..."
    "$PYTHON_CMD" "${SCRIPT_DIR}/install-hooks.py"
fi

echo ""
echo "[+] Setup completed successfully!"
