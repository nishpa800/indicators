# Python is a Python time-based
"""PB & PBJ — 4 Signals -> Python (TIME grain). FULL port.

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/pbj_only_4_signals_tickfriendly.pine"
  (Pine v5, already tick-safe). EVERY one of the 4 detection plots (Sig#1 Bull PB,
  Sig#2 Bull PBJ, Sig#3 Bear PB, Sig#4 Bear PBJ) is produced from OHLCV by the
  shared core (_pbj_only_4_signals_core) — NO stub layer.

Runtime GRAIN: wall-clock time bars. Detection logic is IDENTICAL to the tick port
(bar-grain agnostic): both import the SAME core.compute and differ ONLY in the grain
of the bars fed in. One code path, grain-bound. This indicator has no
relativeVolume / per-TF-seconds dependency, so there is no anchor/tfSec divergence
between grains at all.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # so `_pbj_only_4_signals_core` resolves
sys.path.insert(0, _HERE)
from _nine_nines_common import passthrough_time_bars  # noqa: E402
import _pbj_only_4_signals_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS

GRAIN = "time"

# COMPOSITE_PARTIAL: none — this is a FULL port (same core as the tick module).
COMPOSITE_PARTIAL: list[str] = []


def run_on_rows(rows, *, params: Params | None = None):
    """rows: (ts_ms, o, h, l, c, v) oldest-first. -> 4-plot fire matrix + levels."""
    bars = passthrough_time_bars(rows)
    return run_on_bars(bars, params=params)


def run_on_bars(bars, *, params: Params | None = None, **_ignore):
    """**_ignore swallows tf_seconds kwargs from generic harnesses (no tfSec here)."""
    return core.compute(bars, params=params)


def compute(bars, params=None, **kw):
    """Dict-params or Params convenience entrypoint."""
    if isinstance(params, Params) or params is None:
        return run_on_bars(bars, params=params)
    return core.compute(bars, params=Params(**params))


if __name__ == "__main__":
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    out = run_on_bars(bars)
    fire_keys = [k for k in out if k.startswith("fire_")]
    lvl_keys = [k for k in out if k.startswith("lvl_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python time-based — pbj_only_4_signals (FULL port, 4 plots)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  "
          f"levels={len(lvl_keys)}  total fires={fires}  sigAny={sum(out['sigAny'])}")
    for k in fire_keys:
        print(f"  {k}: {sum(out[k])} fires")
