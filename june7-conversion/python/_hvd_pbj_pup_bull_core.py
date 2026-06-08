"""BASE HV+D <-> PBJ <-> PPD v1 — BULLISH (38) — FULL detection fire-matrix core.

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/hvd_pbj_pup_bull_tickfriendly.pine"
  //@version=5, indicator("BASE HV+D <-> PBJ v1 — BULLISH (38)",
  shorttitle="HVD PBJ BULL"), import TradingView/ta/7 as tv_ta.
  RE10023 tick guards already in source (reg_anchorSafe -> "D" on tick;
  tfSec -> TICK_FALLBACK_SEC=10 on tick; tfSecRaw guarded na).

ULTRACODE FULL PORT — scope statement (read this):
  This module ports EVERY one of the 38 detection plots in the source (38
  `plotshape(...)` detection signals; the alerts mirror the same fires), 1:1,
  directly from OHLCV. Pine `var`/history semantics are preserved (single forward
  pass; `[k]` = k-bars-back; `conf` = barstate.isconfirmed; `nz()` fallbacks
  honoured; recursive `:=` series carried as explicit state).

  This is the BULL half of the bull/bear split. The engine math + all internal
  booleans are byte-identical to the combined source / the bear core
  (_hvd_pbj_ppd_bear_core); only the PLOTTED detection layer differs (bull side).

  The 38 detection plots (PLOT_IDS, exactly the source plotshapes):
    HV+D family (3):     HV+D Bull, PB Bull, PBJ Bull
    USE bull (21):       Bull UUUU, Bull UUU, Bull UU, A* Bull, FOX Bull,
                         Omega-A, OD Bull, D2+ Bull, D3+ Bull, Golf Bull, PAF+,
                         CS1 FVG, CS2 MAT, Combo Bull, CC Bull, LSC Bull, Floor,
                         2F, HW Bull, S! Bull, SD! Bull
    NAG+ (1):            NAG+ Bull
    CO triple (2):       CO HV+D+PBJ+USE Bull, CO HV+D+PB+USE Bull
    Back-to-back (3):    B2B HV+D Bull, B2B HV+D+PBJ Bull, B2B HV+D+PB Bull
    Momentum co-occ (8): HV+D+PUP Bull, HV+D+RVOL Bull, HV+D+CMB Bull,
                         HV+D+PBJ+PUP Bull, HV+D+PBJ+RVOL Bull, HV+D+PBJ+CMB Bull,
                         HV+D+PBJ 2of3 Bull, HV+D+PBJ 3of3 Bull
  3 + 21 + 1 + 2 + 3 + 8 = 38.

  NOTE on Omega: the source computes BOTH sigOmegaLong and sigOmegaLongA, but
  only `fire_OmegaLongA` is a plotshape (line 1132). `sigOmegaLong` is computed
  (it participates in `use_any_bull` for the CO plots and in the dayDetFired
  latch); it has no standalone plot. So Omega-A is the single Omega detection
  plot. Boom Hunter (Ehlers HP / SuperSmoother quotients) + the Omega co-signal
  ladder are FULLY ported here (the bear core did not need them because the bear
  Omega plots were not in its 36; the bull side requires Omega-A).

  EVERY sub-engine in the Pine is ported (no stub layer):
    PIPELINE A  HV+D       volume-rank ladder (50..1000 + HEV) x displacement FVG
    ENGINE 1    RVOL 0.56  SAAB/Kratos/GrandSlam/MOAB/Bull1x/Bear1x (bb spike/vol)
    ENGINE 1b   RVOL Reg   WTC/Hiroshima/Pentagon via canonical relativeVolume shim
    Nagasaki               running all-time-high volume (Pine var maxVol)
    ENGINE 2    FAUNA      MB/RE/TA/GG + TR/ES/GDR exclusion ladder -> Bull/Bear
    ENGINE 3    DISP       Disp Bull/Bear + Consec 2+/3+ (FAUNA-gated streaks)
    ENGINE 4    GZ1/HV FVG fvg_struct array, overlap GZI + HV-tagged FVG
    ENGINE 5    PUP/PPD    price-move% vs highest opposite-colour vol
    ENGINE 6    PBJ        supertrend sig_line + lander/reaccel zone state machine
                          -> sigBullPBJ / sigBullPB (and bear mirror)
    ENGINE 7    Ping-Pong  S/R level array -> bull_pp floor-gravity / bear_pp
    Matrix(Neo)            is_matrix_number x FAUNA -> Neo/Trinity (+ regime align)
    Combo sets 1-4         FVG/Matrix x momentum -> csNew1/2/3
    CC / LSC chains        windowed combo / long-short streak activation
    UU/UUU/UUUU (P21)      IPSF streak + 9-flag scan (pA..pF) bull & bear
    Boom Hunter + Omega    Ehlers HP/SuperSmoother quotients -> omega co-signal
    Floor/2ndFloor         bull_pp x PBJ/PB x HW slot, gated by floor_gated/floor2
    HW / Super / SDuper    displacement5 + PBJ + HW slot + combo ladders
    Foxtrot / Golf / PAF   FAUNA streaks / PUP-PPD sequences
    OD (opening drive)     session bar count <= max x FVG x PUP/PPD x PBJ
    Alpha Strike           first-of-day x pp x GS/RVOL1x x PBJ x fauna ladder
    masterGate             First-Candle-of-Day gate (default OFF -> pass-through)

  relativeVolume ports via the canonical shim (_nn_harness.relative_volume ->
  rti/tv_ta_shim, ta/7) — NEVER re-derived as volume/sma(volume,N).

  Tick vs time: ONE code path. The ONLY grain-bound difference is the RVOL anchor
  ("D" wall-clock day on BOTH grains, per tradingview-import-decoupling, mirroring
  the Pine RE10023 fix of forcing "D" on tick) and tfSec (the per-TF threshold
  key), which is a Params field.

HONESTY: there is NO all-zero stub series in this module. Every plot in PLOT_IDS
is produced by real ported Pine logic. If a plot reads 0 on a tape it is because
the source logic produced 0 on those bars. The parity harness re-derives the core
engines independently and reports a REAL pass/total.

Cosmetic-only Pine objects intentionally NOT ported (not detection plots):
  - line.new S/R level drawings (Ping-Pong / PBJ zones) — banned graphic objects;
    their fire consequences (bull_pp, sigBullPBJ, etc.) ARE ported as logic.
  - the aggregated alert(...) message strings — derived from the same fires.
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nn_harness import (  # noqa: E402
    Bar, nz, sma, stdev, highest, atr as _atr_ohlc, shift, relative_volume,
)
from datetime import datetime, timezone  # noqa: E402


# ──────────────────────────────── parameters ────────────────────────────────
@dataclass
class Params:
    """Every Pine input.* / hardcoded threshold as a parameter (source default)."""
    tfSec: int = 60                  # per-TF threshold table key (seconds/bar)
    nn_tick_assumed_sec: int = 10    # Pine TICK_FALLBACK_SEC on tick charts

    # ---- MASTER ----
    en_firstBarOnly: bool = False
    en_aggregate: bool = True

    # ---- HV+D DISP BASE (pipeline A d1) ----
    d1_type: str = "Open to Close"
    d1_len: int = 100
    d1_mult: float = 5.0

    # ---- HV+D BASE HV ladder toggles ----
    ub50: bool = True; ub75: bool = True; ub100: bool = True; ub150: bool = True
    ub200: bool = True; ub250: bool = True; ub300: bool = True; ub350: bool = True
    ub400: bool = True; ub450: bool = True; ub500: bool = True; ub550: bool = True
    ub600: bool = True; ub650: bool = True; ub700: bool = True; ub750: bool = True
    ub1000: bool = True; useHEV: bool = True

    # ---- detection toggles (Tier 1 / 1b / 1c / 2 / 3 / 0) — bull defaults ----
    show_BullUUUU: bool = True; show_BullUUU: bool = True; show_BullUU: bool = False
    show_OmegaLongA: bool = False; show_AlphaStrikeB: bool = False
    show_FoxtrotB: bool = True; show_OmegaLong: bool = False; show_ODBull: bool = True
    show_DispConsBull2: bool = True; show_DispConsBull3: bool = True
    show_GolfBull: bool = True; show_PAFBull: bool = True
    show_NagPlusBull: bool = True; show_Nagasaki: bool = True
    show_CS1B: bool = False; show_CS2B: bool = False; show_CS3B: bool = True
    show_CCBull: bool = True; show_LSCBull: bool = False
    show_BullFloor: bool = False; show_Bull2ndFloor: bool = False
    show_HWBull: bool = True
    show_SuperBull: bool = False; show_SDuperBull: bool = True

    # ---- HV+D / PB / PBJ co-occurrence toggles (default OFF in source) ----
    en_hvd_bull: bool = False; en_hvd_pb_bull: bool = False; en_hvd_pbj_bull: bool = False
    co_en_bullPBJ: bool = False; co_en_bullPB: bool = False
    b2b_en_bull: bool = True; b2b_en_bull_pbj: bool = True; b2b_en_bull_pb: bool = True
    en_hvdm_pup_bull: bool = True; en_hvdm_rvol_bull: bool = True
    en_hvdm_cmb_bull: bool = True; en_hvdm_2of3_bull: bool = True; en_hvdm_3of3_bull: bool = True

    # ---- RVOL 0.56 (USE ALARM bb) ----
    bb_avgLength: int = 30
    bb_smaLength: int = 20

    # ---- RVOL Reg@Time ----
    reg_length: int = 30
    reg_calculationMode: str = "Cumulative"
    reg_adjustRealtime: bool = True

    # ---- FAUNA ----
    fauna_gg_master: bool = True
    fauna_gg_body: float = 0.80

    # ---- USE displacement ----
    i_disp_type: str = "Open to Close"
    i_std_len: int = 100
    i_std_min: float = 6.0
    i_std_max: float = 100.0
    i_req_fvg: bool = True

    i_disp2_type: str = "Open to Close"
    i_disp2_std_len: int = 100
    i_disp2_std_min: float = 5.0
    i_disp2_std_max: float = 100.0
    i_disp2_req_fvg: bool = True

    i_disp3_type: str = "Open to Close"
    i_disp3_std_len: int = 100
    i_disp3_std_min: float = 4.0
    i_disp3_std_max: float = 100.0
    i_disp3_req_fvg: bool = True

    # ---- GZ1 & HV FVG ----
    gz1_auto: bool = True
    gz1_thresh: float = 2.0
    gz1_dist: int = 12

    # ---- HV settings ----
    hv150_len: int = 150

    # ---- PUP/PPD ----
    pp_barSize: float = 3.0
    pp_lookback: int = 10

    # ---- PBJ (zoo) supertrend + zones ----
    zoo_ma_type: str = "VWMA"
    zoo_ma_len: int = 5
    enable_PB: bool = True
    zoo_pbj_ma_period: int = 20
    zoo_pbj_atr_period: int = 14
    zoo_pbj_hh_ll: int = 25
    zoo_pbj_atr_mult: float = 3.0
    zoo_pbj_vol_period: int = 20
    zoo_pbj_vol_mult: float = 0.1
    zoo_use_st: bool = True
    zoo_st_period: int = 10
    zoo_st_mult: float = 2.0

    # ---- Ping-Pong S/R ----
    pp_min_candles: int = 2
    pp_buffer_ticks: int = 10
    pp_atr_mult: float = 2.0
    pp_trend_cnt: int = 1
    pp_max_levels: int = 50
    pp_min_count: int = 3
    mintick: float = 0.01            # syminfo.mintick proxy

    # ---- Swingin (pivot) ----
    sw_leftBars: int = 5
    sw_rightBars: int = 1
    sw_useAtr: bool = True
    sw_atrMult: float = 2.0
    pp_atr_len: int = 100

    # ---- Opening drive ----
    od_max_bars: int = 2

    # ---- Matrix number (Neo) ----
    neo_len: int = 67

    # ---- Momentum 1 / 2 (long/short) ----
    ls_reg1: float = 10.0; ls_cum1: float = 5.0; ls_body1: float = 0.69
    ls_reg2: float = 8.0;  ls_cum2: float = 4.0; ls_body2: float = 0.69

    # ---- Combo set settings ----
    cs_bodyPct_FVG: float = 0.74
    cs_bodyPct_MAT: float = 0.74
    cs_inc_pentagon_FVG: bool = True
    cs_inc_pentagon_MAT: bool = True

    # ---- Combo chain ----
    cc_min_hits: int = 2
    cc_window: int = 2

    # ---- Long/Short chain ----
    lsc_min_hits: int = 2
    lsc_window: int = 2
    lsc_reg1: float = 10.0; lsc_cum1: float = 5.0; lsc_body1: float = 0.74
    lsc_reg2: float = 8.0;  lsc_cum2: float = 4.0; lsc_body2: float = 0.79

    # ---- Boom Hunter + Omega ----
    bh_LPPeriod: int = 6; bh_K1: float = 0.0; bh_trigno: int = 2
    bh_LPPeriod2: int = 27; bh_K12: float = 0.8; bh_K22: float = 0.3
    bh_LPPeriod3: int = 11; bh_n1: int = 9; bh_n2: int = 6; bh_n3: int = 3
    bh_n4: int = 21; bh_n5: int = 0
    bh_leftBars: int = 1; bh_rightBars: int = 1; bh_leftBars2: int = 5; bh_rightBars2: int = 5
    bh_lsmaline: int = 200


# 38 detection plots — stable ids (the deliverable fire matrix).
PLOT_IDS = [
    # HV+D family (3)
    "HVD_Bull", "PB_Bull", "PBJ_Bull",
    # USE bull (21)
    "BullUUUU", "BullUUU", "BullUU", "AlphaStrikeB", "FoxtrotB", "OmegaLongA",
    "ODBull", "DispConsBull2", "DispConsBull3", "GolfBull", "PAFBull",
    "CS1B", "CS2B", "CS3B", "CCBull", "LSCBull", "BullFloor", "Bull2ndFloor",
    "HWBull", "SuperBull", "SDuperBull",
    # NAG+ (1)
    "NagPlusBull",
    # CO triple co-occurrence (2)
    "CO_PBJ", "CO_PB",
    # Back-to-back (3)
    "B2B_Bull", "B2B_Bull_PBJ", "B2B_Bull_PB",
    # Momentum co-occ (8)
    "HVDM_PUP", "HVDM_RVOL", "HVDM_CMB",
    "HVDM_PBJ_PUP", "HVDM_PBJ_RVOL", "HVDM_PBJ_CMB",
    "HVDM_2of3", "HVDM_3of3",
]


# ──────────────────────────── small Pine helpers ────────────────────────────
def _nzb(series, i, off=0):
    """Pine nz(series[off]) for a boolean/None series at bar i (False fallback)."""
    j = i - off
    return bool(series[j]) if 0 <= j < len(series) else False


# ──────────────────────────────── ENGINE: ma ────────────────────────────────
def _ema(series, length):
    out = [None] * len(series)
    k = 2.0 / (length + 1)
    prev = None
    seed_sum = 0.0
    seed_cnt = 0
    for i, x in enumerate(series):
        xx = None if x is None else float(x)
        if xx is None:
            out[i] = prev
            continue
        if prev is None:
            seed_sum += xx
            seed_cnt += 1
            if seed_cnt == length:
                prev = seed_sum / length
                out[i] = prev
        else:
            prev = (xx - prev) * k + prev
            out[i] = prev
    return out


def _wma(series, length):
    out = [None] * len(series)
    denom = length * (length + 1) / 2.0
    for i in range(len(series)):
        if i + 1 < length:
            continue
        s = 0.0
        ok = True
        for j in range(length):
            val = series[i - j]
            if val is None:
                ok = False
                break
            s += val * (length - j)
        out[i] = (s / denom) if ok else None
    return out


def _hma(series, length):
    half = max(1, length // 2)
    sq = max(1, int(round(math.sqrt(length))))
    w_half = _wma(series, half)
    w_full = _wma(series, length)
    raw = [None if (w_half[i] is None or w_full[i] is None) else 2 * w_half[i] - w_full[i]
           for i in range(len(series))]
    return _wma(raw, sq)


def _vwma(price, volume, length):
    pv = [(price[i] * volume[i]) for i in range(len(price))]
    s_pv = sma(pv, length)
    s_v = sma(volume, length)
    out = [None] * len(price)
    for i in range(len(price)):
        if s_pv[i] is not None and s_v[i] not in (None, 0):
            out[i] = s_pv[i] / s_v[i]
    return out


def _ma(price, volume, length, t):
    if t == "EMA":
        return _ema(price, length)
    if t == "SMA":
        return sma(price, length)
    if t == "WMA":
        return _wma(price, length)
    if t == "HMA":
        return _hma(price, length)
    if t == "VWMA":
        return _vwma(price, volume, length)
    return sma(price, length)


# ════════════════════════════════ THE CORE ══════════════════════════════════
def compute(bars, params: Params | None = None, *, rv_anchor: str = "D"):
    """Single forward pass faithfully reproducing the Pine v5 bullish study.

    Returns dict:
      ts            : list[int] bar open timestamps
      fire_<id>     : list[int] 0/1 per bar for each of the 38 detection plots
      lvl_<id>      : list[float|None] a numeric level/debug scalar per plot
    """
    p = params or Params()
    n = len(bars)
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    l = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]
    conf = [True] * n
    tfSec = p.tfSec if (p.tfSec and p.tfSec > 0) else p.nn_tick_assumed_sec

    if n == 0:
        out = {"ts": []}
        for pid in PLOT_IDS:
            out[f"fire_{pid}"] = []
            out[f"lvl_{pid}"] = []
        return out

    # calendar / session helpers (UTC day; mirrors Pine time("D") day rollover) --
    def _day(i):
        return datetime.fromtimestamp(ts[i] / 1000, tz=timezone.utc).toordinal()

    is_new_day = [False] * n
    prev_day = None
    for i in range(n):
        d = _day(i)
        is_new_day[i] = (prev_day is None) or (d != prev_day)
        prev_day = d

    # session bar count (Pine sessionBarCount) — per-bar, 1-based reset each day
    sessionBarCount = [0] * n
    cnt = 0
    for i in range(n):
        if is_new_day[i]:
            cnt = 1
        else:
            cnt += 1
        sessionBarCount[i] = cnt

    isFirstBar = is_new_day  # session.isfirstbar proxy

    barRange = [h[i] - l[i] for i in range(n)]  # noqa: F841 (kept for _FIRST parity)
    atr14 = _atr_ohlc(o, h, l, c, 14)

    # ── masterGate (First-Candle-of-Day) ──
    HV_PERIODS = [50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550,
                  600, 650, 700, 750, 1000]
    hv_high = {per: highest(v, per) for per in HV_PERIODS}
    anyHV_bar0 = [False] * n
    for i in range(n):
        for per in HV_PERIODS:
            hp = hv_high[per][i]
            if hp is not None and v[i] == hp:
                anyHV_bar0[i] = True
                break
    masterGate = [(not p.en_firstBarOnly) or (isFirstBar[i] and anyHV_bar0[i]) for i in range(n)]

    # ════════════════ PIPELINE A: HV+D (vol rank[1] x displacement) ═══════════
    d1_rng = [abs(o[i] - c[i]) if p.d1_type == "Open to Close" else h[i] - l[i] for i in range(n)]
    d1_std = stdev(d1_rng, p.d1_len)
    d1_thr_1 = shift([None if x is None else x * p.d1_mult for x in d1_std], 1)
    d1_rng_1 = shift(d1_rng, 1)
    d1_prevDisp = [d1_thr_1[i] is not None and d1_rng_1[i] is not None and d1_rng_1[i] > d1_thr_1[i] for i in range(n)]

    def bullFVG(i):
        return i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1]

    def bearFVG(i):
        return i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1]

    d1_bull = [conf[i] and d1_prevDisp[i] and bullFVG(i) for i in range(n)]
    d1_bear = [conf[i] and d1_prevDisp[i] and bearFVG(i) for i in range(n)]

    v_1 = shift(v, 1)
    ub = {50: p.ub50, 75: p.ub75, 100: p.ub100, 150: p.ub150, 200: p.ub200,
          250: p.ub250, 300: p.ub300, 350: p.ub350, 400: p.ub400, 450: p.ub450,
          500: p.ub500, 550: p.ub550, 600: p.ub600, 650: p.ub650, 700: p.ub700,
          750: p.ub750, 1000: p.ub1000}
    hv_high_1 = {per: shift(hv_high[per], 1) for per in HV_PERIODS}
    baseRank = [0] * n
    for i in range(n):
        for per in reversed(HV_PERIODS):   # is1000 first -> highest wins
            hp1 = hv_high_1[per][i]
            if hp1 is not None and v_1[i] is not None and v_1[i] == hp1:
                baseRank[i] = per
                break
    base_enabled = [baseRank[i] != 0 and ub[baseRank[i]] for i in range(n)]
    # HEV: running all-time high on volume[1] (Pine var maxVolEver)
    isHEV = [False] * n
    mxever = 0.0
    for i in range(n):
        if v_1[i] is not None and v_1[i] > mxever:
            mxever = v_1[i]
            isHEV[i] = True
    hev_hit = [p.useHEV and isHEV[i] for i in range(n)]
    base_hv_hit = [hev_hit[i] or (base_enabled[i] and not isHEV[i]) for i in range(n)]
    hvd_fire_bull = [base_hv_hit[i] and d1_bull[i] for i in range(n)]
    hvd_fire_bear = [base_hv_hit[i] and d1_bear[i] for i in range(n)]

    # ════════════════ ENGINE 1: RVOL 0.56 (bb spike vs vol) ═══════════════════
    bb_spike = [abs(c[i] - o[i]) for i in range(n)]
    bb_avgSpikeDenom = shift(sma(bb_spike, p.bb_avgLength), 1)
    bb_normPrice = [_pdiv(bb_spike[i], nz(bb_avgSpikeDenom[i], 1.0)) for i in range(n)]
    bb_avgVolDenom = shift(sma(v, p.bb_avgLength), 1)
    bb_normVol = [_pdiv(v[i], nz(bb_avgVolDenom[i], 1.0)) for i in range(n)]
    bb_diff = [None if (bb_normPrice[i] is None or bb_normVol[i] is None) else bb_normPrice[i] - bb_normVol[i] for i in range(n)]
    bb_posDiff = [bb_diff[i] if (bb_diff[i] is not None and bb_diff[i] > 0) else None for i in range(n)]
    bb_smaDiff = _sma_with_na(bb_posDiff, p.bb_smaLength)
    bb_baseBullish = [c[i] > o[i] and bb_posDiff[i] is not None and bb_smaDiff[i] is not None and bb_posDiff[i] > bb_smaDiff[i] for i in range(n)]
    bb_baseBearish = [c[i] < o[i] and bb_posDiff[i] is not None and bb_smaDiff[i] is not None and bb_posDiff[i] > bb_smaDiff[i] for i in range(n)]

    def f_rvol_1x(s):
        return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else
                23.0 if s <= 45 else 20.0 if s <= 60 else 18.0 if s <= 120 else
                13.0 if s <= 300 else 13.0 if s <= 360 else 11.0 if s <= 540 else
                10.0 if s <= 600 else 9.0 if s <= 660 else 7.5 if s <= 900 else
                6.5 if s <= 1560 else 6.0 if s <= 2340 else 4.5 if s <= 3600 else
                4.0 if s <= 9000 else 3.5 if s <= 11700 else 1.8 if s < 259200 else 1.0)

    def f_gs_moab(s):
        if s < 60:
            return f_rvol_1x(s) * 3.0
        return (35.0 if s <= 300 else 25.0 if s <= 600 else 20.0 if s <= 1500 else
                20.0 if s <= 3000 else 10.0 if s <= 7260 else 8.0 if s <= 11700 else
                7.5 if s <= 86400 else 3.5 if s <= 259200 else 3.0)

    def f_wtc(s):
        return f_rvol_1x(s) * 2.0

    def f_hiroshima(s):
        if s < 60:
            return f_rvol_1x(s) * 3.0
        return (35.0 if s <= 300 else 25.0 if s <= 600 else 25.0 if s <= 1500 else
                20.0 if s <= 3060 else 10.0 if s <= 7260 else 8.0 if s <= 11700 else
                7.5 if s <= 86400 else 5.0 if s <= 259200 else 3.5)

    th_saab = f_rvol_1x(tfSec) * 0.56
    th_1x = f_rvol_1x(tfSec)
    th_gs = f_gs_moab(tfSec)
    th_wtc = f_wtc(tfSec)
    th_hir = f_hiroshima(tfSec)

    def inrange(x, lo, hi):
        return x is not None and x >= lo and x < hi

    def _ge(x, th):
        return x is not None and x >= th

    sigSAAB = [conf[i] and bb_baseBullish[i] and inrange(bb_normPrice[i], th_saab, th_1x) for i in range(n)]
    sigKratos = [conf[i] and bb_baseBearish[i] and inrange(bb_normPrice[i], th_saab, th_1x) for i in range(n)]
    sigGrandSlam = [conf[i] and bb_baseBullish[i] and _ge(bb_normPrice[i], th_gs) for i in range(n)]
    sigMOAB = [conf[i] and bb_baseBearish[i] and _ge(bb_normPrice[i], th_gs) for i in range(n)]
    sigBullRVOL1x = [conf[i] and bb_baseBullish[i] and inrange(bb_normPrice[i], th_1x, th_gs) and not sigGrandSlam[i] for i in range(n)]
    sigBearRVOL1x = [conf[i] and bb_baseBearish[i] and inrange(bb_normPrice[i], th_1x, th_gs) and not sigMOAB[i] for i in range(n)]

    # ── ENGINE 1b: Reg@Time RVOL via canonical shim (WTC/Hiroshima/Pentagon) ──
    cur_reg, past_reg, _ = relative_volume(v, p.reg_length, anchor_timeframe=rv_anchor,
                                           is_cumulative=(p.reg_calculationMode == "Cumulative"),
                                           bar_timestamps=ts)
    relVolRatio = [None] * n
    for i in range(n):
        if cur_reg[i] is not None and past_reg[i] not in (None, 0):
            relVolRatio[i] = cur_reg[i] / past_reg[i]
    sigWTC = [conf[i] and relVolRatio[i] is not None and relVolRatio[i] > th_wtc and relVolRatio[i] <= th_hir for i in range(n)]
    sigHiroshima = [conf[i] and relVolRatio[i] is not None and relVolRatio[i] > th_hir for i in range(n)]
    sigPentagon = [conf[i] and relVolRatio[i] is not None and relVolRatio[i] >= th_1x and relVolRatio[i] <= th_wtc for i in range(n)]

    # ── Nagasaki: running all-time-high volume (Pine var maxVol) ──
    sigNagasaki = [False] * n
    mxv = 0.0
    for i in range(n):
        if i == 0:
            mxv = v[i]
        elif v[i] > mxv:
            sigNagasaki[i] = True
            mxv = v[i]

    # reg + cum ratios for long/short (two separate shim calls, Pine lines 721-723)
    cur_r, past_r, _ = relative_volume(v, p.reg_length, anchor_timeframe=rv_anchor,
                                       is_cumulative=False, bar_timestamps=ts)
    cur_c, past_c, _ = relative_volume(v, p.reg_length, anchor_timeframe=rv_anchor,
                                       is_cumulative=True, bar_timestamps=ts)
    ls_regRatio = [nz((cur_r[i] / past_r[i]) if (cur_r[i] is not None and past_r[i] not in (None, 0)) else None) for i in range(n)]
    ls_cumRatio = [nz((cur_c[i] / past_c[i]) if (cur_c[i] is not None and past_c[i] not in (None, 0)) else None) for i in range(n)]
    ls_bodyRat = [0.0 if (h[i] - l[i]) == 0 else abs(c[i] - o[i]) / (h[i] - l[i]) for i in range(n)]
    sigLong1 = [conf[i] and ls_regRatio[i] > p.ls_reg1 and ls_cumRatio[i] > p.ls_cum1 and c[i] > o[i] and ls_bodyRat[i] >= p.ls_body1 for i in range(n)]
    sigShort1 = [conf[i] and ls_regRatio[i] > p.ls_reg1 and ls_cumRatio[i] > p.ls_cum1 and c[i] < o[i] and ls_bodyRat[i] >= p.ls_body1 for i in range(n)]
    sigLong2 = [conf[i] and ls_regRatio[i] > p.ls_reg2 and ls_cumRatio[i] > p.ls_cum2 and c[i] > o[i] and ls_bodyRat[i] >= p.ls_body2 for i in range(n)]
    sigShort2 = [conf[i] and ls_regRatio[i] > p.ls_reg2 and ls_cumRatio[i] > p.ls_cum2 and c[i] < o[i] and ls_bodyRat[i] >= p.ls_body2 for i in range(n)]

    # ════════════════ ENGINE 2: FAUNA bull/bear ═══════════════════════════════
    avgVol = sma(v, 20)
    avgBody = sma([abs(c[i] - o[i]) for i in range(n)], 20)
    avgDelta = sma([abs(c[i] - c[i - 1]) if i > 0 else 0.0 for i in range(n)], 10)
    trendMA = sma(c, 50)
    avgBody_1 = shift(avgBody, 1)
    avgVol_1 = shift(avgVol, 1)
    sigFAUNABull = [False] * n
    sigFAUNABear = [False] * n
    for i in range(n):
        if atr14[i] is None or avgVol[i] is None:
            continue
        body = c[i] - o[i]
        rng = h[i] - l[i]
        up, dn = body > 0, body < 0
        bsz = abs(body)
        brat = 0.0 if rng == 0 else bsz / rng
        MB_b = up and bsz > 1.6 * atr14[i] and brat > 0.70 and v[i] > 1.8 * avgVol[i]
        RE_b = up and rng > 2.2 * atr14[i] and (h[i] - c[i]) < 0.15 * rng and v[i] > 1.8 * avgVol[i]
        TA_b = (i > 0 and trendMA[i] is not None and trendMA[i - 1] is not None and trendMA[i] > trendMA[i - 1]
                and avgDelta[i] is not None and (c[i] - c[i - 1]) > 1.6 * avgDelta[i] and up and v[i] > 1.8 * avgVol[i])
        MB_r = dn and bsz > 1.6 * atr14[i] and brat > 0.70 and v[i] > 1.8 * avgVol[i]
        RE_r = dn and rng > 2.2 * atr14[i] and (c[i] - l[i]) < 0.15 * rng and v[i] > 1.8 * avgVol[i]
        TA_r = (i > 0 and trendMA[i] is not None and trendMA[i - 1] is not None and trendMA[i] < trendMA[i - 1]
                and avgDelta[i] is not None and (c[i - 1] - c[i]) > 1.6 * avgDelta[i] and dn and v[i] > 1.8 * avgVol[i])
        excl_b = excl_r = False
        if i > 0 and avgBody_1[i] is not None and avgVol_1[i] is not None:
            GG_b = (o[i] - c[i - 1]) > 0.9 * atr14[i] and up and l[i] > c[i - 1] and v[i] > 1.8 * avgVol[i]
            GG_r = (c[i - 1] - o[i]) > 0.9 * atr14[i] and dn and h[i] < c[i - 1] and v[i] > 1.8 * avgVol[i]
            pbody = c[i - 1] - o[i - 1]
            prange = h[i - 1] - l[i - 1]
            StrongBear = c[i - 1] < o[i - 1] and abs(pbody) > 1.5 * avgBody_1[i] and v[i - 1] > 1.5 * avgVol_1[i]
            WeakBear = c[i - 1] < o[i - 1] and (0.0 if prange == 0 else abs(pbody) / prange) <= 0.2
            StrongBull = c[i - 1] > o[i - 1] and abs(pbody) > 1.5 * avgBody_1[i] and v[i - 1] > 1.5 * avgVol_1[i]
            WeakBull = c[i - 1] > o[i - 1] and (0.0 if prange == 0 else abs(pbody) / prange) <= 0.2
            b_core = (1 if MB_b else 0) + (1 if RE_b else 0) + (1 if TA_b else 0)
            b_gg_pass = p.fauna_gg_master and b_core >= 2 and brat >= p.fauna_gg_body
            excl_b = ((WeakBear and (MB_b or RE_b or TA_b)) or (StrongBear and (MB_b or RE_b or TA_b))
                      or (c[i - 1] < o[i - 1] and GG_b) or (GG_b and not b_gg_pass))
            s_core = (1 if MB_r else 0) + (1 if RE_r else 0) + (1 if TA_r else 0)
            s_gg_pass = p.fauna_gg_master and s_core >= 2 and brat >= p.fauna_gg_body
            excl_r = ((WeakBull and (MB_r or RE_r or TA_r)) or (StrongBull and (MB_r or RE_r or TA_r))
                      or (c[i - 1] > o[i - 1] and GG_r) or (GG_r and not s_gg_pass))
        sigFAUNABull[i] = conf[i] and (MB_b or RE_b or TA_b) and not excl_b
        sigFAUNABear[i] = conf[i] and (MB_r or RE_r or TA_r) and not excl_r

    # ════════════════ ENGINE 3: USE DISPLACEMENT ══════════════════════════════
    disp_rng = [abs(o[i] - c[i]) if p.i_disp_type == "Open to Close" else h[i] - l[i] for i in range(n)]
    disp_std = stdev(disp_rng, p.i_std_len)
    disp_rng_1 = shift(disp_rng, 1)
    disp_std_1 = shift(disp_std, 1)
    disp_prevDisp = [disp_std_1[i] is not None and disp_rng_1[i] is not None and disp_rng_1[i] > disp_std_1[i] * p.i_std_min and disp_rng_1[i] <= disp_std_1[i] * p.i_std_max for i in range(n)]
    disp_currDisp = [disp_std[i] is not None and disp_rng[i] > disp_std[i] * p.i_std_min and disp_rng[i] <= disp_std[i] * p.i_std_max for i in range(n)]
    sigDISPBull = [conf[i] and ((disp_prevDisp[i] and bullFVG(i)) if p.i_req_fvg else (disp_currDisp[i] and c[i] > o[i])) for i in range(n)]
    sigDISPBear = [conf[i] and ((disp_prevDisp[i] and bearFVG(i)) if p.i_req_fvg else (disp_currDisp[i] and c[i] < o[i])) for i in range(n)]
    disp5_bull = [conf[i] and disp_std[i] is not None and disp_std[i] > 0 and disp_rng[i] > disp_std[i] * 5.0 and c[i] > o[i] for i in range(n)]
    disp5_bear = [conf[i] and disp_std[i] is not None and disp_std[i] > 0 and disp_rng[i] > disp_std[i] * 5.0 and c[i] < o[i] for i in range(n)]

    # disp2 / disp3 banded + streak (FAUNA-gated). Pine uses i_disp2_type/i_disp3_type
    # for the range type per band.
    def _disp_band_streak(disp_type, std_len, mn, mx_, req_fvg, streak_req, fauna_back):
        rngd = [abs(o[i] - c[i]) if disp_type == "Open to Close" else h[i] - l[i] for i in range(n)]
        stdv = stdev(rngd, std_len)
        stdv_1 = shift(stdv, 1)
        rng_1 = shift(rngd, 1)
        sigBull = [False] * n
        sigBear = [False] * n
        for i in range(n):
            if req_fvg:
                sigBull[i] = conf[i] and stdv_1[i] is not None and rng_1[i] is not None and rng_1[i] > stdv_1[i] * mn and rng_1[i] <= stdv_1[i] * mx_ and (i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1])
                sigBear[i] = conf[i] and stdv_1[i] is not None and rng_1[i] is not None and rng_1[i] > stdv_1[i] * mn and rng_1[i] <= stdv_1[i] * mx_ and (i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1])
            else:
                sigBull[i] = conf[i] and stdv[i] is not None and rngd[i] > stdv[i] * mn and rngd[i] <= stdv[i] * mx_ and c[i] > o[i]
                sigBear[i] = conf[i] and stdv[i] is not None and rngd[i] > stdv[i] * mn and rngd[i] <= stdv[i] * mx_ and c[i] < o[i]
        outBull = [False] * n
        outBear = [False] * n
        sb = 0
        sr = 0
        for i in range(n):
            sb = sb + 1 if sigBull[i] else 0
            sr = sr + 1 if sigBear[i] else 0
            fb = all(_nzb(sigFAUNABull, i, k) for k in range(1, fauna_back + 1))
            fr = all(_nzb(sigFAUNABear, i, k) for k in range(1, fauna_back + 1))
            outBull[i] = sigBull[i] and sb >= streak_req and fb
            outBear[i] = sigBear[i] and sr >= streak_req and fr
        return outBull, outBear

    sigDispConsBull2, sigDispConsBear2 = _disp_band_streak(
        p.i_disp2_type, p.i_disp2_std_len, p.i_disp2_std_min, p.i_disp2_std_max, p.i_disp2_req_fvg, 2, 2)
    sigDispConsBull3, sigDispConsBear3 = _disp_band_streak(
        p.i_disp3_type, p.i_disp3_std_len, p.i_disp3_std_min, p.i_disp3_std_max, p.i_disp3_req_fvg, 3, 3)

    # ════════════════ ENGINE 4: GZ1 / HV FVG arrays ═══════════════════════════
    _hv5000 = shift(highest(v, 5000), 1)
    _hv252 = shift(highest(v, 252), 1)
    _hv63 = shift(highest(v, 63), 1)
    gz_v1 = shift(v, 1)
    gz_isHV = [gz_v1[i] is not None and ((gz_v1[i] == _hv5000[i]) or (gz_v1[i] == _hv252[i]) or (gz_v1[i] == _hv63[i])) for i in range(n)]
    cum_hl = 0.0
    gz_bullGZI = [False] * n
    gz_bearGZI = [False] * n
    gz_bullHV = [False] * n
    gz_bearHV = [False] * n
    fvgs = []   # list of dict(mx,mn,bull,t,idx,hv)
    gz_lastT = None
    for i in range(n):
        cum_hl += (h[i] - l[i]) / l[i] if l[i] != 0 else 0.0
        gz_thresh = (cum_hl / (i + 1)) if p.gz1_auto else (p.gz1_thresh / 100.0)
        bFVG = (i >= 2 and l[i] > h[i - 2] and c[i - 1] > h[i - 2] and h[i - 2] != 0 and (l[i] - h[i - 2]) / h[i - 2] > gz_thresh)
        sFVG = (i >= 2 and h[i] < l[i - 2] and c[i - 1] < l[i - 2] and h[i] != 0 and (l[i - 2] - h[i]) / h[i] > gz_thresh)
        t_i = ts[i]
        if conf[i] and bFVG and t_i != gz_lastT:
            mx, mn = l[i], h[i - 2]
            if gz_isHV[i]:
                gz_bullHV[i] = True
            for e in fvgs:
                if e["bull"] and i - e["idx"] <= p.gz1_dist:
                    if max(e["mn"], mn) < min(e["mx"], mx) or (max(e["mn"], mn) <= min(e["mx"], mx) and e["hv"] and gz_isHV[i]):
                        gz_bullGZI[i] = True
                        break
            fvgs.insert(0, {"mx": mx, "mn": mn, "bull": True, "t": t_i, "idx": i, "hv": gz_isHV[i]})
            gz_lastT = t_i
        if conf[i] and sFVG and t_i != gz_lastT:
            mx, mn = l[i - 2], h[i]
            if gz_isHV[i]:
                gz_bearHV[i] = True
            for e in fvgs:
                if (not e["bull"]) and i - e["idx"] <= p.gz1_dist:
                    if max(e["mn"], mn) < min(e["mx"], mx) or (max(e["mn"], mn) <= min(e["mx"], mx) and e["hv"] and gz_isHV[i]):
                        gz_bearGZI[i] = True
                        break
            fvgs.insert(0, {"mx": mx, "mn": mn, "bull": False, "t": t_i, "idx": i, "hv": gz_isHV[i]})
            gz_lastT = t_i
        fvgs = [g for g in fvgs if not ((g["bull"] and c[i] < g["mn"]) or ((not g["bull"]) and c[i] > g["mx"]))]
        if len(fvgs) > 50:
            fvgs.pop()

    # ════════════════ ENGINE 5: PUP / PPD ═════════════════════════════════════
    pp_redVol = [v[i] if c[i] < o[i] else 0.0 for i in range(n)]
    pp_greenVol = [v[i] if c[i] > o[i] else 0.0 for i in range(n)]
    pp_hiRed = highest(shift(pp_redVol, 1), p.pp_lookback)
    pp_hiGreen = highest(shift(pp_greenVol, 1), p.pp_lookback)
    sigPUP = [False] * n
    sigPPD = [False] * n
    for i in range(n):
        priceUp = ((c[i] - o[i]) / o[i]) * 100 > p.pp_barSize if o[i] != 0 else False
        priceDn = ((o[i] - c[i]) / o[i]) * 100 > p.pp_barSize if o[i] != 0 else False
        sigPUP[i] = conf[i] and priceUp and pp_hiRed[i] is not None and v[i] > pp_hiRed[i]
        sigPPD[i] = conf[i] and priceDn and pp_hiGreen[i] is not None and v[i] > pp_hiGreen[i]

    # ════════════════ ENGINE 6: PBJ (supertrend + lander/reaccel zones) ═══════
    base_ma = _ma(c, v, p.zoo_ma_len, p.zoo_ma_type)
    st_atr = [None if a is None else p.zoo_st_mult * a for a in _atr_ohlc(o, h, l, c, p.zoo_st_period)]
    curr_long = [0.0] * n
    curr_short = [0.0] * n
    st_dir = [1] * n
    sig_line = [None] * n
    for i in range(n):
        bm = base_ma[i]
        sa = st_atr[i]
        if bm is None or sa is None:
            curr_long[i] = curr_long[i - 1] if i > 0 else 0.0
            curr_short[i] = curr_short[i - 1] if i > 0 else 0.0
            st_dir[i] = st_dir[i - 1] if i > 0 else 1
            sig_line[i] = sig_line[i - 1] if i > 0 else None
            continue
        prev_cl = curr_long[i - 1] if i > 0 else (bm - sa)
        prev_cs = curr_short[i - 1] if i > 0 else (bm + sa)
        cl = max(bm - sa, prev_cl) if bm > nz(prev_cl, bm - sa) else (bm - sa)
        cs = min(bm + sa, prev_cs) if bm < nz(prev_cs, bm + sa) else (bm + sa)
        curr_long[i] = cl
        curr_short[i] = cs
        d_prev = st_dir[i - 1] if i > 0 else 1
        if p.zoo_use_st:
            d = d_prev
            if d_prev == -1 and c[i] > prev_cs:
                d = 1
            elif d_prev == 1 and c[i] < prev_cl:
                d = -1
            st_dir[i] = d
            sig_line[i] = cl if d == 1 else cs
        else:
            st_dir[i] = d_prev
            sig_line[i] = bm

    def _crossover(a, b, i):
        return i > 0 and a[i] is not None and b[i] is not None and a[i - 1] is not None and b[i - 1] is not None and a[i] > b[i] and a[i - 1] <= b[i - 1]

    def _crossunder(a, b, i):
        return i > 0 and a[i] is not None and b[i] is not None and a[i - 1] is not None and b[i - 1] is not None and a[i] < b[i] and a[i - 1] >= b[i - 1]

    buy_cross = [_crossover(c, sig_line, i) for i in range(n)]
    sell_cross = [_crossunder(c, sig_line, i) for i in range(n)]
    bull_reaccel = [st_dir[i] == 1 and i >= 2 and sig_line[i] is not None and sig_line[i - 1] is not None and sig_line[i - 2] is not None and sig_line[i] > sig_line[i - 1] and sig_line[i - 1] == sig_line[i - 2] for i in range(n)]
    bear_reaccel = [st_dir[i] == -1 and i >= 2 and sig_line[i] is not None and sig_line[i - 1] is not None and sig_line[i - 2] is not None and sig_line[i] < sig_line[i - 1] and sig_line[i - 1] == sig_line[i - 2] for i in range(n)]

    pbj_ma = _ema(c, p.zoo_pbj_ma_period)
    pbj_atr = _atr_ohlc(o, h, l, c, p.zoo_pbj_atr_period)
    zoo_avg_vol = sma(v, p.zoo_pbj_vol_period)
    lowest_ll = _lowest(l, p.zoo_pbj_hh_ll)
    highest_hh = highest(h, p.zoo_pbj_hh_ll)
    pbj_buy = [False] * n
    pbj_sell = [False] * n
    for i in range(n):
        if pbj_ma[i] is None or pbj_atr[i] is None or zoo_avg_vol[i] is None or c[i] == 0:
            continue
        thresh = pbj_atr[i] / c[i] * p.zoo_pbj_atr_mult
        pbj_buy[i] = l[i] < pbj_ma[i] * (1 - thresh) and lowest_ll[i] is not None and l[i] == lowest_ll[i] and v[i] > zoo_avg_vol[i] * p.zoo_pbj_vol_mult
        pbj_sell[i] = h[i] > pbj_ma[i] * (1 + thresh) and highest_hh[i] is not None and h[i] == highest_hh[i] and v[i] > zoo_avg_vol[i] * p.zoo_pbj_vol_mult

    atr_pb = [None if a is None else a * 2.0 for a in atr14]
    bull_lvls = []
    bear_lvls = []
    wait_buy = wait_sell = wait_pbj_buy = wait_pbj_sell = False
    sigBullPBJ = [False] * n
    sigBullPB = [False] * n
    sigBearPBJ = [False] * n
    sigBearPB = [False] * n

    def _add_lvl(arr, up, lo, vol):
        if abs(up - lo) >= p.mintick:
            arr.append({"upper": up, "lower": lo, "vol": vol, "approached": False})

    for i in range(n):
        apb = atr_pb[i] if atr_pb[i] is not None else 0.0
        if buy_cross[i] and i >= 1:
            up = max(o[i - 1], c[i - 1]); lo = l[i - 1]
            if up - lo < apb * 0.5:
                up = lo + apb * 0.5
            _add_lvl(bull_lvls, up, lo, v[i - 1])
        if sell_cross[i] and i >= 1:
            up = h[i - 1]; lo = min(o[i - 1], c[i - 1])
            if up - lo < apb * 0.5:
                lo = up - apb * 0.5
            _add_lvl(bear_lvls, up, lo, v[i - 1])
        if bull_reaccel[i] and sig_line[i] is not None:
            p1 = sig_line[i]; p2 = min(o[i], c[i])
            _add_lvl(bull_lvls, max(p1, p2), min(p1, p2), v[i])
        if bear_reaccel[i] and sig_line[i] is not None:
            p1 = sig_line[i]; p2 = max(o[i], c[i])
            _add_lvl(bear_lvls, max(p1, p2), min(p1, p2), v[i])

        if conf[i]:
            appr_b = False
            for j in range(len(bull_lvls) - 1, -1, -1):
                lv = bull_lvls[j]
                if c[i] < lv["lower"]:
                    bull_lvls.pop(j)
                    continue
                ap = lv["upper"] * 1.005
                if not lv["approached"] and l[i] <= ap:
                    appr_b = True
                    lv["approached"] = True
                elif lv["approached"] and l[i] > lv["upper"]:
                    lv["approached"] = False
            if appr_b:
                wait_buy = True
            appr_s = False
            for j in range(len(bear_lvls) - 1, -1, -1):
                lv = bear_lvls[j]
                if c[i] > lv["upper"]:
                    bear_lvls.pop(j)
                    continue
                ap = lv["lower"] * 0.995
                if not lv["approached"] and h[i] >= ap:
                    appr_s = True
                    lv["approached"] = True
                elif lv["approached"] and h[i] < lv["lower"]:
                    lv["approached"] = False
            if appr_s:
                wait_sell = True
        if pbj_buy[i]:
            wait_pbj_buy = True
        if pbj_sell[i]:
            wait_pbj_sell = True
        while len(bull_lvls) > 30:
            bull_lvls.pop(0)
        while len(bear_lvls) > 30:
            bear_lvls.pop(0)

        sig_pbj_buy = buy_cross[i] and wait_pbj_buy
        sig_pb_buy = buy_cross[i] and wait_buy
        sig_pbj_sell = sell_cross[i] and wait_pbj_sell
        sig_pb_sell = sell_cross[i] and wait_sell
        if sig_pb_buy:
            wait_buy = False
        if sig_pbj_buy:
            wait_pbj_buy = False
        if sig_pb_sell:
            wait_sell = False
        if sig_pbj_sell:
            wait_pbj_sell = False
        sigBullPBJ[i] = conf[i] and sig_pbj_buy
        sigBullPB[i] = conf[i] and p.enable_PB and sig_pb_buy and not sig_pbj_buy
        sigBearPBJ[i] = conf[i] and sig_pbj_sell
        sigBearPB[i] = conf[i] and p.enable_PB and sig_pb_sell and not sig_pbj_sell

    # ════════════════ ENGINE 7: PING-PONG S/R ═════════════════════════════════
    pp_atr = _atr_ohlc(o, h, l, c, p.pp_atr_len)
    raw_high = _pivothigh(h, p.sw_leftBars, p.sw_rightBars)
    raw_low = _pivotlow(l, p.sw_leftBars, p.sw_rightBars)
    bull_pp = [False] * n
    bear_pp = [False] * n
    srLevels = []
    last_bounce_side = 0
    lastBreakType = None
    lastValidSwingLevel = None

    for i in range(n):
        sig_bull_break = sig_bear_break = sig_res_bounce = sig_sup_bounce = None
        sig_piv_bull = sig_piv_bear = sig_res_reject = sig_sup_reject = None
        bullRegime = False
        bearRegime = False
        body_top = max(o[i], c[i])
        body_bot = min(o[i], c[i])
        price_tol = max(p.mintick * p.pp_buffer_ticks, p.mintick / 10)
        is_new_flat_res = True
        is_new_flat_sup = True
        for k in range(p.pp_min_candles):
            if i - k < 0:
                continue
            if abs(max(o[i - k], c[i - k]) - body_top) > price_tol:
                is_new_flat_res = False
            if abs(min(o[i - k], c[i - k]) - body_bot) > price_tol:
                is_new_flat_sup = False

        thresholdSwing = (pp_atr[i] * p.sw_atrMult) if (p.sw_useAtr and pp_atr[i] is not None) else 0.0
        validSwingHigh = False
        if raw_high[i] is not None:
            if lastValidSwingLevel is None or abs(raw_high[i] - lastValidSwingLevel) >= thresholdSwing:
                validSwingHigh = True
                lastValidSwingLevel = raw_high[i]
        validSwingLow = False
        if raw_low[i] is not None:
            if lastValidSwingLevel is None or abs(raw_low[i] - lastValidSwingLevel) >= thresholdSwing:
                validSwingLow = True
                lastValidSwingLevel = raw_low[i]

        def _has_level(price, tv):
            for lv in srLevels:
                if abs(lv["price"] - price) <= price_tol and lv["levelType"] == tv:
                    return True
            return False

        if is_new_flat_res and not _has_level(body_top, 1):
            srLevels.append({"price": body_top, "levelType": 1, "originType": 0, "state": 0, "count": 0})
        if is_new_flat_sup and not _has_level(body_bot, -1):
            srLevels.append({"price": body_bot, "levelType": -1, "originType": 0, "state": 0, "count": 0})
        if validSwingHigh:
            srLevels.append({"price": raw_high[i], "levelType": 1, "originType": 1, "state": 1, "count": 0})
        if validSwingLow:
            srLevels.append({"price": raw_low[i], "levelType": -1, "originType": 1, "state": 1, "count": 0})

        atrmult = (pp_atr[i] * p.pp_atr_mult) if pp_atr[i] is not None else 0.0
        for j in range(len(srLevels) - 1, -1, -1):
            lv = srLevels[j]
            remove_lv = False
            if lv["levelType"] == 1:
                if c[i] > lv["price"]:
                    if lv["state"] == 1 or lv["originType"] == 1:
                        sig_bull_break = h[i]
                        if lastBreakType == "BD":
                            bullRegime = True
                        lastBreakType = "BO"
                    remove_lv = True
                else:
                    if (lv["state"] == 1 or lv["originType"] == 1) and h[i] >= lv["price"]:
                        sig_res_reject = h[i]
                        lv["count"] = 0
                    if lv["state"] == 0 or (lv["state"] == 1 and lv["count"] >= 0):
                        if c[i] < o[i]:
                            lv["count"] += 1
                        if (lv["price"] - c[i]) > atrmult and lv["count"] >= p.pp_trend_cnt:
                            if lv["state"] == 0:
                                lv["state"] = 1
                            lv["count"] = -1
                            sig_res_bounce = h[i]
                            if last_bounce_side == 1:
                                sig_piv_bear = h[i]
                            last_bounce_side = -1
            else:  # levelType == -1
                if c[i] < lv["price"]:
                    if lv["state"] == 1 or lv["originType"] == 1:
                        sig_bear_break = l[i]
                        if lastBreakType == "BO":
                            bearRegime = True
                        lastBreakType = "BD"
                    remove_lv = True
                else:
                    if (lv["state"] == 1 or lv["originType"] == 1) and l[i] <= lv["price"]:
                        sig_sup_reject = l[i]
                        lv["count"] = 0
                    if lv["state"] == 0 or (lv["state"] == 1 and lv["count"] >= 0):
                        if c[i] > o[i]:
                            lv["count"] += 1
                        if (c[i] - lv["price"]) > atrmult and lv["count"] >= p.pp_trend_cnt:
                            if lv["state"] == 0:
                                lv["state"] = 1
                            lv["count"] = -1
                            sig_sup_bounce = l[i]
                            if last_bounce_side == -1:
                                sig_piv_bull = l[i]
                            last_bounce_side = 1
            if remove_lv:
                srLevels.pop(j)
        while len(srLevels) > p.pp_max_levels:
            srLevels.pop(0)

        bull_state = (32 if validSwingLow else 0) + (16 if sig_piv_bull is not None else 0) + (8 if bullRegime else 0) + (4 if sig_sup_bounce is not None else 0) + (2 if sig_bull_break is not None else 0) + (1 if sig_res_reject is not None else 0)
        bull_cnt = (1 if validSwingLow else 0) + (1 if sig_piv_bull is not None else 0) + (1 if bullRegime else 0) + (1 if sig_sup_bounce is not None else 0) + (1 if sig_bull_break is not None else 0) + (1 if sig_res_reject is not None else 0)
        bull_floor_grav = (bull_state % 8 >= 4) or (bull_state % 32 >= 16) or (bull_state >= 32)
        bear_state = (32 if validSwingHigh else 0) + (16 if sig_piv_bear is not None else 0) + (8 if bearRegime else 0) + (4 if sig_res_bounce is not None else 0) + (2 if sig_bear_break is not None else 0) + (1 if sig_sup_reject is not None else 0)
        bear_cnt = (1 if validSwingHigh else 0) + (1 if sig_piv_bear is not None else 0) + (1 if bearRegime else 0) + (1 if sig_res_bounce is not None else 0) + (1 if sig_bear_break is not None else 0) + (1 if sig_sup_reject is not None else 0)
        bear_ceil_grav = (bear_state % 8 >= 4) or (bear_state % 32 >= 16) or (bear_state >= 32)
        bull_pp[i] = bull_cnt >= p.pp_min_count and bull_floor_grav and bull_state > 0
        bear_pp[i] = bear_cnt >= p.pp_min_count and bear_ceil_grav and bear_state > 0

    # ════════════════ Matrix (Neo) + regime align ═════════════════════════════
    hv_neo = highest(v, p.neo_len)
    is_matrix = [hv_neo[i] is not None and v[i] == hv_neo[i] for i in range(n)]
    sigNeoBull = [conf[i] and is_matrix[i] and sigFAUNABull[i] for i in range(n)]
    sigNeoBear = [conf[i] and is_matrix[i] and sigFAUNABear[i] for i in range(n)]
    sigTrinityBull = [conf[i] and is_matrix[i] and not sigFAUNABull[i] and c[i] > o[i] for i in range(n)]
    sigTrinityBear = [conf[i] and is_matrix[i] and not sigFAUNABear[i] and c[i] < o[i] for i in range(n)]
    neo_bull_aligned = [sigNeoBull[i] and (sigLong1[i] or sigLong2[i]) for i in range(n)]
    neo_bear_aligned = [sigNeoBear[i] and (sigShort1[i] or sigShort2[i]) for i in range(n)]
    trinity_bull_aligned = [sigTrinityBull[i] and (sigLong1[i] or sigLong2[i]) for i in range(n)]
    trinity_bear_aligned = [sigTrinityBear[i] and (sigShort1[i] or sigShort2[i]) for i in range(n)]

    sigFoxtrotBull = [conf[i] and i >= 3 and sigFAUNABull[i] and _nzb(sigFAUNABull, i, 1) and _nzb(sigFAUNABull, i, 2) and _nzb(sigFAUNABull, i, 3) for i in range(n)]
    sigFoxtrotBear = [conf[i] and i >= 3 and sigFAUNABear[i] and _nzb(sigFAUNABear, i, 1) and _nzb(sigFAUNABear, i, 2) and _nzb(sigFAUNABear, i, 3) for i in range(n)]

    # ════════════════ Combo sets 1-4 ══════════════════════════════════════════
    cs_bp1 = [0.0 if (i < 1 or (h[i - 1] - l[i - 1]) == 0) else abs(c[i - 1] - o[i - 1]) / (h[i - 1] - l[i - 1]) for i in range(n)]
    cs_vb = [cs_bp1[i] >= p.cs_bodyPct_FVG for i in range(n)]
    comboSet1_Bull = [conf[i] and cs_vb[i] and (gz_bullHV[i] or gz_bullGZI[i]) and (_nzb(sigSAAB, i, 1) or _nzb(sigBullRVOL1x, i, 1) or _nzb(sigGrandSlam, i, 1)) for i in range(n)]
    comboSet1_Bear = [conf[i] and cs_vb[i] and (gz_bearHV[i] or gz_bearGZI[i]) and (_nzb(sigKratos, i, 1) or _nzb(sigBearRVOL1x, i, 1) or _nzb(sigMOAB, i, 1)) for i in range(n)]
    comboSet2_Bull = [conf[i] and cs_vb[i] and (gz_bullHV[i] or gz_bullGZI[i]) and ((p.cs_inc_pentagon_FVG and _nzb(sigPentagon, i, 1)) or _nzb(sigWTC, i, 1) or _nzb(sigHiroshima, i, 1) or _nzb(sigNagasaki, i, 1)) for i in range(n)]
    comboSet2_Bear = [conf[i] and cs_vb[i] and (gz_bearHV[i] or gz_bearGZI[i]) and ((p.cs_inc_pentagon_FVG and _nzb(sigPentagon, i, 1)) or _nzb(sigWTC, i, 1) or _nzb(sigHiroshima, i, 1) or _nzb(sigNagasaki, i, 1)) for i in range(n)]
    cs_vm = [ls_bodyRat[i] >= p.cs_bodyPct_MAT for i in range(n)]
    matrix_any_bull = [sigNeoBull[i] or sigTrinityBull[i] or neo_bull_aligned[i] or trinity_bull_aligned[i] for i in range(n)]
    matrix_any_bear = [sigNeoBear[i] or sigTrinityBear[i] or neo_bear_aligned[i] or trinity_bear_aligned[i] for i in range(n)]
    comboSet3_Bull = [cs_vm[i] and matrix_any_bull[i] and (sigSAAB[i] or sigBullRVOL1x[i] or sigGrandSlam[i]) for i in range(n)]
    comboSet3_Bear = [cs_vm[i] and matrix_any_bear[i] and (sigKratos[i] or sigBearRVOL1x[i] or sigMOAB[i]) for i in range(n)]
    comboSet4_Bull = [cs_vm[i] and matrix_any_bull[i] and ((p.cs_inc_pentagon_MAT and sigPentagon[i]) or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i]) for i in range(n)]
    comboSet4_Bear = [cs_vm[i] and matrix_any_bear[i] and ((p.cs_inc_pentagon_MAT and sigPentagon[i]) or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i]) for i in range(n)]
    csNew1_Bull = [comboSet1_Bull[i] or comboSet2_Bull[i] for i in range(n)]
    csNew1_Bear = [comboSet1_Bear[i] or comboSet2_Bear[i] for i in range(n)]
    csNew2_Bull = [comboSet3_Bull[i] or comboSet4_Bull[i] for i in range(n)]
    csNew2_Bear = [comboSet3_Bear[i] or comboSet4_Bear[i] for i in range(n)]
    csNew3_Bull = [csNew1_Bull[i] and _nzb(csNew2_Bull, i, 1) for i in range(n)]
    csNew3_Bear = [csNew1_Bear[i] and _nzb(csNew2_Bear, i, 1) for i in range(n)]

    nag_dir_bull = [sigBullRVOL1x[i] or sigGrandSlam[i] or sigFAUNABull[i] or sigDISPBull[i] or sigBullPBJ[i] or sigPUP[i] or gz_bullHV[i] or gz_bullGZI[i] for i in range(n)]
    nag_dir_bear = [sigBearRVOL1x[i] or sigMOAB[i] or sigFAUNABear[i] or sigDISPBear[i] or sigBearPBJ[i] or sigPPD[i] or gz_bearHV[i] or gz_bearGZI[i] for i in range(n)]

    bull_hw_slot = [sigBullRVOL1x[i] or sigGrandSlam[i] or sigWTC[i] or sigHiroshima[i] or (sigNagasaki[i] and nag_dir_bull[i]) for i in range(n)]
    bear_hw_slot = [sigBearRVOL1x[i] or sigMOAB[i] or sigWTC[i] or sigHiroshima[i] or (sigNagasaki[i] and nag_dir_bear[i]) for i in range(n)]
    anyBullFloor = [conf[i] and bull_pp[i] and sigBullPBJ[i] and bull_hw_slot[i] for i in range(n)]
    anyBull2nd = [conf[i] and bull_pp[i] and sigBullPB[i] and bull_hw_slot[i] for i in range(n)]
    anyBearRoof = [conf[i] and bear_pp[i] and sigBearPBJ[i] and bear_hw_slot[i] for i in range(n)]
    anyBearPent = [conf[i] and bear_pp[i] and sigBearPB[i] and bear_hw_slot[i] for i in range(n)]

    hwBull = [(c[i] > o[i]) and disp5_bull[i] and sigBullPBJ[i] and (sigGrandSlam[i] or sigWTC[i] or sigHiroshima[i] or (sigNagasaki[i] and nag_dir_bull[i])) and (anyBullFloor[i] or anyBull2nd[i]) for i in range(n)]
    hwBear = [(c[i] < o[i]) and disp5_bear[i] and sigBearPBJ[i] and (sigMOAB[i] or sigWTC[i] or sigHiroshima[i] or (sigNagasaki[i] and nag_dir_bear[i])) and (anyBearRoof[i] or anyBearPent[i]) for i in range(n)]

    super_hw_bull = [sigBullRVOL1x[i] or sigGrandSlam[i] or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i] for i in range(n)]
    super_hw_bear = [sigBearRVOL1x[i] or sigMOAB[i] or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i] for i in range(n)]
    super_comboAny_bull = [csNew1_Bull[i] or csNew2_Bull[i] for i in range(n)]
    super_comboAny_bear = [csNew1_Bear[i] or csNew2_Bear[i] for i in range(n)]
    superBull = [conf[i] and sigBullPBJ[i] and sigDISPBull[i] and (sigFAUNABull[i] or sigLong1[i]) and super_hw_bull[i] and ((super_comboAny_bull[i] and sigPUP[i]) or (anyBullFloor[i] or anyBull2nd[i])) for i in range(n)]
    superBear = [conf[i] and sigBearPBJ[i] and sigDISPBear[i] and (sigFAUNABear[i] or sigShort1[i]) and super_hw_bear[i] and ((super_comboAny_bear[i] and sigPPD[i]) or (anyBearRoof[i] or anyBearPent[i])) for i in range(n)]
    sduperBull = [conf[i] and (anyBullFloor[i] or anyBull2nd[i]) and sigBullPBJ[i] and super_hw_bull[i] and super_comboAny_bull[i] and sigPUP[i] and sigDISPBull[i] and (sigFAUNABull[i] or sigLong1[i]) for i in range(n)]
    sduperBear = [conf[i] and (anyBearRoof[i] or anyBearPent[i]) and sigBearPBJ[i] and super_hw_bear[i] and super_comboAny_bear[i] and sigPPD[i] and sigDISPBear[i] and (sigFAUNABear[i] or sigShort1[i]) for i in range(n)]

    sigGolfBull = [conf[i] and sigDISPBull[i] and _nzb(sigFAUNABull, i, 1) and _nzb(sigPUP, i, 1) and _nzb(sigDISPBull, i, 1) and _nzb(sigFAUNABull, i, 2) and _nzb(sigPUP, i, 2) for i in range(n)]
    sigGolfBear = [conf[i] and sigDISPBear[i] and _nzb(sigFAUNABear, i, 1) and _nzb(sigPPD, i, 1) and _nzb(sigDISPBear, i, 1) and _nzb(sigFAUNABear, i, 2) and _nzb(sigPPD, i, 2) for i in range(n)]
    sigPAFBull = [conf[i] and sigPUP[i] and sigFAUNABull[i] and _nzb(sigPUP, i, 1) and _nzb(sigFAUNABull, i, 1) for i in range(n)]
    sigPAFBear = [conf[i] and sigPPD[i] and sigFAUNABear[i] and _nzb(sigPPD, i, 1) and _nzb(sigFAUNABear, i, 1) for i in range(n)]

    od_fvg_bull = [gz_bullGZI[i] or comboSet1_Bull[i] or comboSet2_Bull[i] or comboSet3_Bull[i] or comboSet4_Bull[i] for i in range(n)]
    od_fvg_bear = [gz_bearGZI[i] or comboSet1_Bear[i] or comboSet2_Bear[i] or comboSet3_Bear[i] or comboSet4_Bear[i] for i in range(n)]
    sigODBull = [conf[i] and sessionBarCount[i] <= p.od_max_bars and od_fvg_bull[i] and disp_prevDisp[i] and sigPUP[i] and sigBullPBJ[i] for i in range(n)]
    sigODBear = [conf[i] and sessionBarCount[i] <= p.od_max_bars and od_fvg_bear[i] and disp_prevDisp[i] and sigPPD[i] and sigBearPBJ[i] for i in range(n)]

    hv75_1 = shift(highest(v, 75), 1)
    hv150_1 = shift(highest(v, p.hv150_len), 1)
    hv500_1 = shift(highest(v, 500), 1)
    hv1000_1 = shift(highest(v, 1000), 1)
    sigHV75 = [conf[i] and hv75_1[i] is not None and v[i] >= hv75_1[i] for i in range(n)]   # noqa: F841
    sigHV150 = [conf[i] and hv150_1[i] is not None and v[i] >= hv150_1[i] for i in range(n)]  # noqa: F841
    sigHV500 = [conf[i] and hv500_1[i] is not None and v[i] >= hv500_1[i] for i in range(n)]
    sigHV1000 = [conf[i] and hv1000_1[i] is not None and v[i] >= hv1000_1[i] for i in range(n)]

    # ════════════════ CC chain (windowed) ═════════════════════════════════════
    sigCCBull = [False] * n
    sigCCBear = [False] * n
    cc_bull_active = False
    cc_bear_active = False
    for i in range(n):
        cc_win_bull = 0
        cc_pbj_bull = False
        for k in range(p.cc_window):
            hv2 = _nzb(comboSet3_Bull, i, k) or _nzb(comboSet4_Bull, i, k) or _nzb(comboSet1_Bull, i, k) or _nzb(comboSet2_Bull, i, k)
            if hv2:
                cc_win_bull += 1
            if _nzb(sigBullPBJ, i, k) or _nzb(sigBullPB, i, k):
                cc_pbj_bull = True
        cc_win_bear = 0
        cc_pbj_bear = False
        for k in range(p.cc_window):
            hv2 = _nzb(comboSet3_Bear, i, k) or _nzb(comboSet4_Bear, i, k) or _nzb(comboSet1_Bear, i, k) or _nzb(comboSet2_Bear, i, k)
            if hv2:
                cc_win_bear += 1
            if _nzb(sigBearPBJ, i, k) or _nzb(sigBearPB, i, k):
                cc_pbj_bear = True
        if conf[i]:
            if not (comboSet1_Bull[i] or comboSet2_Bull[i] or comboSet3_Bull[i] or comboSet4_Bull[i]):
                cc_bull_active = False
            elif not cc_bull_active and cc_win_bull >= p.cc_min_hits and cc_pbj_bull:
                cc_bull_active = True
            if not (comboSet1_Bear[i] or comboSet2_Bear[i] or comboSet3_Bear[i] or comboSet4_Bear[i]):
                cc_bear_active = False
            elif not cc_bear_active and cc_win_bear >= p.cc_min_hits and cc_pbj_bear:
                cc_bear_active = True
        sigCCBull[i] = conf[i] and cc_bull_active
        sigCCBear[i] = conf[i] and cc_bear_active

    # ════════════════ LSC chain (windowed) ════════════════════════════════════
    lsc_L1 = [conf[i] and ls_regRatio[i] > p.lsc_reg1 and ls_cumRatio[i] > p.lsc_cum1 and c[i] > o[i] and ls_bodyRat[i] >= p.lsc_body1 for i in range(n)]
    lsc_S1 = [conf[i] and ls_regRatio[i] > p.lsc_reg1 and ls_cumRatio[i] > p.lsc_cum1 and c[i] < o[i] and ls_bodyRat[i] >= p.lsc_body1 for i in range(n)]
    lsc_L2 = [conf[i] and ls_regRatio[i] > p.lsc_reg2 and ls_cumRatio[i] > p.lsc_cum2 and c[i] > o[i] and ls_bodyRat[i] >= p.lsc_body2 for i in range(n)]
    lsc_S2 = [conf[i] and ls_regRatio[i] > p.lsc_reg2 and ls_cumRatio[i] > p.lsc_cum2 and c[i] < o[i] and ls_bodyRat[i] >= p.lsc_body2 for i in range(n)]
    sigLSCBull = [False] * n
    sigLSCBear = [False] * n
    lsc_bull_active = False
    lsc_bear_active = False
    for i in range(n):
        lsc_wb = 0
        lsc_pbj_bull = False
        for k in range(p.lsc_window):
            if _nzb(lsc_L1, i, k) or _nzb(lsc_L2, i, k):
                lsc_wb += 1
            if _nzb(sigBullPBJ, i, k) or _nzb(sigBullPB, i, k):
                lsc_pbj_bull = True
        lsc_ws = 0
        lsc_pbj_bear = False
        for k in range(p.lsc_window):
            if _nzb(lsc_S1, i, k) or _nzb(lsc_S2, i, k):
                lsc_ws += 1
            if _nzb(sigBearPBJ, i, k) or _nzb(sigBearPB, i, k):
                lsc_pbj_bear = True
        if conf[i]:
            if not (lsc_L1[i] or lsc_L2[i]):
                lsc_bull_active = False
            elif not lsc_bull_active and lsc_wb >= p.lsc_min_hits and lsc_pbj_bull:
                lsc_bull_active = True
            if not (lsc_S1[i] or lsc_S2[i]):
                lsc_bear_active = False
            elif not lsc_bear_active and lsc_ws >= p.lsc_min_hits and lsc_pbj_bear:
                lsc_bear_active = True
        sigLSCBull[i] = conf[i] and lsc_bull_active
        sigLSCBear[i] = conf[i] and lsc_bear_active

    sigNagPlusBull = [sigNagasaki[i] and (sigBullRVOL1x[i] or sigGrandSlam[i] or sigFAUNABull[i] or sigDISPBull[i] or sigBullPBJ[i] or sigPUP[i] or gz_bullHV[i] or gz_bullGZI[i] or sigLong1[i] or anyBullFloor[i] or anyBull2nd[i]) for i in range(n)]
    sigNagPlusBear = [sigNagasaki[i] and (sigBearRVOL1x[i] or sigMOAB[i] or sigFAUNABear[i] or sigDISPBear[i] or sigBearPBJ[i] or sigPPD[i] or gz_bearHV[i] or gz_bearGZI[i] or sigShort1[i] or anyBearRoof[i] or anyBearPent[i]) for i in range(n)]

    # ════════════════ ENGINE 8: UU / UUU / UUUU (IPSF + P21 scan) ═════════════
    u_qual_bull = [conf[i] and bb_baseBullish[i] and _ge(bb_normPrice[i], 0.5) for i in range(n)]
    u_qual_bear = [conf[i] and bb_baseBearish[i] and _ge(bb_normPrice[i], 0.5) for i in range(n)]
    u_bull_streak = [0] * n
    u_bear_streak = [0] * n
    u_bull_hasDay1 = [False] * n
    u_bear_hasDay1 = [False] * n
    sbk = sbr = 0
    hb = hr = False
    for i in range(n):
        if u_qual_bull[i]:
            sbk += 1
            hb = hb or is_new_day[i]
        else:
            sbk = 0
            hb = False
        if u_qual_bear[i]:
            sbr += 1
            hr = hr or is_new_day[i]
        else:
            sbr = 0
            hr = False
        u_bull_streak[i] = sbk
        u_bear_streak[i] = sbr
        u_bull_hasDay1[i] = hb
        u_bear_hasDay1[i] = hr

    def _uu_scan(i, _n, bull):
        _hp = _hpb = _hh = _hd = _hf = False
        _ad = _asd = True
        _dnp = _pnd = False
        for k in range(_n):
            j = i - k
            if j < 0:
                continue
            if bull:
                bpbj = _nzb(sigBullPBJ, i, k)
                bpb = _nzb(sigBullPB, i, k)
                bhvd = _nzb(hvd_fire_bull, i, k + 1) if k >= 1 else False
                bdisp = _nzb(sigDISPBull, i, k) or bhvd
                bfauna = _nzb(sigFAUNABull, i, k)
                bsaab = _nzb(sigSAAB, i, k) or _nzb(sigBullRVOL1x, i, k) or _nzb(sigGrandSlam, i, k)
            else:
                bpbj = _nzb(sigBearPBJ, i, k)
                bpb = _nzb(sigBearPB, i, k)
                bhvd = _nzb(hvd_fire_bear, i, k + 1) if k >= 1 else False
                bdisp = _nzb(sigDISPBear, i, k) or bhvd
                bfauna = _nzb(sigFAUNABear, i, k)
                bsaab = _nzb(sigKratos, i, k) or _nzb(sigBearRVOL1x, i, k) or _nzb(sigMOAB, i, k)
            bdf = bdisp or bfauna
            if bpbj:
                _hp = True
            if bpb:
                _hpb = True
            if bhvd:
                _hh = True
            if bdisp:
                _hd = True
            if bfauna:
                _hf = True
            if not bdisp:
                _ad = False
            if not bsaab or not bdf:
                _asd = False
            if bdf and not bpbj:
                _dnp = True
            if bpbj and not bdf:
                _pnd = True
        return _hp, _hpb, _hh, _hd, _hf, _ad, _asd, _dnp, _pnd

    sigP21BullUUUU = [False] * n; sigP21BullUUUU_indep = [False] * n
    sigP21BullUUU = [False] * n; sigP21BullUUU_indep = [False] * n
    sigUUBull = [False] * n; sigUUBull_indep = [False] * n
    sigP21BearUUUU = [False] * n; sigP21BearUUUU_indep = [False] * n
    sigP21BearUUU = [False] * n; sigP21BearUUU_indep = [False] * n
    sigUUBear = [False] * n; sigUUBear_indep = [False] * n

    def _bp(i, off):
        x = bb_normPrice[i - off] if 0 <= i - off < n else None
        return nz(x)

    for i in range(n):
        # bull UUUU
        if conf[i] and u_bull_streak[i] >= 4:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _uu_scan(i, min(u_bull_streak[i], 4), True)
            pA = u_bull_hasDay1[i] and hp; pB = ad; pC = asd; pD = hh
            pE = (dnp and hp) or (pnd and (hd or hf)); pF = (hf or hd) and hp
            _s = bb_normPrice[i] + _bp(i, 1) + _bp(i, 2) + _bp(i, 3)
            _pp = _nzb(sigBullPBJ, i, 0) or _nzb(sigBullPBJ, i, 1) or _nzb(sigBullPBJ, i, 2) or _nzb(sigBullPBJ, i, 3)
            _ok = tfSec > 120 or (_s >= th_saab and (_s >= th_1x or _pp))
            sigP21BullUUUU[i] = (pA or pB or pC or pD or pE or pF) and _ok
            sigP21BullUUUU_indep[i] = (pA or pB or pC or pE or pF) and _ok
        if conf[i] and u_bull_streak[i] == 3:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _uu_scan(i, 3, True)
            pA = u_bull_hasDay1[i] and hp; pB = ad; pC = asd; pD = hh
            pE = (dnp and hp) or (pnd and (hd or hf))
            _s = bb_normPrice[i] + _bp(i, 1) + _bp(i, 2)
            _pp = _nzb(sigBullPBJ, i, 0) or _nzb(sigBullPBJ, i, 1) or _nzb(sigBullPBJ, i, 2)
            _ok = tfSec > 120 or (_s >= th_saab and (_s >= th_1x or _pp))
            sigP21BullUUU[i] = (pA or pB or pC or pD or pE) and _ok
            sigP21BullUUU_indep[i] = (pA or pB or pC or pE) and _ok
        if conf[i] and u_bull_streak[i] == 2:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _uu_scan(i, 2, True)
            pA = u_bull_hasDay1[i] and hp; pB = ad; pC = asd; pD = hh and (hpb or hp)
            pE = (dnp and hp) or (pnd and (hd or hf))
            _s = bb_normPrice[i] + _bp(i, 1)
            _pp = _nzb(sigBullPBJ, i, 0) or _nzb(sigBullPBJ, i, 1)
            _ok = tfSec > 120 or (_s >= th_saab and (_s >= th_1x or _pp))
            sigUUBull[i] = (pA or pB or pC or pD or pE) and _ok
            sigUUBull_indep[i] = (pA or pB or pC or pE) and _ok
        # bear UUUU/UUU/UU
        if conf[i] and u_bear_streak[i] >= 4:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _uu_scan(i, min(u_bear_streak[i], 4), False)
            sigP21BearUUUU[i] = (u_bear_hasDay1[i] and hp) or ad or asd or hh or ((dnp and hp) or (pnd and (hd or hf))) or ((hf or hd) and hp)
            sigP21BearUUUU_indep[i] = (u_bear_hasDay1[i] and hp) or ad or asd or ((dnp and hp) or (pnd and (hd or hf))) or ((hf or hd) and hp)
        if conf[i] and u_bear_streak[i] == 3:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _uu_scan(i, 3, False)
            sigP21BearUUU[i] = (u_bear_hasDay1[i] and hp) or ad or asd or hh or ((dnp and hp) or (pnd and (hd or hf)))
            sigP21BearUUU_indep[i] = (u_bear_hasDay1[i] and hp) or ad or asd or ((dnp and hp) or (pnd and (hd or hf)))
        if conf[i] and u_bear_streak[i] == 2:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _uu_scan(i, 2, False)
            sigUUBear[i] = (u_bear_hasDay1[i] and hp) or ad or asd or (hh and (hpb or hp)) or ((dnp and hp) or (pnd and (hd or hf)))
            sigUUBear_indep[i] = (u_bear_hasDay1[i] and hp) or ad or asd or ((dnp and hp) or (pnd and (hd or hf)))

    # ════════════════ BOOM HUNTER + OMEGA (Ehlers HP / SuperSmoother) ══════════
    pi = 2 * math.asin(1)
    alpha1 = (math.cos(.707 * 2 * pi / 100) + math.sin(.707 * 2 * pi / 100) - 1) / math.cos(.707 * 2 * pi / 100)
    bh_K2 = 0.3

    hlc3 = [(h[i] + l[i] + c[i]) / 3.0 for i in range(n)]

    # HP / SuperSmoother filter chain 1 -> Quotient1, Quotient2
    HP = [0.0] * n
    Filt = [0.0] * n
    Peak = [0.0] * n
    a1 = math.exp(-1.414 * pi / p.bh_LPPeriod)
    b1 = 2 * a1 * math.cos(1.414 * pi / p.bh_LPPeriod)
    c2 = b1; c3 = -a1 * a1; c1 = 1 - c2 - c3
    Quotient1 = [0.0] * n
    Quotient2 = [0.0] * n
    for i in range(n):
        cc0 = c[i]
        cc1 = c[i - 1] if i >= 1 else c[i]
        cc2 = c[i - 2] if i >= 2 else cc1
        HP[i] = ((1 - alpha1 / 2) ** 2) * (cc0 - 2 * cc1 + cc2) + 2 * (1 - alpha1) * (HP[i - 1] if i >= 1 else 0.0) - ((1 - alpha1) ** 2) * (HP[i - 2] if i >= 2 else 0.0)
        Filt[i] = c1 * (HP[i] + (HP[i - 1] if i >= 1 else 0.0)) / 2 + c2 * (Filt[i - 1] if i >= 1 else 0.0) + c3 * (Filt[i - 2] if i >= 2 else 0.0)
        pk = .991 * (Peak[i - 1] if i >= 1 else 0.0)
        if abs(Filt[i]) > pk:
            pk = abs(Filt[i])
        Peak[i] = pk
        X = Filt[i] / pk if pk != 0 else 0.0
        Quotient1[i] = (X + p.bh_K1) / (p.bh_K1 * X + 1)
        Quotient2[i] = (X + bh_K2) / (bh_K2 * X + 1)

    # HP / SuperSmoother chain 2 -> Quotient3
    HP2 = [0.0] * n
    Filt2 = [0.0] * n
    Peak2 = [0.0] * n
    a12 = math.exp(-1.414 * pi / p.bh_LPPeriod2)
    b12 = 2 * a12 * math.cos(1.414 * pi / p.bh_LPPeriod2)
    c22 = b12; c32 = -a12 * a12; c12 = 1 - c22 - c32
    Quotient3 = [0.0] * n
    for i in range(n):
        cc0 = c[i]
        cc1 = c[i - 1] if i >= 1 else c[i]
        cc2 = c[i - 2] if i >= 2 else cc1
        HP2[i] = ((1 - alpha1 / 2) ** 2) * (cc0 - 2 * cc1 + cc2) + 2 * (1 - alpha1) * (HP2[i - 1] if i >= 1 else 0.0) - ((1 - alpha1) ** 2) * (HP2[i - 2] if i >= 2 else 0.0)
        Filt2[i] = c12 * (HP2[i] + (HP2[i - 1] if i >= 1 else 0.0)) / 2 + c22 * (Filt2[i - 1] if i >= 1 else 0.0) + c32 * (Filt2[i - 2] if i >= 2 else 0.0)
        pk = .991 * (Peak2[i - 1] if i >= 1 else 0.0)
        if abs(Filt2[i]) > pk:
            pk = abs(Filt2[i])
        Peak2[i] = pk
        X2 = Filt2[i] / pk if pk != 0 else 0.0
        Quotient3[i] = (X2 + p.bh_K12) / (p.bh_K12 * X2 + 1)

    # tci / mf / tradition -> wt1/wt2/wt3
    def _ema_local(series, length):
        return _ema(series, length)

    src5 = hlc3
    ema_n1 = _ema_local(src5, p.bh_n1)
    abs_dev = [abs(src5[i] - ema_n1[i]) if ema_n1[i] is not None else None for i in range(n)]
    ema_absdev = _ema_local(abs_dev, p.bh_n1)
    tci_inner = [None] * n
    for i in range(n):
        if ema_n1[i] is None or ema_absdev[i] is None or ema_absdev[i] == 0:
            tci_inner[i] = None
        else:
            tci_inner[i] = (src5[i] - ema_n1[i]) / (0.025 * ema_absdev[i])
    tci = _ema_local(tci_inner, p.bh_n2)
    tci = [None if x is None else x + 50 for x in tci]

    # mf (money flow) over n3
    chg = [0.0] + [src5[i] - src5[i - 1] for i in range(1, n)]
    pos_mf = [v[i] * (0.0 if chg[i] <= 0 else src5[i]) for i in range(n)]
    neg_mf = [v[i] * (0.0 if chg[i] >= 0 else src5[i]) for i in range(n)]
    mf = [None] * n
    from collections import deque
    pw = deque(); nw = deque(); ps = 0.0; ns = 0.0
    for i in range(n):
        pw.append(pos_mf[i]); ps += pos_mf[i]
        nw.append(neg_mf[i]); ns += neg_mf[i]
        if len(pw) > p.bh_n3:
            ps -= pw.popleft(); ns -= nw.popleft()
        if len(pw) == p.bh_n3:
            mf[i] = 100.0 - 100.0 / (1.0 + ps / ns) if ns != 0 else 100.0

    rsi_n3 = _rsi(src5, p.bh_n3)
    wt1 = [None] * n
    for i in range(n):
        vals = [x for x in (tci[i], mf[i], rsi_n3[i]) if x is not None]
        if len(vals) == 3:
            wt1[i] = (tci[i] + mf[i] + rsi_n3[i]) / 3.0
    wt2 = sma([0.0 if x is None else x for x in wt1], 6)  # ta.sma on wt1
    # mask wt2 where wt1 has na in window (Pine na propagation)
    wt2 = _mask_window_na(wt1, 6, wt2)

    # bounceUp/Down (wt2 crosses of 20/80)
    def _cu(series, level, i):
        return i > 0 and series[i] is not None and series[i - 1] is not None and series[i] < level and series[i - 1] >= level

    def _co(series, level, i):
        return i > 0 and series[i] is not None and series[i - 1] is not None and series[i] > level and series[i - 1] <= level

    barssince_cu20 = _barssince([_cu(wt2, 20, i) for i in range(n)])
    barssince_co80 = _barssince([_co(wt2, 80, i) for i in range(n)])
    bounceUp = [barssince_cu20[i] is not None and barssince_cu20[i] <= 1 and _co(wt2, 20, i) for i in range(n)]
    bounceDown = [barssince_co80[i] is not None and barssince_co80[i] <= 1 and _cu(wt2, 80, i) for i in range(n)]

    q1 = [Quotient1[i] * 60 + 50 for i in range(n)]
    trigger2 = sma(q1, p.bh_trigno)
    crossover2 = [_crossover(q1, trigger2, i) for i in range(n)]   # noqa: F841

    # entries
    entry = [_cu([Quotient2[i] for i in range(n)], -0.9, i) for i in range(n)]   # noqa: F841 (kept for parity)
    warn2 = [_co(Quotient1, -0.9, i) for i in range(n)]
    bs_warn2 = _barssince(warn2)
    bs_q1_co20 = _barssince([_co(q1, 20, i) for i in range(n)])
    co_q1_trig = [_crossover(q1, trigger2, i) for i in range(n)]
    enter3 = [(Quotient3[i] <= -0.9 and co_q1_trig[i] and bs_warn2[i] is not None and bs_warn2[i] <= 7 and q1[i] <= 20 and bs_q1_co20[i] is not None and bs_q1_co20[i] <= 21) for i in range(n)]
    # enter5: barssince(q1<=0 and crossunder(q1,trigger2)) <= 5 and crossover(q1,trigger2)
    cond5 = [(q1[i] <= 0 and _crossunder(q1, trigger2, i)) for i in range(n)]
    bs_cond5 = _barssince(cond5)
    enter5 = [(bs_cond5[i] is not None and bs_cond5[i] <= 5 and co_q1_trig[i]) for i in range(n)]
    cond6 = [(q1[i] <= 20 and _crossunder(q1, trigger2, i)) for i in range(n)]
    bs_cond6 = _barssince(cond6)
    enter6 = [(bs_cond6[i] is not None and bs_cond6[i] <= 11 and co_q1_trig[i]) for i in range(n)]
    enter7 = [(Quotient3[i] <= -0.9 and co_q1_trig[i]) for i in range(n)]
    greyFired = [enter6[i] and q1[i] <= 60 for i in range(n)]
    loneLimeOnly = [enter3[i] and not enter5[i] and not enter7[i] and not greyFired[i] for i in range(n)]
    anyOmega = [(enter3[i] and enter5[i] and enter7[i]) or loneLimeOnly[i] or bounceUp[i] or bounceDown[i] for i in range(n)]

    omega_cosignal = [
        ((sigSAAB[i] or sigPentagon[i]) if tfSec >= 45 else False)
        or sigBullRVOL1x[i] or sigGrandSlam[i]
        or (sigBullPBJ[i] if tfSec >= 60 else False)
        or (sigBullPB[i] if tfSec >= 300 else False)
        or sigPUP[i]
        or ((gz_bullGZI[i] or gz_bullHV[i]) if tfSec >= 300 else False)
        or sigLong1[i] or sigLong2[i] or sigP21BullUUUU[i] or sigP21BullUUU[i] or sigUUBull[i]
        or sigNeoBull[i] or (sigTrinityBull[i] if tfSec >= 300 else False)
        or (sigHV500[i] if tfSec >= 120 else False) or (sigHV1000[i] if tfSec >= 60 else False)
        or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i] or sigFoxtrotBull[i]
        or comboSet1_Bull[i] or comboSet2_Bull[i] or comboSet3_Bull[i] or comboSet4_Bull[i]
        or sigDispConsBull2[i] or sigDispConsBull3[i] or sigODBull[i] or sigCCBull[i] or sigLSCBull[i]
        or sigGolfBull[i] or sigPAFBull[i] or anyBullFloor[i] or anyBull2nd[i] or hwBull[i]
        or superBull[i] or sduperBull[i]
        for i in range(n)]
    # NOTE: omega_cosignal references sigAlphaStrikeBull in Pine; AlphaStrike is
    # computed below in the firstOfDay loop. Pine resolves it on the same bar
    # (AlphaStrike is computed before omega in source order). We fold the
    # AlphaStrike term in after that loop (see _omega_cosignal_full).
    sigOmegaLong = [False] * n
    sigOmegaLongA = [False] * n

    # ════════════════ Alpha Strike (firstOfDay) + dayDetFired latch ════════════
    as_fauna_bull = [sigFAUNABull[i] or sigLong1[i] or sigDISPBull[i] or hvd_fire_bull[i] or sigPUP[i] or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i] for i in range(n)]
    as_fauna_bear = [sigFAUNABear[i] or sigShort1[i] or sigDISPBear[i] or hvd_fire_bear[i] or sigPPD[i] or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i] for i in range(n)]

    firstOfDay = [False] * n
    sigAlphaStrikeBull = [False] * n
    sigAlphaStrikeBear = [False] * n
    dayDetFired = False
    for i in range(n):
        if is_new_day[i]:
            dayDetFired = False
        firstOfDay[i] = not dayDetFired
        sigAlphaStrikeBull[i] = conf[i] and firstOfDay[i] and bull_pp[i] and (sigGrandSlam[i] or sigBullRVOL1x[i]) and sigBullPBJ[i] and as_fauna_bull[i]
        sigAlphaStrikeBear[i] = conf[i] and firstOfDay[i] and bear_pp[i] and (sigMOAB[i] or sigBearRVOL1x[i]) and sigBearPBJ[i] and as_fauna_bear[i]

        # full omega co-signal incl. AlphaStrike (Pine line 1082) + Omega plots (1083/1086)
        oc = omega_cosignal[i] or sigAlphaStrikeBull[i]
        sigOmegaLong[i] = conf[i] and anyOmega[i] and oc and not sigMOAB[i] and not sigDISPBear[i]
        oc_A = ((sigBullPBJ[i] if tfSec >= 60 else False) or sigP21BullUUUU[i] or anyBullFloor[i]
                or anyBull2nd[i] or hwBull[i] or superBull[i] or sduperBull[i] or sigAlphaStrikeBull[i]
                or sigFoxtrotBull[i] or sigODBull[i] or sigDispConsBull3[i] or sigGolfBull[i]
                or sigGrandSlam[i] or (sigBullRVOL1x[i] and sigDISPBull[i]))
        sigOmegaLongA[i] = conf[i] and anyOmega[i] and oc_A and not sigMOAB[i] and not sigDISPBear[i]

        # end-of-bar latch (Pine line 1088): if any detection fired -> dayDetFired
        any_det = (sigP21BullUUUU[i] or sigP21BearUUUU[i] or sigP21BullUUU[i] or sigP21BearUUU[i]
                   or sigUUBull[i] or sigUUBear[i] or sigAlphaStrikeBull[i] or sigAlphaStrikeBear[i]
                   or sigFoxtrotBull[i] or sigFoxtrotBear[i] or sigOmegaLong[i] or sigOmegaLongA[i]
                   or sigODBull[i] or sigODBear[i] or sigDispConsBull2[i] or sigDispConsBear2[i]
                   or sigDispConsBull3[i] or sigDispConsBear3[i] or csNew1_Bull[i] or csNew1_Bear[i]
                   or csNew2_Bull[i] or csNew2_Bear[i] or csNew3_Bull[i] or csNew3_Bear[i]
                   or anyBullFloor[i] or anyBull2nd[i] or anyBearRoof[i] or anyBearPent[i]
                   or hwBull[i] or hwBear[i] or sigCCBull[i] or sigCCBear[i] or sigLSCBull[i] or sigLSCBear[i]
                   or sigGolfBull[i] or sigGolfBear[i] or sigPAFBull[i] or sigPAFBear[i]
                   or superBull[i] or superBear[i] or sduperBull[i] or sduperBear[i]
                   or sigNagPlusBull[i] or sigNagPlusBear[i])
        if conf[i] and any_det:
            dayDetFired = True

    # ════════════════ Bull-specific UU / Floor gates (Pine 986-1000) ═══════════
    oneOfThese_forUU = [sigP21BullUUUU[i] or sigP21BullUUU[i] or sigDISPBull[i] or hvd_fire_bull[i] or sigFAUNABull[i] or sigPUP[i] or sigBullPBJ[i] or sigLong1[i] or sigGrandSlam[i] or sigBullRVOL1x[i] or csNew3_Bull[i] or csNew1_Bull[i] or csNew2_Bull[i] or sigCCBull[i] or sigNagPlusBull[i] or sigDispConsBull2[i] or sigDispConsBull3[i] for i in range(n)]
    uu_gated_bull = [sigUUBull[i] and oneOfThese_forUU[i] for i in range(n)]

    oneOfThese = [sigP21BullUUUU[i] or sigP21BullUUU[i] or sigUUBull[i] or csNew3_Bull[i] or csNew1_Bull[i] or csNew2_Bull[i] or sigNagPlusBull[i] or sigDispConsBull2[i] or sigDispConsBull3[i] for i in range(n)]
    cb_uu_any = [sigP21BullUUUU[i] or sigP21BullUUU[i] or sigUUBull[i] for i in range(n)]
    cb_disp9 = [conf[i] and disp_std[i] is not None and disp_rng[i] > disp_std[i] * 9.0 and c[i] > o[i] for i in range(n)]
    cb1_pass_floor = [cb_uu_any[i] or csNew3_Bull[i] or cb_disp9[i] or sigPUP[i] or sigLong1[i] for i in range(n)]
    cb1_pass = [cb_uu_any[i] or csNew3_Bull[i] or cb_disp9[i] or sigPUP[i] or sigBullPBJ[i] or sigLong1[i] for i in range(n)]
    floor_gated = [anyBullFloor[i] and oneOfThese[i] and cb1_pass_floor[i] for i in range(n)]
    floor2_gated = [anyBull2nd[i] and oneOfThese[i] and cb1_pass[i] for i in range(n)]

    # ════════════════ Pipeline C terminal fire_* (bull) ═══════════════════════
    fire_BullUUUU = [p.show_BullUUUU and sigP21BullUUUU[i] and masterGate[i] for i in range(n)]
    fire_BullUUU = [p.show_BullUUU and sigP21BullUUU[i] and masterGate[i] for i in range(n)]
    fire_BullUU = [p.show_BullUU and uu_gated_bull[i] and masterGate[i] for i in range(n)]
    fire_AlphaStrikeB = [p.show_AlphaStrikeB and sigAlphaStrikeBull[i] and masterGate[i] for i in range(n)]
    fire_FoxtrotB = [p.show_FoxtrotB and sigFoxtrotBull[i] and masterGate[i] for i in range(n)]
    fire_OmegaLongA = [p.show_OmegaLongA and sigOmegaLongA[i] and masterGate[i] for i in range(n)]
    fire_ODBull = [p.show_ODBull and sigODBull[i] and masterGate[i] for i in range(n)]
    fire_DispConsBull2 = [p.show_DispConsBull2 and sigDispConsBull2[i] and masterGate[i] for i in range(n)]
    fire_DispConsBull3 = [p.show_DispConsBull3 and sigDispConsBull3[i] and masterGate[i] for i in range(n)]
    fire_GolfBull = [p.show_GolfBull and sigGolfBull[i] and masterGate[i] for i in range(n)]
    fire_PAFBull = [p.show_PAFBull and sigPAFBull[i] and masterGate[i] for i in range(n)]
    fire_CS1B = [p.show_CS1B and csNew1_Bull[i] and masterGate[i] for i in range(n)]
    fire_CS2B = [p.show_CS2B and csNew2_Bull[i] and masterGate[i] for i in range(n)]
    fire_CS3B = [p.show_CS3B and csNew3_Bull[i] and masterGate[i] for i in range(n)]
    fire_CCBull = [p.show_CCBull and sigCCBull[i] and masterGate[i] for i in range(n)]
    fire_LSCBull = [p.show_LSCBull and sigLSCBull[i] and masterGate[i] for i in range(n)]
    fire_BullFloor = [p.show_BullFloor and floor_gated[i] and masterGate[i] for i in range(n)]
    fire_Bull2ndFloor = [p.show_Bull2ndFloor and floor2_gated[i] and masterGate[i] for i in range(n)]
    fire_HWBull = [p.show_HWBull and hwBull[i] and masterGate[i] for i in range(n)]
    fire_SuperBull = [p.show_SuperBull and superBull[i] and masterGate[i] for i in range(n)]
    fire_SDuperBull = [p.show_SDuperBull and sduperBull[i] and masterGate[i] for i in range(n)]
    fire_NagPlusBull = [p.show_NagPlusBull and sigNagPlusBull[i] and masterGate[i] for i in range(n)]

    # ── HV+D & co-occurrence plots ──
    hvd_pb_bull = [hvd_fire_bull[i] and _nzb(sigBullPB, i, 1) for i in range(n)]
    hvd_pbj_bull = [hvd_fire_bull[i] and _nzb(sigBullPBJ, i, 1) for i in range(n)]
    fire_HVD_Bull = [p.en_hvd_bull and hvd_fire_bull[i] and masterGate[i] for i in range(n)]
    fire_PB_Bull = [p.en_hvd_pb_bull and hvd_pb_bull[i] and masterGate[i] for i in range(n)]
    fire_PBJ_Bull = [p.en_hvd_pbj_bull and hvd_pbj_bull[i] and masterGate[i] for i in range(n)]

    # ── CO triple co-occurrence ──
    use_any_bull = [sigP21BullUUUU_indep[i] or sigP21BullUUU_indep[i] or sigUUBull_indep[i] or sigAlphaStrikeBull[i] or sigFoxtrotBull[i] or sigOmegaLong[i] or sigOmegaLongA[i] or sigODBull[i] or sigDispConsBull2[i] or sigDispConsBull3[i] or sigGolfBull[i] or sigPAFBull[i] or csNew1_Bull[i] or csNew2_Bull[i] or csNew3_Bull[i] or sigCCBull[i] or sigLSCBull[i] or anyBullFloor[i] or anyBull2nd[i] or hwBull[i] or superBull[i] or sduperBull[i] for i in range(n)]
    co_bull_pbj = [hvd_fire_bull[i] and p.co_en_bullPBJ and _nzb(sigBullPBJ, i, 1) and _nzb(use_any_bull, i, 1) for i in range(n)]
    co_bull_pb = [hvd_fire_bull[i] and p.co_en_bullPB and _nzb(sigBullPB, i, 1) and _nzb(use_any_bull, i, 1) for i in range(n)]
    fire_CO_PBJ = [co_bull_pbj[i] and masterGate[i] for i in range(n)]
    fire_CO_PB = [co_bull_pb[i] and masterGate[i] for i in range(n)]

    # ── B2B HV+D ──
    b2b_bull_raw = [hvd_fire_bull[i] and _nzb(hvd_fire_bull, i, 1) for i in range(n)]
    b2b_bull_pbj = [b2b_bull_raw[i] and (_nzb(sigBullPBJ, i, 1) or _nzb(sigBullPBJ, i, 2)) for i in range(n)]
    b2b_bull_pb = [b2b_bull_raw[i] and (_nzb(sigBullPB, i, 1) or _nzb(sigBullPB, i, 2)) and not b2b_bull_pbj[i] for i in range(n)]
    b2b_bull_nopb = [b2b_bull_raw[i] and not b2b_bull_pbj[i] and not b2b_bull_pb[i] for i in range(n)]
    fire_B2B_Bull = [p.b2b_en_bull and b2b_bull_nopb[i] and masterGate[i] for i in range(n)]
    fire_B2B_Bull_PBJ = [p.b2b_en_bull_pbj and b2b_bull_pbj[i] and masterGate[i] for i in range(n)]
    fire_B2B_Bull_PB = [p.b2b_en_bull_pb and b2b_bull_pb[i] and masterGate[i] for i in range(n)]

    # ── HV+D Momentum co-occ (8) ──
    _m_pup1 = [_nzb(sigPUP, i, 1) for i in range(n)]
    _m_rv1b = [_nzb(sigBullRVOL1x, i, 1) or _nzb(sigGrandSlam, i, 1) for i in range(n)]
    _m_cb1b = csNew3_Bull
    _m_pj1b = [_nzb(sigBullPBJ, i, 1) for i in range(n)]
    hvdm_pup_nopbj_b = [hvd_fire_bull[i] and _m_pup1[i] and not _m_pj1b[i] for i in range(n)]
    hvdm_pbjpup_b = [hvd_fire_bull[i] and _m_pj1b[i] and _m_pup1[i] for i in range(n)]
    hvdm_rvol_nopbj_b = [hvd_fire_bull[i] and _m_rv1b[i] and not _m_pj1b[i] for i in range(n)]
    hvdm_pbjrvol_b = [hvd_fire_bull[i] and _m_pj1b[i] and _m_rv1b[i] for i in range(n)]
    hvdm_cmb_nopbj_b = [hvd_fire_bull[i] and _m_cb1b[i] and not _m_pj1b[i] for i in range(n)]
    hvdm_pbjcmb_b = [hvd_fire_bull[i] and _m_pj1b[i] and _m_cb1b[i] for i in range(n)]
    hvdm_b_cnt = [(1 if _m_pup1[i] else 0) + (1 if _m_rv1b[i] else 0) + (1 if _m_cb1b[i] else 0) for i in range(n)]
    hvdm_2of3_b_raw = [hvd_fire_bull[i] and _m_pj1b[i] and hvdm_b_cnt[i] >= 2 for i in range(n)]
    hvdm_3of3_b = [hvd_fire_bull[i] and _m_pj1b[i] and _m_pup1[i] and _m_rv1b[i] and _m_cb1b[i] for i in range(n)]
    hvdm_2of3_b = [hvdm_2of3_b_raw[i] and not hvdm_3of3_b[i] for i in range(n)]
    hvdm_vis_pbjpup_b = [hvdm_pbjpup_b[i] and not hvdm_2of3_b_raw[i] for i in range(n)]
    hvdm_vis_pbjrvol_b = [hvdm_pbjrvol_b[i] and not hvdm_2of3_b_raw[i] for i in range(n)]
    hvdm_vis_pbjcmb_b = [hvdm_pbjcmb_b[i] and not hvdm_2of3_b_raw[i] for i in range(n)]
    fire_HVDM_PUP = [p.en_hvdm_pup_bull and hvdm_pup_nopbj_b[i] and masterGate[i] for i in range(n)]
    fire_HVDM_RVOL = [p.en_hvdm_rvol_bull and hvdm_rvol_nopbj_b[i] and masterGate[i] for i in range(n)]
    fire_HVDM_CMB = [p.en_hvdm_cmb_bull and hvdm_cmb_nopbj_b[i] and masterGate[i] for i in range(n)]
    fire_HVDM_PBJ_PUP = [p.en_hvdm_pup_bull and hvdm_vis_pbjpup_b[i] and masterGate[i] for i in range(n)]
    fire_HVDM_PBJ_RVOL = [p.en_hvdm_rvol_bull and hvdm_vis_pbjrvol_b[i] and masterGate[i] for i in range(n)]
    fire_HVDM_PBJ_CMB = [p.en_hvdm_cmb_bull and hvdm_vis_pbjcmb_b[i] and masterGate[i] for i in range(n)]
    fire_HVDM_2of3 = [p.en_hvdm_2of3_bull and hvdm_2of3_b[i] and masterGate[i] for i in range(n)]
    fire_HVDM_3of3 = [p.en_hvdm_3of3_bull and hvdm_3of3_b[i] and masterGate[i] for i in range(n)]

    # ──────────────── assemble fire matrix + levels ────────────────
    fire_map = {
        "HVD_Bull": fire_HVD_Bull, "PB_Bull": fire_PB_Bull, "PBJ_Bull": fire_PBJ_Bull,
        "BullUUUU": fire_BullUUUU, "BullUUU": fire_BullUUU, "BullUU": fire_BullUU,
        "AlphaStrikeB": fire_AlphaStrikeB, "FoxtrotB": fire_FoxtrotB, "OmegaLongA": fire_OmegaLongA,
        "ODBull": fire_ODBull, "DispConsBull2": fire_DispConsBull2, "DispConsBull3": fire_DispConsBull3,
        "GolfBull": fire_GolfBull, "PAFBull": fire_PAFBull, "CS1B": fire_CS1B, "CS2B": fire_CS2B,
        "CS3B": fire_CS3B, "CCBull": fire_CCBull, "LSCBull": fire_LSCBull,
        "BullFloor": fire_BullFloor, "Bull2ndFloor": fire_Bull2ndFloor, "HWBull": fire_HWBull,
        "SuperBull": fire_SuperBull, "SDuperBull": fire_SDuperBull,
        "NagPlusBull": fire_NagPlusBull,
        "CO_PBJ": fire_CO_PBJ, "CO_PB": fire_CO_PB,
        "B2B_Bull": fire_B2B_Bull, "B2B_Bull_PBJ": fire_B2B_Bull_PBJ, "B2B_Bull_PB": fire_B2B_Bull_PB,
        "HVDM_PUP": fire_HVDM_PUP, "HVDM_RVOL": fire_HVDM_RVOL, "HVDM_CMB": fire_HVDM_CMB,
        "HVDM_PBJ_PUP": fire_HVDM_PBJ_PUP, "HVDM_PBJ_RVOL": fire_HVDM_PBJ_RVOL,
        "HVDM_PBJ_CMB": fire_HVDM_PBJ_CMB, "HVDM_2of3": fire_HVDM_2of3, "HVDM_3of3": fire_HVDM_3of3,
    }
    assert set(fire_map.keys()) == set(PLOT_IDS), "fire_map keys must equal PLOT_IDS"

    out = {"ts": list(ts)}
    for pid in PLOT_IDS:
        fseries = fire_map[pid]
        out[f"fire_{pid}"] = [1 if fseries[i] else 0 for i in range(n)]
        out[f"lvl_{pid}"] = [float(c[i]) if fseries[i] else None for i in range(n)]
    return out


# ─────────────── extra Pine ta.* helpers used only here ──────────────────────
def _pdiv(a, b):
    """Pine float division: x / 0 -> na (None); na operand -> na."""
    if a is None or b is None or b == 0:
        return None
    return a / b


def _sma_with_na(values, length):
    """ta.sma where None inputs make the window's output None (Pine na propagation)."""
    out = [None] * len(values)
    from collections import deque
    win = deque()
    for i, x in enumerate(values):
        win.append(x)
        if len(win) > length:
            win.popleft()
        if len(win) == length and all(w is not None for w in win):
            out[i] = sum(win) / length
    return out


def _mask_window_na(src, length, smaout):
    """Set smaout[i]=None where any of the last `length` src values is None."""
    out = list(smaout)
    from collections import deque
    win = deque()
    for i in range(len(src)):
        win.append(src[i])
        if len(win) > length:
            win.popleft()
        if not (len(win) == length and all(w is not None for w in win)):
            out[i] = None
    return out


def _lowest(values, length):
    out = [None] * len(values)
    from collections import deque
    win = deque()
    for i, x in enumerate(values):
        win.append(None if x is None else float(x))
        if len(win) > length:
            win.popleft()
        vals = [w for w in win if w is not None]
        if len(win) == length and vals:
            out[i] = min(vals)
    return out


def _rsi(series, length):
    """Pine ta.rsi(series, length) via RMA of gains/losses."""
    n = len(series)
    gains = [0.0] * n
    losses = [0.0] * n
    for i in range(1, n):
        ch = series[i] - series[i - 1]
        gains[i] = ch if ch > 0 else 0.0
        losses[i] = -ch if ch < 0 else 0.0
    avg_gain = _rma_local(gains, length)
    avg_loss = _rma_local(losses, length)
    out = [None] * n
    for i in range(n):
        if avg_gain[i] is None or avg_loss[i] is None:
            continue
        if avg_loss[i] == 0:
            out[i] = 100.0
        else:
            rs = avg_gain[i] / avg_loss[i]
            out[i] = 100.0 - 100.0 / (1.0 + rs)
    return out


def _rma_local(values, length):
    out = [None] * len(values)
    prev = None
    seed_sum = 0.0
    seed_cnt = 0
    for i, x in enumerate(values):
        xx = 0.0 if x is None else float(x)
        if prev is None:
            seed_sum += xx
            seed_cnt += 1
            if seed_cnt == length:
                prev = seed_sum / length
                out[i] = prev
        else:
            prev = (prev * (length - 1) + xx) / length
            out[i] = prev
    return out


def _barssince(cond):
    """Pine ta.barssince(cond): bars since cond was last True; None until first True."""
    out = [None] * len(cond)
    last = None
    for i in range(len(cond)):
        if cond[i]:
            last = 0
        elif last is not None:
            last += 1
        out[i] = last
    return out


def _pivothigh(series, left, right):
    """Pine ta.pivothigh(series,left,right): value confirmed `right` bars later."""
    n = len(series)
    out = [None] * n
    for i in range(n):
        piv = i - right
        if piv - left < 0 or piv + right >= n or piv < 0:
            continue
        val = series[piv]
        if val is None:
            continue
        is_piv = True
        for k in range(1, left + 1):
            if series[piv - k] is None or series[piv - k] >= val:
                is_piv = False
                break
        if is_piv:
            for k in range(1, right + 1):
                if series[piv + k] is None or series[piv + k] >= val:
                    is_piv = False
                    break
        if is_piv:
            out[i] = val
    return out


def _pivotlow(series, left, right):
    n = len(series)
    out = [None] * n
    for i in range(n):
        piv = i - right
        if piv - left < 0 or piv + right >= n or piv < 0:
            continue
        val = series[piv]
        if val is None:
            continue
        is_piv = True
        for k in range(1, left + 1):
            if series[piv - k] is None or series[piv - k] <= val:
                is_piv = False
                break
        if is_piv:
            for k in range(1, right + 1):
                if series[piv + k] is None or series[piv + k] <= val:
                    is_piv = False
                    break
        if is_piv:
            out[i] = val
    return out
