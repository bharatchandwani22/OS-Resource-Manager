"""
OS Resource Management Simulator - Main Application
Integrated Python-and-Bash Capstone Project.
Supports interactive terminal menu, automated CLI batch modes, benchmark generation, and visualization.
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

from config import DATA_DIR, OUTPUT_DIR, CHARTS_DIR, TRACES_DIR, logger
from modules.process_scheduler import (
    Process,
    schedule_fcfs,
    schedule_sjf_non_preemptive,
    schedule_srtf,
    schedule_round_robin,
    schedule_priority,
    schedule_mlfq,
    SchedulingResult
)
from modules.memory_manager import (
    allocate_contiguous,
    page_replace_fifo,
    page_replace_lru,
    page_replace_optimal,
    page_replace_lfu,
    analyze_beladys_anomaly,
    PageReplacementResult,
    ContiguousAllocationResult
)
from modules.deadlock_manager import (
    BankersState,
    check_bankers_safety,
    request_resources,
    ResourceAllocationGraph,
    detect_deadlock_multi_instance,
    SafetyResult,
    RAGResult
)
from modules.storage_manager import (
    disk_fcfs,
    disk_sstf,
    disk_scan,
    disk_c_scan,
    disk_look,
    disk_c_look,
    DiskSchedulingResult
)
from modules.telemetry import TelemetryCollector
from analysis.comparator import BenchmarkComparator
from analysis.visualizer import (
    plot_cpu_gantt,
    plot_cpu_comparison,
    plot_page_fault_curves,
    plot_disk_trajectories,
    plot_memory_blocks
)


def load_sample_processes() -> List[Process]:
    path = DATA_DIR / "processes_sample.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Process(**p) for p in data["processes"]]


def load_sample_memory() -> Dict[str, Any]:
    path = DATA_DIR / "memory_sample.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sample_deadlock() -> Dict[str, Any]:
    path = DATA_DIR / "deadlock_sample.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sample_storage() -> Dict[str, Any]:
    path = DATA_DIR / "storage_sample.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# Simulation Runners
# ==============================================================================

def run_process_scheduling(save_charts: bool = False):
    print("\n" + "=" * 70)
    print("           MODULE 1: PROCESS SCHEDULING SIMULATION")
    print("=" * 70)
    procs = load_sample_processes()
    print(f"Loaded {len(procs)} benchmark processes from data/processes_sample.json:")
    for p in procs:
        print(f"  PID: {p.pid:<4} | Arrival: {p.arrival_time:<2} | Burst: {p.burst_time:<2} | Priority: {p.priority}")
    print("-" * 70)

    # Run FCFS
    print("\n>>> 1. First-Come, First-Served (FCFS):")
    res_fcfs = schedule_fcfs(procs)
    print(res_fcfs.summary_table())

    # Run SRTF
    print("\n>>> 2. Shortest Remaining Time First (SRTF Preemptive):")
    res_srtf = schedule_srtf(procs)
    print(res_srtf.summary_table())

    # Run Round Robin (Q=2)
    print("\n>>> 3. Round Robin (RR, Quantum=2):")
    res_rr = schedule_round_robin(procs, quantum=2)
    print(res_rr.summary_table())

    # Run MLFQ
    print("\n>>> 4. Multi-Level Feedback Queue (MLFQ):")
    res_mlfq = schedule_mlfq(procs)
    print(res_mlfq.summary_table())

    if save_charts:
        plot_cpu_gantt(res_srtf, "gantt_srtf.png")
        plot_cpu_gantt(res_rr, "gantt_round_robin.png")
        df_comp = BenchmarkComparator.compare_cpu_schedulers(procs)
        plot_cpu_comparison(df_comp, "cpu_algorithm_comparison.png")
        print("\n>> [Visualizer] CPU Gantt and Comparison charts generated in output/charts/")


def run_memory_management(save_charts: bool = False):
    print("\n" + "=" * 70)
    print("           MODULE 2: MEMORY MANAGEMENT SIMULATION")
    print("=" * 70)
    data = load_sample_memory()

    # Part A: Contiguous Memory Allocation
    print(">>> PART A: Contiguous Memory Partition Allocation")
    raw_blocks = [tuple(b) for b in data["contiguous_allocation"]["blocks"]]
    raw_reqs = [tuple(r) for r in data["contiguous_allocation"]["requests"]]
    
    print("\n-- First Fit Allocation --")
    res_ff = allocate_contiguous("first_fit", raw_blocks, raw_reqs)
    print(res_ff.summary_table())

    print("\n-- Best Fit Allocation --")
    res_bf = allocate_contiguous("best_fit", raw_blocks, raw_reqs)
    print(res_bf.summary_table())

    if save_charts:
        plot_memory_blocks(res_bf, "memory_best_fit_map.png")

    # Part B: Virtual Memory Page Replacement
    print("\n" + "-" * 70)
    print(">>> PART B: Virtual Memory Page Replacement Algorithms")
    ref_string = data["page_replacement"]["standard_reference_string"]
    frames = data["page_replacement"]["frames"]
    print(f"Reference String: {ref_string}")
    print(f"Allocated Frames: {frames}")

    res_fifo = page_replace_fifo(ref_string, frames)
    res_lru = page_replace_lru(ref_string, frames)
    res_opt = page_replace_optimal(ref_string, frames)
    res_lfu = page_replace_lfu(ref_string, frames)

    print(f"\nResults for {frames} Frames:")
    print(f"  * FIFO:    Faults = {res_fifo.page_faults:<2} | Hits = {res_fifo.page_hits:<2} | Hit Ratio = {res_fifo.hit_ratio:.1%}")
    print(f"  * LRU:     Faults = {res_lru.page_faults:<2} | Hits = {res_lru.page_hits:<2} | Hit Ratio = {res_lru.hit_ratio:.1%}")
    print(f"  * Optimal: Faults = {res_opt.page_faults:<2} | Hits = {res_opt.page_hits:<2} | Hit Ratio = {res_opt.hit_ratio:.1%}")
    print(f"  * LFU:     Faults = {res_lfu.page_faults:<2} | Hits = {res_lfu.page_hits:<2} | Hit Ratio = {res_lfu.hit_ratio:.1%}")

    # Part C: Belady's Anomaly
    print("\n" + "-" * 70)
    print(">>> PART C: Belady's Anomaly Verification")
    belady_res = analyze_beladys_anomaly()
    print(f"Evaluated string: {belady_res['reference_string']}")
    for detail in belady_res["details"]:
        print(f"  [ALERT] {detail}")

    if save_charts:
        df_page_comp = BenchmarkComparator.compare_page_replacement(belady_res['reference_string'], frame_sizes=[2, 3, 4, 5, 6])
        plot_page_fault_curves(df_page_comp, "beladys_anomaly_curves.png")
        print("\n>> [Visualizer] Memory Map and Belady curves generated in output/charts/")


def run_deadlock_management():
    print("\n" + "=" * 70)
    print("           MODULE 3: DEADLOCK MANAGEMENT SIMULATION")
    print("=" * 70)
    data = load_sample_deadlock()

    # Part A: Banker's Algorithm
    print(">>> PART A: Banker's Algorithm (Safety & Resource-Request)")
    b_data = data["bankers_algorithm"]
    state = BankersState(
        process_ids=b_data["process_ids"],
        resource_ids=b_data["resource_ids"],
        available=b_data["available"],
        max_matrix=b_data["max_matrix"],
        allocation_matrix=b_data["allocation_matrix"]
    )
    safety_res = check_bankers_safety(state)
    print(safety_res.summary_table())

    # Resource Request evaluation
    print("\n-- Instantaneous Resource-Request Evaluation --")
    safe_req = data["sample_requests"]["safe_request"]
    granted, msg, _ = request_resources(state, safe_req["process_id"], safe_req["request"])
    print(f"Test 1: Process {safe_req['process_id']} requests {safe_req['request']}")
    print(f"  Outcome: {msg}")

    # Part B: RAG Cycle Detection
    print("\n" + "-" * 70)
    print(">>> PART B: Resource Allocation Graph (RAG) Cycle Detection")
    rag = ResourceAllocationGraph()
    for p, r in data["rag_graph"]["deadlock_cycle_case"]["request_edges"]:
        rag.add_request_edge(p, r)
    for r, p in data["rag_graph"]["deadlock_cycle_case"]["assignment_edges"]:
        rag.add_assignment_edge(r, p)
    rag_res = rag.detect_cycles()
    print(rag_res.graph_summary)

    # Part C: Multi-Instance Deadlock Detection & Victim Selection
    print("\n" + "-" * 70)
    print(">>> PART C: Multi-Instance Deadlock Detection & Recovery")
    mi = data["multi_instance_deadlock_detection"]
    det_res = detect_deadlock_multi_instance(
        process_ids=mi["process_ids"],
        resource_ids=mi["resource_ids"],
        available=mi["available"],
        allocation=mi["allocation"],
        request_matrix=mi["request"],
        process_costs=mi.get("costs")
    )
    print(f"Deadlocked Processes: {det_res.deadlocked_processes}")
    if det_res.recovery_recommendation:
        print(f"Recovery Strategy:    {det_res.recovery_recommendation}")


def run_storage_management(save_charts: bool = False):
    print("\n" + "=" * 70)
    print("           MODULE 4: STORAGE / DISK SCHEDULING SIMULATION")
    print("=" * 70)
    data = load_sample_storage()
    requests = data["requests"]
    initial_head = data["initial_head"]
    disk_size = data["disk_size"]

    print(f"Disk Configuration: Size={disk_size} cylinders | Initial Head Position={initial_head}")
    print(f"Incoming Cylinder Requests: {requests}")
    print("-" * 70)

    res_fcfs = disk_fcfs(requests, initial_head, disk_size)
    res_sstf = disk_sstf(requests, initial_head, disk_size)
    res_scan = disk_scan(requests, initial_head, disk_size, direction="up")
    res_cscan = disk_c_scan(requests, initial_head, disk_size)
    res_look = disk_look(requests, initial_head, disk_size, direction="up")
    res_clook = disk_c_look(requests, initial_head, disk_size)

    all_results = [res_fcfs, res_sstf, res_scan, res_cscan, res_look, res_clook]

    print(f"{'Algorithm':<15} {'Total Head Movement':<22} {'Avg Seek Distance':<20} {'Traversal Order'}")
    print("-" * 80)
    for r in sorted(all_results, key=lambda x: x.total_head_movement):
        order_preview = "->".join(map(str, r.traversal_order[:6])) + ("..." if len(r.traversal_order) > 6 else "")
        print(f"{r.algorithm:<15} {r.total_head_movement:<22} {r.average_seek_distance:<20.2f} {order_preview}")

    if save_charts:
        plot_disk_trajectories(all_results, "disk_scheduling_trajectories.png")
        print("\n>> [Visualizer] Disk Trajectory chart generated in output/charts/")


def run_all_benchmarks(save_charts: bool = True):
    print("\n" + "=" * 70)
    print("     PHASE 3: COMPREHENSIVE MULTI-MODULE BENCHMARK & COMPARISON")
    print("=" * 70)
    
    # 1. CPU
    procs = load_sample_processes()
    df_cpu = BenchmarkComparator.compare_cpu_schedulers(procs)
    print("\n[CPU Scheduling Comparison Table]")
    print(df_cpu.to_string(index=False))

    # 2. Memory Contiguous
    mem_data = load_sample_memory()
    blocks = [tuple(b) for b in mem_data["contiguous_allocation"]["blocks"]]
    reqs = [tuple(r) for r in mem_data["contiguous_allocation"]["requests"]]
    df_mem_cont = BenchmarkComparator.compare_contiguous_memory(blocks, reqs)
    print("\n[Contiguous Memory Allocation Comparison Table]")
    print(df_mem_cont.to_string(index=False))

    # 3. Memory Page Replacement
    ref_pages = mem_data["page_replacement"]["standard_reference_string"]
    df_pages = BenchmarkComparator.compare_page_replacement(ref_pages, frame_sizes=[3, 4, 5])
    print("\n[Page Replacement Algorithms Comparison Table]")
    print(df_pages.to_string(index=False))

    # 4. Disk
    stor_data = load_sample_storage()
    df_disk = BenchmarkComparator.compare_disk_schedulers(stor_data["requests"], stor_data["initial_head"])
    print("\n[Disk Scheduling Comparison Table]")
    print(df_disk.to_string(index=False))

    if save_charts:
        plot_cpu_comparison(df_cpu, "cpu_algorithm_comparison.png")
        plot_page_fault_curves(df_pages, "page_replacement_curves.png")
        all_disk = [
            disk_fcfs(stor_data["requests"], stor_data["initial_head"]),
            disk_sstf(stor_data["requests"], stor_data["initial_head"]),
            disk_scan(stor_data["requests"], stor_data["initial_head"]),
            disk_c_scan(stor_data["requests"], stor_data["initial_head"]),
            disk_look(stor_data["requests"], stor_data["initial_head"]),
            disk_c_look(stor_data["requests"], stor_data["initial_head"])
        ]
        plot_disk_trajectories(all_disk, "disk_scheduling_trajectories.png")
        print(f"\n>> All analytical figures saved to: {CHARTS_DIR}")


def show_interactive_menu():
    while True:
        print("\n" + "=" * 70)
        print("    OPERATING SYSTEM RESOURCE MANAGEMENT SIMULATOR (CAPSTONE)")
        print("=" * 70)
        print("  [1] Process Scheduling Simulation (FCFS, SJF, SRTF, RR, Priority, MLFQ)")
        print("  [2] Memory Management Simulation (Contiguous Allocation, Paging, Belady)")
        print("  [3] Deadlock Management Simulation (Banker's Safety, RAG Cycle, Recovery)")
        print("  [4] Storage / Disk Scheduling Simulation (FCFS, SSTF, SCAN, LOOK, etc.)")
        print("  [5] Live OS Telemetry & Real OS Resource Comparison (Bash / psutil)")
        print("  [6] Run Comprehensive Benchmark & Generate All Analytical Charts")
        print("  [7] Run Automated Unit & Boundary Test Suite (Phase 4)")
        print("  [8] Launch Web Dashboard Application (Browser UI)")
        print("  [9] Exit")
        print("=" * 70)
        choice = input("Enter your selection (1-9): ").strip()

        if choice == "1":
            run_process_scheduling(save_charts=True)
        elif choice == "2":
            run_memory_management(save_charts=True)
        elif choice == "3":
            run_deadlock_management()
        elif choice == "4":
            run_storage_management(save_charts=True)
        elif choice == "5":
            print("\n" + TelemetryCollector.format_comparison_summary())
        elif choice == "6":
            run_all_benchmarks(save_charts=True)
        elif choice == "7":
            import unittest
            suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent / "tests"))
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
        elif choice == "8":
            from web.app import run_server
            print("\n>> Launching OS Simulator Web Dashboard on http://127.0.0.1:5000 ...")
            run_server(port=5000)
        elif choice == "9":
            print("\nExiting OS Simulator. Goodbye!")
            break
        else:
            print("[Error] Invalid selection. Please enter a number between 1 and 9.")


def main():
    parser = argparse.ArgumentParser(description="Operating System Resource Management Simulator")
    parser.add_argument("--all", action="store_true", help="Run all modules, benchmarks, and generate charts")
    parser.add_argument("--benchmark", action="store_true", help="Execute batch benchmarks and output CSV tables")
    parser.add_argument("--save-charts", action="store_true", help="Generate and save high-resolution PNG charts")
    parser.add_argument("--module", choices=["cpu", "memory", "deadlock", "storage"], help="Run a specific subsystem")
    parser.add_argument("--telemetry", action="store_true", help="Display live host OS resource telemetry")
    parser.add_argument("--test", action="store_true", help="Run automated test suite")
    parser.add_argument("--web", action="store_true", help="Launch interactive browser web application")
    parser.add_argument("--port", type=int, default=5000, help="Web server port (default: 5000)")
    args = parser.parse_args()

    if args.web:
        from web.app import run_server
        print(f"\n>> Launching OS Simulator Web Dashboard on http://127.0.0.1:{args.port} ...")
        run_server(port=args.port)
        return

    if args.test:
        import unittest
        suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent / "tests"))
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
        return

    if args.telemetry:
        print(TelemetryCollector.format_comparison_summary())
        return

    if args.module:
        if args.module == "cpu":
            run_process_scheduling(save_charts=args.save_charts)
        elif args.module == "memory":
            run_memory_management(save_charts=args.save_charts)
        elif args.module == "deadlock":
            run_deadlock_management()
        elif args.module == "storage":
            run_storage_management(save_charts=args.save_charts)
        return

    if args.benchmark:
        run_all_benchmarks(save_charts=args.save_charts)
        return

    if args.all:
        run_process_scheduling(save_charts=args.save_charts)
        run_memory_management(save_charts=args.save_charts)
        run_deadlock_management()
        run_storage_management(save_charts=args.save_charts)
        print("\n" + TelemetryCollector.format_comparison_summary())
        run_all_benchmarks(save_charts=args.save_charts)
        return

    # Default to interactive menu
    show_interactive_menu()


if __name__ == "__main__":
    main()
