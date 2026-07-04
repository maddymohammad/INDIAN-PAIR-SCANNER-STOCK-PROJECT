"""
main.py
-------
Daily Indian-market pairs-trading scanner.

WHAT THIS DOES (and does not) DO:
  - Monitors PAIRS of related NSE stocks and tests whether each pair
    currently cointegrates (i.e. their spread mean-reverts).
  - For each pair it reports the current z-score and an OUT-OF-SAMPLE
    backtest (beta fit on a training window, tested on held-out data).
  - It is MARKET-NEUTRAL mean-reversion. It does NOT forecast growth,
    does NOT rank "best stocks", and does NOT predict company performance.

MULTIPLE-TESTING DISCIPLINE:
  Scanning N pairs at a 5% threshold expects ~0.05*N false positives per
  run even if nothing truly cointegrates. Each run therefore reports:
    - the per-pair 5% verdict,
    - a Bonferroni-corrected verdict (p < 0.05/N) as the strict tier,
    - and persistence counts across daily runs (see persistence.py).
  A single-day 5% pass is a CANDIDATE. Evidence = persistent passing.

Run:
    python main.py                 # scan the declared pair universe
    python main.py --pair TCS.NS INFY.NS
"""
from __future__ import annotations

import argparse
import logging

import pandas as pd

from data_loader import load_pair
from cointegration import fit_hedge_ratio, build_spread, adf_test, half_life
from signals import rolling_zscore, generate_positions
from backtester import backtest_pair
from metrics import summarise

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ── DECLARED PAIR UNIVERSE ──────────────────────────────────────────────────
# Sector-mates on the NSE. Widened 5 -> 16 on 2026-07-03 (see README
# changelog). Cointegration is TESTED per run, never assumed; non-passing
# pairs are reported as no-signal, not forced into trades.
DEFAULT_PAIRS = [
    # banks
    ("HDFCBANK.NS", "ICICIBANK.NS"),
    ("AXISBANK.NS", "ICICIBANK.NS"),
    ("KOTAKBANK.NS", "HDFCBANK.NS"),
    ("SBIN.NS", "BANKBARODA.NS"),
    # IT
    ("TCS.NS", "INFY.NS"),
    ("INFY.NS", "WIPRO.NS"),
    ("HCLTECH.NS", "TECHM.NS"),
    # cement
    ("ACC.NS", "AMBUJACEM.NS"),
    ("ULTRACEMCO.NS", "SHREECEM.NS"),
    # energy / oil marketing
    ("IOC.NS", "BPCL.NS"),
    ("BPCL.NS", "HINDPETRO.NS"),
    ("ONGC.NS", "COALINDIA.NS"),
    # power utilities
    ("NTPC.NS", "POWERGRID.NS"),
    # autos (two-wheelers)
    ("BAJAJ-AUTO.NS", "HEROMOTOCO.NS"),
    # metals
    ("TATASTEEL.NS", "JSWSTEEL.NS"),
    # pharma
    ("SUNPHARMA.NS", "CIPLA.NS"),
]

SIGNIFICANCE = 0.05      # per-pair threshold (declared, fixed)
TRAIN_FRAC = 0.6         # first 60% fits beta; last 40% is out-of-sample


def analyse_pair(ticker_a, ticker_b, period="3y",
                 window=60, entry_z=2.0, exit_z=0.5, cost_bps=5.0):
    """Full train/test analysis for one pair. Returns a result dict."""
    prices, is_real = load_pair(ticker_a, ticker_b, period=period)
    a_name, b_name = prices.columns[:2]

    # ── Train/test split — the anti-lookahead core ────────────────────────
    n = len(prices)
    split = int(n * TRAIN_FRAC)
    train = prices.iloc[:split]
    test = prices.iloc[split:]

    beta = fit_hedge_ratio(train[a_name], train[b_name])

    train_spread = build_spread(train[a_name], train[b_name], beta)
    coint = adf_test(train_spread)
    hl = half_life(train_spread)

    # ── Out-of-sample application ─────────────────────────────────────────
    full_spread = build_spread(prices[a_name], prices[b_name], beta)
    z_full = rolling_zscore(full_spread, window=window)
    z_test = z_full.loc[test.index]

    positions = generate_positions(z_test, entry_z=entry_z, exit_z=exit_z)
    bt = backtest_pair(test, beta, positions, cost_bps=cost_bps)
    perf = summarise(bt)

    current_z = float(z_test.dropna().iloc[-1]) if z_test.notna().any() else float("nan")
    if pd.isna(current_z):
        signal = "insufficient data"
    elif current_z > entry_z:
        signal = f"SHORT spread (short {b_name}, long {a_name})"
    elif current_z < -entry_z:
        signal = f"LONG spread (long {b_name}, short {a_name})"
    elif abs(current_z) < exit_z:
        signal = "flat / no stretch"
    else:
        signal = "watch (approaching band)"

    return {
        "a": a_name, "b": b_name,
        "is_real": is_real,
        "price_a": float(prices[a_name].iloc[-1]),
        "price_b": float(prices[b_name].iloc[-1]),
        "beta": beta,
        "coint": coint,
        "half_life": hl,
        "current_z": current_z,
        "signal": signal,
        "perf": perf,
        "prices": prices, "z_test": z_test, "equity": bt["equity"],
        "window": window, "entry_z": entry_z, "exit_z": exit_z,
        "split_date": test.index[0],
    }


def print_result(r):
    real_tag = "" if r["is_real"] else "  [SIMULATED DATA — NOT A REAL RESULT]"
    print(f"\n{'='*66}")
    print(f"{r['a']} / {r['b']}{real_tag}")
    print(f"{'='*66}")
    print(f"Latest price     : {r['a']} ₹{r['price_a']:,.2f}  |  "
          f"{r['b']} ₹{r['price_b']:,.2f}")
    print(f"Hedge ratio (train): {r['beta']:.4f}")
    c = r["coint"]
    print(f"Cointegrated @5% : {c['cointegrated_5pct']} "
          f"(ADF {c['adf_stat']:.2f}, p={c['p_value']:.4f})")
    if "coint_bonf" in r:
        print(f"Bonferroni tier  : "
              f"{'PASS' if r['coint_bonf'] else 'fail'} "
              f"(strict α={r['bonf_alpha']:.4f})")
    hl = r["half_life"]
    print(f"Half-life        : {hl:.1f} days" if hl == hl else
          "Half-life        : n/a (not mean-reverting on train)")
    print(f"Current z-score  : {r['current_z']:+.2f}")
    print(f"Signal today     : {r['signal']}")
    if not c["cointegrated_5pct"]:
        print("  NOTE: pair did NOT cointegrate on training data — signal is "
              "not statistically justified; shown for observation only.")
    p = r["perf"]
    print(f"Out-of-sample backtest: Sharpe {p['sharpe']:.2f} | "
          f"return {p['annualised_return']:.2%} | "
          f"maxDD {p['max_drawdown']:.2%} | trades {p['round_trip_trades']}")


def run(pairs=None, **kwargs):
    pairs = pairs or DEFAULT_PAIRS
    n_declared = len(pairs)
    bonf_alpha = SIGNIFICANCE / n_declared

    results = []
    for ta, tb in pairs:
        try:
            r = analyse_pair(ta, tb, **kwargs)
            r["bonf_alpha"] = bonf_alpha
            r["coint_bonf"] = r["coint"]["p_value"] < bonf_alpha
            results.append(r)
            print_result(r)
        except Exception as exc:
            logger.error("Failed to analyse %s/%s: %s", ta, tb, exc)

    # Scan-level multiple-testing footer
    print(f"\n{'-'*66}")
    print(f"Multiple-testing note: {n_declared} pairs scanned at "
          f"{SIGNIFICANCE:.0%}. Expected false positives per run if NOTHING "
          f"truly cointegrates ≈ {SIGNIFICANCE * n_declared:.1f}. "
          f"Strict (Bonferroni) tier: p < {bonf_alpha:.4f}. "
          f"Single-day passes are candidates; persistence is evidence.")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indian pairs-trading scanner")
    parser.add_argument("--pair", nargs=2, metavar=("A", "B"),
                        help="analyse a single NSE pair, e.g. TCS.NS INFY.NS")
    parser.add_argument("--window", type=int, default=60)
    parser.add_argument("--entry", type=float, default=2.0)
    parser.add_argument("--exit", type=float, default=0.5)
    parser.add_argument("--cost", type=float, default=5.0)
    args = parser.parse_args()

    pairs = [tuple(args.pair)] if args.pair else None
    run(pairs=pairs, window=args.window, entry_z=args.entry,
        exit_z=args.exit, cost_bps=args.cost)
