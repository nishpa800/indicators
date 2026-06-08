"""Python is a Python tick
hub_2011_tick — Signal Hub FULL detection fire-matrix on home-grown N-tick bars.

Pine source: "hub 2011.txt" (//@version=5, "HUB_1020_1153am"). FULL port — every
one of the 27 detection plots is genuinely computed (no stub, nothing deferred).
This file is tick-safe natively (no tv_ta.relativeVolume / no time(period,...) /
no timeframe.in_seconds -> no RE10023). hub's RVOL is a LOCAL body-spike
normalization, preserved exactly as in Pine; it does NOT route through the
session-anchored shim (that would change the indicator's meaning).

The tick & time wrappers share ONE core (hub_2011_engine.detect) — only the bar
grain differs. Emits per-bar 0/1 `fires[id]` + numeric `levels[id]`.

CLI: python3 hub_2011_tick.py [n_bars]
"""
from __future__ import annotations
import sys

from nine_codon_core import synth_bars
from hub_2011_engine import Params, detect


def run_tick(bars, *, params: Params = Params()):
    # tf_seconds is informational for hub (its RVOL is local, not the shim).
    return detect(bars, params, tf_seconds=10)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    bars = synth_bars(n, tf_seconds=5)
    res = run_tick(bars)
    counts = {k: sum(a) for k, a in res["fires"].items()}
    print("Python is a Python tick — hub_2011 (FULL: 27 detection plots)")
    print(f"bars={n}  total_fires={sum(counts.values())}  events={len(res['events'])}")
    for k in res["fires"]:
        print(f"  {k:18s} {counts[k]}")
    print(f"  DEFERRED: {len(res['deferred'])}  (FULL port — none)")
