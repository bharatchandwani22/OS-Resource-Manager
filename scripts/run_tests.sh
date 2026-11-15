#!/usr/bin/env bash
# ==============================================================================
# OS Simulator - Automated Test Suite Runner (Phase 4 Verification)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/test_execution.log"

echo "=========================================================="
echo "    OPERATING SYSTEM SIMULATOR - AUTOMATED TEST SUITE    "
echo "=========================================================="
echo "Project Root: $PROJECT_ROOT"
echo "Starting test run at: $(date)"
echo ""

cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run tests with python unittest
if python -m unittest discover -s "$PROJECT_ROOT/tests" -v 2>&1 | tee "$LOG_FILE"; then
    echo ""
    echo ">> [SUCCESS] All test suites passed successfully!"
    echo ">> Execution log saved to: $LOG_FILE"
    exit 0
else
    echo ""
    echo ">> [FAILURE] Test failures detected! Inspect: $LOG_FILE"
    exit 1
fi
