"""heavy_with_2x_detection_plots_engine — detection fire matrix (single code path).

Pine source: "heavy with 2x detection plots.txt" (//@version=5).
Detection plots reproduced (the file's plotshape set + FAUNA, which the tick-friendly
Pine converts from label.new -> plotshape):

  RVOL: SAAB, Kratos, BullRVOL1x, BearRVOL1x, GrandSlam, MOAB, WTC, Hiroshima, Nagasaki
  Sequence (IPSF): UU, UUU, UUUU, DD, DDD, DDDD
  Back-to-back: B2B_2xSAAB, B2B_2xKratos, B2B_2xBull1x, B2B_2xBear1x, B2B_MidBull, B2B_MidBear
  Momentum (hybrid, auto-derive ladder): Long1, Short1, Long2, Short2, Long3, Long4, Long5
  Displacement: DispBull, DispBear, CDispBull2, CDispBear2, CDispBull3, CDispBear3
  HV NRA ([1]): HV75, HV150, HV250, HV500, HV1000, HotSpot
  FAUNA: FaunaBull, FaunaBear

RVOL is daily-anchored (Pine "D" / RE10023 fix). HV / displacement / disp-cons plots
paint offset=-1 in Pine (mark the prior/confirmed bar) — the events honor that.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

from nine_codon_core import Bar, sma, stdev, atr, highest, nz, shift
from tv_ta_shim import relative_volume


@dataclass(frozen=True)
class Params:
    bb_avgLength: int = 30
    bb_smaLength: int = 20
    reg_length: int = 30
    reg_cumulative: bool = True
    reg_anchor: str = "D"
    enableNagasaki: bool = True
    # IPSF sequence thresholds
    th_low_UU_DD: float = 1.0
    th_low_UUU_DDD: float = 1.0
    th_low_UUUU_DDDD: float = 1.0
    seqTh_UU_DD: float = 0.1
    seqTh_UUU_DDD: float = 0.1
    seqTh_UUUU_DDDD: float = 0.1
    seq_th_high: float = 50.0
    # displacement
    disp_type_otc: bool = True       # "Open to Close"
    std_len: int = 100
    std_min: float = 3.0
    std_max: float = 7.0
    # hybrid auto-derive
    hyb_autoDerive: bool = True
    hyb_addReg: float = 5.0
    hyb_addCum: float = 3.0
    hyb_bodyRat: float = 0.65


def _f_rvol_1x(s):
    return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else 23.0 if s <= 45
            else 20.0 if s <= 60 else 19.0 if s <= 120 else 17.0 if s <= 180 else 16.0 if s <= 240
            else 15.0 if s <= 300 else 14.0 if s <= 360 else 12.0 if s <= 420 else 11.0 if s <= 480
            else 10.0 if s <= 540 else 10.0 if s <= 600 else 8.4 if s <= 900 else 6.9 if s <= 1800
            else 5.9 if s <= 3600 else 3.0 if s <= 7200 else 1.8)


def _f_gs_moab(s):
    return (114.0 if s <= 10 else 99.0 if s <= 15 else 84.0 if s <= 30 else 69.0 if s <= 45
            else 35.0 if s <= 60 else 35.0 if s <= 300 else 25.0 if s <= 600 else 20.0 if s <= 900
            else 10.0 if s <= 3600 else 8.0)


def _day_ord(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).toordinal()


def detect(bars: Sequence[Bar], params: Params = Params(), *, tf_seconds: int) -> dict:
    n = len(bars)
    o = [b.open for b in bars]; h = [b.high for b in bars]; lo = [b.low for b in bars]
    c = [b.close for b in bars]; v = [b.volume for b in bars]; ts = [b.ts for b in bars]
    P = params

    th_1x = _f_rvol_1x(tf_seconds)
    th_saab_kratos = th_1x * 0.56
    th_gs_moab = _f_gs_moab(tf_seconds)
    th_wtc = th_1x * 2.0
    th_hiroshima = _f_gs_moab(tf_seconds)

    # bull/bear normalized price
    bb_spike = [abs(c[i] - o[i]) for i in range(n)]
    sma_spike_1 = shift(sma(bb_spike, P.bb_avgLength), 1)
    bb_np = [bb_spike[i] / nz(sma_spike_1[i], 1.0) for i in range(n)]
    sma_vol_1 = shift(sma(v, P.bb_avgLength), 1)
    bb_nv = [v[i] / nz(sma_vol_1[i], 1.0) for i in range(n)]
    bb_diff = [bb_np[i] - bb_nv[i] for i in range(n)]
    bb_posdiff = [(d if d > 0 else None) for d in bb_diff]
    bb_smadiff = sma(bb_posdiff, P.bb_smaLength)

    def pos_gt(i):
        return bb_posdiff[i] is not None and bb_smadiff[i] is not None and bb_posdiff[i] > bb_smadiff[i]

    bull_base = [c[i] > o[i] and pos_gt(i) for i in range(n)]
    bear_base = [c[i] < o[i] and pos_gt(i) for i in range(n)]
    conf = [True] * n

    def in_rng(x, a, bb):
        return a <= x < bb

    sigSAAB = [conf[i] and bull_base[i] and in_rng(bb_np[i], th_saab_kratos, th_1x) for i in range(n)]
    sigKratos = [conf[i] and bear_base[i] and in_rng(bb_np[i], th_saab_kratos, th_1x) for i in range(n)]
    sigBull1x = [conf[i] and bull_base[i] and in_rng(bb_np[i], th_1x, th_gs_moab) for i in range(n)]
    sigBear1x = [conf[i] and bear_base[i] and in_rng(bb_np[i], th_1x, th_gs_moab) for i in range(n)]
    sigGrandSlam = [conf[i] and bull_base[i] and bb_np[i] >= th_gs_moab for i in range(n)]
    sigMOAB = [conf[i] and bear_base[i] and bb_np[i] >= th_gs_moab for i in range(n)]

    # reg @ time
    rv = relative_volume(v, P.reg_length, anchor_timeframe=P.reg_anchor,
                         is_cumulative=P.reg_cumulative, bar_timestamps=ts)
    relVol = [(rv.vol_ratio[i] or 0.0) for i in range(n)]
    rvv = [rv.vol_ratio[i] is not None for i in range(n)]
    sigWTC = [conf[i] and rvv[i] and relVol[i] > th_wtc and relVol[i] <= th_hiroshima for i in range(n)]
    sigHiroshima = [conf[i] and rvv[i] and relVol[i] > th_hiroshima for i in range(n)]

    # hybrid momentum reg(non-cum) + cum
    rvReg = relative_volume(v, P.reg_length, anchor_timeframe=P.reg_anchor, is_cumulative=False, bar_timestamps=ts)
    rvCum = relative_volume(v, P.reg_length, anchor_timeframe=P.reg_anchor, is_cumulative=True, bar_timestamps=ts)
    hybRegRatio = [(rvReg.vol_ratio[i] or 0.0) for i in range(n)]
    hybCumRatio = [(rvCum.vol_ratio[i] or 0.0) for i in range(n)]
    hregv = [rvReg.vol_ratio[i] is not None and rvCum.vol_ratio[i] is not None for i in range(n)]
    body = [abs(c[i] - o[i]) for i in range(n)]
    rng = [h[i] - lo[i] for i in range(n)]
    bodyRat = [(0.0 if rng[i] == 0 else body[i] / rng[i]) for i in range(n)]

    # auto-derive ladder (from Hiroshima threshold)
    H = th_hiroshima
    if P.hyb_autoDerive:
        reg1 = H * 2.85; reg5 = H * 1.1875; step = (reg1 - reg5) / 4.0
        regs = [reg1, reg1 - step, reg1 - 2 * step, reg1 - 3 * step, reg5]
        phi = 1.398 * 1.33
        cums = [phi * math.sqrt(math.log(r)) for r in regs]
        bodies = [0.69, 0.72, 0.75, 0.78, 0.81]
    else:
        regs = [P.hyb_addReg] * 5
        cums = [P.hyb_addCum] * 5
        bodies = [P.hyb_bodyRat] * 5

    def hyb_dir(i, t, want_bull):
        if not (conf[i] and hregv[i]):
            return False
        if not (hybRegRatio[i] > regs[t] and hybCumRatio[i] > cums[t] and bodyRat[i] >= bodies[t]):
            return False
        return (c[i] > o[i]) if want_bull else (c[i] < o[i])

    sigLong1 = [hyb_dir(i, 0, True) for i in range(n)]
    sigShort1 = [hyb_dir(i, 0, False) for i in range(n)]
    sigLong2 = [hyb_dir(i, 1, True) for i in range(n)]
    sigShort2 = [hyb_dir(i, 1, False) for i in range(n)]
    sigLong3 = [hyb_dir(i, 2, True) for i in range(n)]
    sigLong4 = [hyb_dir(i, 3, True) for i in range(n)]
    sigLong5 = [hyb_dir(i, 4, True) for i in range(n)]

    # Nagasaki
    sigNagasaki = [False] * n
    mx = 0.0
    for i in range(n):
        if i == 0:
            mx = v[i]
        elif v[i] > mx:
            sigNagasaki[i] = True; mx = v[i]
    if not P.enableNagasaki:
        sigNagasaki = [False] * n

    # IPSF sequences
    def seq_in(x, lo_t):
        return x > lo_t and x < P.seq_th_high

    def run_seq(low_th, seq_th, target_len, bullside):
        out = [False] * n
        run_len = 0; run_sum = 0.0
        for i in range(n):
            base = bull_base[i] if bullside else bear_base[i]
            qual = base and seq_in(bb_np[i], low_th)
            if qual:
                run_len += 1; run_sum += bb_np[i]
            else:
                run_len = 0; run_sum = 0.0
            out[i] = conf[i] and run_len == target_len and run_sum >= seq_th
        return out

    sig_UU = run_seq(P.th_low_UU_DD, P.seqTh_UU_DD, 2, True)
    sig_UUU = run_seq(P.th_low_UUU_DDD, P.seqTh_UUU_DDD, 3, True)
    sig_UUUU = run_seq(P.th_low_UUUU_DDDD, P.seqTh_UUUU_DDDD, 4, True)
    sig_DD = run_seq(P.th_low_UU_DD, P.seqTh_UU_DD, 2, False)
    sig_DDD = run_seq(P.th_low_UUU_DDD, P.seqTh_UUU_DDD, 3, False)
    sig_DDDD = run_seq(P.th_low_UUUU_DDDD, P.seqTh_UUUU_DDDD, 4, False)

    # back-to-back
    s1 = lambda a, i: bool(a[i - 1]) if i >= 1 else False
    sig_B2B_2xSAAB = [conf[i] and s1(sigSAAB, i) and sigSAAB[i] for i in range(n)]
    sig_B2B_2xKratos = [conf[i] and s1(sigKratos, i) and sigKratos[i] for i in range(n)]
    sig_B2B_2xBull1x = [conf[i] and s1(sigBull1x, i) and sigBull1x[i] for i in range(n)]
    sig_B2B_2xBear1x = [conf[i] and s1(sigBear1x, i) and sigBear1x[i] for i in range(n)]
    sig_B2B_MidBull = [conf[i] and not sig_B2B_2xSAAB[i] and not sig_B2B_2xBull1x[i] and ((s1(sigSAAB, i) and sigBull1x[i]) or (s1(sigBull1x, i) and sigSAAB[i])) for i in range(n)]
    sig_B2B_MidBear = [conf[i] and not sig_B2B_2xKratos[i] and not sig_B2B_2xBear1x[i] and ((s1(sigKratos, i) and sigBear1x[i]) or (s1(sigBear1x, i) and sigKratos[i])) for i in range(n)]

    # displacement
    disp_rng = [abs(o[i] - c[i]) if P.disp_type_otc else h[i] - lo[i] for i in range(n)]
    disp_std = stdev(disp_rng, P.std_len)
    th_min = [(disp_std[i] * P.std_min) if disp_std[i] is not None else None for i in range(n)]
    th_max = [(disp_std[i] * P.std_max) if disp_std[i] is not None else None for i in range(n)]
    th_min_1 = shift(th_min, 1); th_max_1 = shift(th_max, 1); disp_rng_1 = shift(disp_rng, 1)
    prevDisp = [(disp_rng_1[i] is not None and th_min_1[i] is not None and th_max_1[i] is not None and disp_rng_1[i] > th_min_1[i] and disp_rng_1[i] <= th_max_1[i]) for i in range(n)]
    bullFVG = [i >= 2 and lo[i] > h[i - 2] and o[i - 1] < c[i - 1] for i in range(n)]
    bearFVG = [i >= 2 and h[i] < lo[i - 2] and o[i - 1] > c[i - 1] for i in range(n)]
    sigDispBull = [prevDisp[i] and bullFVG[i] for i in range(n)]
    sigDispBear = [prevDisp[i] and bearFVG[i] for i in range(n)]
    bullStreak = [0] * n; bearStreak = [0] * n
    bs = 0; br = 0
    for i in range(n):
        bs = bs + 1 if sigDispBull[i] else 0
        br = br + 1 if sigDispBear[i] else 0
        bullStreak[i] = bs; bearStreak[i] = br
    sigCDispBull2 = [sigDispBull[i] and bullStreak[i] >= 2 for i in range(n)]
    sigCDispBear2 = [sigDispBear[i] and bearStreak[i] >= 2 for i in range(n)]
    sigCDispBull3 = [sigDispBull[i] and bullStreak[i] >= 3 for i in range(n)]
    sigCDispBear3 = [sigDispBear[i] and bearStreak[i] >= 3 for i in range(n)]

    # HV NRA on [1]
    def hv_rank(period):
        hp = shift(highest(v, period), 1)
        v1 = shift(v, 1)
        return [hp[i] is not None and v1[i] is not None and v1[i] == hp[i] for i in range(n)]

    is75 = hv_rank(75); is150 = hv_rank(150); is250 = hv_rank(250); is500 = hv_rank(500); is1000 = hv_rank(1000)
    # hotspot windows (on [1]) — use bar i-1's calendar fields
    def hotspot(i):
        if i < 1:
            return False
        dt = datetime.fromtimestamp(ts[i - 1] / 1000, tz=timezone.utc)
        dom = dt.day; mo = dt.month; dow = dt.isoweekday()  # Mon=1
        opEx = 10 <= dom <= 17 and 1 <= dow <= 3
        qtr = mo in (3, 6, 9, 12) and 23 <= dom <= 27
        russ = mo == 6 and 19 <= dom <= 24
        taxl = mo == 12 and 21 <= dom <= 26
        jan = mo == 12 and 27 <= dom <= 30
        hfr = mo in (5, 11) and 10 <= dom <= 13
        return opEx or qtr or russ or taxl or jan or hfr
    isHotSpot = [hotspot(i) for i in range(n)]
    plot_HV1000 = is1000
    plot_HV500 = [is500[i] and not is1000[i] for i in range(n)]
    plot_HV250 = [is250[i] and not is500[i] and not is1000[i] for i in range(n)]
    plot_HV150 = [is150[i] and not is250[i] and not is500[i] and not is1000[i] for i in range(n)]
    plot_HV75 = [is75[i] and not is150[i] and not is250[i] and not is500[i] and not is1000[i] for i in range(n)]
    plot_HS = isHotSpot

    # FAUNA (boolean active; text resolution is in alert payload, not a plot)
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
            # the file's FAUNA uses hierarchical text but the ACTIVE condition is simply
            # "any family present" (fn_bullText != ""). The exclusions are NOT applied in
            # this file's fauna (unlike the matrix file) — fn_bullActive = any-of-8 present.
            present = MB or RE or TA or GG or TR or ES or GDR
            out[i] = conf[i] and present
        return out

    faunaBull = fauna(True)
    faunaBear = fauna(False)

    fires = {
        "SAAB": sigSAAB, "Kratos": sigKratos, "BullRVOL1x": sigBull1x, "BearRVOL1x": sigBear1x,
        "GrandSlam": sigGrandSlam, "MOAB": sigMOAB, "WTC": sigWTC, "Hiroshima": sigHiroshima, "Nagasaki": sigNagasaki,
        "UU": sig_UU, "UUU": sig_UUU, "UUUU": sig_UUUU, "DD": sig_DD, "DDD": sig_DDD, "DDDD": sig_DDDD,
        "B2B_2xSAAB": sig_B2B_2xSAAB, "B2B_2xKratos": sig_B2B_2xKratos, "B2B_2xBull1x": sig_B2B_2xBull1x,
        "B2B_2xBear1x": sig_B2B_2xBear1x, "B2B_MidBull": sig_B2B_MidBull, "B2B_MidBear": sig_B2B_MidBear,
        "Long1": sigLong1, "Short1": sigShort1, "Long2": sigLong2, "Short2": sigShort2,
        "Long3": sigLong3, "Long4": sigLong4, "Long5": sigLong5,
        "DispBull": sigDispBull, "DispBear": sigDispBear, "CDispBull2": sigCDispBull2, "CDispBear2": sigCDispBear2,
        "CDispBull3": sigCDispBull3, "CDispBear3": sigCDispBear3,
        "HV75": plot_HV75, "HV150": plot_HV150, "HV250": plot_HV250, "HV500": plot_HV500, "HV1000": plot_HV1000,
        "HotSpot": plot_HS, "FaunaBull": faunaBull, "FaunaBear": faunaBear,
    }
    # offsets: displacement (-1), disp-cons (-1), HV (-1) paint the prior bar; rest offset 0.
    off1 = {"DispBull", "DispBear", "CDispBull2", "CDispBear2", "CDispBull3", "CDispBear3",
            "HV75", "HV150", "HV250", "HV500", "HV1000", "HotSpot"}
    events = []
    for k, arr in fires.items():
        offv = -1 if k in off1 else 0
        for i in range(n):
            if arr[i]:
                j = i + offv
                if 0 <= j < n:
                    events.append((ts[j] * 1_000_000, k))
    events.sort()
    return {"fires": fires, "events": events, "series": {"relVol": relVol, "th_hiroshima": [th_hiroshima] * n}}
