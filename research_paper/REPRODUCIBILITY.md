# Reproducibility Dossier: Dual-Layer Tenant Isolation in Shared-Schema SaaS

This document provides step-by-step instructions, hardware configurations, random seeds, and execution scripts to independently reproduce all empirical results, benchmarks, figures, and security proofs presented in the paper:

> **Dual-Layer Tenant Isolation in Shared-Schema SaaS: Combining ORM Filters with PostgreSQL Row-Level Security**  
> *Ibrahim Poonawala, Varad Mandhare, Tanmay Shinde, Prof. Reetika Kerketta*  
> Repository: [https://github.com/Varadha9/multi-tenant-saas-platform](https://github.com/Varadha9/multi-tenant-saas-platform)

---

## 1. System Baseline and Environment Specifications

All experiments reported in the paper were executed under the following controlled environment:

- **Operating System:** Ubuntu 24.04 LTS (Linux kernel 6.6.137)
- **CPU:** AMD EPYC 7763 (10 assigned vCPUs, 2.45 GHz base / 3.5 GHz boost)
- **Memory:** 16 GB DDR4 RAM
- **Storage:** NVMe PCIe 4.0 SSD (ext4 filesystem, `noatime`)
- **Database Engine:** PostgreSQL 17.11 (`pgvector/pgvector:pg17` Docker container)
- **Application Framework:** Spring Boot 3.4.3 on OpenJDK 21 (Temurin 21.0.6)
- **Connection Pool:** HikariCP 5.1.0 (`maximumPoolSize = 32`, `minimumIdle = 32`)
- **Cache / Distributed State:** Redis 7.2 (Alpine container)

### PostgreSQL 17 Server Configuration (`postgresql.conf`)
```ini
shared_buffers = 4GB
work_mem = 64MB
maintenance_work_mem = 512MB
effective_cache_size = 12GB
synchronous_commit = off
wal_buffers = 16MB
max_connections = 200
plan_cache_mode = auto
```

---

## 2. Reproduction Quick Start

Ensure Docker and Docker Compose are installed and running.

```bash
# 1. Clone repository
git clone https://github.com/Varadha9/multi-tenant-saas-platform.git
cd multi-tenant-saas-platform

# 2. Start PostgreSQL 17 and Redis containers
docker compose -f infra/docker/docker-compose.yml up -d postgres redis

# 3. Wait until healthcheck passes
docker compose -f infra/docker/docker-compose.yml ps
```

---

## 3. Experiment 1: RLS Catalog Guard & Negative Policy Mutation Testing

This experiment verifies Section VI-A and Table III of the manuscript, proving that the build-time catalog guard checks the decompiled AST expressions of both `USING` and `WITH CHECK` clauses and prevents permissive bypasses (such as `WITH CHECK (true)` or `USING (true)`).

### Option A: Standalone Bash Script (No Java/Gradle required)
```bash
cd research_paper
chmod +x verify_policy_guard.sh
./verify_policy_guard.sh
```

**Expected Output:**
```
==============================================================================
    NEXUSOPS RLS CATALOG GUARD: MUTATION & EXPRESSION VERIFICATION
==============================================================================
[+] Connected to PostgreSQL at localhost:5433/nexusops as nexusops_owner

--- Running Deliberate Unsafe Policy Mutation Probes ---
[PASS] Mutation 1: Table without RLS enabled -> DETECTED & BLOCKED
[PASS] Mutation 2: Table without FORCE ROW LEVEL SECURITY -> DETECTED & BLOCKED
[PASS] Mutation 3: Permissive 'WITH CHECK (true)' expression -> DETECTED & BLOCKED
[PASS] Mutation 4: Permissive 'USING (true)' expression -> DETECTED & BLOCKED
[PASS] Mutation 5: Omitted WITH CHECK clause -> DETECTED & BLOCKED
[PASS] Mutation 6: Secondary permissive policy injection -> DETECTED & BLOCKED
[PASS] Baseline: Strict Canonical RLS Policy with FORCE -> VALIDATED (CLEAN)

==============================================================================
    MUTATION TESTING SUMMARY: 6/6 VULNERABILITIES DETECTED (100%)
==============================================================================
[SUCCESS] The PostgreSQL catalog guard prevents all evaluated RLS misconfigurations.
```

### Option B: Integration Test Suite (Full CI Environment)
*(Requires the full application platform source: `git clone https://github.com/Varadha9/nexusops.git`)*
```bash
git clone https://github.com/Varadha9/nexusops.git
cd nexusops/backend
./gradlew test --tests com.nexusops.RlsCoverageIT
```
**Assertion Criteria:** All 4 tests pass (`expectedTenantTablesExist`, `everyDirectTenantTableForcesRlsAndMatchesCanonicalTenantExpression`, `allTablesEnforceRlsUnlessExplicitlyGlobal`, `policyGuardRejectsDeliberatelyUnsafeConfigurations`).

---

## 4. Experiment 2: Performance Microbenchmarks & Statistical TOST

This experiment reproduces Section VII, Table IV, Table V, and Figure 3 of the paper.

### Execution Steps
```bash
cd research_paper

# 1. Run the automated paired benchmark runner (30 paired runs per workload)
chmod +x benchmark_reproduce.sh
./benchmark_reproduce.sh

# 2. Compute Two One-Sided Tests (TOST) statistics and regenerate Figure 3
python3 generate_figures.py
```

### Generated Artifacts
- `benchmark_raw_data.csv`: 120 per-run raw throughput and latency records ($n=30$ paired runs $\times$ 4 workloads).
- `figures/fig3_benchmark_ratio.pdf` & `.png`: Ratio distributions with 95% confidence intervals and $\pm 5\%$ equivalence corridor.
- Summary statistical metrics printed to console:

```
Workload        Base Mean (tps)  Dual Mean (tps)  Ratio Mean  95% CI          TOST p-value  Status
Point Lookup    19845 ± 382      19982 ± 410      1.007       [0.998, 1.016]  7.95e-11      EQUIVALENT
Paged List      7890 ± 145       7784 ± 162       0.987       [0.979, 0.994]  1.89e-11      EQUIVALENT
Tenant Count    4912 ± 98        4865 ± 105       0.990       [0.983, 0.998]  2.85e-12      EQUIVALENT
Point Insert    11240 ± 260      11065 ± 295      0.984       [0.976, 0.993]  1.86e-09      EQUIVALENT
```

---

## 5. Experiment 3: 1,000,000-Request Zero-Leak Security Stress Harness

This experiment reproduces Section V and Property 1–3 verification.

### Test Harness Architecture
- **Workers:** 100 concurrent asynchronous virtual threads / worker tasks.
- **Connection Pool:** 32 physical connections managed by HikariCP.
- **Workload Volume:** 1,000,000 total HTTP / SQL requests executing across 100 distinct tenant workspaces.
- **Context Switches:** 940,000 cross-tenant context transitions across recycled connections.
- **Canary Tokens:** Every persisted record contains a cryptographically signed tenant canary: `canary_{tenant_id}_{uuid}`.
- **Verification Rule:** Every query response is asserted against the originating session tenant. If any record belonging to tenant $j$ is observed in tenant $i$'s response ($i \neq j$), the harness aborts with a security violation.

### Running the Security Stress Suite
```bash
cd backend
./gradlew test --tests com.nexusops.TenantIsolationIT --tests com.nexusops.CanonicalRlsIT
```

### Statistical Upper Bound Formulation (Rule of Three)
Under zero observed failures ($k = 0$) across $n = 1,000,000$ independent trials, the 95% upper confidence bound for failure probability $p$ is derived as:
$$\text{Pr}(\text{zero failures}) = (1 - p)^n \ge 0.05 \implies p \le 1 - 0.05^{1/n} \approx \frac{-\ln(0.05)}{n} \approx \frac{2.996}{1,000,000} \approx 3.0 \times 10^{-6}$$
Under the evaluated operational conditions, the cross-tenant leakage rate is bounded below **$3 \times 10^{-6}$** with 95% statistical confidence.

---

## 6. Manifest of Research Artifacts

| File | Description |
| :--- | :--- |
| `research_paper/main.tex` | IEEE-format LaTeX camera-ready source code (10 pages). |
| `research_paper/main.pdf` | Compiled 10-page camera-ready PDF document. |
| `research_paper/benchmark_reproduce.sh` | Automated shell script for schema generation and pgbench workloads. |
| `research_paper/verify_policy_guard.sh` | Automated negative mutation tester for RLS catalog guards. |
| `research_paper/generate_figures.py` | Python script for TOST statistical testing and Figure 3 plotting. |
| `research_paper/benchmark_raw_data.csv` | Raw empirical data (120 paired measurement runs). |
| `research_paper/figures/fig1_architecture.png` | System deployment and modular architecture diagram. |
| `research_paper/figures/fig2_request_trace.png` | Multi-tenant request lifecycle and context binding trace. |
| `research_paper/figures/fig3_benchmark_ratio.pdf` | High-resolution vector plot of paired throughput ratios ($n=30$). |
| `backend/src/test/java/com/nexusops/RlsCoverageIT.java` | Spring Boot integration test with AST inspection and mutation suites. |
| `backend/src/test/java/com/nexusops/CanonicalRlsIT.java` | Raw database-level RLS boundary verification suite. |
| `backend/src/test/java/com/nexusops/TenantIsolationIT.java` | End-to-end multi-tenant isolation and canary verification suite. |

---

## 7. Contact and Support

For questions regarding artifact reproduction, contact:
- **Varad Mandhare:** [varadmandhare924@gmail.com](mailto:varadmandhare924@gmail.com)
- **GitHub Issues:** [https://github.com/Varadha9/multi-tenant-saas-platform/issues](https://github.com/Varadha9/multi-tenant-saas-platform/issues)
