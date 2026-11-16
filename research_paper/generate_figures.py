#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('figures', exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Times'],
    'font.size': 8.5,
    'axes.labelsize': 8.5,
    'legend.fontsize': 7.2,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'text.usetex': False,
    'figure.dpi': 300,
    'lines.linewidth': 1.1
})

# =============================================================================
# 1. FIG 1: System Architecture (Completely contained text & pristine lines)
# =============================================================================
fig, ax = plt.subplots(figsize=(7.1, 3.4))
ax.axis('off')

# Outer Application Boundary
outer_box = patches.FancyBboxPatch((0.2, 1.25), 6.7, 1.85, boxstyle="round,pad=0.04", facecolor='#f8fafc', edgecolor='#334155', linewidth=1.3)
ax.add_patch(outer_box)
ax.text(0.35, 2.95, "NexusOps Enterprise Application Core (Spring Boot 4 / Java 25 Modular Monolith)", fontsize=8, weight='bold', color='#1e293b')

# Modules
modules = [
    ("Tenancy", "Workspace Context"),
    ("Identity", "JWT / RS256 Auth"),
    ("Security", "Role-Based Access"),
    ("Directory", "People & Orgs"),
    ("CRM Core", "Deals & Pipelines"),
    ("Ledger", "Billing & Invoices"),
    ("Auditing", "Immutable Traces")
]

x_start = 0.38
w_mod = 0.88
h_mod = 0.68
gap = 0.08
for i, (m_title, m_sub) in enumerate(modules):
    rect = patches.FancyBboxPatch((x_start + i*(w_mod + gap), 2.10), w_mod, h_mod, boxstyle="round,pad=0.02", facecolor='#ffffff', edgecolor='#2563eb', linewidth=0.9)
    ax.add_patch(rect)
    ax.text(x_start + i*(w_mod + gap) + w_mod/2, 2.10 + h_mod/2 + 0.1, m_title, color='#1e3a8a', weight='bold', fontsize=7.6, ha='center', va='center')
    ax.text(x_start + i*(w_mod + gap) + w_mod/2, 2.10 + h_mod/2 - 0.14, m_sub, color='#64748b', fontsize=5.8, ha='center', va='center')

# Shared Kernel Bar (Two-line cleanly contained text)
kernel_box = patches.FancyBboxPatch((0.38, 1.38), 6.34, 0.55, boxstyle="round,pad=0.02", facecolor='#fef3c7', edgecolor='#d97706', linewidth=1.1)
ax.add_patch(kernel_box)
ax.text(3.55, 1.70, "Shared Security Kernel: TenantContextHolder | TenantAwareDataSource",
        fontsize=7.2, weight='bold', color='#92400e', ha='center', va='center')
ax.text(3.55, 1.50, "@TenantId Abstract Base Entity | Eager DatabaseRoleGuard | ScopedValue Context Propagation",
        fontsize=6.6, color='#78350f', ha='center', va='center')

# Ingress layer (top)
def draw_capsule(ax, x, y, w, h, t1, t2, bg='#eff6ff', border='#3b82f6'):
    r = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", facecolor=bg, edgecolor=border, linewidth=1.1)
    ax.add_patch(r)
    ax.text(x + w/2, y + h/2 + 0.1, t1, color='#1e3a8a', weight='bold', fontsize=7.8, ha='center', va='center')
    ax.text(x + w/2, y + h/2 - 0.13, t2, color='#475569', fontsize=6.5, ha='center', va='center')

draw_capsule(ax, 0.8, 3.25, 2.2, 0.55, "Client Browser (React SPA)", "JWT Bearer Token in Memory")
draw_capsule(ax, 4.1, 3.25, 2.2, 0.55, "Reverse Proxy / Gateway", "Nginx SSL Termination & Routing")

arrow_down = dict(arrowstyle="-|>", color='#1e293b', lw=1.2, mutation_scale=8)
ax.annotate("", xy=(4.05, 3.52), xytext=(3.05, 3.52), arrowprops=arrow_down)
ax.annotate("", xy=(5.2, 3.14), xytext=(5.2, 3.25), arrowprops=arrow_down)

# Persistence Layer (bottom)
draw_capsule(ax, 0.4, 0.10, 2.8, 0.82, "PostgreSQL 17 Relational Storage", "16 Tables with FORCE RLS | Unprivileged nexusops_app", bg='#f0fdf4', border='#166534')
draw_capsule(ax, 3.5, 0.10, 1.6, 0.82, "Redis 7 Cache", "Tenant-Prefixed Keys\nToken Blocklist", bg='#fffbeb', border='#b45309')
draw_capsule(ax, 5.3, 0.10, 1.4, 0.82, "Audit Storage", "Append-Only Immutable\nLedger Trigger", bg='#fef2f2', border='#991b1b')

# Connectors from kernel to persistence
ax.annotate("", xy=(1.8, 0.94), xytext=(1.8, 1.25), arrowprops=arrow_down)
ax.annotate("", xy=(4.3, 0.94), xytext=(4.3, 1.25), arrowprops=arrow_down)
ax.annotate("", xy=(6.0, 0.94), xytext=(6.0, 1.25), arrowprops=arrow_down)

# Clean label beside arrow (zero box crossing)
ax.text(1.92, 1.08, "SET LOCAL app.tenant_id\n(transaction-scoped hook)", fontsize=5.8, color='#334155', ha='left', va='center')

ax.set_xlim(0, 7.1)
ax.set_ylim(0, 3.9)
plt.tight_layout()
plt.savefig('figures/fig1_architecture.pdf')
plt.savefig('figures/fig1_architecture.png', dpi=300)
plt.close()
print("Perfect Fig 1 generated!")

# =============================================================================
# 2. FIG 2: Relational Schema & Crow's Foot ER (Pristine layout)
# =============================================================================
fig, ax = plt.subplots(figsize=(7.1, 3.8))
ax.axis('off')

def draw_clean_table(ax, x, y, w, h, table_name, pk_list, fk_list, attr_list, is_global=False):
    header_bg = '#78350f' if is_global else '#1e3a8a'
    border_color = '#78350f' if is_global else '#2563eb'
    body_bg = '#fffbeb' if is_global else '#ffffff'
    
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", facecolor=body_bg, edgecolor=border_color, linewidth=1.1)
    ax.add_patch(rect)
    
    header_h = 0.28
    h_rect = patches.Rectangle((x, y + h - header_h), w, header_h, facecolor=header_bg, edgecolor=border_color, linewidth=1.1)
    ax.add_patch(h_rect)
    
    ax.text(x + w/2, y + h - header_h/2, table_name, color='white', weight='bold', fontsize=7.2, ha='center', va='center')
    
    curr_y = y + h - header_h - 0.12
    line_h = 0.13
    for pk in pk_list:
        ax.text(x + 0.05, curr_y, pk, color='#991b1b', weight='bold', fontsize=5.8, ha='left', va='center')
        curr_y -= line_h
    for fk in fk_list:
        ax.text(x + 0.05, curr_y, fk, color='#1d4ed8', weight='bold', fontsize=5.8, ha='left', va='center')
        curr_y -= line_h
    for attr in attr_list:
        ax.text(x + 0.05, curr_y, attr, color='#334155', fontsize=5.6, ha='left', va='center')
        curr_y -= line_h

# Row 1 (Top): tenants (Global, left), users (middle-left), audit_events (right)
draw_clean_table(ax, 0.2, 2.2, 1.5, 1.4, "tenants [GLOBAL]",
                 ["PK id : UUID"],
                 [],
                 ["name : VARCHAR", "plan : VARCHAR", "status : VARCHAR", "created_at : TS"], is_global=True)

draw_clean_table(ax, 2.3, 2.2, 1.5, 1.4, "users [FORCED RLS]",
                 ["PK (tenant_id, id)"],
                 ["FK tenant_id : UUID"],
                 ["email : VARCHAR", "role_id : VARCHAR", "is_active : BOOL", "created_at : TS"])

draw_clean_table(ax, 4.4, 2.2, 1.6, 1.4, "audit_events [RLS]",
                 ["PK (tenant_id, id)"],
                 ["FK tenant_id : UUID"],
                 ["actor_id : UUID", "action : VARCHAR", "query_hash : STR", "created_at : TS"])

# Row 2 (Bottom): organizations (left), contacts (mid-left), orders (mid-right), order_items (right)
draw_clean_table(ax, 0.2, 0.3, 1.5, 1.4, "organizations [RLS]",
                 ["PK (tenant_id, id)"],
                 ["FK tenant_id : UUID"],
                 ["legal_name : VARCHAR", "tax_no : VARCHAR", "currency : CHAR(3)", "created_at : TS"])

draw_clean_table(ax, 2.0, 0.3, 1.5, 1.4, "contacts [RLS]",
                 ["PK (tenant_id, id)"],
                 ["FK tenant_id : UUID", "FK (tenant_id, org_id)"],
                 ["first_name : VARCHAR", "last_name : VARCHAR", "email : VARCHAR", "phone : VARCHAR"])

draw_clean_table(ax, 3.8, 0.3, 1.5, 1.4, "orders [RLS]",
                 ["PK (tenant_id, id)"],
                 ["FK tenant_id : UUID", "FK (tenant_id, org_id)"],
                 ["order_date : DATE", "total_amt : NUMERIC", "status : VARCHAR", "currency : CHAR(3)"])

draw_clean_table(ax, 5.5, 0.3, 1.4, 1.4, "order_items [RLS]",
                 ["PK (tenant_id, id)"],
                 ["FK tenant_id : UUID", "FK (tenant_id, order_id)"],
                 ["product_id : UUID", "quantity : INT", "unit_price : NUMERIC", "discount : NUMERIC"])

# Connectors: Zero crossing through tables
arrow_style = dict(arrowstyle="-|>", color='#475569', lw=1.1, mutation_scale=7)

# 1. tenants -> users
ax.annotate("", xy=(2.3, 2.9), xytext=(1.7, 2.9), arrowprops=arrow_style)
ax.text(2.0, 3.0, "1 : N", fontsize=5.8, color='#1e293b', weight='bold', ha='center')

# 2. tenants -> organizations
ax.annotate("", xy=(0.95, 1.7), xytext=(0.95, 2.2), arrowprops=arrow_style)
ax.text(1.15, 1.95, "1 : N", fontsize=5.8, color='#1e293b', weight='bold', ha='left')

# 3. users -> audit_events
ax.annotate("", xy=(4.4, 2.9), xytext=(3.8, 2.9), arrowprops=arrow_style)
ax.text(4.1, 3.0, "1 : N", fontsize=5.8, color='#1e293b', weight='bold', ha='center')

# 4. organizations -> contacts
ax.annotate("", xy=(2.0, 1.0), xytext=(1.7, 1.0), arrowprops=arrow_style)
ax.text(1.85, 1.1, "1 : N", fontsize=5.8, color='#1e293b', weight='bold', ha='center')

# 5. organizations -> orders
ax.plot([0.95, 0.95, 4.55, 4.55], [0.3, 0.15, 0.15, 0.3], color='#475569', lw=1.1)
ax.annotate("", xy=(4.55, 0.3), xytext=(4.55, 0.16), arrowprops=arrow_style)
ax.text(2.75, 0.05, "1 : N (Composite FK pushdown on tenant_id, org_id)", fontsize=5.5, color='#475569', weight='bold', ha='center')

# 6. orders -> order_items
ax.annotate("", xy=(5.5, 1.0), xytext=(5.3, 1.0), arrowprops=arrow_style)
ax.text(5.4, 1.1, "1 : N", fontsize=5.8, color='#1e293b', weight='bold', ha='center')

ax.set_xlim(0, 7.1)
ax.set_ylim(0, 3.8)
plt.tight_layout()
plt.savefig('figures/fig2_schema_er.pdf')
plt.savefig('figures/fig2_schema_er.png', dpi=300)
plt.close()
print("Perfect Fig 2 generated!")

# =============================================================================
# 3. FIG 3: Connection State Machine (Wide gaps, zero label-box collisions)
# =============================================================================
fig, ax = plt.subplots(figsize=(7.1, 2.9))
ax.axis('off')

def draw_state(ax, x, y, w, h, s_id, s_name, bullets, bg='#f8fafc', border='#3b82f6'):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04", facecolor=bg, edgecolor=border, linewidth=1.2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h - 0.16, f"State {s_id}: {s_name}", color='#0f172a', weight='bold', fontsize=7.2, ha='center')
    ax.plot([x + 0.1, x + w - 0.1], [y + h - 0.28, y + h - 0.28], color=border, lw=0.6)
    
    curr_y = y + h - 0.42
    for b in bullets:
        ax.text(x + w/2, curr_y, b, color='#334155', fontsize=5.6, ha='center')
        curr_y -= 0.14

# 4 States across top with ample 0.4 gap
w_box = 1.35
h_box = 0.98
y_top = 1.60

draw_state(ax, 0.2, y_top, w_box, h_box, "S0", "Pool Idle",
           ["HikariCP idle buffer", "tau = NULL", "AutoCommit = true", "Clean connection"],
           bg='#f8fafc', border='#64748b')

draw_state(ax, 1.95, y_top, w_box, h_box, "S1", "Tx Initiated",
           ["PlatformTxManager", "AutoCommit = false", "Tx boundary opened", "Physical conn pinned"],
           bg='#fffbeb', border='#f59e0b')

draw_state(ax, 3.70, y_top, w_box, h_box, "S2", "Context Bound",
           ["SET LOCAL app.tenant_id", "is_local = true", "tau = tenant_uuid", "Session isolated"],
           bg='#fef3c7', border='#d97706')

draw_state(ax, 5.45, y_top, w_box, h_box, "S3", "DML Scoped",
           ["Hibernate AST filter", "PostgreSQL forced RLS", "Index scan pushdown", "Atomic execution"],
           bg='#f0fdf4', border='#16a34a')

# 1 State on bottom center
draw_state(ax, 2.7, 0.15, 2.0, 0.98, "S4", "Purge & Sanitize",
           ["COMMIT or ROLLBACK", "PostgreSQL purges GUC", "tau reverts to NULL", "Zero context residual"],
           bg='#fef2f2', border='#dc2626')

# Forward transitions with labels placed cleanly in the gaps ABOVE the arrow
def clean_forward_arrow(ax, x1, x2, y, label):
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="-|>", color='#1e3a8a', lw=1.2, mutation_scale=8))
    ax.text((x1 + x2)/2, y + 0.10, label, fontsize=5.8, color='#1e3a8a', weight='bold', ha='center', va='bottom')

clean_forward_arrow(ax, 1.55, 1.95, y_top + h_box/2, "getConnection()")
clean_forward_arrow(ax, 3.30, 3.70, y_top + h_box/2, "Tx Hook Exec")
clean_forward_arrow(ax, 5.05, 5.45, y_top + h_box/2, "DML Query")

# S3 -> S4: completion
ax.annotate("", xy=(4.7, 0.8), xytext=(5.6, 1.60),
            arrowprops=dict(arrowstyle="-|>", color='#991b1b', lw=1.2, mutation_scale=8))
ax.text(5.3, 1.05, "Tx Completed\n(Commit/Rollback)", fontsize=5.8, color='#991b1b', weight='bold', ha='left', va='center')

# S4 -> S0: return to pool (orthogonal routing completely outside boxes)
ax.plot([2.7, 0.88, 0.88], [0.65, 0.65, 1.60], color='#166534', lw=1.2)
ax.annotate("", xy=(0.88, 1.60), xytext=(0.88, 1.50),
            arrowprops=dict(arrowstyle="-|>", color='#166534', lw=1.2, mutation_scale=8))
ax.text(1.75, 0.75, "Return Sanitized Connection to Pool", fontsize=6.2, color='#166534', weight='bold', ha='center', va='bottom')

ax.set_xlim(0, 7.1)
ax.set_ylim(0, 2.9)
plt.tight_layout()
plt.savefig('figures/fig3_connection_state_machine.pdf')
plt.savefig('figures/fig3_connection_state_machine.png', dpi=300)
plt.close()
print("Perfect Fig 3 generated!")

# =============================================================================
# 4. FIG 4: Throughput Ratio (Breathable margin, non-overlapping legend)
# =============================================================================
df_raw = pd.read_csv('benchmark/results/raw_runs.csv')
micro_workloads = ['Point Lookup', 'Paged List', 'Tenant Count', 'Point Insert']
df_micro = df_raw[df_raw['workload'].isin(micro_workloads)]

fig, ax = plt.subplots(figsize=(3.4, 2.6))
x_positions = {w: i for i, w in enumerate(micro_workloads)}

# Equivalence corridor +/- 5%
ax.axhspan(0.95, 1.05, color='#f1f5f9', alpha=0.9, zorder=1)
ax.axhline(1.0, color='#94a3b8', linestyle='--', linewidth=0.8, zorder=2)

np.random.seed(42)
for w in micro_workloads:
    subset = df_micro[df_micro['workload'] == w]
    ratios = subset['throughput_ratio'].values
    x_idx = x_positions[w]
    jitter = np.random.uniform(-0.11, 0.11, size=len(ratios))
    
    ax.scatter(x_idx + jitter, ratios, color='#2563eb', alpha=0.6, s=15, edgecolors='none', zorder=3)
    
    mean_val = np.mean(ratios)
    ci_low = np.percentile(ratios, 2.5)
    ci_high = np.percentile(ratios, 97.5)
    
    ax.errorbar(x_idx, mean_val, yerr=[[mean_val - ci_low], [ci_high - mean_val]],
                fmt='D', color='#dc2626', ecolor='#dc2626', elinewidth=1.5, capsize=3.5,
                markersize=4.2, zorder=4)

ax.set_xticks(range(len(micro_workloads)))
ax.set_xticklabels(['Point\nLookup', 'Paged\nList', 'Tenant\nCount', 'Point\nInsert'])
ax.set_ylabel('Throughput Ratio (Dual / Base)')
ax.set_ylim(0.40, 1.55)  # Ample space so dots/errorbars never touch legend
ax.grid(True, linestyle=':', alpha=0.5, zorder=0)

corridor_proxy = patches.Patch(facecolor='#f1f5f9', edgecolor='#cbd5e1', label='±5% Equiv Corridor')
parity_proxy = plt.Line2D([0], [0], color='#94a3b8', linestyle='--', label='Parity (1.00)')
scatter_proxy = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2563eb', markersize=4.5, label='Paired Run (n=30)')
mean_proxy = plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='#dc2626', markeredgecolor='#dc2626', markersize=4.5, label='Mean with 95% CI')

ax.legend(handles=[corridor_proxy, parity_proxy, scatter_proxy, mean_proxy], loc='upper left', framealpha=0.92, fontsize=6.6)

plt.tight_layout()
plt.savefig('figures/fig4_benchmark_ratio.pdf')
plt.savefig('figures/fig4_benchmark_ratio.png', dpi=300)
plt.close()
print("Perfect Fig 4 generated!")


# =============================================================================
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
