# Empirical Benchmark Proofs & Execution Plan Deconstructions

> **Project:** NexusOps: A Tenant-Aware Business Operations Platform for Small and Medium Enterprises  
> **Evaluated By:** Ibrahim Poonawala & Varad Mandhare  
> **Hardware Host:** Apple M4 Silicon (10 Cores, 16 GB Unified Memory)  
> **Database Engine:** PostgreSQL 17.11 inside containerized Linux (allocated 10 vCPUs, 8 GB RAM)  
> **Benchmark Tooling:** `pgbench` in prepared-statement mode (`-M prepared`)  
> **Dataset Scale:** 1,000,000 tuples partitioned across 100 deterministic tenants (10,000 records / tenant)

---

## 1. Summary of Benchmark Measurements (Table II Proofs)

Measurements represent the arithmetic mean and sample standard deviation across 5 randomized paired repetitions (30 seconds per run, preceded by a 5-second warm-up, utilizing 8 concurrent clients across 4 worker threads):

| Workload | Single-Layer Filter-Only (tps) | Dual-Layer Forced RLS (tps) | Measured Delta ($\Delta$) | Mean Latency (Filter / RLS) | Statistical Significance ($p$-value) |
|---|---|---|---|---|---|
| **Point Lookup (Primary Key)** | $19,722 \pm 2,419$ | $20,273 \pm 2,281$ | **$+2.8\%$** | $0.411$\,ms / $0.399$\,ms | $p = 0.0625$ (Not Significant) |
| **Paged List (20 sorted rows)** | $7,956 \pm 496$ | $7,692 \pm 669$ | **$-3.3\%$** | $1.009$\,ms / $1.047$\,ms | $p = 0.0625$ (Not Significant) |
| **Tenant Count (Full Partition)** | $4,930 \pm 526$ | $4,876 \pm 521$ | **$-1.1\%$** | $1.639$\,ms / $1.656$\,ms | $p = 0.0625$ (Not Significant) |

### Key Observation:
* The run-to-run variation across identical hardware runs was **$6\%$ to $12\%$**.
* Because the measured differences between Filter-Only and Forced RLS ($-3.3\%$ to $+2.8\%$) are smaller than the run-to-run hardware variance, the database layer adds **zero cost that can be reliably distinguished from measurement noise**.

---

## 2. Query Execution Plan Deconstructions (`EXPLAIN ANALYZE BUFFERS`)

The following raw query plan traces prove why PostgreSQL Row-Level Security achieves performance parity with manual application-tier filters.

### A. Tenant Count Query Plan Proof

#### 1. Filter-Only Table (`bench_filter`):
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT count(*) FROM bench_filter 
WHERE tenant_id = 'c4ca4238-a0b9-3382-8dcc-509a6f75849b'::uuid;
```
**Execution Output:**
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

#### 2. Forced RLS Table (`bench_rls`):
```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT count(*) FROM bench_rls;
```
**Execution Output:**
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

### Architectural & Mathematical Proof:
1. **Shared Buffer Parity:** Both variants read exactly **64 shared buffer pages** (`shared hit=64`). RLS reads zero additional pages.
2. **Stable Function Plan-Time Evaluation:** In PostgreSQL, `current_setting()` is marked with volatility classification `STABLE`. A stable function cannot modify the database and is guaranteed to return identical results for the same arguments within a single table scan.
3. **Index Scan Conversion:** Because `current_setting()` is stable, the PostgreSQL query planner evaluates `nullif(current_setting(...), '')::uuid` **once** at statement initiation, converting it into a constant value. The optimizer then plans an **Index-Only Scan** over the B-tree composite index `(tenant_id, name)` identically to a literal constant.
4. **Prepared Statement Amortization:** While the initial parse/plan time was slightly higher for the RLS expression (0.97 ms vs 0.47 ms), prepared statements amortize this cost after the 5th execution, making steady-state throughput identical.

---

## 3. Statistical Significance Testing (Two-Sided Sign Test)

To evaluate whether the minor offsets (Point lookups slightly favoring RLS, Paged lists slightly favoring Filter-Only) represent a genuine architectural difference or noise:

* **Hypothesis $H_0$:** The median difference in throughput between Forced RLS and Filter-Only is zero ($\text{Median}(\Delta) = 0$).
* **Alternative $H_1$:** The median difference is non-zero.
* **Sample Size:** $n = 5$ paired repetitions.
* **Sign Test Calculation:** Even if all 5 repetitions agree in sign ($k = 5$ positive or negative differences), the two-sided binomial probability is:
  $$p = 2 \times \left(\frac{1}{2}\right)^5 = 2 \times \frac{1}{32} = \frac{1}{16} = 0.0625$$
* **Conclusion:** Since $p = 0.0625 > \alpha = 0.05$, the null hypothesis $H_0$ cannot be rejected. There is no statistically significant performance difference between single-layer ORM filtering and dual-layer forced RLS.

---

## 4. How to Reproduce Locally

The full reproduction automation script is available at:  
[`/home/varad/projects/Multi-Tenant SaaS/research_paper/benchmark_reproduce.sh`](file:///home/varad/projects/Multi-Tenant%20SaaS/research_paper/benchmark_reproduce.sh)

Run with:
```bash
cd "/home/varad/projects/Multi-Tenant SaaS/research_paper"
./benchmark_reproduce.sh
```
This generates the tables, inserts the 1M rows, and generates the `pgbench` scripts.
