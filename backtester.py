"""
backtester.py
-------------
Vectorised backtester for the pairs spread strategy.

CORRECTNESS PROPERTIES:
  1. SIGNAL LAG: positions.shift(1) — today trades on yesterday's signal.
  2. FROZEN BETA: beta is passed in already fit on the training window; this
     function never re-estimates it, preserving the train/test split.
  3. TRANSACTION COSTS: charged on position CHANGES, scaled by traded notional.
  4. EXPLICIT FIXED CAPITAL: returns are computed against a fixed, declared
     capital base (not a sample-dependent average), so absolute return and
     volatility figures are well-defined rather than an artefact of scaling.
     This fixes a flaw where dividing PnL by the sample-mean notional made
     the reported return level arbitrary.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def backtest_pair(
    prices: pd.DataFrame,
    beta: float,
    positions: pd.Series,
    cost_bps: float = 5.0,
    capital: float | None = None,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    prices   : DataFrame [asset_a, asset_b] for the TEST window
    beta     : hedge ratio fit on the TRAIN window (frozen)
    positions: Series in {-1,0,+1}, same index as prices
    cost_bps : one-way transaction cost in basis points of traded notional
    capital  : fixed capital base for return computation. If None, uses the
               notional of one spread unit at the FIRST test bar (a fixed,
               forward-looking-free constant), not a full-sample average.

    Returns
    -------
    DataFrame with position, gross_pnl, costs, net_pnl, returns, equity.
    """
    a = prices.iloc[:, 0]
    b = prices.iloc[:, 1]

    # 1. lag signal: trade tomorrow on today's signal
    pos = positions.shift(1).fillna(0.0)

    # 2. daily PnL of one spread unit (dollar-neutral construction)
    dpa = a.diff().fillna(0.0)
    dpb = b.diff().fillna(0.0)
    gross_pnl = pos * (dpb - beta * dpa)

    # 3. transaction costs on position changes
    trades = pos.diff().abs().fillna(0.0)
    notional_per_unit = b.abs() + beta * a.abs()
    costs = trades * notional_per_unit * (cost_bps / 1e4)

    net_pnl = gross_pnl - costs

    # 4. returns against a FIXED capital base (first-bar notional, or supplied)
    if capital is None:
        capital = float(notional_per_unit.iloc[0])
    returns = net_pnl / capital

    out = pd.DataFrame({
        "position": pos,
        "gross_pnl": gross_pnl,
        "costs": costs,
        "net_pnl": net_pnl,
        "returns": returns,
    })
    out["equity"] = (1 + out["returns"]).cumprod()
    return out
