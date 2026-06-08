# Python is a Python tick
# =============================================================================
# ULTRA COMBO v57 — Pine v5 -> Python (TICK grain). FULL port.
# -----------------------------------------------------------------------------
# Source (read from disk, path has spaces):
#   ".../June 7/Tick Friendly conversion/ultra_57_tickfriendly.pine"
#   (Pine v5, import TradingView/ta/7; original was //@version=6, made v5 +
#    tick-safe). EVERY one of the 35 detection plotshapes is produced from OHLCV
#    by the shared core (_ultra_57_core) — NO stub layer (COMPOSITE_PARTIAL=[]).
#
# Runtime GRAIN: N-tick bars. relativeVolume anchor = "D" (the wall-clock
#   calendar day of each bar's timestamp) on tick charts — the Pine RE10023 fix
#   forces "D" on tick (tick bars never align to clock times). The per-TF RVOL
#   threshold key tfSec uses the Pine TICK_FALLBACK_SEC=10s fallback because
#   timeframe.in_seconds() is na on tick.
#
# The tick module and the time module (../time/ultra_57_time.py) share ONE core
#   (_ultra_57_core.compute); only the bar grain fed in and tfSec/anchor differ.
# =============================================================================
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # June 7/Python conversion (shared root)
sys.path.insert(0, _HERE)
from _nine_nines_common import build_n_tick_bars   # noqa: E402
import _ultra_57_core as core                       # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS
PLOT_SPEC = core.PLOT_SPEC

GRAIN = "tick"
RVOL_ANCHOR = "D"            # wall-clock DAY anchor even on tick bars (RE10023 fix)
TICK_FALLBACK_SEC = 10       # Pine TICK_FALLBACK_SEC (timeframe.in_seconds() na on tick)

# COMPOSITE_PARTIAL: none — FULL port. Retained (empty) so the honesty gate that
# inspects it sees zero stubbed detection plots held at 0.
COMPOSITE_PARTIAL: list[str] = list(core.COMPOSITE_PARTIAL)


def run_on_trades(trades, n_ticks: int, *, params: Params | None = None):
    """trades: (ts_ms, price, size) oldest-first -> N-tick bars -> fire matrix."""
    bars = build_n_tick_bars(trades, n_ticks)
    return run_on_bars(bars, params=params)


def run_on_bars(bars, *, params: Params | None = None, tf_seconds: int = TICK_FALLBACK_SEC,
                in_session=None):
    if params is None:
        sec = tf_seconds if (tf_seconds and tf_seconds > 0) else TICK_FALLBACK_SEC
        params = Params(tfSec=sec, nn_tick_assumed_sec=TICK_FALLBACK_SEC)
    return core.compute(bars, params=params, rv_anchor=RVOL_ANCHOR, in_session=in_session)


def compute(bars, params=None, *, tf_seconds: int = TICK_FALLBACK_SEC, in_session=None):
    """Dict-params convenience entrypoint (mirrors the older wrapper signature)."""
    if isinstance(params, Params) or params is None:
        return run_on_bars(bars, params=params, tf_seconds=tf_seconds, in_session=in_session)
    sec = tf_seconds if (tf_seconds and tf_seconds > 0) else TICK_FALLBACK_SEC
    return core.compute(bars, params=Params(tfSec=sec, nn_tick_assumed_sec=TICK_FALLBACK_SEC, **params),
                        rv_anchor=RVOL_ANCHOR, in_session=in_session)


if __name__ == "__main__":
    import _nn_harness as H  # noqa: E402

    bars = H.load_bars(grain=GRAIN, n=900)
    out = run_on_bars(bars)
    fire_keys = [k for k in out if k.startswith("fire_")]
    lvl_keys = [k for k in out if k.startswith("lvl_")]
    fires = sum(sum(out[k]) for k in fire_keys)
    print("Python is a Python tick — Ultra Combo v57 (FULL port, 35 plots)")
    print(f"bars={len(out['ts'])}  detection-plots={len(fire_keys)}  levels={len(lvl_keys)}  total fires={fires}")
    nz_plots = sorted(k for k in fire_keys if sum(out[k]) > 0)
    print(f"  plots that fired ({len(nz_plots)}): {[k[5:] for k in nz_plots]}")
    print(f"  COMPOSITE_PARTIAL (stubs held at 0): {COMPOSITE_PARTIAL}")
