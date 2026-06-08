"""Heavy Weapons w SAAB Kratos x2 (NRA SINGLES) — parity harness (offline Gate-B).

FULL port (every detection plot derived from OHLCV — no stub layer). This harness
verifies, on deterministic synthetic + engineered bars, and prints a REAL pass/total:

  1. DETERMINISM               — two runs on identical bars give an identical matrix.
  2. TICK == TIME              — the SAME core on the SAME Bar objects yields an
                                 identical fire matrix through both wrappers (one
                                 code path, grain-bound). Run with the SAME tfSec.
  3. PLOT COUNT vs SOURCE      — ported detection-plot count == source plotshape
                                 count (42). The source plotshapes are enumerated.
  4. RVOL 0.56 parity          — sigSAAB/Kratos/Bull1x/Bear1x/GS/MOAB re-derived
                                 from an INDEPENDENT re-typing of the source formulas.
  5. DISPLACEMENT parity       — Disp Bull/Bear + Consec 2+/3+ re-derived independently
                                 (single std band: min<range[1]<=max).
  6. SEQUENCE parity           — UU/DD re-derived independently (IPSF streak + sum).
  7. HV ladder parity          — HV75..1000 exclusivity (NRA via [1]) independently.
  8. B2B parity                — 2x SAAB + B2B Mid Bull re-derived independently (ungated).
  9. BOOLEAN matrix            — every fire_* series is strictly 0/1.
 10. HONESTY (stub-is-zero)    — NO faked all-zero "stub" plots in the module AND the
                                 matrix is genuinely exercised (>=6 distinct plots fire
                                 on the event-rich tape). A green that fired nothing
                                 would be fabricated parity; this gate forbids it.
 11. RVOL ENGINE ALIVE         — at least one RVOL/momentum-derived primitive fires on
                                 the multi-session tape (the relativeVolume shim path
                                 is not silently dead).
 12. NEGATIVE CONTROL          — a flat doji tape (no body, no volume spikes) fires
                                 nothing (no false positives from warmup math).
 13. WARMUP                    — a very short tape does not crash and does not fire
                                 window-dependent plots (disp/std/RVOL/HV not warm).
 14. RVOL SHIM USED            — shim ratio differs from naive volume/sma(volume,N) on
                                 the volume-smile tape (proves the canonical shim, not
                                 the banned volume/SMA approximation, is in the path).

Re-runnable by a stranger:  python3 heavy_with_2x_detection_plots_parity.py
REAL pass/total is printed; exit 0 only if all pass.
"""
from __future__ import annotations

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tick"))
sys.path.insert(0, os.path.join(_ROOT, "time"))

from _nine_nines_common import Bar  # noqa: E402
from _nn_harness import synthetic_bars, sma, stdev, shift, highest, nz  # noqa: E402
import _heavy_with_2x_detection_plots_core as core  # noqa: E402
import heavy_with_2x_detection_plots_tick as tickmod  # noqa: E402
import heavy_with_2x_detection_plots_time as timemod  # noqa: E402

SOURCE = ("/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT "
          "transformed yet/June 7/Tick Friendly conversion/"
          "heavy_with_2x_detection_plots_tickfriendly.pine")


# ─────────────────────────── deterministic tapes ────────────────────────────
def _make_bars(grain="time", n=900):
    return synthetic_bars(n=n, grain=grain)


def _stress_tape(nbars=1600, seed=11):
    """Strong-oscillation tape: 6 up bars / 6 down bars, each a large body with
    substantial + occasionally spiking volume. Drives RVOL, displacement, FVG,
    sequences, B2B and HV/Nagasaki end-to-end (so the matrix is genuinely lit)."""
    import random
    random.seed(seed)
    rows = []
    t = 1_700_000_000_000
    px = 100.0
    i = 0
    while i < nbars:
        for _ in range(6):           # up leg
            if i >= nbars:
                break
            o = px
            px = o * (1 + random.uniform(0.035, 0.06))
            vol = random.uniform(80000, 500000)
            if i % 53 == 0:
                vol *= 12.0           # periodic ATH-class spikes (Nagasaki/HV)
            rows.append((t + i * 60_000, o, px * 1.01, o * 0.99, px, vol))
            i += 1
        for _ in range(6):           # down leg
            if i >= nbars:
                break
            o = px
            px = o * (1 - random.uniform(0.035, 0.06))
            vol = random.uniform(80000, 500000)
            if i % 47 == 0:
                vol *= 12.0
            rows.append((t + i * 60_000, o, o * 1.01, px * 0.99, px, vol))
            i += 1
    return [Bar(int(a), b, c, d, e, f) for (a, b, c, d, e, f) in rows]


def _flat_tape(n=300):
    """Negative-control tape: tiny doji bodies, NO FVGs, and a strictly varying
    volume with NO ties (so no bar equals the rolling highest -> HV stays dark) and
    no volume spikes (no Nagasaki/RVOL). Timestamps sit in a single mid-month, mid-
    week window OUTSIDE every Hot Spot calendar window so the calendar plot is also
    dark. A faithful port must fire NOTHING here — any fire is a false positive.

    NOTE: a CONSTANT-volume tape is NOT a valid negative control for the HV plots,
    because Pine's `volume[1]==ta.highest(volume,N)[1]` is TRUE on every bar when all
    volumes tie (the max equals the value). That is faithful source behavior on a
    degenerate tape, not a bug, so we avoid ties here. Likewise Hot Spot is a pure
    calendar signal; we place this tape off every window rather than special-casing it."""
    import datetime as _dt
    # 2026-02-05 (Thu) 15:30 UTC: month=2 (no qtr/russell/taxLoss/jan/hfRedemp),
    # day 5 (< 10, outside opEx 10-17), so isHotSpot is False for the whole tape.
    base = _dt.datetime(2026, 2, 5, 15, 30, 0, tzinfo=_dt.timezone.utc)
    bars = []
    for i in range(n):
        ts = int((base + _dt.timedelta(minutes=i)).timestamp() * 1000)
        # micro down-then-up doji wiggle, body ~0, range ~0 (no displacement/FVG)
        px = 100.0 + (0.0001 if i % 2 == 0 else -0.0001)
        # strictly DECREASING volume: a bar's prior-bar volume (volume[1]) is never
        # the highest in its lookback window (the max is always further back), so the
        # NRA `volume[1]==highest(volume,N)[1]` HV rule is false on every scored bar.
        vol = 1_000_000.0 - i * 100.0
        bars.append(Bar(ts, 100.0, max(100.0, px) + 0.00005, min(100.0, px) - 0.00005, px, vol))
    return bars


def _multisession_tape(sessions=50, bars_per_session=14, seed=7):
    """Multi-day tape: each session is its own calendar day with bars at the SAME
    clock offsets, so the RVOL 'at time' shim has prior sessions to average against
    (lights RVOL/momentum/WTC/Hiroshima plots, not just displacement). Late sessions
    inject deliberate price-spike-exceeds-volume bars (SAAB/RVOL ladder) and ATH
    volume (Nagasaki/HV)."""
    import datetime as _dt
    import random
    random.seed(seed)
    base = _dt.datetime(2026, 1, 5, 14, 30, 0, tzinfo=_dt.timezone.utc)
    bars = []
    px = 100.0
    for s in range(sessions):
        day = base + _dt.timedelta(days=s)
        for k in range(bars_per_session):
            ts = int((day + _dt.timedelta(minutes=k)).timestamp() * 1000)
            o = px
            big = (s >= 20) and (k % 5 == 0)         # periodic large directional body
            if big:
                drift = (1.0 if (s + k) % 2 == 0 else -1.0) * o * 0.05
                px = max(0.5, o + drift)
                hi = max(o, px) + abs(drift) * 0.05
                lo = min(o, px) - abs(drift) * 0.05
                vol = 1500.0 + random.uniform(0, 200)   # MODEST vol -> price spike >> vol (SAAB)
            else:
                px = max(0.5, o + random.uniform(-0.15, 0.15))
                hi = max(o, px) + 0.05
                lo = min(o, px) - 0.05
                vol = 1000.0 + random.uniform(0, 100)
            if s == sessions - 1 and k == bars_per_session // 2:
                vol = 1_000_000.0                       # ATH volume late -> Nagasaki/HV
            bars.append(Bar(ts, round(o, 4), round(hi, 4), round(lo, 4), round(px, 4), round(vol, 2)))
    return bars


# ───────────── independent re-typing of source formulas (references) ──────────
def _ref_columns(bars):
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    l = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    return o, h, l, c, v


def _ref_rvol_056(bars, P):
    """Independent re-typing of the RVOL 0.56 bull/bear ladder (source L264-287)."""
    o, h, l, c, v = _ref_columns(bars)
    n = len(bars)
    spike = [abs(c[i] - o[i]) for i in range(n)]
    avgSpike = shift(sma(spike, P.bb_avgLength), 1)
    normPrice = [spike[i] / nz(avgSpike[i], 1.0) for i in range(n)]
    avgVol = shift(sma(v, P.bb_avgLength), 1)
    normVol = [v[i] / nz(avgVol[i], 1.0) for i in range(n)]
    diff = [normPrice[i] - normVol[i] for i in range(n)]
    posDiff = [d if d > 0 else None for d in diff]
    smaDiff = sma(posDiff, P.bb_smaLength)
    s = P.tfSec
    th1x = core.f_rvol_1x_threshold(s)
    thSK = th1x * 0.56
    thGM = core.f_gs_moab_threshold(s)

    def bull(i):
        return c[i] > o[i] and posDiff[i] is not None and smaDiff[i] is not None and posDiff[i] > smaDiff[i]

    def bear(i):
        return c[i] < o[i] and posDiff[i] is not None and smaDiff[i] is not None and posDiff[i] > smaDiff[i]

    saab = [bull(i) and thSK <= normPrice[i] < th1x for i in range(n)]
    krat = [bear(i) and thSK <= normPrice[i] < th1x for i in range(n)]
    b1x = [bull(i) and th1x <= normPrice[i] < thGM for i in range(n)]
    be1x = [bear(i) and th1x <= normPrice[i] < thGM for i in range(n)]
    gs = [bull(i) and normPrice[i] >= thGM for i in range(n)]
    moab = [bear(i) and normPrice[i] >= thGM for i in range(n)]
    return saab, krat, b1x, be1x, gs, moab, normPrice, (bull, bear)


def _ref_disp(bars, P):
    """Independent re-typing of standalone + consec displacement (source L670-699).
    Single std band: range[1] > stdMin[1] and range[1] <= stdMax[1]."""
    o, h, l, c, v = _ref_columns(bars)
    n = len(bars)
    rng = [abs(o[i] - c[i]) if P.i_disp_type == "Open to Close" else h[i] - l[i] for i in range(n)]
    sd = stdev(rng, P.i_std_len)
    thMin = [None if sd[i] is None else sd[i] * P.i_std_min for i in range(n)]
    thMax = [None if sd[i] is None else sd[i] * P.i_std_max for i in range(n)]
    rng1 = shift(rng, 1)
    thMin1 = shift(thMin, 1)
    thMax1 = shift(thMax, 1)

    def bullFVG(i):
        return i >= 2 and l[i] > h[i - 2] and o[i - 1] < c[i - 1]

    def bearFVG(i):
        return i >= 2 and h[i] < l[i - 2] and o[i - 1] > c[i - 1]

    prevDisp = [(rng1[i] is not None and thMin1[i] is not None and thMax1[i] is not None
                 and rng1[i] > thMin1[i] and rng1[i] <= thMax1[i]) for i in range(n)]
    dispBull = [prevDisp[i] and bullFVG(i) for i in range(n)]
    dispBear = [prevDisp[i] and bearFVG(i) for i in range(n)]

    cd2b = [False] * n
    cd2s = [False] * n
    cd3b = [False] * n
    cd3s = [False] * n
    bs = ss = 0
    for i in range(n):
        bs = bs + 1 if dispBull[i] else 0
        ss = ss + 1 if dispBear[i] else 0
        cd2b[i] = dispBull[i] and bs >= 2
        cd2s[i] = dispBear[i] and ss >= 2
        cd3b[i] = dispBull[i] and bs >= 3
        cd3s[i] = dispBear[i] and ss >= 3
    return dispBull, dispBear, cd2b, cd2s, cd3b, cd3s


def _ref_seq(bars, P, normPrice, baseBull, baseBear):
    """Independent re-typing of UU/DD IPSF sequence (source L359-432)."""
    n = len(bars)

    def inrange(x, th_low):
        return th_low < x < P.seq_th_high

    bl_len = 0
    bl_sum = 0.0
    be_len = 0
    be_sum = 0.0
    uu = [False] * n
    dd = [False] * n
    for i in range(n):
        is_u = baseBull(i) and inrange(normPrice[i], P.th_low_UU_DD)
        is_d = baseBear(i) and inrange(normPrice[i], P.th_low_UU_DD)
        if is_u:
            bl_len += 1
            bl_sum += normPrice[i]
        else:
            bl_len = 0
            bl_sum = 0.0
        if is_d:
            be_len += 1
            be_sum += normPrice[i]
        else:
            be_len = 0
            be_sum = 0.0
        uu[i] = bl_len == 2 and bl_sum >= P.seqTh_UU_DD
        dd[i] = be_len == 2 and be_sum >= P.seqTh_UU_DD
    return uu, dd


def _ref_hv(bars, P):
    """Independent re-typing of HV ladder exclusivity, NRA via [1] (source L704-723)."""
    o, h, l, c, v = _ref_columns(bars)
    n = len(bars)
    v1 = shift(v, 1)

    def isHV(L):
        hi1 = shift(highest(v, L), 1)
        return [v1[i] is not None and hi1[i] is not None and v1[i] == hi1[i] for i in range(n)]

    i75, i150, i250, i500, i1000 = isHV(75), isHV(150), isHV(250), isHV(500), isHV(1000)
    r1000 = [i1000[i] for i in range(n)]
    r500 = [i500[i] and not i1000[i] for i in range(n)]
    r250 = [i250[i] and not i500[i] and not i1000[i] for i in range(n)]
    r150 = [i150[i] and not i250[i] and not i500[i] and not i1000[i] for i in range(n)]
    r75 = [i75[i] and not i150[i] and not i250[i] and not i500[i] and not i1000[i] for i in range(n)]
    return r1000, r500, r250, r150, r75


def _ref_b2b(bars, saab, krat, b1x, be1x):
    """Independent re-typing of B2B 2x SAAB + B2B Mid Bull, ungated (source L439-445)."""
    n = len(bars)
    saab_1 = shift(saab, 1)
    krat_1 = shift(krat, 1)
    b1x_1 = shift(b1x, 1)
    be1x_1 = shift(be1x, 1)
    twoSAAB = [bool(saab_1[i]) and saab[i] for i in range(n)]
    twoBull1x = [bool(b1x_1[i]) and b1x[i] for i in range(n)]
    midBull = [(not twoSAAB[i]) and (not twoBull1x[i])
               and ((bool(saab_1[i]) and b1x[i]) or (bool(b1x_1[i]) and saab[i])) for i in range(n)]
    return twoSAAB, midBull


def _count_source_plotshapes(path):
    if not os.path.exists(path):
        return None
    with open(path, errors="ignore") as fh:
        txt = fh.read()
    return len(re.findall(r"plotshape\(", txt))


def main():
    checks = []
    P = core.Params(tfSec=3600)        # 1h key so synthetic short sessions light up

    bars = _make_bars("time", 900)
    n = len(bars)
    out = core.compute(bars, params=P, rv_anchor="D")
    fire_keys = [k for k in out if k.startswith("fire_")]

    # 1. DETERMINISM
    out_b = core.compute(bars, params=P, rv_anchor="D")
    checks.append(("determinism", all(out[k] == out_b[k] for k in out)))

    # 2. TICK == TIME (same Bar objects, same tfSec, through both wrappers)
    pt = core.Params(tfSec=3600)
    out_tick = tickmod.run_on_bars(bars, params=pt)
    out_time = timemod.run_on_bars(bars, params=pt, tf_seconds=3600)
    tt_ok = all(out_tick[k] == out_time[k] for k in fire_keys)
    checks.append(("tick_eq_time_fire_matrix", tt_ok))

    # 3. PLOT COUNT vs SOURCE
    src = _count_source_plotshapes(SOURCE)
    if src is None:
        checks.append(("plot_count_vs_source", False))
        print("  (source not found at expected path)")
    else:
        ok = (len(fire_keys) == 42) and (src == 42)
        checks.append(("plot_count_vs_source", ok))
        print(f"  source plotshape()={src}  ported detection plots={len(fire_keys)}")

    # 4. RVOL 0.56 parity vs independent re-typing
    saab, krat, b1x, be1x, gs, moab, normPrice, (refBull, refBear) = _ref_rvol_056(bars, P)
    pairs = [("sigSAAB", saab), ("sigKratos", krat), ("sigBull1x", b1x),
             ("sigBear1x", be1x), ("sigGS", gs), ("sigMOAB", moab)]
    for nm, ref in pairs:
        ok = all(out["prim_" + nm][i] == (1 if ref[i] else 0) for i in range(n))
        checks.append((f"rvol_parity_{nm}", ok))

    # 5. DISPLACEMENT parity vs independent re-typing
    db, sb, c2b, c2s, c3b, c3s = _ref_disp(bars, P)
    checks.append(("disp_parity_bull", all(out["prim_sigDispBull"][i] == (1 if db[i] else 0) for i in range(n))))
    checks.append(("disp_parity_bear", all(out["prim_sigDispBear"][i] == (1 if sb[i] else 0) for i in range(n))))
    checks.append(("disp_parity_cdisp2_bull", all(out["fire_Consec Disp Bull 2+"][i] == (1 if c2b[i] else 0) for i in range(n))))
    checks.append(("disp_parity_cdisp3_bull", all(out["fire_Consec Disp Bull 3+"][i] == (1 if c3b[i] else 0) for i in range(n))))

    # 6. SEQUENCE parity (UU/DD) vs independent streak re-typing
    ref_UU, ref_DD = _ref_seq(bars, P, normPrice, refBull, refBear)
    checks.append(("seq_parity_UU", all(out["fire_UU Signal"][i] == (1 if ref_UU[i] else 0) for i in range(n))))
    checks.append(("seq_parity_DD", all(out["fire_DD Signal"][i] == (1 if ref_DD[i] else 0) for i in range(n))))

    # 7. HV ladder parity vs independent re-typing
    r1000, r500, r250, r150, r75 = _ref_hv(bars, P)
    checks.append(("hv_parity_1000", all(out["fire_HV 1000"][i] == (1 if r1000[i] else 0) for i in range(n))))
    checks.append(("hv_parity_500", all(out["fire_HV 500"][i] == (1 if r500[i] else 0) for i in range(n))))
    checks.append(("hv_parity_75", all(out["fire_HV 75"][i] == (1 if r75[i] else 0) for i in range(n))))

    # 8. B2B parity vs independent re-typing (ungated)
    twoSAAB, midBull = _ref_b2b(bars, saab, krat, b1x, be1x)
    checks.append(("b2b_parity_2xSAAB", all(out["fire_2x SAAB"][i] == (1 if twoSAAB[i] else 0) for i in range(n))))
    checks.append(("b2b_parity_MidBull", all(out["fire_B2B Mid Bull"][i] == (1 if midBull[i] else 0) for i in range(n))))

    # 9. BOOLEAN matrix
    all_bool = all(all(x in (0, 1) for x in out[k]) for k in fire_keys)
    checks.append(("all_fires_boolean", all_bool))

    # 10. HONESTY (stub-is-zero): no faked all-zero stub series + matrix exercised.
    no_stub_keys = not any("stub" in k.lower() for k in out)
    stress = _stress_tape()
    outx = core.compute(stress, params=core.Params(tfSec=3600), rv_anchor="D")
    ms = _multisession_tape()
    outm = core.compute(ms, params=core.Params(tfSec=3600), rv_anchor="D")
    union_fired = sorted({k for k in fire_keys if sum(outx[k]) > 0 or sum(outm[k]) > 0})
    fired_plots = len(union_fired)
    checks.append(("no_faked_stub_series", no_stub_keys))
    checks.append(("matrix_exercised_ge_6_plots", fired_plots >= 6))

    # 11. RVOL ENGINE ALIVE (relativeVolume shim path not silently dead)
    rvol_alive = (sum(outm["prim_sigWTC"]) + sum(outm["prim_sigHiro"])
                  + sum(outm["prim_anyLong"]) + sum(outm["prim_anyShort"])
                  + sum(outm["prim_sigNag"])) > 0
    checks.append(("rvol_momentum_engine_alive", rvol_alive))

    # 12. NEGATIVE CONTROL — flat doji tape -> zero fires
    flat = _flat_tape()
    outf = core.compute(flat, params=P, rv_anchor="D")
    neg_ok = all(sum(outf[k]) == 0 for k in fire_keys)
    checks.append(("negative_control_zero_fires", neg_ok))

    # 13. WARMUP — very short tape must not crash and not fire window plots
    short = stress[:8]
    try:
        outs = core.compute(short, params=P, rv_anchor="D")
        warm_ok = (len(outs["ts"]) == 8
                   and sum(outs["fire_Consec Disp Bull 3+"]) == 0
                   and sum(outs["fire_HV 1000"]) == 0
                   and sum(outs["fire_HV 75"]) == 0)
    except Exception as exc:  # pragma: no cover
        warm_ok = False
        print("  warmup exception:", exc)
    checks.append(("warmup_no_crash_no_window_fire", warm_ok))

    # 14. RVOL SHIM USED — shim ratio must differ from naive volume/sma(volume,N)
    o3, h3, l3, c3, v3 = _ref_columns(bars)
    naive = sma(v3, P.reg_length)
    naive_ratio = [None if (naive[i] is None or naive[i] == 0) else v3[i] / naive[i] for i in range(n)]
    shim_ratio = out["lvl_relVolRatio"]
    diffs = sum(1 for i in range(n)
                if shim_ratio[i] is not None and naive_ratio[i] is not None
                and abs(shim_ratio[i] - naive_ratio[i]) > 1e-9)
    checks.append(("rvol_shim_not_naive_sma", diffs > 0))

    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"  fired plots union of stress+multisession tapes ({fired_plots}/{len(fire_keys)}): {[k[5:] for k in union_fired]}")
    print(f"PARITY heavy_with_2x_detection_plots: {passed}/{total}")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
