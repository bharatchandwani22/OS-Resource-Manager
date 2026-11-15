/**
 * OS Resource Management Simulator - Web Application Frontend Logic
 */

// Global Chart Instances
let cpuChartInstance = null;
let beladyChartInstance = null;
let diskChartInstance = null;

// Palette for Processes
const PROCESS_COLORS = [
    '#3b82f6', '#f97316', '#ef4444', '#10b981', '#8b5cf6', 
    '#ec4899', '#06b6d4', '#eab308', '#14b8a6', '#6366f1'
];

document.addEventListener("DOMContentLoaded", () => {
    // Initialize default states
    loadCpuPreset();
    loadMemoryPreset();
    loadDeadlockPreset();
    loadDiskPreset();
    fetchTelemetry();
});

// ==============================================================================
// Tab Navigation
// ==============================================================================
function switchTab(tabId) {
    // Hide all tab sections
    const tabs = ['overview', 'cpu', 'memory', 'deadlock', 'storage', 'telemetry', 'reports'];
    tabs.forEach(t => {
        const sec = document.getElementById(`tab-${t}`);
        const btn = document.getElementById(`nav-${t}`);
        if (sec) sec.classList.add('hidden');
        if (btn) btn.classList.remove('active');
    });

    const activeSec = document.getElementById(`tab-${tabId}`);
    const activeBtn = document.getElementById(`nav-${tabId}`);
    if (activeSec) activeSec.classList.remove('hidden');
    if (activeBtn) activeBtn.classList.add('active');

    // Tab-specific hooks
    if (tabId === 'telemetry') {
        fetchTelemetry();
    }
}

function switchMemSubTab(subTabId) {
    ['contiguous', 'paging', 'belady'].forEach(st => {
        const sec = document.getElementById(`memSection-${st}`);
        const btn = document.getElementById(`memSubTab-${st}`);
        if (sec) sec.classList.add('hidden');
        if (btn) {
            btn.classList.remove('bg-emerald-600', 'text-white');
            btn.classList.add('bg-slate-800', 'text-slate-400');
        }
    });

    const activeSec = document.getElementById(`memSection-${subTabId}`);
    const activeBtn = document.getElementById(`memSubTab-${subTabId}`);
    if (activeSec) activeSec.classList.remove('hidden');
    if (activeBtn) {
        activeBtn.classList.add('bg-emerald-600', 'text-white');
        activeBtn.classList.remove('bg-slate-800', 'text-slate-400');
    }
}


// ==============================================================================
// Module 1: CPU Process Scheduling
// ==============================================================================
function addCpuProcessRow(pid = "", arrival = 0, burst = 1, priority = 0) {
    const tbody = document.getElementById("cpuTableBody");
    const rowCount = tbody.rows.length;
    const assignedPid = pid || `P${rowCount + 1}`;

    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-800/40 transition";
    tr.innerHTML = `
        <td class="py-2.5 px-3">
            <input type="text" value="${assignedPid}" class="w-20 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-blue-500">
        </td>
        <td class="py-2.5 px-3">
            <input type="number" min="0" value="${arrival}" class="w-20 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-blue-500">
        </td>
        <td class="py-2.5 px-3">
            <input type="number" min="1" value="${burst}" class="w-20 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-blue-500">
        </td>
        <td class="py-2.5 px-3">
            <input type="number" value="${priority}" class="w-20 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-blue-500">
        </td>
        <td class="py-2.5 px-3 text-right">
            <button onclick="this.closest('tr').remove()" class="text-rose-400 hover:text-rose-300 text-xs px-2 py-1 rounded hover:bg-rose-500/10 transition">
                <i class="fa-solid fa-trash"></i>
            </button>
        </td>
    `;
    tbody.appendChild(tr);
}

function loadCpuPreset() {
    const tbody = document.getElementById("cpuTableBody");
    tbody.innerHTML = "";
    const preset = [
        { pid: "P1", arrival_time: 0, burst_time: 5, priority: 2 },
        { pid: "P2", arrival_time: 1, burst_time: 3, priority: 1 },
        { pid: "P3", arrival_time: 2, burst_time: 8, priority: 4 },
        { pid: "P4", arrival_time: 3, burst_time: 6, priority: 3 },
        { pid: "P5", arrival_time: 4, burst_time: 4, priority: 5 }
    ];
    preset.forEach(p => addCpuProcessRow(p.pid, p.arrival_time, p.burst_time, p.priority));
}

function getCpuProcessesFromTable() {
    const rows = document.querySelectorAll("#cpuTableBody tr");
    const procs = [];
    rows.forEach(r => {
        const inputs = r.querySelectorAll("input");
        procs.push({
            pid: inputs[0].value.trim(),
            arrival_time: parseInt(inputs[1].value) || 0,
            burst_time: parseInt(inputs[2].value) || 1,
            priority: parseInt(inputs[3].value) || 0
        });
    });
    return procs;
}

async function runCpuSimulation() {
    const procs = getCpuProcessesFromTable();
    const algorithm = document.getElementById("cpuAlgorithmSelect").value;
    const quantum = parseInt(document.getElementById("cpuQuantumInput").value) || 2;

    try {
        const res = await fetch("/api/cpu/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ algorithm, quantum, processes: procs })
        });
        const data = await res.json();
        if (!data.success) {
            alert("Error: " + data.error);
            return;
        }

        // Render Results
        document.getElementById("cpuResultsArea").classList.remove("hidden");
        document.getElementById("cpuCompareChartCard").classList.add("hidden");

        // Metrics
        document.getElementById("statAvgTat").innerText = data.avg_tat.toFixed(2);
        document.getElementById("statAvgWt").innerText = data.avg_wt.toFixed(2);
        document.getElementById("statAvgRt").innerText = data.avg_rt.toFixed(2);
        document.getElementById("statCpuUtil").innerText = data.cpu_utilization.toFixed(1) + "%";
        document.getElementById("statTotalTime").innerText = data.total_time + " ticks";

        // Gantt Chart Rendering
        renderGanttChart(data.timeline, data.total_time);

        // Process Table
        const resTbody = document.getElementById("cpuResultTableBody");
        resTbody.innerHTML = "";
        data.processes.forEach(p => {
            const tr = document.createElement("tr");
            tr.className = "hover:bg-slate-800/40 text-slate-200";
            tr.innerHTML = `
                <td class="py-2 px-3 font-bold text-white">${p.PID}</td>
                <td class="py-2 px-3">${p.Arrival}</td>
                <td class="py-2 px-3">${p.Burst}</td>
                <td class="py-2 px-3">${p.Start ?? '-'}</td>
                <td class="py-2 px-3">${p.Completion}</td>
                <td class="py-2 px-3 font-semibold text-blue-400">${p.Turnaround}</td>
                <td class="py-2 px-3 font-semibold text-amber-400">${p.Waiting}</td>
                <td class="py-2 px-3 font-semibold text-purple-400">${p.Response}</td>
            `;
            resTbody.appendChild(tr);
        });

    } catch (err) {
        alert("Failed to run CPU simulation: " + err);
    }
}

function renderGanttChart(timeline, totalTime) {
    const container = document.getElementById("ganttContainer");
    container.innerHTML = "";

    const wrapper = document.createElement("div");
    wrapper.className = "w-full min-w-[650px]";

    // Bar container
    const barTrack = document.createElement("div");
    barTrack.className = "h-14 w-full flex rounded-xl overflow-hidden border border-slate-700 bg-slate-950 p-1 gap-1";

    // Tick labels container
    const tickTrack = document.createElement("div");
    tickTrack.className = "w-full flex text-2xs font-mono text-slate-400 mt-1 relative h-6";

    timeline.forEach((block, idx) => {
        const duration = block.end - block.start;
        const pct = (duration / totalTime) * 100;
        const isIdle = block.pid === "IDLE";

        // Assign distinct color per PID
        const color = isIdle ? "#334155" : PROCESS_COLORS[idx % PROCESS_COLORS.length];

        const segment = document.createElement("div");
        segment.className = "gantt-bar h-full rounded flex items-center justify-center font-bold text-xs shadow-sm cursor-pointer";
        segment.style.width = `${pct}%`;
        segment.style.backgroundColor = color;
        segment.style.color = isIdle ? "#94a3b8" : "#ffffff";
        segment.title = `${block.pid} [${block.start} - ${block.end}] (${duration} ticks)`;
        segment.innerHTML = `<span>${block.pid}</span>`;

        barTrack.appendChild(segment);
    });

    // Generate timeline time markers
    const timeMarks = new Set([0]);
    timeline.forEach(b => { timeMarks.add(b.start); timeMarks.add(b.end); });
    const sortedMarks = Array.from(timeMarks).sort((a, b) => a - b);

    sortedMarks.forEach(t => {
        const pct = (t / totalTime) * 100;
        const mark = document.createElement("span");
        mark.className = "absolute -translate-x-1/2 text-2xs font-mono";
        mark.style.left = `${pct}%`;
        mark.innerText = t;
        tickTrack.appendChild(mark);
    });

    wrapper.appendChild(barTrack);
    wrapper.appendChild(tickTrack);
    container.appendChild(wrapper);
}

async function compareAllCpu() {
    const procs = getCpuProcessesFromTable();
    const quantum = parseInt(document.getElementById("cpuQuantumInput").value) || 2;

    try {
        const res = await fetch("/api/cpu/compare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ processes: procs, quantum })
        });
        const data = await res.json();
        if (!data.success) {
            alert("Comparison error: " + data.error);
            return;
        }

        document.getElementById("cpuResultsArea").classList.remove("hidden");
        const chartCard = document.getElementById("cpuCompareChartCard");
        chartCard.classList.remove("hidden");

        // Chart.js render
        const comp = data.comparison;
        const labels = comp.map(c => c["Algorithm"]);
        const tatData = comp.map(c => c["Avg Turnaround Time"]);
        const wtData = comp.map(c => c["Avg Waiting Time"]);
        const rtData = comp.map(c => c["Avg Response Time"]);

        if (cpuChartInstance) cpuChartInstance.destroy();
        const ctx = document.getElementById("cpuCompareChartCanvas").getContext("2d");
        cpuChartInstance = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    { label: "Avg Turnaround (TAT)", data: tatData, backgroundColor: "#3b82f6" },
                    { label: "Avg Waiting (WT)", data: wtData, backgroundColor: "#f97316" },
                    { label: "Avg Response (RT)", data: rtData, backgroundColor: "#8b5cf6" }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: "#e2e8f0" } }
                },
                scales: {
                    x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
                    y: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" }, title: { display: true, text: "Time Units", color: "#94a3b8" } }
                }
            }
        });
    } catch (err) {
        alert("Failed to compare algorithms: " + err);
    }
}


// ==============================================================================
// Module 2: Memory Management
// ==============================================================================
function addMemoryBlockRow(id = "", size = 100) {
    const tbody = document.getElementById("memBlockTableBody");
    const bid = id || (tbody.rows.length + 1);
    const tr = document.createElement("tr");
    tr.className = "border-b border-slate-800";
    tr.innerHTML = `
        <td class="py-1.5"><input type="number" value="${bid}" class="w-16 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs font-mono"></td>
        <td class="py-1.5"><input type="number" min="1" value="${size}" class="w-24 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs font-mono"></td>
        <td class="py-1.5 text-right"><button onclick="this.closest('tr').remove()" class="text-rose-400 text-xs"><i class="fa-solid fa-trash"></i></button></td>
    `;
    tbody.appendChild(tr);
}

function addMemoryReqRow(pid = "", size = 100) {
    const tbody = document.getElementById("memReqTableBody");
    const rpid = pid || `P${tbody.rows.length + 1}`;
    const tr = document.createElement("tr");
    tr.className = "border-b border-slate-800";
    tr.innerHTML = `
        <td class="py-1.5"><input type="text" value="${rpid}" class="w-20 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs font-mono"></td>
        <td class="py-1.5"><input type="number" min="1" value="${size}" class="w-24 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs font-mono"></td>
        <td class="py-1.5 text-right"><button onclick="this.closest('tr').remove()" class="text-rose-400 text-xs"><i class="fa-solid fa-trash"></i></button></td>
    `;
    tbody.appendChild(tr);
}

function loadMemoryPreset() {
    // Blocks
    const bBody = document.getElementById("memBlockTableBody");
    bBody.innerHTML = "";
    [[1, 100], [2, 500], [3, 200], [4, 300], [5, 600]].forEach(b => addMemoryBlockRow(b[0], b[1]));

    // Reqs
    const rBody = document.getElementById("memReqTableBody");
    rBody.innerHTML = "";
    [["P1", 212], ["P2", 417], ["P3", 112], ["P4", 426]].forEach(r => addMemoryReqRow(r[0], r[1]));
}

async function runContiguousAllocation() {
    const bRows = document.querySelectorAll("#memBlockTableBody tr");
    const blocks = [];
    bRows.forEach(r => {
        const ins = r.querySelectorAll("input");
        blocks.push([parseInt(ins[0].value), parseInt(ins[1].value)]);
    });

    const rRows = document.querySelectorAll("#memReqTableBody tr");
    const requests = [];
    rRows.forEach(r => {
        const ins = r.querySelectorAll("input");
        requests.push([ins[0].value.trim(), parseInt(ins[1].value)]);
    });

    const strategy = document.getElementById("contiguousStrategySelect").value;

    try {
        const res = await fetch("/api/memory/contiguous", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ strategy, blocks, requests })
        });
        const data = await res.json();
        if (!data.success) {
            alert("Error: " + data.error);
            return;
        }

        document.getElementById("contiguousResultArea").classList.remove("hidden");
        document.getElementById("statContigTotal").innerText = `Total: ${data.total_memory} B`;
        document.getElementById("statContigAlloc").innerText = `Used: ${data.allocated_memory} B`;
        document.getElementById("statContigInternal").innerText = `Internal Frag: ${data.internal_fragmentation} B`;
        document.getElementById("statContigExternal").innerText = `External Frag: ${data.external_fragmentation} B`;

        // Render Segmentation Map
        const mapContainer = document.getElementById("contiguousBlockMap");
        mapContainer.innerHTML = "";
        data.blocks.forEach(b => {
            const pct = (b.size / data.total_memory) * 100;
            const seg = document.createElement("div");
            seg.className = "h-full rounded flex flex-col items-center justify-center text-3xs font-mono overflow-hidden transition";
            seg.style.width = `${pct}%`;

            if (b.is_free) {
                seg.style.backgroundColor = "#334155";
                seg.innerHTML = `<span class="text-slate-300">Free</span><span>${b.size}B</span>`;
            } else {
                seg.style.backgroundColor = "#1e40af";
                seg.innerHTML = `<span class="font-bold text-white">${b.allocated_to}</span><span>${b.allocated_size}B / ${b.size}B</span>`;
            }
            mapContainer.appendChild(seg);
        });

        // Table
        const tbody = document.getElementById("contiguousResultTbody");
        tbody.innerHTML = "";
        data.blocks.forEach(b => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td class="py-2">${b.block_id}</td>
                <td class="py-2">${b.start_address}</td>
                <td class="py-2">${b.size} B</td>
                <td class="py-2 ${b.is_free ? 'text-slate-400' : 'text-emerald-400 font-semibold'}">${b.is_free ? 'Free' : 'Allocated'}</td>
                <td class="py-2">${b.allocated_to || '-'}</td>
                <td class="py-2 font-mono text-amber-400">${b.internal_fragmentation} B</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        alert("Failed contiguous allocation: " + err);
    }
}

async function runPagingSimulation() {
    const rawRef = document.getElementById("pagingRefStringInput").value;
    const refString = rawRef.split(",").map(x => parseInt(x.trim())).filter(x => !isNaN(x));
    const frames = parseInt(document.getElementById("pagingFramesInput").value) || 3;
    const algorithm = document.getElementById("pagingAlgoSelect").value;

    try {
        const res = await fetch("/api/memory/paging", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reference_string: refString, frames, algorithm })
        });
        const data = await res.json();
        if (!data.success) {
            alert("Error: " + data.error);
            return;
        }

        document.getElementById("pagingResultArea").classList.remove("hidden");
        document.getElementById("pagingFaultsStat").innerText = data.page_faults;
        document.getElementById("pagingHitsStat").innerText = data.page_hits;
        document.getElementById("pagingFaultRatioStat").innerText = data.fault_ratio + "%";
        document.getElementById("pagingHitRatioStat").innerText = data.hit_ratio + "%";

        // Build header
        const thead = document.getElementById("pagingTableHeader");
        let headerHtml = `<th class="py-2">Step</th><th class="py-2">Page</th>`;
        for (let i = 0; i < frames; i++) {
            headerHtml += `<th class="py-2">Frame ${i + 1}</th>`;
        }
        headerHtml += `<th class="py-2">Result</th>`;
        thead.innerHTML = headerHtml;

        // Build step rows
        const tbody = document.getElementById("pagingTableBody");
        tbody.innerHTML = "";
        data.steps.forEach(s => {
            const tr = document.createElement("tr");
            tr.className = "border-b border-slate-800 text-slate-300";

            let rowHtml = `<td class="py-2 font-mono">${s.step}</td><td class="py-2 font-bold text-white font-mono">${s.page}</td>`;
            for (let i = 0; i < frames; i++) {
                const val = (s.frames && s.frames[i] !== null && s.frames[i] !== undefined) ? s.frames[i] : "-";
                rowHtml += `<td class="py-2 font-mono">${val}</td>`;
            }
            const badgeClass = s.hit ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "bg-rose-500/20 text-rose-400 border border-rose-500/30";
            rowHtml += `<td class="py-2"><span class="px-2 py-0.5 rounded-full font-bold text-2xs ${badgeClass}">${s.hit ? 'HIT' : 'FAULT'}</span></td>`;
            tr.innerHTML = rowHtml;
            tbody.appendChild(tr);
        });

    } catch (err) {
        alert("Failed paging simulation: " + err);
    }
}

async function runBeladyAnalysis() {
    try {
        const res = await fetch("/api/memory/belady", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
        });
        const data = await res.json();
        if (!data.success) {
            alert("Error: " + data.error);
            return;
        }

        document.getElementById("beladyResultArea").classList.remove("hidden");
        const alertBox = document.getElementById("beladyAlertBadge");

        if (data.anomaly_detected) {
            alertBox.className = "p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-300 text-xs space-y-1 font-mono";
            alertBox.innerHTML = `<strong><i class="fa-solid fa-triangle-exclamation"></i> Belady's Anomaly Confirmed!</strong><br>` + data.details.join("<br>");
        } else {
            alertBox.className = "p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-xs font-mono";
            alertBox.innerHTML = `No anomaly detected for this reference string.`;
        }

        // Render Chart.js line curves
        const frameLabels = Object.keys(data.results.FIFO);
        const fifoFaults = Object.values(data.results.FIFO);
        const lruFaults = Object.values(data.results.LRU);
        const optFaults = Object.values(data.results.Optimal);

        if (beladyChartInstance) beladyChartInstance.destroy();
        const ctx = document.getElementById("beladyChartCanvas").getContext("2d");
        beladyChartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: frameLabels.map(f => `${f} Frames`),
                datasets: [
                    { label: "FIFO (Anomaly Visible)", data: fifoFaults, borderColor: "#ef4444", backgroundColor: "#ef4444", borderWidth: 2.5, tension: 0.1 },
                    { label: "LRU (Stack Algorithm)", data: lruFaults, borderColor: "#3b82f6", backgroundColor: "#3b82f6", borderWidth: 2, tension: 0.1 },
                    { label: "Optimal (OPT)", data: optFaults, borderColor: "#10b981", backgroundColor: "#10b981", borderWidth: 2, tension: 0.1 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: "#e2e8f0" } } },
                scales: {
                    x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
                    y: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" }, title: { display: true, text: "Page Faults", color: "#94a3b8" } }
                }
            }
        });

    } catch (err) {
        alert("Belady analysis error: " + err);
    }
}


// ==============================================================================
// Module 3: Deadlock Engine
// ==============================================================================
const DEFAULT_BANKERS = {
    pids: ["P0", "P1", "P2", "P3", "P4"],
    rids: ["A", "B", "C"],
    available: [3, 3, 2],
    max_matrix: [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3]
    ],
    alloc_matrix: [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2]
    ]
};

function loadDeadlockPreset() {
    document.getElementById("avail_A").value = DEFAULT_BANKERS.available[0];
    document.getElementById("avail_B").value = DEFAULT_BANKERS.available[1];
    document.getElementById("avail_C").value = DEFAULT_BANKERS.available[2];

    const allocBody = document.getElementById("bankersAllocBody");
    const maxBody = document.getElementById("bankersMaxBody");
    allocBody.innerHTML = "";
    maxBody.innerHTML = "";

    DEFAULT_BANKERS.pids.forEach((pid, i) => {
        // Alloc row
        const trA = document.createElement("tr");
        trA.className = "border-b border-slate-800";
        trA.innerHTML = `
            <td class="py-1.5 text-left font-bold text-white">${pid}</td>
            <td><input type="number" min="0" value="${DEFAULT_BANKERS.alloc_matrix[i][0]}" class="w-14 bg-slate-900 border border-slate-700 text-center rounded text-xs font-mono"></td>
            <td><input type="number" min="0" value="${DEFAULT_BANKERS.alloc_matrix[i][1]}" class="w-14 bg-slate-900 border border-slate-700 text-center rounded text-xs font-mono"></td>
            <td><input type="number" min="0" value="${DEFAULT_BANKERS.alloc_matrix[i][2]}" class="w-14 bg-slate-900 border border-slate-700 text-center rounded text-xs font-mono"></td>
        `;
        allocBody.appendChild(trA);

        // Max row
        const trM = document.createElement("tr");
        trM.className = "border-b border-slate-800";
        trM.innerHTML = `
            <td class="py-1.5 text-left font-bold text-white">${pid}</td>
            <td><input type="number" min="0" value="${DEFAULT_BANKERS.max_matrix[i][0]}" class="w-14 bg-slate-900 border border-slate-700 text-center rounded text-xs font-mono"></td>
            <td><input type="number" min="0" value="${DEFAULT_BANKERS.max_matrix[i][1]}" class="w-14 bg-slate-900 border border-slate-700 text-center rounded text-xs font-mono"></td>
            <td><input type="number" min="0" value="${DEFAULT_BANKERS.max_matrix[i][2]}" class="w-14 bg-slate-900 border border-slate-700 text-center rounded text-xs font-mono"></td>
        `;
        maxBody.appendChild(trM);
    });
}

function getBankersPayload() {
    const pids = DEFAULT_BANKERS.pids;
    const rids = DEFAULT_BANKERS.rids;
    const available = [
        parseInt(document.getElementById("avail_A").value) || 0,
        parseInt(document.getElementById("avail_B").value) || 0,
        parseInt(document.getElementById("avail_C").value) || 0
    ];

    const alloc_rows = document.querySelectorAll("#bankersAllocBody tr");
    const allocation_matrix = [];
    alloc_rows.forEach(r => {
        const ins = r.querySelectorAll("input");
        allocation_matrix.push([parseInt(ins[0].value), parseInt(ins[1].value), parseInt(ins[2].value)]);
    });

    const max_rows = document.querySelectorAll("#bankersMaxBody tr");
    const max_matrix = [];
    max_rows.forEach(r => {
        const ins = r.querySelectorAll("input");
        max_matrix.push([parseInt(ins[0].value), parseInt(ins[1].value), parseInt(ins[2].value)]);
    });

    return { process_ids: pids, resource_ids: rids, available, max_matrix, allocation_matrix };
}

async function checkBankersSafety() {
    const payload = getBankersPayload();
    try {
        const res = await fetch("/api/deadlock/safety", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!data.success) {
            alert("Banker's error: " + data.error);
            return;
        }

        document.getElementById("bankersResultArea").classList.remove("hidden");
        const badge = document.getElementById("bankersStatusBadge");
        if (data.is_safe) {
            badge.className = "p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 font-bold flex items-center gap-3";
            badge.innerHTML = `<i class="fa-solid fa-circle-check text-xl"></i> Safe State Confirmed! Safe Sequence: &lt; ${data.safe_sequence.join(" &rarr; ")} &gt;`;
        } else {
            badge.className = "p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-400 font-bold flex items-center gap-3";
            badge.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-xl"></i> Unsafe State! Potential Deadlock Detected. No Safe Sequence exists.`;
        }

        const tracesBox = document.getElementById("bankersTraces");
        tracesBox.innerHTML = data.traces.map(t => `<div>&bull; ${t}</div>`).join("");

    } catch (err) {
        alert("Failed safety check: " + err);
    }
}

async function testResourceRequest() {
    const basePayload = getBankersPayload();
    const pid = document.getElementById("requestPidSelect").value;
    const reqVec = [
        parseInt(document.getElementById("req_A").value) || 0,
        parseInt(document.getElementById("req_B").value) || 0,
        parseInt(document.getElementById("req_C").value) || 0
    ];

    const payload = {
        ...basePayload,
        request_pid: pid,
        request_vector: reqVec
    };

    try {
        const res = await fetch("/api/deadlock/request", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        const box = document.getElementById("requestTestResult");
        box.classList.remove("hidden");

        if (data.granted) {
            box.className = "text-xs font-mono p-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
            box.innerHTML = `<strong>[REQUEST GRANTED]</strong> ${data.message}`;
        } else {
            box.className = "text-xs font-mono p-3 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300";
            box.innerHTML = `<strong>[REQUEST REJECTED / WAIT]</strong> ${data.message}`;
        }
    } catch (err) {
        alert("Request test failed: " + err);
    }
}


// ==============================================================================
// Module 4: Storage / Disk Scheduling
// ==============================================================================
function loadDiskPreset() {
    document.getElementById("diskRequestsInput").value = "98, 183, 37, 122, 14, 124, 65, 67";
    document.getElementById("diskHeadInput").value = "53";
    document.getElementById("diskSizeInput").value = "200";
}

async function runDiskSimulation() {
    const rawReq = document.getElementById("diskRequestsInput").value;
    const requests = rawReq.split(",").map(x => parseInt(x.trim())).filter(x => !isNaN(x));
    const initialHead = parseInt(document.getElementById("diskHeadInput").value) || 53;
    const diskSize = parseInt(document.getElementById("diskSizeInput").value) || 200;
    const algorithm = document.getElementById("diskAlgoSelect").value;
    const direction = document.getElementById("diskDirectionSelect").value;

    try {
        const res = await fetch("/api/storage/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ algorithm, requests, initial_head: initialHead, disk_size: diskSize, direction })
        });
        const data = await res.json();
        if (!data.success) {
            alert("Disk error: " + data.error);
            return;
        }

        document.getElementById("diskResultArea").classList.remove("hidden");
        document.getElementById("diskTotalMoveStat").innerText = `${data.total_head_movement} cylinders`;
        document.getElementById("diskAvgSeekStat").innerText = `${data.average_seek_distance.toFixed(2)} cylinders`;

        if (data.all_comparisons && data.all_comparisons.length > 0) {
            document.getElementById("diskOptimalAlgoStat").innerText = data.all_comparisons[0].algorithm;
        }

        // Render Step table
        const tbody = document.getElementById("diskStepTableBody");
        tbody.innerHTML = "";
        data.seek_steps.forEach((s, idx) => {
            const tr = document.createElement("tr");
            tr.className = "border-b border-slate-800 text-slate-300 font-mono";
            tr.innerHTML = `
                <td class="py-1.5">${idx + 1}</td>
                <td class="py-1.5">${s.from}</td>
                <td class="py-1.5 font-bold text-white">${s.to}</td>
                <td class="py-1.5 text-purple-400 font-semibold">${s.distance}</td>
            `;
            tbody.appendChild(tr);
        });

        // Trajectory Chart
        const steps = data.traversal_order.map((_, i) => `Step ${i}`);
        if (diskChartInstance) diskChartInstance.destroy();
        const ctx = document.getElementById("diskTrajectoryChartCanvas").getContext("2d");
        diskChartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: steps,
                datasets: [{
                    label: `${data.algorithm} Trajectory (Cylinder)`,
                    data: data.traversal_order,
                    borderColor: "#a855f7",
                    backgroundColor: "#a855f7",
                    borderWidth: 2.5,
                    tension: 0.1,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: "#e2e8f0" } } },
                scales: {
                    x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
                    y: { 
                        min: 0, 
                        max: diskSize, 
                        ticks: { color: "#94a3b8" }, 
                        grid: { color: "#1e293b" },
                        title: { display: true, text: "Cylinder Track Index", color: "#94a3b8" }
                    }
                }
            }
        });

    } catch (err) {
        alert("Failed disk simulation: " + err);
    }
}


// ==============================================================================
// Module 5: Host OS Telemetry
// ==============================================================================
async function fetchTelemetry() {
    try {
        const res = await fetch("/api/telemetry");
        const data = await res.json();
        if (!data.success) return;

        const m = data.metrics;
        document.getElementById("telemKernel").innerText = `${m.system.os} ${m.system.kernel}`;
        document.getElementById("telemSource").innerText = m.source || "Host Subprocess";
        document.getElementById("telemCpuLoad").innerText = `${m.cpu.load_avg_1m} / ${m.cpu.load_avg_5m}`;
        document.getElementById("telemThreads").innerText = `Active PIDs: ${m.cpu.runnable_threads} | Total Threads: ${m.cpu.total_threads}`;

        const availMb = Math.round(m.memory.available_kb / 1024);
        const totalMb = Math.round(m.memory.total_kb / 1024);
        document.getElementById("telemMemAvail").innerText = `${availMb} / ${totalMb} MB`;
        const swapUsedMb = Math.round((m.memory.swap_total_kb - m.memory.swap_free_kb) / 1024);
        document.getElementById("telemSwap").innerText = `Swap Used: ${swapUsedMb} MB`;

        document.getElementById("telemDiskIO").innerText = `${m.storage.reads_completed} Reads / ${m.storage.writes_completed} Writes`;
        document.getElementById("headerTelemetryStatus").innerText = `Host: ${m.system.os}`;

    } catch (err) {
        console.warn("Could not fetch live telemetry: ", err);
    }
}
