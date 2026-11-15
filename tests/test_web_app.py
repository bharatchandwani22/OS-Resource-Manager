"""
Unit Tests for Flask Web Application & REST APIs
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import json
from web.app import app


class TestWebApp(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_index_route(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"OS Resource Management Simulator", res.data)

    def test_cpu_simulation_api(self):
        payload = {
            "algorithm": "srtf",
            "quantum": 2,
            "processes": [
                {"pid": "P1", "arrival_time": 0, "burst_time": 4, "priority": 1},
                {"pid": "P2", "arrival_time": 1, "burst_time": 2, "priority": 2}
            ]
        }
        res = self.client.post("/api/cpu/simulate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["total_time"], 6)

    def test_memory_paging_api(self):
        payload = {
            "algorithm": "lru",
            "frames": 3,
            "reference_string": [7, 0, 1, 2, 0, 3]
        }
        res = self.client.post("/api/memory/paging", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["page_faults"], 0)

    def test_deadlock_safety_api(self):
        payload = {
            "process_ids": ["P1", "P2"],
            "resource_ids": ["A"],
            "available": [2],
            "max_matrix": [[2], [1]],
            "allocation_matrix": [[1], [0]]
        }
        res = self.client.post("/api/deadlock/safety", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["is_safe"])

    def test_storage_simulation_api(self):
        payload = {
            "algorithm": "sstf",
            "requests": [50, 20, 80],
            "initial_head": 45,
            "disk_size": 200
        }
        res = self.client.post("/api/storage/simulate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["traversal_order"][0], 45)

    def test_telemetry_api(self):
        res = self.client.get("/api/telemetry")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("metrics", data)


if __name__ == '__main__':
    unittest.main()
