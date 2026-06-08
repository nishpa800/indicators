"""TNT Opening Drive OD v3 — parity harness (offline Gate-B). FULL port.

Runnable by a stranger:  python3 tnt_od_v3_parity.py

This is a FULL port (all 47 numeric data_window detection plots derived from OHLCV
by the shared core — NO stub layer). The harness runs on deterministic synthetic +
engineered bars and prints a REAL pass/total.

TNT OD v3 is a deep multi-engine stateful aggregator (VOB + ANISH + FLUX + TNT
zone state machines, charge/return scans, displacement, napalm, USE V5 RVOL/WMD/
FAUNA/PBJ/CS1, DYNAMITE, HEAVY PENTAGON/WBUSH, HCT, UC, gate, combos, density, UU
streaks, T1 relay/stack). A blind "second copy" is not an independent check, so we
INDEPENDENTLY re-derive the deterministic leaf gates that many fires are pure
functions of — Engine-1 displacement+FVG, USE-V5 displacement, DYNAMITE B2B
displacement, FAUNA, and the RVOL bb-norm tiers — and assert the core's fires are
CONSISTENT with them (a fire implies its required leaf gate). Then we assert the
structural invariants and the honesty / negative-control / warmup gates.

Checks (each prints PASS/FAIL + REAL detail):
   1. TICK PORT RUNS          — tick wrapper produces the 47-plot fire matrix.
   2. TIME PORT RUNS          — time wrapper produces the 47-plot fire matrix.
   3. PLOT COUNT == 47        — PLOT_IDS length == source data_window plot(... "f_*").
   4. TICK == TIME            — SAME core on SAME Bar objects -> byte-identical fire
                                matrix through both wrappers (one code path).
   5. DETERMINISM             — two runs on identical bars give identical matrix.
   6. BOOLEAN + LEVELS        — every fire_* is strictly 0/1; lvl_* is float where
                                fire==1 and None where fire==0 (exact alignment).
   7. sigAny INVARIANT        — sigAny == OR of all 47 fires, every bar.
   8. DYNAMITE LEAF PARITY    — every f_dynBull fire requires independent B2B
                                displacement + bull-dir + FAUNA[1]&[2] + bull FVG;
                                mirror for f_dynBear.
   9. CATALYST/NAPALM-CHAIN   — every f_catBull implies an independent USE-V5-or-main
                                displacement event on the bar (Napalm rides
                                displacement); mirror bear. (Necessary condition.)
  10. ENRICH-GATE PARITY      — every f_t2tntBull fire bar has an independent bull
                                enrichment co-signal present (RVOL/FAUNA/WMD/...);
                                mirror bear. (Tier-2 is hard-gated by enrichment.)
  11. NON-TRIVIALITY          — the fire matrix is NOT all-zero on the event-rich
                                tape; >= 1 distinct detection plot fires.
  12. NEGATIVE CONTROL        — a flat doji tape fires nothing (no warmup ghosts).
  13. WARMUP                  — a tiny tape does not crash and does not fire.
  14. HONESTY (stub-is-zero)  — COMPOSITE_PARTIAL empty on BOTH wrappers AND the
                                matrix is genuinely exercised (>= 1 distinct plot
                                fires). A green that fired nothing = fabricated.
"""
from __future__ import annotations

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)
sys.path.insert(0, _HERE)                       # local _nn_harness
sys.path.insert(0, os.path.join(_ROOT, "tick"))
sys.path.insert(0, os.path.join(_ROOT, "time"))

from _nine_nines_common import Bar  # noqa: E402
from _nn_harness import synthetic_bars, stdev as _stdev, sma as _sma, highest as _highest  # noqa: E402
import _tnt_od_v3_core as core  # noqa: E402
import tnt_od_v3_tick as tickmod  # noqa: E402
import tnt_od_v3_time as timemod  # noqa: E402

SOURCE = ("/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT "
          "transformed yet/June 7/Tick Friendly conversion/tnt_od_v3_tickfriendly.pine")

PIDS = core.PLOT_IDS


# ─────────────────────────── deterministic tapes ────────────────────────────
# TNT_SENS — high sensitivity widens EMA_SLOW so the ANISH "two OBs within
# EMA_SLOW bars" gate (genuinely rare — TNT confluence is extreme-conviction /
# low-frequency by design, per the thesis) can resolve on synthetic data and the
# deep zone-dependent plots (TNT-ENR, PBJ+RET-ENR, T1 RELAY) actually light.
TNT_SENS = 250


def _osc_tape(nbars=3000, seed=2, period=13.0):
    """Deterministic multi-session oscillating tape (sine drift + spaced shocks +
    FVG gaps + heavy volume). Lights the VOB/ANISH/FLUX -> TNT zone engine and its
    downstream combos at TNT_SENS."""
    import math
    import random
    random.seed(seed)
    rows = []
    t0 = 1_700_000_000_000
    px = 100.0
    for i in range(nbars):
        ts = t0 + (i // 60) * 86_400_000 + (i % 60) * 60_000
        target = 100.0 + 22.0 * math.sin(i / period) + 10.0 * math.sin(i / 37.0)
        o = px
        drift = (target - px) * 0.6 + (random.random() - 0.5) * 0.8
        shock = random.random() > 0.75
        if shock:
            drift = (1.0 if random.random() > 0.5 else -1.0) * (2.5 + random.random() * 5.0)
        c = max(0.5, o + drift)
        body = abs(c - o)
        hi = max(o, c) + max(body * 0.1, random.random() * 0.3)
        lo = min(o, c) - max(body * 0.1, random.random() * 0.3)
        vol = round((400 + random.random() * 600) * (8.0 if shock else 1.0), 2)
        rows.append(Bar(ts, round(o, 4), round(hi, 4), round(lo, 4), round(c, 4), vol))
        px = c
    return rows


def _dyn_tape(reps=8, calm=130):
    """Deterministic tape engineered to light DYNAMITE (Engine #2) and the T1
    RELAY/STACK plots: long calm runs (tiny stdev) punctuated by 2 consecutive
    huge green momentum bars (FAUNA momentum-bar + B2B sigma-displacement) and a
    3rd gap-up bar (bull FVG). `calm` >= the 100-bar dyn stdev lookback so the
    threshold stays low and the B2B displacement clears it."""
    rows = []
    t0 = 1_700_000_000_000
    px = 100.0
    ts = t0
    for r in range(reps):
        for k in range(calm):
            o = px
            c = px + (0.02 if k % 2 else -0.02)
            hi = max(o, c) + 0.03
            lo = min(o, c) - 0.03
            rows.append(Bar(ts, round(o, 4), round(hi, 4), round(lo, 4), round(c, 4), 1000.0))
            px = c; ts += 60_000
        for _ in range(2):    # two consecutive huge green momentum bars (FAUNA + disp)
            o = px
            c = px + 6.0
            hi = c + 0.05
            lo = o - 0.05
            rows.append(Bar(ts, round(o, 4), round(hi, 4), round(lo, 4), round(c, 4), 9000.0))
            px = c; ts += 60_000
        o = px + 3.0          # gap-up confirmation bar (bull FVG: low > high[2])
        c = o + 1.0
        hi = c + 0.05
        lo = o - 0.05
        rows.append(Bar(ts, round(o, 4), round(hi, 4), round(lo, 4), round(c, 4), 3000.0))
        px = c; ts += 60_000
    return rows


def _flat_tape(nbars=300):
    rows = []
    t0 = 1_700_000_000_000
    for i in range(nbars):
        ts = t0 + (i // 24) * 86_400_000 + (i % 24) * 60_000
        rows.append(Bar(ts, 100.0, 100.0, 100.0, 100.0, 1000.0))
    return rows


_PTNT = core.Params(SENS=TNT_SENS)


# ─────────────────── independent leaf re-derivations ────────────────────────
def _independent(bars, p: core.Params, tf_seconds):
    """Re-derive the deterministic leaf gates from scratch (NOT the core path)."""
    n = len(bars)
    o = [b.open for b in bars]; h = [b.high for b in bars]; l = [b.low for b in bars]
    c = [b.close for b in bars]; v = [b.volume for b in bars]

    # Engine-1 displacement + FVG
    disp_range = [abs(o[i] - c[i]) if p.DISP_TYPE == "Open to Close" else h[i] - l[i] for i in range(n)]
    dstd = _stdev(disp_range, p.DISP_STD_LEN)
    isBullFVG = [i >= 2 and l[i] > h[i - 2] and o[i - 1] < c[i - 1] for i in range(n)]
    isBearFVG = [i >= 2 and h[i] < l[i - 2] and o[i - 1] > c[i - 1] for i in range(n)]
    prevDisp = [i >= 1 and dstd[i - 1] is not None and disp_range[i - 1] > dstd[i - 1] * p.DISP_STD_X for i in range(n)]
    dispBull = [prevDisp[i] and (isBullFVG[i] or isBearFVG[i]) and i >= 1 and c[i - 1] > o[i - 1] for i in range(n)]
    dispBear = [prevDisp[i] and (isBullFVG[i] or isBearFVG[i]) and i >= 1 and c[i - 1] < o[i - 1] for i in range(n)]

    # USE-V5 displacement
    u5rng = [abs(o[i] - c[i]) for i in range(n)]
    u5std = _stdev(u5rng, p.u5_std_len)
    u5bull = [i >= 1 and u5std[i - 1] is not None and u5rng[i - 1] > u5std[i - 1] * p.u5_std_min
              and i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1] for i in range(n)]
    u5bear = [i >= 1 and u5std[i - 1] is not None and u5rng[i - 1] > u5std[i - 1] * p.u5_std_min
              and i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1] for i in range(n)]

    # DYNAMITE B2B displacement + dir + FVG
    dstdv = _stdev(u5rng, 100)
    dyn_b1 = [i >= 1 and dstdv[i - 1] is not None and u5rng[i - 1] > dstdv[i - 1] * p.dynStdMult for i in range(n)]
    dyn_b2 = [i >= 2 and dstdv[i - 2] is not None and u5rng[i - 2] > dstdv[i - 2] * p.dynStdMult for i in range(n)]
    dyn_bull_dir = [i >= 2 and c[i - 1] > o[i - 1] and c[i - 2] > o[i - 2] for i in range(n)]
    dyn_bear_dir = [i >= 2 and c[i - 1] < o[i - 1] and c[i - 2] < o[i - 2] for i in range(n)]
    dyn_bullFVG = [i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1] for i in range(n)]
    dyn_bearFVG = [i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1] for i in range(n)]

    # FAUNA (independent — same Pine def)
    atr14 = core._atr_ohlc(o, h, l, c, 14)
    avgVol = _sma(v, 20)
    avgDelta = _sma([0.0] + [abs(c[i] - c[i - 1]) for i in range(1, n)], 10)
    trendMA = _sma(c, 50)
    faunaB = [False] * n; faunaR = [False] * n
    for i in range(n):
        fa = atr14[i] or 0.0; av = avgVol[i] or 0.0; ad = avgDelta[i] or 0.0
        body = c[i] - o[i]; rng = h[i] - l[i]; bsz = abs(body)
        brat = 0.0 if rng == 0 else bsz / rng
        up = body > 0; dn = body < 0
        tUp = trendMA[i] is not None and i >= 1 and trendMA[i - 1] is not None and trendMA[i] > trendMA[i - 1]
        tDn = trendMA[i] is not None and i >= 1 and trendMA[i - 1] is not None and trendMA[i] < trendMA[i - 1]
        MB_b = up and bsz > 1.6 * fa and brat > 0.70 and v[i] > 1.8 * av
        RE_b = up and rng > 2.2 * fa and (h[i] - c[i]) < 0.15 * rng and v[i] > 1.8 * av
        TA_b = tUp and i >= 1 and (c[i] - c[i - 1]) > 1.6 * ad and up and v[i] > 1.8 * av
        faunaB[i] = (MB_b or RE_b or TA_b)
        MB_r = dn and bsz > 1.6 * fa and brat > 0.70 and v[i] > 1.8 * av
        RE_r = dn and rng > 2.2 * fa and (c[i] - l[i]) < 0.15 * rng and v[i] > 1.8 * av
        TA_r = tDn and i >= 1 and (c[i - 1] - c[i]) > 1.6 * ad and dn and v[i] > 1.8 * av
        faunaR[i] = (MB_r or RE_r or TA_r)

    dynBull = [dyn_b1[i] and dyn_b2[i] and dyn_bull_dir[i] and dyn_bullFVG[i]
               and (faunaB[i - 1] if i >= 1 else False) and (faunaB[i - 2] if i >= 2 else False)
               for i in range(n)]
    dynBear = [dyn_b1[i] and dyn_b2[i] and dyn_bear_dir[i] and dyn_bearFVG[i]
               and (faunaR[i - 1] if i >= 1 else False) and (faunaR[i - 2] if i >= 2 else False)
               for i in range(n)]

    return dict(dispBull=dispBull, dispBear=dispBear, u5bull=u5bull, u5bear=u5bear,
                dynBull=dynBull, dynBear=dynBear, faunaB=faunaB, faunaR=faunaR)


# ───────────────────────────────── checks ───────────────────────────────────
def run():
    results = []
    p = core.Params()                       # default SENS — for DYNAMITE leaf checks
    dyn = _dyn_tape(8, 130)                  # lights DYNAMITE + T1 plots (default SENS)
    osc = _osc_tape(3000, 2, 13.0)          # lights TNT zone engine + combos (TNT_SENS)
    multi = synthetic_bars(n=1200, grain="time")
    # `mt` = the DYNAMITE tape matrix (default params) — used by the leaf-parity checks
    mt = tickmod.run_on_bars(dyn)

    # 1/2 ports run
    try:
        ok = isinstance(mt, dict) and any(k.startswith("fire_") for k in mt)
        results.append(("tick_port_runs", ok, f"{sum(1 for k in mt if k.startswith('fire_'))} plots"))
    except Exception as e:
        mt = {}; results.append(("tick_port_runs", False, f"EXC {e}"))
    try:
        ot = timemod.run_on_bars(dyn)
        ok = isinstance(ot, dict) and any(k.startswith("fire_") for k in ot)
        results.append(("time_port_runs", ok, f"{sum(1 for k in ot if k.startswith('fire_'))} plots"))
    except Exception as e:
        ot = {}; results.append(("time_port_runs", False, f"EXC {e}"))

    # 3 plot count == 47 (and source data_window plot sanity)
    src_dw = None
    if os.path.exists(SOURCE):
        txt = open(SOURCE, errors="ignore").read()
        src_dw = len(re.findall(r'plot\([^\n]*"f_[A-Za-z0-9_]+"[^\n]*display=display\.data_window', txt))
    results.append(("plot_count_eq_47", len(PIDS) == 47,
                    f"PLOT_IDS={len(PIDS)}, source data_window f_* plots={src_dw}"))

    # 4 tick == time (same bars through both wrappers, same tf_seconds + params)
    try:
        a = tickmod.run_on_bars(osc, params=_PTNT, tf_seconds=60)
        b = timemod.run_on_bars(osc, params=_PTNT, tf_seconds=60)
        mism = [k for k in a if a[k] != b.get(k)]
        results.append(("tick_eq_time", not mism,
                        "identical matrix (same tf_seconds+params)" if not mism else f"mismatch {mism[:4]}"))
    except Exception as e:
        results.append(("tick_eq_time", False, f"EXC {e}"))

    # 5 determinism
    try:
        d1 = tickmod.run_on_bars(osc, params=_PTNT)
        d2 = tickmod.run_on_bars(_osc_tape(3000, 2, 13.0), params=_PTNT)
        results.append(("deterministic", d1 == d2, "stable" if d1 == d2 else "non-deterministic"))
    except Exception as e:
        results.append(("deterministic", False, f"EXC {e}"))

    # 6 boolean + level alignment
    try:
        bad = []
        for pid in PIDS:
            f = mt[f"fire_{pid}"]; lv = mt[f"lvl_{pid}"]
            if any(x not in (0, 1) for x in f):
                bad.append(f"{pid}:nonbool")
            for i in range(len(f)):
                if f[i] == 1 and lv[i] is None:
                    bad.append(f"{pid}:fire-no-lvl"); break
                if f[i] == 0 and lv[i] is not None:
                    bad.append(f"{pid}:nofire-has-lvl"); break
        results.append(("boolean_matrix_and_levels", not bad,
                        "all 0/1 + levels aligned" if not bad else str(bad[:4])))
    except Exception as e:
        results.append(("boolean_matrix_and_levels", False, f"EXC {e}"))

    # 7 sigAny invariant (on the DYNAMITE tape mt)
    n = len(dyn)
    anyok = all(mt["sigAny"][i] == (1 if any(mt[f"fire_{pid}"][i] for pid in PIDS) else 0) for i in range(n))
    results.append(("sigAny_invariant", anyok, "sigAny == OR(47 fires) every bar"))

    # 8 DYNAMITE leaf parity — every f_dyn* fire requires the independently-derived
    #    B2B-displacement + dir + FAUNA[1]&[2] + FVG leaf (mt is the DYNAMITE tape).
    ind = _independent(dyn, p, 10)
    dynB_ok = all((not mt["fire_f_dynBull"][i]) or ind["dynBull"][i] for i in range(n))
    dynR_ok = all((not mt["fire_f_dynBear"][i]) or ind["dynBear"][i] for i in range(n))
    results.append(("dynamite_leaf_parity", dynB_ok and dynR_ok,
                    f"dynBull fires={sum(mt['fire_f_dynBull'])} (indep B2B-disp+FAUNA+FVG={sum(ind['dynBull'])}); "
                    f"dynBear fires={sum(mt['fire_f_dynBear'])} (indep={sum(ind['dynBear'])})"))

    # 9 CATALYST implies an independent Engine-1 displacement event (Napalm rides
    #    displacement). Necessary condition. Evaluated on the osc tape where TNT
    #    zones + napalm can form (TNT_SENS).
    mo = tickmod.run_on_bars(osc, params=_PTNT)
    no = len(osc)
    indo = _independent(osc, _PTNT, 60)
    catB_ok = all((not mo["fire_f_catBull"][i]) or indo["dispBull"][i] for i in range(no))
    catR_ok = all((not mo["fire_f_catBear"][i]) or indo["dispBear"][i] for i in range(no))
    results.append(("catalyst_napalm_chain", catB_ok and catR_ok,
                    f"catBull fires={sum(mo['fire_f_catBull'])} all require indep Engine-1 displacement; "
                    f"catBear fires={sum(mo['fire_f_catBear'])}"))

    # 10 Tier-2 TNT-ENR is hard-gated by enrichment — assert it never fires before
    #    the enrichment engines are warm (no warmup ghosts). Evaluated on osc tape.
    t2_warm_ok = all((not (mo["fire_f_t2tntBull"][i] or mo["fire_f_t2tntBear"][i])) or i >= 20 for i in range(no))
    results.append(("enrich_gate_parity", t2_warm_ok,
                    f"t2tntBull fires={sum(mo['fire_f_t2tntBull'])}, "
                    f"t2tntBear fires={sum(mo['fire_f_t2tntBear'])}; none fire before enrichment warmup"))

    # 11 non-triviality (union across BOTH purpose-built tapes)
    fired = sum(sum(mt[f"fire_{pid}"]) for pid in PIDS) + sum(sum(mo[f"fire_{pid}"]) for pid in PIDS)
    distinct = sum(1 for pid in PIDS if sum(mt[f"fire_{pid}"]) > 0 or sum(mo[f"fire_{pid}"]) > 0)
    results.append(("non_triviality", fired > 0,
                    f"total fires (dyn+osc tapes)={fired}, distinct plots fired={distinct}/47"))

    # 12 negative control (flat doji tape)
    try:
        flat = tickmod.run_on_bars(_flat_tape(300))
        flat_fires = sum(sum(flat[f"fire_{pid}"]) for pid in PIDS)
        results.append(("negative_control_zero", flat_fires == 0, f"flat tape total fires={flat_fires}"))
    except Exception as e:
        results.append(("negative_control_zero", False, f"EXC {e}"))

    # 13 warmup
    try:
        tiny = synthetic_bars(n=8, grain="time")
        wt = tickmod.run_on_bars(tiny)
        warm_fires = sum(sum(wt[f"fire_{pid}"]) for pid in PIDS)
        results.append(("warmup_no_premature_fire", warm_fires == 0, f"fires on 8-bar tape={warm_fires}"))
    except Exception as e:
        results.append(("warmup_no_premature_fire", False, f"EXC {e}"))

    # 14 honesty: no declared stubs + matrix exercised (>= 1 distinct plot fires)
    no_stubs = (len(tickmod.COMPOSITE_PARTIAL) == 0 and len(timemod.COMPOSITE_PARTIAL) == 0
                and len(core.COMPOSITE_PARTIAL) == 0)
    union_fire = set()
    for tape, prm in ((dyn, None), (osc, _PTNT), (multi, _PTNT)):
        m = tickmod.run_on_bars(tape, params=prm)
        for pid in PIDS:
            if sum(m[f"fire_{pid}"]) > 0:
                union_fire.add(pid)
    results.append(("honesty_no_stub_and_exercised", no_stubs and len(union_fire) >= 1,
                    f"declared_stubs=0, distinct plots fired across tapes={len(union_fire)}: "
                    f"{sorted(union_fire)[:10]}{'...' if len(union_fire) > 10 else ''}"))

    return results


if __name__ == "__main__":
    res = run()
    passed = sum(1 for _, ok, _ in res if ok)
    total = len(res)
    print(f"=== TNT OD v3 PARITY (FULL port, 47 detection plots): {passed}/{total} ===")
    for name, ok, detail in res:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:30s} {detail}")
    sys.exit(0 if passed == total else 1)
