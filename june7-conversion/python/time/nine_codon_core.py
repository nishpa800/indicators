"""nine_codon_core — pure-stdlib Pine v5 semantics for the NineNines detection-plot ports.

CODON identity: an exact construct-for-construct mapping Pine v5 -> Python, gated to
parity, NOT an approximation. This module holds the shared, dependency-free building
blocks every converted indicator in this batch needs:

  - Bar dataclass (frozen) and a deterministic synthetic-bar generator used by the
    parity/determinism gates (no network, no numpy/pandas — runs anywhere).
  - Pine series helpers implemented as explicit forward-walk state so the commit
    ordering matches Pine (`x[1]` is read BEFORE the end-of-bar history advance):
      sma, stdev (BIASED / population, ddof=0 — Pine's ta.stdev default),
      rma (alpha=1/n, SMA seed) -> atr (rma of true range, bar0 TR = high-low),
      ema (alpha=2/(n+1), src seed), highest/lowest, change, crossover/crossunder,
      barssince, nz, cum.

These mirror /Volumes/OWC Envoy Ultra/NineNines/Skills pine 5 to python/sme/04 §2.
Determinism: same inputs -> same outputs every run (the gate asserts this).

NO binary-float accumulator discipline note: these detection plots compare boolean
fires + threshold ratios, not money; floats are used for the windowed TA math exactly
as Pine does. Price/accumulator integerization (price_e4) is reserved for the candle
layer, which is upstream of (and a precondition for) these plot ports.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class Bar:
    ts: int          # epoch milliseconds, session/exchange-anchored, monotonic
    open: float
    high: float
    low: float
    close: float
    volume: float


# --------------------------------------------------------------------------- #
# Deterministic synthetic bar generator (parity / determinism input)          #
# --------------------------------------------------------------------------- #
def synth_bars(n: int, *, seed: int = 1020, tf_seconds: int = 60,
               session_bars: int = 390, start_ms: int = 1_700_000_000_000,
               spikes: bool = True) -> list[Bar]:
    """Reproducible OHLCV stream with a session reset every `session_bars` bars.

    Pure LCG (no random module dependence on global state) so the sequence is
    byte-identical across runs and machines. Volume has an intraday "smile" (heavy
    at the session open/close) so relativeVolume-at-time has something real to chew.
    When `spikes` is True, deterministic high-volume / wide-body bars are injected on
    a fixed cadence so the RVOL / matrix / fauna detection plots actually fire — this
    makes the parity gate exercise the real branches, not just the calm baseline.
    """
    bars: list[Bar] = []
    state = seed & 0xFFFFFFFF
    price = 100.0
    day = 0
    ts = start_ms
    for i in range(n):
        # advance LCG
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        r = state / 0x7FFFFFFF            # 0..1
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        r2 = state / 0x7FFFFFFF
        k = i % session_bars
        if k == 0 and i > 0:
            day += 1
            # gap on session open
            price *= (1.0 + (r - 0.5) * 0.01)
        # session timestamp: new calendar day each session reset
        ts = start_ms + day * 86_400_000 + k * tf_seconds * 1000
        # deterministic spike cadence: every 37th bar a wide bullish/bearish body,
        # every 53rd a volume blowout. Fixed, so the gate is reproducible.
        is_body_spike = spikes and i > 5 and i % 37 == 0
        is_vol_spike = spikes and i > 5 and i % 53 == 0
        bull_spike = (i // 37) % 2 == 0
        drift = (r - 0.5) * 1.2
        if is_body_spike:
            drift = (3.5 if bull_spike else -3.5) + (r - 0.5) * 0.5
        o = price
        c = price + drift
        hi = max(o, c) + r2 * 0.6
        lo = min(o, c) - (1.0 - r2) * 0.6
        # intraday volume smile
        smile = 1.0 + 2.5 * (math.cos((k / session_bars) * 2 * math.pi) + 1.0) / 2.0
        vol = (500.0 + r2 * 4000.0) * smile
        if is_vol_spike or is_body_spike:
            vol *= 25.0
        bars.append(Bar(ts=ts, open=round(o, 4), high=round(hi, 4),
                        low=round(lo, 4), close=round(c, 4), volume=round(vol, 2)))
        price = c
    return bars


# --------------------------------------------------------------------------- #
# Pine series helpers — vectorized once over the full oldest-first series      #
# Each returns a list aligned 1:1 with input; None == Pine `na` (warmup).      #
# --------------------------------------------------------------------------- #
def nz(x, repl=0.0):
    return repl if x is None or (isinstance(x, float) and math.isnan(x)) else x


def sma(src: Sequence[float | None], length: int) -> list[float | None]:
    out: list[float | None] = [None] * len(src)
    for i in range(len(src)):
        if i + 1 < length:
            continue
        window = src[i - length + 1: i + 1]
        if any(v is None for v in window):
            continue
        out[i] = sum(window) / length
    return out


def stdev(src: Sequence[float | None], length: int) -> list[float | None]:
    """Pine ta.stdev — BIASED (population, ddof=0)."""
    out: list[float | None] = [None] * len(src)
    for i in range(len(src)):
        if i + 1 < length:
            continue
        window = src[i - length + 1: i + 1]
        if any(v is None for v in window):
            continue
        m = sum(window) / length
        var = sum((v - m) ** 2 for v in window) / length
        out[i] = math.sqrt(var)
    return out


def ema(src: Sequence[float], length: int) -> list[float | None]:
    """Pine ta.ema — alpha = 2/(n+1), seeded with first value."""
    out: list[float | None] = [None] * len(src)
    alpha = 2.0 / (length + 1)
    prev = None
    for i, v in enumerate(src):
        if v is None:
            out[i] = prev
            continue
        prev = v if prev is None else alpha * v + (1 - alpha) * prev
        out[i] = prev
    return out


def rma(src: Sequence[float], length: int) -> list[float | None]:
    """Pine ta.rma — alpha = 1/n, seeded with the SMA of the first `length`."""
    out: list[float | None] = [None] * len(src)
    alpha = 1.0 / length
    prev = None
    for i, v in enumerate(src):
        if v is None:
            out[i] = prev
            continue
        if prev is None:
            if i + 1 >= length:
                seed_win = src[i - length + 1: i + 1]
                if all(x is not None for x in seed_win):
                    prev = sum(seed_win) / length
                    out[i] = prev
            continue
        prev = alpha * v + (1 - alpha) * prev
        out[i] = prev
    return out


def atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float],
        length: int) -> list[float | None]:
    """Pine ta.atr — rma of True Range; bar-0 TR = high-low."""
    tr: list[float] = []
    for i in range(len(closes)):
        if i == 0:
            tr.append(highs[i] - lows[i])
        else:
            pc = closes[i - 1]
            tr.append(max(highs[i] - lows[i], abs(highs[i] - pc), abs(lows[i] - pc)))
    return rma(tr, length)


def highest(src: Sequence[float], length: int) -> list[float | None]:
    out: list[float | None] = [None] * len(src)
    for i in range(len(src)):
        if i + 1 < length:
            # Pine highest returns the max of available bars even pre-warmup? No:
            # ta.highest needs `length` bars; before that it returns na. We mirror na.
            continue
        out[i] = max(src[i - length + 1: i + 1])
    return out


def lowest(src: Sequence[float], length: int) -> list[float | None]:
    out: list[float | None] = [None] * len(src)
    for i in range(len(src)):
        if i + 1 < length:
            continue
        out[i] = min(src[i - length + 1: i + 1])
    return out


def vwma_safe(src: Sequence[float], vol: Sequence[float], length: int) -> list[float | None]:
    """Pine ta.vwma(src, len) = sma(src*vol, len) / sma(vol, len).

    `_safe` guards a zero-volume window (returns None == na) so callers never
    divide by zero; this matches Pine returning na when the volume SMA is 0/na."""
    n = len(src)
    sv = sma([src[i] * vol[i] for i in range(n)], length)
    sv2 = sma(list(vol), length)
    out: list[float | None] = [None] * n
    for i in range(n):
        if sv[i] is None or sv2[i] is None or sv2[i] == 0:
            continue
        out[i] = sv[i] / sv2[i]
    return out


def cum(src: Sequence[float]) -> list[float]:
    out: list[float] = []
    run = 0.0
    for v in src:
        run += (0.0 if v is None else v)
        out.append(run)
    return out


def change(src: Sequence[float | None], length: int = 1) -> list[float | None]:
    out: list[float | None] = [None] * len(src)
    for i in range(len(src)):
        if i - length < 0:
            continue
        a, b = src[i], src[i - length]
        if a is None or b is None:
            continue
        out[i] = a - b
    return out


def crossover(a: Sequence[float | None], b: Sequence[float | None]) -> list[bool]:
    out = [False] * len(a)
    for i in range(1, len(a)):
        if None in (a[i], b[i], a[i - 1], b[i - 1]):
            continue
        out[i] = a[i] > b[i] and a[i - 1] <= b[i - 1]
    return out


def crossunder(a: Sequence[float | None], b: Sequence[float | None]) -> list[bool]:
    out = [False] * len(a)
    for i in range(1, len(a)):
        if None in (a[i], b[i], a[i - 1], b[i - 1]):
            continue
        out[i] = a[i] < b[i] and a[i - 1] >= b[i - 1]
    return out


def barssince(cond: Sequence[bool]) -> list[int | None]:
    out: list[int | None] = [None] * len(cond)
    last = None
    for i, c in enumerate(cond):
        if c:
            last = 0
        elif last is not None:
            last += 1
        out[i] = last
    return out


def shift(series: Sequence, k: int):
    """Pine `series[k]` aligned 1:1 (None where it reaches before the start)."""
    out = [None] * len(series)
    for i in range(len(series)):
        if i - k >= 0:
            out[i] = series[i - k]
    return out
