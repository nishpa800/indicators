# Python is a Python tick
"""VOB v11 MULTIPLES TICK-FRIENDLY -> Python (TICK grain). FULL port.

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/vob_11_tickfriendly.pine"
  (Pine v5, tick-safe: reg_anchorSafe forces "D" on tick charts; in_seconds guard
  with tick_assumed_tfsec fallback; relativeVolume via tv_ta ta/7 anchorSafe.)

EVERY detection plot the v11 MULTIPLES source emits (Nagasaki, ZONEFORM_BULL/BEAR
A..F, zone-creation markers, T3 buy/sell A..F, VLB bull/bear, multi-zone 2/3
bull/bear, T3 cluster, VOBxHW coincidence) is produced from OHLCV by the shared
core (_vob_11_core) — there is NO stub layer. The deep multi-sensitivity zone
engine + strict F->A VLB ladder + embedded HW-Single v3 engine are all ported.

Runtime GRAIN: N-tick bars (built from raw trades). relativeVolume (HWS Reg@Time)
anchors to the wall-clock CALENDAR DAY of each bar timestamp (tick bars do not
align to clock times), exactly the nine-nines harness convention — see
tradingview-import-decoupling. tf_seconds defaults to TICK_FALLBACK_SEC on tick
(the source's tick_assumed_tfsec guard).

The tick module and the time module (../time/vob_11_time.py) share ONE core; the
only difference is the bar-construction grain fed in here (N-tick bars vs
wall-clock time bars) and the tf_seconds passed to the HWS threshold ladder.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # parent -> _vob_11_core, _nine_nines_common
sys.path.insert(0, _HERE)                     # local -> _nn_harness
from _nine_nines_common import build_n_tick_bars  # noqa: E402
import _vob_11_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS

GRAIN = "tick"
TICK_FALLBACK_SEC = 60   # source tick_assumed_tfsec default (line 1726)

# COMPOSITE_PARTIAL: none — FULL port. Retained (empty) so honesty gates see 0 stubs.
COMPOSITE_PARTIAL: list[str] = []


def run_on_trades(trades, n_ticks: int, *, params: Params | None = None, tf_seconds=None):
    """trades: (ts_ms, price, size) oldest-first -> full fire matrix + levels."""
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
    fire_keys = [k for k in PLOT_IDS]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python tick — vob_11 (FULL port)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  "
          f"total fires={fires}  sigAny={sum(out['sigAny'])}  hws_any={sum(out['hws_any'])}")
    for k in fire_keys:
        nn = sum(out[k])
        if nn:
            print(f"  {k}: {nn} fires")
