# Phase 3: Analysis and Comparison

**Module Title:** Performance Metrics and Comparative Evaluation  
**Marks Weightage:** 20 Marks  
**Submission Target:** Valid metrics, meaningful comparison, labelled visualizations, and technical observations.

---

## 1. Mathematical Formulas & Performance Metrics

### 1.1 CPU Scheduling Metrics
- **Turnaround Time ($TAT$):**  
  $$TAT = T_{\text{completion}} - T_{\text{arrival}}$$
- **Waiting Time ($WT$):**  
  $$WT = TAT - T_{\text{burst}}$$
- **Response Time ($RT$):**  
  $$RT = T_{\text{first\_dispatch}} - T_{\text{arrival}}$$
- **CPU Utilization ($\%$):**  
  $$\text{Utilization} = \frac{\sum T_{\text{burst}}}{T_{\text{total}}} \times 100\%$$
- **Throughput:**  
  $$\text{Throughput} = \frac{N_{\text{processes}}}{T_{\text{total}}}$$

### 1.2 Memory Management Metrics
- **Page Fault Ratio:**  
  $$\text{Fault Ratio} = \frac{\text{Faults}}{\text{Total Page References}}$$
- **Page Hit Ratio:**  
  $$\text{Hit Ratio} = \frac{\text{Hits}}{\text{Total Page References}} = 1 - \text{Fault Ratio}$$
- **Internal Fragmentation:**  
  $$\text{Internal Frag} = \sum_{b \in \text{Allocated Blocks}} (\text{Block Capacity}_b - \text{Requested Size}_b)$$

### 1.3 Disk Scheduling Metrics
- **Total Head Movement ($THM$):**  
  $$THM = \sum_{i=1}^{k} |C_i - C_{i-1}|$$
- **Average Seek Distance:**  
  $$\text{Avg Seek} = \frac{THM}{k}$$

---

## 2. Experimental Benchmark Results

### 2.1 Process Scheduling Comparative Benchmark
Evaluated on benchmark dataset ($N=5$ processes: $P_1(0, 5), P_2(1, 3), P_3(2, 8), P_4(3, 6), P_5(4, 4)$):

| Algorithm | Avg Turnaround Time | Avg Waiting Time | Avg Response Time | CPU Util (%) | Throughput (proc/unit) | Total Time |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **SRTF (Preemptive)** | **11.60** | **6.40** | 5.80 | 100.0% | 0.1923 | 26 |
| **SJF (Non-Preemptive)** | 11.80 | 6.60 | 6.60 | 100.0% | 0.1923 | 26 |
| **Priority (Preemptive)** | 12.80 | 7.60 | 7.00 | 100.0% | 0.1923 | 26 |
| **Priority (Non-Preemptive)**| 13.00 | 7.80 | 7.80 | 100.0% | 0.1923 | 26 |
| **FCFS** | 13.40 | 8.20 | 8.20 | 100.0% | 0.1923 | 26 |
| **Round Robin ($q=2$)** | 17.80 | 12.60 | **2.80** | 100.0% | 0.1923 | 26 |
| **MLFQ** | 17.80 | 12.60 | **2.00** | 100.0% | 0.1923 | 26 |

**Analytical Observations:**
1. **SRTF achieves optimal average waiting time (6.40 units)** by preemptively prioritizing shorter remaining jobs, minimizing the queue buildup.
2. **Round Robin and MLFQ prioritize responsiveness (Response Time 2.80 and 2.00 units)** at the cost of higher average turnaround time due to frequent context interleaving. This proves why interactive modern operating systems utilize RR and MLFQ variants.

---

### 2.2 Virtual Memory Page Replacement Comparison
Evaluated on reference string $[7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]$ across varying frame sizes:

| Frames | FIFO Faults (Fault %) | LRU Faults (Fault %) | Optimal Faults (Fault %) | LFU Faults (Fault %) |
| :---: | :---: | :---: | :---: | :---: |
| **3 Frames** | 15 (75.0%) | 12 (60.0%) | **9 (45.0%)** | 13 (65.0%) |
| **4 Frames** | 10 (50.0%) | 8 (40.0%) | **8 (40.0%)** | 8 (40.0%) |
| **5 Frames** | 9 (45.0%) | 7 (35.0%) | **7 (35.0%)** | 7 (35.0%) |

**Analytical Observations:**
- **Optimal (OPT) consistently forms the theoretical lower bound** on page faults (9 faults with 3 frames).
- **LRU closely approximates Optimal performance** (12 faults with 3 frames) because of the temporal locality principle in instruction streams.

#### Belady's Anomaly Demonstration:
Evaluated on Belady reference string $[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]$:
- **3 Frames in FIFO:** 9 page faults.
- **4 Frames in FIFO:** **10 page faults!**
- **Conclusion:** Adding more memory frames directly caused **more page faults** under FIFO. The simulator successfully detects and logs this anomaly. Under LRU and Optimal, page faults monotonically decrease, verifying stack property inclusion.

---

### 2.3 Contiguous Memory Partition Allocation Comparison
Evaluated with partitions $[100, 500, 200, 300, 600]\text{ B}$ and requests $[P_1: 212, P_2: 417, P_3: 112, P_4: 426]\text{ B}$:

| Strategy | Allocated Requests | Unallocated Requests | Internal Frag (B) | Memory Utilization |
| :--- | :---: | :---: | :---: | :---: |
| **Best Fit** | **4 of 4 (100%)** | **0** | **433 B** | **68.6%** |
| **First Fit** | 3 of 4 (75%) | 1 ($P_4: 426\text{ B}$) | 559 B | 43.6% |
| **Worst Fit** | 3 of 4 (75%) | 1 ($P_4: 426\text{ B}$) | 659 B | 43.6% |

**Analytical Observations:**
- **Best Fit successfully satisfies all four requests** with the lowest internal fragmentation (433 B).
- **First Fit and Worst Fit allocate suboptimal large partitions prematurely**, leaving inadequate contiguous space for $P_4$ ($426\text{ B}$), resulting in memory allocation failure.

---

### 2.4 Disk Head Scheduling Comparison
Evaluated on cylinder request stream $[98, 183, 37, 122, 14, 124, 65, 67]$ starting at head position 53 on a 200-cylinder disk:

| Algorithm | Total Head Movement (cylinders) | Average Seek Distance (cylinders) | Traversal Sequence |
| :--- | :---: | :---: | :--- |
| **SSTF** | **236** | **29.50** | $53 \to 65 \to 67 \to 37 \to 14 \to 98 \to 122 \to 124 \to 183$ |
| **LOOK (UP)** | 299 | 37.38 | $53 \to 65 \to 67 \to 98 \to 122 \to 124 \to 183 \to 37 \to 14$ |
| **C-LOOK** | 322 | 40.25 | $53 \to 65 \to 67 \to 98 \to 122 \to 124 \to 183 \to 14 \to 37$ |
| **SCAN (UP)** | 331 | 36.78 | $53 \to 65 \to 67 \to 98 \to 122 \to 124 \to 183 \to 199 \to 37 \to 14$ |
| **C-SCAN** | 382 | 38.20 | $53 \to 65 \to 67 \to 98 \to 122 \to 124 \to 183 \to 199 \to 0 \to 14 \to 37$ |
| **FCFS** | 640 | 80.00 | $53 \to 98 \to 183 \to 37 \to 122 \to 14 \to 124 \to 65 \to 67$ |

**Analytical Observations:**
- **SSTF achieves minimal head travel (236 cylinders)** by greedily visiting neighboring cylinders, though it carries a known risk of starvation for distant tracks.
- **LOOK and SCAN provide fair, deterministic sweeps**, reducing wild swings compared to unoptimized FCFS (which wastes 640 cylinders—almost triple the movement).
- **LOOK improves on SCAN** by avoiding the unnecessary travel to physical cylinder 199.

---

## 3. Visual Charts Generated

All charts are generated at 300 DPI publication resolution in `output/charts/`:
1. `cpu_gantt_chart.png` / `gantt_srtf.png`: Exact timeline intervals color-coded by process with idle markers.
2. `cpu_algorithm_comparison.png`: Grouped comparative bar chart comparing Turnaround, Waiting, and Response times.
3. `page_replacement_curves.png`: Multiline plot of page faults vs frames illustrating performance slopes.
4. `beladys_anomaly_curves.png`: Visual verification of Belady's Anomaly where FIFO fault curve spikes upwards from 3 to 4 frames.
5. `disk_scheduling_trajectories.png`: Cylinder position vs seek sequence showing actuator sweeping curves.
6. `memory_best_fit_map.png`: Physical layout map displaying process allocation blocks and internal fragments.
