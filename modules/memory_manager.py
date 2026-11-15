"""
Memory Management Module
Covers:
1. Contiguous Allocation: First Fit, Best Fit, Worst Fit (calculating internal & external fragmentation).
2. Virtual Memory Page Replacement: FIFO, LRU, Optimal, LFU.
3. Belady's Anomaly comparative analysis and verification.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
import copy
from config import logger

class MemoryValidationError(ValueError):
    """Custom exception raised for invalid memory inputs."""
    pass


# -------------------------------------------------------------
# Part 1: Contiguous Allocation
# -------------------------------------------------------------

@dataclass
class MemoryBlock:
    block_id: int
    size: int
    start_address: int
    allocated_to: Optional[str] = None
    allocated_size: int = 0

    @property
    def is_free(self) -> bool:
        return self.allocated_to is None

    @property
    def internal_fragmentation(self) -> int:
        if not self.is_free:
            return self.size - self.allocated_size
        return 0


@dataclass
class ContiguousAllocationResult:
    strategy: str
    blocks: List[MemoryBlock]
    allocated_requests: Dict[str, int] # Process PID -> Block ID
    unallocated_requests: List[Tuple[str, int]] # (PID, requested_size)
    total_memory: int
    allocated_memory: int
    internal_fragmentation: int
    external_fragmentation: int
    traces: List[str] = field(default_factory=list)

    def summary_table(self) -> str:
        lines = [
            f"Contiguous Allocation Strategy: {self.strategy}",
            f"{'Block ID':<10} {'Start Addr':<12} {'Capacity':<10} {'Status':<15} {'Process':<10} {'Internal Frag':<14}",
            "-" * 75
        ]
        for b in self.blocks:
            status = "Free" if b.is_free else f"Allocated ({b.allocated_size}B)"
            pid_str = "-" if b.is_free else str(b.allocated_to)
            lines.append(f"{b.block_id:<10} {b.start_address:<12} {b.size:<10} {status:<15} {pid_str:<10} {b.internal_fragmentation:<14}")
        lines.append("-" * 75)
        lines.append(f"Total Internal Fragmentation: {self.internal_fragmentation} B")
        lines.append(f"Total External Fragmentation: {self.external_fragmentation} B")
        if self.unallocated_requests:
            lines.append(f"Unallocated Requests: {self.unallocated_requests}")
        return "\n".join(lines)


def allocate_contiguous(strategy: str, 
                        initial_blocks: List[Tuple[int, int]], 
                        process_requests: List[Tuple[str, int]]) -> ContiguousAllocationResult:
    """
    Simulates Contiguous Memory Allocation using First-Fit, Best-Fit, or Worst-Fit.
    - initial_blocks: List of (block_id, size)
    - process_requests: List of (pid, requested_size)
    """
    strategy = strategy.lower().strip()
    if strategy not in ["first_fit", "best_fit", "worst_fit"]:
        raise MemoryValidationError(f"Unknown allocation strategy: {strategy}. Expected first_fit, best_fit, or worst_fit.")

    if not initial_blocks:
        raise MemoryValidationError("Initial memory blocks list cannot be empty.")
    if not process_requests:
        raise MemoryValidationError("Process requests list cannot be empty.")

    # Build memory blocks
    blocks: List[MemoryBlock] = []
    curr_addr = 0
    for bid, bsize in initial_blocks:
        if bsize <= 0:
            raise MemoryValidationError(f"Block size must be > 0. Got {bsize} for block {bid}.")
        blocks.append(MemoryBlock(block_id=bid, size=bsize, start_address=curr_addr))
        curr_addr += bsize

    total_memory = sum(b.size for b in blocks)
    allocated: Dict[str, int] = {}
    unallocated: List[Tuple[str, int]] = []
    traces: List[str] = []

    logger.info(f"Running Contiguous Memory Allocation with strategy={strategy}.")

    for pid, req_size in process_requests:
        if req_size <= 0:
            raise MemoryValidationError(f"Requested size for {pid} must be positive. Got {req_size}.")

        # Find eligible free blocks
        eligible = [(idx, b) for idx, b in enumerate(blocks) if b.is_free and b.size >= req_size]

        if not eligible:
            traces.append(f"Request {pid} ({req_size}B): NO sufficient free block available. Denied.")
            unallocated.append((pid, req_size))
            continue

        selected_block: Optional[MemoryBlock] = None
        if strategy == "first_fit":
            selected_block = eligible[0][1]
        elif strategy == "best_fit":
            # Smallest block that fits
            eligible.sort(key=lambda x: (x[1].size, x[1].block_id))
            selected_block = eligible[0][1]
        elif strategy == "worst_fit":
            # Largest block available
            eligible.sort(key=lambda x: (-x[1].size, x[1].block_id))
            selected_block = eligible[0][1]

        selected_block.allocated_to = pid
        selected_block.allocated_size = req_size
        allocated[pid] = selected_block.block_id
        traces.append(f"Request {pid} ({req_size}B): Allocated to Block {selected_block.block_id} (Capacity {selected_block.size}B, Frag={selected_block.internal_fragmentation}B).")

    total_internal_frag = sum(b.internal_fragmentation for b in blocks if not b.is_free)
    total_free_space = sum(b.size for b in blocks if b.is_free)
    
    # External fragmentation exists when total free space >= unallocated request size, but no single block could fit it
    external_frag = 0
    for upid, usize in unallocated:
        if total_free_space >= usize:
            external_frag = total_free_space
            break

    total_allocated = sum(b.allocated_size for b in blocks if not b.is_free)

    return ContiguousAllocationResult(
        strategy=strategy,
        blocks=blocks,
        allocated_requests=allocated,
        unallocated_requests=unallocated,
        total_memory=total_memory,
        allocated_memory=total_allocated,
        internal_fragmentation=total_internal_frag,
        external_fragmentation=external_frag,
        traces=traces
    )


# -------------------------------------------------------------
# Part 2: Virtual Memory Page Replacement
# -------------------------------------------------------------

@dataclass
class PageReplacementStep:
    step: int
    page: int
    frames_snapshot: List[Optional[int]]
    hit: bool
    evicted_page: Optional[int] = None


@dataclass
class PageReplacementResult:
    algorithm: str
    reference_string: List[int]
    num_frames: int
    page_faults: int
    page_hits: int
    hit_ratio: float
    fault_ratio: float
    step_history: List[PageReplacementStep]

    def summary_table(self) -> str:
        lines = [
            f"Page Replacement Algorithm: {self.algorithm} (Frames: {self.num_frames})",
            f"Reference String: {self.reference_string}",
            "-" * 65,
            f"{'Step':<6} {'Page':<6} {'Frame State':<30} {'Status':<10} {'Evicted':<8}",
            "-" * 65
        ]
        for s in self.step_history:
            frames_str = str([f if f is not None else "-" for f in s.frames_snapshot])
            status = "HIT" if s.hit else "FAULT"
            evicted = str(s.evicted_page) if s.evicted_page is not None else "-"
            lines.append(f"{s.step:<6} {s.page:<6} {frames_str:<30} {status:<10} {evicted:<8}")
        lines.append("-" * 65)
        lines.append(f"Total Page Faults: {self.page_faults} ({self.fault_ratio:.2%})")
        lines.append(f"Total Page Hits:   {self.page_hits} ({self.hit_ratio:.2%})")
        return "\n".join(lines)


def _validate_page_inputs(reference_string: List[int], num_frames: int):
    if not reference_string:
        raise MemoryValidationError("Reference string cannot be empty.")
    if num_frames <= 0:
        raise MemoryValidationError(f"Number of frames must be > 0. Got {num_frames}.")
    for p in reference_string:
        if not isinstance(p, int) or p < 0:
            raise MemoryValidationError(f"Invalid page reference '{p}'. Pages must be non-negative integers.")


def page_replace_fifo(reference_string: List[int], num_frames: int) -> PageReplacementResult:
    """First-In, First-Out (FIFO) page replacement."""
    _validate_page_inputs(reference_string, num_frames)
    logger.info(f"Running FIFO Page Replacement with {num_frames} frames.")
    
    frames: List[Optional[int]] = [None] * num_frames
    fifo_queue: List[int] = [] # Tracks arrival order
    faults = 0
    hits = 0
    history: List[PageReplacementStep] = []

    for step_idx, page in enumerate(reference_string):
        evicted = None
        if page in frames:
            hits += 1
            hit = True
        else:
            faults += 1
            hit = False
            if None in frames:
                # Find first empty slot
                empty_idx = frames.index(None)
                frames[empty_idx] = page
                fifo_queue.append(page)
            else:
                # Evict oldest
                evicted = fifo_queue.pop(0)
                evict_idx = frames.index(evicted)
                frames[evict_idx] = page
                fifo_queue.append(page)

        history.append(PageReplacementStep(
            step=step_idx + 1,
            page=page,
            frames_snapshot=list(frames),
            hit=hit,
            evicted_page=evicted
        ))

    total = len(reference_string)
    return PageReplacementResult(
        algorithm="FIFO",
        reference_string=reference_string,
        num_frames=num_frames,
        page_faults=faults,
        page_hits=hits,
        hit_ratio=hits / total,
        fault_ratio=faults / total,
        step_history=history
    )


def page_replace_lru(reference_string: List[int], num_frames: int) -> PageReplacementResult:
    """Least Recently Used (LRU) page replacement."""
    _validate_page_inputs(reference_string, num_frames)
    logger.info(f"Running LRU Page Replacement with {num_frames} frames.")

    frames: List[Optional[int]] = [None] * num_frames
    last_used: Dict[int, int] = {}
    faults = 0
    hits = 0
    history: List[PageReplacementStep] = []

    for step_idx, page in enumerate(reference_string):
        evicted = None
        if page in frames:
            hits += 1
            hit = True
        else:
            faults += 1
            hit = False
            if None in frames:
                empty_idx = frames.index(None)
                frames[empty_idx] = page
            else:
                # Find page with oldest timestamp in last_used
                evicted = min(frames, key=lambda p: last_used.get(p, -1))
                evict_idx = frames.index(evicted)
                frames[evict_idx] = page

        last_used[page] = step_idx
        history.append(PageReplacementStep(
            step=step_idx + 1,
            page=page,
            frames_snapshot=list(frames),
            hit=hit,
            evicted_page=evicted
        ))

    total = len(reference_string)
    return PageReplacementResult(
        algorithm="LRU",
        reference_string=reference_string,
        num_frames=num_frames,
        page_faults=faults,
        page_hits=hits,
        hit_ratio=hits / total,
        fault_ratio=faults / total,
        step_history=history
    )


def page_replace_optimal(reference_string: List[int], num_frames: int) -> PageReplacementResult:
    """Belady's Optimal Page Replacement (OPT)."""
    _validate_page_inputs(reference_string, num_frames)
    logger.info(f"Running Optimal Page Replacement with {num_frames} frames.")

    frames: List[Optional[int]] = [None] * num_frames
    faults = 0
    hits = 0
    history: List[PageReplacementStep] = []
    total = len(reference_string)

    for step_idx, page in enumerate(reference_string):
        evicted = None
        if page in frames:
            hits += 1
            hit = True
        else:
            faults += 1
            hit = False
            if None in frames:
                empty_idx = frames.index(None)
                frames[empty_idx] = page
            else:
                # For each resident page, find its next occurrence in the future
                furthest_use = -1
                evict_candidate = frames[0]

                for resident in frames:
                    try:
                        next_use = reference_string.index(resident, step_idx + 1)
                    except ValueError:
                        next_use = float('inf') # Never used again
                    
                    if next_use > furthest_use:
                        furthest_use = next_use
                        evict_candidate = resident

                evicted = evict_candidate
                evict_idx = frames.index(evicted)
                frames[evict_idx] = page

        history.append(PageReplacementStep(
            step=step_idx + 1,
            page=page,
            frames_snapshot=list(frames),
            hit=hit,
            evicted_page=evicted
        ))

    return PageReplacementResult(
        algorithm="Optimal",
        reference_string=reference_string,
        num_frames=num_frames,
        page_faults=faults,
        page_hits=hits,
        hit_ratio=hits / total,
        fault_ratio=faults / total,
        step_history=history
    )


def page_replace_lfu(reference_string: List[int], num_frames: int) -> PageReplacementResult:
    """Least Frequently Used (LFU) page replacement."""
    _validate_page_inputs(reference_string, num_frames)
    logger.info(f"Running LFU Page Replacement with {num_frames} frames.")

    frames: List[Optional[int]] = [None] * num_frames
    frequency: Dict[int, int] = {}
    arrival_order: Dict[int, int] = {} # Tie-breaker: earlier arrival
    faults = 0
    hits = 0
    history: List[PageReplacementStep] = []
    total = len(reference_string)

    for step_idx, page in enumerate(reference_string):
        evicted = None
        frequency[page] = frequency.get(page, 0) + 1

        if page in frames:
            hits += 1
            hit = True
        else:
            faults += 1
            hit = False
            if None in frames:
                empty_idx = frames.index(None)
                frames[empty_idx] = page
                arrival_order[page] = step_idx
            else:
                # Evict lowest frequency; tie-breaker: oldest arrival
                evicted = min(frames, key=lambda p: (frequency.get(p, 0), arrival_order.get(p, step_idx)))
                evict_idx = frames.index(evicted)
                frames[evict_idx] = page
                arrival_order[page] = step_idx

        history.append(PageReplacementStep(
            step=step_idx + 1,
            page=page,
            frames_snapshot=list(frames),
            hit=hit,
            evicted_page=evicted
        ))

    return PageReplacementResult(
        algorithm="LFU",
        reference_string=reference_string,
        num_frames=num_frames,
        page_faults=faults,
        page_hits=hits,
        hit_ratio=hits / total,
        fault_ratio=faults / total,
        step_history=history
    )


def analyze_beladys_anomaly(reference_string: Optional[List[int]] = None, 
                            min_frames: int = 2, 
                            max_frames: int = 6) -> Dict[str, Any]:
    """
    Demonstrates and checks for Belady's Anomaly where allocating more page frames
    results in more page faults under FIFO.
    Standard reference string: [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    """
    if reference_string is None:
        reference_string = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]

    results: Dict[str, Dict[int, int]] = {
        "FIFO": {},
        "LRU": {},
        "Optimal": {}
    }

    for f in range(min_frames, max_frames + 1):
        results["FIFO"][f] = page_replace_fifo(reference_string, f).page_faults
        results["LRU"][f] = page_replace_lru(reference_string, f).page_faults
        results["Optimal"][f] = page_replace_optimal(reference_string, f).page_faults

    # Detect anomaly in FIFO
    anomaly_detected = False
    anomaly_details = []
    fifo_counts = results["FIFO"]
    for f in range(min_frames, max_frames):
        if fifo_counts[f + 1] > fifo_counts[f]:
            anomaly_detected = True
            msg = f"Belady's Anomaly DETECTED in FIFO: Frame {f} had {fifo_counts[f]} faults, but Frame {f+1} had {fifo_counts[f+1]} faults!"
            anomaly_details.append(msg)
            logger.warning(msg)

    return {
        "reference_string": reference_string,
        "results": results,
        "anomaly_detected": anomaly_detected,
        "details": anomaly_details
    }
