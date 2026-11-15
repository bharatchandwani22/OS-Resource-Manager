"""
Deadlock Management Module
Includes:
1. Banker's Algorithm (Safety Check & Resource-Request Algorithm).
2. Resource Allocation Graph (RAG) Cycle Detection using Graph Coloring DFS.
3. Multi-instance Deadlock Detection & Recovery (Victim Selection).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
import copy
from config import logger

class DeadlockValidationError(ValueError):
    """Custom exception raised for invalid deadlock parameters or matrix dimensions."""
    pass


@dataclass
class BankersState:
    process_ids: List[str]
    resource_ids: List[str]
    available: List[int]
    max_matrix: List[List[int]]
    allocation_matrix: List[List[int]]
    need_matrix: List[List[int]] = field(init=False)

    def __post_init__(self):
        # Validate dimensions
        n_p = len(self.process_ids)
        n_r = len(self.resource_ids)
        
        if n_p == 0 or n_r == 0:
            raise DeadlockValidationError("Process and Resource lists must be non-empty.")
        if len(self.available) != n_r:
            raise DeadlockValidationError(f"Available vector length ({len(self.available)}) does not match resource count ({n_r}).")
        if len(self.max_matrix) != n_p or any(len(row) != n_r for row in self.max_matrix):
            raise DeadlockValidationError("Max matrix dimensions do not match processes and resources.")
        if len(self.allocation_matrix) != n_p or any(len(row) != n_r for row in self.allocation_matrix):
            raise DeadlockValidationError("Allocation matrix dimensions do not match processes and resources.")

        # Compute Need = Max - Allocation
        self.need_matrix = []
        for i in range(n_p):
            row = []
            for j in range(n_r):
                if self.allocation_matrix[i][j] < 0 or self.max_matrix[i][j] < 0:
                    raise DeadlockValidationError(f"Negative values found in matrices for process {self.process_ids[i]}.")
                if self.allocation_matrix[i][j] > self.max_matrix[i][j]:
                    raise DeadlockValidationError(
                        f"Process {self.process_ids[i]} has allocated {self.allocation_matrix[i][j]} > max {self.max_matrix[i][j]} for resource {self.resource_ids[j]}."
                    )
                row.append(self.max_matrix[i][j] - self.allocation_matrix[i][j])
            self.need_matrix.append(row)


@dataclass
class SafetyResult:
    is_safe: bool
    safe_sequence: List[str]
    traces: List[str]
    work_snapshots: List[Dict[str, Any]]

    def summary_table(self) -> str:
        lines = [
            f"Banker's Algorithm State: {'SAFE' if self.is_safe else 'UNSAFE (Deadlock / Deadlock Risk)'}",
            "-" * 65
        ]
        if self.is_safe:
            seq_str = " -> ".join(self.safe_sequence)
            lines.append(f"Safe Execution Sequence: < {seq_str} >")
        else:
            lines.append("No safe sequence exists! The system is in an unsafe state.")
        lines.append("-" * 65)
        lines.append("Step-by-step Evaluation Traces:")
        for t in self.traces:
            lines.append(f"  * {t}")
        return "\n".join(lines)


def check_bankers_safety(state: BankersState) -> SafetyResult:
    """Runs Banker's Safety Algorithm to find a safe execution sequence."""
    logger.info("Executing Banker's Safety Algorithm.")
    n_p = len(state.process_ids)
    n_r = len(state.resource_ids)
    
    work = list(state.available)
    finish = [False] * n_p
    safe_sequence: List[str] = []
    traces: List[str] = [f"Initial Available Work vector: {dict(zip(state.resource_ids, work))}"]
    work_snapshots = []

    while len(safe_sequence) < n_p:
        found_candidate = False
        for i in range(n_p):
            if not finish[i]:
                # Check if Need[i] <= Work
                can_allocate = all(state.need_matrix[i][j] <= work[j] for j in range(n_r))
                if can_allocate:
                    # Allocate, process finishes and releases resources
                    for j in range(n_r):
                        work[j] += state.allocation_matrix[i][j]
                    finish[i] = True
                    safe_sequence.append(state.process_ids[i])
                    found_candidate = True
                    
                    trace_msg = (
                        f"Process {state.process_ids[i]} satisfies Need {state.need_matrix[i]} <= Work. "
                        f"Executed and freed resources {state.allocation_matrix[i]}. New Work: {work}"
                    )
                    traces.append(trace_msg)
                    work_snapshots.append({
                        "process": state.process_ids[i],
                        "work_after": list(work)
                    })
                    break

        if not found_candidate:
            # Cannot proceed, unsafe state
            traces.append(f"Unsafe condition: No unfinished process has Need <= Work {work}.")
            break

    is_safe = (len(safe_sequence) == n_p)
    logger.info(f"Banker's Safety check result: Safe={is_safe}, Sequence={safe_sequence}")
    return SafetyResult(
        is_safe=is_safe,
        safe_sequence=safe_sequence if is_safe else [],
        traces=traces,
        work_snapshots=work_snapshots
    )


def request_resources(state: BankersState, process_id: str, request_vector: List[int]) -> Tuple[bool, str, Optional[SafetyResult]]:
    """
    Banker's Resource-Request Algorithm:
    Evaluates whether an instantaneous request by process_id can be safely granted.
    """
    if process_id not in state.process_ids:
        raise DeadlockValidationError(f"Process ID '{process_id}' not found.")
    
    p_idx = state.process_ids.index(process_id)
    n_r = len(state.resource_ids)
    if len(request_vector) != n_r:
        raise DeadlockValidationError(f"Request vector length ({len(request_vector)}) does not match resource count ({n_r}).")

    logger.info(f"Process {process_id} requested resources: {request_vector}")

    # Condition 1: Request <= Need
    for j in range(n_r):
        if request_vector[j] > state.need_matrix[p_idx][j]:
            msg = f"Request DENIED: Process {process_id} requested {request_vector[j]} of {state.resource_ids[j]} exceeding its maximum claim need {state.need_matrix[p_idx][j]}."
            logger.warning(msg)
            return False, msg, None

    # Condition 2: Request <= Available
    for j in range(n_r):
        if request_vector[j] > state.available[j]:
            msg = f"Process {process_id} must WAIT: Requested resources exceed currently available {state.available[j]} of {state.resource_ids[j]}."
            logger.info(msg)
            return False, msg, None

    # Condition 3: Pretend allocation
    hypothetical_state = copy.deepcopy(state)
    for j in range(n_r):
        hypothetical_state.available[j] -= request_vector[j]
        hypothetical_state.allocation_matrix[p_idx][j] += request_vector[j]
        hypothetical_state.need_matrix[p_idx][j] -= request_vector[j]

    # Run safety algorithm on hypothetical state
    safety_res = check_bankers_safety(hypothetical_state)
    if safety_res.is_safe:
        msg = f"Request GRANTED: Safe state preserved. Safe sequence: < {' -> '.join(safety_res.safe_sequence)} >"
        logger.info(msg)
        return True, msg, safety_res
    else:
        msg = "Request REJECTED / BLOCKED: Granting this request would lead to an unsafe state (potential deadlock)."
        logger.warning(msg)
        return False, msg, safety_res


# -------------------------------------------------------------
# Part 2: Resource Allocation Graph (RAG) & Cycle Detection
# -------------------------------------------------------------

@dataclass
class RAGResult:
    has_deadlock_cycle: bool
    cycles_detected: List[List[str]]
    edges: List[Tuple[str, str]] # (source, target)
    graph_summary: str


class ResourceAllocationGraph:
    """
    RAG representation for single-instance resources.
    Nodes can be processes ('P1', 'P2') or resources ('R1', 'R2').
    Edges:
      P -> R : Request edge (Process waiting for Resource)
      R -> P : Assignment edge (Resource allocated to Process)
    """
    def __init__(self):
        self.adj_list: Dict[str, List[str]] = {}
        self.node_types: Dict[str, str] = {} # node -> 'process' | 'resource'

    def add_process(self, pid: str):
        if pid not in self.adj_list:
            self.adj_list[pid] = []
            self.node_types[pid] = 'process'

    def add_resource(self, rid: str):
        if rid not in self.adj_list:
            self.adj_list[rid] = []
            self.node_types[rid] = 'resource'

    def add_request_edge(self, pid: str, rid: str):
        """Process requests Resource (P -> R)"""
        self.add_process(pid)
        self.add_resource(rid)
        if rid not in self.adj_list[pid]:
            self.adj_list[pid].append(rid)

    def add_assignment_edge(self, rid: str, pid: str):
        """Resource assigned to Process (R -> P)"""
        self.add_resource(rid)
        self.add_process(pid)
        if pid not in self.adj_list[rid]:
            self.adj_list[rid].append(pid)

    def detect_cycles(self) -> RAGResult:
        """
        Detects directed cycles using 3-color DFS (WHITE=0, GRAY=1, BLACK=2).
        Returns all elementary deadlock cycles found.
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {node: WHITE for node in self.adj_list}
        parent = {node: None for node in self.adj_list}
        cycles = []

        def dfs(u: str, path: List[str]):
            colors[u] = GRAY
            path.append(u)

            for v in self.adj_list.get(u, []):
                if colors[v] == GRAY:
                    # Cycle detected: backtrack along current path
                    cycle_start = path.index(v)
                    detected_cycle = path[cycle_start:] + [v]
                    cycles.append(detected_cycle)
                elif colors[v] == WHITE:
                    parent[v] = u
                    dfs(v, path)

            path.pop()
            colors[u] = BLACK

        for node in list(self.adj_list.keys()):
            if colors[node] == WHITE:
                dfs(node, [])

        edges = []
        for src, dests in self.adj_list.items():
            for d in dests:
                edges.append((src, d))

        summary_lines = [
            f"RAG Cycle Detection: {'DEADLOCK DETECTED (Cycle exists)' if cycles else 'NO DEADLOCK (Acyclic Graph)'}",
            f"Total Nodes: {len(self.adj_list)}, Total Edges: {len(edges)}"
        ]
        if cycles:
            summary_lines.append("Detected Deadlock Cycles:")
            for idx, c in enumerate(cycles, 1):
                summary_lines.append(f"  Cycle {idx}: " + " -> ".join(c))
        else:
            summary_lines.append("The resource allocation graph has no cycles. The system is deadlock-free.")

        return RAGResult(
            has_deadlock_cycle=len(cycles) > 0,
            cycles_detected=cycles,
            edges=edges,
            graph_summary="\n".join(summary_lines)
        )


# -------------------------------------------------------------
# Part 3: Deadlock Detection & Recovery (Multi-Instance)
# -------------------------------------------------------------

@dataclass
class DeadlockDetectionResult:
    is_deadlocked: bool
    deadlocked_processes: List[str]
    recovery_recommendation: Optional[str]
    traces: List[str]


def detect_deadlock_multi_instance(
    process_ids: List[str],
    resource_ids: List[str],
    available: List[int],
    allocation: List[List[int]],
    request_matrix: List[List[int]],
    process_costs: Optional[Dict[str, int]] = None
) -> DeadlockDetectionResult:
    """
    Standard Operating System Deadlock Detection Algorithm for multi-instance resources.
    Identifies exact deadlocked processes and selects an optimal victim for preemption/termination.
    """
    n_p = len(process_ids)
    n_r = len(resource_ids)
    work = list(available)
    finish = [False] * n_p
    traces = []

    # Step 1: If Allocation[i] == 0, Finish[i] = True (it holds no resources)
    for i in range(n_p):
        if all(allocation[i][j] == 0 for j in range(n_r)):
            finish[i] = True

    traces.append(f"Initial Work: {work}. Processes with zero allocation marked finished.")

    # Step 2: Iterate
    progress = True
    while progress:
        progress = False
        for i in range(n_p):
            if not finish[i]:
                # Check if Request[i] <= Work
                if all(request_matrix[i][j] <= work[j] for j in range(n_r)):
                    # Assume process completes, releases allocation
                    for j in range(n_r):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    progress = True
                    traces.append(f"Process {process_ids[i]} requests can be satisfied. Released allocation {allocation[i]}. New Work: {work}")
                    break

    deadlocked_pids = [process_ids[i] for i in range(n_p) if not finish[i]]
    is_deadlocked = len(deadlocked_pids) > 0

    recovery = None
    if is_deadlocked:
        traces.append(f"DEADLOCK DETECTED among processes: {deadlocked_pids}")
        # Victim selection: pick process with lowest termination cost or least resources held
        if process_costs:
            victim = min(deadlocked_pids, key=lambda pid: process_costs.get(pid, 9999))
            recovery = f"Recommended Recovery: Terminate victim process '{victim}' (Lowest recovery cost: {process_costs.get(victim)})."
        else:
            # Pick process with least resources allocated
            def total_alloc(pid: str) -> int:
                idx = process_ids.index(pid)
                return sum(allocation[idx])
            victim = min(deadlocked_pids, key=total_alloc)
            recovery = f"Recommended Recovery: Abort victim process '{victim}' (Minimizes released resources disturbance: {total_alloc(victim)} units)."
        traces.append(recovery)
    else:
        traces.append("System is deadlock-free. All current resource requests can eventually be granted.")

    return DeadlockDetectionResult(
        is_deadlocked=is_deadlocked,
        deadlocked_processes=deadlocked_pids,
        recovery_recommendation=recovery,
        traces=traces
    )
