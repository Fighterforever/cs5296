"""Load k6 output (CSV streaming log + JSON summary) into tidy DataFrames."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"

FNAME_RE = re.compile(r"(?P<platform>[a-z0-9]+)-(?P<scenario>[a-z0-9]+)\.out\.csv$")


@dataclass(frozen=True)
class Run:
    run_id: str
    platform: str
    scenario: str
    csv_path: Path
    json_path: Path


def list_runs(run_id: str | None = None) -> list[Run]:
    root = RESULTS_DIR if run_id is None else RESULTS_DIR / run_id
    out: list[Run] = []
    for p in root.rglob("*.out.csv"):
        m = FNAME_RE.search(p.name)
        if not m:
            continue
        rid = p.parent.name if run_id is None else run_id
        out.append(
            Run(
                run_id=rid,
                platform=m["platform"],
                scenario=m["scenario"],
                csv_path=p,
                json_path=p.with_suffix("").with_suffix(".json"),
            )
        )
    return sorted(out, key=lambda r: (r.run_id, r.scenario, r.platform))


def load_csv(path: Path) -> pd.DataFrame:
    """k6 csv output has columns: metric_name,timestamp,metric_value,check,...
    Keep only http_req_duration samples, return relative seconds."""
    df = pd.read_csv(path)
    df = df[df["metric_name"] == "http_req_duration"].copy()
    df["ts"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["lat_ms"] = pd.to_numeric(df["metric_value"], errors="coerce")
    df = df.dropna(subset=["ts", "lat_ms"])
    df["t_rel"] = df["ts"] - df["ts"].min()
    # keep only meaningful tag columns we emit
    keep = ["t_rel", "lat_ms", "status", "method", "url"]
    for col in ("scenario", "endpoint", "platform", "phase", "stage"):
        if col in df.columns:
            keep.append(col)
    return df[[c for c in keep if c in df.columns]].reset_index(drop=True)


def load_summary(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open() as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return {}
