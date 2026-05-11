"""
Python port of HEAVY_PENTAGON_v1.pine (canonical RVOL roots indicator).

Source Pine:  heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine
CHANGELOG:    heavy-pentagon/CHANGELOG.md

Heavy PENTAGON is the canonical home for:

  Pipeline 1 — Standard RVOL (normalized price spike) roots:
    SAAB (Bull), Kratos (Bear), Bull RVOL 1x, Bear RVOL 1x,
    Grand Slam (Bull), MOAB (Bear)

  Pipeline 2 — Reg @ Time RVOL (time-regularized volume ratio) roots:
    Pentagon, WTC, Hiroshima

  Pipeline 3 — All-Time High Volume root:
    Nagasaki (HEV)

  Stage 5 Heavy Combo composites (15 total — Bull/Bear/Neutral each):
    Heavy Yin-Yang, Heavy Nagasaki, Heavy Nagasaki Vol,
    Heavy Trident, Neutral Heavy x2

  Internal displacement-direction classifier (NOT a root — helper only):
    dispBull / dispBear / noDisp

Conventions (mirrors python_ports/hvd_pbj_ppd/the_only_one.py):
  - df is expected to have columns: open, high, low, close, volume.
    Index should be a monotonic int (bar index) or DatetimeIndex; bar order
    must be ascending.
  - Each detection function returns a pd.Series[bool] aligned to df.index.
  - IPSF (input.*) parameters live in DEFAULTS and may be overridden via the
    ``params`` dict passed to every detection.
  - Hardcoded Pine constants (NOT input.*) stay hardcoded here so future
    edits do not silently introduce drift.
  - SD-003: IPSF defaults preserved in DEFAULTS exactly as in Pine.
  - Pipeline 2 requires Pine's ``tv_ta.relativeVolume()`` — that engine is
    STUBBED. Caller must inject ``relVolRatio`` (currentVolume_reg /
    pastVolume_reg) via ``df.attrs["relVolRatio"]``. Without it, Pipeline 2
    roots (Pentagon, WTC, Hiroshima) and every composite that consumes them
    (Heavy Yin-Yang, Heavy Nagasaki Vol, Heavy Trident, Neutral Heavy x2)
    will return all-False.

This module is import-only safe; it does NOT contain tests. The harness
runs validation tests separately.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd

# ============================================================================
# IPSF DEFAULTS — mirror Pine input.* defaults exactly (SD-003).
# ============================================================================
DEFAULTS: Dict = {
    # ── GLOBAL PLOT/ALERT TOGGLES — Standalone 10 ───────────────────────────
    "show_SAAB": False,
    "show_Kratos": False,
    "show_BullRVOL1x": False,
    "show_BearRVOL1x": False,
    "show_GrandSlam": True,
    "show_MOAB": True,
    "show_Pentagon": False,
    "show_WTC": True,
    "show_Hiroshima": True,
    "show_Nagasaki": True,

    # ── Phantom toggles (reserved — no logic connected in Pine) ─────────────
    "show_FAUNABull": False, "show_FAUNABear": False,
    "show_DISPABull": False, "show_DISPABear": False,
    "show_DISPBBull": False, "show_DISPBBear": False,
    "show_DISPCBull": False, "show_DISPCBear": False,
    "show_Long1": False, "show_Short1": False,
    "show_Long2": False, "show_Short2": False,
    "show_HV75": False, "show_HV150": False, "show_HV250": False,
    "show_HV500": False, "show_HV1000": False, "show_HotSpot": False,

    # ── HEAVY COMBO TOGGLES (all True by default in Pine) ───────────────────
    "show_HYYBull": True, "show_HYYBear": True, "show_HYYNeutral": True,
    "show_HNBull": True, "show_HNBear": True, "show_HNNeutral": True,
    "show_HNVBull": True, "show_HNVBear": True, "show_HNVNeutral": True,
    "show_HTBull": True, "show_HTBear": True, "show_HTNeutral": True,
    "show_NHx2Bull": True, "show_NHx2Bear": True, "show_NHx2Neutral": True,

    # ── Pipeline 1 — Standard RVOL Bull/Bear ────────────────────────────────
    "bb_avgLength": 30,
    "bb_smaLength": 20,

    # ── Pipeline 2 — Reg @ Time RVOL ────────────────────────────────────────
    "reg_anchorTimeframe": "",          # blank = chart TF
    "reg_length": 30,
    "reg_calculationMode": "Cumulative",  # "Cumulative" | "Regular"
    "reg_adjustRealtime": True,

    # ── Displacement engine (building block) ────────────────────────────────
    "disp_strength": 6.0,
    "disp_lookback": 100,
    "threshPct": 2.0,
    "auto": True,

    # ── Bar timeframe in seconds (caller supplies; defaults to 60s = 1m) ────
    "tfSec": 60,
}


# ============================================================================
# _helpers — utilities (mirror the_only_one.py)
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


def _sma(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=length).mean()


def _nz_f(s: pd.Series, fill: float = 0.0) -> pd.Series:
    """Pine nz(floatSeries[, fill])."""
    return s.fillna(fill)


def _conf(df: pd.DataFrame) -> pd.Series:
    """Pine ``barstate.isconfirmed`` — for historical bars this is True everywhere."""
    return pd.Series(True, index=df.index)


# ============================================================================
# RVOL threshold tables — verbatim from Pine source lines 121-160.
# These are HARDCODED in Pine (not input.*), so they stay hardcoded here.
# ============================================================================
def _rvol_1x_threshold(tfsec: float) -> float:
    """f_rvol_1x_threshold — Pine lines 121-141."""
    s = float(tfsec)
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
    if s <= 900:  return 8.4
    if s <= 1800: return 6.9
    if s <= 3600: return 5.9
    if s <= 7200: return 3.0
    return 1.8


def _saab_kratos_threshold(tfsec: float) -> float:
    """Pine line 143."""
    return _rvol_1x_threshold(tfsec) * 0.56


def _gs_moab_threshold(tfsec: float) -> float:
    """f_gs_moab_threshold — Pine lines 145-156."""
    s = float(tfsec)
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


def _wtc_threshold(tfsec: float) -> float:
    """Pine line 158."""
    return _rvol_1x_threshold(tfsec) * 2.0


def _hiroshima_threshold(tfsec: float) -> float:
    """Pine line 159 — Hiroshima reuses the Grand Slam / MOAB threshold table."""
    return _gs_moab_threshold(tfsec)


# ============================================================================
# _engines — vectorized building blocks.
# Compute all shared signals once and cache on df.attrs so repeated detection
# calls are cheap.
# ============================================================================
def _ensure_engines(df: pd.DataFrame, params: Dict) -> Dict[str, pd.Series]:
    """Compute all root + composite signal series once and cache on df.attrs."""
    cache = df.attrs.setdefault("_heavy_pentagon_eng", {})
    cache_key = (
        "v1",
        id(df),
        tuple(sorted(
            (k, v) for k, v in params.items()
            if isinstance(v, (int, float, str, bool))
        )),
    )
    if cache.get("_key") == cache_key and "sigSAAB" in cache:
        return cache
    cache.clear()
    cache["_key"] = cache_key

    p = params
    conf = _conf(df)
    tfSec = float(p["tfSec"])

    # ── THRESHOLDS (per-tf scalars; broadcast as float) ────────────────────
    th_saab_kratos = _saab_kratos_threshold(tfSec)
    th_1x          = _rvol_1x_threshold(tfSec)
    th_gs_moab     = _gs_moab_threshold(tfSec)
    th_wtc         = _wtc_threshold(tfSec)
    th_hiroshima   = _hiroshima_threshold(tfSec)

    # =====================================================================
    # PIPELINE 1: RVOL Bull/Bear (Standard — Normalized Price Spike)
    # Pine lines 110-190.
    # =====================================================================
    o = df["open"].astype(float)
    h = df["high"].astype(float)
    l = df["low"].astype(float)
    c = df["close"].astype(float)
    vol = df["volume"].astype(float)

    bb_avgLength = int(p["bb_avgLength"])
    bb_smaLength = int(p["bb_smaLength"])

    bb_spike = (c - o).abs()
    # Pine: ta.sma(bb_spike, bb_avgLength)[1]  →  SMA shifted 1 bar
    bb_avgSpikeDenom = _sma(bb_spike, bb_avgLength).shift(1)
    # nz(bb_avgSpikeDenom, 1.0)
    bb_avgSpikeDenom = bb_avgSpikeDenom.where(bb_avgSpikeDenom.notna(), 1.0)
    bb_normalizedPrice = bb_spike / bb_avgSpikeDenom

    bb_avgVolDenom = _sma(vol, bb_avgLength).shift(1)
    bb_avgVolDenom = bb_avgVolDenom.where(bb_avgVolDenom.notna(), 1.0)
    bb_normalizedVolume = vol / bb_avgVolDenom

    bb_diff = bb_normalizedPrice - bb_normalizedVolume
    # bb_positiveDiff = diff > 0 ? diff : na
    bb_positiveDiff = bb_diff.where(bb_diff > 0, np.nan)
    # ta.sma over a series that may contain NaN — Pine ta.sma skips na values.
    # rolling.mean() in pandas also skips NaN by default.
    bb_smaDiff = bb_positiveDiff.rolling(bb_smaLength, min_periods=bb_smaLength).mean()

    # bb_baseBullish/Bearish: NaN-aware comparison — NaN > NaN is False, matches Pine.
    bb_baseBullish = (c > o) & (bb_positiveDiff > bb_smaDiff)
    bb_baseBearish = (c < o) & (bb_positiveDiff > bb_smaDiff)

    # Pine bb_inRange(v, lowTh, highTh) => v >= lowTh and v < highTh
    in_saab = (bb_normalizedPrice >= th_saab_kratos) & (bb_normalizedPrice < th_1x)
    in_1x   = (bb_normalizedPrice >= th_1x)          & (bb_normalizedPrice < th_gs_moab)

    sigSAAB       = conf & bb_baseBullish & in_saab
    sigKratos     = conf & bb_baseBearish & in_saab
    sigBullRVOL1x = conf & bb_baseBullish & in_1x
    sigBearRVOL1x = conf & bb_baseBearish & in_1x
    sigGrandSlam  = conf & bb_baseBullish & (bb_normalizedPrice >= th_gs_moab)
    sigMOAB       = conf & bb_baseBearish & (bb_normalizedPrice >= th_gs_moab)

    # =====================================================================
    # PIPELINE 2: RVOL Reg @ Time (Time-Regularized Volume Ratio)
    # Pine lines 192-210.
    #
    # tv_ta.relativeVolume() is a TradingView library call that requires
    # request.security-style multi-tf state machinery. We cannot reproduce
    # it standalone. Caller MUST inject ``relVolRatio`` via df.attrs.
    # If absent, Pipeline 2 roots default to all-False.
    # =====================================================================
    if "relVolRatio" in df.attrs:
        relVolRatio = pd.Series(df.attrs["relVolRatio"], index=df.index).astype(float)
        sigPentagon  = conf & (relVolRatio >= th_1x)       & (relVolRatio <= th_wtc)
        sigWTC       = conf & (relVolRatio >  th_wtc)      & (relVolRatio <= th_hiroshima)
        sigHiroshima = conf & (relVolRatio >  th_hiroshima)
    else:
        false_s = pd.Series(False, index=df.index)
        sigPentagon  = false_s.copy()
        sigWTC       = false_s.copy()
        sigHiroshima = false_s.copy()

    # =====================================================================
    # PIPELINE 3: NAGASAKI (All-Time High Volume) — Pine lines 212-229.
    # Streaming all-time-high tracker on volume itself (NOT vsh shifted).
    # Pine semantics:
    #   var maxVol = 0.0
    #   if conf:
    #     if bar_index == 0:  maxVol := vol           (no fire)
    #     elif vol > maxVol:  isNagasaki := true; maxVol := vol
    # =====================================================================
    isNagasaki = np.zeros(len(df), dtype=bool)
    vol_arr = vol.to_numpy()
    max_vol = 0.0
    for i in range(len(vol_arr)):
        v = vol_arr[i]
        if v is None or (isinstance(v, float) and np.isnan(v)):
            continue
        if i == 0:
            max_vol = v
        elif v > max_vol:
            isNagasaki[i] = True
            max_vol = v
    sigNagasaki = conf & pd.Series(isNagasaki, index=df.index)

    # =====================================================================
    # DISPLACEMENT ENGINE (building block — NOT a root).
    # Pine lines 231-256.
    # =====================================================================
    disp_strength = float(p["disp_strength"])
    disp_lookback = int(p["disp_lookback"])
    threshPct_v   = float(p["threshPct"])
    auto_v        = bool(p["auto"])

    # bar_index: 0..N-1 (use np.arange so divisions match Pine)
    bar_index = np.arange(len(df), dtype=float)
    # ta.cum((high - low) / low)
    range_over_low = ((h - l) / l).fillna(0.0)
    cum_rol = range_over_low.cumsum()
    # bar_index 0 → division by zero in Pine yields na; treat as 0 thresh.
    with np.errstate(divide="ignore", invalid="ignore"):
        auto_thresh = np.where(bar_index > 0, cum_rol.to_numpy() / np.where(bar_index == 0, 1.0, bar_index), 0.0)
    auto_thresh = pd.Series(auto_thresh, index=df.index)
    thresh = auto_thresh if auto_v else pd.Series(threshPct_v / 100.0, index=df.index)

    h_2 = h.shift(2)
    l_2 = l.shift(2)
    c_1 = c.shift(1)

    # bFVG: low > high[2] and close[1] > high[2] and (low - high[2]) / high[2] > thresh
    bFVG = (l > h_2) & (c_1 > h_2) & (((l - h_2) / h_2) > thresh)
    # sFVG: high < low[2] and close[1] < low[2] and (low[2] - high) / high > thresh
    sFVG = (h < l_2) & (c_1 < l_2) & (((l_2 - h) / h) > thresh)
    bFVG = bFVG.fillna(False)
    sFVG = sFVG.fillna(False)

    # Bar range at bar[1]
    barRange_d = (h.shift(1) - l.shift(1))
    rangeStdev = _stdev(h - l, disp_lookback)
    # nz(rangeStdev[1])
    rangeStdev_1 = _nz_f(rangeStdev.shift(1), 0.0)
    dispCandleMet = barRange_d > (disp_strength * rangeStdev_1)
    dispCandleMet = dispCandleMet.fillna(False)

    o_1 = o.shift(1)
    bull_bar_1 = (c_1 > o_1).fillna(False)
    bear_bar_1 = (c_1 < o_1).fillna(False)

    dispBull = conf & dispCandleMet & bull_bar_1 & bFVG
    dispBear = conf & dispCandleMet & bear_bar_1 & sFVG
    noDisp   = (~dispBull) & (~dispBear)

    # =====================================================================
    # STAGE 5: HEAVY COMBO DETECTIONS (Pine lines 258-315).
    # =====================================================================
    groupA_Bull = sigBullRVOL1x | sigGrandSlam
    groupA_Bear = sigBearRVOL1x | sigMOAB
    groupB      = sigPentagon | sigWTC | sigHiroshima

    baseYinYang   = (groupA_Bull | groupA_Bear) & groupB
    baseNagasaki  = sigNagasaki & (groupA_Bull | groupA_Bear)
    baseNagasakiV = sigNagasaki & groupB
    baseTrident   = sigNagasaki & (groupA_Bull | groupA_Bear) & groupB
    # baseNHx2 — VALIDATE 9 (docs/validation/2026-05-10-floor-heavy-nagasaki-cross.md
    # §"NEUTRAL_HEAVY_X2 always-False suspicion"):
    #   baseNHx2 = (P AND W) OR (P AND H) OR (W AND H)
    # where P=sigPentagon, W=sigWTC, H=sigHiroshima are three NON-OVERLAPPING
    # band conditions (mutually exclusive disjoint relVolRatio ranges). Only
    # one of P/W/H can fire on any given bar, so each AND-pair is
    # structurally always-False, hence baseNHx2 is structurally always-False.
    # Pending TV firing confirmation; ported here verbatim per "no
    # semantic-drift without approval" policy.
    baseNHx2 = (sigPentagon & sigWTC) | (sigPentagon & sigHiroshima) | (sigWTC & sigHiroshima)

    # Heavy Yin-Yang (P1 + P2)
    sigHYYBull    = baseYinYang   & dispBull
    sigHYYBear    = baseYinYang   & dispBear
    sigHYYNeutral = baseYinYang   & noDisp
    # Heavy Nagasaki (P3 + P1)
    sigHNBull     = baseNagasaki  & dispBull
    sigHNBear     = baseNagasaki  & dispBear
    sigHNNeutral  = baseNagasaki  & noDisp
    # Heavy Nagasaki Vol (P3 + P2)
    sigHNVBull    = baseNagasakiV & dispBull
    sigHNVBear    = baseNagasakiV & dispBear
    sigHNVNeutral = baseNagasakiV & noDisp
    # Heavy Trident (P1 + P2 + P3)
    sigHTBull     = baseTrident   & dispBull
    sigHTBear     = baseTrident   & dispBear
    sigHTNeutral  = baseTrident   & noDisp
    # Neutral Heavy x2 (P2 × 2) — see baseNHx2 caveat above.
    sigNHx2Bull    = baseNHx2 & dispBull
    sigNHx2Bear    = baseNHx2 & dispBear
    sigNHx2Neutral = baseNHx2 & noDisp

    # =====================================================================
    # FIRE BOOLEANS — show_* checkbox AND signal (matches Pine 1:1).
    # =====================================================================
    def _b(name: str) -> bool:
        return bool(p[name])

    fire_SAAB       = sigSAAB       & _b("show_SAAB")
    fire_Kratos     = sigKratos     & _b("show_Kratos")
    fire_BullRVOL1x = sigBullRVOL1x & _b("show_BullRVOL1x")
    fire_BearRVOL1x = sigBearRVOL1x & _b("show_BearRVOL1x")
    fire_GrandSlam  = sigGrandSlam  & _b("show_GrandSlam")
    fire_MOAB       = sigMOAB       & _b("show_MOAB")
    fire_Pentagon   = sigPentagon   & _b("show_Pentagon")
    fire_WTC        = sigWTC        & _b("show_WTC")
    fire_Hiroshima  = sigHiroshima  & _b("show_Hiroshima")
    fire_Nagasaki   = sigNagasaki   & _b("show_Nagasaki")

    fire_HYYBull    = sigHYYBull    & _b("show_HYYBull")
    fire_HYYBear    = sigHYYBear    & _b("show_HYYBear")
    fire_HYYNeutral = sigHYYNeutral & _b("show_HYYNeutral")
    fire_HNBull     = sigHNBull     & _b("show_HNBull")
    fire_HNBear     = sigHNBear     & _b("show_HNBear")
    fire_HNNeutral  = sigHNNeutral  & _b("show_HNNeutral")
    fire_HNVBull    = sigHNVBull    & _b("show_HNVBull")
    fire_HNVBear    = sigHNVBear    & _b("show_HNVBear")
    fire_HNVNeutral = sigHNVNeutral & _b("show_HNVNeutral")
    fire_HTBull     = sigHTBull     & _b("show_HTBull")
    fire_HTBear     = sigHTBear     & _b("show_HTBear")
    fire_HTNeutral  = sigHTNeutral  & _b("show_HTNeutral")
    fire_NHx2Bull    = sigNHx2Bull    & _b("show_NHx2Bull")
    fire_NHx2Bear    = sigNHx2Bear    & _b("show_NHx2Bear")
    fire_NHx2Neutral = sigNHx2Neutral & _b("show_NHx2Neutral")

    # ── Stash everything ────────────────────────────────────────────────
    cache.update({
        # P1 roots (signal-level)
        "sigSAAB": sigSAAB, "sigKratos": sigKratos,
        "sigBullRVOL1x": sigBullRVOL1x, "sigBearRVOL1x": sigBearRVOL1x,
        "sigGrandSlam": sigGrandSlam, "sigMOAB": sigMOAB,
        # P2 roots
        "sigPentagon": sigPentagon, "sigWTC": sigWTC, "sigHiroshima": sigHiroshima,
        # P3 root
        "sigNagasaki": sigNagasaki,
        # Displacement helper (NOT a root)
        "dispBull": dispBull, "dispBear": dispBear, "noDisp": noDisp,
        # 15 composites — signal level
        "sigHYYBull": sigHYYBull, "sigHYYBear": sigHYYBear, "sigHYYNeutral": sigHYYNeutral,
        "sigHNBull": sigHNBull, "sigHNBear": sigHNBear, "sigHNNeutral": sigHNNeutral,
        "sigHNVBull": sigHNVBull, "sigHNVBear": sigHNVBear, "sigHNVNeutral": sigHNVNeutral,
        "sigHTBull": sigHTBull, "sigHTBear": sigHTBear, "sigHTNeutral": sigHTNeutral,
        "sigNHx2Bull": sigNHx2Bull, "sigNHx2Bear": sigNHx2Bear, "sigNHx2Neutral": sigNHx2Neutral,
        # Base helpers (handy for cross-validation tooling)
        "baseYinYang": baseYinYang, "baseNagasaki": baseNagasaki,
        "baseNagasakiV": baseNagasakiV, "baseTrident": baseTrident, "baseNHx2": baseNHx2,
        # Fire booleans (checkbox AND signal)
        "fire_SAAB": fire_SAAB, "fire_Kratos": fire_Kratos,
        "fire_BullRVOL1x": fire_BullRVOL1x, "fire_BearRVOL1x": fire_BearRVOL1x,
        "fire_GrandSlam": fire_GrandSlam, "fire_MOAB": fire_MOAB,
        "fire_Pentagon": fire_Pentagon, "fire_WTC": fire_WTC,
        "fire_Hiroshima": fire_Hiroshima, "fire_Nagasaki": fire_Nagasaki,
        "fire_HYYBull": fire_HYYBull, "fire_HYYBear": fire_HYYBear, "fire_HYYNeutral": fire_HYYNeutral,
        "fire_HNBull": fire_HNBull, "fire_HNBear": fire_HNBear, "fire_HNNeutral": fire_HNNeutral,
        "fire_HNVBull": fire_HNVBull, "fire_HNVBear": fire_HNVBear, "fire_HNVNeutral": fire_HNVNeutral,
        "fire_HTBull": fire_HTBull, "fire_HTBear": fire_HTBear, "fire_HTNeutral": fire_HTNeutral,
        "fire_NHx2Bull": fire_NHx2Bull, "fire_NHx2Bear": fire_NHx2Bear, "fire_NHx2Neutral": fire_NHx2Neutral,
        # Threshold scalars (handy for debugging)
        "th_saab_kratos": th_saab_kratos, "th_1x": th_1x, "th_gs_moab": th_gs_moab,
        "th_wtc": th_wtc, "th_hiroshima": th_hiroshima,
    })
    return cache


# ============================================================================
# Detection-function builder — each detect_* returns a bool Series aligned
# to df.index.  Names mirror Pine plot titles so the harness can round-trip
# with the validator.
# ============================================================================
def _wrap(key: str) -> Callable:
    """Wrap an _ensure_engines cache key as a detect_* function."""
    def _fn(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
        p = _p(params)
        eng = _ensure_engines(df, p)
        s = eng[key]
        return s.fillna(False).astype(bool)
    _fn.__name__ = f"detect_{key}"
    return _fn


# ─── Pipeline 1 — Standard RVOL roots ───────────────────────────────────────
detect_SAAB         = _wrap("fire_SAAB")
detect_Kratos       = _wrap("fire_Kratos")
detect_BullRVOL1x   = _wrap("fire_BullRVOL1x")
detect_BearRVOL1x   = _wrap("fire_BearRVOL1x")
detect_GrandSlam    = _wrap("fire_GrandSlam")
detect_MOAB         = _wrap("fire_MOAB")

# ─── Pipeline 2 — Reg @ Time RVOL roots ─────────────────────────────────────
detect_Pentagon     = _wrap("fire_Pentagon")
detect_WTC          = _wrap("fire_WTC")
detect_Hiroshima    = _wrap("fire_Hiroshima")

# ─── Pipeline 3 — All-Time High Volume root ─────────────────────────────────
# Pine title is "Nagasaki (HEV)" with both names canonical. We register both
# aliases pointing to the same firing series.
detect_Nagasaki     = _wrap("fire_Nagasaki")
detect_HEV          = _wrap("fire_Nagasaki")

# ─── Internal helper (NOT a root) — displacement direction classifier ───────
def detect_dispBull(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
    """Internal helper: bar[1] bullish disp candle + bar[0] bullish FVG."""
    p = _p(params)
    return _ensure_engines(df, p)["dispBull"].fillna(False).astype(bool)


def detect_dispBear(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
    """Internal helper: bar[1] bearish disp candle + bar[0] bearish FVG."""
    p = _p(params)
    return _ensure_engines(df, p)["dispBear"].fillna(False).astype(bool)


def detect_noDisp(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
    """Internal helper: neither dispBull nor dispBear."""
    p = _p(params)
    return _ensure_engines(df, p)["noDisp"].fillna(False).astype(bool)


# ─── 15 Heavy Combo composites ──────────────────────────────────────────────
detect_HYYBull      = _wrap("fire_HYYBull")
detect_HYYBear      = _wrap("fire_HYYBear")
detect_HYYNeutral   = _wrap("fire_HYYNeutral")

detect_HNBull       = _wrap("fire_HNBull")
detect_HNBear       = _wrap("fire_HNBear")
detect_HNNeutral    = _wrap("fire_HNNeutral")

detect_HNVBull      = _wrap("fire_HNVBull")
detect_HNVBear      = _wrap("fire_HNVBear")
detect_HNVNeutral   = _wrap("fire_HNVNeutral")

detect_HTBull       = _wrap("fire_HTBull")
detect_HTBear       = _wrap("fire_HTBear")
detect_HTNeutral    = _wrap("fire_HTNeutral")

detect_NHx2Bull     = _wrap("fire_NHx2Bull")
detect_NHx2Bear     = _wrap("fire_NHx2Bear")
detect_NHx2Neutral  = _wrap("fire_NHx2Neutral")


# ============================================================================
# Stubbed sub-engines — Pine-only intrinsics required.
# Keys are conceptual; values describe the inject path.
# ============================================================================
STUBBED: Dict[str, str] = {
    # tv_ta.relativeVolume — Pipeline 2's relVolRatio. Inject via
    # df.attrs["relVolRatio"] (numeric Series aligned to df.index). Without
    # it, sigPentagon / sigWTC / sigHiroshima default to all-False, and
    # every composite that depends on them (Heavy Yin-Yang, Heavy Nagasaki
    # Vol, Heavy Trident, Neutral Heavy x2) also returns all-False.
    "_rel_vol_engine": (
        "tv_ta.relativeVolume(reg_length, reg_anchorTimeframe, isCumulative, "
        "adjustRealtime) not reproduced — requires TradingView's anchor-TF "
        "rollup state machine. Inject relVolRatio via df.attrs."
    ),
}


# ============================================================================
# DETECTIONS registry — name → detect_* function.
# Names mirror Pine plotshape titles for round-trip with the validator.
# ============================================================================
DETECTIONS: Dict[str, Callable] = {
    # ── Pipeline 1 — Standard RVOL roots (6) ─────────────────────────────
    "SAAB": detect_SAAB,
    "Kratos": detect_Kratos,
    "Bull RVOL 1x": detect_BullRVOL1x,
    "Bear RVOL 1x": detect_BearRVOL1x,
    "Grand Slam": detect_GrandSlam,
    "MOAB": detect_MOAB,
    # ── Pipeline 2 — Reg @ Time RVOL roots (3) ───────────────────────────
    "Pentagon": detect_Pentagon,
    "WTC": detect_WTC,
    "Hiroshima": detect_Hiroshima,
    # ── Pipeline 3 — All-Time High Volume root (1) ───────────────────────
    "Nagasaki (HEV)": detect_Nagasaki,
    # ── 15 Heavy Combo composites ────────────────────────────────────────
    "Heavy Yin-Yang Bull": detect_HYYBull,
    "Heavy Yin-Yang Bear": detect_HYYBear,
    "Heavy Yin-Yang Neutral": detect_HYYNeutral,
    "Heavy Nagasaki Bull": detect_HNBull,
    "Heavy Nagasaki Bear": detect_HNBear,
    "Heavy Nagasaki Neutral": detect_HNNeutral,
    "Heavy Nagasaki Vol Bull": detect_HNVBull,
    "Heavy Nagasaki Vol Bear": detect_HNVBear,
    "Heavy Nagasaki Vol Neutral": detect_HNVNeutral,
    "Heavy Trident Bull": detect_HTBull,
    "Heavy Trident Bear": detect_HTBear,
    "Heavy Trident Neutral": detect_HTNeutral,
    "Neutral Heavy x2 Bull": detect_NHx2Bull,
    "Neutral Heavy x2 Bear": detect_NHx2Bear,
    "Neutral Heavy x2 Neutral": detect_NHx2Neutral,
}


if __name__ == "__main__":
    print(f"DETECTIONS: {len(DETECTIONS)}")
    print(f"STUBBED engine notes: {len(STUBBED)}")
    print("Detection names:")
    for n in DETECTIONS:
        print("  ", n)
