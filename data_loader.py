"""
data_loader.py
--------------
Loads REAL daily price data for Indian (NSE) stock pairs via Yahoo Finance.

Primary mode is LIVE real data — this project is explicitly about real
Indian stocks, not synthetic series. A synthetic generator is retained
ONLY as an offline fallback for CI smoke-tests and local development when
Yahoo is unreachable; it is never the basis for any reported result and
is clearly logged when used.

NSE tickers use the '.NS' suffix on Yahoo Finance (e.g. 'HDFCBANK.NS').
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def load_live_prices(
    ticker_a: str,
    ticker_b: str,
    period: str = "3y",
) -> pd.DataFrame:
    """
    Download auto-adjusted daily closes for two NSE tickers.
    Returns a DataFrame with columns [ticker_a, ticker_b], inner-joined on
    dates both traded, missing values dropped.
    """
    import yfinance as yf

    raw = yf.download([ticker_a, ticker_b], period=period,
                      auto_adjust=True, progress=False)
    close = raw["Close"]
    # Ensure column order matches the requested pair
    close = close[[ticker_a, ticker_b]].dropna()
    if len(close) < 250:
        raise ValueError(
            f"Only {len(close)} overlapping days for {ticker_a}/{ticker_b} — "
            "insufficient history for a reliable test."
        )
    return close


def simulate_cointegrated_pair(
    ticker_a: str = "SIM_A.NS",
    ticker_b: str = "SIM_B.NS",
    n_days: int = 750,
    seed: int = 42,
) -> pd.DataFrame:
    """
    OFFLINE FALLBACK ONLY. Simulate a cointegrated pair so CI can smoke-test
    the pipeline without network access. NOT a source of real results.
    Column names carry a 'SIM_' prefix so simulated data is unmistakable in
    any report that accidentally uses it.
    """
    logger.warning("Using SIMULATED data — not a real result. For testing only.")
    rng = np.random.default_rng(seed)
    log_ret = 0.0002 + 0.012 * rng.standard_normal(n_days)
    price_a = 100.0 * np.exp(np.cumsum(log_ret))

    spread = np.zeros(n_days)
    shocks = rng.standard_normal(n_days)
    for t in range(1, n_days):
        spread[t] = spread[t - 1] + 0.05 * (0.0 - spread[t - 1]) + 0.6 * shocks[t]

    price_b = 1.5 * price_a + spread
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n_days)
    return pd.DataFrame({ticker_a: price_a, ticker_b: price_b}, index=dates)


def load_pair(
    ticker_a: str,
    ticker_b: str,
    period: str = "3y",
    allow_synthetic_fallback: bool = True,
) -> tuple[pd.DataFrame, bool]:
    """
    Single entry point. Returns (prices, is_real).

    Attempts real Yahoo Finance data first. If that fails and
    allow_synthetic_fallback is True, returns simulated data flagged
    is_real=False so callers can label the output honestly.
    """
    try:
        prices = load_live_prices(ticker_a, ticker_b, period=period)
        logger.info("Loaded %d real days for %s/%s", len(prices), ticker_a, ticker_b)
        return prices, True
    except Exception as exc:
        logger.warning("Real data fetch failed for %s/%s: %s", ticker_a, ticker_b, exc)
        if not allow_synthetic_fallback:
            raise
        return simulate_cointegrated_pair(ticker_a, ticker_b), False
