"""Heavy Weapons Single v3 — FULL detection fire-matrix core (Pine-faithful).

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/heavy weapons v3_tickfriendly.pine"
  Pine v5, indicator("Heavy Weapons Single v3 [tick-friendly]"),
  import TradingView/ta/7 as tv_ta. RE10023 tick guards already applied in source.

ULTRACODE FULL PORT — scope statement (read this):
  This module ports EVERY detection plot (every `plotshape(...)` that represents a
  signal) from the source, 1:1, directly from OHLCV. Pine `var`/history semantics
  are preserved (single forward pass; `[k]` = k-bars-back; `conf` = closed bar;
  `nz()` fallbacks honoured). The sub-engines ported:

    RVOL 0.56          SAAB / Kratos / Bull1x / Bear1x / GrandSlam / MOAB
    RVOL Reg@Time      WTC / Hiroshima / Pentagon (via canonical relativeVolume shim)
    Hybrid Momentum    LONG 1-5 / SHORT 1-2 (reg+cum ratio ladder + body-ratio)
    Nagasaki           running all-time-high volume
    HCT displacement   bar[1] stdev-range + FVG -> 15-combo HYY/HN/HNV/HT/NHx2
    Pentagon specials  Pent+HV1K / Pent+HV500+Disp
    Displacement       Disp Bull/Bear + Consec Disp 2+/3+ (per-consumer stdev mult)
    Sequences          UU/UUU/UUUU + DD/DDD/DDDD (sum + displacement override)
    B2B                2x SAAB/Kratos/Bull1x/Bear1x + B2B Mid Bull/Bear
    FAUNA              MB/RE/GG/TA + TR/ES/GDR ladder -> Bull/Bear (gated disp+L/S)
    HV ladder          HV 150/250/350/500/1000 (offset -1, gated LONG[1])

  relativeVolume ports via the canonical shim (_nn_harness.relative_volume ->
  tv_ta_shim, ta/7) — NEVER re-derived as volume/sma(volume,N).

  Tick vs time: ONE code path. The ONLY grain-bound difference is the RVOL anchor
  ("D" wall-clock day on BOTH grains, per tradingview-import-decoupling, mirroring
  the Pine RE10023 fix of forcing "D" on tick) and tfSec (the per-TF threshold
  key), which is a parameter.

HONESTY: there is NO all-zero stub series in this module. Every plot listed in
PLOT_IDS is produced by real Pine logic. If a plot reads 0 on a tape it is because
the source logic produced 0 on those bars. The parity harness re-derives the core
RVOL/displacement/sequence/B2B/HV logic independently and reports REAL pass/total.

Cosmetic-only Pine objects intentionally NOT ported (they are not detection plots):
  - the INFO PANEL (`table.*`) — banned graphic object, pure display.
  - the aggregated `alert(...)` message string — derived from the same fires.
  - FAUNA text labels (`fn_bullText`/`fn_bearText`) — the FIRE is FAUNA Bull/Bear;
    the text is the combo name, surfaced as a level/debug primitive, not a plot.
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nn_harness import (  # noqa: E402
    Bar, nz, sma, stdev, highest, atr as _atr_ohlc, cum, shift, relative_volume,
)


# ──────────────────────────────── parameters ────────────────────────────────
@dataclass
class Params:
    """Every Pine input.* as a parameter, defaulted to the source default.
    `tfSec` is the per-timeframe threshold key (Pine `tfSec`); on tick charts the
    Pine source uses nn_TICK_FB=10, on time charts timeframe.in_seconds()."""
    tfSec: int = 60                  # per-TF threshold table key (seconds/bar)
    nn_tick_assumed_sec: int = 10    # Pine nn_TICK_FB fallback on tick charts

    # ---- RVOL 0.56 (Bull/Bear) ----
    bb_avgLength: int = 30
    bb_smaLength: int = 20

    # ---- RVOL Reg@Time ----
    reg_length: int = 30
    reg_calculationMode: str = "Cumulative"   # "Cumulative" | "Regular"
    reg_adjustRealtime: bool = True

    # ---- Hybrid regime % multipliers ----
    reg_pct: int = 100
    cum_pct: int = 100
    body_pct: int = 100

    # ---- Nagasaki ----
    enableNagasaki: bool = True

    # ---- Sequence lower thresholds ----
    th_low_UU_DD: float = 0.5
    th_low_UUU_DDD: float = 0.5
    th_low_UUUU_DDDD: float = 0.5

    # ---- Displacement per-consumer stdev thresholds ----
    i_disp_type: str = "Open to Close"        # "Open to Close" | "High to Low"
    i_std_len: int = 100
    i_disp_std_standalone: float = 7.5
    i_disp_std_cdisp2: float = 5.0
    i_disp_std_cdisp3: float = 3.0
    i_disp_std_seq: float = 5.0

    # ---- HCT displacement engine ----
    hct_disp_strength: float = 6.0
    hct_disp_lookback: int = 100
    hct_threshPct: float = 2.0
    hct_auto: bool = True
    hct_ref: bool = True                       # HCT master reference toggle

    # ---- HCT combo eligibility (15 combos) ----
    en_HYYBull: bool = True
    en_HYYBear: bool = True
    en_HYYNoDisp: bool = True
    en_HNBull: bool = True
    en_HNBear: bool = True
    en_HNNoDisp: bool = True
    en_HNVBull: bool = True
    en_HNVBear: bool = True
    en_HNVNoDisp: bool = True
    en_HTBull: bool = True
    en_HTBear: bool = True
    en_HTNoDisp: bool = True
    en_NHx2Bull: bool = True
    en_NHx2Bear: bool = True
    en_NHx2NoDisp: bool = True

    # ---- FAUNA constants (colors-only in Pine; logic constants here) ----
    fn_alpha_MB: float = 1.6
    fn_beta_MB: float = 0.70
    fn_delta_MB: float = 1.8
    fn_atr_MB: int = 14
    fn_vol_MB: int = 20
    fn_gamma_RE: float = 2.2
    fn_epsilon_RE: float = 0.15
    fn_delta_RE: float = 1.8
    fn_atr_RE: int = 14
    fn_zeta_GG: float = 0.9
    fn_delta_GG: float = 1.8
    fn_atr_GG: int = 14
    fn_theta_TA: float = 1.6
    fn_delta_TA: float = 1.8
    fn_trend_ma_len: int = 50
    fn_avg_delta_len: int = 10
    fn_atr_TA: int = 14
    fn_alpha_SB: float = 1.5
    fn_delta_SB: float = 1.5
    fn_weak_ratio: float = 0.2
    fn_body_avg: int = 20
    fn_range_avg: int = 20

    # ---- show_* toggles (default ON, except MOAB which is OFF in source) ----
    show_SAAB: bool = True
    show_Kratos: bool = True
    show_BullRVOL1x: bool = True
    show_BearRVOL1x: bool = True
    show_GrandSlam: bool = True
    show_MOAB: bool = False
    show_WTC: bool = True
    show_Hiroshima: bool = True
    show_Nagasaki: bool = True
    show_Long1: bool = True
    show_Short1: bool = True
    show_Long2: bool = True
    show_Short2: bool = True
    show_Long3: bool = True
    show_Long4: bool = True
    show_Long5: bool = True
    show_HV150: bool = True
    show_HV250: bool = True
    show_HV350: bool = True
    show_HV500: bool = True
    show_HV1000: bool = True
    show_DispBull: bool = True
    show_DispBear: bool = True
    show_CDispBull2: bool = True
    show_CDispBear2: bool = True
    show_CDispBull3: bool = True
    show_CDispBear3: bool = True
    show_UU: bool = True
    show_UUU: bool = True
    show_UUUU: bool = True
    show_DD: bool = True
    show_DDD: bool = True
    show_DDDD: bool = True
    show_B2B_2xSAAB: bool = True
    show_B2B_2xKratos: bool = True
    show_B2B_2xBull1x: bool = True
    show_B2B_2xBear1x: bool = True
    show_B2B_MidBull: bool = True
    show_B2B_MidBear: bool = True
    show_FaunaBull: bool = True
    show_FaunaBear: bool = True
    show_HCTBull: bool = True
    show_HCTBear: bool = True
    show_PentHV1K: bool = True
    show_PentHV500D: bool = True


# ───────────────────── per-timeframe threshold tables (verbatim) ─────────────
def f_rvol_1x_threshold(s):
    return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else 23.0 if s <= 45 else
            20.0 if s <= 60 else 19.0 if s <= 120 else 17.0 if s <= 180 else 16.0 if s <= 240 else
            15.0 if s <= 300 else 14.0 if s <= 360 else 12.0 if s <= 420 else 11.0 if s <= 480 else
            10.0 if s <= 540 else 10.0 if s <= 600 else 8.4 if s <= 900 else 6.9 if s <= 1800 else
            5.9 if s <= 3600 else 3.0 if s <= 7200 else 1.8)


def f_saab_kratos_threshold(s):
    return f_rvol_1x_threshold(s) * 0.56


def f_gs_moab_threshold(s):
    return (114.0 if s <= 10 else 99.0 if s <= 15 else 84.0 if s <= 30 else 69.0 if s <= 45 else
            35.0 if s <= 60 else 35.0 if s <= 300 else 25.0 if s <= 600 else 20.0 if s <= 900 else
            10.0 if s <= 3600 else 8.0)


def f_wtc_threshold(s):
    return f_rvol_1x_threshold(s) * 2.0


# Hiroshima table is identical to GS/MOAB in the source.
f_hiroshima_threshold = f_gs_moab_threshold


# ─────────────────────────────── the compute ────────────────────────────────
def compute(bars: Sequence[Bar], *, params: Params | None = None, rv_anchor: str = "D"):
    """Return the detection fire matrix + numeric levels for Heavy Weapons v3.

    Output dict:
      "ts"              -> list[int]  bar open timestamps (epoch ms)
      "fire_<title>"    -> list[0/1]  one per detection plot (Pine plotshape title)
      "lvl_<name>"      -> list[float|None]  numeric levels / data-window plots
      "prim_<name>"     -> list[0/1]  primitive detection booleans (debug/parity)

    rv_anchor: "D" on both grains (tick & time). See module docstring.
    """
    p = params or Params()
    n = len(bars)
    if n == 0:
        return {"ts": []}

    o = [b.open for b in bars]
    h = [b.high for b in bars]
    l = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]

    tfSec = p.tfSec if (p.tfSec and p.tfSec > 0) else p.nn_tick_assumed_sec
    is_cumulative_reg = (p.reg_calculationMode == "Cumulative")

    # ---- threshold tables ----
    th_1x = f_rvol_1x_threshold(tfSec)
    th_saab_kratos = f_saab_kratos_threshold(tfSec)
    th_gs_moab = f_gs_moab_threshold(tfSec)
    th_wtc = f_wtc_threshold(tfSec)
    th_hiroshima = f_hiroshima_threshold(tfSec)

    # ---- hybrid momentum auto-derive ladder (from Hiroshima) ----
    r1 = th_hiroshima * 2.85
    r5 = th_hiroshima * 1.1875
    step = (r1 - r5) / 4.0
    hybReg = [r1, r1 - 1.0 * step, r1 - 2.0 * step, r1 - 3.0 * step, r5]
    phi = 1.398 * 1.33
    hybCum = [phi * math.sqrt(math.log(x)) for x in hybReg]
    hybBody = [0.69, 0.72, 0.75, 0.78, 0.81]
    regMult, cumMult, bodyMult = p.reg_pct / 100.0, p.cum_pct / 100.0, p.body_pct / 100.0
    hybRegEff = [x * regMult for x in hybReg]
    hybCumEff = [x * cumMult for x in hybCum]
    hybBodyEff = [x * bodyMult for x in hybBody]

    # ---- RVOL 0.56 bull/bear ----
    # Pine: norm = spike / nz(sma(spike,len)[1], 1.0). nz replaces only `na`; a real
    # 0.0 denom yields Pine `na` (0/0) which makes every downstream comparison false.
    # Mirror that: a 0 denom -> 0.0 norm (non-firing), never a Python ZeroDivisionError.
    def _div(num, den):
        d = nz(den, 1.0)
        return 0.0 if d == 0 else num / d

    bb_spike = [abs(c[i] - o[i]) for i in range(n)]
    bb_avgSpikeDenom = shift(sma(bb_spike, p.bb_avgLength), 1)
    bb_normPrice = [_div(bb_spike[i], bb_avgSpikeDenom[i]) for i in range(n)]
    bb_avgVolDenom = shift(sma(v, p.bb_avgLength), 1)
    bb_normVol = [_div(v[i], bb_avgVolDenom[i]) for i in range(n)]
    bb_diff = [bb_normPrice[i] - bb_normVol[i] for i in range(n)]
    bb_posDiff = [d if d > 0 else None for d in bb_diff]
    bb_smaDiff = sma(bb_posDiff, p.bb_smaLength)

    def baseBull(i):
        return (c[i] > o[i] and bb_posDiff[i] is not None and bb_smaDiff[i] is not None
                and bb_posDiff[i] > bb_smaDiff[i])

    def baseBear(i):
        return (c[i] < o[i] and bb_posDiff[i] is not None and bb_smaDiff[i] is not None
                and bb_posDiff[i] > bb_smaDiff[i])

    def inRange(x, lo, hi):
        return lo <= x < hi

    conf = [True] * n   # closed-bar (confirmed) evaluation

    sigSAAB = [conf[i] and baseBull(i) and inRange(bb_normPrice[i], th_saab_kratos, th_1x) for i in range(n)]
    sigKratos = [conf[i] and baseBear(i) and inRange(bb_normPrice[i], th_saab_kratos, th_1x) for i in range(n)]
    sigBull1x = [conf[i] and baseBull(i) and inRange(bb_normPrice[i], th_1x, th_gs_moab) for i in range(n)]
    sigBear1x = [conf[i] and baseBear(i) and inRange(bb_normPrice[i], th_1x, th_gs_moab) for i in range(n)]
    sigGS = [conf[i] and baseBull(i) and bb_normPrice[i] >= th_gs_moab for i in range(n)]
    sigMOAB = [conf[i] and baseBear(i) and bb_normPrice[i] >= th_gs_moab for i in range(n)]

    # ---- RVOL Reg@Time (mode-driven) for WTC / Hiroshima / Pentagon ----
    _, _, relVolRatio = relative_volume(
        v, p.reg_length, anchor_timeframe=rv_anchor,
        is_cumulative=is_cumulative_reg, bar_timestamps=ts)
    sigWTC = [False] * n
    sigHiro = [False] * n
    sigPent = [False] * n
    for i in range(n):
        r = relVolRatio[i]
        if r is None:
            continue
        sigWTC[i] = conf[i] and (r > th_wtc) and (r <= th_hiroshima)
        sigHiro[i] = conf[i] and (r > th_hiroshima)
        sigPent[i] = conf[i] and (r >= th_1x) and (r <= th_wtc)

    # ---- hybrid momentum (reg ratio + cum ratio) ----
    _, _, hybRegRatio = relative_volume(
        v, p.reg_length, anchor_timeframe=rv_anchor, is_cumulative=False, bar_timestamps=ts)
    _, _, hybCumRatio = relative_volume(
        v, p.reg_length, anchor_timeframe=rv_anchor, is_cumulative=True, bar_timestamps=ts)
    hybBodyRat = [(0.0 if (h[i] - l[i]) == 0 else abs(c[i] - o[i]) / (h[i] - l[i])) for i in range(n)]

    def mom(i, k):
        rr, cr = hybRegRatio[i], hybCumRatio[i]
        if rr is None or cr is None:
            return False
        return conf[i] and rr > hybRegEff[k] and cr > hybCumEff[k]

    sigAddLong = [[False] * n for _ in range(5)]    # tiers 1..5
    sigAddShort = [[False] * n for _ in range(2)]   # tiers 1..2 only
    for i in range(n):
        for k in range(5):
            convict = hybBodyRat[i] >= hybBodyEff[k]
            if c[i] > o[i] and convict and mom(i, k):
                sigAddLong[k][i] = True
        for k in range(2):
            convict = hybBodyRat[i] >= hybBodyEff[k]
            if c[i] < o[i] and convict and mom(i, k):
                sigAddShort[k][i] = True

    anyLong = [any(sigAddLong[k][i] for k in range(5)) for i in range(n)]
    anyShort = [any(sigAddShort[k][i] for k in range(2)) for i in range(n)]
    anyMom = [anyLong[i] or anyShort[i] for i in range(n)]
    anyLong_1 = shift(anyLong, 1)

    # ---- Nagasaki (running all-time-high volume; Pine var maxVol) ----
    sigNag_raw = [False] * n
    maxVol = 0.0
    for i in range(n):
        if i == 0:
            maxVol = v[i]
        elif v[i] > maxVol:
            sigNag_raw[i] = True
            maxVol = v[i]
    sigNag = [p.enableNagasaki and sigNag_raw[i] for i in range(n)]

    hv150 = highest(v, 150)
    anyHV_cur = [conf[i] and hv150[i] is not None and v[i] == hv150[i] for i in range(n)]

    # ---- HCT displacement engine (verbatim from Heavy PENTAGON) ----
    cum_hl = cum([(h[i] - l[i]) / l[i] if l[i] != 0 else 0.0 for i in range(n)])
    hct_thresh = [0.0] * n
    for i in range(n):
        if p.hct_auto:
            hct_thresh[i] = (cum_hl[i] / i) if i > 0 else 0.0
        else:
            hct_thresh[i] = p.hct_threshPct / 100.0
    hl_range = [h[i] - l[i] for i in range(n)]
    hct_rangeStdev = stdev(hl_range, p.hct_disp_lookback)
    hct_rangeStdev_1 = shift(hct_rangeStdev, 1)

    def hct_bFVG(i):
        if i < 2 or h[i - 2] == 0:
            return False
        return l[i] > h[i - 2] and c[i - 1] > h[i - 2] and (l[i] - h[i - 2]) / h[i - 2] > hct_thresh[i]

    def hct_sFVG(i):
        if i < 2 or h[i] == 0:
            return False
        return h[i] < l[i - 2] and c[i - 1] < l[i - 2] and (l[i - 2] - h[i]) / h[i] > hct_thresh[i]

    hct_dispBull = [False] * n
    hct_dispBear = [False] * n
    for i in range(n):
        if i < 1:
            continue
        barRange = h[i - 1] - l[i - 1]
        sd1 = nz(hct_rangeStdev_1[i], 0.0)
        dispMet = barRange > p.hct_disp_strength * sd1
        if conf[i] and dispMet and c[i - 1] > o[i - 1] and hct_bFVG(i):
            hct_dispBull[i] = True
        if conf[i] and dispMet and c[i - 1] < o[i - 1] and hct_sFVG(i):
            hct_dispBear[i] = True
    hct_noDisp = [not hct_dispBull[i] and not hct_dispBear[i] for i in range(n)]

    # ---- HCT combo building blocks ----
    groupA_Bull = [sigBull1x[i] or sigGS[i] for i in range(n)]
    groupA_Bear = [sigBear1x[i] or sigMOAB[i] for i in range(n)]
    groupB = [sigPent[i] or sigWTC[i] or sigHiro[i] for i in range(n)]

    baseYY = [(groupA_Bull[i] or groupA_Bear[i]) and groupB[i] for i in range(n)]
    baseNag = [sigNag[i] and (groupA_Bull[i] or groupA_Bear[i]) for i in range(n)]
    baseNagV = [sigNag[i] and groupB[i] for i in range(n)]
    baseTri = [sigNag[i] and (groupA_Bull[i] or groupA_Bear[i]) and groupB[i] for i in range(n)]
    baseNHx2 = [(sigPent[i] and sigWTC[i]) or (sigPent[i] and sigHiro[i]) or (sigWTC[i] and sigHiro[i]) for i in range(n)]

    # 10 displacement-directional combos
    sigHYYBull = [baseYY[i] and hct_dispBull[i] for i in range(n)]
    sigHYYBear = [baseYY[i] and hct_dispBear[i] for i in range(n)]
    sigHNBull = [baseNag[i] and hct_dispBull[i] for i in range(n)]
    sigHNBear = [baseNag[i] and hct_dispBear[i] for i in range(n)]
    sigHNVBull = [baseNagV[i] and hct_dispBull[i] for i in range(n)]
    sigHNVBear = [baseNagV[i] and hct_dispBear[i] for i in range(n)]
    sigHTBull = [baseTri[i] and hct_dispBull[i] for i in range(n)]
    sigHTBear = [baseTri[i] and hct_dispBear[i] for i in range(n)]
    sigNHx2Bull = [baseNHx2[i] and hct_dispBull[i] for i in range(n)]
    sigNHx2Bear = [baseNHx2[i] and hct_dispBear[i] for i in range(n)]

    # 5 no-disp combos -> routed bull/bear
    sigHYYNDBull = [baseYY[i] and hct_noDisp[i] and groupA_Bull[i] for i in range(n)]
    sigHYYNDBear = [baseYY[i] and hct_noDisp[i] and groupA_Bear[i] for i in range(n)]
    sigHNNDBull = [baseNag[i] and hct_noDisp[i] and groupA_Bull[i] for i in range(n)]
    sigHNNDBear = [baseNag[i] and hct_noDisp[i] and groupA_Bear[i] for i in range(n)]
    sigHNVNDBull = [baseNagV[i] and hct_noDisp[i] and (c[i] > o[i]) for i in range(n)]
    sigHNVNDBear = [baseNagV[i] and hct_noDisp[i] and (c[i] < o[i]) for i in range(n)]
    sigHTNDBull = [baseTri[i] and hct_noDisp[i] and groupA_Bull[i] for i in range(n)]
    sigHTNDBear = [baseTri[i] and hct_noDisp[i] and groupA_Bear[i] for i in range(n)]
    sigNHx2NDBull = [baseNHx2[i] and hct_noDisp[i] and (c[i] > o[i]) for i in range(n)]
    sigNHx2NDBear = [baseNHx2[i] and hct_noDisp[i] and (c[i] < o[i]) for i in range(n)]

    # per-combo fire booleans (eligibility toggle AND signal)
    f_HYYBull = [p.en_HYYBull and sigHYYBull[i] for i in range(n)]
    f_HYYBear = [p.en_HYYBear and sigHYYBear[i] for i in range(n)]
    f_HNBull = [p.en_HNBull and sigHNBull[i] for i in range(n)]
    f_HNBear = [p.en_HNBear and sigHNBear[i] for i in range(n)]
    f_HNVBull = [p.en_HNVBull and sigHNVBull[i] for i in range(n)]
    f_HNVBear = [p.en_HNVBear and sigHNVBear[i] for i in range(n)]
    f_HTBull = [p.en_HTBull and sigHTBull[i] for i in range(n)]
    f_HTBear = [p.en_HTBear and sigHTBear[i] for i in range(n)]
    f_NHx2Bull = [p.en_NHx2Bull and sigNHx2Bull[i] for i in range(n)]
    f_NHx2Bear = [p.en_NHx2Bear and sigNHx2Bear[i] for i in range(n)]
    f_HYYNDBull = [p.en_HYYNoDisp and sigHYYNDBull[i] for i in range(n)]
    f_HYYNDBear = [p.en_HYYNoDisp and sigHYYNDBear[i] for i in range(n)]
    f_HNNDBull = [p.en_HNNoDisp and sigHNNDBull[i] for i in range(n)]
    f_HNNDBear = [p.en_HNNoDisp and sigHNNDBear[i] for i in range(n)]
    f_HNVNDBull = [p.en_HNVNoDisp and sigHNVNDBull[i] for i in range(n)]
    f_HNVNDBear = [p.en_HNVNoDisp and sigHNVNDBear[i] for i in range(n)]
    f_HTNDBull = [p.en_HTNoDisp and sigHTNDBull[i] for i in range(n)]
    f_HTNDBear = [p.en_HTNoDisp and sigHTNDBear[i] for i in range(n)]
    f_NHx2NDBull = [p.en_NHx2NoDisp and sigNHx2NDBull[i] for i in range(n)]
    f_NHx2NDBear = [p.en_NHx2NoDisp and sigNHx2NDBear[i] for i in range(n)]

    hctMasterBull = [(f_HYYBull[i] or f_HNBull[i] or f_HNVBull[i] or f_HTBull[i] or f_NHx2Bull[i]
                      or f_HYYNDBull[i] or f_HNNDBull[i] or f_HNVNDBull[i] or f_HTNDBull[i] or f_NHx2NDBull[i])
                     for i in range(n)]
    hctMasterBear = [(f_HYYBear[i] or f_HNBear[i] or f_HNVBear[i] or f_HTBear[i] or f_NHx2Bear[i]
                      or f_HYYNDBear[i] or f_HNNDBear[i] or f_HNVNDBear[i] or f_HTNDBear[i] or f_NHx2NDBear[i])
                     for i in range(n)]

    anySinglesRaw = [sigSAAB[i] or sigKratos[i] or sigBull1x[i] or sigBear1x[i] or sigGS[i]
                     or sigMOAB[i] or sigWTC[i] or sigHiro[i] or sigNag[i] or anyLong[i] or anyShort[i]
                     for i in range(n)]
    hctGatedBull = [p.hct_ref and hctMasterBull[i] and anySinglesRaw[i] for i in range(n)]
    hctGatedBear = [p.hct_ref and hctMasterBear[i] and anySinglesRaw[i] for i in range(n)]

    # ---- Pentagon specials ----
    hv1000 = highest(v, 1000)
    hv500 = highest(v, 500)
    pentDisp5 = [(h[i] - l[i]) > nz(hct_rangeStdev[i], 0.0) * 5.0 for i in range(n)]
    sigPentHV1K = [conf[i] and sigPent[i] and hv1000[i] is not None and v[i] == hv1000[i] for i in range(n)]
    sigPentHV500D = [conf[i] and sigPent[i] and hv500[i] is not None and v[i] == hv500[i] and pentDisp5[i] for i in range(n)]

    # ---- displacement engine (standalone + consecutive) ----
    disp_range = [abs(o[i] - c[i]) if p.i_disp_type == "Open to Close" else h[i] - l[i] for i in range(n)]
    disp_std = stdev(disp_range, p.i_std_len)
    disp_range_1 = shift(disp_range, 1)
    disp_std_1 = shift(disp_std, 1)

    def isBullFVG(i):
        return i >= 2 and l[i] > h[i - 2] and o[i - 1] < c[i - 1]

    def isBearFVG(i):
        return i >= 2 and h[i] < l[i - 2] and o[i - 1] > c[i - 1]

    disp_cur_seq = [disp_std[i] is not None and disp_range[i] > disp_std[i] * p.i_disp_std_seq for i in range(n)]
    b2b_gate = [anyHV_cur[i] or disp_cur_seq[i] for i in range(n)]

    def prev_disp(mult):
        return [disp_std_1[i] is not None and disp_range_1[i] is not None and disp_range_1[i] > disp_std_1[i] * mult
                for i in range(n)]

    pd_standalone = prev_disp(p.i_disp_std_standalone)
    sigDispBull = [pd_standalone[i] and isBullFVG(i) for i in range(n)]
    sigDispBear = [pd_standalone[i] and isBearFVG(i) for i in range(n)]

    pd_c2 = prev_disp(p.i_disp_std_cdisp2)
    db2 = [pd_c2[i] and isBullFVG(i) for i in range(n)]
    sb2 = [pd_c2[i] and isBearFVG(i) for i in range(n)]
    bstreak2 = sstreak2 = 0
    sigCDispBull2 = [False] * n
    sigCDispBear2 = [False] * n
    for i in range(n):
        bstreak2 = bstreak2 + 1 if db2[i] else 0
        sstreak2 = sstreak2 + 1 if sb2[i] else 0
        sigCDispBull2[i] = db2[i] and bstreak2 >= 2
        sigCDispBear2[i] = sb2[i] and sstreak2 >= 2

    pd_c3 = prev_disp(p.i_disp_std_cdisp3)
    db3 = [pd_c3[i] and isBullFVG(i) for i in range(n)]
    sb3 = [pd_c3[i] and isBearFVG(i) for i in range(n)]
    bstreak3 = sstreak3 = 0
    sigCDispBull3 = [False] * n
    sigCDispBear3 = [False] * n
    for i in range(n):
        bstreak3 = bstreak3 + 1 if db3[i] else 0
        sstreak3 = sstreak3 + 1 if sb3[i] else 0
        sigCDispBull3[i] = db3[i] and bstreak3 >= 3
        sigCDispBear3[i] = sb3[i] and sstreak3 >= 3

    # ---- sequences UU/UUU/UUUU & DD/DDD/DDDD (Pine var running state) ----
    def seq_state(th_low):
        """Return per-bar (bull_len,bull_sum,bull_disp) and (bear_*) tuples,
        mirroring the Pine var streak accumulators."""
        bull = [None] * n
        bear = [None] * n
        bl_len = bl_sum = bl_disp = 0
        be_len = be_sum = be_disp = 0
        for i in range(n):
            is_u = baseBull(i) and bb_normPrice[i] > th_low
            is_d = baseBear(i) and bb_normPrice[i] > th_low
            if is_u:
                bl_len += 1
                bl_sum += bb_normPrice[i]
                bl_disp += 1 if disp_cur_seq[i] else 0
            else:
                bl_len = bl_sum = bl_disp = 0
            if is_d:
                be_len += 1
                be_sum += bb_normPrice[i]
                be_disp += 1 if disp_cur_seq[i] else 0
            else:
                be_len = be_sum = be_disp = 0
            bull[i] = (bl_len, bl_sum, bl_disp)
            bear[i] = (be_len, be_sum, be_disp)
        return bull, bear

    uu_b, dd_b = seq_state(p.th_low_UU_DD)
    uuu_b, ddd_b = seq_state(p.th_low_UUU_DDD)
    uuuu_b, dddd_b = seq_state(p.th_low_UUUU_DDDD)

    sig_bull_UU = [conf[i] and uu_b[i][0] == 2 and uu_b[i][1] >= th_saab_kratos and uu_b[i][2] >= 1 for i in range(n)]
    sig_bear_DD = [conf[i] and dd_b[i][0] == 2 and dd_b[i][1] >= th_saab_kratos and dd_b[i][2] >= 1 for i in range(n)]

    def seqN(arr, length):
        out = [False] * n
        ovr = [False] * n
        for i in range(n):
            ln, sm, dp = arr[i]
            base = conf[i] and ln == length
            override = base and dp >= 2
            normal = base and dp >= 1 and sm >= th_saab_kratos
            out[i] = override or normal
            ovr[i] = override
        return out, ovr

    sig_bull_UUU, ovr_UUU = seqN(uuu_b, 3)
    sig_bear_DDD, ovr_DDD = seqN(ddd_b, 3)
    sig_bull_UUUU, ovr_UUUU = seqN(uuuu_b, 4)
    sig_bear_DDDD, ovr_DDDD = seqN(dddd_b, 4)

    # ---- B2B (gated by HV or displacement) ----
    sigSAAB_1 = shift(sigSAAB, 1)
    sigKratos_1 = shift(sigKratos, 1)
    sigBull1x_1 = shift(sigBull1x, 1)
    sigBear1x_1 = shift(sigBear1x, 1)
    b2b_2xSAAB = [conf[i] and bool(sigSAAB_1[i]) and sigSAAB[i] and b2b_gate[i] for i in range(n)]
    b2b_2xKratos = [conf[i] and bool(sigKratos_1[i]) and sigKratos[i] and b2b_gate[i] for i in range(n)]
    b2b_2xBull1x = [conf[i] and bool(sigBull1x_1[i]) and sigBull1x[i] and b2b_gate[i] for i in range(n)]
    b2b_2xBear1x = [conf[i] and bool(sigBear1x_1[i]) and sigBear1x[i] and b2b_gate[i] for i in range(n)]
    b2b_MidBull = [conf[i] and not b2b_2xSAAB[i] and not b2b_2xBull1x[i]
                   and ((bool(sigSAAB_1[i]) and sigBull1x[i]) or (bool(sigBull1x_1[i]) and sigSAAB[i]))
                   and b2b_gate[i] for i in range(n)]
    b2b_MidBear = [conf[i] and not b2b_2xKratos[i] and not b2b_2xBear1x[i]
                   and ((bool(sigKratos_1[i]) and sigBear1x[i]) or (bool(sigBear1x_1[i]) and sigKratos[i]))
                   and b2b_gate[i] for i in range(n)]

    # ---- FAUNA (presence ladder -> gated by disp + LONG/SHORT) ----
    atr_MB = _atr_ohlc(o, h, l, c, p.fn_atr_MB)
    atr_RE = _atr_ohlc(o, h, l, c, p.fn_atr_RE)
    atr_GG = _atr_ohlc(o, h, l, c, p.fn_atr_GG)
    avgVol = sma(v, p.fn_vol_MB)
    avgBody = sma([abs(c[i] - o[i]) for i in range(n)], p.fn_body_avg)
    avgDelta = sma([abs(c[i] - c[i - 1]) if i > 0 else 0.0 for i in range(n)], p.fn_avg_delta_len)
    trendMA = sma(c, p.fn_trend_ma_len)
    avgBody_1 = shift(avgBody, 1)
    avgVol_1 = shift(avgVol, 1)

    fn_bullPresent = [False] * n
    fn_bearPresent = [False] * n
    fn_bullText = [""] * n
    fn_bearText = [""] * n
    for i in range(n):
        if atr_MB[i] is None or avgVol[i] is None:
            continue
        body = c[i] - o[i]
        rng = h[i] - l[i]
        body_up = body > 0
        body_dn = body < 0
        body_sz = abs(body)
        body_ratio = 0.0 if rng == 0 else body_sz / rng
        MB_bull = body_up and body_sz > p.fn_alpha_MB * atr_MB[i] and body_ratio > p.fn_beta_MB and v[i] > p.fn_delta_MB * avgVol[i]
        MB_bear = body_dn and body_sz > p.fn_alpha_MB * atr_MB[i] and body_ratio > p.fn_beta_MB and v[i] > p.fn_delta_MB * avgVol[i]
        wide = atr_RE[i] is not None and rng > p.fn_gamma_RE * atr_RE[i]
        RE_bull = body_up and wide and (h[i] - c[i]) < p.fn_epsilon_RE * rng and v[i] > p.fn_delta_RE * avgVol[i]
        RE_bear = body_dn and wide and (c[i] - l[i]) < p.fn_epsilon_RE * rng and v[i] > p.fn_delta_RE * avgVol[i]
        GG_bull = GG_bear = False
        if i > 0 and atr_GG[i] is not None:
            GG_bull = (o[i] - c[i - 1]) > p.fn_zeta_GG * atr_GG[i] and body_up and l[i] > c[i - 1] and v[i] > p.fn_delta_GG * avgVol[i]
            GG_bear = (c[i - 1] - o[i]) > p.fn_zeta_GG * atr_GG[i] and body_dn and h[i] < c[i - 1] and v[i] > p.fn_delta_GG * avgVol[i]
        TA_bull = TA_bear = False
        if i > 0 and trendMA[i] is not None and trendMA[i - 1] is not None and avgDelta[i] is not None:
            up_t = trendMA[i] > trendMA[i - 1]
            dn_t = trendMA[i] < trendMA[i - 1]
            TA_bull = up_t and body_up and (c[i] - c[i - 1]) > p.fn_theta_TA * avgDelta[i] and v[i] > p.fn_delta_TA * avgVol[i]
            TA_bear = dn_t and body_dn and (c[i - 1] - c[i]) > p.fn_theta_TA * avgDelta[i] and v[i] > p.fn_delta_TA * avgVol[i]
        ES_bull = TR_bull = GDR_bull = ES_bear = TR_bear = GDR_bear = False
        if i > 0 and avgBody_1[i] is not None and avgVol_1[i] is not None:
            prev_body = c[i - 1] - o[i - 1]
            prev_range = h[i - 1] - l[i - 1]
            StrongBear = c[i - 1] < o[i - 1] and abs(prev_body) > p.fn_alpha_SB * avgBody_1[i] and v[i - 1] > p.fn_delta_SB * avgVol_1[i]
            WeakBear = c[i - 1] < o[i - 1] and (0.0 if prev_range == 0 else abs(prev_body) / prev_range) <= p.fn_weak_ratio
            StrongBull = c[i - 1] > o[i - 1] and abs(prev_body) > p.fn_alpha_SB * avgBody_1[i] and v[i - 1] > p.fn_delta_SB * avgVol_1[i]
            WeakBull = c[i - 1] > o[i - 1] and (0.0 if prev_range == 0 else abs(prev_body) / prev_range) <= p.fn_weak_ratio
            TR_bull = WeakBear and (MB_bull or RE_bull or TA_bull)
            ES_bull = StrongBear and (MB_bull or RE_bull or TA_bull)
            GDR_bull = c[i - 1] < o[i - 1] and GG_bull
            TR_bear = WeakBull and (MB_bear or RE_bear or TA_bear)
            ES_bear = StrongBull and (MB_bear or RE_bear or TA_bear)
            GDR_bear = c[i - 1] > o[i - 1] and GG_bear

        # bull text ladder (priority order, verbatim from source)
        bt = ""
        if p.show_FaunaBull:
            if GG_bull and MB_bull and RE_bull and TA_bull: bt = "GG+MB+RE+TA"
            elif MB_bull and TA_bull and RE_bull: bt = "MB+TA+RE"
            elif GG_bull and TA_bull and MB_bull: bt = "GG+TA+MB"
            elif GG_bull and TA_bull and RE_bull: bt = "GG+TA+RE"
            elif GDR_bull and RE_bull and MB_bull: bt = "GDR+RE+MB"
            elif MB_bull and RE_bull: bt = "MB+RE"
            elif MB_bull and GG_bull: bt = "MB+GG"
            elif MB_bull and TA_bull: bt = "MB+TA"
            elif MB_bull and TR_bull: bt = "MB+TR"
            elif MB_bull and ES_bull: bt = "MB+ES"
            elif MB_bull and GDR_bull: bt = "MB+GDR"
            elif RE_bull and GG_bull: bt = "RE+GG"
            elif RE_bull and TA_bull: bt = "RE+TA"
            elif RE_bull and TR_bull: bt = "RE+TR"
            elif RE_bull and ES_bull: bt = "RE+ES"
            elif RE_bull and GDR_bull: bt = "RE+GDR"
            elif GG_bull and TA_bull: bt = "GG+TA"
            elif GG_bull and TR_bull: bt = "GG+TR"
            elif GG_bull and ES_bull: bt = "GG+ES"
            elif GG_bull and GDR_bull: bt = "GG+GDR"
            elif TA_bull and TR_bull: bt = "TA+TR"
            elif TA_bull and ES_bull: bt = "TA+ES"
            elif TA_bull and GDR_bull: bt = "TA+GDR"
            elif GDR_bull: bt = "GDR"
            elif ES_bull: bt = "ES"
            elif TR_bull: bt = "TR"
            elif MB_bull: bt = "MB"
            elif RE_bull: bt = "RE"
            elif GG_bull: bt = "GG"
            elif TA_bull: bt = "TA"
        fn_bullText[i] = bt
        fn_bullPresent[i] = bt != ""

        # bear text ladder (priority order, verbatim from source)
        bx = ""
        if p.show_FaunaBear:
            if GG_bear and MB_bear and RE_bear and TA_bear: bx = "GG+MB+RE+TA"
            elif MB_bear and TA_bear and RE_bear: bx = "MB+TA+RE"
            elif GG_bear and TA_bear and MB_bear: bx = "GG+TA+MB"
            elif GG_bear and TA_bear and RE_bear: bx = "GG+TA+RE"
            elif GDR_bear and RE_bear and MB_bear: bx = "GDR+RE+MB"
            elif MB_bear and RE_bear: bx = "MB+RE"
            elif MB_bear and GG_bear: bx = "MB+GG"
            elif MB_bear and TA_bear: bx = "MB+TA"
            elif MB_bear and TR_bear: bx = "MB+TR"
            elif MB_bear and ES_bear: bx = "MB+ES"
            elif MB_bear and GDR_bear: bx = "MB+GDR"
            elif RE_bear and GG_bear: bx = "RE+GG"
            elif RE_bear and TA_bear: bx = "RE+TA"
            elif RE_bear and TR_bear: bx = "RE+TR"
            elif RE_bear and ES_bear: bx = "RE+ES"
            elif RE_bear and GDR_bear: bx = "RE+GDR"
            elif GG_bear and TA_bear: bx = "GG+TA"
            elif GG_bear and TR_bear: bx = "GG+TR"
            elif GG_bear and ES_bear: bx = "GG+ES"
            elif GG_bear and GDR_bear: bx = "GG+GDR"
            elif TA_bear and TR_bear: bx = "TA+TR"
            elif TA_bear and ES_bear: bx = "TA+ES"
            elif TA_bear and GDR_bear: bx = "TA+GDR"
            elif GDR_bear: bx = "GDR"
            elif ES_bear: bx = "ES"
            elif TR_bear: bx = "TR"
            elif MB_bear: bx = "MB"
            elif RE_bear: bx = "RE"
            elif GG_bear: bx = "GG"
            elif TA_bear: bx = "TA"
        fn_bearText[i] = bx
        fn_bearPresent[i] = bx != ""

    fn_bullActive = [p.show_FaunaBull and fn_bullPresent[i] and conf[i] and disp_cur_seq[i] and anyLong[i] for i in range(n)]
    fn_bearActive = [p.show_FaunaBear and fn_bearPresent[i] and conf[i] and disp_cur_seq[i] and anyShort[i] for i in range(n)]

    # ---- HV plots (offset -1, gated by LONG[1]) ----
    v_1 = shift(v, 1)
    hv150_1 = shift(highest(v, 150), 1)
    hv250_1 = shift(highest(v, 250), 1)
    hv350_1 = shift(highest(v, 350), 1)
    hv500_1 = shift(highest(v, 500), 1)
    hv1000_1 = shift(highest(v, 1000), 1)

    def isHV(prev, hi):
        return [prev[i] is not None and hi[i] is not None and prev[i] == hi[i] for i in range(n)]

    is150 = isHV(v_1, hv150_1)
    is250 = isHV(v_1, hv250_1)
    is350 = isHV(v_1, hv350_1)
    is500 = isHV(v_1, hv500_1)
    is1000 = isHV(v_1, hv1000_1)

    raw_HV1000 = [p.show_HV1000 and is1000[i] for i in range(n)]
    raw_HV500 = [p.show_HV500 and is500[i] and not is1000[i] for i in range(n)]
    raw_HV350 = [p.show_HV350 and is350[i] and not is500[i] and not is1000[i] for i in range(n)]
    raw_HV250 = [p.show_HV250 and is250[i] and not is350[i] and not is500[i] and not is1000[i] for i in range(n)]
    raw_HV150 = [p.show_HV150 and is150[i] and not is250[i] and not is350[i] and not is500[i] and not is1000[i] for i in range(n)]

    plot_HV1000 = [raw_HV1000[i] and bool(anyLong_1[i]) for i in range(n)]
    plot_HV500 = [raw_HV500[i] and bool(anyLong_1[i]) for i in range(n)]
    plot_HV350 = [raw_HV350[i] and bool(anyLong_1[i]) for i in range(n)]
    plot_HV250 = [raw_HV250[i] and bool(anyLong_1[i]) for i in range(n)]
    plot_HV150 = [raw_HV150[i] and bool(anyLong_1[i]) for i in range(n)]

    # ─────────────────────── assemble fire matrix (0/1) ──────────────────────
    # keys EXACTLY match the Pine plotshape titles (so the slicer maps 1:1).
    def b01(x):
        return [1 if y else 0 for y in x]

    fire = {}
    fire["SAAB +LONG"] = b01([p.show_SAAB and sigSAAB[i] and anyLong[i] for i in range(n)])
    fire["Kratos +SHORT"] = b01([p.show_Kratos and sigKratos[i] and anyShort[i] for i in range(n)])
    fire["Bull RVOL 1x +LONG"] = b01([p.show_BullRVOL1x and sigBull1x[i] and anyLong[i] for i in range(n)])
    fire["Bear RVOL 1x +SHORT"] = b01([p.show_BearRVOL1x and sigBear1x[i] and anyShort[i] for i in range(n)])
    fire["Grand Slam +LONG"] = b01([p.show_GrandSlam and sigGS[i] and anyLong[i] for i in range(n)])
    fire["MOAB +SHORT"] = b01([p.show_MOAB and sigMOAB[i] and anyShort[i] for i in range(n)])
    fire["WTC +LONG/+SHORT"] = b01([p.show_WTC and sigWTC[i] and anyMom[i] for i in range(n)])
    fire["Hiroshima +LONG/+SHORT"] = b01([p.show_Hiroshima and sigHiro[i] and anyMom[i] for i in range(n)])
    fire["Nagasaki +LONG/+SHORT"] = b01([p.show_Nagasaki and sigNag[i] and anyMom[i] for i in range(n)])

    fire["UU +disp"] = b01([p.show_UU and sig_bull_UU[i] for i in range(n)])
    fire["UUU +disp"] = b01([p.show_UUU and sig_bull_UUU[i] for i in range(n)])
    fire["UUUU +disp"] = b01([p.show_UUUU and sig_bull_UUUU[i] for i in range(n)])
    fire["DD +disp"] = b01([p.show_DD and sig_bear_DD[i] for i in range(n)])
    fire["DDD +disp"] = b01([p.show_DDD and sig_bear_DDD[i] for i in range(n)])
    fire["DDDD +disp"] = b01([p.show_DDDD and sig_bear_DDDD[i] for i in range(n)])

    fire["2x SAAB +HV/disp"] = b01([p.show_B2B_2xSAAB and b2b_2xSAAB[i] for i in range(n)])
    fire["2x Kratos +HV/disp"] = b01([p.show_B2B_2xKratos and b2b_2xKratos[i] for i in range(n)])
    fire["2x Bull 1x +HV/disp"] = b01([p.show_B2B_2xBull1x and b2b_2xBull1x[i] for i in range(n)])
    fire["2x Bear 1x +HV/disp"] = b01([p.show_B2B_2xBear1x and b2b_2xBear1x[i] for i in range(n)])
    fire["B2B Mid Bull +HV/disp"] = b01([p.show_B2B_MidBull and b2b_MidBull[i] for i in range(n)])
    fire["B2B Mid Bear +HV/disp"] = b01([p.show_B2B_MidBear and b2b_MidBear[i] for i in range(n)])

    fire["FAUNA Bull +disp+LONG"] = b01(fn_bullActive)
    fire["FAUNA Bear +disp+SHORT"] = b01(fn_bearActive)

    fire["Disp Bull"] = b01([p.show_DispBull and sigDispBull[i] for i in range(n)])
    fire["Disp Bear"] = b01([p.show_DispBear and sigDispBear[i] for i in range(n)])
    fire["Consec Disp Bull 2+"] = b01([p.show_CDispBull2 and sigCDispBull2[i] for i in range(n)])
    fire["Consec Disp Bear 2+"] = b01([p.show_CDispBear2 and sigCDispBear2[i] for i in range(n)])
    fire["Consec Disp Bull 3+"] = b01([p.show_CDispBull3 and sigCDispBull3[i] for i in range(n)])
    fire["Consec Disp Bear 3+"] = b01([p.show_CDispBear3 and sigCDispBear3[i] for i in range(n)])

    fire["LONG 1"] = b01([p.show_Long1 and sigAddLong[0][i] for i in range(n)])
    fire["SHORT 1"] = b01([p.show_Short1 and sigAddShort[0][i] for i in range(n)])
    fire["LONG 2"] = b01([p.show_Long2 and sigAddLong[1][i] for i in range(n)])
    fire["SHORT 2"] = b01([p.show_Short2 and sigAddShort[1][i] for i in range(n)])
    fire["LONG 3"] = b01([p.show_Long3 and sigAddLong[2][i] for i in range(n)])
    fire["LONG 4"] = b01([p.show_Long4 and sigAddLong[3][i] for i in range(n)])
    fire["LONG 5"] = b01([p.show_Long5 and sigAddLong[4][i] for i in range(n)])

    fire["HV 1000 +LONG[1]"] = b01(plot_HV1000)
    fire["HV 500 +LONG[1]"] = b01(plot_HV500)
    fire["HV 350 +LONG[1]"] = b01(plot_HV350)
    fire["HV 250 +LONG[1]"] = b01(plot_HV250)
    fire["HV 150 +LONG[1]"] = b01(plot_HV150)

    fire["HCT Bull +Singles"] = b01([p.show_HCTBull and hctGatedBull[i] for i in range(n)])
    fire["HCT Bear +Singles"] = b01([p.show_HCTBear and hctGatedBear[i] for i in range(n)])
    fire["Pent+HV1K"] = b01([p.show_PentHV1K and sigPentHV1K[i] for i in range(n)])
    fire["Pent+HV500+Disp"] = b01([p.show_PentHV500D and sigPentHV500D[i] for i in range(n)])

    # ───────────────────── numeric levels (data_window) ──────────────────────
    out = {"ts": list(ts)}
    for k, arr in fire.items():
        out["fire_" + k] = arr

    out["lvl_bb_normPrice"] = list(bb_normPrice)
    out["lvl_bb_normVol"] = list(bb_normVol)
    out["lvl_relVolRatio"] = list(relVolRatio)
    out["lvl_hybRegRatio"] = list(hybRegRatio)
    out["lvl_hybCumRatio"] = list(hybCumRatio)
    out["lvl_hybBodyRat"] = list(hybBodyRat)
    out["lvl_disp_range"] = list(disp_range)
    out["lvl_disp_std"] = list(disp_std)
    out["lvl_hct_rangeStdev"] = list(hct_rangeStdev)
    out["lvl_hct_thresh"] = list(hct_thresh)
    # live threshold values (info-panel content, as data-window scalars)
    out["lvl_th_1x"] = [th_1x] * n
    out["lvl_th_saab_kratos"] = [th_saab_kratos] * n
    out["lvl_th_gs_moab"] = [th_gs_moab] * n
    out["lvl_th_wtc"] = [th_wtc] * n
    out["lvl_th_hiroshima"] = [th_hiroshima] * n
    out["lvl_hybReg1Eff"] = [hybRegEff[0]] * n
    out["lvl_hybReg5Eff"] = [hybRegEff[4]] * n
    # FAUNA combo names (debug; the FIRE is the plot, text is the named combo)
    out["lvl_fn_bullText"] = list(fn_bullText)
    out["lvl_fn_bearText"] = list(fn_bearText)

    # ───────────────────── primitive detection series (0/1) ──────────────────
    prims = {
        "sigSAAB": sigSAAB, "sigKratos": sigKratos, "sigBull1x": sigBull1x,
        "sigBear1x": sigBear1x, "sigGS": sigGS, "sigMOAB": sigMOAB,
        "sigWTC": sigWTC, "sigHiro": sigHiro, "sigPent": sigPent, "sigNag": sigNag,
        "anyLong": anyLong, "anyShort": anyShort, "anyMom": anyMom,
        "anyHV_cur": anyHV_cur, "disp_cur_seq": disp_cur_seq, "b2b_gate": b2b_gate,
        "hct_dispBull": hct_dispBull, "hct_dispBear": hct_dispBear, "hct_noDisp": hct_noDisp,
        "hctMasterBull": hctMasterBull, "hctMasterBear": hctMasterBear,
        "groupA_Bull": groupA_Bull, "groupA_Bear": groupA_Bear, "groupB": groupB,
        "sigDispBull": sigDispBull, "sigDispBear": sigDispBear,
        "sig_bull_UU": sig_bull_UU, "sig_bear_DD": sig_bear_DD,
        "sig_bull_UUU": sig_bull_UUU, "sig_bear_DDD": sig_bear_DDD,
        "sig_bull_UUUU": sig_bull_UUUU, "sig_bear_DDDD": sig_bear_DDDD,
        "ovr_UUU": ovr_UUU, "ovr_DDD": ovr_DDD, "ovr_UUUU": ovr_UUUU, "ovr_DDDD": ovr_DDDD,
        "fn_bullPresent": fn_bullPresent, "fn_bearPresent": fn_bearPresent,
        "is150": is150, "is250": is250, "is350": is350, "is500": is500, "is1000": is1000,
        "sigPentHV1K": sigPentHV1K, "sigPentHV500D": sigPentHV500D,
    }
    for k, arr in prims.items():
        out["prim_" + k] = [1 if x else 0 for x in arr]

    return out


# ─────────────────── detection-plot dictionary (id -> descriptor) ────────────
# Stable ids for the 44 detection plots (every Pine plotshape signal).
PLOT_IDS = {
    "SAAB +LONG": "RVOL 0.56 bullish (SAAB/Kratos tier), gated +LONG",
    "Kratos +SHORT": "RVOL 0.56 bearish (SAAB/Kratos tier), gated +SHORT",
    "Bull RVOL 1x +LONG": "RVOL 0.56 bull 1x tier, gated +LONG",
    "Bear RVOL 1x +SHORT": "RVOL 0.56 bear 1x tier, gated +SHORT",
    "Grand Slam +LONG": "RVOL 0.56 bull extreme (>= GS/MOAB th), gated +LONG",
    "MOAB +SHORT": "RVOL 0.56 bear extreme (>= GS/MOAB th), gated +SHORT (default OFF)",
    "WTC +LONG/+SHORT": "RVOL Reg@Time mid-tier (WTC,Hiroshima], gated +mom",
    "Hiroshima +LONG/+SHORT": "RVOL Reg@Time top-tier (> Hiroshima), gated +mom",
    "Nagasaki +LONG/+SHORT": "All-time-high volume, gated +mom",
    "UU +disp": "2 consecutive LONGs, sum>=SAAB th + 1 disp",
    "UUU +disp": "3 consecutive LONGs, sum>=SAAB th (or 2-disp override)",
    "UUUU +disp": "4 consecutive LONGs, sum>=SAAB th (or 2-disp override)",
    "DD +disp": "2 consecutive SHORTs, sum>=SAAB th + 1 disp",
    "DDD +disp": "3 consecutive SHORTs, sum>=SAAB th (or 2-disp override)",
    "DDDD +disp": "4 consecutive SHORTs, sum>=SAAB th (or 2-disp override)",
    "2x SAAB +HV/disp": "SAAB on bar0 and bar1, gated HV150+/disp",
    "2x Kratos +HV/disp": "Kratos on bar0 and bar1, gated HV150+/disp",
    "2x Bull 1x +HV/disp": "Bull1x on bar0 and bar1, gated HV150+/disp",
    "2x Bear 1x +HV/disp": "Bear1x on bar0 and bar1, gated HV150+/disp",
    "B2B Mid Bull +HV/disp": "mixed bull RVOL tiers consecutive, gated HV150+/disp",
    "B2B Mid Bear +HV/disp": "mixed bear RVOL tiers consecutive, gated HV150+/disp",
    "FAUNA Bull +disp+LONG": "named bull combo (MB/RE/GG/TA/TR/ES/GDR), gated disp+LONG",
    "FAUNA Bear +disp+SHORT": "named bear combo, gated disp+SHORT",
    "Disp Bull": "bar[1] stdev-displacement + bull FVG (offset -1)",
    "Disp Bear": "bar[1] stdev-displacement + bear FVG (offset -1)",
    "Consec Disp Bull 2+": "2+ back-to-back bull displacements (offset -1)",
    "Consec Disp Bear 2+": "2+ back-to-back bear displacements (offset -1)",
    "Consec Disp Bull 3+": "3+ back-to-back bull displacements (offset -1)",
    "Consec Disp Bear 3+": "3+ back-to-back bear displacements (offset -1)",
    "LONG 1": "hybrid momentum tier 1 bull (no gate)",
    "SHORT 1": "hybrid momentum tier 1 bear (no gate)",
    "LONG 2": "hybrid momentum tier 2 bull",
    "SHORT 2": "hybrid momentum tier 2 bear",
    "LONG 3": "hybrid momentum tier 3 bull (long-only)",
    "LONG 4": "hybrid momentum tier 4 bull (long-only)",
    "LONG 5": "hybrid momentum tier 5 bull (long-only)",
    "HV 1000 +LONG[1]": "volume[1]==highest(vol,1000)[1], gated LONG[1] (offset -1)",
    "HV 500 +LONG[1]": "volume[1]==highest(vol,500)[1] not 1000, gated LONG[1]",
    "HV 350 +LONG[1]": "volume[1]==highest(vol,350)[1] not 500+, gated LONG[1]",
    "HV 250 +LONG[1]": "volume[1]==highest(vol,250)[1] not 350+, gated LONG[1]",
    "HV 150 +LONG[1]": "volume[1]==highest(vol,150)[1] not 250+, gated LONG[1]",
    "HCT Bull +Singles": "OR of 15 HCT bull combos, gated any Singles signal",
    "HCT Bear +Singles": "OR of 15 HCT bear combos, gated any Singles signal",
    "Pent+HV1K": "Pentagon and volume==highest(vol,1000) same candle",
    "Pent+HV500+Disp": "Pentagon and volume==highest(vol,500) and range>5*stdev",
}
