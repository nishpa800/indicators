"""Python is a Python tick — Fauna Dual Mode 2.0 fire-matrix on N-tick bars.

Source: "fauna_dual_mode_tickfriendly.pine" (Pine v5, NINE NINES tick-friendly).
FULL port — every one of the 18 detection plots in the source is produced from
pure OHLCV by the shared core (_fauna_core). NO stub layer.

Detection plots (PLOT_IDS):
  * BULL_COMBO_CODE / BEAR_COMBO_CODE — the FAUNA Bull/Bear plotshape markers;
    NINE NINES replaces the banned graphic-label call () combo text with the numeric
    resolved combo CODE (Pine plot(display=display.data_window)). fire = marker
    active (combo code != 0 on a closed bar); level = the resolved CODE.
  * 14 family booleans MB/RE/GG/TA/TR/ES/GDR x bull/bear — the data-window 0/1
    detector plots, fire == level.

Runtime GRAIN: N-tick bars (built by _nine_nines_common.build_n_tick_bars, which
drops the still-forming partial bar so only CLOSED bars are scored — matching the
Pine barstate.isconfirmed gate).

NOTE on relativeVolume: this indicator's source uses NO tv_ta / relativeVolume /
timeframe.* calls (it is pure OHLCV + ta.atr/ta.sma + prior-bar refs), so there is
no RVOL anchor to set and no RE10023 surface. The canonical shim
~/code/anish/realtime-indicators/rti/tv_ta_shim.py is therefore not invoked by this
port; it remains the mandated path for any indicator that DOES use relativeVolume.

The tick module and the time module (../time/fauna_dual_mode_time.py) share ONE
core; the only difference is the bar-construction grain fed in here.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from _nine_nines_common import build_n_tick_bars  # noqa: E402
import _fauna_core as core  # noqa: E402

PLOT_IDS = core.PLOT_IDS
STUB_IDS = core.STUB_IDS


def run_on_trades(trades, n_ticks: int, *, show_bull=True, show_bear=True):
    """trades: (ts_ms, price, size) oldest-first. -> 18-plot fire matrix."""
    bars = build_n_tick_bars(trades, n_ticks)
    return run_on_bars(bars, show_bull=show_bull, show_bear=show_bear)


def run_on_bars(bars, *, show_bull=True, show_bear=True):
    return core.fire_matrix(bars, show_bull=show_bull, show_bear=show_bear)


if __name__ == "__main__":
    import random
    random.seed(3)
    N = 25                                   # ticks per bar
    trades = []
    t = 1_700_000_000_000
    px = 100.0
    bar_no = 0
    # Build trades whose 25-tick bars include strong gap/momentum bodies so the
    # fire matrix is exercised on the tick grain too. On a shock bar we drive a
    # large, almost-monotone move (close far from open, tiny wicks, big volume);
    # on calm bars we drift quietly with normal volume.
    for k in range(6000):
        if k % N == 0:
            bar_no += 1
            shock = (bar_no % 7) == 0
            up = (bar_no % 2) == 0
            if shock:
                target = px * (1 + (0.05 if up else -0.05))
                step = (target - px) / N
                tick_vol = lambda: random.uniform(3000, 6000)
            else:
                step = 0.0
                tick_vol = lambda: random.uniform(1, 60)
        px += step + (random.uniform(-0.003, 0.003) if step else random.uniform(-0.01, 0.01))
        trades.append((t, max(0.5, px), tick_vol()))
        t += 1000
    out = run_on_trades(trades, N)
    fire_keys = [k for k in out if k.startswith("fire_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python tick — Fauna Dual Mode 2.0 (FULL port)")
    print(f"bars={len(out['ts'])}  fire-plots={len(fire_keys)}  stub-plots={len(STUB_IDS)}  total fires={fires}")
    print(f"  bull_active={sum(out['bull_active'])}  bear_active={sum(out['bear_active'])}")
    nz = sorted(k for k in fire_keys if sum(out[k]) > 0)
    print(f"  plots that fired ({len(nz)}): {nz}")
