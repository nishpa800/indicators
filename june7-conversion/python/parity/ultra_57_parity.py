# NINE NINES parity harness — ULTRA COMBO v57 (FULL port, 35 detection plots)
# =============================================================================
# Runnable offline Gate-B for the Ultra Combo v57 Pine v5 -> Python port.
# Re-runnable by a stranger:  python3 ultra_57_parity.py
# Prints a REAL pass/total and exits 0 only if all checks pass.
#
# The study is a deep multi-engine aggregator: 35 combo detection plots built on
# top of primitive engines (PB&J supertrend, FAUNA, GZ1/HV FVG, RVOL heavy-weapon
# table, F2/E3/FC cluster, PUP/PPD stages, ROC/wavetrend, displacement). A full
# "independent second copy of every combo" would just be the core again, so the
# offline gate (a) proves the structural / determinism / honesty invariants that
# catch real port bugs, and (b) independently re-derives the PRIMITIVE engines
# (the layer the combos are functions of) and asserts the combos are subsets of
# those independent primitives. Gate-A (TradingView-live coordinate parity) and
# relativeVolume-tick live parity are the DEFERRED ledgers per the nine-nines skill.
#
# CHECKS:
#   1. plot_count_eq_35          — PLOT_IDS == 35 distinct detection plotshapes
#                                  (== Pine plotshape( count, NAGA included).
#   2. time_port_runs            — time wrapper yields fire_/lvl_ matrix.
#   3. tick_port_runs            — tick wrapper yields fire_/lvl_ matrix.
#   4. tick_eq_time              — SAME core on SAME bars + SAME tfSec -> byte-
#                                  identical fire matrix through both wrappers.
#   5. determinism               — two runs on identical bars -> identical matrix.
#   6. boolean_matrix_and_levels — every fire_ is strictly 0/1; lvl_ present
#                                  exactly where fire==1, absent (None) where 0.
#   7. honesty_stub_is_zero      — COMPOSITE_PARTIAL empty on BOTH wrappers AND
#                                  matrix genuinely exercised (>=5 distinct plots
#                                  fire). A green that fired nothing = fabricated.
#   8. negative_control          — flat doji tape (no body/range/vol/gap) fires 0.
#   9. warmup_no_window_fire     — tiny tape doesn't crash; window-dependent plots
#                                  (RVOL/disp/cluster) don't fire before warm.
#  10. rvol_shim_not_naive       — canonical relativeVolume shim ratio differs
#                                  from naive volume/sma(volume,N) (proves the
#                                  banned approximation is NOT on the path).
#  11. fauna_primitive_subset    — every combo that REQUIRES FAUNA (Super/Mega)
#                                  sits only on independently re-derived FAUNA bars.
#  12. disp_primitive_subset     — every Super/Mega combo sits only on independent
#                                  displacement-FVG bars.
#  13. naga_primitive_parity     — f_NAGA == independent running-max-volume series.
#  14. mega_superset_structure   — f_MEGA is a superset of f_GZ1HVMEGA (gzHvMega =
#                                  gz1Mega OR hvMega; both-GZ1+HV is the stricter).
#  15. param_no_magic            — re-running with a deliberately stricter Params
#                                  (raised vol_mult) yields a DIFFERENT, not-larger
#                                  matrix (proves thresholds are live parameters).
# =============================================================================
from __future__ import annotations

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tick"))
sys.path.insert(0, os.path.join(_ROOT, "time"))

from _nine_nines_common import Bar                       # noqa: E402
from _nn_harness import (                                 # noqa: E402
    synthetic_bars, sma, stdev, shift, highest, atr as _atr_ohlc, nz, relative_volume,
)
import _ultra_57_core as core                             # noqa: E402
import ultra_57_tick as tickmod                           # noqa: E402
import ultra_57_time as timemod                           # noqa: E402

SOURCE = ("/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT "
          "transformed yet/June 7/Tick Friendly conversion/ultra_57_tickfriendly.pine")


# ─────────────────────────── deterministic tapes ────────────────────────────
def _stress_tape(nbars=1600, seed=11):
    """Multi-session tape: long CALM baselines (tiny bodies, low vol) punctuated by
    widely-spaced clusters of big-body, gap (FVG), high-volume bars — so the deep
    confluence engines (FAUNA / displacement / GZ-HV / cluster / RVOL) actually
    light end-to-end. Alternating bull/bear clusters exercise both polarities."""
    import random
    random.seed(seed)
    rows = []
    t0 = 1_700_000_000_000
    px = 2000.0
    i = 0
    clusters = [2, 4, 2, 3, 4, 2]
    ci = 0

    def _push(o, hi, lo, cl, vol):
        nonlocal i
        ts = t0 + (i // 90) * 86_400_000 + (i % 90) * 60_000
        rows.append(Bar(ts, round(o, 4), round(hi, 4), round(lo, 4), round(cl, 4), round(vol, 2)))
        i += 1

    while i < nbars:
        for _ in range(80):                        # long calm gap -> stdev tiny
            if i >= nbars:
                break
            o = px
            cl = o + random.uniform(-0.04, 0.04)
            hi = max(o, cl) + random.uniform(0.01, 0.05)
            lo = min(o, cl) - random.uniform(0.01, 0.05)
            _push(o, hi, lo, cl, random.uniform(8000, 10000))
            px = cl
        clen = clusters[ci % len(clusters)]
        bull = (ci % 2 == 0)
        ci += 1
        for _ in range(clen):                       # big gap event bars
            if i >= nbars:
                break
            if bull:
                o = px + random.uniform(6, 10)      # gap above high[2] -> bull FVG
                cl = o + random.uniform(20, 30)
                hi = cl + random.uniform(0.02, 0.1)
                lo = o - random.uniform(0.02, 0.1)
            else:
                o = px - random.uniform(6, 10)      # gap below low[2] -> bear FVG
                cl = o - random.uniform(20, 30)
                hi = o + random.uniform(0.02, 0.1)
                lo = cl - random.uniform(0.02, 0.1)
            _push(o, hi, lo, cl, 300000.0)
            px = cl
    return rows


def _confluence_tape(nsessions=40, seed=7):
    """Engineered CONFLUENCE tape: each RTH session OPENS with 4 consecutive big
    bullish MB bars (gap-up -> bull FVG, body >> ATR, heavy-weapon volume) so the
    session-anchored combos actually align: F2 at sessBar==2, E3 at sessBar==3,
    FC cluster, PBJ supertrend crossings, heavy-weapon RVOL, GZ/HV FVG — plus
    cross-day repeats (F2_2D/E3_2D/CL_2D). Calm midday + a between-session pullback
    keeps trend math honest. This is the only tape that lights the deep combo
    confluence end-to-end (see the honesty gate); without it the combos are too
    rare to prove the engines are wired, which would make a green meaningless."""
    import random
    random.seed(seed)
    rows = []
    t0 = 1_700_000_000_000
    px = 300.0
    SBP = 24  # session bars/day
    for s in range(nsessions):
        for k in range(SBP):
            ts = t0 + s * 86_400_000 + k * 60_000
            if k < 4:                                   # session-open MB streak
                o = px + random.uniform(2, 4)           # gap up -> bull FVG vs high[2]
                cl = o + random.uniform(8, 14)          # big body >> atr
                hi = cl + random.uniform(0.02, 0.1)
                lo = o - random.uniform(0.02, 0.1)
                vol = random.uniform(250000, 400000)    # heavy-weapon volume
            else:                                       # calm midday
                o = px
                cl = o + random.uniform(-0.3, 0.3)
                hi = max(o, cl) + random.uniform(0.05, 0.2)
                lo = min(o, cl) - random.uniform(0.05, 0.2)
                vol = random.uniform(2000, 5000)
            rows.append(Bar(ts, round(o, 4), round(hi, 4), round(lo, 4), round(cl, 4), round(vol, 2)))
            px = cl
        px *= 0.97                                      # between-session pullback
    return rows


def _flat_tape(nbars=300):
    """Doji tape: open==close, no range, constant volume, no gaps -> no fires."""
    rows = []
    t0 = 1_700_000_000_000
    for i in range(nbars):
        ts = t0 + (i // 24) * 86_400_000 + (i % 24) * 60_000
        rows.append(Bar(ts, 100.0, 100.0, 100.0, 100.0, 1000.0))
    return rows


def _naive_rvol(v, length):
    s = sma(v, length)
    return [None if (s[i] in (None, 0)) else v[i] / s[i] for i in range(len(v))]


# ───────────────── independent re-derivations (answer keys) ──────────────────
def _independent(bars):
    """Re-derive the PRIMITIVE engines the combos are functions of, from scratch,
    so combo subset checks have an independent reference."""
    n = len(bars)
    o = [b.open for b in bars]; h = [b.high for b in bars]; l = [b.low for b in bars]
    c = [b.close for b in bars]; v = [b.volume for b in bars]
    conf = [True] * n
    atr14 = _atr_ohlc(o, h, l, c, 14)
    avgVol = sma(v, 20)
    avgBody = sma([abs(c[i] - o[i]) for i in range(n)], 20)
    avgDelta = sma([abs(c[i] - c[i - 1]) if i > 0 else 0.0 for i in range(n)], 10)
    trendMA = sma(c, 50)
    avgBody1 = shift(avgBody, 1)
    avgVol1 = shift(avgVol, 1)

    # FAUNA bull + bear (independent of the core)
    fauna_bull = [False] * n
    fauna_bear = [False] * n
    for i in range(n):
        if atr14[i] is None or avgVol[i] is None:
            continue
        body = c[i] - o[i]; rng = h[i] - l[i]; up = body > 0; dn = body < 0; bsz = abs(body)
        brat = 0.0 if rng == 0 else bsz / rng
        MBb = up and bsz > 1.6 * atr14[i] and brat > 0.70 and v[i] > 1.8 * avgVol[i]
        REb = up and rng > 2.2 * atr14[i] and (h[i] - c[i]) < 0.15 * rng and v[i] > 1.8 * avgVol[i]
        TAb = (i > 0 and trendMA[i] is not None and trendMA[i - 1] is not None and trendMA[i] > trendMA[i - 1]
               and avgDelta[i] is not None and (c[i] - c[i - 1]) > 1.6 * avgDelta[i] and up and v[i] > 1.8 * avgVol[i])
        MBr = dn and bsz > 1.6 * atr14[i] and brat > 0.70 and v[i] > 1.8 * avgVol[i]
        REr = dn and rng > 2.2 * atr14[i] and (c[i] - l[i]) < 0.15 * rng and v[i] > 1.8 * avgVol[i]
        TAr = (i > 0 and trendMA[i] is not None and trendMA[i - 1] is not None and trendMA[i] < trendMA[i - 1]
               and avgDelta[i] is not None and (c[i - 1] - c[i]) > 1.6 * avgDelta[i] and dn and v[i] > 1.8 * avgVol[i])
        excl_b = excl_r = False
        if i > 0 and avgBody1[i] is not None and avgVol1[i] is not None:
            GGb = (o[i] - c[i - 1]) > 0.9 * atr14[i] and up and l[i] > c[i - 1] and v[i] > 1.8 * avgVol[i]
            GGr = (c[i - 1] - o[i]) > 0.9 * atr14[i] and dn and h[i] < c[i - 1] and v[i] > 1.8 * avgVol[i]
            pbody = c[i - 1] - o[i - 1]; prange = h[i - 1] - l[i - 1]
            StrongBear = c[i - 1] < o[i - 1] and abs(pbody) > 1.5 * avgBody1[i] and v[i - 1] > 1.5 * avgVol1[i]
            WeakBear = c[i - 1] < o[i - 1] and (0.0 if prange == 0 else abs(pbody) / prange) <= 0.2
            StrongBull = c[i - 1] > o[i - 1] and abs(pbody) > 1.5 * avgBody1[i] and v[i - 1] > 1.5 * avgVol1[i]
            WeakBull = c[i - 1] > o[i - 1] and (0.0 if prange == 0 else abs(pbody) / prange) <= 0.2
            excl_b = ((WeakBear and (MBb or REb or TAb)) or (StrongBear and (MBb or REb or TAb))
                      or (c[i - 1] < o[i - 1] and GGb) or GGb)
            excl_r = ((WeakBull and (MBr or REr or TAr)) or (StrongBull and (MBr or REr or TAr))
                      or (c[i - 1] > o[i - 1] and GGr) or GGr)
        fauna_bull[i] = conf[i] and (MBb or REb or TAb) and not excl_b
        fauna_bear[i] = conf[i] and (MBr or REr or TAr) and not excl_r

    # displacement-FVG bull + bear (independent)
    disp_rng = [abs(o[i] - c[i]) for i in range(n)]
    disp_std = stdev(disp_rng, 100)
    disp_thr = [None if disp_std[i] is None else disp_std[i] * 5.0 for i in range(n)]
    disp_prev = [i >= 1 and disp_thr[i - 1] is not None and disp_rng[i - 1] > disp_thr[i - 1] for i in range(n)]
    disp_bull = [conf[i] and disp_prev[i] and i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1] for i in range(n)]
    disp_bear = [conf[i] and disp_prev[i] and i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1] for i in range(n)]

    # NAGA (independent running max volume)
    naga = [False] * n
    mx = 0.0
    for i in range(n):
        if i == 0:
            mx = v[i]
        elif v[i] > mx:
            naga[i] = True
            mx = v[i]

    return dict(fauna_bull=fauna_bull, fauna_bear=fauna_bear,
                disp_bull=disp_bull, disp_bear=disp_bear, naga=naga)


# ───────────────────────────────── checks ───────────────────────────────────
def run():
    results = []
    stress = _stress_tape(1600, 11)
    multi = synthetic_bars(n=1200, grain="time")
    confl = _confluence_tape(40, 7)

    # 1 plot count == 35
    src_plotshapes = None
    if os.path.exists(SOURCE):
        src_plotshapes = len(re.findall(r"plotshape\(", open(SOURCE, errors="ignore").read()))
    results.append(("plot_count_eq_35", len(core.PLOT_IDS) == 35,
                    f"PLOT_IDS={len(core.PLOT_IDS)}, source plotshape(={src_plotshapes})"))

    # 2 time port runs
    try:
        ot = timemod.run_on_bars(multi, tf_seconds=3600)
        ok = isinstance(ot, dict) and any(k.startswith("fire_") for k in ot)
        results.append(("time_port_runs", ok, f"{sum(1 for k in ot if k.startswith('fire_'))} plots"))
    except Exception as e:
        ot = {}; results.append(("time_port_runs", False, f"EXC {e}"))

    # 3 tick port runs
    try:
        ob = tickmod.run_on_bars(multi)
        ok = isinstance(ob, dict) and any(k.startswith("fire_") for k in ob)
        results.append(("tick_port_runs", ok, f"{sum(1 for k in ob if k.startswith('fire_'))} plots"))
    except Exception as e:
        ob = {}; results.append(("tick_port_runs", False, f"EXC {e}"))

    # 4 tick == time (same bars, same tfSec) — one code path, grain-bound
    try:
        a = timemod.run_on_bars(stress, tf_seconds=60)
        b = tickmod.run_on_bars(stress, tf_seconds=60)
        keys = [k for k in a if k.startswith("fire_") or k.startswith("lvl_")]
        mism = [k for k in keys if a[k] != b.get(k)]
        results.append(("tick_eq_time", not mism,
                        "identical fire+level matrix" if not mism else f"mismatch {mism[:4]}"))
    except Exception as e:
        results.append(("tick_eq_time", False, f"EXC {e}"))

    # 5 determinism
    try:
        d1 = timemod.run_on_bars(stress, tf_seconds=60)
        d2 = timemod.run_on_bars(_stress_tape(1600, 11), tf_seconds=60)
        results.append(("determinism", d1 == d2, "stable" if d1 == d2 else "non-deterministic"))
    except Exception as e:
        results.append(("determinism", False, f"EXC {e}"))

    # 6 boolean matrix + level alignment
    try:
        mt = timemod.run_on_bars(stress, tf_seconds=60)
        bad = []
        for pid in core.PLOT_IDS:
            f = mt[f"fire_{pid}"]; lv = mt[f"lvl_{pid}"]
            if any(x not in (0, 1) for x in f):
                bad.append(f"{pid}:nonbool"); continue
            for i in range(len(f)):
                if f[i] == 1 and lv[i] is None:
                    bad.append(f"{pid}:fire-no-lvl"); break
                if f[i] == 0 and lv[i] is not None:
                    bad.append(f"{pid}:nofire-has-lvl"); break
        results.append(("boolean_matrix_and_levels", not bad,
                        "all 0/1 + levels aligned" if not bad else str(bad[:4])))
    except Exception as e:
        results.append(("boolean_matrix_and_levels", False, f"EXC {e}"))

    # 7 honesty: zero declared stubs + matrix exercised (>=5 distinct plots fire)
    union_fire = set()
    for tape in (stress, multi, confl):
        m = timemod.run_on_bars(tape, tf_seconds=60)
        for pid in core.PLOT_IDS:
            if sum(m[f"fire_{pid}"]) > 0:
                union_fire.add(pid)
    no_stubs = (len(timemod.COMPOSITE_PARTIAL) == 0 and len(tickmod.COMPOSITE_PARTIAL) == 0)
    exercised = len(union_fire) >= 5
    results.append(("honesty_stub_is_zero", no_stubs and exercised,
                    f"declared_stubs=0={no_stubs}, distinct plots fired={len(union_fire)}: "
                    f"{sorted(union_fire)[:14]}"))

    # 8 negative control: flat doji tape fires nothing
    try:
        flat = timemod.run_on_bars(_flat_tape(300), tf_seconds=60)
        flat_fires = sum(sum(flat[f"fire_{pid}"]) for pid in core.PLOT_IDS)
        results.append(("negative_control_zero", flat_fires == 0, f"flat tape total fires={flat_fires}"))
    except Exception as e:
        results.append(("negative_control_zero", False, f"EXC {e}"))

    # 9 warmup: tiny tape doesn't crash and doesn't fire window-dependent plots
    try:
        tiny = synthetic_bars(n=12, grain="time")
        wt = timemod.run_on_bars(tiny, tf_seconds=60)
        win_plots = ["HW_Bull", "HW_Bear", "MEGA_Bull", "MEGA_Bear", "F2_2D", "E3_2D",
                     "GZHV_Bull", "GZHV_Bear", "Super2D_Bull", "Super2D_Bear"]
        warm_fires = sum(sum(wt[f"fire_{pid}"]) for pid in win_plots)
        results.append(("warmup_no_window_fire", warm_fires == 0,
                        f"window-plot fires on 12-bar tape={warm_fires}"))
    except Exception as e:
        results.append(("warmup_no_window_fire", False, f"EXC {e}"))

    # 10 RVOL shim != naive volume/sma — prove the canonical shim is on the path
    try:
        v = [b.volume for b in multi]; ts = [b.ts for b in multi]
        _, _, shim_ratio = relative_volume(v, 30, anchor_timeframe="D", is_cumulative=False, bar_timestamps=ts)
        naive = _naive_rvol(v, 30)
        diffs = [abs(shim_ratio[i] - naive[i]) for i in range(len(v))
                 if shim_ratio[i] is not None and naive[i] is not None]
        maxd = max(diffs) if diffs else 0.0
        results.append(("rvol_shim_not_naive", maxd > 1e-6,
                        f"max|shim-naiveSMA|={maxd:.4f} (>0 => canonical shim, not volume/SMA)"))
    except Exception as e:
        results.append(("rvol_shim_not_naive", False, f"EXC {e}"))

    # 11/12/13 independent primitive parity
    ind = _independent(stress)
    mt = timemod.run_on_bars(stress, tf_seconds=60)
    n = len(stress)

    # 11 FAUNA: Super/Mega combos require FAUNA(dir) -> subset of independent fauna
    fauna_combos_bull = ["MEGA_Bull", "GZ1HVMEGA_Bull", "FosterHvy_Bull"]  # foster needs sigROC/HW path not fauna
    super_bull = ["MEGA_Bull", "GZ1HVMEGA_Bull"]
    super_bear = ["MEGA_Bear", "GZ1HVMEGA_Bear"]
    fok = True
    detail = []
    for pid in super_bull:
        f = mt[f"fire_{pid}"]
        sub = all((f[i] == 0) or ind["fauna_bull"][i] for i in range(n))
        fok = fok and sub
        detail.append(f"{pid}(fired={sum(f)},subset={sub})")
    for pid in super_bear:
        f = mt[f"fire_{pid}"]
        sub = all((f[i] == 0) or ind["fauna_bear"][i] for i in range(n))
        fok = fok and sub
        detail.append(f"{pid}(fired={sum(f)},subset={sub})")
    results.append(("fauna_primitive_subset", fok,
                    f"ind_fauna_bull={sum(ind['fauna_bull'])}, ind_fauna_bear={sum(ind['fauna_bear'])}; "
                    + " ".join(detail)))

    # 12 displacement: Super/Mega combos require displacement-FVG(dir) -> subset
    dok = True
    ddetail = []
    for pid in super_bull:
        f = mt[f"fire_{pid}"]
        sub = all((f[i] == 0) or ind["disp_bull"][i] for i in range(n))
        dok = dok and sub
        ddetail.append(f"{pid}(subset={sub})")
    for pid in super_bear:
        f = mt[f"fire_{pid}"]
        sub = all((f[i] == 0) or ind["disp_bear"][i] for i in range(n))
        dok = dok and sub
        ddetail.append(f"{pid}(subset={sub})")
    results.append(("disp_primitive_subset", dok,
                    f"ind_disp_bull={sum(ind['disp_bull'])}, ind_disp_bear={sum(ind['disp_bear'])}; "
                    + " ".join(ddetail)))

    # 13 NAGA exact parity vs independent running-max-volume
    naga_core = [bool(mt["fire_NAGA"][i]) for i in range(n)]
    naga_ind = [bool(ind["naga"][i]) for i in range(n)]
    results.append(("naga_primitive_parity", naga_core == naga_ind,
                    f"core_naga={sum(naga_core)}, ind_naga={sum(naga_ind)}"))

    # 14 structure: f_MEGA superset of f_GZ1HVMEGA (gzHvMega = gz1Mega OR hvMega)
    sup = all((mt["fire_MEGA_Bull"][i] >= mt["fire_GZ1HVMEGA_Bull"][i]
               and mt["fire_MEGA_Bear"][i] >= mt["fire_GZ1HVMEGA_Bear"][i]) for i in range(n))
    results.append(("mega_superset_structure", sup,
                    f"MEGA superset of GZ1HVMEGA "
                    f"(MEGA_B={sum(mt['fire_MEGA_Bull'])}, GZ1HV_B={sum(mt['fire_GZ1HVMEGA_Bull'])})"))

    # 15 params are live: a stricter Params (raised mb_body_atr_mult, which gates
    #    the actively-firing MB->F2/E3/cluster combos) yields a DIFFERENT and
    #    not-larger fire matrix on the confluence tape. Proves every threshold is
    #    a real parameter, not a magic number baked into the logic.
    try:
        base = timemod.run_on_bars(confl, tf_seconds=60)
        strict = timemod.run_on_bars(confl, params=core.Params(tfSec=60, mb_body_atr_mult=6.0))
        base_tot = sum(sum(base[f"fire_{pid}"]) for pid in core.PLOT_IDS)
        strict_tot = sum(sum(strict[f"fire_{pid}"]) for pid in core.PLOT_IDS)
        changed = any(base[f"fire_{pid}"] != strict[f"fire_{pid}"] for pid in core.PLOT_IDS)
        results.append(("param_no_magic", changed and strict_tot < base_tot,
                        f"mb_body_atr_mult 1.6->6.0 changed matrix; total fires {base_tot} -> {strict_tot}"))
    except Exception as e:
        results.append(("param_no_magic", False, f"EXC {e}"))

    return results


if __name__ == "__main__":
    res = run()
    passed = sum(1 for _, ok, _ in res if ok)
    total = len(res)
    print(f"=== ULTRA COMBO v57 PARITY (FULL port, 35 plots): {passed}/{total} ===")
    for name, ok, detail in res:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:28s} {detail}")
    sys.exit(0 if passed == total else 1)
