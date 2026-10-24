# Empirical Benchmark Proofs & Execution Plan Deconstructions

> **Project:** NexusOps: A Tenant-Aware Business Operations Platform for Small and Medium Enterprises  
> **Authors:** Ibrahim Poonawala, Varad Mandhare, Tanmay Shinde, Prof. Reetika Kerketta  
> **Paper Title:** *Dual-Layer Tenant Isolation in Shared-Schema SaaS: Combining ORM Filters with PostgreSQL Row-Level Security*  
> **Hardware Host:** AMD EPYC 7763 (10 assigned vCPUs, 16 GB DDR4 RAM, NVMe PCIe 4.0 SSD)  
> **Database Engine:** PostgreSQL 17.11 (`pgvector/pgvector:pg17` container on Linux kernel 6.6)  
> **Benchmark Tooling:** `pgbench` in prepared-statement mode (`-M prepared`)  
> **Dataset Scale:** 1,000,000 tuples partitioned across 100 deterministic tenants (10,000 records / tenant)  
> **Paired Sample Size:** $n = 30$ randomized paired repetitions per workload  

---

## 1. Summary of Primary Benchmark Measurements ($n = 30$ Paired Runs)

Following rigorous systems benchmarking methodology (Georges et al. 2007, Kalibera & Jones 2013, Mytkowicz et al. 2009), all measurements represent arithmetic means, sample standard deviations, 95% confidence intervals, and tail latencies across $n = 30$ randomized paired repetitions. Each run executed for 30 seconds preceded by a 10-second warm-up, utilizing 8 concurrent clients across 4 worker threads over Unix domain sockets:

| Workload | Filter Baseline (tps) | Filter + Sanitized (tps) | Dual-Layer RLS (tps) | Throughput Ratio (Dual / Base) | 95% Confidence Interval | Two One-Sided Tests (TOST, $\pm 5\%$) | Mean Latency (Base / Dual) | p99 Latency (Base / Dual) |
|---|---|---|---|---|---|---|---|---|
| **Point Lookup** | $19,845 \pm 382$ | $19,610 \pm 395$ | $19,982 \pm 410$ | **$1.007$** | $[0.998, 1.016]$ | **Equivalent** ($p = 7.95 \times 10^{-11}$) | $0.40$ / $0.40$\,ms | $0.88$ / $0.89$\,ms |
| **Paged List (20 rows)** | $7,890 \pm 145$ | $7,812 \pm 150$ | $7,784 \pm 162$ | **$0.987$** | $[0.979, 0.994]$ | **Equivalent** ($p = 1.89 \times 10^{-11}$) | $1.01$ / $1.03$\,ms | $2.14$ / $2.18$\,ms |
| **Tenant Count** | $4,912 \pm 98$ | $4,880 \pm 102$ | $4,865 \pm 105$ | **$0.990$** | $[0.983, 0.998]$ | **Equivalent** ($p = 2.85 \times 10^{-12}$) | $1.63$ / $1.64$\,ms | $3.42$ / $3.45$\,ms |
| **Point Insert** | $11,240 \pm 260$ | $11,115 \pm 275$ | $11,065 \pm 295$ | **$0.984$** | $[0.976, 0.993]$ | **Equivalent** ($p = 1.86 \times 10^{-9}$) | $0.71$ / $0.72$\,ms | $1.52$ / $1.56$\,ms |

### Key Empirical Findings:
1. **Bounded Runtime Overhead ($\le 1.6\%$):** The standalone cost of executing transaction-scoped `set_config('app.tenant_id', ?, true)` was measured at $0.038 \pm 0.004$\,ms. This accounts for the minor $\sim 1.2\%$ throughput delta in the Filter + Sanitized variant.
2. **Equivalence Bounds:** All four 95% confidence intervals fall strictly within the enterprise SaaS Service Level Objective (SLO) equivalence corridor $[\theta_L = 0.95, \theta_U = 1.05]$.
3. **Statistical Power:** Sensitivity analysis confirms statistical power $(1 - \beta) > 0.999$ at $\alpha = 0.05$ with $n = 30$ to detect a 5% deviation. Standardized effect sizes yielded Cohen's $d < 0.20$ across all conditions (negligible effect size).

---

## 2. Statistical Equivalence Testing Formulation (TOST)

Rather than relying on underpowered null hypothesis testing ($p > 0.05$), we applied Two One-Sided Tests (TOST) for equivalence (Schuirmann 1987, Lakens 2018):

$$\mathcal{H}_{01}: \mu_z \le \ln(0.95) \quad \text{versus} \quad \mathcal{H}_{11}: \mu_z > \ln(0.95)$$
$$\mathcal{H}_{02}: \mu_z \ge \ln(1.05) \quad \text{versus} \quad \mathcal{H}_{12}: \mu_z < \ln(1.05)$$

Where $z_i = \ln(\text{Throughput}_{\text{Dual}, i} / \text{Throughput}_{\text{Base}, i})$. Rejection of both null hypotheses at $\alpha = 0.05$ demonstrates equivalence within the $\pm 5\%$ margin:

* **Point Lookup:** $t_1 = 12.38$ ($p < 10^{-10}$), $t_2 = -8.76$ ($p < 10^{-10}$) $\implies p_{\text{TOST}} = 7.95 \times 10^{-11}$ (**Equivalent**)
* **Paged List:** $t_1 = 9.14$ ($p < 10^{-10}$), $t_2 = -15.42$ ($p < 10^{-11}$) $\implies p_{\text{TOST}} = 1.89 \times 10^{-11}$ (**Equivalent**)
* **Tenant Count:** $t_1 = 10.82$ ($p < 10^{-11}$), $t_2 = -16.20$ ($p < 10^{-12}$) $\implies p_{\text{TOST}} = 2.85 \times 10^{-12}$ (**Equivalent**)
* **Point Insert:** $t_1 = 7.42$ ($p < 10^{-9}$), $t_2 = -14.11$ ($p < 10^{-11}$) $\implies p_{\text{TOST}} = 1.86 \times 10^{-9}$ (**Equivalent**)

---

## 3. Complex Workload Evaluations: Joins, Skew, and Concurrency Saturation

Enterprise multi-tenant platforms depart from uniform single-table access across three operational dimensions. We evaluated $n = 30$ paired runs under each regime:

| Workload Dimension | Filter Baseline (tps) | Dual-Layer RLS (tps) | Throughput Ratio | TOST $p$-value | Equivalence Status |
|---|---|---|---|---|---|
| **Two-Table Join (`parties` $\bowtie$ `party_roles`)** | $6,420 \pm 115$ | $6,345 \pm 122$ | **$0.988$** $[0.981, 0.995]$ | $4.85 \times 10^{-11}$ | **Equivalent** ($\pm 5\%$) |
| **Three-Table Join ($\bowtie$ `activities`)** | $4,215 \pm 88$ | $4,162 \pm 94$ | **$0.987$** $[0.980, 0.994]$ | $3.12 \times 10^{-10}$ | **Equivalent** ($\pm 5\%$) |
| **Small Tenant (0.05% rows, 500 records)** | $21,120 \pm 410$ | $21,050 \pm 425$ | **$0.997$** $[0.988, 1.006]$ | $6.21 \times 10^{-12}$ | **Equivalent** ($\pm 5\%$) |
| **Whale Tenant (25.0% rows, 250k records)** | $16,840 \pm 310$ | $16,610 \pm 330$ | **$0.986$** $[0.978, 0.994]$ | $1.05 \times 10^{-9}$ | **Equivalent** ($\pm 5\%$) |
| **8 Clients (Under-subscribed)** | $19,845 \pm 382$ | $19,982 \pm 410$ | **$1.007$** $[0.998, 1.016]$ | $7.95 \times 10^{-11}$ | **Equivalent** ($\pm 5\%$) |
| **32 Clients (Pool Saturation Boundary)** | $38,420 \pm 620$ | $38,110 \pm 650$ | **$0.992$** $[0.985, 0.999]$ | $2.44 \times 10^{-11}$ | **Equivalent** ($\pm 5\%$) |
| **128 Clients (4$\times$ Pool Oversubscribed)** | $36,250 \pm 780$ | $35,890 \pm 810$ | **$0.990$** $[0.981, 0.999]$ | $5.18 \times 10^{-9}$ | **Equivalent** ($\pm 5\%$) |

### Architectural Insights:
1. **Foreign Key Pushdown:** In multi-table joins, composite foreign keys `(tenant_id, parent_id)` allow the query planner to push the stable tenant predicate directly into each index scan branch, executing Nested Loop Inner Index Scans without cross-table hash spills.
2. **Heavy-Tailed Tenant Skew:** Under an 80/20 Pareto distribution, B-tree depth remains fixed at 3 levels across both small (500 records) and whale (250k records) partitions, preserving $>99.8\%$ shared buffer hit rates.
3. **Queue Latency Dominance:** At 128 clients against 32 HikariCP connections, connection wait time accounts for 82% of total transaction latency ($14.2$\,ms), completely dwarfing database-tier RLS overhead ($0.038$\,ms) by **$350\times$**.

---

## 4. Query Execution Plan Deconstructions (`EXPLAIN ANALYZE BUFFERS`)

### A. Tenant Count Query Plan Proof

#### 1. Filter-Only Baseline Table (`bench_filter`):
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT count(*) FROM bench_filter 
WHERE tenant_id = 'c4ca4238-a0b9-3382-8dcc-509a6f75849b'::uuid;
```
```
Aggregate  (cost=184.25..184.26 rows=1 width=8) (actual time=1.412..1.413 rows=1 loops=1)
  Output: count(*)
  Buffers: shared hit=64
  ->  Index Only Scan using idx_bench_filter_tenant_name on public.bench_filter  
        (cost=0.42..159.25 rows=10000 width=0) (actual time=0.021..0.892 rows=10000 loops=1)
        Output: tenant_id, name
        Index Cond: (bench_filter.tenant_id = 'c4ca4238-a0b9-3382-8dcc-509a6f75849b'::uuid)
        Heap Fetches: 0
        Buffers: shared hit=64
Planning Time: 0.471 ms
Execution Time: 1.442 ms
```

#### 2. Dual-Layer Forced RLS Table (`bench_rls`):
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT count(*) FROM bench_rls;
```
```
Aggregate  (cost=184.25..184.26 rows=1 width=8) (actual time=1.428..1.429 rows=1 loops=1)
  Output: count(*)
  Buffers: shared hit=64
  ->  Index Only Scan using idx_bench_rls_tenant_name on public.bench_rls  
        (cost=0.42..159.25 rows=10000 width=0) (actual time=0.024..0.910 rows=10000 loops=1)
        Output: tenant_id, name
        Index Cond: (bench_rls.tenant_id = (nullif(current_setting('app.tenant_id'::text, true), ''::text))::uuid)
        Heap Fetches: 0
        Buffers: shared hit=64
Planning Time: 0.972 ms
Execution Time: 1.458 ms
```

### Plan Equivalence Proof:
* **Buffer Hits:** Both variants read exactly **64 shared buffer pages** (`shared hit=64`). RLS reads zero additional buffer pages.
* **Scan Type:** Both plans execute an **Index-Only Scan** on the composite B-tree index `(tenant_id, name)`.
* **Volatility Classification:** `current_setting()` is declared `STABLE` in PostgreSQL. Stable functions are evaluated once at scan startup, allowing the planner to treat the runtime tenant identity as an executor constant.

---

## 5. Security Stress Test Proof (1,000,000 Requests, Zero Leaks)

The security verification harness (`TenantIsolationIT`) subjected the dual-layer architecture to extreme concurrency stress:

* **Concurrency:** 100 concurrent asynchronous virtual threads.
* **Connection Pool:** 32 physical connections managed by HikariCP.
* **Total Volume:** 1,000,000 total HTTP / SQL operations across 100 tenants.
* **Context Transitions:** 940,000 cross-tenant context switches over recycled pool connections.
* **Canary Verification:** Every entity persists a unique cryptographic canary: `canary_{tenant_id}_{uuid}`.
* **Observed Leaks:** **$k = 0$ cross-tenant leakages.**

### Rule of Three Upper Confidence Bound:
Under zero observed failures ($k = 0$) across $n = 1,000,000$ independent trials, the 95% upper confidence bound for failure probability $p$ is derived as (Hanley & Lippman-Hand 1983):
$$p \le \frac{-\ln(0.05)}{n} \approx \frac{2.996}{1,000,000} \approx \mathbf{3.0 \times 10^{-6}}$$
Under the evaluated operational conditions, cross-tenant leakage probability is bounded below **$3 \times 10^{-6}$** with 95% confidence.

---

## 6. Catalog Guard & Negative Policy Mutation Verification Proof

To prove that the build-time catalog guard checks the actual AST expressions and rejects permissive bypasses, we executed 6 deliberate negative mutations against an ephemeral probe table (`RlsCoverageIT` and `verify_policy_guard.sh`):

1. **Mutation 1:** Table without RLS enabled $\rightarrow$ **Blocked**
2. **Mutation 2:** Table with RLS enabled but not forced $\rightarrow$ **Blocked**
3. **Mutation 3:** Permissive `WITH CHECK (true)` bypass $\rightarrow$ **Blocked**
4. **Mutation 4:** Permissive `USING (true)` bypass $\rightarrow$ **Blocked**
5. **Mutation 5:** Omitted `WITH CHECK` clause $\rightarrow$ **Blocked**
6. **Mutation 6:** Permissive secondary policy injection $\rightarrow$ **Blocked**
7. **Safe Baseline:** Canonical policy with `FORCE ROW LEVEL SECURITY` $\rightarrow$ **Clean Pass**

**Detection Rate: 6/6 vulnerabilities detected (100% detection rate).**

---

## 7. Artifact Manifest & Reproduction Scripts

All raw data and reproduction runners are committed to GitHub:
- **Raw Data (120 paired runs):** [`research_paper/benchmark_raw_data.csv`](../benchmark_raw_data.csv)
- **Automated Benchmark Runner:** [`research_paper/benchmark_reproduce.sh`](../benchmark_reproduce.sh)
- **Policy Mutation Tester:** [`research_paper/verify_policy_guard.sh`](../verify_policy_guard.sh)
- **Figure & TOST Generator:** [`research_paper/generate_figures.py`](../generate_figures.py)
- **Reproducibility Guide:** [`research_paper/REPRODUCIBILITY.md`](../REPRODUCIBILITY.md)
