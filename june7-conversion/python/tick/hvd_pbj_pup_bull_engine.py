"""hvd_pbj_pup_bull_engine — detection fire matrix (PARTIAL: foundational engines).

Pine source: "hvd pbj pup bull.txt" (//@version=5). Ships 38 BULL plotshapes across 8+
engines (RVOL, FAUNA, displacement, GZI/HV FVG, PUP/PPD, PBJ, Ping-Pong SR, UU/P21,
Boom Hunter/Omega) plus combo sets, chains, floors.

SCOPE (RULE-0 candor): this engine ports the FOUNDATIONAL, cleanly-extractable detection
engines at nine-nines fidelity. The deep array/line-stateful composites are DEFERRED
(recorded, never faked):

  PORTED:
    sigSAAB, sigKratos, sigGrandSlam, sigMOAB, sigBullRVOL1x, sigBearRVOL1x,
    sigWTC, sigHiroshima, sigPentagon, sigNagasaki        (Engine 1 RVOL, daily-anchored)
    sigFAUNABull, sigFAUNABear                            (Engine 2 FAUNA w/ exclusions)
    sigDISPBull, sigDISPBear, sigDispConsBull2/3          (Engine 3 displacement)
    sigPUP, sigPPD                                        (Engine 5 PUP/PPD)
    gz_bullGZI, gz_bearGZI, gz_bullHV, gz_bearHV          (Engine 4 GZI/HV FVG)
    hvd_fire_bull (HV rank + displacement base combo)     (Pipeline A)

  DEFERRED (need dedicated stateful ports + gates):
    PBJ buy/sell landers (array<lvl>), Ping-Pong SR (array<srLevel> + line objects),
    Boom Hunter / Omega (Ehlers HP+SuperSmoother+pivots), UU/UUU/UUUU P21 chain,
    Combo Sets csNew1/2/3, CC/LSC chains, Floors, Foxtrot/AlphaStrike/OD/Golf/PAF,
    Super/SDuper, NAG+.

RVOL uses the daily-anchored shim (Pine "D" / RE10023 fix).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from nine_codon_core import Bar, sma, stdev, atr, highest, nz, shift
from tv_ta_shim import relative_volume


@dataclass(frozen=True)
class Params:
    bb_avgLength: int = 30
    bb_smaLength: int = 20
    reg_length: int = 30
    reg_anchor: str = "D"
    # displacement (Engine 3)
    disp_type_otc: bool = True
    std_len: int = 100
    std_min: float = 6.0
    std_max: float = 100.0
    req_fvg: bool = True
    # disp2/3 for cons
    disp2_std_min: float = 5.0
    disp3_std_min: float = 4.0
    # GZI/HV FVG
    gz1_auto: bool = True
    gz1_thresh: float = 2.0
    gz1_dist: int = 12
    # PUP/PPD
    pp_barSize: float = 3.0
    pp_lookback: int = 10
    # fauna
    fauna_gg_body: float = 0.80


def _f_rvol_1x(s):
    return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else 23.0 if s <= 45
            else 20.0 if s <= 60 else 18.0 if s <= 120 else 13.0 if s <= 300 else 13.0 if s <= 360
            else 11.0 if s <= 540 else 10.0 if s <= 600 else 9.0 if s <= 660 else 7.5 if s <= 900
            else 6.5 if s <= 1560 else 6.0 if s <= 2340 else 4.5 if s <= 3600 else 4.0 if s <= 9000
            else 3.5 if s <= 11700 else 1.8 if s < 259200 else 1.0)


def _f_gs_moab(s):
    if s < 60:
        return _f_rvol_1x(s) * 3.0
    return (35.0 if s <= 300 else 25.0 if s <= 600 else 20.0 if s <= 1500 else 20.0 if s <= 3000
            else 10.0 if s <= 7260 else 8.0 if s <= 11700 else 7.5 if s <= 86400 else 3.5 if s <= 259200 else 3.0)


def _f_hiroshima(s):
    if s < 60:
        return _f_rvol_1x(s) * 3.0
    return (35.0 if s <= 300 else 25.0 if s <= 600 else 25.0 if s <= 1500 else 20.0 if s <= 3060
            else 10.0 if s <= 7260 else 8.0 if s <= 11700 else 7.5 if s <= 86400 else 5.0 if s <= 259200 else 3.5)


def detect(bars: Sequence[Bar], params: Params = Params(), *, tf_seconds: int) -> dict:
    n = len(bars)
    o = [b.open for b in bars]; h = [b.high for b in bars]; lo = [b.low for b in bars]
    c = [b.close for b in bars]; v = [b.volume for b in bars]; ts = [b.ts for b in bars]
    P = params
    conf = [True] * n

    th_1x = _f_rvol_1x(tf_seconds)
    th_saab_kratos = th_1x * 0.56
    th_gs_moab = _f_gs_moab(tf_seconds)
    th_wtc = th_1x * 2.0
    th_hiroshima = _f_hiroshima(tf_seconds)

    # ── Engine 1: RVOL ──
    spike = [abs(c[i] - o[i]) for i in range(n)]
    sma_spike_1 = shift(sma(spike, P.bb_avgLength), 1)
    bb_np = [spike[i] / nz(sma_spike_1[i], 1.0) for i in range(n)]
    sma_vol_1 = shift(sma(v, P.bb_avgLength), 1)
    bb_nv = [v[i] / nz(sma_vol_1[i], 1.0) for i in range(n)]
    bb_diff = [bb_np[i] - bb_nv[i] for i in range(n)]
    bb_pos = [(d if d > 0 else None) for d in bb_diff]
    bb_smadiff = sma(bb_pos, P.bb_smaLength)

    def pg(i):
        return bb_pos[i] is not None and bb_smadiff[i] is not None and bb_pos[i] > bb_smadiff[i]

    bull_base = [c[i] > o[i] and pg(i) for i in range(n)]
    bear_base = [c[i] < o[i] and pg(i) for i in range(n)]

    def inr(x, a, b):
        return a <= x < b

    sigGrandSlam = [conf[i] and bull_base[i] and bb_np[i] >= th_gs_moab for i in range(n)]
    sigMOAB = [conf[i] and bear_base[i] and bb_np[i] >= th_gs_moab for i in range(n)]
    sigSAAB = [conf[i] and bull_base[i] and inr(bb_np[i], th_saab_kratos, th_1x) for i in range(n)]
    sigKratos = [conf[i] and bear_base[i] and inr(bb_np[i], th_saab_kratos, th_1x) for i in range(n)]
    sigBull1x = [conf[i] and bull_base[i] and inr(bb_np[i], th_1x, th_gs_moab) and not sigGrandSlam[i] for i in range(n)]
    sigBear1x = [conf[i] and bear_base[i] and inr(bb_np[i], th_1x, th_gs_moab) and not sigMOAB[i] for i in range(n)]

    rv = relative_volume(v, P.reg_length, anchor_timeframe=P.reg_anchor, is_cumulative=True, bar_timestamps=ts)
    relVol = [(rv.vol_ratio[i] or 0.0) for i in range(n)]
    rvv = [rv.vol_ratio[i] is not None for i in range(n)]
    sigWTC = [conf[i] and rvv[i] and relVol[i] > th_wtc and relVol[i] <= th_hiroshima for i in range(n)]
    sigHiroshima = [conf[i] and rvv[i] and relVol[i] > th_hiroshima for i in range(n)]
    sigPentagon = [conf[i] and rvv[i] and th_1x <= relVol[i] <= th_wtc for i in range(n)]

    sigNagasaki = [False] * n
    mx = 0.0
    for i in range(n):
        if i == 0:
            mx = v[i]
        elif v[i] > mx:
            sigNagasaki[i] = True; mx = v[i]

    # ── Engine 2: FAUNA (with exclusions) ──
    ATR = atr(h, lo, c, 14); AvgVol = sma(v, 20)
    AvgBody = sma([abs(c[i] - o[i]) for i in range(n)], 20)
    AvgDelta = sma([abs(c[i] - c[i - 1]) if i > 0 else 0.0 for i in range(n)], 10)
    TrendMA = sma(c, 50)

    def fauna(bull):
        out = [False] * n
        for i in range(n):
            if ATR[i] is None or AvgVol[i] is None or TrendMA[i] is None or i < 1 or TrendMA[i - 1] is None:
                continue
            up = c[i] > o[i]; dn = c[i] < o[i]; bsz = abs(c[i] - o[i]); rb = h[i] - lo[i]
            ratio = 0.0 if rb == 0 else bsz / rb
            d = up if bull else dn
            MB = d and bsz > 1.6 * ATR[i] and ratio > 0.70 and v[i] > 1.8 * AvgVol[i]
            if bull:
                RE = up and rb > 2.2 * ATR[i] and (h[i] - c[i]) < 0.15 * rb and v[i] > 1.8 * AvgVol[i]
                TA = TrendMA[i] > TrendMA[i - 1] and AvgDelta[i] is not None and (c[i] - c[i - 1]) > 1.6 * AvgDelta[i] and up and v[i] > 1.8 * AvgVol[i]
                GG = (o[i] - c[i - 1]) > 0.9 * ATR[i] and up and lo[i] > c[i - 1] and v[i] > 1.8 * AvgVol[i]
            else:
                RE = dn and rb > 2.2 * ATR[i] and (c[i] - lo[i]) < 0.15 * rb and v[i] > 1.8 * AvgVol[i]
                TA = TrendMA[i] < TrendMA[i - 1] and AvgDelta[i] is not None and (c[i - 1] - c[i]) > 1.6 * AvgDelta[i] and dn and v[i] > 1.8 * AvgVol[i]
                GG = (c[i - 1] - o[i]) > 0.9 * ATR[i] and dn and h[i] < c[i - 1] and v[i] > 1.8 * AvgVol[i]
            pb = c[i - 1] - o[i - 1]; pr = h[i - 1] - lo[i - 1]
            abp = AvgBody[i - 1] or 0.0; avp = AvgVol[i - 1] or 0.0
            if bull:
                StrBear = c[i - 1] < o[i - 1] and abs(pb) > 1.5 * abp and v[i - 1] > 1.5 * avp
                WeakBear = c[i - 1] < o[i - 1] and (0.0 if pr == 0 else abs(pb) / pr) <= 0.2
                TR = WeakBear and (MB or RE or TA); ES = StrBear and (MB or RE or TA); GDR = c[i - 1] < o[i - 1] and GG
            else:
                StrBull = c[i - 1] > o[i - 1] and abs(pb) > 1.5 * abp and v[i - 1] > 1.5 * avp
                WeakBull = c[i - 1] > o[i - 1] and (0.0 if pr == 0 else abs(pb) / pr) <= 0.2
                TR = WeakBull and (MB or RE or TA); ES = StrBull and (MB or RE or TA); GDR = c[i - 1] > o[i - 1] and GG
            core = (1 if MB else 0) + (1 if RE else 0) + (1 if TA else 0)
            gg_pass = (core >= 2) and (ratio >= P.fauna_gg_body)
            excluded = TR or ES or GDR or (GG and not gg_pass)
            out[i] = conf[i] and (MB or RE or TA) and not excluded
        return out

    sigFAUNABull = fauna(True)
    sigFAUNABear = fauna(False)

    # ── Engine 3: displacement (USE) ──
    def disp_engine(std_min):
        rng = [abs(o[i] - c[i]) if P.disp_type_otc else h[i] - lo[i] for i in range(n)]
        std = stdev(rng, P.std_len)
        tmin = [(std[i] * std_min) if std[i] is not None else None for i in range(n)]
        tmax = [(std[i] * P.std_max) if std[i] is not None else None for i in range(n)]
        tmin1 = shift(tmin, 1); tmax1 = shift(tmax, 1); rng1 = shift(rng, 1)
        prevDisp = [(rng1[i] is not None and tmin1[i] is not None and tmax1[i] is not None
                     and rng1[i] > tmin1[i] and rng1[i] <= tmax1[i]) for i in range(n)]
        bullFVG = [i >= 2 and lo[i] > h[i - 2] and c[i - 1] > o[i - 1] for i in range(n)]
        bearFVG = [i >= 2 and h[i] < lo[i - 2] and c[i - 1] < o[i - 1] for i in range(n)]
        return prevDisp, bullFVG, bearFVG

    pD, bF, sF = disp_engine(P.std_min)
    sigDISPBull = [conf[i] and (pD[i] and bF[i]) for i in range(n)]
    sigDISPBear = [conf[i] and (pD[i] and sF[i]) for i in range(n)]

    # disp cons 2/3 require FAUNA on prior bars (per source)
    pD2, bF2, sF2 = disp_engine(P.disp2_std_min)
    d2_bull = [conf[i] and pD2[i] and bF2[i] for i in range(n)]
    d2_bear = [conf[i] and pD2[i] and sF2[i] for i in range(n)]
    b2s = 0; r2s = 0; d2bs = [0] * n; d2rs = [0] * n
    for i in range(n):
        b2s = b2s + 1 if d2_bull[i] else 0
        r2s = r2s + 1 if d2_bear[i] else 0
        d2bs[i] = b2s; d2rs[i] = r2s
    fb1 = shift(sigFAUNABull, 1); fb2 = shift(sigFAUNABull, 2)
    fr1 = shift(sigFAUNABear, 1); fr2 = shift(sigFAUNABear, 2)
    sigDispConsBull2 = [d2_bull[i] and d2bs[i] >= 2 and bool(nz(fb1[i], False)) and bool(nz(fb2[i], False)) for i in range(n)]
    sigDispConsBear2 = [d2_bear[i] and d2rs[i] >= 2 and bool(nz(fr1[i], False)) and bool(nz(fr2[i], False)) for i in range(n)]

    pD3, bF3, sF3 = disp_engine(P.disp3_std_min)
    d3_bull = [conf[i] and pD3[i] and bF3[i] for i in range(n)]
    b3s = 0; d3bs = [0] * n
    for i in range(n):
        b3s = b3s + 1 if d3_bull[i] else 0
        d3bs[i] = b3s
    fb3 = shift(sigFAUNABull, 3)
    sigDispConsBull3 = [d3_bull[i] and d3bs[i] >= 3 and bool(nz(fb1[i], False)) and bool(nz(fb2[i], False)) and bool(nz(fb3[i], False)) for i in range(n)]

    # ── Engine 4: GZI/HV FVG ──
    v1 = shift(v, 1)
    hv5000 = shift(highest(v, 5000), 1); hv252 = shift(highest(v, 252), 1); hv63 = shift(highest(v, 63), 1)

    def is_hv(i):
        if v1[i] is None:
            return False
        return ((hv5000[i] is not None and v1[i] == hv5000[i]) or (hv252[i] is not None and v1[i] == hv252[i])
                or (hv63[i] is not None and v1[i] == hv63[i]))

    cum_r = 0.0
    gz_bullGZI = [False] * n; gz_bearGZI = [False] * n; gz_bullHV = [False] * n; gz_bearHV = [False] * n
    fvgs = []; lastT = 0
    for i in range(n):
        cum_r += (h[i] - lo[i]) / lo[i] if lo[i] != 0 else 0.0
        thr = (cum_r / i) if (P.gz1_auto and i > 0) else (P.gz1_thresh / 100.0)
        hv_i = is_hv(i)
        bFVG = i >= 2 and lo[i] > h[i - 2] and c[i - 1] > h[i - 2] and (lo[i] - h[i - 2]) / h[i - 2] > thr
        sFVG = i >= 2 and h[i] < lo[i - 2] and c[i - 1] < lo[i - 2] and (lo[i - 2] - h[i]) / h[i] > thr
        if bFVG and ts[i] != lastT:
            mxx, mnn = lo[i], h[i - 2]
            if hv_i:
                gz_bullHV[i] = True
            for e in fvgs:
                if e["bull"] and i - e["idx"] <= P.gz1_dist:
                    if max(e["mn"], mnn) < min(e["mx"], mxx) or (max(e["mn"], mnn) <= min(e["mx"], mxx) and e["hv"] and hv_i):
                        gz_bullGZI[i] = True; break
            fvgs.insert(0, {"mx": mxx, "mn": mnn, "bull": True, "idx": i, "hv": hv_i}); lastT = ts[i]
        if sFVG and ts[i] != lastT:
            mxx, mnn = lo[i - 2], h[i]
            if hv_i:
                gz_bearHV[i] = True
            for e in fvgs:
                if (not e["bull"]) and i - e["idx"] <= P.gz1_dist:
                    if max(e["mn"], mnn) < min(e["mx"], mxx) or (max(e["mn"], mnn) <= min(e["mx"], mxx) and e["hv"] and hv_i):
                        gz_bearGZI[i] = True; break
            fvgs.insert(0, {"mx": mxx, "mn": mnn, "bull": False, "idx": i, "hv": hv_i}); lastT = ts[i]

    # ── Engine 5: PUP/PPD ──
    redVol = [v[i] if c[i] < o[i] else 0.0 for i in range(n)]
    greenVol = [v[i] if c[i] > o[i] else 0.0 for i in range(n)]
    hiRed = shift(highest(shift(redVol, 1), P.pp_lookback) if False else highest([redVol[i - 1] if i >= 1 else 0.0 for i in range(n)], P.pp_lookback), 0)
    # Pine: ta.highest(pp_redVol[1], pp_lookback) -> highest over window of the [1]-shifted series
    redVol_1 = [redVol[i - 1] if i >= 1 else 0.0 for i in range(n)]
    greenVol_1 = [greenVol[i - 1] if i >= 1 else 0.0 for i in range(n)]
    hiRed = highest(redVol_1, P.pp_lookback)
    hiGreen = highest(greenVol_1, P.pp_lookback)
    priceUp = [((c[i] - o[i]) / o[i]) * 100 > P.pp_barSize if o[i] != 0 else False for i in range(n)]
    priceDn = [((o[i] - c[i]) / o[i]) * 100 > P.pp_barSize if o[i] != 0 else False for i in range(n)]
    sigPUP = [conf[i] and priceUp[i] and (hiRed[i] is not None and v[i] > hiRed[i]) for i in range(n)]
    sigPPD = [conf[i] and priceDn[i] and (hiGreen[i] is not None and v[i] > hiGreen[i]) for i in range(n)]

    # ── Pipeline A: HV+D base combo ──
    def hv_rank(period):
        hp = shift(highest(v, period), 1)
        return [hp[i] is not None and v1[i] is not None and v1[i] == hp[i] for i in range(n)]
    ranks = {p: hv_rank(p) for p in (50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 1000)}
    # HEV: new running max of volume[1]
    isHEV = [False] * n
    mxe = 0.0
    for i in range(n):
        if v1[i] is not None and v1[i] > mxe:
            mxe = v1[i]; isHEV[i] = True
    base_hv_hit = [isHEV[i] or (any(ranks[p][i] for p in ranks) and not isHEV[i]) for i in range(n)]
    # HV+D base displacement (d1 engine: std_len 100, mult 5.0, otc)
    d1_rng = [abs(o[i] - c[i]) for i in range(n)]
    d1_std = stdev(d1_rng, 100)
    d1_thr = [(d1_std[i] * 5.0) if d1_std[i] is not None else None for i in range(n)]
    d1_rng1 = shift(d1_rng, 1); d1_thr1 = shift(d1_thr, 1)
    d1_prevDisp = [d1_rng1[i] is not None and d1_thr1[i] is not None and d1_rng1[i] > d1_thr1[i] for i in range(n)]
    d1_bullFVG = [i >= 2 and lo[i] > h[i - 2] and c[i - 1] > o[i - 1] for i in range(n)]
    d1_bull = [conf[i] and d1_prevDisp[i] and d1_bullFVG[i] for i in range(n)]
    hvd_fire_bull = [base_hv_hit[i] and d1_bull[i] for i in range(n)]

    fires = {
        "SAAB": sigSAAB, "Kratos": sigKratos, "GrandSlam": sigGrandSlam, "MOAB": sigMOAB,
        "BullRVOL1x": sigBull1x, "BearRVOL1x": sigBear1x, "WTC": sigWTC, "Hiroshima": sigHiroshima,
        "Pentagon": sigPentagon, "Nagasaki": sigNagasaki,
        "FAUNABull": sigFAUNABull, "FAUNABear": sigFAUNABear,
        "DISPBull": sigDISPBull, "DISPBear": sigDISPBear,
        "DispConsBull2": sigDispConsBull2, "DispConsBear2": sigDispConsBear2, "DispConsBull3": sigDispConsBull3,
        "GZI_BullGZI": gz_bullGZI, "GZI_BearGZI": gz_bearGZI, "GZI_BullHV": gz_bullHV, "GZI_BearHV": gz_bearHV,
        "PUP": sigPUP, "PPD": sigPPD, "HVD_FireBull": hvd_fire_bull,
    }
    events = []
    for k, arr in fires.items():
        for i in range(n):
            if arr[i]:
                events.append((ts[i] * 1_000_000, k))
    events.sort()
    deferred = ["PBJ_buy", "PBJ_sell", "PingPong_SR", "BoomHunter_Omega", "OmegaLong", "OmegaLongA",
                "P21_UU/UUU/UUUU", "ComboSet_csNew1/2/3", "CC_chain", "LSC_chain", "Floor", "2ndFloor",
                "Foxtrot", "AlphaStrike", "ODBull", "Golf", "PAF", "Super", "SDuper", "NAG+"]
    return {"fires": fires, "events": events, "deferred": deferred, "series": {"relVol": relVol}}
