#!/usr/bin/env bash
# ==============================================================================
# OS Simulator - Kernel & System Telemetry Collector (Bash Integration)
# Collects live operating system resource management metrics from /proc and coreutils.
# ==============================================================================

# System Info
OS_NAME=$(uname -s 2>/dev/null | tr -d '\r\n')
KERNEL_VER=$(uname -r 2>/dev/null | tr -d '\r\n')

# CPU Scheduling Telemetry
LOAD_1="0.0"
LOAD_5="0.0"
RUNNABLE_PROCS="1"
TOTAL_PROCS="50"

if [ -f /proc/loadavg ]; then
    LOAD_1=$(awk '{print $1}' /proc/loadavg | tr -d '\r\n')
    LOAD_5=$(awk '{print $2}' /proc/loadavg | tr -d '\r\n')
    RUNNABLE_PROCS=$(awk -F'/' '{print $1}' /proc/loadavg | awk '{print $NF}' | tr -d '\r\n')
    TOTAL_PROCS=$(awk -F'/' '{print $2}' /proc/loadavg | awk '{print $1}' | tr -d '\r\n')
fi

# Memory Paging Telemetry
MEM_TOTAL="16777216"
MEM_FREE="8388608"
MEM_AVAIL="8388608"
SWAP_TOTAL="4194304"
SWAP_FREE="4194304"
ACTIVE_PAGES="4194304"
INACTIVE_PAGES="2097152"

if [ -f /proc/meminfo ]; then
    MEM_TOTAL=$(awk '/MemTotal/ {print $2}' /proc/meminfo | tr -d '\r\n')
    MEM_FREE=$(awk '/MemFree/ {print $2}' /proc/meminfo | tr -d '\r\n')
    MEM_AVAIL=$(awk '/MemAvailable/ {print $2}' /proc/meminfo | tr -d '\r\n')
    SWAP_TOTAL=$(awk '/SwapTotal/ {print $2}' /proc/meminfo | tr -d '\r\n')
    SWAP_FREE=$(awk '/SwapFree/ {print $2}' /proc/meminfo | tr -d '\r\n')
    ACTIVE_PAGES=$(awk '/Active:/ {print $2}' /proc/meminfo | tr -d '\r\n')
    INACTIVE_PAGES=$(awk '/Inactive:/ {print $2}' /proc/meminfo | tr -d '\r\n')
fi

# Storage / Disk I/O Telemetry
READS="1024"
WRITES="512"
IO_IN_PROGRESS="0"

if [ -f /proc/diskstats ]; then
    DEV_LINE=$(grep -E ' (sda|sdb|nvme0n1|vda) ' /proc/diskstats | head -n 1)
    if [ -n "$DEV_LINE" ]; then
        READS=$(echo "$DEV_LINE" | awk '{print $4}' | tr -d '\r\n')
        WRITES=$(echo "$DEV_LINE" | awk '{print $8}' | tr -d '\r\n')
        IO_IN_PROGRESS=$(echo "$DEV_LINE" | awk '{print $12}' | tr -d '\r\n')
    fi
fi

cat <<EOF
{
  "system": {
    "os": "${OS_NAME:-Linux}",
    "kernel": "${KERNEL_VER:-WSL2}"
  },
  "cpu": {
    "load_avg_1m": ${LOAD_1:-0.0},
    "load_avg_5m": ${LOAD_5:-0.0},
    "runnable_threads": ${RUNNABLE_PROCS:-1},
    "total_threads": ${TOTAL_PROCS:-50}
  },
  "memory": {
    "total_kb": ${MEM_TOTAL:-0},
    "free_kb": ${MEM_FREE:-0},
    "available_kb": ${MEM_AVAIL:-0},
    "active_pages_kb": ${ACTIVE_PAGES:-0},
    "inactive_pages_kb": ${INACTIVE_PAGES:-0},
    "swap_total_kb": ${SWAP_TOTAL:-0},
    "swap_free_kb": ${SWAP_FREE:-0}
  },
  "storage": {
    "reads_completed": ${READS:-0},
    "writes_completed": ${WRITES:-0},
    "io_in_progress": ${IO_IN_PROGRESS:-0}
  }
}
EOF
exit 0
