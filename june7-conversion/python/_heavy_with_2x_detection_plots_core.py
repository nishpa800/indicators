"""Heavy Weapons w SAAB Kratos x2 (NRA SINGLES) — FULL detection fire-matrix core.

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/heavy_with_2x_detection_plots_tickfriendly.pine"
  //@version=5, indicator("Heavy Weapons w saab kratos x 2 long shorts NON
  REPAINTING NRA ****SINGLES**** ...", shorttitle="heavy uncap oG"),
  import TradingView/ta/7 as tv_ta. RE10023 tick guards already applied in source
  (reg_anchorSafe -> "D" on tick; tfSec -> TICK_FALLBACK_SEC on tick).

ULTRACODE FULL PORT — scope statement (read this):
  This module ports EVERY one of the 42 `plotshape(...)` detection plots in the
  source, 1:1, directly from OHLCV. Pine `var`/history semantics are preserved
  (single forward pass; `[k]` = k-bars-back; `conf` = barstate.isconfirmed;
  `nz()` fallbacks honoured). Sub-engines ported:

    RVOL 0.56          SAAB / Kratos / BullRVOL1x / BearRVOL1x / GrandSlam / MOAB
    RVOL Reg@Time      WTC / Hiroshima            (via canonical relativeVolume shim)
    Hybrid Momentum    LONG 1-5 / SHORT 1-2       (reg+cum ratio + body-ratio ladder,
                                                   auto-derived from Hiroshima)
    Nagasaki           running all-time-high volume (Pine var maxVol)
    Sequences (IPSF)   UU/UUU/UUUU + DD/DDD/DDDD  (independent per-pair streak/sum)
    B2B                2x SAAB/Kratos/Bull1x/Bear1x + B2B Mid Bull/Bear (ungated)
    FAUNA              MB/RE/GG/TA + TR/ES/GDR ladder -> Bull/Bear (present + conf)
    Displacement       Disp Bull/Bear + Consec Disp 2+/3+ (min<range<=max band)
    HV ladder          HV 75/150/250/500/1000 (NRA via [1], offset -1, exclusivity)
    Hot Spot           calendar windows (opEx/qtrEnd/Russell/taxLoss/janEffect/hfRedemp)

  relativeVolume ports via the canonical shim (_nn_harness.relative_volume ->
  rti/tv_ta_shim, ta/7) — NEVER re-derived as volume/sma(volume,N).

  Tick vs time: ONE code path. The ONLY grain-bound difference is the RVOL anchor
  ("D" wall-clock day on BOTH grains, per tradingview-import-decoupling, mirroring
  the Pine RE10023 fix of forcing "D" on tick) and tfSec (the per-TF threshold
  key), which is a parameter.

HONESTY: there is NO all-zero stub series in this module. Every plot listed in
PLOT_IDS is produced by real Pine logic. If a plot reads 0 on a tape it is because
the source logic produced 0 on those bars. The parity harness re-derives the core
RVOL / displacement / sequence / B2B / HV logic independently and reports a REAL
pass/total.

Cosmetic-only Pine objects intentionally NOT ported (they are not detection plots):
  - the INFO PANEL (`table.*`) — banned graphic object, pure display; its live
    threshold/ratio values ARE emitted here as data-window `lvl_*` scalars.
  - the aggregated `alert(...)` message string — derived from the same fires.
  - FAUNA combo text (`fn_bullText`/`fn_bearText`) — the FIRE is FAUNA Bull/Bear;
    the text is the combo name, surfaced as a `lvl_` level/debug primitive.

ONE GRAIN-BOUND CAVEAT (Hot Spot): the Pine Hot Spot plot keys off calendar fields
(dayofmonth[1]/month[1]/dayofweek[1]) of each bar's timestamp. On time bars this is
faithful. On home-grown N-tick bars the calendar fields come from the bar's open
timestamp identically — so Hot Spot is fully ported on BOTH grains (not stubbed).
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nn_harness import (  # noqa: E402
    Bar, nz, sma, stdev, highest, atr as _atr_ohlc, shift, relative_volume,
)


# ──────────────────────────────── parameters ────────────────────────────────
@dataclass
class Params:
    """Every Pine input.* as a parameter, defaulted to the source default.
    `tfSec` is the per-timeframe threshold key (Pine `tfSec`); on tick charts the
    Pine source uses TICK_FALLBACK_SEC=10, on time charts timeframe.in_seconds()."""
    tfSec: int = 60                  # per-TF threshold table key (seconds/bar)
    nn_tick_assumed_sec: int = 10    # Pine TICK_FALLBACK_SEC fallback on tick charts

    # ---- RVOL 0.56 (Bull/Bear) ----
    bb_avgLength: int = 30
    bb_smaLength: int = 20

    # ---- RVOL Reg@Time ----
    reg_length: int = 30
    reg_calculationMode: str = "Cumulative"   # "Cumulative" | "Regular"
    reg_adjustRealtime: bool = True

    # ---- Hybrid regime auto-derive (master ON) + manual fallbacks ----
    hyb_autoDerive: bool = True
    hyb_addReg1: float = 5.0
    hyb_addCum1: float = 3.0
    hyb_bodyRat1: float = 0.65
    hyb_addReg2: float = 5.0
    hyb_addCum2: float = 3.0
    hyb_bodyRat2: float = 0.65
    hyb_addReg3: float = 5.0
    hyb_addCum3: float = 3.0
    hyb_bodyRat3: float = 0.65
    hyb_addReg4: float = 5.0
    hyb_addCum4: float = 3.0
    hyb_bodyRat4: float = 0.65
    hyb_addReg5: float = 5.0
    hyb_addCum5: float = 3.0
    hyb_bodyRat5: float = 0.65

    # ---- Nagasaki ----
    enableNagasaki: bool = True

    # ---- Sequence lower + sum thresholds (IPSF, per-pair) ----
    th_low_UU_DD: float = 1.0
    th_low_UUU_DDD: float = 1.0
    th_low_UUUU_DDDD: float = 1.0
    seqTh_UU_DD: float = 0.1
    seqTh_UUU_DDD: float = 0.1
    seqTh_UUUU_DDDD: float = 0.1
    seq_th_high: float = 50.0

    # ---- Displacement (single std band: min < range <= max) ----
    i_disp_type: str = "Open to Close"        # "Open to Close" | "High to Low"
    i_std_len: int = 100
    i_std_min: float = 3.0
    i_std_max: float = 7.0

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
    show_HV75: bool = True
    show_HV150: bool = True
    show_HV250: bool = True
    show_HV500: bool = True
    show_HV1000: bool = True
    show_HotSpot: bool = True
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


# ───────────────────── calendar fields (Pine dayofmonth/month/...) ───────────
# Pine's dayofmonth/month/dayofweek read the bar timestamp in the chart timezone.
# We use the bar's OPEN ts in UTC (deterministic + reproducible). dayofweek in Pine
# is 1=Sunday..7=Saturday; Python weekday() is 0=Monday..6=Sunday -> map below.
def _cal(ts_ms):
    d = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    pine_dow = (d.weekday() + 1) % 7 + 1   # Mon..Sun -> 2..7,1 ; matches 1=Sun..7=Sat
    return d.month, d.day, pine_dow


_DOW_MON = 2   # Pine dayofweek.monday == 2
_DOW_WED = 4   # Pine dayofweek.wednesday == 4


# ─────────────────────────────── the compute ────────────────────────────────
def compute(bars: Sequence[Bar], *, params: Params | None = None, rv_anchor: str = "D"):
    """Return the detection fire matrix + numeric levels for Heavy Weapons x2.

    Output dict:
      "ts"              -> list[int]  bar open timestamps (epoch ms)
      "fire_<title>"    -> list[0/1]  one per detection plot (Pine plotshape title)
      "lvl_<name>"      -> list[float|None|str]  numeric levels / data-window plots
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
    # Reg: linear ramp H*2.85 (M1) -> H*1.1875 (M5)
    r1 = th_hiroshima * 2.85
    r5 = th_hiroshima * 1.1875
    step = (r1 - r5) / 4.0
    hybAutoReg = [r1, r1 - 1.0 * step, r1 - 2.0 * step, r1 - 3.0 * step, r5]
    # Cum: CUM = (1.398*1.33) * sqrt(ln(REG))
    phi = 1.398 * 1.33
    hybAutoCum = [phi * math.sqrt(math.log(x)) for x in hybAutoReg]
    hybAutoBody = [0.69, 0.72, 0.75, 0.78, 0.81]
    # manual fallbacks (used only when hyb_autoDerive is False)
    manReg = [p.hyb_addReg1, p.hyb_addReg2, p.hyb_addReg3, p.hyb_addReg4, p.hyb_addReg5]
    manCum = [p.hyb_addCum1, p.hyb_addCum2, p.hyb_addCum3, p.hyb_addCum4, p.hyb_addCum5]
    manBody = [p.hyb_bodyRat1, p.hyb_bodyRat2, p.hyb_bodyRat3, p.hyb_bodyRat4, p.hyb_bodyRat5]
    hybRegEff = hybAutoReg if p.hyb_autoDerive else manReg
    hybCumEff = hybAutoCum if p.hyb_autoDerive else manCum
    hybBodyEff = hybAutoBody if p.hyb_autoDerive else manBody

    conf = [True] * n   # closed-bar (confirmed) evaluation; we score closed bars only

    # ---- RVOL 0.56 bull/bear ----
    # Pine: norm = spike / nz(sma(spike,len)[1], 1.0). nz replaces only `na`; a real
    # 0.0 denom yields Pine `na` (0/0) which makes every downstream comparison false.
    # Mirror that: a 0 denom -> 0.0 norm (non-firing), never a ZeroDivisionError.
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

    def inRange(x, lo, hi):     # Pine bb_inRange: v >= lowTh and v < highTh
        return lo <= x < hi

    sigSAAB = [conf[i] and baseBull(i) and inRange(bb_normPrice[i], th_saab_kratos, th_1x) for i in range(n)]
    sigKratos = [conf[i] and baseBear(i) and inRange(bb_normPrice[i], th_saab_kratos, th_1x) for i in range(n)]
    sigBull1x = [conf[i] and baseBull(i) and inRange(bb_normPrice[i], th_1x, th_gs_moab) for i in range(n)]
    sigBear1x = [conf[i] and baseBear(i) and inRange(bb_normPrice[i], th_1x, th_gs_moab) for i in range(n)]
    sigGS = [conf[i] and baseBull(i) and bb_normPrice[i] >= th_gs_moab for i in range(n)]
    sigMOAB = [conf[i] and baseBear(i) and bb_normPrice[i] >= th_gs_moab for i in range(n)]

    # ---- RVOL Reg@Time (mode-driven) for WTC / Hiroshima ----
    _, _, relVolRatio = relative_volume(
        v, p.reg_length, anchor_timeframe=rv_anchor,
        is_cumulative=is_cumulative_reg, bar_timestamps=ts)
    sigWTC = [False] * n
    sigHiro = [False] * n
    for i in range(n):
        r = relVolRatio[i]
        if r is None:
            continue
        sigWTC[i] = conf[i] and (r > th_wtc) and (r <= th_hiroshima)
        sigHiro[i] = conf[i] and (r > th_hiroshima)

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
    sigAddShort = [[False] * n for _ in range(2)]   # tiers 1..2 only (source)
    for i in range(n):
        for k in range(5):
            convict = hybBodyRat[i] >= hybBodyEff[k]
            if c[i] > o[i] and convict and mom(i, k):
                sigAddLong[k][i] = True
        for k in range(2):
            convict = hybBodyRat[i] >= hybBodyEff[k]
            if c[i] < o[i] and convict and mom(i, k):
                sigAddShort[k][i] = True

    # ---- Nagasaki (running all-time-high volume; Pine var maxVol) ----
    sigNag_raw = [False] * n
    maxVol = 0.0
    for i in range(n):
        if not conf[i]:
            continue
        if i == 0:
            maxVol = v[i]
        elif v[i] > maxVol:
            sigNag_raw[i] = True
            maxVol = v[i]
    sigNag = [p.enableNagasaki and sigNag_raw[i] for i in range(n)]

    # ---- RVOL sequences (IPSF) — independent per-pair streak/sum ----
    def seq_inRange_pair(x, th_low):
        return th_low < x < p.seq_th_high

    def seq_state(th_low):
        """Return per-bar (bull_len, bull_sum) and (bear_len, bear_sum), mirroring
        the Pine var streak accumulators (reset to 0 on a non-qualifying bar)."""
        bull = [None] * n
        bear = [None] * n
        bl_len = 0
        bl_sum = 0.0
        be_len = 0
        be_sum = 0.0
        for i in range(n):
            is_u = baseBull(i) and seq_inRange_pair(bb_normPrice[i], th_low)
            is_d = baseBear(i) and seq_inRange_pair(bb_normPrice[i], th_low)
            if conf[i]:
                if is_u:
                    bl_len += 1
                    bl_sum += bb_normPrice[i]
                else:
                    bl_len = 0
                    bl_sum = 0.0
                if is_d:
                    be_len += 1
                    be_sum += bb_normPrice[i]
                else:
                    be_len = 0
                    be_sum = 0.0
            bull[i] = (bl_len, bl_sum)
            bear[i] = (be_len, be_sum)
        return bull, bear

    uu_b, dd_b = seq_state(p.th_low_UU_DD)
    uuu_b, ddd_b = seq_state(p.th_low_UUU_DDD)
    uuuu_b, dddd_b = seq_state(p.th_low_UUUU_DDDD)

    sig_bull_UU = [conf[i] and uu_b[i][0] == 2 and uu_b[i][1] >= p.seqTh_UU_DD for i in range(n)]
    sig_bull_UUU = [conf[i] and uuu_b[i][0] == 3 and uuu_b[i][1] >= p.seqTh_UUU_DDD for i in range(n)]
    sig_bull_UUUU = [conf[i] and uuuu_b[i][0] == 4 and uuuu_b[i][1] >= p.seqTh_UUUU_DDDD for i in range(n)]
    sig_bear_DD = [conf[i] and dd_b[i][0] == 2 and dd_b[i][1] >= p.seqTh_UU_DD for i in range(n)]
    sig_bear_DDD = [conf[i] and ddd_b[i][0] == 3 and ddd_b[i][1] >= p.seqTh_UUU_DDD for i in range(n)]
    sig_bear_DDDD = [conf[i] and dddd_b[i][0] == 4 and dddd_b[i][1] >= p.seqTh_UUUU_DDDD for i in range(n)]

    # ---- B2B (ungated in this source) ----
    sigSAAB_1 = shift(sigSAAB, 1)
    sigKratos_1 = shift(sigKratos, 1)
    sigBull1x_1 = shift(sigBull1x, 1)
    sigBear1x_1 = shift(sigBear1x, 1)
    b2b_2xSAAB = [conf[i] and bool(sigSAAB_1[i]) and sigSAAB[i] for i in range(n)]
    b2b_2xKratos = [conf[i] and bool(sigKratos_1[i]) and sigKratos[i] for i in range(n)]
    b2b_2xBull1x = [conf[i] and bool(sigBull1x_1[i]) and sigBull1x[i] for i in range(n)]
    b2b_2xBear1x = [conf[i] and bool(sigBear1x_1[i]) and sigBear1x[i] for i in range(n)]
    b2b_MidBull = [conf[i] and not b2b_2xSAAB[i] and not b2b_2xBull1x[i]
                   and ((bool(sigSAAB_1[i]) and sigBull1x[i]) or (bool(sigBull1x_1[i]) and sigSAAB[i]))
                   for i in range(n)]
    b2b_MidBear = [conf[i] and not b2b_2xKratos[i] and not b2b_2xBear1x[i]
                   and ((bool(sigKratos_1[i]) and sigBear1x[i]) or (bool(sigBear1x_1[i]) and sigKratos[i]))
                   for i in range(n)]

    # ---- FAUNA (presence ladder; active = present + conf in this source) ----
    atr_MB = _atr_ohlc(o, h, l, c, p.fn_atr_MB)
    atr_RE = _atr_ohlc(o, h, l, c, p.fn_atr_RE)
    atr_GG = _atr_ohlc(o, h, l, c, p.fn_atr_GG)
    avgVol = sma(v, p.fn_vol_MB)
    avgBody = sma([abs(c[i] - o[i]) for i in range(n)], p.fn_body_avg)
    avgRange = sma([h[i] - l[i] for i in range(n)], p.fn_range_avg)
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

        # bull text ladder (priority order, verbatim from source L536-596)
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

        # bear text ladder (priority order, verbatim from source L602-662)
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

    fn_bullActive = [p.show_FaunaBull and fn_bullPresent[i] and conf[i] for i in range(n)]
    fn_bearActive = [p.show_FaunaBear and fn_bearPresent[i] and conf[i] for i in range(n)]

    # ---- displacement engine (single std band: min < range[1] <= max; FVG[1]) ----
    disp_isBullFVG = [i >= 2 and l[i] > h[i - 2] and o[i - 1] < c[i - 1] for i in range(n)]
    disp_isBearFVG = [i >= 2 and h[i] < l[i - 2] and o[i - 1] > c[i - 1] for i in range(n)]
    disp_range = [abs(o[i] - c[i]) if p.i_disp_type == "Open to Close" else h[i] - l[i] for i in range(n)]
    disp_std = stdev(disp_range, p.i_std_len)
    disp_thMin = [None if disp_std[i] is None else disp_std[i] * p.i_std_min for i in range(n)]
    disp_thMax = [None if disp_std[i] is None else disp_std[i] * p.i_std_max for i in range(n)]
    disp_range_1 = shift(disp_range, 1)
    disp_thMin_1 = shift(disp_thMin, 1)
    disp_thMax_1 = shift(disp_thMax, 1)

    # Pine: disp_isPrevBarDisplaced = range[1] > thMin[1] and range[1] <= thMax[1]
    disp_prevDisplaced = [
        (disp_range_1[i] is not None and disp_thMin_1[i] is not None and disp_thMax_1[i] is not None
         and disp_range_1[i] > disp_thMin_1[i] and disp_range_1[i] <= disp_thMax_1[i])
        for i in range(n)
    ]

    sigDispBull = [disp_prevDisplaced[i] and disp_isBullFVG[i] for i in range(n)]
    sigDispBear = [disp_prevDisplaced[i] and disp_isBearFVG[i] for i in range(n)]

    # consecutive streaks (Pine var disp_bullStreak / disp_bearStreak)
    sigCDispBull2 = [False] * n
    sigCDispBear2 = [False] * n
    sigCDispBull3 = [False] * n
    sigCDispBear3 = [False] * n
    bstreak = 0
    sstreak = 0
    for i in range(n):
        bstreak = bstreak + 1 if sigDispBull[i] else 0
        sstreak = sstreak + 1 if sigDispBear[i] else 0
        sigCDispBull2[i] = sigDispBull[i] and bstreak >= 2
        sigCDispBear2[i] = sigDispBear[i] and sstreak >= 2
        sigCDispBull3[i] = sigDispBull[i] and bstreak >= 3
        sigCDispBear3[i] = sigDispBear[i] and sstreak >= 3

    # ---- HV ladder (NRA via [1]) + Hot Spot calendar ----
    v_1 = shift(v, 1)
    hv75_1 = shift(highest(v, 75), 1)
    hv150_1 = shift(highest(v, 150), 1)
    hv250_1 = shift(highest(v, 250), 1)
    hv500_1 = shift(highest(v, 500), 1)
    hv1000_1 = shift(highest(v, 1000), 1)

    def isHV(prev, hi):
        return [prev[i] is not None and hi[i] is not None and prev[i] == hi[i] for i in range(n)]

    is75 = isHV(v_1, hv75_1)
    is150 = isHV(v_1, hv150_1)
    is250 = isHV(v_1, hv250_1)
    is500 = isHV(v_1, hv500_1)
    is1000 = isHV(v_1, hv1000_1)

    # Hot Spot calendar windows (read from bar[1] calendar fields, per Pine)
    isHotSpot = [False] * n
    for i in range(n):
        if i < 1:
            continue
        month1, day1, dow1 = _cal(ts[i - 1])
        opEx = (10 <= day1 <= 17) and (_DOW_MON <= dow1 <= _DOW_WED)
        qtrEnd = (month1 in (3, 6, 9, 12)) and (23 <= day1 <= 27)
        russell = (month1 == 6) and (19 <= day1 <= 24)
        taxLoss = (month1 == 12) and (21 <= day1 <= 26)
        janEffect = (month1 == 12) and (27 <= day1 <= 30)
        hfRedemp = (month1 in (5, 11)) and (10 <= day1 <= 13)
        isHotSpot[i] = opEx or qtrEnd or russell or taxLoss or janEffect or hfRedemp

    plot_HV1000 = [p.show_HV1000 and is1000[i] for i in range(n)]
    plot_HV500 = [p.show_HV500 and is500[i] and not is1000[i] for i in range(n)]
    plot_HV250 = [p.show_HV250 and is250[i] and not is500[i] and not is1000[i] for i in range(n)]
    plot_HV150 = [p.show_HV150 and is150[i] and not is250[i] and not is500[i] and not is1000[i] for i in range(n)]
    plot_HV75 = [p.show_HV75 and is75[i] and not is150[i] and not is250[i] and not is500[i] and not is1000[i] for i in range(n)]
    plot_HS = [p.show_HotSpot and isHotSpot[i] for i in range(n)]

    # ─────────────────────── assemble fire matrix (0/1) ──────────────────────
    # keys EXACTLY match the Pine plotshape titles (so the slicer maps 1:1).
    def b01(x):
        return [1 if y else 0 for y in x]

    fire = {}
    # RVOL 0.56 + Reg@Time (9)
    fire["SAAB"] = b01([p.show_SAAB and sigSAAB[i] for i in range(n)])
    fire["Kratos"] = b01([p.show_Kratos and sigKratos[i] for i in range(n)])
    fire["Bull RVOL 1x"] = b01([p.show_BullRVOL1x and sigBull1x[i] for i in range(n)])
    fire["Bear RVOL 1x"] = b01([p.show_BearRVOL1x and sigBear1x[i] for i in range(n)])
    fire["Grand Slam"] = b01([p.show_GrandSlam and sigGS[i] for i in range(n)])
    fire["MOAB"] = b01([p.show_MOAB and sigMOAB[i] for i in range(n)])
    fire["WTC"] = b01([p.show_WTC and sigWTC[i] for i in range(n)])
    fire["Hiroshima"] = b01([p.show_Hiroshima and sigHiro[i] for i in range(n)])
    fire["Nagasaki (HEV)"] = b01([p.show_Nagasaki and sigNag[i] for i in range(n)])

    # RVOL sequences IPSF (6)
    fire["UU Signal"] = b01([p.show_UU and sig_bull_UU[i] for i in range(n)])
    fire["UUU Signal"] = b01([p.show_UUU and sig_bull_UUU[i] for i in range(n)])
    fire["UUUU Signal"] = b01([p.show_UUUU and sig_bull_UUUU[i] for i in range(n)])
    fire["DD Signal"] = b01([p.show_DD and sig_bear_DD[i] for i in range(n)])
    fire["DDD Signal"] = b01([p.show_DDD and sig_bear_DDD[i] for i in range(n)])
    fire["DDDD Signal"] = b01([p.show_DDDD and sig_bear_DDDD[i] for i in range(n)])

    # back-to-back (6)
    fire["2x SAAB"] = b01([p.show_B2B_2xSAAB and b2b_2xSAAB[i] for i in range(n)])
    fire["2x Kratos"] = b01([p.show_B2B_2xKratos and b2b_2xKratos[i] for i in range(n)])
    fire["2x Bull 1x"] = b01([p.show_B2B_2xBull1x and b2b_2xBull1x[i] for i in range(n)])
    fire["2x Bear 1x"] = b01([p.show_B2B_2xBear1x and b2b_2xBear1x[i] for i in range(n)])
    fire["B2B Mid Bull"] = b01([p.show_B2B_MidBull and b2b_MidBull[i] for i in range(n)])
    fire["B2B Mid Bear"] = b01([p.show_B2B_MidBear and b2b_MidBear[i] for i in range(n)])

    # FAUNA (2)
    fire["FAUNA Bull"] = b01(fn_bullActive)
    fire["FAUNA Bear"] = b01(fn_bearActive)

    # displacement (6, offset -1 in Pine; fire lands on the FVG bar, marks displaced bar)
    fire["Disp Bull"] = b01([p.show_DispBull and sigDispBull[i] for i in range(n)])
    fire["Disp Bear"] = b01([p.show_DispBear and sigDispBear[i] for i in range(n)])
    fire["Consec Disp Bull 2+"] = b01([p.show_CDispBull2 and sigCDispBull2[i] for i in range(n)])
    fire["Consec Disp Bear 2+"] = b01([p.show_CDispBear2 and sigCDispBear2[i] for i in range(n)])
    fire["Consec Disp Bull 3+"] = b01([p.show_CDispBull3 and sigCDispBull3[i] for i in range(n)])
    fire["Consec Disp Bear 3+"] = b01([p.show_CDispBear3 and sigCDispBear3[i] for i in range(n)])

    # momentum (7)
    fire["LONG 1"] = b01([p.show_Long1 and sigAddLong[0][i] for i in range(n)])
    fire["SHORT 1"] = b01([p.show_Short1 and sigAddShort[0][i] for i in range(n)])
    fire["LONG 2"] = b01([p.show_Long2 and sigAddLong[1][i] for i in range(n)])
    fire["SHORT 2"] = b01([p.show_Short2 and sigAddShort[1][i] for i in range(n)])
    fire["LONG 3"] = b01([p.show_Long3 and sigAddLong[2][i] for i in range(n)])
    fire["LONG 4"] = b01([p.show_Long4 and sigAddLong[3][i] for i in range(n)])
    fire["LONG 5"] = b01([p.show_Long5 and sigAddLong[4][i] for i in range(n)])

    # HV ladder + Hot Spot (6, offset -1 in Pine)
    fire["HV 1000"] = b01(plot_HV1000)
    fire["HV 500"] = b01(plot_HV500)
    fire["HV 250"] = b01(plot_HV250)
    fire["HV 150"] = b01(plot_HV150)
    fire["HV 75"] = b01(plot_HV75)
    fire["Hot Spot"] = b01(plot_HS)

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
    # live threshold values (info-panel content, as data-window scalars)
    out["lvl_th_1x"] = [th_1x] * n
    out["lvl_th_saab_kratos"] = [th_saab_kratos] * n
    out["lvl_th_gs_moab"] = [th_gs_moab] * n
    out["lvl_th_wtc"] = [th_wtc] * n
    out["lvl_th_hiroshima"] = [th_hiroshima] * n
    # M1..M5 effective reg/cum/body ladder (Pine data-window plots)
    for k in range(5):
        out[f"lvl_hybReg{k+1}Eff"] = [hybRegEff[k]] * n
        out[f"lvl_hybCum{k+1}Eff"] = [hybCumEff[k]] * n
        out[f"lvl_hybBody{k+1}Eff"] = [hybBodyEff[k]] * n
    # FAUNA combo names (debug; the FIRE is the plot, text is the named combo)
    out["lvl_fn_bullText"] = list(fn_bullText)
    out["lvl_fn_bearText"] = list(fn_bearText)

    # ───────────────────── primitive detection series (0/1) ──────────────────
    anyLong = [any(sigAddLong[k][i] for k in range(5)) for i in range(n)]
    anyShort = [any(sigAddShort[k][i] for k in range(2)) for i in range(n)]
    prims = {
        "sigSAAB": sigSAAB, "sigKratos": sigKratos, "sigBull1x": sigBull1x,
        "sigBear1x": sigBear1x, "sigGS": sigGS, "sigMOAB": sigMOAB,
        "sigWTC": sigWTC, "sigHiro": sigHiro, "sigNag": sigNag,
        "anyLong": anyLong, "anyShort": anyShort,
        "sigDispBull": sigDispBull, "sigDispBear": sigDispBear,
        "disp_prevDisplaced": disp_prevDisplaced,
        "sig_bull_UU": sig_bull_UU, "sig_bear_DD": sig_bear_DD,
        "sig_bull_UUU": sig_bull_UUU, "sig_bear_DDD": sig_bear_DDD,
        "sig_bull_UUUU": sig_bull_UUUU, "sig_bear_DDDD": sig_bear_DDDD,
        "b2b_2xSAAB": b2b_2xSAAB, "b2b_2xKratos": b2b_2xKratos,
        "b2b_MidBull": b2b_MidBull, "b2b_MidBear": b2b_MidBear,
        "fn_bullPresent": fn_bullPresent, "fn_bearPresent": fn_bearPresent,
        "is75": is75, "is150": is150, "is250": is250, "is500": is500, "is1000": is1000,
        "isHotSpot": isHotSpot,
        "sigAddLong1": sigAddLong[0], "sigAddLong2": sigAddLong[1],
        "sigAddLong3": sigAddLong[2], "sigAddLong4": sigAddLong[3],
        "sigAddLong5": sigAddLong[4],
        "sigAddShort1": sigAddShort[0], "sigAddShort2": sigAddShort[1],
    }
    for k, arr in prims.items():
        out["prim_" + k] = [1 if x else 0 for x in arr]

    return out


# ─────────────────── detection-plot dictionary (id -> descriptor) ────────────
# Stable ids for the 42 detection plots (every Pine plotshape signal in source).
PLOT_IDS = {
    "SAAB": "RVOL 0.56 bullish, normPrice in [SAAB/Kratos th, 1x th)",
    "Kratos": "RVOL 0.56 bearish, normPrice in [SAAB/Kratos th, 1x th)",
    "Bull RVOL 1x": "RVOL 0.56 bull, normPrice in [1x th, GS/MOAB th)",
    "Bear RVOL 1x": "RVOL 0.56 bear, normPrice in [1x th, GS/MOAB th)",
    "Grand Slam": "RVOL 0.56 bull extreme (normPrice >= GS/MOAB th)",
    "MOAB": "RVOL 0.56 bear extreme (normPrice >= GS/MOAB th); default OFF",
    "WTC": "RVOL Reg@Time mid-tier (WTC th, Hiroshima th]",
    "Hiroshima": "RVOL Reg@Time top-tier (> Hiroshima th)",
    "Nagasaki (HEV)": "running all-time-high volume (Pine var maxVol)",
    "UU Signal": "2 consecutive bull bars (IPSF), sum>=seqTh_UU_DD",
    "UUU Signal": "3 consecutive bull bars (IPSF), sum>=seqTh_UUU_DDD",
    "UUUU Signal": "4 consecutive bull bars (IPSF), sum>=seqTh_UUUU_DDDD",
    "DD Signal": "2 consecutive bear bars (IPSF), sum>=seqTh_UU_DD",
    "DDD Signal": "3 consecutive bear bars (IPSF), sum>=seqTh_UUU_DDD",
    "DDDD Signal": "4 consecutive bear bars (IPSF), sum>=seqTh_UUUU_DDDD",
    "2x SAAB": "SAAB on bar[1] and bar[0]",
    "2x Kratos": "Kratos on bar[1] and bar[0]",
    "2x Bull 1x": "Bull RVOL 1x on bar[1] and bar[0]",
    "2x Bear 1x": "Bear RVOL 1x on bar[1] and bar[0]",
    "B2B Mid Bull": "mixed bull RVOL tiers (SAAB+1x) consecutive, not a pure 2x",
    "B2B Mid Bear": "mixed bear RVOL tiers (Kratos+1x) consecutive, not a pure 2x",
    "FAUNA Bull": "named bull combo present (MB/RE/GG/TA/TR/ES/GDR ladder)",
    "FAUNA Bear": "named bear combo present (MB/RE/GG/TA/TR/ES/GDR ladder)",
    "Disp Bull": "bar[1] in stdev displacement band + bull FVG (offset -1)",
    "Disp Bear": "bar[1] in stdev displacement band + bear FVG (offset -1)",
    "Consec Disp Bull 2+": "2+ back-to-back bull displacements (offset -1)",
    "Consec Disp Bear 2+": "2+ back-to-back bear displacements (offset -1)",
    "Consec Disp Bull 3+": "3+ back-to-back bull displacements (offset -1)",
    "Consec Disp Bear 3+": "3+ back-to-back bear displacements (offset -1)",
    "LONG 1": "hybrid momentum tier 1 bull (reg+cum ratio + body, auto-derived)",
    "SHORT 1": "hybrid momentum tier 1 bear",
    "LONG 2": "hybrid momentum tier 2 bull",
    "SHORT 2": "hybrid momentum tier 2 bear",
    "LONG 3": "hybrid momentum tier 3 bull (long-only)",
    "LONG 4": "hybrid momentum tier 4 bull (long-only)",
    "LONG 5": "hybrid momentum tier 5 bull (long-only)",
    "HV 1000": "volume[1]==highest(vol,1000)[1] (offset -1)",
    "HV 500": "volume[1]==highest(vol,500)[1] not 1000 (offset -1)",
    "HV 250": "volume[1]==highest(vol,250)[1] not 500+ (offset -1)",
    "HV 150": "volume[1]==highest(vol,150)[1] not 250+ (offset -1)",
    "HV 75": "volume[1]==highest(vol,75)[1] not 150+ (offset -1)",
    "Hot Spot": "calendar window (opEx/qtrEnd/Russell/taxLoss/janEffect/hfRedemp) on bar[1]",
}
