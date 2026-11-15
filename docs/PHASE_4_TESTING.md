# Phase 4: Testing and Reliability

**Module Title:** Verification, Validation, and Activity Logging  
**Marks Weightage:** 20 Marks  
**Submission Target:** Test quality, robust validation, error handling, correctness, and reliability.

---

## 1. Quality Assurance Strategy & Test Matrix

The test harness uses Python's standard `unittest` framework (compatible with `pytest`) and is structured into 5 dedicated test modules with 47 automated tests covering valid, invalid, and boundary scenarios:

| Category | Description | Count | Pass Rate |
| :--- | :--- | :---: | :---: |
| **Valid Tests** | Standard textbook test scenarios with known theoretical solutions | 18 | 100% |
| **Boundary Tests** | Empty queues, single process/frame, zero initial head, boundary cylinders | 14 | 100% |
| **Invalid Tests** | Negative bursts/arrivals, out-of-range memory, invalid matrices, duplicate PIDs | 15 | 100% |
| **Total Tests** | Comprehensive automated test coverage | **47** | **100% (47/47)** |

---

## 2. Detailed Test Matrix by Subsystem

### 2.1 Process Scheduling Subsystem (`tests/test_process_scheduler.py`)
- `test_fcfs_execution`: Verifies mathematical correctness of FCFS turnaround and waiting times against manual hand calculations.
- `test_sjf_non_preemptive`: Verifies shortest burst prioritization when multiple jobs become ready.
- `test_srtf_preemptive`: Verifies immediate preemption when shorter remaining time arrives.
- `test_round_robin`: Verifies queue rotation under time slice $q=2$.
- `test_mlfq_execution`: Verifies 3-tier queue demotion and aging mechanism.
- `test_single_process`: Boundary test verifying $N=1$ process starts and finishes properly without waiting time.
- `test_simultaneous_arrival`: Boundary test where multiple processes arrive at $T=0$.
- `test_empty_process_list`: Invalid test verifying `ProcessValidationError` is raised when process list is empty.
- `test_negative_burst_time`: Invalid test verifying `ProcessValidationError` on burst $\le 0$.
- `test_negative_arrival_time`: Invalid test verifying `ProcessValidationError` on arrival $< 0$.
- `test_duplicate_pid`: Invalid test verifying PID uniqueness enforcement.
- `test_invalid_rr_quantum`: Invalid test verifying quantum $\le 0$ rejection.

### 2.2 Memory Management Subsystem (`tests/test_memory_manager.py`)
- `test_first_fit`: Verifies first-fit partition placement and fragmentation.
- `test_best_fit`: Verifies optimal partition fitting with minimal fragmentation.
- `test_worst_fit`: Verifies placement into largest available partition.
- `test_fifo_page_faults`: Verifies exact count of 15 page faults on Silberschatz reference string with 3 frames.
- `test_lru_page_faults`: Verifies 12 page faults on same string.
- `test_optimal_page_faults`: Verifies 9 page faults (optimal theoretical lower bound).
- `test_beladys_anomaly_detection`: Verifies automated detection of Belady's Anomaly where FIFO faults increase from 9 (3 frames) to 10 (4 frames).
- `test_single_frame`: Boundary test where memory capacity is exactly 1 frame.
- `test_zero_frames_raises_error`: Invalid test verifying `MemoryValidationError` on frames $\le 0$.
- `test_empty_reference_string_raises_error`: Invalid test on empty page access string.
- `test_negative_block_size`: Invalid test on memory block size $\le 0$.
- `test_invalid_allocation_strategy`: Invalid test when strategy is not first_fit, best_fit, or worst_fit.

### 2.3 Deadlock Management Subsystem (`tests/test_deadlock_manager.py`)
- `test_bankers_safety_standard`: Verifies Banker's Safety algorithm returns true and finds valid permutation sequence $\langle P_1, P_3, P_0, P_2, P_4 \rangle$.
- `test_bankers_safe_request`: Verifies instantaneous request within Need and Available is safely granted.
- `test_bankers_unsafe_request`: Verifies request exceeding Need or Available is rejected without state corruption.
- `test_rag_cycle_detection`: Verifies 3-color DFS cycle detector finds cycle $P_1 \to R_1 \to P_2 \to R_2 \to P_1$.
- `test_rag_acyclic_graph`: Verifies acyclic system correctly reports deadlock-free status.
- `test_multi_instance_detection_and_victim_selection`: Verifies deadlock detection in multi-instance systems and recommends victim with lowest termination cost.
- `test_mismatched_dimensions`: Invalid test verifying `DeadlockValidationError` on dimension mismatch.
- `test_allocation_exceeding_max`: Invalid test verifying `DeadlockValidationError` when allocation $>$ max claim.

### 2.4 Storage / Disk Scheduling Subsystem (`tests/test_storage_manager.py`)
- `test_disk_fcfs`: Verifies traversal order and head movement (640 cylinders).
- `test_disk_sstf`: Verifies greedy seek optimization (236 cylinders).
- `test_disk_scan_up`: Verifies boundary movement to 199 and reversal (331 cylinders).
- `test_disk_c_scan`: Verifies circular sweep and return to 0 (382 cylinders).
- `test_disk_look_up`: Verifies reversal at max pending request (299 cylinders).
- `test_disk_c_look`: Verifies circular jump to lowest request (322 cylinders).
- `test_empty_requests`: Invalid test verifying `StorageValidationError` on empty request stream.
- `test_head_out_of_bounds`: Invalid test on initial head $\ge \text{disk\_size}$.
- `test_request_out_of_bounds`: Invalid test on cylinder request outside $[0, \text{disk\_size}-1]$.
- `test_invalid_direction`: Invalid test on unknown sweep direction.

### 2.5 Validation & Robustness Integration (`tests/test_validation_edge_cases.py`)
- `test_activity_logging_records_events`: Verifies operations write timestamped audit entries to `logs/os_simulator.log`.
- `test_json_workloads_loading`: Verifies syntax and schema validity of all JSON workload configurations in `data/`.
- `test_zero_burst_rejection`: Boundary validation rejecting zero-duration CPU tasks.
- `test_negative_memory_request`: Robustness validation rejecting negative memory requests.
- `test_extreme_cylinder_requests`: Boundary test validating cylinders at 0 and 199.

---

## 3. Exception Handling Architecture

The project replaces generic crashes with custom domain exceptions:
- `ProcessValidationError`: Raised for corrupt process structures, duplicate PIDs, negative timing values, or invalid time quanta.
- `SchedulerError`: Raised for dispatch queue logic violations.
- `MemoryValidationError`: Raised for negative block sizes, zero frames, unparseable strategies, or empty reference strings.
- `DeadlockValidationError`: Raised for mismatched vector/matrix dimensions, allocation exceeding max claim, or unmapped process references.
- `StorageValidationError`: Raised for out-of-boundary cylinder coordinates, invalid sweep directions, or empty queues.

Every exception records a structured `ERROR` log message with call stack and diagnostic context before propagating cleanly.

---

## 4. Activity Logging Architecture

Activity logging is configured centrally via `config.py`:
- **Dual Output:** Simultaneous logging to standard output and persistent log file (`logs/os_simulator.log`).
- **Audit Format:**
  ```
  [2026-11-13 11:31:02] [INFO    ] [process_scheduler:schedule_srtf:180]: Starting SRTF Preemptive simulation.
  [2026-11-13 11:31:02] [INFO    ] [process_scheduler:_build_result:98]: [SRTF (Preemptive)] Complete. Avg TAT: 11.60, Avg WT: 6.40, CPU Util: 100.00%
  [2026-11-13 11:31:03] [WARNING ] [memory_manager:analyze_beladys_anomaly:314]: Belady's Anomaly DETECTED in FIFO: Frame 3 had 9 faults, but Frame 4 had 10 faults!
  ```
- **Traceability:** Logs capture process arrivals, preemptions, context switches, page hits/faults, frame evictions, safe sequence allocations, and disk seeks.
