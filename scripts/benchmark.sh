#!/usr/bin/env bash
# ==============================================================================
# OS Simulator - Batch Benchmark & Analytics Runner (Phase 3 Execution)
# Runs automated multi-algorithm comparison across all OS subsystems.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================================="
echo "    OS RESOURCE MANAGEMENT SUITE - BATCH BENCHMARK       "
echo "=========================================================="
echo "Project Root: $PROJECT_ROOT"
echo "Execution Time: $(date)"
echo ""

cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run Python benchmark command
python main.py --benchmark --save-charts

echo ""
echo ">> [SUCCESS] Batch benchmark complete!"
echo ">> CSV Traces saved in: $PROJECT_ROOT/output/traces"
echo ">> Generated Charts saved in: $PROJECT_ROOT/output/charts"
