# Python is a Python tick
# =============================================================================
# Jumbo CIA * 1st PUP FAUNA  ->  Python (TICK grain)  [base = 1st_pup_fauna]
# Source (tick-friendly Pine v5):
#   ".../June 7/Tick Friendly conversion/1st pup fauna_tickfriendly.pine"
#
# This is a THIN grain-binder. ALL detection logic lives in the ONE shared core
# (_first_pup_fauna_core) which both this tick port and the time port import.
# The ONLY tick-specific things here:
#   * GRAIN = "tick"             (bars are N-tick OHLCV bars)
#   * RVOL anchor "D"            (tick bars anchor RVOL to the calendar day,
#                                 never the tick index -- RE10023 fix mirror)
#   * tf_seconds tick fallback   (per-TF threshold tables can't read a tick TF)
#
# Output: per-bar 0/1 fire + numeric level for EVERY one of the 34 detection
# plots. No plot is stubbed (FULL faithful port).
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

GRAIN = "tick"
RVOL_ANCHOR = "D"
TICK_FALLBACK_SEC = _CORE.TICK_FALLBACK_SEC
DEFAULTS = dict(_CORE.DEFAULTS)
PLOT_IDS = list(_CORE.PLOT_IDS)
STUB_PARTIAL = list(_CORE.STUB_PARTIAL)


def compute(bars, params=None, *, tf_seconds=TICK_FALLBACK_SEC):
    """Run the shared detection core on N-tick bars.

    Returns dict: {fires, levels, plot_ids, n, stub_partial}.
    fires[plot_id] = list[int] (0/1 per bar); levels[plot_id] = list[float|None].
    """
    if tf_seconds is None or tf_seconds <= 0:
        tf_seconds = TICK_FALLBACK_SEC
    return _CORE.compute(bars, params=params, tf_seconds=tf_seconds)


def compute_fires_bool(bars, params=None, *, tf_seconds=TICK_FALLBACK_SEC):
    return _CORE.compute_fires_bool(bars, params=params, tf_seconds=tf_seconds)


if __name__ == "__main__":
    bars = H.load_bars(grain=GRAIN, n=900)
    res = compute(bars, params={"reg_length": 30})
    fired = sum(1 for k in res["plot_ids"] if sum(res["fires"][k]) > 0)
    print(f"1st PUP FAUNA TICK -- {res['n']} bars, {len(res['plot_ids'])} detection plots, "
          f"{fired} plots fired, {len(res['stub_partial'])} stubbed")
    for k in res["plot_ids"]:
        c = sum(res["fires"][k])
        if c:
            print(f"  {k:22s} fired {c}")
