# Python is a Python time-based
# =============================================================================
# Jumbo CIA * 1st PUP FAUNA  ->  Python (TIME grain)  [base = 1st_pup_fauna]
# Source (tick-friendly Pine v5):
#   ".../June 7/Tick Friendly conversion/1st pup fauna_tickfriendly.pine"
#
# This is a THIN grain-binder. ALL detection logic lives in the ONE shared core
# (_first_pup_fauna_core) which both this time port and the tick port import.
# The ONLY time-specific things here:
#   * GRAIN = "time"            (bars are wall-clock OHLCV bars)
#   * RVOL anchor "D"           (Pine "D" keys off the wall-clock day)
#   * tf_seconds = the actual bar timeframe in seconds (drives threshold tables)
#
# Output: per-bar 0/1 fire + numeric level for EVERY one of the 34 detection
# plots. No plot is stubbed (FULL faithful port). Tick and time share ONE core,
# so on identical bars the fire matrix is byte-identical (proven in parity).
# =============================================================================
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_CORE_DIR = HERE.parent           # "Python conversion/" holds the shared core
sys.path.insert(0, str(HERE))      # local _nn_harness
sys.path.insert(0, str(_CORE_DIR))

import _nn_harness as H            # noqa: E402
import _first_pup_fauna_core as _CORE  # noqa: E402

GRAIN = "time"
RVOL_ANCHOR = "D"
DEFAULTS = dict(_CORE.DEFAULTS)
PLOT_IDS = list(_CORE.PLOT_IDS)
STUB_PARTIAL = list(_CORE.STUB_PARTIAL)


def compute(bars, params=None, *, tf_seconds=60):
    """Run the shared detection core on wall-clock time bars.

    Returns dict: {fires, levels, plot_ids, n, stub_partial}.
    """
    return _CORE.compute(bars, params=params, tf_seconds=tf_seconds)


def compute_fires_bool(bars, params=None, *, tf_seconds=60):
    return _CORE.compute_fires_bool(bars, params=params, tf_seconds=tf_seconds)


if __name__ == "__main__":
    bars = H.load_bars(grain=GRAIN, n=900)
    res = compute(bars, params={"reg_length": 30}, tf_seconds=3600)
    fired = sum(1 for k in res["plot_ids"] if sum(res["fires"][k]) > 0)
    print(f"1st PUP FAUNA TIME -- {res['n']} bars, {len(res['plot_ids'])} detection plots, "
          f"{fired} plots fired, {len(res['stub_partial'])} stubbed")
    for k in res["plot_ids"]:
        c = sum(res["fires"][k])
        if c:
            print(f"  {k:22s} fired {c}")
