"""
Unit & Boundary Tests for Memory Management Module
Phase 4: Valid, Invalid, Boundary, and Belady Anomaly Verification
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from modules.memory_manager import (
    allocate_contiguous,
    page_replace_fifo,
    page_replace_lru,
    page_replace_optimal,
    page_replace_lfu,
    analyze_beladys_anomaly,
    MemoryValidationError
)


class TestMemoryManager(unittest.TestCase):

    def setUp(self):
        self.blocks = [(1, 100), (2, 500), (3, 200), (4, 300), (5, 600)]
        self.requests = [("P1", 212), ("P2", 417), ("P3", 112), ("P4", 426)]
        self.standard_pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]

    # ------------------ Contiguous Memory Tests ------------------
    def test_first_fit(self):
        res = allocate_contiguous("first_fit", self.blocks, self.requests)
        self.assertEqual(res.allocated_requests["P1"], 2) # Block 2 (500) fits 212
        self.assertEqual(res.allocated_requests["P2"], 5) # Block 5 (600) fits 417
        self.assertEqual(res.allocated_requests["P3"], 3) # Block 3 (200) fits 112
        # P4 needs 426; remaining blocks: 1 (100), 4 (300). None fits 426!
        self.assertIn(("P4", 426), res.unallocated_requests)

    def test_best_fit(self):
        res = allocate_contiguous("best_fit", self.blocks, self.requests)
        # P1 (212) -> Block 4 (300)
        self.assertEqual(res.allocated_requests["P1"], 4)
        # P2 (417) -> Block 2 (500)
        self.assertEqual(res.allocated_requests["P2"], 2)
        # P3 (112) -> Block 3 (200)
        self.assertEqual(res.allocated_requests["P3"], 3)
        # P4 (426) -> Block 5 (600)
        self.assertEqual(res.allocated_requests["P4"], 5)
        self.assertEqual(len(res.unallocated_requests), 0)

    def test_worst_fit(self):
        res = allocate_contiguous("worst_fit", self.blocks, self.requests)
        # P1 (212) -> largest block 5 (600)
        self.assertEqual(res.allocated_requests["P1"], 5)
        # P2 (417) -> next largest block 2 (500)
        self.assertEqual(res.allocated_requests["P2"], 2)

    # ------------------ Page Replacement Tests ------------------
    def test_fifo_page_faults(self):
        res = page_replace_fifo(self.standard_pages, num_frames=3)
        self.assertEqual(res.page_faults, 15)

    def test_lru_page_faults(self):
        res = page_replace_lru(self.standard_pages, num_frames=3)
        self.assertEqual(res.page_faults, 12)

    def test_optimal_page_faults(self):
        res = page_replace_optimal(self.standard_pages, num_frames=3)
        self.assertEqual(res.page_faults, 9)

    def test_beladys_anomaly_detection(self):
        # On [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5], FIFO faults: Frame 3 = 9 faults, Frame 4 = 10 faults!
        anomaly_data = analyze_beladys_anomaly()
        self.assertTrue(anomaly_data["anomaly_detected"])
        self.assertEqual(anomaly_data["results"]["FIFO"][3], 9)
        self.assertEqual(anomaly_data["results"]["FIFO"][4], 10)

    # ------------------ Boundary & Invalid Tests ------------------
    def test_single_frame(self):
        res = page_replace_fifo([1, 2, 1, 2], num_frames=1)
        self.assertEqual(res.page_faults, 4)

    def test_zero_frames_raises_error(self):
        with self.assertRaises(MemoryValidationError):
            page_replace_fifo([1, 2, 3], num_frames=0)

    def test_empty_reference_string_raises_error(self):
        with self.assertRaises(MemoryValidationError):
            page_replace_lru([], num_frames=3)

    def test_negative_block_size(self):
        with self.assertRaises(MemoryValidationError):
            allocate_contiguous("first_fit", [(1, -100)], [("P1", 50)])

    def test_invalid_allocation_strategy(self):
        with self.assertRaises(MemoryValidationError):
            allocate_contiguous("magic_fit", self.blocks, self.requests)


if __name__ == '__main__':
    unittest.main()
