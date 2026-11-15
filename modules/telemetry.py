"""
System Telemetry & Real OS Resource Management Bridge
Executes Bash scripts to capture live kernel metrics (Linux /proc or psutil fallback)
and contrasts real OS metrics with simulator models.
"""

import subprocess
import json
import shutil
import platform
from typing import Dict, Any, Optional
from pathlib import Path
from config import BASE_DIR, logger

class TelemetryCollector:
    """Collects real operating system resource management data via Bash integration."""

    @staticmethod
    def collect_live_metrics() -> Dict[str, Any]:
        """Runs scripts/sys_telemetry.sh via Bash; falls back to psutil if bash fails."""
        script_path = BASE_DIR / "scripts" / "sys_telemetry.sh"
        bash_path = shutil.which("bash")

        if script_path.exists():
            # Check for WSL on Windows or native bash on Linux/macOS
            cmd = None
            if platform.system() == "Windows" and shutil.which("wsl"):
                cmd = ["wsl", "-e", "bash", "-c"]
            elif shutil.which("bash"):
                cmd = ["bash", "-c"]

            if cmd:
                try:
                    with open(script_path, "r", encoding="utf-8") as f:
                        script_content = f.read()
                    
                    result = subprocess.run(
                        cmd + [script_content],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=True
                    )
                    data = json.loads(result.stdout)
                    data["source"] = f"Bash Subprocess ({'WSL' if 'wsl' in cmd[0] else 'Native'} / scripts/sys_telemetry.sh)"
                    logger.info("Successfully gathered live telemetry via Bash script.")
                    return data
                except Exception as e:
                    logger.warning(f"Bash telemetry script notice ({e}). Falling back to psutil.")

        # Fallback to psutil
        return TelemetryCollector._psutil_fallback()

    @staticmethod
    def _psutil_fallback() -> Dict[str, Any]:
        """Provides native Python psutil collection if bash /proc is not available."""
        import psutil

        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_io_counters()

        # Load average / CPU
        try:
            load_1, load_5, _ = psutil.getloadavg()
        except (AttributeError, OSError):
            load_1 = psutil.cpu_percent(interval=0.1) / 100.0
            load_5 = load_1

        return {
            "source": "Python psutil Native Collector",
            "system": {
                "os": platform.system(),
                "kernel": platform.release()
            },
            "cpu": {
                "load_avg_1m": round(load_1, 2),
                "load_avg_5m": round(load_5, 2),
                "runnable_threads": len(psutil.pids()),
                "total_threads": sum(p.num_threads() for p in psutil.process_iter(['num_threads']) if p.info.get('num_threads'))
            },
            "memory": {
                "total_kb": mem.total // 1024,
                "free_kb": mem.free // 1024,
                "available_kb": mem.available // 1024,
                "active_pages_kb": getattr(mem, 'active', mem.used) // 1024,
                "inactive_pages_kb": getattr(mem, 'inactive', 0) // 1024,
                "swap_total_kb": swap.total // 1024,
                "swap_free_kb": swap.free // 1024
            },
            "storage": {
                "reads_completed": disk.read_count if disk else 0,
                "writes_completed": disk.write_count if disk else 0,
                "io_in_progress": 0
            }
        }

    @staticmethod
    def format_comparison_summary() -> str:
        """Formats an analytical comparison between Simulated Models vs Live OS."""
        metrics = TelemetryCollector.collect_live_metrics()
        source = metrics.get('source', 'Unknown')
        os_info = f"{metrics['system']['os']} {metrics['system']['kernel']}"
        cpu_runnable = metrics['cpu']['runnable_threads']
        cpu_threads = metrics['cpu']['total_threads']
        load_1m = metrics['cpu']['load_avg_1m']
        avail_mb = metrics['memory']['available_kb'] // 1024
        swap_used_mb = (metrics['memory']['swap_total_kb'] - metrics['memory']['swap_free_kb']) // 1024
        reads = metrics['storage']['reads_completed']
        writes = metrics['storage']['writes_completed']

        lines = [
            "=" * 75,
            f"LIVE OS TELEMETRY & SIMULATOR ARCHITECTURE COMPARISON",
            f"Source: {source} | Host OS: {os_info}",
            "=" * 75,
            f"{'Subsystem':<20} {'Simulated Metric':<25} {'Live OS Counter':<25}",
            "-" * 75,
            f"{'CPU Scheduling':<20} {'Burst/Quantum Time':<25} {f'Active PIDs: {cpu_runnable}, Threads: {cpu_threads}':<25}",
            f"{'':<20} {'Turnaround/Wait Time':<25} {f'Load Avg (1m): {load_1m}':<25}",
            f"{'Memory Paging':<20} {'Page Hits/Faults (FIFO/LRU)':<25} {f'Available: {avail_mb} MB':<25}",
            f"{'':<20} {'Belady Anomaly Detection':<25} {f'Swap Used: {swap_used_mb} MB':<25}",
            f"{'Disk Scheduling':<20} {'Cylinder Seek Distance':<25} {f'Reads: {reads}, Writes: {writes}':<25}",
            f"{'Deadlock Mgmt':<20} {'Banker Safety / RAG Cycles':<25} {'Kernel Lock/Mutex Semaphores':<25}",
            "=" * 75
        ]
        return "\n".join(lines)
