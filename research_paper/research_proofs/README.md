# NexusOps Research Proofs & Evidence Dossier

> **Academic Project:** NexusOps: A Tenant-Aware Business Operations Platform for Small and Medium Enterprises  
> **Group ID:** LYSMAD05 · B.Tech (Information Technology), MIT School of Computing, MIT ADT University, Pune  
> **Research Lead:** Varad Mandhare (ADT23SOCB1574)  
> **Team Members:** Ibrahim Poonawala (ADT23SOCB1523), Varad Mandhare (ADT23SOCB1574), Tanmay Shinde (ADT23SOCB1617)  
> **Project Guide:** Prof. Reetika Kerketta  
> **Associated Research Paper:** *Isolation Twice, Cost Once: Defense-in-Depth Multi-Tenant Architecture Combining ORM Filters with PostgreSQL Row-Level Security*

---

## Overview

This directory contains the **complete, verifiable evidence trail** of all academic, market, architectural, and experimental research conducted for the NexusOps platform and its IEEE research paper.

Every claim, dataset, pricing calculation, architectural decision, and benchmark number cited in the **Research Paper**, **Project Report**, and **Final Presentation** is proven and cross-referenced in the files below.

---

## Directory Index & Proof Modules

### 📁 [`01_LITERATURE_SURVEY_MAPPING.md`](01_LITERATURE_SURVEY_MAPPING.md)
* **What It Contains:** Complete academic mapping of all **30 Scopus-indexed and IEEE/ACM peer-reviewed papers** cited in the research paper.
* **Details Documented:** Authors, publication venue, Scopus quartile, digital object identifier (DOI), and the exact technical finding integrated into NexusOps (e.g., Panko spreadsheet errors, Chong multi-tenancy models, Force.com metadata engine, Sandhu RBAC, Sastry automated catalog verification).

### 📁 [`02_MARKET_RESEARCH_PROOFS.md`](02_MARKET_RESEARCH_PROOFS.md)
* **What It Contains:** Verified industry data and primary government publications cited in **Section 3.6 of the Project Report** and **Annexure-1/3**.
* **Key Proof Sources:**
  * **Ministry of MSME, Govt. of India (Annual Report 2023-24):** Proves the 63.4 million MSME market size, 30% GDP contribution, and 110M+ employment.
  * **Salesforce, Deloitte, & NASSCOM Research:** Proves that 57% of SMBs are trapped on spreadsheets, and only 1 in 3 Indian SMBs use digital tools.
  * **Enterprise Software Pricing Breakdown:** Direct pricing audits proving Salesforce costs ₹2.75L/mo, Microsoft Dynamics costs ₹1.08L/mo, and SAP requires ₹5–20L implementation—pricing out 20-person businesses.
  * **Capterra Abandonment Survey:** Proves the #1 and #2 reasons SMBs abandon enterprise tools are complexity (44%) and paying for unused bloat (38%).

### 📁 [`03_DAILY_RESEARCH_LOGS.md`](03_DAILY_RESEARCH_LOGS.md)
* **What It Contains:** The chronological archive of the **10 automated daily research investigations** conducted by Varad Mandhare from August 13 to August 22, 2026.
* **Topics & Real-World Evidence Covered:**
  * Rate limiting with Redis token buckets (Stripe case study: 40% reduction in cascading failures).
  * Soft delete vs. hard delete (Martin Fowler patterns & PostgreSQL partial indexing).
  * Connection pool context sanitization (HikariCP lifecycle).
  * Feature flags and runtime module toggles (LaunchDarkly: 97% reduction in MTTR).
  * Transactional outbox & webhooks (Stripe & GitHub webhook signature verification).
  * SaaS churn prevention metrics (Baremetrics & ProfitWell time-to-value benchmarks).

### 📁 [`04_EMPIRICAL_BENCHMARK_PROOFS.md`](04_EMPIRICAL_BENCHMARK_PROOFS.md)
* **What It Contains:** Raw experimental data, hardware parameters, and query plan deconstructions for the **1,000,000-row `pgbench` benchmark**.
* **Key Empirical Evidence:**
  * **Table II Benchmark Measurements:** Mean throughput and latency across 5 randomized paired runs.
  * **`EXPLAIN (ANALYZE, BUFFERS)` Proof Traces:** Proves both Filter-Only and Forced RLS read identical 64 shared buffer pages and plan into identical B-tree index scans.
  * **PostgreSQL Planner Mechanics:** Details why `current_setting()` stability classification (`STABLE`) allows single plan-time evaluation without runtime overhead.
  * **Statistical Significance Testing:** Shows two-sided sign test yields $p = 0.0625$ ($\alpha = 0.05$), proving the $-3.3\%$ to $+2.8\%$ delta is indistinguishable from hardware noise.

---

## How This Proves the PBL Project Deliverables

| Deliverable | Section / Slide | How This Research Dossier Proves It |
|---|---|---|
| **IEEE Research Paper** | Section I, II, V | `01_LITERATURE_SURVEY_MAPPING.md` provides all 30 Scopus references; `04_EMPIRICAL_BENCHMARK_PROOFS.md` provides the 1M-row execution plans. |
| **Project Report** | Section 3.6 & Annexure A | `02_MARKET_RESEARCH_PROOFS.md` documents the exact government and vendor pricing studies credited to Varad Mandhare. |
| **Synopsis (Annexure-3)** | Table 1 (Literature Survey) | `01_LITERATURE_SURVEY_MAPPING.md` maps directly to Table 1 in the submitted synopsis. |
| **Ideation (Annexure-1)** | Empathy Map & Survey | `02_MARKET_RESEARCH_PROOFS.md` provides the empirical evidence for lost messages, overwritten spreadsheets, and pricing barriers. |
| **Final Presentation** | Slides 4, 6, 14, 20, 21 | `03_DAILY_RESEARCH_LOGS.md` and `04_EMPIRICAL_BENCHMARK_PROOFS.md` back up every architectural slide and benchmark graph. |

---

## Benchmark Reproduction Script

To rerun the empirical benchmark on your local PostgreSQL instance:
```bash
cd "/home/varad/projects/Multi-Tenant SaaS/research_paper"
./benchmark_reproduce.sh
```
This script provisions the tables, generates the 1,000,000 tuples across 100 tenants, and executes the `pgbench` test suites.
