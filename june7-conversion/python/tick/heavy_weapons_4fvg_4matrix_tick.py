"""Python is a Python tick
heavy_weapons_4fvg_4matrix_tick — detection fire matrix on home-grown N-tick bars.

Source (read from disk, quoted exactly):
  "/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT transformed
   yet/June 7/Tick Friendly conversion/heavy_weapons_4fvg_4matrix_tickfriendly.pine"
  Pine v5, "Heavy Weapons NRA + GZI/FVG + Matrix Combos 2 bodies not 1 NRAFR".

Runtime grain: N-tick OHLCV bars (build_n_tick_bars). The detection core
(_heavy_weapons_4fvg_4matrix_core.compute / fire_matrix) is runtime-grain agnostic;
this wrapper only binds raw trades -> N-tick bars and calls the shared core. Tick
and time share ONE core (CODON: batch == streaming == fresh-rerun).

relativeVolume is DAILY-anchored off wall-clock day (the Pine reg_anchorSafe -> "D"
RE10023 fix) — NEVER the tick grain, because tick bars do not align to clock times.
tf_seconds uses the Pine TICK_FALLBACK_SEC guard so the per-TF threshold tables
don't silently die on a tick chart.

Emits per-bar 0/1 fire + numeric level for every detection plot (see core.PLOT_IDS),
plus the offset-applied coordinate events (FVG combos paint offset=-1).

CLI:  python3 heavy_weapons_4fvg_4matrix_tick.py [n_bars] [n_ticks]
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))  # Python conversion/ (shared core + harness)
from _nine_nines_common import build_n_tick_bars  # noqa: E402
import _heavy_weapons_4fvg_4matrix_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS
STUB_IDS = core.STUB_IDS


def run_on_trades(trades, n_ticks: int, *, params: Params | None = None):
    """trades: oldest-first list of (ts_ms, price, size). Returns the fire matrix.

    Aggregates trades into N-tick OHLCV bars (drops the still-forming partial),
    then runs the shared detection core at the tick-fallback timeframe row.
    """
    P = params or Params()
    bars = build_n_tick_bars(trades, n_ticks)
    return core.fire_matrix(bars, P, tf_seconds=P.tick_fallback_sec)


def run_on_bars(bars, *, params: Params | None = None):
    """Already-built N-tick Bar list (oldest-first). RVOL stays daily-anchored."""
    P = params or Params()
    return core.fire_matrix(bars, P, tf_seconds=P.tick_fallback_sec)


def run_tick(bars, *, tick_fallback_sec: int | None = None, params: Params | None = None):
    """Compatibility entry: detect on a tick-bar series, returning the raw
    {'fires','events'} matrix at the given tick-fallback timeframe row."""
    P = params or Params()
    tfs = tick_fallback_sec if tick_fallback_sec is not None else P.tick_fallback_sec
    return core.fire_matrix(bars, P, tf_seconds=tfs)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 800
    n_ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 25

    # deterministic synthetic trades (self-contained LCG; no external deps)
    _state = [20260608]

    def rnd():
        _state[0] = (1103515245 * _state[0] + 12345) & 0x7FFFFFFF
        return _state[0] / 0x7FFFFFFF

    trades = []
    t = 1_700_000_000_000
    px = 100.0
    day = 0
    bar_in_day = 0
    bars_per_day = 18
    for _ in range(n * n_ticks):
        # roll to a new calendar day every bars_per_day*n_ticks trades so RVOL has
        # many prior sessions to average over.
        shock = rnd() > 0.90
        drift = (1.0 if rnd() > 0.5 else -1.0) * (3.0 + rnd() * 5.0) if shock else (rnd() - 0.5) * 0.4
        px = max(0.5, px + drift / n_ticks)
        size = (40.0 + rnd() * 60.0) if rnd() > 0.985 else (1 + rnd() * 49)
        trades.append((t + day * 86_400_000 + bar_in_day * 3000, px, size))
        if len(trades) % n_ticks == 0:
            bar_in_day += 1
            if bar_in_day >= bars_per_day:
                bar_in_day = 0
                day += 1

    out = run_on_trades(trades, n_ticks)
    counts = {pid: sum(out["fire_" + pid]) for pid in PLOT_IDS}
    total = sum(counts.values())
    print("Python is a Python tick — heavy_weapons_4fvg_4matrix")
    print(f"bars={len(out['ts'])}  n_ticks={n_ticks}  total_fires={total}  events={len(out['events'])}")
    for pid, ct in counts.items():
        if ct:
            print(f"  {pid:12s} {ct}")
