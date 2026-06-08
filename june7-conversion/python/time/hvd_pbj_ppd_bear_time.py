# Python is a Python time-based
"""BASE HV+D <-> PBJ <-> PPD v1 — BEARISH (36) -> Python (TIME grain). FULL port.

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/hvd pbj ppd bear_tickfriendly.pine"
  (Pine v5, import TradingView/ta/7). EVERY one of the 36 detection plots is
  produced from OHLCV by the shared core (_hvd_pbj_ppd_bear_core) — NO stub layer.

Runtime GRAIN: wall-clock time bars. relativeVolume anchor = "D" (Pine "D" session
day). The time module and the tick module (../tick/hvd_pbj_ppd_bear_tick.py) share
ONE core; the only differences are (a) the bar-construction grain fed in and (b)
tfSec (the per-TF threshold key), which on time bars is the real bar duration.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)
import _hvd_pbj_ppd_bear_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS

GRAIN = "time"
RVOL_ANCHOR = "D"
COMPOSITE_PARTIAL: list[str] = []   # FULL port — zero stubbed plots


def run_on_bars(bars, *, params: Params | None = None, tf_seconds: int = 60):
    if params is None:
        params = Params(tfSec=tf_seconds)
    return core.compute(bars, params=params, rv_anchor=RVOL_ANCHOR)


def compute(bars, params=None, *, tf_seconds: int = 60):
    """Dict-params convenience entrypoint (mirrors the older wrapper signature)."""
    if isinstance(params, Params):
        return core.compute(bars, params=params, rv_anchor=RVOL_ANCHOR)
    if params is None:
        return core.compute(bars, params=Params(tfSec=tf_seconds), rv_anchor=RVOL_ANCHOR)
    return core.compute(bars, params=Params(tfSec=tf_seconds, **params), rv_anchor=RVOL_ANCHOR)


if __name__ == "__main__":
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    out = run_on_bars(bars, tf_seconds=3600)
    fire_keys = [k for k in out if k.startswith("fire_")]
    lvl_keys = [k for k in out if k.startswith("lvl_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python time-based — hvd_pbj_ppd_bear (FULL port, 36 plots)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  levels={len(lvl_keys)}  total fires={fires}")
    nz_plots = sorted(k for k in fire_keys if sum(out[k]) > 0)
    print(f"  plots that fired ({len(nz_plots)}): {[k[5:] for k in nz_plots]}")
