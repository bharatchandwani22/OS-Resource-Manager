#!/usr/bin/env bash
# ==============================================================================
# Launch OS Resource Management Simulator Web Application (Bash Launcher)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

echo "===================================================================="
echo "  LAUNCHING OS RESOURCE MANAGEMENT SIMULATOR WEB APPLICATION"
echo "  Access URL: http://127.0.0.1:5000"
echo "===================================================================="

python3 main.py --web --port 5000 || python main.py --web --port 5000
