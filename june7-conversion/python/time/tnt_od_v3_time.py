# Python is a Python time-based
"""TNT Opening Drive OD v3 -> Python (TIME grain). FULL port (47 detection plots).

Time-grain entry point. Logic identical to the tick port — both call the SAME
shared core (_tnt_od_v3_core.compute), one code path, grain-bound. The only
difference is the bar-construction grain (wall-clock time bars here vs N-tick bars
in ../tick/tnt_od_v3_tick.py) and tf_seconds (defaults 60 on time vs the tick
fallback on tick). EVERY one of the 47 data_window detection plots is ported from
OHLCV — NO stub layer (supersedes the earlier PARTIAL port).
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # parent -> _tnt_od_v3_core
sys.path.insert(0, _HERE)                     # local -> _nn_harness
import _tnt_od_v3_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS

GRAIN = "time"
DEFAULT_TF_SECONDS = 60

# COMPOSITE_PARTIAL: none — FULL port. Retained (empty) for honesty-gate inspection.
COMPOSITE_PARTIAL: list[str] = []


def run_on_bars(bars, *, params: Params | None = None, tf_seconds=None, **_ignore):
    if tf_seconds is None:
        tf_seconds = DEFAULT_TF_SECONDS
    return core.compute(bars, params=params, tf_seconds=tf_seconds, grain="time")


def compute(bars, params=None, tf_seconds=None, **kw):
    if isinstance(params, Params) or params is None:
        return run_on_bars(bars, params=params, tf_seconds=tf_seconds)
    return core.compute(bars, params=Params(**params), tf_seconds=tf_seconds, grain="time")


def run(grain="time", n=900, path=None):
    import _nn_harness as nn  # noqa: E402
    bars = nn.load_bars(path, grain=grain, n=n)
    return bars, run_on_bars(bars)


if __name__ == "__main__":
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    out = run_on_bars(bars)
    fire_keys = [k for k in out if k.startswith("fire_")]
    lvl_keys = [k for k in out if k.startswith("lvl_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python time-based — tnt_od_v3 (FULL port, 47 detection plots)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  "
          f"level-cols={len(lvl_keys)}  total fires={fires}  sigAny={sum(out['sigAny'])}")
    for k in fire_keys:
        n = sum(out[k])
        if n:
            print(f"  {k}: {n} fires")
