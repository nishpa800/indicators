"""Python is a Python tick — B2B PUP Combined 5.4 fire-matrix on N-tick bars.

Source: "b2b_pup_tickfriendly.pine" (Pine v5). FULL port — every one of the 38
detection plots (fire_S1..S18 + S19/UC2 + S20/FMU x bull/bear) is produced from
OHLCV by the shared core (_b2b_pup_core). NO stub engine layer.

Runtime GRAIN: N-tick bars. relativeVolume anchor = "D" (wall-clock calendar day
of each bar's timestamp) on tick charts, per tradingview-import-decoupling — tick
bars never align to clock times so RVOL anchors to the bar's calendar day.

The tick module and the time module (../time/b2b_pup_time.py) share ONE core; the
only difference is the bar-construction grain fed in here.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from _nine_nines_common import build_n_tick_bars  # noqa: E402
import _b2b_pup_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS

# tick charts: assume 60s/bar for the per-TF threshold key (Pine
# nn_tick_assumed_sec default 60), and anchor RVOL to the wall-clock day.
TICK_ASSUMED_SEC = 60


def run_on_trades(trades, n_ticks: int, *, params: Params | None = None):
    """trades: (ts_ms, price, size) oldest-first. -> 38-plot fire matrix."""
    bars = build_n_tick_bars(trades, n_ticks)
    return run_on_bars(bars, params=params)


def run_on_bars(bars, *, params: Params | None = None):
    if params is None:
        params = Params(tfSec=TICK_ASSUMED_SEC, nn_tick_assumed_sec=TICK_ASSUMED_SEC)
    return core.compute(bars, params=params, rv_anchor="D")


if __name__ == "__main__":
    import random
    random.seed(13)
    # Build trades whose 50-tick bars form a strong oscillation (each bar a large
    # body) so the deep fire matrix is exercised on the tick grain too.
    trades = []
    t = 1_700_000_000_000
    px = 100.0
    bar_no = 0
    up = True
    for k in range(120000):
        if k % 50 == 0:                 # start of a new 50-tick bar
            bar_no += 1
            up = (bar_no % 12) < 6      # 6 up bars then 6 down bars
            target = px * (1 + (0.05 if up else -0.05))
            step = (target - px) / 50.0
        px += step + random.uniform(-0.002, 0.002)
        sz = random.uniform(2000, 12000)
        trades.append((t, max(0.5, px), sz))
        t += 1000
    out = run_on_trades(trades, 50)
    fire_keys = [k for k in out if k.startswith("fire_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python tick — B2B PUP Combined 5.4 (FULL port)")
    print(f"bars={len(out['ts'])}  fire-plots={len(fire_keys)}  total fires={fires}")
    print(f"  det_b2bPUP={sum(out['det_b2bPUP'])}  det_b2bPPD={sum(out['det_b2bPPD'])}")
    nz_plots = sorted(k for k in fire_keys if sum(out[k]) > 0)
    print(f"  plots that fired ({len(nz_plots)}): {nz_plots}")
