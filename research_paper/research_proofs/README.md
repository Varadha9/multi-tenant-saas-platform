# NexusOps Research Proofs & Evidence Dossier

> **Academic Project:** NexusOps: A Tenant-Aware Business Operations Platform for Small and Medium Enterprises  
> **Group ID:** LYSMAD05 · B.Tech (Information Technology), MIT School of Computing, MIT ADT University, Pune  
> **Research Lead:** Varad Mandhare (ADT23SOCB1574)  
> **Team Members:** Ibrahim Poonawala (ADT23SOCB1523), Varad Mandhare (ADT23SOCB1574), Tanmay Shinde (ADT23SOCB1617)  
> **Project Guide:** Prof. Reetika Kerketta  
> **Associated Camera-Ready Research Paper:** *Dual-Layer Tenant Isolation in Shared-Schema SaaS: Combining ORM Filters with PostgreSQL Row-Level Security* (10 Pages, IEEE Format)  
> **Repository:** [https://github.com/Varadha9/multi-tenant-saas-platform](https://github.com/Varadha9/multi-tenant-saas-platform)  

---

## Overview

This directory contains the **complete, verifiable evidence trail** of all academic, market, architectural, and experimental research conducted for the NexusOps platform and its IEEE research paper.

Every claim, dataset, pricing calculation, architectural decision, and benchmark number cited in the **Research Paper**, **Project Report**, and **Final Presentation** is proven and cross-referenced in the files below.

---

## Directory Index & Proof Modules

### 📁 [`01_LITERATURE_SURVEY_MAPPING.md`](01_LITERATURE_SURVEY_MAPPING.md)
* **What It Contains:** Complete academic mapping of all **37 Scopus-indexed and IEEE/ACM peer-reviewed papers** cited in the research paper.
* **Details Documented:** Authors, publication venue, Scopus quartile, digital object identifier (DOI), and the exact technical finding integrated into NexusOps (e.g., Panko spreadsheet errors, Chong multi-tenancy models, Aulbach schema mapping, Sandhu RBAC, Stonebraker query modification, Hanley Rule-of-Three, Georges Java benchmarking, Schuirmann/Lakens TOST equivalence testing).

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
  * Connection pool context sanitization (HikariCP lifecycle and `set_config` transaction scoping).
  * Feature flags and runtime module toggles (LaunchDarkly: 97% reduction in MTTR).
  * Transactional outbox & webhooks (Stripe & GitHub webhook signature verification).
  * SaaS churn prevention metrics (Baremetrics & ProfitWell time-to-value benchmarks).

### 📁 [`04_EMPIRICAL_BENCHMARK_PROOFS.md`](04_EMPIRICAL_BENCHMARK_PROOFS.md)
* **What It Contains:** Raw experimental data, hardware parameters, query plan deconstructions, and statistical derivations for the **1,000,000-row benchmark suite**.
* **Key Empirical Evidence:**
  * **Primary Microbenchmarks ($n = 30$ paired runs):** Point Lookup, Paged List, Tenant Count, Point Insert.
  * **Two One-Sided Tests (TOST):** Statistically proves equivalence within an enterprise $\pm 5\%$ margin ($p < 10^{-8}$).
  * **Complex Workloads:** Multi-table relational graph joins (2-table and 3-table), heavy-tailed Pareto 80/20 tenant size skew, and connection pool saturation (8, 32, 128 clients).
  * **Query Plan Equivalence:** Proves both Filter-Only and Forced RLS read identical 64 shared buffer pages (`shared hit=64`) under stable plan-time function evaluation.
  * **1M-Request Security Stress Harness:** 100 workers, 32 connections, 940k context switches, canary tokens, zero observed leaks, yielding a 95% Rule-of-Three upper confidence bound of **$3.0 \times 10^{-6}$**.
  * **Automated Policy Guard Mutation Testing:** 6 deliberate unsafe configurations blocked with a **100% detection rate**.

---

## How This Proves the PBL Project Deliverables

| Deliverable | Section / Slide | How This Research Dossier Proves It |
|---|---|---|
| **IEEE Research Paper** | Section I, II, IV, VI, VII | `01_LITERATURE_SURVEY_MAPPING.md` provides all 37 Scopus references; `04_EMPIRICAL_BENCHMARK_PROOFS.md` provides the 1M-row execution plans, TOST tests, and mutation proofs. |
| **Project Report** | Section 3.6 & Annexure A | `02_MARKET_RESEARCH_PROOFS.md` documents the exact government and vendor pricing studies credited to Varad Mandhare. |
| **Synopsis (Annexure-3)** | Table 1 (Literature Survey) | `01_LITERATURE_SURVEY_MAPPING.md` maps directly to Table 1 in the submitted synopsis. |
| **Ideation (Annexure-1)** | Empathy Map & Survey | `02_MARKET_RESEARCH_PROOFS.md` provides the empirical evidence for lost messages, overwritten spreadsheets, and pricing barriers. |
| **Final Presentation** | Slides 4, 6, 14, 20, 21 | `03_DAILY_RESEARCH_LOGS.md` and `04_EMPIRICAL_BENCHMARK_PROOFS.md` back up every architectural slide and benchmark graph. |

---

## Local Reproduction Tooling

The complete artifact reproduction suite is available in the parent directory:
* [`../REPRODUCIBILITY.md`](../REPRODUCIBILITY.md) — Comprehensive step-by-step reproduction guide.
* [`../benchmark_reproduce.sh`](../benchmark_reproduce.sh) — Automated schema generator and pgbench harness.
* [`../verify_policy_guard.sh`](../verify_policy_guard.sh) — Standalone negative mutation policy tester.
* [`../generate_figures.py`](../generate_figures.py) — TOST statistical analyzer and Figure 3 plotter.
* [`../benchmark_raw_data.csv`](../benchmark_raw_data.csv) — 120 per-run raw measurement records.
