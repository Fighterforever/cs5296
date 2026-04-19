"""Entry point: `python -m analysis.build_figures [RUN_ID]` builds all figures
and aggregate CSV tables under report/figures/. If there are no real runs
yet, we generate a synthetic dataset so the pipeline, figures and report can
be validated end-to-end. The synthetic path is clearly labelled in the
produced figures."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .load import RESULTS_DIR, list_runs
from .plots import _setup, plot_coldstart, plot_cost_pareto, plot_elasticity, plot_pareto, plot_steady


def _synth():
    """Produce synthetic data for pipeline validation. Same schema as k6 csv."""
    rng = np.random.default_rng(42)
    out_root = RESULTS_DIR / "synth"
    out_root.mkdir(parents=True, exist_ok=True)

    steady_rps = [50, 100, 250, 500, 1000]

    def emit(platform: str, scenario: str, df: pd.DataFrame):
        base = out_root / f"{platform}-{scenario}"
        df.to_csv(f"{base}.out.csv", index=False)
        (Path(f"{base}.json")).write_text('{"scenario": "' + scenario + '"}')

    for plat, slope, floor, tail in (("ec2", 0.02, 6, 2.0), ("fargate", 0.03, 9, 2.5), ("lambda", 0.08, 25, 6.0)):
        rows = []
        t = 0.0
        for rps in steady_rps:
            n = rps * 90  # 90s stage
            lat = rng.lognormal(mean=np.log(floor + slope * rps), sigma=0.35, size=n) + rng.pareto(tail, size=n) * 2
            ts = t + rng.uniform(0, 90, size=n)
            for s_i, l_i in zip(np.sort(ts), lat):
                rows.append({"metric_name": "http_req_duration", "timestamp": s_i, "metric_value": float(l_i), "status": 200, "method": "GET", "url": f"http://{plat}/r/x"})
            t += 90 + 20
        emit(plat, "steady", pd.DataFrame(rows))

        # burst: pre/burst/post
        rows = []
        for start, dur, rps in ((0, 60, 5), (60, 240, 800), (300, 60, 5)):
            n = rps * dur
            ts = start + rng.uniform(0, dur, size=n)
            base_lat = floor + slope * rps
            if plat == "lambda" and start == 60:
                decay = np.exp(-(ts - 60) / 30)
                lat = rng.lognormal(mean=np.log(base_lat * (1 + 6 * decay)), sigma=0.5, size=n)
            elif plat == "ec2" and start == 60:
                decay = np.exp(-(ts - 60) / 45)
                lat = rng.lognormal(mean=np.log(base_lat * (1 + 3 * decay)), sigma=0.4, size=n)
            elif plat == "fargate" and start == 60:
                decay = np.exp(-(ts - 60) / 25)
                lat = rng.lognormal(mean=np.log(base_lat * (1 + 2.5 * decay)), sigma=0.4, size=n)
            else:
                lat = rng.lognormal(mean=np.log(base_lat), sigma=0.3, size=n)
            for s_i, l_i in zip(np.sort(ts), lat):
                rows.append({"metric_name": "http_req_duration", "timestamp": float(s_i), "metric_value": float(l_i), "status": 200, "method": "GET", "url": f"http://{plat}/r/x"})
        emit(plat, "burst", pd.DataFrame(rows))

        # cold start: lambda shows bimodal distribution; ec2/fargate narrow
        rows = []
        n = 25
        if plat == "lambda":
            cold = rng.lognormal(mean=np.log(800), sigma=0.25, size=n // 3)
            warm = rng.lognormal(mean=np.log(25), sigma=0.15, size=n - n // 3)
            lat = np.concatenate([cold, warm])
        else:
            lat = rng.lognormal(mean=np.log(floor), sigma=0.2, size=n)
        ts = np.arange(n) * 45.0
        rng.shuffle(ts)
        rows = [
            {"metric_name": "http_req_duration", "timestamp": float(s), "metric_value": float(v), "status": 200, "method": "GET", "url": "http://x/healthz"}
            for s, v in zip(np.sort(ts), lat)
        ]
        emit(plat, "coldstart", pd.DataFrame(rows))


def main(run_id: str | None = None):
    _setup()
    runs = list_runs(run_id)
    if not runs:
        if run_id == "synth":
            print(">> synthetic pipeline check requested; generating fixture data under data/results/synth/")
            _synth()
            runs = list_runs("synth")
        else:
            raise SystemExit(
                f">> no real runs found for run_id={run_id!r}. "
                "Expected at least one *.out.csv under data/results/. "
                "Pass run_id=synth to explicitly generate the synthetic pipeline fixture."
            )

    print(f">> found {len(runs)} run files across {len({r.scenario for r in runs})} scenarios")
    plot_steady(runs)
    plot_elasticity(runs)
    plot_coldstart(runs)
    plot_cost_pareto()
    plot_pareto(runs)
    print(">> figures written to report/figures/")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
