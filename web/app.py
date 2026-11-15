"""
Flask Web Application for OS Resource Management Simulator
Exposes RESTful APIs and serves the interactive browser dashboard.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, request, jsonify, send_from_directory
from typing import List, Dict, Any
import json

from config import DATA_DIR, CHARTS_DIR, TRACES_DIR, logger
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
from modules.memory_manager import (
    allocate_contiguous,
    page_replace_fifo,
    page_replace_lru,
    page_replace_optimal,
    page_replace_lfu,
    analyze_beladys_anomaly,
    MemoryValidationError
)
from modules.deadlock_manager import (
    BankersState,
    check_bankers_safety,
    request_resources,
    ResourceAllocationGraph,
    detect_deadlock_multi_instance,
    DeadlockValidationError
)
from modules.storage_manager import (
    disk_fcfs,
    disk_sstf,
    disk_scan,
    disk_c_scan,
    disk_look,
    disk_c_look,
    StorageValidationError
)
from modules.telemetry import TelemetryCollector
from analysis.comparator import BenchmarkComparator
from analysis.visualizer import (
    plot_cpu_gantt,
    plot_cpu_comparison,
    plot_page_fault_curves,
    plot_disk_trajectories,
    plot_memory_blocks
)

app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "web" / "templates"),
    static_folder=str(PROJECT_ROOT / "web" / "static")
)


@app.route("/")
def index():
    """Serves the main interactive OS Simulator dashboard."""
    return render_template("index.html")


@app.route("/api/charts/<path:filename>")
def serve_chart(filename):
    """Serves generated PNG charts."""
    return send_from_directory(CHARTS_DIR, filename)


# ==============================================================================
# Module 1: CPU Scheduling APIs
# ==============================================================================

@app.route("/api/cpu/simulate", methods=["POST"])
def api_cpu_simulate():
    try:
        data = request.json or {}
        algorithm = data.get("algorithm", "fcfs").lower()
        quantum = int(data.get("quantum", 2))
        raw_procs = data.get("processes", [])

        if not raw_procs:
            return jsonify({"success": False, "error": "Process list cannot be empty."}), 400

        procs = [
            Process(
                pid=str(p["pid"]),
                arrival_time=int(p["arrival_time"]),
                burst_time=int(p["burst_time"]),
                priority=int(p.get("priority", 0))
            )
            for p in raw_procs
        ]

        if algorithm == "fcfs":
            res = schedule_fcfs(procs)
        elif algorithm == "sjf":
            res = schedule_sjf_non_preemptive(procs)
        elif algorithm == "srtf":
            res = schedule_srtf(procs)
        elif algorithm == "rr":
            res = schedule_round_robin(procs, quantum=quantum)
        elif algorithm == "priority_non_preemptive":
            res = schedule_priority(procs, preemptive=False)
        elif algorithm == "priority_preemptive":
            res = schedule_priority(procs, preemptive=True)
        elif algorithm == "mlfq":
            res = schedule_mlfq(procs, q0_quantum=quantum, q1_quantum=quantum * 2)
        else:
            return jsonify({"success": False, "error": f"Unknown algorithm: {algorithm}"}), 400

        # Save Gantt chart for reference
        chart_file = f"web_gantt_{algorithm}.png"
        plot_cpu_gantt(res, chart_file)

        return jsonify({
            "success": True,
            "algorithm": res.algorithm,
            "total_time": res.total_time,
            "cpu_utilization": round(res.cpu_utilization, 2),
            "throughput": round(res.throughput, 4),
            "avg_tat": round(res.avg_turnaround_time, 2),
            "avg_wt": round(res.avg_waiting_time, 2),
            "avg_rt": round(res.avg_response_time, 2),
            "timeline": [{"start": s, "end": e, "pid": pid} for s, e, pid in res.timeline],
            "processes": [p.to_dict() for p in res.processes],
            "traces": res.step_traces,
            "chart_url": f"/api/charts/{chart_file}"
        })
    except Exception as e:
        logger.error(f"CPU simulation error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/cpu/compare", methods=["POST"])
def api_cpu_compare():
    try:
        data = request.json or {}
        raw_procs = data.get("processes", [])
        quantum = int(data.get("quantum", 2))
        if not raw_procs:
            return jsonify({"success": False, "error": "Process list cannot be empty."}), 400

        procs = [
            Process(
                pid=str(p["pid"]),
                arrival_time=int(p["arrival_time"]),
                burst_time=int(p["burst_time"]),
                priority=int(p.get("priority", 0))
            )
            for p in raw_procs
        ]

        df = BenchmarkComparator.compare_cpu_schedulers(procs, rr_quantum=quantum)
        chart_file = "web_cpu_comparison.png"
        plot_cpu_comparison(df, chart_file)

        return jsonify({
            "success": True,
            "comparison": df.to_dict(orient="records"),
            "chart_url": f"/api/charts/{chart_file}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ==============================================================================
# Module 2: Memory Management APIs
# ==============================================================================

@app.route("/api/memory/contiguous", methods=["POST"])
def api_memory_contiguous():
    try:
        data = request.json or {}
        strategy = data.get("strategy", "best_fit")
        blocks = [tuple(b) for b in data.get("blocks", [])]
        requests = [tuple(r) for r in data.get("requests", [])]

        res = allocate_contiguous(strategy, blocks, requests)
        chart_file = f"web_memory_map_{strategy}.png"
        plot_memory_blocks(res, chart_file)

        blocks_out = []
        for b in res.blocks:
            blocks_out.append({
                "block_id": b.block_id,
                "size": b.size,
                "start_address": b.start_address,
                "is_free": b.is_free,
                "allocated_to": b.allocated_to,
                "allocated_size": b.allocated_size,
                "internal_fragmentation": b.internal_fragmentation
            })

        return jsonify({
            "success": True,
            "strategy": res.strategy,
            "total_memory": res.total_memory,
            "allocated_memory": res.allocated_memory,
            "internal_fragmentation": res.internal_fragmentation,
            "external_fragmentation": res.external_fragmentation,
            "allocated_requests": res.allocated_requests,
            "unallocated_requests": res.unallocated_requests,
            "blocks": blocks_out,
            "traces": res.traces,
            "chart_url": f"/api/charts/{chart_file}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/memory/paging", methods=["POST"])
def api_memory_paging():
    try:
        data = request.json or {}
        algorithm = data.get("algorithm", "fifo").lower()
        ref_string = [int(x) for x in data.get("reference_string", [])]
        num_frames = int(data.get("frames", 3))

        if algorithm == "fifo":
            res = page_replace_fifo(ref_string, num_frames)
        elif algorithm == "lru":
            res = page_replace_lru(ref_string, num_frames)
        elif algorithm == "optimal":
            res = page_replace_optimal(ref_string, num_frames)
        elif algorithm == "lfu":
            res = page_replace_lfu(ref_string, num_frames)
        else:
            return jsonify({"success": False, "error": f"Unknown page replacement algorithm: {algorithm}"}), 400

        steps = []
        for s in res.step_history:
            steps.append({
                "step": s.step,
                "page": s.page,
                "frames": s.frames_snapshot,
                "hit": s.hit,
                "evicted": s.evicted_page
            })

        return jsonify({
            "success": True,
            "algorithm": res.algorithm,
            "frames": res.num_frames,
            "page_faults": res.page_faults,
            "page_hits": res.page_hits,
            "fault_ratio": round(res.fault_ratio * 100, 2),
            "hit_ratio": round(res.hit_ratio * 100, 2),
            "steps": steps
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/memory/belady", methods=["POST"])
def api_memory_belady():
    try:
        data = request.json or {}
        ref_string = data.get("reference_string")
        if ref_string:
            ref_string = [int(x) for x in ref_string]

        res = analyze_beladys_anomaly(ref_string)
        df_comp = BenchmarkComparator.compare_page_replacement(res["reference_string"], frame_sizes=[2, 3, 4, 5, 6])
        chart_file = "web_belady_curves.png"
        plot_page_fault_curves(df_comp, chart_file)

        return jsonify({
            "success": True,
            "reference_string": res["reference_string"],
            "results": res["results"],
            "anomaly_detected": res["anomaly_detected"],
            "details": res["details"],
            "chart_url": f"/api/charts/{chart_file}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ==============================================================================
# Module 3: Deadlock Management APIs
# ==============================================================================

@app.route("/api/deadlock/safety", methods=["POST"])
def api_deadlock_safety():
    try:
        data = request.json or {}
        state = BankersState(
            process_ids=data["process_ids"],
            resource_ids=data["resource_ids"],
            available=[int(x) for x in data["available"]],
            max_matrix=[[int(c) for c in row] for row in data["max_matrix"]],
            allocation_matrix=[[int(c) for c in row] for row in data["allocation_matrix"]]
        )

        res = check_bankers_safety(state)
        return jsonify({
            "success": True,
            "is_safe": res.is_safe,
            "safe_sequence": res.safe_sequence,
            "need_matrix": state.need_matrix,
            "traces": res.traces,
            "work_snapshots": res.work_snapshots
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/deadlock/request", methods=["POST"])
def api_deadlock_request():
    try:
        data = request.json or {}
        state = BankersState(
            process_ids=data["process_ids"],
            resource_ids=data["resource_ids"],
            available=[int(x) for x in data["available"]],
            max_matrix=[[int(c) for c in row] for row in data["max_matrix"]],
            allocation_matrix=[[int(c) for c in row] for row in data["allocation_matrix"]]
        )
        pid = str(data["request_pid"])
        req_vec = [int(x) for x in data["request_vector"]]

        granted, msg, safety_res = request_resources(state, pid, req_vec)
        return jsonify({
            "success": True,
            "granted": granted,
            "message": msg,
            "safe_sequence": safety_res.safe_sequence if safety_res and safety_res.is_safe else []
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/deadlock/rag", methods=["POST"])
def api_deadlock_rag():
    try:
        data = request.json or {}
        rag = ResourceAllocationGraph()
        for p, r in data.get("request_edges", []):
            rag.add_request_edge(p, r)
        for r, p in data.get("assignment_edges", []):
            rag.add_assignment_edge(r, p)

        res = rag.detect_cycles()
        return jsonify({
            "success": True,
            "has_deadlock": res.has_deadlock_cycle,
            "cycles": res.cycles_detected,
            "summary": res.graph_summary
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/deadlock/detect", methods=["POST"])
def api_deadlock_detect():
    try:
        data = request.json or {}
        res = detect_deadlock_multi_instance(
            process_ids=data["process_ids"],
            resource_ids=data["resource_ids"],
            available=[int(x) for x in data["available"]],
            allocation=[[int(c) for c in row] for row in data["allocation"]],
            request_matrix=[[int(c) for c in row] for row in data["request"]],
            process_costs=data.get("costs")
        )
        return jsonify({
            "success": True,
            "is_deadlocked": res.is_deadlocked,
            "deadlocked_processes": res.deadlocked_processes,
            "recovery_recommendation": res.recovery_recommendation,
            "traces": res.traces
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ==============================================================================
# Module 4: Storage / Disk Scheduling APIs
# ==============================================================================

@app.route("/api/storage/simulate", methods=["POST"])
def api_storage_simulate():
    try:
        data = request.json or {}
        algorithm = data.get("algorithm", "fcfs").lower()
        requests = [int(x) for x in data.get("requests", [])]
        initial_head = int(data.get("initial_head", 53))
        disk_size = int(data.get("disk_size", 200))
        direction = data.get("direction", "up").lower()

        if algorithm == "fcfs":
            res = disk_fcfs(requests, initial_head, disk_size)
        elif algorithm == "sstf":
            res = disk_sstf(requests, initial_head, disk_size)
        elif algorithm == "scan":
            res = disk_scan(requests, initial_head, disk_size, direction=direction)
        elif algorithm == "c_scan":
            res = disk_c_scan(requests, initial_head, disk_size)
        elif algorithm == "look":
            res = disk_look(requests, initial_head, disk_size, direction=direction)
        elif algorithm == "c_look":
            res = disk_c_look(requests, initial_head, disk_size)
        else:
            return jsonify({"success": False, "error": f"Unknown disk algorithm: {algorithm}"}), 400

        # Also run all for comparison trajectory chart
        all_results = [
            disk_fcfs(requests, initial_head, disk_size),
            disk_sstf(requests, initial_head, disk_size),
            disk_scan(requests, initial_head, disk_size, direction=direction),
            disk_c_scan(requests, initial_head, disk_size),
            disk_look(requests, initial_head, disk_size, direction=direction),
            disk_c_look(requests, initial_head, disk_size)
        ]
        chart_file = "web_disk_trajectories.png"
        plot_disk_trajectories(all_results, chart_file)

        return jsonify({
            "success": True,
            "algorithm": res.algorithm,
            "initial_head": res.initial_head,
            "total_head_movement": res.total_head_movement,
            "average_seek_distance": round(res.average_seek_distance, 2),
            "traversal_order": res.traversal_order,
            "seek_steps": [{"from": f, "to": t, "distance": d} for f, t, d in res.seek_steps],
            "chart_url": f"/api/charts/{chart_file}",
            "all_comparisons": [
                {
                    "algorithm": r.algorithm,
                    "total_movement": r.total_head_movement,
                    "avg_seek": round(r.average_seek_distance, 2)
                }
                for r in sorted(all_results, key=lambda x: x.total_head_movement)
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ==============================================================================
# Module 5: Real OS Telemetry API
# ==============================================================================

@app.route("/api/telemetry", methods=["GET"])
def api_telemetry():
    try:
        metrics = TelemetryCollector.collect_live_metrics()
        return jsonify({
            "success": True,
            "metrics": metrics
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==============================================================================
# Presets API
# ==============================================================================

@app.route("/api/presets/<name>", methods=["GET"])
def api_presets(name):
    try:
        file_map = {
            "processes": "processes_sample.json",
            "memory": "memory_sample.json",
            "deadlock": "deadlock_sample.json",
            "storage": "storage_sample.json"
        }
        if name not in file_map:
            return jsonify({"success": False, "error": f"Unknown preset: {name}"}), 404

        file_path = DATA_DIR / file_map[name]
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def run_server(port: int = 5000, host: str = "127.0.0.1", debug: bool = False):
    """Runs the Flask web server."""
    logger.info(f"Starting OS Simulator Web Application on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(port=5000, debug=True)
