"""Python is a Python tick — f2 e3 detection on N-tick bars.

Runtime grain: N-tick OHLCV bars (build_n_tick_bars). The detection core
(_f2_e3_core.compute) is runtime-grain agnostic; this wrapper only binds raw
trades -> N-tick bars and calls the shared core. Tick and time share ONE core.

Source: "/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT
transformed yet/June 7/Tick Friendly conversion/f2_e3_tickfriendly.pine"
(Pine v5, "e3 f2 cluster THIS bull bear 58% reduction THIS").

Fire matrix: S1..S8 (every plotshape; see _f2_e3_core.PLOT_IDS).
Emits per-bar 0/1 fire + numeric level for every detection plot.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))  # Python conversion/ (shared core)
from _nine_nines_common import build_n_tick_bars  # noqa: E402
import _f2_e3_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS


def run_on_trades(trades, n_ticks: int, *, use_session: bool = True, params=None):
    """trades: oldest-first list of (ts_ms, price, size). Returns fire matrix.

    Aggregates trades into N-tick OHLCV bars (drops the still-forming partial),
    then runs the shared detection core.
    """
    bars = build_n_tick_bars(trades, n_ticks)
    return core.compute(bars, use_session=use_session, params=params)


def run_on_bars(bars, *, use_session: bool = True, params=None):
    """Already-built N-tick Bar list (oldest-first)."""
    return core.compute(bars, use_session=use_session, params=params)


if __name__ == "__main__":
    # tiny deterministic smoke run (self-contained LCG, no external deps)
    _state = [7]

    def rnd():
        _state[0] = (1103515245 * _state[0] + 12345) & 0x7FFFFFFF
        return _state[0] / 0x7FFFFFFF

    trades = []
    t = 1_700_000_000_000
    px = 100.0
    for _ in range(5000):
        px += (rnd() - 0.5) * 0.1
        trades.append((t, px, 1 + rnd() * 49))
        t += 1000
    out = run_on_trades(trades, 25, use_session=False)
    fires = sum(out["S7_any_bull"]) + sum(out["S8_any_bear"])
    print(f"f2_e3 tick: {len(out['ts'])} bars, any-fires={fires}")
