"""Python is a Python time-based — Heavy Weapons w SAAB Kratos x2 fire-matrix on time bars.

Source: ".../June 7/Tick Friendly conversion/heavy_with_2x_detection_plots_tickfriendly.pine"
        (Pine v5, import TradingView/ta/7). FULL port — same shared core as the tick
        wrapper (_heavy_with_2x_detection_plots_core). Every one of the 42 detection
        plots is produced from OHLCV; there is NO stub engine layer.

Runtime GRAIN: wall-clock time bars. relativeVolume anchor = "D" (the wall-clock
calendar day), matching the Pine source on time charts (blank anchor -> chart TF;
we anchor to "D" exactly as the source does after the RE10023 anchorSafe coercion).
tfSec is the per-TF threshold key in seconds/bar (Pine timeframe.in_seconds()).
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from _nine_nines_common import passthrough_time_bars  # noqa: E402
import _heavy_with_2x_detection_plots_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS
compute = core.compute

GRAIN = "time"
RVOL_ANCHOR = "D"           # wall-clock day anchor (Pine "" -> chart; we use "D")


def run_on_rows(rows, *, params: Params | None = None, tf_seconds: int = 60):
    """rows: (ts_ms, o, h, l, c, v) oldest-first. -> 42-plot fire matrix + levels."""
    bars = passthrough_time_bars(rows)
    return run_on_bars(bars, params=params, tf_seconds=tf_seconds)


def run_on_bars(bars, *, params: Params | None = None, tf_seconds: int = 60):
    if params is None:
        params = Params(tfSec=tf_seconds)
    return core.compute(bars, params=params, rv_anchor=RVOL_ANCHOR)


if __name__ == "__main__":
    sys.path.insert(0, _HERE)
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    out = run_on_bars(bars, tf_seconds=60)
    fire_keys = [k for k in out if k.startswith("fire_")]
    lvl_keys = [k for k in out if k.startswith("lvl_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python time-based — heavy_with_2x_detection_plots (FULL port)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  levels={len(lvl_keys)}  total fires={fires}")
    nz_plots = sorted(k for k in fire_keys if sum(out[k]) > 0)
    print(f"  plots that fired ({len(nz_plots)}): {[k[5:] for k in nz_plots]}")
