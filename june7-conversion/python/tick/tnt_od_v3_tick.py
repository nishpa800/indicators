# Python is a Python tick
"""TNT Opening Drive OD v3 -> Python (TICK grain). FULL port (47 detection plots).

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/tnt_od_v3_tickfriendly.pine"
  (Pine v5, tick-safe: t_isTickChart / t_regAnchorSafe / TICK_FALLBACK_SEC guards,
  relativeVolume via tv_ta ta/7 anchorSafe.)

EVERY one of the 47 numeric data_window detection plots (`plot(p_* ? 1 : 0, "f_*")`)
is produced from OHLCV by the shared core (_tnt_od_v3_core) — NO stub layer. This
SUPERSEDES the earlier PARTIAL port that stubbed 39 fires at 0.

Runtime GRAIN: N-tick bars (built from raw trades). relativeVolume anchors to the
wall-clock CALENDAR DAY of each bar timestamp (tick bars do not align to clock
times), exactly the nine-nines harness convention — see tradingview-import-decoupling.
tf_seconds defaults to TICK_FALLBACK_SEC (10) on tick (the source's tick guard).

The tick module and the time module (../time/tnt_od_v3_time.py) share ONE core;
the only difference is the bar-construction grain fed in here (N-tick bars vs
wall-clock time bars) and the tf_seconds passed to the per-TF threshold curves.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # parent -> _tnt_od_v3_core, _nine_nines_common
sys.path.insert(0, _HERE)                     # local -> _nn_harness
from _nine_nines_common import build_n_tick_bars  # noqa: E402
import _tnt_od_v3_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS

GRAIN = "tick"
TICK_FALLBACK_SEC = 10

# COMPOSITE_PARTIAL: none — FULL port. Retained (empty) so honesty gates see 0 stubs.
COMPOSITE_PARTIAL: list[str] = []


def run_on_trades(trades, n_ticks: int, *, params: Params | None = None, tf_seconds=None):
    """trades: (ts_ms, price, size) oldest-first -> 47-plot fire matrix + levels."""
    bars = build_n_tick_bars(trades, n_ticks)
    return run_on_bars(bars, params=params, tf_seconds=tf_seconds)


def run_on_bars(bars, *, params: Params | None = None, tf_seconds=None, **_ignore):
    if tf_seconds is None:
        tf_seconds = TICK_FALLBACK_SEC
    return core.compute(bars, params=params, tf_seconds=tf_seconds, grain="tick")


def compute(bars, params=None, tf_seconds=None, **kw):
    if isinstance(params, Params) or params is None:
        return run_on_bars(bars, params=params, tf_seconds=tf_seconds)
    return core.compute(bars, params=Params(**params), tf_seconds=tf_seconds, grain="tick")


if __name__ == "__main__":
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    out = run_on_bars(bars)
    fire_keys = [k for k in out if k.startswith("fire_")]
    lvl_keys = [k for k in out if k.startswith("lvl_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python tick — tnt_od_v3 (FULL port, 47 detection plots)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  "
          f"level-cols={len(lvl_keys)}  total fires={fires}  sigAny={sum(out['sigAny'])}")
    for k in fire_keys:
        n = sum(out[k])
        if n:
            print(f"  {k}: {n} fires")
