# Python is a Python time-based
"""VOB v11 MULTIPLES TICK-FRIENDLY -> Python (TIME grain). FULL port.

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/vob_11_tickfriendly.pine"

Same shared core (_vob_11_core) as the tick wrapper — ONE detection code path.
The only difference is the runtime GRAIN of the bars fed in (wall-clock time bars
here vs N-tick bars in ../tick/vob_11_tick.py) and the tf_seconds passed to the
HWS threshold ladder (the bar period in seconds).

EVERY detection plot is produced from OHLCV by the core. No stub layer.
relativeVolume (HWS Reg@Time) via the canonical tv_ta shim (anchor "D").
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # parent -> _vob_11_core, _nine_nines_common
sys.path.insert(0, _HERE)                     # local -> _nn_harness
from _nine_nines_common import passthrough_time_bars  # noqa: E402
import _vob_11_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS

GRAIN = "time"
DEFAULT_TF_SEC = 60   # 1-minute bars by default

# COMPOSITE_PARTIAL: none — FULL port. Retained (empty) so honesty gates see 0 stubs.
COMPOSITE_PARTIAL: list[str] = []


def run_on_rows(rows, *, params: Params | None = None, tf_seconds=None):
    """rows: (ts_ms, o, h, l, c, v) oldest-first -> full fire matrix + levels."""
    bars = passthrough_time_bars(rows)
    return run_on_bars(bars, params=params, tf_seconds=tf_seconds)


def run_on_bars(bars, *, params: Params | None = None, tf_seconds=None, **_ignore):
    if tf_seconds is None:
        tf_seconds = DEFAULT_TF_SEC
    return core.compute(bars, params=params, tf_seconds=tf_seconds, grain="time")


def compute(bars, params=None, tf_seconds=None, **kw):
    if isinstance(params, Params) or params is None:
        return run_on_bars(bars, params=params, tf_seconds=tf_seconds)
    return core.compute(bars, params=Params(**params), tf_seconds=tf_seconds, grain="time")


if __name__ == "__main__":
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    out = run_on_bars(bars)
    fire_keys = [k for k in PLOT_IDS]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python time-based — vob_11 (FULL port)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  "
          f"total fires={fires}  sigAny={sum(out['sigAny'])}  hws_any={sum(out['hws_any'])}")
    for k in fire_keys:
        nn = sum(out[k])
        if nn:
            print(f"  {k}: {nn} fires")
