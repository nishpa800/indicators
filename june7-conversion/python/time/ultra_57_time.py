# Python is a Python time-based
# =============================================================================
# ULTRA COMBO v57 — Pine v5 -> Python (TIME grain). FULL port.
# -----------------------------------------------------------------------------
# Source (read from disk, path has spaces):
#   ".../June 7/Tick Friendly conversion/ultra_57_tickfriendly.pine"
#   (Pine v5, import TradingView/ta/7). EVERY one of the 35 detection plotshapes
#   is produced from OHLCV by the shared core (_ultra_57_core) — NO stub layer.
#
# Runtime GRAIN: wall-clock time bars. relativeVolume anchor = "D" (Pine "D"
#   session day). The time module and the tick module (../tick/ultra_57_tick.py)
#   share ONE core; only the bar grain fed in and tfSec (the real bar duration)
#   differ. Identical detection logic — one code path, grain-bound.
# =============================================================================
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # June 7/Python conversion (shared root)
sys.path.insert(0, _HERE)
import _ultra_57_core as core   # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS
PLOT_SPEC = core.PLOT_SPEC

GRAIN = "time"
RVOL_ANCHOR = "D"
COMPOSITE_PARTIAL: list[str] = list(core.COMPOSITE_PARTIAL)   # FULL port — zero stubs


def run_on_bars(bars, *, params: Params | None = None, tf_seconds: int = 60,
                in_session=None):
    if params is None:
        params = Params(tfSec=tf_seconds)
    return core.compute(bars, params=params, rv_anchor=RVOL_ANCHOR, in_session=in_session)


def compute(bars, params=None, *, tf_seconds: int = 60, in_session=None):
    """Dict-params convenience entrypoint (mirrors the older wrapper signature)."""
    if isinstance(params, Params):
        return core.compute(bars, params=params, rv_anchor=RVOL_ANCHOR, in_session=in_session)
    if params is None:
        return core.compute(bars, params=Params(tfSec=tf_seconds), rv_anchor=RVOL_ANCHOR, in_session=in_session)
    return core.compute(bars, params=Params(tfSec=tf_seconds, **params),
                        rv_anchor=RVOL_ANCHOR, in_session=in_session)


if __name__ == "__main__":
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    out = run_on_bars(bars, tf_seconds=3600)
    fire_keys = [k for k in out if k.startswith("fire_")]
    lvl_keys = [k for k in out if k.startswith("lvl_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python time-based — Ultra Combo v57 (FULL port, 35 plots)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  levels={len(lvl_keys)}  total fires={fires}")
    nz_plots = sorted(k for k in fire_keys if sum(out[k]) > 0)
    print(f"  plots that fired ({len(nz_plots)}): {[k[5:] for k in nz_plots]}")
    print(f"  COMPOSITE_PARTIAL (stubs held at 0): {COMPOSITE_PARTIAL}")
