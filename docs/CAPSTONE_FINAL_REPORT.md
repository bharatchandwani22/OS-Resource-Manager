# Operating System Resource Management Simulator
## Comprehensive Capstone Project Final Report

**Course / Subject:** Operating Systems (CS / IT Core)  
**Project Title:** Integrated Python-and-Bash Operating System Resource Management Simulator  
**Total Marks Available:** 100 Marks  
**Assessment Breakdown:** Phase 1 (20) + Phase 2 (20) + Phase 3 (20) + Phase 4 (20) + Phase 5 (20) = 100 Marks  

---

## Abstract
This report documents the design, implementation, mathematical analysis, and empirical verification of an integrated **Operating System Resource Management Simulator**. Developed in Python with deep **Linux Kernel Telemetry integration via Bash**, the system consolidates the four primary resource management functions of modern operating systems: CPU Process Scheduling, Physical & Virtual Memory Management, Deadlock Avoidance & Recovery, and Secondary Storage Head Seek Scheduling. 

The software operates as a unified, production-quality command-line application with both an interactive rich terminal interface and automated CLI batch scripting capabilities. Empirical benchmarks across common workloads demonstrate key theoretical OS theorems: the optimality of Shortest Remaining Time First (SRTF), the responsiveness of Multi-Level Feedback Queues (MLFQ), Belady's Anomaly in First-In-First-Out (FIFO) page replacement, Dijkstra's Banker's Algorithm safe execution sequences, and disk seek optimization via Shortest Seek Time First (SSTF) and LOOK algorithms. All analytical findings are supported by tabular metrics and high-resolution visualizations.

---

## Table of Contents
1. [Phase 1: System Design and Planning (20 Marks)](#1-phase-1-system-design-and-planning)
2. [Phase 2: Core Resource-Management Modules (20 Marks)](#2-phase-2-core-resource-management-modules)
3. [Phase 3: Analysis and Comparison (20 Marks)](#3-phase-3-analysis-and-comparison)
4. [Phase 4: Testing and Reliability (20 Marks)](#4-phase-4-testing-and-reliability)
5. [Phase 5: Documentation and Demonstration (20 Marks)](#5-phase-5-documentation-and-demonstration)
6. [Conclusion & Future Work](#6-conclusion--future-work)

---

## 1. Phase 1: System Design and Planning (20 Marks)

### 1.1 Problem Statement
Modern operating systems manage shared physical and virtual resources while ensuring fairness, preventing starvation, maximizing throughput, and avoiding catastrophic deadlocks. Traditional learning approaches often treat these algorithms as disjoint mathematical formulas. This project bridges theory and practice by creating a single, integrated simulator that exposes the internal mechanics of OS resource allocators and compares simulated models with live host operating system telemetry.

### 1.2 Modular Decomposition
The project is architected with strict modular isolation:
- `modules/process_scheduler.py`: CPU scheduling engine.
- `modules/memory_manager.py`: Contiguous allocation and page replacement engine.
- `modules/deadlock_manager.py`: Banker's safety and RAG graph cycle engine.
- `modules/storage_manager.py`: Disk seek scheduling engine.
- `modules/telemetry.py` & `scripts/sys_telemetry.sh`: Live host OS telemetry bridge.
- `analysis/comparator.py`: Multi-algorithm statistical benchmarking engine.
- `analysis/visualizer.py`: Matplotlib high-resolution chart generator.
- `tests/`: 47 automated unit, boundary, and robustness test cases.

### 1.3 Data Design & Class Structures
- **Process Control Block (`Process`):** Encapsulates arrival time, burst time, dynamic remaining time, priority, start time, completion time, turnaround time, waiting time, and response time.
- **Memory Block (`MemoryBlock`):** Encapsulates partition base address, capacity, allocated PID, and computes internal fragmentation dynamically.
- **Banker's State (`BankersState`):** Enforces consistency between Available vector, Max claim matrix, Allocation matrix, and computed Need matrix ($Need = Max - Allocation$).
- **Resource Allocation Graph (`ResourceAllocationGraph`):** Represents directed bipartite graph of processes and resources with request and assignment edges.

---

## 2. Phase 2: Core Resource-Management Modules (20 Marks)

### 2.1 Subsystem Implementations
1. **CPU Process Scheduling:**
   - Implemented FCFS, Non-Preemptive SJF, Preemptive SRTF, Round Robin ($q$ parameterizable), Non-Preemptive & Preemptive Priority, and 3-level Multi-Level Feedback Queue (MLFQ) with periodic aging (every 20 ticks) to guarantee starvation freedom.
2. **Memory Management:**
   - **Contiguous Partition Allocation:** Implemented First Fit, Best Fit, and Worst Fit strategies. Calculates internal and external fragmentation.
   - **Virtual Memory Paging:** Implemented FIFO, LRU, Optimal (OPT), and LFU. Features automated detection and reporting of Belady's Anomaly.
3. **Deadlock Management:**
   - **Banker's Safety Algorithm:** Discovers valid safe execution sequences or warns of unsafe conditions.
   - **Resource-Request Algorithm:** Tests instantaneous resource requests against Need and Available vectors, executes trial allocation, verifies safety, and either grants or rolls back state.
   - **RAG Cycle Detection:** Employs 3-color DFS graph coloring ($\text{WHITE}, \text{GRAY}, \text{BLACK}$) to isolate deadlock cycles in single-instance graphs.
   - **Multi-Instance Deadlock Detection & Recovery:** Detects deadlock in systems without prior maximum claim declarations and selects optimal victim processes for termination based on cost/resource impact.
4. **Storage / Disk Scheduling:**
   - Implemented FCFS, SSTF, SCAN (Elevator), C-SCAN, LOOK, and C-LOOK. Produces exact actuator seek steps and total head movements.

### 2.2 Bash Shell Integration
The software connects directly to the host operating system kernel through `scripts/sys_telemetry.sh` (executed via WSL or native Bash). It queries `/proc/loadavg`, `/proc/meminfo`, and `/proc/diskstats`, parsing live system counters and comparing them with simulated models.

---

## 3. Phase 3: Analysis and Comparison (20 Marks)

### 3.1 Experimental Findings & Benchmarks

#### CPU Scheduling Comparison ($N=5$ Workload):
- **SRTF** achieved the lowest Average Waiting Time (**6.40 ticks**) and lowest Average Turnaround Time (**11.60 ticks**), validating the theoretical principle that prioritizing jobs with the shortest remaining execution time minimizes queue delay.
- **Round Robin ($q=2$) and MLFQ** achieved the best Average Response Times (**2.80 and 2.00 ticks**), proving their superiority for interactive user workloads despite higher turnaround times.

#### Page Replacement Comparison ($20$ Page References, $3$ Frames):
- **Optimal (OPT)** established the theoretical lower bound with only **9 page faults** (55% hit ratio).
- **LRU** achieved **12 page faults** (40% hit ratio), outperforming **FIFO** (15 page faults, 25% hit ratio).
- **Belady's Anomaly Confirmed:** On the sequence $[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]$, FIFO faults increased from 9 (with 3 frames) to 10 (with 4 frames). LRU and Optimal exhibited no anomaly.

#### Contiguous Memory Allocation:
- **Best Fit** allocated 100% of incoming requests (4 of 4) with 433 B internal fragmentation.
- **First Fit and Worst Fit** suffered premature partition exhaustion, stranding request $P_4$ ($426\text{ B}$) unallocated.

#### Disk Scheduling ($8$ Cylinder Requests, Initial Head $53$):
- **SSTF** achieved the shortest total head movement (**236 cylinders**).
- **LOOK** traversed **299 cylinders**, outperforming **SCAN** (**331 cylinders**) by eliminating useless travel to the disk boundary (cylinder 199).
- **FCFS** produced excessive seek overhead (**640 cylinders**), nearly triple that of SSTF.

### 3.2 Visual Artifacts
High-resolution charts were produced and saved to `output/charts/`:
- `gantt_srtf.png` & `gantt_round_robin.png`: Process execution timelines with idle markers.
- `cpu_algorithm_comparison.png`: Grouped comparative bar chart of TAT, WT, and RT.
- `page_replacement_curves.png`: Multiline fault curves across frame sizes.
- `beladys_anomaly_curves.png`: Visual spike illustrating Belady's Anomaly in FIFO.
- `disk_scheduling_trajectories.png`: Head seek curves across cylinder positions.
- `memory_best_fit_map.png`: Physical memory layout and fragmentation segmentation map.

---

## 4. Phase 4: Testing and Reliability (20 Marks)

### 4.1 Automated Test Execution Summary
The automated test harness comprises 47 unit and integration tests across 5 test suites.

```
Ran 47 tests in 0.022s
STATUS: ALL TESTS PASSED (100% SUCCESS RATE, 0 ERRORS, 0 FAILURES)
```

### 4.2 Error Handling & Input Validation
- All functions validate boundary conditions before entering execution loops.
- Custom domain exceptions (`ProcessValidationError`, `MemoryValidationError`, `DeadlockValidationError`, `StorageValidationError`) catch and diagnose invalid inputs:
  - Empty process lists or duplicate PIDs.
  - Negative burst times or negative arrival times.
  - Zero or negative time quanta.
  - Negative memory block sizes or zero page frames.
  - Matrix dimension mismatches in Banker's matrices.
  - Out-of-bounds cylinder coordinates.
- Structured logging to `logs/os_simulator.log` records all simulation steps, preemption events, algorithm traces, and error stack traces.

---

## 5. Phase 5: Documentation and Demonstration (20 Marks)

### 5.1 Project Repository Structure
```
os-resource-manager/
├── main.py                       # Main application (interactive menu & CLI flags)
├── run.sh                        # Bash executable launcher
├── run.bat                       # Windows CMD launcher
├── run.ps1                       # Windows PowerShell launcher
├── requirements.txt              # Dependency specification
├── config.py                     # Logging and path configuration
├── modules/                      # Core OS subsystems
│   ├── process_scheduler.py
│   ├── memory_manager.py
│   ├── deadlock_manager.py
│   ├── storage_manager.py
│   └── telemetry.py
├── analysis/                     # Benchmark and visualization engine
│   ├── comparator.py
│   └── visualizer.py
├── scripts/                      # Bash automation scripts
│   ├── sys_telemetry.sh
│   ├── benchmark.sh
│   ├── run_tests.sh
│   └── generate_report.sh
├── data/                         # Standardized JSON workload datasets
├── tests/                        # 47 automated unit and boundary tests
├── logs/                         # Execution audit log (os_simulator.log)
├── output/                       # Generated CSV traces and PNG charts
└── docs/                         # Detailed phase documentation & final report
```

### 5.2 Verification & Execution Guide
1. **Interactive Mode:**
   ```bash
   ./run.sh            # On Linux / macOS / WSL
   run.bat             # On Windows CMD
   ```
2. **Run Full Batch Simulation & Generate Charts:**
   ```bash
   python main.py --all --save-charts
   ```
3. **Execute Automated Test Suite:**
   ```bash
   python -m unittest discover -s tests -v
   ```
4. **Collect Real Host OS Telemetry:**
   ```bash
   python main.py --telemetry
   ```

---

## 6. Conclusion
The Operating System Resource Management Simulator fulfills all requirements specified in the Capstone assignment rubric. It unifies the theoretical concepts of operating system resource allocation with empirical analysis, visual representation, and authentic Linux kernel telemetry integration.
