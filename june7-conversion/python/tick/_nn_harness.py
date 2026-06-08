# Python is a Python tick   /   Python is a Python time-based
# =============================================================================
# NINE NINES shared conversion harness
# -----------------------------------------------------------------------------
# Provides the common machinery every Pine v5 -> Python detection-plot port in
# this batch needs:
#   * Bar          : a single OHLCV bar (immutable).
#   * Series       : Pine-style series accessor s[i] = i bars back (s[0]=current).
#   * rolling helpers (sma, stdev, highest, lowest, atr, cum) that mirror Pine ta.*
#   * relative_volume shim re-export (canonical tv_ta.relativeVolume, ta/7).
#   * synthetic_bars / load_bars : deterministic OHLCV for runnable parity.
#
# This file is imported by both the tick/ and time/ ports. The ONLY difference
# between a tick port and a time port is the runtime GRAIN of the bars fed in
# (N-tick bars vs wall-clock minute bars) and the relative_volume anchor:
#   - time grain : anchor "D" keys off the wall-clock day (Pine "D").
#   - tick grain : anchor is STILL the wall-clock day (tick bars do not align to
#                  clock times, so RVOL anchors to the calendar day of each bar's
#                  timestamp, never the tick index). See tradingview-import-decoupling.
# =============================================================================
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

# --- canonical relativeVolume shim (vendored re-export) ----------------------
# Prefer the live repo shim; fall back to the local vendored copy beside this file.
_SHIM = None
for _p in (
    "/Users/anishpatel/code/anish/realtime-indicators",
):
    if Path(_p).exists() and _p not in sys.path:
        sys.path.insert(0, _p)
try:
    from rti import tv_ta_shim as _SHIM  # type: ignore
except Exception:
    _SHIM = None

if _SHIM is None:
    # vendored fallback beside this harness
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import tv_ta_shim_vendored as _SHIM  # type: ignore


def relative_volume(volume, length, *, anchor_timeframe="D", is_cumulative=True,
                    bar_timestamps):
    """Canonical Pine tv_ta.relativeVolume(ta/7). Returns (curr, past, ratio) lists."""
    res = _SHIM.relative_volume(
        list(volume), int(length),
        anchor_timeframe=anchor_timeframe,
        is_cumulative=bool(is_cumulative),
        bar_timestamps=list(bar_timestamps),
    )
    return res.curr_vol, res.past_vol, res.vol_ratio


# --- Bar ---------------------------------------------------------------------
@dataclass(frozen=True)
class Bar:
    ts: int      # epoch millis (bar OPEN time)
    open: float
    high: float
    low: float
    close: float
    volume: float


# --- Series (Pine series semantics: s[0] = current bar, s[i] = i bars back) ---
class Series:
    """Forward-built series. Append values in chronological order; index with
    Pine offset semantics relative to a cursor `i` (the current bar index)."""

    __slots__ = ("_v",)

    def __init__(self, values: Sequence[float] | None = None):
        self._v: list = list(values) if values is not None else []

    def append(self, x):
        self._v.append(x)

    def at(self, i: int, off: int = 0):
        """Value `off` bars back from bar index i. Returns None (Pine na) OOB."""
        j = i - off
        if j < 0 or j >= len(self._v):
            return None
        return self._v[j]

    def __len__(self):
        return len(self._v)

    def __getitem__(self, k):
        return self._v[k]

    def tolist(self):
        return list(self._v)


# --- Pine ta.* equivalents (vector form, oldest-first) -----------------------
def _f(x):
    return None if x is None else float(x)


def nz(x, repl=0.0):
    return repl if (x is None or (isinstance(x, float) and math.isnan(x))) else x


def sma(values, length):
    """ta.sma: simple moving average; None until `length` real values available."""
    out = [None] * len(values)
    s = 0.0
    cnt = 0
    from collections import deque
    win = deque()
    for i, v in enumerate(values):
        vv = None if v is None else float(v)
        win.append(vv)
        if vv is not None:
            s += vv
            cnt += 1
        if len(win) > length:
            old = win.popleft()
            if old is not None:
                s -= old
                cnt -= 1
        if len(win) == length and cnt == length:
            out[i] = s / length
    return out


def stdev(values, length):
    """ta.stdev: population standard deviation over `length` (biased, like Pine)."""
    out = [None] * len(values)
    from collections import deque
    win = deque()
    for i, v in enumerate(values):
        vv = None if v is None else float(v)
        win.append(vv)
        if len(win) > length:
            win.popleft()
        if len(win) == length and all(w is not None for w in win):
            m = sum(win) / length
            var = sum((w - m) ** 2 for w in win) / length
            out[i] = math.sqrt(var)
    return out


def highest(values, length):
    out = [None] * len(values)
    from collections import deque
    win = deque()
    for i, v in enumerate(values):
        win.append(None if v is None else float(v))
        if len(win) > length:
            win.popleft()
        vals = [w for w in win if w is not None]
        if len(win) == length and vals:
            out[i] = max(vals)
    return out


def lowest(values, length):
    out = [None] * len(values)
    from collections import deque
    win = deque()
    for i, v in enumerate(values):
        win.append(None if v is None else float(v))
        if len(win) > length:
            win.popleft()
        vals = [w for w in win if w is not None]
        if len(win) == length and vals:
            out[i] = min(vals)
    return out


def rma(values, length):
    """Wilder's RMA (used by ta.atr)."""
    out = [None] * len(values)
    prev = None
    seed_sum = 0.0
    seed_cnt = 0
    for i, v in enumerate(values):
        vv = None if v is None else float(v)
        if vv is None:
            out[i] = prev
            continue
        if prev is None:
            seed_sum += vv
            seed_cnt += 1
            if seed_cnt == length:
                prev = seed_sum / length
                out[i] = prev
        else:
            prev = (prev * (length - 1) + vv) / length
            out[i] = prev
    return out


def true_range(o, h, l, c):
    n = len(c)
    tr = [None] * n
    for i in range(n):
        if i == 0:
            tr[i] = h[i] - l[i]
        else:
            tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    return tr


def atr(o, h, l, c, length):
    return rma(true_range(o, h, l, c), length)


def cum(values):
    out = [None] * len(values)
    s = 0.0
    for i, v in enumerate(values):
        s += 0.0 if v is None else float(v)
        out[i] = s
    return out


def shift(values, off):
    """Pine values[off] as a vector (off>0 = look back)."""
    n = len(values)
    out = [None] * n
    for i in range(n):
        j = i - off
        out[i] = values[j] if 0 <= j < n else None
    return out


# --- deterministic synthetic OHLCV (for runnable parity) ---------------------
def synthetic_bars(n=900, *, grain="time", seed=20260607, start_ts=None):
    """Deterministic OHLCV bars. grain='time' -> 1-minute wall-clock bars across
    several RTH sessions; grain='tick' -> 500-tick bars stamped within sessions.
    Uses a self-contained LCG so output is identical on every machine/run."""
    import datetime as _dt

    state = seed & 0x7FFFFFFF

    def rnd():
        nonlocal state
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        return state / 0x7FFFFFFF

    if start_ts is None:
        base = _dt.datetime(2026, 5, 1, 8, 30, 0)  # 08:30 CST RTH open
    else:
        base = _dt.datetime.utcfromtimestamp(start_ts / 1000)

    bars = []
    price = 100.0
    # Keep sessions SHORT so a 900-bar run spans many days. RVOL "at time"
    # averages over prior sessions, so we need lots of them (>= reg_length+1).
    bars_per_session = 20 if grain == "time" else 18
    minute = 0
    session = 0
    cnt = 0
    while cnt < n:
        for k in range(bars_per_session):
            if cnt >= n:
                break
            # day rollover
            day = base + _dt.timedelta(days=session)
            if grain == "time":
                ts_dt = day + _dt.timedelta(minutes=k)
            else:
                # tick bars: cluster within the session, ~3s apart, irregular
                ts_dt = day + _dt.timedelta(seconds=int(k * (3 + rnd() * 4)))
            ts = int(ts_dt.timestamp() * 1000)

            # base drift, with deliberate SHOCK candles so the detection-plot
            # fire matrix is actually exercised (otherwise every plot reads 0 and
            # parity proves nothing). Shocks: large body + FVG-creating gap + vol.
            shock = rnd() > 0.90
            mega = rnd() > 0.985
            drift = (rnd() - 0.5) * 0.6
            if shock:
                drift = (1.0 if rnd() > 0.5 else -1.0) * (3.0 + rnd() * 5.0)
            o = price
            c = max(0.5, o + drift)
            body = abs(c - o)
            if shock:
                hi = max(o, c) + body * (0.05 + rnd() * 0.15)
                lo = min(o, c) - body * (0.05 + rnd() * 0.15)
            else:
                hi = max(o, c) + rnd() * 0.4
                lo = min(o, c) - rnd() * 0.4
            # volume smile: heavy at open/close, thin midday + occasional spikes
            smile = 1.0 + 1.8 * math.cos((k / bars_per_session) * math.pi) ** 2
            spike = 1.0
            if shock:
                spike = 8.0 + rnd() * 8.0
            if mega:
                spike = 40.0 + rnd() * 60.0   # ATH-class volume for Nagasaki/HV
            vol = round((400 + rnd() * 600) * smile * spike, 2)
            bars.append(Bar(ts, round(o, 4), round(hi, 4), round(lo, 4), round(c, 4), vol))
            price = c
            cnt += 1
        session += 1
    return bars


def load_bars(path=None, *, grain="time", n=900):
    """Load bars from CSV (ts,open,high,low,close,volume) if `path` given and
    exists; otherwise return deterministic synthetic bars."""
    if path and Path(path).exists():
        import csv
        out = []
        with open(path) as fh:
            for row in csv.DictReader(fh):
                out.append(Bar(int(float(row["ts"])), float(row["open"]),
                               float(row["high"]), float(row["low"]),
                               float(row["close"]), float(row["volume"])))
        return out
    return synthetic_bars(n=n, grain=grain)


# --- columns helper ----------------------------------------------------------
def columns(bars):
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    l = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]
    return o, h, l, c, v, ts
