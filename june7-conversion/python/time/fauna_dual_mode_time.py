"""Python is a Python time-based — Fauna Dual Mode 2.0 fire-matrix on time bars.

Source: "fauna_dual_mode_tickfriendly.pine" (Pine v5, NINE NINES tick-friendly).
FULL port — every one of the 18 detection plots in the source is produced from
pure OHLCV by the shared core (_fauna_core). Same detection core as the tick
wrapper; the ONLY difference is the bar grain fed in (wall-clock time bars here).

Detection plots (PLOT_IDS):
  * BULL_COMBO_CODE / BEAR_COMBO_CODE — the FAUNA Bull/Bear plotshape markers;
    NINE NINES replaces the banned graphic-label call () combo text with the numeric
    resolved combo CODE. fire = marker active (combo code != 0 on a closed bar);
    level = the resolved CODE.
  * 14 family booleans MB/RE/GG/TA/TR/ES/GDR x bull/bear, fire == level.

Runtime GRAIN: time bars (1m/5m/15m/1h/daily/any named interval). Rows are
(ts_ms, o, h, l, c, v) oldest-first and every row is a CLOSED bar.

NOTE on relativeVolume: this source uses NO tv_ta / relativeVolume / timeframe.*
calls (pure OHLCV + ta.atr/ta.sma + prior-bar refs), so there is no RVOL anchor
and the canonical shim is not invoked by this port.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from _nine_nines_common import passthrough_time_bars  # noqa: E402
import _fauna_core as core  # noqa: E402

PLOT_IDS = core.PLOT_IDS
STUB_IDS = core.STUB_IDS


def run_on_rows(rows, *, show_bull=True, show_bear=True):
    """rows: (ts_ms, o, h, l, c, v) oldest-first. -> 18-plot fire matrix."""
    bars = passthrough_time_bars(rows)
    return run_on_bars(bars, show_bull=show_bull, show_bear=show_bear)


def run_on_bars(bars, *, show_bull=True, show_bear=True):
    return core.fire_matrix(bars, show_bull=show_bull, show_bear=show_bear)


if __name__ == "__main__":
    import random
    random.seed(5)
    rows = []
    t = 1_700_000_000_000
    px = 100.0
    for i in range(1000):
        o = px
        if i % 37 == 0:                         # injected gap/momentum shock
            px = o + (4.0 if (i // 37) % 2 == 0 else -4.0)
            hi = max(o, px) + 0.05
            lo = min(o, px) - 0.05
            vol = random.uniform(120000, 200000)
        else:
            px += random.uniform(-0.3, 0.3)
            hi = max(o, px) + random.uniform(0, 0.2)
            lo = min(o, px) - random.uniform(0, 0.2)
            vol = random.uniform(1000, 6000)
        rows.append((t, o, hi, lo, max(0.5, px), vol))
        t += 60_000
    out = run_on_rows(rows)
    fire_keys = [k for k in out if k.startswith("fire_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python time-based — Fauna Dual Mode 2.0 (FULL port)")
    print(f"bars={len(out['ts'])}  fire-plots={len(fire_keys)}  stub-plots={len(STUB_IDS)}  total fires={fires}")
    print(f"  bull_active={sum(out['bull_active'])}  bear_active={sum(out['bear_active'])}")
    nz = sorted(k for k in fire_keys if sum(out[k]) > 0)
    print(f"  plots that fired ({len(nz)}): {nz}")
