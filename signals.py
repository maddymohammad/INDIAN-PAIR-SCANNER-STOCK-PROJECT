"""
signals.py
----------
Convert a spread series into trading positions via a rolling z-score.

CORRECTNESS: the z-score uses a TRAILING window (min_periods enforced),
so the value at time t uses only data up to and including t. The backtester
additionally lags positions by one bar, so no trade ever uses same-bar or
future information.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def rolling_zscore(spread: pd.Series, window: int = 60) -> pd.Series:
    """
    Trailing z-score: (spread - rolling_mean) / rolling_std.
    Uses a backward-looking window only. Requires a full window of data
    before emitting a value (min_periods=window) to avoid unstable early
    estimates.
    """
    mean = spread.rolling(window, min_periods=window).mean()
    std = spread.rolling(window, min_periods=window).std()
    z = (spread - mean) / std
    return z.replace([np.inf, -np.inf], np.nan)


def generate_positions(
    z: pd.Series,
    entry_z: float = 2.0,
    exit_z: float = 0.5,
) -> pd.Series:
    """
    State-machine position logic on the z-score:
      - Enter SHORT spread (-1) when z rises above +entry_z (spread too high)
      - Enter LONG spread (+1) when z falls below -entry_z (spread too low)
      - Exit to flat (0) when |z| falls back below exit_z
      - Otherwise hold the current position

    Returns a Series in {-1, 0, +1} aligned to z's index. Positions are
    NOT lagged here — the backtester applies the one-bar lag.
    """
    pos = pd.Series(0.0, index=z.index)
    current = 0.0

    for i, zi in enumerate(z.values):
        if np.isnan(zi):
            pos.iloc[i] = current
            continue

        if current == 0.0:
            if zi > entry_z:
                current = -1.0
            elif zi < -entry_z:
                current = 1.0
        else:
            if abs(zi) < exit_z:
                current = 0.0
        pos.iloc[i] = current

    return pos
