"""Figure generation. All plots are written as both PDF (for LaTeX) and PNG."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .load import Run, load_csv, load_summary
from .stats import CostInput, cost_ec2, cost_fargate, cost_lambda, percentile_ci, summarise_latency, time_to_steady

FIG_DIR = Path(__file__).resolve().parent.parent / "report" / "figures"

PLATFORM_COLORS = {"ec2": "#1f77b4", "fargate": "#2ca02c", "lambda": "#d62728"}
PLATFORM_LABELS = {"ec2": "EC2 (ASG)", "fargate": "ECS Fargate", "lambda": "Lambda"}


def _setup():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(context="paper", style="whitegrid", font_scale=1.0)
    matplotlib.rcParams.update({
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "figure.dpi": 120,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def save(fig, name: str):
    for ext in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"{name}.{ext}")
    plt.close(fig)


def plot_steady(runs: list[Run]):
    rows = []
    for r in [x for x in runs if x.scenario == "steady"]:
        # Prefer k6's scenario tag (rps_25, rps_50, ...) for clean per-stage stats;
        # fall back to time-window RPS inference for legacy CSVs that lack it.
        import pandas as _pd
        raw = _pd.read_csv(r.csv_path, low_memory=False)
        raw = raw[raw["metric_name"] == "http_req_duration"].copy()
        raw["lat_ms"] = _pd.to_numeric(raw["metric_value"], errors="coerce")
        raw["status"] = _pd.to_numeric(raw["status"], errors="coerce")
        ok = raw[raw["status"].notna() & (raw["status"] > 0)]
        have_scenario_tag = "scenario" in ok.columns and ok["scenario"].astype(str).str.startswith("rps_").any()
        if have_scenario_tag:
            for sc, sub in ok.groupby("scenario"):
                if not str(sc).startswith("rps_"):
                    continue
                rps = int(str(sc).split("_")[1])
                arr = sub["lat_ms"].dropna().to_numpy()
                if len(arr) < 200:
                    continue
                s = summarise_latency(arr)
                total = int((raw["scenario"] == sc).sum())
                s["err_pct"] = 100.0 * (1 - len(arr) / total) if total else 0.0
                rows.append({"platform": r.platform, "rps_bucket": f"rps_{rps}", "rps_mid": float(rps), **s})
        else:
            df = load_csv(r.csv_path)
            df["t_bin"] = df["t_rel"].astype(int)
            rps_by_bin = df.groupby("t_bin").size()
            df = df.merge(rps_by_bin.rename("rps"), left_on="t_bin", right_index=True)
            for rps, sub in df.groupby(pd.cut(df["rps"], bins=[0, 75, 175, 375, 750, 1500, 3000, 10000]), observed=True):
                if len(sub) < 500:
                    continue
                arr = sub["lat_ms"].to_numpy()
                s = summarise_latency(arr)
                s["err_pct"] = 0.0
                rows.append({"platform": r.platform, "rps_bucket": str(rps), "rps_mid": (rps.left + rps.right) / 2, **s})

    if not rows:
        return
    tbl = pd.DataFrame(rows)
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2), sharey=False)
    for ax, q, label in zip(axes, (50, 95, 99), ("p50", "p95", "p99")):
        for plat, sub in tbl.groupby("platform"):
            sub = sub.sort_values("rps_mid")
            ax.errorbar(
                sub["rps_mid"],
                sub[f"p{q}"],
                yerr=[sub[f"p{q}"] - sub[f"p{q}_lo"], sub[f"p{q}_hi"] - sub[f"p{q}"]],
                marker="o",
                color=PLATFORM_COLORS.get(plat, "grey"),
                label=PLATFORM_LABELS.get(plat, plat),
                capsize=3,
            )
        ax.set_title(label)
        ax.set_xlabel("Offered RPS")
        ax.set_ylabel("Latency (ms)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "steady_latency_vs_rps")
    tbl.to_csv(FIG_DIR / "steady_summary.csv", index=False)


def plot_elasticity(runs: list[Run]):
    out = {}
    fig, ax = plt.subplots(figsize=(7, 3.5))
    for r in [x for x in runs if x.scenario == "burst"]:
        df = load_csv(r.csv_path)
        if df.empty:
            continue
        # bin per-second p95
        df["t_bin"] = df["t_rel"].astype(int)
        per_sec = df.groupby("t_bin")["lat_ms"].quantile(0.95).reset_index()
        ax.plot(per_sec["t_bin"], per_sec["lat_ms"], color=PLATFORM_COLORS.get(r.platform), label=PLATFORM_LABELS.get(r.platform, r.platform))
        summary = load_summary(r.json_path)
        burst_start = int(summary.get("burst_start_s", 60))
        out[r.platform] = time_to_steady(df, burst_start_s=burst_start)
    ax.set_xlabel("Seconds since run start")
    ax.set_ylabel("Per-second p95 (ms)")
    ax.set_yscale("log")
    ax.axvspan(60, 300, alpha=0.08, color="grey", label="burst window")
    ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "elasticity_p95_trace")

    if out:
        fig2, ax2 = plt.subplots(figsize=(4.5, 3))
        keys = list(out.keys())
        ax2.bar(keys, [out[k] for k in keys], color=[PLATFORM_COLORS.get(k, "grey") for k in keys])
        ax2.set_ylabel("Time to steady state (s)")
        ax2.set_xticks(range(len(keys)))
        ax2.set_xticklabels([PLATFORM_LABELS.get(k, k) for k in keys], rotation=0)
        fig2.tight_layout()
        save(fig2, "elasticity_ttss")
        pd.Series(out, name="ttss_seconds").to_csv(FIG_DIR / "elasticity_ttss.csv")


def plot_coldstart(runs: list[Run]):
    frames = []
    for r in [x for x in runs if x.scenario == "coldstart"]:
        df = load_csv(r.csv_path)
        if df.empty:
            continue
        df["platform"] = r.platform
        frames.append(df)
    if not frames:
        return
    big = pd.concat(frames, ignore_index=True)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    for plat, sub in big.groupby("platform"):
        arr = sub["lat_ms"].to_numpy()
        ax.ecdf = getattr(ax, "ecdf", None)
        x = np.sort(arr)
        y = np.arange(1, len(x) + 1) / len(x)
        ax.plot(x, y, label=PLATFORM_LABELS.get(plat, plat), color=PLATFORM_COLORS.get(plat, "grey"))
    ax.set_xlabel("End-to-end latency (ms)")
    ax.set_ylabel("CDF")
    ax.set_xscale("log")
    ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "coldstart_cdf")

    # stats table
    rows = []
    for plat, sub in big.groupby("platform"):
        arr = sub["lat_ms"].to_numpy()
        s = summarise_latency(arr)
        rows.append({"platform": plat, **s})
    pd.DataFrame(rows).to_csv(FIG_DIR / "coldstart_summary.csv", index=False)


def plot_cost_pareto():
    rps_grid = np.logspace(0, 4, 50)
    ci = CostInput(rps=1, ratio_reads=0.7, p50_ms=12, p95_ms=40)
    # one instance/task baseline
    ec2_1 = np.array([cost_ec2(CostInput(rps=rps, ratio_reads=0.7, p50_ms=12, p95_ms=40), instances=max(1, rps / 400)) for rps in rps_grid])
    fg_1 = np.array([cost_fargate(CostInput(rps=rps, ratio_reads=0.7, p50_ms=12, p95_ms=40), tasks=max(1, rps / 300)) for rps in rps_grid])
    lb_1 = np.array([cost_lambda(CostInput(rps=rps, ratio_reads=0.7, p50_ms=30, p95_ms=120)) for rps in rps_grid])

    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.plot(rps_grid, ec2_1, label="EC2 (t3.small ASG)", color=PLATFORM_COLORS["ec2"])
    ax.plot(rps_grid, fg_1, label="Fargate (0.5 vCPU, 1 GB)", color=PLATFORM_COLORS["fargate"])
    ax.plot(rps_grid, lb_1, label="Lambda (1 GB)", color=PLATFORM_COLORS["lambda"])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Sustained RPS")
    ax.set_ylabel("Monthly cost (USD)")

    # break-even points: ec2 == lambda, fargate == lambda
    def cross(a, b):
        idx = np.where(np.diff(np.sign(a - b)))[0]
        return rps_grid[idx[0]] if len(idx) else None
    lb_ec2 = cross(lb_1, ec2_1)
    lb_fg = cross(lb_1, fg_1)
    if lb_ec2:
        ax.axvline(lb_ec2, linestyle=":", color="grey")
        ax.text(lb_ec2, ax.get_ylim()[1] * 0.6, f"λ→EC2 @ {lb_ec2:.0f} RPS", rotation=90, fontsize=8, color="grey", ha="right")
    if lb_fg:
        ax.axvline(lb_fg, linestyle=":", color="grey")
        ax.text(lb_fg, ax.get_ylim()[1] * 0.3, f"λ→Fargate @ {lb_fg:.0f} RPS", rotation=90, fontsize=8, color="grey", ha="right")

    ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "cost_vs_rps")

    out = pd.DataFrame({"rps": rps_grid, "ec2_usd_mo": ec2_1, "fargate_usd_mo": fg_1, "lambda_usd_mo": lb_1})
    out.to_csv(FIG_DIR / "cost_curves.csv", index=False)


def plot_pareto(runs):
    """Cost-vs-p95-latency Pareto plot. Uses real measurements when available
    by joining each platform's mean p95 across the steady sweep with the cost
    model. Cost is normalised to USD per million requests at 100 RPS."""
    rows = []
    rps_for_cost = 100.0
    for r in [x for x in runs if x.scenario == "steady"]:
        df = load_csv(r.csv_path)
        if df.empty:
            continue
        p95 = float(np.percentile(df["lat_ms"].to_numpy(), 95))
        p50 = float(np.percentile(df["lat_ms"].to_numpy(), 50))
        ci = CostInput(rps=rps_for_cost, ratio_reads=0.7, p50_ms=p50, p95_ms=p95)
        if r.platform == "ec2":
            cost = cost_ec2(ci, instances=1) * 12  # annual to make numbers readable
        elif r.platform == "fargate":
            cost = cost_fargate(ci, tasks=1) * 12
        else:
            cost = cost_lambda(ci) * 12
        usd_per_million = cost / (rps_for_cost * 3600 * 730 * 12) * 1e6
        rows.append({"platform": r.platform, "p95_ms": p95, "usd_per_M": usd_per_million})
    if not rows:
        return
    tbl = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    for plat, sub in tbl.groupby("platform"):
        ax.scatter(sub["p95_ms"], sub["usd_per_M"], s=120, color=PLATFORM_COLORS.get(plat), label=PLATFORM_LABELS.get(plat, plat), edgecolor="black", linewidth=0.5, zorder=3)
        for _, row in sub.iterrows():
            ax.annotate(PLATFORM_LABELS.get(plat, plat), (row["p95_ms"], row["usd_per_M"]), xytext=(6, 4), textcoords="offset points", fontsize=8)
    ax.set_xlabel("p95 latency (ms, lower is better)")
    ax.set_ylabel("USD per 1M requests (lower is better)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    save(fig, "cost_latency_pareto")
    tbl.to_csv(FIG_DIR / "cost_latency_pareto.csv", index=False)
