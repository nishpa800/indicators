# =============================================================================
# Python parity harness -- 1st PUP FAUNA  [base = 1st_pup_fauna]
# -----------------------------------------------------------------------------
# HONEST offline parity (NINE NINES Stage-4 Gate-B). This proves the Python port
# is internally consistent and faithful to the Pine LOGIC on deterministic
# synthetic bars. It does NOT claim bar-for-bar parity vs the live TradingView
# chart (Gate-A, TV bridge, is a separate SOW and is NOT run here).
#
# Gates (each is a real pass/fail, printed with REAL counts):
#   1  time_port_runs            -- time module returns a fire matrix
#   2  tick_port_runs            -- tick module returns a fire matrix
#   3  plot_count_vs_source      -- ported plot count == Pine plotshape() count
#   4  every_plot_present        -- all 34 expected plot ids emitted
#   5  fires_are_binary          -- every fire value is exactly 0 or 1
#   6  levels_aligned            -- every plot has a level series of length n
#   7  tick_eq_time_same_bars    -- IDENTICAL fire matrix on identical bars
#                                   (one shared core, grain-bound)
#   8  determinism               -- same input -> byte-identical output
#   9  matrix_exercised          -- >= 1 plot actually fires (non-trivial)
#  10  stub_is_zero_honesty      -- declared stubs are []; if any existed they'd
#                                   be forced all-zero. Vacuously true here.
#  11  negative_control          -- a flat, no-volume tape fires nothing
#  12  warmup_clean              -- no fire before its minimum lookback warms up
#
# Re-runnable by a stranger: `python3 1st_pup_fauna_parity.py`.
# =============================================================================
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))             # local _nn_harness
sys.path.insert(0, str(ROOT))             # shared core
sys.path.insert(0, str(ROOT / "tick"))
sys.path.insert(0, str(ROOT / "time"))

import _nn_harness as H                    # noqa: E402

# import the two grain ports by file path (filenames start with a digit)
import importlib.util


def _load(mod_name, path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


MT = _load("first_pup_fauna_time_x", ROOT / "time" / "1st_pup_fauna_time.py")
MK = _load("first_pup_fauna_tick_x", ROOT / "tick" / "1st_pup_fauna_tick.py")

SOURCE = Path("/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT transformed yet/"
              "June 7/Tick Friendly conversion/1st pup fauna_tickfriendly.pine")
PARAMS = {"reg_length": 30}
N = 900
EXPECTED_PLOTS = 33   # exact count of plotshape() detection plots in the Pine source


def _flat_bars(n=300):
    """Negative control: a dead-flat tape, constant price, near-zero volume.
    Nothing should fire."""
    import datetime as _dt
    base = _dt.datetime(2026, 5, 1, 8, 30, 0)
    out = []
    for i in range(n):
        ts = int((base + _dt.timedelta(minutes=i)).timestamp() * 1000)
        out.append(H.Bar(ts, 100.0, 100.0, 100.0, 100.0, 1.0))
    return out


def run():
    results = []

    # 1 + 2: ports run
    try:
        bt = H.load_bars(grain="time", n=N)
        rt = MT.compute(bt, params=PARAMS, tf_seconds=3600)
        ft = rt["fires"]
        ok = isinstance(ft, dict) and len(ft) == EXPECTED_PLOTS
        results.append(("time_port_runs", ok, f"{len(ft)} plots"))
    except Exception as e:  # pragma: no cover
        results.append(("time_port_runs", False, f"EXC {e}")); rt = {"fires": {}, "levels": {}, "n": 0, "stub_partial": []}; ft = {}
    try:
        bk = H.load_bars(grain="tick", n=N)
        rk = MK.compute(bk, params=PARAMS)
        fk = rk["fires"]
        ok = isinstance(fk, dict) and len(fk) == EXPECTED_PLOTS
        results.append(("tick_port_runs", ok, f"{len(fk)} plots"))
    except Exception as e:  # pragma: no cover
        results.append(("tick_port_runs", False, f"EXC {e}")); rk = {"fires": {}}; fk = {}

    # 3: plot count == Pine plotshape() count
    src = None
    if SOURCE.exists():
        src = len(re.findall(r"plotshape\(", SOURCE.read_text(errors="ignore")))
    results.append(("plot_count_vs_source", (src == EXPECTED_PLOTS and len(ft) == EXPECTED_PLOTS),
                    f"source plotshape={src}, ported={len(ft)}"))

    # 4: every expected plot present
    missing = [pid for pid in MT.PLOT_IDS if pid not in ft]
    results.append(("every_plot_present", not missing and len(MT.PLOT_IDS) == EXPECTED_PLOTS,
                    f"{len(MT.PLOT_IDS)} ids, missing={missing[:4]}"))

    # 5: fires strictly binary
    bad = []
    for pid, arr in ft.items():
        for x in arr:
            if x not in (0, 1):
                bad.append((pid, x)); break
    results.append(("fires_are_binary", not bad, "all 0/1" if not bad else f"bad {bad[:3]}"))

    # 6: levels aligned (one series per plot, length n)
    lev = rt.get("levels", {})
    n = rt.get("n", 0)
    lev_ok = (set(lev.keys()) == set(ft.keys())) and all(len(v) == n for v in lev.values())
    results.append(("levels_aligned", lev_ok, f"{len(lev)} level series len {n}"))

    # 7: tick == time on IDENTICAL bars (one shared core)
    try:
        fts = MT.compute(bt, params=PARAMS, tf_seconds=3600)["fires"]
        fks = MK.compute(bt, params=PARAMS, tf_seconds=3600)["fires"]
        mism = [pid for pid in fts if fts[pid] != fks.get(pid)]
        results.append(("tick_eq_time_same_bars", not mism,
                        "identical" if not mism else f"mismatch {mism[:5]}"))
    except Exception as e:  # pragma: no cover
        results.append(("tick_eq_time_same_bars", False, f"EXC {e}"))

    # 8: determinism
    try:
        a = MT.compute(H.load_bars(grain="time", n=N), params=PARAMS, tf_seconds=3600)["fires"]
        b = MT.compute(H.load_bars(grain="time", n=N), params=PARAMS, tf_seconds=3600)["fires"]
        results.append(("determinism", a == b, "stable" if a == b else "non-deterministic"))
    except Exception as e:  # pragma: no cover
        results.append(("determinism", False, f"EXC {e}"))

    # 9: matrix exercised
    fired = [pid for pid, arr in ft.items() if sum(arr) > 0]
    results.append(("matrix_exercised", len(fired) >= 1,
                    f"{len(fired)}/{len(ft)} plots fired: {fired[:8]}"))

    # 10: stub-is-zero honesty (no plot is stubbed in this port)
    stubs = rt.get("stub_partial", [])
    stub_zero_ok = (len(stubs) == 0) or all(sum(ft.get(s, [])) == 0 for s in stubs)
    results.append(("stub_is_zero_honesty", stub_zero_ok,
                    f"declared stubs={stubs} (all forced 0)" if stubs else "no stubs (full port)"))

    # 11: negative control -> nothing fires on a flat tape
    try:
        flat = _flat_bars(300)
        rf = MT.compute(flat, params=PARAMS, tf_seconds=3600)["fires"]
        total = sum(sum(arr) for arr in rf.values())
        results.append(("negative_control", total == 0, f"{total} fires on flat tape"))
    except Exception as e:  # pragma: no cover
        results.append(("negative_control", False, f"EXC {e}"))

    # 12: warmup clean -- FAUNA+ Bull needs >=100-bar stdev; no fire before bar 100
    try:
        warm_ok = True
        detail = "ok"
        for pid in ("FAUNA+ Bull", "FAUNA+ Bear", "Golf Bull", "Opening Drive Bull"):
            arr = ft.get(pid, [])
            early = [i for i in range(min(len(arr), 100)) if arr[i]]
            if early:
                warm_ok = False
                detail = f"{pid} fired early at {early[:3]}"
                break
        results.append(("warmup_clean", warm_ok, detail))
    except Exception as e:  # pragma: no cover
        results.append(("warmup_clean", False, f"EXC {e}"))

    return results


if __name__ == "__main__":
    res = run()
    passed = sum(1 for _, ok, _ in res if ok)
    print(f"=== 1st PUP FAUNA PARITY: {passed}/{len(res)} ===")
    for name, ok, detail in res:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:24s} {detail}")
    sys.exit(0 if passed == len(res) else 1)
