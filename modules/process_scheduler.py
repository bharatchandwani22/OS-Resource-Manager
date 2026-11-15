"""
Process Scheduling Module
Implements FCFS, SJF (Preemptive SRTF & Non-Preemptive), Priority (Preemptive & Non-Preemptive),
Round Robin (RR), and Multi-Level Feedback Queue (MLFQ).
Includes analytical metrics: Turnaround Time, Waiting Time, Response Time, CPU Utilization, Throughput.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
import copy
from config import logger

class SchedulerError(Exception):
    """Custom exception raised for process scheduling logic failures."""
    pass

class ProcessValidationError(ValueError):
    """Custom exception raised for invalid process parameter configurations."""
    pass


@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    
    # Dynamic Simulation State
    remaining_time: int = 0
    start_time: Optional[int] = None
    completion_time: int = 0
    waiting_time: int = 0
    turnaround_time: int = 0
    response_time: int = -1

    def __post_init__(self):
        self.remaining_time = self.burst_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "PID": self.pid,
            "Arrival": self.arrival_time,
            "Burst": self.burst_time,
            "Priority": self.priority,
            "Start": self.start_time,
            "Completion": self.completion_time,
            "Waiting": self.waiting_time,
            "Turnaround": self.turnaround_time,
            "Response": self.response_time
        }


@dataclass
class SchedulingResult:
    algorithm: str
    processes: List[Process]
    timeline: List[Tuple[int, int, str]] # (start_time, end_time, pid_or_IDLE)
    avg_turnaround_time: float
    avg_waiting_time: float
    avg_response_time: float
    cpu_utilization: float
    throughput: float
    total_time: int
    step_traces: List[str] = field(default_factory=list)

    def summary_table(self) -> str:
        header = f"{'PID':<6} {'Arrival':<8} {'Burst':<6} {'Priority':<9} {'Finish':<7} {'TAT':<6} {'WT':<6} {'RT':<6}"
        separator = "-" * len(header)
        lines = [header, separator]
        for p in sorted(self.processes, key=lambda x: x.pid):
            lines.append(f"{p.pid:<6} {p.arrival_time:<8} {p.burst_time:<6} {p.priority:<9} {p.completion_time:<7} {p.turnaround_time:<6} {p.waiting_time:<6} {p.response_time:<6}")
        lines.append(separator)
        lines.append(f"Average Turnaround Time: {self.avg_turnaround_time:.2f}")
        lines.append(f"Average Waiting Time:    {self.avg_waiting_time:.2f}")
        lines.append(f"Average Response Time:   {self.avg_response_time:.2f}")
        lines.append(f"CPU Utilization:         {self.cpu_utilization:.2f}%")
        lines.append(f"Throughput:              {self.throughput:.4f} proc/unit time")
        return "\n".join(lines)


def validate_processes(processes: List[Process]) -> None:
    """Validates boundary conditions, negative values, and ID uniqueness."""
    if not processes:
        logger.error("Process validation failed: Empty process list provided.")
        raise ProcessValidationError("Process list cannot be empty.")
    
    seen_pids = set()
    for p in processes:
        if not isinstance(p.pid, str) or not p.pid.strip():
            raise ProcessValidationError(f"Invalid PID: '{p.pid}'. PID must be a non-empty string.")
        if p.pid in seen_pids:
            raise ProcessValidationError(f"Duplicate PID detected: '{p.pid}'. All PIDs must be unique.")
        seen_pids.add(p.pid)
        
        if not isinstance(p.arrival_time, int) or p.arrival_time < 0:
            raise ProcessValidationError(f"Process {p.pid} has invalid arrival time {p.arrival_time}. Must be integer >= 0.")
        if not isinstance(p.burst_time, int) or p.burst_time <= 0:
            raise ProcessValidationError(f"Process {p.pid} has invalid burst time {p.burst_time}. Must be integer > 0.")
        if not isinstance(p.priority, int):
            raise ProcessValidationError(f"Process {p.pid} priority must be an integer, got {p.priority}.")


def _build_result(algorithm: str, processes: List[Process], raw_timeline: List[Tuple[int, int, str]], 
                  current_time: int, traces: List[str]) -> SchedulingResult:
    """Consolidates contiguous execution intervals, computes metrics and returns SchedulingResult."""
    # Consolidate raw timeline into contiguous blocks
    consolidated_timeline: List[Tuple[int, int, str]] = []
    for start, end, pid in raw_timeline:
        if start == end:
            continue
        if consolidated_timeline and consolidated_timeline[-1][2] == pid and consolidated_timeline[-1][1] == start:
            prev_start, _, prev_pid = consolidated_timeline[-1]
            consolidated_timeline[-1] = (prev_start, end, prev_pid)
        else:
            consolidated_timeline.append((start, end, pid))

    n = len(processes)
    total_tat = sum(p.turnaround_time for p in processes)
    total_wt = sum(p.waiting_time for p in processes)
    total_rt = sum(p.response_time for p in processes)
    
    busy_time = sum(p.burst_time for p in processes)
    cpu_util = (busy_time / current_time * 100.0) if current_time > 0 else 0.0
    throughput = (n / current_time) if current_time > 0 else 0.0

    result = SchedulingResult(
        algorithm=algorithm,
        processes=processes,
        timeline=consolidated_timeline,
        avg_turnaround_time=total_tat / n,
        avg_waiting_time=total_wt / n,
        avg_response_time=total_rt / n,
        cpu_utilization=cpu_util,
        throughput=throughput,
        total_time=current_time,
        step_traces=traces
    )
    logger.info(f"[{algorithm}] Complete. Avg TAT: {result.avg_turnaround_time:.2f}, Avg WT: {result.avg_waiting_time:.2f}, CPU Util: {result.cpu_utilization:.2f}%")
    return result


def schedule_fcfs(process_list: List[Process]) -> SchedulingResult:
    """First-Come, First-Served (FCFS) non-preemptive scheduling."""
    validate_processes(process_list)
    logger.info("Starting FCFS scheduling simulation.")
    procs = [copy.deepcopy(p) for p in process_list]
    procs.sort(key=lambda x: (x.arrival_time, x.pid))
    
    current_time = 0
    raw_timeline = []
    traces = []
    
    for p in procs:
        if current_time < p.arrival_time:
            traces.append(f"T={current_time}: CPU Idle until T={p.arrival_time}")
            raw_timeline.append((current_time, p.arrival_time, "IDLE"))
            current_time = p.arrival_time
            
        p.start_time = current_time
        p.response_time = p.start_time - p.arrival_time
        traces.append(f"T={current_time}: Process {p.pid} dispatched. Runs for {p.burst_time} units.")
        
        raw_timeline.append((current_time, current_time + p.burst_time, p.pid))
        current_time += p.burst_time
        
        p.completion_time = current_time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        p.remaining_time = 0
        traces.append(f"T={current_time}: Process {p.pid} completed (TAT={p.turnaround_time}, WT={p.waiting_time}).")
        
    return _build_result("FCFS", procs, raw_timeline, current_time, traces)


def schedule_sjf_non_preemptive(process_list: List[Process]) -> SchedulingResult:
    """Shortest Job First (SJF) Non-Preemptive scheduling."""
    validate_processes(process_list)
    logger.info("Starting SJF Non-Preemptive simulation.")
    procs = [copy.deepcopy(p) for p in process_list]
    current_time = 0
    completed = []
    remaining = procs[:]
    raw_timeline = []
    traces = []

    while remaining:
        available = [p for p in remaining if p.arrival_time <= current_time]
        if not available:
            next_arrival = min(p.arrival_time for p in remaining)
            raw_timeline.append((current_time, next_arrival, "IDLE"))
            traces.append(f"T={current_time}: CPU Idle until next arrival T={next_arrival}")
            current_time = next_arrival
            continue

        # Pick shortest burst time, tie-breaker: arrival time, then pid
        available.sort(key=lambda x: (x.burst_time, x.arrival_time, x.pid))
        p = available[0]
        remaining.remove(p)

        p.start_time = current_time
        p.response_time = p.start_time - p.arrival_time
        traces.append(f"T={current_time}: Process {p.pid} (Burst={p.burst_time}) dispatched.")
        
        raw_timeline.append((current_time, current_time + p.burst_time, p.pid))
        current_time += p.burst_time
        
        p.completion_time = current_time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        p.remaining_time = 0
        completed.append(p)
        traces.append(f"T={current_time}: Process {p.pid} completed.")

    return _build_result("SJF (Non-Preemptive)", completed, raw_timeline, current_time, traces)


def schedule_srtf(process_list: List[Process]) -> SchedulingResult:
    """Shortest Remaining Time First (SRTF) Preemptive SJF scheduling."""
    validate_processes(process_list)
    logger.info("Starting SRTF Preemptive simulation.")
    procs = [copy.deepcopy(p) for p in process_list]
    current_time = 0
    completed = []
    raw_timeline = []
    traces = []
    n = len(procs)

    active_p: Optional[Process] = None

    while len(completed) < n:
        available = [p for p in procs if p.arrival_time <= current_time and p.remaining_time > 0]
        if not available:
            next_arrival = min(p.arrival_time for p in procs if p.remaining_time > 0)
            raw_timeline.append((current_time, next_arrival, "IDLE"))
            current_time = next_arrival
            continue

        available.sort(key=lambda x: (x.remaining_time, x.arrival_time, x.pid))
        chosen = available[0]

        if active_p != chosen:
            if active_p is not None and active_p.remaining_time > 0:
                traces.append(f"T={current_time}: Process {active_p.pid} preempted by {chosen.pid} (Remaining={chosen.remaining_time}).")
            active_p = chosen
            if active_p.start_time is None:
                active_p.start_time = current_time
                active_p.response_time = current_time - active_p.arrival_time
            traces.append(f"T={current_time}: Process {active_p.pid} dispatched (Remaining={active_p.remaining_time}).")

        # Advance by 1 time unit
        raw_timeline.append((current_time, current_time + 1, active_p.pid))
        active_p.remaining_time -= 1
        current_time += 1

        if active_p.remaining_time == 0:
            active_p.completion_time = current_time
            active_p.turnaround_time = active_p.completion_time - active_p.arrival_time
            active_p.waiting_time = active_p.turnaround_time - active_p.burst_time
            completed.append(active_p)
            traces.append(f"T={current_time}: Process {active_p.pid} completed.")
            active_p = None

    return _build_result("SRTF (Preemptive)", completed, raw_timeline, current_time, traces)


def schedule_round_robin(process_list: List[Process], quantum: int = 2) -> SchedulingResult:
    """Round Robin (RR) scheduling with time slice / quantum."""
    validate_processes(process_list)
    if quantum <= 0:
        logger.error(f"Invalid quantum {quantum} for Round Robin.")
        raise ProcessValidationError("Time quantum must be a positive integer > 0.")
    
    logger.info(f"Starting Round Robin simulation with quantum={quantum}.")
    procs = [copy.deepcopy(p) for p in process_list]
    procs.sort(key=lambda x: (x.arrival_time, x.pid))
    
    current_time = 0
    ready_queue: List[Process] = []
    completed: List[Process] = []
    raw_timeline = []
    traces = []
    
    arrival_idx = 0
    n = len(procs)

    while len(completed) < n:
        # Enqueue new arrivals up to current_time
        while arrival_idx < n and procs[arrival_idx].arrival_time <= current_time:
            ready_queue.append(procs[arrival_idx])
            traces.append(f"T={current_time}: Process {procs[arrival_idx].pid} arrived and placed in ready queue.")
            arrival_idx += 1

        if not ready_queue:
            if arrival_idx < n:
                next_arrival = procs[arrival_idx].arrival_time
                raw_timeline.append((current_time, next_arrival, "IDLE"))
                current_time = next_arrival
                continue
            break

        p = ready_queue.pop(0)
        if p.start_time is None:
            p.start_time = current_time
            p.response_time = current_time - p.arrival_time

        exec_time = min(quantum, p.remaining_time)
        traces.append(f"T={current_time}: Process {p.pid} running for {exec_time} units (Remaining before: {p.remaining_time}).")
        raw_timeline.append((current_time, current_time + exec_time, p.pid))
        p.remaining_time -= exec_time
        current_time += exec_time

        # Check for newly arrived processes during this time slice
        while arrival_idx < n and procs[arrival_idx].arrival_time <= current_time:
            ready_queue.append(procs[arrival_idx])
            traces.append(f"T={current_time}: Process {procs[arrival_idx].pid} arrived during slice.")
            arrival_idx += 1

        if p.remaining_time > 0:
            ready_queue.append(p)
            traces.append(f"T={current_time}: Process {p.pid} quantum expired. Re-enqueued (Remaining: {p.remaining_time}).")
        else:
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            completed.append(p)
            traces.append(f"T={current_time}: Process {p.pid} finished execution.")

    return _build_result(f"Round Robin (Q={quantum})", completed, raw_timeline, current_time, traces)


def schedule_priority(process_list: List[Process], preemptive: bool = False, 
                      lower_number_higher_priority: bool = True) -> SchedulingResult:
    """
    Priority Scheduling (both Non-Preemptive and Preemptive).
    Default: lower priority number implies higher priority (standard UNIX style).
    """
    validate_processes(process_list)
    algo_name = f"Priority ({'Preemptive' if preemptive else 'Non-Preemptive'})"
    logger.info(f"Starting {algo_name} simulation.")
    
    procs = [copy.deepcopy(p) for p in process_list]
    current_time = 0
    completed: List[Process] = []
    raw_timeline = []
    traces = []
    n = len(procs)

    def priority_key(p: Process):
        # Tuple: (priority, arrival, pid)
        pri = p.priority if lower_number_higher_priority else -p.priority
        return (pri, p.arrival_time, p.pid)

    if not preemptive:
        remaining = procs[:]
        while remaining:
            available = [p for p in remaining if p.arrival_time <= current_time]
            if not available:
                next_arr = min(p.arrival_time for p in remaining)
                raw_timeline.append((current_time, next_arr, "IDLE"))
                current_time = next_arr
                continue
            
            available.sort(key=priority_key)
            p = available[0]
            remaining.remove(p)

            p.start_time = current_time
            p.response_time = p.start_time - p.arrival_time
            traces.append(f"T={current_time}: Process {p.pid} (Priority={p.priority}) dispatched.")
            
            raw_timeline.append((current_time, current_time + p.burst_time, p.pid))
            current_time += p.burst_time
            
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            p.remaining_time = 0
            completed.append(p)
            traces.append(f"T={current_time}: Process {p.pid} completed.")
    else:
        active_p: Optional[Process] = None
        while len(completed) < n:
            available = [p for p in procs if p.arrival_time <= current_time and p.remaining_time > 0]
            if not available:
                next_arr = min(p.arrival_time for p in procs if p.remaining_time > 0)
                raw_timeline.append((current_time, next_arr, "IDLE"))
                current_time = next_arr
                continue

            available.sort(key=priority_key)
            chosen = available[0]

            if active_p != chosen:
                if active_p is not None and active_p.remaining_time > 0:
                    traces.append(f"T={current_time}: Process {active_p.pid} preempted by higher priority {chosen.pid}.")
                active_p = chosen
                if active_p.start_time is None:
                    active_p.start_time = current_time
                    active_p.response_time = current_time - active_p.arrival_time
                traces.append(f"T={current_time}: Process {active_p.pid} running (Priority={active_p.priority}).")

            raw_timeline.append((current_time, current_time + 1, active_p.pid))
            active_p.remaining_time -= 1
            current_time += 1

            if active_p.remaining_time == 0:
                active_p.completion_time = current_time
                active_p.turnaround_time = active_p.completion_time - active_p.arrival_time
                active_p.waiting_time = active_p.turnaround_time - active_p.burst_time
                completed.append(active_p)
                traces.append(f"T={current_time}: Process {active_p.pid} completed.")
                active_p = None

    return _build_result(algo_name, completed, raw_timeline, current_time, traces)


def schedule_mlfq(process_list: List[Process], 
                   q0_quantum: int = 2, 
                   q1_quantum: int = 4, 
                   aging_interval: int = 20) -> SchedulingResult:
    """
    Multi-Level Feedback Queue (MLFQ):
    - Level 0: RR with time slice q0_quantum
    - Level 1: RR with time slice q1_quantum
    - Level 2: FCFS
    - Aging: Every aging_interval, all uncompleted processes are promoted to Queue 0 to prevent starvation.
    """
    validate_processes(process_list)
    logger.info("Starting MLFQ simulation.")
    procs = [copy.deepcopy(p) for p in process_list]
    procs.sort(key=lambda x: (x.arrival_time, x.pid))
    
    current_time = 0
    q0: List[Process] = []
    q1: List[Process] = []
    q2: List[Process] = []
    
    completed: List[Process] = []
    raw_timeline = []
    traces = []
    arrival_idx = 0
    n = len(procs)
    last_aging_time = 0

    while len(completed) < n:
        # Periodic Priority Boost (Aging)
        if current_time - last_aging_time >= aging_interval and current_time > 0:
            demoted_count = len(q1) + len(q2)
            if demoted_count > 0:
                q0.extend(q1)
                q0.extend(q2)
                q1.clear()
                q2.clear()
                traces.append(f"T={current_time}: [AGING BOOST] Promoted {demoted_count} processes back to Queue 0.")
            last_aging_time = current_time

        # Enqueue arrivals
        while arrival_idx < n and procs[arrival_idx].arrival_time <= current_time:
            q0.append(procs[arrival_idx])
            traces.append(f"T={current_time}: Process {procs[arrival_idx].pid} arrived into Queue 0.")
            arrival_idx += 1

        # Check idle
        if not q0 and not q1 and not q2:
            if arrival_idx < n:
                next_arr = procs[arrival_idx].arrival_time
                raw_timeline.append((current_time, next_arr, "IDLE"))
                current_time = next_arr
                continue
            break

        # Select queue level
        if q0:
            p = q0.pop(0)
            quantum = q0_quantum
            next_q = q1
            q_name = "Q0 (RR-2)"
        elif q1:
            p = q1.pop(0)
            quantum = q1_quantum
            next_q = q2
            q_name = "Q1 (RR-4)"
        else:
            p = q2.pop(0)
            quantum = p.remaining_time # FCFS
            next_q = q2
            q_name = "Q2 (FCFS)"

        if p.start_time is None:
            p.start_time = current_time
            p.response_time = current_time - p.arrival_time

        exec_time = min(quantum, p.remaining_time)
        traces.append(f"T={current_time}: Running {p.pid} from {q_name} for {exec_time} units (Remaining: {p.remaining_time}).")
        raw_timeline.append((current_time, current_time + exec_time, p.pid))
        p.remaining_time -= exec_time
        current_time += exec_time

        # Collect any new arrivals during execution
        while arrival_idx < n and procs[arrival_idx].arrival_time <= current_time:
            q0.append(procs[arrival_idx])
            traces.append(f"T={current_time}: Process {procs[arrival_idx].pid} arrived into Queue 0.")
            arrival_idx += 1

        if p.remaining_time > 0:
            next_q.append(p)
            traces.append(f"T={current_time}: Process {p.pid} did not finish, demoted to next queue level.")
        else:
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            completed.append(p)
            traces.append(f"T={current_time}: Process {p.pid} finished execution.")

    return _build_result("MLFQ", completed, raw_timeline, current_time, traces)
