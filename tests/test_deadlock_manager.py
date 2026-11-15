"""
Unit & Boundary Tests for Deadlock Management Module
Phase 4: Banker's Safety, Resource-Request, RAG Cycle Detection, and Recovery
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from modules.deadlock_manager import (
    BankersState,
    check_bankers_safety,
    request_resources,
    ResourceAllocationGraph,
    detect_deadlock_multi_instance,
    DeadlockValidationError
)


class TestDeadlockManager(unittest.TestCase):

    def setUp(self):
        self.pids = ["P0", "P1", "P2", "P3", "P4"]
        self.rids = ["A", "B", "C"]
        self.avail = [3, 3, 2]
        self.max_mat = [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3]
        ]
        self.alloc_mat = [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2]
        ]
        self.state = BankersState(
            process_ids=self.pids,
            resource_ids=self.rids,
            available=self.avail,
            max_matrix=self.max_mat,
            allocation_matrix=self.alloc_mat
        )

    # ------------------ Banker's Safety Tests ------------------
    def test_bankers_safety_standard(self):
        result = check_bankers_safety(self.state)
        self.assertTrue(result.is_safe)
        self.assertEqual(len(result.safe_sequence), 5)
        # Safe sequence must be a valid permutation
        self.assertEqual(set(result.safe_sequence), set(self.pids))

    def test_bankers_safe_request(self):
        # P1 requests [1, 0, 2] -> should be granted safely
        granted, msg, res = request_resources(self.state, "P1", [1, 0, 2])
        self.assertTrue(granted)
        self.assertIsNotNone(res)
        self.assertTrue(res.is_safe)

    def test_bankers_unsafe_request(self):
        # Request exceeding Available: P4 requests [3, 3, 0], available is [3, 3, 2]
        # But if allocated, Available becomes [0, 0, 2] which may not satisfy any process
        # P0 requests [0, 2, 0]: available is [3, 3, 2]. P0 Need is [7, 4, 3]. Request <= Need.
        # Check an unsafe request or request exceeding need:
        # P1 requests [2, 3, 0] -> Need is [1, 2, 2] -> 3 exceeds need 2 -> FAILS
        granted, msg, _ = request_resources(self.state, "P1", [2, 3, 0])
        self.assertFalse(granted)
        self.assertIn("exceeding its maximum claim", msg)

    # ------------------ RAG Cycle Detection Tests ------------------
    def test_rag_cycle_detection(self):
        rag = ResourceAllocationGraph()
        # Create cycle: P1 -> R1 -> P2 -> R2 -> P1
        rag.add_request_edge("P1", "R1")
        rag.add_assignment_edge("R1", "P2")
        rag.add_request_edge("P2", "R2")
        rag.add_assignment_edge("R2", "P1")

        result = rag.detect_cycles()
        self.assertTrue(result.has_deadlock_cycle)
        self.assertGreaterEqual(len(result.cycles_detected), 1)

    def test_rag_acyclic_graph(self):
        rag = ResourceAllocationGraph()
        # Acyclic: P1 -> R1 -> P2
        rag.add_request_edge("P1", "R1")
        rag.add_assignment_edge("R1", "P2")
        rag.add_assignment_edge("R2", "P3")

        result = rag.detect_cycles()
        self.assertFalse(result.has_deadlock_cycle)

    # ------------------ Multi-Instance Detection Tests ------------------
    def test_multi_instance_detection_and_victim_selection(self):
        # Case where P1 and P2 are deadlocked
        pids = ["P1", "P2"]
        rids = ["R1", "R2"]
        avail = [0, 0]
        alloc = [[1, 0], [0, 1]]
        req = [[0, 1], [1, 0]]
        costs = {"P1": 10, "P2": 20}

        res = detect_deadlock_multi_instance(pids, rids, avail, alloc, req, costs)
        self.assertTrue(res.is_deadlocked)
        self.assertEqual(set(res.deadlocked_processes), {"P1", "P2"})
        self.assertIn("P1", res.recovery_recommendation) # Lower cost victim

    # ------------------ Boundary & Invalid Tests ------------------
    def test_mismatched_dimensions(self):
        with self.assertRaises(DeadlockValidationError):
            BankersState(
                process_ids=["P1"],
                resource_ids=["A", "B"],
                available=[1], # mismatch!
                max_matrix=[[2, 2]],
                allocation_matrix=[[1, 1]]
            )

    def test_allocation_exceeding_max(self):
        with self.assertRaises(DeadlockValidationError):
            BankersState(
                process_ids=["P1"],
                resource_ids=["A"],
                available=[1],
                max_matrix=[[2]],
                allocation_matrix=[[3]] # 3 > 2!
            )


if __name__ == '__main__':
    unittest.main()
