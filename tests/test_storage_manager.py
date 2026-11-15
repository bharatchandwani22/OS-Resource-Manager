"""
Unit & Boundary Tests for Storage / Disk Scheduling Module
Phase 4: FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK and Boundary Verifications
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from modules.storage_manager import (
    disk_fcfs,
    disk_sstf,
    disk_scan,
    disk_c_scan,
    disk_look,
    disk_c_look,
    StorageValidationError
)


class TestStorageManager(unittest.TestCase):

    def setUp(self):
        # Classic textbook example: initial head = 53, disk size = 200
        self.requests = [98, 183, 37, 122, 14, 124, 65, 67]
        self.initial_head = 53

    # ------------------ Valid Tests ------------------
    def test_disk_fcfs(self):
        res = disk_fcfs(self.requests, self.initial_head)
        self.assertEqual(res.traversal_order, [53, 98, 183, 37, 122, 14, 124, 65, 67])
        self.assertEqual(res.total_head_movement, 640)

    def test_disk_sstf(self):
        res = disk_sstf(self.requests, self.initial_head)
        # From 53 -> 65 -> 67 -> 37 -> 14 -> 98 -> 122 -> 124 -> 183
        self.assertEqual(res.traversal_order, [53, 65, 67, 37, 14, 98, 122, 124, 183])
        self.assertEqual(res.total_head_movement, 236)

    def test_disk_scan_up(self):
        res = disk_scan(self.requests, self.initial_head, disk_size=200, direction="up")
        # Head moves up: 53 -> 65 -> 67 -> 98 -> 122 -> 124 -> 183 -> 199 (boundary) -> 37 -> 14
        self.assertEqual(res.traversal_order, [53, 65, 67, 98, 122, 124, 183, 199, 37, 14])
        self.assertEqual(res.total_head_movement, (199 - 53) + (199 - 14)) # 146 + 185 = 331

    def test_disk_c_scan(self):
        res = disk_c_scan(self.requests, self.initial_head, disk_size=200)
        # 53 -> 65 -> 67 -> 98 -> 122 -> 124 -> 183 -> 199 -> 0 -> 14 -> 37
        self.assertEqual(res.traversal_order, [53, 65, 67, 98, 122, 124, 183, 199, 0, 14, 37])
        self.assertEqual(res.total_head_movement, (199 - 53) + 199 + 37) # 146 + 199 + 37 = 382

    def test_disk_look_up(self):
        res = disk_look(self.requests, self.initial_head, disk_size=200, direction="up")
        # Up to max request (183) without hitting 199, then reverse down to 14
        self.assertEqual(res.traversal_order, [53, 65, 67, 98, 122, 124, 183, 37, 14])
        self.assertEqual(res.total_head_movement, (183 - 53) + (183 - 14)) # 130 + 169 = 299

    def test_disk_c_look(self):
        res = disk_c_look(self.requests, self.initial_head, disk_size=200)
        # 53 -> 65 -> 67 -> 98 -> 122 -> 124 -> 183 -> jumps to 14 -> 37
        self.assertEqual(res.traversal_order, [53, 65, 67, 98, 122, 124, 183, 14, 37])
        self.assertEqual(res.total_head_movement, (183 - 53) + (183 - 14) + (37 - 14)) # 130 + 169 + 23 = 322

    # ------------------ Boundary & Invalid Tests ------------------
    def test_empty_requests(self):
        with self.assertRaises(StorageValidationError):
            disk_fcfs([], initial_head=50)

    def test_head_out_of_bounds(self):
        with self.assertRaises(StorageValidationError):
            disk_fcfs([50, 60], initial_head=250, disk_size=200)

    def test_request_out_of_bounds(self):
        with self.assertRaises(StorageValidationError):
            disk_fcfs([50, 201], initial_head=50, disk_size=200)

    def test_invalid_direction(self):
        with self.assertRaises(StorageValidationError):
            disk_scan(self.requests, self.initial_head, direction="sideways")


if __name__ == '__main__':
    unittest.main()
