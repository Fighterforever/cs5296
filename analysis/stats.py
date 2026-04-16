"""Statistics helpers: percentile bootstrap CIs, time-to-steady, cost model."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def percentile_ci(x: np.ndarray, q: float, n_boot: int = 1000, alpha: float = 0.05, seed: int = 7) -> tuple[float, float, float]:
    """Return (point, lo, hi) for percentile q on a 1-d array."""
    rng = np.random.default_rng(seed)
    point = float(np.percentile(x, q))
    if len(x) < 20:
        return point, float("nan"), float("nan")
    bs = np.empty(n_boot)
    for i in range(n_boot):
        s = rng.choice(x, size=len(x), replace=True)
        bs[i] = np.percentile(s, q)
    lo, hi = np.percentile(bs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point, float(lo), float(hi)


def summarise_latency(lat_ms: np.ndarray) -> dict:
    out = {"n": int(len(lat_ms))}
    for q in (50, 90, 95, 99, 99.9):
        pt, lo, hi = percentile_ci(lat_ms, q)
        out[f"p{q}"] = pt
        out[f"p{q}_lo"] = lo
        out[f"p{q}_hi"] = hi
    out["mean"] = float(lat_ms.mean()) if len(lat_ms) else float("nan")
    return out


def time_to_steady(df: pd.DataFrame, burst_start_s: float, quantile: float = 0.95, bin_s: float = 1.0, tol_ratio: float = 1.2) -> float:
    """Given a step-arrival burst, find seconds from burst_start until the
    per-second p95 stabilises within tol_ratio*steady, where steady is the
    median of the last 20% of the burst window."""
    w = df[df["t_rel"] >= burst_start_s].copy()
    if w.empty:
        return float("nan")
    w["bin"] = (w["t_rel"] - burst_start_s) // bin_s
    agg = w.groupby("bin")["lat_ms"].quantile(quantile).reset_index()
    agg["t_rel"] = agg["bin"] * bin_s
    steady = float(agg["lat_ms"].tail(max(5, len(agg) // 5)).median())
    target = tol_ratio * steady
    for _, row in agg.iterrows():
        if row["lat_ms"] <= target:
            return float(row["t_rel"])
    return float("nan")


# -----------------------------------------------------------------------------
# Cost model (us-east-1 on-demand, April 2026 public pricing, USD).
# All figures sourced from the AWS pricing pages and cited in the report.
# -----------------------------------------------------------------------------

EC2_HOURLY = {
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
    "c5.large": 0.085,
    "c6g.large": 0.068,
}

FARGATE_VCPU_HOUR = 0.04048
FARGATE_GB_HOUR = 0.004445
FARGATE_VCPU_HOUR_ARM = 0.03238
FARGATE_GB_HOUR_ARM = 0.003556

LAMBDA_REQ_USD = 2e-7                 # $0.20 per 1M requests
LAMBDA_GB_S_USD = 16.67e-6            # $0.0000166667 per GB-second (x86)
LAMBDA_GB_S_USD_ARM = 13.33e-6        # Graviton2 pricing
LAMBDA_PC_GB_S_USD = 4.167e-6         # provisioned concurrency, idle billing

DDB_PPR_WRITE = 1.25e-6               # on-demand write request unit
DDB_PPR_READ = 0.25e-6                # on-demand read request unit

ALB_HOURLY = 0.0225
ALB_LCU_HOURLY = 0.008


@dataclass
class CostInput:
    rps: float          # sustained requests per second
    ratio_reads: float  # share of requests that are reads (GET redirects)
    p50_ms: float
    p95_ms: float


def cost_ec2(c: CostInput, instances: float, instance_type: str = "t3.small", hours: float = 730) -> float:
    """Monthly cost in USD: EC2 hours + ALB + DDB requests."""
    compute = EC2_HOURLY[instance_type] * instances * hours
    reqs = c.rps * 3600 * hours
    ddb = reqs * (c.ratio_reads * DDB_PPR_READ + (1 - c.ratio_reads) * DDB_PPR_WRITE)
    alb = ALB_HOURLY * hours
    return compute + ddb + alb


def cost_fargate(c: CostInput, tasks: float, cpu_units: int = 512, memory_mb: int = 1024, hours: float = 730) -> float:
    vcpu = cpu_units / 1024.0
    gb = memory_mb / 1024.0
    compute = tasks * hours * (vcpu * FARGATE_VCPU_HOUR + gb * FARGATE_GB_HOUR)
    reqs = c.rps * 3600 * hours
    ddb = reqs * (c.ratio_reads * DDB_PPR_READ + (1 - c.ratio_reads) * DDB_PPR_WRITE)
    alb = ALB_HOURLY * hours
    return compute + ddb + alb


def cost_lambda(c: CostInput, memory_mb: int = 1024, hours: float = 730, pc_instances: int = 0) -> float:
    reqs = c.rps * 3600 * hours
    avg_s = c.p50_ms / 1000.0
    gb = memory_mb / 1024.0
    exec_cost = reqs * (LAMBDA_REQ_USD + gb * avg_s * LAMBDA_GB_S_USD)
    ddb = reqs * (c.ratio_reads * DDB_PPR_READ + (1 - c.ratio_reads) * DDB_PPR_WRITE)
    pc_cost = pc_instances * gb * LAMBDA_PC_GB_S_USD * 3600 * hours
    return exec_cost + ddb + pc_cost
