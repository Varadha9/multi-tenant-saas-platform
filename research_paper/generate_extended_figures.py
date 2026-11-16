#!/usr/bin/env python3
"""
Generate extended publication-quality figures for the NexusOps research paper.
Produces:
1. figures/fig4_benchmark_ratio.pdf (Throughput ratio distribution & TOST corridor)
2. figures/fig5_latency_cdf.pdf (Latency distribution across percentiles)
3. figures/fig6_concurrency_scaling.pdf (Concurrency scaling & tail latency comparison)
4. figures/fig2_schema_er.pdf (Vector schema ER diagram)
5. figures/fig3_connection_state_machine.pdf (Vector connection lifecycle state machine)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('figures', exist_ok=True)

# Set high-quality IEEE typography
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 9,
    'axes.labelsize': 9,
    'legend.fontsize': 8,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'text.usetex': False,
    'figure.dpi': 300,
    'lines.linewidth': 1.2
})

# -----------------------------------------------------------------------------
# 1. Fig 4: Throughput Ratios across 4 Microbenchmarks (n = 30)
# -----------------------------------------------------------------------------
df_raw = pd.read_csv('benchmark/results/raw_runs.csv')
micro_workloads = ['Point Lookup', 'Paged List', 'Tenant Count', 'Point Insert']
df_micro = df_raw[df_raw['workload'].isin(micro_workloads)]

fig, ax = plt.subplots(figsize=(3.4, 2.6))
x_positions = {w: i for i, w in enumerate(micro_workloads)}

# Equivalence corridor +/- 5%
ax.axhspan(0.95, 1.05, color='#e0e0e0', alpha=0.6, label='±5% Equiv Corridor', zorder=1)
ax.axhline(1.0, color='gray', linestyle='--', linewidth=0.8, label='Parity (1.00)', zorder=2)

np.random.seed(42)
for w in micro_workloads:
    subset = df_micro[df_micro['workload'] == w]
    ratios = subset['throughput_ratio'].values
    x_idx = x_positions[w]
    jitter = np.random.uniform(-0.12, 0.12, size=len(ratios))
    
    ax.scatter(x_idx + jitter, ratios, color='#1f77b4', alpha=0.65, s=18, edgecolors='none', zorder=3)
    
    mean_val = np.mean(ratios)
    ci_low = np.percentile(ratios, 2.5)
    ci_high = np.percentile(ratios, 97.5)
    
    ax.errorbar(x_idx, mean_val, yerr=[[mean_val - ci_low], [ci_high - mean_val]],
                fmt='D', color='#d62728', ecolor='#d62728', elinewidth=1.6, capsize=3.5,
                markersize=4.5, zorder=4)

ax.set_xticks(range(len(micro_workloads)))
ax.set_xticklabels(['Point\nLookup', 'Paged\nList', 'Tenant\nCount', 'Point\nInsert'])
ax.set_ylabel('Throughput Ratio (Dual / Base)')
ax.set_ylim(0.45, 1.25)
ax.grid(True, linestyle=':', alpha=0.5, zorder=0)

handles, labels = ax.get_legend_handles_labels()
# Add custom legend entry for scatter and mean
scatter_proxy = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#1f77b4', markersize=5, label='Paired Run (n=30)')
mean_proxy = plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='#d62728', markeredgecolor='#d62728', markersize=5, label='Mean with 95% CI')
ax.legend(handles=[handles[0], handles[1], scatter_proxy, mean_proxy], loc='upper right', framealpha=0.9)

plt.tight_layout()
plt.savefig('figures/fig4_benchmark_ratio.pdf')
plt.savefig('figures/fig4_benchmark_ratio.png')
plt.close()
print("Generated Fig 4: fig4_benchmark_ratio.pdf")

# -----------------------------------------------------------------------------
# 2. Fig 5: Latency Comparison across Workloads (Base vs. Dual Mean & p99)
# -----------------------------------------------------------------------------
workload_order = [
    'Point Lookup', 'Paged List', 'Tenant Count', 'Point Insert',
    'Two-Table Join', 'Three-Table Join', 'Small Tenant Skew', 'Whale Tenant Skew'
]

mean_base = []
mean_dual = []
p99_base = []
p99_dual = []

for w in workload_order:
    sub = df_raw[df_raw['workload'] == w]
    mean_base.append(sub['baseline_mean_ms'].mean())
    mean_dual.append(sub['dual_mean_ms'].mean())
    p99_base.append(sub['baseline_p99_ms'].mean())
    p99_dual.append(sub['dual_p99_ms'].mean())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.5), sharey=False)

x = np.arange(len(workload_order))
width = 0.38

# Subplot 1: Mean Latency
ax1.bar(x - width/2, mean_base, width, label='Filter Baseline', color='#4a7bb0', edgecolor='black', linewidth=0.6)
ax1.bar(x + width/2, mean_dual, width, label='Dual-Layer (RLS)', color='#e67e22', edgecolor='black', linewidth=0.6)
ax1.set_ylabel('Mean Latency (ms)')
ax1.set_title('(a) Mean Transaction Latency', fontsize=9)
ax1.set_xticks(x)
ax1.set_xticklabels(['Lookup', 'Paged', 'Count', 'Insert', '2-Join', '3-Join', 'Small', 'Whale'], rotation=25)
ax1.grid(True, linestyle=':', alpha=0.5, axis='y')
ax1.legend(loc='upper left', framealpha=0.9)

# Subplot 2: p99 Tail Latency
ax2.bar(x - width/2, p99_base, width, label='Filter Baseline', color='#4a7bb0', edgecolor='black', linewidth=0.6)
ax2.bar(x + width/2, p99_dual, width, label='Dual-Layer (RLS)', color='#e67e22', edgecolor='black', linewidth=0.6)
ax2.set_ylabel('p99 Tail Latency (ms)')
ax2.set_title('(b) p99 Empirical Tail Latency', fontsize=9)
ax2.set_xticks(x)
ax2.set_xticklabels(['Lookup', 'Paged', 'Count', 'Insert', '2-Join', '3-Join', 'Small', 'Whale'], rotation=25)
ax2.grid(True, linestyle=':', alpha=0.5, axis='y')
ax2.legend(loc='upper left', framealpha=0.9)

plt.tight_layout()
plt.savefig('figures/fig5_latency_cdf.pdf')
plt.savefig('figures/fig5_latency_cdf.png')
plt.close()
print("Generated Fig 5: fig5_latency_cdf.pdf")

# -----------------------------------------------------------------------------
# 3. Fig 6: Concurrency Scaling & Pool Saturation (8 vs 32 clients)
# -----------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.4))

clients = ['8 Clients\n(Standard)', '32 Clients\n(Saturation)']
x = np.arange(len(clients))
width = 0.35

sub_8 = df_raw[df_raw['workload'] == 'Point Lookup']
sub_32 = df_raw[df_raw['workload'] == 'Connection Saturation (32 clients)']

tps_base = [sub_8['baseline_tps'].mean(), sub_32['baseline_tps'].mean()]
tps_dual = [sub_8['dual_layer_tps'].mean(), sub_32['dual_layer_tps'].mean()]

lat_base = [sub_8['baseline_mean_ms'].mean(), sub_32['baseline_mean_ms'].mean()]
lat_dual = [sub_8['dual_mean_ms'].mean(), sub_32['dual_mean_ms'].mean()]
p99_base = [sub_8['baseline_p99_ms'].mean(), sub_32['baseline_p99_ms'].mean()]
p99_dual = [sub_8['dual_p99_ms'].mean(), sub_32['dual_p99_ms'].mean()]

# Panel A: Throughput
ax1.bar(x - width/2, tps_base, width, label='Filter Baseline', color='#2b5c8f', edgecolor='black', linewidth=0.6)
ax1.bar(x + width/2, tps_dual, width, label='Dual-Layer (RLS)', color='#d95f02', edgecolor='black', linewidth=0.6)
ax1.set_ylabel('Throughput (transactions / sec)')
ax1.set_title('(a) System Throughput under Load', fontsize=9)
ax1.set_xticks(x)
ax1.set_xticklabels(clients)
ax1.grid(True, linestyle=':', alpha=0.5, axis='y')
ax1.legend(loc='lower left', framealpha=0.9)

# Panel B: Latency Inflation
ax2.plot(x, lat_base, marker='o', linewidth=1.5, color='#2b5c8f', label='Base Mean Latency')
ax2.plot(x, lat_dual, marker='s', linewidth=1.5, color='#d95f02', label='Dual Mean Latency')
ax2.plot(x, p99_base, marker='^', linestyle='--', linewidth=1.2, color='#2b5c8f', alpha=0.7, label='Base p99 Latency')
ax2.plot(x, p99_dual, marker='v', linestyle='--', linewidth=1.2, color='#d95f02', alpha=0.7, label='Dual p99 Latency')
ax2.set_ylabel('Latency (ms)')
ax2.set_title('(b) Latency Scaling & Pool Queueing', fontsize=9)
ax2.set_xticks(x)
ax2.set_xticklabels(clients)
ax2.grid(True, linestyle=':', alpha=0.5)
ax2.legend(loc='upper left', framealpha=0.9, fontsize=7.5)

plt.tight_layout()
plt.savefig('figures/fig6_concurrency_scaling.pdf')
plt.savefig('figures/fig6_concurrency_scaling.png')
plt.close()
print("Generated Fig 6: fig6_concurrency_scaling.pdf")

# -----------------------------------------------------------------------------
# 4. Fig 2: Schema ER & Composite Key Architecture
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.0, 3.2))
ax.axis('off')

def draw_table(ax, x, y, title, columns, width=1.5, height=1.1, color='#eef3f8', border='#2b5c8f'):
    rect = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.04",
                                  facecolor=color, edgecolor=border, linewidth=1.2)
    ax.add_patch(rect)
    # Header bar
    header_rect = patches.FancyBboxPatch((x, y + height - 0.28), width, 0.28, boxstyle="round,pad=0.02",
                                         facecolor=border, edgecolor=border)
    ax.add_patch(header_rect)
    ax.text(x + width/2, y + height - 0.15, title, color='white', weight='bold',
            fontsize=7.5, ha='center', va='center')
    
    # Column text
    col_str = "\n".join(columns)
    ax.text(x + 0.08, y + height - 0.38, col_str, color='#222222', fontsize=6.2, ha='left', va='top', family='monospace')

# Tenant Table
draw_table(ax, 0.2, 1.8, "tenants (Global)", ["+ id: UUID (PK)", "  name: VARCHAR", "  plan: VARCHAR", "  created_at: TS"], width=1.45, height=1.1, color='#fdfbf7', border='#b35806')

# Tenant-owned Core Tables
draw_table(ax, 2.0, 1.8, "users (RLS)", ["+ id: UUID (PK)", "# tenant_id: UUID (FK)", "  email: VARCHAR", "  role: VARCHAR", "PK: (tenant_id, id)"], width=1.55, height=1.25)
draw_table(ax, 3.8, 1.8, "organizations (RLS)", ["+ id: UUID (PK)", "# tenant_id: UUID (FK)", "  name: VARCHAR", "  industry: VARCHAR", "PK: (tenant_id, id)"], width=1.55, height=1.25)
draw_table(ax, 5.6, 1.8, "audit_events (RLS)", ["+ id: BIGINT (PK)", "# tenant_id: UUID (FK)", "  action: VARCHAR", "  actor_id: UUID", "  created_at: TS"], width=1.55, height=1.25, color='#fef0d9', border='#d7301f')

# Child domain tables
draw_table(ax, 0.2, 0.2, "contacts (RLS)", ["+ id: UUID (PK)", "# tenant_id: UUID", "  org_id: UUID (FK)", "  first_name: STR", "  email: STR"], width=1.45, height=1.2)
draw_table(ax, 2.0, 0.2, "orders (RLS)", ["+ id: BIGINT (PK)", "# tenant_id: UUID", "  customer_id: UUID", "  total_amt: NUMERIC", "PK: (tenant_id, id)"], width=1.55, height=1.2)
draw_table(ax, 3.8, 0.2, "order_items (RLS)", ["+ id: BIGINT (PK)", "# tenant_id: UUID", "# order_id: BIGINT", "  product_id: UUID", "FK: (tenant_id, order_id)"], width=1.65, height=1.2)
draw_table(ax, 5.7, 0.2, "order_payments (RLS)", ["+ id: BIGINT (PK)", "# tenant_id: UUID", "# item_id: BIGINT", "  amount: NUMERIC", "FK: (tenant_id, item_id)"], width=1.55, height=1.2)

# Connector arrows
arrow_props = dict(arrowstyle="->", color='#4a7bb0', lw=1.0)
ax.annotate("", xy=(2.0, 2.3), xytext=(1.65, 2.3), arrowprops=arrow_props)
ax.annotate("", xy=(3.8, 2.3), xytext=(3.55, 2.3), arrowprops=arrow_props)
ax.annotate("", xy=(5.6, 2.3), xytext=(5.35, 2.3), arrowprops=arrow_props)

ax.annotate("", xy=(2.7, 1.8), xytext=(2.7, 1.4), arrowprops=arrow_props)
ax.annotate("", xy=(3.8, 0.8), xytext=(3.55, 0.8), arrowprops=arrow_props)
ax.annotate("", xy=(5.7, 0.8), xytext=(5.45, 0.8), arrowprops=arrow_props)

ax.set_xlim(0, 7.4)
ax.set_ylim(0, 3.2)
plt.tight_layout()
plt.savefig('figures/fig2_schema_er.pdf')
plt.savefig('figures/fig2_schema_er.png')
plt.close()
print("Generated Fig 2: fig2_schema_er.pdf")

# -----------------------------------------------------------------------------
# 5. Fig 3: Connection Lifecycle State Machine Diagram
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.0, 2.5))
ax.axis('off')

def draw_state(ax, x, y, label, subtext="", width=1.4, height=0.75, color='#e0f3f8', border='#02818a'):
    rect = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.06",
                                  facecolor=color, edgecolor=border, linewidth=1.2)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2 + 0.1, label, color='#01464c', weight='bold',
            fontsize=7.5, ha='center', va='center')
    if subtext:
        ax.text(x + width/2, y + height/2 - 0.14, subtext, color='#444444',
                fontsize=5.8, ha='center', va='center')

draw_state(ax, 0.2, 0.9, "1. Pool Idle", "HikariCP idle buffer\ntau = NULL / prior state", color='#f7f7f7', border='#636363')
draw_state(ax, 1.9, 0.9, "2. Check Out", "getConnection()\nautoCommit = false", color='#fff7bc', border='#d95f0e')
draw_state(ax, 3.6, 0.9, "3. Context Bind", "SET LOCAL app.tenant_id\nis_local = true", color='#ccebc5', border='#2b8cbe')
draw_state(ax, 5.3, 0.9, "4. DML Execution", "Hibernate Filter + RLS\nAtomic boundary", color='#e0f3f8', border='#0868ac')

# Return state
draw_state(ax, 3.6, 0.05, "5. Tx Commit/Rollback", "PostgreSQL purges GUC\nContext wipes automatically", color='#fbb4ae', border='#cb181d')

arrow_style = dict(arrowstyle="-|>", color='#222222', lw=1.2, mutation_scale=10)
# 1 -> 2
ax.annotate("Request\nAcquire", xy=(1.9, 1.27), xytext=(1.6, 1.27), arrowprops=arrow_style, fontsize=6.5, ha='center', va='bottom')
# 2 -> 3
ax.annotate("Tx Begin\nHook", xy=(3.6, 1.27), xytext=(3.3, 1.27), arrowprops=arrow_style, fontsize=6.5, ha='center', va='bottom')
# 3 -> 4
ax.annotate("DML Queries\nPrepared Stmts", xy=(5.3, 1.27), xytext=(5.0, 1.27), arrowprops=arrow_style, fontsize=6.5, ha='center', va='bottom')
# 4 -> 5
ax.annotate("Tx End", xy=(5.0, 0.42), xytext=(5.7, 0.9), arrowprops=arrow_style, fontsize=6.5, ha='left')
# 5 -> 1
ax.annotate("Return sanitized connection to pool", xy=(0.9, 0.9), xytext=(3.6, 0.42), arrowprops=arrow_style, fontsize=6.5, ha='center')

ax.set_xlim(0, 7.0)
ax.set_ylim(0, 2.2)
plt.tight_layout()
plt.savefig('figures/fig3_connection_state_machine.pdf')
plt.savefig('figures/fig3_connection_state_machine.png')
plt.close()
print("Generated Fig 3: fig3_connection_state_machine.pdf")

print("All extended figures successfully generated!")
