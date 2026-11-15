"""
Unit & Boundary Tests for Process Scheduling Module
Phase 4: Valid, Invalid, and Boundary Verification
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from modules.process_scheduler import (
    Process,
    schedule_fcfs,
    schedule_sjf_non_preemptive,
    schedule_srtf,
    schedule_round_robin,
    schedule_priority,
    schedule_mlfq,
    ProcessValidationError
)


class TestProcessScheduler(unittest.TestCase):

    def setUp(self):
        self.standard_procs = [
            Process(pid="P1", arrival_time=0, burst_time=4, priority=2),
            Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
            Process(pid="P3", arrival_time=2, burst_time=1, priority=3)
        ]

    # ------------------ Valid Tests ------------------
    def test_fcfs_execution(self):
        res = schedule_fcfs(self.standard_procs)
        self.assertEqual(res.total_time, 8)
        p1 = next(p for p in res.processes if p.pid == "P1")
        p2 = next(p for p in res.processes if p.pid == "P2")
        p3 = next(p for p in res.processes if p.pid == "P3")
        self.assertEqual(p1.completion_time, 4)
        self.assertEqual(p2.completion_time, 7)
        self.assertEqual(p3.completion_time, 8)
        self.assertEqual(p1.waiting_time, 0)
        self.assertEqual(p2.waiting_time, 3) # arrived at 1, started at 4
        self.assertEqual(p3.waiting_time, 5) # arrived at 2, started at 7

    def test_sjf_non_preemptive(self):
        res = schedule_sjf_non_preemptive(self.standard_procs)
        # At T=0, P1 starts (runs 0-4). At T=4, P2 (burst 3) and P3 (burst 1) are ready.
        # P3 runs next (4-5), then P2 (5-8).
        p3 = next(p for p in res.processes if p.pid == "P3")
        p2 = next(p for p in res.processes if p.pid == "P2")
        self.assertEqual(p3.completion_time, 5)
        self.assertEqual(p2.completion_time, 8)

    def test_srtf_preemptive(self):
        # P1 arrives 0, burst 4. At T=1, P2 arrives with burst 3 < remaining 3 -> preemption!
        # At T=2, P3 arrives with burst 1 < P2 remaining 2 -> preemption!
        res = schedule_srtf(self.standard_procs)
        p3 = next(p for p in res.processes if p.pid == "P3")
        self.assertEqual(p3.completion_time, 3) # runs 2 to 3

    def test_round_robin(self):
        res = schedule_round_robin(self.standard_procs, quantum=2)
        self.assertEqual(res.total_time, 8)
        self.assertAlmostEqual(res.cpu_utilization, 100.0)

    def test_mlfq_execution(self):
        res = schedule_mlfq(self.standard_procs, q0_quantum=2, q1_quantum=4)
        self.assertEqual(res.total_time, 8)
        self.assertEqual(len(res.processes), 3)

    # ------------------ Boundary Tests ------------------
    def test_single_process(self):
        solo = [Process(pid="P1", arrival_time=5, burst_time=10)]
        res = schedule_fcfs(solo)
        self.assertEqual(res.total_time, 15)
        p = res.processes[0]
        self.assertEqual(p.start_time, 5)
        self.assertEqual(p.completion_time, 15)
        self.assertEqual(p.waiting_time, 0)

    def test_simultaneous_arrival(self):
        procs = [
            Process(pid="P1", arrival_time=0, burst_time=5),
            Process(pid="P2", arrival_time=0, burst_time=2)
        ]
        res = schedule_sjf_non_preemptive(procs)
        p2 = next(p for p in res.processes if p.pid == "P2")
        self.assertEqual(p2.start_time, 0) # P2 has smaller burst

    # ------------------ Invalid Tests ------------------
    def test_empty_process_list(self):
        with self.assertRaises(ProcessValidationError):
            schedule_fcfs([])

    def test_negative_burst_time(self):
        with self.assertRaises(ProcessValidationError):
            schedule_fcfs([Process(pid="P1", arrival_time=0, burst_time=-4)])

    def test_negative_arrival_time(self):
        with self.assertRaises(ProcessValidationError):
            schedule_fcfs([Process(pid="P1", arrival_time=-1, burst_time=4)])

    def test_duplicate_pid(self):
        with self.assertRaises(ProcessValidationError):
            schedule_fcfs([
                Process(pid="P1", arrival_time=0, burst_time=4),
                Process(pid="P1", arrival_time=1, burst_time=2)
            ])

    def test_invalid_rr_quantum(self):
        with self.assertRaises(ProcessValidationError):
            schedule_round_robin(self.standard_procs, quantum=0)


if __name__ == '__main__':
    unittest.main()
