"""Python is a Python time-based
heavy_weapons_4fvg_4matrix_time — detection fire matrix on time-based candles.

Source (read from disk, quoted exactly):
  "/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT transformed
   yet/June 7/Tick Friendly conversion/heavy_weapons_4fvg_4matrix_tickfriendly.pine"
  Pine v5, "Heavy Weapons NRA + GZI/FVG + Matrix Combos 2 bodies not 1 NRAFR".

Runtime grain: time candles at an EXPLICIT timeframe (pass tf_seconds, e.g. 60 for
1m, 300 for 5m). The per-TF threshold tables are keyed off this tf_seconds. The
detection core is the SAME single code path the tick wrapper uses (CODON: batch ==
streaming == fresh-rerun); only the bar grain differs. relativeVolume is daily-
anchored off wall-clock day (the Pine reg_anchorSafe -> "D").

Emits per-bar 0/1 fire + numeric level for every detection plot (see core.PLOT_IDS),
plus the offset-applied coordinate events (FVG combos paint offset=-1).

CLI:  python3 heavy_weapons_4fvg_4matrix_time.py [n_bars] [tf_seconds]
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))  # Python conversion/ (shared core + harness)
from _nine_nines_common import passthrough_time_bars  # noqa: E402
import _heavy_weapons_4fvg_4matrix_core as core  # noqa: E402

Params = core.Params
PLOT_IDS = core.PLOT_IDS
STUB_IDS = core.STUB_IDS


def run_on_rows(rows, *, tf_seconds: int, params: Params | None = None):
    """rows: oldest-first list of (ts_ms, o, h, l, c, v). Returns the fire matrix."""
    if tf_seconds <= 0:
        raise ValueError("tf_seconds must be a positive, explicit timeframe")
    P = params or Params()
    bars = passthrough_time_bars(rows)
    return core.fire_matrix(bars, P, tf_seconds=tf_seconds)


def run_on_bars(bars, *, tf_seconds: int, params: Params | None = None):
    """Already-built time Bar list (oldest-first) at an explicit timeframe."""
    if tf_seconds <= 0:
        raise ValueError("tf_seconds must be a positive, explicit timeframe")
    P = params or Params()
    return core.fire_matrix(bars, P, tf_seconds=tf_seconds)


def run_time(bars, *, tf_seconds: int, params: Params | None = None):
    """Compatibility entry: detect on a time-candle series at an explicit timeframe."""
    if tf_seconds <= 0:
        raise ValueError("tf_seconds must be a positive, explicit timeframe")
    P = params or Params()
    return core.fire_matrix(bars, P, tf_seconds=tf_seconds)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 800
    tf = int(sys.argv[2]) if len(sys.argv) > 2 else 60

    # deterministic synthetic time candles (self-contained LCG; many sessions)
    import math
    _state = [20260608]

    def rnd():
        _state[0] = (1103515245 * _state[0] + 12345) & 0x7FFFFFFF
        return _state[0] / 0x7FFFFFFF

    rows = []
    t0 = 1_700_000_000_000
    px = 100.0
    bars_per_day = 20
    for i in range(n):
        day = i // bars_per_day
        k = i % bars_per_day
        ts = t0 + day * 86_400_000 + k * tf * 1000
        shock = rnd() > 0.90
        mega = rnd() > 0.985
        drift = (1.0 if rnd() > 0.5 else -1.0) * (3.0 + rnd() * 5.0) if shock else (rnd() - 0.5) * 0.6
        o = px
        c = max(0.5, o + drift)
        b = abs(c - o)
        hi = max(o, c) + (b * (0.05 + rnd() * 0.15) if shock else rnd() * 0.4)
        loo = min(o, c) - (b * (0.05 + rnd() * 0.15) if shock else rnd() * 0.4)
        smile = 1.0 + 1.8 * math.cos((k / bars_per_day) * math.pi) ** 2
        spike = (40.0 + rnd() * 60.0) if mega else ((8.0 + rnd() * 8.0) if shock else 1.0)
        vol = round((400 + rnd() * 600) * smile * spike, 2)
        rows.append((ts, round(o, 4), round(hi, 4), round(loo, 4), round(c, 4), vol))
        px = c

    out = run_on_rows(rows, tf_seconds=tf)
    counts = {pid: sum(out["fire_" + pid]) for pid in PLOT_IDS}
    total = sum(counts.values())
    print(f"Python is a Python time-based — heavy_weapons_4fvg_4matrix (tf={tf}s)")
    print(f"bars={len(out['ts'])}  total_fires={total}  events={len(out['events'])}")
    for pid, ct in counts.items():
        if ct:
            print(f"  {pid:12s} {ct}")
