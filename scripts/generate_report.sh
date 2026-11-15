#!/usr/bin/env bash
# ==============================================================================
# OS Simulator - Report & Execution Evidence Generator (Phase 5)
# Generates full comparative benchmarks, charts, and audit traces.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================================="
echo "    GENERATING CAPSTONE REPORT & EXECUTION ARTIFACTS      "
echo "=========================================================="

cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run full simulation pipeline
python main.py --all --save-charts

echo ""
echo ">> [SUCCESS] All traces, charts, and report matrices generated!"
echo ">> Review documentation in: $PROJECT_ROOT/docs/"
