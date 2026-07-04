# Indian Pairs-Trading Scanner — 2026-07-03

> **What this is:** a market-neutral *pairs mean-reversion* scanner. It flags when two related NSE stocks have drifted apart far enough that their historical relationship signals a possible convergence trade. It does **not** forecast growth, rank "best" stocks, or predict company performance. A signal means the *spread between two stocks* is stretched — nothing about either stock being a good investment. Not investment advice; do your own research.

## Methodology (fixed in advance)

- **Universe:** 16 declared sector-mate pairs. Parameters (3y window, 60/40 train-test, z-entry 2.0, z-exit 0.5, 5 bps costs) are pre-registered; changes are logged in the README changelog *before* looking at results.
- **Multiple testing:** at the 5% level across 16 pairs, **≈0.8 false positives per run are expected by chance alone** even if nothing truly cointegrates. A single-day pass is a candidate, not a discovery.
- **Strict tier:** Bonferroni-corrected threshold p < 0.0031 (marked ✓✓).
- **Evidence = persistence:** the Persistence column counts how often each pair has passed the 5% test across all *real-data* daily runs recorded in `reports/history.csv`. Pairs deserve attention only when they pass persistently.

> ⚠️ **Some results use SIMULATED fallback data** (real data was unreachable this run) and are not real market results. These are marked below and are EXCLUDED from persistence counts.

## Summary

| Pair | p-value | Coint. | Persistence | Current z | Signal | OOS Sharpe |
|---|---|---|---|---|---|---|
| HDFCBANK.NS/ICICIBANK.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| AXISBANK.NS/ICICIBANK.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| KOTAKBANK.NS/HDFCBANK.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| SBIN.NS/BANKBARODA.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| TCS.NS/INFY.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| INFY.NS/WIPRO.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| HCLTECH.NS/TECHM.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| ACC.NS/AMBUJACEM.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| ULTRACEMCO.NS/SHREECEM.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| IOC.NS/BPCL.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| BPCL.NS/HINDPETRO.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| ONGC.NS/COALINDIA.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| NTPC.NS/POWERGRID.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| BAJAJ-AUTO.NS/HEROMOTOCO.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| TATASTEEL.NS/JSWSTEEL.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |
| SUNPHARMA.NS/CIPLA.NS *(sim)* | 0.0030 | ✓✓ | 0/0* | -1.55 | watch | 1.13 |

_Legend: ✓✓ passes strict Bonferroni tier · ✓ passes 5% only · ✗ fails. Persistence = 5%-passes / real-data runs recorded. \*no real-data history yet._

---

### HDFCBANK.NS / ICICIBANK.NS · _SIMULATED_

- **Latest prices:** HDFCBANK.NS ₹77.27 · ICICIBANK.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![HDFCBANK.NS/ICICIBANK.NS chart](charts/2026-07-03/HDFCBANK-NS_ICICIBANK-NS.png)

---

### AXISBANK.NS / ICICIBANK.NS · _SIMULATED_

- **Latest prices:** AXISBANK.NS ₹77.27 · ICICIBANK.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![AXISBANK.NS/ICICIBANK.NS chart](charts/2026-07-03/AXISBANK-NS_ICICIBANK-NS.png)

---

### KOTAKBANK.NS / HDFCBANK.NS · _SIMULATED_

- **Latest prices:** KOTAKBANK.NS ₹77.27 · HDFCBANK.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![KOTAKBANK.NS/HDFCBANK.NS chart](charts/2026-07-03/KOTAKBANK-NS_HDFCBANK-NS.png)

---

### SBIN.NS / BANKBARODA.NS · _SIMULATED_

- **Latest prices:** SBIN.NS ₹77.27 · BANKBARODA.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![SBIN.NS/BANKBARODA.NS chart](charts/2026-07-03/SBIN-NS_BANKBARODA-NS.png)

---

### TCS.NS / INFY.NS · _SIMULATED_

- **Latest prices:** TCS.NS ₹77.27 · INFY.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![TCS.NS/INFY.NS chart](charts/2026-07-03/TCS-NS_INFY-NS.png)

---

### INFY.NS / WIPRO.NS · _SIMULATED_

- **Latest prices:** INFY.NS ₹77.27 · WIPRO.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![INFY.NS/WIPRO.NS chart](charts/2026-07-03/INFY-NS_WIPRO-NS.png)

---

### HCLTECH.NS / TECHM.NS · _SIMULATED_

- **Latest prices:** HCLTECH.NS ₹77.27 · TECHM.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![HCLTECH.NS/TECHM.NS chart](charts/2026-07-03/HCLTECH-NS_TECHM-NS.png)

---

### ACC.NS / AMBUJACEM.NS · _SIMULATED_

- **Latest prices:** ACC.NS ₹77.27 · AMBUJACEM.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![ACC.NS/AMBUJACEM.NS chart](charts/2026-07-03/ACC-NS_AMBUJACEM-NS.png)

---

### ULTRACEMCO.NS / SHREECEM.NS · _SIMULATED_

- **Latest prices:** ULTRACEMCO.NS ₹77.27 · SHREECEM.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![ULTRACEMCO.NS/SHREECEM.NS chart](charts/2026-07-03/ULTRACEMCO-NS_SHREECEM-NS.png)

---

### IOC.NS / BPCL.NS · _SIMULATED_

- **Latest prices:** IOC.NS ₹77.27 · BPCL.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![IOC.NS/BPCL.NS chart](charts/2026-07-03/IOC-NS_BPCL-NS.png)

---

### BPCL.NS / HINDPETRO.NS · _SIMULATED_

- **Latest prices:** BPCL.NS ₹77.27 · HINDPETRO.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![BPCL.NS/HINDPETRO.NS chart](charts/2026-07-03/BPCL-NS_HINDPETRO-NS.png)

---

### ONGC.NS / COALINDIA.NS · _SIMULATED_

- **Latest prices:** ONGC.NS ₹77.27 · COALINDIA.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![ONGC.NS/COALINDIA.NS chart](charts/2026-07-03/ONGC-NS_COALINDIA-NS.png)

---

### NTPC.NS / POWERGRID.NS · _SIMULATED_

- **Latest prices:** NTPC.NS ₹77.27 · POWERGRID.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![NTPC.NS/POWERGRID.NS chart](charts/2026-07-03/NTPC-NS_POWERGRID-NS.png)

---

### BAJAJ-AUTO.NS / HEROMOTOCO.NS · _SIMULATED_

- **Latest prices:** BAJAJ-AUTO.NS ₹77.27 · HEROMOTOCO.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![BAJAJ-AUTO.NS/HEROMOTOCO.NS chart](charts/2026-07-03/BAJAJ-AUTO-NS_HEROMOTOCO-NS.png)

---

### TATASTEEL.NS / JSWSTEEL.NS · _SIMULATED_

- **Latest prices:** TATASTEEL.NS ₹77.27 · JSWSTEEL.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![TATASTEEL.NS/JSWSTEEL.NS chart](charts/2026-07-03/TATASTEEL-NS_JSWSTEEL-NS.png)

---

### SUNPHARMA.NS / CIPLA.NS · _SIMULATED_

- **Latest prices:** SUNPHARMA.NS ₹77.27 · CIPLA.NS ₹113.78
- **Hedge ratio (train-fitted):** 1.5557
- **Cointegration (train):** PASS at 5% — ADF -3.79, p=0.0030 · **passes strict Bonferroni tier**
- **Persistence:** no real-data history yet
- **Spread half-life:** 14.0 days
- **Current z-score:** -1.55
- **Signal today:** watch (approaching band)

**Out-of-sample backtest** (beta frozen from train window):

| Metric | Value |
|---|---|
| Sharpe | 1.13 |
| Sortino | 0.86 |
| Annualised return | 1.88% |
| Annualised vol | 1.66% |
| Max drawdown | -1.19% |
| Round-trip trades | 5 |

![SUNPHARMA.NS/CIPLA.NS chart](charts/2026-07-03/SUNPHARMA-NS_CIPLA-NS.png)

---

_Generated 2026-07-03 · pairs mean-reversion scanner · out-of-sample backtest · multiple-testing-aware · not investment advice._
