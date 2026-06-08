"""Python is a Python time-based
hub_2011_time — Signal Hub FULL detection fire-matrix on time-based candles.

Pine source: "hub 2011.txt" (//@version=5, "HUB_1020_1153am"). FULL port — every
one of the 27 detection plots is genuinely computed (no stub, nothing deferred).
Explicit timeframe via tf_seconds. SAME single core code path as the tick wrapper
(hub_2011_engine.detect); only the bar grain differs.

CLI: python3 hub_2011_time.py [n_bars] [tf_seconds]
"""
from __future__ import annotations
import sys

from nine_codon_core import synth_bars
from hub_2011_engine import Params, detect


def run_time(bars, *, tf_seconds: int, params: Params = Params()):
    if tf_seconds <= 0:
        raise ValueError("tf_seconds must be an explicit positive timeframe")
    return detect(bars, params, tf_seconds=tf_seconds)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    tf = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    bars = synth_bars(n, tf_seconds=tf)
    res = run_time(bars, tf_seconds=tf)
    counts = {k: sum(a) for k, a in res["fires"].items()}
    print(f"Python is a Python time-based — hub_2011 (FULL: 27 plots; tf={tf}s)")
    print(f"bars={n}  total_fires={sum(counts.values())}  events={len(res['events'])}")
    for k in res["fires"]:
        print(f"  {k:18s} {counts[k]}")
    print(f"  DEFERRED: {len(res['deferred'])}  (FULL port — none)")
