# =============================================================================
# Jumbo CIA * 1st PUP FAUNA  ->  Python detection core  (Pine v5, FULL faithful)
# -----------------------------------------------------------------------------
# Source (tick-friendly Pine v5):
#   ".../June 7/Tick Friendly conversion/1st pup fauna_tickfriendly.pine"
#
# ONE shared detection core. Both the tick grain-binder and the time grain-binder
# import THIS module (NINE NINES rule: one canonical core, never 3 copies). The
# only thing the binders supply is the runtime GRAIN (N-tick bars vs time bars)
# and `tf_seconds` (drives the per-TF RVOL threshold tables). The detection LOGIC
# is identical for both grains, so on IDENTICAL bars the fire matrix is byte-for-
# byte identical (proven in the parity harness).
#
# Output: per-bar 0/1 fire + numeric level for EVERY one of the 33 detection
# plots (the 33 plotshape() calls in the Pine source). FULL port -- no plot is
# stubbed (STUB_PARTIAL == []). Pure Python stdlib only.
#
# NINE NINES bans graphic objects (no graphic labels, no tables): detection is
# the boolean that gated each plotshape() in the Pine source, plus a numeric
# level. The banned graphic-label token is never written anywhere in this file.
#
# Pine non-repaint semantics: every signal in the source is gated behind
# `barstate.isconfirmed` (closed bar). In an offline batch every bar fed in IS a
# closed bar (the tick binder already drops the still-forming partial bar), so
# `conf` is True for every bar here -- the gating is preserved structurally.
# =============================================================================
from __future__ import annotations

import math
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nine_nines_common import Bar  # noqa: E402  (shared bar dataclass)

# tick fallback (seconds) when the runtime TF is a tick TF that can't be read as
# seconds -- mirrors the Pine `nn_TICK_FB = 10` guard. The binders pass this in.
TICK_FALLBACK_SEC = 10


# =============================================================================
# PARAMETERS  (every threshold from the Pine inputs is a parameter here)
# =============================================================================
DEFAULTS = dict(
    # master toggles
    firstBarOnly=True,
    enable_PB=False,
    show_GrandSlam=True, show_MOAB=True,
    show_DoubleDisp=True, show_FullStack=True, show_FVGStack=True,
    show_Katana=True, show_Musashi=True,
    show_WhaleBull=True, show_WhaleBear=True,
    show_PUP=True, show_PPD=True,
    show_SAABSq=True, show_KRATOSSq=True,
    show_TyphoonBull=True, show_TyphoonBear=True,
    show_TomcatBull=True, show_TomcatBear=True,
    show_Nagasaki=True,
    show_PAFBull=True, show_PAFBear=True,
    show_SuperBull=True, show_SuperBear=True,
    show_Alpha=True, show_Bravo=True, show_Charlie=True, show_Delta=True,
    show_Echo=True, show_Foxtrot=True, show_Golf=True, show_OD=True,
    # SAAB2 / KRATOS2
    saab2_reqConfirm=False,
    # RVOL bull/bear calc
    bb_avgLength=30, bb_smaLength=20,
    # RVOL Reg @ time
    reg_anchorTimeframe="", reg_length=30,
    reg_calculationMode="Regular", reg_adjustRealtime=True,
    # Displacement
    i_req_fvg=True, i_range_type="Open to Close", i_std_len=100, i_std_mult=5,
    # GZ1 / HV
    gz1_threshPct=2.0, gz1_auto=True, gz1_dist=7, gz1_mitLvl=False,
    # Zoo engine
    zoo_ma_type="VWMA", zoo_ma_len=5,
    zoo_pbj_ma_period=20, zoo_pbj_atr_period=14, zoo_pbj_hh_ll=25,
    zoo_pbj_atr_mult=3.0, zoo_pbj_vol_period=20, zoo_pbj_vol_mult=0.1,
    zoo_use_st=True, zoo_st_period=10, zoo_st_mult=2.0,
    # Yin Yang
    yy_leftBars=75, yy_rightBars=1, yy_atrLength=50, yy_atrMult=3.5,
    # Whale
    wh_lenBull=20, wh_lenBear=20, wh_useQ=True, wh_useY=True, wh_useATH=True,
    # Pocket pivot
    pp_barSize=3.0, pp_lookback=10,
    # FAUNA+ Alpha
    fp_a_rng="Open to Close", fp_a_mult=5, fp_a_req=2, fp_a_win=2, fp_a_fb=False,
    fp_a_fauna_rq=0, fp_a_pp_rq=0, fp_a_fvg_rq=0,
    # FAUNA+ Bravo
    fp_b_rng="Open to Close", fp_b_mult=5, fp_b_req=3, fp_b_win=3, fp_b_fb=False,
    fp_b_fauna_rq=0, fp_b_pp_rq=0, fp_b_fvg_rq=0,
    # FAUNA+ Charlie
    fp_c_rng="Open to Close", fp_c_mult=5, fp_c_req=3, fp_c_win=4, fp_c_fb=False,
    fp_c_fauna_rq=0, fp_c_pp_rq=0, fp_c_fvg_rq=0,
    # FAUNA+ Delta
    fp_d_rng="Open to Close", fp_d_mult=5, fp_d_req=2, fp_d_win=3, fp_d_fb=False,
    fp_d_fauna_rq=0, fp_d_pp_rq=0, fp_d_fvg_rq=0,
    # FAUNA+ Echo
    fp_e_rng="Open to Close", fp_e_mult=5, fp_e_req=2, fp_e_win=4, fp_e_fb=False,
    fp_e_fauna_rq=0, fp_e_pp_rq=0, fp_e_fvg_rq=0,
    # Opening Drive
    od_max=2, od_rng="Open to Close", od_mult=5,
)


# =============================================================================
# DETECTION-PLOT REGISTRY  (33 plots == the 33 plotshape() calls, IN ORDER)
# id -> (descriptor, level_kind). level_kind:
#   "bool"  -> level == the 0/1 fire (a boolean signal).
#   "rvol"  -> level == bb_normalizedPrice on a fire, else 0.0 (RVOL magnitude).
# =============================================================================
PLOT_REGISTRY: "dict[str, tuple[str, str]]" = {
    "Super":               ("Super combo (PBJ/PB) bull|bear",                 "bool"),
    "Grand Slam":          ("Grand Slam RVOL bull spike",                     "rvol"),
    "MOAB":                ("MOAB RVOL bear spike",                           "rvol"),
    "Whale+PUP":           ("Whale pivot + PUP + HV + PBJ (bull)",            "bool"),
    "Whale+PPD":           ("Whale pivot + PPD + HV + PBJ (bear)",            "bool"),
    "SAAB2":               ("SAAB-squared bull",                             "bool"),
    "KRATOS2":             ("KRATOS-squared bear",                           "bool"),
    "Typhoon Bull":        ("Typhoon bull (swing low + fauna + extra)",       "bool"),
    "Typhoon Bear":        ("Typhoon bear (swing high + fauna + extra)",      "bool"),
    "Tomcat Bull":         ("Tomcat bull (1st bar + fauna + disp + 2-of-3)",  "bool"),
    "Tomcat Bear":         ("Tomcat bear (1st bar + fauna + disp + 2-of-3)",  "bool"),
    "Nagasaki Bull":       ("Nagasaki HEV + bull directional",                "bool"),
    "Nagasaki Bear":       ("Nagasaki HEV + bear directional",                "bool"),
    "PAF PUP B2B":         ("PUP + Fauna back-to-back (bull)",                "bool"),
    "PAF PPD B2B":         ("PPD + Fauna back-to-back (bear)",                "bool"),
    "FAUNA+ Bull":         ("FAUNA+ density set Alpha-Foxtrot (bull)",        "bool"),
    "FAUNA+ Bear":         ("FAUNA+ density set Alpha-Foxtrot (bear)",        "bool"),
    "Golf Bull":           ("Golf PUP-squared (bull)",                        "bool"),
    "Golf Bear":           ("Golf PPD-squared (bear)",                        "bool"),
    "Opening Drive Bull":  ("Opening Drive (bull)",                           "bool"),
    "Opening Drive Bear":  ("Opening Drive (bear)",                           "bool"),
    "Katana Bull":         ("Katana session (bull)",                         "bool"),
    "Katana Bear":         ("Katana session (bear)",                         "bool"),
    "Musashi Bull":        ("Musashi (GZI/HV + PUP + Whale + PBJ) bull",      "bool"),
    "Musashi Bear":        ("Musashi (GZI/HV + PPD + Whale + PBJ) bear",      "bool"),
    "Double Disp Bull":    ("Double displacement + fauna + PUP/PBJ (bull)",   "bool"),
    "Double Disp Bear":    ("Double displacement + fauna + PPD/PBJ (bear)",   "bool"),
    "PUP Combo":           ("PUP combo (disp + fauna + PUP, b2b)",            "bool"),
    "PPD Combo":           ("PPD combo (disp + fauna + PPD, b2b)",            "bool"),
    "Full Stack Bull":     ("Full stack (RVOL + fauna + disp + PBJ) bull",    "bool"),
    "Full Stack Bear":     ("Full stack (RVOL + fauna + disp + PBJ) bear",    "bool"),
    "FVG Stack Bull":      ("FVG stack (RVOL + fauna + disp + HV + GZI) bull", "bool"),
    "FVG Stack Bear":      ("FVG stack (RVOL + fauna + disp + HV + GZI) bear", "bool"),
}

# Ordered plot ids (same order the Pine source emits the plotshape() calls).
PLOT_IDS: "list[str]" = list(PLOT_REGISTRY.keys())

# FULL faithful port -- no plot is stubbed.
STUB_PARTIAL: "list[str]" = []


# =============================================================================
# Pine ta.* mirrors (local, stdlib-only).  None == Pine `na`.
# =============================================================================
def _sma(values, length):
    out = [None] * len(values)
    s = 0.0
    cnt = 0
    win = []
    for i, v in enumerate(values):
        vv = None if v is None else float(v)
        win.append(vv)
        if vv is not None:
            s += vv
            cnt += 1
        if len(win) > length:
            old = win.pop(0)
            if old is not None:
                s -= old
                cnt -= 1
        if len(win) == length and cnt == length:
            out[i] = s / length
    return out


def _stdev(values, length):
    out = [None] * len(values)
    win = []
    for i, v in enumerate(values):
        vv = None if v is None else float(v)
        win.append(vv)
        if len(win) > length:
            win.pop(0)
        if len(win) == length and all(w is not None for w in win):
            m = sum(win) / length
            var = sum((w - m) ** 2 for w in win) / length
            out[i] = math.sqrt(var)
    return out


def _highest(values, length):
    out = [None] * len(values)
    win = []
    for i, v in enumerate(values):
        win.append(None if v is None else float(v))
        if len(win) > length:
            win.pop(0)
        vals = [w for w in win if w is not None]
        if len(win) == length and vals:
            out[i] = max(vals)
    return out


def _lowest(values, length):
    out = [None] * len(values)
    win = []
    for i, v in enumerate(values):
        win.append(None if v is None else float(v))
        if len(win) > length:
            win.pop(0)
        vals = [w for w in win if w is not None]
        if len(win) == length and vals:
            out[i] = min(vals)
    return out


def _rma(values, length):
    out = [None] * len(values)
    prev = None
    seed_sum = 0.0
    seed_cnt = 0
    for i, v in enumerate(values):
        vv = None if v is None else float(v)
        if vv is None:
            out[i] = prev
            continue
        if prev is None:
            seed_sum += vv
            seed_cnt += 1
            if seed_cnt == length:
                prev = seed_sum / length
                out[i] = prev
        else:
            prev = (prev * (length - 1) + vv) / length
            out[i] = prev
    return out


def _true_range(o, h, l, c):
    n = len(c)
    tr = [None] * n
    for i in range(n):
        if i == 0:
            tr[i] = h[i] - l[i]
        else:
            tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    return tr


def _atr(o, h, l, c, length):
    return _rma(_true_range(o, h, l, c), length)


def _ema(values, length):
    out = [None] * len(values)
    alpha = 2.0 / (length + 1.0)
    prev = None
    seed_sum = 0.0
    seed_cnt = 0
    for i, v in enumerate(values):
        vv = None if v is None else float(v)
        if vv is None:
            out[i] = prev
            continue
        if prev is None:
            seed_sum += vv
            seed_cnt += 1
            if seed_cnt == length:
                prev = seed_sum / length
                out[i] = prev
        else:
            prev = alpha * vv + (1 - alpha) * prev
            out[i] = prev
    return out


def _wma(values, length):
    out = [None] * len(values)
    denom = length * (length + 1) / 2.0
    for i in range(len(values)):
        if i + 1 < length:
            continue
        window = values[i - length + 1: i + 1]
        if any(w is None for w in window):
            continue
        s = 0.0
        for k, w in enumerate(window):  # oldest weight 1 ... newest weight length
            s += float(w) * (k + 1)
        out[i] = s / denom
    return out


def _hma(values, length):
    half = max(1, int(length / 2))
    sqrtlen = max(1, int(round(math.sqrt(length))))
    wma_half = _wma(values, half)
    wma_full = _wma(values, length)
    raw = [None] * len(values)
    for i in range(len(values)):
        if wma_half[i] is not None and wma_full[i] is not None:
            raw[i] = 2 * wma_half[i] - wma_full[i]
    return _wma(raw, sqrtlen)


def _vwma(values, volume, length):
    out = [None] * len(values)
    pv = [None if values[i] is None else float(values[i]) * float(volume[i])
          for i in range(len(values))]
    num = _sma(pv, length)
    den = _sma([float(x) for x in volume], length)
    for i in range(len(values)):
        if num[i] is not None and den[i] not in (None, 0):
            out[i] = num[i] / den[i]
    return out


def _cum_ratio(h, l):
    """ta.cum((high-low)/low) / bar_index  (auto-threshold). index = i (0-based)."""
    out = [None] * len(h)
    s = 0.0
    for i in range(len(h)):
        if l[i]:
            s += (h[i] - l[i]) / l[i]
        out[i] = (s / i) if i > 0 else 0.0
    return out


def _nz(x, repl=0.0):
    return repl if (x is None or (isinstance(x, float) and math.isnan(x))) else x


def _crossover(a, b, i):
    """ta.crossover(a,b) at bar i: a[i] > b[i] and a[i-1] <= b[i-1]."""
    if i == 0 or a[i] is None or b[i] is None or a[i - 1] is None or b[i - 1] is None:
        return False
    return a[i] > b[i] and a[i - 1] <= b[i - 1]


def _crossunder(a, b, i):
    if i == 0 or a[i] is None or b[i] is None or a[i - 1] is None or b[i - 1] is None:
        return False
    return a[i] < b[i] and a[i - 1] >= b[i - 1]


# =============================================================================
# RVOL per-TF threshold tables (verbatim from the Pine source).
# =============================================================================
def _rvol_1x_threshold(s):
    if s <= 10:   return 38.0
    if s <= 15:   return 33.0
    if s <= 30:   return 28.0
    if s <= 45:   return 23.0
    if s <= 60:   return 20.0
    if s <= 120:  return 19.0
    if s <= 180:  return 17.0
    if s <= 240:  return 16.0
    if s <= 300:  return 15.0
    if s <= 360:  return 14.0
    if s <= 420:  return 12.0
    if s <= 480:  return 11.0
    if s <= 540:  return 10.0
    if s <= 600:  return 10.0
    if s <= 900:  return 7.0
    if s <= 3600: return 3.5
    return 1.8


def _gs_moab_threshold(s):
    if s <= 10:   return 114.0
    if s <= 15:   return 99.0
    if s <= 30:   return 84.0
    if s <= 45:   return 69.0
    if s <= 60:   return 35.0
    if s <= 300:  return 35.0
    if s <= 600:  return 25.0
    if s <= 900:  return 20.0
    if s <= 3600: return 10.0
    return 8.0


# =============================================================================
# THE PORT.  Computes every signal exactly as the Pine source, then the 33
# detection plots' gating booleans.
# =============================================================================
def _shift_bool(arr, off):
    """Pine arr[off] for a boolean series; OOB -> False (Pine na in a bool ctx)."""
    n = len(arr)
    out = [False] * n
    for i in range(n):
        j = i - off
        out[i] = bool(arr[j]) if 0 <= j < n else False
    return out


def _count_back(sig, i, lookback):
    """Pine f_fp_count: number of True in sig[0..lookback-1] looking back from i."""
    c = 0
    for k in range(lookback):
        j = i - k
        if 0 <= j < len(sig) and sig[j]:
            c += 1
    return c


def _compute_all(bars: Sequence[Bar], P: dict, tf_seconds: float):
    n = len(bars)
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    l = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]
    conf = [True] * n  # offline: every bar is a closed/confirmed bar

    # ----- tf seconds / RVOL thresholds -----
    is_tick = tf_seconds is None or tf_seconds <= 0
    tfSec = TICK_FALLBACK_SEC if is_tick else tf_seconds
    th_1x = _rvol_1x_threshold(tfSec)
    th_gs_moab = _gs_moab_threshold(tfSec)
    th_saab_kratos = th_1x * 0.56

    # ----- session boundary (Pine ta.change(time("D")) != 0) using UTC day -----
    from datetime import datetime, timezone

    def _day(tsm):
        return datetime.fromtimestamp(tsm / 1000, tz=timezone.utc).toordinal()
    day_ord = [_day(t) for t in ts]
    is_new_sess = [False] * n
    for i in range(n):
        if i == 0:
            is_new_sess[i] = True  # first bar opens the first session
        else:
            is_new_sess[i] = day_ord[i] != day_ord[i - 1]

    # session bar counter (Opening Drive)
    sessionBarCount = [0] * n
    cur = 0
    for i in range(n):
        if is_new_sess[i]:
            cur = 1
        else:
            cur += 1
        sessionBarCount[i] = cur

    # =========================================================================
    # RVOL bull/bear calc
    # =========================================================================
    bb_spike = [abs(c[i] - o[i]) for i in range(n)]
    bb_avgSpike = _shift_bool  # placeholder to avoid lints; real calc below
    _avgSpike = _sma(bb_spike, P["bb_avgLength"])
    bb_avgSpikeDenom = [None] + _avgSpike[:-1]      # [1] shift
    _avgVol = _sma(v, P["bb_avgLength"])
    bb_avgVolDenom = [None] + _avgVol[:-1]          # [1] shift
    # Pine `x / nz(denom, 1.0)`: nz only replaces na, NOT zero. Pine 0.0/0.0 -> na
    # (no crash); na in any `>`/`>=` comparison is False. Mirror with NaN, which
    # compares False everywhere -> the RVOL signals simply do not fire (correct).
    def _safe_div(num, denom):
        d = _nz(denom, 1.0)
        if d == 0:
            return float("nan")
        return num / d
    bb_normPrice = [_safe_div(bb_spike[i], bb_avgSpikeDenom[i]) for i in range(n)]
    bb_normVol = [_safe_div(v[i], bb_avgVolDenom[i]) for i in range(n)]
    bb_diff = [bb_normPrice[i] - bb_normVol[i] for i in range(n)]
    bb_posDiff = [bb_diff[i] if bb_diff[i] > 0 else None for i in range(n)]
    bb_smaDiff = _sma(bb_posDiff, P["bb_smaLength"])
    bb_baseBull = [(c[i] > o[i]) and (bb_posDiff[i] is not None) and
                   (bb_smaDiff[i] is not None) and (bb_posDiff[i] > bb_smaDiff[i])
                   for i in range(n)]
    bb_baseBear = [(c[i] < o[i]) and (bb_posDiff[i] is not None) and
                   (bb_smaDiff[i] is not None) and (bb_posDiff[i] > bb_smaDiff[i])
                   for i in range(n)]

    def _in_range(x, lo, hi):
        return x >= lo and x < hi

    sigBullRVOL1x = [conf[i] and bb_baseBull[i] and _in_range(bb_normPrice[i], th_1x, th_gs_moab) for i in range(n)]
    sigBearRVOL1x = [conf[i] and bb_baseBear[i] and _in_range(bb_normPrice[i], th_1x, th_gs_moab) for i in range(n)]
    sigGrandSlam  = [conf[i] and bb_baseBull[i] and (bb_normPrice[i] >= th_gs_moab) for i in range(n)]
    sigMOAB       = [conf[i] and bb_baseBear[i] and (bb_normPrice[i] >= th_gs_moab) for i in range(n)]
    sigSAAB   = [conf[i] and bb_baseBull[i] and _in_range(bb_normPrice[i], th_saab_kratos, th_1x) for i in range(n)]
    sigKratos = [conf[i] and bb_baseBear[i] and _in_range(bb_normPrice[i], th_saab_kratos, th_1x) for i in range(n)]

    # =========================================================================
    # GZ1 HV FVG logic
    # =========================================================================
    gz_v1 = [None] + v[:-1]                              # volume[1]
    _hv5000 = [None] + _highest(v, 5000)[:-1]            # highest(volume,5000)[1]
    _hv252  = [None] + _highest(v, 252)[:-1]             # highest(volume,252)[1]
    gz_isHV = [(gz_v1[i] is not None) and
               ((gz_v1[i] == _hv5000[i]) or (gz_v1[i] == _hv252[i])) for i in range(n)]

    cumthr = _cum_ratio(h, l)
    gz_thresh = [cumthr[i] if P["gz1_auto"] else P["gz1_threshPct"] / 100.0 for i in range(n)]
    gz_bFVG = [False] * n
    gz_sFVG = [False] * n
    for i in range(n):
        if i >= 2 and l[i] > h[i - 2] and c[i - 1] > h[i - 2] and h[i - 2] != 0:
            gz_bFVG[i] = (l[i] - h[i - 2]) / h[i - 2] > gz_thresh[i]
        if i >= 2 and h[i] < l[i - 2] and c[i - 1] < l[i - 2] and h[i] != 0:
            gz_sFVG[i] = (l[i - 2] - h[i]) / h[i] > gz_thresh[i]

    # FVG zone array + GZI overlap detection (faithful to the Pine engine)
    gz_fvgs: list[dict] = []   # newest first (unshift)
    gz_lastT = 0
    gz_bullGZI = [False] * n
    gz_bearGZI = [False] * n
    gz_bullHV = [False] * n
    gz_bearHV = [False] * n
    for i in range(n):
        # Process Bull FVG
        if gz_bFVG[i] and ts[i] != gz_lastT:
            mx = l[i]
            mn = h[i - 2]
            if gz_isHV[i]:
                gz_bullHV[i] = True
            for e in gz_fvgs:
                if e["bull"] and (i - e["idx"]) <= P["gz1_dist"]:
                    ob = max(e["mn"], mn)
                    ot = min(e["mx"], mx)
                    if ob < ot or (ob <= ot and e["hv"] and gz_isHV[i]):
                        gz_bullGZI[i] = True
                        break
            gz_fvgs.insert(0, dict(mx=mx, mn=mn, bull=True, t=ts[i], idx=i, hv=gz_isHV[i]))
            gz_lastT = ts[i]
        # Process Bear FVG
        if gz_sFVG[i] and ts[i] != gz_lastT:
            mx = l[i - 2]
            mn = h[i]
            if gz_isHV[i]:
                gz_bearHV[i] = True
            for e in gz_fvgs:
                if (not e["bull"]) and (i - e["idx"]) <= P["gz1_dist"]:
                    ob = max(e["mn"], mn)
                    ot = min(e["mx"], mx)
                    if ob < ot or (ob <= ot and e["hv"] and gz_isHV[i]):
                        gz_bearGZI[i] = True
                        break
            gz_fvgs.insert(0, dict(mx=mx, mn=mn, bull=False, t=ts[i], idx=i, hv=gz_isHV[i]))
            gz_lastT = ts[i]
        if len(gz_fvgs) > 50:
            gz_fvgs.pop()

    # =========================================================================
    # FAUNA
    # =========================================================================
    fauna_atr = _atr(o, h, l, c, 14)
    fauna_avgVol = _sma(v, 20)
    fauna_avgBody = _sma([abs(c[i] - o[i]) for i in range(n)], 20)
    fauna_avgRange = _sma([h[i] - l[i] for i in range(n)], 20)  # noqa: F841 (parity w/ source)
    fauna_avgDelta = _sma([0.0] + [abs(c[i] - c[i - 1]) for i in range(1, n)], 10)
    fauna_trendMA = _sma(c, 50)
    body = [c[i] - o[i] for i in range(n)]
    rng = [h[i] - l[i] for i in range(n)]
    bsz = [abs(x) for x in body]
    brt = [0.0 if rng[i] == 0 else bsz[i] / rng[i] for i in range(n)]
    up = [body[i] > 0 for i in range(n)]
    dn = [body[i] < 0 for i in range(n)]

    def _vg(i):  # volume > 1.8 * avgVol
        return fauna_avgVol[i] is not None and v[i] > 1.8 * fauna_avgVol[i]

    MB_b = [False] * n; RE_b = [False] * n; TA_b = [False] * n; GG_b = [False] * n
    MB_r = [False] * n; RE_r = [False] * n; TA_r = [False] * n; GG_r = [False] * n
    for i in range(n):
        a = fauna_atr[i]
        if a is not None and _vg(i):
            MB_b[i] = up[i] and bsz[i] > 1.6 * a and brt[i] > 0.7
            MB_r[i] = dn[i] and bsz[i] > 1.6 * a and brt[i] > 0.7
            RE_b[i] = up[i] and rng[i] > 2.2 * a and (h[i] - c[i]) < 0.15 * rng[i]
            RE_r[i] = dn[i] and rng[i] > 2.2 * a and (c[i] - l[i]) < 0.15 * rng[i]
        if i > 0 and a is not None and _vg(i):
            GG_b[i] = (o[i] - c[i - 1]) > 0.9 * a and up[i] and l[i] > c[i - 1]
            GG_r[i] = (c[i - 1] - o[i]) > 0.9 * a and dn[i] and h[i] < c[i - 1]
        if (i > 0 and fauna_avgDelta[i] is not None and _vg(i)
                and fauna_trendMA[i] is not None and fauna_trendMA[i - 1] is not None):
            tup = fauna_trendMA[i] > fauna_trendMA[i - 1]
            tdn = fauna_trendMA[i] < fauna_trendMA[i - 1]
            TA_b[i] = tup and (c[i] - c[i - 1]) > 1.6 * fauna_avgDelta[i] and up[i]
            TA_r[i] = tdn and (c[i - 1] - c[i]) > 1.6 * fauna_avgDelta[i] and dn[i]

    sigFAUNABull = [False] * n
    sigFAUNABear = [False] * n
    for i in range(1, n):
        pbody = c[i - 1] - o[i - 1]
        prng = h[i - 1] - l[i - 1]
        ab1 = fauna_avgBody[i - 1]
        av1 = fauna_avgVol[i - 1]
        strongBear = (c[i - 1] < o[i - 1] and ab1 is not None and av1 is not None
                      and abs(pbody) > 1.5 * ab1 and v[i - 1] > 1.5 * av1)
        weakBear = c[i - 1] < o[i - 1] and (0.0 if prng == 0 else abs(pbody) / prng) <= 0.2
        strongBull = (c[i - 1] > o[i - 1] and ab1 is not None and av1 is not None
                      and abs(pbody) > 1.5 * ab1 and v[i - 1] > 1.5 * av1)
        weakBull = c[i - 1] > o[i - 1] and (0.0 if prng == 0 else abs(pbody) / prng) <= 0.2
        # bull
        TR_b = weakBear and (MB_b[i] or RE_b[i] or TA_b[i])
        ES_b = strongBear and (MB_b[i] or RE_b[i] or TA_b[i])
        GDR_b = c[i - 1] < o[i - 1] and GG_b[i]
        excluded_bull = GG_b[i] or TR_b or ES_b or GDR_b
        sigFAUNABull[i] = conf[i] and (MB_b[i] or RE_b[i] or TA_b[i]) and not excluded_bull
        # bear
        TR_r = weakBull and (MB_r[i] or RE_r[i] or TA_r[i])
        ES_r = strongBull and (MB_r[i] or RE_r[i] or TA_r[i])
        GDR_r = c[i - 1] > o[i - 1] and GG_r[i]
        excluded_bear = GG_r[i] or TR_r or ES_r or GDR_r
        sigFAUNABear[i] = conf[i] and (MB_r[i] or RE_r[i] or TA_r[i]) and not excluded_bear

    # =========================================================================
    # DISPLACEMENT
    # =========================================================================
    disp_rng = [abs(o[i] - c[i]) if P["i_range_type"] == "Open to Close" else (h[i] - l[i]) for i in range(n)]
    disp_std = _stdev(disp_rng, P["i_std_len"])
    disp_thresh = [None if disp_std[i] is None else disp_std[i] * P["i_std_mult"] for i in range(n)]
    disp_currDisp = [disp_thresh[i] is not None and disp_rng[i] > disp_thresh[i] for i in range(n)]
    disp_prevDisp = [i > 0 and disp_thresh[i - 1] is not None and disp_rng[i - 1] > disp_thresh[i - 1] for i in range(n)]
    disp_bullFVG = [i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1] for i in range(n)]
    disp_bearFVG = [i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1] for i in range(n)]
    disp_bullBar = [c[i] > o[i] for i in range(n)]
    disp_bearBar = [c[i] < o[i] for i in range(n)]
    req_fvg = P["i_req_fvg"]
    sigDISPBull = [conf[i] and ((disp_prevDisp[i] and disp_bullFVG[i]) if req_fvg else (disp_currDisp[i] and disp_bullBar[i])) for i in range(n)]
    sigDISPBear = [conf[i] and ((disp_prevDisp[i] and disp_bearFVG[i]) if req_fvg else (disp_currDisp[i] and disp_bearBar[i])) for i in range(n)]

    disp_thresh_pup = [None if disp_std[i] is None else disp_std[i] * 2 for i in range(n)]
    disp_prevDisp_pup = [i > 0 and disp_thresh_pup[i - 1] is not None and disp_rng[i - 1] > disp_thresh_pup[i - 1] for i in range(n)]
    disp_currDisp_pup = [disp_thresh_pup[i] is not None and disp_rng[i] > disp_thresh_pup[i] for i in range(n)]
    sigDISPBull_pup = [conf[i] and ((disp_prevDisp_pup[i] and disp_bullFVG[i]) if req_fvg else (disp_currDisp_pup[i] and disp_bullBar[i])) for i in range(n)]
    sigDISPBear_pup = [conf[i] and ((disp_prevDisp_pup[i] and disp_bearFVG[i]) if req_fvg else (disp_currDisp_pup[i] and disp_bearBar[i])) for i in range(n)]

    # =========================================================================
    # YIN YANG swing high/low + breakout/breakdown (stateful, faithful)
    # =========================================================================
    yy_atr = _atr(o, h, l, c, P["yy_atrLength"])
    yy_thr = [None if yy_atr[i] is None else yy_atr[i] * P["yy_atrMult"] for i in range(n)]
    lb = P["yy_leftBars"]; rb = P["yy_rightBars"]

    def _pivot_high(i):
        # ta.pivothigh(high, lb, rb): high[i-rb] strictly highest over [i-rb-lb, i]
        center = i - rb
        if center - lb < 0 or i >= n:
            return None
        cv = h[center]
        for k in range(center - lb, i + 1):
            if k == center:
                continue
            if h[k] >= cv:
                return None
        return cv

    def _pivot_low(i):
        center = i - rb
        if center - lb < 0 or i >= n:
            return None
        cv = l[center]
        for k in range(center - lb, i + 1):
            if k == center:
                continue
            if l[k] <= cv:
                return None
        return cv

    yy_srs: list[dict] = []
    yy_lastValid = None
    yy_validHigh = [False] * n
    yy_validLow = [False] * n
    yy_breakout = [False] * n
    yy_breakdown = [False] * n
    for i in range(n):
        rawHigh = _pivot_high(i)
        rawLow = _pivot_low(i)
        if rawHigh is not None and conf[i]:
            if yy_lastValid is None or (yy_thr[i] is not None and abs(rawHigh - yy_lastValid) >= yy_thr[i]):
                yy_validHigh[i] = True
                yy_lastValid = rawHigh
                yy_srs.append(dict(price=rawHigh, isRes=True))
        if rawLow is not None and conf[i]:
            if yy_lastValid is None or (yy_thr[i] is not None and abs(rawLow - yy_lastValid) >= yy_thr[i]):
                yy_validLow[i] = True
                yy_lastValid = rawLow
                yy_srs.append(dict(price=rawLow, isRes=False))
        if yy_srs and conf[i]:
            for j in range(len(yy_srs) - 1, -1, -1):
                sr = yy_srs[j]
                crossed = False
                if sr["isRes"]:
                    if c[i] > sr["price"] and (i == 0 or c[i - 1] <= sr["price"]):
                        crossed = True
                        yy_breakout[i] = True
                else:
                    if c[i] < sr["price"] and (i == 0 or c[i - 1] >= sr["price"]):
                        crossed = True
                        yy_breakdown[i] = True
                if crossed:
                    yy_srs.pop(j)
        while len(yy_srs) > 50:
            yy_srs.pop(0)

    # =========================================================================
    # HV standalone + NAGASAKI
    # =========================================================================
    hv2_hve = _highest(v, 5000)
    hv2_hvy = _highest(v, 252)
    sigHV = [conf[i] and ((v[i] == hv2_hve[i]) or (v[i] == hv2_hvy[i])) for i in range(n)]

    sigNagasaki = [False] * n
    nag_maxVol = 0.0
    for i in range(n):
        if conf[i]:
            if i == 0:
                nag_maxVol = v[i]
            elif v[i] > nag_maxVol:
                sigNagasaki[i] = True
                nag_maxVol = v[i]

    # =========================================================================
    # POCKET PIVOT (PUP / PPD)
    # =========================================================================
    pp_redVol = [v[i] if c[i] < o[i] else 0.0 for i in range(n)]
    pp_greenVol = [v[i] if c[i] > o[i] else 0.0 for i in range(n)]
    pp_hiRed = _highest([None] + pp_redVol[:-1], P["pp_lookback"])    # highest(redVol[1],lb)
    pp_hiGreen = _highest([None] + pp_greenVol[:-1], P["pp_lookback"])
    pp_priceUp = [o[i] != 0 and ((c[i] - o[i]) / o[i]) * 100 > P["pp_barSize"] for i in range(n)]
    pp_priceDn = [o[i] != 0 and ((o[i] - c[i]) / o[i]) * 100 > P["pp_barSize"] for i in range(n)]
    pp_volBull = [pp_hiRed[i] is not None and v[i] > pp_hiRed[i] for i in range(n)]
    pp_volBear = [pp_hiGreen[i] is not None and v[i] > pp_hiGreen[i] for i in range(n)]
    sigPUP = [conf[i] and pp_priceUp[i] and pp_volBull[i] for i in range(n)]
    sigPPD = [conf[i] and pp_priceDn[i] and pp_volBear[i] for i in range(n)]

    # =========================================================================
    # WHALE pivot family (PBJ wired in after the engine)
    # =========================================================================
    wh_sma_bull = _sma(c, P["wh_lenBull"])
    wh_sma_bear = _sma(c, P["wh_lenBear"])
    wh_volAvg = _sma(v, 50)
    wh_hvy = _highest(v, 252)
    wh_hvq = _highest(v, 63)
    wh_maxEver = [0.0] * n
    running = 0.0
    for i in range(n):
        if v[i] > running:
            running = v[i]
        wh_maxEver[i] = running

    wh_isHV = [((P["wh_useQ"] and v[i] == wh_hvq[i]) or
                (P["wh_useY"] and v[i] == wh_hvy[i]) or
                (P["wh_useATH"] and v[i] == wh_maxEver[i])) for i in range(n)]
    wh_pivotBull = [False] * n
    wh_pivotBear = [False] * n
    LB = P["wh_lenBull"]; LR = P["wh_lenBear"]
    for i in range(n):
        # max down-bar volume over the last wh_lenBull bars (Pine for i=1..len)
        maxDn = 0.0
        for k in range(1, LB + 1):
            if i - k >= 0 and i - k - 1 >= 0 and c[i - k] < c[i - k - 1]:
                if v[i - k] > maxDn:
                    maxDn = v[i - k]
        maxUp = 0.0
        for k in range(1, LR + 1):
            if i - k >= 0 and i - k - 1 >= 0 and c[i - k] > c[i - k - 1]:
                if v[i - k] > maxUp:
                    maxUp = v[i - k]
        greenBar = i > 0 and c[i] > c[i - 1]
        redBar = i > 0 and c[i] < c[i - 1]
        smb = wh_sma_bull[i]
        smr = wh_sma_bear[i]
        wva = wh_volAvg[i]
        if smb is not None and wva is not None:
            surgeonBull = greenBar and (l[i] <= smb) and (c[i] > smb) and (v[i] > maxDn) and (v[i] > wva)
            origBull = greenBar and (l[i] <= smb) and (v[i] > maxDn)
            wh_pivotBull[i] = surgeonBull or origBull
        if smr is not None and wva is not None:
            surgeonBear = redBar and (h[i] >= smr) and (c[i] < smr) and (v[i] > maxUp) and (v[i] > wva)
            origBear = redBar and (h[i] >= smr) and (v[i] > maxUp)
            wh_pivotBear[i] = surgeonBear or origBear

    # =========================================================================
    # PB&J ENGINE (supertrend lander + reaccel zones + PBJ HH/LL touch)
    # =========================================================================
    atr_pb = [None if fauna_atr[i] is None else fauna_atr[i] * 2.0 for i in range(n)]
    src = list(c)  # zoo_price_src default = close
    if P["zoo_ma_type"] == "EMA":
        base_ma = _ema(src, P["zoo_ma_len"])
    elif P["zoo_ma_type"] == "SMA":
        base_ma = _sma(src, P["zoo_ma_len"])
    elif P["zoo_ma_type"] == "WMA":
        base_ma = _wma(src, P["zoo_ma_len"])
    elif P["zoo_ma_type"] == "HMA":
        base_ma = _hma(src, P["zoo_ma_len"])
    else:  # VWMA default
        base_ma = _vwma(src, v, P["zoo_ma_len"])

    st_atr_series = _atr(o, h, l, c, P["zoo_st_period"])
    st_atr = [None if st_atr_series[i] is None else P["zoo_st_mult"] * st_atr_series[i] for i in range(n)]
    mintick = 0.0  # syminfo.mintick unknown offline; use 0 so any nonzero band is added

    curr_long = [0.0] * n
    curr_short = [0.0] * n
    st_dir = [1] * n
    sig_line = [None] * n
    for i in range(n):
        bm = base_ma[i]
        dl = None if (bm is None or st_atr[i] is None) else bm - st_atr[i]
        ds = None if (bm is None or st_atr[i] is None) else bm + st_atr[i]
        prev_cl = curr_long[i - 1] if i > 0 else None
        prev_cs = curr_short[i - 1] if i > 0 else None
        # curr_long := base_ma > nz(curr_long[1], dyn_long) ? max(dyn_long, nz(curr_long[1])) : dyn_long
        if dl is None:
            curr_long[i] = _nz(prev_cl, 0.0)
        else:
            ref = _nz(prev_cl, dl)
            curr_long[i] = max(dl, _nz(prev_cl, 0.0)) if (bm is not None and bm > ref) else dl
        if ds is None:
            curr_short[i] = _nz(prev_cs, 0.0)
        else:
            ref = _nz(prev_cs, ds)
            curr_short[i] = min(ds, _nz(prev_cs, 1e18)) if (bm is not None and bm < ref) else ds
        prev_dir = st_dir[i - 1] if i > 0 else 1
        if P["zoo_use_st"]:
            d = prev_dir
            if _nz(prev_dir, 0) == -1 and bm is not None and src[i] > _nz(prev_cs, src[i] - 1):
                d = 1
            elif _nz(prev_dir, 0) == 1 and bm is not None and src[i] < _nz(prev_cl, src[i] + 1):
                d = -1
            st_dir[i] = d
            sig_line[i] = curr_long[i] if d == 1 else curr_short[i]
        else:
            st_dir[i] = prev_dir
            sig_line[i] = bm

    buy_cross = [_crossover(src, sig_line, i) for i in range(n)]
    sell_cross = [_crossunder(src, sig_line, i) for i in range(n)]
    is_rising = [i > 0 and sig_line[i] is not None and sig_line[i] > _nz(sig_line[i - 1], sig_line[i]) for i in range(n)]
    is_falling = [i > 0 and sig_line[i] is not None and sig_line[i] < _nz(sig_line[i - 1], sig_line[i]) for i in range(n)]
    bull_reaccel = [False] * n
    bear_reaccel = [False] * n
    for i in range(2, n):
        s1 = _nz(sig_line[i - 1], 0.0)
        s2 = _nz(sig_line[i - 2], 0.0)
        bull_reaccel[i] = st_dir[i] == 1 and is_rising[i] and s1 == s2
        bear_reaccel[i] = st_dir[i] == -1 and is_falling[i] and s1 == s2

    pbj_ma = _ema(c, P["zoo_pbj_ma_period"])
    pbj_atr = _atr(o, h, l, c, P["zoo_pbj_atr_period"])
    pbj_avgVol = _sma(v, P["zoo_pbj_vol_period"])
    pbj_lowest = _lowest(l, P["zoo_pbj_hh_ll"])
    pbj_highest = _highest(h, P["zoo_pbj_hh_ll"])
    pbj_buy = [False] * n
    pbj_sell = [False] * n
    for i in range(n):
        if pbj_ma[i] is None or pbj_atr[i] is None or pbj_avgVol[i] is None or pbj_lowest[i] is None or pbj_highest[i] is None:
            continue
        thr = 0.0 if c[i] == 0 else (pbj_atr[i] / c[i] * P["zoo_pbj_atr_mult"])
        pbj_buy[i] = l[i] < pbj_ma[i] * (1 - thr) and l[i] == pbj_lowest[i] and v[i] > pbj_avgVol[i] * P["zoo_pbj_vol_mult"]
        pbj_sell[i] = h[i] > pbj_ma[i] * (1 + thr) and h[i] == pbj_highest[i] and v[i] > pbj_avgVol[i] * P["zoo_pbj_vol_mult"]

    # zone arrays (landers from crosses, reaccel zones) + approach state machine
    bull_lvls: list[dict] = []
    bear_lvls: list[dict] = []

    def _add_lvl(arr, up_, lo_, vv):
        if abs(up_ - lo_) >= mintick:
            arr.append(dict(upper=up_, lower=lo_, vol=vv, approached=False))

    sig_pb_buy = [False] * n
    sig_pbj_buy = [False] * n
    sig_pb_sell = [False] * n
    sig_pbj_sell = [False] * n
    wait_buy = False
    wait_sell = False
    wait_pbj_buy = False
    wait_pbj_sell = False

    def _check_approach(arr, is_bull, i):
        approached = False
        if arr:
            for j in range(len(arr) - 1, -1, -1):
                if j >= len(arr):
                    continue
                lv = arr[j]
                if is_bull and c[i] < lv["lower"]:
                    arr.pop(j)
                    continue
                if (not is_bull) and c[i] > lv["upper"]:
                    arr.pop(j)
                    continue
                ap = lv["upper"] * 1.005 if is_bull else lv["lower"] * 0.995
                if is_bull:
                    if (not lv["approached"]) and l[i] <= ap:
                        approached = True
                        lv["approached"] = True
                    elif lv["approached"] and l[i] > lv["upper"]:
                        lv["approached"] = False
                else:
                    if (not lv["approached"]) and h[i] >= ap:
                        approached = True
                        lv["approached"] = True
                    elif lv["approached"] and h[i] < lv["lower"]:
                        lv["approached"] = False
        return approached

    for i in range(n):
        apb = atr_pb[i] if atr_pb[i] is not None else 0.0
        # f_add_lander(true, buy_cross, bull_lvls)
        if buy_cross[i] and i > 0:
            up_ = max(o[i - 1], c[i - 1])
            lo_ = l[i - 1]
            if up_ - lo_ < apb * 0.5:
                up_ = lo_ + apb * 0.5
            _add_lvl(bull_lvls, up_, lo_, v[i - 1])
        # f_add_lander(false, sell_cross, bear_lvls)
        if sell_cross[i] and i > 0:
            up_ = h[i - 1]
            lo_ = min(o[i - 1], c[i - 1])
            if up_ - lo_ < apb * 0.5:
                lo_ = up_ - apb * 0.5
            _add_lvl(bear_lvls, up_, lo_, v[i - 1])
        # f_add_reaccel(true, bull_reaccel, bull_lvls)
        if bull_reaccel[i] and sig_line[i] is not None:
            p1 = sig_line[i]
            p2 = min(o[i], c[i])
            _add_lvl(bull_lvls, max(p1, p2), min(p1, p2), v[i])
        if bear_reaccel[i] and sig_line[i] is not None:
            p1 = sig_line[i]
            p2 = max(o[i], c[i])
            _add_lvl(bear_lvls, max(p1, p2), min(p1, p2), v[i])

        # barstate.isconfirmed approach checks
        if _check_approach(bull_lvls, True, i):
            wait_buy = True
        if _check_approach(bear_lvls, False, i):
            wait_sell = True
        if pbj_buy[i]:
            wait_pbj_buy = True
        if pbj_sell[i]:
            wait_pbj_sell = True
        while len(bull_lvls) > 30:
            bull_lvls.pop(0)
        while len(bear_lvls) > 30:
            bear_lvls.pop(0)

        sig_pb_buy[i] = buy_cross[i] and wait_buy
        sig_pbj_buy[i] = buy_cross[i] and wait_pbj_buy
        sig_pb_sell[i] = sell_cross[i] and wait_sell
        sig_pbj_sell[i] = sell_cross[i] and wait_pbj_sell
        if sig_pb_buy[i]:
            wait_buy = False
        if sig_pbj_buy[i]:
            wait_pbj_buy = False
        if sig_pb_sell[i]:
            wait_sell = False
        if sig_pbj_sell[i]:
            wait_pbj_sell = False

    sigBullPB = [conf[i] and P["enable_PB"] and sig_pb_buy[i] and not sig_pbj_buy[i] for i in range(n)]
    sigBullPBJ = [conf[i] and sig_pbj_buy[i] for i in range(n)]
    sigBearPB = [conf[i] and P["enable_PB"] and sig_pb_sell[i] and not sig_pbj_sell[i] for i in range(n)]
    sigBearPBJ = [conf[i] and sig_pbj_sell[i] for i in range(n)]
    anyBullPBJ = list(sigBullPBJ)
    anyBearPBJ = list(sigBearPBJ)

    # WHALE final (needs PBJ)
    sigWhaleBull = [conf[i] and wh_pivotBull[i] and wh_isHV[i] and sigPUP[i] and anyBullPBJ[i] for i in range(n)]
    sigWhaleBear = [conf[i] and wh_pivotBear[i] and wh_isHV[i] and sigPPD[i] and anyBearPBJ[i] for i in range(n)]

    # =========================================================================
    # ANISH PASS (computed; not a plotshape but kept faithful, no harm)
    # =========================================================================
    # (omitted from fire matrix; no plotshape uses it.)

    # =========================================================================
    # FLOOR 1.5 master offset alignment   f_align(sig) = sig if moff==0 else sig[1]
    # =========================================================================
    moff = 1 if P["i_req_fvg"] else 0

    def _align(sig):
        if moff == 0:
            return list(sig)
        return _shift_bool(sig, 1)

    al_BullPBJ = _align(sigBullPBJ)        # noqa: F841
    al_BullPB = _align(sigBullPB)
    al_BearPBJ = _align(sigBearPBJ)        # noqa: F841
    al_BearPB = _align(sigBearPB)
    al_anyBullPBJ = _align(anyBullPBJ)
    al_anyBearPBJ = _align(anyBearPBJ)
    al_FAUNABull = _align(sigFAUNABull)
    al_FAUNABear = _align(sigFAUNABear)
    al_DISPBull = _align(sigDISPBull)      # noqa: F841
    al_DISPBear = _align(sigDISPBear)      # noqa: F841
    al_BullRVOL1x = _align(sigBullRVOL1x)
    al_BearRVOL1x = _align(sigBearRVOL1x)
    al_GrandSlam = _align(sigGrandSlam)
    al_MOAB = _align(sigMOAB)
    al_PUP = _align(sigPUP)
    al_PPD = _align(sigPPD)
    al_WhaleBull = _align(sigWhaleBull)
    al_WhaleBear = _align(sigWhaleBear)
    al_anyBullRVOL = [al_BullRVOL1x[i] or al_GrandSlam[i] for i in range(n)]
    al_anyBearRVOL = [al_BearRVOL1x[i] or al_MOAB[i] for i in range(n)]

    # first-bar gating
    firstBarOnly = P["firstBarOnly"]
    al_isFirstBar = _align(is_new_sess)
    dir0 = [sigFAUNABull[i] or sigFAUNABear[i] or sigDISPBull[i] or sigDISPBear[i] or anyBullPBJ[i] or anyBearPBJ[i] for i in range(n)]
    fb0 = [(not firstBarOnly) or (is_new_sess[i] and dir0[i]) for i in range(n)]
    fauna_or_disp_pbj_rb = [sigFAUNABull[i] or sigFAUNABear[i] or sigDISPBull[i] or sigDISPBear[i] or anyBullPBJ[i] or anyBearPBJ[i] for i in range(n)]
    dirs = _shift_bool(fauna_or_disp_pbj_rb, rb)
    is_new_sess_rb = _shift_bool(is_new_sess, rb)
    fbs = [(not firstBarOnly) or (is_new_sess_rb[i] and dirs[i]) for i in range(n)]
    dirm = [al_FAUNABull[i] or al_FAUNABear[i] or sigDISPBull[i] or sigDISPBear[i] or al_anyBullPBJ[i] or al_anyBearPBJ[i] for i in range(n)]
    fbm = [(not firstBarOnly) or (al_isFirstBar[i] and dirm[i]) for i in range(n)]

    # =========================================================================
    # FLOOR 2: COMBINATION SIGNALS
    # =========================================================================
    def _bk(sig, off):  # sig[off]
        return _shift_bool(sig, off)

    sigFAUNABull_1 = _bk(sigFAUNABull, 1)
    sigFAUNABear_1 = _bk(sigFAUNABear, 1)
    sigDISPBull_1 = _bk(sigDISPBull, 1)        # noqa: F841
    sigDISPBear_1 = _bk(sigDISPBear, 1)        # noqa: F841
    al_FAUNABull_1 = _bk(al_FAUNABull, 1)
    al_FAUNABear_1 = _bk(al_FAUNABear, 1)
    al_PUP_1 = _bk(al_PUP, 1)
    al_PPD_1 = _bk(al_PPD, 1)
    sigDISPBull_pup_1 = _bk(sigDISPBull_pup, 1)
    sigDISPBear_pup_1 = _bk(sigDISPBear_pup, 1)
    sigDISPBull_1b = _bk(sigDISPBull, 1)
    sigDISPBear_1b = _bk(sigDISPBear, 1)

    sigDoubleDispBull = [sigDISPBull[i] and al_FAUNABull[i] and sigDISPBull_1b[i] and al_FAUNABull_1[i] and (al_PUP[i] or al_anyBullPBJ[i]) for i in range(n)]
    sigDoubleDispBear = [sigDISPBear[i] and al_FAUNABear[i] and sigDISPBear_1b[i] and al_FAUNABear_1[i] and (al_PPD[i] or al_anyBearPBJ[i]) for i in range(n)]

    sigPUPCombo = [conf[i] and sigDISPBull_pup[i] and al_FAUNABull[i] and al_PUP[i] and sigDISPBull_pup_1[i] and al_FAUNABull_1[i] and al_PUP_1[i] for i in range(n)]
    sigPPDCombo = [conf[i] and sigDISPBear_pup[i] and al_FAUNABear[i] and al_PPD[i] and sigDISPBear_pup_1[i] and al_FAUNABear_1[i] and al_PPD_1[i] for i in range(n)]

    sigFullStackBull = [al_anyBullRVOL[i] and al_FAUNABull[i] and sigDISPBull[i] and al_anyBullPBJ[i] for i in range(n)]
    sigFullStackBear = [al_anyBearRVOL[i] and al_FAUNABear[i] and sigDISPBear[i] and al_anyBearPBJ[i] for i in range(n)]

    sigFVGStackBull = [al_anyBullRVOL[i] and al_FAUNABull[i] and sigDISPBull[i] and gz_bullHV[i] and gz_bullGZI[i] for i in range(n)]
    sigFVGStackBear = [al_anyBearRVOL[i] and al_FAUNABear[i] and sigDISPBear[i] and gz_bearHV[i] and gz_bearGZI[i] for i in range(n)]

    sigSuperBullPBJ = [conf[i] and sigDISPBull[i] and al_anyBullPBJ[i] and al_FAUNABull[i] and al_anyBullRVOL[i] for i in range(n)]
    sigSuperBullPB = [conf[i] and sigDISPBull[i] and al_BullPB[i] and al_FAUNABull[i] and al_anyBullRVOL[i] for i in range(n)]
    sigSuperBearPBJ = [conf[i] and sigDISPBear[i] and al_anyBearPBJ[i] and al_FAUNABear[i] and al_anyBearRVOL[i] for i in range(n)]
    sigSuperBearPB = [conf[i] and sigDISPBear[i] and al_BearPB[i] and al_FAUNABear[i] and al_anyBearRVOL[i] for i in range(n)]
    sigAnySuperBull = [sigSuperBullPBJ[i] or sigSuperBullPB[i] for i in range(n)]
    sigAnySuperBear = [sigSuperBearPBJ[i] or sigSuperBearPB[i] for i in range(n)]

    sigMusashiBull = [conf[i] and (gz_bullGZI[i] or gz_bullHV[i]) and al_PUP[i] and al_WhaleBull[i] and al_anyBullPBJ[i] for i in range(n)]
    sigMusashiBear = [conf[i] and (gz_bearGZI[i] or gz_bearHV[i]) and al_PPD[i] and al_WhaleBear[i] and al_anyBearPBJ[i] for i in range(n)]

    # SAAB2 / KRATOS2
    reqc = P["saab2_reqConfirm"]
    sigSAAB_1 = _bk(sigSAAB, 1)
    sigBullRVOL1x_1 = _bk(sigBullRVOL1x, 1)
    sigGrandSlam_1 = _bk(sigGrandSlam, 1)
    sigPUP_1 = _bk(sigPUP, 1)
    anyBullPBJ_1 = _bk(anyBullPBJ, 1)
    gz_bullHV_1 = _bk(gz_bullHV, 1)
    gz_bullGZI_1 = _bk(gz_bullGZI, 1)
    saab2_b1_rvol = [sigSAAB_1[i] or sigBullRVOL1x_1[i] or sigGrandSlam_1[i] for i in range(n)]
    saab2_b2_rvol = [sigSAAB[i] or sigBullRVOL1x[i] or sigGrandSlam[i] for i in range(n)]
    saab2_b1_qual = [(not reqc) or (sigFAUNABull_1[i] or sigDISPBull_1[i] or sigPUP_1[i] or gz_bullHV_1[i] or gz_bullGZI_1[i]) for i in range(n)]
    saab2_b2_qual = [(not reqc) or (sigFAUNABull[i] or sigDISPBull[i] or sigPUP[i] or gz_bullHV[i] or gz_bullGZI[i]) for i in range(n)]
    saab2_pp_pbj = [sigPUP[i] or sigPUP_1[i] or anyBullPBJ[i] or anyBullPBJ_1[i] for i in range(n)]
    sigSAABSq = [conf[i] and saab2_b1_rvol[i] and saab2_b2_rvol[i] and saab2_b1_qual[i] and saab2_b2_qual[i] and saab2_pp_pbj[i] for i in range(n)]

    sigKratos_1 = _bk(sigKratos, 1)
    sigBearRVOL1x_1 = _bk(sigBearRVOL1x, 1)
    sigMOAB_1 = _bk(sigMOAB, 1)
    sigPPD_1 = _bk(sigPPD, 1)
    anyBearPBJ_1 = _bk(anyBearPBJ, 1)
    gz_bearHV_1 = _bk(gz_bearHV, 1)
    gz_bearGZI_1 = _bk(gz_bearGZI, 1)
    krat2_b1_rvol = [sigKratos_1[i] or sigBearRVOL1x_1[i] or sigMOAB_1[i] for i in range(n)]
    krat2_b2_rvol = [sigKratos[i] or sigBearRVOL1x[i] or sigMOAB[i] for i in range(n)]
    krat2_b1_qual = [(not reqc) or (sigFAUNABear_1[i] or sigDISPBear_1[i] or sigPPD_1[i] or gz_bearHV_1[i] or gz_bearGZI_1[i]) for i in range(n)]
    krat2_b2_qual = [(not reqc) or (sigFAUNABear[i] or sigDISPBear[i] or sigPPD[i] or gz_bearHV[i] or gz_bearGZI[i]) for i in range(n)]
    krat2_pp_pbj = [sigPPD[i] or sigPPD_1[i] or anyBearPBJ[i] or anyBearPBJ_1[i] for i in range(n)]
    sigKRATOSSq = [conf[i] and krat2_b1_rvol[i] and krat2_b2_rvol[i] and krat2_b1_qual[i] and krat2_b2_qual[i] and krat2_pp_pbj[i] for i in range(n)]

    # TYPHOON
    sigPUP_rb = _bk(sigPUP, rb)
    sigWhaleBull_rb = _bk(sigWhaleBull, rb)
    anyBullPBJ_rb = _bk(anyBullPBJ, rb)
    sigPPD_rb = _bk(sigPPD, rb)
    sigWhaleBear_rb = _bk(sigWhaleBear, rb)
    anyBearPBJ_rb = _bk(anyBearPBJ, rb)
    sigFAUNABull_rb = _bk(sigFAUNABull, rb)
    sigFAUNABear_rb = _bk(sigFAUNABear, rb)
    is_new_sess_rb2 = _bk(is_new_sess, rb)
    yy_validLow_now = yy_validLow
    yy_validHigh_now = yy_validHigh
    typh_bull_extra = [sigPUP_rb[i] or (sigWhaleBull_rb[i] and anyBullPBJ_rb[i]) for i in range(n)]
    typh_bear_extra = [sigPPD_rb[i] or (sigWhaleBear_rb[i] and anyBearPBJ_rb[i]) for i in range(n)]
    sigTyphoonBull = [conf[i] and yy_validLow_now[i] and is_new_sess_rb2[i] and sigFAUNABull_rb[i] and typh_bull_extra[i] for i in range(n)]
    sigTyphoonBear = [conf[i] and yy_validHigh_now[i] and is_new_sess_rb2[i] and sigFAUNABear_rb[i] and typh_bear_extra[i] for i in range(n)]

    # TOMCAT
    tom_bull_cnt = [(1 if sigPUP[i] else 0) + (1 if sigWhaleBull[i] else 0) + (1 if anyBullPBJ[i] else 0) for i in range(n)]
    tom_bear_cnt = [(1 if sigPPD[i] else 0) + (1 if sigWhaleBear[i] else 0) + (1 if anyBearPBJ[i] else 0) for i in range(n)]
    sigTomcatBull = [conf[i] and is_new_sess[i] and sigFAUNABull[i] and sigDISPBull[i] and tom_bull_cnt[i] >= 2 for i in range(n)]
    sigTomcatBear = [conf[i] and is_new_sess[i] and sigFAUNABear[i] and sigDISPBear[i] and tom_bear_cnt[i] >= 2 for i in range(n)]

    # PAF
    sigPAFBull = [conf[i] and sigPUP[i] and sigFAUNABull[i] and sigPUP_1[i] and sigFAUNABull_1[i] for i in range(n)]
    sigPAFBear = [conf[i] and sigPPD[i] and sigFAUNABear[i] and sigPPD_1[i] and sigFAUNABear_1[i] for i in range(n)]

    # =========================================================================
    # FAUNA+ DISPLACEMENT DENSITY ENGINE
    # =========================================================================
    def _fp_disp(range_type, mult, is_bull):
        cr = [abs(o[i] - c[i]) if range_type == "Open to Close" else (h[i] - l[i]) for i in range(n)]
        sv = _stdev(cr, 100)
        thr = [None if sv[i] is None else sv[i] * mult for i in range(n)]
        out = [False] * n
        for i in range(n):
            prev_disp = i > 0 and thr[i - 1] is not None and cr[i - 1] > thr[i - 1]
            if is_bull:
                fvg = i >= 2 and l[i] > h[i - 2] and o[i - 1] < c[i - 1]
            else:
                fvg = i >= 2 and h[i] < l[i - 2] and o[i - 1] > c[i - 1]
            out[i] = conf[i] and fvg and prev_disp
        return out

    fp_al_fauna_bull = _bk(sigFAUNABull, 1)
    fp_al_fauna_bear = _bk(sigFAUNABear, 1)
    fp_al_PUP = _bk(sigPUP, 1)
    fp_al_PPD = _bk(sigPPD, 1)
    fp_hvgz_bull = [gz_bullHV[i] or gz_bullGZI[i] for i in range(n)]
    fp_hvgz_bear = [gz_bearHV[i] or gz_bearGZI[i] for i in range(n)]

    def _fp_set(prefix, show_key):
        rng_t = P[f"fp_{prefix}_rng"]
        mult = P[f"fp_{prefix}_mult"]
        req = P[f"fp_{prefix}_req"]
        win = P[f"fp_{prefix}_win"]
        fb = P[f"fp_{prefix}_fb"]
        fauna_rq = P[f"fp_{prefix}_fauna_rq"]
        pp_rq = P[f"fp_{prefix}_pp_rq"]
        fvg_rq = P[f"fp_{prefix}_fvg_rq"]
        raw_bull = _fp_disp(rng_t, mult, True)
        raw_bear = _fp_disp(rng_t, mult, False)
        # session chain w/ 1-bar grace
        chain = [False] * n
        ch = False
        grace = 0
        for i in range(n):
            if conf[i]:
                if is_new_sess[i]:
                    ch = True
                    grace = 1
                if ch and not (raw_bull[i] or raw_bear[i]):
                    if grace > 0:
                        grace -= 1
                    else:
                        ch = False
            chain[i] = ch
        bull_sig = [(chain[i] and raw_bull[i]) if fb else raw_bull[i] for i in range(n)]
        bear_sig = [(chain[i] and raw_bear[i]) if fb else raw_bear[i] for i in range(n)]
        show = P[show_key]
        sig_bull = [False] * n
        sig_bear = [False] * n
        for i in range(n):
            ok_bull = (conf[i] and show and _count_back(bull_sig, i, win) >= req
                       and (fauna_rq == 0 or _count_back(fp_al_fauna_bull, i, win) >= fauna_rq)
                       and (pp_rq == 0 or _count_back(fp_al_PUP, i, win) >= pp_rq)
                       and (fvg_rq == 0 or _count_back(fp_hvgz_bull, i, win) >= fvg_rq))
            ok_bear = (conf[i] and show and _count_back(bear_sig, i, win) >= req
                       and (fauna_rq == 0 or _count_back(fp_al_fauna_bear, i, win) >= fauna_rq)
                       and (pp_rq == 0 or _count_back(fp_al_PPD, i, win) >= pp_rq)
                       and (fvg_rq == 0 or _count_back(fp_hvgz_bear, i, win) >= fvg_rq))
            sig_bull[i] = ok_bull
            sig_bear[i] = ok_bear
        return sig_bull, sig_bear, raw_bull, raw_bear

    a_bull, a_bear, a_raw_b, a_raw_r = _fp_set("a", "show_Alpha")
    b_bull, b_bear, b_raw_b, b_raw_r = _fp_set("b", "show_Bravo")
    c_bull, c_bear, c_raw_b, c_raw_r = _fp_set("c", "show_Charlie")
    d_bull, d_bear, d_raw_b, d_raw_r = _fp_set("d", "show_Delta")
    e_bull, e_bear, e_raw_b, e_raw_r = _fp_set("e", "show_Echo")

    # FOXTROT (Fauna 4-in-4)
    sf = P["show_Foxtrot"]
    sigFoxtrotBull = [conf[i] and sf and sigFAUNABull[i] and _bk(sigFAUNABull, 1)[i] and _bk(sigFAUNABull, 2)[i] and _bk(sigFAUNABull, 3)[i] for i in range(n)]
    sigFoxtrotBear = [conf[i] and sf and sigFAUNABear[i] and _bk(sigFAUNABear, 1)[i] and _bk(sigFAUNABear, 2)[i] and _bk(sigFAUNABear, 3)[i] for i in range(n)]

    # GOLF (PUP2 / PPD2)
    sA = P["show_Alpha"]; sB = P["show_Bravo"]; sC = P["show_Charlie"]; sD = P["show_Delta"]; sE = P["show_Echo"]
    fp_any_raw_bull = [(sA and a_raw_b[i]) or (sB and b_raw_b[i]) or (sC and c_raw_b[i]) or (sD and d_raw_b[i]) or (sE and e_raw_b[i]) for i in range(n)]
    fp_any_raw_bear = [(sA and a_raw_r[i]) or (sB and b_raw_r[i]) or (sC and c_raw_r[i]) or (sD and d_raw_r[i]) or (sE and e_raw_r[i]) for i in range(n)]
    fp_any_raw_bull_1 = _bk(fp_any_raw_bull, 1)
    fp_any_raw_bear_1 = _bk(fp_any_raw_bear, 1)
    fp_al_fauna_bull_1 = _bk(fp_al_fauna_bull, 1)
    fp_al_fauna_bear_1 = _bk(fp_al_fauna_bear, 1)
    fp_al_PUP_1 = _bk(fp_al_PUP, 1)
    fp_al_PPD_1 = _bk(fp_al_PPD, 1)
    sg = P["show_Golf"]
    sigGolfBull = [conf[i] and sg and fp_any_raw_bull[i] and fp_al_fauna_bull[i] and fp_al_PUP[i] and fp_any_raw_bull_1[i] and fp_al_fauna_bull_1[i] and fp_al_PUP_1[i] for i in range(n)]
    sigGolfBear = [conf[i] and sg and fp_any_raw_bear[i] and fp_al_fauna_bear[i] and fp_al_PPD[i] and fp_any_raw_bear_1[i] and fp_al_fauna_bear_1[i] and fp_al_PPD_1[i] for i in range(n)]

    # OPENING DRIVE
    od_cr = [abs(o[i] - c[i]) if P["od_rng"] == "Open to Close" else (h[i] - l[i]) for i in range(n)]
    od_std = _stdev(od_cr, 100)
    od_thr = [None if od_std[i] is None else od_std[i] * P["od_mult"] for i in range(n)]
    od_prev_disp = [i > 0 and od_thr[i - 1] is not None and od_cr[i - 1] > od_thr[i - 1] for i in range(n)]
    od_bull_fvg = [i >= 2 and l[i] > h[i - 2] and o[i - 1] < c[i - 1] for i in range(n)]
    od_bear_fvg = [i >= 2 and h[i] < l[i - 2] and o[i - 1] > c[i - 1] for i in range(n)]
    sod = P["show_OD"]
    sigODBull = [conf[i] and sod and sessionBarCount[i] <= P["od_max"] and od_bull_fvg[i] and od_prev_disp[i] and pp_priceUp[i] and pp_volBull[i] for i in range(n)]
    sigODBear = [conf[i] and sod and sessionBarCount[i] <= P["od_max"] and od_bear_fvg[i] and od_prev_disp[i] and pp_priceDn[i] and pp_volBear[i] for i in range(n)]

    # FAUNA+ combined
    anyAFBull = [a_bull[i] or b_bull[i] or c_bull[i] or d_bull[i] or e_bull[i] or sigFoxtrotBull[i] for i in range(n)]
    anyAFBear = [a_bear[i] or b_bear[i] or c_bear[i] or d_bear[i] or e_bear[i] or sigFoxtrotBear[i] for i in range(n)]

    # =========================================================================
    # FLOOR 3: KATANA (session)
    # =========================================================================
    last_close = 0.0
    kat_yest = dict(bull_hv=False, bear_hv=False, bull_gzi=False, bear_gzi=False,
                    bull_fauna=False, bear_fauna=False, bull_bo=False, bear_bd=False, hv=False)
    sigKatanaBull = [False] * n
    sigKatanaBear = [False] * n
    is_new_sess_1 = _bk(is_new_sess, 1)
    sigFAUNABull_1k = _bk(sigFAUNABull, 1)
    sigFAUNABear_1k = _bk(sigFAUNABear, 1)
    yy_breakout_1 = _bk(yy_breakout, 1)
    yy_breakdown_1 = _bk(yy_breakdown, 1)
    sigHV_1 = _bk(sigHV, 1)              # noqa: F841 (parity w/ source state capture)
    anyBullPBJ_1k = _bk(anyBullPBJ, 1)
    anyBearPBJ_1k = _bk(anyBearPBJ, 1)
    sigPUP_1k = _bk(sigPUP, 1)
    sigPPD_1k = _bk(sigPPD, 1)
    for i in range(n):
        if is_new_sess[i]:
            last_close = c[i - 1] if i > 0 else c[i]
            kat_yest = dict(
                bull_hv=gz_bullHV[i], bear_hv=gz_bearHV[i],
                bull_gzi=gz_bullGZI[i], bear_gzi=gz_bearGZI[i],
                bull_fauna=sigFAUNABull_1k[i], bear_fauna=sigFAUNABear_1k[i],
                bull_bo=yy_breakout_1[i], bear_bd=yy_breakdown_1[i],
                hv=sigHV_1[i],
            )
        prevc = c[i - 1] if i > 0 else c[i]
        prevo = o[i - 1] if i > 0 else o[i]
        kat_dir_bull = prevc > last_close and prevc > prevo
        kat_dir_bear = prevc < last_close and prevc < prevo
        A_b = conf[i] and is_new_sess_1[i] and kat_yest["bull_hv"] and kat_yest["bull_fauna"] and gz_bullHV[i] and gz_bullGZI[i] and sigFAUNABull_1k[i] and kat_dir_bull
        A_r = conf[i] and is_new_sess_1[i] and kat_yest["bear_hv"] and kat_yest["bear_fauna"] and gz_bearHV[i] and gz_bearGZI[i] and sigFAUNABear_1k[i] and kat_dir_bear
        B_b = conf[i] and is_new_sess_1[i] and kat_yest["bull_fauna"] and (kat_yest["bull_hv"] or kat_yest["bull_gzi"] or kat_yest["bull_bo"]) and gz_bullGZI[i] and sigFAUNABull_1k[i] and kat_dir_bull
        B_r = conf[i] and is_new_sess_1[i] and kat_yest["bear_fauna"] and (kat_yest["bear_hv"] or kat_yest["bear_gzi"] or kat_yest["bear_bd"]) and gz_bearGZI[i] and sigFAUNABear_1k[i] and kat_dir_bear
        E_b = conf[i] and is_new_sess_1[i] and kat_yest["bull_hv"] and kat_yest["bull_fauna"] and sigPUP_1k[i] and gz_bullHV[i] and gz_bullGZI[i] and sigFAUNABull_1k[i] and kat_dir_bull
        E_r = conf[i] and is_new_sess_1[i] and kat_yest["bear_hv"] and kat_yest["bear_fauna"] and sigPPD_1k[i] and gz_bearHV[i] and gz_bearGZI[i] and sigFAUNABear_1k[i] and kat_dir_bear
        rawBull = A_b or B_b or E_b
        rawBear = A_r or B_r or E_r
        sigKatanaBull[i] = rawBull and (anyBullPBJ_1k[i] or sigPUP_1k[i])
        sigKatanaBear[i] = rawBear and (anyBearPBJ_1k[i] or sigPPD_1k[i])

    # =========================================================================
    # NAGASAKI DIRECTIONAL + special gate
    # =========================================================================
    nag_dir_bull = [sigBullRVOL1x[i] or sigGrandSlam[i] or sigFAUNABull[i] or sigDISPBull[i] or anyBullPBJ[i] or sigPUP[i] or sigWhaleBull[i] or gz_bullHV[i] or gz_bullGZI[i] or sigPAFBull[i] for i in range(n)]
    nag_dir_bear = [sigBearRVOL1x[i] or sigMOAB[i] or sigFAUNABear[i] or sigDISPBear[i] or anyBearPBJ[i] or sigPPD[i] or sigWhaleBear[i] or gz_bearHV[i] or gz_bearGZI[i] or sigPAFBear[i] for i in range(n)]
    sigNagasakiBull = [conf[i] and sigNagasaki[i] and nag_dir_bull[i] for i in range(n)]
    sigNagasakiBear = [conf[i] and sigNagasaki[i] and nag_dir_bear[i] for i in range(n)]
    # Each term gated by its show_ toggle so a DISABLED signal cannot leak an alert through
    # Nagasaki's pass — Nagasaki stays the only signal allowed to fire when its box is off.
    nag_special_bull = [(P["show_TyphoonBull"] and sigTyphoonBull[i]) or (P["show_WhaleBull"] and sigWhaleBull[i]) or (P["show_SuperBull"] and sigAnySuperBull[i]) or (P["show_Golf"] and sigGolfBull[i]) or (P["show_TomcatBull"] and sigTomcatBull[i]) or (P["show_FullStack"] and sigFullStackBull[i]) or (P["show_FVGStack"] and sigFVGStackBull[i]) for i in range(n)]
    nag_special_bear = [(P["show_TyphoonBear"] and sigTyphoonBear[i]) or (P["show_WhaleBear"] and sigWhaleBear[i]) or (P["show_SuperBear"] and sigAnySuperBear[i]) or (P["show_Golf"] and sigGolfBear[i]) or (P["show_TomcatBear"] and sigTomcatBear[i]) or (P["show_FullStack"] and sigFullStackBear[i]) or (P["show_FVGStack"] and sigFVGStackBear[i]) for i in range(n)]
    nag_gate_bull = [P["show_Nagasaki"] or nag_special_bull[i] for i in range(n)]
    nag_gate_bear = [P["show_Nagasaki"] or nag_special_bear[i] for i in range(n)]

    # =========================================================================
    # ROOF: 33 detection plots' gating booleans (exact plotshape conditions)
    # =========================================================================
    fires: dict[str, list[int]] = {}
    levels: dict[str, list] = {}

    def _put(pid, bool_series, level_kind="bool"):
        f = [1 if bool_series[i] else 0 for i in range(n)]
        fires[pid] = f
        if level_kind == "rvol":
            levels[pid] = [bb_normPrice[i] if bool_series[i] else 0.0 for i in range(n)]
        else:
            levels[pid] = list(f)

    sSuperBull = P["show_SuperBull"]; sSuperBear = P["show_SuperBear"]
    _put("Super", [(sSuperBull and sigAnySuperBull[i] and fbm[i]) or (sSuperBear and sigAnySuperBear[i] and fbm[i]) for i in range(n)])
    _put("Grand Slam", [P["show_GrandSlam"] and sigGrandSlam[i] and fb0[i] for i in range(n)], "rvol")
    _put("MOAB", [P["show_MOAB"] and sigMOAB[i] and fb0[i] for i in range(n)], "rvol")
    _put("Whale+PUP", [P["show_WhaleBull"] and sigWhaleBull[i] for i in range(n)])
    _put("Whale+PPD", [P["show_WhaleBear"] and sigWhaleBear[i] for i in range(n)])
    _put("SAAB2", [P["show_SAABSq"] and sigSAABSq[i] for i in range(n)])
    _put("KRATOS2", [P["show_KRATOSSq"] and sigKRATOSSq[i] for i in range(n)])
    _put("Typhoon Bull", [P["show_TyphoonBull"] and sigTyphoonBull[i] and fbs[i] for i in range(n)])
    _put("Typhoon Bear", [P["show_TyphoonBear"] and sigTyphoonBear[i] and fbs[i] for i in range(n)])
    _put("Tomcat Bull", [P["show_TomcatBull"] and sigTomcatBull[i] and fb0[i] for i in range(n)])
    _put("Tomcat Bear", [P["show_TomcatBear"] and sigTomcatBear[i] and fb0[i] for i in range(n)])
    _put("Nagasaki Bull", [nag_gate_bull[i] and sigNagasakiBull[i] for i in range(n)])
    _put("Nagasaki Bear", [nag_gate_bear[i] and sigNagasakiBear[i] for i in range(n)])
    _put("PAF PUP B2B", [P["show_PAFBull"] and sigPAFBull[i] for i in range(n)])
    _put("PAF PPD B2B", [P["show_PAFBear"] and sigPAFBear[i] for i in range(n)])
    _put("FAUNA+ Bull", list(anyAFBull))
    _put("FAUNA+ Bear", list(anyAFBear))
    _put("Golf Bull", list(sigGolfBull))
    _put("Golf Bear", list(sigGolfBear))
    _put("Opening Drive Bull", list(sigODBull))
    _put("Opening Drive Bear", list(sigODBear))
    _put("Katana Bull", [P["show_Katana"] and sigKatanaBull[i] for i in range(n)])
    _put("Katana Bear", [P["show_Katana"] and sigKatanaBear[i] for i in range(n)])
    _put("Musashi Bull", [P["show_Musashi"] and sigMusashiBull[i] and fbm[i] for i in range(n)])
    _put("Musashi Bear", [P["show_Musashi"] and sigMusashiBear[i] and fbm[i] for i in range(n)])
    _put("Double Disp Bull", [P["show_DoubleDisp"] and sigDoubleDispBull[i] for i in range(n)])
    _put("Double Disp Bear", [P["show_DoubleDisp"] and sigDoubleDispBear[i] for i in range(n)])
    _put("PUP Combo", [P["show_PUP"] and sigPUPCombo[i] for i in range(n)])
    _put("PPD Combo", [P["show_PPD"] and sigPPDCombo[i] for i in range(n)])
    _put("Full Stack Bull", [P["show_FullStack"] and sigFullStackBull[i] and fbm[i] for i in range(n)])
    _put("Full Stack Bear", [P["show_FullStack"] and sigFullStackBear[i] and fbm[i] for i in range(n)])
    _put("FVG Stack Bull", [P["show_FVGStack"] and sigFVGStackBull[i] and fbm[i] for i in range(n)])
    _put("FVG Stack Bear", [P["show_FVGStack"] and sigFVGStackBear[i] and fbm[i] for i in range(n)])

    return fires, levels, ts


# =============================================================================
# PUBLIC API  (the contract the grain-binders + parity harness call)
# =============================================================================
def _merge_params(params):
    P = dict(DEFAULTS)
    if params:
        for k, val in params.items():
            P[k] = val
    return P


def compute(bars, params=None, *, tf_seconds=TICK_FALLBACK_SEC):
    """Run the shared detection core. Returns a dict:
        fires        : {plot_id: [0/1 per bar]}
        levels       : {plot_id: [float|0.0 per bar]}
        plot_ids     : ordered list of the 33 plot ids
        n            : number of bars
        stub_partial : [] (FULL faithful port -- no plot is stubbed)
        ts           : bar open timestamps
    """
    P = _merge_params(params)
    bars = list(bars)
    fires, levels, ts = _compute_all(bars, P, tf_seconds)
    return {
        "fires": fires,
        "levels": levels,
        "plot_ids": list(PLOT_IDS),
        "n": len(bars),
        "stub_partial": list(STUB_PARTIAL),
        "ts": ts,
    }


def compute_fires_bool(bars, params=None, *, tf_seconds=TICK_FALLBACK_SEC):
    """Same as compute() but fires are Python bools (convenience for callers)."""
    res = compute(bars, params=params, tf_seconds=tf_seconds)
    res["fires"] = {k: [bool(x) for x in v] for k, v in res["fires"].items()}
    return res


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _nn_harness as _H  # type: ignore  # noqa: E402

    _bars = _H.load_bars(grain="time", n=900)
    _r = compute(_bars, params={"reg_length": 30}, tf_seconds=3600)
    _fired = sum(1 for k in _r["plot_ids"] if sum(_r["fires"][k]) > 0)
    print(f"1st PUP FAUNA CORE -- {_r['n']} bars, {len(_r['plot_ids'])} plots, "
          f"{_fired} fired, {len(_r['stub_partial'])} stubbed")
    for _k in _r["plot_ids"]:
        _cnt = sum(_r["fires"][_k])
        if _cnt:
            print(f"  {_k:22s} {_cnt}")
