"""
Python port of ULTRA_COMBO_v57_pine6.pine (1147 lines).

Source Pine:  ultra-combo/versions/ULTRA_COMBO_v57_pine6.pine
Sibling v5:   ultra-combo/versions/ULTRA_COMBO_v57_pine5.pine
              (1:1 logic per ultra-combo/CHANGELOG.md — only pine6 is ported).

Re-implements every detection plot, alertcondition composite, and root
operand in Ultra Combo as a vectorized pandas function suitable for
replaying against a bar-history DataFrame.

Conventions (mirror python_ports/hvd_pbj_ppd/the_only_one.py):
  - df is expected to have columns: open, high, low, close, volume.
    Index should be a monotonic int (bar index) or DatetimeIndex; bar
    order must be ascending.
  - Each detection function returns a pd.Series[bool] aligned to df.index.
  - IPSF (input.*) parameters live in DEFAULTS and may be overridden via
    the ``params`` dict passed to every detection. (SD-003: IPSF defaults
    preserved verbatim from the Pine source.)
  - Hardcoded Pine constants (NOT input.*) stay hardcoded here so future
    edits do not silently introduce drift.
  - Stateful detections (Supertrend dir, PBJ landing-zone arrays, GZ1 FVG
    array, TB/Foster windows, b1/b4 cluster overlap, Nagasaki streaming
    ATH, anti-armed PUP/PPD trackers) are wrapped in classes in
    STATE_MACHINES.
  - Detections that require Pine-only intrinsics
    (request.security multi-TF, tv_ta.relativeVolume) are STUBBED and
    registered in STUBBED. Caller may inject precomputed series via
    df.attrs.

Standing decisions:
  - SD-001 (Pentagon always included) — Ultra Combo does not reference
    csNew3 / FVG-side Matrix / cs_inc_pentagon_* gates. No-op here, but
    documented for traceability.
  - SD-003 (IPSF defaults are not drift) — every input.* default from
    the Pine source is preserved verbatim in DEFAULTS.

This module is import-only safe; it does NOT contain tests. The harness
runs validation tests separately.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd


# ============================================================================
# IPSF DEFAULTS — mirror Pine input.* defaults exactly. SD-003 applied.
# Ultra Combo's only input.* are 36 show_* toggles (lines 28-77 of source);
# every threshold/length/window is a hardcoded constant in the Pine.
# ============================================================================
DEFAULTS: Dict = {
    # Group: PBJ/PB + F2/E3/CLUSTER
    "show_pbjF2": True, "show_pbjE3": True, "show_pbjCluster": True,
    "show_pbF2": True, "show_pbE3": True, "show_pbCluster": True,
    # Group: SEQUENTIAL COMBOS
    "show_f2ClusterE3": True, "show_f2ClusterB2B": True,
    "show_b2bF2": True, "show_e3PUP": True,
    # Group: CONSECUTIVE DAY COMBOS
    "show_f2B2B": True, "show_e3B2B": True,
    "show_f2e3Consec": True, "show_clusterB2BDays": True,
    # Group: HEAVY WEAPON + F2/E3
    "show_hwBullAny": True, "show_hwBearAny": True,
    # Group: GZ1/HV + F2/E3
    "show_gzHvAny": True, "show_hvGziCombo": True,
    # Group: MEGA COMBOS
    "show_gzHvMega": True, "show_gz1hvMegaCombo": True,
    # Group: FIRST CANDLE OPENER
    "show_openerBull": True, "show_openerBear": True,
    # Group: 3-BAR WINDOW
    "show_3barBull": True, "show_3barBear": True,
    # Group: FOSTER/TB + HEAVY
    "show_fosterHeavyBull": True, "show_tbHeavyBear": True,
    # Group: GZ1/HV + HEAVY
    "show_gzHvHeavyBull": True, "show_gzHvHeavyBear": True,
    # Group: SUPER COMBO B2B DAYS
    "show_superB2BDays": True,
    # Bar timeframe in seconds (caller supplies; defaults to 60s = 1-min)
    "tfSec": 60,
    # Session window for inSession; Ultra Combo hardcodes "0930-1600"
    # America/New_York. Caller may inject `inSession` via df.attrs.
    "session": "0930-1600",
    "session_tz": "America/New_York",
}


# ============================================================================
# _helpers — utilities used by many detections
# ============================================================================
def _p(params: Optional[Dict]) -> Dict:
    """Merge user params over DEFAULTS, returning a fresh dict."""
    out = dict(DEFAULTS)
    if params:
        out.update(params)
    return out


def _stdev(s: pd.Series, length: int) -> pd.Series:
    """Pine ta.stdev — population stdev (ddof=0) over rolling window."""
    return s.rolling(length, min_periods=length).std(ddof=0)


def _highest(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=1).max()


def _lowest(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=1).min()


def _sma(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=length).mean()


def _ema(s: pd.Series, length: int) -> pd.Series:
    return s.ewm(span=length, adjust=False, min_periods=length).mean()


def _atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([(h - l), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    # Pine ta.atr uses Wilder's RMA = EMA with alpha=1/length
    return tr.ewm(alpha=1.0 / length, adjust=False, min_periods=length).mean()


def _nz_b(s: pd.Series) -> pd.Series:
    """Pine nz(boolSeries) — replace NaN with False, return bool series."""
    return s.fillna(False).astype(bool)


def _nz_f(s: pd.Series, fill: float = 0.0) -> pd.Series:
    """Pine nz(floatSeries[, fill])."""
    return s.fillna(fill)


def _conf(df: pd.DataFrame) -> pd.Series:
    """Pine ``barstate.isconfirmed`` — True everywhere for historical bars."""
    return pd.Series(True, index=df.index)


# RVOL threshold tables (Ultra Combo source lines 308-320).
# NB: these differ from heavy-pentagon — Ultra Combo bakes its own scale.
def _rvol_1x(tfsec: float) -> float:
    s = tfsec
    if s <= 10:    return 38.0
    if s <= 15:    return 33.0
    if s <= 30:    return 28.0
    if s <= 45:    return 23.0
    if s <= 60:    return 20.0
    if s <= 120:   return 18.0
    if s <= 300:   return 13.0
    if s <= 360:   return 12.0
    if s <= 540:   return 10.0
    if s <= 600:   return 9.0
    if s <= 660:   return 8.0
    if s <= 900:   return 7.0
    if s <= 1560:  return 6.0
    if s <= 2340:  return 4.5
    if s <= 3600:  return 3.5
    if s <= 9000:  return 3.5
    if s <= 11700: return 2.5
    if s < 259200: return 1.8
    return 1.0


def _gs_moab(tfsec: float) -> float:
    s = tfsec
    day = 86400.0
    if s < 60:        return _rvol_1x(s) * 3.0
    if s <= 300:      return 35.0
    if s <= 600:      return 25.0
    if s <= 1500:     return 20.0
    if s <= 3060:     return 20.0
    if s <= 7260:     return 10.0
    if s <= 11700:    return 8.0
    if s <= day:      return 8.0
    if s <= 3.0 * day: return 3.5
    return 3.0


def _hiroshima(tfsec: float) -> float:
    s = tfsec
    day = 86400.0
    if s < 60:        return _rvol_1x(s) * 3.0
    if s <= 300:      return 35.0
    if s <= 600:      return 25.0
    if s <= 1500:     return 25.0
    if s <= 3060:     return 20.0
    if s <= 7260:     return 10.0
    if s <= 11700:    return 8.0
    if s <= day:      return 8.0
    if s <= 3.0 * day: return 3.5
    return 3.0


def _wtc(tfsec: float) -> float:
    # Source line 324: th_wtc = f_rvol_1x_threshold(tfSec) — same as th_1x
    return _rvol_1x(tfsec)


def _attr_or_false(df: pd.DataFrame, name: str) -> pd.Series:
    s = df.attrs.get(name)
    if s is None:
        return pd.Series(False, index=df.index)
    return s.reindex(df.index).fillna(False).astype(bool)


def _attr_or_nan(df: pd.DataFrame, name: str) -> pd.Series:
    s = df.attrs.get(name)
    if s is None:
        return pd.Series(np.nan, index=df.index)
    return s.reindex(df.index)


def _streak(series: pd.Series) -> pd.Series:
    a = series.fillna(False).to_numpy()
    out = np.zeros(len(a), dtype=int)
    c = 0
    for i, v in enumerate(a):
        c = c + 1 if v else 0
        out[i] = c
    return pd.Series(out, index=series.index)


def _streak_resetday(qual: pd.Series, day_change: pd.Series) -> pd.Series:
    """Pine streak that resets when ta.change(dayofmonth) != 0 (used by b1_s2/b4_s2)."""
    q = qual.fillna(False).to_numpy()
    d = day_change.fillna(False).to_numpy()
    out = np.zeros(len(q), dtype=int)
    c = 0
    for i in range(len(q)):
        # Pine semantics in source:
        #   if change(dayofmonth) != 0 -> s := 0
        #   else if not ev -> s := 0
        #   if ev -> s += 1
        if d[i]:
            c = 0
        elif not q[i]:
            c = 0
        if q[i]:
            c += 1
        out[i] = c
    return pd.Series(out, index=qual.index)


# ============================================================================
# _engines — vectorized building blocks. Cache on df.attrs.
# ============================================================================
def _ensure_engines(df: pd.DataFrame, params: Dict) -> Dict[str, pd.Series]:
    cache = df.attrs.setdefault("_ultra_combo_eng", {})
    cache_key = (
        "v57_pine6",
        id(df),
        tuple(sorted((k, v) for k, v in params.items()
                     if isinstance(v, (int, float, str, bool)))),
    )
    if cache.get("_key") == cache_key and "comboPBJ_F2_Bull" in cache:
        return cache
    cache.clear()
    cache["_key"] = cache_key

    p = params
    tfSec = float(p["tfSec"])
    conf = _conf(df)

    o, h, l, c, v = df["open"], df["high"], df["low"], df["close"], df["volume"]

    # ── Session / day change ────────────────────────────────────────────────
    # inSession: caller may inject; otherwise default to True (matches
    # 24/7 chart). Pine uses `time(timeframe.period, "0930-1600", "NY")`.
    inSession = df.attrs.get("inSession")
    if inSession is None:
        inSession = pd.Series(True, index=df.index)
    else:
        inSession = inSession.reindex(df.index).fillna(False).astype(bool)

    # is_new_day: ta.change(dayofmonth) != 0
    is_new_day = df.attrs.get("is_new_day")
    if is_new_day is None:
        if isinstance(df.index, pd.DatetimeIndex):
            day = pd.Series(df.index.day, index=df.index)
            is_new_day = (day != day.shift(1)).fillna(True)
        else:
            tmp = np.zeros(len(df), dtype=bool); tmp[0] = True
            is_new_day = pd.Series(tmp, index=df.index)

    # ── Core shared (Pine lines 82-96) ──────────────────────────────────────
    atr14 = _atr(df, 14)
    avgVol20 = _sma(v, 20)
    avgDelta = _sma((c - c.shift(1)).abs(), 10)
    trendMA = _sma(c, 50)
    body = c - o
    rng = h - l
    bodySize = body.abs()
    bodyRatio = (bodySize / rng.replace(0, np.nan)).fillna(0.0)
    bodyUp = body > 0
    bodyDn = body < 0
    wide = rng > 2.2 * atr14
    upTrend = trendMA > trendMA.shift(1)
    dnTrend = trendMA < trendMA.shift(1)

    # MB / RE / TA (bull and bear) — shared between FC cluster and FAUNA.
    bull_MB = conf & bodyUp & (bodySize > 1.6 * atr14) & (bodyRatio > 0.7) & (v > 1.8 * avgVol20)
    bull_RE = conf & bodyUp & wide & ((h - c) < 0.15 * rng) & (v > 1.8 * avgVol20)
    bull_TA = conf & upTrend & ((c - c.shift(1)) > 1.6 * avgDelta) & bodyUp & (v > 1.8 * avgVol20)
    bear_MB = conf & bodyDn & (bodySize > 1.6 * atr14) & (bodyRatio > 0.7) & (v > 1.8 * avgVol20)
    bear_RE = conf & bodyDn & wide & ((c - l) < 0.15 * rng) & (v > 1.8 * avgVol20)
    bear_TA = conf & dnTrend & ((c.shift(1) - c) > 1.6 * avgDelta) & bodyDn & (v > 1.8 * avgVol20)

    # ── sessBar (Pine 108-119) ──────────────────────────────────────────────
    # Pine logic: on isNewDay & inSession, sessBar:=1; else if inSession &&
    # sessBar>0, sessBar+=1; else if not inSession, sessBar:=0.
    nd_arr = is_new_day.fillna(False).to_numpy()
    is_arr = inSession.to_numpy()
    sb = np.zeros(len(df), dtype=int)
    cur = 0
    new_day_pending = False
    for i in range(len(df)):
        if nd_arr[i]:
            new_day_pending = True
        if new_day_pending and is_arr[i]:
            cur = 1
            new_day_pending = False
        elif is_arr[i] and cur > 0:
            cur += 1
        elif not is_arr[i]:
            cur = 0
        sb[i] = cur
    sessBar = pd.Series(sb, index=df.index)

    # ── F2 / E3 / FC CLUSTER (Pine lines 121-299) ───────────────────────────
    # BULLISH cluster
    b1_s1 = _streak(bull_MB)
    b1_ind1 = bull_MB & (b1_s1 >= 2)

    b1_ev2 = bull_MB | bull_RE | bull_TA
    b1_s2 = _streak_resetday(b1_ev2, is_new_day)
    b1_ind2 = b1_ev2 & (b1_s2 >= 2)

    b1_ev3 = (bull_MB | bull_RE) & inSession
    b1_s3 = _streak(b1_ev3)
    b1_ind3 = b1_ev3 & (b1_s3 >= 2)

    b1_2of3 = ((b1_ind1.astype(int) + b1_ind2.astype(int) + b1_ind3.astype(int)) >= 2)

    # b1 overlap-array engine — stateful, bar-by-bar.
    b1_spk = body.abs()
    b1_avgSpk = _sma(b1_spk, 30).shift(1)
    b1_rvolP = b1_spk / _nz_f(b1_avgSpk, 1.0)
    b1_avgVolD = _sma(v, 30).shift(1)
    b1_rvolV = v / _nz_f(b1_avgVolD, 1.0)
    b1_diff = b1_rvolP - b1_rvolV
    b1_pos = b1_diff.where(b1_diff > 0, np.nan)
    b1_smaP = _sma(b1_pos, 20)
    b1_base = bodyUp & (_nz_f(b1_pos) > _nz_f(b1_smaP))
    b1_inRng = (b1_rvolP > 2.9) & (b1_rvolP < 1_000_000.0)
    b1_thEv = (b1_base & b1_inRng & conf).fillna(False)
    b1_uBar = (b1_base & b1_inRng).fillna(False)

    # b1_seqEv: streak length >= 2 and sum of rvolP >= 0.1
    ub = b1_uBar.to_numpy()
    rp = _nz_f(b1_rvolP).to_numpy()
    seq = np.zeros(len(df), dtype=bool)
    le = 0
    sm = 0.0
    for i in range(len(df)):
        if ub[i]:
            le += 1
            sm += rp[i]
        else:
            le = 0
            sm = 0.0
        seq[i] = (le >= 2 and sm >= 0.1)
    b1_seqEv = pd.Series(seq, index=df.index) & conf

    # Range-overlap engine (b1_ovlp) — explicit bar-by-bar with windowed arrays
    b1_ovlp = _range_overlap_engine(df, b1_thEv, b1_seqEv, window=20)

    sBullFC = conf & b1_2of3 & b1_ovlp
    b2_ev = bull_MB | bull_RE | bull_TA
    sBullE3 = conf & (sessBar == 3) & b2_ev & _nz_b(b2_ev.shift(1)) & _nz_b(b2_ev.shift(2))
    sBullF2 = conf & (sessBar == 2) & bull_MB & _nz_b(bull_MB.shift(1))

    # BEARISH cluster
    b4_s1 = _streak(bear_MB)
    b4_ind1 = bear_MB & (b4_s1 >= 2)
    b4_ev2 = bear_MB | bear_RE | bear_TA
    b4_s2 = _streak_resetday(b4_ev2, is_new_day)
    b4_ind2 = b4_ev2 & (b4_s2 >= 2)
    b4_ev3 = (bear_MB | bear_RE) & inSession
    b4_s3 = _streak(b4_ev3)
    b4_ind3 = b4_ev3 & (b4_s3 >= 2)
    b4_2of3 = ((b4_ind1.astype(int) + b4_ind2.astype(int) + b4_ind3.astype(int)) >= 2)

    b4_spk = body.abs()
    b4_avgSpk = _sma(b4_spk, 30).shift(1)
    b4_rvolP = b4_spk / _nz_f(b4_avgSpk, 1.0)
    b4_avgVolD = _sma(v, 30).shift(1)
    b4_rvolV = v / _nz_f(b4_avgVolD, 1.0)
    b4_diff = b4_rvolP - b4_rvolV
    # Source line 239: b4_neg = (b4_diff > 0 AND bodyDn) ? b4_diff : na
    b4_neg = b4_diff.where((b4_diff > 0) & bodyDn, np.nan)
    b4_smaN = _sma(b4_neg, 20)
    b4_base = bodyDn & (_nz_f(b4_neg) > _nz_f(b4_smaN))
    b4_inRng = (b4_rvolP > 2.9) & (b4_rvolP < 1_000_000.0)
    b4_thEv = (b4_base & b4_inRng & conf).fillna(False)
    b4_dBar = (b4_base & b4_inRng).fillna(False)

    db = b4_dBar.to_numpy()
    rpn = _nz_f(b4_rvolP).to_numpy()
    seq4 = np.zeros(len(df), dtype=bool)
    le = 0; sm = 0.0
    for i in range(len(df)):
        if db[i]:
            le += 1; sm += rpn[i]
        else:
            le = 0; sm = 0.0
        seq4[i] = (le >= 2 and sm >= 0.5)
    b4_seqEv = pd.Series(seq4, index=df.index) & conf

    b4_ovlp = _range_overlap_engine(df, b4_thEv, b4_seqEv, window=20)

    sBearFC = conf & b4_2of3 & b4_ovlp
    b5_ev = bear_MB | bear_RE | bear_TA
    sBearE3 = conf & (sessBar == 3) & b5_ev & _nz_b(b5_ev.shift(1)) & _nz_b(b5_ev.shift(2))
    sBearF2 = conf & (sessBar == 2) & bear_MB & _nz_b(bear_MB.shift(1))

    sAnyBull = sBullFC | sBullE3 | sBullF2
    sAnyBear = sBearFC | sBearE3 | sBearF2

    # ── RVOL / HEAVY WEAPON (Pine 301-364) ─────────────────────────────────
    bb_avgLength = 30
    bb_smaLength = 20
    th_1x = _rvol_1x(tfSec)
    th_gs_moab = _gs_moab(tfSec)
    th_wtc = _wtc(tfSec)
    th_hiroshima = _hiroshima(tfSec)

    bb_spike = (c - o).abs()
    bb_avgSpikeDenom = _sma(bb_spike, bb_avgLength).shift(1)
    bb_normalizedPrice = bb_spike / _nz_f(bb_avgSpikeDenom, 1.0)
    bb_avgVolDenom = _sma(v, bb_avgLength).shift(1)
    bb_normalizedVolume = v / _nz_f(bb_avgVolDenom, 1.0)
    bb_diff = bb_normalizedPrice - bb_normalizedVolume
    bb_positiveDiff = bb_diff.where(bb_diff > 0, np.nan)
    bb_smaDiff = _sma(bb_positiveDiff, bb_smaLength)
    bb_baseBullish = (c > o) & (bb_positiveDiff > bb_smaDiff)
    bb_baseBearish = (c < o) & (bb_positiveDiff > bb_smaDiff)

    sigBullRVOL1x = conf & bb_baseBullish & (bb_normalizedPrice >= th_1x) & (bb_normalizedPrice < th_gs_moab)
    sigBearRVOL1x = conf & bb_baseBearish & (bb_normalizedPrice >= th_1x) & (bb_normalizedPrice < th_gs_moab)
    sigGrandSlam = conf & bb_baseBullish & (bb_normalizedPrice >= th_gs_moab)
    sigMOAB = conf & bb_baseBearish & (bb_normalizedPrice >= th_gs_moab)

    # tv_ta.relativeVolume — STUBBED. Inject relVolRatio via df.attrs.
    relVolRatio = _attr_or_nan(df, "relVolRatio")
    sigWTC = conf & (relVolRatio > th_wtc) & (relVolRatio <= th_hiroshima)
    sigHiroshima = conf & (relVolRatio > th_hiroshima)

    # Nagasaki — streaming ATH (source 357-364). Note: sigNagasaki only True
    # AFTER bar_index==0; bar 0 just seeds maxVol.
    v_arr = v.to_numpy()
    nag_arr = np.zeros(len(df), dtype=bool)
    if len(df) > 0:
        cur_max = v_arr[0] if not (isinstance(v_arr[0], float) and np.isnan(v_arr[0])) else -np.inf
        for i in range(1, len(df)):
            if not (isinstance(v_arr[i], float) and np.isnan(v_arr[i])) and v_arr[i] > cur_max:
                nag_arr[i] = True
                cur_max = v_arr[i]
    sigNagasaki = pd.Series(nag_arr, index=df.index)

    # ── PBJ / PB engine (Pine 366-519) — STUBBED ────────────────────────────
    # Requires Supertrend dir state + landing-zone arrays + reaccel detection
    # (bar-by-bar). Caller must inject pre-computed series via df.attrs:
    #   sigBullPBJ, sigBullPB, sigBearPBJ, sigBearPB
    sigBullPBJ = _attr_or_false(df, "sigBullPBJ")
    sigBullPB = _attr_or_false(df, "sigBullPB")
    sigBearPBJ = _attr_or_false(df, "sigBearPBJ")
    sigBearPB = _attr_or_false(df, "sigBearPB")

    # ── PUP/PPD / Anish Stages (Pine 521-579) ───────────────────────────────
    ema50 = _ema(c, 50)
    ema150 = _ema(c, 150)
    ema200 = _ema(c, 200)
    ema200_1m = ema200.shift(21)
    w52Hi = _highest(h, 252)
    w52Lo = _lowest(l, 252)

    bullPass = (
        (c > ema50) & (c >= ema150) & (c >= ema200) &
        (ema50 > ema150) & (ema50 > ema200) & (ema150 >= ema200) &
        (ema200 > ema200_1m) & (c > (w52Lo * 1.30)) & (c >= (w52Hi * 0.75))
    )
    bearPass = (
        (c < ema50) & (c <= ema150) & (c <= ema200) &
        (ema50 < ema150) & (ema50 < ema200) & (ema150 <= ema200) &
        (ema200 < ema200_1m) & (c < (w52Hi * 0.70)) & (c <= (w52Lo * 1.25))
    )

    redVol = v.where(c < o, 0.0)
    greenVol = v.where(c > o, 0.0)
    hiRedVol = _highest(redVol.shift(1), 10)
    hiGreenVol = _highest(greenVol.shift(1), 10)
    priceUp = ((c - o) / o.replace(0, np.nan)) * 100 > 3.0
    priceDn = ((o - c) / o.replace(0, np.nan)) * 100 > 3.0
    volBull = v > hiRedVol
    volBear = v > hiGreenVol
    sPPBull = conf & priceUp & volBull
    sPPBear = conf & priceDn & volBear
    b2bPUP = sPPBull & _nz_b(sPPBull.shift(1))
    b2bPPD = sPPBear & _nz_b(sPPBear.shift(1))
    superPup = sPPBull & bullPass
    superPPD = sPPBear & bearPass

    # neutralPhase / armed PUP+PPD trackers — stateful (Pine 551-579)
    isNeutral = (~bullPass.fillna(False)) & (~bearPass.fillna(False))
    nbc = np.zeros(len(df), dtype=int)
    cur = 0
    in_arr = isNeutral.to_numpy()
    for i, b in enumerate(in_arr):
        cur = cur + 1 if b else 0
        nbc[i] = cur
    neutralBarCount = pd.Series(nbc, index=df.index)

    nPC_arr = np.zeros(len(df), dtype=bool)
    cur = False
    for i in range(len(df)):
        if nbc[i] >= 5:
            cur = True
        nPC_arr[i] = cur

    pup_arr = np.zeros(len(df), dtype=bool)
    fpup_arr = np.zeros(len(df), dtype=bool)
    ppd_arr = np.zeros(len(df), dtype=bool)
    fppd_arr = np.zeros(len(df), dtype=bool)
    bull_arr = bullPass.fillna(False).to_numpy()
    bear_arr = bearPass.fillna(False).to_numpy()
    spp_arr = sPPBull.fillna(False).to_numpy()
    spd_arr = sPPBear.fillna(False).to_numpy()
    npc = nPC_arr.copy()
    pup_armed = False
    ppd_armed = False
    prev_bull = False
    prev_bear = False
    for i in range(len(df)):
        cur_nPC = npc[i]
        # PUP arm side
        if cur_nPC and spp_arr[i]:
            pup_armed = True
        if bear_arr[i] and pup_armed:
            pup_armed = False
            cur_nPC = False
            npc[i] = False
        first_pup = pup_armed and bull_arr[i] and not prev_bull
        if first_pup:
            pup_armed = False
            cur_nPC = False
            npc[i] = False
        fpup_arr[i] = first_pup
        pup_arr[i] = pup_armed

        # PPD arm side (uses possibly-updated cur_nPC)
        if cur_nPC and spd_arr[i]:
            ppd_armed = True
        if bull_arr[i] and ppd_armed:
            ppd_armed = False
            npc[i] = False
        first_ppd = ppd_armed and bear_arr[i] and not prev_bear
        if first_ppd:
            ppd_armed = False
            npc[i] = False
        fppd_arr[i] = first_ppd
        ppd_arr[i] = ppd_armed

        prev_bull = bull_arr[i]
        prev_bear = bear_arr[i]
    firstPUPPass = pd.Series(fpup_arr, index=df.index)
    firstPPDPass = pd.Series(fppd_arr, index=df.index)

    # ── TB / Foster windows (Pine 581-642) — stateful ──────────────────────
    cab_arr = np.zeros(len(df), dtype=int)
    cur = 0
    for i, b in enumerate(bull_arr):
        cur = cur + 1 if b else 0
        cab_arr[i] = cur
    consecAnishBull = cab_arr  # raw

    car_arr = np.zeros(len(df), dtype=int)
    cur = 0
    for i, b in enumerate(bear_arr):
        cur = cur + 1 if b else 0
        car_arr[i] = cur
    consecAnishBear = car_arr

    # TB window (bull-collapse trigger)
    tb_open = False
    tb_count = 0
    tb_sig = np.zeros(len(df), dtype=bool)
    tb_pbj = np.zeros(len(df), dtype=bool)
    tb_pb = np.zeros(len(df), dtype=bool)
    spp_bear_arr = sPPBear.fillna(False).to_numpy()
    sBearPBJ_arr = sigBearPBJ.fillna(False).to_numpy()
    sBearPB_arr = sigBearPB.fillna(False).to_numpy()
    for i in range(len(df)):
        prev_cab = consecAnishBull[i - 1] if i > 0 else 0
        if (not bull_arr[i]) and prev_cab >= 5:
            tb_open = True
            tb_count = 0
        if tb_open:
            tb_count += 1
            if bull_arr[i]:
                tb_open = False
            elif spp_bear_arr[i]:
                tb_sig[i] = True
                tb_open = False
            elif sBearPBJ_arr[i]:
                tb_pbj[i] = True
                tb_open = False
            elif sBearPB_arr[i]:
                tb_pb[i] = True
                tb_open = False
            elif tb_count > 1:
                tb_open = False
    tbSignal = pd.Series(tb_sig, index=df.index)
    tbPBJSignal = pd.Series(tb_pbj, index=df.index)
    tbPBSignal = pd.Series(tb_pb, index=df.index)

    # Foster window (bear-collapse trigger)
    fos_open = False
    fos_count = 0
    fos_sig = np.zeros(len(df), dtype=bool)
    fos_pbj = np.zeros(len(df), dtype=bool)
    fos_pb = np.zeros(len(df), dtype=bool)
    sBullPBJ_arr = sigBullPBJ.fillna(False).to_numpy()
    sBullPB_arr = sigBullPB.fillna(False).to_numpy()
    for i in range(len(df)):
        prev_car = consecAnishBear[i - 1] if i > 0 else 0
        if (not bear_arr[i]) and prev_car >= 5:
            fos_open = True
            fos_count = 0
        if fos_open:
            fos_count += 1
            if bear_arr[i]:
                fos_open = False
            elif spp_arr[i]:
                fos_sig[i] = True
                fos_open = False
            elif sBullPBJ_arr[i]:
                fos_pbj[i] = True
                fos_open = False
            elif sBullPB_arr[i]:
                fos_pb[i] = True
                fos_open = False
            elif fos_count > 1:
                fos_open = False
    fosterSignal = pd.Series(fos_sig, index=df.index)
    fosterPBJSignal = pd.Series(fos_pbj, index=df.index)
    fosterPBSignal = pd.Series(fos_pb, index=df.index)

    # ── ROC / DISPLACEMENT (Pine 644-698) ───────────────────────────────────
    roc_pN = c.shift(5)
    roc_val = ((c - roc_pN) / roc_pN.replace(0, np.nan)).fillna(0.0) * 100
    roc_ar = _sma((roc_val - roc_val.shift(1)).abs(), 100)
    roc_inp = (roc_val / roc_ar).where(roc_ar != 0, 0.0)
    roc_ema = _ema(roc_inp, 5)

    hlc3 = (h + l + c) / 3.0
    ld_esa = _ema(hlc3, 8)
    ld_atr = _atr(df, 100)
    ld_ci = ((hlc3 - ld_esa) / ld_atr.where(ld_atr != 0, 1.0)) * 100
    ld_wt1 = _ema(ld_ci, 21)
    ld_wt2 = _sma(ld_wt1, 4)
    ld_hist = ld_wt1 - ld_wt2
    ld_xup = (ld_wt1 > ld_wt2) & (_nz_f(ld_wt1.shift(1)) <= _nz_f(ld_wt2.shift(1)))
    ld_xdn = (ld_wt1 < ld_wt2) & (_nz_f(ld_wt1.shift(1)) >= _nz_f(ld_wt2.shift(1)))

    b1_roc = (roc_ema > 2.0) & (_nz_f(roc_ema.shift(1)) <= 2.0)
    b2_roc = ld_xup & (ld_wt1 < -60)
    b3_roc = ld_xup & (ld_hist > 5.0)
    b4_roc = (ld_hist > 15.0) & (_nz_f(ld_hist.shift(1)) <= 15.0)
    # b5_roc = ld_xup[1] AND close > high[1]  (Pine 665)
    b5_roc = _nz_b(ld_xup.shift(1)) & (c > h.shift(1))

    r1_roc = (roc_ema < -1.25) & (_nz_f(roc_ema.shift(1)) >= -1.25)
    r2_roc = ld_xdn & (ld_wt1 > 60)
    r3_roc = ld_xdn & (ld_hist < -5.0)
    r4_roc = (ld_hist < -15.0) & (_nz_f(ld_hist.shift(1)) >= -15.0)
    r5_roc = _nz_b(ld_xdn.shift(1)) & (c < l.shift(1))

    # f_has(sig, 1) is equivalent to sig itself on the current bar; Pine
    # body iterates i=0 to math.min(win-1, bar_index). With win=1 → just sig.
    bull2_cond = (b1_roc & b4_roc) | (b3_roc & b2_roc)
    bear2_cond = (r1_roc & r4_roc) | (r3_roc & r2_roc)

    hasBullHW = sigBullRVOL1x | sigGrandSlam | sigWTC | sigHiroshima | sigNagasaki
    hasBearHW = sigBearRVOL1x | sigMOAB | sigWTC | sigHiroshima | sigNagasaki

    sigBullCombo = sigBullPBJ & bull2_cond
    sigBearCombo = sigBearPBJ & bear2_cond
    sigROCBull = conf & sigBullCombo & hasBullHW & (c > o)
    sigROCBear = conf & sigBearCombo & hasBearHW & (c < o)

    # Displacement (5x stdev of open-to-close range)
    disp_rng = (o - c).abs()
    disp_thresh = _stdev(disp_rng, 100) * 5.0
    disp_prevDisp = disp_rng.shift(1) > disp_thresh.shift(1)
    disp_bullFVG = (l > h.shift(2)) & (c.shift(1) > o.shift(1))
    disp_bearFVG = (h < l.shift(2)) & (c.shift(1) < o.shift(1))
    sigDISPBull = conf & disp_prevDisp & disp_bullFVG
    sigDISPBear = conf & disp_prevDisp & disp_bearFVG

    # ── FAUNA (Pine 700-748) — MB+RE+TA core, GG/TR/ES/GDR exclusions ───────
    fauna_atr = _atr(df, 14)
    fauna_avgVol = _sma(v, 20)
    fauna_avgBody = _sma((c - o).abs(), 20)
    fauna_avgDelta = _sma((c - c.shift(1)).abs(), 10)
    fauna_trendMA = _sma(c, 50)
    fauna_body = c - o
    fauna_rng2 = h - l
    fauna_bodySz = fauna_body.abs()
    fauna_bodyRat = (fauna_bodySz / fauna_rng2.replace(0, np.nan)).fillna(0.0)
    fauna_up = fauna_body > 0
    fauna_dn = fauna_body < 0

    fMB_b = conf & fauna_up & (fauna_bodySz > 1.6 * fauna_atr) & (fauna_bodyRat > 0.7) & (v > 1.8 * fauna_avgVol)
    fRE_b = conf & fauna_up & (fauna_rng2 > 2.2 * fauna_atr) & ((h - c) < 0.15 * fauna_rng2) & (v > 1.8 * fauna_avgVol)
    fTA_b = conf & (fauna_trendMA > fauna_trendMA.shift(1)) & ((c - c.shift(1)) > 1.6 * fauna_avgDelta) & fauna_up & (v > 1.8 * fauna_avgVol)

    fGG_b = ((o - c.shift(1)) > 0.9 * fauna_atr) & fauna_up & (l > c.shift(1)) & (v > 1.8 * fauna_avgVol)
    fauna_prev_body = c.shift(1) - o.shift(1)
    fauna_prev_range = h.shift(1) - l.shift(1)
    fauna_StrongBear = (c.shift(1) < o.shift(1)) & (fauna_prev_body.abs() > 1.5 * fauna_avgBody.shift(1)) & (v.shift(1) > 1.5 * fauna_avgVol.shift(1))
    fauna_WeakBear = (c.shift(1) < o.shift(1)) & ((fauna_prev_body.abs() / fauna_prev_range.replace(0, np.nan)).fillna(0.0) <= 0.2)
    fTR_b = fauna_WeakBear & (fMB_b | fRE_b | fTA_b)
    fES_b = fauna_StrongBear & (fMB_b | fRE_b | fTA_b)
    fGDR_b = (c.shift(1) < o.shift(1)) & fGG_b
    # NB: Ultra Combo's exclusion = fGG_b OR fTR_b OR fES_b OR fGDR_b
    # (unconditional GG exclusion — different from the_only_one which has
    # a 2-core-pass override). Per FAUNA composition spec, this matches
    # ultra-combo's CHANGELOG: "FAUNA = (MB OR RE OR TA) AND NOT
    # (GG OR TR OR ES OR GDR)".
    excluded_bull = fGG_b | fTR_b | fES_b | fGDR_b
    sigFAUNABull = (fMB_b | fRE_b | fTA_b) & ~excluded_bull

    fMB_r = conf & fauna_dn & (fauna_bodySz > 1.6 * fauna_atr) & (fauna_bodyRat > 0.7) & (v > 1.8 * fauna_avgVol)
    fRE_r = conf & fauna_dn & (fauna_rng2 > 2.2 * fauna_atr) & ((c - l) < 0.15 * fauna_rng2) & (v > 1.8 * fauna_avgVol)
    fTA_r = conf & (fauna_trendMA < fauna_trendMA.shift(1)) & ((c.shift(1) - c) > 1.6 * fauna_avgDelta) & fauna_dn & (v > 1.8 * fauna_avgVol)
    fGG_r = ((c.shift(1) - o) > 0.9 * fauna_atr) & fauna_dn & (h < c.shift(1)) & (v > 1.8 * fauna_avgVol)
    fauna_StrongBull = (c.shift(1) > o.shift(1)) & (fauna_prev_body.abs() > 1.5 * fauna_avgBody.shift(1)) & (v.shift(1) > 1.5 * fauna_avgVol.shift(1))
    fauna_WeakBull = (c.shift(1) > o.shift(1)) & ((fauna_prev_body.abs() / fauna_prev_range.replace(0, np.nan)).fillna(0.0) <= 0.2)
    fTR_r = fauna_WeakBull & (fMB_r | fRE_r | fTA_r)
    fES_r = fauna_StrongBull & (fMB_r | fRE_r | fTA_r)
    fGDR_r = (c.shift(1) > o.shift(1)) & fGG_r
    excluded_bear = fGG_r | fTR_r | fES_r | fGDR_r
    sigFAUNABear = (fMB_r | fRE_r | fTA_r) & ~excluded_bear

    # ── SUPER signals (Pine 750-759) ────────────────────────────────────────
    anyBullRVOL = sigBullRVOL1x | sigGrandSlam | sigWTC | sigHiroshima | sigNagasaki
    anyBearRVOL = sigBearRVOL1x | sigMOAB | sigWTC | sigHiroshima | sigNagasaki

    sigSuperBullPBJ = conf & sigDISPBull & sigBullPBJ & sigFAUNABull & anyBullRVOL
    sigSuperBullPB = conf & sigDISPBull & sigBullPB & sigFAUNABull & anyBullRVOL
    sigSuperBearPBJ = conf & sigDISPBear & sigBearPBJ & sigFAUNABear & anyBearRVOL
    sigSuperBearPB = conf & sigDISPBear & sigBearPB & sigFAUNABear & anyBearRVOL

    anySuperBull = sigSuperBullPBJ | sigSuperBullPB
    anySuperBear = sigSuperBearPBJ | sigSuperBearPB

    # ── GZ1 / HV FVG engine (Pine 761-823) — STUBBED ────────────────────────
    # Requires bar-by-bar fvg array. Caller injects:
    #   bullGZI, bearGZI, bullHV, bearHV via df.attrs.
    bullGZI = _attr_or_false(df, "bullGZI")
    bearGZI = _attr_or_false(df, "bearGZI")
    bullHV = _attr_or_false(df, "bullHV")
    bearHV = _attr_or_false(df, "bearHV")

    # ── ALL COMBO SIGNALS (Pine 825-920) ────────────────────────────────────
    # PBJ × cluster
    comboPBJ_F2_Bull = sigBullPBJ & sBullF2
    comboPBJ_E3_Bull = sigBullPBJ & sBullE3
    comboPBJ_Cluster_Bull = sigBullPBJ & sBullFC
    comboPBJ_F2_Bear = sigBearPBJ & sBearF2
    comboPBJ_E3_Bear = sigBearPBJ & sBearE3
    comboPBJ_Cluster_Bear = sigBearPBJ & sBearFC

    # PB × cluster
    comboPB_F2_Bull = sigBullPB & sBullF2
    comboPB_E3_Bull = sigBullPB & sBullE3
    comboPB_Cluster_Bull = sigBullPB & sBullFC
    comboPB_F2_Bear = sigBearPB & sBearF2
    comboPB_E3_Bear = sigBearPB & sBearE3
    comboPB_Cluster_Bear = sigBearPB & sBearFC

    # Sequential combos
    comboF2Cluster_E3_Bull = _nz_b(sBullF2.shift(1)) & _nz_b(sBullFC.shift(1)) & sBullE3
    comboF2Cluster_E3_Bear = _nz_b(sBearF2.shift(1)) & _nz_b(sBearFC.shift(1)) & sBearE3
    comboF2ClusterB2B_Bull = sBullF2 & sBullFC & b2bPUP
    comboF2ClusterB2B_Bear = sBearF2 & sBearFC & b2bPPD
    comboB2B_F2_Bull = b2bPUP & sBullF2
    comboB2B_F2_Bear = b2bPPD & sBearF2
    pupCountE3 = (sPPBull.astype(int) + _nz_b(sPPBull.shift(1)).astype(int) + _nz_b(sPPBull.shift(2)).astype(int))
    comboE3_2of3PUP_Bull = sBullE3 & (pupCountE3 >= 2)
    ppdCountE3 = (sPPBear.astype(int) + _nz_b(sPPBear.shift(1)).astype(int) + _nz_b(sPPBear.shift(2)).astype(int))
    comboE3_2of3PPD_Bear = sBearE3 & (ppdCountE3 >= 2)

    # Consecutive-day combos. f_hadSignalYesterday(sig) = "did sig fire any
    # bar in [1 .. barsPerDay*2]". We compute barsPerDay from tfSec.
    def _bars_per_day(tfsec: float) -> int:
        tf_min = tfsec / 60.0
        raw_bars = 1 if tf_min >= 390 else int(np.ceil(390.0 / tf_min))
        return int(np.ceil(raw_bars * 1.25))
    barsPerDay = _bars_per_day(tfSec)
    yesterday_window = max(1, barsPerDay * 2)

    def _had_yesterday(sig: pd.Series) -> pd.Series:
        # Pine: for i = 1 to math.min(win, bar_index) of sig[i]
        # → rolling-any over the *previous* `win` bars (excludes current).
        s = sig.fillna(False).astype(bool)
        return s.shift(1).rolling(yesterday_window, min_periods=1).max().fillna(0).astype(bool)

    comboF2_B2BDays_Bull = sBullF2 & _had_yesterday(sBullF2)
    comboF2_B2BDays_Bear = sBearF2 & _had_yesterday(sBearF2)
    comboE3_B2BDays_Bull = sBullE3 & _had_yesterday(sBullE3)
    comboE3_B2BDays_Bear = sBearE3 & _had_yesterday(sBearE3)
    comboF2E3_Consec_Bull = (sBullF2 & _had_yesterday(sBullE3)) | (sBullE3 & _had_yesterday(sBullF2))
    comboF2E3_Consec_Bear = (sBearF2 & _had_yesterday(sBearE3)) | (sBearE3 & _had_yesterday(sBearF2))
    comboCluster_B2BDays_Bull = sBullFC & _had_yesterday(sBullFC)
    comboCluster_B2BDays_Bear = sBearFC & _had_yesterday(sBearFC)

    # Heavy Weapon + Any
    anyBullHW = sigBullRVOL1x | sigGrandSlam | sigWTC | sigHiroshima | sigNagasaki | sigROCBull | sigSuperBullPBJ | sigSuperBullPB
    anyBearHW = sigBearRVOL1x | sigMOAB | sigWTC | sigHiroshima | sigNagasaki | sigROCBear | sigSuperBearPBJ | sigSuperBearPB
    comboHW_AnyBull = anyBullHW & sAnyBull
    comboHW_AnyBear = anyBearHW & sAnyBear

    # GZ1/HV + Any (same bar OR previous bar of sAnyBull)
    comboHV_AnyBull = bullHV & (sAnyBull | _nz_b(sAnyBull.shift(1)))
    comboHV_AnyBear = bearHV & (sAnyBear | _nz_b(sAnyBear.shift(1)))
    comboGZ_AnyBull = bullGZI & (sAnyBull | _nz_b(sAnyBull.shift(1)))
    comboGZ_AnyBear = bearGZI & (sAnyBear | _nz_b(sAnyBear.shift(1)))
    comboGZHV_AnyBull = comboHV_AnyBull | comboGZ_AnyBull
    comboGZHV_AnyBear = comboHV_AnyBear | comboGZ_AnyBear

    # HV+GZI combo (sessBar==2 AND HV on bar-1 AND HV+GZI same bar)
    hvGziComboBull = (sessBar == 2) & _nz_b(bullHV.shift(1)) & bullHV & bullGZI
    hvGziComboBear = (sessBar == 2) & _nz_b(bearHV.shift(1)) & bearHV & bearGZI

    # MEGAs
    gz1MegaBull = bullGZI & anySuperBull & sPPBull & sigFAUNABull & sigDISPBull
    hvMegaBull = bullHV & anySuperBull & sPPBull & sigFAUNABull & sigDISPBull
    gz1hvMegaBull = bullGZI & bullHV & anySuperBull & sPPBull & sigFAUNABull & sigDISPBull
    gz1MegaBear = bearGZI & anySuperBear & sPPBear & sigFAUNABear & sigDISPBear
    hvMegaBear = bearHV & anySuperBear & sPPBear & sigFAUNABear & sigDISPBear
    gz1hvMegaBear = bearGZI & bearHV & anySuperBear & sPPBear & sigFAUNABear & sigDISPBear
    gzHvMegaBull = gz1MegaBull | hvMegaBull
    gzHvMegaBear = gz1MegaBear | hvMegaBear

    # Opener (first session bar)
    openerBull = (sessBar == 1) & (bullGZI | bullHV) & (anyBullHW | sigBullPBJ | sigROCBull | (firstPUPPass & superPup))
    openerBear = (sessBar == 1) & (bearGZI | bearHV) & (anyBearHW | sigBearPBJ | sigROCBear | (firstPPDPass & superPPD))

    # 3-bar window
    pbjIn3Bull = sigBullPBJ | _nz_b(sigBullPBJ.shift(1)) | _nz_b(sigBullPBJ.shift(2))
    b2bIn3Bull = b2bPUP | _nz_b(b2bPUP.shift(1)) | _nz_b(b2bPUP.shift(2))
    pupsIn3Bull = sPPBull.astype(int) + _nz_b(sPPBull.shift(1)).astype(int) + _nz_b(sPPBull.shift(2)).astype(int)
    scenarioA_Bull = pbjIn3Bull & b2bIn3Bull
    scenarioB_Bull = pbjIn3Bull & (pupsIn3Bull >= 2)
    threeBar_Bull = scenarioA_Bull | scenarioB_Bull

    pbjIn3Bear = sigBearPBJ | _nz_b(sigBearPBJ.shift(1)) | _nz_b(sigBearPBJ.shift(2))
    b2bIn3Bear = b2bPPD | _nz_b(b2bPPD.shift(1)) | _nz_b(b2bPPD.shift(2))
    ppdsIn3Bear = sPPBear.astype(int) + _nz_b(sPPBear.shift(1)).astype(int) + _nz_b(sPPBear.shift(2)).astype(int)
    scenarioA_Bear = pbjIn3Bear & b2bIn3Bear
    scenarioB_Bear = pbjIn3Bear & (ppdsIn3Bear >= 2)
    threeBar_Bear = scenarioA_Bear | scenarioB_Bear

    # Foster/TB + Heavy
    anyFoster = fosterSignal | fosterPBJSignal | fosterPBSignal
    anyTB = tbSignal | tbPBJSignal | tbPBSignal
    fosterHeavyBull = anyFoster & (sigROCBull | anyBullHW | anySuperBull)
    tbHeavyBear = anyTB & (sigROCBear | anyBearHW | anySuperBear)

    # GZ/HV + Heavy
    gzHvHeavyBull = (bullGZI | bullHV) & (anyBullHW | anySuperBull | sigROCBull)
    gzHvHeavyBear = (bearGZI | bearHV) & (anyBearHW | anySuperBear | sigROCBear)

    # SUPER B2B days
    superB2BDaysBull = anySuperBull & _had_yesterday(anySuperBull)
    superB2BDaysBear = anySuperBear & _had_yesterday(anySuperBear)

    # ── PIPELINE C: fire_* outputs gated by show_* IPSF toggles ─────────────
    def _g(name: str, sig: pd.Series) -> pd.Series:
        return sig & bool(p.get(f"show_{name}", True))

    fire = {
        # PBJ × cluster
        "fire_PBJ_F2_Bull":      _g("pbjF2",      comboPBJ_F2_Bull),
        "fire_PBJ_F2_Bear":      _g("pbjF2",      comboPBJ_F2_Bear),
        "fire_PBJ_E3_Bull":      _g("pbjE3",      comboPBJ_E3_Bull),
        "fire_PBJ_E3_Bear":      _g("pbjE3",      comboPBJ_E3_Bear),
        "fire_PBJ_Cluster_Bull": _g("pbjCluster", comboPBJ_Cluster_Bull),
        "fire_PBJ_Cluster_Bear": _g("pbjCluster", comboPBJ_Cluster_Bear),
        # PB × cluster
        "fire_PB_F2_Bull":       _g("pbF2",       comboPB_F2_Bull),
        "fire_PB_F2_Bear":       _g("pbF2",       comboPB_F2_Bear),
        "fire_PB_E3_Bull":       _g("pbE3",       comboPB_E3_Bull),
        "fire_PB_E3_Bear":       _g("pbE3",       comboPB_E3_Bear),
        "fire_PB_Cluster_Bull":  _g("pbCluster",  comboPB_Cluster_Bull),
        "fire_PB_Cluster_Bear":  _g("pbCluster",  comboPB_Cluster_Bear),
        # Sequential
        "fire_F2Cluster_E3_Bull":   _g("f2ClusterE3",   comboF2Cluster_E3_Bull),
        "fire_F2Cluster_E3_Bear":   _g("f2ClusterE3",   comboF2Cluster_E3_Bear),
        "fire_F2ClusterB2B_Bull":   _g("f2ClusterB2B",  comboF2ClusterB2B_Bull),
        "fire_F2ClusterB2B_Bear":   _g("f2ClusterB2B",  comboF2ClusterB2B_Bear),
        "fire_B2B_F2_Bull":         _g("b2bF2",         comboB2B_F2_Bull),
        "fire_B2B_F2_Bear":         _g("b2bF2",         comboB2B_F2_Bear),
        "fire_E3_2of3PUP_Bull":     _g("e3PUP",         comboE3_2of3PUP_Bull),
        "fire_E3_2of3PPD_Bear":     _g("e3PUP",         comboE3_2of3PPD_Bear),
        # Consecutive day
        "fire_F2_B2BDays_Bull":      _g("f2B2B",         comboF2_B2BDays_Bull),
        "fire_F2_B2BDays_Bear":      _g("f2B2B",         comboF2_B2BDays_Bear),
        "fire_E3_B2BDays_Bull":      _g("e3B2B",         comboE3_B2BDays_Bull),
        "fire_E3_B2BDays_Bear":      _g("e3B2B",         comboE3_B2BDays_Bear),
        "fire_F2E3_Consec_Bull":     _g("f2e3Consec",    comboF2E3_Consec_Bull),
        "fire_F2E3_Consec_Bear":     _g("f2e3Consec",    comboF2E3_Consec_Bear),
        "fire_Cluster_B2BDays_Bull": _g("clusterB2BDays",comboCluster_B2BDays_Bull),
        "fire_Cluster_B2BDays_Bear": _g("clusterB2BDays",comboCluster_B2BDays_Bear),
        # Heavy Weapon
        "fire_HW_AnyBull":           _g("hwBullAny",     comboHW_AnyBull),
        "fire_HW_AnyBear":           _g("hwBearAny",     comboHW_AnyBear),
        # GZ1/HV + Any
        "fire_GZHV_AnyBull":         _g("gzHvAny",       comboGZHV_AnyBull),
        "fire_GZHV_AnyBear":         _g("gzHvAny",       comboGZHV_AnyBear),
        "fire_HV_GZI_Bull":          _g("hvGziCombo",    hvGziComboBull),
        "fire_HV_GZI_Bear":          _g("hvGziCombo",    hvGziComboBear),
        # MEGAs
        "fire_GZHV_Mega_Bull":       _g("gzHvMega",      gzHvMegaBull),
        "fire_GZHV_Mega_Bear":       _g("gzHvMega",      gzHvMegaBear),
        "fire_GZ1HV_Mega_Bull":      _g("gz1hvMegaCombo",gz1hvMegaBull),
        "fire_GZ1HV_Mega_Bear":      _g("gz1hvMegaCombo",gz1hvMegaBear),
        # Opener
        "fire_OpenerBull":           _g("openerBull",    openerBull),
        "fire_OpenerBear":           _g("openerBear",    openerBear),
        # 3-bar
        "fire_3BarBull":             _g("3barBull",      threeBar_Bull),
        "fire_3BarBear":             _g("3barBear",      threeBar_Bear),
        # Foster/TB + Heavy
        "fire_FosterHeavyBull":      _g("fosterHeavyBull", fosterHeavyBull),
        "fire_TBHeavyBear":          _g("tbHeavyBear",   tbHeavyBear),
        # GZ/HV + Heavy
        "fire_GZHV_HeavyBull":       _g("gzHvHeavyBull", gzHvHeavyBull),
        "fire_GZHV_HeavyBear":       _g("gzHvHeavyBear", gzHvHeavyBear),
        # SUPER B2B days
        "fire_SuperB2BDays_Bull":    _g("superB2BDays",  superB2BDaysBull),
        "fire_SuperB2BDays_Bear":    _g("superB2BDays",  superB2BDaysBear),
        # Naked Nagasaki plot (no show_* gate in source — always plotted)
        "fire_Nagasaki":             sigNagasaki,
    }

    cache.update({
        # Root operands
        "sigBullPBJ": sigBullPBJ, "sigBullPB": sigBullPB,
        "sigBearPBJ": sigBearPBJ, "sigBearPB": sigBearPB,
        "sigBullRVOL1x": sigBullRVOL1x, "sigBearRVOL1x": sigBearRVOL1x,
        "sigGrandSlam": sigGrandSlam, "sigMOAB": sigMOAB,
        "sigWTC": sigWTC, "sigHiroshima": sigHiroshima, "sigNagasaki": sigNagasaki,
        "sigFAUNABull": sigFAUNABull, "sigFAUNABear": sigFAUNABear,
        "sigDISPBull": sigDISPBull, "sigDISPBear": sigDISPBear,
        "sigROCBull": sigROCBull, "sigROCBear": sigROCBear,
        # SUPER decomposed (the headline Ultra signals)
        "sigSuperBullPBJ": sigSuperBullPBJ, "sigSuperBullPB": sigSuperBullPB,
        "sigSuperBearPBJ": sigSuperBearPBJ, "sigSuperBearPB": sigSuperBearPB,
        "anySuperBull": anySuperBull, "anySuperBear": anySuperBear,
        # Cluster / F2 / E3 / FC
        "sBullF2": sBullF2, "sBearF2": sBearF2,
        "sBullE3": sBullE3, "sBearE3": sBearE3,
        "sBullFC": sBullFC, "sBearFC": sBearFC,
        "sAnyBull": sAnyBull, "sAnyBear": sAnyBear,
        # PUP/PPD
        "sPPBull": sPPBull, "sPPBear": sPPBear,
        "b2bPUP": b2bPUP, "b2bPPD": b2bPPD,
        "firstPUPPass": firstPUPPass, "firstPPDPass": firstPPDPass,
        "superPup": superPup, "superPPD": superPPD,
        # TB / Foster
        "tbSignal": tbSignal, "tbPBJSignal": tbPBJSignal, "tbPBSignal": tbPBSignal,
        "fosterSignal": fosterSignal, "fosterPBJSignal": fosterPBJSignal,
        "fosterPBSignal": fosterPBSignal,
        # GZ1/HV (stubs)
        "bullGZI": bullGZI, "bearGZI": bearGZI,
        "bullHV": bullHV, "bearHV": bearHV,
        # Composites
        "comboPBJ_F2_Bull": comboPBJ_F2_Bull, "comboPBJ_F2_Bear": comboPBJ_F2_Bear,
        "comboPBJ_E3_Bull": comboPBJ_E3_Bull, "comboPBJ_E3_Bear": comboPBJ_E3_Bear,
        "comboPBJ_Cluster_Bull": comboPBJ_Cluster_Bull, "comboPBJ_Cluster_Bear": comboPBJ_Cluster_Bear,
        "comboPB_F2_Bull": comboPB_F2_Bull, "comboPB_F2_Bear": comboPB_F2_Bear,
        "comboPB_E3_Bull": comboPB_E3_Bull, "comboPB_E3_Bear": comboPB_E3_Bear,
        "comboPB_Cluster_Bull": comboPB_Cluster_Bull, "comboPB_Cluster_Bear": comboPB_Cluster_Bear,
        "comboF2Cluster_E3_Bull": comboF2Cluster_E3_Bull, "comboF2Cluster_E3_Bear": comboF2Cluster_E3_Bear,
        "comboF2ClusterB2B_Bull": comboF2ClusterB2B_Bull, "comboF2ClusterB2B_Bear": comboF2ClusterB2B_Bear,
        "comboB2B_F2_Bull": comboB2B_F2_Bull, "comboB2B_F2_Bear": comboB2B_F2_Bear,
        "comboE3_2of3PUP_Bull": comboE3_2of3PUP_Bull, "comboE3_2of3PPD_Bear": comboE3_2of3PPD_Bear,
        "comboF2_B2BDays_Bull": comboF2_B2BDays_Bull, "comboF2_B2BDays_Bear": comboF2_B2BDays_Bear,
        "comboE3_B2BDays_Bull": comboE3_B2BDays_Bull, "comboE3_B2BDays_Bear": comboE3_B2BDays_Bear,
        "comboF2E3_Consec_Bull": comboF2E3_Consec_Bull, "comboF2E3_Consec_Bear": comboF2E3_Consec_Bear,
        "comboCluster_B2BDays_Bull": comboCluster_B2BDays_Bull, "comboCluster_B2BDays_Bear": comboCluster_B2BDays_Bear,
        "comboHW_AnyBull": comboHW_AnyBull, "comboHW_AnyBear": comboHW_AnyBear,
        "comboHV_AnyBull": comboHV_AnyBull, "comboHV_AnyBear": comboHV_AnyBear,
        "comboGZ_AnyBull": comboGZ_AnyBull, "comboGZ_AnyBear": comboGZ_AnyBear,
        "comboGZHV_AnyBull": comboGZHV_AnyBull, "comboGZHV_AnyBear": comboGZHV_AnyBear,
        "hvGziComboBull": hvGziComboBull, "hvGziComboBear": hvGziComboBear,
        "gz1MegaBull": gz1MegaBull, "hvMegaBull": hvMegaBull, "gz1hvMegaBull": gz1hvMegaBull,
        "gz1MegaBear": gz1MegaBear, "hvMegaBear": hvMegaBear, "gz1hvMegaBear": gz1hvMegaBear,
        "gzHvMegaBull": gzHvMegaBull, "gzHvMegaBear": gzHvMegaBear,
        "openerBull": openerBull, "openerBear": openerBear,
        "threeBar_Bull": threeBar_Bull, "threeBar_Bear": threeBar_Bear,
        "fosterHeavyBull": fosterHeavyBull, "tbHeavyBear": tbHeavyBear,
        "gzHvHeavyBull": gzHvHeavyBull, "gzHvHeavyBear": gzHvHeavyBear,
        "superB2BDaysBull": superB2BDaysBull, "superB2BDaysBear": superB2BDaysBear,
        "anyBullHW": anyBullHW, "anyBearHW": anyBearHW,
        # Fire dict (show_*-gated)
        **fire,
    })
    return cache


# ----------------------------------------------------------------------------
# Range-overlap engine (Pine b1/b4 array-of-rects)
# ----------------------------------------------------------------------------
def _range_overlap_engine(df: pd.DataFrame,
                          thEv: pd.Series,
                          seqEv: pd.Series,
                          window: int = 20) -> pd.Series:
    """Bar-by-bar reproduction of Pine's b1_thIdx/b1_sqIdx overlap arrays.

    For each bar:
      - drop entries older than `window` from both arrays
      - if thEv: push (low, high) onto thArr; ovlp := any sq entry overlaps
      - if seqEv and NOT ovlp: push (low, high) onto sqArr; ovlp := any th
        entry overlaps
    Returns a per-bar boolean `ovlp`.

    NB: Pine's semantics: ovlp is a *bar-local* var that resets to False at
    the top of each bar's evaluation. So the returned series == ovlp at end
    of bar.
    """
    n = len(df)
    lo_arr = df["low"].to_numpy()
    hi_arr = df["high"].to_numpy()
    th_arr = thEv.fillna(False).to_numpy()
    sq_arr = seqEv.fillna(False).to_numpy()
    out = np.zeros(n, dtype=bool)

    # Each entry: (bar_index, hi, lo)
    th_list: list = []
    sq_list: list = []

    for i in range(n):
        # Prune stale entries
        while th_list and (i - th_list[0][0]) > window:
            th_list.pop(0)
        while sq_list and (i - sq_list[0][0]) > window:
            sq_list.pop(0)

        ovlp = False
        cur_lo = lo_arr[i]
        cur_hi = hi_arr[i]

        if th_arr[i]:
            th_list.append((i, cur_hi, cur_lo))
            # Compare current bar's [lo, hi] against existing sq entries
            for (_, ehi, elo) in sq_list:
                if cur_lo <= ehi and elo <= cur_hi:
                    ovlp = True
                    break

        if sq_arr[i] and not ovlp:
            sq_list.append((i, cur_hi, cur_lo))
            for (_, ehi, elo) in th_list:
                if cur_lo <= ehi and elo <= cur_hi:
                    ovlp = True
                    break

        out[i] = ovlp
    return pd.Series(out, index=df.index)


# ============================================================================
# Public detection functions
# ============================================================================
def _wrap(name: str) -> Callable[[pd.DataFrame, Optional[Dict]], pd.Series]:
    def _fn(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
        eng = _ensure_engines(df, _p(params))
        s = eng[name]
        return s.fillna(False).astype(bool)
    _fn.__name__ = f"detect_{name}"
    return _fn


# ─── Root operand detections (Ultra Combo's own definitions) ───────────────
detect_sigBullPBJ = _wrap("sigBullPBJ")
detect_sigBullPB = _wrap("sigBullPB")
detect_sigBearPBJ = _wrap("sigBearPBJ")
detect_sigBearPB = _wrap("sigBearPB")
detect_sigBullRVOL1x = _wrap("sigBullRVOL1x")
detect_sigBearRVOL1x = _wrap("sigBearRVOL1x")
detect_sigGrandSlam = _wrap("sigGrandSlam")
detect_sigMOAB = _wrap("sigMOAB")
detect_sigWTC = _wrap("sigWTC")
detect_sigHiroshima = _wrap("sigHiroshima")
detect_sigNagasaki = _wrap("sigNagasaki")
detect_sigFAUNABull = _wrap("sigFAUNABull")
detect_sigFAUNABear = _wrap("sigFAUNABear")
detect_sigDISPBull = _wrap("sigDISPBull")
detect_sigDISPBear = _wrap("sigDISPBear")
detect_sigROCBull = _wrap("sigROCBull")
detect_sigROCBear = _wrap("sigROCBear")

# ─── ULTRA SUPER (decomposed) — the headline signals ──────────────────────
detect_sigSuperBullPBJ = _wrap("sigSuperBullPBJ")
detect_sigSuperBullPB = _wrap("sigSuperBullPB")
detect_sigSuperBearPBJ = _wrap("sigSuperBearPBJ")
detect_sigSuperBearPB = _wrap("sigSuperBearPB")

# ─── Cluster primitives ────────────────────────────────────────────────────
detect_sBullF2 = _wrap("sBullF2")
detect_sBearF2 = _wrap("sBearF2")
detect_sBullE3 = _wrap("sBullE3")
detect_sBearE3 = _wrap("sBearE3")
detect_sBullFC = _wrap("sBullFC")
detect_sBearFC = _wrap("sBearFC")

# ─── PBJ × cluster ─────────────────────────────────────────────────────────
detect_pbjF2_bull = _wrap("fire_PBJ_F2_Bull")
detect_pbjF2_bear = _wrap("fire_PBJ_F2_Bear")
detect_pbjE3_bull = _wrap("fire_PBJ_E3_Bull")
detect_pbjE3_bear = _wrap("fire_PBJ_E3_Bear")
detect_pbjCluster_bull = _wrap("fire_PBJ_Cluster_Bull")
detect_pbjCluster_bear = _wrap("fire_PBJ_Cluster_Bear")

# ─── PB × cluster ──────────────────────────────────────────────────────────
detect_pbF2_bull = _wrap("fire_PB_F2_Bull")
detect_pbF2_bear = _wrap("fire_PB_F2_Bear")
detect_pbE3_bull = _wrap("fire_PB_E3_Bull")
detect_pbE3_bear = _wrap("fire_PB_E3_Bear")
detect_pbCluster_bull = _wrap("fire_PB_Cluster_Bull")
detect_pbCluster_bear = _wrap("fire_PB_Cluster_Bear")

# ─── Sequential combos ─────────────────────────────────────────────────────
detect_f2ClusterE3_bull = _wrap("fire_F2Cluster_E3_Bull")
detect_f2ClusterE3_bear = _wrap("fire_F2Cluster_E3_Bear")
detect_f2ClusterB2B_bull = _wrap("fire_F2ClusterB2B_Bull")
detect_f2ClusterB2B_bear = _wrap("fire_F2ClusterB2B_Bear")
detect_b2bF2_bull = _wrap("fire_B2B_F2_Bull")
detect_b2bF2_bear = _wrap("fire_B2B_F2_Bear")
detect_e3PUP_bull = _wrap("fire_E3_2of3PUP_Bull")
detect_e3PPD_bear = _wrap("fire_E3_2of3PPD_Bear")

# ─── Consecutive day combos ────────────────────────────────────────────────
detect_f2B2BDays_bull = _wrap("fire_F2_B2BDays_Bull")
detect_f2B2BDays_bear = _wrap("fire_F2_B2BDays_Bear")
detect_e3B2BDays_bull = _wrap("fire_E3_B2BDays_Bull")
detect_e3B2BDays_bear = _wrap("fire_E3_B2BDays_Bear")
detect_f2e3Consec_bull = _wrap("fire_F2E3_Consec_Bull")
detect_f2e3Consec_bear = _wrap("fire_F2E3_Consec_Bear")
detect_clusterB2BDays_bull = _wrap("fire_Cluster_B2BDays_Bull")
detect_clusterB2BDays_bear = _wrap("fire_Cluster_B2BDays_Bear")

# ─── HW + Any / GZ/HV + Any ────────────────────────────────────────────────
detect_hwAnyBull = _wrap("fire_HW_AnyBull")
detect_hwAnyBear = _wrap("fire_HW_AnyBear")
detect_gzHvAnyBull = _wrap("fire_GZHV_AnyBull")
detect_gzHvAnyBear = _wrap("fire_GZHV_AnyBear")
detect_hvGziBull = _wrap("fire_HV_GZI_Bull")
detect_hvGziBear = _wrap("fire_HV_GZI_Bear")

# ─── MEGAs ─────────────────────────────────────────────────────────────────
detect_gzHvMegaBull = _wrap("fire_GZHV_Mega_Bull")
detect_gzHvMegaBear = _wrap("fire_GZHV_Mega_Bear")
detect_gz1hvMegaBull = _wrap("fire_GZ1HV_Mega_Bull")
detect_gz1hvMegaBear = _wrap("fire_GZ1HV_Mega_Bear")

# ─── Opener / 3-Bar / Foster-TB+Heavy / GZ-HV+Heavy / Super-B2B ────────────
detect_openerBull = _wrap("fire_OpenerBull")
detect_openerBear = _wrap("fire_OpenerBear")
detect_threeBarBull = _wrap("fire_3BarBull")
detect_threeBarBear = _wrap("fire_3BarBear")
detect_fosterHeavyBull = _wrap("fire_FosterHeavyBull")
detect_tbHeavyBear = _wrap("fire_TBHeavyBear")
detect_gzHvHeavyBull = _wrap("fire_GZHV_HeavyBull")
detect_gzHvHeavyBear = _wrap("fire_GZHV_HeavyBear")
detect_superB2BDays_bull = _wrap("fire_SuperB2BDays_Bull")
detect_superB2BDays_bear = _wrap("fire_SuperB2BDays_Bear")
detect_nagasakiPlot = _wrap("fire_Nagasaki")


# ============================================================================
# Stubbed detections — Pine-only intrinsics required.
# Keys are subsystem names; values describe what to inject via df.attrs.
# ============================================================================
STUBBED: Dict[str, str] = {
    # tv_ta.relativeVolume(30, "", false, true) — Pine library v6 only.
    # Inject `relVolRatio` via df.attrs (used by sigWTC/sigHiroshima).
    "_rel_vol_engine": "tv_ta.relativeVolume not reproduced; inject relVolRatio via df.attrs",
    # PBJ engine: Supertrend dir state + landing-zone arrays (bull_lvls,
    # bear_lvls) + reaccel detection + approach tracking. Bar-by-bar.
    # Inject sigBullPBJ / sigBullPB / sigBearPBJ / sigBearPB via df.attrs.
    "_pbj_engine": "PBJ landing-zone arrays + Supertrend dir requires bar-by-bar state; inject sigBullPBJ/sigBullPB/sigBearPBJ/sigBearPB via df.attrs",
    # GZ1 / HV FVG engine: array of fvg structs with per-bar pruning,
    # bullGZI/bearGZI/bullHV/bearHV outputs. Inject via df.attrs.
    "_gz_engine": "GZ1 FVG struct array not reproduced; inject bullGZI/bearGZI/bullHV/bearHV via df.attrs",
    # Session window — `time(timeframe.period, "0930-1600", "America/New_York")`
    # requires intraday timezone-aware filtering. Caller may inject `inSession`
    # boolean via df.attrs; default is True on every bar.
    "_session_engine": "RTH window `time(..., \"0930-1600\", NY)` not reproduced; inject inSession via df.attrs",
}


# ============================================================================
# State machines — exposed for the harness; they read from df.attrs.
# ============================================================================
@dataclass
class SuperTrendState:
    """Supertrend dir flip — required by PBJ engine; STUBBED in this port."""
    name: str = "SuperTrend"


@dataclass
class PBJLandingZoneState:
    """PBJ bull_lvls / bear_lvls array engine — STUBBED in this port."""
    name: str = "PBJLandingZone"


@dataclass
class GZ1FVGArrayState:
    """GZ1/HV FVG struct array — STUBBED in this port."""
    name: str = "GZ1FVGArray"


@dataclass
class RangeOverlapState:
    """b1/b4 cluster overlap-rect array — built into _ensure_engines."""
    name: str = "RangeOverlap"


@dataclass
class NagasakiATHState:
    """Streaming all-time-high volume tracker — built into _ensure_engines."""
    name: str = "NagasakiATH"


@dataclass
class AnishStageArmingState:
    """neutralPhase / pupArmed / ppdArmed / firstPUPPass / firstPPDPass —
    built into _ensure_engines."""
    name: str = "AnishStageArming"


@dataclass
class TBWindowState:
    """TB collapse-window tracker — built into _ensure_engines."""
    name: str = "TBWindow"


@dataclass
class FosterWindowState:
    """Foster collapse-window tracker — built into _ensure_engines."""
    name: str = "FosterWindow"


@dataclass
class SessionBarCounterState:
    """sessBar incrementer with inSession + new-day reset — built into
    _ensure_engines."""
    name: str = "SessionBarCounter"


STATE_MACHINES: Dict[str, type] = {
    "SuperTrend": SuperTrendState,
    "PBJLandingZone": PBJLandingZoneState,
    "GZ1FVGArray": GZ1FVGArrayState,
    "RangeOverlap": RangeOverlapState,
    "NagasakiATH": NagasakiATHState,
    "AnishStageArming": AnishStageArmingState,
    "TBWindow": TBWindowState,
    "FosterWindow": FosterWindowState,
    "SessionBarCounter": SessionBarCounterState,
}


# ============================================================================
# DETECTIONS registry — name → detect_* function.
# Names mirror Pine plot/alertcondition identifiers and root signal names
# so the harness can round-trip with the validator.
# ============================================================================
DETECTIONS: Dict[str, Callable] = {
    # ─── Root operands ────────────────────────────────────────────────────
    "sigBullPBJ":      detect_sigBullPBJ,
    "sigBullPB":       detect_sigBullPB,
    "sigBearPBJ":      detect_sigBearPBJ,
    "sigBearPB":       detect_sigBearPB,
    "sigBullRVOL1x":   detect_sigBullRVOL1x,
    "sigBearRVOL1x":   detect_sigBearRVOL1x,
    "sigGrandSlam":    detect_sigGrandSlam,
    "sigMOAB":         detect_sigMOAB,
    "sigWTC":          detect_sigWTC,
    "sigHiroshima":    detect_sigHiroshima,
    "sigNagasaki":     detect_sigNagasaki,
    "sigFAUNABull":    detect_sigFAUNABull,
    "sigFAUNABear":    detect_sigFAUNABear,
    "sigDISPBull":     detect_sigDISPBull,
    "sigDISPBear":     detect_sigDISPBear,
    "sigROCBull":      detect_sigROCBull,
    "sigROCBear":      detect_sigROCBear,
    # ─── ULTRA SUPER (decomposed) ─────────────────────────────────────────
    "sigSuperBullPBJ": detect_sigSuperBullPBJ,
    "sigSuperBullPB":  detect_sigSuperBullPB,
    "sigSuperBearPBJ": detect_sigSuperBearPBJ,
    "sigSuperBearPB":  detect_sigSuperBearPB,
    # ─── Cluster primitives ───────────────────────────────────────────────
    "F2 Bull":         detect_sBullF2,
    "F2 Bear":         detect_sBearF2,
    "E3 Bull":         detect_sBullE3,
    "E3 Bear":         detect_sBearE3,
    "FC Cluster Bull": detect_sBullFC,
    "FC Cluster Bear": detect_sBearFC,
    # ─── PBJ × cluster ────────────────────────────────────────────────────
    "PBJ+F2 Bull":     detect_pbjF2_bull,
    "PBJ+F2 Bear":     detect_pbjF2_bear,
    "PBJ+E3 Bull":     detect_pbjE3_bull,
    "PBJ+E3 Bear":     detect_pbjE3_bear,
    "PBJ+Cluster Bull": detect_pbjCluster_bull,
    "PBJ+Cluster Bear": detect_pbjCluster_bear,
    # ─── PB × cluster ─────────────────────────────────────────────────────
    "PB+F2 Bull":      detect_pbF2_bull,
    "PB+F2 Bear":      detect_pbF2_bear,
    "PB+E3 Bull":      detect_pbE3_bull,
    "PB+E3 Bear":      detect_pbE3_bear,
    "PB+Cluster Bull": detect_pbCluster_bull,
    "PB+Cluster Bear": detect_pbCluster_bear,
    # ─── Sequential ───────────────────────────────────────────────────────
    "F2Cluster→E3 Bull":  detect_f2ClusterE3_bull,
    "F2Cluster→E3 Bear":  detect_f2ClusterE3_bear,
    "F2Cluster+B2B Bull": detect_f2ClusterB2B_bull,
    "F2Cluster+B2B Bear": detect_f2ClusterB2B_bear,
    "B2B+F2 Bull":        detect_b2bF2_bull,
    "B2B+F2 Bear":        detect_b2bF2_bear,
    "E3 2/3 PUP Bull":    detect_e3PUP_bull,
    "E3 2/3 PPD Bear":    detect_e3PPD_bear,
    # ─── Consecutive day ──────────────────────────────────────────────────
    "F2 B2B Days Bull":      detect_f2B2BDays_bull,
    "F2 B2B Days Bear":      detect_f2B2BDays_bear,
    "E3 B2B Days Bull":      detect_e3B2BDays_bull,
    "E3 B2B Days Bear":      detect_e3B2BDays_bear,
    "F2/E3 Consec Bull":     detect_f2e3Consec_bull,
    "F2/E3 Consec Bear":     detect_f2e3Consec_bear,
    "Cluster B2B Days Bull": detect_clusterB2BDays_bull,
    "Cluster B2B Days Bear": detect_clusterB2BDays_bear,
    # ─── HW + Any / GZ/HV + Any ───────────────────────────────────────────
    "HW+Any Bull":       detect_hwAnyBull,
    "HW+Any Bear":       detect_hwAnyBear,
    "GZ/HV+Any Bull":    detect_gzHvAnyBull,
    "GZ/HV+Any Bear":    detect_gzHvAnyBear,
    "HV+GZI Combo Bull": detect_hvGziBull,
    "HV+GZI Combo Bear": detect_hvGziBear,
    # ─── MEGAs ────────────────────────────────────────────────────────────
    "GZ/HV Mega Bull":   detect_gzHvMegaBull,
    "GZ/HV Mega Bear":   detect_gzHvMegaBear,
    "GZ1+HV Mega Bull":  detect_gz1hvMegaBull,
    "GZ1+HV Mega Bear":  detect_gz1hvMegaBear,
    # ─── Opener / 3-Bar / Foster-TB / GZ-HV+Heavy / Super-B2B-Days ────────
    "Opener Bull":        detect_openerBull,
    "Opener Bear":        detect_openerBear,
    "3Bar Bull":          detect_threeBarBull,
    "3Bar Bear":          detect_threeBarBear,
    "Foster+Heavy Bull":  detect_fosterHeavyBull,
    "TB+Heavy Bear":      detect_tbHeavyBear,
    "GZ/HV+Heavy Bull":   detect_gzHvHeavyBull,
    "GZ/HV+Heavy Bear":   detect_gzHvHeavyBear,
    "Super B2B Days Bull": detect_superB2BDays_bull,
    "Super B2B Days Bear": detect_superB2BDays_bear,
    "Nagasaki Plot":       detect_nagasakiPlot,
}


if __name__ == "__main__":
    print(f"DETECTIONS: {len(DETECTIONS)}")
    print(f"STUBBED engine notes: {len(STUBBED)}")
    print(f"STATE_MACHINES: {len(STATE_MACHINES)}")
    print("First 5 detection names:")
    for n in list(DETECTIONS)[:5]:
        print("  ", n)
