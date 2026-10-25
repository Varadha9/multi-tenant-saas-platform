#!/usr/bin/env bash
# ==============================================================================
# NexusOps Multi-Tenant Isolation Benchmark Reproduction Suite
# Paper: "Dual-Layer Tenant Isolation in Shared-Schema SaaS:
#         Combining ORM Filters with PostgreSQL Row-Level Security"
# Authors: Ibrahim Poonawala, Varad Mandhare, Tanmay Shinde, Prof. Reetika Kerketta
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCH_DIR="${SCRIPT_DIR}/benchmark"

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5433}"
DB_NAME="${DB_NAME:-nexusops}"
OWNER_USER="${OWNER_USER:-nexusops_owner}"
OWNER_PASSWORD="${OWNER_PASSWORD:-nexusops_owner_local}"
APP_USER="${APP_USER:-nexusops_app}"
APP_PASSWORD="${APP_PASSWORD:-nexusops_app_local}"

export DB_HOST DB_PORT DB_NAME OWNER_USER OWNER_PASSWORD APP_USER APP_PASSWORD

echo "=============================================================================="
echo "    NEXUSOPS EMPIRICAL MULTI-TENANT BENCHMARK REPRODUCTION SUITE"
echo "=============================================================================="

# 1. Connectivity Check
if ! pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" >/dev/null 2>&1; then
    echo "[!] PostgreSQL is not responding on ${DB_HOST}:${DB_PORT}."
    echo "    Please start the database container before executing benchmarks."
    exit 1
fi
echo "[+] PostgreSQL 17 online at ${DB_HOST}:${DB_PORT}/${DB_NAME}"

# 2. Database Schema and Deterministic Data Seeding
echo ""
echo "=== Step 1: Initializing Database Schema & Seeding 1M Records ==="
PGPASSWORD="${OWNER_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -f "${BENCH_DIR}/setup_schema.sql" >/dev/null
echo "[+] Schema created, partitioned records seeded, and RLS policies enforced."

# 3. Real Empirical pgbench Execution
echo ""
echo "=== Step 2: Executing Real Empirical pgbench Workloads (n=30 paired runs) ==="
python3 "${BENCH_DIR}/run_real_benchmark.py"

# 4. Statistical Analysis & TOST Equivalence Testing
echo ""
echo "=== Step 3: Conducting Statistical Analysis & Equivalence Testing ==="
python3 "${BENCH_DIR}/analyze_real.py"

# 5. Figure Generation
echo ""
echo "=== Step 4: Generating Figure 3 Directly from Measured Data ==="
python3 "${SCRIPT_DIR}/generate_figures.py"

echo ""
echo "=============================================================================="
echo "    [SUCCESS] All empirical benchmarks and statistical analyses completed."
echo "    Raw data:    research_paper/benchmark/results/raw_runs.csv"
echo "    Summary:     research_paper/benchmark/results/summary.csv"
echo "    Figure 3:    research_paper/figures/fig3_benchmark_ratio.pdf"
echo "=============================================================================="
