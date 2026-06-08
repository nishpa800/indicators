# Python is a Python tick
# =============================================================================
# VOB Asym T3 x6 + MutEx Lines + Claude v10  ->  Python (TICK-BASED grain)
# Source (disk, path has spaces):
#   ".../June 7/Tick Friendly conversion/vob v10_tickfriendly.pine"
#
# FULL FAITHFUL PORT — ZERO STUBS. All 31 Pine plotshape() detection plots emit a
# per-bar 0/1 fire + numeric level. VOB v10 is fully OHLCV-derivable (NO
# relativeVolume, NO PB&J, NO request.security), so the deep zone engine, T3
# volume-pool comparison, Nagasaki, VLB F->A ladder, and multi-zone counts are
# all ported construct-for-construct in the shared core (../_vob_v10_core.py).
#
# TICK DISTINCTION: bar grain only. VOB has no per-TF threshold table and no RVOL
# anchor, so there is NO RE10023 exposure here. EMA `sens` lengths count BARS (not
# wall-clock), which is identical semantics on N-tick bars. The tick module and
# the time module (../time/vob_v10_time.py) share ONE core; the only difference is
# the bar-construction grain fed in (N-tick bars vs wall-clock time bars).
# =============================================================================
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # parent -> _vob_v10_core, _nine_nines_common
sys.path.insert(0, _HERE)                     # local  -> _nn_harness
from _nine_nines_common import build_n_tick_bars  # noqa: E402
import _vob_v10_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS
fires_by_label = core.fires_by_label

GRAIN = "tick"
TICK_FALLBACK_SEC = 10

# COMPOSITE_PARTIAL: none — FULL port. Empty so honesty gates see 0 stubs.
COMPOSITE_PARTIAL: list[str] = []


def run_on_trades(trades, n_ticks: int, *, params=None, tf_seconds=None):
    """trades: (ts_ms, price, size) oldest-first -> N-tick bars -> 31-plot matrix."""
    bars = build_n_tick_bars(trades, n_ticks)
    return run_on_bars(bars, params=params, tf_seconds=tf_seconds)


def run_on_bars(bars, *, params=None, tf_seconds=None, **_ignore):
    if tf_seconds is None:
        tf_seconds = TICK_FALLBACK_SEC
    return core.compute(bars, params=params, tf_seconds=tf_seconds, grain="tick")


def compute(bars, params=None, tf_seconds=None, **kw):
    return run_on_bars(bars, params=params, tf_seconds=tf_seconds)


if __name__ == "__main__":
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    short = dict(a=120, b=100, c=80, d=60, e=40, f=20)
    out = run_on_bars(bars, params={"sens": short, "cooldown_bars": 5})
    fire_keys = [k for k in out if k.startswith("fire_")]
    lvl_keys = [k for k in out if k.startswith("lvl_")]
    total = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python tick — vob_v10 (FULL port, 31 detection plots)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  "
          f"level-cols={len(lvl_keys)}  total fires={total}  sigAny={sum(out['sigAny'])}")
    for k in fire_keys:
        nf = sum(out[k])
        if nf:
            print(f"  {k}: {nf} fires")
