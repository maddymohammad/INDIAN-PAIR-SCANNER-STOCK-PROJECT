# Indian Pairs-Trading Scanner

A market-neutral **pairs mean-reversion** engine for NSE (Indian) stocks. It
runs daily, tests whether related stock pairs currently cointegrate, and
commits a dated report, charts, and an accumulating evidence trail to this
repo every weekday.

## What this is — and what it is NOT

**It is:** a statistical-arbitrage engine. It watches the *spread* between two
related stocks (e.g. two banks) and signals when that spread has stretched far
enough that history suggests it may revert. It is market-neutral — it profits
from the *relationship* reverting, not from either stock going up.

**It is NOT:**
- a growth forecaster — it has no model of future prices or company performance
- a stock picker — it does not rank "best" stocks to buy
- investment advice — every signal is a research observation to verify yourself

## Pre-registered methodology

All parameters below are declared in advance and held fixed. Any change must
be recorded in the changelog **with a stated reason, before looking at how the
change affects results**. This is the project's defence against p-hacking —
iterating on parameters until something passes would manufacture the
appearance of a strategy out of noise.

| Parameter | Value |
|---|---|
| Data window | 3 years, daily |
| Train / test split | first 60% train (fits beta), last 40% out-of-sample |
| Z-score window | 60 days, trailing |
| Entry / exit | \|z\| > 2.0 enter, \|z\| < 0.5 exit |
| Transaction cost | 5 bps one-way |
| Pair universe | 16 declared sector-mate pairs (see `main.py`) |
| Per-pair significance | 5% (ADF on train spread) |
| Strict tier | Bonferroni: p < 0.05 / 16 = 0.003125 |

### Multiple-testing discipline

Scanning 16 pairs at 5% expects **~0.8 false positives per run by chance
alone**, even if no pair truly cointegrates. Therefore:

- A **single-day 5% pass is a candidate, not a discovery.**
- The **strict tier** (Bonferroni, marked ✓✓) corrects for the number of
  tests per run.
- **Evidence is persistence:** `reports/history.csv` records every real-data
  run's verdict per pair, and each report shows how often each pair has
  passed across all recorded runs. Pairs deserve attention only when they
  pass persistently. Synthetic-fallback runs are excluded from these counts.

### Changelog

- **2026-07-03** — Universe widened 5 → 16 pairs (reason: a 5-pair scan was
  undersized for discovery; sector-mate expansion declared before observing
  results). Added Bonferroni strict tier and persistence tracking — these are
  reporting-layer additions; **no signal parameter was changed**.
- **2026-07-02** — Initial release: train/test split (fixes hedge-ratio
  lookahead), fixed capital base, real NSE data with flagged synthetic
  fallback.

## Correctness properties

1. **No lookahead in the hedge ratio.** Beta is estimated on the training
   window and frozen; the backtest runs only on held-out data.
2. **Real data, honestly labelled.** Real NSE prices via Yahoo Finance. The
   synthetic fallback exists only for offline CI smoke-tests, is loudly
   flagged `SIMULATED`, and never counts toward persistence evidence.
3. **Cointegration is tested, never assumed.** Failing pairs are reported as
   "no valid signal", not forced into trades.
4. **Fixed capital base.** Return/vol levels are well-defined, not artefacts
   of sample-dependent scaling.

## Honest limitations

- The out-of-sample backtest is a *single* train/test split on historical
  data — far more honest than in-sample, but not walk-forward or live-tracked.
- Cointegration relationships decay; a pair that passed on the training
  window may stop cointegrating. This is a property of markets, not a bug.
- The ADF test has limited power on ~21-month training windows; borderline
  pairs (p just above 0.05) may be real relationships the test cannot yet
  confirm. Persistence tracking is the honest way to accumulate evidence
  either way.

## Usage

```bash
pip install -r requirements.txt
python main.py                        # scan the declared universe
python main.py --pair TCS.NS INFY.NS  # analyse a single pair
python run_daily.py                   # full daily run: history + charts + report
```

## Daily automation

`.github/workflows/daily.yml` runs `run_daily.py` every weekday at 18:30 IST
(after NSE close) and commits `reports/` — the dated report, charts, and the
growing `history.csv`. Uses GitHub's free built-in token; no secrets required.

## Files

- `data_loader.py` — real NSE data fetch + flagged synthetic fallback
- `cointegration.py` — Engle-Granger test, train-only beta fit, half-life
- `signals.py` — trailing z-score, position state machine
- `backtester.py` — lagged-signal, cost-aware, fixed-capital backtest
- `metrics.py` — Sharpe, Sortino, drawdown, etc.
- `persistence.py` — cross-run evidence trail (multiple-testing defence)
- `main.py` — per-pair train/test analysis + declared universe
- `report.py` — charts + methodology-aware markdown report
- `run_daily.py` — daily entry point
