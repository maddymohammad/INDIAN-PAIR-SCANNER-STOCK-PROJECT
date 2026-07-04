"""
persistence.py
--------------
Tracks per-pair cointegration verdicts across daily runs, so a pair is only
treated as interesting when it passes PERSISTENTLY — not on a single day.

Why this exists (multiple testing): scanning N pairs at a 5% threshold
expects ~0.05*N false positives per run even if NO pair truly cointegrates.
With 16 pairs that is ~0.8 spurious passes per run. A single day's PASS is
therefore a candidate, not a discovery. Persistence across many daily runs
is the accumulating evidence that separates structure from noise.

History lives at reports/history.csv. The daily CI job commits reports/,
so the evidence trail is public and grows automatically.

Synthetic-fallback runs (is_real=False) are recorded but EXCLUDED from
persistence counts — CI smoke-tests must never inflate the evidence.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

HISTORY_PATH = Path("reports/history.csv")

COLUMNS = [
    "run_date", "pair", "is_real", "p_value",
    "coint_5pct", "coint_bonf", "current_z", "oos_sharpe",
]


def load_history(path: Path = HISTORY_PATH) -> pd.DataFrame:
    if Path(path).exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=COLUMNS)


def update_history(results: list, run_date, bonf_alpha: float,
                   path: Path = HISTORY_PATH) -> pd.DataFrame:
    """
    Append this run's rows to the history CSV.
    Re-running on the same date REPLACES that date's rows (no double count).
    """
    hist = load_history(path)
    rows = []
    for r in results:
        z = r.get("current_z", float("nan"))
        rows.append({
            "run_date": str(run_date),
            "pair": f"{r['a']}/{r['b']}",
            "is_real": bool(r["is_real"]),
            "p_value": float(r["coint"]["p_value"]),
            "coint_5pct": bool(r["coint"]["cointegrated_5pct"]),
            "coint_bonf": bool(r["coint"]["p_value"] < bonf_alpha),
            "current_z": float(z) if z == z else float("nan"),
            "oos_sharpe": float(r["perf"]["sharpe"]),
        })
    new = pd.DataFrame(rows, columns=COLUMNS)
    if len(hist):
        hist = hist[hist["run_date"].astype(str) != str(run_date)]
    out = pd.concat([hist, new], ignore_index=True)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)
    return out


def _real_rows(history: pd.DataFrame, pair: str) -> pd.DataFrame:
    """Rows for one pair, REAL data only (robust to CSV bool round-trip)."""
    h = history[history["pair"] == pair]
    mask = h["is_real"].astype(str).str.lower().isin(["true", "1"])
    return h[mask]


def persistence_stats(history: pd.DataFrame, pair: str) -> dict:
    """
    Pass counts over real-data runs for one pair.
    Returns {passes_5pct, passes_bonf, real_runs}.
    """
    if history is None or not len(history):
        return {"passes_5pct": 0, "passes_bonf": 0, "real_runs": 0}
    h = _real_rows(history, pair)
    if not len(h):
        return {"passes_5pct": 0, "passes_bonf": 0, "real_runs": 0}
    p5 = h["coint_5pct"].astype(str).str.lower().isin(["true", "1"]).sum()
    pb = h["coint_bonf"].astype(str).str.lower().isin(["true", "1"]).sum()
    return {
        "passes_5pct": int(p5),
        "passes_bonf": int(pb),
        "real_runs": int(len(h)),
    }
