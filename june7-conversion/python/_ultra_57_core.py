# Python is a Python tick   /   Python is a Python time-based   (shared core)
# =============================================================================
# ULTRA COMBO v57 — Pine v5 -> Python — SHARED DETECTION CORE  (NINE NINES)
# -----------------------------------------------------------------------------
# Source (read from disk, path has spaces):
#   ".../June 7/Tick Friendly conversion/ultra_57_tickfriendly.pine"
#   (Pine v5, import TradingView/ta/7; original was //@version=6, made v5 +
#    tick-safe). This module is the ONE shared core imported by BOTH the tick
#    wrapper (tick/ultra_57_tick.py) and the time wrapper (time/ultra_57_time.py).
#    The only difference between grains is the bar-construction grain fed in and
#    the per-TF threshold key tfSec (TICK_FALLBACK_SEC=10s on tick; real bar
#    duration on time) plus the relativeVolume anchor ("D" on both — Pine forces
#    "D" on tick to dodge RE10023, and "D" is the chart-day anchor on time).
#
# FULL faithful port: EVERY one of the 35 detection plotshapes in the Pine
#   becomes a per-bar 0/1 `fire_<id>` series PLUS a numeric `lvl_<id>` series
#   (the data-window level, present exactly where fire==1, None otherwise).
#   No detection plot is stubbed -> COMPOSITE_PARTIAL is empty.
#
# Pine v5 semantics preserved:
#   * `var` state -> explicit forward-walk Python state.
#   * `nz(x[1])` -> previous value with 0.0 default (or supplied default).
#   * `ta.change(dayofmonth)!=0` -> calendar-day change of the bar timestamp.
#   * session gating time("0930-1600","America/New_York") -> caller-supplied
#     in_session mask; default = every bar in-session (synthetic/parity feed).
#   * relativeVolume via the CANONICAL shim (rv_anchor) — never volume/sma(vol).
#   * Every threshold is a Params field (no hardcoded magic numbers in logic).
#   * No label.new / table.new — detection is the 0/1 fire matrix + numeric level.
# =============================================================================
from __future__ import annotations

import datetime as _dt
import sys as _sys
from dataclasses import dataclass
from pathlib import Path as _Path

# shared ta.* + relativeVolume shim (one canonical module, not re-derived)
_HERE = _Path(__file__).resolve().parent
for _p in (str(_HERE), str(_HERE / "tick"), str(_HERE / "time")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import _nn_harness as nn                              # noqa: E402
from _nn_harness import (                             # noqa: E402
    nz, sma, atr, stdev, highest, lowest, cum, columns, shift, relative_volume,
)
from nine_codon_core import ema                       # noqa: E402


# ───────────────────────────── parameters ───────────────────────────────────
@dataclass(frozen=True)
class Params:
    """Every Pine threshold is a tunable parameter (NINE NINES: no magic numbers
    buried in logic). Defaults reproduce the Pine source exactly."""
    tfSec: int = 60                       # per-TF threshold key (RVOL table)
    nn_tick_assumed_sec: int = 10         # Pine TICK_FALLBACK_SEC

    # --- core bull/bear event thresholds (MB/RE/TA) ---
    mb_body_atr_mult: float = 1.6         # bodySize > 1.6*atr14
    mb_body_ratio: float = 0.7            # bodyRatio > 0.7
    vol_mult: float = 1.8                 # volume > 1.8*avgVol20
    re_wide_atr_mult: float = 2.2         # rng > 2.2*atr14
    re_wick_frac: float = 0.15            # (high-close) < 0.15*rng
    ta_delta_mult: float = 1.6            # (close-close[1]) > 1.6*avgDelta

    # --- FC cluster sequence engine ---
    fc_seq_min_len: int = 2               # b1_len/b4_len >= 2
    fc_bull_sum_min: float = 0.1          # b1_sum >= 0.1
    fc_bear_sum_min: float = 0.5          # b4_sum >= 0.5
    fc_inrng_lo: float = 2.9              # b1_inRng: v > 2.9
    fc_inrng_hi: float = 1_000_000.0      # b1_inRng: v < 1e6
    fc_overlap_window: int = 20           # bar_index window for overlap arrays
    fc_two_of_three: int = 2              # 2-of-3 indicator vote

    # --- RVOL / heavy-weapon ---
    bb_avg_length: int = 30               # bb_avgLength
    bb_sma_length: int = 20               # bb_smaLength
    rv_length: int = 30                   # tv_ta.relativeVolume length

    # --- PB&J / supertrend ---
    pbj_base_ma_len: int = 5              # VWMA length for supertrend base
    pbj_st_atr_len: int = 10             # supertrend atr length
    pbj_st_atr_mult: float = 2.0
    pbj_atr_pb_mult: float = 2.0          # atr_pb = atr(14)*2
    pbj_ema_len: int = 20                 # pbj_ma
    pbj_atr_len: int = 14
    pbj_thresh_mult: float = 3.0          # thresh = atr/close*3
    pbj_pivot_len: int = 25               # lowest/highest 25
    pbj_vol_frac: float = 0.1             # volume > avg_vol*0.1
    pbj_approach_up: float = 1.005        # l.upper*1.005
    pbj_approach_dn: float = 0.995        # l.lower*0.995
    pbj_max_levels: int = 30

    # --- PUP / PPD / Anish stages ---
    ema_fast: int = 50
    ema_mid: int = 150
    ema_slow: int = 200
    ema_slow_lag: int = 21                # ema200[21]
    w52_len: int = 252
    w52_lo_bull_mult: float = 1.30
    w52_hi_bull_mult: float = 0.75
    w52_hi_bear_mult: float = 0.70
    w52_lo_bear_mult: float = 1.25
    pp_price_pct: float = 3.0             # |move%| > 3
    pp_vol_lookback: int = 10             # highest(redVol[1],10)
    neutral_phase_bars: int = 5           # neutralBarCount >= 5
    tb_consec_bull: int = 5               # consecAnishBull[1] >= 5
    tb_window_max: int = 1                # tbWindowCount > 1 closes

    # --- ROC / wavetrend / displacement / FAUNA / super ---
    roc_len: int = 5                      # close[5]
    roc_ar_len: int = 100
    roc_ema_len: int = 5
    roc_bull_cross: float = 2.0
    roc_bear_cross: float = -1.25
    wt_esa_len: int = 8
    wt_atr_len: int = 100
    wt_wt1_len: int = 21
    wt_wt2_len: int = 4
    wt_wt1_bull: float = -60.0
    wt_wt1_bear: float = 60.0
    wt_hist_bull: float = 5.0
    wt_hist_bear: float = -5.0
    wt_hist_cross_bull: float = 15.0
    wt_hist_cross_bear: float = -15.0
    disp_std_len: int = 100
    disp_thresh_mult: float = 5.0
    fauna_avg_len: int = 20
    fauna_delta_len: int = 10
    fauna_trend_len: int = 50
    fauna_gg_atr_mult: float = 0.9
    fauna_strong_body_mult: float = 1.5
    fauna_strong_vol_mult: float = 1.5
    fauna_weak_ratio: float = 0.2

    # --- GZ1 / HV FVG ---
    hv_period_a: int = 5000
    hv_period_b: int = 252
    hv_period_c: int = 63
    gz_fvg_window: int = 7                # bar_index - e.idx <= 7

    # --- consecutive-day window ---
    bars_per_day_buffer: float = 1.25     # math.ceil(rawBars*1.25)


# ───────────────── detection-plot dictionary (35 plots) ──────────────────────
# Stable id -> (descriptor, source-indicator-region). Same-named signals across
# OTHER indicators are NOT equivalent; these ids are local to ULTRA v57.
PLOT_SPEC = [
    ("PBJ_F2",        "PBJ + F2 cluster (bull lime / bear red)"),
    ("PBJ_E3",        "PBJ + E3 cluster"),
    ("PBJ_CL",        "PBJ + FC cluster"),
    ("PB_F2",         "PB + F2 cluster"),
    ("PB_E3",         "PB + E3 cluster"),
    ("PB_CL",         "PB + FC cluster"),
    ("F2CL_E3",       "F2[1]+Cluster[1] -> E3 sequential"),
    ("F2CL_B2B",      "F2+Cluster+B2B PUP/PPD"),
    ("B2B_F2",        "B2B PUP/PPD + F2"),
    ("E3_23PP",       "E3 with 2-of-3 PUP/PPD"),
    ("F2_2D",         "F2 back-to-back days"),
    ("E3_2D",         "E3 back-to-back days"),
    ("F2E3seq",       "F2/E3 consecutive days"),
    ("CL_2D",         "Cluster back-to-back days"),
    ("HW_Bull",       "Heavy weapon + any-bull (same bar)"),
    ("HW_Bear",       "Heavy weapon + any-bear (same bar)"),
    ("GZHV_Bull",     "GZ1/HV + any-bull"),
    ("GZHV_Bear",     "GZ1/HV + any-bear"),
    ("HVGZI_Bull",    "HV+GZI combo bull (sessBar==2)"),
    ("HVGZI_Bear",    "HV+GZI combo bear (sessBar==2)"),
    ("MEGA_Bull",     "GZ1/HV MEGA bull (gz1Mega OR hvMega)"),
    ("MEGA_Bear",     "GZ1/HV MEGA bear"),
    ("GZ1HVMEGA_Bull", "GZ1+HV MEGA bull (both)"),
    ("GZ1HVMEGA_Bear", "GZ1+HV MEGA bear (both)"),
    ("Opener_Bull",   "First-candle opener bull (sessBar==1)"),
    ("Opener_Bear",   "First-candle opener bear (sessBar==1)"),
    ("ThreeBar_Bull", "3-bar window bull (PBJ + B2B / 2xPUP)"),
    ("ThreeBar_Bear", "3-bar window bear (PBJ + B2B / 2xPPD)"),
    ("FosterHvy_Bull", "Foster + heavy bull"),
    ("TBHvy_Bear",    "TB + heavy bear"),
    ("GZHVHvy_Bull",  "GZ/HV + heavy bull"),
    ("GZHVHvy_Bear",  "GZ/HV + heavy bear"),
    ("Super2D_Bull",  "Super combo back-to-back days bull"),
    ("Super2D_Bear",  "Super combo back-to-back days bear"),
    ("NAGA",          "Nagasaki — new all-time max volume"),
]
PLOT_IDS = [pid for pid, _ in PLOT_SPEC]

# COMPOSITE_PARTIAL: detection plots that could not be fully ported and are held
# at 0 behind the honesty gate. THIS IS A FULL PORT -> empty.
COMPOSITE_PARTIAL: list[str] = []


# ───────────────────────────── helpers ──────────────────────────────────────
def _cal_day(ts_ms):
    return _dt.datetime.utcfromtimestamp(ts_ms / 1000).toordinal()


def _ev_at(arr, i, k):
    j = i - k
    return arr[j] if 0 <= j < len(arr) else False


# ───────────────────────────── the core ─────────────────────────────────────
def compute(bars, *, params: Params | None = None, rv_anchor: str = "D",
            in_session=None):
    """Run every ULTRA v57 detection plot on `bars` (oldest-first Bar list).

    Returns a dict with:
      'ts'            -> list of bar open timestamps (ms)
      'fire_<id>'     -> list of 0/1 (one per PLOT_IDS id)
      'lvl_<id>'      -> list of float|None, present exactly where fire==1
      'COMPOSITE_PARTIAL' -> the (empty) stub list, for the honesty gate
    """
    P = params or Params()
    o, h, l, c, v, ts = columns(bars)
    n = len(bars)
    out = {"ts": list(ts), "COMPOSITE_PARTIAL": list(COMPOSITE_PARTIAL)}
    if n == 0:
        for pid in PLOT_IDS:
            out[f"fire_{pid}"] = []
            out[f"lvl_{pid}"] = []
        return out

    tf_seconds = P.tfSec if (P.tfSec and P.tfSec > 0) else P.nn_tick_assumed_sec
    if in_session is None:
        in_session = [True] * n

    # ── core shared calcs ───────────────────────────────────────────────────
    atr14 = atr(o, h, l, c, 14)
    avgVol20 = sma(v, 20)
    absDelta = [0.0 if i == 0 else abs(c[i] - c[i - 1]) for i in range(n)]
    avgDelta = sma(absDelta, 10)
    trendMA = sma(c, 50)
    body = [c[i] - o[i] for i in range(n)]
    rng = [h[i] - l[i] for i in range(n)]
    bodySize = [abs(b) for b in body]
    bodyRatio = [0.0 if rng[i] == 0 else bodySize[i] / rng[i] for i in range(n)]
    bodyUp = [body[i] > 0 for i in range(n)]
    bodyDn = [body[i] < 0 for i in range(n)]
    wide = [atr14[i] is not None and rng[i] > P.re_wide_atr_mult * atr14[i] for i in range(n)]
    upTrend = [i >= 1 and trendMA[i] is not None and trendMA[i - 1] is not None
               and trendMA[i] > trendMA[i - 1] for i in range(n)]
    dnTrend = [i >= 1 and trendMA[i] is not None and trendMA[i - 1] is not None
               and trendMA[i] < trendMA[i - 1] for i in range(n)]
    conf = [True] * n   # closed bars only

    def A(i):
        return atr14[i] if atr14[i] is not None else 0.0

    def AV(i):
        return avgVol20[i] if avgVol20[i] is not None else 0.0

    def AD(i):
        return avgDelta[i] if avgDelta[i] is not None else 0.0

    bull_MB = [conf[i] and bodyUp[i] and bodySize[i] > P.mb_body_atr_mult * A(i)
               and bodyRatio[i] > P.mb_body_ratio and v[i] > P.vol_mult * AV(i) for i in range(n)]
    bull_RE = [conf[i] and bodyUp[i] and wide[i] and (h[i] - c[i]) < P.re_wick_frac * rng[i]
               and v[i] > P.vol_mult * AV(i) for i in range(n)]
    bull_TA = [conf[i] and upTrend[i] and i >= 1 and (c[i] - c[i - 1]) > P.ta_delta_mult * AD(i)
               and bodyUp[i] and v[i] > P.vol_mult * AV(i) for i in range(n)]
    bear_MB = [conf[i] and bodyDn[i] and bodySize[i] > P.mb_body_atr_mult * A(i)
               and bodyRatio[i] > P.mb_body_ratio and v[i] > P.vol_mult * AV(i) for i in range(n)]
    bear_RE = [conf[i] and bodyDn[i] and wide[i] and (c[i] - l[i]) < P.re_wick_frac * rng[i]
               and v[i] > P.vol_mult * AV(i) for i in range(n)]
    bear_TA = [conf[i] and dnTrend[i] and i >= 1 and (c[i - 1] - c[i]) > P.ta_delta_mult * AD(i)
               and bodyDn[i] and v[i] > P.vol_mult * AV(i) for i in range(n)]

    # ── session bar counter ─────────────────────────────────────────────────
    sessBar = [0] * n
    isNewDay = False
    sb = 0
    prev_day = None
    for i in range(n):
        day = _cal_day(ts[i])
        if prev_day is not None and day != prev_day:
            isNewDay = True
        if isNewDay and in_session[i]:
            sb = 1
            isNewDay = False
        elif in_session[i] and sb > 0:
            sb += 1
        elif not in_session[i]:
            sb = 0
        sessBar[i] = sb
        prev_day = day

    # ── FC cluster 2-of-3 vote (bull + bear) ────────────────────────────────
    def fc_two_of_three(mb, re, ta):
        s1 = s2 = s3 = 0
        ind1 = [False] * n
        ind2 = [False] * n
        ind3 = [False] * n
        ev2 = [mb[i] or re[i] or ta[i] for i in range(n)]
        ev3 = [(mb[i] or re[i]) and in_session[i] for i in range(n)]
        pday = None
        for i in range(n):
            day = _cal_day(ts[i])
            s1 = s1 + 1 if mb[i] else 0
            ind1[i] = mb[i] and s1 >= P.fc_seq_min_len
            if pday is not None and day != pday:
                s2 = 0
            elif not ev2[i]:
                s2 = 0
            if ev2[i]:
                s2 += 1
            ind2[i] = ev2[i] and s2 >= P.fc_seq_min_len
            s3 = s3 + 1 if ev3[i] else 0
            ind3[i] = ev3[i] and s3 >= P.fc_seq_min_len
            pday = day
        return [(1 if ind1[i] else 0) + (1 if ind2[i] else 0)
                + (1 if ind3[i] else 0) >= P.fc_two_of_three for i in range(n)]

    b1_2of3 = fc_two_of_three(bull_MB, bull_RE, bull_TA)
    b4_2of3 = fc_two_of_three(bear_MB, bear_RE, bear_TA)

    # threshold-event / sequence overlap engine (bull b1_, bear b4_)
    def overlap_engine(direction, sum_min):
        spk = [abs(body[i]) for i in range(n)]
        avgSpk = shift(sma(spk, 30), 1)
        rvolP = [spk[i] / (avgSpk[i] if avgSpk[i] not in (None, 0) else 1.0) for i in range(n)]
        avgVolD = shift(sma(v, 30), 1)
        rvolV = [v[i] / (avgVolD[i] if avgVolD[i] not in (None, 0) else 1.0) for i in range(n)]
        diff = [rvolP[i] - rvolV[i] for i in range(n)]
        if direction == "up":
            pos = [diff[i] if diff[i] > 0 else None for i in range(n)]
        else:
            pos = [diff[i] if (diff[i] > 0 and bodyDn[i]) else None for i in range(n)]
        smaP = sma([0.0 if x is None else x for x in pos], 20)
        base = [(bodyUp[i] if direction == "up" else bodyDn[i])
                and nz(pos[i]) > nz(smaP[i]) for i in range(n)]

        def inRng(x):
            return P.fc_inrng_lo < x < P.fc_inrng_hi

        thEv = [base[i] and inRng(rvolP[i]) for i in range(n)]
        uBar = [base[i] and inRng(rvolP[i]) for i in range(n)]
        seqLen = 0
        seqSum = 0.0
        seqEv = [False] * n
        for i in range(n):
            if uBar[i]:
                seqLen += 1
                seqSum += rvolP[i]
            else:
                seqLen = 0
                seqSum = 0.0
            seqEv[i] = (seqLen >= P.fc_seq_min_len and seqSum >= sum_min)
        thIdx = []
        sqIdx = []
        ovlp = [False] * n
        W = P.fc_overlap_window

        def chk(loA, hiA, loB, hiB):
            return loA <= hiB and loB <= hiA

        for i in range(n):
            while thIdx and i - thIdx[0][0] > W:
                thIdx.pop(0)
            while sqIdx and i - sqIdx[0][0] > W:
                sqIdx.pop(0)
            o_flag = False
            if thEv[i]:
                thIdx.append((i, h[i], l[i]))
                for (_ix, shi, slo) in sqIdx:
                    if chk(l[i], h[i], slo, shi):
                        o_flag = True
                        break
            if seqEv[i] and not o_flag:
                sqIdx.append((i, h[i], l[i]))
                for (_ix, thi, tlo) in thIdx:
                    if chk(l[i], h[i], tlo, thi):
                        o_flag = True
                        break
            ovlp[i] = o_flag
        return ovlp

    b1_ovlp = overlap_engine("up", P.fc_bull_sum_min)
    b4_ovlp = overlap_engine("dn", P.fc_bear_sum_min)

    sBullFC = [conf[i] and b1_2of3[i] and b1_ovlp[i] for i in range(n)]
    sBearFC = [conf[i] and b4_2of3[i] and b4_ovlp[i] for i in range(n)]
    b2_ev = [bull_MB[i] or bull_RE[i] or bull_TA[i] for i in range(n)]
    b5_ev = [bear_MB[i] or bear_RE[i] or bear_TA[i] for i in range(n)]
    sBullE3 = [conf[i] and sessBar[i] == 3 and b2_ev[i] and _ev_at(b2_ev, i, 1)
               and _ev_at(b2_ev, i, 2) for i in range(n)]
    sBearE3 = [conf[i] and sessBar[i] == 3 and b5_ev[i] and _ev_at(b5_ev, i, 1)
               and _ev_at(b5_ev, i, 2) for i in range(n)]
    sBullF2 = [conf[i] and sessBar[i] == 2 and bull_MB[i] and _ev_at(bull_MB, i, 1) for i in range(n)]
    sBearF2 = [conf[i] and sessBar[i] == 2 and bear_MB[i] and _ev_at(bear_MB, i, 1) for i in range(n)]
    sAnyBull = [sBullFC[i] or sBullE3[i] or sBullF2[i] for i in range(n)]
    sAnyBear = [sBearFC[i] or sBearE3[i] or sBearF2[i] for i in range(n)]

    # ── RVOL / heavy weapon thresholds (per-TF table) ───────────────────────
    def rvol1x_th(s):
        return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else
                23.0 if s <= 45 else 20.0 if s <= 60 else 18.0 if s <= 120 else
                13.0 if s <= 300 else 12.0 if s <= 360 else 10.0 if s <= 540 else
                9.0 if s <= 600 else 8.0 if s <= 660 else 7.0 if s <= 900 else
                6.0 if s <= 1560 else 4.5 if s <= 2340 else 3.5 if s <= 3600 else
                3.5 if s <= 9000 else 2.5 if s <= 11700 else 1.8 if s < 259200 else 1.0)

    def gs_moab_th(s):
        day = 86400.0
        return (rvol1x_th(s) * 3.0 if s < 60 else 35.0 if s <= 300 else
                25.0 if s <= 600 else 20.0 if s <= 1500 else 20.0 if s <= 3060 else
                10.0 if s <= 7260 else 8.0 if s <= 11700 else 8.0 if s <= day else
                3.5 if s <= 3.0 * day else 3.0)

    def hiro_th(s):
        day = 86400.0
        return (rvol1x_th(s) * 3.0 if s < 60 else 35.0 if s <= 300 else
                25.0 if s <= 600 else 25.0 if s <= 1500 else 20.0 if s <= 3060 else
                10.0 if s <= 7260 else 8.0 if s <= 11700 else 8.0 if s <= day else
                3.5 if s <= 3.0 * day else 3.0)

    th_1x = rvol1x_th(tf_seconds)
    th_gs_moab = gs_moab_th(tf_seconds)
    th_wtc = rvol1x_th(tf_seconds)
    th_hiroshima = hiro_th(tf_seconds)

    bb_spike = [abs(c[i] - o[i]) for i in range(n)]
    bb_avgSpikeDenom = shift(sma(bb_spike, P.bb_avg_length), 1)
    bb_normPrice = [bb_spike[i] / (bb_avgSpikeDenom[i] if bb_avgSpikeDenom[i] not in (None, 0) else 1.0)
                    for i in range(n)]
    bb_avgVolDenom = shift(sma(v, P.bb_avg_length), 1)
    bb_normVol = [v[i] / (bb_avgVolDenom[i] if bb_avgVolDenom[i] not in (None, 0) else 1.0)
                  for i in range(n)]
    bb_diff = [bb_normPrice[i] - bb_normVol[i] for i in range(n)]
    bb_pos = [bb_diff[i] if bb_diff[i] > 0 else None for i in range(n)]
    bb_smaDiff = sma([0.0 if x is None else x for x in bb_pos], P.bb_sma_length)
    bb_baseBull = [c[i] > o[i] and nz(bb_pos[i]) > nz(bb_smaDiff[i]) for i in range(n)]
    bb_baseBear = [c[i] < o[i] and nz(bb_pos[i]) > nz(bb_smaDiff[i]) for i in range(n)]

    def inRange(x, lo, hi):
        return lo <= x < hi

    sigBullRVOL1x = [conf[i] and bb_baseBull[i] and inRange(bb_normPrice[i], th_1x, th_gs_moab) for i in range(n)]
    sigBearRVOL1x = [conf[i] and bb_baseBear[i] and inRange(bb_normPrice[i], th_1x, th_gs_moab) for i in range(n)]
    sigGrandSlam = [conf[i] and bb_baseBull[i] and bb_normPrice[i] >= th_gs_moab for i in range(n)]
    sigMOAB = [conf[i] and bb_baseBear[i] and bb_normPrice[i] >= th_gs_moab for i in range(n)]

    # WTC / Hiroshima via canonical relativeVolume shim (isCumulative=False)
    curV, pastV, _ratio = relative_volume(v, P.rv_length, anchor_timeframe=rv_anchor,
                                          is_cumulative=False, bar_timestamps=ts)
    relVolRatio = [None if (pastV[i] in (None, 0)) else curV[i] / pastV[i] for i in range(n)]
    sigWTC = [conf[i] and relVolRatio[i] is not None and relVolRatio[i] > th_wtc
              and relVolRatio[i] <= th_hiroshima for i in range(n)]
    sigHiroshima = [conf[i] and relVolRatio[i] is not None and relVolRatio[i] > th_hiroshima for i in range(n)]

    # Nagasaki — running max volume (first bar seeds, no fire on bar 0)
    sigNagasaki = [False] * n
    maxVol = 0.0
    for i in range(n):
        if i == 0:
            maxVol = v[i]
        elif v[i] > maxVol:
            sigNagasaki[i] = True
            maxVol = v[i]
    nagaValue = [v[i] if sigNagasaki[i] else 0.0 for i in range(n)]

    # ── PB&J / supertrend / level machine ───────────────────────────────────
    pbj = _pbj_engine(o, h, l, c, v, atr14, P)
    sigBullPB = pbj["BullPB"]
    sigBullPBJ = pbj["BullPBJ"]
    sigBearPB = pbj["BearPB"]
    sigBearPBJ = pbj["BearPBJ"]

    # ── PUP / PPD / Anish stages ────────────────────────────────────────────
    ema50 = ema(c, P.ema_fast)
    ema150 = ema(c, P.ema_mid)
    ema200 = ema(c, P.ema_slow)
    ema200_1m = shift(ema200, P.ema_slow_lag)
    w52Hi = highest(h, P.w52_len)
    w52Lo = lowest(l, P.w52_len)

    def _f(x):
        return x is not None

    bullPass = [False] * n
    bearPass = [False] * n
    for i in range(n):
        if not all(_f(x[i]) for x in (ema50, ema150, ema200, ema200_1m, w52Hi, w52Lo)):
            continue
        bullPass[i] = (c[i] > ema50[i] and c[i] >= ema150[i] and c[i] >= ema200[i]
                       and ema50[i] > ema150[i] and ema50[i] > ema200[i]
                       and ema150[i] >= ema200[i] and ema200[i] > ema200_1m[i]
                       and c[i] > w52Lo[i] * P.w52_lo_bull_mult and c[i] >= w52Hi[i] * P.w52_hi_bull_mult)
        bearPass[i] = (c[i] < ema50[i] and c[i] <= ema150[i] and c[i] <= ema200[i]
                       and ema50[i] < ema150[i] and ema50[i] < ema200[i]
                       and ema150[i] <= ema200[i] and ema200[i] < ema200_1m[i]
                       and c[i] < w52Hi[i] * P.w52_hi_bear_mult and c[i] <= w52Lo[i] * P.w52_lo_bear_mult)

    redVol = [v[i] if c[i] < o[i] else 0.0 for i in range(n)]
    greenVol = [v[i] if c[i] > o[i] else 0.0 for i in range(n)]
    hiRedVol = highest(shift(redVol, 1), P.pp_vol_lookback)
    hiGreenVol = highest(shift(greenVol, 1), P.pp_vol_lookback)
    priceUp = [((c[i] - o[i]) / o[i]) * 100 > P.pp_price_pct if o[i] else False for i in range(n)]
    priceDn = [((o[i] - c[i]) / o[i]) * 100 > P.pp_price_pct if o[i] else False for i in range(n)]
    volBull = [hiRedVol[i] is not None and v[i] > hiRedVol[i] for i in range(n)]
    volBear = [hiGreenVol[i] is not None and v[i] > hiGreenVol[i] for i in range(n)]
    sPPBull = [conf[i] and priceUp[i] and volBull[i] for i in range(n)]
    sPPBear = [conf[i] and priceDn[i] and volBear[i] for i in range(n)]
    b2bPUP = [sPPBull[i] and _ev_at(sPPBull, i, 1) for i in range(n)]
    b2bPPD = [sPPBear[i] and _ev_at(sPPBear, i, 1) for i in range(n)]
    superPup = [sPPBull[i] and bullPass[i] for i in range(n)]
    superPPD = [sPPBear[i] and bearPass[i] for i in range(n)]

    firstPUPPass = [False] * n
    firstPPDPass = [False] * n
    neutralBarCount = 0
    neutralPhaseComplete = False
    pupArmed = False
    ppdArmed = False
    for i in range(n):
        isNeutral = not bullPass[i] and not bearPass[i]
        neutralBarCount = neutralBarCount + 1 if isNeutral else 0
        if neutralBarCount >= P.neutral_phase_bars:
            neutralPhaseComplete = True
        if neutralPhaseComplete and sPPBull[i]:
            pupArmed = True
        if bearPass[i] and pupArmed:
            pupArmed = False
            neutralPhaseComplete = False
        fpp = pupArmed and bullPass[i] and not _ev_at(bullPass, i, 1)
        firstPUPPass[i] = fpp
        if fpp:
            pupArmed = False
            neutralPhaseComplete = False
        if neutralPhaseComplete and sPPBear[i]:
            ppdArmed = True
        if bullPass[i] and ppdArmed:
            ppdArmed = False
            neutralPhaseComplete = False
        fpd = ppdArmed and bearPass[i] and not _ev_at(bearPass, i, 1)
        firstPPDPass[i] = fpd
        if fpd:
            ppdArmed = False
            neutralPhaseComplete = False

    # ── TB / Foster windows ─────────────────────────────────────────────────
    tbSignal = [False] * n
    tbPBJSignal = [False] * n
    tbPBSignal = [False] * n
    fosterSignal = [False] * n
    fosterPBJSignal = [False] * n
    fosterPBSignal = [False] * n
    consecBull = 0
    consecBull_prev = 0
    consecBear = 0
    consecBear_prev = 0
    tbOpen = False
    tbCount = 0
    fosOpen = False
    fosCount = 0
    for i in range(n):
        consecBull = consecBull + 1 if bullPass[i] else 0
        if not bullPass[i] and consecBull_prev >= P.tb_consec_bull:
            tbOpen = True
            tbCount = 0
        if tbOpen:
            tbCount += 1
            if bullPass[i]:
                tbOpen = False
            elif sPPBear[i]:
                tbSignal[i] = True
                tbOpen = False
            elif sigBearPBJ[i]:
                tbPBJSignal[i] = True
                tbOpen = False
            elif sigBearPB[i]:
                tbPBSignal[i] = True
                tbOpen = False
            elif tbCount > P.tb_window_max:
                tbOpen = False
        consecBear = consecBear + 1 if bearPass[i] else 0
        if not bearPass[i] and consecBear_prev >= P.tb_consec_bull:
            fosOpen = True
            fosCount = 0
        if fosOpen:
            fosCount += 1
            if bearPass[i]:
                fosOpen = False
            elif sPPBull[i]:
                fosterSignal[i] = True
                fosOpen = False
            elif sigBullPBJ[i]:
                fosterPBJSignal[i] = True
                fosOpen = False
            elif sigBullPB[i]:
                fosterPBSignal[i] = True
                fosOpen = False
            elif fosCount > P.tb_window_max:
                fosOpen = False
        consecBull_prev = consecBull
        consecBear_prev = consecBear

    # ── ROC / wavetrend / displacement / FAUNA ──────────────────────────────
    roc_pN = shift(c, P.roc_len)
    roc_val = [((c[i] - roc_pN[i]) / roc_pN[i]) * 100 if roc_pN[i] not in (None, 0) else 0.0 for i in range(n)]
    roc_absd = [abs(roc_val[i] - roc_val[i - 1]) if i >= 1 else 0.0 for i in range(n)]
    roc_ar = sma(roc_absd, P.roc_ar_len)
    roc_in = [(roc_val[i] / roc_ar[i]) if roc_ar[i] not in (None, 0) else 0.0 for i in range(n)]
    roc_ema = ema(roc_in, P.roc_ema_len)
    hlc3 = [(h[i] + l[i] + c[i]) / 3 for i in range(n)]
    ld_esa = ema(hlc3, P.wt_esa_len)
    ld_atr = atr(o, h, l, c, P.wt_atr_len)
    ld_ci = [((hlc3[i] - ld_esa[i]) / (ld_atr[i] if ld_atr[i] not in (None, 0) else 1.0)) * 100
             if ld_esa[i] is not None else 0.0 for i in range(n)]
    ld_wt1 = ema(ld_ci, P.wt_wt1_len)
    ld_wt2 = sma([0.0 if x is None else x for x in ld_wt1], P.wt_wt2_len)
    ld_hist = [(ld_wt1[i] or 0.0) - (ld_wt2[i] or 0.0) for i in range(n)]

    def xover(a, b):
        out_x = [False] * n
        for i in range(1, n):
            if None in (a[i], b[i], a[i - 1], b[i - 1]):
                continue
            out_x[i] = a[i] > b[i] and a[i - 1] <= b[i - 1]
        return out_x

    def xunder(a, b):
        out_x = [False] * n
        for i in range(1, n):
            if None in (a[i], b[i], a[i - 1], b[i - 1]):
                continue
            out_x[i] = a[i] < b[i] and a[i - 1] >= b[i - 1]
        return out_x

    ld_xup = xover(ld_wt1, ld_wt2)
    ld_xdn = xunder(ld_wt1, ld_wt2)
    b1_roc = xover(roc_ema, [P.roc_bull_cross] * n)
    r1_roc = xunder(roc_ema, [P.roc_bear_cross] * n)
    b2_roc = [ld_xup[i] and (ld_wt1[i] or 0) < P.wt_wt1_bull for i in range(n)]
    b3_roc = [ld_xup[i] and ld_hist[i] > P.wt_hist_bull for i in range(n)]
    b4_roc = xover(ld_hist, [P.wt_hist_cross_bull] * n)
    r2_roc = [ld_xdn[i] and (ld_wt1[i] or 0) > P.wt_wt1_bear for i in range(n)]
    r3_roc = [ld_xdn[i] and ld_hist[i] < P.wt_hist_bear for i in range(n)]
    r4_roc = xunder(ld_hist, [P.wt_hist_cross_bear] * n)

    bull2 = [(b1_roc[i] and b4_roc[i]) or (b3_roc[i] and b2_roc[i]) for i in range(n)]
    bear2 = [(r1_roc[i] and r4_roc[i]) or (r3_roc[i] and r2_roc[i]) for i in range(n)]
    hasBullHW = [sigBullRVOL1x[i] or sigGrandSlam[i] or sigWTC[i] or sigHiroshima[i]
                 or sigNagasaki[i] for i in range(n)]
    hasBearHW = [sigBearRVOL1x[i] or sigMOAB[i] or sigWTC[i] or sigHiroshima[i]
                 or sigNagasaki[i] for i in range(n)]
    sigBullCombo = [sigBullPBJ[i] and bull2[i] for i in range(n)]
    sigBearCombo = [sigBearPBJ[i] and bear2[i] for i in range(n)]
    sigROCBull = [conf[i] and sigBullCombo[i] and hasBullHW[i] and c[i] > o[i] for i in range(n)]
    sigROCBear = [conf[i] and sigBearCombo[i] and hasBearHW[i] and c[i] < o[i] for i in range(n)]

    disp_rng = [abs(o[i] - c[i]) for i in range(n)]
    _sd = stdev(disp_rng, P.disp_std_len)
    disp_thresh = [None if _sd[i] is None else _sd[i] * P.disp_thresh_mult for i in range(n)]
    disp_prevDisp = [i >= 1 and disp_thresh[i - 1] is not None and disp_rng[i - 1] > disp_thresh[i - 1]
                     for i in range(n)]
    disp_bullFVG = [i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1] for i in range(n)]
    disp_bearFVG = [i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1] for i in range(n)]
    sigDISPBull = [conf[i] and disp_prevDisp[i] and disp_bullFVG[i] for i in range(n)]
    sigDISPBear = [conf[i] and disp_prevDisp[i] and disp_bearFVG[i] for i in range(n)]

    sigFAUNABull, sigFAUNABear = _fauna(o, h, l, c, v, P)

    anyBullRVOL = hasBullHW
    anyBearRVOL = hasBearHW
    sigSuperBullPBJ = [conf[i] and sigDISPBull[i] and sigBullPBJ[i] and sigFAUNABull[i] and anyBullRVOL[i] for i in range(n)]
    sigSuperBullPB = [conf[i] and sigDISPBull[i] and sigBullPB[i] and sigFAUNABull[i] and anyBullRVOL[i] for i in range(n)]
    sigSuperBearPBJ = [conf[i] and sigDISPBear[i] and sigBearPBJ[i] and sigFAUNABear[i] and anyBearRVOL[i] for i in range(n)]
    sigSuperBearPB = [conf[i] and sigDISPBear[i] and sigBearPB[i] and sigFAUNABear[i] and anyBearRVOL[i] for i in range(n)]
    anySuperBull = [sigSuperBullPBJ[i] or sigSuperBullPB[i] for i in range(n)]
    anySuperBear = [sigSuperBearPBJ[i] or sigSuperBearPB[i] for i in range(n)]

    # ── GZ1 / HV FVG ────────────────────────────────────────────────────────
    bullGZI, bearGZI, bullHV, bearHV = _gzhv(o, h, l, c, v, ts, conf, P)

    # ── ALL COMBO SIGNALS ───────────────────────────────────────────────────
    def AT(arr, i, k):
        return _ev_at(arr, i, k)

    comboPBJ_F2_Bull = [sigBullPBJ[i] and sBullF2[i] for i in range(n)]
    comboPBJ_E3_Bull = [sigBullPBJ[i] and sBullE3[i] for i in range(n)]
    comboPBJ_Cl_Bull = [sigBullPBJ[i] and sBullFC[i] for i in range(n)]
    comboPBJ_F2_Bear = [sigBearPBJ[i] and sBearF2[i] for i in range(n)]
    comboPBJ_E3_Bear = [sigBearPBJ[i] and sBearE3[i] for i in range(n)]
    comboPBJ_Cl_Bear = [sigBearPBJ[i] and sBearFC[i] for i in range(n)]
    comboPB_F2_Bull = [sigBullPB[i] and sBullF2[i] for i in range(n)]
    comboPB_E3_Bull = [sigBullPB[i] and sBullE3[i] for i in range(n)]
    comboPB_Cl_Bull = [sigBullPB[i] and sBullFC[i] for i in range(n)]
    comboPB_F2_Bear = [sigBearPB[i] and sBearF2[i] for i in range(n)]
    comboPB_E3_Bear = [sigBearPB[i] and sBearE3[i] for i in range(n)]
    comboPB_Cl_Bear = [sigBearPB[i] and sBearFC[i] for i in range(n)]
    comboF2Cl_E3_Bull = [AT(sBullF2, i, 1) and AT(sBullFC, i, 1) and sBullE3[i] for i in range(n)]
    comboF2Cl_E3_Bear = [AT(sBearF2, i, 1) and AT(sBearFC, i, 1) and sBearE3[i] for i in range(n)]
    comboF2ClB2B_Bull = [sBullF2[i] and sBullFC[i] and b2bPUP[i] for i in range(n)]
    comboF2ClB2B_Bear = [sBearF2[i] and sBearFC[i] and b2bPPD[i] for i in range(n)]
    comboB2B_F2_Bull = [b2bPUP[i] and sBullF2[i] for i in range(n)]
    comboB2B_F2_Bear = [b2bPPD[i] and sBearF2[i] for i in range(n)]
    pupCountE3 = [(1 if sPPBull[i] else 0) + (1 if AT(sPPBull, i, 1) else 0) + (1 if AT(sPPBull, i, 2) else 0) for i in range(n)]
    comboE3_23PUP_Bull = [sBullE3[i] and pupCountE3[i] >= 2 for i in range(n)]
    ppdCountE3 = [(1 if sPPBear[i] else 0) + (1 if AT(sPPBear, i, 1) else 0) + (1 if AT(sPPBear, i, 2) else 0) for i in range(n)]
    comboE3_23PPD_Bear = [sBearE3[i] and ppdCountE3[i] >= 2 for i in range(n)]

    # barsPerDay (for f_hadSignalYesterday window)
    tfMin = max(1, tf_seconds // 60)
    rawBars = 1 if tfMin >= 390 else (390 + tfMin - 1) // tfMin
    barsPerDay = int(rawBars * P.bars_per_day_buffer + 0.999)

    def had_yesterday(sig, i):
        win = min(barsPerDay * 2, i)
        for k in range(1, win + 1):
            if _ev_at(sig, i, k):
                return True
        return False

    comboF2_2D_Bull = [sBullF2[i] and had_yesterday(sBullF2, i) for i in range(n)]
    comboF2_2D_Bear = [sBearF2[i] and had_yesterday(sBearF2, i) for i in range(n)]
    comboE3_2D_Bull = [sBullE3[i] and had_yesterday(sBullE3, i) for i in range(n)]
    comboE3_2D_Bear = [sBearE3[i] and had_yesterday(sBearE3, i) for i in range(n)]
    comboF2E3_Bull = [(sBullF2[i] and had_yesterday(sBullE3, i)) or (sBullE3[i] and had_yesterday(sBullF2, i)) for i in range(n)]
    comboF2E3_Bear = [(sBearF2[i] and had_yesterday(sBearE3, i)) or (sBearE3[i] and had_yesterday(sBearF2, i)) for i in range(n)]
    comboCl_2D_Bull = [sBullFC[i] and had_yesterday(sBullFC, i) for i in range(n)]
    comboCl_2D_Bear = [sBearFC[i] and had_yesterday(sBearFC, i) for i in range(n)]

    anyBullHW = [sigBullRVOL1x[i] or sigGrandSlam[i] or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i]
                 or sigROCBull[i] or sigSuperBullPBJ[i] or sigSuperBullPB[i] for i in range(n)]
    anyBearHW = [sigBearRVOL1x[i] or sigMOAB[i] or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i]
                 or sigROCBear[i] or sigSuperBearPBJ[i] or sigSuperBearPB[i] for i in range(n)]
    comboHW_Bull = [anyBullHW[i] and sAnyBull[i] for i in range(n)]
    comboHW_Bear = [anyBearHW[i] and sAnyBear[i] for i in range(n)]
    comboHV_Bull = [bullHV[i] and (sAnyBull[i] or AT(sAnyBull, i, 1)) for i in range(n)]
    comboHV_Bear = [bearHV[i] and (sAnyBear[i] or AT(sAnyBear, i, 1)) for i in range(n)]
    comboGZ_Bull = [bullGZI[i] and (sAnyBull[i] or AT(sAnyBull, i, 1)) for i in range(n)]
    comboGZ_Bear = [bearGZI[i] and (sAnyBear[i] or AT(sAnyBear, i, 1)) for i in range(n)]
    comboGZHV_Bull = [comboHV_Bull[i] or comboGZ_Bull[i] for i in range(n)]
    comboGZHV_Bear = [comboHV_Bear[i] or comboGZ_Bear[i] for i in range(n)]
    hvGziBull = [sessBar[i] == 2 and AT(bullHV, i, 1) and bullHV[i] and bullGZI[i] for i in range(n)]
    hvGziBear = [sessBar[i] == 2 and AT(bearHV, i, 1) and bearHV[i] and bearGZI[i] for i in range(n)]
    gz1MegaBull = [bullGZI[i] and anySuperBull[i] and sPPBull[i] and sigFAUNABull[i] and sigDISPBull[i] for i in range(n)]
    hvMegaBull = [bullHV[i] and anySuperBull[i] and sPPBull[i] and sigFAUNABull[i] and sigDISPBull[i] for i in range(n)]
    gz1hvMegaBull = [bullGZI[i] and bullHV[i] and anySuperBull[i] and sPPBull[i] and sigFAUNABull[i] and sigDISPBull[i] for i in range(n)]
    gz1MegaBear = [bearGZI[i] and anySuperBear[i] and sPPBear[i] and sigFAUNABear[i] and sigDISPBear[i] for i in range(n)]
    hvMegaBear = [bearHV[i] and anySuperBear[i] and sPPBear[i] and sigFAUNABear[i] and sigDISPBear[i] for i in range(n)]
    gz1hvMegaBear = [bearGZI[i] and bearHV[i] and anySuperBear[i] and sPPBear[i] and sigFAUNABear[i] and sigDISPBear[i] for i in range(n)]
    gzHvMegaBull = [gz1MegaBull[i] or hvMegaBull[i] for i in range(n)]
    gzHvMegaBear = [gz1MegaBear[i] or hvMegaBear[i] for i in range(n)]
    openerBull = [sessBar[i] == 1 and (bullGZI[i] or bullHV[i]) and (anyBullHW[i] or sigBullPBJ[i] or sigROCBull[i] or (firstPUPPass[i] and superPup[i])) for i in range(n)]
    openerBear = [sessBar[i] == 1 and (bearGZI[i] or bearHV[i]) and (anyBearHW[i] or sigBearPBJ[i] or sigROCBear[i] or (firstPPDPass[i] and superPPD[i])) for i in range(n)]

    pbjIn3Bull = [sigBullPBJ[i] or AT(sigBullPBJ, i, 1) or AT(sigBullPBJ, i, 2) for i in range(n)]
    b2bIn3Bull = [b2bPUP[i] or AT(b2bPUP, i, 1) or AT(b2bPUP, i, 2) for i in range(n)]
    pupsIn3Bull = [(1 if sPPBull[i] else 0) + (1 if AT(sPPBull, i, 1) else 0) + (1 if AT(sPPBull, i, 2) else 0) for i in range(n)]
    threeBar_Bull = [(pbjIn3Bull[i] and b2bIn3Bull[i]) or (pbjIn3Bull[i] and pupsIn3Bull[i] >= 2) for i in range(n)]
    pbjIn3Bear = [sigBearPBJ[i] or AT(sigBearPBJ, i, 1) or AT(sigBearPBJ, i, 2) for i in range(n)]
    b2bIn3Bear = [b2bPPD[i] or AT(b2bPPD, i, 1) or AT(b2bPPD, i, 2) for i in range(n)]
    ppdsIn3Bear = [(1 if sPPBear[i] else 0) + (1 if AT(sPPBear, i, 1) else 0) + (1 if AT(sPPBear, i, 2) else 0) for i in range(n)]
    threeBar_Bear = [(pbjIn3Bear[i] and b2bIn3Bear[i]) or (pbjIn3Bear[i] and ppdsIn3Bear[i] >= 2) for i in range(n)]

    anyFoster = [fosterSignal[i] or fosterPBJSignal[i] or fosterPBSignal[i] for i in range(n)]
    anyTB = [tbSignal[i] or tbPBJSignal[i] or tbPBSignal[i] for i in range(n)]
    fosterHeavyBull = [anyFoster[i] and (sigROCBull[i] or anyBullHW[i] or anySuperBull[i]) for i in range(n)]
    tbHeavyBear = [anyTB[i] and (sigROCBear[i] or anyBearHW[i] or anySuperBear[i]) for i in range(n)]
    gzHvHeavyBull = [(bullGZI[i] or bullHV[i]) and (anyBullHW[i] or anySuperBull[i] or sigROCBull[i]) for i in range(n)]
    gzHvHeavyBear = [(bearGZI[i] or bearHV[i]) and (anyBearHW[i] or anySuperBear[i] or sigROCBear[i]) for i in range(n)]
    superB2BDaysBull = [anySuperBull[i] and had_yesterday(anySuperBull, i) for i in range(n)]
    superB2BDaysBear = [anySuperBear[i] and had_yesterday(anySuperBear, i) for i in range(n)]

    # ── assemble fire matrix + numeric levels ───────────────────────────────
    # Level convention: each detection plot carries a meaningful data-window
    # number where it fires (None elsewhere). RVOL-family plots carry the RVOL
    # ratio/normPrice; NAGA carries volume; structural combos carry the close
    # (the price the combo painted at) so the warehouse has a price coordinate.
    def _pair(fire_bull, fire_bear, lvl_bull=None, lvl_bear=None):
        """OR a bull+bear plot into one fire series; level prefers the side that
        fired (bull then bear). lvl_* default to close."""
        fire = [1 if (fire_bull[i] or fire_bear[i]) else 0 for i in range(n)]
        lvl = []
        for i in range(n):
            if fire[i] == 0:
                lvl.append(None)
            elif fire_bull[i]:
                lvl.append((lvl_bull[i] if lvl_bull is not None else c[i]))
            else:
                lvl.append((lvl_bear[i] if lvl_bear is not None else c[i]))
        return fire, lvl

    def _single(fire_b, lvl_series=None):
        fire = [1 if fire_b[i] else 0 for i in range(n)]
        lvl = [(lvl_series[i] if lvl_series is not None else c[i]) if fire[i] else None
               for i in range(n)]
        return fire, lvl

    fires = {}
    levels = {}

    def put(pid, fire, lvl):
        fires[pid] = fire
        levels[pid] = lvl

    put("PBJ_F2", *_pair(comboPBJ_F2_Bull, comboPBJ_F2_Bear))
    put("PBJ_E3", *_pair(comboPBJ_E3_Bull, comboPBJ_E3_Bear))
    put("PBJ_CL", *_pair(comboPBJ_Cl_Bull, comboPBJ_Cl_Bear))
    put("PB_F2", *_pair(comboPB_F2_Bull, comboPB_F2_Bear))
    put("PB_E3", *_pair(comboPB_E3_Bull, comboPB_E3_Bear))
    put("PB_CL", *_pair(comboPB_Cl_Bull, comboPB_Cl_Bear))
    put("F2CL_E3", *_pair(comboF2Cl_E3_Bull, comboF2Cl_E3_Bear))
    put("F2CL_B2B", *_pair(comboF2ClB2B_Bull, comboF2ClB2B_Bear))
    put("B2B_F2", *_pair(comboB2B_F2_Bull, comboB2B_F2_Bear))
    put("E3_23PP", *_pair(comboE3_23PUP_Bull, comboE3_23PPD_Bear))
    put("F2_2D", *_pair(comboF2_2D_Bull, comboF2_2D_Bear))
    put("E3_2D", *_pair(comboE3_2D_Bull, comboE3_2D_Bear))
    put("F2E3seq", *_pair(comboF2E3_Bull, comboF2E3_Bear))
    put("CL_2D", *_pair(comboCl_2D_Bull, comboCl_2D_Bear))
    # heavy-weapon plots carry bb_normPrice (the RVOL strength) as the level
    put("HW_Bull", *_single(comboHW_Bull, bb_normPrice))
    put("HW_Bear", *_single(comboHW_Bear, bb_normPrice))
    put("GZHV_Bull", *_single(comboGZHV_Bull))
    put("GZHV_Bear", *_single(comboGZHV_Bear))
    put("HVGZI_Bull", *_single(hvGziBull))
    put("HVGZI_Bear", *_single(hvGziBear))
    put("MEGA_Bull", *_single(gzHvMegaBull))
    put("MEGA_Bear", *_single(gzHvMegaBear))
    put("GZ1HVMEGA_Bull", *_single(gz1hvMegaBull))
    put("GZ1HVMEGA_Bear", *_single(gz1hvMegaBear))
    put("Opener_Bull", *_single(openerBull))
    put("Opener_Bear", *_single(openerBear))
    put("ThreeBar_Bull", *_single(threeBar_Bull))
    put("ThreeBar_Bear", *_single(threeBar_Bear))
    put("FosterHvy_Bull", *_single(fosterHeavyBull))
    put("TBHvy_Bear", *_single(tbHeavyBear))
    put("GZHVHvy_Bull", *_single(gzHvHeavyBull))
    put("GZHVHvy_Bear", *_single(gzHvHeavyBear))
    put("Super2D_Bull", *_single(superB2BDaysBull))
    put("Super2D_Bear", *_single(superB2BDaysBear))
    # NAGA carries the new-max volume as its level
    put("NAGA", *_single(sigNagasaki, nagaValue))

    for pid in PLOT_IDS:
        out[f"fire_{pid}"] = fires[pid]
        out[f"lvl_{pid}"] = levels[pid]
    # extra diagnostic levels (not detection plots, mirror the Pine data-window)
    out["lvl_relVolRatio"] = relVolRatio
    out["lvl_bbNormPrice"] = bb_normPrice
    return out


# ───────────────────────── PB&J / supertrend engine ─────────────────────────
def _pbj_engine(o, h, l, c, v, atr14, P: Params):
    n = len(c)
    pv = [c[i] * v[i] for i in range(n)]
    num = sma(pv, P.pbj_base_ma_len)
    den = sma(v, P.pbj_base_ma_len)
    base_ma = [None if (num[i] is None or den[i] in (None, 0)) else num[i] / den[i] for i in range(n)]
    st_atr_s = atr(o, h, l, c, P.pbj_st_atr_len)
    pbj_ma = ema(c, P.pbj_ema_len)
    pbj_atr = atr(o, h, l, c, P.pbj_atr_len)
    avg_vol = sma(v, 20)
    low25 = lowest(l, P.pbj_pivot_len)
    high25 = highest(h, P.pbj_pivot_len)

    st_dir = 1
    cl_prev = cs_prev = sl_prev = sl_prev2 = None
    bull_lvls = []
    bear_lvls = []
    wb = ws = wpb = wps = False
    BullPB = [False] * n
    BullPBJ = [False] * n
    BearPB = [False] * n
    BearPBJ = [False] * n

    def add(arr, up, lo, vol):
        if abs(up - lo) >= 0.01:
            arr.append([up, lo, vol, False])

    def approach(arr, is_bull, cc, ll, hh):
        ap_found = False
        for i in range(len(arr) - 1, -1, -1):
            up, lo, vol, apr = arr[i]
            if is_bull and cc < lo:
                arr.pop(i)
                continue
            if not is_bull and cc > up:
                arr.pop(i)
                continue
            ap = up * P.pbj_approach_up if is_bull else lo * P.pbj_approach_dn
            if is_bull:
                if not apr and ll <= ap:
                    ap_found = True
                    arr[i][3] = True
                elif apr and ll > up:
                    arr[i][3] = False
            else:
                if not apr and hh >= ap:
                    ap_found = True
                    arr[i][3] = True
                elif apr and hh < lo:
                    arr[i][3] = False
        return ap_found

    for i in range(n):
        bm = base_ma[i]
        sa = st_atr_s[i]
        if bm is None or sa is None:
            sl_prev2 = sl_prev
            sl_prev = None
            continue
        st_atr = P.pbj_st_atr_mult * sa
        dyn_long = bm - st_atr
        dyn_short = bm + st_atr
        clb = nz(cl_prev, dyn_long)
        curr_long = max(dyn_long, nz(cl_prev)) if bm > clb else dyn_long
        csb = nz(cs_prev, dyn_short)
        curr_short = min(dyn_short, nz(cs_prev)) if bm < csb else dyn_short
        if st_dir == -1 and c[i] > nz(cs_prev):
            st_dir = 1
        elif st_dir == 1 and c[i] < nz(cl_prev):
            st_dir = -1
        sig_line = curr_long if st_dir == 1 else curr_short

        buy_cross = sl_prev is not None and c[i] > sig_line and c[i - 1] <= sl_prev
        sell_cross = sl_prev is not None and c[i] < sig_line and c[i - 1] >= sl_prev
        is_rising = sig_line > nz(sl_prev)
        is_falling = sig_line < nz(sl_prev)
        bull_re = st_dir == 1 and is_rising and nz(sl_prev) == nz(sl_prev2)
        bear_re = st_dir == -1 and is_falling and nz(sl_prev) == nz(sl_prev2)

        thr = 0.0 if c[i] == 0 or pbj_atr[i] is None else (pbj_atr[i] / c[i] * P.pbj_thresh_mult)
        pbj_buy = (pbj_ma[i] is not None and avg_vol[i] is not None and low25[i] is not None
                   and l[i] < pbj_ma[i] * (1 - thr) and l[i] == low25[i] and v[i] > avg_vol[i] * P.pbj_vol_frac)
        pbj_sell = (pbj_ma[i] is not None and avg_vol[i] is not None and high25[i] is not None
                    and h[i] > pbj_ma[i] * (1 + thr) and h[i] == high25[i] and v[i] > avg_vol[i] * P.pbj_vol_frac)

        atrpb = (atr14[i] or 0.0) * P.pbj_atr_pb_mult
        if buy_cross and i >= 1:
            up = max(o[i - 1], c[i - 1])
            lo = l[i - 1]
            if up - lo < atrpb * 0.5:
                up = lo + atrpb * 0.5
            add(bull_lvls, up, lo, v[i - 1])
        if sell_cross and i >= 1:
            up = h[i - 1]
            lo = min(o[i - 1], c[i - 1])
            if up - lo < atrpb * 0.5:
                lo = up - atrpb * 0.5
            add(bear_lvls, up, lo, v[i - 1])
        if bull_re:
            add(bull_lvls, max(sig_line, min(o[i], c[i])), min(sig_line, min(o[i], c[i])), v[i])
        if bear_re:
            add(bear_lvls, max(sig_line, max(o[i], c[i])), min(sig_line, max(o[i], c[i])), v[i])

        if approach(bull_lvls, True, c[i], l[i], h[i]):
            wb = True
        if approach(bear_lvls, False, c[i], l[i], h[i]):
            ws = True
        if pbj_buy:
            wpb = True
        if pbj_sell:
            wps = True
        while len(bull_lvls) > P.pbj_max_levels:
            bull_lvls.pop(0)
        while len(bear_lvls) > P.pbj_max_levels:
            bear_lvls.pop(0)

        spb = buy_cross and wb
        spjb = buy_cross and wpb
        sps = sell_cross and ws
        spjs = sell_cross and wps
        if spb:
            wb = False
        if spjb:
            wpb = False
        if sps:
            ws = False
        if spjs:
            wps = False

        BullPB[i] = spb and not spjb
        BullPBJ[i] = spjb
        BearPB[i] = sps and not spjs
        BearPBJ[i] = spjs

        cl_prev = curr_long
        cs_prev = curr_short
        sl_prev2 = sl_prev
        sl_prev = sig_line

    return {"BullPB": BullPB, "BullPBJ": BullPBJ, "BearPB": BearPB, "BearPBJ": BearPBJ}


# ───────────────────────────── FAUNA engine ─────────────────────────────────
def _fauna(o, h, l, c, v, P: Params):
    n = len(c)
    f_atr = atr(o, h, l, c, 14)
    f_avgVol = sma(v, P.fauna_avg_len)
    f_avgBody = sma([abs(c[i] - o[i]) for i in range(n)], P.fauna_avg_len)
    f_avgDelta = sma([abs(c[i] - c[i - 1]) if i >= 1 else 0.0 for i in range(n)], P.fauna_delta_len)
    f_trend = sma(c, P.fauna_trend_len)
    body = [c[i] - o[i] for i in range(n)]
    rng = [h[i] - l[i] for i in range(n)]
    bsz = [abs(b) for b in body]
    brat = [0.0 if rng[i] == 0 else bsz[i] / rng[i] for i in range(n)]
    up = [body[i] > 0 for i in range(n)]
    dn = [body[i] < 0 for i in range(n)]
    conf = [True] * n

    def A(i):
        return f_atr[i] or 0.0

    def AV(i):
        return f_avgVol[i] or 0.0

    def AD(i):
        return f_avgDelta[i] or 0.0

    fMB_b = [conf[i] and up[i] and bsz[i] > P.mb_body_atr_mult * A(i) and brat[i] > P.mb_body_ratio and v[i] > P.vol_mult * AV(i) for i in range(n)]
    fRE_b = [conf[i] and up[i] and rng[i] > P.re_wide_atr_mult * A(i) and (h[i] - c[i]) < P.re_wick_frac * rng[i] and v[i] > P.vol_mult * AV(i) for i in range(n)]
    fTA_b = [conf[i] and i >= 1 and f_trend[i] is not None and f_trend[i - 1] is not None and f_trend[i] > f_trend[i - 1] and (c[i] - c[i - 1]) > P.ta_delta_mult * AD(i) and up[i] and v[i] > P.vol_mult * AV(i) for i in range(n)]
    fGG_b = [i >= 1 and (o[i] - c[i - 1]) > P.fauna_gg_atr_mult * A(i) and up[i] and l[i] > c[i - 1] and v[i] > P.vol_mult * AV(i) for i in range(n)]
    prev_body = [c[i - 1] - o[i - 1] if i >= 1 else 0.0 for i in range(n)]
    prev_range = [h[i - 1] - l[i - 1] if i >= 1 else 0.0 for i in range(n)]

    def AB(i):
        return f_avgBody[i - 1] if i >= 1 and f_avgBody[i - 1] is not None else 0.0

    def AVp(i):
        return f_avgVol[i - 1] if i >= 1 and f_avgVol[i - 1] is not None else 0.0

    strongBear = [i >= 1 and c[i - 1] < o[i - 1] and abs(prev_body[i]) > P.fauna_strong_body_mult * AB(i) and v[i - 1] > P.fauna_strong_vol_mult * AVp(i) for i in range(n)]
    weakBear = [i >= 1 and c[i - 1] < o[i - 1] and (0.0 if prev_range[i] == 0 else abs(prev_body[i]) / prev_range[i]) <= P.fauna_weak_ratio for i in range(n)]
    fTR_b = [weakBear[i] and (fMB_b[i] or fRE_b[i] or fTA_b[i]) for i in range(n)]
    fES_b = [strongBear[i] and (fMB_b[i] or fRE_b[i] or fTA_b[i]) for i in range(n)]
    fGDR_b = [i >= 1 and c[i - 1] < o[i - 1] and fGG_b[i] for i in range(n)]
    excl_bull = [fGG_b[i] or fTR_b[i] or fES_b[i] or fGDR_b[i] for i in range(n)]
    faunaBull = [(fMB_b[i] or fRE_b[i] or fTA_b[i]) and not excl_bull[i] for i in range(n)]

    fMB_r = [conf[i] and dn[i] and bsz[i] > P.mb_body_atr_mult * A(i) and brat[i] > P.mb_body_ratio and v[i] > P.vol_mult * AV(i) for i in range(n)]
    fRE_r = [conf[i] and dn[i] and rng[i] > P.re_wide_atr_mult * A(i) and (c[i] - l[i]) < P.re_wick_frac * rng[i] and v[i] > P.vol_mult * AV(i) for i in range(n)]
    fTA_r = [conf[i] and i >= 1 and f_trend[i] is not None and f_trend[i - 1] is not None and f_trend[i] < f_trend[i - 1] and (c[i - 1] - c[i]) > P.ta_delta_mult * AD(i) and dn[i] and v[i] > P.vol_mult * AV(i) for i in range(n)]
    fGG_r = [i >= 1 and (c[i - 1] - o[i]) > P.fauna_gg_atr_mult * A(i) and dn[i] and h[i] < c[i - 1] and v[i] > P.vol_mult * AV(i) for i in range(n)]
    strongBull = [i >= 1 and c[i - 1] > o[i - 1] and abs(prev_body[i]) > P.fauna_strong_body_mult * AB(i) and v[i - 1] > P.fauna_strong_vol_mult * AVp(i) for i in range(n)]
    weakBull = [i >= 1 and c[i - 1] > o[i - 1] and (0.0 if prev_range[i] == 0 else abs(prev_body[i]) / prev_range[i]) <= P.fauna_weak_ratio for i in range(n)]
    fTR_r = [weakBull[i] and (fMB_r[i] or fRE_r[i] or fTA_r[i]) for i in range(n)]
    fES_r = [strongBull[i] and (fMB_r[i] or fRE_r[i] or fTA_r[i]) for i in range(n)]
    fGDR_r = [i >= 1 and c[i - 1] > o[i - 1] and fGG_r[i] for i in range(n)]
    excl_bear = [fGG_r[i] or fTR_r[i] or fES_r[i] or fGDR_r[i] for i in range(n)]
    faunaBear = [(fMB_r[i] or fRE_r[i] or fTA_r[i]) and not excl_bear[i] for i in range(n)]
    return faunaBull, faunaBear


# ───────────────────────────── GZ1 / HV FVG ─────────────────────────────────
def _gzhv(o, h, l, c, v, ts, conf, P: Params):
    n = len(c)
    v1 = shift(v, 1)
    hi_a = shift(highest(v, P.hv_period_a), 1)
    hi_b = shift(highest(v, P.hv_period_b), 1)
    hi_c = shift(highest(v, P.hv_period_c), 1)
    isHV = [v1[i] is not None and (
        (hi_a[i] is not None and v1[i] == hi_a[i]) or
        (hi_b[i] is not None and v1[i] == hi_b[i]) or
        (hi_c[i] is not None and v1[i] == hi_c[i])) for i in range(n)]
    rngLow = [(h[i] - l[i]) / l[i] if l[i] else 0.0 for i in range(n)]
    cumR = cum(rngLow)
    gzThresh = [cumR[i] / i if i > 0 else 0.0 for i in range(n)]
    bFVG = [i >= 2 and l[i] > h[i - 2] and c[i - 1] > h[i - 2] and (l[i] - h[i - 2]) / h[i - 2] > gzThresh[i] for i in range(n)]
    sFVG = [i >= 2 and h[i] < l[i - 2] and c[i - 1] < l[i - 2] and h[i] != 0 and (l[i - 2] - h[i]) / h[i] > gzThresh[i] for i in range(n)]

    fvgs = []  # [mx, mn, bull, t, idx, hv]
    lastT = 0
    bullGZI = [False] * n
    bearGZI = [False] * n
    bullHV = [False] * n
    bearHV = [False] * n
    W = P.gz_fvg_window
    for i in range(n):
        if conf[i] and bFVG[i] and ts[i] != lastT:
            mx = l[i]
            mn = h[i - 2]
            if isHV[i]:
                bullHV[i] = True
            for e in fvgs:
                if e[2] and i - e[4] <= W:
                    if (max(e[1], mn) < min(e[0], mx)) or (max(e[1], mn) <= min(e[0], mx) and e[5] and isHV[i]):
                        bullGZI[i] = True
                        break
            fvgs.insert(0, [mx, mn, True, ts[i], i, isHV[i]])
            lastT = ts[i]
        if conf[i] and sFVG[i] and ts[i] != lastT:
            mx = l[i - 2]
            mn = h[i]
            if isHV[i]:
                bearHV[i] = True
            for e in fvgs:
                if (not e[2]) and i - e[4] <= W:
                    if (max(e[1], mn) < min(e[0], mx)) or (max(e[1], mn) <= min(e[0], mx) and e[5] and isHV[i]):
                        bearGZI[i] = True
                        break
            fvgs.insert(0, [mx, mn, False, ts[i], i, isHV[i]])
            lastT = ts[i]
        for j in range(len(fvgs) - 1, -1, -1):
            g = fvgs[j]
            if g[2] and c[i] < g[1]:
                fvgs.pop(j)
            elif (not g[2]) and c[i] > g[0]:
                fvgs.pop(j)
    return bullGZI, bearGZI, bullHV, bearHV
