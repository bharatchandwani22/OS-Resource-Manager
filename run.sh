#!/usr/bin/env bash
# ==============================================================================
# OS Simulator Launcher (Bash Entrypoint)
# Environment verification, dependency checks, and integrated CLI launcher.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "    OPERATING SYSTEM RESOURCE MANAGEMENT SIMULATOR       "
echo "=========================================================="

# Check Python 3
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "[ERROR] Python 3 was not found in PATH. Please install Python 3.8+."
    exit 1
fi

PYTHON_CMD="python"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
fi

# Set PYTHONPATH to project root
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Pass through arguments or launch interactive menu
if [ $# -gt 0 ]; then
    "$PYTHON_CMD" main.py "$@"
else
    "$PYTHON_CMD" main.py
fi
