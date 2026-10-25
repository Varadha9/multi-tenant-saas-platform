#!/usr/bin/env python3
"""
NexusOps Figure 3 Generator
Generates publication-quality Figure 3 directly from real empirical pgbench measurements.
Strictly zero synthetic or simulated data.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd
from matplotlib.lines import Line2D

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_CSV = os.path.join(BASE_DIR, "benchmark", "results", "raw_runs.csv")
if not os.path.exists(RAW_CSV):
    RAW_CSV = os.path.join(BASE_DIR, "benchmark_raw_data.csv")

if not os.path.exists(RAW_CSV):
    print(f"Error: {RAW_CSV} not found! Please run the benchmark suite first.")
    sys.exit(1)

df = pd.read_csv(RAW_CSV)

workloads = ['Point Lookup', 'Paged List', 'Tenant Count', 'Point Insert']
workload_labels = ['Point\nLookup', 'Paged\nList', 'Tenant\nCount', 'Point\nInsert']

plot_data = {}

for w in workloads:
    sub = df[df['workload'] == w]
    if len(sub) == 0:
        print(f"Warning: workload {w} not found in CSV!")
        continue
    ratios = sub['throughput_ratio'].values
    n = len(ratios)
    m = float(np.mean(ratios))
    ci = stats.t.interval(0.95, df=n-1, loc=m, scale=stats.sem(ratios))
    plot_data[w] = {
        'ratios': ratios,
        'mean': m,
        'ci': ci,
        'n': n
    }

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 8.5,
    'axes.labelsize': 8.5,
    'axes.titlesize': 9,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 7,
})

fig, ax = plt.subplots(figsize=(3.45, 2.7), dpi=300)

# Shaded equivalence corridor [0.95, 1.05]
ax.axhspan(0.95, 1.05, color='#e6f4ea', alpha=0.9, zorder=1)
ax.axhline(1.00, color='#444444', linestyle='--', linewidth=0.8, zorder=2)
ax.axhline(0.95, color='#93c47d', linestyle=':', linewidth=0.7, zorder=2)
ax.axhline(1.05, color='#93c47d', linestyle=':', linewidth=0.7, zorder=2)

x_pos = np.arange(len(workloads))
np.random.seed(42) # Seed for consistent scatter plot visual jitter only

for i, w in enumerate(workloads):
    if w not in plot_data:
        continue
    pts = plot_data[w]['ratios']
    m = plot_data[w]['mean']
    ci = plot_data[w]['ci']
    n = plot_data[w]['n']
    
    jitter = np.random.uniform(-0.14, 0.14, size=n)
    ax.scatter(x_pos[i] + jitter, pts, color='#2b5797', alpha=0.45, s=12, edgecolors='none', zorder=3)
    
    yerr = [[m - ci[0]], [ci[1] - m]]
    ax.errorbar(x_pos[i], m, yerr=yerr, fmt='D', color='#b22222', markersize=4.5,
                capsize=3.5, capthick=1.0, elinewidth=1.2, zorder=4)

legend_elements = [
    Line2D([0], [0], color='#e6f4ea', lw=5, label=r'$\pm 5\%$ Equivalence Corridor'),
    Line2D([0], [0], color='#444444', linestyle='--', lw=0.9, label='Parity (Ratio = 1.00)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#2b5797', alpha=0.6, markersize=4.5, label='Paired Run ($n=30$)'),
    Line2D([0], [0], marker='D', color='#b22222', markersize=4.5, lw=1.2, label='Mean with 95% CI')
]

ax.set_xticks(x_pos)
ax.set_xticklabels(workload_labels)
ax.set_ylabel('Throughput Ratio (Dual / Base)')

# Compute dynamic y-limits based on actual data with headroom
all_pts = np.concatenate([plot_data[w]['ratios'] for w in workloads if w in plot_data])
y_min = min(0.90, np.min(all_pts) - 0.03)
y_max = max(1.10, np.max(all_pts) + 0.03)
ax.set_ylim(y_min, y_max)
ax.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)

ax.legend(handles=legend_elements, loc='upper right', frameon=True, framealpha=0.92, edgecolor='#dddddd', fontsize=6.5)

plt.tight_layout()
plt.subplots_adjust(left=0.19, right=0.96, top=0.96, bottom=0.17)

os.makedirs(os.path.join(BASE_DIR, 'figures'), exist_ok=True)
pdf_path = os.path.join(BASE_DIR, 'figures', 'fig3_benchmark_ratio.pdf')
png_path = os.path.join(BASE_DIR, 'figures', 'fig3_benchmark_ratio.png')
plt.savefig(pdf_path, format='pdf')
plt.savefig(png_path, format='png', dpi=300)
print(f"Generated {pdf_path} and {png_path} directly from measured data.")
