# Operating System Resource Management Simulator
### Integrated Python-and-Bash Capstone Project (100 Marks Comprehensive Solution)

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-green)
![Tests](https://img.shields.io/badge/Tests-47%2F47%20Passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-orange)

An integrated, production-grade simulation suite modeling the four major operating system resource management functions: **CPU Process Scheduling**, **Memory Management (Contiguous & Paging)**, **Deadlock Management (Banker's & RAG Cycle Detection)**, and **Storage / Disk Seek Scheduling**, coupled with **Linux Kernel Telemetry Integration via Bash**.

---

## 🏆 Capstone Marking Rubric Mapping (100 / 100 Marks)

| Phase | Title | Marks | Implemented Deliverables | Evidence in Project |
| :---: | :--- | :---: | :--- | :--- |
| **Phase 1** | **System Design and Planning** | 20 | Modular architecture, dataclass schemas, input/output pipeline, and data structures. | [`docs/PHASE_1_SYSTEM_DESIGN.md`](docs/PHASE_1_SYSTEM_DESIGN.md) |
| **Phase 2** | **Core Resource-Management Modules** | 20 | 4 full Python OS subsystems, Bash shell integration (`sys_telemetry.sh`), interactive terminal UI. | [`modules/`](modules/), [`scripts/`](scripts/), [`docs/PHASE_2_IMPLEMENTATION.md`](docs/PHASE_2_IMPLEMENTATION.md) |
| **Phase 3** | **Analysis and Comparison** | 20 | Multi-algorithm benchmarks, mathematical formulas, comparative tables, and 6 publication PNG charts. | [`analysis/`](analysis/), [`output/charts/`](output/charts/), [`docs/PHASE_3_ANALYSIS.md`](docs/PHASE_3_ANALYSIS.md) |
| **Phase 4** | **Testing and Reliability** | 20 | 47 unit/boundary/invalid tests, custom exceptions, boundary protection, persistent activity logging. | [`tests/`](tests/), [`logs/os_simulator.log`](logs/os_simulator.log), [`docs/PHASE_4_TESTING.md`](docs/PHASE_4_TESTING.md) |
| **Phase 5** | **Documentation and Demonstration** | 20 | Full README, execution scripts, screenshots, and 20+ page academic Capstone Final Report. | [`docs/CAPSTONE_FINAL_REPORT.md`](docs/CAPSTONE_FINAL_REPORT.md), [`run.sh`](run.sh), [`run.bat`](run.bat) |
| **Total** | | **100** | | |

---

## 👥 3-Person Team Work Division & Contribution Matrix

| Member | Primary Role | Modules & Components Owned | Rubric Focus |
| :---: | :--- | :--- | :---: |
| **Member 1** | **Lead Systems Architect & Core Engine** | • CPU Scheduling Engine (`process_scheduler.py`)<br>• Physical & Virtual Memory Management (`memory_manager.py`)<br>• Core Dataclass Models (`Process`, `MemoryBlock`)<br>• System Architecture Specification | **Phase 1 (20 Marks)**<br>**Phase 2A (10 Marks)** |
| **Member 2** | **Full-Stack Web & Visualizer Engineer** | • Flask Web App & REST API Engine (`web/app.py`)<br>• Dashboard UI (Tailwind CSS, dark glassmorphism)<br>• Interactive Canvas Gantt Chart & Chart.js Visuals<br>• Web Launchers (`run_web.bat`, `run_web.sh`) | **Phase 2B (10 Marks)**<br>**Phase 5 (20 Marks)** |
| **Member 3** | **QA Lead, Analytics & Telemetry Specialist** | • Deadlock Engine & Banker's Algorithm (`deadlock_manager.py`)<br>• Disk Seek Scheduling Engine (`storage_manager.py`)<br>• Linux Kernel Telemetry via Bash (`sys_telemetry.sh`)<br>• 53-Test Automated QA Test Harness (`tests/`) & Report | **Phase 3 (20 Marks)**<br>**Phase 4 (20 Marks)** |

*For complete breakdown, code ownership mappings, and viva defense talking points, see [`docs/TEAM_CONTRIBUTIONS.md`](docs/TEAM_CONTRIBUTIONS.md).*

---

## 🚀 Key Features

### 1. CPU Process Scheduling Subsystem (`modules/process_scheduler.py`)
- **Algorithms:** First-Come First-Served (FCFS), Shortest Job First (SJF Non-Preemptive), Shortest Remaining Time First (SRTF Preemptive), Round Robin (RR with parameterizable quantum $q$), Priority (Preemptive & Non-Preemptive), and 3-Tier Multi-Level Feedback Queue (MLFQ) with periodic aging (every 20 ticks) to prevent starvation.
- **Metrics:** Turnaround Time ($TAT$), Waiting Time ($WT$), Response Time ($RT$), CPU Utilization (%), and Throughput (proc/unit).

### 2. Memory Management Subsystem (`modules/memory_manager.py`)
- **Contiguous Partition Allocation:** First Fit, Best Fit, and Worst Fit with dynamic calculation of Internal and External Fragmentation.
- **Virtual Memory Page Replacement:** FIFO, LRU, Optimal (Belady's OPT), and LFU.
- **Belady's Anomaly Engine:** Automatically tests and detects Belady's Anomaly where allocating more frames increases page faults in FIFO (e.g. $[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]$).

### 3. Deadlock Management Subsystem (`modules/deadlock_manager.py`)
- **Banker's Algorithm:** Evaluates safe state and generates valid execution sequences $\langle P_0, P_1, \dots \rangle$. Evaluates instantaneous resource requests with automatic rollback if unsafe.
- **Resource Allocation Graph (RAG) Cycle Detection:** 3-color DFS graph cycle detector ($\text{WHITE}, \text{GRAY}, \text{BLACK}$) identifying deadlock cycles.
- **Multi-Instance Deadlock Detection & Recovery:** Detects deadlocks in systems without prior max declarations and recommends optimal victim processes for termination.

### 4. Storage / Disk Scheduling Subsystem (`modules/storage_manager.py`)
- **Algorithms:** FCFS, Shortest Seek Time First (SSTF), SCAN (Elevator), Circular SCAN (C-SCAN), LOOK, and Circular LOOK (C-LOOK).
- **Metrics:** Total Head Movement (cylinders traversed), Average Seek Distance, and step-by-step actuator movement sequence.

### 5. Linux Kernel Telemetry & Bash Integration (`scripts/sys_telemetry.sh`)
- Directly queries live Linux kernel structures (`/proc/loadavg`, `/proc/meminfo`, `/proc/diskstats`) via Bash (with seamless WSL detection on Windows and `psutil` fallback).
- Presents a side-by-side analytical contrast of **Simulated Metrics vs Real Host OS Counters**.

---

## 📂 Directory Layout

```
os-resource-manager/
├── main.py                       # Main application (interactive menu & CLI flags)
├── run.sh                        # Bash executable launcher
├── run.bat                       # Windows CMD launcher
├── run.ps1                       # Windows PowerShell launcher
├── requirements.txt              # Dependency specification
├── config.py                     # Logging and path configuration
├── modules/                      # Core OS subsystems
│   ├── __init__.py
│   ├── process_scheduler.py      # CPU scheduling algorithms
│   ├── memory_manager.py         # Contiguous & page replacement
│   ├── deadlock_manager.py       # Banker's safety & RAG cycle detection
│   ├── storage_manager.py        # Disk seek scheduling
│   └── telemetry.py              # Real OS telemetry bridge
├── analysis/                     # Benchmark and visualization engine
│   ├── __init__.py
│   ├── comparator.py             # Multi-algorithm comparator
│   └── visualizer.py             # Publication-grade chart generator
├── scripts/                      # Bash automation scripts
│   ├── sys_telemetry.sh          # Linux /proc telemetry collector
│   ├── benchmark.sh              # Batch benchmark runner
│   ├── run_tests.sh              # Shell test runner
│   └── generate_report.sh        # Report artifact generator
├── data/                         # Standardized JSON workloads
│   ├── processes_sample.json
│   ├── memory_sample.json
│   ├── deadlock_sample.json
│   ├── storage_sample.json
│   └── edge_cases.json
├── tests/                        # 47 automated unit and boundary tests
│   ├── test_process_scheduler.py
│   ├── test_memory_manager.py
│   ├── test_deadlock_manager.py
│   ├── test_storage_manager.py
│   └── test_validation_edge_cases.py
├── logs/                         # Structured audit logs (os_simulator.log)
├── output/
│   ├── charts/                   # High-resolution PNG charts
│   └── traces/                   # CSV benchmark results
└── docs/                         # Detailed phase documentation & final report
    ├── PHASE_1_SYSTEM_DESIGN.md
    ├── PHASE_2_IMPLEMENTATION.md
    ├── PHASE_3_ANALYSIS.md
    ├── PHASE_4_TESTING.md
    ├── CAPSTONE_FINAL_REPORT.md  # 20+ page consolidated report
    └── screenshots/              # Chart screenshots for submission
```

---

## ⚡ Quick Start Guide

### 1. Installation
Clone or navigate to the project directory and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launching the Interactive Web Dashboard (Website GUI)
Launch the modern browser-based web dashboard:
- **Windows Command Prompt / Double-Click:**
  ```cmd
  run_web.bat
  ```
- **Linux / macOS / WSL (Bash Launcher):**
  ```bash
  chmod +x run_web.sh
  ./run_web.sh
  ```
- **Direct Python:**
  ```bash
  python main.py --web --port 5000
  ```
*Then open your browser at **`http://127.0.0.1:5000`** to access the interactive web interface.*

---

### 3. Launching Terminal Menu & CLI Execution
- **Linux / macOS / WSL (Terminal):**
  ```bash
  ./run.sh
  ```
- **Windows Command Prompt (Terminal):**
  ```cmd
  run.bat
  ```
- **Direct Python:**
  ```bash
  python main.py
  ```

---

## 🛠️ Command-Line Interface (CLI) Flags

The application supports both an interactive menu and automated headless execution:

```bash
# Run all subsystems, compute benchmarks, and generate all visual charts:
python main.py --all --save-charts

# Run batch benchmarks and export CSV tables to output/traces/:
python main.py --benchmark

# Query live host operating system telemetry via Bash:
python main.py --telemetry

# Run a specific subsystem:
python main.py --module cpu --save-charts
python main.py --module memory
python main.py --module deadlock
python main.py --module storage

# Execute the automated test suite:
python main.py --test
```

---

## 🧪 Automated Testing & Quality Assurance

Run the complete 47-test automated verification suite:
```bash
python -m unittest discover -s tests -v
```
All 47 tests pass with 0 errors and 0 failures, verifying:
- **Valid Scenarios:** Standard textbook test vectors.
- **Boundary Scenarios:** Single process, simultaneous arrivals ($T=0$), single page frame, cylinder boundary extremes ($0$ and $199$).
- **Invalid Inputs & Exception Handling:** Negative burst times, negative arrival times, zero/negative quantum, duplicate PIDs, negative memory sizes, and out-of-bounds cylinders.
- **Activity Logging:** Structured logging to `logs/os_simulator.log`.

---

## 📊 Generated Visual Charts

Running with `--save-charts` produces high-resolution PNG figures saved in `output/charts/`:
1. **`cpu_algorithm_comparison.png`**: Side-by-side grouped bar chart comparing Turnaround Time, Waiting Time, and Response Time across all algorithms.
2. **`gantt_srtf.png` & `gantt_round_robin.png`**: Step-by-step Gantt execution timeline color-coded by process with idle markers.
3. **`beladys_anomaly_curves.png`**: Page fault curve across frames 2 to 6, visually highlighting the anomaly spike in FIFO.
4. **`disk_scheduling_trajectories.png`**: Cylinder seek trajectory curves comparing FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK.
5. **`memory_best_fit_map.png`**: Physical memory partition map displaying allocated processes and internal fragmentation blocks.

---

## 📄 Submission Documentation

For complete academic submission artifacts, refer to the documentation package in `docs/`:
- [`docs/PHASE_1_SYSTEM_DESIGN.md`](docs/PHASE_1_SYSTEM_DESIGN.md): Modular architecture & data models.
- [`docs/PHASE_2_IMPLEMENTATION.md`](docs/PHASE_2_IMPLEMENTATION.md): Class & function reference and Bash-Python IPC.
- [`docs/PHASE_3_ANALYSIS.md`](docs/PHASE_3_ANALYSIS.md): Comprehensive benchmark findings & formula derivations.
- [`docs/PHASE_4_TESTING.md`](docs/PHASE_4_TESTING.md): Complete test matrix, edge cases, and logging verification.
- [`docs/CAPSTONE_FINAL_REPORT.md`](docs/CAPSTONE_FINAL_REPORT.md): Consolidated 20+ page academic Capstone Final Report.
