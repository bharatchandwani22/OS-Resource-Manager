# Team Work Division & Contribution Matrix (3 Members)
## Integrated OS Resource Management Simulator & Web Dashboard
**Course / Capstone:** Operating Systems (CS / IT Core) — 100 Marks Capstone Project  
**Team Size:** 3 Members  

---

## 👥 Executive Role Breakdown

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               3-MEMBER WORK DIVISION OVERVIEW                          │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│  MEMBER 1: Lead Architect│  MEMBER 2: Full-Stack Web   │  MEMBER 3: QA, Analytics &    │
│  & Backend Core Engine   │  & Interactive UI Engineer  │  OS Telemetry Specialist      │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ • CPU Scheduling Module  │ • Web Architecture & Flask  │ • Deadlock & Storage Modules  │
│ • Memory Mgmt Subsystem  │ • Dashboard UI (Tailwind)   │ • Bash Telemetry Integration  │
│ • System Design (Phase 1)│ • Chart.js & Canvas Gantt   │ • 53-Test QA Suite (Phase 4)  │
│ • Core Logic (Phase 2A)  │ • REST API Layer (Phase 2B) │ • Analysis & Benchmarks (P3)  │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

---

## 📌 Detailed Responsibilities by Member

### 👨‍💻 Member 1: Lead Systems Architect & Core Resource Engine
*Focus: System architecture, process scheduling algorithms, physical/virtual memory management, and theoretical correctness.*

#### 1. Core Technical Ownership:
- **Phase 1: System Design and Planning (20 Marks)**
  - Architected overall system modular decomposition and component interfaces.
  - Defined fundamental data structures and dataclasses (`Process`, `MemoryBlock`, `ContiguousAllocationResult`, `PageReplacementResult`).
  - Authored the system architecture specification: [`docs/PHASE_1_SYSTEM_DESIGN.md`](PHASE_1_SYSTEM_DESIGN.md).
- **Subsystem 1: CPU Process Scheduling (`modules/process_scheduler.py`)**
  - Implemented all 6 CPU algorithms: FCFS, Non-Preemptive SJF, Preemptive SRTF, Round Robin ($q$), Priority (Preemptive & Non-Preemptive), and 3-Queue MLFQ with aging.
  - Formulated metrics formulas: Turnaround Time ($TAT$), Waiting Time ($WT$), Response Time ($RT$), CPU Utilization (%), and Throughput.
- **Subsystem 2: Memory Management Subsystem (`modules/memory_manager.py`)**
  - Implemented Contiguous Partition Allocation: First Fit, Best Fit, and Worst Fit with dynamic internal and external fragmentation calculation.
  - Implemented Virtual Memory Page Replacement: FIFO, LRU, Optimal (Belady's OPT), and LFU algorithms.
  - Built the automated **Belady's Anomaly Detection Engine** evaluating fault rate anomalies across frame sweeps.
- **Backend APIs:**
  - Designed backend API endpoints: `/api/cpu/simulate`, `/api/cpu/compare`, `/api/memory/contiguous`, `/api/memory/paging`, `/api/memory/belady`.

#### 2. Key Code Artifacts Owned:
- `modules/process_scheduler.py`
- `modules/memory_manager.py`
- `data/processes_sample.json`, `data/memory_sample.json`
- `docs/PHASE_1_SYSTEM_DESIGN.md`

#### 3. Viva / Presentation Talking Points:
- Explain the algorithmic difference between SJF and SRTF, and why SRTF mathematically minimizes waiting time.
- Explain the mechanism of starvation prevention in the MLFQ queue via periodic aging boosts.
- Demonstrate why Belady's Anomaly occurs in FIFO and why it is impossible in stack algorithms like LRU and Optimal.

---

### 👨‍💻 Member 2: Full-Stack Web Application & Visualizer Engineer
*Focus: Web architecture, RESTful API layer, responsive frontend dashboard, interactive Canvas Gantt charts, and Chart.js visualizations.*

#### 1. Core Technical Ownership:
- **Phase 2 & Phase 5: Web Application Implementation & Visual Demonstration (40 Marks)**
  - Architected and built the complete Flask web application (`web/app.py`) providing a unified GUI for all simulated subsystems.
  - Engineered the single-page responsive dashboard (`web/templates/index.html`) using Tailwind CSS, dark glassmorphism styling, and FontAwesome icons.
  - Built the modular client-side logic engine (`web/static/js/app.js`) handling dynamic DOM updates, AJAX payloads, and input tables.
- **Interactive UI Components:**
  - **Dynamic Canvas Gantt Chart Generator:** Custom client-side Gantt chart renderer displaying exact time intervals, process colors, hover tooltips, and tick markers.
  - **Physical Memory Segmentation Bar:** Visual interactive block map showing allocated processes, free space, and internal fragmentation in real time.
  - **Virtual Memory Step-by-Step Frame Matrix:** Dynamic tabular visualization showing page residency per tick with color-coded `HIT` and `FAULT` badges.
  - **Banker's Algorithm Matrix Grid:** Interactive editable input tables for Allocation, Max Claim, and Available vectors.
- **Visualization Subsystem (`analysis/visualizer.py`):**
  - Integrated Chart.js for real-time frontend charts (CPU grouped comparison bar charts, Belady fault curves, disk seek trajectory line plots).
  - Integrated Matplotlib publication figure exports (300 DPI PNGs saved in `output/charts/`).
- **Launchers & Packaging:**
  - Created `run_web.bat`, `run_web.sh`, `main.py --web` launcher scripts.

#### 2. Key Code Artifacts Owned:
- `web/app.py`
- `web/templates/index.html`
- `web/static/js/app.js`
- `web/static/css/style.css`
- `analysis/visualizer.py`
- `run_web.bat`, `run_web.sh`

#### 3. Viva / Presentation Talking Points:
- Explain the full-stack client-server interaction: how user input flows from the Tailwind table $\to$ REST API $\to$ Python engine $\to$ JSON response $\to$ Chart.js / Canvas render.
- Demonstrate the live interactive Gantt chart and how hover tooltips reflect exact start/end dispatch timestamps.
- Explain how the web app enables live dynamic parameter tuning (changing time quantum, adding custom processes, switching allocation strategies).

---

### 👨‍💻 Member 3: QA Lead, Systems Analytics & OS Telemetry Specialist
*Focus: Deadlock management, secondary storage scheduling, Linux kernel telemetry via Bash, automated testing harness, and statistical reporting.*

#### 1. Core Technical Ownership:
- **Subsystem 3: Deadlock Management Subsystem (`modules/deadlock_manager.py`)**
  - Implemented Dijkstra's Banker's Safety Algorithm and Resource-Request Algorithm with automatic trial allocation and state rollback.
  - Implemented 3-color DFS cycle detection ($\text{WHITE}, \text{GRAY}, \text{BLACK}$) on Resource Allocation Graphs (RAG) to locate circular waits.
  - Implemented Multi-Instance Deadlock Detection & Cost-Optimized Victim Selection for recovery.
- **Subsystem 4: Storage / Disk Scheduling Subsystem (`modules/storage_manager.py`)**
  - Implemented FCFS, SSTF, SCAN (Elevator), C-SCAN, LOOK, and C-LOOK disk seek algorithms.
  - Calculated Total Head Movement ($THM$), Average Seek Distance, and exact actuator step trajectories.
- **Linux Kernel Telemetry & Bash Integration (`scripts/sys_telemetry.sh`, `modules/telemetry.py`)**
  - Authored the native Bash shell script `scripts/sys_telemetry.sh` querying live Linux `/proc/loadavg`, `/proc/meminfo`, and `/proc/diskstats`.
  - Built the cross-platform IPC bridge in `modules/telemetry.py` running via WSL/Bash with seamless `psutil` fallback.
  - Formulated the "Simulated OS vs Live Host OS" comparative architecture matrix.
- **Phase 3 & Phase 4: Statistical Analysis & Quality Assurance (40 Marks)**
  - Authored `analysis/comparator.py` conducting batch benchmarks and generating CSV traces in `output/traces/`.
  - Built the comprehensive **53-test automated QA test harness** (`tests/`) covering valid, invalid, and boundary test cases with 100% pass rate.
  - Configured custom domain exception hierarchies and structured activity logging (`logs/os_simulator.log`).
  - Authored [`docs/CAPSTONE_FINAL_REPORT.md`](CAPSTONE_FINAL_REPORT.md) and [`docs/PHASE_4_TESTING.md`](PHASE_4_TESTING.md).

#### 2. Key Code Artifacts Owned:
- `modules/deadlock_manager.py`
- `modules/storage_manager.py`
- `modules/telemetry.py`
- `scripts/sys_telemetry.sh`, `scripts/benchmark.sh`, `scripts/run_tests.sh`
- `analysis/comparator.py`
- `tests/` (All 6 test suites, 53 tests)
- `data/deadlock_sample.json`, `data/storage_sample.json`, `data/edge_cases.json`
- `docs/PHASE_3_ANALYSIS.md`, `docs/PHASE_4_TESTING.md`, `docs/CAPSTONE_FINAL_REPORT.md`

#### 3. Viva / Presentation Talking Points:
- Explain the safety criteria of Dijkstra's Banker's algorithm ($\text{Need} \le \text{Work}$) and how unsafe states are distinguished from deadlocked states.
- Explain the mechanical differences between SCAN, C-SCAN, LOOK, and C-LOOK and why LOOK eliminates wasted boundary traversals.
- Demonstrate the 53-test automated test suite and explain boundary handling (zero bursts, negative inputs, cycle detection).
- Demonstrate the live Linux `/proc` telemetry captured by the Bash script.

---

## 📊 Capstone Evaluation & Rubric Contribution Matrix

| Capstone Phase | Marks | Primary Owner | Secondary Contributor | Verifiable Deliverables |
| :--- | :---: | :--- | :--- | :--- |
| **Phase 1: System Design & Planning** | **20** | **Member 1** | Member 3 | Data models, class diagrams, flow architecture, `PHASE_1_SYSTEM_DESIGN.md` |
| **Phase 2: Core Modules & Bash Integration** | **20** | **Member 1 & 3** | Member 2 | 4 core OS subsystems, Bash `/proc` script, menu flow, `PHASE_2_IMPLEMENTATION.md` |
| **Phase 3: Analysis & Comparison** | **20** | **Member 3** | Member 2 | Benchmark comparator, CSV traces, comparative tables, `PHASE_3_ANALYSIS.md` |
| **Phase 4: Testing & Reliability** | **20** | **Member 3** | Member 1 | 53 unit/boundary tests, custom exceptions, audit logging, `PHASE_4_TESTING.md` |
| **Phase 5: Documentation & Web Demo** | **20** | **Member 2** | Member 1 & 3 | Full web app, Canvas Gantt, Chart.js, README, final report, `run_web.bat` |
| **Total Marks** | **100** | **Equally Distributed (~33.3% per member)** | | Comprehensive Full-Stack Capstone Project |

---

## 🎯 Suggested Presentation / Demo Order for Defense / Viva

1. **Introduction & System Architecture (Member 1 - 3 mins):**
   - Introduce project goals, modular architecture, and the core scheduling and memory management engines.
   - Run the CPU Scheduling and Memory Management interactive web demo.
2. **Web Application & Visualizer Dashboard (Member 2 - 3 mins):**
   - Present the full-stack web dashboard architecture (Flask + REST APIs + Tailwind + Chart.js).
   - Demonstrate dynamic process insertion, real-time Canvas Gantt chart generation, and the Belady's Anomaly interactive curve.
3. **Deadlock Engine, Storage, Telemetry & QA (Member 3 - 4 mins):**
   - Demonstrate the Banker's safety check and RAG cycle detection.
   - Demonstrate disk scheduling seek trajectories and live host Linux telemetry queried via Bash.
   - Run the 53-test automated verification suite (`python -m unittest discover -s tests -v`) demonstrating 100% test reliability.
