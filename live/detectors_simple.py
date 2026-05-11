"""Demo-tier detectors for the 4 AM BTC smoke test.

These are NOT canonical indicator plots. They are deliberately simple
OHLC-only conditions chosen to fire visibly on a low-volatility BTC 1m
chart so the UI/UX shows movement during the smoke test. The canonical
heavy_pentagon plots fire less frequently (correctly so — the thresholds
are calibrated for high-conviction setups).

Per Anish 2026-05-11: "make it something stupid that we know will happen
frequently, and then we'll just make sure that you are getting the exact
time."

Plots:
- Vol Spike       — volume >= 3x rolling 20-bar mean AND |c-o| >= 0.3% close
- Body 3 sigma    — |close-open| >= 3 * rolling-50 stdev of |close-open|
"""
from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


def detect_vol_spike(df: pd.DataFrame) -> bool:
    if len(df) < 21:
        return False
    vol = df["volume"]
    avg_vol = vol.iloc[-21:-1].mean()
    if avg_vol <= 0:
        return False
    rel_vol = vol.iloc[-1] / avg_vol
    body_pct = abs(df["close"].iloc[-1] - df["open"].iloc[-1]) / df["close"].iloc[-1]
    return bool(rel_vol >= 3.0 and body_pct >= 0.003)


def detect_body_3sigma(df: pd.DataFrame) -> bool:
    if len(df) < 51:
        return False
    body = (df["close"] - df["open"]).abs()
    sigma = body.iloc[-51:-1].std()
    if not np.isfinite(sigma) or sigma <= 0:
        return False
    return bool(body.iloc[-1] >= 3.0 * sigma)


SIMPLE_DETECTORS: Dict[str, callable] = {
    "Vol Spike": detect_vol_spike,
    "Body 3σ": detect_body_3sigma,
}
