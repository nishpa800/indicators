"""Python is a Python time-based — f2 e3 detection on time bars.

Runtime grain: standard time OHLCV bars (1m/5m/.../1D). SAME detection core as
the tick wrapper (_f2_e3_core.compute); this binds (ts,o,h,l,c,v) rows -> Bar
list. Tick and time share ONE core module — identical detection logic.

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
from _nine_nines_common import passthrough_time_bars  # noqa: E402
import _f2_e3_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS


def run_on_rows(rows, *, use_session: bool = True, params=None):
    """rows: oldest-first (ts_ms, o, h, l, c, v). Returns fire matrix dict."""
    bars = passthrough_time_bars(rows)
    return core.compute(bars, use_session=use_session, params=params)


def run_on_bars(bars, *, use_session: bool = True, params=None):
    return core.compute(bars, use_session=use_session, params=params)


if __name__ == "__main__":
    # tiny deterministic smoke run (self-contained LCG, no external deps)
    _state = [11]

    def rnd():
        _state[0] = (1103515245 * _state[0] + 12345) & 0x7FFFFFFF
        return _state[0] / 0x7FFFFFFF

    rows = []
    t = 1_700_000_000_000
    px = 100.0
    for _ in range(800):
        o = px
        px += (rnd() - 0.5) * 0.6
        hi = max(o, px) + rnd() * 0.2
        lo = min(o, px) - rnd() * 0.2
        rows.append((t, o, hi, lo, px, 1000 + rnd() * 4000))
        t += 60_000
    out = run_on_rows(rows, use_session=False)
    fires = sum(out["S7_any_bull"]) + sum(out["S8_any_bear"])
    print(f"f2_e3 time: {len(out['ts'])} bars, any-fires={fires}")
