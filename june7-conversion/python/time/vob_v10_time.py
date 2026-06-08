# Python is a Python time-based
# =============================================================================
# VOB Asym T3 x6 + MutEx Lines + Claude v10  ->  Python (TIME-BASED grain)
# Source (disk, path has spaces):
#   ".../June 7/Tick Friendly conversion/vob v10_tickfriendly.pine"
#
# FULL FAITHFUL PORT — ZERO STUBS. All 31 Pine plotshape() detection plots emit a
# per-bar 0/1 fire + numeric level. VOB v10 is fully OHLCV-derivable (NO
# relativeVolume, NO PB&J, NO request.security). The deep zone engine (f_vob A..F
# with proximity-dedup + close-through invalidation + T3 volume-pool comparison),
# Nagasaki, the strict F->A VLB ladder state machine, and the multi-zone
# same-candle counts are all ported construct-for-construct in the shared core
# (../_vob_v10_core.py).
#
# Time-grain entry point. Logic IDENTICAL to the tick port — both call the SAME
# shared core (_vob_v10_core.compute), one code path, grain-bound. The only
# difference is the bar-construction grain (wall-clock time bars here vs N-tick
# bars in ../tick/vob_v10_tick.py) and tf_seconds (60 on time vs the tick
# fallback). VOB has no per-TF table, so tf_seconds does not change the math.
#
# NOTE ON SENSITIVITY: production defaults are sens A..F = 2500..1000 (EMA lengths
# far exceeding a 900-bar synthetic run, so nothing fires on the demo data). The
# parity harness runs a SHORT-EMA sens set so the 31-plot fire matrix is exercised.
# =============================================================================
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # parent -> _vob_v10_core
sys.path.insert(0, _HERE)                     # local  -> _nn_harness
import _vob_v10_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS
fires_by_label = core.fires_by_label

GRAIN = "time"
DEFAULT_TF_SECONDS = 60

# COMPOSITE_PARTIAL: none — FULL port. Empty for honesty-gate inspection.
COMPOSITE_PARTIAL: list[str] = []


def run_on_bars(bars, *, params=None, tf_seconds=None, **_ignore):
    if tf_seconds is None:
        tf_seconds = DEFAULT_TF_SECONDS
    return core.compute(bars, params=params, tf_seconds=tf_seconds, grain="time")


def compute(bars, params=None, tf_seconds=None, **kw):
    return run_on_bars(bars, params=params, tf_seconds=tf_seconds)


def run(grain="time", n=900, path=None):
    import _nn_harness as nn  # noqa: E402
    bars = nn.load_bars(path, grain=grain, n=n)
    return bars, run_on_bars(bars)


if __name__ == "__main__":
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    short = dict(a=120, b=100, c=80, d=60, e=40, f=20)
    out = run_on_bars(bars, params={"sens": short, "cooldown_bars": 5})
    fire_keys = [k for k in out if k.startswith("fire_")]
    lvl_keys = [k for k in out if k.startswith("lvl_")]
    total = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python time-based — vob_v10 (FULL port, 31 detection plots, short-EMA demo)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  "
          f"level-cols={len(lvl_keys)}  total fires={total}  sigAny={sum(out['sigAny'])}")
    for k in fire_keys:
        nf = sum(out[k])
        if nf:
            print(f"  {k}: {nf} fires")
