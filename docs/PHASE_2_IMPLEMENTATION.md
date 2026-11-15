# Phase 2: Core Resource-Management Modules

**Module Title:** Implementation and Architecture  
**Marks Weightage:** 20 Marks  
**Submission Target:** Correct implementation, reusable functions/classes, readable code, and working menu flow with Bash integration.

---

## 1. Subsystem Implementation Overview

The simulator implements all four fundamental OS resource subsystems in pure Python (utilizing OOP, dataclasses, and typing), integrated with a native Bash shell layer.

### 1.1 Process Scheduling Subsystem (`modules/process_scheduler.py`)
Provides deterministic simulation of CPU scheduling with millisecond-exact timelines and preemptions:
- **FCFS (`schedule_fcfs`):** Dispatches processes in order of arrival times without preemption. Calculates idle ticks when the CPU has no ready tasks.
- **SJF Non-Preemptive (`schedule_sjf_non_preemptive`):** Evaluates ready queue upon process completion and selects the job with the minimum CPU burst time.
- **SRTF / SJF Preemptive (`schedule_srtf`):** Evaluates remaining burst time on every tick. Preempts currently active process if a newly arrived process presents a strictly lower remaining burst.
- **Round Robin (`schedule_round_robin`):** Enforces time slicing with parameterizable quantum $q$. Handles new arrivals during slice execution and places preempted tasks at the tail of the ready queue.
- **Priority Scheduling (`schedule_priority`):** Supports both preemptive and non-preemptive modes using lower-number-higher-priority semantics (standard UNIX/POSIX convention).
- **Multi-Level Feedback Queue (`schedule_mlfq`):** 
  - Queue 0: High priority with Round Robin ($q_0 = 2$).
  - Queue 1: Medium priority with Round Robin ($q_1 = 4$).
  - Queue 2: Low priority with FCFS.
  - **Starvation Avoidance:** Features periodic priority boost (aging every 20 ticks) promoting all starving lower-queue tasks back to Queue 0.

### 1.2 Memory Management Subsystem (`modules/memory_manager.py`)
Addresses both physical contiguous partition allocation and virtual memory page replacement:
- **Contiguous Allocation:**
  - `first_fit`: Allocates the first free memory block large enough to fit the request.
  - `best_fit`: Searches all eligible free blocks and allocates the smallest block that fits, minimizing internal fragmentation.
  - `worst_fit`: Allocates the largest available free block to prevent small unusable fragments.
  - Computes both **Internal Fragmentation** (unused bytes within allocated block) and **External Fragmentation** (total free bytes that cannot satisfy an incoming process due to discontiguity).
- **Virtual Memory Page Replacement:**
  - `page_replace_fifo`: Evicts the page resident in memory the longest.
  - `page_replace_lru`: Tracks access timestamps and evicts the page unreferenced for the greatest duration.
  - `page_replace_optimal`: Forward-scans future page references and evicts the page that will not be accessed for the longest period (theoretical optimum).
  - `page_replace_lfu`: Maintains reference frequency counters, evicting the least frequently accessed page (breaking ties by oldest arrival).
  - `analyze_beladys_anomaly`: Evaluates page fault numbers across varying frame sizes ($2 \le f \le 6$) to demonstrate FIFO anomaly.

### 1.3 Deadlock Management Subsystem (`modules/deadlock_manager.py`)
- **Banker's Safety Algorithm (`check_bankers_safety`):** Computes $\text{Need} = \text{Max} - \text{Allocation}$. Maintains $\text{Work} = \text{Available}$ and tests for an unfinished process where $\text{Need}_i \le \text{Work}$. Returns boolean safety flag and full safe sequence $\langle P_{\pi(1)}, P_{\pi(2)}, \dots \rangle$.
- **Resource-Request Algorithm (`request_resources`):** Tests if $\text{Request} \le \text{Need}$ and $\text{Request} \le \text{Available}$. Temporarily allocates resources and evaluates safety; grants or rolls back state with clear diagnostics.
- **RAG Cycle Detection (`ResourceAllocationGraph`):** Implements a 3-color DFS graph algorithm ($\text{WHITE} = 0, \text{GRAY} = 1, \text{BLACK} = 2$) on directed graphs comprising Process and Resource nodes, identifying elementary deadlock cycles.
- **Multi-Instance Deadlock Detection & Victim Selection (`detect_deadlock_multi_instance`):** Identifies blocked processes and recommends an optimal victim for termination to break the deadlock at minimal cost.

### 1.4 Storage / Disk Scheduling Subsystem (`modules/storage_manager.py`)
Simulates the mechanical motion of the hard disk actuator head across cylinder tracks:
- **FCFS (`disk_fcfs`):** Services requests in arrival order.
- **SSTF (`disk_sstf`):** Selects the request closest to the current head position.
- **SCAN (`disk_scan`):** Moves head towards boundary (e.g., cylinder 199), servicing requests, then reverses direction.
- **C-SCAN (`disk_c_scan`):** Sweeps to high end (cylinder 199), wraps around to cylinder 0 without servicing on return, and sweeps upward.
- **LOOK (`disk_look`):** Reverses direction at the highest pending request rather than traveling to physical disk limits.
- **C-LOOK (`disk_c_look`):** Jumps from highest request directly to lowest request without touching cylinder 0 or 199.

---

## 2. Bash Scripting Integration & Architecture

The project seamlessly integrates Bash scripting into the Python runtime:

1. **`scripts/sys_telemetry.sh` (Kernel Telemetry Collector):**
   - Direct execution in Linux / WSL environments.
   - Extracts live OS data:
     - Load averages from `/proc/loadavg`
     - Memory allocation and swap states from `/proc/meminfo`
     - Physical drive block I/O reads/writes from `/proc/diskstats`
   - Formats and emits a clean JSON payload to standard output.
2. **`modules/telemetry.py` (IPC Bridge):**
   - Executes `sys_telemetry.sh` as a child process via `subprocess.run(["wsl", "-e", "bash", "-c", ...])` or native `bash`.
   - Parses the JSON stream and pairs live host operating system counters with simulation parameters.
   - In environments where Bash is unavailable, provides an automatic zero-crash fallback to `psutil`.
3. **`scripts/benchmark.sh`:**
   - Automated batch runner executing multi-module benchmarks through Python CLI flags.
4. **`scripts/run_tests.sh`:**
   - Automated shell script executing the test suite and writing execution logs.
5. **`run.sh` / `run.bat`:**
   - Cross-platform root launchers providing one-click environment setup and interactive menu dispatch.

---

## 3. Interactive Menu Navigation Flow

When launched via `python main.py` or `./run.sh`, the system presents a unified menu interface:

```
======================================================================
    OPERATING SYSTEM RESOURCE MANAGEMENT SIMULATOR (CAPSTONE)
======================================================================
  [1] Process Scheduling Simulation (FCFS, SJF, SRTF, RR, Priority, MLFQ)
  [2] Memory Management Simulation (Contiguous Allocation, Paging, Belady)
  [3] Deadlock Management Simulation (Banker's Safety, RAG Cycle, Recovery)
  [4] Storage / Disk Scheduling Simulation (FCFS, SSTF, SCAN, LOOK, etc.)
  [5] Live OS Telemetry & Real OS Resource Comparison (Bash / psutil)
  [6] Run Comprehensive Benchmark & Generate All Analytical Charts
  [7] Run Automated Unit & Boundary Test Suite (Phase 4)
  [8] Exit
======================================================================
```
All selections produce formatted ASCII trace tables and can output high-resolution PNG charts directly to `output/charts/`.
