"""
Storage / Disk Scheduling Module
Implements:
1. FCFS (First-Come, First-Served)
2. SSTF (Shortest Seek Time First)
3. SCAN (Elevator Algorithm)
4. C-SCAN (Circular SCAN)
5. LOOK
6. C-LOOK
Calculates Total Head Movement, Average Seek Distance, and Step-by-Step Traversal Traces.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
import copy
from config import logger

class StorageValidationError(ValueError):
    """Custom exception raised for invalid disk parameters or out-of-bound requests."""
    pass


@dataclass
class DiskSchedulingResult:
    algorithm: str
    initial_head: int
    requests: List[int]
    traversal_order: List[int]
    seek_steps: List[Tuple[int, int, int]] # (from_cyl, to_cyl, distance)
    total_head_movement: int
    average_seek_distance: float
    direction: Optional[str] = None

    def summary_table(self) -> str:
        lines = [
            f"Disk Scheduling Algorithm: {self.algorithm}",
            f"Initial Head Position:     {self.initial_head}",
            f"Disk Request Queue:        {self.requests}",
            f"Head Traversal Sequence:   {' -> '.join(map(str, self.traversal_order))}",
            "-" * 65,
            f"{'Step':<6} {'From Cylinder':<16} {'To Cylinder':<16} {'Head Movement':<15}",
            "-" * 65
        ]
        for idx, (f_cyl, t_cyl, dist) in enumerate(self.seek_steps, 1):
            lines.append(f"{idx:<6} {f_cyl:<16} {t_cyl:<16} {dist:<15}")
        lines.append("-" * 65)
        lines.append(f"Total Head Movement:       {self.total_head_movement} cylinders")
        lines.append(f"Average Seek Distance:     {self.average_seek_distance:.2f} cylinders")
        return "\n".join(lines)


def _validate_disk_inputs(requests: List[int], initial_head: int, disk_size: int = 200):
    if not requests:
        raise StorageValidationError("Disk request queue cannot be empty.")
    if disk_size <= 0:
        raise StorageValidationError(f"Disk size must be > 0. Got {disk_size}.")
    if not (0 <= initial_head < disk_size):
        raise StorageValidationError(f"Initial head position {initial_head} out of range [0, {disk_size - 1}].")
    for r in requests:
        if not isinstance(r, int) or not (0 <= r < disk_size):
            raise StorageValidationError(f"Disk request {r} out of valid cylinder range [0, {disk_size - 1}].")


def _compute_steps(traversal: List[int]) -> Tuple[List[Tuple[int, int, int]], int, float]:
    seek_steps = []
    total_movement = 0
    for i in range(len(traversal) - 1):
        f = traversal[i]
        t = traversal[i + 1]
        dist = abs(t - f)
        seek_steps.append((f, t, dist))
        total_movement += dist
    
    num_transitions = len(seek_steps)
    avg_seek = (total_movement / num_transitions) if num_transitions > 0 else 0.0
    return seek_steps, total_movement, avg_seek


def disk_fcfs(requests: List[int], initial_head: int, disk_size: int = 200) -> DiskSchedulingResult:
    """First-Come, First-Served (FCFS) disk scheduling."""
    _validate_disk_inputs(requests, initial_head, disk_size)
    logger.info("Executing Disk FCFS algorithm.")

    traversal = [initial_head] + list(requests)
    steps, total_move, avg_seek = _compute_steps(traversal)

    return DiskSchedulingResult(
        algorithm="FCFS",
        initial_head=initial_head,
        requests=requests,
        traversal_order=traversal,
        seek_steps=steps,
        total_head_movement=total_move,
        average_seek_distance=avg_seek
    )


def disk_sstf(requests: List[int], initial_head: int, disk_size: int = 200) -> DiskSchedulingResult:
    """Shortest Seek Time First (SSTF) disk scheduling."""
    _validate_disk_inputs(requests, initial_head, disk_size)
    logger.info("Executing Disk SSTF algorithm.")

    remaining = list(requests)
    current_head = initial_head
    traversal = [current_head]

    while remaining:
        # Pick cylinder closest to current head
        closest = min(remaining, key=lambda c: (abs(c - current_head), c))
        traversal.append(closest)
        remaining.remove(closest)
        current_head = closest

    steps, total_move, avg_seek = _compute_steps(traversal)
    return DiskSchedulingResult(
        algorithm="SSTF",
        initial_head=initial_head,
        requests=requests,
        traversal_order=traversal,
        seek_steps=steps,
        total_head_movement=total_move,
        average_seek_distance=avg_seek
    )


def disk_scan(requests: List[int], initial_head: int, disk_size: int = 200, direction: str = "up") -> DiskSchedulingResult:
    """
    SCAN (Elevator Algorithm):
    Moves in current direction towards boundary (disk_size - 1 or 0), servicing requests,
    then reverses direction.
    """
    _validate_disk_inputs(requests, initial_head, disk_size)
    direction = direction.lower()
    if direction not in ["up", "down"]:
        raise StorageValidationError(f"Invalid direction '{direction}'. Must be 'up' or 'down'.")

    logger.info(f"Executing Disk SCAN algorithm (direction={direction}).")

    left = sorted([r for r in requests if r < initial_head])
    right = sorted([r for r in requests if r >= initial_head])

    traversal = [initial_head]
    if direction == "up":
        traversal.extend(right)
        if left: # Head hits the disk boundary before reversing
            traversal.append(disk_size - 1)
            traversal.extend(reversed(left))
    else:
        traversal.extend(reversed(left))
        if right:
            traversal.append(0)
            traversal.extend(right)

    steps, total_move, avg_seek = _compute_steps(traversal)
    return DiskSchedulingResult(
        algorithm=f"SCAN ({direction.upper()})",
        initial_head=initial_head,
        requests=requests,
        traversal_order=traversal,
        seek_steps=steps,
        total_head_movement=total_move,
        average_seek_distance=avg_seek,
        direction=direction
    )


def disk_c_scan(requests: List[int], initial_head: int, disk_size: int = 200) -> DiskSchedulingResult:
    """
    C-SCAN (Circular SCAN):
    Services requests moving towards high end (disk_size - 1), jumps immediately to 0
    without servicing requests on return, and services remaining upward.
    """
    _validate_disk_inputs(requests, initial_head, disk_size)
    logger.info("Executing Disk C-SCAN algorithm.")

    left = sorted([r for r in requests if r < initial_head])
    right = sorted([r for r in requests if r >= initial_head])

    traversal = [initial_head]
    traversal.extend(right)
    if left:
        traversal.append(disk_size - 1)
        traversal.append(0)
        traversal.extend(left)

    steps, total_move, avg_seek = _compute_steps(traversal)
    return DiskSchedulingResult(
        algorithm="C-SCAN",
        initial_head=initial_head,
        requests=requests,
        traversal_order=traversal,
        seek_steps=steps,
        total_head_movement=total_move,
        average_seek_distance=avg_seek,
        direction="up"
    )


def disk_look(requests: List[int], initial_head: int, disk_size: int = 200, direction: str = "up") -> DiskSchedulingResult:
    """
    LOOK Algorithm:
    Similar to SCAN, but only travels as far as the final request in each direction,
    without going all the way to cylinder 0 or (disk_size - 1).
    """
    _validate_disk_inputs(requests, initial_head, disk_size)
    direction = direction.lower()
    if direction not in ["up", "down"]:
        raise StorageValidationError(f"Invalid direction '{direction}'. Must be 'up' or 'down'.")

    logger.info(f"Executing Disk LOOK algorithm (direction={direction}).")

    left = sorted([r for r in requests if r < initial_head])
    right = sorted([r for r in requests if r >= initial_head])

    traversal = [initial_head]
    if direction == "up":
        traversal.extend(right)
        traversal.extend(reversed(left))
    else:
        traversal.extend(reversed(left))
        traversal.extend(right)

    steps, total_move, avg_seek = _compute_steps(traversal)
    return DiskSchedulingResult(
        algorithm=f"LOOK ({direction.upper()})",
        initial_head=initial_head,
        requests=requests,
        traversal_order=traversal,
        seek_steps=steps,
        total_head_movement=total_move,
        average_seek_distance=avg_seek,
        direction=direction
    )


def disk_c_look(requests: List[int], initial_head: int, disk_size: int = 200) -> DiskSchedulingResult:
    """
    C-LOOK Algorithm:
    Services requests towards high end up to maximum request, then jumps directly
    to the lowest request without visiting boundaries, and continues upward.
    """
    _validate_disk_inputs(requests, initial_head, disk_size)
    logger.info("Executing Disk C-LOOK algorithm.")

    left = sorted([r for r in requests if r < initial_head])
    right = sorted([r for r in requests if r >= initial_head])

    traversal = [initial_head]
    traversal.extend(right)
    traversal.extend(left)

    steps, total_move, avg_seek = _compute_steps(traversal)
    return DiskSchedulingResult(
        algorithm="C-LOOK",
        initial_head=initial_head,
        requests=requests,
        traversal_order=traversal,
        seek_steps=steps,
        total_head_movement=total_move,
        average_seek_distance=avg_seek,
        direction="up"
    )
