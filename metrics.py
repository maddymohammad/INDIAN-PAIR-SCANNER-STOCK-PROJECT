"""
metrics.py
----------
Performance and risk statistics on daily returns, annualised at 252 days.

These formulas were audited and are standard. Note: absolute return, vol,
and Calmar depend on the capital base chosen in the backtester; with the
fixed-capital convention now in place they are well-defined. Scale-invariant
metrics (Sharpe, Sortino, max drawdown %) are the most robust to report.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def sharpe_ratio(returns: pd.Series, rf: float = 0.0) -> float:
    excess = returns - rf / TRADING_DAYS
    if excess.std() == 0 or np.isnan(excess.std()):
        return 0.0
    return float(np.sqrt(TRADING_DAYS) * excess.mean() / excess.std())


def sortino_ratio(returns: pd.Series, rf: float = 0.0) -> float:
    excess = returns - rf / TRADING_DAYS
    downside = excess[excess < 0].std()
    if downside == 0 or np.isnan(downside):
        return float("nan")
    return float(np.sqrt(TRADING_DAYS) * excess.mean() / downside)


def max_drawdown(equity: pd.Series) -> float:
    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    return float(drawdown.min())


def annualised_return(equity: pd.Series) -> float:
    n_days = len(equity)
    if n_days < 2:
        return float("nan")
    total = equity.iloc[-1] / equity.iloc[0]
    return float(total ** (TRADING_DAYS / n_days) - 1)


def calmar_ratio(equity: pd.Series) -> float:
    mdd = abs(max_drawdown(equity))
    if mdd == 0:
        return float("nan")
    return float(annualised_return(equity) / mdd)


def summarise(results: pd.DataFrame) -> dict:
    """Return a plain dict of metrics (numbers, not strings) for reuse."""
    r = results["returns"].dropna()
    eq = results["equity"]
    n_trades = int(results["position"].diff().abs().sum())
    return {
        "annualised_return": annualised_return(eq),
        "annualised_vol": float(r.std() * np.sqrt(TRADING_DAYS)),
        "sharpe": sharpe_ratio(r),
        "sortino": sortino_ratio(r),
        "max_drawdown": max_drawdown(eq),
        "calmar": calmar_ratio(eq),
        "round_trip_trades": n_trades // 2,
        "total_cost": float(results["costs"].sum()),
    }
