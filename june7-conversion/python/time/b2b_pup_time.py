"""Python is a Python time-based — B2B PUP Combined 5.4 fire-matrix on time bars.

Source: "b2b_pup_tickfriendly.pine" (Pine v5). FULL port — same shared core as the
tick wrapper (_b2b_pup_core). Every one of the 38 detection plots is produced from
OHLCV; there is NO stub engine layer.

Runtime GRAIN: wall-clock time bars. relativeVolume anchor = "D" (the wall-clock
calendar day), matching the Pine source ("" -> identical-to-source on time charts).
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from _nine_nines_common import passthrough_time_bars  # noqa: E402
import _b2b_pup_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS


def run_on_rows(rows, *, params: Params | None = None, tf_seconds: int = 60):
    """rows: (ts_ms, o, h, l, c, v) oldest-first. -> 38-plot fire matrix."""
    bars = passthrough_time_bars(rows)
    return run_on_bars(bars, params=params, tf_seconds=tf_seconds)


def run_on_bars(bars, *, params: Params | None = None, tf_seconds: int = 60):
    if params is None:
        params = Params(tfSec=tf_seconds)
    return core.compute(bars, params=params, rv_anchor="D")


if __name__ == "__main__":
    import random
    random.seed(17)
    rows = []
    t = 1_700_000_000_000
    px = 100.0
    for i in range(1500):
        o = px
        if i % 47 in (0, 1):        # back-to-back up moves -> exercise b2bPUP
            px = o * 1.05
            hi, lo, vol = px, o, 500000.0
        elif i % 61 in (0, 1):      # back-to-back down moves -> b2bPPD
            px = o * 0.95
            hi, lo, vol = o, px, 500000.0
        else:
            px = o + random.uniform(-0.2, 0.2)
            hi = max(o, px) + 0.1
            lo = min(o, px) - 0.1
            vol = 1000.0
        rows.append((t + i * 60_000, o, hi, lo, px, vol))
    out = run_on_rows(rows)
    fire_keys = [k for k in out if k.startswith("fire_")]
    print("Python is a Python time-based — B2B PUP Combined 5.4 (FULL port)")
    print(f"bars={len(out['ts'])}  fire-plots={len(fire_keys)}")
    print(f"  det_b2bPUP={sum(out['det_b2bPUP'])}  S1_bull fires={sum(out['fire_S1_bull'])}")
    nz_plots = sorted(k for k in fire_keys if sum(out[k]) > 0)
    print(f"  plots that fired ({len(nz_plots)}): {nz_plots}")
