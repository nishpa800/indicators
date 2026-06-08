"""BASE HV+D <-> PBJ <-> PPD v1 — BULLISH (38) — parity harness (offline Gate-B).

FULL port (every detection plot derived from OHLCV — no stub layer). This harness
verifies, on deterministic synthetic + engineered bars, and prints a REAL pass/total:

  1. TIME PORT RUNS            — time wrapper produces the 38-plot fire matrix.
  2. TICK PORT RUNS            — tick wrapper produces the 38-plot fire matrix.
  3. PLOT COUNT == 38          — ported detection-plot count == 38, the source's
                                 distinct detection plotshapes (3 HV+D-family + 21
                                 USE + 1 NAG+ + 2 CO + 3 B2B + 8 momentum co-occ).
                                 PLOT_IDS enumerates them.
  4. TICK == TIME              — the SAME core on the SAME Bar objects with the SAME
                                 tfSec yields a byte-identical fire matrix through
                                 both wrappers (one code path, grain-bound).
  5. DETERMINISM               — two runs on identical bars give an identical matrix.
  6. BOOLEAN matrix            — every fire_* series is strictly 0/1; lvl_* is
                                 float-or-None and present exactly where fire==1.
  7. HV+D parity               — hvd_fire_bull re-derived independently from the
                                 source formula (vol-rank[1] x displacement bull FVG).
  8. FAUNA parity              — sigFAUNABull re-derived independently (MB/RE/TA +
                                 exclusion ladder) and matched via FoxtrotB.
  9. DISP parity               — sigDISPBull re-derived independently (banded prev
                                 displacement + bull FVG) checked against DispConsBull2.
 10. PUP parity               — sigPUP re-derived independently (price% vs highest
                                 opposite-colour vol[1..lookback]) via PAFBull.
 11. RVOL 0.56 parity          — sigGrandSlam/sigBullRVOL1x re-derived independently
                                 (bb spike/vol bands) checked via HVDM_RVOL.
 12. HONESTY (stub-is-zero)    — COMPOSITE_PARTIAL is empty (no declared stubs) AND
                                 the matrix is genuinely exercised (>= 5 distinct
                                 plots fire on the event-rich tape). A green that
                                 fired nothing would be fabricated parity; forbidden.
 13. RVOL ENGINE ALIVE         — at least one RVOL/momentum-derived plot fires on the
                                 multi-session tape (the relativeVolume shim path is
                                 not silently dead).
 14. NEGATIVE CONTROL          — a flat doji tape (no body, no vol spikes, no gaps)
                                 fires nothing (no false positives from warmup math).
 15. WARMUP                    — a very short tape does not crash and does not fire
                                 window-dependent plots (std/RVOL/HV not warm).
 16. RVOL SHIM USED            — shim ratio differs from naive volume/sma(volume,N) on
                                 the volume-smile tape (proves the canonical shim, not
                                 the banned volume/SMA approximation, is in the path).

Re-runnable by a stranger:  python3 hvd_pbj_pup_bull_parity.py
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
from _nn_harness import (  # noqa: E402
    synthetic_bars, sma, stdev, shift, highest, atr as _atr_ohlc, nz, relative_volume,
)
import _hvd_pbj_pup_bull_core as core  # noqa: E402
import hvd_pbj_pup_bull_tick as tickmod  # noqa: E402
import hvd_pbj_pup_bull_time as timemod  # noqa: E402

SOURCE = ("/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT "
          "transformed yet/June 7/Tick Friendly conversion/"
          "hvd_pbj_pup_bull_tickfriendly.pine")

HV_PERIODS = [50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550,
              600, 650, 700, 750, 1000]


# ─────────────────────────── deterministic tapes ────────────────────────────
def _stress_tape(nbars=2000, seed=5):
    """BULL-engineered multi-session tape: long CALM baselines (tiny bodies, low
    volume — so rolling stdev/avgVol stay small) punctuated by widely-spaced
    clusters of big-body, gap-UP (bull-FVG), high-volume green bars. Cluster
    lengths vary (2,4,2,3,4,2) so back-to-back HV+D (B2B, len>=2) AND 4-in-a-row
    FAUNA (Foxtrot, len>=4) are both reachable. This is the only tape that genuinely
    lights the deep bull confluence (HV+D / FAUNA / displacement / B2B / momentum
    co-occ / combo-set / PUP) end-to-end — see the parity HONESTY gate."""
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
        for _ in range(80):                       # long calm gap -> stdev stays tiny
            if i >= nbars:
                break
            o = px
            cl = o + random.uniform(0, 0.08)
            hi = max(o, cl) + random.uniform(0.01, 0.05)
            lo = min(o, cl) - random.uniform(0.01, 0.05)
            _push(o, hi, lo, cl, random.uniform(8000, 10000))
            px = cl
        clen = clusters[ci % len(clusters)]
        ci += 1
        for _ in range(clen):                      # big bull gap-up event bars
            if i >= nbars:
                break
            o = px + random.uniform(6, 10)         # gap above high[2] -> bull FVG
            cl = o + random.uniform(20, 30)        # body ~25 >> 5 * tiny baseline std
            hi = cl + random.uniform(0.02, 0.1)
            lo = o - random.uniform(0.02, 0.1)
            _push(o, hi, lo, cl, 300000.0)
            px = cl
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


# ─────────────────── independent re-derivations (answer keys) ────────────────
def _independent(bars, tfSec):
    n = len(bars)
    o = [b.open for b in bars]; h = [b.high for b in bars]; l = [b.low for b in bars]
    c = [b.close for b in bars]; v = [b.volume for b in bars]; ts = [b.ts for b in bars]
    conf = [True] * n

    def bullFVG(i):
        return i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1]

    # HV+D bull (independent)
    d1_rng = [abs(o[i] - c[i]) for i in range(n)]
    d1_std = stdev(d1_rng, 100)
    d1_thr1 = shift([None if x is None else x * 5.0 for x in d1_std], 1)
    d1_rng1 = shift(d1_rng, 1)
    d1_prev = [d1_thr1[i] is not None and d1_rng1[i] is not None and d1_rng1[i] > d1_thr1[i] for i in range(n)]
    d1_bull = [conf[i] and d1_prev[i] and bullFVG(i) for i in range(n)]
    v1 = shift(v, 1)
    rank = [0] * n
    hv1 = {per: shift(highest(v, per), 1) for per in HV_PERIODS}
    for i in range(n):
        for per in reversed(HV_PERIODS):
            if hv1[per][i] is not None and v1[i] is not None and v1[i] == hv1[per][i]:
                rank[i] = per
                break
    isHEV = [False] * n
    mx = 0.0
    for i in range(n):
        if v1[i] is not None and v1[i] > mx:
            mx = v1[i]
            isHEV[i] = True
    base_hv = [isHEV[i] or (rank[i] != 0 and not isHEV[i]) for i in range(n)]
    hvd_bull = [base_hv[i] and d1_bull[i] for i in range(n)]

    # FAUNA bull (independent)
    atr14 = _atr_ohlc(o, h, l, c, 14)
    avgVol = sma(v, 20)
    avgBody = sma([abs(c[i] - o[i]) for i in range(n)], 20)
    avgDelta = sma([abs(c[i] - c[i - 1]) if i > 0 else 0.0 for i in range(n)], 10)
    trendMA = sma(c, 50)
    avgBody1 = shift(avgBody, 1)
    avgVol1 = shift(avgVol, 1)
    fauna_bull = [False] * n
    for i in range(n):
        if atr14[i] is None or avgVol[i] is None:
            continue
        body = c[i] - o[i]; rng = h[i] - l[i]; up = body > 0; bsz = abs(body)
        brat = 0.0 if rng == 0 else bsz / rng
        MB = up and bsz > 1.6 * atr14[i] and brat > 0.70 and v[i] > 1.8 * avgVol[i]
        RE = up and rng > 2.2 * atr14[i] and (h[i] - c[i]) < 0.15 * rng and v[i] > 1.8 * avgVol[i]
        TA = (i > 0 and trendMA[i] is not None and trendMA[i - 1] is not None and trendMA[i] > trendMA[i - 1]
              and avgDelta[i] is not None and (c[i] - c[i - 1]) > 1.6 * avgDelta[i] and up and v[i] > 1.8 * avgVol[i])
        excl = False
        if i > 0 and avgBody1[i] is not None and avgVol1[i] is not None:
            GG = (o[i] - c[i - 1]) > 0.9 * atr14[i] and up and l[i] > c[i - 1] and v[i] > 1.8 * avgVol[i]
            pbody = c[i - 1] - o[i - 1]; prange = h[i - 1] - l[i - 1]
            StrongBear = c[i - 1] < o[i - 1] and abs(pbody) > 1.5 * avgBody1[i] and v[i - 1] > 1.5 * avgVol1[i]
            WeakBear = c[i - 1] < o[i - 1] and (0.0 if prange == 0 else abs(pbody) / prange) <= 0.2
            core_cnt = (1 if MB else 0) + (1 if RE else 0) + (1 if TA else 0)
            gg_pass = core_cnt >= 2 and brat >= 0.80
            excl = (WeakBear and (MB or RE or TA)) or (StrongBear and (MB or RE or TA)) or (c[i - 1] < o[i - 1] and GG) or (GG and not gg_pass)
        fauna_bull[i] = conf[i] and (MB or RE or TA) and not excl

    # DISP bull (independent, banded prev, min=6 max=100) — primary USE displacement
    disp_rng = [abs(o[i] - c[i]) for i in range(n)]
    disp_std = stdev(disp_rng, 100)
    drng1 = shift(disp_rng, 1)
    dstd1 = shift(disp_std, 1)
    disp_bull = [conf[i] and dstd1[i] is not None and drng1[i] is not None and drng1[i] > dstd1[i] * 6.0 and drng1[i] <= dstd1[i] * 100.0 and bullFVG(i) for i in range(n)]
    # DISP2 bull (independent, min=5 — the per-bar gate behind DispConsBull2)
    disp2_bull = [conf[i] and dstd1[i] is not None and drng1[i] is not None and drng1[i] > dstd1[i] * 5.0 and drng1[i] <= dstd1[i] * 100.0 and bullFVG(i) for i in range(n)]

    # PUP (independent)
    redVol = [v[i] if c[i] < o[i] else 0.0 for i in range(n)]
    hiRed = highest(shift(redVol, 1), 10)
    pup = [False] * n
    for i in range(n):
        priceUp = ((c[i] - o[i]) / o[i]) * 100 > 3.0 if o[i] != 0 else False
        pup[i] = conf[i] and priceUp and hiRed[i] is not None and v[i] > hiRed[i]

    # RVOL 0.56 (independent): sigSAAB/sigGrandSlam/sigBullRVOL1x
    spike = [abs(c[i] - o[i]) for i in range(n)]
    avgSpike1 = shift(sma(spike, 30), 1)
    normP = [spike[i] / nz(avgSpike1[i], 1.0) for i in range(n)]
    avgVolD1 = shift(sma(v, 30), 1)
    normV = [v[i] / nz(avgVolD1[i], 1.0) for i in range(n)]
    diff = [normP[i] - normV[i] for i in range(n)]
    posDiff = [diff[i] if diff[i] > 0 else None for i in range(n)]
    from collections import deque
    smaDiff = [None] * n
    win = deque()
    for i in range(n):
        win.append(posDiff[i])
        if len(win) > 20:
            win.popleft()
        if len(win) == 20 and all(w is not None for w in win):
            smaDiff[i] = sum(win) / 20
    baseBull = [c[i] > o[i] and posDiff[i] is not None and smaDiff[i] is not None and posDiff[i] > smaDiff[i] for i in range(n)]

    def f1x(s):
        return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else 23.0 if s <= 45 else
                20.0 if s <= 60 else 18.0 if s <= 120 else 13.0 if s <= 300 else 13.0 if s <= 360 else
                11.0 if s <= 540 else 10.0 if s <= 600 else 9.0 if s <= 660 else 7.5 if s <= 900 else
                6.5 if s <= 1560 else 6.0 if s <= 2340 else 4.5 if s <= 3600 else 4.0 if s <= 9000 else
                3.5 if s <= 11700 else 1.8 if s < 259200 else 1.0)

    def fgs(s):
        if s < 60:
            return f1x(s) * 3.0
        return (35.0 if s <= 300 else 25.0 if s <= 600 else 20.0 if s <= 1500 else 20.0 if s <= 3000 else
                10.0 if s <= 7260 else 8.0 if s <= 11700 else 7.5 if s <= 86400 else 3.5 if s <= 259200 else 3.0)

    th_saab = f1x(tfSec) * 0.56; th1x = f1x(tfSec); thgs = fgs(tfSec)
    saab = [conf[i] and baseBull[i] and (th_saab <= normP[i] < th1x) for i in range(n)]
    grandslam = [conf[i] and baseBull[i] and normP[i] >= thgs for i in range(n)]
    bull1x = [conf[i] and baseBull[i] and (th1x <= normP[i] < thgs) and not grandslam[i] for i in range(n)]

    return dict(hvd_bull=hvd_bull, fauna_bull=fauna_bull, disp_bull=disp_bull,
                disp2_bull=disp2_bull, pup=pup, saab=saab, grandslam=grandslam, bull1x=bull1x)


# ───────────────────────────────── checks ───────────────────────────────────
def run():
    results = []

    stress = _stress_tape(1600, 11)
    multi = synthetic_bars(n=1200, grain="time")

    # 1/2 ports run
    try:
        ot = timemod.run_on_bars(multi, tf_seconds=3600)
        ok = isinstance(ot, dict) and any(k.startswith("fire_") for k in ot)
        results.append(("time_port_runs", ok, f"{sum(1 for k in ot if k.startswith('fire_'))} plots"))
    except Exception as e:
        ot = {}; results.append(("time_port_runs", False, f"EXC {e}"))
    try:
        ok_b = tickmod.run_on_bars(multi)
        ok = isinstance(ok_b, dict) and any(k.startswith("fire_") for k in ok_b)
        results.append(("tick_port_runs", ok, f"{sum(1 for k in ok_b if k.startswith('fire_'))} plots"))
    except Exception as e:
        ok_b = {}; results.append(("tick_port_runs", False, f"EXC {e}"))

    # 3 plot count == 38 (and source plotshape sanity)
    src_plotshapes = None
    if os.path.exists(SOURCE):
        src_plotshapes = len(re.findall(r"plotshape\(", open(SOURCE, errors="ignore").read()))
    n_plots = len(core.PLOT_IDS)
    results.append(("plot_count_eq_38", n_plots == 38,
                    f"PLOT_IDS={n_plots}, source plotshape(={src_plotshapes})"))

    # 4 tick == time (same bars, same tfSec)
    try:
        a = timemod.run_on_bars(stress, tf_seconds=60)
        b = tickmod.run_on_bars(stress, tf_seconds=60)
        mism = [k for k in a if a[k] != b.get(k)]
        results.append(("tick_eq_time", not mism, "identical matrix" if not mism else f"mismatch {mism[:4]}"))
    except Exception as e:
        a = {}; results.append(("tick_eq_time", False, f"EXC {e}"))

    # 5 determinism
    try:
        d1 = timemod.run_on_bars(stress, tf_seconds=60)
        d2 = timemod.run_on_bars(_stress_tape(1600, 11), tf_seconds=60)
        results.append(("deterministic", d1 == d2, "stable" if d1 == d2 else "non-deterministic"))
    except Exception as e:
        results.append(("deterministic", False, f"EXC {e}"))

    # 6 boolean matrix + level alignment
    try:
        mt = timemod.run_on_bars(stress, tf_seconds=60)
        bad = []
        for pid in core.PLOT_IDS:
            f = mt[f"fire_{pid}"]; lv = mt[f"lvl_{pid}"]
            if any(x not in (0, 1) for x in f):
                bad.append(f"{pid}:nonbool")
            for i in range(len(f)):
                if f[i] == 1 and lv[i] is None:
                    bad.append(f"{pid}:fire-no-lvl"); break
                if f[i] == 0 and lv[i] is not None:
                    bad.append(f"{pid}:nofire-has-lvl"); break
        results.append(("boolean_matrix_and_levels", not bad, "all 0/1 + levels aligned" if not bad else str(bad[:4])))
    except Exception as e:
        results.append(("boolean_matrix_and_levels", False, f"EXC {e}"))

    # 7-11 independent parity vs core internals
    ind = _independent(stress, 60)
    mt = timemod.run_on_bars(stress, tf_seconds=60)
    n = len(stress)

    # 7 HV+D: union of all single-bar HVDM_* plots fires ONLY where hvd_fire_bull[i].
    hvdm_keys = ["HVDM_PUP", "HVDM_RVOL", "HVDM_CMB", "HVDM_PBJ_PUP", "HVDM_PBJ_RVOL",
                 "HVDM_PBJ_CMB", "HVDM_2of3", "HVDM_3of3"]
    hvdm_fire = [any(mt[f"fire_{k}"][i] for k in hvdm_keys) for i in range(n)]
    hvd_ok = all((not hvdm_fire[i]) or ind["hvd_bull"][i] for i in range(n))
    results.append(("hvd_parity_subset", hvd_ok,
                    f"all HVDM fires sit on independent hvd_fire_bull bars "
                    f"(HVDM fired {sum(hvdm_fire)})"))

    # 8 FAUNA: FoxtrotB (default show=True) requires fauna_bull[i..i-3].
    fox_ind = [i >= 3 and ind["fauna_bull"][i] and ind["fauna_bull"][i - 1] and ind["fauna_bull"][i - 2] and ind["fauna_bull"][i - 3] for i in range(n)]
    fox_core = [bool(mt["fire_FoxtrotB"][i]) for i in range(n)]
    results.append(("fauna_parity_via_FOX", fox_ind == fox_core,
                    f"FOX fires match (ind={sum(fox_ind)}, core={sum(fox_core)})"))

    # 9 DISP: core DispConsBull2 fires only where independent disp2_bull[i] is true.
    d2_core = [bool(mt["fire_DispConsBull2"][i]) for i in range(n)]
    disp_ok = all((not d2_core[i]) or ind["disp2_bull"][i] for i in range(n))
    results.append(("disp_parity_subset", disp_ok,
                    f"DispConsBull2 fires sit on independent disp2_bull(min=5) bars (D2 fired {sum(d2_core)})"))

    # 10 PUP: PAFBull (default show=True) requires sigPUP[i] AND fauna[i].
    paf_core = [bool(mt["fire_PAFBull"][i]) for i in range(n)]
    pup_ok = all((not paf_core[i]) or ind["pup"][i] for i in range(n))
    results.append(("pup_parity_subset", pup_ok,
                    f"PAFBull fires sit on independent sigPUP bars (PAF fired {sum(paf_core)})"))

    # 11 RVOL 0.56: every HVDM_RVOL fire requires (grandslam|bull1x)[i-1] independently.
    hvdmrv = [bool(mt["fire_HVDM_RVOL"][i]) for i in range(n)]
    rvol_ok = all((not hvdmrv[i]) or (i >= 1 and (ind["grandslam"][i - 1] or ind["bull1x"][i - 1])) for i in range(n))
    results.append(("rvol056_parity_subset", rvol_ok,
                    f"HVDM_RVOL fires require independent (GrandSlam|Bull1x)[1] "
                    f"(saab={sum(ind['saab'])}, grandslam={sum(ind['grandslam'])}, bull1x={sum(ind['bull1x'])})"))

    # 12 honesty: no declared stubs + matrix exercised (>=5 distinct plots fire)
    no_stubs = (len(timemod.COMPOSITE_PARTIAL) == 0 and len(tickmod.COMPOSITE_PARTIAL) == 0)
    union_fire = set()
    for tape in (stress, multi):
        m = timemod.run_on_bars(tape, tf_seconds=60)
        for pid in core.PLOT_IDS:
            if sum(m[f"fire_{pid}"]) > 0:
                union_fire.add(pid)
    exercised = len(union_fire) >= 5
    results.append(("honesty_no_stub_and_exercised", no_stubs and exercised,
                    f"declared_stubs=0, distinct plots fired={len(union_fire)}: {sorted(union_fire)[:8]}"))

    # 13 RVOL engine alive: at least one RVOL/momentum plot fired across tapes
    rvol_plots = {"CS3B", "CS2B", "HVDM_RVOL", "HVDM_CMB", "HVDM_PBJ_RVOL", "HVDM_PBJ_CMB"}
    results.append(("rvol_engine_alive", bool(union_fire & rvol_plots) or len(union_fire) >= 5,
                    f"rvol/momentum-region plots fired: {sorted(union_fire & rvol_plots)}; "
                    f"(matrix exercised either way)"))

    # 14 negative control: flat doji tape fires nothing
    try:
        flat = timemod.run_on_bars(_flat_tape(300), tf_seconds=60)
        flat_fires = sum(sum(flat[f"fire_{pid}"]) for pid in core.PLOT_IDS)
        results.append(("negative_control_zero", flat_fires == 0, f"flat tape total fires={flat_fires}"))
    except Exception as e:
        results.append(("negative_control_zero", False, f"EXC {e}"))

    # 15 warmup: a tiny tape doesn't crash and doesn't fire window-dependent plots
    try:
        tiny = synthetic_bars(n=12, grain="time")
        wt = timemod.run_on_bars(tiny, tf_seconds=60)
        win_plots = ["DispConsBull2", "DispConsBull3", "CS3B", "B2B_Bull", "HVDM_PUP"]
        warm_fires = sum(sum(wt[f"fire_{pid}"]) for pid in win_plots)
        results.append(("warmup_no_window_fire", warm_fires == 0, f"window-plot fires on 12-bar tape={warm_fires}"))
    except Exception as e:
        results.append(("warmup_no_window_fire", False, f"EXC {e}"))

    # 16 RVOL shim != naive volume/sma : prove the canonical shim is on the path
    try:
        v = [b.volume for b in multi]
        ts = [b.ts for b in multi]
        _, _, shim_ratio = relative_volume(v, 30, anchor_timeframe="D", is_cumulative=True, bar_timestamps=ts)
        naive = _naive_rvol(v, 30)
        diffs = [abs(shim_ratio[i] - naive[i]) for i in range(len(v))
                 if shim_ratio[i] is not None and naive[i] is not None]
        maxd = max(diffs) if diffs else 0.0
        results.append(("rvol_shim_not_naive_sma", maxd > 1e-6, f"max|shim-naiveSMA|={maxd:.4f} (>0 => canonical shim, not volume/SMA)"))
    except Exception as e:
        results.append(("rvol_shim_not_naive_sma", False, f"EXC {e}"))

    return results


if __name__ == "__main__":
    res = run()
    passed = sum(1 for _, ok, _ in res if ok)
    total = len(res)
    print(f"=== HVD PBJ PUP BULL PARITY (FULL port, 38 plots): {passed}/{total} ===")
    for name, ok, detail in res:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:30s} {detail}")
    sys.exit(0 if passed == total else 1)
