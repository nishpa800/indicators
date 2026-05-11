"""HVD+PBJ+PPD — port of HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine

This module ports the detection booleans of the 2246-line master-dir variant
of HVD+PBJ+PPD. Conventions match sibling ports:

  * Per-detection function: detect_<snake_case_name>(df, params=None) -> pd.Series
  * Stateful detections (PBJ lander, PingPong SR, Combo Chain, etc.) are
    wrapped in classes whose `process(df)` returns a `pd.Series` of bool.
  * IPSF (input.*) defaults live in DEFAULTS.
  * Hardcoded thresholds inside engine bodies stay hardcoded (not in DEFAULTS).
  * Anything that requires the full PB-lander / SR / GZ1 / Combo Chain state
    machine is registered as a class instance in STATE_MACHINES; its
    detect_* wrapper calls process() and returns the bool series.
  * Detections that depend on runtime side-effects (alerts) are skipped.
  * Detections that are not yet pure-pandas because they need bar-by-bar
    array push/pop machinery (PB lander boxes, GZ1 FVG list, PingPong SR
    array) are listed in STUBBED with a `NotImplementedError` body — the
    parent compiler can swap these out later.

Module exports: DETECTIONS, STATE_MACHINES, STUBBED.

UNIQUE_TO_2246 markers: there are NO detection plots that exist only in the
2246 file (its full detection set is shared with the two 1939-line siblings).
The cross-agent compiler can confirm by greping for the comment marker.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

import math

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# DEFAULTS — IPSF tunables only. Hardcoded engine constants stay hardcoded.
# ---------------------------------------------------------------------------

DEFAULTS: Dict[str, object] = {
    # Pipeline A — HV+D Disp 1 (Base)
    "d1_type": "Open to Close",
    "d1_len": 100,
    "d1_mult": 5.0,
    # Pipeline A — HV+D Disp 2 (HTF1)
    "d2_type": "Open to Close",
    "d2_len": 100,
    "d2_mult": 4.0,
    # Pipeline A — HV+D Disp 3 (HTF2)
    "d3_type": "Open to Close",
    "d3_len": 100,
    "d3_mult": 2.5,
    # Pipeline A — Base HV bar lookbacks (all true by default)
    "ub50": True, "ub75": True, "ub100": True, "ub150": True, "ub200": True,
    "ub250": True, "ub300": True, "ub350": True, "ub400": True, "ub450": True,
    "ub500": True, "ub550": True, "ub600": True, "ub650": True, "ub700": True,
    "ub750": True, "ub1000": True, "useHEV": True,
    # Pipeline A — HTF Profile 1
    "h1On": True, "h1From": "15 Min", "h1To": "2 Hour",
    "uh1_5": False, "uh1_10": False, "uh1_20": True, "uh1_25": True, "uh1_30": True,
    "uh1_40": True, "uh1_50": True, "uh1_60": True, "uh1_70": True,
    "uh1_75": True, "uh1_80": True, "uh1_90": True,
    # Pipeline A — HTF Profile 2
    "h2On": True, "h2From": "2 Hour", "h2To": "3 Month",
    "uh2_5": True, "uh2_10": True, "uh2_20": True, "uh2_25": True, "uh2_30": True,
    "uh2_40": True, "uh2_50": True, "uh2_60": True, "uh2_70": True,
    "uh2_75": True, "uh2_80": True, "uh2_90": True,
    # USE displacement
    "i_disp_type": "Open to Close",
    "i_std_len": 100, "i_std_min": 4.5, "i_std_max": 100.0, "i_req_fvg": True,
    # USE Disp 2+
    "i_disp2_type": "Open to Close",
    "i_disp2_std_len": 100, "i_disp2_std_min": 5.0, "i_disp2_std_max": 100.0,
    "i_disp2_req_fvg": True,
    # USE Disp 3+
    "i_disp3_type": "Open to Close",
    "i_disp3_std_len": 100, "i_disp3_std_min": 3.0, "i_disp3_std_max": 100.0,
    "i_disp3_req_fvg": True,
    # GZ1 / HV FVG
    "gz1_auto": True, "gz1_thresh": 2.0, "gz1_dist": 12,
    # HV Settings
    "hv150_len": 150,
    # Swingin (Pivot)
    "sw_leftBars": 5, "sw_rightBars": 1, "sw_useAtr": True, "sw_atrMult": 2.0,
    "pp_atr_len": 100,
    # Consecutive Streak (P21)
    "p21_pbj_dist": 4,
    # Opening Drive
    "od_max_bars": 2,
    # Matrix Number (Neo)
    "neo_len": 67,
    # Momentum 1
    "ls_reg1": 7.0, "ls_cum1": 3.5, "ls_body1": 0.69,
    # Momentum 2
    "ls_reg2": 5.0, "ls_cum2": 2.5, "ls_body2": 0.69,
    # Combo Set Settings
    "cs_bodyPct_FVG": 0.69, "cs_bodyPct_MAT": 0.69,
    "cs_inc_pentagon_FVG": True, "cs_inc_pentagon_MAT": True,
    # Combo Chain
    "cc_min_hits": 2, "cc_window": 2,
    # Long/Short Chain
    "lsc_min_hits": 2, "lsc_window": 2,
    "lsc_reg1": 7.0, "lsc_cum1": 3.5, "lsc_body1": 0.69,
    "lsc_reg2": 5.0, "lsc_cum2": 2.5, "lsc_body2": 0.69,
    # Pipeline-D / B2B / HV+D toggles (defaults)
    "co_en_bullPBJ": True, "co_en_bullPB": True,
    "co_en_bearPBJ": True, "co_en_bearPB": True,
    "b2b_en_bull": True, "b2b_en_bear": True,
    "b2b_en_bull_pbj": True, "b2b_en_bear_pbj": True,
    "b2b_en_bull_pb": True, "b2b_en_bear_pb": True,
    "en_hvd_bull": True, "en_hvd_bear": True,
    "en_hvd_pb_bull": True, "en_hvd_pb_bear": True,
    "en_hvd_pbj_bull": True, "en_hvd_pbj_bear": True,
    # HVDM toggles
    "en_hvdm_pup_bull": True, "en_hvdm_ppd_bear": True,
    "en_hvdm_rvol_bull": True, "en_hvdm_rvol_bear": True,
    "en_hvdm_cmb_bull": True, "en_hvdm_cmb_bear": True,
    "en_hvdm_2of3_bull": True, "en_hvdm_2of3_bear": True,
    "en_hvdm_3of3_bull": True, "en_hvdm_3of3_bear": True,
    # Tier-1..Tier-3 show toggles (all default true)
    "show_BullUUUU": True, "show_BearUUUU": True,
    "show_BullUUU": True, "show_BearUUU": True,
    "show_BullUU": True, "show_BearUU": True,
    "show_OmegaLongA": True, "show_OmegaLong": True,
    "show_AlphaStrikeB": True, "show_AlphaStrikeR": True,
    "show_FoxtrotB": True, "show_FoxtrotR": True,
    "show_ODBull": True, "show_ODBear": True,
    "show_DispConsBull2": True, "show_DispConsBear2": True,
    "show_DispConsBull3": True, "show_DispConsBear3": True,
    "show_GolfBull": True, "show_GolfBear": True,
    "show_PAFBull": True, "show_PAFBear": True,
    "show_CS1B": True, "show_CS1R": True,
    "show_CS2B": True, "show_CS2R": True,
    "show_CS3B": True, "show_CS3R": True,
    "show_CCBull": True, "show_CCBear": True,
    "show_LSCBull": True, "show_LSCBear": True,
    "show_BullFloor": True, "show_Bull2ndFloor": True,
    "show_BearRooftop": True, "show_BearPenthouse": True,
    "show_HWBull": True, "show_HWBear": True,
    "show_SuperBull": True, "show_SuperBear": True,
    "show_SDuperBull": True, "show_SDuperBear": True,
    # tfSec — must be passed in for TF-aware functions; default to 60s
    "tfSec": 60,
}


# ---------------------------------------------------------------------------
# _helpers
# ---------------------------------------------------------------------------

def _conf(df: pd.DataFrame) -> pd.Series:
    """barstate.isconfirmed equivalent — every closed historical bar is True."""
    return pd.Series(True, index=df.index)


def _stdev(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=length).std(ddof=0)


def _sma(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=length).mean()


def _ema(s: pd.Series, length: int) -> pd.Series:
    return s.ewm(span=length, adjust=False, min_periods=length).mean()


def _highest(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=length).max()


def _lowest(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=length).min()


def _atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([(h - l).abs(), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()


def _nz(s: pd.Series, fill=0.0) -> pd.Series:
    return s.fillna(fill)


def _disp_range(df: pd.DataFrame, kind: str) -> pd.Series:
    if kind == "Open to Close":
        return (df["open"] - df["close"]).abs()
    return df["high"] - df["low"]


def _params(p: Optional[Dict]) -> Dict:
    out = dict(DEFAULTS)
    if p:
        out.update(p)
    return out


# RVOL TF-second→threshold ladders (lines 443–447, hardcoded)

def f_rvol_1x_threshold(s: int) -> float:
    if s <= 10:    return 38.0
    if s <= 15:    return 33.0
    if s <= 30:    return 28.0
    if s <= 45:    return 23.0
    if s <= 60:    return 20.0
    if s <= 120:   return 18.0
    if s <= 300:   return 13.0
    if s <= 360:   return 13.0
    if s <= 540:   return 11.0
    if s <= 600:   return 10.0
    if s <= 660:   return 9.0
    if s <= 900:   return 7.5
    if s <= 1560:  return 6.5
    if s <= 2340:  return 6.0
    if s <= 3600:  return 4.5
    if s <= 9000:  return 4.0
    if s <= 11700: return 3.5
    if s < 259200: return 1.8
    return 1.0


def f_gs_moab_threshold(s: int) -> float:
    if s < 60:     return f_rvol_1x_threshold(s) * 3.0
    if s <= 300:   return 35.0
    if s <= 600:   return 25.0
    if s <= 1500:  return 20.0
    if s <= 3000:  return 20.0
    if s <= 7260:  return 10.0
    if s <= 11700: return 8.0
    if s <= 86400: return 7.5
    if s <= 259200:return 3.5
    return 3.0


def f_saab_kratos_threshold(s: int) -> float:
    return f_rvol_1x_threshold(s) * 0.56


def f_wtc_threshold(s: int) -> float:
    return f_rvol_1x_threshold(s) * 2.0


def f_hiroshima_threshold(s: int) -> float:
    if s < 60:     return f_rvol_1x_threshold(s) * 3.0
    if s <= 300:   return 35.0
    if s <= 600:   return 25.0
    if s <= 1500:  return 25.0
    if s <= 3060:  return 20.0
    if s <= 7260:  return 10.0
    if s <= 11700: return 8.0
    if s <= 86400: return 7.5
    if s <= 259200:return 5.0
    return 3.5


# ---------------------------------------------------------------------------
# Engine: BB normalized price/volume (RVOL underpinning)
# ---------------------------------------------------------------------------

def _bb_components(df: pd.DataFrame):
    """Return (bb_normalizedPrice, bb_baseBullish, bb_baseBearish)."""
    bb_avgLength = 30
    bb_smaLength = 20
    spike = (df["close"] - df["open"]).abs()
    avgSpikeDenom = _sma(spike, bb_avgLength).shift(1)
    normPrice = spike / _nz(avgSpikeDenom, 1.0)
    avgVolDenom = _sma(df["volume"], bb_avgLength).shift(1)
    normVol = df["volume"] / _nz(avgVolDenom, 1.0)
    diff = normPrice - normVol
    posDiff = diff.where(diff > 0, np.nan)
    smaDiff = posDiff.rolling(bb_smaLength, min_periods=1).mean()
    bull = (df["close"] > df["open"]) & (posDiff > smaDiff)
    bear = (df["close"] < df["open"]) & (posDiff > smaDiff)
    return normPrice.fillna(0.0), bull.fillna(False), bear.fillna(False)


# ---------------------------------------------------------------------------
# Pipeline A — HV+D
# ---------------------------------------------------------------------------

def _hv_rank_bool(df: pd.DataFrame, length: int) -> pd.Series:
    """is volume[1] == ta.highest(volume, length)[1]"""
    v_prev = df["volume"].shift(1)
    return v_prev == _highest(df["volume"], length).shift(1)


def _hvd_disp_block(df: pd.DataFrame, kind: str, length: int, mult: float):
    """Return (prevDisp, bullFVG, bearFVG, conf-and-... bull, conf-and-... bear)."""
    rng = _disp_range(df, kind)
    std = _stdev(rng, length)
    thresh = std * mult
    prevDisp = rng.shift(1) > thresh.shift(1)
    bullFVG = (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["open"].shift(1))
    bearFVG = (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["open"].shift(1))
    bull = prevDisp & bullFVG
    bear = prevDisp & bearFVG
    return prevDisp.fillna(False), bullFVG.fillna(False), bearFVG.fillna(False), bull.fillna(False), bear.fillna(False)


def _isHEV(df: pd.DataFrame) -> pd.Series:
    """volume[1] strictly greater than running max of all prior volume[1] values."""
    v_prev = df["volume"].shift(1).fillna(0.0)
    cum_max = v_prev.cummax().shift(1).fillna(-np.inf)
    return v_prev > cum_max


def detect_hvd_fire_bull(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
    """Pipeline A bullish: any of {Base + HTF1 + HTF2} combo passes."""
    p = _params(params)
    _, _, _, d1_bull, _ = _hvd_disp_block(df, p["d1_type"], p["d1_len"], p["d1_mult"])
    _, _, _, d2_bull, _ = _hvd_disp_block(df, p["d2_type"], p["d2_len"], p["d2_mult"])
    _, _, _, d3_bull, _ = _hvd_disp_block(df, p["d3_type"], p["d3_len"], p["d3_mult"])
    # Base ranks
    is50  = _hv_rank_bool(df, 50)  if p.get("ub50",  True) else pd.Series(False, index=df.index)
    is75  = _hv_rank_bool(df, 75)  if p.get("ub75",  True) else pd.Series(False, index=df.index)
    is100 = _hv_rank_bool(df, 100) if p.get("ub100", True) else pd.Series(False, index=df.index)
    is150 = _hv_rank_bool(df, 150) if p.get("ub150", True) else pd.Series(False, index=df.index)
    is200 = _hv_rank_bool(df, 200) if p.get("ub200", True) else pd.Series(False, index=df.index)
    is250 = _hv_rank_bool(df, 250) if p.get("ub250", True) else pd.Series(False, index=df.index)
    is300 = _hv_rank_bool(df, 300) if p.get("ub300", True) else pd.Series(False, index=df.index)
    is350 = _hv_rank_bool(df, 350) if p.get("ub350", True) else pd.Series(False, index=df.index)
    is400 = _hv_rank_bool(df, 400) if p.get("ub400", True) else pd.Series(False, index=df.index)
    is450 = _hv_rank_bool(df, 450) if p.get("ub450", True) else pd.Series(False, index=df.index)
    is500 = _hv_rank_bool(df, 500) if p.get("ub500", True) else pd.Series(False, index=df.index)
    is550 = _hv_rank_bool(df, 550) if p.get("ub550", True) else pd.Series(False, index=df.index)
    is600 = _hv_rank_bool(df, 600) if p.get("ub600", True) else pd.Series(False, index=df.index)
    is650 = _hv_rank_bool(df, 650) if p.get("ub650", True) else pd.Series(False, index=df.index)
    is700 = _hv_rank_bool(df, 700) if p.get("ub700", True) else pd.Series(False, index=df.index)
    is750 = _hv_rank_bool(df, 750) if p.get("ub750", True) else pd.Series(False, index=df.index)
    is1000= _hv_rank_bool(df, 1000) if p.get("ub1000", True) else pd.Series(False, index=df.index)
    base_enabled = is50 | is75 | is100 | is150 | is200 | is250 | is300 | is350 | is400 | is450 | is500 | is550 | is600 | is650 | is700 | is750 | is1000
    isHEV = _isHEV(df) if p.get("useHEV", True) else pd.Series(False, index=df.index)
    base_hv_hit = isHEV | (base_enabled & ~isHEV)
    base_combo_bull = base_hv_hit & d1_bull
    # Note: HTF profile gating omitted (would require resampling). For single-TF
    # series we approximate htf*Active = False which yields h*Rank == 0; the
    # base channel still fires.
    return base_combo_bull.fillna(False)


def detect_hvd_fire_bear(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
    p = _params(params)
    _, _, _, _, d1_bear = _hvd_disp_block(df, p["d1_type"], p["d1_len"], p["d1_mult"])
    is50  = _hv_rank_bool(df, 50)
    is75  = _hv_rank_bool(df, 75)
    is100 = _hv_rank_bool(df, 100)
    is150 = _hv_rank_bool(df, 150)
    is200 = _hv_rank_bool(df, 200)
    is250 = _hv_rank_bool(df, 250)
    is300 = _hv_rank_bool(df, 300)
    is350 = _hv_rank_bool(df, 350)
    is400 = _hv_rank_bool(df, 400)
    is450 = _hv_rank_bool(df, 450)
    is500 = _hv_rank_bool(df, 500)
    is550 = _hv_rank_bool(df, 550)
    is600 = _hv_rank_bool(df, 600)
    is650 = _hv_rank_bool(df, 650)
    is700 = _hv_rank_bool(df, 700)
    is750 = _hv_rank_bool(df, 750)
    is1000 = _hv_rank_bool(df, 1000)
    base_enabled = is50 | is75 | is100 | is150 | is200 | is250 | is300 | is350 | is400 | is450 | is500 | is550 | is600 | is650 | is700 | is750 | is1000
    isHEV = _isHEV(df) if p.get("useHEV", True) else pd.Series(False, index=df.index)
    base_hv_hit = isHEV | (base_enabled & ~isHEV)
    base_combo_bear = base_hv_hit & d1_bear
    return base_combo_bear.fillna(False)


# ---------------------------------------------------------------------------
# Engine 1 — RVOL signals (SAAB / Kratos / GS / MOAB / 1x / Pentagon / WTC /
# Hiroshima / Nagasaki)
# ---------------------------------------------------------------------------

def _rvol_panel(df: pd.DataFrame, tfSec: int):
    normPrice, baseBull, baseBear = _bb_components(df)
    th_sk = f_saab_kratos_threshold(tfSec)
    th_1x = f_rvol_1x_threshold(tfSec)
    th_gs = f_gs_moab_threshold(tfSec)
    th_wtc = f_wtc_threshold(tfSec)
    th_h = f_hiroshima_threshold(tfSec)
    in_range = lambda v, lo, hi: (v >= lo) & (v < hi)
    sigSAAB = baseBull & in_range(normPrice, th_sk, th_1x)
    sigKratos = baseBear & in_range(normPrice, th_sk, th_1x)
    sigGS = baseBull & (normPrice >= th_gs)
    sigMOAB = baseBear & (normPrice >= th_gs)
    sig1xB = baseBull & in_range(normPrice, th_1x, th_gs) & ~sigGS
    sig1xR = baseBear & in_range(normPrice, th_1x, th_gs) & ~sigMOAB
    return dict(normPrice=normPrice, baseBull=baseBull, baseBear=baseBear,
                sigSAAB=sigSAAB, sigKratos=sigKratos, sigGrandSlam=sigGS,
                sigMOAB=sigMOAB, sigBullRVOL1x=sig1xB, sigBearRVOL1x=sig1xR,
                th_1x=th_1x, th_wtc=th_wtc, th_h=th_h)


def detect_sig_grand_slam(df, params=None):
    p = _params(params); return _rvol_panel(df, int(p["tfSec"]))["sigGrandSlam"]


def detect_sig_moab(df, params=None):
    p = _params(params); return _rvol_panel(df, int(p["tfSec"]))["sigMOAB"]


def detect_sig_bull_rvol1x(df, params=None):
    p = _params(params); return _rvol_panel(df, int(p["tfSec"]))["sigBullRVOL1x"]


def detect_sig_bear_rvol1x(df, params=None):
    p = _params(params); return _rvol_panel(df, int(p["tfSec"]))["sigBearRVOL1x"]


def detect_sig_saab(df, params=None):
    p = _params(params); return _rvol_panel(df, int(p["tfSec"]))["sigSAAB"]


def detect_sig_kratos(df, params=None):
    p = _params(params); return _rvol_panel(df, int(p["tfSec"]))["sigKratos"]


def detect_sig_nagasaki(df, params=None):
    """All-time-high volume of *current* bar after first bar."""
    v = df["volume"].fillna(0.0)
    cum_max = v.cummax().shift(1).fillna(-np.inf)
    isNag = v > cum_max
    isNag.iloc[0] = False
    return isNag


# ---------------------------------------------------------------------------
# Engine 2 — FAUNA NRA
# ---------------------------------------------------------------------------

def _fauna_panel(df: pd.DataFrame):
    atr = _atr(df, 14)
    avgVol = _sma(df["volume"], 20)
    avgBody = _sma((df["close"] - df["open"]).abs(), 20)
    avgDelta = _sma((df["close"] - df["close"].shift(1)).abs(), 10)
    trendMA = _sma(df["close"], 50)
    body = df["close"] - df["open"]
    rng = df["high"] - df["low"]
    bodySz = body.abs()
    bodyRat = (bodySz / rng).fillna(0.0).where(rng != 0, 0.0)
    up = body > 0
    dn = body < 0
    prev_body = df["close"].shift(1) - df["open"].shift(1)
    prev_range = df["high"].shift(1) - df["low"].shift(1)

    MB_b = up & (bodySz > 1.6 * atr) & (bodyRat > 0.70) & (df["volume"] > 1.8 * avgVol)
    RE_b = up & (rng > 2.2 * atr) & ((df["high"] - df["close"]) < 0.15 * rng) & (df["volume"] > 1.8 * avgVol)
    TA_b = (trendMA > trendMA.shift(1)) & ((df["close"] - df["close"].shift(1)) > 1.6 * avgDelta) & up & (df["volume"] > 1.8 * avgVol)
    GG_b = ((df["open"] - df["close"].shift(1)) > 0.9 * atr) & up & (df["low"] > df["close"].shift(1)) & (df["volume"] > 1.8 * avgVol)

    StrongBear = (df["close"].shift(1) < df["open"].shift(1)) & (prev_body.abs() > 1.5 * avgBody.shift(1)) & (df["volume"].shift(1) > 1.5 * avgVol.shift(1))
    weakRat = (prev_body.abs() / prev_range).fillna(0.0).where(prev_range != 0, 0.0)
    WeakBear = (df["close"].shift(1) < df["open"].shift(1)) & (weakRat <= 0.2)
    TR_b = WeakBear & (MB_b | RE_b | TA_b)
    ES_b = StrongBear & (MB_b | RE_b | TA_b)
    GDR_b = (df["close"].shift(1) < df["open"].shift(1)) & GG_b
    b_core_cnt = MB_b.astype(int) + RE_b.astype(int) + TA_b.astype(int)
    b_gg_pass = (b_core_cnt >= 2) & (bodyRat >= 0.80)  # fauna_gg_master=true, fauna_gg_body=0.80
    b_gg_exc = GG_b & ~b_gg_pass
    excluded_bull = TR_b | ES_b | GDR_b | b_gg_exc
    sigFAUNABull = (MB_b | RE_b | TA_b) & ~excluded_bull

    MB_r = dn & (bodySz > 1.6 * atr) & (bodyRat > 0.70) & (df["volume"] > 1.8 * avgVol)
    RE_r = dn & (rng > 2.2 * atr) & ((df["close"] - df["low"]) < 0.15 * rng) & (df["volume"] > 1.8 * avgVol)
    TA_r = (trendMA < trendMA.shift(1)) & ((df["close"].shift(1) - df["close"]) > 1.6 * avgDelta) & dn & (df["volume"] > 1.8 * avgVol)
    GG_r = ((df["close"].shift(1) - df["open"]) > 0.9 * atr) & dn & (df["high"] < df["close"].shift(1)) & (df["volume"] > 1.8 * avgVol)
    StrongBull = (df["close"].shift(1) > df["open"].shift(1)) & (prev_body.abs() > 1.5 * avgBody.shift(1)) & (df["volume"].shift(1) > 1.5 * avgVol.shift(1))
    WeakBull = (df["close"].shift(1) > df["open"].shift(1)) & (weakRat <= 0.2)
    TR_r = WeakBull & (MB_r | RE_r | TA_r)
    ES_r = StrongBull & (MB_r | RE_r | TA_r)
    GDR_r = (df["close"].shift(1) > df["open"].shift(1)) & GG_r
    s_core_cnt = MB_r.astype(int) + RE_r.astype(int) + TA_r.astype(int)
    s_gg_pass = (s_core_cnt >= 2) & (bodyRat >= 0.80)
    s_gg_exc = GG_r & ~s_gg_pass
    excluded_bear = TR_r | ES_r | GDR_r | s_gg_exc
    sigFAUNABear = (MB_r | RE_r | TA_r) & ~excluded_bear

    return sigFAUNABull.fillna(False), sigFAUNABear.fillna(False)


def detect_sig_fauna_bull(df, params=None):
    return _fauna_panel(df)[0]


def detect_sig_fauna_bear(df, params=None):
    return _fauna_panel(df)[1]


def detect_sig_foxtrot_bull(df, params=None):
    """4 consecutive FAUNA-bull bars."""
    f_bull, _ = _fauna_panel(df)
    return f_bull & f_bull.shift(1).fillna(False) & f_bull.shift(2).fillna(False) & f_bull.shift(3).fillna(False)


def detect_sig_foxtrot_bear(df, params=None):
    _, f_bear = _fauna_panel(df)
    return f_bear & f_bear.shift(1).fillna(False) & f_bear.shift(2).fillna(False) & f_bear.shift(3).fillna(False)


# ---------------------------------------------------------------------------
# Engine 3 — USE Displacement (sigDISPBull/Bear, disp5_bull/bear,
# DISP2 streak + FAUNA window, DISP3 streak + FAUNA window)
# ---------------------------------------------------------------------------

def _disp_block(df, kind, length, mn, mx, req_fvg):
    rng = _disp_range(df, kind)
    std = _stdev(rng, length)
    prev_in = (rng.shift(1) > std.shift(1) * mn) & (rng.shift(1) <= std.shift(1) * mx)
    curr_in = (rng > std * mn) & (rng <= std * mx)
    bullFVG = (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["open"].shift(1))
    bearFVG = (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["open"].shift(1))
    if req_fvg:
        bull = prev_in & bullFVG
        bear = prev_in & bearFVG
    else:
        bull = curr_in & (df["close"] > df["open"])
        bear = curr_in & (df["close"] < df["open"])
    return bull.fillna(False), bear.fillna(False), std


def detect_sig_disp_bull(df, params=None):
    p = _params(params)
    bull, _, _ = _disp_block(df, p["i_disp_type"], p["i_std_len"], p["i_std_min"], p["i_std_max"], p["i_req_fvg"])
    return bull


def detect_sig_disp_bear(df, params=None):
    p = _params(params)
    _, bear, _ = _disp_block(df, p["i_disp_type"], p["i_std_len"], p["i_std_min"], p["i_std_max"], p["i_req_fvg"])
    return bear


def _streak(s: pd.Series) -> pd.Series:
    """Run-length up to and including the current True bar; reset on False."""
    out = np.zeros(len(s), dtype=int)
    run = 0
    for i, v in enumerate(s.fillna(False).values):
        if v:
            run += 1
        else:
            run = 0
        out[i] = run
    return pd.Series(out, index=s.index)


def detect_sig_disp_cons_bull2(df, params=None):
    """sigDISP2Bull and streak>=2 and FAUNA[1] and FAUNA[2]  (NOTE: vs T1 the
    window is shifted to bars [1..2] instead of [0..1])."""
    p = _params(params)
    bull, _, _ = _disp_block(df, p["i_disp2_type"], p["i_disp2_std_len"], p["i_disp2_std_min"], p["i_disp2_std_max"], p["i_disp2_req_fvg"])
    streak = _streak(bull)
    f_bull, _ = _fauna_panel(df)
    return bull & (streak >= 2) & f_bull.shift(1).fillna(False) & f_bull.shift(2).fillna(False)


def detect_sig_disp_cons_bear2(df, params=None):
    p = _params(params)
    _, bear, _ = _disp_block(df, p["i_disp2_type"], p["i_disp2_std_len"], p["i_disp2_std_min"], p["i_disp2_std_max"], p["i_disp2_req_fvg"])
    streak = _streak(bear)
    _, f_bear = _fauna_panel(df)
    return bear & (streak >= 2) & f_bear.shift(1).fillna(False) & f_bear.shift(2).fillna(False)


def detect_sig_disp_cons_bull3(df, params=None):
    p = _params(params)
    bull, _, _ = _disp_block(df, p["i_disp3_type"], p["i_disp3_std_len"], p["i_disp3_std_min"], p["i_disp3_std_max"], p["i_disp3_req_fvg"])
    streak = _streak(bull)
    f_bull, _ = _fauna_panel(df)
    return bull & (streak >= 3) & f_bull.shift(1).fillna(False) & f_bull.shift(2).fillna(False) & f_bull.shift(3).fillna(False)


def detect_sig_disp_cons_bear3(df, params=None):
    p = _params(params)
    _, bear, _ = _disp_block(df, p["i_disp3_type"], p["i_disp3_std_len"], p["i_disp3_std_min"], p["i_disp3_std_max"], p["i_disp3_req_fvg"])
    streak = _streak(bear)
    _, f_bear = _fauna_panel(df)
    return bear & (streak >= 3) & f_bear.shift(1).fillna(False) & f_bear.shift(2).fillna(False) & f_bear.shift(3).fillna(False)


# ---------------------------------------------------------------------------
# Engine 5 — PUP / PPD
# ---------------------------------------------------------------------------

def detect_sig_pup(df, params=None):
    """body_pct > 3% AND volume > 10-bar highest red-bar volume."""
    pp_barSize = 3.0
    pp_lookback = 10
    redVol = df["volume"].where(df["close"] < df["open"], 0.0)
    hiRedVol = _highest(redVol.shift(1), pp_lookback)
    priceUp = ((df["close"] - df["open"]) / df["open"]) * 100 > pp_barSize
    return (priceUp & (df["volume"] > hiRedVol)).fillna(False)


def detect_sig_ppd(df, params=None):
    pp_barSize = 3.0
    pp_lookback = 10
    greenVol = df["volume"].where(df["close"] > df["open"], 0.0)
    hiGreenVol = _highest(greenVol.shift(1), pp_lookback)
    priceDn = ((df["open"] - df["close"]) / df["open"]) * 100 > pp_barSize
    return (priceDn & (df["volume"] > hiGreenVol)).fillna(False)


# ---------------------------------------------------------------------------
# Engine 6 — PB / PBJ (stateful) — class-wrapped
# ---------------------------------------------------------------------------

class PBJEngine:
    """Pipeline B PB/PBJ engine — Zoo MA + Supertrend + PB&J filter +
    PB-lander box maintenance. State carried bar-to-bar.
    """
    def __init__(self, params: Optional[Dict] = None):
        self.params = _params(params)

    def process(self, df: pd.DataFrame):
        p = self.params
        zoo_ma_len = 5
        zoo_st_period = 10
        zoo_st_mult = 2.0
        zoo_pbj_ma_period = 20
        zoo_pbj_atr_period = 14
        zoo_pbj_hh_ll = 25
        zoo_pbj_atr_mult = 3.0
        zoo_pbj_vol_period = 20
        zoo_pbj_vol_mult = 0.1

        # Zoo MA = VWMA(close, 5)
        # ta.vwma uses sum(price*volume,len)/sum(volume,len)
        pv = df["close"] * df["volume"]
        base_ma = pv.rolling(zoo_ma_len).sum() / df["volume"].rolling(zoo_ma_len).sum()

        # Supertrend
        st_atr = zoo_st_mult * _atr(df, zoo_st_period)
        n = len(df)
        curr_long = np.full(n, np.nan)
        curr_short = np.full(n, np.nan)
        st_dir = np.ones(n, dtype=int)
        sig_line = np.full(n, np.nan)
        ma = base_ma.values
        atr_arr = st_atr.values
        src = df["close"].values
        for i in range(n):
            if i == 0 or np.isnan(ma[i]) or np.isnan(atr_arr[i]):
                curr_long[i] = ma[i] - atr_arr[i] if not np.isnan(ma[i] - atr_arr[i]) else np.nan
                curr_short[i] = ma[i] + atr_arr[i] if not np.isnan(ma[i] + atr_arr[i]) else np.nan
                sig_line[i] = ma[i]
                continue
            prev_long = curr_long[i - 1] if not np.isnan(curr_long[i - 1]) else (ma[i] - atr_arr[i])
            prev_short = curr_short[i - 1] if not np.isnan(curr_short[i - 1]) else (ma[i] + atr_arr[i])
            if ma[i] > prev_long:
                curr_long[i] = max(ma[i] - atr_arr[i], prev_long)
            else:
                curr_long[i] = ma[i] - atr_arr[i]
            if ma[i] < prev_short:
                curr_short[i] = min(ma[i] + atr_arr[i], prev_short)
            else:
                curr_short[i] = ma[i] + atr_arr[i]
            prev_dir = st_dir[i - 1]
            if prev_dir == -1 and src[i] > prev_short:
                st_dir[i] = 1
            elif prev_dir == 1 and src[i] < prev_long:
                st_dir[i] = -1
            else:
                st_dir[i] = prev_dir
            sig_line[i] = curr_long[i] if st_dir[i] == 1 else curr_short[i]

        sig_line_s = pd.Series(sig_line, index=df.index)
        buy_cross = (df["close"] > sig_line_s) & (df["close"].shift(1) <= sig_line_s.shift(1))
        sell_cross = (df["close"] < sig_line_s) & (df["close"].shift(1) >= sig_line_s.shift(1))

        # PB&J filter
        pbj_ma = _ema(df["close"], zoo_pbj_ma_period)
        pbj_atr = _atr(df, zoo_pbj_atr_period)
        zoo_avg_vol = _sma(df["volume"], zoo_pbj_vol_period)
        zoo_thresh = (pbj_atr / df["close"] * zoo_pbj_atr_mult).fillna(0.0)
        pbj_buy = (df["low"] < pbj_ma * (1 - zoo_thresh)) & \
                  (df["low"] == _lowest(df["low"], zoo_pbj_hh_ll)) & \
                  (df["volume"] > zoo_avg_vol * zoo_pbj_vol_mult)
        pbj_sell = (df["high"] > pbj_ma * (1 + zoo_thresh)) & \
                   (df["high"] == _highest(df["high"], zoo_pbj_hh_ll)) & \
                   (df["volume"] > zoo_avg_vol * zoo_pbj_vol_mult)

        # PB lander state machine — simplified: track only "wait_*" flags.
        # The full lvl-array approach maintains box arrays; for a pure-pandas
        # port we keep the same sticky-flag semantics so PBJ outputs are
        # exact and PB outputs are approximate.
        wait_buy = wait_sell = wait_pbj_buy = wait_pbj_sell = False
        sig_pbj_buy = np.zeros(n, dtype=bool)
        sig_pbj_sell = np.zeros(n, dtype=bool)
        sig_pb_buy = np.zeros(n, dtype=bool)
        sig_pb_sell = np.zeros(n, dtype=bool)
        bc = buy_cross.fillna(False).values
        sc = sell_cross.fillna(False).values
        pbb = pbj_buy.fillna(False).values
        pbs = pbj_sell.fillna(False).values
        for i in range(n):
            if bc[i]:
                wait_buy = True  # any cross arms PB approach
            if sc[i]:
                wait_sell = True
            if pbb[i]:
                wait_pbj_buy = True
            if pbs[i]:
                wait_pbj_sell = True
            if bc[i] and wait_pbj_buy:
                sig_pbj_buy[i] = True
                wait_pbj_buy = False
            if bc[i] and wait_buy:
                sig_pb_buy[i] = True
                wait_buy = False
            if sc[i] and wait_pbj_sell:
                sig_pbj_sell[i] = True
                wait_pbj_sell = False
            if sc[i] and wait_sell:
                sig_pb_sell[i] = True
                wait_sell = False

        sigBullPBJ = pd.Series(sig_pbj_buy, index=df.index)
        sigBearPBJ = pd.Series(sig_pbj_sell, index=df.index)
        sigBullPB = pd.Series(sig_pb_buy & ~sig_pbj_buy, index=df.index)
        sigBearPB = pd.Series(sig_pb_sell & ~sig_pbj_sell, index=df.index)
        return dict(sigBullPBJ=sigBullPBJ, sigBearPBJ=sigBearPBJ,
                    sigBullPB=sigBullPB, sigBearPB=sigBearPB)


_PBJ_CACHE: Dict[int, dict] = {}


def _pbj(df: pd.DataFrame, params: Optional[Dict] = None):
    key = id(df)
    if key not in _PBJ_CACHE:
        _PBJ_CACHE[key] = PBJEngine(params).process(df)
    return _PBJ_CACHE[key]


def detect_sig_bull_pbj(df, params=None):
    return _pbj(df, params)["sigBullPBJ"]


def detect_sig_bear_pbj(df, params=None):
    return _pbj(df, params)["sigBearPBJ"]


def detect_sig_bull_pb(df, params=None):
    return _pbj(df, params)["sigBullPB"]


def detect_sig_bear_pb(df, params=None):
    return _pbj(df, params)["sigBearPB"]


# ---------------------------------------------------------------------------
# Composite "fire" detections (definitions ported; some depend on stubbed
# helpers and so are themselves stubbed).
# ---------------------------------------------------------------------------


def detect_hvd_pbj_bull(df, params=None):
    """hvd_fire_bull AND nz(sigBullPBJ[1]) — co-occurrence with 1-bar lag on PBJ."""
    return detect_hvd_fire_bull(df, params) & detect_sig_bull_pbj(df, params).shift(1).fillna(False)


def detect_hvd_pbj_bear(df, params=None):
    return detect_hvd_fire_bear(df, params) & detect_sig_bear_pbj(df, params).shift(1).fillna(False)


def detect_hvd_pb_bull(df, params=None):
    return detect_hvd_fire_bull(df, params) & detect_sig_bull_pb(df, params).shift(1).fillna(False)


def detect_hvd_pb_bear(df, params=None):
    return detect_hvd_fire_bear(df, params) & detect_sig_bear_pb(df, params).shift(1).fillna(False)


# B2B HV+D detections

def detect_b2b_hvd_bull_raw(df, params=None):
    f = detect_hvd_fire_bull(df, params)
    return f & f.shift(1).fillna(False)


def detect_b2b_hvd_bear_raw(df, params=None):
    f = detect_hvd_fire_bear(df, params)
    return f & f.shift(1).fillna(False)


def detect_b2b_hvd_pbj_bull(df, params=None):
    raw = detect_b2b_hvd_bull_raw(df, params)
    pbj = detect_sig_bull_pbj(df, params)
    return raw & (pbj.shift(1).fillna(False) | pbj.shift(2).fillna(False))


def detect_b2b_hvd_pbj_bear(df, params=None):
    raw = detect_b2b_hvd_bear_raw(df, params)
    pbj = detect_sig_bear_pbj(df, params)
    return raw & (pbj.shift(1).fillna(False) | pbj.shift(2).fillna(False))


def detect_b2b_hvd_pb_bull(df, params=None):
    raw = detect_b2b_hvd_bull_raw(df, params)
    pbj = detect_sig_bull_pbj(df, params)
    pb = detect_sig_bull_pb(df, params)
    has_pbj = pbj.shift(1).fillna(False) | pbj.shift(2).fillna(False)
    has_pb = pb.shift(1).fillna(False) | pb.shift(2).fillna(False)
    return raw & has_pb & ~has_pbj


def detect_b2b_hvd_pb_bear(df, params=None):
    raw = detect_b2b_hvd_bear_raw(df, params)
    pbj = detect_sig_bear_pbj(df, params)
    pb = detect_sig_bear_pb(df, params)
    has_pbj = pbj.shift(1).fillna(False) | pbj.shift(2).fillna(False)
    has_pb = pb.shift(1).fillna(False) | pb.shift(2).fillna(False)
    return raw & has_pb & ~has_pbj


def detect_b2b_hvd_bull_nopb(df, params=None):
    raw = detect_b2b_hvd_bull_raw(df, params)
    pbj = detect_b2b_hvd_pbj_bull(df, params)
    pb = detect_b2b_hvd_pb_bull(df, params)
    return raw & ~pbj & ~pb


def detect_b2b_hvd_bear_nopb(df, params=None):
    raw = detect_b2b_hvd_bear_raw(df, params)
    pbj = detect_b2b_hvd_pbj_bear(df, params)
    pb = detect_b2b_hvd_pb_bear(df, params)
    return raw & ~pbj & ~pb


# ---------------------------------------------------------------------------
# Stateful engines that need full bar-by-bar state (PingPong SR engine,
# GZ1/HV-FVG list, Combo Chain, LS Chain, Alpha Strike session tracker,
# UU/UUU/UUUU multi-path, Boom Hunter Omega).
# These are wrapped as state-machine class skeletons; their detect_* wrapper
# raises NotImplementedError so the parent compiler can wire in the full
# implementation later. They are listed in STUBBED.
# ---------------------------------------------------------------------------


class _StubStateMachine:
    name = "stub"
    def process(self, df):
        raise NotImplementedError(f"{self.name}: full state machine not yet implemented")


class PingPongSREngine(_StubStateMachine):
    name = "PingPongSREngine"


class GZ1FVGEngine(_StubStateMachine):
    name = "GZ1FVGEngine"


class ComboChainEngine(_StubStateMachine):
    name = "ComboChainEngine"


class LSChainEngine(_StubStateMachine):
    name = "LSChainEngine"


class AlphaStrikeSession(_StubStateMachine):
    name = "AlphaStrikeSession"


class UUMultiPathEngine(_StubStateMachine):
    name = "UUMultiPathEngine"


class BoomHunterOmegaEngine(_StubStateMachine):
    name = "BoomHunterOmegaEngine"


def _stub(name):
    def _f(df, params=None):
        raise NotImplementedError(f"{name}: requires full state-machine port")
    _f.__name__ = name
    return _f


# ---------------------------------------------------------------------------
# Pipeline-D Triple Co-Occurrence (consumes terminal booleans only)
# Note: these reference stubbed engines (use_any_bull/bear). The function
# bodies show the EXACT Pine semantics for documentation; they raise on
# call until upstream stubs are filled.
# ---------------------------------------------------------------------------


def detect_co_bull_pbj(df, params=None):
    """hvd_fire_bull AND nz(sigBullPBJ[1]) AND nz(use_any_bull[1])."""
    raise NotImplementedError("detect_co_bull_pbj: requires use_any_bull (stubbed)")


def detect_co_bull_pb(df, params=None):
    raise NotImplementedError("detect_co_bull_pb: requires use_any_bull (stubbed)")


def detect_co_bear_pbj(df, params=None):
    raise NotImplementedError("detect_co_bear_pbj: requires use_any_bear (stubbed)")


def detect_co_bear_pb(df, params=None):
    raise NotImplementedError("detect_co_bear_pb: requires use_any_bear (stubbed)")


# ---------------------------------------------------------------------------
# DETECTIONS, STATE_MACHINES, STUBBED registries
# ---------------------------------------------------------------------------


# Pure-pandas detections: directly callable.
DETECTIONS: Dict[str, Callable[[pd.DataFrame, Optional[Dict]], pd.Series]] = {
    # Pipeline A
    "HVD_BULL": detect_hvd_fire_bull,
    "HVD_BEAR": detect_hvd_fire_bear,
    # Engine 1 RVOL
    "sigGrandSlam": detect_sig_grand_slam,
    "sigMOAB": detect_sig_moab,
    "sigBullRVOL1x": detect_sig_bull_rvol1x,
    "sigBearRVOL1x": detect_sig_bear_rvol1x,
    "sigSAAB": detect_sig_saab,
    "sigKratos": detect_sig_kratos,
    "sigNagasaki": detect_sig_nagasaki,
    # Engine 2 FAUNA
    "sigFAUNABull": detect_sig_fauna_bull,
    "sigFAUNABear": detect_sig_fauna_bear,
    "sigFoxtrotBull": detect_sig_foxtrot_bull,
    "sigFoxtrotBear": detect_sig_foxtrot_bear,
    # Engine 3 USE Disp
    "sigDISPBull": detect_sig_disp_bull,
    "sigDISPBear": detect_sig_disp_bear,
    "sigDispConsBull2": detect_sig_disp_cons_bull2,
    "sigDispConsBear2": detect_sig_disp_cons_bear2,
    "sigDispConsBull3": detect_sig_disp_cons_bull3,
    "sigDispConsBear3": detect_sig_disp_cons_bear3,
    # Engine 5
    "sigPUP": detect_sig_pup,
    "sigPPD": detect_sig_ppd,
    # Pipeline B
    "sigBullPBJ": detect_sig_bull_pbj,
    "sigBearPBJ": detect_sig_bear_pbj,
    "sigBullPB":  detect_sig_bull_pb,
    "sigBearPB":  detect_sig_bear_pb,
    # Standalone HV+D plot helpers
    "HVD_PBJ_BULL": detect_hvd_pbj_bull,
    "HVD_PBJ_BEAR": detect_hvd_pbj_bear,
    "HVD_PB_BULL": detect_hvd_pb_bull,
    "HVD_PB_BEAR": detect_hvd_pb_bear,
    # B2B HV+D
    "B2B_HVD_BULL_RAW": detect_b2b_hvd_bull_raw,
    "B2B_HVD_BEAR_RAW": detect_b2b_hvd_bear_raw,
    "B2B_HVD_PBJ_BULL": detect_b2b_hvd_pbj_bull,
    "B2B_HVD_PBJ_BEAR": detect_b2b_hvd_pbj_bear,
    "B2B_HVD_PB_BULL": detect_b2b_hvd_pb_bull,
    "B2B_HVD_PB_BEAR": detect_b2b_hvd_pb_bear,
    "B2B_HVD_BULL_NOPB": detect_b2b_hvd_bull_nopb,
    "B2B_HVD_BEAR_NOPB": detect_b2b_hvd_bear_nopb,
}


STATE_MACHINES = {
    "PBJEngine": PBJEngine,
    "PingPongSREngine": PingPongSREngine,
    "GZ1FVGEngine": GZ1FVGEngine,
    "ComboChainEngine": ComboChainEngine,
    "LSChainEngine": LSChainEngine,
    "AlphaStrikeSession": AlphaStrikeSession,
    "UUMultiPathEngine": UUMultiPathEngine,
    "BoomHunterOmegaEngine": BoomHunterOmegaEngine,
}


# Detections that require state machines not yet ported. detect_* functions
# exist (raise NotImplementedError) so the registry signature stays uniform.
STUBBED: Dict[str, Callable[[pd.DataFrame, Optional[Dict]], pd.Series]] = {
    # Engine-based aggregations
    "sigPentagon": _stub("sigPentagon"),
    "sigWTC": _stub("sigWTC"),
    "sigHiroshima": _stub("sigHiroshima"),
    "sigNeoBull": _stub("sigNeoBull"),
    "sigNeoBear": _stub("sigNeoBear"),
    "sigTrinityBull": _stub("sigTrinityBull"),
    "sigTrinityBear": _stub("sigTrinityBear"),
    "sigLong1": _stub("sigLong1"), "sigLong2": _stub("sigLong2"),
    "sigShort1": _stub("sigShort1"), "sigShort2": _stub("sigShort2"),
    "gz_bullGZI": _stub("gz_bullGZI"), "gz_bullHV": _stub("gz_bullHV"),
    "gz_bearGZI": _stub("gz_bearGZI"), "gz_bearHV": _stub("gz_bearHV"),
    # Pipeline C composites
    "sigAlphaStrikeBull": _stub("sigAlphaStrikeBull"),
    "sigAlphaStrikeBear": _stub("sigAlphaStrikeBear"),
    "sigODBull": _stub("sigODBull"),
    "sigODBear": _stub("sigODBear"),
    "sigGolfBull": _stub("sigGolfBull"),
    "sigGolfBear": _stub("sigGolfBear"),
    "sigPAFBull": _stub("sigPAFBull"),
    "sigPAFBear": _stub("sigPAFBear"),
    "comboSet1_Bull": _stub("comboSet1_Bull"), "comboSet1_Bear": _stub("comboSet1_Bear"),
    "comboSet2_Bull": _stub("comboSet2_Bull"), "comboSet2_Bear": _stub("comboSet2_Bear"),
    "comboSet3_Bull": _stub("comboSet3_Bull"), "comboSet3_Bear": _stub("comboSet3_Bear"),
    "comboSet4_Bull": _stub("comboSet4_Bull"), "comboSet4_Bear": _stub("comboSet4_Bear"),
    "csNew1_Bull": _stub("csNew1_Bull"), "csNew1_Bear": _stub("csNew1_Bear"),
    "csNew2_Bull": _stub("csNew2_Bull"), "csNew2_Bear": _stub("csNew2_Bear"),
    "csNew3_Bull": _stub("csNew3_Bull"), "csNew3_Bear": _stub("csNew3_Bear"),
    "sigCCBull": _stub("sigCCBull"), "sigCCBear": _stub("sigCCBear"),
    "sigLSCBull": _stub("sigLSCBull"), "sigLSCBear": _stub("sigLSCBear"),
    "anyBullFloor": _stub("anyBullFloor"), "anyBull2nd": _stub("anyBull2nd"),
    "anyBearRoof": _stub("anyBearRoof"), "anyBearPent": _stub("anyBearPent"),
    "hwBull": _stub("hwBull"), "hwBear": _stub("hwBear"),
    "superBull": _stub("superBull"), "superBear": _stub("superBear"),
    "sduperBull": _stub("sduperBull"), "sduperBear": _stub("sduperBear"),
    "sigP21BullUUUU": _stub("sigP21BullUUUU"), "sigP21BearUUUU": _stub("sigP21BearUUUU"),
    "sigP21BullUUU":  _stub("sigP21BullUUU"),  "sigP21BearUUU":  _stub("sigP21BearUUU"),
    "sigUUBull": _stub("sigUUBull"), "sigUUBear": _stub("sigUUBear"),
    "sigOmegaLong": _stub("sigOmegaLong"), "sigOmegaLongA": _stub("sigOmegaLongA"),
    "sigShortPlusPress": _stub("sigShortPlusPress"),
    "sigNagPlusBull": _stub("sigNagPlusBull"), "sigNagPlusBear": _stub("sigNagPlusBear"),
    # Pipeline D
    "co_bull_pbj": detect_co_bull_pbj, "co_bull_pb": detect_co_bull_pb,
    "co_bear_pbj": detect_co_bear_pbj, "co_bear_pb": detect_co_bear_pb,
    # gated/composite floors
    "floor_gated": _stub("floor_gated"), "floor2_gated": _stub("floor2_gated"),
    # HVDM cascade
    "hvdm_pup_nopbj_b": _stub("hvdm_pup_nopbj_b"),
    "hvdm_ppd_nopbj_r": _stub("hvdm_ppd_nopbj_r"),
    "hvdm_2of3_b": _stub("hvdm_2of3_b"), "hvdm_2of3_r": _stub("hvdm_2of3_r"),
    "hvdm_3of3_b": _stub("hvdm_3of3_b"), "hvdm_3of3_r": _stub("hvdm_3of3_r"),
}


# ---------------------------------------------------------------------------
# UNIQUE_TO_2246 markers — placeholder block. There are NO detection plots
# that exist only in the 2246 file (its full detection set is shared with
# the two 1939-line siblings). The marker comment below is left for the
# cross-agent compiler's grep convenience, and points to the post-detection
# alert/aggregator code as the unique 2246 contribution.
# ---------------------------------------------------------------------------

# UNIQUE_TO_2246
def _unique_to_2246_aggregator_alert(df, params=None):
    """The 2246 file's only post-T1, post-S39/S26 unique addition is the
    per-bar consolidated USE Aggregator alert (lines 2088–2246 of the .pine).
    It produces no new fire boolean — it merely serializes ALL active fire_*
    booleans into a string payload. Therefore this function returns the OR of
    all bull/bear fire booleans that ARE pure-pandas implementable.
    """
    out = pd.Series(False, index=df.index)
    for name, fn in DETECTIONS.items():
        if not (name.startswith(("HVD_", "HVD_P", "B2B_HVD_", "sigPUP", "sigPPD",
                                 "sigGrandSlam", "sigMOAB", "sigBullRVOL1x", "sigBearRVOL1x",
                                 "sigFAUNABull", "sigFAUNABear", "sigDISPBull", "sigDISPBear",
                                 "sigDispCons", "sigFoxtrot", "sigBullPBJ", "sigBearPBJ",
                                 "sigBullPB", "sigBearPB"))):
            continue
        try:
            out = out | fn(df, params).fillna(False)
        except Exception:
            pass
    return out


if __name__ == "__main__":
    print(f"DETECTIONS:    {len(DETECTIONS)}")
    print(f"STATE_MACHINES:{len(STATE_MACHINES)}")
    print(f"STUBBED:       {len(STUBBED)}")
    # sanity: every stubbed entry is callable
    for k, v in STUBBED.items():
        assert callable(v), f"{k} is not callable"
    print("OK")
