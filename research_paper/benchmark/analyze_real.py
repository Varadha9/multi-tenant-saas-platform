#!/usr/bin/env python3
"""
Statistical Analysis of Real Empirical pgbench Data
Calculates TOST equivalence, Cohen's d, Shapiro-Wilk, autocorrelation,
and bootstrap confidence intervals directly from measured raw_runs.csv.
"""

import os
import sys
import numpy as np
import pandas as pd
import scipy.stats as stats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
RAW_CSV = os.path.join(RESULTS_DIR, "raw_runs.csv")

def bootstrap_ci(data, n_boot=10000, alpha=0.05):
    boot_means = np.empty(n_boot)
    n = len(data)
    for b in range(n_boot):
        sample = np.random.choice(data, size=n, replace=True)
        boot_means[b] = np.mean(sample)
    low = np.percentile(boot_means, 100 * (alpha / 2))
    high = np.percentile(boot_means, 100 * (1 - alpha / 2))
    return low, high

def calc_lag1_autocorr(series):
    n = len(series)
    if n < 3:
        return 0.0
    s_mean = np.mean(series)
    denom = np.sum((series - s_mean) ** 2)
    if denom == 0:
        return 0.0
    numer = np.sum((series[:-1] - s_mean) * (series[1:] - s_mean))
    return float(numer / denom)

def main():
    if not os.path.exists(RAW_CSV):
        print(f"Error: {RAW_CSV} not found! Run run_real_benchmark.py first.")
        sys.exit(1)

    df = pd.read_csv(RAW_CSV)
    workloads = df["workload"].unique()
    
    summary_rows = []
    latex_tab5 = []
    latex_tab6 = []

    print("\n==============================================================================")
    print("      REAL EMPIRICAL BENCHMARK ANALYSIS & EQUIVALENCE TESTING (TOST)")
    print("==============================================================================")

    for w in workloads:
        sub = df[df["workload"] == w].copy()
        n = len(sub)
        
        base_tps = sub["baseline_tps"].values
        dual_tps = sub["dual_layer_tps"].values
        san_tps = sub["sanitized_tps"].values if "sanitized_tps" in sub.columns else None
        
        # Exact measured paired ratios
        ratios = dual_tps / base_tps
        mean_ratio = float(np.mean(ratios))
        
        # Student's t 95% CI
        ci_t = stats.t.interval(0.95, df=n-1, loc=mean_ratio, scale=stats.sem(ratios))
        # Bootstrap 95% CI
        ci_boot = bootstrap_ci(ratios)
        
        # Log-transformed TOST test against +/- 5% margin [ln(0.95), ln(1.05)]
        log_r = np.log(ratios)
        z_mean = float(np.mean(log_r))
        z_se = float(stats.sem(log_r))
        
        # Lower bound test: H01: mu_z <= ln(0.95)
        t1 = (z_mean - np.log(0.95)) / z_se
        p1 = 1 - stats.t.cdf(t1, df=n-1)
        
        # Upper bound test: H02: mu_z >= ln(1.05)
        t2 = (np.log(1.05) - z_mean) / z_se
        p2 = 1 - stats.t.cdf(t2, df=n-1)
        
        p_tost_5 = max(p1, p2)
        
        # Sensitivity analysis (+/- 2% and +/- 3%)
        # 3%:
        t1_3 = (z_mean - np.log(0.97)) / z_se
        t2_3 = (np.log(1.03) - z_mean) / z_se
        p_tost_3 = max(1 - stats.t.cdf(t1_3, df=n-1), 1 - stats.t.cdf(t2_3, df=n-1))

        # 2%:
        t1_2 = (z_mean - np.log(0.98)) / z_se
        t2_2 = (np.log(1.02) - z_mean) / z_se
        p_tost_2 = max(1 - stats.t.cdf(t1_2, df=n-1), 1 - stats.t.cdf(t2_2, df=n-1))

        # Paired Cohen's d: diff = dual - base
        diffs = dual_tps - base_tps
        d_mean = np.mean(diffs)
        d_sd = np.std(diffs, ddof=1)
        cohens_d = float(d_mean / d_sd) if d_sd > 0 else 0.0

        # Normality (Shapiro-Wilk)
        shapiro_stat, shapiro_p = stats.shapiro(ratios)

        # Autocorrelation (lag-1)
        r1 = calc_lag1_autocorr(ratios)

        # Latencies
        b_lat_mean = float(np.mean(sub["baseline_mean_ms"]))
        d_lat_mean = float(np.mean(sub["dual_mean_ms"]))
        b_p99_mean = float(np.mean(sub["baseline_p99_ms"]))
        d_p99_mean = float(np.mean(sub["dual_p99_ms"]))

        b_tps_mean = float(np.mean(base_tps))
        b_tps_sd = float(np.std(base_tps, ddof=1))
        d_tps_mean = float(np.mean(dual_tps))
        d_tps_sd = float(np.std(dual_tps, ddof=1))
        
        s_tps_mean = float(np.mean(san_tps)) if san_tps is not None and np.mean(san_tps) > 0 else 0.0
        s_tps_sd = float(np.std(san_tps, ddof=1)) if san_tps is not None and np.mean(san_tps) > 0 else 0.0

        equiv_verdict = "Equivalent" if p_tost_5 < 0.05 else "Inconclusive"

        summary_rows.append({
            "workload": w,
            "n": n,
            "base_tps_mean": round(b_tps_mean, 1),
            "base_tps_sd": round(b_tps_sd, 1),
            "san_tps_mean": round(s_tps_mean, 1),
            "san_tps_sd": round(s_tps_sd, 1),
            "dual_tps_mean": round(d_tps_mean, 1),
            "dual_tps_sd": round(d_tps_sd, 1),
            "mean_ratio": round(mean_ratio, 4),
            "ci95_low": round(ci_t[0], 4),
            "ci95_high": round(ci_t[1], 4),
            "boot_ci95_low": round(ci_boot[0], 4),
            "boot_ci95_high": round(ci_boot[1], 4),
            "p_tost_5pct": p_tost_5,
            "p_tost_3pct": p_tost_3,
            "p_tost_2pct": p_tost_2,
            "cohens_d": round(cohens_d, 3),
            "shapiro_w": round(shapiro_stat, 3),
            "shapiro_p": round(shapiro_p, 4),
            "lag1_r1": round(r1, 3),
            "base_lat_mean_ms": round(b_lat_mean, 2),
            "dual_lat_mean_ms": round(d_lat_mean, 2),
            "base_p99_ms": round(b_p99_mean, 2),
            "dual_p99_ms": round(d_p99_mean, 2),
            "verdict": equiv_verdict
        })

        print(f"\nWorkload: {w}")
        print(f"  Base TPS:  {b_tps_mean:8.1f} +/- {b_tps_sd:5.1f}")
        if s_tps_mean > 0:
            print(f"  Sanit TPS: {s_tps_mean:8.1f} +/- {s_tps_sd:5.1f}")
        print(f"  Dual TPS:  {d_tps_mean:8.1f} +/- {d_tps_sd:5.1f}")
        print(f"  Ratio:     {mean_ratio:.4f} (95% CI: [{ci_t[0]:.4f}, {ci_t[1]:.4f}])")
        print(f"  TOST (5%): p = {p_tost_5:.3e} -> {equiv_verdict}")
        print(f"  Cohen's d: {cohens_d:.3f} | Shapiro-Wilk W: {shapiro_stat:.3f} | Lag-1 r1: {r1:.3f}")
        print(f"  Latency:   Base {b_lat_mean:.2f} ms (p99: {b_p99_mean:.2f} ms) | Dual {d_lat_mean:.2f} ms (p99: {d_p99_mean:.2f} ms)")

    sum_df = pd.DataFrame(summary_rows)
    sum_csv = os.path.join(RESULTS_DIR, "summary.csv")
    sum_df.to_csv(sum_csv, index=False)
    print(f"\nSummary table saved to {sum_csv}")

if __name__ == "__main__":
    main()
