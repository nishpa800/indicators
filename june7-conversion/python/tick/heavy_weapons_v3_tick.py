"""Python is a Python tick — Heavy Weapons Single v3 fire-matrix on N-tick bars.

Source: ".../June 7/Tick Friendly conversion/heavy weapons v3_tickfriendly.pine"
        (Pine v5, import TradingView/ta/7). FULL port — every one of the 44
        detection plots (every plotshape signal in the source) is produced from
        OHLCV by the shared core (_heavy_weapons_v3_core). NO stub engine layer.

Runtime GRAIN: N-tick bars. relativeVolume anchor = "D" (wall-clock calendar day
of each bar's timestamp) on tick charts, per tradingview-import-decoupling and the
Pine RE10023 fix (force "D" on tick) — tick bars never align to clock times so RVOL
anchors to the bar's calendar day, never the tick index.

The tick module and the time module (../time/heavy_weapons_v3_time.py) share ONE
core; the only differences are (a) the bar-construction grain fed in here and
(b) the per-TF threshold key tfSec, which on tick uses the Pine nn_TICK_FB=10s
fallback (timeframe.in_seconds() is na on tick).
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from _nine_nines_common import build_n_tick_bars  # noqa: E402
import _heavy_weapons_v3_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS
compute = core.compute

GRAIN = "tick"
RVOL_ANCHOR = "D"            # wall-clock DAY anchor even on tick bars (RE10023 fix)
TICK_FALLBACK_SEC = 10       # Pine nn_TICK_FB (timeframe.in_seconds() na on tick)


def run_on_trades(trades, n_ticks: int, *, params: Params | None = None):
    """trades: (ts_ms, price, size) oldest-first. -> 44-plot fire matrix + levels."""
    bars = build_n_tick_bars(trades, n_ticks)
    return run_on_bars(bars, params=params)


def run_on_bars(bars, *, params: Params | None = None, tf_seconds: int = TICK_FALLBACK_SEC):
    if params is None:
        params = Params(tfSec=tf_seconds, nn_tick_assumed_sec=TICK_FALLBACK_SEC)
    return core.compute(bars, params=params, rv_anchor=RVOL_ANCHOR)


if __name__ == "__main__":
    import sys as _sys
    from pathlib import Path
    _sys.path.insert(0, _HERE)
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    out = run_on_bars(bars)
    fire_keys = [k for k in out if k.startswith("fire_")]
    lvl_keys = [k for k in out if k.startswith("lvl_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python tick — Heavy Weapons Single v3 (FULL port)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  levels={len(lvl_keys)}  total fires={fires}")
    nz_plots = sorted(k for k in fire_keys if sum(out[k]) > 0)
    print(f"  plots that fired ({len(nz_plots)}): {[k[5:] for k in nz_plots]}")
