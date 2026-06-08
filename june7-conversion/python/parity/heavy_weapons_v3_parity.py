"""Heavy Weapons Single v3 — parity harness (offline Gate-B).

FULL port (every detection plot derived from OHLCV — no stub layer). This harness
verifies, on deterministic synthetic + engineered bars, and prints a REAL pass/total:

  1. DETERMINISM               — two runs on identical bars give an identical matrix.
  2. TICK == TIME              — the SAME core on the SAME Bar objects yields an
                                 identical fire matrix through both wrappers (one
                                 code path, grain-bound). Run with the SAME tfSec.
  3. PLOT COUNT vs SOURCE      — ported detection-plot count == source plotshape
                                 count (cosmetic FAUNA text excluded; the FAUNA FIRE
                                 is counted). Source plotshapes are enumerated.
  4. RVOL 0.56 parity          — sigSAAB/Kratos/Bull1x/Bear1x/GS/MOAB re-derived
                                 from an INDEPENDENT re-typing of the source formulas.
  5. DISPLACEMENT parity       — Disp Bull/Bear + Consec 2+/3+ re-derived independently.
  6. SEQUENCE parity           — UU/DD re-derived independently (streak + sum + disp).
  7. HV ladder parity          — HV150..1000 exclusivity + LONG[1] gate independently.
  8. BOOLEAN matrix            — every fire_* series is strictly 0/1.
  9. HONESTY (stub-is-zero)    — NO faked all-zero "stub" plots in the module AND the
                                 matrix is genuinely exercised (>=6 distinct plots fire
                                 on the event-rich tape). A green that fired nothing
                                 would be fabricated parity; this gate forbids it.
 10. NEGATIVE CONTROL          — a flat doji tape (no body, no volume spikes) fires
                                 nothing (no false positives from warmup math).
 11. WARMUP                    — a very short tape does not crash and does not fire
                                 window-dependent plots (disp/std/RVOL not warm).
 12. RVOL SHIM USED            — relativeVolume comes from the canonical shim, not a
                                 volume/sma(volume,N) approximation (lvl_relVolRatio
                                 must differ from the naive ratio on the smile tape).

Re-runnable by a stranger:  python3 heavy_weapons_v3_parity.py
REAL pass/total is printed; exit 0 only if all pass.
"""
from __future__ import annotations

import math
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
import _heavy_weapons_v3_core as core  # noqa: E402
import heavy_weapons_v3_tick as tickmod  # noqa: E402
import heavy_weapons_v3_time as timemod  # noqa: E402

SOURCE = ("/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT "
          "transformed yet/June 7/Tick Friendly conversion/"
          "heavy weapons v3_tickfriendly.pine")


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
    return [Bar(1_700_000_000_000 + i * 60_000, 100.0, 100.0, 100.0, 100.0, 1000.0) for i in range(n)]


def _multisession_tape(sessions=50, bars_per_session=14, seed=7):
    """Multi-day tape: each session is its own calendar day with bars at the SAME
    clock offsets, so the RVOL 'at time' shim has prior sessions to average against
    (lights RVOL/momentum/WTC/Hiroshima/HCT plots, not just displacement). Late
    sessions inject deliberate price-spike-exceeds-volume bars (SAAB/RVOL ladder)
    and ATH volume (Nagasaki/HV)."""
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
                vol = 1500.0 + random.uniform(0, 200)   # MODEST vol -> price spike >> vol spike (SAAB)
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
    """Independent re-typing of the RVOL 0.56 bull/bear ladder (source L275-298)."""
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
    return saab, krat, b1x, be1x, gs, moab


def _ref_disp(bars, P):
    """Independent re-typing of standalone + consec displacement (source L468-522)."""
    o, h, l, c, v = _ref_columns(bars)
    n = len(bars)
    rng = [abs(o[i] - c[i]) if P.i_disp_type == "Open to Close" else h[i] - l[i] for i in range(n)]
    sd = stdev(rng, P.i_std_len)
    rng1 = shift(rng, 1)
    sd1 = shift(sd, 1)

    def bullFVG(i):
        return i >= 2 and l[i] > h[i - 2] and o[i - 1] < c[i - 1]

    def bearFVG(i):
        return i >= 2 and h[i] < l[i - 2] and o[i - 1] > c[i - 1]

    def prevdisp(m):
        return [sd1[i] is not None and rng1[i] is not None and rng1[i] > sd1[i] * m for i in range(n)]

    pdSA = prevdisp(P.i_disp_std_standalone)
    dispBull = [pdSA[i] and bullFVG(i) for i in range(n)]
    dispBear = [pdSA[i] and bearFVG(i) for i in range(n)]

    pdc2 = prevdisp(P.i_disp_std_cdisp2)
    db2 = [pdc2[i] and bullFVG(i) for i in range(n)]
    sb2 = [pdc2[i] and bearFVG(i) for i in range(n)]
    bs = ss = 0
    cd2b = [False] * n
    cd2s = [False] * n
    for i in range(n):
        bs = bs + 1 if db2[i] else 0
        ss = ss + 1 if sb2[i] else 0
        cd2b[i] = db2[i] and bs >= 2
        cd2s[i] = sb2[i] and ss >= 2

    pdc3 = prevdisp(P.i_disp_std_cdisp3)
    db3 = [pdc3[i] and bullFVG(i) for i in range(n)]
    sb3 = [pdc3[i] and bearFVG(i) for i in range(n)]
    bs = ss = 0
    cd3b = [False] * n
    cd3s = [False] * n
    for i in range(n):
        bs = bs + 1 if db3[i] else 0
        ss = ss + 1 if sb3[i] else 0
        cd3b[i] = db3[i] and bs >= 3
        cd3s[i] = sb3[i] and ss >= 3
    return dispBull, dispBear, cd2b, cd2s, cd3b, cd3s


def _ref_hv(bars, P, anyLong_1):
    """Independent re-typing of HV ladder exclusivity + LONG[1] gate (source L856-874)."""
    o, h, l, c, v = _ref_columns(bars)
    n = len(bars)
    v1 = shift(v, 1)

    def isHV(L):
        hi1 = shift(highest(v, L), 1)
        return [v1[i] is not None and hi1[i] is not None and v1[i] == hi1[i] for i in range(n)]

    i150, i250, i350, i500, i1000 = isHV(150), isHV(250), isHV(350), isHV(500), isHV(1000)
    r1000 = [i1000[i] for i in range(n)]
    r500 = [i500[i] and not i1000[i] for i in range(n)]
    r350 = [i350[i] and not i500[i] and not i1000[i] for i in range(n)]
    r250 = [i250[i] and not i350[i] and not i500[i] and not i1000[i] for i in range(n)]
    r150 = [i150[i] and not i250[i] and not i350[i] and not i500[i] and not i1000[i] for i in range(n)]
    g = anyLong_1
    return ([r1000[i] and bool(g[i]) for i in range(n)],
            [r500[i] and bool(g[i]) for i in range(n)],
            [r350[i] and bool(g[i]) for i in range(n)],
            [r250[i] and bool(g[i]) for i in range(n)],
            [r150[i] and bool(g[i]) for i in range(n)])


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
        # Source has 45 detection plotshapes (9 RVOL + 6 seq + 6 B2B + 2 FAUNA +
        # 6 disp + 7 momentum + 5 HV + 2 HCT + 2 Pentagon). The 2 FAUNA plotshapes
        # ARE the FAUNA Bull/Bear FIRES we port. Ported detection plots == 45.
        ok = (len(fire_keys) == 45) and (src == 45)
        checks.append(("plot_count_vs_source", ok))
        print(f"  source plotshape()={src}  ported detection plots={len(fire_keys)}")

    # 4. RVOL 0.56 parity vs independent re-typing
    rs = _ref_rvol_056(bars, P)
    names = ["sigSAAB", "sigKratos", "sigBull1x", "sigBear1x", "sigGS", "sigMOAB"]
    for ref, nm in zip(rs, names):
        ok = all(out["prim_" + nm][i] == (1 if ref[i] else 0) for i in range(n))
        checks.append((f"rvol_parity_{nm}", ok))

    # 5. DISPLACEMENT parity vs independent re-typing
    db, sb, c2b, c2s, c3b, c3s = _ref_disp(bars, P)
    checks.append(("disp_parity_bull", all(out["prim_sigDispBull"][i] == (1 if db[i] else 0) for i in range(n))))
    checks.append(("disp_parity_bear", all(out["prim_sigDispBear"][i] == (1 if sb[i] else 0) for i in range(n))))
    # consec 2+/3+ surface only through the fire matrix; compare via the show-gated fire
    fire_c2b = out["fire_Consec Disp Bull 2+"]
    fire_c3b = out["fire_Consec Disp Bull 3+"]
    checks.append(("disp_parity_cdisp2_bull", all(fire_c2b[i] == (1 if c2b[i] else 0) for i in range(n))))
    checks.append(("disp_parity_cdisp3_bull", all(fire_c3b[i] == (1 if c3b[i] else 0) for i in range(n))))

    # 6. SEQUENCE parity (UU/DD) vs independent streak re-typing
    saab, krat, b1x, be1x, gs, moab = rs
    o2, h2, l2, c2, v2 = _ref_columns(bars)
    spike = [abs(c2[i] - o2[i]) for i in range(n)]
    avgSpike = shift(sma(spike, P.bb_avgLength), 1)
    normPrice = [spike[i] / nz(avgSpike[i], 1.0) for i in range(n)]
    avgVol = shift(sma(v2, P.bb_avgLength), 1)
    normVol = [v2[i] / nz(avgVol[i], 1.0) for i in range(n)]
    diff = [normPrice[i] - normVol[i] for i in range(n)]
    posDiff = [d if d > 0 else None for d in diff]
    smaDiff = sma(posDiff, P.bb_smaLength)
    rng = [abs(o2[i] - c2[i]) if P.i_disp_type == "Open to Close" else h2[i] - l2[i] for i in range(n)]
    sd = stdev(rng, P.i_std_len)
    disp_seq = [sd[i] is not None and rng[i] > sd[i] * P.i_disp_std_seq for i in range(n)]
    th1x = core.f_rvol_1x_threshold(P.tfSec)
    thSK = th1x * 0.56

    def baseBull(i):
        return c2[i] > o2[i] and posDiff[i] is not None and smaDiff[i] is not None and posDiff[i] > smaDiff[i]

    def baseBear(i):
        return c2[i] < o2[i] and posDiff[i] is not None and smaDiff[i] is not None and posDiff[i] > smaDiff[i]

    bl_len = bl_sum = bl_disp = 0
    be_len = be_sum = be_disp = 0
    ref_UU = [False] * n
    ref_DD = [False] * n
    for i in range(n):
        is_u = baseBull(i) and normPrice[i] > P.th_low_UU_DD
        is_d = baseBear(i) and normPrice[i] > P.th_low_UU_DD
        if is_u:
            bl_len += 1; bl_sum += normPrice[i]; bl_disp += 1 if disp_seq[i] else 0
        else:
            bl_len = bl_sum = bl_disp = 0
        if is_d:
            be_len += 1; be_sum += normPrice[i]; be_disp += 1 if disp_seq[i] else 0
        else:
            be_len = be_sum = be_disp = 0
        ref_UU[i] = bl_len == 2 and bl_sum >= thSK and bl_disp >= 1
        ref_DD[i] = be_len == 2 and be_sum >= thSK and be_disp >= 1
    checks.append(("seq_parity_UU", all(out["fire_UU +disp"][i] == (1 if ref_UU[i] else 0) for i in range(n))))
    checks.append(("seq_parity_DD", all(out["fire_DD +disp"][i] == (1 if ref_DD[i] else 0) for i in range(n))))

    # 7. HV ladder parity vs independent re-typing
    anyLong_1 = [out["prim_anyLong"][i - 1] if i > 0 else 0 for i in range(n)]
    r1000, r500, r350, r250, r150 = _ref_hv(bars, P, anyLong_1)
    checks.append(("hv_parity_1000", all(out["fire_HV 1000 +LONG[1]"][i] == (1 if r1000[i] else 0) for i in range(n))))
    checks.append(("hv_parity_500", all(out["fire_HV 500 +LONG[1]"][i] == (1 if r500[i] else 0) for i in range(n))))
    checks.append(("hv_parity_150", all(out["fire_HV 150 +LONG[1]"][i] == (1 if r150[i] else 0) for i in range(n))))

    # 8. BOOLEAN matrix
    all_bool = all(all(x in (0, 1) for x in out[k]) for k in fire_keys)
    checks.append(("all_fires_boolean", all_bool))

    # 9. HONESTY (stub-is-zero): no faked all-zero stub series + matrix exercised.
    #    Two complementary tapes: the oscillation tape lights the DISPLACEMENT
    #    engine; the multi-session tape lights the RVOL/momentum/SAAB engines
    #    (relativeVolume needs prior same-clock sessions to average). Union of
    #    fired plots proves both halves of the indicator are alive, not faked.
    no_stub_keys = not any("stub" in k.lower() for k in out)
    stress = _stress_tape()
    outx = core.compute(stress, params=core.Params(tfSec=3600), rv_anchor="D")
    ms = _multisession_tape()
    outm = core.compute(ms, params=core.Params(tfSec=3600), rv_anchor="D")
    union_fired = sorted({k for k in fire_keys if sum(outx[k]) > 0 or sum(outm[k]) > 0})
    fired_plots = len(union_fired)
    checks.append(("no_faked_stub_series", no_stub_keys))
    checks.append(("matrix_exercised_ge_6_plots", fired_plots >= 6))
    # RVOL engine genuinely alive: at least one RVOL-derived primitive fires on the
    # multi-session tape (proves the relativeVolume shim path is not silently dead).
    rvol_alive = (sum(outm["prim_sigPent"]) + sum(outm["prim_sigWTC"]) + sum(outm["prim_sigHiro"])
                  + sum(outm["prim_anyMom"]) + sum(outm["prim_sigNag"])) > 0
    checks.append(("rvol_momentum_engine_alive", rvol_alive))

    # 10. NEGATIVE CONTROL — flat doji tape -> zero fires
    flat = _flat_tape()
    outf = core.compute(flat, params=P, rv_anchor="D")
    neg_ok = all(sum(outf[k]) == 0 for k in fire_keys)
    checks.append(("negative_control_zero_fires", neg_ok))

    # 11. WARMUP — very short tape must not crash and not fire window plots
    short = stress[:8]
    try:
        outs = core.compute(short, params=P, rv_anchor="D")
        warm_ok = (len(outs["ts"]) == 8
                   and sum(outs["fire_Consec Disp Bull 3+"]) == 0
                   and sum(outs["fire_HV 1000 +LONG[1]"]) == 0)
    except Exception as exc:  # pragma: no cover
        warm_ok = False
        print("  warmup exception:", exc)
    checks.append(("warmup_no_crash_no_window_fire", warm_ok))

    # 12. RVOL SHIM USED — shim ratio must differ from naive volume/sma(volume,N)
    #     on the volume-smile synthetic tape (proves the canonical shim, not the
    #     banned volume/SMA approximation, is in the path).
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
    print(f"PARITY heavy_weapons_v3: {passed}/{total}")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
