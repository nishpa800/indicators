# Python is a Python time-based
# =============================================================================
# HV NRA — High-Volume (100..1000 / HEV / Hot Spot) — Pine v5 -> Python (TIME)
# -----------------------------------------------------------------------------
# base = hv_to_1k
# Source: "hv to 1k_06_07_124pm.txt" (June 7 batch) / corrected tick-friendly
#         "sources/pine_studies/plots/hv_to_1k/hv_to_1k.pine".
# Runtime GRAIN: wall-clock time bars (1m/5m/.../1D).
#
# Detection logic is IDENTICAL to the tick port: BOTH import the SAME shared core
# `_hv_to_1k_core.py`. HV NRA is bar-grain agnostic — `volume[1] ==
# ta.highest(volume,N)[1]` and the calendar Hot Spot windows read each bar's real
# timestamp, so the only difference between time and tick is the grain of the
# bars fed in. One code path, grain-bound (nine-nines rule).
# =============================================================================
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))  # the Python conversion root (has the core)

from _nine_nines_common import passthrough_time_bars  # noqa: E402
import _nn_harness as nn                               # noqa: E402
import _hv_to_1k_core as core                          # noqa: E402

HVInputs = core.HVInputs
DETECTION_PLOTS = core.DETECTION_PLOTS

# Match the tick default so tick==time parity is run on the same bar count.
DEFAULT_N = 1100


def run_on_rows(rows, *, inp: HVInputs | None = None):
    """Detect on (ts_ms, o, h, l, c, v) time-bar rows (oldest-first)."""
    bars = passthrough_time_bars(rows)
    return bars, core.compute(bars, inp)


def run_on_bars(bars, *, inp: HVInputs | None = None):
    """Detect on an already-built oldest-first list[Bar] of time bars."""
    return core.compute(bars, inp)


def run(grain: str = "time", n: int = DEFAULT_N, path: str | None = None,
        inp: HVInputs | None = None):
    bars = nn.load_bars(path, grain=grain, n=n)
    return bars, core.compute(bars, inp)


if __name__ == "__main__":
    bars, fires = run(grain="time")
    print("Python is a Python time-based — HV NRA (hv_to_1k)")
    print(f"bars={len(bars)}")
    plot_keys = ["plot_HEV"] + [f"plot_{N}" for N in core.LENS] + ["plot_HS"]
    for k in plot_keys:
        print(f"  {k}: {sum(fires[k])} fires")
