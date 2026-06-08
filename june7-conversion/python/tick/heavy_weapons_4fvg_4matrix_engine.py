"""heavy_weapons_4fvg_4matrix_engine — shared detection-plot fire matrix.

Pine source: "heavy weapons with 4 fvg 4 matrix.txt" (//@version=5).
This is the ONE code path (CODON rule: batch == streaming == fresh-rerun). Both the
tick wrapper and the time wrapper call `detect(bars, params)`; the only thing that
differs between them is how the bars were manufactured (N-tick fold vs time candle)
and that relativeVolume is ALWAYS daily-anchored off wall-clock day (the Pine "D"
anchor / RE10023 fix), never the bar grain.

Detection plots reproduced (22 plotshapes in the Pine source):
  SAAB, Kratos, BullRVOL1x, BearRVOL1x, GrandSlam, MOAB,
  Pentagon, WTC, Hiroshima, Nagasaki,
  Long1, Short1, Long2, Short2,
  CS1_Bull, CS1_Bear, CS2_Bull, CS2_Bear (FVG/GZI combos),
  CS3_Bull, CS3_Bear, CS4_Bull, CS4_Bear (Matrix combos).

Each is emitted as a coordinate event (computed_bar_epoch_ns, applied_bar_epoch_ns,
location, shape, plot_id) honoring the Pine `offset` (FVG combos paint offset=-1).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

from nine_codon_core import (
    Bar, sma, atr, highest, nz, shift,
)
from tv_ta_shim import relative_volume


@dataclass(frozen=True)
class Params:
    bb_avgLength: int = 30
    bb_smaLength: int = 20
    reg_length: int = 30
    reg_cumulative: bool = True          # "Cumulative"
    reg_anchor: str = "D"                 # RE10023 fix: daily anchor always
    matrix_len: int = 67
    comboBodyPct_FVG: float = 0.85
    comboBodyPct_MAT: float = 0.85
    inc_pentagon_FVG: bool = True
    inc_pentagon_MAT: bool = True
    gziDist: int = 7
    auto_thresh: bool = True
    threshPct: float = 2.0
    hyb_addReg1: float = 5.0
    hyb_addCum1: float = 3.0
    hyb_bodyRat1: float = 0.65
    hyb_addReg2: float = 5.0
    hyb_addCum2: float = 3.0
    hyb_bodyRat2: float = 0.65
    # global show toggles — default to the Pine source's defaults so the fire matrix
    # matches the shipped indicator. Set all True to expose every signal.
    show_SAAB: bool = False
    show_Kratos: bool = False
    show_BullRVOL1x: bool = False
    show_BearRVOL1x: bool = False
    show_GrandSlam: bool = True
    show_MOAB: bool = True
    show_Pentagon: bool = False
    show_WTC: bool = True
    show_Hiroshima: bool = True
    show_Nagasaki: bool = True
    show_Long1: bool = False
    show_Short1: bool = False
    show_Long2: bool = False
    show_Short2: bool = False
    show_CS1_Bull: bool = True
    show_CS1_Bear: bool = True
    show_CS2_Bull: bool = True
    show_CS2_Bear: bool = True
    show_CS3_Bull: bool = True
    show_CS3_Bear: bool = True
    show_CS4_Bull: bool = True
    show_CS4_Bear: bool = True


@dataclass(frozen=True, slots=True)
class FireEvent:
    computed_ts_ms: int      # bar whose close computed the signal
    applied_ts_ms: int       # bar the shape paints on after Pine `offset`
    plot_id: str
    location: str            # 'belowbar'|'abovebar'|'top'|'bottom'
    shape: str


# matrix threshold tables (exact from Pine source) ------------------------------
def _f_rvol_1x(s: float) -> float:
    return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else 23.0 if s <= 45
            else 20.0 if s <= 60 else 19.0 if s <= 120 else 17.0 if s <= 180 else 16.0 if s <= 240
            else 15.0 if s <= 300 else 14.0 if s <= 360 else 12.0 if s <= 420 else 11.0 if s <= 480
            else 10.0 if s <= 540 else 10.0 if s <= 600 else 8.4 if s <= 900 else 6.9 if s <= 1800
            else 5.9 if s <= 3600 else 3.0 if s <= 7200 else 1.8)


def _f_gs_moab(s: float) -> float:
    return (114.0 if s <= 10 else 99.0 if s <= 15 else 84.0 if s <= 30 else 69.0 if s <= 45
            else 35.0 if s <= 60 else 35.0 if s <= 300 else 25.0 if s <= 600 else 20.0 if s <= 900
            else 10.0 if s <= 3600 else 8.0)


def detect(bars: Sequence[Bar], params: Params = Params(), *, tf_seconds: int) -> dict:
    """Return {'fires': {plot_id: [bool per bar]}, 'events': [FireEvent], 'series': {...}}.

    `tf_seconds` selects the per-TF threshold row (tick wrapper passes the tick
    fallback seconds; time wrapper passes the real bar seconds).
    """
    n = len(bars)
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    lo = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]

    th_1x = _f_rvol_1x(tf_seconds)
    th_saab_kratos = th_1x * 0.56
    th_wtc = th_1x * 2.0
    th_gs_moab = _f_gs_moab(tf_seconds)
    th_hiroshima = th_gs_moab

    # --- RVOL 0.56 / Bull-Bear normalized price ---
    bb_spike = [abs(c[i] - o[i]) for i in range(n)]
    sma_spike = sma(bb_spike, params.bb_avgLength)
    sma_spike_1 = shift(sma_spike, 1)
    bb_np = [bb_spike[i] / nz(sma_spike_1[i], 1.0) for i in range(n)]
    sma_vol = sma(v, params.bb_avgLength)
    sma_vol_1 = shift(sma_vol, 1)
    bb_nv = [v[i] / nz(sma_vol_1[i], 1.0) for i in range(n)]
    bb_diff = [bb_np[i] - bb_nv[i] for i in range(n)]
    bb_posdiff = [(d if d > 0 else None) for d in bb_diff]
    bb_smadiff = sma(bb_posdiff, params.bb_smaLength)

    def pos_gt_sma(i):
        return bb_posdiff[i] is not None and bb_smadiff[i] is not None and bb_posdiff[i] > bb_smadiff[i]

    bull_base = [(c[i] > o[i]) and pos_gt_sma(i) for i in range(n)]
    bear_base = [(c[i] < o[i]) and pos_gt_sma(i) for i in range(n)]

    def in_rng(x, lo_t, hi_t):
        return x >= lo_t and x < hi_t

    conf = [True] * n  # batch over closed bars only

    sigSAAB = [conf[i] and bull_base[i] and in_rng(bb_np[i], th_saab_kratos, th_1x) for i in range(n)]
    sigKratos = [conf[i] and bear_base[i] and in_rng(bb_np[i], th_saab_kratos, th_1x) for i in range(n)]
    sigBull1x = [conf[i] and bull_base[i] and in_rng(bb_np[i], th_1x, th_gs_moab) for i in range(n)]
    sigBear1x = [conf[i] and bear_base[i] and in_rng(bb_np[i], th_1x, th_gs_moab) for i in range(n)]
    sigGrandSlam = [conf[i] and bull_base[i] and bb_np[i] >= th_gs_moab for i in range(n)]
    sigMOAB = [conf[i] and bear_base[i] and bb_np[i] >= th_gs_moab for i in range(n)]

    # --- Reg @ time RVOL (daily anchor — RE10023 fix) ---
    rv = relative_volume(v, params.reg_length, anchor_timeframe=params.reg_anchor,
                         is_cumulative=params.reg_cumulative, bar_timestamps=ts)
    relVol = [(rv.vol_ratio[i] if rv.vol_ratio[i] is not None else 0.0) for i in range(n)]
    rv_valid = [rv.vol_ratio[i] is not None for i in range(n)]

    sigPentagon = [conf[i] and rv_valid[i] and relVol[i] >= th_1x and relVol[i] <= th_wtc for i in range(n)]
    sigWTC = [conf[i] and rv_valid[i] and relVol[i] > th_wtc and relVol[i] <= th_hiroshima for i in range(n)]
    sigHiroshima = [conf[i] and rv_valid[i] and relVol[i] > th_hiroshima for i in range(n)]

    # --- Nagasaki: new running-max volume ---
    sigNagasaki = [False] * n
    maxVol = 0.0
    for i in range(n):
        if i == 0:
            maxVol = v[i]
        elif v[i] > maxVol:
            sigNagasaki[i] = True
            maxVol = v[i]

    # --- Hybrid momentum (Long1/2, Short1/2) — cumulative RVOL ratio reused ---
    hybRegRatio = relVol  # source sets hybRegRatio = relVolRatio (cumulative)
    hybCum = relative_volume(v, params.reg_length, anchor_timeframe=params.reg_anchor,
                             is_cumulative=True, bar_timestamps=ts)
    hybCumRatio = [(hybCum.vol_ratio[i] if hybCum.vol_ratio[i] is not None else 0.0) for i in range(n)]
    body = [abs(c[i] - o[i]) for i in range(n)]
    rng = [h[i] - lo[i] for i in range(n)]
    bodyRat = [(0.0 if rng[i] == 0 else body[i] / rng[i]) for i in range(n)]

    def hyb(i, reg_floor, cum_floor, body_floor):
        return conf[i] and rv_valid[i] and hybRegRatio[i] > reg_floor and hybCumRatio[i] > cum_floor and bodyRat[i] >= body_floor

    sigLong1 = [hyb(i, params.hyb_addReg1, params.hyb_addCum1, params.hyb_bodyRat1) and c[i] > o[i] for i in range(n)]
    sigShort1 = [hyb(i, params.hyb_addReg1, params.hyb_addCum1, params.hyb_bodyRat1) and c[i] < o[i] for i in range(n)]
    sigLong2 = [hyb(i, params.hyb_addReg2, params.hyb_addCum2, params.hyb_bodyRat2) and c[i] > o[i] for i in range(n)]
    sigShort2 = [hyb(i, params.hyb_addReg2, params.hyb_addCum2, params.hyb_bodyRat2) and c[i] < o[i] for i in range(n)]

    # --- GZI / HV FVG (array-stateful, conf-gated) ---
    v1 = shift(v, 1)
    hv5000 = shift(highest(v, 5000), 1)
    hv252 = shift(highest(v, 252), 1)
    hv63 = shift(highest(v, 63), 1)

    def is_hv(i):
        if v1[i] is None:
            return False
        return (hv5000[i] is not None and v1[i] == hv5000[i]) or \
               (hv252[i] is not None and v1[i] == hv252[i]) or \
               (hv63[i] is not None and v1[i] == hv63[i])

    cum_range = 0.0
    bullGZI = [False] * n
    bearGZI = [False] * n
    bullHV = [False] * n
    bearHV = [False] * n
    fvgs: list[dict] = []
    lastT = 0
    for i in range(n):
        cum_range += (h[i] - lo[i]) / lo[i] if lo[i] != 0 else 0.0
        thresh = (cum_range / i) if (params.auto_thresh and i > 0) else (params.threshPct / 100.0)
        hv_i = is_hv(i)
        bFVG = i >= 2 and lo[i] > h[i - 2] and c[i - 1] > h[i - 2] and (lo[i] - h[i - 2]) / h[i - 2] > thresh
        sFVG = i >= 2 and h[i] < lo[i - 2] and c[i - 1] < lo[i - 2] and (lo[i - 2] - h[i]) / h[i] > thresh
        if bFVG and ts[i] != lastT:
            mx, mn = lo[i], h[i - 2]
            if hv_i:
                bullHV[i] = True
            for e in fvgs:
                if e["bull"] and i - e["idx"] <= params.gziDist:
                    ob = max(e["mn"], mn); ot = min(e["mx"], mx)
                    if ob < ot or (ob <= ot and e["hv"] and hv_i):
                        bullGZI[i] = True
                        break
            fvgs.insert(0, {"mx": mx, "mn": mn, "bull": True, "idx": i, "hv": hv_i})
            lastT = ts[i]
        if sFVG and ts[i] != lastT:
            mx, mn = lo[i - 2], h[i]
            if hv_i:
                bearHV[i] = True
            for e in fvgs:
                if (not e["bull"]) and i - e["idx"] <= params.gziDist:
                    ob = max(e["mn"], mn); ot = min(e["mx"], mx)
                    if ob < ot or (ob <= ot and e["hv"] and hv_i):
                        bearGZI[i] = True
                        break
            fvgs.insert(0, {"mx": mx, "mn": mn, "bull": False, "idx": i, "hv": hv_i})
            lastT = ts[i]
        # mitigation removal (close beyond zone) — affects future GZI overlaps
        survivors = []
        for g in fvgs:
            if g["bull"] and c[i] < g["mn"]:
                continue
            if (not g["bull"]) and c[i] > g["mx"]:
                continue
            survivors.append(g)
        fvgs = survivors

    # --- Matrix / Fauna ---
    ATR = atr(h, lo, c, 14)
    AvgVol = sma(v, 20)
    hv_mat = highest(v, params.matrix_len)
    is_matrix = [hv_mat[i] is not None and v[i] == hv_mat[i] for i in range(n)]

    def fauna_side(bull: bool):
        AvgBody = sma([abs(c[i] - o[i]) for i in range(n)], 20)
        AvgDelta = sma([abs(c[i] - c[i - 1]) if i > 0 else 0.0 for i in range(n)], 10)
        TrendMA = sma(c, 50)
        out = [False] * n
        for i in range(n):
            if ATR[i] is None or AvgVol[i] is None or TrendMA[i] is None or i < 1:
                continue
            body_up = c[i] > o[i]; body_dn = c[i] < o[i]
            bs = abs(c[i] - o[i]); rb = h[i] - lo[i]
            ratio = 0.0 if rb == 0 else bs / rb
            dir_ok = body_up if bull else body_dn
            MB = dir_ok and bs > 1.6 * ATR[i] and ratio > 0.70 and v[i] > 1.8 * AvgVol[i]
            if bull:
                RE = body_up and rb > 2.2 * ATR[i] and (h[i] - c[i]) < 0.15 * rb and v[i] > 1.8 * AvgVol[i]
                TA = TrendMA[i] is not None and TrendMA[i - 1] is not None and TrendMA[i] > TrendMA[i - 1] and AvgDelta[i] is not None and (c[i] - c[i - 1]) > 1.6 * AvgDelta[i] and body_up and v[i] > 1.8 * AvgVol[i]
                GG = (o[i] - c[i - 1]) > 0.9 * ATR[i] and body_up and lo[i] > c[i - 1] and v[i] > 1.8 * AvgVol[i]
            else:
                RE = body_dn and rb > 2.2 * ATR[i] and (c[i] - lo[i]) < 0.15 * rb and v[i] > 1.8 * AvgVol[i]
                TA = TrendMA[i] is not None and TrendMA[i - 1] is not None and TrendMA[i] < TrendMA[i - 1] and AvgDelta[i] is not None and (c[i - 1] - c[i]) > 1.6 * AvgDelta[i] and body_dn and v[i] > 1.8 * AvgVol[i]
                GG = (c[i - 1] - o[i]) > 0.9 * ATR[i] and body_dn and h[i] < c[i - 1] and v[i] > 1.8 * AvgVol[i]
            prev_body = c[i - 1] - o[i - 1]
            prev_rng = h[i - 1] - lo[i - 1]
            ab_prev = AvgBody[i - 1] if AvgBody[i - 1] is not None else 0.0
            av_prev = AvgVol[i - 1] if AvgVol[i - 1] is not None else 0.0
            if bull:
                StrBear = c[i - 1] < o[i - 1] and abs(prev_body) > 1.5 * ab_prev and v[i - 1] > 1.5 * av_prev
                WeakBear = c[i - 1] < o[i - 1] and (0.0 if prev_rng == 0 else abs(prev_body) / prev_rng) <= 0.2
                TR = WeakBear and (MB or RE or TA); ES = StrBear and (MB or RE or TA); GDR = c[i - 1] < o[i - 1] and GG
            else:
                StrBull = c[i - 1] > o[i - 1] and abs(prev_body) > 1.5 * ab_prev and v[i - 1] > 1.5 * av_prev
                WeakBull = c[i - 1] > o[i - 1] and (0.0 if prev_rng == 0 else abs(prev_body) / prev_rng) <= 0.2
                TR = WeakBull and (MB or RE or TA); ES = StrBull and (MB or RE or TA); GDR = c[i - 1] > o[i - 1] and GG
            core = (1 if MB else 0) + (1 if RE else 0) + (1 if TA else 0)
            gg_pass = (core >= 2) and (ratio >= 0.85)
            excluded = TR or ES or GDR or (GG and not gg_pass)
            out[i] = (MB or RE or TA) and not excluded
        return out

    fauna_bull = fauna_side(True)
    fauna_bear = fauna_side(False)

    neo_bull = [conf[i] and is_matrix[i] and fauna_bull[i] for i in range(n)]
    neo_bear = [conf[i] and is_matrix[i] and fauna_bear[i] for i in range(n)]
    trin_bull = [conf[i] and is_matrix[i] and (not fauna_bull[i]) and c[i] > o[i] for i in range(n)]
    trin_bear = [conf[i] and is_matrix[i] and (not fauna_bear[i]) and c[i] < o[i] for i in range(n)]

    neo_bull_al = [neo_bull[i] and (sigLong1[i] or sigLong2[i]) for i in range(n)]
    neo_bear_al = [neo_bear[i] and (sigShort1[i] or sigShort2[i]) for i in range(n)]
    trin_bull_al = [trin_bull[i] and (sigLong1[i] or sigLong2[i]) for i in range(n)]
    trin_bear_al = [trin_bear[i] and (sigShort1[i] or sigShort2[i]) for i in range(n)]

    # --- Combination signals ---
    sigSAAB_1 = shift(sigSAAB, 1); sigBull1x_1 = shift(sigBull1x, 1); sigGS_1 = shift(sigGrandSlam, 1)
    sigKr_1 = shift(sigKratos, 1); sigBear1x_1 = shift(sigBear1x, 1); sigMOAB_1 = shift(sigMOAB, 1)
    sigPent_1 = shift(sigPentagon, 1); sigWTC_1 = shift(sigWTC, 1); sigHiro_1 = shift(sigHiroshima, 1); sigNaga_1 = shift(sigNagasaki, 1)
    body1 = [abs(c[i - 1] - o[i - 1]) if i >= 1 else 0.0 for i in range(n)]
    rng1 = [h[i - 1] - lo[i - 1] if i >= 1 else 0.0 for i in range(n)]
    bodyPct1 = [(0.0 if rng1[i] == 0 else body1[i] / rng1[i]) for i in range(n)]
    validBody_FVG = [bodyPct1[i] >= params.comboBodyPct_FVG for i in range(n)]
    validBody_MAT = [bodyRat[i] >= params.comboBodyPct_MAT for i in range(n)]

    def b(x, i):
        return bool(x[i]) if x[i] is not None else False

    cs1_bull = [conf[i] and validBody_FVG[i] and (bullHV[i] or bullGZI[i]) and (b(sigSAAB_1, i) or b(sigBull1x_1, i) or b(sigGS_1, i)) for i in range(n)]
    cs1_bear = [conf[i] and validBody_FVG[i] and (bearHV[i] or bearGZI[i]) and (b(sigKr_1, i) or b(sigBear1x_1, i) or b(sigMOAB_1, i)) for i in range(n)]
    volRegBull_FVG = [((params.inc_pentagon_FVG and b(sigPent_1, i)) or b(sigWTC_1, i) or b(sigHiro_1, i) or b(sigNaga_1, i)) for i in range(n)]
    cs2_bull = [conf[i] and validBody_FVG[i] and (bullHV[i] or bullGZI[i]) and volRegBull_FVG[i] for i in range(n)]
    cs2_bear = [conf[i] and validBody_FVG[i] and (bearHV[i] or bearGZI[i]) and volRegBull_FVG[i] for i in range(n)]

    matrix_any_bull = [neo_bull[i] or trin_bull[i] or neo_bull_al[i] or trin_bull_al[i] for i in range(n)]
    matrix_any_bear = [neo_bear[i] or trin_bear[i] or neo_bear_al[i] or trin_bear_al[i] for i in range(n)]
    cs3_bull = [validBody_MAT[i] and matrix_any_bull[i] and (sigSAAB[i] or sigBull1x[i] or sigGrandSlam[i]) for i in range(n)]
    cs3_bear = [validBody_MAT[i] and matrix_any_bear[i] and (sigKratos[i] or sigBear1x[i] or sigMOAB[i]) for i in range(n)]
    volRegBull_MAT = [((params.inc_pentagon_MAT and sigPentagon[i]) or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i]) for i in range(n)]
    cs4_bull = [validBody_MAT[i] and matrix_any_bull[i] and volRegBull_MAT[i] for i in range(n)]
    cs4_bear = [validBody_MAT[i] and matrix_any_bear[i] and volRegBull_MAT[i] for i in range(n)]

    P = params
    fires = {
        "SAAB": [P.show_SAAB and sigSAAB[i] for i in range(n)],
        "Kratos": [P.show_Kratos and sigKratos[i] for i in range(n)],
        "BullRVOL1x": [P.show_BullRVOL1x and sigBull1x[i] for i in range(n)],
        "BearRVOL1x": [P.show_BearRVOL1x and sigBear1x[i] for i in range(n)],
        "GrandSlam": [P.show_GrandSlam and sigGrandSlam[i] for i in range(n)],
        "MOAB": [P.show_MOAB and sigMOAB[i] for i in range(n)],
        "Pentagon": [P.show_Pentagon and sigPentagon[i] for i in range(n)],
        "WTC": [P.show_WTC and sigWTC[i] for i in range(n)],
        "Hiroshima": [P.show_Hiroshima and sigHiroshima[i] for i in range(n)],
        "Nagasaki": [P.show_Nagasaki and sigNagasaki[i] for i in range(n)],
        "Long1": [P.show_Long1 and sigLong1[i] for i in range(n)],
        "Short1": [P.show_Short1 and sigShort1[i] for i in range(n)],
        "Long2": [P.show_Long2 and sigLong2[i] for i in range(n)],
        "Short2": [P.show_Short2 and sigShort2[i] for i in range(n)],
        "CS1_Bull": [P.show_CS1_Bull and cs1_bull[i] for i in range(n)],
        "CS1_Bear": [P.show_CS1_Bear and cs1_bear[i] for i in range(n)],
        "CS2_Bull": [P.show_CS2_Bull and cs2_bull[i] for i in range(n)],
        "CS2_Bear": [P.show_CS2_Bear and cs2_bear[i] for i in range(n)],
        "CS3_Bull": [P.show_CS3_Bull and cs3_bull[i] for i in range(n)],
        "CS3_Bear": [P.show_CS3_Bear and cs3_bear[i] for i in range(n)],
        "CS4_Bull": [P.show_CS4_Bull and cs4_bull[i] for i in range(n)],
        "CS4_Bear": [P.show_CS4_Bear and cs4_bear[i] for i in range(n)],
    }
    # offsets per Pine source: FVG combos paint offset=-1; everything else offset=0.
    offset = {k: 0 for k in fires}
    for k in ("CS1_Bull", "CS1_Bear", "CS2_Bull", "CS2_Bear"):
        offset[k] = -1
    loc = {
        "SAAB": "belowbar", "Kratos": "abovebar", "BullRVOL1x": "belowbar", "BearRVOL1x": "abovebar",
        "GrandSlam": "belowbar", "MOAB": "abovebar", "Pentagon": "top", "WTC": "top", "Hiroshima": "top",
        "Nagasaki": "top", "Long1": "belowbar", "Short1": "abovebar", "Long2": "belowbar", "Short2": "abovebar",
        "CS1_Bull": "belowbar", "CS1_Bear": "abovebar", "CS2_Bull": "belowbar", "CS2_Bear": "abovebar",
        "CS3_Bull": "belowbar", "CS3_Bear": "abovebar", "CS4_Bull": "belowbar", "CS4_Bear": "abovebar",
    }
    events: list[FireEvent] = []
    for k, arr in fires.items():
        off = offset[k]
        for i in range(n):
            if arr[i]:
                j = i + off  # Pine offset=-1 paints one bar back along the real bar sequence
                if 0 <= j < n:
                    events.append(FireEvent(computed_ts_ms=ts[i] * 1_000_000,
                                            applied_ts_ms=ts[j] * 1_000_000,
                                            plot_id=k, location=loc[k], shape="plotshape"))
    events.sort(key=lambda e: (e.applied_ts_ms, e.plot_id))
    return {"fires": fires, "events": events, "series": {"relVol": relVol, "bb_np": bb_np}}
