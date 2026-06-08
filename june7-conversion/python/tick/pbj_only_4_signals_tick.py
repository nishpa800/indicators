# Python is a Python tick
"""PB & PBJ — 4 Signals -> Python (TICK grain). FULL port.

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/pbj_only_4_signals_tickfriendly.pine"
  (Pine v5, ALREADY tick-safe — no `import TradingView/...`, no tv_ta.relativeVolume,
  no timeframe.in_seconds(), no per-TF threshold table, no time(timeframe.period,..)).
  EVERY one of the 4 detection plots (Sig#1 Bull PB, Sig#2 Bull PBJ, Sig#3 Bear PB,
  Sig#4 Bear PBJ) is produced from OHLCV by the shared core
  (_pbj_only_4_signals_core) — NO stub layer.

Runtime GRAIN: N-tick bars (built from raw trades). This indicator has NO
relativeVolume / per-TF-seconds dependency, so there is NO RVOL anchor and NO
tfSec key — the engines (Zoo MA, ATR supertrend, PB&J filter, level/approach
state machine) are bar-grain agnostic and run identically on tick and time bars.

The tick module and the time module (../time/pbj_only_4_signals_time.py) share ONE
core; the only difference is the bar-construction grain fed in here (N-tick bars
vs wall-clock time bars). One code path, grain-bound.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # so `_pbj_only_4_signals_core` resolves
sys.path.insert(0, _HERE)
from _nine_nines_common import build_n_tick_bars  # noqa: E402
import _pbj_only_4_signals_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS

GRAIN = "tick"

# COMPOSITE_PARTIAL: none — this is a FULL port. Retained (empty) so any honesty
# gate that inspects it sees zero stubbed plots.
COMPOSITE_PARTIAL: list[str] = []


def run_on_trades(trades, n_ticks: int, *, params: Params | None = None):
    """trades: (ts_ms, price, size) oldest-first. -> 4-plot fire matrix + levels."""
    bars = build_n_tick_bars(trades, n_ticks)
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
    print("Python is a Python tick — pbj_only_4_signals (FULL port, 4 plots)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  "
          f"levels={len(lvl_keys)}  total fires={fires}  sigAny={sum(out['sigAny'])}")
    for k in fire_keys:
        print(f"  {k}: {sum(out[k])} fires")
