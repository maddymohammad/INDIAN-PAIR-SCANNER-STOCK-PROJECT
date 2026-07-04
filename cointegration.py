"""
cointegration.py
----------------
Engle-Granger cointegration test and spread half-life estimation.

KEY CORRECTNESS PROPERTY (train/test split):
    The hedge ratio (beta) must be estimated on a TRAINING window only,
    then FROZEN and applied to the out-of-sample test window. Estimating
    beta on the full sample and then backtesting over that same sample is
    lookahead bias — the strategy would be using future data to size its
    positions. This module exposes fit_hedge_ratio() (train only) and
    build_spread() (apply frozen beta) so the pipeline can enforce the split.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller


def fit_hedge_ratio(price_a: pd.Series, price_b: pd.Series) -> float:
    """
    Estimate the hedge ratio beta by regressing B on A (with intercept):
        B = alpha + beta * A + residual
    Returns beta only. Fit this on the TRAINING window exclusively.
    """
    x = sm.add_constant(price_a.values)
    model = sm.OLS(price_b.values, x).fit()
    return float(model.params[1])


def build_spread(price_a: pd.Series, price_b: pd.Series, beta: float) -> pd.Series:
    """
    Construct the spread B - beta*A using a PRE-FITTED beta.
    Safe to call on the test window with a beta fit on the train window.
    """
    return price_b - beta * price_a


def adf_test(spread: pd.Series) -> dict:
    """
    Augmented Dickey-Fuller stationarity test on a spread series.
    A stationary spread is the statistical justification for mean-reversion
    trading. Returns the statistic, p-value, and a 5% cointegration verdict.
    """
    spread = pd.Series(spread).dropna()
    stat, pvalue, _, _, crit, _ = adfuller(spread.values, autolag="AIC")
    return {
        "adf_stat": float(stat),
        "p_value": float(pvalue),
        "crit_5pct": float(crit["5%"]),
        "cointegrated_5pct": bool(stat < crit["5%"]),
    }


def engle_granger_test(price_a: pd.Series, price_b: pd.Series) -> dict:
    """
    Full-sample Engle-Granger test — for REPORTING whether a pair
    cointegrates over the whole history. This is the statistically correct
    use of the full sample (a descriptive test), and is kept SEPARATE from
    the backtest's beta, which must come from fit_hedge_ratio on train only.
    """
    beta = fit_hedge_ratio(price_a, price_b)
    spread = build_spread(price_a, price_b, beta)
    result = {"beta": beta, "spread": spread}
    result.update(adf_test(spread))
    return result


def half_life(spread: pd.Series) -> float:
    """
    Estimate mean-reversion half-life via an AR(1) fit on the spread:
        dS_t = lambda * S_{t-1} + eps
    half-life = -ln(2) / lambda. Returns NaN if the series isn't
    mean-reverting (lambda >= 0).
    """
    spread = pd.Series(spread).dropna()
    lagged = spread.shift(1).dropna()
    delta = spread.diff().dropna()
    lagged = lagged.loc[delta.index]

    x = sm.add_constant(lagged.values)
    model = sm.OLS(delta.values, x).fit()
    lam = model.params[1]
    if lam >= 0:
        return float("nan")
    return float(-np.log(2) / lam)
