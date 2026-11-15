"""
Comparative Analysis Engine
Runs multi-algorithm evaluations across identical workloads to produce statistical benchmarks,
comparative metrics tables, and CSV exports.
"""

from typing import List, Dict, Tuple, Any, Optional
import pandas as pd
from pathlib import Path

from config import TRACES_DIR, logger
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
    PageReplacementResult,
    ContiguousAllocationResult
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


class BenchmarkComparator:
    """Manages cross-algorithm benchmarks and statistical metric generation."""

    @staticmethod
    def compare_cpu_schedulers(processes: List[Process], rr_quantum: int = 2) -> pd.DataFrame:
        """Runs all CPU scheduling algorithms on the same process dataset."""
        logger.info("Executing comprehensive CPU Scheduler Benchmark.")
        results: List[SchedulingResult] = [
            schedule_fcfs(processes),
            schedule_sjf_non_preemptive(processes),
            schedule_srtf(processes),
            schedule_round_robin(processes, quantum=rr_quantum),
            schedule_priority(processes, preemptive=False),
            schedule_priority(processes, preemptive=True),
            schedule_mlfq(processes)
        ]

        data = []
        for r in results:
            data.append({
                "Algorithm": r.algorithm,
                "Avg Turnaround Time": round(r.avg_turnaround_time, 2),
                "Avg Waiting Time": round(r.avg_waiting_time, 2),
                "Avg Response Time": round(r.avg_response_time, 2),
                "CPU Utilization (%)": round(r.cpu_utilization, 2),
                "Throughput (p/unit)": round(r.throughput, 4),
                "Total Time": r.total_time
            })

        df = pd.DataFrame(data)
        out_csv = TRACES_DIR / "cpu_scheduler_benchmark.csv"
        df.to_csv(out_csv, index=False)
        logger.info(f"Saved CPU benchmark table to {out_csv}")
        return df

    @staticmethod
    def compare_page_replacement(reference_string: List[int], frame_sizes: List[int] = [3, 4, 5]) -> pd.DataFrame:
        """Compares FIFO, LRU, Optimal, and LFU across specified frame counts."""
        logger.info("Executing Page Replacement Multi-Algorithm Benchmark.")
        data = []

        for f in frame_sizes:
            algorithms = [
                page_replace_fifo(reference_string, f),
                page_replace_lru(reference_string, f),
                page_replace_optimal(reference_string, f),
                page_replace_lfu(reference_string, f)
            ]
            for res in algorithms:
                data.append({
                    "Algorithm": res.algorithm,
                    "Frames": f,
                    "Page Faults": res.page_faults,
                    "Page Hits": res.page_hits,
                    "Fault Ratio (%)": round(res.fault_ratio * 100, 2),
                    "Hit Ratio (%)": round(res.hit_ratio * 100, 2)
                })

        df = pd.DataFrame(data)
        out_csv = TRACES_DIR / "page_replacement_benchmark.csv"
        df.to_csv(out_csv, index=False)
        logger.info(f"Saved Page Replacement benchmark table to {out_csv}")
        return df

    @staticmethod
    def compare_disk_schedulers(requests: List[int], initial_head: int, disk_size: int = 200) -> pd.DataFrame:
        """Compares FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK on identical disk queues."""
        logger.info("Executing Disk Scheduling Multi-Algorithm Benchmark.")
        results: List[DiskSchedulingResult] = [
            disk_fcfs(requests, initial_head, disk_size),
            disk_sstf(requests, initial_head, disk_size),
            disk_scan(requests, initial_head, disk_size, direction="up"),
            disk_c_scan(requests, initial_head, disk_size),
            disk_look(requests, initial_head, disk_size, direction="up"),
            disk_c_look(requests, initial_head, disk_size)
        ]

        data = []
        for r in results:
            data.append({
                "Algorithm": r.algorithm,
                "Initial Head": r.initial_head,
                "Total Head Movement": r.total_head_movement,
                "Average Seek Distance": round(r.average_seek_distance, 2)
            })

        df = pd.DataFrame(data)
        # Sort by best (lowest) head movement
        df = df.sort_values(by="Total Head Movement", ascending=True)
        out_csv = TRACES_DIR / "disk_scheduling_benchmark.csv"
        df.to_csv(out_csv, index=False)
        logger.info(f"Saved Disk Scheduling benchmark table to {out_csv}")
        return df

    @staticmethod
    def compare_contiguous_memory(initial_blocks: List[Tuple[int, int]], 
                                  requests: List[Tuple[str, int]]) -> pd.DataFrame:
        """Compares First-Fit, Best-Fit, and Worst-Fit contiguous allocations."""
        logger.info("Executing Contiguous Memory Allocation Benchmark.")
        strategies = ["first_fit", "best_fit", "worst_fit"]
        data = []

        for strat in strategies:
            res: ContiguousAllocationResult = allocate_contiguous(strat, initial_blocks, requests)
            data.append({
                "Strategy": strat.replace("_", " ").title(),
                "Allocated Count": len(res.allocated_requests),
                "Unallocated Count": len(res.unallocated_requests),
                "Internal Frag (B)": res.internal_fragmentation,
                "External Frag (B)": res.external_fragmentation,
                "Total Memory (B)": res.total_memory,
                "Used Memory (B)": res.allocated_memory
            })

        df = pd.DataFrame(data)
        out_csv = TRACES_DIR / "contiguous_memory_benchmark.csv"
        df.to_csv(out_csv, index=False)
        return df
