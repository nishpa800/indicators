# Python is a Python tick
# =============================================================================
# HV NRA — High-Volume (100..1000 / HEV / Hot Spot) — Pine v5 -> Python (TICK)
# -----------------------------------------------------------------------------
# base = hv_to_1k
# Source: "hv to 1k_06_07_124pm.txt" (June 7 batch) / corrected tick-friendly
#         "sources/pine_studies/plots/hv_to_1k/hv_to_1k.pine".
# Runtime GRAIN: N-tick bars (each Bar is one completed N-tick candle).
#
# This is a THIN wrapper. ALL detection logic lives in the ONE shared core
# `_hv_to_1k_core.py` (imported by both the tick and time modules), so the tick
# and time ports run the SAME code path on different bar grains — exactly the
# nine-nines "one canonical core" rule.
#
# FULL faithful port: every detection plot (plot_HEV, plot_1000..plot_100,
# plot_HS) + every raw condition (is100..is1000, isHEV, isHotSpot) + numeric
# levels. Nothing is stubbed (the source has zero Tier-C/D surface).
# =============================================================================
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))  # the Python conversion root (has the core)

from _nine_nines_common import build_n_tick_bars  # noqa: E402
import _nn_harness as nn                           # noqa: E402
import _hv_to_1k_core as core                      # noqa: E402

HVInputs = core.HVInputs
DETECTION_PLOTS = core.DETECTION_PLOTS

# Default sample large enough to WARM the 1000-bar rolling high (else plot_1000 /
# HEV can never fire on the synthetic feed and parity would prove nothing).
DEFAULT_N = 1100


def run_on_trades(trades, n_ticks: int, *, inp: HVInputs | None = None):
    """Aggregate raw (ts_ms, price, size) trades into N-tick bars, then detect."""
    bars = build_n_tick_bars(trades, n_ticks)
    return bars, core.compute(bars, inp)


def run_on_bars(bars, *, inp: HVInputs | None = None):
    """Detect on an already-built oldest-first list[Bar] of N-tick bars."""
    return core.compute(bars, inp)


def run(grain: str = "tick", n: int = DEFAULT_N, path: str | None = None,
        inp: HVInputs | None = None):
    bars = nn.load_bars(path, grain=grain, n=n)
    return bars, core.compute(bars, inp)


if __name__ == "__main__":
    bars, fires = run(grain="tick")
    print("Python is a Python tick — HV NRA (hv_to_1k)")
    print(f"bars={len(bars)}")
    plot_keys = ["plot_HEV"] + [f"plot_{N}" for N in core.LENS] + ["plot_HS"]
    for k in plot_keys:
        print(f"  {k}: {sum(fires[k])} fires")
