"""
Comprehensive Validation & Robustness Test Suite
Phase 4: Verification of activity logging, malformed payloads, and edge cases.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import json
import logging
from pathlib import Path

from config import LOG_FILE, DATA_DIR, logger
from modules.process_scheduler import Process, schedule_fcfs, ProcessValidationError
from modules.memory_manager import allocate_contiguous, MemoryValidationError
from modules.deadlock_manager import BankersState, DeadlockValidationError
from modules.storage_manager import disk_fcfs, StorageValidationError


class TestValidationAndEdgeCases(unittest.TestCase):

    def test_activity_logging_records_events(self):
        """Verifies that operations write timestamped trace logs into os_simulator.log."""
        logger.info("TEST_MARKER: Activity logging verification test.")
        
        # Run an operation
        p = [Process(pid="LogTest", arrival_time=0, burst_time=2)]
        schedule_fcfs(p)
        
        self.assertTrue(LOG_FILE.exists())
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("TEST_MARKER", content)
            self.assertIn("Starting FCFS scheduling simulation", content)

    def test_json_workloads_loading(self):
        """Verifies that all pre-packaged data JSON files are valid and loadable."""
        json_files = list(DATA_DIR.glob("*.json"))
        self.assertGreaterEqual(len(json_files), 4)
        for jf in json_files:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertIsInstance(data, dict)

    def test_zero_burst_rejection(self):
        """Processes with burst time == 0 must be rejected."""
        with self.assertRaises(ProcessValidationError):
            schedule_fcfs([Process(pid="Zero", arrival_time=0, burst_time=0)])

    def test_negative_memory_request(self):
        """Memory requests with negative sizes must be rejected."""
        with self.assertRaises(MemoryValidationError):
            allocate_contiguous("first_fit", [(1, 100)], [("P1", -50)])

    def test_extreme_cylinder_requests(self):
        """Cylinder boundary cases (0 and disk_size - 1) must be handled gracefully."""
        res = disk_fcfs([0, 199], initial_head=0, disk_size=200)
        self.assertEqual(res.traversal_order, [0, 0, 199])
        self.assertEqual(res.total_head_movement, 199)


if __name__ == '__main__':
    unittest.main()
