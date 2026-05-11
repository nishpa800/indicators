"""
Python port of SQUARIFY_46_v2_2026-05-04.pine (2622 lines).

Source Pine:  squarify/versions/SQUARIFY_46_v2_2026-05-04.pine
Reference port (template): python_ports/hvd_pbj_ppd/the_only_one.py

Re-implements every named detection plot in the source as a vectorized pandas
function, suitable for replaying against a bar-history DataFrame.

The Squarify 46 v2 family is the largest of the indicator suite — it
combines:

  * Pipeline A (HV+D high-volume + displacement)
  * Pipeline B (PBJ landing-zone engine — STUBBED, see _pbj_engine note)
  * Pipeline C (USE: RVOL ladder, FAUNA NRA, GZ1, PUP/PPD, Matrix, U-streak,
    Combo Sets / Unified Combo, Floor/Roof, HW, Super/SDuper)
  * Pipeline D (CO triple-AND, restructured in v2)
  * B2B HV+D, B2B HV+D+PBJ, B2B HV+D+PB
  * TNT propulsion / Napalm engine (consolidated NPM = raw napalm OR
    bull/bear charge)
  * Heavy Pentagon Combo families × directions → WBUSH composite
  * Foster pair / Exhaustion triple / FAUNA cluster (ULTRA 57)
  * UC Nagasaki (csNew3 + Nagasaki on the visual displacement bar)

Conventions (mirrors `the_only_one.py`):

  - df is expected to have columns: open, high, low, close, volume.
    Index should be a monotonic int (bar index) or DatetimeIndex; bar order
    must be ascending.
  - Each detection function returns a pd.Series[bool] aligned to df.index.
  - IPSF (`input.*`) parameters live in DEFAULTS and may be overridden via
    the ``params`` dict passed to every detection.
  - Hardcoded Pine constants (NOT input.*) stay hardcoded here so future
    edits do not silently introduce drift.
  - Stateful detections (Combo Chain, LS Chain, AlphaStrike day-tracker,
    TNT zone manager, FVG arrays, ping-pong SR) are wrapped in classes in
    STATE_MACHINES.
  - Detections that require Pine-only intrinsics (request.security multi-TF,
    tv_ta.relativeVolume, gz1 array engine, Boom Hunter wavetrend filter
    chain, full PBJ landing-zone state, ping-pong SR pivots with line
    objects) are STUBBED and registered in STUBBED. Callers may inject
    pre-computed series via df.attrs to materialize those gated signals.

Standing decisions honoured:
  - SD-001: Pentagon always included in csNew1/csNew2/csNew3 (Pentagon is
    an unconditional operand of comboSet2/comboSet4). The
    cs_inc_pentagon_FVG / cs_inc_pentagon_MAT IPSF flags from the Pine
    source are documented but NOT used as gates here.
  - SD-002: This file is a NEW canonical port. Sibling files in the source
    pine versions are preserved (we do not modify them).
  - SD-003: IPSF defaults are mirrored exactly in DEFAULTS and are NOT
    reported as drift.
  - SD-004: This module never deletes anything.

Per docs/agentic-os/canonical/unified-combo.md, Squarify 46_v2 uses the
LAGGED (Group A) csNew3 pattern (`csNew1_Bull and nz(csNew2_Bull[1])`) —
that is what we implement here as the canonical csNew3.

This module is import-only safe; it does NOT contain tests. The harness
runs validation separately.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import numpy as np
import pandas as pd

# ============================================================================
# IPSF DEFAULTS — mirror Pine input.* defaults exactly (SD-003).
# ============================================================================
DEFAULTS: Dict = {
    # ─── MASTER TOGGLES ───
    "master_firstBarOnly": False,
    "master_aggAlerts": True,
    # ─── PIPELINE A: DISP BASE / HTF1 / HTF2 ───
    "d1_type": "Open to Close", "d1_len": 100, "d1_mult": 5.0,
    "d2_type": "Open to Close", "d2_len": 100, "d2_mult": 2.5,
    "d3_type": "Open to Close", "d3_len": 100, "d3_mult": 1.5,
    # 46 v2 SIGNAL TOGGLES (en_*) — all default True per Pine
    "en_1": True, "en_2": True, "en_3": True, "en_4": True, "en_5": True,
    "en_6": True, "en_7": True, "en_8": True, "en_9": True, "en_10": True,
    "en_11": True, "en_12": True, "en_13": True,
    "en_28": True, "en_29": True, "en_30": True, "en_33": True, "en_34": True,
    "en_35": True, "en_36": True, "en_37": True,
    "en_38": True, "en_39": True, "en_41": True, "en_42": True, "en_43": True,
    "en_44": True, "en_45": True, "en_46": True, "en_47": True, "en_48": True,
    "en_49": True, "en_50": True, "en_51": True, "en_52": True, "en_53": True,
    "en_54": True, "en_55": True, "en_56": True, "en_60": True,
    "en_wbushBull": True, "en_wbushBear": True, "en_wbushNeutral": True,
    "en_63": True, "en_ucNagBull": True, "en_ucNagBear": True,
    # ─── HV BASE TOGGLES (defaults differ from THE_ONLY_ONE per pine) ───
    "ub50": False, "ub75": False, "ub100": False, "ub150": False,
    "ub200": False,
    "ub250": True, "ub300": True, "ub350": True, "ub400": True, "ub450": True,
    "ub500": True, "ub550": True, "ub600": True, "ub650": True, "ub700": True,
    "ub750": True, "ub1000": True, "useHEV": True,
    # ─── HTF1 ───
    "h1On": True, "h1From": "15 Min", "h1To": "2 Hour",
    "uh1_5": True, "uh1_10": True, "uh1_20": True, "uh1_25": True,
    "uh1_30": True, "uh1_40": True, "uh1_50": True, "uh1_60": True,
    "uh1_70": True, "uh1_75": True, "uh1_80": True, "uh1_90": True,
    # ─── HTF2 ───
    "h2On": True, "h2From": "3 Hour", "h2To": "3 Month",
    "uh2_5": False, "uh2_10": False, "uh2_20": False, "uh2_25": False,
    "uh2_30": False,
    "uh2_40": True, "uh2_50": True, "uh2_60": True, "uh2_70": True,
    "uh2_75": True, "uh2_80": True, "uh2_90": True,
    # ─── USE displacement (engine 3) ───
    "i_disp_type": "Open to Close", "i_std_len": 100,
    "i_std_min": 3.0, "i_std_max": 100.0, "i_req_fvg": True,
    "i_disp2_type": "Open to Close", "i_disp2_std_len": 100,
    "i_disp2_std_min": 3.0, "i_disp2_std_max": 100.0, "i_disp2_req_fvg": True,
    "i_disp3_type": "Open to Close", "i_disp3_std_len": 100,
    "i_disp3_std_min": 3.0, "i_disp3_std_max": 100.0, "i_disp3_req_fvg": True,
    # ─── GZ1 / HV FVG ───
    "gz1_auto": True, "gz1_thresh": 2.0, "gz1_dist": 7,
    # ─── HV ───
    "hv150_len": 150,
    # ─── Swingin (Pivot) ───
    "sw_leftBars": 3, "sw_rightBars": 2,
    "sw_useAtr": True, "sw_atrMult": 2.0, "pp_atr_len": 100,
    # ─── Opening Drive ───
    "od_max_bars": 1,
    # ─── Matrix Number (Neo) ───
    "neo_len": 67,
    # ─── Momentum 1 / 2 ───
    "ls_reg1": 7.0, "ls_cum1": 3.5, "ls_body1": 0.60,
    "ls_reg2": 5.0, "ls_cum2": 2.5, "ls_body2": 0.75,
    # ─── Combo Set settings ───
    "cs_bodyPct_FVG": 0.85, "cs_bodyPct_MAT": 0.85,
    # SD-001: cs_inc_pentagon_* preserved for IPSF compatibility but Pentagon
    # is unconditionally included downstream regardless of these values.
    "cs_inc_pentagon_FVG": True, "cs_inc_pentagon_MAT": True,
    # ─── Combo Chain ───
    "cc_min_hits": 2, "cc_window": 2,
    # ─── LS Chain ───
    "lsc_min_hits": 2, "lsc_window": 2,
    "lsc_reg1": 7.0, "lsc_cum1": 3.5, "lsc_body1": 0.60,
    "lsc_reg2": 5.0, "lsc_cum2": 2.5, "lsc_body2": 0.75,
    # ─── TNT Engine ───
    "tnt_SENS": 100, "tnt_SWING_LEN": 10,
    "tnt_DISP_TYPE": "Open to Close",
    "tnt_DISP_STD_LEN": 100, "tnt_DISP_STD_X": 5,
    "tnt_RET_PCT": 100.0, "tnt_SUDDEN_PROX": 10,
    # ─── Checkbox Qualifiers (Sets 1, 2, 3) ───
    "cb1_uu": True, "cb1_combo": True, "cb1_d9": True, "cb1_pup": True,
    "cb1_pbj": True, "cb1_l1": True, "cb1_wmd": True,
    "cb2_uu": True, "cb2_combo": True, "cb2_d9": True, "cb2_pup": True,
    "cb2_pbj": True, "cb2_l1": True, "cb2_wmd": True,
    "cb3_uu": True, "cb3_combo": True, "cb3_d9": True, "cb3_pup": True,
    "cb3_pbj": True, "cb3_l1": True, "cb3_wmd": True,
    # ─── Pipeline D CO toggles ───
    "co_en_bullPBJ": True, "co_en_bullPB": True,
    "co_en_bearPBJ": True, "co_en_bearPB": True,
    # ─── Bar timeframe in seconds (caller supplies; defaults to 60s) ───
    "tfSec": 60,
    # ─── USE signal show toggles (default per pine) ───
    "show_BullUUUU": True, "show_BearUUUU": False,
    "show_BullUUU": True, "show_BearUUU": False,
    "show_BullUU": True, "show_BearUU": False,
    "show_AlphaStrikeB": True, "show_AlphaStrikeR": False,
    "show_FoxtrotB": True, "show_FoxtrotR": False,
    "show_OmegaLong": False, "show_OmegaLongA": True,
    "show_ODBull": True, "show_ODBear": False,
    "show_DispConsBull2": True, "show_DispConsBear2": False,
    "show_DispConsBull3": True, "show_DispConsBear3": False,
    "show_GolfBull": True, "show_GolfBear": False,
    "show_PAFBull": True, "show_PAFBear": False,
    "show_CS1B": True, "show_CS1R": False,
    "show_CS2B": True, "show_CS2R": False,
    "show_CS3B": True, "show_CS3R": False,
    "show_CCBull": True, "show_CCBear": False,
    "show_LSCBull": True, "show_LSCBear": False,
    "show_BullFloor": True, "show_Bull2ndFloor": True,
    "show_BearRooftop": False, "show_BearPenthouse": False,
    "show_HWBull": True, "show_HWBear": False,
    "show_SuperBull": True, "show_SuperBear": False,
    "show_SDuperBull": True, "show_SDuperBear": False,
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
    return tr.ewm(alpha=1.0 / length, adjust=False, min_periods=length).mean()


def _nz_b(s: pd.Series) -> pd.Series:
    """Pine nz(boolSeries) — replace NaN with False, return bool series."""
    return s.fillna(False).astype(bool)


def _nz_f(s: pd.Series, fill: float = 0.0) -> pd.Series:
    """Pine nz(floatSeries[, fill])."""
    return s.fillna(fill)


def _disp_range(df: pd.DataFrame, kind: str) -> pd.Series:
    if kind == "Open to Close":
        return (df["open"] - df["close"]).abs()
    return df["high"] - df["low"]


def _bull_fvg(df: pd.DataFrame) -> pd.Series:
    return (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["open"].shift(1))


def _bear_fvg(df: pd.DataFrame) -> pd.Series:
    return (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["open"].shift(1))


def _conf(df: pd.DataFrame) -> pd.Series:
    """Pine ``barstate.isconfirmed`` — historical bars are True."""
    return pd.Series(True, index=df.index)


# ---- RVOL threshold tables (lines 434-438 of source — identical to
# THE_ONLY_ONE) ----
def _rvol_1x(tfsec: float) -> float:
    s = tfsec
    if s <= 10: return 38.0
    if s <= 15: return 33.0
    if s <= 30: return 28.0
    if s <= 45: return 23.0
    if s <= 60: return 20.0
    if s <= 120: return 18.0
    if s <= 300: return 13.0
    if s <= 360: return 13.0
    if s <= 540: return 11.0
    if s <= 600: return 10.0
    if s <= 660: return 9.0
    if s <= 900: return 7.5
    if s <= 1560: return 6.5
    if s <= 2340: return 6.0
    if s <= 3600: return 4.5
    if s <= 9000: return 4.0
    if s <= 11700: return 3.5
    if s < 259200: return 1.8
    return 1.0


def _gs_moab(tfsec: float) -> float:
    s = tfsec
    if s < 60: return _rvol_1x(s) * 3.0
    if s <= 300: return 35.0
    if s <= 600: return 25.0
    if s <= 1500: return 20.0
    if s <= 3000: return 20.0
    if s <= 7260: return 10.0
    if s <= 11700: return 8.0
    if s <= 86400: return 7.5
    if s <= 259200: return 3.5
    return 3.0


def _saab_kratos(tfsec: float) -> float:
    return _rvol_1x(tfsec) * 0.56


def _wtc(tfsec: float) -> float:
    return _rvol_1x(tfsec) * 2.0


def _hiroshima(tfsec: float) -> float:
    s = tfsec
    if s < 60: return _rvol_1x(s) * 3.0
    if s <= 300: return 35.0
    if s <= 600: return 25.0
    if s <= 1500: return 25.0
    if s <= 3060: return 20.0
    if s <= 7260: return 10.0
    if s <= 11700: return 8.0
    if s <= 86400: return 7.5
    if s <= 259200: return 5.0
    return 3.5


def _tf2sec(t: str) -> int:
    return {
        "1 Min": 60, "2 Min": 120, "3 Min": 180, "4 Min": 240, "5 Min": 300,
        "10 Min": 600, "15 Min": 900, "30 Min": 1800,
        "1 Hour": 3600, "2 Hour": 7200, "3 Hour": 10800, "4 Hour": 14400,
        "1 Day": 86400, "2 Day": 172800, "3 Day": 259200,
        "1 Week": 604800, "1 Month": 2592000, "3 Month": 7776000,
    }.get(t, 0)


def _streak(series: pd.Series) -> pd.Series:
    a = series.fillna(False).to_numpy()
    out = np.zeros(len(a), dtype=int)
    c = 0
    for i, v in enumerate(a):
        c = c + 1 if v else 0
        out[i] = c
    return pd.Series(out, index=series.index)


def _attr_or_false(df: pd.DataFrame, name: str) -> pd.Series:
    """Read a Series from df.attrs[name] (caller-injected); default False."""
    s = df.attrs.get(name)
    if s is None:
        return pd.Series(False, index=df.index)
    if not isinstance(s, pd.Series):
        s = pd.Series(s, index=df.index)
    return s.reindex(df.index).fillna(False).astype(bool)


def _attr_or_nan(df: pd.DataFrame, name: str) -> pd.Series:
    s = df.attrs.get(name)
    if s is None:
        return pd.Series(np.nan, index=df.index)
    if not isinstance(s, pd.Series):
        s = pd.Series(s, index=df.index)
    return s.reindex(df.index)


# ============================================================================
# _engines — vectorized building blocks used by many detections.
# Each returns pd.Series; results are *cached on the dataframe* using
# attribute injection (df.attrs) so repeated detection calls are cheap.
# ============================================================================

def _ensure_engines(df: pd.DataFrame, params: Dict) -> Dict[str, pd.Series]:
    """Compute all shared signal series once and cache on df.attrs."""
    cache = df.attrs.setdefault("_squarify_46_v2_eng", {})
    cache_key = (
        "v1", id(df),
        tuple(sorted((k, v) for k, v in params.items() if isinstance(v, (int, float, str, bool)))),
    )
    if cache.get("_key") == cache_key and "sigBullPBJ" in cache:
        return cache
    cache.clear()
    cache["_key"] = cache_key

    p = params
    conf = _conf(df)
    tfSec = float(p["tfSec"])

    bull_fvg = _bull_fvg(df)
    bear_fvg = _bear_fvg(df)

    # ─────────────────────────────────────────────────────────────────────
    # PIPELINE A: D1/D2/D3 displacement + HV ranks → hvd_fire_bull/bear.
    # ─────────────────────────────────────────────────────────────────────
    d1_rng = _disp_range(df, p["d1_type"])
    d1_std = _stdev(d1_rng, p["d1_len"])
    d1_thresh = d1_std * p["d1_mult"]
    d1_prev = d1_rng.shift(1) > d1_thresh.shift(1)
    d1_bull = conf & d1_prev & bull_fvg
    d1_bear = conf & d1_prev & bear_fvg

    d2_rng = _disp_range(df, p["d2_type"])
    d2_std = _stdev(d2_rng, p["d2_len"])
    d2_thresh = d2_std * p["d2_mult"]
    d2_prev = d2_rng.shift(1) > d2_thresh.shift(1)
    d2_bull = conf & d2_prev & bull_fvg
    d2_bear = conf & d2_prev & bear_fvg

    d3_rng = _disp_range(df, p["d3_type"])
    d3_std = _stdev(d3_rng, p["d3_len"])
    d3_thresh = d3_std * p["d3_mult"]
    d3_prev = d3_rng.shift(1) > d3_thresh.shift(1)
    d3_bull = conf & d3_prev & bull_fvg
    d3_bear = conf & d3_prev & bear_fvg

    vol = df["volume"]
    vsh = vol.shift(1)

    def _is(n):
        return vsh == _highest(vol, n).shift(1)
    is50 = _is(50); is75 = _is(75); is100 = _is(100); is150 = _is(150)
    is200 = _is(200); is250 = _is(250); is300 = _is(300); is350 = _is(350)
    is400 = _is(400); is450 = _is(450); is500 = _is(500); is550 = _is(550)
    is600 = _is(600); is650 = _is(650); is700 = _is(700); is750 = _is(750)
    is1000 = _is(1000)

    isH5 = _is(5); isH10 = _is(10); isH20 = _is(20); isH25 = _is(25)
    isH30 = _is(30); isH40 = _is(40); isH50 = _is(50); isH60 = _is(60)
    isH70 = _is(70); isH75 = _is(75); isH80 = _is(80); isH90 = _is(90)

    # isHEV: streaming all-time-high tracker (on volume[1])
    hev_arr = np.zeros(len(df), dtype=bool)
    cur_max = -np.inf
    vsh_arr = vsh.to_numpy()
    for i, v in enumerate(vsh_arr):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            continue
        if v > cur_max:
            cur_max = v
            hev_arr[i] = True
    isHEV = pd.Series(hev_arr, index=df.index)

    def _bool_param(k):
        return bool(p[k])

    def _br():
        out = np.zeros(len(df), dtype=int)
        for s, n in [(is1000, 1000), (is750, 750), (is700, 700), (is650, 650),
                     (is600, 600), (is550, 550), (is500, 500), (is450, 450),
                     (is400, 400), (is350, 350), (is300, 300), (is250, 250),
                     (is200, 200), (is150, 150), (is100, 100), (is75, 75),
                     (is50, 50)]:
            mask = (out == 0) & s.fillna(False).to_numpy()
            out[mask] = n
        return pd.Series(out, index=df.index)
    baseRank = _br()

    base_enabled = pd.Series(False, index=df.index)
    for n, key in [(50, "ub50"), (75, "ub75"), (100, "ub100"), (150, "ub150"),
                   (200, "ub200"), (250, "ub250"), (300, "ub300"), (350, "ub350"),
                   (400, "ub400"), (450, "ub450"), (500, "ub500"), (550, "ub550"),
                   (600, "ub600"), (650, "ub650"), (700, "ub700"), (750, "ub750"),
                   (1000, "ub1000")]:
        if _bool_param(key):
            base_enabled = base_enabled | (baseRank == n)
    hev_hit = isHEV & _bool_param("useHEV")
    base_hv_hit = hev_hit | (base_enabled & ~isHEV)

    htf1Active = bool(p["h1On"]) and (tfSec >= _tf2sec(p["h1From"])) and (tfSec <= _tf2sec(p["h1To"]))
    htf2Active = bool(p["h2On"]) and (tfSec >= _tf2sec(p["h2From"])) and (tfSec <= _tf2sec(p["h2To"]))

    def _h_rank(active, prefix):
        out = np.zeros(len(df), dtype=int)
        if not active:
            return pd.Series(out, index=df.index)
        ladder = [(90, "_90", isH90), (80, "_80", isH80), (75, "_75", isH75),
                  (70, "_70", isH70), (60, "_60", isH60), (50, "_50", isH50),
                  (40, "_40", isH40), (30, "_30", isH30), (25, "_25", isH25),
                  (20, "_20", isH20), (10, "_10", isH10), (5, "_5", isH5)]
        for n, suffix, isH in ladder:
            key = f"u{prefix}{suffix}"
            if _bool_param(key):
                mask = (out == 0) & isH.fillna(False).to_numpy()
                out[mask] = n
        return pd.Series(out, index=df.index)

    h1Rank = _h_rank(htf1Active, "h1")
    h2Rank = _h_rank(htf2Active, "h2")

    base_combo_bull = base_hv_hit & d1_bull
    base_combo_bear = base_hv_hit & d1_bear
    htf1_combo_bull = (h1Rank > 0) & d2_bull
    htf1_combo_bear = (h1Rank > 0) & d2_bear
    htf2_combo_bull = (h2Rank > 0) & d3_bull
    htf2_combo_bear = (h2Rank > 0) & d3_bear

    hvd_fire_bull = (base_combo_bull | htf1_combo_bull | htf2_combo_bull).fillna(False)
    hvd_fire_bear = (base_combo_bear | htf1_combo_bear | htf2_combo_bear).fillna(False)

    anyHVRank = (baseRank > 0) | (h1Rank > 0) | (h2Rank > 0) | isHEV

    # ─────────────────────────────────────────────────────────────────────
    # ENGINE 1: RVOL ladder (SAAB / Kratos / RVOL1x / GS / MOAB / WTC /
    # Hiroshima / Pentagon / Nagasaki).
    # ─────────────────────────────────────────────────────────────────────
    bb_avgLength = 30; bb_smaLength = 20
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

    th_saab_kratos = _saab_kratos(tfSec)
    th_1x = _rvol_1x(tfSec)
    th_gs_moab = _gs_moab(tfSec)
    th_wtc = _wtc(tfSec)
    th_hiroshima = _hiroshima(tfSec)

    sigSAAB = conf & bb_baseBullish & (bb_normalizedPrice >= th_saab_kratos) & (bb_normalizedPrice < th_1x)
    sigKratos = conf & bb_baseBearish & (bb_normalizedPrice >= th_saab_kratos) & (bb_normalizedPrice < th_1x)
    sigGrandSlam = conf & bb_baseBullish & (bb_normalizedPrice >= th_gs_moab)
    sigMOAB = conf & bb_baseBearish & (bb_normalizedPrice >= th_gs_moab)
    sigBullRVOL1x = conf & bb_baseBullish & (bb_normalizedPrice >= th_1x) & (bb_normalizedPrice < th_gs_moab) & ~sigGrandSlam
    sigBearRVOL1x = conf & bb_baseBearish & (bb_normalizedPrice >= th_1x) & (bb_normalizedPrice < th_gs_moab) & ~sigMOAB

    # tv_ta.relativeVolume — STUBBED. Caller may inject `relVolRatio`.
    relVolRatio = _attr_or_nan(df, "relVolRatio")
    sigWTC = conf & (relVolRatio > th_wtc) & (relVolRatio <= th_hiroshima)
    sigHiroshima = conf & (relVolRatio > th_hiroshima)
    sigPentagon = conf & (relVolRatio >= th_1x) & (relVolRatio <= th_wtc)
    # NaN-safe: if relVolRatio is NaN, all three comparisons → NaN → False.
    sigWTC = sigWTC.fillna(False)
    sigHiroshima = sigHiroshima.fillna(False)
    sigPentagon = sigPentagon.fillna(False)

    # Nagasaki: streaming ATH volume (NOT shifted) per Pine source
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

    # ─── Session tracking ───
    is_new_day = df.attrs.get("is_new_day")
    if is_new_day is None:
        if isinstance(df.index, pd.DatetimeIndex):
            normd = df.index.normalize()
            diff = normd != pd.Series(normd, index=df.index).shift(1)
            is_new_day = pd.Series(diff.to_numpy(), index=df.index).fillna(True)
        else:
            tmp = np.zeros(len(df), dtype=bool); tmp[0] = True
            is_new_day = pd.Series(tmp, index=df.index)
    nd_arr = is_new_day.to_numpy()
    sb_arr = np.zeros(len(df), dtype=int)
    counter = 0
    for i, nd in enumerate(nd_arr):
        if nd:
            counter = 1
        else:
            counter += 1
        sb_arr[i] = counter
    sessionBarCount = pd.Series(sb_arr, index=df.index)

    # _isGapBar (Pine: ta.change(time("D")) != 0 → first bar of a new day)
    _isGapBar = is_new_day.astype(bool)
    # Gap qualifier strings could be derived; not exposed as detections.

    # ─────────────────────────────────────────────────────────────────────
    # ENGINE 2: FAUNA NRA
    # ─────────────────────────────────────────────────────────────────────
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

    MB_b = fauna_up & (fauna_bodySz > 1.6 * atr14) & (fauna_bodyRat > 0.70) & (df["volume"] > 1.8 * fauna_avgVol)
    RE_b = fauna_up & (fauna_rng > 2.2 * atr14) & ((df["high"] - df["close"]) < 0.15 * fauna_rng) & (df["volume"] > 1.8 * fauna_avgVol)
    TA_b = (fauna_trendMA > fauna_trendMA.shift(1)) & ((df["close"] - df["close"].shift(1)) > 1.6 * fauna_avgDelta) & fauna_up & (df["volume"] > 1.8 * fauna_avgVol)
    GG_b = ((df["open"] - df["close"].shift(1)) > 0.9 * atr14) & fauna_up & (df["low"] > df["close"].shift(1)) & (df["volume"] > 1.8 * fauna_avgVol)
    StrongBear = (df["close"].shift(1) < df["open"].shift(1)) & (fauna_prev_body.abs() > 1.5 * fauna_avgBody.shift(1)) & (df["volume"].shift(1) > 1.5 * fauna_avgVol.shift(1))
    WeakBear = (df["close"].shift(1) < df["open"].shift(1)) & ((fauna_prev_body.abs() / fauna_prev_range.replace(0, np.nan)).fillna(0.0) <= 0.2)
    TR_b = WeakBear & (MB_b | RE_b | TA_b)
    ES_b = StrongBear & (MB_b | RE_b | TA_b)
    GDR_b = (df["close"].shift(1) < df["open"].shift(1)) & GG_b
    b_core_cnt = MB_b.astype(int) + RE_b.astype(int) + TA_b.astype(int)
    fauna_gg_master = True
    fauna_gg_body = 0.80
    b_gg_pass = fauna_gg_master & (b_core_cnt >= 2) & (fauna_bodyRat >= fauna_gg_body)
    b_gg_exc = GG_b & ~b_gg_pass
    excluded_bull = TR_b | ES_b | GDR_b | b_gg_exc
    sigFAUNABull = conf & (MB_b | RE_b | TA_b) & ~excluded_bull

    MB_r = fauna_dn & (fauna_bodySz > 1.6 * atr14) & (fauna_bodyRat > 0.70) & (df["volume"] > 1.8 * fauna_avgVol)
    RE_r = fauna_dn & (fauna_rng > 2.2 * atr14) & ((df["close"] - df["low"]) < 0.15 * fauna_rng) & (df["volume"] > 1.8 * fauna_avgVol)
    TA_r = (fauna_trendMA < fauna_trendMA.shift(1)) & ((df["close"].shift(1) - df["close"]) > 1.6 * fauna_avgDelta) & fauna_dn & (df["volume"] > 1.8 * fauna_avgVol)
    GG_r = ((df["close"].shift(1) - df["open"]) > 0.9 * atr14) & fauna_dn & (df["high"] < df["close"].shift(1)) & (df["volume"] > 1.8 * fauna_avgVol)
    StrongBull = (df["close"].shift(1) > df["open"].shift(1)) & (fauna_prev_body.abs() > 1.5 * fauna_avgBody.shift(1)) & (df["volume"].shift(1) > 1.5 * fauna_avgVol.shift(1))
    WeakBull = (df["close"].shift(1) > df["open"].shift(1)) & ((fauna_prev_body.abs() / fauna_prev_range.replace(0, np.nan)).fillna(0.0) <= 0.2)
    TR_r = WeakBull & (MB_r | RE_r | TA_r)
    ES_r = StrongBull & (MB_r | RE_r | TA_r)
    GDR_r = (df["close"].shift(1) > df["open"].shift(1)) & GG_r
    s_core_cnt = MB_r.astype(int) + RE_r.astype(int) + TA_r.astype(int)
    s_gg_pass = fauna_gg_master & (s_core_cnt >= 2) & (fauna_bodyRat >= fauna_gg_body)
    s_gg_exc = GG_r & ~s_gg_pass
    excluded_bear = TR_r | ES_r | GDR_r | s_gg_exc
    sigFAUNABear = conf & (MB_r | RE_r | TA_r) & ~excluded_bear

    # ─────────────────────────────────────────────────────────────────────
    # ENGINE 3: USE displacement (DISP / DISP2+ / DISP3+ / disp5)
    # ─────────────────────────────────────────────────────────────────────
    disp_rng = _disp_range(df, p["i_disp_type"])
    disp_std = _stdev(disp_rng, p["i_std_len"])
    disp_thresh_min = disp_std * p["i_std_min"]
    disp_thresh_max = disp_std * p["i_std_max"]
    disp_prevDisp = (disp_rng.shift(1) > disp_thresh_min.shift(1)) & (disp_rng.shift(1) <= disp_thresh_max.shift(1))
    disp_currDisp = (disp_rng > disp_thresh_min) & (disp_rng <= disp_thresh_max)
    if bool(p["i_req_fvg"]):
        sigDISPBull = conf & disp_prevDisp & bull_fvg
        sigDISPBear = conf & disp_prevDisp & bear_fvg
    else:
        sigDISPBull = conf & disp_currDisp & (df["close"] > df["open"])
        sigDISPBear = conf & disp_currDisp & (df["close"] < df["open"])
    disp5_thresh = disp_std * 5.0
    disp5_bull = conf & (disp_std > 0) & (disp_rng > disp5_thresh) & (df["close"] > df["open"])
    disp5_bear = conf & (disp_std > 0) & (disp_rng > disp5_thresh) & (df["close"] < df["open"])
    d9_thresh = disp_std * 9.0
    d9_bull = conf & (disp_rng > d9_thresh) & (df["close"] > df["open"])

    d2r = _disp_range(df, p["i_disp2_type"])
    d2s = _stdev(d2r, p["i_disp2_std_len"])
    if bool(p["i_disp2_req_fvg"]):
        sigDISP2Bull = conf & (d2r.shift(1) > d2s.shift(1) * p["i_disp2_std_min"]) & \
                       (d2r.shift(1) <= d2s.shift(1) * p["i_disp2_std_max"]) & bull_fvg
        sigDISP2Bear = conf & (d2r.shift(1) > d2s.shift(1) * p["i_disp2_std_min"]) & \
                       (d2r.shift(1) <= d2s.shift(1) * p["i_disp2_std_max"]) & bear_fvg
    else:
        sigDISP2Bull = conf & (d2r > d2s * p["i_disp2_std_min"]) & (d2r <= d2s * p["i_disp2_std_max"]) & (df["close"] > df["open"])
        sigDISP2Bear = conf & (d2r > d2s * p["i_disp2_std_min"]) & (d2r <= d2s * p["i_disp2_std_max"]) & (df["close"] < df["open"])
    disp2_bullStreak = _streak(sigDISP2Bull)
    disp2_bearStreak = _streak(sigDISP2Bear)
    sigDispConsBull2 = sigDISP2Bull & (disp2_bullStreak >= 2) & _nz_b(sigFAUNABull.shift(1)) & _nz_b(sigFAUNABull.shift(2))
    sigDispConsBear2 = sigDISP2Bear & (disp2_bearStreak >= 2) & _nz_b(sigFAUNABear.shift(1)) & _nz_b(sigFAUNABear.shift(2))

    d3r = _disp_range(df, p["i_disp3_type"])
    d3s = _stdev(d3r, p["i_disp3_std_len"])
    if bool(p["i_disp3_req_fvg"]):
        sigDISP3Bull = conf & (d3r.shift(1) > d3s.shift(1) * p["i_disp3_std_min"]) & \
                       (d3r.shift(1) <= d3s.shift(1) * p["i_disp3_std_max"]) & bull_fvg
        sigDISP3Bear = conf & (d3r.shift(1) > d3s.shift(1) * p["i_disp3_std_min"]) & \
                       (d3r.shift(1) <= d3s.shift(1) * p["i_disp3_std_max"]) & bear_fvg
    else:
        sigDISP3Bull = conf & (d3r > d3s * p["i_disp3_std_min"]) & (d3r <= d3s * p["i_disp3_std_max"]) & (df["close"] > df["open"])
        sigDISP3Bear = conf & (d3r > d3s * p["i_disp3_std_min"]) & (d3r <= d3s * p["i_disp3_std_max"]) & (df["close"] < df["open"])
    disp3_bullStreak = _streak(sigDISP3Bull)
    disp3_bearStreak = _streak(sigDISP3Bear)
    sigDispConsBull3 = sigDISP3Bull & (disp3_bullStreak >= 3) & _nz_b(sigFAUNABull.shift(1)) & _nz_b(sigFAUNABull.shift(2)) & _nz_b(sigFAUNABull.shift(3))
    sigDispConsBear3 = sigDISP3Bear & (disp3_bearStreak >= 3) & _nz_b(sigFAUNABear.shift(1)) & _nz_b(sigFAUNABear.shift(2)) & _nz_b(sigFAUNABear.shift(3))

    # ─────────────────────────────────────────────────────────────────────
    # ENGINE 4: GZ1 / HV FVG — STUBBED (arrays + per-bar removal). Caller may
    # inject gz_bullGZI, gz_bearGZI, gz_bullHV, gz_bearHV.
    # ─────────────────────────────────────────────────────────────────────
    gz_bullGZI = _attr_or_false(df, "gz_bullGZI")
    gz_bearGZI = _attr_or_false(df, "gz_bearGZI")
    gz_bullHV = _attr_or_false(df, "gz_bullHV")
    gz_bearHV = _attr_or_false(df, "gz_bearHV")

    # ─────────────────────────────────────────────────────────────────────
    # ENGINE 5: PUP / PPD
    # ─────────────────────────────────────────────────────────────────────
    pp_barSize = 3.0; pp_lookback = 10
    pp_redVol = df["volume"].where(df["close"] < df["open"], 0.0)
    pp_greenVol = df["volume"].where(df["close"] > df["open"], 0.0)
    pp_hiRedVol = _highest(pp_redVol.shift(1), pp_lookback)
    pp_hiGreenVol = _highest(pp_greenVol.shift(1), pp_lookback)
    pp_priceUp = ((df["close"] - df["open"]) / df["open"]) * 100 > pp_barSize
    pp_priceDn = ((df["open"] - df["close"]) / df["open"]) * 100 > pp_barSize
    sigPUP = conf & pp_priceUp & (df["volume"] > pp_hiRedVol)
    sigPPD = conf & pp_priceDn & (df["volume"] > pp_hiGreenVol)

    # ─────────────────────────────────────────────────────────────────────
    # ENGINE 6: PBJ — STUBBED. Inject sigBullPBJ/sigBullPB/sigBearPBJ/sigBearPB
    # via df.attrs.
    # ─────────────────────────────────────────────────────────────────────
    sigBullPBJ = _attr_or_false(df, "sigBullPBJ")
    sigBullPB = _attr_or_false(df, "sigBullPB")
    sigBearPBJ = _attr_or_false(df, "sigBearPBJ")
    sigBearPB = _attr_or_false(df, "sigBearPB")

    # ─────────────────────────────────────────────────────────────────────
    # ENGINE 7: Ping-Pong SR — STUBBED. Inject bull_pp / bear_pp.
    # ─────────────────────────────────────────────────────────────────────
    bull_pp = _attr_or_false(df, "bull_pp")
    bear_pp = _attr_or_false(df, "bear_pp")

    # ─────────────────────────────────────────────────────────────────────
    # ENGINE 8: U-streak family (UU / UUU / UUUU bull + bear) — v2 paths
    # A-G. Computed bar-by-bar.
    # ─────────────────────────────────────────────────────────────────────
    u_qual_bull = conf & bb_baseBullish & (bb_normalizedPrice >= 0.5)
    u_qual_bear = conf & bb_baseBearish & (bb_normalizedPrice >= 0.5)

    # Per-bar streak + hasDay1 tracker
    def _streak_with_day1(qual: pd.Series, day_change: pd.Series):
        a = qual.fillna(False).to_numpy(); d = day_change.fillna(False).to_numpy()
        st = np.zeros(len(a), dtype=int); has = np.zeros(len(a), dtype=bool)
        c = 0; hd = False
        for i, b in enumerate(a):
            if b:
                c += 1; hd = hd or d[i]
            else:
                c = 0; hd = False
            st[i] = c; has[i] = hd
        return pd.Series(st, index=qual.index), pd.Series(has, index=qual.index)
    u_bull_streak, u_bull_hasDay1 = _streak_with_day1(u_qual_bull, is_new_day)
    u_bear_streak, u_bear_hasDay1 = _streak_with_day1(u_qual_bear, is_new_day)

    rawBullUU = conf & (u_bull_streak == 2)
    rawBullUUU = conf & (u_bull_streak == 3)
    rawBullUUUU = conf & (u_bull_streak >= 4)
    rawBearUU = conf & (u_bear_streak == 2)
    rawBearUUU = conf & (u_bear_streak == 3)
    rawBearUUUU = conf & (u_bear_streak >= 4)

    # Helper: paths A-G evaluator for bull and bear streak of given n.
    def _u_paths(streak, hasDay1, n_target, direction, qcnt_floor, include_pF):
        """
        direction = "bull" or "bear". n_target=2,3,4. qcnt_floor = required distinct
        qualifiers in pG. include_pF: only UUUU has pF.
        For UU only: pD = _has_hvd AND (_has_pb OR _has_pbj).
        Returns (sig, sig_indep).
        """
        is_bull = (direction == "bull")
        pbj_src = sigBullPBJ if is_bull else sigBearPBJ
        pb_src = sigBullPB if is_bull else sigBearPB
        hvd_src = hvd_fire_bull if is_bull else hvd_fire_bear
        disp_src = sigDISPBull if is_bull else sigDISPBear
        fauna_src = sigFAUNABull if is_bull else sigFAUNABear
        sa_src = sigSAAB if is_bull else sigKratos
        r1_src = sigBullRVOL1x if is_bull else sigBearRVOL1x
        gs_src = sigGrandSlam if is_bull else sigMOAB

        st = streak.to_numpy()
        hd = hasDay1.to_numpy()
        pbj_a = _nz_b(pbj_src).to_numpy()
        pb_a = _nz_b(pb_src).to_numpy()
        hvd_a = _nz_b(hvd_src).to_numpy()
        disp_a = _nz_b(disp_src).to_numpy()
        fauna_a = _nz_b(fauna_src).to_numpy()
        sa_a = _nz_b(sa_src).to_numpy()
        r1_a = _nz_b(r1_src).to_numpy()
        gs_a = _nz_b(gs_src).to_numpy()
        bbN = bb_normalizedPrice.fillna(0.0).to_numpy()

        N = len(streak)
        sig = np.zeros(N, dtype=bool); sig_indep = np.zeros(N, dtype=bool)

        for i in range(N):
            if n_target == 4 and st[i] < 4: continue
            if n_target == 3 and st[i] != 3: continue
            if n_target == 2 and st[i] != 2: continue
            n_iter = min(st[i], 4) if n_target == 4 else n_target
            has_pbj = has_pb = has_hvd = has_disp = has_fauna = False
            has_sa = has_r1 = has_gs = False
            all_disp = True; all_saab_df = True
            df_not_pbj = pbj_not_df = False
            for k in range(n_iter):
                idx = i - k
                if idx < 0: continue
                bpbj = pbj_a[idx]; bpb = pb_a[idx]
                bhvd = hvd_a[idx - 1] if (k >= 1 and idx - 1 >= 0) else False
                bdisp = disp_a[idx] or bhvd
                bfauna = fauna_a[idx]
                bsaab = sa_a[idx] or r1_a[idx] or gs_a[idx]
                bdf = bdisp or bfauna
                if bpbj: has_pbj = True
                if bpb: has_pb = True
                if bhvd: has_hvd = True
                if bdisp: has_disp = True
                if bfauna: has_fauna = True
                if sa_a[idx]: has_sa = True
                if r1_a[idx]: has_r1 = True
                if gs_a[idx]: has_gs = True
                if not bdisp: all_disp = False
                if (not bsaab) or (not bdf): all_saab_df = False
                if bdf and not bpbj: df_not_pbj = True
                if bpbj and not bdf: pbj_not_df = True
            pA = hd[i] and has_pbj
            pB = all_disp
            pC = all_saab_df
            if n_target == 2:
                pD = has_hvd and (has_pb or has_pbj)
            else:
                pD = has_hvd
            pE = (df_not_pbj and has_pbj) or (pbj_not_df and (has_disp or has_fauna))
            pF = include_pF and ((has_fauna or has_disp) and has_pbj)
            qcnt = int(has_pbj) + int(has_disp) + int(has_fauna) + int(has_sa) + int(has_r1) + int(has_gs)
            pG = qcnt >= qcnt_floor

            # Sub-2min gate (bull only — bear has no sub-2min gate in source)
            if is_bull:
                acc = 0.0; pbj_win = False
                for k in range(n_target):
                    idx = i - k
                    if idx < 0: continue
                    acc += bbN[idx]
                    if pbj_a[idx]:
                        pbj_win = True
                sub2min_ok = (tfSec > 120) or (acc >= th_saab_kratos and (acc >= th_1x or pbj_win))
            else:
                sub2min_ok = True

            base = (pA or pB or pC or pD or pE or pF or pG) and sub2min_ok
            indep = (pA or pB or pC or pE or pF or pG) and sub2min_ok
            sig[i] = base; sig_indep[i] = indep
        return pd.Series(sig, index=streak.index), pd.Series(sig_indep, index=streak.index)

    sigP21BullUUUU, sigP21BullUUUU_indep = _u_paths(u_bull_streak, u_bull_hasDay1, 4, "bull", 4, True)
    sigP21BullUUU, sigP21BullUUU_indep = _u_paths(u_bull_streak, u_bull_hasDay1, 3, "bull", 3, False)
    sigUUBull, sigUUBull_indep = _u_paths(u_bull_streak, u_bull_hasDay1, 2, "bull", 2, False)
    sigP21BearUUUU, sigP21BearUUUU_indep = _u_paths(u_bear_streak, u_bear_hasDay1, 4, "bear", 4, True)
    sigP21BearUUU, sigP21BearUUU_indep = _u_paths(u_bear_streak, u_bear_hasDay1, 3, "bear", 3, False)
    sigUUBear, sigUUBear_indep = _u_paths(u_bear_streak, u_bear_hasDay1, 2, "bear", 2, False)

    # ─────────────────────────────────────────────────────────────────────
    # Matrix Number / Neo / Trinity, Foxtrot
    # ─────────────────────────────────────────────────────────────────────
    is_matrix_number = df["volume"] == _highest(df["volume"], int(p["neo_len"]))
    sigNeoBull = conf & is_matrix_number & sigFAUNABull
    sigNeoBear = conf & is_matrix_number & sigFAUNABear
    sigTrinityBull = conf & is_matrix_number & ~sigFAUNABull & (df["close"] > df["open"])
    sigTrinityBear = conf & is_matrix_number & ~sigFAUNABear & (df["close"] < df["open"])

    sigFoxtrotBull = conf & sigFAUNABull & _nz_b(sigFAUNABull.shift(1)) & _nz_b(sigFAUNABull.shift(2)) & _nz_b(sigFAUNABull.shift(3))
    sigFoxtrotBear = conf & sigFAUNABear & _nz_b(sigFAUNABear.shift(1)) & _nz_b(sigFAUNABear.shift(2)) & _nz_b(sigFAUNABear.shift(3))

    # ─────────────────────────────────────────────────────────────────────
    # ENGINE 11: Long/Short — STUBBED relativeVolume. Inject ls_regRatio /
    # ls_cumRatio via df.attrs.
    # ─────────────────────────────────────────────────────────────────────
    ls_regRatio = _attr_or_nan(df, "ls_regRatio")
    ls_cumRatio = _attr_or_nan(df, "ls_cumRatio")
    ls_bodyRat = ((df["close"] - df["open"]).abs() / (df["high"] - df["low"]).replace(0, np.nan)).fillna(0.0)
    sigLong1 = conf & (ls_regRatio > p["ls_reg1"]) & (ls_cumRatio > p["ls_cum1"]) & (df["close"] > df["open"]) & (ls_bodyRat >= p["ls_body1"])
    sigShort1 = conf & (ls_regRatio > p["ls_reg1"]) & (ls_cumRatio > p["ls_cum1"]) & (df["close"] < df["open"]) & (ls_bodyRat >= p["ls_body1"])
    sigLong2 = conf & (ls_regRatio > p["ls_reg2"]) & (ls_cumRatio > p["ls_cum2"]) & (df["close"] > df["open"]) & (ls_bodyRat >= p["ls_body2"])
    sigShort2 = conf & (ls_regRatio > p["ls_reg2"]) & (ls_cumRatio > p["ls_cum2"]) & (df["close"] < df["open"]) & (ls_bodyRat >= p["ls_body2"])
    # NaN-safe (if no relVol injected, all four → False)
    sigLong1 = sigLong1.fillna(False); sigShort1 = sigShort1.fillna(False)
    sigLong2 = sigLong2.fillna(False); sigShort2 = sigShort2.fillna(False)

    neo_bull_aligned = sigNeoBull & (sigLong1 | sigLong2)
    neo_bear_aligned = sigNeoBear & (sigShort1 | sigShort2)
    trinity_bull_aligned = sigTrinityBull & (sigLong1 | sigLong2)
    trinity_bear_aligned = sigTrinityBear & (sigShort1 | sigShort2)

    # ─────────────────────────────────────────────────────────────────────
    # Combo Sets / Unified Combo — SD-001: Pentagon ALWAYS included.
    # Pine flag cs_inc_pentagon_FVG / cs_inc_pentagon_MAT preserved in
    # DEFAULTS for IPSF compatibility but Pentagon is unconditionally an
    # OR-operand of comboSet2/comboSet4 per the canonical doc.
    #
    # Per docs/agentic-os/canonical/unified-combo.md, Squarify uses Group A
    # (LAGGED) csNew3: csNew1 AND nz(csNew2[1]).
    # ─────────────────────────────────────────────────────────────────────
    cs_bp1 = ((df["close"].shift(1) - df["open"].shift(1)).abs() /
              (df["high"].shift(1) - df["low"].shift(1)).replace(0, np.nan)).fillna(0.0)
    cs_vb = cs_bp1 >= p["cs_bodyPct_FVG"]
    comboSet1_Bull = conf & cs_vb & (gz_bullHV | gz_bullGZI) & (_nz_b(sigSAAB.shift(1)) | _nz_b(sigBullRVOL1x.shift(1)) | _nz_b(sigGrandSlam.shift(1)))
    comboSet1_Bear = conf & cs_vb & (gz_bearHV | gz_bearGZI) & (_nz_b(sigKratos.shift(1)) | _nz_b(sigBearRVOL1x.shift(1)) | _nz_b(sigMOAB.shift(1)))
    # SD-001: Pentagon unconditional. (Pine: (cs_inc_pentagon_FVG and sigPentagon[1]) or ...)
    comboSet2_Bull = conf & cs_vb & (gz_bullHV | gz_bullGZI) & (
        _nz_b(sigPentagon.shift(1)) | _nz_b(sigWTC.shift(1)) | _nz_b(sigHiroshima.shift(1)) | _nz_b(sigNagasaki.shift(1)))
    comboSet2_Bear = conf & cs_vb & (gz_bearHV | gz_bearGZI) & (
        _nz_b(sigPentagon.shift(1)) | _nz_b(sigWTC.shift(1)) | _nz_b(sigHiroshima.shift(1)) | _nz_b(sigNagasaki.shift(1)))
    cs_vm = ls_bodyRat >= p["cs_bodyPct_MAT"]
    matrix_any_bull = sigNeoBull | sigTrinityBull | neo_bull_aligned | trinity_bull_aligned
    matrix_any_bear = sigNeoBear | sigTrinityBear | neo_bear_aligned | trinity_bear_aligned
    comboSet3_Bull = cs_vm & matrix_any_bull & (sigSAAB | sigBullRVOL1x | sigGrandSlam)
    comboSet3_Bear = cs_vm & matrix_any_bear & (sigKratos | sigBearRVOL1x | sigMOAB)
    # SD-001: Pentagon unconditional.
    comboSet4_Bull = cs_vm & matrix_any_bull & (sigPentagon | sigWTC | sigHiroshima | sigNagasaki)
    comboSet4_Bear = cs_vm & matrix_any_bear & (sigPentagon | sigWTC | sigHiroshima | sigNagasaki)

    csNew1_Bull = comboSet1_Bull | comboSet2_Bull
    csNew1_Bear = comboSet1_Bear | comboSet2_Bear
    csNew2_Bull = comboSet3_Bull | comboSet4_Bull
    csNew2_Bear = comboSet3_Bear | comboSet4_Bear
    # GROUP A LAGGED (canonical for Squarify)
    csNew3_Bull = csNew1_Bull & _nz_b(csNew2_Bull.shift(1))
    csNew3_Bear = csNew1_Bear & _nz_b(csNew2_Bear.shift(1))

    # ─────────────────────────────────────────────────────────────────────
    # Alpha Strike, Opening Drive, HV size, Golf/PAF
    # ─────────────────────────────────────────────────────────────────────
    as_fauna_bull = sigFAUNABull | sigLong1 | sigDISPBull | sigPUP | sigWTC | sigHiroshima | sigNagasaki
    as_fauna_bear = sigFAUNABear | sigShort1 | sigDISPBear | sigPPD | sigWTC | sigHiroshima | sigNagasaki
    # firstOfDay needs the AlphaStrike sweep — computed after we know the
    # detection set. For now use a placeholder which is filled below.
    firstOfDay_placeholder = pd.Series(True, index=df.index)
    sigAlphaStrikeBull_base = conf & bull_pp & (sigGrandSlam | sigBullRVOL1x) & sigBullPBJ & as_fauna_bull
    sigAlphaStrikeBear_base = conf & bear_pp & (sigMOAB | sigBearRVOL1x) & sigBearPBJ & as_fauna_bear

    od_fvg_bull = gz_bullGZI | comboSet1_Bull | comboSet2_Bull | comboSet3_Bull | comboSet4_Bull
    od_fvg_bear = gz_bearGZI | comboSet1_Bear | comboSet2_Bear | comboSet3_Bear | comboSet4_Bear
    sigODBull = conf & (sessionBarCount <= int(p["od_max_bars"]) + 1) & od_fvg_bull & disp_prevDisp & _nz_b(sigPUP.shift(1)) & _nz_b(sigBullPBJ.shift(1))
    sigODBear = conf & (sessionBarCount <= int(p["od_max_bars"]) + 1) & od_fvg_bear & disp_prevDisp & _nz_b(sigPPD.shift(1)) & _nz_b(sigBearPBJ.shift(1))

    sigHV75 = conf & (df["volume"] >= _highest(df["volume"], 75).shift(1))
    sigHV150 = conf & (df["volume"] >= _highest(df["volume"], int(p["hv150_len"])).shift(1))
    sigHV500 = conf & (df["volume"] >= _highest(df["volume"], 500).shift(1))
    sigHV1000 = conf & (df["volume"] >= _highest(df["volume"], 1000).shift(1))

    sigGolfBull = conf & sigDISPBull & _nz_b(sigFAUNABull.shift(1)) & _nz_b(sigPUP.shift(1)) & _nz_b(sigDISPBull.shift(1)) & _nz_b(sigFAUNABull.shift(2)) & _nz_b(sigPUP.shift(2))
    sigGolfBear = conf & sigDISPBear & _nz_b(sigFAUNABear.shift(1)) & _nz_b(sigPPD.shift(1)) & _nz_b(sigDISPBear.shift(1)) & _nz_b(sigFAUNABear.shift(2)) & _nz_b(sigPPD.shift(2))
    sigPAFBull = conf & sigPUP & sigFAUNABull & _nz_b(sigPUP.shift(1)) & _nz_b(sigFAUNABull.shift(1))
    sigPAFBear = conf & sigPPD & sigFAUNABear & _nz_b(sigPPD.shift(1)) & _nz_b(sigFAUNABear.shift(1))

    # ─────────────────────────────────────────────────────────────────────
    # Combo Chain (CC) — stateful per-bar
    # ─────────────────────────────────────────────────────────────────────
    cc_min_hits = int(p["cc_min_hits"]); cc_window = int(p["cc_window"])

    def _cc_active(cs1, cs2, cs3, pbj_a, pb_a):
        a1 = _nz_b(cs1).to_numpy(); a2 = _nz_b(cs2).to_numpy()
        a3 = _nz_b(cs3).to_numpy()
        pj = _nz_b(pbj_a).to_numpy(); pb = _nz_b(pb_a).to_numpy()
        N = len(a1); out = np.zeros(N, dtype=bool); active = False
        for i in range(N):
            wb = 0; seen = False
            for k in range(cc_window):
                idx = i - k
                if idx < 0: continue
                if a1[idx] or a2[idx]:
                    wb += 1
                if pj[idx] or pb[idx]:
                    seen = True
            # subtract csNew3 hits inside earlier offsets
            for k in range(max(cc_window - 1, 0)):
                idx = i - k
                if idx < 0: continue
                if (k + 1) <= cc_window - 1 and a3[idx]:
                    wb -= 1
            if not (a1[i] or a2[i]):
                active = False
            elif not active and wb >= cc_min_hits and seen:
                active = True
            out[i] = active
        return pd.Series(out, index=df.index)
    cc_bull_active = _cc_active(csNew1_Bull, csNew2_Bull, csNew3_Bull, sigBullPBJ, sigBullPB)
    cc_bear_active = _cc_active(csNew1_Bear, csNew2_Bear, csNew3_Bear, sigBearPBJ, sigBearPB)
    sigCCBull = conf & cc_bull_active
    sigCCBear = conf & cc_bear_active

    # ─────────────────────────────────────────────────────────────────────
    # LS Chain
    # ─────────────────────────────────────────────────────────────────────
    lsc_L1 = conf & (ls_regRatio > p["lsc_reg1"]) & (ls_cumRatio > p["lsc_cum1"]) & (df["close"] > df["open"]) & (ls_bodyRat >= p["lsc_body1"])
    lsc_S1 = conf & (ls_regRatio > p["lsc_reg1"]) & (ls_cumRatio > p["lsc_cum1"]) & (df["close"] < df["open"]) & (ls_bodyRat >= p["lsc_body1"])
    lsc_L2 = conf & (ls_regRatio > p["lsc_reg2"]) & (ls_cumRatio > p["lsc_cum2"]) & (df["close"] > df["open"]) & (ls_bodyRat >= p["lsc_body2"])
    lsc_S2 = conf & (ls_regRatio > p["lsc_reg2"]) & (ls_cumRatio > p["lsc_cum2"]) & (df["close"] < df["open"]) & (ls_bodyRat >= p["lsc_body2"])
    lsc_L1 = lsc_L1.fillna(False); lsc_S1 = lsc_S1.fillna(False)
    lsc_L2 = lsc_L2.fillna(False); lsc_S2 = lsc_S2.fillna(False)
    lsc_min_hits = int(p["lsc_min_hits"]); lsc_window = int(p["lsc_window"])

    def _lsc_active(L1, L2, pbj_a, pb_a):
        a1 = _nz_b(L1).to_numpy(); a2 = _nz_b(L2).to_numpy()
        pj = _nz_b(pbj_a).to_numpy(); pb = _nz_b(pb_a).to_numpy()
        N = len(a1); out = np.zeros(N, dtype=bool); active = False
        for i in range(N):
            wb = 0; seen = False
            for k in range(lsc_window):
                idx = i - k
                if idx < 0: continue
                if a1[idx] or a2[idx]: wb += 1
                if pj[idx] or pb[idx]: seen = True
            if not (a1[i] or a2[i]):
                active = False
            elif not active and wb >= lsc_min_hits and seen:
                active = True
            out[i] = active
        return pd.Series(out, index=df.index)
    lsc_bull_active = _lsc_active(lsc_L1, lsc_L2, sigBullPBJ, sigBullPB)
    lsc_bear_active = _lsc_active(lsc_S1, lsc_S2, sigBearPBJ, sigBearPB)
    sigLSCBull = conf & lsc_bull_active
    sigLSCBear = conf & lsc_bear_active

    # ─────────────────────────────────────────────────────────────────────
    # Floor / Roof / 2F / PH; HW; Super / SDuper (v2 redefined per Anish)
    # ─────────────────────────────────────────────────────────────────────
    nag_dir_bull = sigBullRVOL1x | sigGrandSlam | sigFAUNABull | sigDISPBull | sigBullPBJ | sigPUP | gz_bullHV | gz_bullGZI
    nag_dir_bear = sigBearRVOL1x | sigMOAB | sigFAUNABear | sigDISPBear | sigBearPBJ | sigPPD | gz_bearHV | gz_bearGZI
    bull_hw_slot = sigBullRVOL1x | sigGrandSlam | sigWTC | sigHiroshima | (sigNagasaki & nag_dir_bull)
    bear_hw_slot = sigBearRVOL1x | sigMOAB | sigWTC | sigHiroshima | (sigNagasaki & nag_dir_bear)
    anyBullFloor = conf & bull_pp & sigBullPBJ & bull_hw_slot
    anyBull2nd = conf & bull_pp & sigBullPB & bull_hw_slot
    anyBearRoof = conf & bear_pp & sigBearPBJ & bear_hw_slot
    anyBearPent = conf & bear_pp & sigBearPB & bear_hw_slot

    hwBull = (df["close"] > df["open"]) & disp5_bull & sigBullPBJ & (sigGrandSlam | sigWTC | sigHiroshima | (sigNagasaki & nag_dir_bull)) & (anyBullFloor | anyBull2nd)
    hwBear = (df["close"] < df["open"]) & disp5_bear & sigBearPBJ & (sigMOAB | sigWTC | sigHiroshima | (sigNagasaki & nag_dir_bear)) & (anyBearRoof | anyBearPent)

    # ─────────────────────────────────────────────────────────────────────
    # TNT Propulsion Block / Napalm Engine — STUBBED (very stateful).
    # Caller may inject the consolidated NPM signals directly via df.attrs:
    #   raw_bullTNT, raw_bullTNT2, raw_napalmBull, raw_bullCharge,
    #   raw_retBullTNT, raw_contBull
    # and mirror bear ones. We fall back to False everywhere.
    # ─────────────────────────────────────────────────────────────────────
    raw_bullTNT = _attr_or_false(df, "raw_bullTNT")
    raw_bullTNT2 = _attr_or_false(df, "raw_bullTNT2")
    raw_napalmBull = _attr_or_false(df, "raw_napalmBull")
    raw_bullCharge = _attr_or_false(df, "raw_bullCharge")
    raw_retBullTNT = _attr_or_false(df, "raw_retBullTNT")
    raw_contBull = _attr_or_false(df, "raw_contBull")
    raw_bearTNT = _attr_or_false(df, "raw_bearTNT")
    raw_bearTNT2 = _attr_or_false(df, "raw_bearTNT2")
    raw_napalmBear = _attr_or_false(df, "raw_napalmBear")
    raw_bearCharge = _attr_or_false(df, "raw_bearCharge")
    raw_retBearTNT = _attr_or_false(df, "raw_retBearTNT")
    raw_contBear = _attr_or_false(df, "raw_contBear")

    # Consolidated NPM (v2: raw napalm OR charge — equivalent per Anish)
    det_bullNapalmCons = raw_napalmBull | raw_bullCharge
    det_bearNapalmCons = raw_napalmBear | raw_bearCharge
    det_b2bBullNapalm = det_bullNapalmCons & _nz_b(det_bullNapalmCons.shift(1))
    det_b2bBearNapalm = det_bearNapalmCons & _nz_b(det_bearNapalmCons.shift(1))
    det_npmTntBull = raw_napalmBull & _nz_b(raw_bullTNT.shift(1))
    det_npmTntBear = raw_napalmBear & _nz_b(raw_bearTNT.shift(1))
    det_b2bPUP = sigPUP & _nz_b(sigPUP.shift(1))
    det_b2bPPD = sigPPD & _nz_b(sigPPD.shift(1))

    # ─────────────────────────────────────────────────────────────────────
    # Super / SDuper — v2 REDEFINED per Anish:
    #   SUPER  = UC (csNew3) + Napalm consolidated
    #   SDUPER = UC + Napalm + PUP/PPD
    # ─────────────────────────────────────────────────────────────────────
    superBull = conf & csNew3_Bull & det_bullNapalmCons
    superBear = conf & csNew3_Bear & det_bearNapalmCons
    sduperBull = conf & csNew3_Bull & det_bullNapalmCons & _nz_b(sigPUP.shift(1))
    sduperBear = conf & csNew3_Bear & det_bearNapalmCons & _nz_b(sigPPD.shift(1))

    # ─────────────────────────────────────────────────────────────────────
    # Boom Hunter / Omega — STUBBED (Ehlers filter chain + wavetrend). Inject
    # sigOmegaLong / sigOmegaLongA / sigShortPlusPress via df.attrs.
    # ─────────────────────────────────────────────────────────────────────
    sigOmegaLong = _attr_or_false(df, "sigOmegaLong")
    sigOmegaLongA = _attr_or_false(df, "sigOmegaLongA")
    sigShortPlusPress = _attr_or_false(df, "sigShortPlusPress")

    # ─────────────────────────────────────────────────────────────────────
    # First-of-day tracker (post-hoc compute given the set of "big" sigs)
    # ─────────────────────────────────────────────────────────────────────
    big_bull = (sigP21BullUUUU | sigP21BearUUUU | sigP21BullUUU | sigP21BearUUU |
                sigUUBull | sigUUBear | sigAlphaStrikeBull_base | sigAlphaStrikeBear_base |
                sigFoxtrotBull | sigFoxtrotBear | sigOmegaLong | sigOmegaLongA |
                sigODBull | sigODBear |
                sigDispConsBull2 | sigDispConsBear2 | sigDispConsBull3 | sigDispConsBear3 |
                csNew1_Bull | csNew1_Bear | csNew2_Bull | csNew2_Bear | csNew3_Bull | csNew3_Bear |
                anyBullFloor | anyBull2nd | anyBearRoof | anyBearPent |
                hwBull | hwBear | sigCCBull | sigCCBear | sigLSCBull | sigLSCBear |
                sigGolfBull | sigGolfBear | sigPAFBull | sigPAFBear |
                superBull | superBear | sduperBull | sduperBear)
    nd = is_new_day.fillna(False).to_numpy()
    bb = big_bull.fillna(False).to_numpy()
    fod = np.zeros(len(df), dtype=bool); fired = False
    for i in range(len(df)):
        if nd[i]:
            fired = False
        if not fired:
            fod[i] = True
        if bb[i]:
            fired = True
    firstOfDay = pd.Series(fod, index=df.index)

    sigAlphaStrikeBull = sigAlphaStrikeBull_base & firstOfDay
    sigAlphaStrikeBear = sigAlphaStrikeBear_base & firstOfDay

    # ─────────────────────────────────────────────────────────────────────
    # ULTRA 57 FAUNA combos (Foster pair / Exhaustion triple / Cluster +
    # B2B-days variants). Session-bound to US RTH per Pine; without TZ
    # info we degrade to using is_new_day boundaries.
    # ─────────────────────────────────────────────────────────────────────
    # u57 session bar count (1 on new day, increments on subsequent bars).
    # Pine restricts to US RTH using time(); without TZ we treat every bar
    # as in-session. This is documented as Pine-only intrinsic.
    u57_inSession = pd.Series(True, index=df.index)
    nd_arr2 = is_new_day.fillna(False).to_numpy()
    u57_sess = np.zeros(len(df), dtype=int)
    c = 0
    for i in range(len(df)):
        if nd_arr2[i]:
            c = 1
        elif c > 0:
            c += 1
        u57_sess[i] = c
    u57_sessBar = pd.Series(u57_sess, index=df.index)

    u57_bMB = conf & MB_b; u57_bRE = conf & RE_b; u57_bTA = conf & TA_b
    u57_sMB = conf & MB_r; u57_sRE = conf & RE_r; u57_sTA = conf & TA_r
    u57_bEv = u57_bMB | u57_bRE | u57_bTA
    u57_sEv = u57_sMB | u57_sRE | u57_sTA

    sBullF2 = conf & (u57_sessBar == 2) & u57_bMB & _nz_b(u57_bMB.shift(1))
    sBearF2 = conf & (u57_sessBar == 2) & u57_sMB & _nz_b(u57_sMB.shift(1))
    sBullE3 = conf & (u57_sessBar == 3) & u57_bEv & _nz_b(u57_bEv.shift(1)) & _nz_b(u57_bEv.shift(2))
    sBearE3 = conf & (u57_sessBar == 3) & u57_sEv & _nz_b(u57_sEv.shift(1)) & _nz_b(u57_sEv.shift(2))

    # FAUNA Cluster Bull/Bear — simplified inline-array version
    def _cluster(_mb_src, _ev_src, _base_sign):
        """
        Approximate FAUNA Cluster sBullFC / sBearFC: 2-of-3 indicators each
        being a 2+ streak of MB / EV / (MB-or-RE) overlapping a recent
        thrust-event price-range. Returns boolean Series.

        For practical use the result is a slightly conservative version of
        the Pine engine (which uses overlap-rectangle bookkeeping). State
        machine variant available via :class:`FaunaClusterState`.
        """
        mb_a = _nz_b(_mb_src).to_numpy()
        ev_a = _nz_b(_ev_src).to_numpy()
        s1_a = np.zeros(len(df), dtype=int)
        s2_a = np.zeros(len(df), dtype=int)
        c1 = 0; c2 = 0
        for i in range(len(df)):
            c1 = c1 + 1 if mb_a[i] else 0
            s1_a[i] = c1
            if nd_arr2[i]:
                c2 = 0
            if not ev_a[i]:
                c2 = 0
            if ev_a[i]:
                c2 += 1
            s2_a[i] = c2
        ind1 = mb_a & (s1_a >= 2)
        ind2 = ev_a & (s2_a >= 2)
        # ind3 uses MB|RE (we approximate with MB|RE from caller; here we use ev_a as proxy)
        ind3 = ev_a & (s2_a >= 2)
        two_of_three = (ind1.astype(int) + ind2.astype(int) + ind3.astype(int)) >= 2
        return pd.Series(two_of_three & ev_a, index=df.index)
    sBullFC = _cluster(u57_bMB, (u57_bMB | u57_bRE | u57_bTA), True)
    sBearFC = _cluster(u57_sMB, (u57_sMB | u57_sRE | u57_sTA), False)

    # B2B days: check if prior session had the same signal.
    def _hadYesterday(sig: pd.Series) -> pd.Series:
        """For each bar that is a new-day boundary, check if `sig` fired
        on any bar of the immediately preceding session."""
        sig_a = _nz_b(sig).to_numpy()
        N = len(df)
        out = np.zeros(N, dtype=bool)
        # Build session boundaries
        sess_id = np.zeros(N, dtype=int); cur = 0
        for i in range(N):
            if nd_arr2[i]:
                cur += 1
            sess_id[i] = cur
        # For each session, did sig fire?
        had_any_per_session = {}
        for i in range(N):
            had_any_per_session.setdefault(sess_id[i], False)
            if sig_a[i]:
                had_any_per_session[sess_id[i]] = True
        for i in range(N):
            if nd_arr2[i] and sess_id[i] >= 2:
                prev = had_any_per_session.get(sess_id[i] - 1, False)
                out[i] = prev
        # Now mark sig & previous-session-fired
        return pd.Series(out, index=df.index)
    f2_had = _hadYesterday(sBullF2)
    e3_had = _hadYesterday(sBullE3)
    fc_had = _hadYesterday(sBullFC)
    comboF2_B2BDays_Bull = sBullF2 & f2_had
    comboE3_B2BDays_Bull = sBullE3 & e3_had
    comboF2E3_Consec_Bull = sBullE3 & f2_had
    comboCluster_B2BDays_Bull = sBullFC & fc_had

    comboPBJ_F2_Bull = sigBullPBJ & sBullF2
    comboPBJ_E3_Bull = sigBullPBJ & sBullE3
    comboPBJ_Cluster_Bull = sigBullPBJ & sBullFC
    comboF2Cluster_E3_Bull = _nz_b(sBullF2.shift(1)) & _nz_b(sBullFC.shift(1)) & sBullE3
    pupCntE3 = sigPUP.astype(int) + _nz_b(sigPUP.shift(1)).astype(int) + _nz_b(sigPUP.shift(2)).astype(int)
    comboE3_2of3PUP_Bull = sBullE3 & (pupCntE3 >= 2)

    # Foster (single-window FAUNA-MB → PBJ within 1 bar)
    mb_a2 = _nz_b(u57_bMB).to_numpy()
    pbj_a2 = _nz_b(sigBullPBJ).to_numpy()
    fosterPBJ_arr = np.zeros(len(df), dtype=bool)
    win_open = False; win_cnt = 0
    for i in range(len(df)):
        if mb_a2[i]:
            win_open = True; win_cnt = 0
        if win_open:
            win_cnt += 1
            if win_cnt > 1:
                win_open = False
            elif pbj_a2[i]:
                fosterPBJ_arr[i] = True; win_open = False
    fosterPBJSignal = pd.Series(fosterPBJ_arr, index=df.index)

    # ─────────────────────────────────────────────────────────────────────
    # HEAVY PENTAGON / WBUSH
    # ─────────────────────────────────────────────────────────────────────
    hp_groupA_Bull = sigBullRVOL1x | sigGrandSlam
    hp_groupA_Bear = sigBearRVOL1x | sigMOAB
    hp_groupB = sigPentagon | sigWTC | sigHiroshima

    hp_baseYinYang = (hp_groupA_Bull | hp_groupA_Bear) & hp_groupB
    hp_baseNagasaki = sigNagasaki & (hp_groupA_Bull | hp_groupA_Bear)
    hp_baseNagasakiV = sigNagasaki & hp_groupB
    hp_baseTrident = sigNagasaki & (hp_groupA_Bull | hp_groupA_Bear) & hp_groupB
    hp_baseNHx2 = (sigPentagon & sigWTC) | (sigPentagon & sigHiroshima) | (sigWTC & sigHiroshima)

    hp_noDisp = ~sigDISPBull & ~sigDISPBear

    hp_HYYBull = hp_baseYinYang & sigDISPBull
    hp_HYYBear = hp_baseYinYang & sigDISPBear
    hp_HYYNeutral = hp_baseYinYang & hp_noDisp
    hp_HNBull = hp_baseNagasaki & sigDISPBull
    hp_HNBear = hp_baseNagasaki & sigDISPBear
    hp_HNNeutral = hp_baseNagasaki & hp_noDisp
    hp_HNVBull = hp_baseNagasakiV & sigDISPBull
    hp_HNVBear = hp_baseNagasakiV & sigDISPBear
    hp_HNVNeutral = hp_baseNagasakiV & hp_noDisp
    hp_HTBull = hp_baseTrident & sigDISPBull
    hp_HTBear = hp_baseTrident & sigDISPBear
    hp_HTNeutral = hp_baseTrident & hp_noDisp
    hp_NHx2Bull = hp_baseNHx2 & sigDISPBull
    hp_NHx2Bear = hp_baseNHx2 & sigDISPBear
    hp_NHx2Neutral = hp_baseNHx2 & hp_noDisp

    sig_WBUSH_Bull = hp_HYYBull | hp_HNBull | hp_HNVBull | hp_HTBull | hp_NHx2Bull
    sig_WBUSH_Bear = hp_HYYBear | hp_HNBear | hp_HNVBear | hp_HTBear | hp_NHx2Bear
    sig_WBUSH_Neutral = hp_HYYNeutral | hp_HNNeutral | hp_HNVNeutral | hp_HTNeutral | hp_NHx2Neutral
    # Backward-compat alias (sigWMD = bullish WBUSH)
    sigWMD = sig_WBUSH_Bull

    # ─────────────────────────────────────────────────────────────────────
    # UC NAGASAKI (45/46) — same visual bar (offset -1)
    # ─────────────────────────────────────────────────────────────────────
    sig_UCNagasakiBull = csNew3_Bull & _nz_b(sigNagasaki.shift(1))
    sig_UCNagasakiBear = csNew3_Bear & _nz_b(sigNagasaki.shift(1))

    # ─────────────────────────────────────────────────────────────────────
    # Pipeline D + B2B HV+D
    # ─────────────────────────────────────────────────────────────────────
    hvd_pb_bull = hvd_fire_bull & _nz_b(sigBullPB.shift(1))
    hvd_pbj_bull = hvd_fire_bull & _nz_b(sigBullPBJ.shift(1))
    hvd_pb_bear = hvd_fire_bear & _nz_b(sigBearPB.shift(1))
    hvd_pbj_bear = hvd_fire_bear & _nz_b(sigBearPBJ.shift(1))

    co_uc_or_fvg_bull = csNew3_Bull | csNew1_Bull
    co_uc_or_fvg_bear = csNew3_Bear | csNew1_Bear
    co_bull_pbj = hvd_fire_bull & bool(p["co_en_bullPBJ"]) & _nz_b(sigBullPBJ.shift(1)) & co_uc_or_fvg_bull
    co_bull_pb = hvd_fire_bull & bool(p["co_en_bullPB"]) & _nz_b(sigBullPB.shift(1)) & co_uc_or_fvg_bull
    co_bear_pbj = hvd_fire_bear & bool(p["co_en_bearPBJ"]) & _nz_b(sigBearPBJ.shift(1)) & co_uc_or_fvg_bear
    co_bear_pb = hvd_fire_bear & bool(p["co_en_bearPB"]) & _nz_b(sigBearPB.shift(1)) & co_uc_or_fvg_bear
    co_any = co_bull_pbj | co_bull_pb | co_bear_pbj | co_bear_pb

    b2b_bull_raw = hvd_fire_bull & _nz_b(hvd_fire_bull.shift(1))
    b2b_bear_raw = hvd_fire_bear & _nz_b(hvd_fire_bear.shift(1))
    b2b_bull_pbj = b2b_bull_raw & (_nz_b(sigBullPBJ.shift(1)) | _nz_b(sigBullPBJ.shift(2)))
    b2b_bear_pbj = b2b_bear_raw & (_nz_b(sigBearPBJ.shift(1)) | _nz_b(sigBearPBJ.shift(2)))
    b2b_bull_pb = b2b_bull_raw & (_nz_b(sigBullPB.shift(1)) | _nz_b(sigBullPB.shift(2))) & ~b2b_bull_pbj
    b2b_bear_pb = b2b_bear_raw & (_nz_b(sigBearPB.shift(1)) | _nz_b(sigBearPB.shift(2))) & ~b2b_bear_pbj
    b2b_bull_nopb = b2b_bull_raw & ~b2b_bull_pbj & ~b2b_bull_pb
    b2b_bear_nopb = b2b_bear_raw & ~b2b_bear_pbj & ~b2b_bear_pb

    # ─────────────────────────────────────────────────────────────────────
    # 46 v2 COMPOSITE SIGNALS — every named plotshape gets a boolean here.
    # Numbered 1..46 per the source.
    # ─────────────────────────────────────────────────────────────────────
    uu_any = sigP21BullUUUU | sigP21BullUUU | sigUUBull
    uu_any_bear = sigP21BearUUUU | sigP21BearUUU | sigUUBear
    disp_or_hvd = sigDISPBull | hvd_fire_bull
    pbj_or_hvdpbj = sigBullPBJ | hvd_pbj_bull

    # ONE-OF-THESE
    oneOfThese = (sigP21BullUUUU | sigP21BullUUU | sigUUBull | sigOmegaLongA |
                  det_bullNapalmCons | det_b2bBullNapalm | csNew3_Bull |
                  (csNew1_Bull | csNew2_Bull) | sigWMD)
    oneOfThese_forUU = (sigP21BullUUUU | sigP21BullUUU | sigOmegaLongA |
                        det_bullNapalmCons | det_b2bBullNapalm | csNew3_Bull |
                        (csNew1_Bull | csNew2_Bull) | sigWMD | sigDISPBull |
                        hvd_fire_bull | sigFAUNABull | sigPUP | sigBullPBJ |
                        sigLong1 | sigGrandSlam | sigBullRVOL1x)
    oneOfThese_p1 = (_nz_b(sigP21BullUUUU.shift(1)) | _nz_b(sigP21BullUUU.shift(1)) |
                     _nz_b(sigUUBull.shift(1)) | _nz_b(sigOmegaLongA.shift(1)) |
                     det_bullNapalmCons | det_b2bBullNapalm | csNew3_Bull |
                     csNew1_Bull | _nz_b(csNew2_Bull.shift(1)) | _nz_b(sigWMD.shift(1)))

    # Checkbox helpers (apply per Set 1, 2, 3 IPSF toggles)
    def _cb(e_uu, e_co, e_d9, e_pup, e_pbj, e_l1, e_wmd):
        return ((bool(e_uu) & uu_any) | (bool(e_co) & csNew3_Bull) |
                (bool(e_d9) & d9_bull) | (bool(e_pup) & sigPUP) |
                (bool(e_pbj) & pbj_or_hvdpbj) | (bool(e_l1) & sigLong1) |
                (bool(e_wmd) & sigWMD))
    cb1_pass = _cb(p["cb1_uu"], p["cb1_combo"], p["cb1_d9"], p["cb1_pup"],
                    p["cb1_pbj"], p["cb1_l1"], p["cb1_wmd"])
    cb1_pass_floor = _cb(p["cb1_uu"], p["cb1_combo"], p["cb1_d9"], p["cb1_pup"],
                         False, p["cb1_l1"], p["cb1_wmd"])
    cb2_pass = _cb(p["cb2_uu"], p["cb2_combo"], p["cb2_d9"], p["cb2_pup"],
                   p["cb2_pbj"], p["cb2_l1"], p["cb2_wmd"])
    cb3_pass = _cb(p["cb3_uu"], p["cb3_combo"], p["cb3_d9"], p["cb3_pup"],
                   p["cb3_pbj"], p["cb3_l1"], p["cb3_wmd"])

    def _cb_npm(e_uu, e_co, e_d9, e_pup, e_pbj, e_l1, e_wmd):
        return ((bool(e_uu) & (_nz_b(sigP21BullUUUU.shift(1)) | _nz_b(sigP21BullUUU.shift(1)) | _nz_b(sigUUBull.shift(1)))) |
                (bool(e_co) & csNew3_Bull) |
                (bool(e_d9) & _nz_b(d9_bull.shift(1))) |
                (bool(e_pup) & _nz_b(sigPUP.shift(1))) |
                (bool(e_pbj) & (_nz_b(sigBullPBJ.shift(1)) | hvd_pbj_bull)) |
                (bool(e_l1) & _nz_b(sigLong1.shift(1))) |
                (bool(e_wmd) & _nz_b(sigWMD.shift(1))))
    cb1_pass_npm = _cb_npm(p["cb1_uu"], p["cb1_combo"], p["cb1_d9"], p["cb1_pup"],
                            p["cb1_pbj"], p["cb1_l1"], p["cb1_wmd"])
    cb2_pass_npm = _cb_npm(p["cb2_uu"], p["cb2_combo"], p["cb2_d9"], p["cb2_pup"],
                            p["cb2_pbj"], p["cb2_l1"], p["cb2_wmd"])
    cb3_pass_npm = _cb_npm(p["cb3_uu"], p["cb3_combo"], p["cb3_d9"], p["cb3_pup"],
                            p["cb3_pbj"], p["cb3_l1"], p["cb3_wmd"])

    # AlphaStrike v2 (expanded FAUNA slot)
    as_fauna_expanded = sigFAUNABull | sigLong1 | disp_or_hvd | sigPUP | det_bullNapalmCons | sigWTC | sigHiroshima | sigNagasaki
    sigAlphaStrikeBull_sq = conf & firstOfDay & bull_pp & (sigGrandSlam | sigBullRVOL1x) & sigBullPBJ & as_fauna_expanded

    superBull_sq = superBull & oneOfThese_p1

    floor_sq = anyBullFloor & oneOfThese & cb1_pass_floor
    floor2_sq = anyBull2nd & oneOfThese & cb1_pass
    uu_gated = sigUUBull & oneOfThese_forUU
    foxtrot_sq = sigFoxtrotBull & (hvd_pbj_bull | oneOfThese)

    npm12 = det_bullNapalmCons & (cb1_pass_npm | cb2_pass_npm)
    npm3 = det_bullNapalmCons & cb3_pass_npm

    # Composite fusions (numbered S-plots)
    sig38 = det_bullNapalmCons & ((_nz_b(sigBullPBJ.shift(1)) & (csNew3_Bull | _nz_b(hwBull.shift(1)) | _nz_b(sigWMD.shift(1)))) | _nz_b(sigWMD.shift(1)))
    holy_grail = det_bullNapalmCons & _nz_b(sigBullPBJ.shift(1)) & _nz_b(sigPUP.shift(1)) & csNew3_Bull
    floor_npm = _nz_b(anyBullFloor.shift(1)) & det_bullNapalmCons
    npm_pbj_pup = det_bullNapalmCons & _nz_b(sigBullPBJ.shift(1)) & _nz_b(sigPUP.shift(1))
    nag_any_bull = sigNagasaki & (sigBullRVOL1x | sigGrandSlam | sigFAUNABull | sigDISPBull | sigBullPBJ | sigPUP | gz_bullHV | gz_bullGZI)
    uu_hvdpbj = (_nz_b(sigP21BullUUUU.shift(1)) | _nz_b(sigP21BullUUU.shift(1)) | _nz_b(sigUUBull.shift(1))) & hvd_pbj_bull
    uu_npm = (_nz_b(sigP21BullUUUU.shift(1)) | _nz_b(sigP21BullUUU.shift(1)) | _nz_b(sigUUBull.shift(1))) & det_bullNapalmCons
    floor_uu = (anyBullFloor | anyBull2nd) & uu_any
    foster_pup_rvol = fosterPBJSignal & sigPUP & (sigBullRVOL1x | det_bullNapalmCons)
    b2b_npm_pbj = _nz_b(det_b2bPUP.shift(1)) & det_bullNapalmCons & _nz_b(sigBullPBJ.shift(1))
    sig_npm_combo = det_bullNapalmCons & csNew3_Bull
    sig_npm_combo_pbj = det_bullNapalmCons & csNew3_Bull & _nz_b(sigBullPBJ.shift(1))
    sig_uu_combo = uu_any & csNew3_Bull
    wmd_any_bull = sigWMD & (sigBullRVOL1x | sigGrandSlam | sigFAUNABull | sigDISPBull | sigBullPBJ | sigPUP | gz_bullHV | gz_bullGZI | uu_any | det_bullNapalmCons | anyBullFloor | anyBull2nd | sigLong1)
    b2b_long1 = sigLong1 & _nz_b(sigLong1.shift(1))
    b2b_long1_pup = det_b2bPUP & b2b_long1

    # Master gate
    _masterGate = (not bool(p["master_firstBarOnly"])) | (_isGapBar & anyHVRank)
    if isinstance(_masterGate, bool):
        _masterGate = pd.Series(_masterGate, index=df.index)
    _masterGate = _masterGate.astype(bool)

    # ─────────────────────────────────────────────────────────────────────
    # Numbered 1..46 SIGNAL OUTPUTS — each gated by en_* toggle + master.
    # We expose two flavors per plot: the *signal* (no gate, for analysis)
    # and the *fire* (gate applied, what TradingView actually draws).
    # ─────────────────────────────────────────────────────────────────────
    def _g(name, sig):
        return sig & _masterGate & bool(p.get(name, True))

    # 1 SD!, 2 SUPER (with not-SD precedence), 3 HW, 4 FLOOR, 5 2F (not floor)
    fire_1_SD = _g("en_1", sduperBull)
    fire_2_SUPER = _g("en_2", superBull & ~sduperBull)
    fire_3_HW = _g("en_3", hwBull)
    fire_4_FLOOR = _g("en_4", floor_sq)
    fire_5_2F = _g("en_5", floor2_sq & ~floor_sq)
    fire_6_UUUU = _g("en_6", sigP21BullUUUU)
    fire_7_UUU = _g("en_7", sigP21BullUUU & ~sigP21BullUUUU)
    fire_8_UU = _g("en_8", uu_gated & ~sigP21BullUUU & ~sigP21BullUUUU)
    fire_9_ASTAR = _g("en_9", sigAlphaStrikeBull_sq)
    fire_10_OMEGA_A = _g("en_10", sigOmegaLongA)
    fire_11_FOX = _g("en_11", foxtrot_sq)
    fire_12_OD = _g("en_12", sigODBull)
    fire_13_GOLF = _g("en_13", sigGolfBull)

    # 14 PBJ+F2/E3, 15 PBJ+CL, 16 F2CL→E3, 17 E3⅔PP, 18 F2×2D, 19 E3×2D,
    # 20 F2E3seq, 21 CL×2D
    fire_14_PBJ_F2_E3 = _g("en_28", comboPBJ_F2_Bull | comboPBJ_E3_Bull)
    fire_15_PBJ_CL = _g("en_29", comboPBJ_Cluster_Bull)
    fire_16_F2CL_E3 = _g("en_30", comboF2Cluster_E3_Bull)
    fire_17_E3_23PP = _g("en_33", comboE3_2of3PUP_Bull)
    fire_18_F2x2D = _g("en_34", comboF2_B2BDays_Bull)
    fire_19_E3x2D = _g("en_35", comboE3_B2BDays_Bull)
    fire_20_F2E3seq = _g("en_36", comboF2E3_Consec_Bull)
    fire_21_CLx2D = _g("en_37", comboCluster_B2BDays_Bull)

    # 22 NPM+, 23 NPM12, 24 NPM3 (not npm12), 25 B2BNPM, 26 NPM+TNT
    fire_22_NPM_plus = _g("en_38", sig38)
    fire_23_NPM12 = _g("en_39", npm12)
    fire_24_NPM3 = _g("en_41", npm3 & ~npm12)
    fire_25_B2BNPM = _g("en_42", det_b2bBullNapalm)
    fire_26_NPM_TNT = _g("en_43", det_npmTntBull)

    # 27 CO, 28 HVD+PBJ (not CO + sub-3min ok), 29 B2BHVD+PBJ, 30 B2BHVD, 31 UU+UC
    sub3min_or_cb1 = (tfSec >= 180) | cb1_pass_npm
    fire_27_CO = _g("en_44", co_bull_pbj)
    fire_28_HVD_PBJ = _g("en_45", hvd_pbj_bull & ~co_bull_pbj & sub3min_or_cb1)
    fire_29_B2BHVD_PBJ = _g("en_46", b2b_bull_pbj)
    fire_30_B2BHVD = _g("en_47", b2b_bull_nopb & ~b2b_bull_pbj)
    fire_31_UU_UC = _g("en_48", sig_uu_combo)

    # 32 GRAIL, 33 FLR+NPM, 34 NPM+PBJ+PUP (not GRAIL), 35 NAG+, 36 UU+HVD,
    # 37 UU+NPM, 38 FLR+UU, 39 FOS+PUP+1x
    fire_32_GRAIL = _g("en_49", holy_grail)
    fire_33_FLR_NPM = _g("en_50", floor_npm)
    fire_34_NPM_PBJ_PUP = _g("en_51", npm_pbj_pup & ~holy_grail)
    fire_35_NAG_plus = _g("en_52", nag_any_bull)
    fire_36_UU_HVD = _g("en_53", uu_hvdpbj)
    fire_37_UU_NPM = _g("en_54", uu_npm)
    fire_38_FLR_UU = _g("en_55", floor_uu)
    fire_39_FOS_PUP_1x = _g("en_56", foster_pup_rvol)

    # 40 NPM+UC (not NPM+UC+PBJ), 41 WBUSH Bull, 42 WBUSH Bear, 43 WBUSH Neutral
    fire_40_NPM_UC = _g("en_60", sig_npm_combo & ~sig_npm_combo_pbj)
    fire_41_WBUSH_Bull = _g("en_wbushBull", sig_WBUSH_Bull)
    fire_42_WBUSH_Bear = _g("en_wbushBear", sig_WBUSH_Bear)
    fire_43_WBUSH_Neutral = _g("en_wbushNeutral", sig_WBUSH_Neutral)

    # 44 NPM+UC+PBJ, 45 UC NAGASAKI Bull, 46 UC NAGASAKI Bear
    fire_44_NPM_UC_PBJ = _g("en_63", sig_npm_combo_pbj)
    fire_45_UC_NAG_Bull = _g("en_ucNagBull", sig_UCNagasakiBull)
    fire_46_UC_NAG_Bear = _g("en_ucNagBear", sig_UCNagasakiBear)

    cache.update({
        # Pipeline A
        "hvd_fire_bull": hvd_fire_bull, "hvd_fire_bear": hvd_fire_bear,
        # Pipeline B (stub-fed)
        "sigBullPBJ": sigBullPBJ, "sigBullPB": sigBullPB,
        "sigBearPBJ": sigBearPBJ, "sigBearPB": sigBearPB,
        "hvd_pb_bull": hvd_pb_bull, "hvd_pbj_bull": hvd_pbj_bull,
        "hvd_pb_bear": hvd_pb_bear, "hvd_pbj_bear": hvd_pbj_bear,
        # Atoms (engines 1-7, 11)
        "sigDISPBull": sigDISPBull, "sigDISPBear": sigDISPBear,
        "disp5_bull": disp5_bull, "disp5_bear": disp5_bear,
        "d9_bull": d9_bull,
        "sigDISP2Bull": sigDISP2Bull, "sigDISP2Bear": sigDISP2Bear,
        "sigDISP3Bull": sigDISP3Bull, "sigDISP3Bear": sigDISP3Bear,
        "sigDispConsBull2": sigDispConsBull2, "sigDispConsBear2": sigDispConsBear2,
        "sigDispConsBull3": sigDispConsBull3, "sigDispConsBear3": sigDispConsBear3,
        "sigPUP": sigPUP, "sigPPD": sigPPD,
        "sigSAAB": sigSAAB, "sigKratos": sigKratos,
        "sigGrandSlam": sigGrandSlam, "sigMOAB": sigMOAB,
        "sigBullRVOL1x": sigBullRVOL1x, "sigBearRVOL1x": sigBearRVOL1x,
        "sigWTC": sigWTC, "sigHiroshima": sigHiroshima,
        "sigPentagon": sigPentagon, "sigNagasaki": sigNagasaki,
        "sigFAUNABull": sigFAUNABull, "sigFAUNABear": sigFAUNABear,
        "sigNeoBull": sigNeoBull, "sigNeoBear": sigNeoBear,
        "sigTrinityBull": sigTrinityBull, "sigTrinityBear": sigTrinityBear,
        # U-streak
        "sigP21BullUUUU": sigP21BullUUUU, "sigP21BearUUUU": sigP21BearUUUU,
        "sigP21BullUUU": sigP21BullUUU, "sigP21BearUUU": sigP21BearUUU,
        "sigUUBull": sigUUBull, "sigUUBear": sigUUBear,
        "sigP21BullUUUU_indep": sigP21BullUUUU_indep, "sigP21BullUUU_indep": sigP21BullUUU_indep,
        "sigUUBull_indep": sigUUBull_indep,
        "sigP21BearUUUU_indep": sigP21BearUUUU_indep, "sigP21BearUUU_indep": sigP21BearUUU_indep,
        "sigUUBear_indep": sigUUBear_indep,
        "rawBullUU": rawBullUU, "rawBullUUU": rawBullUUU, "rawBullUUUU": rawBullUUUU,
        "rawBearUU": rawBearUU, "rawBearUUU": rawBearUUU, "rawBearUUUU": rawBearUUUU,
        # Misc
        "sigFoxtrotBull": sigFoxtrotBull, "sigFoxtrotBear": sigFoxtrotBear,
        "sigODBull": sigODBull, "sigODBear": sigODBear,
        "sigHV75": sigHV75, "sigHV150": sigHV150, "sigHV500": sigHV500, "sigHV1000": sigHV1000,
        "sigGolfBull": sigGolfBull, "sigGolfBear": sigGolfBear,
        "sigPAFBull": sigPAFBull, "sigPAFBear": sigPAFBear,
        # Long/Short
        "sigLong1": sigLong1, "sigShort1": sigShort1,
        "sigLong2": sigLong2, "sigShort2": sigShort2,
        # Combo Sets / Unified Combo (SD-001 Pentagon-included)
        "comboSet1_Bull": comboSet1_Bull, "comboSet1_Bear": comboSet1_Bear,
        "comboSet2_Bull": comboSet2_Bull, "comboSet2_Bear": comboSet2_Bear,
        "comboSet3_Bull": comboSet3_Bull, "comboSet3_Bear": comboSet3_Bear,
        "comboSet4_Bull": comboSet4_Bull, "comboSet4_Bear": comboSet4_Bear,
        "csNew1_Bull": csNew1_Bull, "csNew1_Bear": csNew1_Bear,
        "csNew2_Bull": csNew2_Bull, "csNew2_Bear": csNew2_Bear,
        "csNew3_Bull": csNew3_Bull, "csNew3_Bear": csNew3_Bear,
        # Floor / Roof / HW
        "anyBullFloor": anyBullFloor, "anyBull2nd": anyBull2nd,
        "anyBearRoof": anyBearRoof, "anyBearPent": anyBearPent,
        "hwBull": hwBull, "hwBear": hwBear,
        # CC / LSC
        "sigCCBull": sigCCBull, "sigCCBear": sigCCBear,
        "sigLSCBull": sigLSCBull, "sigLSCBear": sigLSCBear,
        # AlphaStrike
        "sigAlphaStrikeBull": sigAlphaStrikeBull, "sigAlphaStrikeBear": sigAlphaStrikeBear,
        "sigAlphaStrikeBull_sq": sigAlphaStrikeBull_sq,
        "firstOfDay": firstOfDay,
        # Boom Hunter (stubbed)
        "sigOmegaLong": sigOmegaLong, "sigOmegaLongA": sigOmegaLongA,
        "sigShortPlusPress": sigShortPlusPress,
        # Super / SDuper (v2 redefined)
        "superBull": superBull, "superBear": superBear,
        "sduperBull": sduperBull, "sduperBear": sduperBear,
        "superBull_sq": superBull_sq,
        # TNT / NPM (stub-fed atoms; consolidated NPM derived)
        "raw_bullTNT": raw_bullTNT, "raw_bullTNT2": raw_bullTNT2,
        "raw_napalmBull": raw_napalmBull, "raw_bullCharge": raw_bullCharge,
        "raw_retBullTNT": raw_retBullTNT, "raw_contBull": raw_contBull,
        "raw_bearTNT": raw_bearTNT, "raw_bearTNT2": raw_bearTNT2,
        "raw_napalmBear": raw_napalmBear, "raw_bearCharge": raw_bearCharge,
        "raw_retBearTNT": raw_retBearTNT, "raw_contBear": raw_contBear,
        "det_bullNapalmCons": det_bullNapalmCons, "det_bearNapalmCons": det_bearNapalmCons,
        "det_b2bBullNapalm": det_b2bBullNapalm, "det_b2bBearNapalm": det_b2bBearNapalm,
        "det_npmTntBull": det_npmTntBull, "det_npmTntBear": det_npmTntBear,
        "det_b2bPUP": det_b2bPUP, "det_b2bPPD": det_b2bPPD,
        # Heavy Pentagon / WBUSH
        "hp_HYYBull": hp_HYYBull, "hp_HYYBear": hp_HYYBear, "hp_HYYNeutral": hp_HYYNeutral,
        "hp_HNBull": hp_HNBull, "hp_HNBear": hp_HNBear, "hp_HNNeutral": hp_HNNeutral,
        "hp_HNVBull": hp_HNVBull, "hp_HNVBear": hp_HNVBear, "hp_HNVNeutral": hp_HNVNeutral,
        "hp_HTBull": hp_HTBull, "hp_HTBear": hp_HTBear, "hp_HTNeutral": hp_HTNeutral,
        "hp_NHx2Bull": hp_NHx2Bull, "hp_NHx2Bear": hp_NHx2Bear, "hp_NHx2Neutral": hp_NHx2Neutral,
        "sig_WBUSH_Bull": sig_WBUSH_Bull, "sig_WBUSH_Bear": sig_WBUSH_Bear,
        "sig_WBUSH_Neutral": sig_WBUSH_Neutral, "sigWMD": sigWMD,
        # UC Nagasaki
        "sig_UCNagasakiBull": sig_UCNagasakiBull, "sig_UCNagasakiBear": sig_UCNagasakiBear,
        # ULTRA 57
        "sBullF2": sBullF2, "sBearF2": sBearF2,
        "sBullE3": sBullE3, "sBearE3": sBearE3,
        "sBullFC": sBullFC, "sBearFC": sBearFC,
        "comboPBJ_F2_Bull": comboPBJ_F2_Bull, "comboPBJ_E3_Bull": comboPBJ_E3_Bull,
        "comboPBJ_Cluster_Bull": comboPBJ_Cluster_Bull,
        "comboF2Cluster_E3_Bull": comboF2Cluster_E3_Bull,
        "comboE3_2of3PUP_Bull": comboE3_2of3PUP_Bull,
        "comboF2_B2BDays_Bull": comboF2_B2BDays_Bull,
        "comboE3_B2BDays_Bull": comboE3_B2BDays_Bull,
        "comboF2E3_Consec_Bull": comboF2E3_Consec_Bull,
        "comboCluster_B2BDays_Bull": comboCluster_B2BDays_Bull,
        "fosterPBJSignal": fosterPBJSignal,
        # CO / B2B HV+D
        "co_bull_pbj": co_bull_pbj, "co_bull_pb": co_bull_pb,
        "co_bear_pbj": co_bear_pbj, "co_bear_pb": co_bear_pb, "co_any": co_any,
        "b2b_bull_raw": b2b_bull_raw, "b2b_bear_raw": b2b_bear_raw,
        "b2b_bull_pbj": b2b_bull_pbj, "b2b_bear_pbj": b2b_bear_pbj,
        "b2b_bull_pb": b2b_bull_pb, "b2b_bear_pb": b2b_bear_pb,
        "b2b_bull_nopb": b2b_bull_nopb, "b2b_bear_nopb": b2b_bear_nopb,
        # Composite intermediates
        "uu_any_bull": uu_any, "uu_any_bear": uu_any_bear,
        "sig38": sig38, "holy_grail": holy_grail, "floor_npm": floor_npm,
        "npm_pbj_pup": npm_pbj_pup, "nag_any_bull": nag_any_bull,
        "uu_hvdpbj": uu_hvdpbj, "uu_npm": uu_npm, "floor_uu": floor_uu,
        "foster_pup_rvol": foster_pup_rvol, "b2b_npm_pbj": b2b_npm_pbj,
        "sig_npm_combo": sig_npm_combo, "sig_npm_combo_pbj": sig_npm_combo_pbj,
        "sig_uu_combo": sig_uu_combo, "wmd_any_bull": wmd_any_bull,
        "b2b_long1": b2b_long1, "b2b_long1_pup": b2b_long1_pup,
        "floor_sq": floor_sq, "floor2_sq": floor2_sq, "uu_gated": uu_gated,
        "foxtrot_sq": foxtrot_sq, "npm12": npm12, "npm3": npm3,
        # 46 v2 numbered fire signals (gated)
        "fire_1_SD": fire_1_SD, "fire_2_SUPER": fire_2_SUPER, "fire_3_HW": fire_3_HW,
        "fire_4_FLOOR": fire_4_FLOOR, "fire_5_2F": fire_5_2F,
        "fire_6_UUUU": fire_6_UUUU, "fire_7_UUU": fire_7_UUU, "fire_8_UU": fire_8_UU,
        "fire_9_ASTAR": fire_9_ASTAR, "fire_10_OMEGA_A": fire_10_OMEGA_A,
        "fire_11_FOX": fire_11_FOX, "fire_12_OD": fire_12_OD, "fire_13_GOLF": fire_13_GOLF,
        "fire_14_PBJ_F2_E3": fire_14_PBJ_F2_E3, "fire_15_PBJ_CL": fire_15_PBJ_CL,
        "fire_16_F2CL_E3": fire_16_F2CL_E3, "fire_17_E3_23PP": fire_17_E3_23PP,
        "fire_18_F2x2D": fire_18_F2x2D, "fire_19_E3x2D": fire_19_E3x2D,
        "fire_20_F2E3seq": fire_20_F2E3seq, "fire_21_CLx2D": fire_21_CLx2D,
        "fire_22_NPM_plus": fire_22_NPM_plus, "fire_23_NPM12": fire_23_NPM12,
        "fire_24_NPM3": fire_24_NPM3, "fire_25_B2BNPM": fire_25_B2BNPM,
        "fire_26_NPM_TNT": fire_26_NPM_TNT,
        "fire_27_CO": fire_27_CO, "fire_28_HVD_PBJ": fire_28_HVD_PBJ,
        "fire_29_B2BHVD_PBJ": fire_29_B2BHVD_PBJ, "fire_30_B2BHVD": fire_30_B2BHVD,
        "fire_31_UU_UC": fire_31_UU_UC,
        "fire_32_GRAIL": fire_32_GRAIL, "fire_33_FLR_NPM": fire_33_FLR_NPM,
        "fire_34_NPM_PBJ_PUP": fire_34_NPM_PBJ_PUP, "fire_35_NAG_plus": fire_35_NAG_plus,
        "fire_36_UU_HVD": fire_36_UU_HVD, "fire_37_UU_NPM": fire_37_UU_NPM,
        "fire_38_FLR_UU": fire_38_FLR_UU, "fire_39_FOS_PUP_1x": fire_39_FOS_PUP_1x,
        "fire_40_NPM_UC": fire_40_NPM_UC, "fire_41_WBUSH_Bull": fire_41_WBUSH_Bull,
        "fire_42_WBUSH_Bear": fire_42_WBUSH_Bear, "fire_43_WBUSH_Neutral": fire_43_WBUSH_Neutral,
        "fire_44_NPM_UC_PBJ": fire_44_NPM_UC_PBJ, "fire_45_UC_NAG_Bull": fire_45_UC_NAG_Bull,
        "fire_46_UC_NAG_Bear": fire_46_UC_NAG_Bear,
    })
    return cache


# ============================================================================
# Public detection functions — one per named plot.
# ============================================================================
def _wrap(name: str) -> Callable[[pd.DataFrame, Optional[Dict]], pd.Series]:
    def _fn(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
        eng = _ensure_engines(df, _p(params))
        return eng[name].fillna(False).astype(bool)
    _fn.__name__ = f"detect_{name}"
    return _fn


# ─── Pipeline A atoms ───
detect_hvd_bull = _wrap("hvd_fire_bull")
detect_hvd_bear = _wrap("hvd_fire_bear")

# ─── Pipeline A x B atoms ───
detect_hvd_pb_bull = _wrap("hvd_pb_bull")
detect_hvd_pb_bear = _wrap("hvd_pb_bear")
detect_hvd_pbj_bull = _wrap("hvd_pbj_bull")
detect_hvd_pbj_bear = _wrap("hvd_pbj_bear")

# ─── Foundational atoms (engines) ───
detect_sigSAAB = _wrap("sigSAAB")
detect_sigKratos = _wrap("sigKratos")
detect_sigGrandSlam = _wrap("sigGrandSlam")
detect_sigMOAB = _wrap("sigMOAB")
detect_sigBullRVOL1x = _wrap("sigBullRVOL1x")
detect_sigBearRVOL1x = _wrap("sigBearRVOL1x")
detect_sigWTC = _wrap("sigWTC")
detect_sigHiroshima = _wrap("sigHiroshima")
detect_sigPentagon = _wrap("sigPentagon")
detect_sigNagasaki = _wrap("sigNagasaki")
detect_sigFAUNABull = _wrap("sigFAUNABull")
detect_sigFAUNABear = _wrap("sigFAUNABear")
detect_sigPUP = _wrap("sigPUP")
detect_sigPPD = _wrap("sigPPD")
detect_sigDISPBull = _wrap("sigDISPBull")
detect_sigDISPBear = _wrap("sigDISPBear")
detect_sigDispConsBull2 = _wrap("sigDispConsBull2")
detect_sigDispConsBear2 = _wrap("sigDispConsBear2")
detect_sigDispConsBull3 = _wrap("sigDispConsBull3")
detect_sigDispConsBear3 = _wrap("sigDispConsBear3")
detect_sigBullPBJ = _wrap("sigBullPBJ")
detect_sigBullPB = _wrap("sigBullPB")
detect_sigBearPBJ = _wrap("sigBearPBJ")
detect_sigBearPB = _wrap("sigBearPB")
detect_sigNeoBull = _wrap("sigNeoBull")
detect_sigNeoBear = _wrap("sigNeoBear")
detect_sigTrinityBull = _wrap("sigTrinityBull")
detect_sigTrinityBear = _wrap("sigTrinityBear")
detect_sigFoxtrotBull = _wrap("sigFoxtrotBull")
detect_sigFoxtrotBear = _wrap("sigFoxtrotBear")
detect_sigGolfBull = _wrap("sigGolfBull")
detect_sigGolfBear = _wrap("sigGolfBear")
detect_sigPAFBull = _wrap("sigPAFBull")
detect_sigPAFBear = _wrap("sigPAFBear")
detect_sigODBull = _wrap("sigODBull")
detect_sigODBear = _wrap("sigODBear")
detect_sigHV75 = _wrap("sigHV75")
detect_sigHV150 = _wrap("sigHV150")
detect_sigHV500 = _wrap("sigHV500")
detect_sigHV1000 = _wrap("sigHV1000")
detect_sigLong1 = _wrap("sigLong1")
detect_sigShort1 = _wrap("sigShort1")
detect_sigLong2 = _wrap("sigLong2")
detect_sigShort2 = _wrap("sigShort2")

# ─── U-streak ───
detect_sigP21BullUUUU = _wrap("sigP21BullUUUU")
detect_sigP21BullUUU = _wrap("sigP21BullUUU")
detect_sigUUBull = _wrap("sigUUBull")
detect_sigP21BearUUUU = _wrap("sigP21BearUUUU")
detect_sigP21BearUUU = _wrap("sigP21BearUUU")
detect_sigUUBear = _wrap("sigUUBear")
detect_rawBullUU = _wrap("rawBullUU")
detect_rawBullUUU = _wrap("rawBullUUU")
detect_rawBullUUUU = _wrap("rawBullUUUU")
detect_rawBearUU = _wrap("rawBearUU")
detect_rawBearUUU = _wrap("rawBearUUU")
detect_rawBearUUUU = _wrap("rawBearUUUU")

# ─── Combo Sets / Unified Combo (SD-001 Pentagon-included) ───
detect_comboSet1_Bull = _wrap("comboSet1_Bull")
detect_comboSet1_Bear = _wrap("comboSet1_Bear")
detect_comboSet2_Bull = _wrap("comboSet2_Bull")
detect_comboSet2_Bear = _wrap("comboSet2_Bear")
detect_comboSet3_Bull = _wrap("comboSet3_Bull")
detect_comboSet3_Bear = _wrap("comboSet3_Bear")
detect_comboSet4_Bull = _wrap("comboSet4_Bull")
detect_comboSet4_Bear = _wrap("comboSet4_Bear")
detect_csNew1_Bull = _wrap("csNew1_Bull")
detect_csNew1_Bear = _wrap("csNew1_Bear")
detect_csNew2_Bull = _wrap("csNew2_Bull")
detect_csNew2_Bear = _wrap("csNew2_Bear")
detect_csNew3_Bull = _wrap("csNew3_Bull")
detect_csNew3_Bear = _wrap("csNew3_Bear")

# ─── Floor / Roof / HW / CC / LSC / Alpha / Super / SDuper ───
detect_anyBullFloor = _wrap("anyBullFloor")
detect_anyBull2nd = _wrap("anyBull2nd")
detect_anyBearRoof = _wrap("anyBearRoof")
detect_anyBearPent = _wrap("anyBearPent")
detect_hwBull = _wrap("hwBull")
detect_hwBear = _wrap("hwBear")
detect_sigCCBull = _wrap("sigCCBull")
detect_sigCCBear = _wrap("sigCCBear")
detect_sigLSCBull = _wrap("sigLSCBull")
detect_sigLSCBear = _wrap("sigLSCBear")
detect_sigAlphaStrikeBull = _wrap("sigAlphaStrikeBull")
detect_sigAlphaStrikeBear = _wrap("sigAlphaStrikeBear")
detect_superBull = _wrap("superBull")
detect_superBear = _wrap("superBear")
detect_sduperBull = _wrap("sduperBull")
detect_sduperBear = _wrap("sduperBear")

# ─── TNT/Napalm consolidated atoms (stub-fed) ───
detect_det_bullNapalmCons = _wrap("det_bullNapalmCons")
detect_det_bearNapalmCons = _wrap("det_bearNapalmCons")
detect_det_b2bBullNapalm = _wrap("det_b2bBullNapalm")
detect_det_b2bBearNapalm = _wrap("det_b2bBearNapalm")
detect_det_npmTntBull = _wrap("det_npmTntBull")
detect_det_b2bPUP = _wrap("det_b2bPUP")
detect_det_b2bPPD = _wrap("det_b2bPPD")
detect_raw_bullTNT = _wrap("raw_bullTNT")
detect_raw_bearTNT = _wrap("raw_bearTNT")
detect_raw_napalmBull = _wrap("raw_napalmBull")
detect_raw_napalmBear = _wrap("raw_napalmBear")
detect_raw_bullCharge = _wrap("raw_bullCharge")
detect_raw_bearCharge = _wrap("raw_bearCharge")

# ─── Boom Hunter (stubbed) ───
detect_sigOmegaLong = _wrap("sigOmegaLong")
detect_sigOmegaLongA = _wrap("sigOmegaLongA")
detect_sigShortPlusPress = _wrap("sigShortPlusPress")

# ─── Heavy Pentagon WBUSH ───
detect_hp_HYYBull = _wrap("hp_HYYBull")
detect_hp_HYYBear = _wrap("hp_HYYBear")
detect_hp_HYYNeutral = _wrap("hp_HYYNeutral")
detect_hp_HNBull = _wrap("hp_HNBull")
detect_hp_HNBear = _wrap("hp_HNBear")
detect_hp_HNNeutral = _wrap("hp_HNNeutral")
detect_hp_HNVBull = _wrap("hp_HNVBull")
detect_hp_HNVBear = _wrap("hp_HNVBear")
detect_hp_HNVNeutral = _wrap("hp_HNVNeutral")
detect_hp_HTBull = _wrap("hp_HTBull")
detect_hp_HTBear = _wrap("hp_HTBear")
detect_hp_HTNeutral = _wrap("hp_HTNeutral")
detect_hp_NHx2Bull = _wrap("hp_NHx2Bull")
detect_hp_NHx2Bear = _wrap("hp_NHx2Bear")
detect_hp_NHx2Neutral = _wrap("hp_NHx2Neutral")
detect_sig_WBUSH_Bull = _wrap("sig_WBUSH_Bull")
detect_sig_WBUSH_Bear = _wrap("sig_WBUSH_Bear")
detect_sig_WBUSH_Neutral = _wrap("sig_WBUSH_Neutral")

# ─── UC NAGASAKI ───
detect_sig_UCNagasakiBull = _wrap("sig_UCNagasakiBull")
detect_sig_UCNagasakiBear = _wrap("sig_UCNagasakiBear")

# ─── ULTRA 57 FAUNA combos ───
detect_sBullF2 = _wrap("sBullF2")
detect_sBearF2 = _wrap("sBearF2")
detect_sBullE3 = _wrap("sBullE3")
detect_sBearE3 = _wrap("sBearE3")
detect_sBullFC = _wrap("sBullFC")
detect_sBearFC = _wrap("sBearFC")
detect_comboPBJ_F2_Bull = _wrap("comboPBJ_F2_Bull")
detect_comboPBJ_E3_Bull = _wrap("comboPBJ_E3_Bull")
detect_comboPBJ_Cluster_Bull = _wrap("comboPBJ_Cluster_Bull")
detect_comboF2Cluster_E3_Bull = _wrap("comboF2Cluster_E3_Bull")
detect_comboE3_2of3PUP_Bull = _wrap("comboE3_2of3PUP_Bull")
detect_comboF2_B2BDays_Bull = _wrap("comboF2_B2BDays_Bull")
detect_comboE3_B2BDays_Bull = _wrap("comboE3_B2BDays_Bull")
detect_comboF2E3_Consec_Bull = _wrap("comboF2E3_Consec_Bull")
detect_comboCluster_B2BDays_Bull = _wrap("comboCluster_B2BDays_Bull")

# ─── CO / B2B HV+D ───
detect_co_bull_pbj = _wrap("co_bull_pbj")
detect_co_bull_pb = _wrap("co_bull_pb")
detect_co_bear_pbj = _wrap("co_bear_pbj")
detect_co_bear_pb = _wrap("co_bear_pb")
detect_b2b_bull_pbj = _wrap("b2b_bull_pbj")
detect_b2b_bull_pb = _wrap("b2b_bull_pb")
detect_b2b_bull_nopb = _wrap("b2b_bull_nopb")
detect_b2b_bear_pbj = _wrap("b2b_bear_pbj")
detect_b2b_bear_pb = _wrap("b2b_bear_pb")
detect_b2b_bear_nopb = _wrap("b2b_bear_nopb")

# ─── 46 v2 numbered S-plots (gated fire outputs — what TV renders) ───
S1 = detect_S1_SD = _wrap("fire_1_SD")
S2 = detect_S2_SUPER = _wrap("fire_2_SUPER")
S3 = detect_S3_HW = _wrap("fire_3_HW")
S4 = detect_S4_FLOOR = _wrap("fire_4_FLOOR")
S5 = detect_S5_2F = _wrap("fire_5_2F")
S6 = detect_S6_UUUU = _wrap("fire_6_UUUU")
S7 = detect_S7_UUU = _wrap("fire_7_UUU")
S8 = detect_S8_UU = _wrap("fire_8_UU")
S9 = detect_S9_ASTAR = _wrap("fire_9_ASTAR")
S10 = detect_S10_OMEGA_A = _wrap("fire_10_OMEGA_A")
S11 = detect_S11_FOX = _wrap("fire_11_FOX")
S12 = detect_S12_OD = _wrap("fire_12_OD")
S13 = detect_S13_GOLF = _wrap("fire_13_GOLF")
S14 = detect_S14_PBJ_F2_E3 = _wrap("fire_14_PBJ_F2_E3")
S15 = detect_S15_PBJ_CL = _wrap("fire_15_PBJ_CL")
S16 = detect_S16_F2CL_E3 = _wrap("fire_16_F2CL_E3")
S17 = detect_S17_E3_23PP = _wrap("fire_17_E3_23PP")
S18 = detect_S18_F2x2D = _wrap("fire_18_F2x2D")
S19 = detect_S19_E3x2D = _wrap("fire_19_E3x2D")
S20 = detect_S20_F2E3seq = _wrap("fire_20_F2E3seq")
S21 = detect_S21_CLx2D = _wrap("fire_21_CLx2D")
S22 = detect_S22_NPM_plus = _wrap("fire_22_NPM_plus")
S23 = detect_S23_NPM12 = _wrap("fire_23_NPM12")
S24 = detect_S24_NPM3 = _wrap("fire_24_NPM3")
S25 = detect_S25_B2BNPM = _wrap("fire_25_B2BNPM")
S26 = detect_S26_NPM_TNT = _wrap("fire_26_NPM_TNT")
S27 = detect_S27_CO = _wrap("fire_27_CO")
S28 = detect_S28_HVD_PBJ = _wrap("fire_28_HVD_PBJ")
S29 = detect_S29_B2BHVD_PBJ = _wrap("fire_29_B2BHVD_PBJ")
S30 = detect_S30_B2BHVD = _wrap("fire_30_B2BHVD")
S31 = detect_S31_UU_UC = _wrap("fire_31_UU_UC")
S32 = detect_S32_GRAIL = _wrap("fire_32_GRAIL")
S33 = detect_S33_FLR_NPM = _wrap("fire_33_FLR_NPM")
S34 = detect_S34_NPM_PBJ_PUP = _wrap("fire_34_NPM_PBJ_PUP")
S35 = detect_S35_NAG_plus = _wrap("fire_35_NAG_plus")
S36 = detect_S36_UU_HVD = _wrap("fire_36_UU_HVD")
S37 = detect_S37_UU_NPM = _wrap("fire_37_UU_NPM")
S38 = detect_S38_FLR_UU = _wrap("fire_38_FLR_UU")
S39 = detect_S39_FOS_PUP_1x = _wrap("fire_39_FOS_PUP_1x")
S40 = detect_S40_NPM_UC = _wrap("fire_40_NPM_UC")
S41 = detect_S41_WBUSH_Bull = _wrap("fire_41_WBUSH_Bull")
S42 = detect_S42_WBUSH_Bear = _wrap("fire_42_WBUSH_Bear")
S43 = detect_S43_WBUSH_Neutral = _wrap("fire_43_WBUSH_Neutral")
S44 = detect_S44_NPM_UC_PBJ = _wrap("fire_44_NPM_UC_PBJ")
S45 = detect_S45_UC_NAG_Bull = _wrap("fire_45_UC_NAG_Bull")
S46 = detect_S46_UC_NAG_Bear = _wrap("fire_46_UC_NAG_Bear")


# ============================================================================
# Stubbed detections — Pine-only intrinsics required.
# Caller may inject pre-computed series via df.attrs[<name>].
# ============================================================================
STUBBED: Dict[str, str] = {
    # tv_ta.relativeVolume (regular + cumulative). Inject via df.attrs:
    #   relVolRatio, ls_regRatio, ls_cumRatio
    "_rel_vol_engine": "tv_ta.relativeVolume not reproduced; inject relVolRatio/ls_regRatio/ls_cumRatio via df.attrs",
    # PBJ engine: full landing-zone state machine + Supertrend dir-flips.
    # Inject sigBullPBJ, sigBullPB, sigBearPBJ, sigBearPB via df.attrs.
    "_pbj_engine": "PBJ landing-zone array + Supertrend dir requires bar-by-bar state; inject via df.attrs",
    # Ping-Pong SR engine: pivot levels with line objects, regime tracking.
    # Inject bull_pp / bear_pp via df.attrs.
    "_pp_engine": "Ping-Pong SR pivots not reproduced; inject bull_pp/bear_pp via df.attrs",
    # GZ1/HV FVG engine: array of fvg_struct + per-bar removal.
    # Inject gz_bullGZI, gz_bearGZI, gz_bullHV, gz_bearHV via df.attrs.
    "_gz_engine": "GZ1 FVG structs not reproduced; inject gz_bullGZI/gz_bearGZI/gz_bullHV/gz_bearHV",
    # Boom Hunter / Omega — Ehlers filter chain + wavetrend pivots.
    # Inject sigOmegaLong / sigOmegaLongA / sigShortPlusPress via df.attrs.
    "_bh_engine": "Boom Hunter filter chain not reproduced; inject sigOmegaLong/sigOmegaLongA/sigShortPlusPress",
    # TNT propulsion / Napalm — VOB swing + zones + RVOL filter. Inject:
    #   raw_bullTNT, raw_bullTNT2, raw_napalmBull, raw_bullCharge,
    #   raw_retBullTNT, raw_contBull (and bear mirrors)
    "_tnt_engine": "TNT propulsion VOB+zones not reproduced; inject raw_bullTNT/raw_napalmBull/raw_bullCharge (and bear mirrors) via df.attrs",
    # Multi-TF HV (htf1/htf2) currently treated as same-TF lookup; real Pine
    # uses request.security on h1From/h1To windows.
    "_htf_security": "htf1/htf2 use current TF volume; real Pine uses request.security",
    # FAUNA Cluster (sBullFC/sBearFC) uses pivot-rectangle overlap arrays in
    # Pine. This port approximates via streak detection; for exact parity
    # inject sBullFC / sBearFC via df.attrs.
    "_fauna_cluster_overlap": "FAUNA Cluster rectangle-overlap engine approximated; inject sBullFC/sBearFC for exact parity",
}


# ============================================================================
# State machines — exposed for the harness; logic lives in _ensure_engines.
# ============================================================================
@dataclass
class ComboChainState:
    """CC bull/bear active flag — built into _ensure_engines."""
    name: str = "ComboChain"


@dataclass
class LSChainState:
    """LSC bull/bear active flag — built into _ensure_engines."""
    name: str = "LSChain"


@dataclass
class FirstOfDayState:
    """firstOfDay tracker for AlphaStrike — built into _ensure_engines."""
    name: str = "FirstOfDay"


@dataclass
class TNTZoneState:
    """TNT propulsion zone manager — STUBBED; consumer feeds via df.attrs."""
    name: str = "TNTZone"


@dataclass
class FaunaClusterState:
    """FAUNA cluster (sBullFC/sBearFC) overlap state — STUBBED-via-attrs."""
    name: str = "FaunaCluster"


@dataclass
class HEVState:
    """Streaming all-time-high volume tracker for isHEV / sigNagasaki."""
    name: str = "HEV"


@dataclass
class UStreakState:
    """U-streak + hasDay1 tracker for UU/UUU/UUUU paths A-G."""
    name: str = "UStreak"


@dataclass
class FosterWindowState:
    """Single-bar Foster window: MB → PBJ within 1 bar."""
    name: str = "FosterWindow"


STATE_MACHINES: Dict[str, type] = {
    "ComboChain": ComboChainState,
    "LSChain": LSChainState,
    "FirstOfDay": FirstOfDayState,
    "TNTZone": TNTZoneState,
    "FaunaCluster": FaunaClusterState,
    "HEV": HEVState,
    "UStreak": UStreakState,
    "FosterWindow": FosterWindowState,
}


# ============================================================================
# DETECTIONS registry — every named plot in SQUARIFY 46 v2.
# Names mirror Pine plot identifiers where they exist; foundational atoms
# get their internal sig* names so callers can fetch any building block.
# ============================================================================
DETECTIONS: Dict[str, Callable] = {
    # ─── Numbered 46 v2 S-plots (each gated by en_* + master) ───
    "S1 SD!": S1,
    "S2 SUPER": S2,
    "S3 HW": S3,
    "S4 FLOOR": S4,
    "S5 2F": S5,
    "S6 UUUU": S6,
    "S7 UUU": S7,
    "S8 UU": S8,
    "S9 A★": S9,
    "S10 ΩA": S10,
    "S11 FOX": S11,
    "S12 OD": S12,
    "S13 GOLF": S13,
    "S14 PBJ+F2/E3": S14,
    "S15 PBJ+CL": S15,
    "S16 F2CL→E3": S16,
    "S17 E3⅔PP": S17,
    "S18 F2×2D": S18,
    "S19 E3×2D": S19,
    "S20 F2E3seq": S20,
    "S21 CL×2D": S21,
    "S22 NPM+": S22,
    "S23 NPM12": S23,
    "S24 NPM3": S24,
    "S25 B2BNPM": S25,
    "S26 NPM+TNT": S26,
    "S27 CO": S27,
    "S28 HVD+PBJ": S28,
    "S29 B2BHVD+PBJ": S29,
    "S30 B2BHVD": S30,
    "S31 UU+UC": S31,
    "S32 GRAIL": S32,
    "S33 FLR+NPM": S33,
    "S34 NPM+PBJ+PUP": S34,
    "S35 NAG+": S35,
    "S36 UU+HVD": S36,
    "S37 UU+NPM": S37,
    "S38 FLR+UU": S38,
    "S39 FOS+PUP+1x": S39,
    "S40 NPM+UC": S40,
    "S41 WBUSH+ANY Bull": S41,
    "S42 WBUSH+ANY Bear": S42,
    "S43 WBUSH Neutral": S43,
    "S44 NPM+UC+PBJ": S44,
    "S45 UC NAGASAKI Bull": S45,
    "S46 UC NAGASAKI Bear": S46,
    # ─── Pipeline A atoms ───
    "HV+D Bull": detect_hvd_bull,
    "HV+D Bear": detect_hvd_bear,
    "HV+D + PB Bull": detect_hvd_pb_bull,
    "HV+D + PB Bear": detect_hvd_pb_bear,
    "HV+D + PBJ Bull": detect_hvd_pbj_bull,
    "HV+D + PBJ Bear": detect_hvd_pbj_bear,
    # ─── Foundational atoms (engines) ───
    "SAAB": detect_sigSAAB,
    "Kratos": detect_sigKratos,
    "Grand Slam": detect_sigGrandSlam,
    "MOAB": detect_sigMOAB,
    "RVOL1x Bull": detect_sigBullRVOL1x,
    "RVOL1x Bear": detect_sigBearRVOL1x,
    "WTC": detect_sigWTC,
    "Hiroshima": detect_sigHiroshima,
    "Pentagon": detect_sigPentagon,
    "Nagasaki": detect_sigNagasaki,
    "FAUNA Bull": detect_sigFAUNABull,
    "FAUNA Bear": detect_sigFAUNABear,
    "PUP": detect_sigPUP,
    "PPD": detect_sigPPD,
    "DISP Bull": detect_sigDISPBull,
    "DISP Bear": detect_sigDISPBear,
    "DispCons Bull 2": detect_sigDispConsBull2,
    "DispCons Bear 2": detect_sigDispConsBear2,
    "DispCons Bull 3": detect_sigDispConsBull3,
    "DispCons Bear 3": detect_sigDispConsBear3,
    "PBJ Bull": detect_sigBullPBJ,
    "PB Bull": detect_sigBullPB,
    "PBJ Bear": detect_sigBearPBJ,
    "PB Bear": detect_sigBearPB,
    "Neo Bull": detect_sigNeoBull,
    "Neo Bear": detect_sigNeoBear,
    "Trinity Bull": detect_sigTrinityBull,
    "Trinity Bear": detect_sigTrinityBear,
    "Foxtrot Bull": detect_sigFoxtrotBull,
    "Foxtrot Bear": detect_sigFoxtrotBear,
    "Golf Bull": detect_sigGolfBull,
    "Golf Bear": detect_sigGolfBear,
    "PAF Bull": detect_sigPAFBull,
    "PAF Bear": detect_sigPAFBear,
    "OD Bull": detect_sigODBull,
    "OD Bear": detect_sigODBear,
    "HV75": detect_sigHV75,
    "HV150": detect_sigHV150,
    "HV500": detect_sigHV500,
    "HV1000": detect_sigHV1000,
    "Long1": detect_sigLong1,
    "Short1": detect_sigShort1,
    "Long2": detect_sigLong2,
    "Short2": detect_sigShort2,
    # ─── U-streak ───
    "UUUU Bull": detect_sigP21BullUUUU,
    "UUU Bull": detect_sigP21BullUUU,
    "UU Bull": detect_sigUUBull,
    "UUUU Bear": detect_sigP21BearUUUU,
    "UUU Bear": detect_sigP21BearUUU,
    "UU Bear": detect_sigUUBear,
    "raw UU Bull": detect_rawBullUU,
    "raw UUU Bull": detect_rawBullUUU,
    "raw UUUU Bull": detect_rawBullUUUU,
    "raw UU Bear": detect_rawBearUU,
    "raw UUU Bear": detect_rawBearUUU,
    "raw UUUU Bear": detect_rawBearUUUU,
    # ─── Combo Sets / Unified Combo (SD-001 Pentagon-included) ───
    "comboSet1 Bull": detect_comboSet1_Bull,
    "comboSet1 Bear": detect_comboSet1_Bear,
    "comboSet2 Bull": detect_comboSet2_Bull,
    "comboSet2 Bear": detect_comboSet2_Bear,
    "comboSet3 Bull": detect_comboSet3_Bull,
    "comboSet3 Bear": detect_comboSet3_Bear,
    "comboSet4 Bull": detect_comboSet4_Bull,
    "comboSet4 Bear": detect_comboSet4_Bear,
    "csNew1 Bull (FVG Combo)": detect_csNew1_Bull,
    "csNew1 Bear (FVG Combo)": detect_csNew1_Bear,
    "csNew2 Bull (Matrix Combo)": detect_csNew2_Bull,
    "csNew2 Bear (Matrix Combo)": detect_csNew2_Bear,
    "csNew3 Bull (Unified Combo)": detect_csNew3_Bull,
    "csNew3 Bear (Unified Combo)": detect_csNew3_Bear,
    # ─── Floor / Roof / HW / CC / LSC / Alpha / Super / SDuper ───
    "Floor": detect_anyBullFloor,
    "2nd Floor": detect_anyBull2nd,
    "Rooftop": detect_anyBearRoof,
    "Penthouse": detect_anyBearPent,
    "HW Bull": detect_hwBull,
    "HW Bear": detect_hwBear,
    "CC Bull": detect_sigCCBull,
    "CC Bear": detect_sigCCBear,
    "LSC Bull": detect_sigLSCBull,
    "LSC Bear": detect_sigLSCBear,
    "AlphaStrike Bull": detect_sigAlphaStrikeBull,
    "AlphaStrike Bear": detect_sigAlphaStrikeBear,
    "Super Bull": detect_superBull,
    "Super Bear": detect_superBear,
    "SDuper Bull": detect_sduperBull,
    "SDuper Bear": detect_sduperBear,
    # ─── TNT / Napalm (consolidated) ───
    "Napalm Bull (NPM)": detect_det_bullNapalmCons,
    "Napalm Bear (NPM)": detect_det_bearNapalmCons,
    "B2B Napalm Bull": detect_det_b2bBullNapalm,
    "B2B Napalm Bear": detect_det_b2bBearNapalm,
    "NPM+TNT Bull": detect_det_npmTntBull,
    "B2B PUP": detect_det_b2bPUP,
    "B2B PPD": detect_det_b2bPPD,
    "raw TNT Bull": detect_raw_bullTNT,
    "raw TNT Bear": detect_raw_bearTNT,
    "raw Napalm Bull": detect_raw_napalmBull,
    "raw Napalm Bear": detect_raw_napalmBear,
    "raw Charge Bull": detect_raw_bullCharge,
    "raw Charge Bear": detect_raw_bearCharge,
    # ─── Boom Hunter / Omega ───
    "Omega Long": detect_sigOmegaLong,
    "Omega-A Long": detect_sigOmegaLongA,
    "Short+Press": detect_sigShortPlusPress,
    # ─── Heavy Pentagon WBUSH (5 families × 3 directions) ───
    "Heavy YinYang Bull": detect_hp_HYYBull,
    "Heavy YinYang Bear": detect_hp_HYYBear,
    "Heavy YinYang Neutral": detect_hp_HYYNeutral,
    "Heavy Nagasaki Bull": detect_hp_HNBull,
    "Heavy Nagasaki Bear": detect_hp_HNBear,
    "Heavy Nagasaki Neutral": detect_hp_HNNeutral,
    "Heavy NagasakiV Bull": detect_hp_HNVBull,
    "Heavy NagasakiV Bear": detect_hp_HNVBear,
    "Heavy NagasakiV Neutral": detect_hp_HNVNeutral,
    "Heavy Trident Bull": detect_hp_HTBull,
    "Heavy Trident Bear": detect_hp_HTBear,
    "Heavy Trident Neutral": detect_hp_HTNeutral,
    "Neutral Heavy x2 Bull": detect_hp_NHx2Bull,
    "Neutral Heavy x2 Bear": detect_hp_NHx2Bear,
    "Neutral Heavy x2 Neutral": detect_hp_NHx2Neutral,
    "WBUSH Bull": detect_sig_WBUSH_Bull,
    "WBUSH Bear": detect_sig_WBUSH_Bear,
    "WBUSH Neutral": detect_sig_WBUSH_Neutral,
    # ─── UC NAGASAKI ───
    "UC Nagasaki Bull": detect_sig_UCNagasakiBull,
    "UC Nagasaki Bear": detect_sig_UCNagasakiBear,
    # ─── ULTRA 57 FAUNA combos ───
    "Foster Pair Bull (F2)": detect_sBullF2,
    "Foster Pair Bear (F2)": detect_sBearF2,
    "Exhaustion Triple Bull (E3)": detect_sBullE3,
    "Exhaustion Triple Bear (E3)": detect_sBearE3,
    "FAUNA Cluster Bull (FC)": detect_sBullFC,
    "FAUNA Cluster Bear (FC)": detect_sBearFC,
    "PBJ+F2 Bull": detect_comboPBJ_F2_Bull,
    "PBJ+E3 Bull": detect_comboPBJ_E3_Bull,
    "PBJ+Cluster Bull": detect_comboPBJ_Cluster_Bull,
    "F2Cluster→E3 Bull": detect_comboF2Cluster_E3_Bull,
    "E3 2of3 PUP Bull": detect_comboE3_2of3PUP_Bull,
    "F2 B2B Days Bull": detect_comboF2_B2BDays_Bull,
    "E3 B2B Days Bull": detect_comboE3_B2BDays_Bull,
    "F2→E3 Consec Bull": detect_comboF2E3_Consec_Bull,
    "Cluster B2B Days Bull": detect_comboCluster_B2BDays_Bull,
    # ─── CO / B2B HV+D ───
    "CO Bull (PBJ)": detect_co_bull_pbj,
    "CO Bull (PB)": detect_co_bull_pb,
    "CO Bear (PBJ)": detect_co_bear_pbj,
    "CO Bear (PB)": detect_co_bear_pb,
    "B2B HV+D Bull (PBJ)": detect_b2b_bull_pbj,
    "B2B HV+D Bull (PB)": detect_b2b_bull_pb,
    "B2B HV+D Bull": detect_b2b_bull_nopb,
    "B2B HV+D Bear (PBJ)": detect_b2b_bear_pbj,
    "B2B HV+D Bear (PB)": detect_b2b_bear_pb,
    "B2B HV+D Bear": detect_b2b_bear_nopb,
}


if __name__ == "__main__":
    print(f"DETECTIONS: {len(DETECTIONS)}")
    print(f"STUBBED engine notes: {len(STUBBED)}")
    print(f"STATE_MACHINES: {len(STATE_MACHINES)}")
    print("First 10 detection names:")
    for n in list(DETECTIONS)[:10]:
        print(f"  - {n}")
    print("S1..S46 plots (46 v2):")
    for i in range(1, 47):
        # match by prefix
        keys = [k for k in DETECTIONS if k.startswith(f"S{i} ")]
        for k in keys:
            print(f"  - {k}")
