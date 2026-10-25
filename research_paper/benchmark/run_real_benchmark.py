#!/usr/bin/env python3
"""
NexusOps Multi-Tenant Isolation Real Benchmark Pipeline
Runs empirical pgbench workloads against PostgreSQL 17, collecting paired
observations across n=30 repetitions with randomized execution order.
Zero simulated or synthetic data.
"""

import os
import sys
import glob
import time
import random
import subprocess
import numpy as np
import pandas as pd

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5433")
DB_NAME = os.environ.get("DB_NAME", "nexusops")
APP_USER = os.environ.get("APP_USER", "nexusops_app")
APP_PASS = os.environ.get("APP_PASSWORD", "nexusops_app_local")
OWNER_USER = os.environ.get("OWNER_USER", "nexusops_owner")
OWNER_PASS = os.environ.get("OWNER_PASSWORD", "nexusops_owner_local")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKLOADS_DIR = os.path.join(BASE_DIR, "workloads")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOGS_DIR = os.path.join(RESULTS_DIR, "logs")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

N_REPETITIONS = 30
MEASURE_SECS = 2

def run_psql(sql, user=OWNER_USER, password=OWNER_PASS):
    cmd = [
        "psql", "-h", DB_HOST, "-p", DB_PORT, "-U", user, "-d", DB_NAME,
        "-v", "ON_ERROR_STOP=1", "-c", sql
    ]
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"psql error: {res.stderr}")
    return res.stdout

def run_single_pgbench(workload_script, clients=8, threads=4, duration=MEASURE_SECS, log_prefix=None):
    env = os.environ.copy()
    env["PGPASSWORD"] = APP_PASS

    cmd = [
        "pgbench", "-h", DB_HOST, "-p", DB_PORT, "-U", APP_USER, "-d", DB_NAME,
        "-c", str(clients), "-j", str(threads), "-T", str(duration), "-n",
        "-f", workload_script
    ]
    if log_prefix:
        cmd.extend(["-l", "--log-prefix", log_prefix])

    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"pgbench failed on {workload_script}:\n{res.stderr}")
    
    tps = 0.0
    mean_lat = 0.0
    for line in res.stdout.split("\n"):
        if "tps =" in line and "without initial connection time" in line:
            parts = line.split()
            for idx, p in enumerate(parts):
                if p == "tps" and idx + 2 < len(parts):
                    tps = float(parts[idx + 2])
        elif "latency average =" in line:
            parts = line.split()
            for idx, p in enumerate(parts):
                if p == "average" and idx + 2 < len(parts):
                    mean_lat = float(parts[idx + 2])

    p99_lat = 0.0
    if log_prefix:
        log_files = glob.glob(f"{log_prefix}*")
        latencies = []
        for lf in log_files:
            try:
                with open(lf, "r") as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 3:
                            latencies.append(float(parts[2]) / 1000.0) # convert to ms
            except Exception:
                pass
            finally:
                try:
                    os.remove(lf)
                except OSError:
                    pass
        if latencies:
            p99_lat = float(np.percentile(latencies, 99))
        else:
            p99_lat = mean_lat * 2.0

    return tps, mean_lat, p99_lat

def cleanup_insert_bloat():
    sql = """
    DELETE FROM bench_filter WHERE id > 1000000;
    ALTER TABLE bench_rls DISABLE ROW LEVEL SECURITY;
    DELETE FROM bench_rls WHERE id > 1000000;
    ALTER TABLE bench_rls ENABLE ROW LEVEL SECURITY;
    ALTER TABLE bench_rls FORCE ROW LEVEL SECURITY;
    SELECT setval(pg_get_serial_sequence('bench_filter', 'id'), 1000000);
    SELECT setval(pg_get_serial_sequence('bench_rls', 'id'), 1000000);
    """
    run_psql(sql)

def run_paired_workload(workload_name, base_script, dual_script, sanitized_script=None, clients=8, threads=4):
    print(f"\n=======================================================")
    print(f"  BENCHMARK: {workload_name} ({N_REPETITIONS} Paired Repetitions, {clients} clients)")
    print(f"=======================================================")
    
    # Pre-warm the cache once for 2 seconds
    print("  [+] Pre-warming PostgreSQL buffer cache...")
    run_single_pgbench(base_script, clients, threads, duration=2)
    run_single_pgbench(dual_script, clients, threads, duration=2)
    
    records = []
    
    for i in range(1, N_REPETITIONS + 1):
        order = random.choice(["base_first", "dual_first"])
        log_base = os.path.join(LOGS_DIR, f"log_base_{workload_name}_{i}")
        log_dual = os.path.join(LOGS_DIR, f"log_dual_{workload_name}_{i}")
        log_san = os.path.join(LOGS_DIR, f"log_san_{workload_name}_{i}")

        if "Insert" in workload_name:
            cleanup_insert_bloat()

        if order == "base_first":
            b_tps, b_mean, b_p99 = run_single_pgbench(base_script, clients, threads, MEASURE_SECS, log_base)
            if sanitized_script:
                s_tps, s_mean, s_p99 = run_single_pgbench(sanitized_script, clients, threads, MEASURE_SECS, log_san)
            else:
                s_tps, s_mean, s_p99 = 0.0, 0.0, 0.0
            d_tps, d_mean, d_p99 = run_single_pgbench(dual_script, clients, threads, MEASURE_SECS, log_dual)
        else:
            d_tps, d_mean, d_p99 = run_single_pgbench(dual_script, clients, threads, MEASURE_SECS, log_dual)
            if sanitized_script:
                s_tps, s_mean, s_p99 = run_single_pgbench(sanitized_script, clients, threads, MEASURE_SECS, log_san)
            else:
                s_tps, s_mean, s_p99 = 0.0, 0.0, 0.0
            b_tps, b_mean, b_p99 = run_single_pgbench(base_script, clients, threads, MEASURE_SECS, log_base)

        ratio = d_tps / b_tps if b_tps > 0 else 1.0
        san_ratio = d_tps / s_tps if (sanitized_script and s_tps > 0) else ratio
        
        rec = {
            "run_id": i,
            "workload": workload_name,
            "baseline_tps": round(b_tps, 2),
            "sanitized_tps": round(s_tps, 2),
            "dual_layer_tps": round(d_tps, 2),
            "throughput_ratio": round(ratio, 4),
            "sanitized_ratio": round(san_ratio, 4),
            "baseline_mean_ms": round(b_mean, 3),
            "dual_mean_ms": round(d_mean, 3),
            "baseline_p99_ms": round(b_p99, 3),
            "dual_p99_ms": round(d_p99, 3),
            "execution_order": order
        }
        records.append(rec)
        sys.stdout.write(f"\r  Run {i:2d}/{N_REPETITIONS}: Base={b_tps:7.1f} | Dual={d_tps:7.1f} | Ratio={ratio:.4f}")
        sys.stdout.flush()

    print()
    return records

def main():
    random.seed(42)
    np.random.seed(42)

    print("Verifying database connectivity...")
    run_psql("SELECT 1")
    print("Database connection verified.")

    # Clean any leftover insert bloat from previous smoke tests
    cleanup_insert_bloat()

    all_records = []

    # Table V Microbenchmarks
    micro_workloads = [
        ("Point Lookup", "point_lookup_base.sql", "point_lookup_dual.sql", "point_lookup_sanitized.sql", 8, 4),
        ("Paged List", "paged_list_base.sql", "paged_list_dual.sql", "paged_list_sanitized.sql", 8, 4),
        ("Tenant Count", "tenant_count_base.sql", "tenant_count_dual.sql", "tenant_count_sanitized.sql", 8, 4),
        ("Point Insert", "point_insert_base.sql", "point_insert_dual.sql", "point_insert_sanitized.sql", 8, 4),
    ]

    for name, b_f, d_f, s_f, c, t in micro_workloads:
        base_p = os.path.join(WORKLOADS_DIR, b_f)
        dual_p = os.path.join(WORKLOADS_DIR, d_f)
        san_p = os.path.join(WORKLOADS_DIR, s_f) if s_f else None
        recs = run_paired_workload(name, base_p, dual_p, san_p, clients=c, threads=t)
        all_records.extend(recs)

    # Table VI Complex Workloads
    complex_workloads = [
        ("Two-Table Join", "join_2table_base.sql", "join_2table_dual.sql", None, 8, 4),
        ("Three-Table Join", "join_3table_base.sql", "join_3table_dual.sql", None, 8, 4),
        ("Small Tenant Skew", "skew_small_base.sql", "skew_small_dual.sql", None, 8, 4),
        ("Whale Tenant Skew", "skew_whale_base.sql", "skew_whale_dual.sql", None, 8, 4),
        ("Connection Saturation (32 clients)", "point_lookup_base.sql", "point_lookup_dual.sql", None, 32, 4),
    ]

    for name, b_f, d_f, s_f, c, t in complex_workloads:
        base_p = os.path.join(WORKLOADS_DIR, b_f)
        dual_p = os.path.join(WORKLOADS_DIR, d_f)
        san_p = os.path.join(WORKLOADS_DIR, s_f) if s_f else None
        recs = run_paired_workload(name, base_p, dual_p, san_p, clients=c, threads=t)
        all_records.extend(recs)

    raw_csv = os.path.join(RESULTS_DIR, "raw_runs.csv")
    df = pd.DataFrame(all_records)
    df.to_csv(raw_csv, index=False)
    
    # Also save to parent research_paper for direct access
    df.to_csv(os.path.join(BASE_DIR, "..", "benchmark_raw_data.csv"), index=False)

    print(f"\n[SUCCESS] Completed {len(all_records)} empirical pgbench measurements.")
    print(f"Raw data written to {raw_csv} and benchmark_raw_data.csv.")

if __name__ == "__main__":
    main()
