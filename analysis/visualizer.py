"""
Visualizer Module
Generates high-resolution analytical charts using Matplotlib:
1. CPU Scheduling Gantt Charts
2. CPU Scheduling Multi-Algorithm Comparative Bar Charts
3. Page Replacement Faults vs Frames Curve (Highlighting Belady's Anomaly)
4. Disk Head Trajectory Curves
5. Memory Block Allocation Physical Map
"""

import matplotlib
matplotlib.use('Agg')  # Headless backend for terminal / server execution
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

from config import CHARTS_DIR, logger
from modules.process_scheduler import SchedulingResult
from modules.storage_manager import DiskSchedulingResult
from modules.memory_manager import ContiguousAllocationResult

# Set clean aesthetic style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8


def plot_cpu_gantt(result: SchedulingResult, filename: str = "cpu_gantt_chart.png") -> Path:
    """Generates a detailed Gantt Chart for CPU scheduling execution timeline."""
    logger.info(f"Generating Gantt Chart for {result.algorithm}...")
    fig, ax = plt.subplots(figsize=(12, 3.5), dpi=300)

    # Distinct palette
    palette = ['#4C78A8', '#F58518', '#E45756', '#72B7B2', '#54A24B', '#EECA3B', '#B279A2', '#FF9DA6']
    pids = sorted(list(set(p.pid for p in result.processes)))
    color_map = {pid: palette[i % len(palette)] for i, pid in enumerate(pids)}
    color_map["IDLE"] = "#D3D3D3"

    y_pos = 0.5
    bar_height = 0.5

    for start, end, pid in result.timeline:
        duration = end - start
        color = color_map.get(pid, "#888888")
        hatch = '//' if pid == "IDLE" else None
        
        ax.broken_barh([(start, duration)], (y_pos - bar_height/2, bar_height),
                         facecolors=color, edgecolor='black', linewidth=1.2, hatch=hatch)
        
        # Center text label
        text_color = 'black' if pid == "IDLE" else 'white'
        font_weight = 'bold'
        ax.text(start + duration / 2, y_pos, pid, ha='center', va='center',
                color=text_color, fontweight=font_weight, fontsize=10)

    # Collect time ticks
    time_ticks = set([0])
    for start, end, _ in result.timeline:
        time_ticks.add(start)
        time_ticks.add(end)
    sorted_ticks = sorted(list(time_ticks))

    ax.set_yticks([])
    ax.set_xticks(sorted_ticks)
    ax.set_xlabel("Simulation Time Units (Ticks)", fontsize=11, fontweight='bold')
    ax.set_title(f"CPU Scheduling Gantt Chart — {result.algorithm}\n(Total Time: {result.total_time}, CPU Util: {result.cpu_utilization:.1f}%)", 
                 fontsize=12, fontweight='bold', pad=12)

    # Legend
    legend_patches = [mpatches.Patch(facecolor=color_map[p], edgecolor='black', label=f"Process {p}") for p in pids]
    if any(pid == "IDLE" for _, _, pid in result.timeline):
        legend_patches.append(mpatches.Patch(facecolor="#D3D3D3", edgecolor='black', hatch='//', label="CPU Idle"))
    ax.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=min(6, len(legend_patches)))

    plt.tight_layout()
    out_path = CHARTS_DIR / filename
    plt.savefig(out_path, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"Gantt chart saved to {out_path}")
    return out_path


def plot_cpu_comparison(df: pd.DataFrame, filename: str = "cpu_comparison_bar.png") -> Path:
    """Generates grouped bar chart comparing CPU scheduling algorithms across TAT, WT, and RT."""
    logger.info("Generating CPU comparative bar chart...")
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)

    algorithms = df["Algorithm"].tolist()
    x = np.arange(len(algorithms))
    width = 0.25

    tat = df["Avg Turnaround Time"].tolist()
    wt = df["Avg Waiting Time"].tolist()
    rt = df["Avg Response Time"].tolist()

    rects1 = ax.bar(x - width, tat, width, label='Avg Turnaround Time (TAT)', color='#2b5c8f', edgecolor='black', alpha=0.9)
    rects2 = ax.bar(x, wt, width, label='Avg Waiting Time (WT)', color='#d95f02', edgecolor='black', alpha=0.9)
    rects3 = ax.bar(x + width, rt, width, label='Avg Response Time (RT)', color='#7570b3', edgecolor='black', alpha=0.9)

    ax.set_ylabel('Time Units', fontsize=11, fontweight='bold')
    ax.set_title('Comparative Performance of CPU Scheduling Algorithms', fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms, rotation=18, ha='right', fontsize=9.5)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Value labels
    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.tight_layout()
    out_path = CHARTS_DIR / filename
    plt.savefig(out_path, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"CPU comparison chart saved to {out_path}")
    return out_path


def plot_page_fault_curves(df: pd.DataFrame, filename: str = "page_fault_curves.png") -> Path:
    """Generates multi-line plot showing page faults vs frame counts for each algorithm."""
    logger.info("Generating Page Replacement curves...")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    algos = df["Algorithm"].unique()
    markers = {'FIFO': 'o', 'LRU': 's', 'Optimal': '^', 'LFU': 'd'}
    colors = {'FIFO': '#e41a1c', 'LRU': '#377eb8', 'Optimal': '#4daf4a', 'LFU': '#984ea3'}

    for algo in algos:
        sub_df = df[df["Algorithm"] == algo].sort_values(by="Frames")
        ax.plot(sub_df["Frames"], sub_df["Page Faults"],
                marker=markers.get(algo, 'o'), markersize=8, linewidth=2.2,
                color=colors.get(algo, '#333333'), label=algo)

    ax.set_xlabel('Allocated Page Frames', fontsize=11, fontweight='bold')
    ax.set_ylabel('Total Page Faults', fontsize=11, fontweight='bold')
    ax.set_title('Page Replacement Algorithms: Page Faults vs Allocated Frames', fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(sorted(df["Frames"].unique()))
    ax.legend(frameon=True, fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    out_path = CHARTS_DIR / filename
    plt.savefig(out_path, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"Page replacement curves saved to {out_path}")
    return out_path


def plot_disk_trajectories(results: List[DiskSchedulingResult], filename: str = "disk_head_trajectories.png") -> Path:
    """Plots cylinder seek trajectory for multiple disk scheduling algorithms."""
    logger.info("Generating Disk Head Trajectory curves...")
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    markers = ['o', 's', '^', 'v', 'D', 'x']

    for idx, r in enumerate(results):
        steps = list(range(len(r.traversal_order)))
        ax.plot(steps, r.traversal_order,
                marker=markers[idx % len(markers)],
                linewidth=1.8,
                markersize=6,
                color=colors[idx % len(colors)],
                label=f"{r.algorithm} (Movement: {r.total_head_movement})")

    ax.set_xlabel('Seek Step Sequence', fontsize=11, fontweight='bold')
    ax.set_ylabel('Disk Cylinder Number', fontsize=11, fontweight='bold')
    ax.set_title('Disk Head Scheduling: Cylinder Seek Trajectories', fontsize=13, fontweight='bold', pad=15)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='best')
    ax.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    out_path = CHARTS_DIR / filename
    plt.savefig(out_path, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"Disk trajectories saved to {out_path}")
    return out_path


def plot_memory_blocks(result: ContiguousAllocationResult, filename: str = "memory_allocation_map.png") -> Path:
    """Plots horizontal physical memory segmentation map showing allocated vs free blocks."""
    logger.info("Generating Memory Allocation Map...")
    fig, ax = plt.subplots(figsize=(12, 3.2), dpi=300)

    y_pos = 0.5
    bar_height = 0.5

    for b in result.blocks:
        start = b.start_address
        total_size = b.size
        
        if b.is_free:
            ax.broken_barh([(start, total_size)], (y_pos - bar_height/2, bar_height),
                           facecolors='#e0e0e0', edgecolor='black', linewidth=1.2, hatch='..')
            ax.text(start + total_size/2, y_pos, f"Free\n({total_size}B)",
                    ha='center', va='center', fontsize=8.5, color='#333333', fontweight='bold')
        else:
            # Allocated segment
            alloc_size = b.allocated_size
            frag_size = b.internal_fragmentation
            
            ax.broken_barh([(start, alloc_size)], (y_pos - bar_height/2, bar_height),
                           facecolors='#2b5c8f', edgecolor='black', linewidth=1.2)
            ax.text(start + alloc_size/2, y_pos, f"{b.allocated_to}\n({alloc_size}B)",
                    ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')
            
            # Internal fragmentation segment
            if frag_size > 0:
                ax.broken_barh([(start + alloc_size, frag_size)], (y_pos - bar_height/2, bar_height),
                               facecolors='#f4a582', edgecolor='black', linewidth=1.2, hatch='//')
                ax.text(start + alloc_size + frag_size/2, y_pos, f"Frag\n{frag_size}B",
                        ha='center', va='center', fontsize=7, color='black')

    # Tick marks at block boundaries
    addresses = [b.start_address for b in result.blocks] + [result.total_memory]
    ax.set_yticks([])
    ax.set_xticks(addresses)
    ax.set_xlabel("Physical Memory Byte Address", fontsize=11, fontweight='bold')
    ax.set_title(f"Contiguous Memory Partition Map — {result.strategy.replace('_', ' ').title()}\n(Total Memory: {result.total_memory}B, Internal Frag: {result.internal_fragmentation}B)",
                 fontsize=12, fontweight='bold', pad=12)

    legend_patches = [
        mpatches.Patch(facecolor='#2b5c8f', edgecolor='black', label="Allocated Process"),
        mpatches.Patch(facecolor='#f4a582', edgecolor='black', hatch='//', label="Internal Fragmentation"),
        mpatches.Patch(facecolor='#e0e0e0', edgecolor='black', hatch='..', label="Free Memory Block")
    ]
    ax.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=3)

    plt.tight_layout()
    out_path = CHARTS_DIR / filename
    plt.savefig(out_path, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"Memory map saved to {out_path}")
    return out_path
