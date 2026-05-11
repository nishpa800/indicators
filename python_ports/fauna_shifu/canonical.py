"""
Python port of FAUNA_SHIFU_JUMBO_CIA_1ST_PUP_v1.pine (2338 lines).

Source Pine:  fauna-shifu/versions/FAUNA_SHIFU_JUMBO_CIA_1ST_PUP_v1.pine
Reference port: python_ports/hvd_pbj_ppd/the_only_one.py

Fauna-Shifu is the FAUNA-decomposed PBJ variant family — the indicator that
defines the ULTRA-decomposed SUPER signals per VALIDATE 7:

    sigSuperBullPBJ = conf and dirConfBull and al_anyBullPBJ and al_anyBullRVOL
    sigSuperBullPB  = conf and dirConfBull and al_anyBullPB  and al_anyBullRVOL
    sigSuperBearPBJ = conf and dirConfBear and al_anyBearPBJ and al_anyBearRVOL
    sigSuperBearPB  = conf and dirConfBear and al_anyBearPB  and al_anyBearRVOL

Same SUPER decomposition as ultra-combo (Group C in the SUPER family doc),
but THIS Pine adds Fauna+Shifu-specific JUMBO / CIA / 1ST_PUP variants:

  - **JUMBO**: SAAB², KRATOS² (squared / back-to-back RVOL "weapons")
  - **CIA**: Typhoon, Tomcat, Musashi, Gripen — multi-engine combo specials
  - **1ST_PUP**: PUP Combo (PUP² back-to-back), PPD Combo, Whale+PUP, Whale+PPD,
                 PAF PUP B2B, PAF PPD B2B, Opening Drive, Katana session signals
  - **FAUNA+ density sets**: Alpha / Bravo / Charlie / Delta / Echo + Foxtrot (4-in-4) + Golf (PUP²/PPD²)
  - **Shifu**: KC + Q3 BHP + Ping-Pong S/R qualifier feeding anyBullPBJ / anyBearPBJ

Conventions (mirror python_ports.hvd_pbj_ppd.the_only_one):
  - df is expected to have columns: open, high, low, close, volume.
  - Each detection function returns pd.Series[bool] aligned to df.index.
  - IPSF (input.*) parameters live in DEFAULTS and may be overridden via params.
  - Hardcoded Pine constants (NOT input.*) stay hardcoded here.
  - Pine-only intrinsics (Supertrend PBJ state, GZ1 FVG arrays, YY pivot SR,
    tv_ta.relativeVolume, BHP Ehlers chain, Whale array per-bar, Ping-Pong SR)
    are STUBBED. Caller may inject precomputed series via df.attrs[<name>].

This module is import-only safe; no tests inside.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd

# ============================================================================
# IPSF DEFAULTS — mirror Pine input.* defaults exactly (SD-003 preserved).
# ============================================================================
DEFAULTS: Dict = {
    # Global toggles
    "firstBarOnly": True,
    "enable_PB": False,
    # RVOL Weapons / shows
    "show_GrandSlam": True, "show_MOAB": True,
    "show_DoubleDisp": True, "show_FullStack": True, "show_FVGStack": True,
    "show_Katana": True, "show_Musashi": True,
    "show_WhaleBull": True, "show_WhaleBear": True,
    "show_PUP": True, "show_PPD": True,
    "show_SAABSq": True, "show_KRATOSSq": True,
    "show_TyphoonBull": True, "show_TyphoonBear": True,
    "show_TomcatBull": True, "show_TomcatBear": True,
    "show_Nagasaki": True,
    "show_PAFBull": True, "show_PAFBear": True,
    "show_SuperBull": True, "show_SuperBear": True,
    "show_Alpha": True, "show_Bravo": True, "show_Charlie": True,
    "show_Delta": True, "show_Echo": True,
    "show_Foxtrot": True, "show_Golf": True, "show_OD": True,
    # SAAB² / KRATOS² Settings
    "saab2_reqConfirm": False,
    # RVOL Bull/Bear calc
    "bb_avgLength": 30, "bb_smaLength": 20,
    # RVOL Reg @ Time
    "reg_anchorTimeframe": "", "reg_length": 30,
    "reg_calculationMode": "Regular", "reg_adjustRealtime": True,
    # LONG 1 / MOMENTUM 1
    "hyb_addReg1": 5.0, "hyb_addCum1": 3.0, "hyb_bodyRat1": 0.65,
    # Displacement
    "i_req_fvg": True, "i_range_type": "Open to Close",
    "i_std_len": 100, "i_std_mult": 5,
    # GZ1 / HV
    "gz1_threshPct": 2.0, "gz1_auto": True, "gz1_dist": 7, "gz1_mitLvl": False,
    # OKEH Zoo (PBJ engine)
    "zoo_ma_type": "VWMA", "zoo_ma_len": 5,
    "zoo_pbj_ma_period": 20, "zoo_pbj_atr_period": 14,
    "zoo_pbj_hh_ll": 25, "zoo_pbj_atr_mult": 3.0,
    "zoo_pbj_vol_period": 20, "zoo_pbj_vol_mult": 0.1,
    "zoo_use_st": True, "zoo_st_period": 10, "zoo_st_mult": 2.0,
    # YY pivot
    "yy_leftBars": 75, "yy_rightBars": 1,
    "yy_atrLength": 50, "yy_atrMult": 3.5,
    # Shifu KC
    "sh_kc_maType": "VWMA", "sh_kc_length": 20, "sh_kc_mult_inp": 3.0,
    "sh_kc_bandsStyle": "Average True Range", "sh_kc_atrLength": 14,
    "show_sh_KCBasis": True,
    "sh_kc_slopeLookbackBars": 4,
    "sh_kc_bullishSlopeThreshold": 0.25, "sh_kc_bearishSlopeThreshold": 0.25,
    "sh_volatilityLookback": 2, "sh_volatilityMinChange": 8.0,
    # Shifu BHP
    "sh_LPPeriod2": 27, "sh_K12": 0.8,
    "sh_threshold": -0.9, "sh_ob_threshold": 0.9,
    # Shifu Ping Pong
    "sh_min_candles": 2, "sh_buffer_ticks": 10,
    "sh_atr_mult": 2.0, "sh_trend_cnt": 1,
    # Shifu Swingin
    "sh_leftBars": 3, "sh_rightBars": 2,
    "sh_useAtrFilter": True, "sh_atrMultSwing": 2.0,
    # Shifu General
    "sh_atr_len": 100,
    # Master Filter
    "sh_mfModeBull": "KC + Candle", "sh_mfModeBear": "KC + Candle",
    # Whale
    "wh_lenBull": 20, "wh_lenBear": 20,
    "wh_useQ": True, "wh_useY": True, "wh_useATH": True,
    # Pocket Pivot
    "pp_barSize": 3.0, "pp_lookback": 10,
    # FAUNA+ density sets (Alpha–Echo)
    "fp_a_rng": "Open to Close", "fp_a_mult": 5, "fp_a_req": 2, "fp_a_win": 2,
    "fp_a_fb": False, "fp_a_fauna_rq": 0, "fp_a_pp_rq": 0, "fp_a_fvg_rq": 0,
    "fp_b_rng": "Open to Close", "fp_b_mult": 5, "fp_b_req": 3, "fp_b_win": 3,
    "fp_b_fb": False, "fp_b_fauna_rq": 0, "fp_b_pp_rq": 0, "fp_b_fvg_rq": 0,
    "fp_c_rng": "Open to Close", "fp_c_mult": 5, "fp_c_req": 3, "fp_c_win": 4,
    "fp_c_fb": False, "fp_c_fauna_rq": 0, "fp_c_pp_rq": 0, "fp_c_fvg_rq": 0,
    "fp_d_rng": "Open to Close", "fp_d_mult": 5, "fp_d_req": 2, "fp_d_win": 3,
    "fp_d_fb": False, "fp_d_fauna_rq": 0, "fp_d_pp_rq": 0, "fp_d_fvg_rq": 0,
    "fp_e_rng": "Open to Close", "fp_e_mult": 5, "fp_e_req": 2, "fp_e_win": 4,
    "fp_e_fb": False, "fp_e_fauna_rq": 0, "fp_e_pp_rq": 0, "fp_e_fvg_rq": 0,
    # Opening Drive
    "od_max": 2, "od_rng": "Open to Close", "od_mult": 5,
    # Bar timeframe in seconds (caller supplies; defaults to 60s)
    "tfSec": 60,
}


# ============================================================================
# _helpers — utilities used by many detections (parity w/ reference port)
# ============================================================================
def _p(params: Optional[Dict]) -> Dict:
    out = dict(DEFAULTS)
    if params:
        out.update(params)
    return out


def _stdev(s: pd.Series, length: int) -> pd.Series:
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
    # Wilder's RMA = EMA(alpha=1/length)
    return tr.ewm(alpha=1.0 / length, adjust=False, min_periods=length).mean()


def _nz_b(s: pd.Series) -> pd.Series:
    return s.fillna(False).astype(bool)


def _nz_f(s: pd.Series, fill: float = 0.0) -> pd.Series:
    return s.fillna(fill)


def _conf(df: pd.DataFrame) -> pd.Series:
    return pd.Series(True, index=df.index)


def _disp_range(df: pd.DataFrame, kind: str) -> pd.Series:
    if kind == "Open to Close":
        return (df["open"] - df["close"]).abs()
    return df["high"] - df["low"]


def _bull_fvg(df: pd.DataFrame) -> pd.Series:
    # Fauna-Shifu uses the same FVG shape as HVDPBJPPD: low > high[2] and close[1] > open[1]
    return (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["open"].shift(1))


def _bear_fvg(df: pd.DataFrame) -> pd.Series:
    return (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["open"].shift(1))


def _gz_bull_fvg(df: pd.DataFrame) -> pd.Series:
    # GZ1 bull FVG (slightly different — close[1] > high[2])
    return (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["high"].shift(2))


def _gz_bear_fvg(df: pd.DataFrame) -> pd.Series:
    return (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["low"].shift(2))


# RVOL threshold tables (Fauna-Shifu source lines 329-362; NOTE: different from
# HVDPBJPPD — Fauna-Shifu has its own ladder).
def _rvol_1x(tfsec: float) -> float:
    s = tfsec
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


def _gs_moab(tfsec: float) -> float:
    s = tfsec
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


def _saab_kratos(tfsec: float) -> float:
    return _rvol_1x(tfsec) * 0.56


# ============================================================================
# _engines — single-pass build of every signal Fauna-Shifu plots.
# Cached on df.attrs so detection wrappers stay cheap.
# ============================================================================
def _ensure_engines(df: pd.DataFrame, params: Dict) -> Dict[str, pd.Series]:
    cache = df.attrs.setdefault("_fauna_shifu_eng", {})
    cache_key = ("v1", id(df), tuple(sorted(
        (k, v) for k, v in params.items()
        if isinstance(v, (int, float, str, bool))
    )))
    if cache.get("_key") == cache_key and "sigSuperBullPBJ" in cache:
        return cache
    cache.clear()
    cache["_key"] = cache_key

    p = params
    conf = _conf(df)
    tfSec = float(p["tfSec"])

    # --- Session boundary ---
    is_new_day = df.attrs.get("is_new_day")
    if is_new_day is None:
        if isinstance(df.index, pd.DatetimeIndex):
            nd = df.index.normalize() != pd.Series(df.index.normalize(), index=df.index).shift(1)
            is_new_day = pd.Series(nd.to_numpy(), index=df.index).fillna(True)
        else:
            tmp = np.zeros(len(df), dtype=bool); tmp[0] = True
            is_new_day = pd.Series(tmp, index=df.index)
    is_new_sess = is_new_day.fillna(False).astype(bool)

    nd_arr = is_new_sess.to_numpy()
    sb_arr = np.zeros(len(df), dtype=int)
    counter = 0
    for i, nd in enumerate(nd_arr):
        if nd:
            counter = 1
        else:
            counter += 1
        sb_arr[i] = counter
    sessionBarCount = pd.Series(sb_arr, index=df.index)

    # --- RVOL Bull/Bear (engine 1, FS source ~L367-388) ---
    bb_avgLength = int(p["bb_avgLength"])
    bb_smaLength = int(p["bb_smaLength"])
    bb_spike = (df["close"] - df["open"]).abs()
    bb_avgSpikeDenom = _sma(bb_spike, bb_avgLength).shift(1)
    bb_normalizedPrice = bb_spike / _nz_f(bb_avgSpikeDenom, 1.0)
    bb_avgVolDenom = _sma(df["volume"], bb_avgLength).shift(1)
    bb_normalizedVolume = df["volume"] / _nz_f(bb_avgVolDenom, 1.0)
    bb_diff = bb_normalizedPrice - bb_normalizedVolume
    bb_positiveDiff = bb_diff.where(bb_diff > 0, np.nan)
    bb_smaDiff = _sma(bb_positiveDiff, bb_smaLength)
    bb_baseBullish = (df["close"] > df["open"]) & (bb_positiveDiff > bb_smaDiff)
    bb_baseBearish = (df["close"] < df["open"]) & (bb_positiveDiff > bb_smaDiff)

    th_1x = _rvol_1x(tfSec)
    th_gs_moab = _gs_moab(tfSec)
    th_saab_kratos = _saab_kratos(tfSec)

    sigBullRVOL1x = conf & bb_baseBullish & (bb_normalizedPrice >= th_1x) & (bb_normalizedPrice < th_gs_moab)
    sigBearRVOL1x = conf & bb_baseBearish & (bb_normalizedPrice >= th_1x) & (bb_normalizedPrice < th_gs_moab)
    sigGrandSlam = conf & bb_baseBullish & (bb_normalizedPrice >= th_gs_moab)
    sigMOAB = conf & bb_baseBearish & (bb_normalizedPrice >= th_gs_moab)
    sigSAAB = conf & bb_baseBullish & (bb_normalizedPrice >= th_saab_kratos) & (bb_normalizedPrice < th_1x)
    sigKratos = conf & bb_baseBearish & (bb_normalizedPrice >= th_saab_kratos) & (bb_normalizedPrice < th_1x)

    # --- LONG 1 / SHORT 1 (Momentum 1) — needs tv_ta.relativeVolume (STUBBED) ---
    # Caller may inject hybRegRatio / hybCumRatio via df.attrs.
    hybRegRatio = df.attrs.get("hybRegRatio", pd.Series(np.nan, index=df.index))
    hybCumRatio = df.attrs.get("hybCumRatio", pd.Series(np.nan, index=df.index))
    hybBodySz = (df["close"] - df["open"]).abs()
    hybRange = (df["high"] - df["low"]).replace(0, np.nan)
    hybBodyRat = (hybBodySz / hybRange).fillna(0.0)
    hybConvict1 = hybBodyRat >= p["hyb_bodyRat1"]
    hybBull1 = (df["close"] > df["open"]) & hybConvict1
    hybBear1 = (df["close"] < df["open"]) & hybConvict1
    hybMom1 = conf & (hybRegRatio > p["hyb_addReg1"]) & (hybCumRatio > p["hyb_addCum1"])
    sigAddLong1 = hybMom1 & hybBull1
    sigAddShort1 = hybMom1 & hybBear1

    # --- FAUNA (engine 2, FS source L417-462) — identical to HVDPBJPPD ---
    atr14 = _atr(df, 14)
    fauna_avgVol = _sma(df["volume"], 20)
    fauna_avgBody = _sma((df["close"] - df["open"]).abs(), 20)
    fauna_avgDelta = _sma((df["close"] - df["close"].shift(1)).abs(), 10)
    fauna_trendMA = _sma(df["close"], 50)
    fauna_body = df["close"] - df["open"]
    fauna_rng = df["high"] - df["low"]
    fauna_bodySz = fauna_body.abs()
    fauna_bodyRat = (fauna_bodySz / fauna_rng.replace(0, np.nan)).fillna(0.0)
    fauna_up = fauna_body > 0
    fauna_dn = fauna_body < 0
    fauna_prev_body = df["close"].shift(1) - df["open"].shift(1)
    fauna_prev_range = df["high"].shift(1) - df["low"].shift(1)

    MB_b = fauna_up & (fauna_bodySz > 1.6 * atr14) & (fauna_bodyRat > 0.7) & (df["volume"] > 1.8 * fauna_avgVol)
    RE_b = fauna_up & (fauna_rng > 2.2 * atr14) & ((df["high"] - df["close"]) < 0.15 * fauna_rng) & (df["volume"] > 1.8 * fauna_avgVol)
    TA_b = (fauna_trendMA > fauna_trendMA.shift(1)) & ((df["close"] - df["close"].shift(1)) > 1.6 * fauna_avgDelta) & fauna_up & (df["volume"] > 1.8 * fauna_avgVol)
    GG_b = ((df["open"] - df["close"].shift(1)) > 0.9 * atr14) & fauna_up & (df["low"] > df["close"].shift(1)) & (df["volume"] > 1.8 * fauna_avgVol)
    fauna_StrongBear = (df["close"].shift(1) < df["open"].shift(1)) & (fauna_prev_body.abs() > 1.5 * fauna_avgBody.shift(1)) & (df["volume"].shift(1) > 1.5 * fauna_avgVol.shift(1))
    fauna_WeakBear = (df["close"].shift(1) < df["open"].shift(1)) & ((fauna_prev_body.abs() / fauna_prev_range.replace(0, np.nan)).fillna(0.0) <= 0.2)
    TR_b = fauna_WeakBear & (MB_b | RE_b | TA_b)
    ES_b = fauna_StrongBear & (MB_b | RE_b | TA_b)
    GDR_b = (df["close"].shift(1) < df["open"].shift(1)) & GG_b
    # NOTE drift: Fauna-Shifu source has `excluded_bull = GG_b or TR_b or ES_b or GDR_b`
    # — GG_b is unconditionally excluded (no b_gg_pass override like HVDPBJPPD).
    excluded_bull = GG_b | TR_b | ES_b | GDR_b
    sigFAUNABull = conf & (MB_b | RE_b | TA_b) & ~excluded_bull

    MB_r = fauna_dn & (fauna_bodySz > 1.6 * atr14) & (fauna_bodyRat > 0.7) & (df["volume"] > 1.8 * fauna_avgVol)
    RE_r = fauna_dn & (fauna_rng > 2.2 * atr14) & ((df["close"] - df["low"]) < 0.15 * fauna_rng) & (df["volume"] > 1.8 * fauna_avgVol)
    TA_r = (fauna_trendMA < fauna_trendMA.shift(1)) & ((df["close"].shift(1) - df["close"]) > 1.6 * fauna_avgDelta) & fauna_dn & (df["volume"] > 1.8 * fauna_avgVol)
    GG_r = ((df["close"].shift(1) - df["open"]) > 0.9 * atr14) & fauna_dn & (df["high"] < df["close"].shift(1)) & (df["volume"] > 1.8 * fauna_avgVol)
    fauna_StrongBull = (df["close"].shift(1) > df["open"].shift(1)) & (fauna_prev_body.abs() > 1.5 * fauna_avgBody.shift(1)) & (df["volume"].shift(1) > 1.5 * fauna_avgVol.shift(1))
    fauna_WeakBull = (df["close"].shift(1) > df["open"].shift(1)) & ((fauna_prev_body.abs() / fauna_prev_range.replace(0, np.nan)).fillna(0.0) <= 0.2)
    TR_r = fauna_WeakBull & (MB_r | RE_r | TA_r)
    ES_r = fauna_StrongBull & (MB_r | RE_r | TA_r)
    GDR_r = (df["close"].shift(1) > df["open"].shift(1)) & GG_r
    excluded_bear = GG_r | TR_r | ES_r | GDR_r
    sigFAUNABear = conf & (MB_r | RE_r | TA_r) & ~excluded_bear

    # --- DISPLACEMENT (FS source L467-484) ---
    i_req_fvg = bool(p["i_req_fvg"])
    disp_rng = _disp_range(df, p["i_range_type"])
    disp_std = _stdev(disp_rng, int(p["i_std_len"]))
    disp_thresh = disp_std * p["i_std_mult"]
    disp_currDisp = disp_rng > disp_thresh
    disp_prevDisp = disp_rng.shift(1) > disp_thresh.shift(1)
    disp_bullFVG = _bull_fvg(df)
    disp_bearFVG = _bear_fvg(df)
    disp_bullBar = df["close"] > df["open"]
    disp_bearBar = df["close"] < df["open"]
    if i_req_fvg:
        sigDISPBull = conf & disp_prevDisp & disp_bullFVG
        sigDISPBear = conf & disp_prevDisp & disp_bearFVG
    else:
        sigDISPBull = conf & disp_currDisp & disp_bullBar
        sigDISPBear = conf & disp_currDisp & disp_bearBar

    # PUP/PPD-flavored disp uses mult=2
    disp_thresh_pup = disp_std * 2
    disp_prevDisp_pup = disp_rng.shift(1) > disp_thresh_pup.shift(1)
    disp_currDisp_pup = disp_rng > disp_thresh_pup
    if i_req_fvg:
        sigDISPBull_pup = conf & disp_prevDisp_pup & disp_bullFVG
        sigDISPBear_pup = conf & disp_prevDisp_pup & disp_bearFVG
    else:
        sigDISPBull_pup = conf & disp_currDisp_pup & disp_bullBar
        sigDISPBear_pup = conf & disp_currDisp_pup & disp_bearBar

    # --- HV standalone (FS source L549-551) ---
    hv2_hve = _highest(df["volume"], 5000)
    hv2_hvy = _highest(df["volume"], 252)
    sigHV = conf & ((df["volume"] == hv2_hve) | (df["volume"] == hv2_hvy))

    # --- NAGASAKI (streaming ATH, FS source L555-563) ---
    nag_arr = np.zeros(len(df), dtype=bool)
    cur_max = -np.inf
    v_arr = df["volume"].to_numpy()
    for i, v in enumerate(v_arr):
        if i == 0:
            cur_max = v if v is not None and not (isinstance(v, float) and np.isnan(v)) else -np.inf
            continue
        if v is not None and v > cur_max:
            nag_arr[i] = True
            cur_max = v
    sigNagasaki = pd.Series(nag_arr, index=df.index)

    # --- POCKET PIVOT (PUP/PPD; FS source L567-577) ---
    pp_lookback = int(p["pp_lookback"])
    pp_barSize = float(p["pp_barSize"])
    pp_redVol = df["volume"].where(df["close"] < df["open"], 0.0)
    pp_greenVol = df["volume"].where(df["close"] > df["open"], 0.0)
    pp_hiRedVol = _highest(pp_redVol.shift(1), pp_lookback)
    pp_hiGreenVol = _highest(pp_greenVol.shift(1), pp_lookback)
    pp_priceUp = ((df["close"] - df["open"]) / df["open"]) * 100 > pp_barSize
    pp_priceDn = ((df["open"] - df["close"]) / df["open"]) * 100 > pp_barSize
    pp_volBull = df["volume"] > pp_hiRedVol
    pp_volBear = df["volume"] > pp_hiGreenVol
    sigPUP = conf & pp_priceUp & pp_volBull
    sigPPD = conf & pp_priceDn & pp_volBear

    # --- ANISH PASS (Stage 2 / Stage 4) — pure deterministic ---
    an_ema50 = _ema(df["close"], 50)
    an_ema150 = _ema(df["close"], 150)
    an_ema200 = _ema(df["close"], 200)
    an_ema200_1m = an_ema200.shift(21)
    an_w52Hi = _highest(df["high"], 252)
    an_w52Lo = _lowest(df["low"], 252)
    sigAnishBull = (conf & (df["close"] > an_ema50) & (df["close"] >= an_ema150) &
                    (df["close"] >= an_ema200) & (an_ema50 > an_ema150) &
                    (an_ema50 > an_ema200) & (an_ema150 >= an_ema200) &
                    (an_ema200 > an_ema200_1m) & (df["close"] > an_w52Lo * 1.30) &
                    (df["close"] >= an_w52Hi * 0.75))
    sigAnishBear = (conf & (df["close"] < an_ema50) & (df["close"] <= an_ema150) &
                    (df["close"] <= an_ema200) & (an_ema50 < an_ema150) &
                    (an_ema50 < an_ema200) & (an_ema150 <= an_ema200) &
                    (an_ema200 < an_ema200_1m) & (df["close"] < an_w52Hi * 0.70) &
                    (df["close"] <= an_w52Lo * 1.25))

    # --- WHALE pivot pattern (FS source L595-626) — uses per-bar arrays.
    # Vectorize: for each bar, look at bars i-1..i-len, capture max down/up vol.
    wh_lenBull = int(p["wh_lenBull"]); wh_lenBear = int(p["wh_lenBear"])
    wh_sma_bull = _sma(df["close"], wh_lenBull)
    wh_sma_bear = _sma(df["close"], wh_lenBear)
    wh_volAvg = _sma(df["volume"], 50)
    wh_hvy = _highest(df["volume"], 252)
    wh_hvq = _highest(df["volume"], 63)
    # Streaming "max-vol-ever" tracker
    wh_maxVolEver_arr = np.zeros(len(df))
    cur_max = -np.inf
    for i, v in enumerate(v_arr):
        if v is not None and not (isinstance(v, float) and np.isnan(v)):
            if v > cur_max:
                cur_max = v
        wh_maxVolEver_arr[i] = cur_max
    wh_maxVolEver = pd.Series(wh_maxVolEver_arr, index=df.index)

    # wh_maxDnVol[i] = max(volume[k] for k in [1..lenBull] where close[k] < close[k+1])
    closes = df["close"].to_numpy()
    vols = df["volume"].to_numpy()
    wh_maxDnVol_arr = np.zeros(len(df))
    wh_maxUpVol_arr = np.zeros(len(df))
    for i in range(len(df)):
        # bull: scan k=1..wh_lenBull
        mx_dn = 0.0
        for k in range(1, wh_lenBull + 1):
            j = i - k
            jp = i - (k + 1)
            if j < 0 or jp < 0:
                continue
            if closes[j] < closes[jp]:
                if vols[j] > mx_dn:
                    mx_dn = vols[j]
        wh_maxDnVol_arr[i] = mx_dn
        mx_up = 0.0
        for k in range(1, wh_lenBear + 1):
            j = i - k
            jp = i - (k + 1)
            if j < 0 or jp < 0:
                continue
            if closes[j] > closes[jp]:
                if vols[j] > mx_up:
                    mx_up = vols[j]
        wh_maxUpVol_arr[i] = mx_up
    wh_maxDnVol = pd.Series(wh_maxDnVol_arr, index=df.index)
    wh_maxUpVol = pd.Series(wh_maxUpVol_arr, index=df.index)

    wh_isHV = ((bool(p["wh_useQ"]) & (df["volume"] == wh_hvq)) |
               (bool(p["wh_useY"]) & (df["volume"] == wh_hvy)) |
               (bool(p["wh_useATH"]) & (df["volume"] == wh_maxVolEver)))
    wh_greenBar = df["close"] > df["close"].shift(1)
    wh_surgeonBull = wh_greenBar & (df["low"] <= wh_sma_bull) & (df["close"] > wh_sma_bull) & (df["volume"] > wh_maxDnVol) & (df["volume"] > wh_volAvg)
    wh_origBull = wh_greenBar & (df["low"] <= wh_sma_bull) & (df["volume"] > wh_maxDnVol)
    wh_pivotBull = wh_surgeonBull | wh_origBull
    wh_redBar = df["close"] < df["close"].shift(1)
    wh_surgeonBear = wh_redBar & (df["high"] >= wh_sma_bear) & (df["close"] < wh_sma_bear) & (df["volume"] > wh_maxUpVol) & (df["volume"] > wh_volAvg)
    wh_origBear = wh_redBar & (df["high"] >= wh_sma_bear) & (df["volume"] > wh_maxUpVol)
    wh_pivotBear = wh_surgeonBear | wh_origBear

    # --- PBJ engine (Supertrend + landing-zone arrays) — STUBBED.
    # Caller may inject sigBullPBJ / sigBullPB / sigBearPBJ / sigBearPB via df.attrs.
    def _attr_or_false(name):
        s = df.attrs.get(name)
        if s is None:
            return pd.Series(False, index=df.index)
        return s.reindex(df.index).fillna(False).astype(bool)
    sigBullPBJ = _attr_or_false("sigBullPBJ")
    sigBullPB = _attr_or_false("sigBullPB") if bool(p["enable_PB"]) else pd.Series(False, index=df.index)
    sigBearPBJ = _attr_or_false("sigBearPBJ")
    sigBearPB = _attr_or_false("sigBearPB") if bool(p["enable_PB"]) else pd.Series(False, index=df.index)

    # --- Shifu qualifiers (KC + BHP Q3 + Ping-Pong S/R) — STUBBED.
    # Caller may inject sh_bullQualifier / sh_bearQualifier via df.attrs;
    # also pp_bull_pp / pp_bear_pp for downstream consumers.
    sh_bullQualifier = _attr_or_false("sh_bullQualifier")
    sh_bearQualifier = _attr_or_false("sh_bearQualifier")

    # --- Future-proof PBJ/PB wrappers (FS source L1040-1045) ---
    anyBullPBJ = sigBullPBJ | sh_bullQualifier
    anyBearPBJ = sigBearPBJ | sh_bearQualifier
    anyBullPB = sigBullPB | sh_bullQualifier
    anyBearPB = sigBearPB | sh_bearQualifier

    # --- WHALE signal (defined after PBJ; FS source L1050-1051) ---
    sigWhaleBull = conf & wh_pivotBull & wh_isHV & sigPUP & anyBullPBJ
    sigWhaleBear = conf & wh_pivotBear & wh_isHV & sigPPD & anyBearPBJ

    # --- GZ1 engine (HV FVG + GZI struct array) — STUBBED.
    # Caller may inject gz_bullHV / gz_bearHV / gz_bullGZI / gz_bearGZI via df.attrs.
    gz_bullHV = _attr_or_false("gz_bullHV")
    gz_bearHV = _attr_or_false("gz_bearHV")
    gz_bullGZI = _attr_or_false("gz_bullGZI")
    gz_bearGZI = _attr_or_false("gz_bearGZI")

    # --- YY pivot / breakout — STUBBED (state machine over yy_srs array).
    # Caller may inject yy_validHigh / yy_validLow / yy_breakoutDetected / yy_breakdownDetected.
    yy_validHigh = _attr_or_false("yy_validHigh")
    yy_validLow = _attr_or_false("yy_validLow")
    yy_breakoutDetected = _attr_or_false("yy_breakoutDetected")
    yy_breakdownDetected = _attr_or_false("yy_breakdownDetected")

    # --- Master offset alignment (FS source L1079-1081) ---
    moff = 1 if i_req_fvg else 0
    def _align(s: pd.Series) -> pd.Series:
        return _nz_b(s.shift(moff)) if moff != 0 else _nz_b(s)

    al_BullPBJ = _align(sigBullPBJ); al_BullPB = _align(sigBullPB)
    al_BearPBJ = _align(sigBearPBJ); al_BearPB = _align(sigBearPB)
    al_anyBullPBJ = _align(anyBullPBJ); al_anyBearPBJ = _align(anyBearPBJ)
    al_anyBullPB = _align(anyBullPB); al_anyBearPB = _align(anyBearPB)
    al_FAUNABull = _align(sigFAUNABull); al_FAUNABear = _align(sigFAUNABear)
    al_DISPBull = _align(sigDISPBull); al_DISPBear = _align(sigDISPBear)
    al_BullRVOL1x = _align(sigBullRVOL1x); al_BearRVOL1x = _align(sigBearRVOL1x)
    al_GrandSlam = _align(sigGrandSlam); al_MOAB = _align(sigMOAB)
    al_bullHV = _align(gz_bullHV); al_bearHV = _align(gz_bearHV)
    al_bullGZI = _align(gz_bullGZI); al_bearGZI = _align(gz_bearGZI)
    al_isFirstBar = _align(is_new_sess)
    al_PUP = _align(sigPUP); al_PPD = _align(sigPPD)
    al_HV = _align(sigHV)
    al_WhaleBull = _align(sigWhaleBull); al_WhaleBear = _align(sigWhaleBear)
    al_SAAB = _align(sigSAAB); al_Kratos = _align(sigKratos)
    al_SL = _align(yy_validLow); al_SH = _align(yy_validHigh)
    al_Breakout = _align(yy_breakoutDetected); al_Breakdown = _align(yy_breakdownDetected)

    al_anyBullRVOL = al_BullRVOL1x | al_GrandSlam
    al_anyBearRVOL = al_BearRVOL1x | al_MOAB

    # --- Directional confirm (FS source L1144-1148) ---
    dirConfBull = al_FAUNABull | sigDISPBull
    dirConfBear = al_FAUNABear | sigDISPBear
    dirConfBullRaw = sigFAUNABull | sigDISPBull
    dirConfBearRaw = sigFAUNABear | sigDISPBear

    # --- First-bar gates (FS source L1070-1074, L1116-1117) ---
    dir0 = sigFAUNABull | sigFAUNABear | sigDISPBull | sigDISPBear | anyBullPBJ | anyBearPBJ
    fb0 = (~bool(p["firstBarOnly"])) | (is_new_sess & dir0)
    yyR = int(p["yy_rightBars"])
    dirs = (_nz_b(sigFAUNABull.shift(yyR)) | _nz_b(sigFAUNABear.shift(yyR)) |
            _nz_b(sigDISPBull.shift(yyR)) | _nz_b(sigDISPBear.shift(yyR)) |
            _nz_b(anyBullPBJ.shift(yyR)) | _nz_b(anyBearPBJ.shift(yyR)))
    fbs = (~bool(p["firstBarOnly"])) | (_nz_b(is_new_sess.shift(yyR)) & dirs)
    dirm = al_FAUNABull | al_FAUNABear | sigDISPBull | sigDISPBear | al_anyBullPBJ | al_anyBearPBJ
    fbm = (~bool(p["firstBarOnly"])) | (al_isFirstBar & dirm)

    # =========================================================================
    # FLOOR 2: COMBINATION SIGNALS — Fauna-Shifu's JUMBO / CIA / 1ST_PUP set.
    # =========================================================================

    # --- DOUBLE DISP ---
    sigDoubleDispBull = sigDISPBull & al_FAUNABull & _nz_b(sigDISPBull.shift(1)) & _nz_b(al_FAUNABull.shift(1)) & (al_PUP | al_anyBullPBJ)
    sigDoubleDispBear = sigDISPBear & al_FAUNABear & _nz_b(sigDISPBear.shift(1)) & _nz_b(al_FAUNABear.shift(1)) & (al_PPD | al_anyBearPBJ)

    # --- PUP COMBO / PPD COMBO (1ST_PUP: back-to-back with PUP/PPD) ---
    pupComboConfBull = sigDISPBull_pup | al_FAUNABull | yy_breakoutDetected
    pupComboConfBear = sigDISPBear_pup | al_FAUNABear | yy_breakdownDetected
    sigPUPCombo = conf & pupComboConfBull & al_PUP & _nz_b(pupComboConfBull.shift(1)) & _nz_b(al_PUP.shift(1))
    sigPPDCombo = conf & pupComboConfBear & al_PPD & _nz_b(pupComboConfBear.shift(1)) & _nz_b(al_PPD.shift(1))

    # --- FULL STACK ---
    sigFullStackBull = al_anyBullRVOL & dirConfBull & al_anyBullPBJ
    sigFullStackBear = al_anyBearRVOL & dirConfBear & al_anyBearPBJ

    # --- FVG STACK ---
    sigFVGStackBull = al_anyBullRVOL & dirConfBull & gz_bullHV & gz_bullGZI
    sigFVGStackBear = al_anyBearRVOL & dirConfBear & gz_bearHV & gz_bearGZI

    # --- SUPER COMBO (ULTRA decomposed PBJ vs PB, the CANONICAL name) ---
    # Per VALIDATE 7 — these four are the Group-C decomposition.
    sigSuperBullPBJ = conf & dirConfBull & al_anyBullPBJ & al_anyBullRVOL
    sigSuperBullPB = conf & dirConfBull & al_anyBullPB & al_anyBullRVOL
    sigSuperBearPBJ = conf & dirConfBear & al_anyBearPBJ & al_anyBearRVOL
    sigSuperBearPB = conf & dirConfBear & al_anyBearPB & al_anyBearRVOL
    sigAnySuperBull = sigSuperBullPBJ | sigSuperBullPB
    sigAnySuperBear = sigSuperBearPBJ | sigSuperBearPB

    # --- MUSASHI (CIA: GZI/HV + PUP/PPD + Whale + anyPBJ) ---
    sigMusashiBull = conf & (gz_bullGZI | gz_bullHV) & al_PUP & al_WhaleBull & al_anyBullPBJ
    sigMusashiBear = conf & (gz_bearGZI | gz_bearHV) & al_PPD & al_WhaleBear & al_anyBearPBJ

    # --- GRIPEN (CIA: SAAB + FAUNA-or-DISP + PB-or-PBJ on session-start with valid pivot) ---
    sigGripenBull = (conf & yy_validLow & _nz_b(is_new_sess.shift(yyR)) &
                     (_nz_b(sigSAAB.shift(yyR)) | _nz_b(sigBullRVOL1x.shift(yyR)) | _nz_b(sigGrandSlam.shift(yyR))) &
                     (_nz_b(sigFAUNABull.shift(yyR)) | _nz_b(sigDISPBull.shift(yyR))) &
                     (_nz_b(anyBullPB.shift(yyR)) | _nz_b(anyBullPBJ.shift(yyR))))
    sigGripenBear = (conf & yy_validHigh & _nz_b(is_new_sess.shift(yyR)) &
                     (_nz_b(sigKratos.shift(yyR)) | _nz_b(sigBearRVOL1x.shift(yyR)) | _nz_b(sigMOAB.shift(yyR))) &
                     (_nz_b(sigFAUNABear.shift(yyR)) | _nz_b(sigDISPBear.shift(yyR))) &
                     (_nz_b(anyBearPB.shift(yyR)) | _nz_b(anyBearPBJ.shift(yyR))))

    # --- SAAB² / KRATOS² (JUMBO: squared RVOL weapon, back-to-back) ---
    saab2_reqConfirm = bool(p["saab2_reqConfirm"])
    saab2_b1_rvol = _nz_b(sigSAAB.shift(1)) | _nz_b(sigBullRVOL1x.shift(1)) | _nz_b(sigGrandSlam.shift(1))
    saab2_b2_rvol = sigSAAB | sigBullRVOL1x | sigGrandSlam
    saab2_b1_qual_chk = _nz_b(sigFAUNABull.shift(1)) | _nz_b(sigDISPBull.shift(1)) | _nz_b(sigPUP.shift(1)) | _nz_b(gz_bullHV.shift(1)) | _nz_b(gz_bullGZI.shift(1))
    saab2_b2_qual_chk = sigFAUNABull | sigDISPBull | sigPUP | gz_bullHV | gz_bullGZI
    saab2_b1_qual = pd.Series(True, index=df.index) if not saab2_reqConfirm else saab2_b1_qual_chk
    saab2_b2_qual = pd.Series(True, index=df.index) if not saab2_reqConfirm else saab2_b2_qual_chk
    saab2_pp_pbj = sigPUP | _nz_b(sigPUP.shift(1)) | anyBullPBJ | _nz_b(anyBullPBJ.shift(1))
    sigSAABSq = conf & saab2_b1_rvol & saab2_b2_rvol & saab2_b1_qual & saab2_b2_qual & saab2_pp_pbj

    krat2_b1_rvol = _nz_b(sigKratos.shift(1)) | _nz_b(sigBearRVOL1x.shift(1)) | _nz_b(sigMOAB.shift(1))
    krat2_b2_rvol = sigKratos | sigBearRVOL1x | sigMOAB
    krat2_b1_qual_chk = _nz_b(sigFAUNABear.shift(1)) | _nz_b(sigDISPBear.shift(1)) | _nz_b(sigPPD.shift(1)) | _nz_b(gz_bearHV.shift(1)) | _nz_b(gz_bearGZI.shift(1))
    krat2_b2_qual_chk = sigFAUNABear | sigDISPBear | sigPPD | gz_bearHV | gz_bearGZI
    krat2_b1_qual = pd.Series(True, index=df.index) if not saab2_reqConfirm else krat2_b1_qual_chk
    krat2_b2_qual = pd.Series(True, index=df.index) if not saab2_reqConfirm else krat2_b2_qual_chk
    krat2_pp_pbj = sigPPD | _nz_b(sigPPD.shift(1)) | anyBearPBJ | _nz_b(anyBearPBJ.shift(1))
    sigKRATOSSq = conf & krat2_b1_rvol & krat2_b2_rvol & krat2_b1_qual & krat2_b2_qual & krat2_pp_pbj

    # --- TYPHOON (CIA: pivot + FAUNA-or-DISP + extras) ---
    typh_bull_extra = _nz_b(sigPUP.shift(yyR)) | (_nz_b(sigWhaleBull.shift(yyR)) & _nz_b(anyBullPBJ.shift(yyR)))
    typh_bear_extra = _nz_b(sigPPD.shift(yyR)) | (_nz_b(sigWhaleBear.shift(yyR)) & _nz_b(anyBearPBJ.shift(yyR)))
    sigTyphoonBull = (conf & yy_validLow & _nz_b(is_new_sess.shift(yyR)) &
                      (_nz_b(sigFAUNABull.shift(yyR)) | _nz_b(sigDISPBull.shift(yyR))) & typh_bull_extra)
    sigTyphoonBear = (conf & yy_validHigh & _nz_b(is_new_sess.shift(yyR)) &
                      (_nz_b(sigFAUNABear.shift(yyR)) | _nz_b(sigDISPBear.shift(yyR))) & typh_bear_extra)

    # --- TOMCAT (CIA: first-bar + dirConfRaw + 2-of-3 {PUP/PPD, Whale, anyPBJ}) ---
    tom_bull_cnt = sigPUP.astype(int) + sigWhaleBull.astype(int) + anyBullPBJ.astype(int)
    tom_bear_cnt = sigPPD.astype(int) + sigWhaleBear.astype(int) + anyBearPBJ.astype(int)
    sigTomcatBull = conf & is_new_sess & dirConfBullRaw & (tom_bull_cnt >= 2)
    sigTomcatBear = conf & is_new_sess & dirConfBearRaw & (tom_bear_cnt >= 2)

    # --- PAF PUP B2B / PAF PPD B2B (1ST_PUP: PUP+FAUNA back-to-back) ---
    sigPAFBull = conf & sigPUP & sigFAUNABull & _nz_b(sigPUP.shift(1)) & _nz_b(sigFAUNABull.shift(1))
    sigPAFBear = conf & sigPPD & sigFAUNABear & _nz_b(sigPPD.shift(1)) & _nz_b(sigFAUNABear.shift(1))

    # =========================================================================
    # FAUNA+ DENSITY ENGINE (Alpha–Echo density sets, Foxtrot 4-in-4, Golf)
    # =========================================================================

    fp_al_fauna_bull = _nz_b(sigFAUNABull.shift(1))
    fp_al_fauna_bear = _nz_b(sigFAUNABear.shift(1))
    fp_al_PUP = _nz_b(sigPUP.shift(1))
    fp_al_PPD = _nz_b(sigPPD.shift(1))
    fp_hvgz_bull = gz_bullHV | gz_bullGZI
    fp_hvgz_bear = gz_bearHV | gz_bearGZI

    def _fp_disp_bull(range_type: str, multiplier: int) -> pd.Series:
        candle_range = _disp_range(df, range_type)
        std_val = _stdev(candle_range, 100)
        thresh = std_val * multiplier
        prev_disp = (candle_range.shift(1) > thresh.shift(1)) | _nz_b(sigAddLong1.shift(1))
        bull_fvg = (df["low"] > df["high"].shift(2)) & (df["open"].shift(1) < df["close"].shift(1))
        return conf & bull_fvg & prev_disp

    def _fp_disp_bear(range_type: str, multiplier: int) -> pd.Series:
        candle_range = _disp_range(df, range_type)
        std_val = _stdev(candle_range, 100)
        thresh = std_val * multiplier
        prev_disp = (candle_range.shift(1) > thresh.shift(1)) | _nz_b(sigAddShort1.shift(1))
        bear_fvg = (df["high"] < df["low"].shift(2)) & (df["open"].shift(1) > df["close"].shift(1))
        return conf & bear_fvg & prev_disp

    def _fp_count(sig: pd.Series, lookback: int) -> pd.Series:
        # Pine f_fp_count is a backward-scanning sum over [i .. i-(lookback-1)].
        a = _nz_b(sig).to_numpy().astype(int)
        return pd.Series(
            np.array([a[max(0, i - lookback + 1):i + 1].sum() for i in range(len(a))]),
            index=sig.index,
        )

    def _fp_chain(raw_bull: pd.Series, raw_bear: pd.Series) -> pd.Series:
        """chain := stays True from new_sess; grace=1; cleared after 2-bar idle."""
        rb = _nz_b(raw_bull).to_numpy()
        rr = _nz_b(raw_bear).to_numpy()
        nd_ = nd_arr
        chain = np.zeros(len(df), dtype=bool); grace = 0; active = False
        for i in range(len(df)):
            if nd_[i]:
                active = True; grace = 1
            elif active and not (rb[i] or rr[i]):
                if grace > 0:
                    grace -= 1
                else:
                    active = False
            chain[i] = active
        return pd.Series(chain, index=df.index)

    def _fp_emit(letter: str) -> tuple:
        rng = p[f"fp_{letter}_rng"]
        mult = int(p[f"fp_{letter}_mult"])
        req = int(p[f"fp_{letter}_req"])
        win = int(p[f"fp_{letter}_win"])
        fb = bool(p[f"fp_{letter}_fb"])
        f_rq = int(p[f"fp_{letter}_fauna_rq"])
        pp_rq = int(p[f"fp_{letter}_pp_rq"])
        fvg_rq = int(p[f"fp_{letter}_fvg_rq"])
        show_key = {"a": "show_Alpha", "b": "show_Bravo", "c": "show_Charlie",
                    "d": "show_Delta", "e": "show_Echo"}[letter]
        show = bool(p[show_key])

        raw_bull = _fp_disp_bull(rng, mult)
        raw_bear = _fp_disp_bear(rng, mult)
        chain = _fp_chain(raw_bull, raw_bear)
        bull_sig = (chain & raw_bull) if fb else raw_bull
        bear_sig = (chain & raw_bear) if fb else raw_bear

        ok_bull = conf & show & (_fp_count(bull_sig, win) >= req)
        ok_bear = conf & show & (_fp_count(bear_sig, win) >= req)
        if f_rq > 0:
            ok_bull &= (_fp_count(fp_al_fauna_bull, win) >= f_rq)
            ok_bear &= (_fp_count(fp_al_fauna_bear, win) >= f_rq)
        if pp_rq > 0:
            ok_bull &= (_fp_count(fp_al_PUP, win) >= pp_rq)
            ok_bear &= (_fp_count(fp_al_PPD, win) >= pp_rq)
        if fvg_rq > 0:
            ok_bull &= (_fp_count(fp_hvgz_bull, win) >= fvg_rq)
            ok_bear &= (_fp_count(fp_hvgz_bear, win) >= fvg_rq)
        return ok_bull, ok_bear, raw_bull, raw_bear

    sigAlphaBull, sigAlphaBear, fp_a_raw_bull, fp_a_raw_bear = _fp_emit("a")
    sigBravoBull, sigBravoBear, fp_b_raw_bull, fp_b_raw_bear = _fp_emit("b")
    sigCharlieBull, sigCharlieBear, fp_c_raw_bull, fp_c_raw_bear = _fp_emit("c")
    sigDeltaBull, sigDeltaBear, fp_d_raw_bull, fp_d_raw_bear = _fp_emit("d")
    sigEchoBull, sigEchoBear, fp_e_raw_bull, fp_e_raw_bear = _fp_emit("e")

    # --- FOXTROT (Fauna 4-in-4) ---
    sigFoxtrotBull = (conf & bool(p["show_Foxtrot"]) & sigFAUNABull &
                      _nz_b(sigFAUNABull.shift(1)) & _nz_b(sigFAUNABull.shift(2)) & _nz_b(sigFAUNABull.shift(3)))
    sigFoxtrotBear = (conf & bool(p["show_Foxtrot"]) & sigFAUNABear &
                      _nz_b(sigFAUNABear.shift(1)) & _nz_b(sigFAUNABear.shift(2)) & _nz_b(sigFAUNABear.shift(3)))

    # --- GOLF (PUP² / PPD² B2B with FAUNA + density) ---
    fp_any_raw_bull = ((bool(p["show_Alpha"]) & fp_a_raw_bull) |
                       (bool(p["show_Bravo"]) & fp_b_raw_bull) |
                       (bool(p["show_Charlie"]) & fp_c_raw_bull) |
                       (bool(p["show_Delta"]) & fp_d_raw_bull) |
                       (bool(p["show_Echo"]) & fp_e_raw_bull))
    fp_any_raw_bear = ((bool(p["show_Alpha"]) & fp_a_raw_bear) |
                       (bool(p["show_Bravo"]) & fp_b_raw_bear) |
                       (bool(p["show_Charlie"]) & fp_c_raw_bear) |
                       (bool(p["show_Delta"]) & fp_d_raw_bear) |
                       (bool(p["show_Echo"]) & fp_e_raw_bear))
    sigGolfBull = (conf & bool(p["show_Golf"]) & fp_any_raw_bull & fp_al_fauna_bull & fp_al_PUP &
                   _nz_b(fp_any_raw_bull.shift(1)) & _nz_b(fp_al_fauna_bull.shift(1)) & _nz_b(fp_al_PUP.shift(1)))
    sigGolfBear = (conf & bool(p["show_Golf"]) & fp_any_raw_bear & fp_al_fauna_bear & fp_al_PPD &
                   _nz_b(fp_any_raw_bear.shift(1)) & _nz_b(fp_al_fauna_bear.shift(1)) & _nz_b(fp_al_PPD.shift(1)))

    # --- OPENING DRIVE (1ST_PUP — first-N-bars) ---
    od_max = int(p["od_max"])
    od_rng = _disp_range(df, p["od_rng"])
    od_std = _stdev(od_rng, 100)
    od_threshold = od_std * int(p["od_mult"])
    od_prev_disp_bull = (od_rng.shift(1) > od_threshold.shift(1)) | _nz_b(sigAddLong1.shift(1))
    od_prev_disp_bear = (od_rng.shift(1) > od_threshold.shift(1)) | _nz_b(sigAddShort1.shift(1))
    od_bull_fvg = (df["low"] > df["high"].shift(2)) & (df["open"].shift(1) < df["close"].shift(1))
    od_bear_fvg = (df["high"] < df["low"].shift(2)) & (df["open"].shift(1) > df["close"].shift(1))
    sigODBull = (conf & bool(p["show_OD"]) & (sessionBarCount <= od_max) &
                 od_bull_fvg & od_prev_disp_bull & pp_priceUp & pp_volBull)
    sigODBear = (conf & bool(p["show_OD"]) & (sessionBarCount <= od_max) &
                 od_bear_fvg & od_prev_disp_bear & pp_priceDn & pp_volBear)

    # =========================================================================
    # FLOOR 3: SESSION SIGNALS — KATANA (1ST_PUP)
    # Katana uses per-session "yesterday" snapshots; emulate via streaming loop.
    # =========================================================================
    n = len(df)
    kat_y_bull_hv = np.zeros(n, dtype=bool)
    kat_y_bear_hv = np.zeros(n, dtype=bool)
    kat_y_bull_gzi = np.zeros(n, dtype=bool)
    kat_y_bear_gzi = np.zeros(n, dtype=bool)
    kat_y_bull_fauna = np.zeros(n, dtype=bool)
    kat_y_bear_fauna = np.zeros(n, dtype=bool)
    kat_y_bull_disp = np.zeros(n, dtype=bool)
    kat_y_bear_disp = np.zeros(n, dtype=bool)
    kat_y_bull_bo = np.zeros(n, dtype=bool)
    kat_y_bear_bd = np.zeros(n, dtype=bool)
    last_close_arr = np.zeros(n)

    arr_bullHV = _nz_b(gz_bullHV).to_numpy()
    arr_bearHV = _nz_b(gz_bearHV).to_numpy()
    arr_bullGZI = _nz_b(gz_bullGZI).to_numpy()
    arr_bearGZI = _nz_b(gz_bearGZI).to_numpy()
    arr_FB = _nz_b(sigFAUNABull).to_numpy()
    arr_FR = _nz_b(sigFAUNABear).to_numpy()
    arr_DB = _nz_b(sigDISPBull).to_numpy()
    arr_DR = _nz_b(sigDISPBear).to_numpy()
    arr_BO = _nz_b(yy_breakoutDetected).to_numpy()
    arr_BD = _nz_b(yy_breakdownDetected).to_numpy()

    yb_hv = False; yr_hv = False; yb_gzi = False; yr_gzi = False
    yb_fa = False; yr_fa = False; yb_dp = False; yr_dp = False
    yb_bo = False; yr_bd = False
    last_close = 0.0
    for i in range(n):
        if nd_arr[i] and i > 0:
            last_close = closes[i - 1]
            yb_hv = arr_bullHV[i]; yr_hv = arr_bearHV[i]
            yb_gzi = arr_bullGZI[i]; yr_gzi = arr_bearGZI[i]
            yb_fa = arr_FB[i - 1] if i >= 1 else False
            yr_fa = arr_FR[i - 1] if i >= 1 else False
            yb_dp = arr_DB[i - 1] if i >= 1 else False
            yr_dp = arr_DR[i - 1] if i >= 1 else False
            yb_bo = arr_BO[i - 1] if i >= 1 else False
            yr_bd = arr_BD[i - 1] if i >= 1 else False
        last_close_arr[i] = last_close
        kat_y_bull_hv[i] = yb_hv; kat_y_bear_hv[i] = yr_hv
        kat_y_bull_gzi[i] = yb_gzi; kat_y_bear_gzi[i] = yr_gzi
        kat_y_bull_fauna[i] = yb_fa; kat_y_bear_fauna[i] = yr_fa
        kat_y_bull_disp[i] = yb_dp; kat_y_bear_disp[i] = yr_dp
        kat_y_bull_bo[i] = yb_bo; kat_y_bear_bd[i] = yr_bd

    last_close_s = pd.Series(last_close_arr, index=df.index)
    kat_dir_bull = (df["close"].shift(1) > last_close_s) & (df["close"].shift(1) > df["open"].shift(1))
    kat_dir_bear = (df["close"].shift(1) < last_close_s) & (df["close"].shift(1) < df["open"].shift(1))

    kat_yest_bull_hv = pd.Series(kat_y_bull_hv, index=df.index)
    kat_yest_bear_hv = pd.Series(kat_y_bear_hv, index=df.index)
    kat_yest_bull_gzi = pd.Series(kat_y_bull_gzi, index=df.index)
    kat_yest_bear_gzi = pd.Series(kat_y_bear_gzi, index=df.index)
    kat_yest_bull_fauna = pd.Series(kat_y_bull_fauna, index=df.index)
    kat_yest_bear_fauna = pd.Series(kat_y_bear_fauna, index=df.index)
    kat_yest_bull_disp = pd.Series(kat_y_bull_disp, index=df.index)
    kat_yest_bear_disp = pd.Series(kat_y_bear_disp, index=df.index)
    kat_yest_bull_bo = pd.Series(kat_y_bull_bo, index=df.index)
    kat_yest_bear_bd = pd.Series(kat_y_bear_bd, index=df.index)

    kat_yest_dirconf_bull = kat_yest_bull_fauna | kat_yest_bull_disp
    kat_yest_dirconf_bear = kat_yest_bear_fauna | kat_yest_bear_disp
    kat_today_dirconf_bull = _nz_b(sigFAUNABull.shift(1)) | _nz_b(sigDISPBull.shift(1))
    kat_today_dirconf_bear = _nz_b(sigFAUNABear.shift(1)) | _nz_b(sigDISPBear.shift(1))
    is_new_sess_prev = _nz_b(is_new_sess.shift(1))

    sigKatanaBull_A = (conf & is_new_sess_prev & kat_yest_bull_hv & kat_yest_dirconf_bull &
                       gz_bullHV & gz_bullGZI & kat_today_dirconf_bull & kat_dir_bull)
    sigKatanaBear_A = (conf & is_new_sess_prev & kat_yest_bear_hv & kat_yest_dirconf_bear &
                       gz_bearHV & gz_bearGZI & kat_today_dirconf_bear & kat_dir_bear)
    sigKatanaBull_B = (conf & is_new_sess_prev & kat_yest_dirconf_bull &
                       (kat_yest_bull_hv | kat_yest_bull_gzi | kat_yest_bull_bo) &
                       gz_bullGZI & kat_today_dirconf_bull & kat_dir_bull)
    sigKatanaBear_B = (conf & is_new_sess_prev & kat_yest_dirconf_bear &
                       (kat_yest_bear_hv | kat_yest_bear_gzi | kat_yest_bear_bd) &
                       gz_bearGZI & kat_today_dirconf_bear & kat_dir_bear)
    sigKatanaBull_E = (conf & is_new_sess_prev & kat_yest_bull_hv & kat_yest_dirconf_bull &
                       _nz_b(sigPUP.shift(1)) & gz_bullHV & gz_bullGZI &
                       kat_today_dirconf_bull & kat_dir_bull)
    sigKatanaBear_E = (conf & is_new_sess_prev & kat_yest_bear_hv & kat_yest_dirconf_bear &
                       _nz_b(sigPPD.shift(1)) & gz_bearHV & gz_bearGZI &
                       kat_today_dirconf_bear & kat_dir_bear)
    sigKatanaRawBull = sigKatanaBull_A | sigKatanaBull_B | sigKatanaBull_E
    sigKatanaRawBear = sigKatanaBear_A | sigKatanaBear_B | sigKatanaBear_E
    sigKatanaBull = sigKatanaRawBull & (_nz_b(anyBullPBJ.shift(1)) | _nz_b(sigPUP.shift(1)))
    sigKatanaBear = sigKatanaRawBear & (_nz_b(anyBearPBJ.shift(1)) | _nz_b(sigPPD.shift(1)))

    # =========================================================================
    # NAGASAKI DIRECTIONAL (HEV + directional)
    # =========================================================================
    nag_dir_bull = (sigBullRVOL1x | sigGrandSlam | sigFAUNABull | sigDISPBull |
                    anyBullPBJ | sigPUP | sigWhaleBull | gz_bullHV | gz_bullGZI | sigPAFBull)
    nag_dir_bear = (sigBearRVOL1x | sigMOAB | sigFAUNABear | sigDISPBear |
                    anyBearPBJ | sigPPD | sigWhaleBear | gz_bearHV | gz_bearGZI | sigPAFBear)
    sigNagasakiBull = conf & sigNagasaki & nag_dir_bull
    sigNagasakiBear = conf & sigNagasaki & nag_dir_bear

    # =========================================================================
    # MASTER FILTER (KC + Candle) — STUBBED: needs Shifu KC ma series.
    # Caller may inject `sh_kc_ma` via df.attrs; else MF treated as TRUE everywhere.
    # =========================================================================
    sh_kc_ma = df.attrs.get("sh_kc_ma")
    if sh_kc_ma is not None:
        sh_kc_ma = sh_kc_ma.reindex(df.index)
        mode_bull = p["sh_mfModeBull"]
        mode_bear = p["sh_mfModeBear"]
        if mode_bull == "KC + Candle":
            mf_bull = conf & (df["high"] >= sh_kc_ma) & (df["close"] > df["open"])
        elif mode_bull == "Q3 + KC + Candle":
            # Q3 series also stubbed; allow caller to inject sh_Quotient3.
            sh_q3 = df.attrs.get("sh_Quotient3", pd.Series(np.nan, index=df.index))
            mf_bull = conf & (sh_q3 < 0) & (df["high"] >= sh_kc_ma) & (df["close"] > df["open"])
        else:
            mf_bull = pd.Series(True, index=df.index)
        if mode_bear == "KC + Candle":
            mf_bear = conf & (df["low"] <= sh_kc_ma) & (df["close"] < df["open"])
        elif mode_bear == "Q3 + KC + Candle":
            sh_q3 = df.attrs.get("sh_Quotient3", pd.Series(np.nan, index=df.index))
            mf_bear = conf & (sh_q3 > 0) & (df["low"] <= sh_kc_ma) & (df["close"] < df["open"])
        else:
            mf_bear = pd.Series(True, index=df.index)
    else:
        mf_bull = pd.Series(True, index=df.index)
        mf_bear = pd.Series(True, index=df.index)
    al_mf_bull = _align(mf_bull)
    al_mf_bear = _align(mf_bear)

    # =========================================================================
    # FINAL PLOT GATES — apply show_* + first-bar gate + master filter.
    # Mirrors the Pine plotshape() expressions exactly.
    # =========================================================================
    fire_Super_Bull = bool(p["show_SuperBull"]) & sigAnySuperBull & fbm & al_mf_bull
    fire_Super_Bear = bool(p["show_SuperBear"]) & sigAnySuperBear & fbm & al_mf_bear
    fire_SuperBullPBJ = bool(p["show_SuperBull"]) & sigSuperBullPBJ & fbm & al_mf_bull
    fire_SuperBullPB = bool(p["show_SuperBull"]) & sigSuperBullPB & fbm & al_mf_bull
    fire_SuperBearPBJ = bool(p["show_SuperBear"]) & sigSuperBearPBJ & fbm & al_mf_bear
    fire_SuperBearPB = bool(p["show_SuperBear"]) & sigSuperBearPB & fbm & al_mf_bear

    fire_GrandSlam = bool(p["show_GrandSlam"]) & sigGrandSlam & fb0 & mf_bull
    fire_MOAB = bool(p["show_MOAB"]) & sigMOAB & fb0 & mf_bear

    fire_WhaleBull = bool(p["show_WhaleBull"]) & sigWhaleBull & mf_bull
    fire_WhaleBear = bool(p["show_WhaleBear"]) & sigWhaleBear & mf_bear

    fire_SAABSq = bool(p["show_SAABSq"]) & sigSAABSq & mf_bull
    fire_KRATOSSq = bool(p["show_KRATOSSq"]) & sigKRATOSSq & mf_bear

    fire_TyphoonBull = bool(p["show_TyphoonBull"]) & sigTyphoonBull & fbs & _nz_b(mf_bull.shift(yyR))
    fire_TyphoonBear = bool(p["show_TyphoonBear"]) & sigTyphoonBear & fbs & _nz_b(mf_bear.shift(yyR))

    fire_TomcatBull = bool(p["show_TomcatBull"]) & sigTomcatBull & fb0 & mf_bull
    fire_TomcatBear = bool(p["show_TomcatBear"]) & sigTomcatBear & fb0 & mf_bear

    nag_special_bull = sigTyphoonBull | sigWhaleBull | sigAnySuperBull | sigGolfBull | sigTomcatBull | sigFullStackBull | sigFVGStackBull
    nag_special_bear = sigTyphoonBear | sigWhaleBear | sigAnySuperBear | sigGolfBear | sigTomcatBear | sigFullStackBear | sigFVGStackBear
    nag_gate_bull = bool(p["show_Nagasaki"]) | nag_special_bull
    nag_gate_bear = bool(p["show_Nagasaki"]) | nag_special_bear
    fire_NagasakiBull = nag_gate_bull & sigNagasakiBull & mf_bull
    fire_NagasakiBear = nag_gate_bear & sigNagasakiBear & mf_bear

    fire_PAFBull = bool(p["show_PAFBull"]) & sigPAFBull & mf_bull
    fire_PAFBear = bool(p["show_PAFBear"]) & sigPAFBear & mf_bear

    # FAUNA+ density (Alpha–Foxtrot combined) — gated by mf_bull[1] in Pine.
    al_mf_bull_1 = _nz_b(mf_bull.shift(1))
    al_mf_bear_1 = _nz_b(mf_bear.shift(1))
    fire_AlphaBull = sigAlphaBull & al_mf_bull_1
    fire_AlphaBear = sigAlphaBear & al_mf_bear_1
    fire_BravoBull = sigBravoBull & al_mf_bull_1
    fire_BravoBear = sigBravoBear & al_mf_bear_1
    fire_CharlieBull = sigCharlieBull & al_mf_bull_1
    fire_CharlieBear = sigCharlieBear & al_mf_bear_1
    fire_DeltaBull = sigDeltaBull & al_mf_bull_1
    fire_DeltaBear = sigDeltaBear & al_mf_bear_1
    fire_EchoBull = sigEchoBull & al_mf_bull_1
    fire_EchoBear = sigEchoBear & al_mf_bear_1
    fire_FoxtrotBull = sigFoxtrotBull & al_mf_bull_1
    fire_FoxtrotBear = sigFoxtrotBear & al_mf_bear_1

    fire_GolfBull = sigGolfBull & al_mf_bull_1
    fire_GolfBear = sigGolfBear & al_mf_bear_1

    fire_ODBull = sigODBull & al_mf_bull_1
    fire_ODBear = sigODBear & al_mf_bear_1

    fire_KatanaBull = bool(p["show_Katana"]) & sigKatanaBull & al_mf_bull_1
    fire_KatanaBear = bool(p["show_Katana"]) & sigKatanaBear & al_mf_bear_1

    fire_MusashiBull = bool(p["show_Musashi"]) & sigMusashiBull & fbm & al_mf_bull
    fire_MusashiBear = bool(p["show_Musashi"]) & sigMusashiBear & fbm & al_mf_bear

    fire_DoubleDispBull = bool(p["show_DoubleDisp"]) & sigDoubleDispBull & al_mf_bull
    fire_DoubleDispBear = bool(p["show_DoubleDisp"]) & sigDoubleDispBear & al_mf_bear

    fire_PUPCombo = bool(p["show_PUP"]) & sigPUPCombo & al_mf_bull
    fire_PPDCombo = bool(p["show_PPD"]) & sigPPDCombo & al_mf_bear

    fire_FullStackBull = bool(p["show_FullStack"]) & sigFullStackBull & fbm & al_mf_bull
    fire_FullStackBear = bool(p["show_FullStack"]) & sigFullStackBear & fbm & al_mf_bear

    fire_FVGStackBull = bool(p["show_FVGStack"]) & sigFVGStackBull & fbm & al_mf_bull
    fire_FVGStackBear = bool(p["show_FVGStack"]) & sigFVGStackBear & fbm & al_mf_bear

    cache.update({
        # Primitives
        "sigBullRVOL1x": sigBullRVOL1x, "sigBearRVOL1x": sigBearRVOL1x,
        "sigGrandSlam": sigGrandSlam, "sigMOAB": sigMOAB,
        "sigSAAB": sigSAAB, "sigKratos": sigKratos,
        "sigAddLong1": sigAddLong1, "sigAddShort1": sigAddShort1,
        "sigFAUNABull": sigFAUNABull, "sigFAUNABear": sigFAUNABear,
        "sigDISPBull": sigDISPBull, "sigDISPBear": sigDISPBear,
        "sigDISPBull_pup": sigDISPBull_pup, "sigDISPBear_pup": sigDISPBear_pup,
        "sigHV": sigHV, "sigNagasaki": sigNagasaki,
        "sigPUP": sigPUP, "sigPPD": sigPPD,
        "sigAnishBull": sigAnishBull, "sigAnishBear": sigAnishBear,
        "sigBullPBJ": sigBullPBJ, "sigBullPB": sigBullPB,
        "sigBearPBJ": sigBearPBJ, "sigBearPB": sigBearPB,
        "anyBullPBJ": anyBullPBJ, "anyBearPBJ": anyBearPBJ,
        "anyBullPB": anyBullPB, "anyBearPB": anyBearPB,
        "sigWhaleBull": sigWhaleBull, "sigWhaleBear": sigWhaleBear,
        # CANONICAL SUPER (ULTRA-decomposed PBJ vs PB — VALIDATE 7 Group C)
        "sigSuperBullPBJ": sigSuperBullPBJ, "sigSuperBullPB": sigSuperBullPB,
        "sigSuperBearPBJ": sigSuperBearPBJ, "sigSuperBearPB": sigSuperBearPB,
        "sigAnySuperBull": sigAnySuperBull, "sigAnySuperBear": sigAnySuperBear,
        # JUMBO / CIA / 1ST_PUP variants
        "sigSAABSq": sigSAABSq, "sigKRATOSSq": sigKRATOSSq,
        "sigTyphoonBull": sigTyphoonBull, "sigTyphoonBear": sigTyphoonBear,
        "sigTomcatBull": sigTomcatBull, "sigTomcatBear": sigTomcatBear,
        "sigMusashiBull": sigMusashiBull, "sigMusashiBear": sigMusashiBear,
        "sigGripenBull": sigGripenBull, "sigGripenBear": sigGripenBear,
        "sigPAFBull": sigPAFBull, "sigPAFBear": sigPAFBear,
        "sigDoubleDispBull": sigDoubleDispBull, "sigDoubleDispBear": sigDoubleDispBear,
        "sigPUPCombo": sigPUPCombo, "sigPPDCombo": sigPPDCombo,
        "sigFullStackBull": sigFullStackBull, "sigFullStackBear": sigFullStackBear,
        "sigFVGStackBull": sigFVGStackBull, "sigFVGStackBear": sigFVGStackBear,
        # FAUNA+ density
        "sigAlphaBull": sigAlphaBull, "sigAlphaBear": sigAlphaBear,
        "sigBravoBull": sigBravoBull, "sigBravoBear": sigBravoBear,
        "sigCharlieBull": sigCharlieBull, "sigCharlieBear": sigCharlieBear,
        "sigDeltaBull": sigDeltaBull, "sigDeltaBear": sigDeltaBear,
        "sigEchoBull": sigEchoBull, "sigEchoBear": sigEchoBear,
        "sigFoxtrotBull": sigFoxtrotBull, "sigFoxtrotBear": sigFoxtrotBear,
        "sigGolfBull": sigGolfBull, "sigGolfBear": sigGolfBear,
        "sigODBull": sigODBull, "sigODBear": sigODBear,
        "sigKatanaBull": sigKatanaBull, "sigKatanaBear": sigKatanaBear,
        "sigNagasakiBull": sigNagasakiBull, "sigNagasakiBear": sigNagasakiBear,
        # Plot gates (final fires, with show_* + master filter applied)
        "fire_Super_Bull": fire_Super_Bull, "fire_Super_Bear": fire_Super_Bear,
        "fire_SuperBullPBJ": fire_SuperBullPBJ, "fire_SuperBullPB": fire_SuperBullPB,
        "fire_SuperBearPBJ": fire_SuperBearPBJ, "fire_SuperBearPB": fire_SuperBearPB,
        "fire_GrandSlam": fire_GrandSlam, "fire_MOAB": fire_MOAB,
        "fire_WhaleBull": fire_WhaleBull, "fire_WhaleBear": fire_WhaleBear,
        "fire_SAABSq": fire_SAABSq, "fire_KRATOSSq": fire_KRATOSSq,
        "fire_TyphoonBull": fire_TyphoonBull, "fire_TyphoonBear": fire_TyphoonBear,
        "fire_TomcatBull": fire_TomcatBull, "fire_TomcatBear": fire_TomcatBear,
        "fire_NagasakiBull": fire_NagasakiBull, "fire_NagasakiBear": fire_NagasakiBear,
        "fire_PAFBull": fire_PAFBull, "fire_PAFBear": fire_PAFBear,
        "fire_AlphaBull": fire_AlphaBull, "fire_AlphaBear": fire_AlphaBear,
        "fire_BravoBull": fire_BravoBull, "fire_BravoBear": fire_BravoBear,
        "fire_CharlieBull": fire_CharlieBull, "fire_CharlieBear": fire_CharlieBear,
        "fire_DeltaBull": fire_DeltaBull, "fire_DeltaBear": fire_DeltaBear,
        "fire_EchoBull": fire_EchoBull, "fire_EchoBear": fire_EchoBear,
        "fire_FoxtrotBull": fire_FoxtrotBull, "fire_FoxtrotBear": fire_FoxtrotBear,
        "fire_GolfBull": fire_GolfBull, "fire_GolfBear": fire_GolfBear,
        "fire_ODBull": fire_ODBull, "fire_ODBear": fire_ODBear,
        "fire_KatanaBull": fire_KatanaBull, "fire_KatanaBear": fire_KatanaBear,
        "fire_MusashiBull": fire_MusashiBull, "fire_MusashiBear": fire_MusashiBear,
        "fire_DoubleDispBull": fire_DoubleDispBull, "fire_DoubleDispBear": fire_DoubleDispBear,
        "fire_PUPCombo": fire_PUPCombo, "fire_PPDCombo": fire_PPDCombo,
        "fire_FullStackBull": fire_FullStackBull, "fire_FullStackBear": fire_FullStackBear,
        "fire_FVGStackBull": fire_FVGStackBull, "fire_FVGStackBear": fire_FVGStackBear,
    })
    return cache


# ============================================================================
# Public detection functions — every named plot in the Pine source has one.
# ============================================================================
def _wrap(name: str) -> Callable[[pd.DataFrame, Optional[Dict]], pd.Series]:
    def _fn(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
        eng = _ensure_engines(df, _p(params))
        return eng[name].fillna(False).astype(bool)
    _fn.__name__ = f"detect_{name}"
    return _fn


# CANONICAL SUPER family (ULTRA decomposed — VALIDATE 7 Group C)
detect_SuperBullPBJ = _wrap("fire_SuperBullPBJ")
detect_SuperBullPB = _wrap("fire_SuperBullPB")
detect_SuperBearPBJ = _wrap("fire_SuperBearPBJ")
detect_SuperBearPB = _wrap("fire_SuperBearPB")
detect_Super_Bull = _wrap("fire_Super_Bull")
detect_Super_Bear = _wrap("fire_Super_Bear")

# RVOL Weapons
detect_GrandSlam = _wrap("fire_GrandSlam")
detect_MOAB = _wrap("fire_MOAB")

# 1ST_PUP family (Whale, PUP/PPD combo, PAF, Opening Drive, Katana)
detect_WhaleBull = _wrap("fire_WhaleBull")
detect_WhaleBear = _wrap("fire_WhaleBear")
detect_PUPCombo = _wrap("fire_PUPCombo")
detect_PPDCombo = _wrap("fire_PPDCombo")
detect_PAFBull = _wrap("fire_PAFBull")
detect_PAFBear = _wrap("fire_PAFBear")
detect_ODBull = _wrap("fire_ODBull")
detect_ODBear = _wrap("fire_ODBear")
detect_KatanaBull = _wrap("fire_KatanaBull")
detect_KatanaBear = _wrap("fire_KatanaBear")

# JUMBO (squared RVOL weapons)
detect_SAABSq = _wrap("fire_SAABSq")
detect_KRATOSSq = _wrap("fire_KRATOSSq")

# CIA (multi-engine combo specials)
detect_TyphoonBull = _wrap("fire_TyphoonBull")
detect_TyphoonBear = _wrap("fire_TyphoonBear")
detect_TomcatBull = _wrap("fire_TomcatBull")
detect_TomcatBear = _wrap("fire_TomcatBear")
detect_MusashiBull = _wrap("fire_MusashiBull")
detect_MusashiBear = _wrap("fire_MusashiBear")

# Stacks & density
detect_DoubleDispBull = _wrap("fire_DoubleDispBull")
detect_DoubleDispBear = _wrap("fire_DoubleDispBear")
detect_FullStackBull = _wrap("fire_FullStackBull")
detect_FullStackBear = _wrap("fire_FullStackBear")
detect_FVGStackBull = _wrap("fire_FVGStackBull")
detect_FVGStackBear = _wrap("fire_FVGStackBear")

# FAUNA+ density sets
detect_AlphaBull = _wrap("fire_AlphaBull")
detect_AlphaBear = _wrap("fire_AlphaBear")
detect_BravoBull = _wrap("fire_BravoBull")
detect_BravoBear = _wrap("fire_BravoBear")
detect_CharlieBull = _wrap("fire_CharlieBull")
detect_CharlieBear = _wrap("fire_CharlieBear")
detect_DeltaBull = _wrap("fire_DeltaBull")
detect_DeltaBear = _wrap("fire_DeltaBear")
detect_EchoBull = _wrap("fire_EchoBull")
detect_EchoBear = _wrap("fire_EchoBear")
detect_FoxtrotBull = _wrap("fire_FoxtrotBull")
detect_FoxtrotBear = _wrap("fire_FoxtrotBear")
detect_GolfBull = _wrap("fire_GolfBull")
detect_GolfBear = _wrap("fire_GolfBear")

# Nagasaki (HEV + directional)
detect_NagasakiBull = _wrap("fire_NagasakiBull")
detect_NagasakiBear = _wrap("fire_NagasakiBear")


# ============================================================================
# Stubbed engines — Pine-only intrinsics required. Caller may inject
# precomputed series via df.attrs[<name>] before calling any detection.
# ============================================================================
STUBBED: Dict[str, str] = {
    # PBJ engine: full landing-zone array + Supertrend dir-flips (zoo_*).
    # Inject via df.attrs: sigBullPBJ, sigBullPB, sigBearPBJ, sigBearPB.
    "_pbj_engine": (
        "OKEH Zoo PBJ engine (Supertrend + landing-zone array) not reproduced; "
        "inject sigBullPBJ/sigBullPB/sigBearPBJ/sigBearPB via df.attrs"
    ),
    # GZ1 / HV FVG engine: gz_fvg struct array, gz1_dist proximity matching.
    # Inject via df.attrs: gz_bullHV, gz_bearHV, gz_bullGZI, gz_bearGZI.
    "_gz_engine": (
        "GZ1 FVG struct array not reproduced; "
        "inject gz_bullHV/gz_bearHV/gz_bullGZI/gz_bearGZI via df.attrs"
    ),
    # Yin-Yang pivot SR engine: yy_srs array with breakout/breakdown tracking.
    # Inject via df.attrs: yy_validHigh, yy_validLow, yy_breakoutDetected, yy_breakdownDetected.
    "_yy_engine": (
        "Yin-Yang pivot SR (yy_srs array) not reproduced; "
        "inject yy_validHigh/yy_validLow/yy_breakoutDetected/yy_breakdownDetected via df.attrs"
    ),
    # Shifu BHP Q3 + KC + Ping-Pong S/R qualifiers (Ehlers filter chain).
    # Inject via df.attrs: sh_bullQualifier, sh_bearQualifier, sh_kc_ma, sh_Quotient3.
    "_shifu_engine": (
        "Shifu BHP Q3 / KC / Ping-Pong SR qualifier chain not reproduced; "
        "inject sh_bullQualifier/sh_bearQualifier/sh_kc_ma/sh_Quotient3 via df.attrs"
    ),
    # tv_ta.relativeVolume (regular + cumulative) for LONG 1 / SHORT 1.
    # Inject via df.attrs: hybRegRatio, hybCumRatio.
    "_rel_vol_engine": (
        "tv_ta.relativeVolume not reproduced; "
        "inject hybRegRatio/hybCumRatio via df.attrs (else Long1/Short1 stay False)"
    ),
    # Master filter requires sh_kc_ma — without injection MF treated as TRUE.
    "_master_filter": (
        "Master filter (KC + Candle) needs sh_kc_ma; "
        "without injection mf_bull / mf_bear default to TRUE (no MF gating)"
    ),
}


# ============================================================================
# State machines — exposed for the harness; they read from df.attrs.
# ============================================================================
@dataclass
class FaunaPlusChainState:
    """FAUNA+ density-set chain (Alpha–Echo) — session-anchored with grace=1.
    Built into _ensure_engines."""
    name: str = "FaunaPlusChain"


@dataclass
class KatanaYesterdayState:
    """Per-session 'yesterday' snapshot tracker for Katana A/B/E — built into _ensure_engines."""
    name: str = "KatanaYesterday"


@dataclass
class NagasakiState:
    """Streaming all-time-high volume tracker — built into _ensure_engines."""
    name: str = "Nagasaki"


@dataclass
class WhaleVolArrayState:
    """Whale per-bar down/up vol look-around array — built into _ensure_engines."""
    name: str = "WhaleVolArray"


STATE_MACHINES: Dict[str, type] = {
    "FaunaPlusChain": FaunaPlusChainState,
    "KatanaYesterday": KatanaYesterdayState,
    "Nagasaki": NagasakiState,
    "WhaleVolArray": WhaleVolArrayState,
}


# ============================================================================
# DETECTIONS registry — name → detect_* function.
# Names mirror the Pine plotshape() title argument so the harness round-trips
# with the validator.
# ============================================================================
DETECTIONS: Dict[str, Callable] = {
    # CANONICAL SUPER family (ULTRA decomposed — VALIDATE 7 Group C)
    "SuperBullPBJ": detect_SuperBullPBJ,
    "SuperBullPB": detect_SuperBullPB,
    "SuperBearPBJ": detect_SuperBearPBJ,
    "SuperBearPB": detect_SuperBearPB,
    "Super": detect_Super_Bull,  # combined plot is the union; "Super" Bull-flavored
    "Super Bear": detect_Super_Bear,
    # RVOL Weapons
    "Grand Slam": detect_GrandSlam,
    "MOAB": detect_MOAB,
    # 1ST_PUP family
    "Whale+PUP": detect_WhaleBull,
    "Whale+PPD": detect_WhaleBear,
    "PUP Combo": detect_PUPCombo,
    "PPD Combo": detect_PPDCombo,
    "PAF PUP B2B": detect_PAFBull,
    "PAF PPD B2B": detect_PAFBear,
    "Opening Drive Bull": detect_ODBull,
    "Opening Drive Bear": detect_ODBear,
    "Katana Bull": detect_KatanaBull,
    "Katana Bear": detect_KatanaBear,
    # JUMBO
    "SAAB2": detect_SAABSq,
    "KRATOS2": detect_KRATOSSq,
    # CIA
    "Typhoon Bull": detect_TyphoonBull,
    "Typhoon Bear": detect_TyphoonBear,
    "Tomcat Bull": detect_TomcatBull,
    "Tomcat Bear": detect_TomcatBear,
    "Musashi Bull": detect_MusashiBull,
    "Musashi Bear": detect_MusashiBear,
    # Stacks & density
    "Double Disp Bull": detect_DoubleDispBull,
    "Double Disp Bear": detect_DoubleDispBear,
    "Full Stack Bull": detect_FullStackBull,
    "Full Stack Bear": detect_FullStackBear,
    "FVG Stack Bull": detect_FVGStackBull,
    "FVG Stack Bear": detect_FVGStackBear,
    # FAUNA+ density sets (named via the combined "FAUNA+ Bull/Bear" plot,
    # but each letter is independently exposed for granular validation)
    "Alpha Bull": detect_AlphaBull,
    "Alpha Bear": detect_AlphaBear,
    "Bravo Bull": detect_BravoBull,
    "Bravo Bear": detect_BravoBear,
    "Charlie Bull": detect_CharlieBull,
    "Charlie Bear": detect_CharlieBear,
    "Delta Bull": detect_DeltaBull,
    "Delta Bear": detect_DeltaBear,
    "Echo Bull": detect_EchoBull,
    "Echo Bear": detect_EchoBear,
    "Foxtrot Bull": detect_FoxtrotBull,
    "Foxtrot Bear": detect_FoxtrotBear,
    "Golf Bull": detect_GolfBull,
    "Golf Bear": detect_GolfBear,
    # Nagasaki (HEV + directional)
    "Nagasaki Bull": detect_NagasakiBull,
    "Nagasaki Bear": detect_NagasakiBear,
}


if __name__ == "__main__":
    print(f"DETECTIONS: {len(DETECTIONS)}")
    print(f"STUBBED engine notes: {len(STUBBED)}")
    print(f"STATE_MACHINES: {len(STATE_MACHINES)}")
    print("First 10 detection names:")
    for n in list(DETECTIONS)[:10]:
        print("  ", n)
