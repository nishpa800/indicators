"""NINE NINES — shared Python helpers for Pine v5 -> Python detection ports.

Python is a Python tick  /  Python is a Python time-based  (shared substrate)

This module holds the small, verified primitives every converted indicator
needs so each port does not re-derive them:

  * Bar         — one OHLCV bar (oldest-first series are lists of Bar).
  * sma / atr / change helpers that mirror Pine's ta.* exactly (Wilder ATR via
    RMA, simple SMA, first-N -> None like Pine na).
  * session bucketing helpers (UTC-day ordinal) reused for "new day" logic.
  * build_n_tick_bars / passthrough_time_bars — runtime-grain binders so the
    SAME detection code runs on N-tick bars and on time bars.

relativeVolume is NOT re-implemented here — when a port needs it, it imports the
canonical shim at ~/code/anish/realtime-indicators/rti/tv_ta_shim.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Sequence


@dataclass(frozen=True, slots=True)
class Bar:
    ts: int          # epoch milliseconds, bar OPEN time (oldest-first series)
    open: float
    high: float
    low: float
    close: float
    volume: float


# ───────────────────────── ta.* mirrors (Pine-faithful) ─────────────────────
def sma(series: Sequence[float], length: int) -> list[float | None]:
    """Pine ta.sma: simple moving average; first (length-1) bars are None (na)."""
    out: list[float | None] = []
    s = 0.0
    from collections import deque

    win: deque[float] = deque()
    for v in series:
        win.append(float(v))
        s += float(v)
        if len(win) > length:
            s -= win.popleft()
        out.append(s / length if len(win) == length else None)
    return out


def rma(series: Sequence[float], length: int) -> list[float | None]:
    """Pine ta.rma (Wilder's smoothing) — used by ta.atr."""
    out: list[float | None] = []
    prev: float | None = None
    seed_sum = 0.0
    for i, v in enumerate(series):
        v = float(v)
        if prev is None:
            seed_sum += v
            if i + 1 == length:
                prev = seed_sum / length
                out.append(prev)
            else:
                out.append(None)
        else:
            prev = (prev * (length - 1) + v) / length
            out.append(prev)
    return out


def true_range(bars: Sequence[Bar]) -> list[float]:
    """Pine ta.tr(true) equivalent series."""
    out: list[float] = []
    for i, b in enumerate(bars):
        if i == 0:
            out.append(b.high - b.low)
        else:
            pc = bars[i - 1].close
            out.append(max(b.high - b.low, abs(b.high - pc), abs(b.low - pc)))
    return out


def atr(bars: Sequence[Bar], length: int) -> list[float | None]:
    """Pine ta.atr(length) = rma(true_range, length)."""
    return rma(true_range(bars), length)


def change_nonzero(series: Sequence[float]) -> list[bool]:
    """Pine ta.change(x) != 0 as a boolean series (first bar False)."""
    out = [False]
    for i in range(1, len(series)):
        out.append(series[i] != series[i - 1])
    return out


def utc_day_ordinal(ts_ms: int) -> int:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).toordinal()


# ───────────────────────── runtime-grain binders ────────────────────────────
def build_n_tick_bars(trades: Sequence[tuple[int, float, float]], n: int) -> list[Bar]:
    """Aggregate raw (ts_ms, price, size) trades into N-tick OHLCV bars.

    Tick bars are stamped with the FIRST trade's ts (bar-open convention),
    matching the Pine tick-friendly outputs that score closed bars only.
    """
    bars: list[Bar] = []
    cnt = 0
    o = h = l = c = 0.0
    vol = 0.0
    ts0 = 0
    for ts, price, size in trades:
        if cnt == 0:
            o = h = l = c = price
            vol = 0.0
            ts0 = int(ts)
        h = max(h, price)
        l = min(l, price)
        c = price
        vol += float(size)
        cnt += 1
        if cnt == n:
            bars.append(Bar(ts0, o, h, l, c, vol))
            cnt = 0
    return bars  # drops the still-forming partial bar (closed bars only)


def passthrough_time_bars(rows: Sequence[tuple[int, float, float, float, float, float]]) -> list[Bar]:
    """Wrap (ts_ms, o, h, l, c, v) rows (oldest-first) into Bar objects."""
    return [Bar(int(t), float(o), float(hi), float(lo), float(cl), float(v)) for (t, o, hi, lo, cl, v) in rows]
