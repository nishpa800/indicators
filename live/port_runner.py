"""Runs heavy_pentagon Pipeline-1 detections on each closed bar."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from python_ports.heavy_pentagon import canonical as hp
from live import detectors_simple

# Heavy-pentagon Pipeline-1 plots — pure OHLCV, no STUBBED upstream needed.
# Calibrated for high-conviction setups; will fire less often than the simple
# demo detectors below.
HEAVY_PENTAGON_PLOTS: List[str] = [
    "Bull RVOL 1x",
    "Bear RVOL 1x",
    "MOAB",
]

# Demo-tier simple detectors — fire frequently for UI/UX demo. Per Anish
# 2026-05-11: "make it something stupid that we know will happen frequently."
SIMPLE_PLOTS: List[str] = list(detectors_simple.SIMPLE_DETECTORS.keys())

# Full plot list shown in the leaderboard (order = column order).
SMOKE_TEST_PLOTS: List[str] = HEAVY_PENTAGON_PLOTS + SIMPLE_PLOTS

# Pine's `show_*` IPSF flags gate `fire_*` outputs and default to False for
# Bull RVOL 1x / Bear RVOL 1x in the .pine source. We force-enable so the
# canonical signals get evaluated regardless of plot visibility defaults.
_FORCE_SHOW_PARAMS: Dict[str, bool] = {
    "show_BullRVOL1x": True,
    "show_BearRVOL1x": True,
    "show_MOAB": True,
}

MIN_BARS = 50


def run_smoke_test(df: pd.DataFrame) -> Dict[str, bool]:
    """Run all smoke-test plots on df; return last-bar fire state per plot."""
    if len(df) < MIN_BARS:
        return {name: False for name in SMOKE_TEST_PLOTS}
    df.attrs.pop("_heavy_pentagon_eng", None)
    out: Dict[str, bool] = {}
    for name in HEAVY_PENTAGON_PLOTS:
        detect = hp.DETECTIONS[name]
        series = detect(df, _FORCE_SHOW_PARAMS)
        out[name] = bool(series.iloc[-1])
    for name, fn in detectors_simple.SIMPLE_DETECTORS.items():
        out[name] = bool(fn(df))
    return out
