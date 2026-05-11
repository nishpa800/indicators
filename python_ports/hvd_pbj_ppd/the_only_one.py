"""
Python port of HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine (1767 lines).

Source Pine:  hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine
Audit report: bible-input/agent-reports/hvd-pbj-ppd-delta-the-only-one.md

Re-implements every detection plot in the source as a vectorized pandas
function, suitable for replaying against a bar-history DataFrame.

Conventions:
  - df is expected to have columns: open, high, low, close, volume.
    Index should be a monotonic int (bar index) or DatetimeIndex; bar order
    must be ascending.
  - Each detection function returns a pd.Series[bool] aligned to df.index.
  - IPSF (input.*) parameters live in DEFAULTS and may be overridden via the
    ``params`` dict passed to every detection.
  - Hardcoded Pine constants (NOT input.*) stay hardcoded here so future
    edits do not silently introduce drift.
  - Stateful detections (Combo Chain, LS Chain, AlphaStrike day-tracker,
    Boom Hunter / Omega) are wrapped in classes in STATE_MACHINES.
  - Detections that require Pine-only intrinsics (request.security multi-TF,
    tv_ta.relativeVolume, gz1 array engine, Boom Hunter wavetrend, Ping-Pong
    pivot SR, full PBJ landing-zone state) are STUBBED and registered in
    STUBBED.

This module is import-only safe; it does NOT contain tests. The harness
runs validation tests separately.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

import numpy as np
import pandas as pd

# ============================================================================
# IPSF DEFAULTS — mirror Pine input.* defaults exactly.
# ============================================================================
DEFAULTS: Dict = {
    # PIPELINE A: DISP BASE / HTF1 / HTF2
    "d1_type": "Open to Close",
    "d1_len": 100,
    "d1_mult": 5.0,
    "d2_type": "Open to Close",
    "d2_len": 100,
    "d2_mult": 2.5,
    "d3_type": "Open to Close",
    "d3_len": 100,
    "d3_mult": 1.5,
    # BASE HV bar-bucket toggles
    "ub50": True, "ub75": True, "ub100": True, "ub150": True,
    "ub200": True, "ub250": True, "ub300": True, "ub350": True,
    "ub400": True, "ub450": True, "ub500": True, "ub550": True,
    "ub600": True, "ub650": True, "ub700": True, "ub750": True,
    "ub1000": True, "useHEV": True,
    # HTF1
    "h1On": False, "h1From": "15 Min", "h1To": "2 Hour",
    "uh1_5": True, "uh1_10": True, "uh1_20": True, "uh1_25": True,
    "uh1_30": True, "uh1_40": True, "uh1_50": True, "uh1_60": True,
    "uh1_70": True, "uh1_75": True, "uh1_80": True, "uh1_90": True,
    # HTF2
    "h2On": False, "h2From": "3 Hour", "h2To": "3 Month",
    "uh2_5": True, "uh2_10": True, "uh2_20": True, "uh2_25": True,
    "uh2_30": True, "uh2_40": True, "uh2_50": True, "uh2_60": True,
    "uh2_70": True, "uh2_75": True, "uh2_80": True, "uh2_90": True,
    # USE displacement (engine 3)
    "i_disp_type": "Open to Close", "i_std_len": 100,
    "i_std_min": 3.0, "i_std_max": 100.0, "i_req_fvg": True,
    "i_disp2_type": "Open to Close", "i_disp2_std_len": 100,
    "i_disp2_std_min": 3.0, "i_disp2_std_max": 100.0, "i_disp2_req_fvg": True,
    "i_disp3_type": "Open to Close", "i_disp3_std_len": 100,
    "i_disp3_std_min": 3.0, "i_disp3_std_max": 100.0, "i_disp3_req_fvg": True,
    # GZ1 / HV FVG
    "gz1_auto": True, "gz1_thresh": 2.0, "gz1_dist": 7,
    # HV settings
    "hv150_len": 150,
    # Swingin (Pivot)
    "sw_leftBars": 3, "sw_rightBars": 2,
    "sw_useAtr": True, "sw_atrMult": 2.0, "pp_atr_len": 100,
    # Streak
    "p21_pbj_dist": 4,
    # Opening Drive
    "od_max_bars": 1,
    # Matrix Number
    "neo_len": 67,
    # Momentum 1 / 2
    "ls_reg1": 7.0, "ls_cum1": 3.5, "ls_body1": 0.60,
    "ls_reg2": 5.0, "ls_cum2": 2.5, "ls_body2": 0.75,
    # Combo Set settings
    "cs_bodyPct_FVG": 0.85, "cs_bodyPct_MAT": 0.85,
    "cs_inc_pentagon_FVG": True, "cs_inc_pentagon_MAT": True,
    # Combo Chain
    "cc_min_hits": 2, "cc_window": 2,
    # LS Chain
    "lsc_min_hits": 2, "lsc_window": 2,
    "lsc_reg1": 7.0, "lsc_cum1": 3.5, "lsc_body1": 0.60,
    "lsc_reg2": 5.0, "lsc_cum2": 2.5, "lsc_body2": 0.75,
    # Bar timeframe in seconds (caller supplies; defaults to 60s)
    "tfSec": 60,
    # Pipeline-D / B2B / HV+D & HV+D+PBJ toggles (all default True)
    "en_hvd_bull": True, "en_hvd_bear": True,
    "en_hvd_pb_bull": True, "en_hvd_pb_bear": True,
    "en_hvd_pbj_bull": True, "en_hvd_pbj_bear": True,
    "co_en_bullPBJ": True, "co_en_bullPB": True,
    "co_en_bearPBJ": True, "co_en_bearPB": True,
    "b2b_en_bull": True, "b2b_en_bear": True,
    "b2b_en_bull_pbj": True, "b2b_en_bear_pbj": True,
    "b2b_en_bull_pb": True, "b2b_en_bear_pb": True,
    # USE signal show toggles
    "show_BullUUUU": True, "show_BearUUUU": True,
    "show_BullUUU": True, "show_BearUUU": True,
    "show_BullUU": True, "show_BearUU": True,
    "show_BullUSub": True, "show_BearUSub": True,
    "show_AlphaStrikeB": True, "show_AlphaStrikeR": True,
    "show_FoxtrotB": True, "show_FoxtrotR": True,
    "show_OmegaLong": True,
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


def _series(arr, index) -> pd.Series:
    return pd.Series(arr, index=index)


def _abs(s: pd.Series) -> pd.Series:
    return s.abs()


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


def _shift(s: pd.Series, n: int) -> pd.Series:
    """Pine s[n] equivalent. nz(...) wrapped via fillna(False) at call site."""
    return s.shift(n)


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
    """Pine ``barstate.isconfirmed`` — for historical bars this is True everywhere."""
    return pd.Series(True, index=df.index)


# RVOL threshold tables (lines 444-448 of source)
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


# ============================================================================
# _engines — vectorized building blocks used by many detections.
# Each returns pd.Series; results are *cached on the dataframe* using
# attribute injection (df.attrs) so repeated detection calls are cheap.
# ============================================================================

def _ensure_engines(df: pd.DataFrame, params: Dict) -> Dict[str, pd.Series]:
    """Compute all shared signal series once and cache on df.attrs."""
    cache = df.attrs.setdefault("_hvdppppd_eng", {})
    cache_key = ("v1", id(df), tuple(sorted((k, v) for k, v in params.items() if isinstance(v, (int, float, str, bool)))))
    if cache.get("_key") == cache_key and "sigBullPBJ" in cache:
        return cache
    cache.clear()
    cache["_key"] = cache_key

    p = params
    conf = _conf(df)
    tfSec = float(p["tfSec"])

    # --- PIPELINE A: D1/D2/D3 displacement & FVGs (used downstream) ---
    d1_rng = _disp_range(df, p["d1_type"])
    d1_std = _stdev(d1_rng, p["d1_len"])
    d1_thresh = d1_std * p["d1_mult"]
    d1_prev = d1_rng.shift(1) > d1_thresh.shift(1)
    bull_fvg = _bull_fvg(df)
    bear_fvg = _bear_fvg(df)
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

    # --- BASE HV is/isHEV ranks ---
    vol = df["volume"]
    vsh = vol.shift(1)
    def _is(n):
        return vsh == _highest(vol, n).shift(1)
    is50 = _is(50); is75 = _is(75); is100 = _is(100); is150 = _is(150)
    is200 = _is(200); is250 = _is(250); is300 = _is(300); is350 = _is(350)
    is400 = _is(400); is450 = _is(450); is500 = _is(500); is550 = _is(550)
    is600 = _is(600); is650 = _is(650); is700 = _is(700); is750 = _is(750)
    is1000 = _is(1000)

    # isHEV: streaming all-time-high tracker
    isHEV = pd.Series(False, index=df.index)
    cur_max = -np.inf
    vsh_arr = vsh.to_numpy()
    hev_arr = np.zeros(len(df), dtype=bool)
    for i, v in enumerate(vsh_arr):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            continue
        if v > cur_max:
            cur_max = v
            hev_arr[i] = True
    isHEV = pd.Series(hev_arr, index=df.index)

    def _bool_param(k):
        return bool(p[k])

    # baseRank priority chain
    def _br():
        out = np.zeros(len(df), dtype=int)
        # iterate in priority order — numpy where in descending priority
        # Pine: is1000?1000:is750?750: ... :0
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

    # NOTE: HTF1/HTF2 ranks rely on multi-TF lookups in real Pine via
    # request.security; THE_ONLY_ONE actually computes them on the *current*
    # TF's volume (1-bar lookback). We still need an isH<n> table though.
    def _ish(n): return vsh == _highest(vol, n).shift(1)
    isH5 = _ish(5); isH10 = _ish(10); isH20 = _ish(20); isH25 = _ish(25)
    isH30 = _ish(30); isH40 = _ish(40); isH50 = _ish(50); isH60 = _ish(60)
    isH70 = _ish(70); isH75 = _ish(75); isH80 = _ish(80); isH90 = _ish(90)

    # HTF activation gates by tfSec — we treat htf1Active/htf2Active as input-derived.
    # The TF window-string-to-seconds table (hvd_tf2sec) is reproduced inline.
    def _tf2sec(t: str) -> int:
        return {
            "1 Min": 60, "2 Min": 120, "3 Min": 180, "4 Min": 240, "5 Min": 300,
            "10 Min": 600, "15 Min": 900, "30 Min": 1800,
            "1 Hour": 3600, "2 Hour": 7200, "3 Hour": 10800, "4 Hour": 14400,
            "1 Day": 86400, "2 Day": 172800, "3 Day": 259200,
            "1 Week": 604800, "1 Month": 2592000, "3 Month": 7776000,
        }.get(t, 0)
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

    # --- USE displacement (engine 3) ---
    disp_rng = _disp_range(df, p["i_disp_type"])
    disp_std = _stdev(disp_rng, p["i_std_len"])
    disp_thresh_min = disp_std * p["i_std_min"]
    disp_thresh_max = disp_std * p["i_std_max"]
    disp_prevDisp = (disp_rng.shift(1) > disp_thresh_min.shift(1)) & (disp_rng.shift(1) <= disp_thresh_max.shift(1))
    disp_currDisp = (disp_rng > disp_thresh_min) & (disp_rng <= disp_thresh_max)
    disp_bullFVG = bull_fvg
    disp_bearFVG = bear_fvg
    if bool(p["i_req_fvg"]):
        sigDISPBull = conf & disp_prevDisp & disp_bullFVG
        sigDISPBear = conf & disp_prevDisp & disp_bearFVG
    else:
        sigDISPBull = conf & disp_currDisp & (df["close"] > df["open"])
        sigDISPBear = conf & disp_currDisp & (df["close"] < df["open"])
    disp5_thresh = disp_std * 5.0
    disp5_bull = conf & (disp_std > 0) & (disp_rng > disp5_thresh) & (df["close"] > df["open"])
    disp5_bear = conf & (disp_std > 0) & (disp_rng > disp5_thresh) & (df["close"] < df["open"])

    # Disp 2+
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
    # Streak counters
    def _streak(series: pd.Series) -> pd.Series:
        a = series.fillna(False).to_numpy()
        out = np.zeros(len(a), dtype=int)
        c = 0
        for i, v in enumerate(a):
            c = c + 1 if v else 0
            out[i] = c
        return pd.Series(out, index=series.index)
    disp2_bullStreak = _streak(sigDISP2Bull)
    disp2_bearStreak = _streak(sigDISP2Bear)

    # Disp 3+
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

    # --- RVOL (engine 1) ---
    bb_avgLength = 30
    bb_smaLength = 20
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

    # tv_ta.relativeVolume — we cannot replicate the Pine library here.
    # We expose th_wtc/th_hiroshima but mark sigWTC/sigHiroshima/sigPentagon
    # as STUBBED-via-attrs. Caller may inject `relVolRatio` on df.
    relVolRatio = df.attrs.get("relVolRatio")
    if relVolRatio is None:
        relVolRatio = pd.Series(np.nan, index=df.index)
    sigWTC = conf & (relVolRatio > th_wtc) & (relVolRatio <= th_hiroshima)
    sigHiroshima = conf & (relVolRatio > th_hiroshima)
    sigPentagon = conf & (relVolRatio >= th_1x) & (relVolRatio <= th_wtc)

    # Nagasaki: streaming ATH volume (NOT shifted) per Pine source
    isNagasaki = pd.Series(False, index=df.index)
    cur_max = -np.inf
    nag_arr = np.zeros(len(df), dtype=bool)
    v_arr = df["volume"].to_numpy()
    for i, v in enumerate(v_arr):
        if i == 0:
            cur_max = v if v is not None and not (isinstance(v, float) and np.isnan(v)) else -np.inf
            continue
        if v is not None and v > cur_max:
            nag_arr[i] = True
            cur_max = v
    isNagasaki = pd.Series(nag_arr, index=df.index)
    sigNagasaki = isNagasaki

    # --- Session tracking ---
    # is_new_day requires a day-grouping; if df has DatetimeIndex use it,
    # else assume bar 0 only is "new day" (caller should set day_change boolean
    # via df.attrs["is_new_day"]).
    is_new_day = df.attrs.get("is_new_day")
    if is_new_day is None:
        if isinstance(df.index, pd.DatetimeIndex):
            is_new_day = df.index.normalize() != pd.Series(df.index.normalize(), index=df.index).shift(1)
            is_new_day = pd.Series(is_new_day.to_numpy(), index=df.index).fillna(True)
        else:
            tmp = np.zeros(len(df), dtype=bool); tmp[0] = True
            is_new_day = pd.Series(tmp, index=df.index)
    sessionBarCount = pd.Series(0, index=df.index, dtype=int)
    counter = 0
    nd_arr = is_new_day.to_numpy()
    sb_arr = np.zeros(len(df), dtype=int)
    for i, nd in enumerate(nd_arr):
        if nd:
            counter = 1
        else:
            counter += 1
        sb_arr[i] = counter
    sessionBarCount = pd.Series(sb_arr, index=df.index)

    # --- FAUNA (engine 2) ---
    atr14 = _atr(df, 14)
    fauna_avgVol = _sma(df["volume"], 20)
    fauna_avgBody = _sma((df["close"] - df["open"]).abs(), 20)
    fauna_avgDelta = _sma((df["close"] - df["close"].shift(1)).abs(), 10)
    fauna_trendMA = _sma(df["close"], 50)
    fauna_body = df["close"] - df["open"]
    fauna_rng = df["high"] - df["low"]
    fauna_bodySz = fauna_body.abs()
    fauna_bodyRat = fauna_bodySz / fauna_rng.replace(0, np.nan)
    fauna_bodyRat = fauna_bodyRat.fillna(0.0)
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

    # --- PUP / PPD (engine 5) ---
    pp_barSize = 3.0; pp_lookback = 10
    pp_redVol = df["volume"].where(df["close"] < df["open"], 0.0)
    pp_greenVol = df["volume"].where(df["close"] > df["open"], 0.0)
    pp_hiRedVol = _highest(pp_redVol.shift(1), pp_lookback)
    pp_hiGreenVol = _highest(pp_greenVol.shift(1), pp_lookback)
    pp_priceUp = ((df["close"] - df["open"]) / df["open"]) * 100 > pp_barSize
    pp_priceDn = ((df["open"] - df["close"]) / df["open"]) * 100 > pp_barSize
    sigPUP = conf & pp_priceUp & (df["volume"] > pp_hiRedVol)
    sigPPD = conf & pp_priceDn & (df["volume"] > pp_hiGreenVol)

    # --- PBJ engine (engine 6) — STUBBED in this port (requires Supertrend
    # state machine + landing-zone array). Caller may inject these series
    # via df.attrs["sigBullPBJ"], df.attrs["sigBullPB"], etc. ---
    def _attr_or_false(name):
        s = df.attrs.get(name)
        if s is None:
            return pd.Series(False, index=df.index)
        return s.reindex(df.index).fillna(False).astype(bool)
    sigBullPBJ = _attr_or_false("sigBullPBJ")
    sigBullPB = _attr_or_false("sigBullPB")
    sigBearPBJ = _attr_or_false("sigBearPBJ")
    sigBearPB = _attr_or_false("sigBearPB")

    # --- Ping-Pong SR engine (engine 7) — STUBBED (state arrays + lines). ---
    bull_pp = _attr_or_false("bull_pp")
    bear_pp = _attr_or_false("bear_pp")

    # --- GZ1 engine (engine 4) — STUBBED. ---
    gz_bullGZI = _attr_or_false("gz_bullGZI")
    gz_bearGZI = _attr_or_false("gz_bearGZI")
    gz_bullHV = _attr_or_false("gz_bullHV")
    gz_bearHV = _attr_or_false("gz_bearHV")

    # --- P21 / UU engine (engine 8) ---
    p21_qual_bull = conf & bb_baseBullish & (bb_normalizedPrice >= 2.0)
    p21_qual_bear = conf & bb_baseBearish & (bb_normalizedPrice >= 2.0)
    def _streak_sum(qual: pd.Series, value: pd.Series):
        a = qual.fillna(False).to_numpy(); v = value.fillna(0.0).to_numpy()
        s = np.zeros(len(a), dtype=int); accum = np.zeros(len(a))
        c = 0; sm = 0.0
        for i, b in enumerate(a):
            if b:
                c += 1; sm += v[i]
            else:
                c = 0; sm = 0.0
            s[i] = c; accum[i] = sm
        return pd.Series(s, index=qual.index), pd.Series(accum, index=qual.index)
    p21_bull_streak, p21_bull_sum = _streak_sum(p21_qual_bull, bb_normalizedPrice)
    p21_bear_streak, p21_bear_sum = _streak_sum(p21_qual_bear, bb_normalizedPrice)

    rawBullUU = conf & (p21_bull_streak == 2)
    rawBullUUU = conf & (p21_bull_streak == 3)
    rawBullUUUU = conf & (p21_bull_streak >= 4)
    rawBearUU = conf & (p21_bear_streak == 2)
    rawBearUUU = conf & (p21_bear_streak == 3)
    rawBearUUUU = conf & (p21_bear_streak >= 4)

    # 4U
    u4_qual_bull = conf & (df["close"] > df["open"])
    u4_qual_bear = conf & (df["close"] < df["open"])
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
    u4_bull_streak, u4_bull_hasDay1 = _streak_with_day1(u4_qual_bull, is_new_day)
    u4_bear_streak, u4_bear_hasDay1 = _streak_with_day1(u4_qual_bear, is_new_day)

    def _scan_any(streak: pd.Series, n: int, source: pd.Series) -> pd.Series:
        """For each bar with streak>=n, return True if source[i..i-(n-1)] has any True."""
        st = streak.to_numpy()
        sa = _nz_b(source).to_numpy()
        out = np.zeros(len(st), dtype=bool)
        for i in range(len(st)):
            if st[i] >= n:
                lo = max(0, i - (n - 1))
                if sa[lo:i + 1].any():
                    out[i] = True
        return pd.Series(out, index=streak.index)

    u4_pbj_bull = _scan_any(u4_bull_streak, 4, sigBullPBJ)
    u4_pbj_bear = _scan_any(u4_bear_streak, 4, sigBearPBJ)
    u4_disp_bull = _scan_any(u4_bull_streak, 4, sigDISPBull)
    u4_disp_bear = _scan_any(u4_bear_streak, 4, sigDISPBear)
    sigP21BullUUUU = conf & (u4_bull_streak >= 4) & u4_bull_hasDay1 & u4_pbj_bull & u4_disp_bull
    sigP21BearUUUU = conf & (u4_bear_streak >= 4) & u4_bear_hasDay1 & u4_pbj_bear & u4_disp_bear

    # 3U
    u3_qual_bull = conf & bb_baseBullish & (bb_normalizedPrice > 1.0)
    u3_qual_bear = conf & bb_baseBearish & (bb_normalizedPrice > 1.0)
    u3_bull_streak, u3_bull_hasDay1 = _streak_with_day1(u3_qual_bull, is_new_day)
    u3_bear_streak, u3_bear_hasDay1 = _streak_with_day1(u3_qual_bear, is_new_day)
    u3_pbj_bull = _scan_any(u3_bull_streak, 3, sigBullPBJ)
    u3_pbj_bear = _scan_any(u3_bear_streak, 3, sigBearPBJ)
    u3_disp_bull = _scan_any(u3_bull_streak, 3, sigDISPBull)
    u3_disp_bear = _scan_any(u3_bear_streak, 3, sigDISPBear)
    sigP21BullUUU = conf & (u3_bull_streak >= 3) & u3_bull_hasDay1 & u3_pbj_bull & u3_disp_bull
    sigP21BearUUU = conf & (u3_bear_streak >= 3) & u3_bear_hasDay1 & u3_pbj_bear & u3_disp_bear

    # 2U (UU)
    uu_disp_bull = sigDISPBull | _nz_b(sigDISPBull.shift(1))
    uu_disp_bear = sigDISPBear | _nz_b(sigDISPBear.shift(1))
    uu_pbj_bull = sigBullPBJ | _nz_b(sigBullPBJ.shift(1))
    uu_pbj_bear = sigBearPBJ | _nz_b(sigBearPBJ.shift(1))
    uu_excA_bull = (sessionBarCount <= 2) & disp5_bull & _nz_b(disp5_bull.shift(1))
    uu_excA_bear = (sessionBarCount <= 2) & disp5_bear & _nz_b(disp5_bear.shift(1))
    uu_excC_bull = sigPUP & _nz_b(sigPUP.shift(1)) & uu_disp_bull
    uu_excC_bear = sigPPD & _nz_b(sigPPD.shift(1)) & uu_disp_bear
    sigUUBull = conf & (p21_bull_streak == 2) & (p21_bull_sum >= th_1x) & ((uu_pbj_bull & uu_disp_bull) | uu_excA_bull | uu_excC_bull)
    sigUUBear = conf & (p21_bear_streak == 2) & (p21_bear_sum >= th_1x) & ((uu_pbj_bear & uu_disp_bear) | uu_excA_bear | uu_excC_bear)

    # U-Sub
    def _scan_min(streak: pd.Series, source: pd.Series, cap: int) -> pd.Series:
        st = streak.to_numpy(); sa = _nz_b(source).to_numpy()
        out = np.zeros(len(st), dtype=bool)
        for i in range(len(st)):
            if st[i] >= 3:
                n = min(int(st[i]) - 1, cap) + 1
                lo = max(0, i - (n - 1))
                if sa[lo:i + 1].any():
                    out[i] = True
        return pd.Series(out, index=streak.index)
    p21_pbj_sub_bull = _scan_min(p21_bull_streak, sigBullPBJ, 3)
    p21_pbj_sub_bear = _scan_min(p21_bear_streak, sigBearPBJ, 3)
    usub_disp_bull = _scan_min(p21_bull_streak, sigDISPBull, 3)
    usub_disp_bear = _scan_min(p21_bear_streak, sigDISPBear, 3)
    sigUSubBull = conf & (p21_bull_streak >= 3) & (p21_bull_sum >= th_1x) & p21_pbj_sub_bull & usub_disp_bull
    sigUSubBear = conf & (p21_bear_streak >= 3) & (p21_bear_sum >= th_1x) & p21_pbj_sub_bear & usub_disp_bear

    # Matrix Number / Neo / Trinity
    is_matrix_number = df["volume"] == _highest(df["volume"], int(p["neo_len"]))
    sigNeoBull = conf & is_matrix_number & sigFAUNABull
    sigNeoBear = conf & is_matrix_number & sigFAUNABear
    sigTrinityBull = conf & is_matrix_number & ~sigFAUNABull & (df["close"] > df["open"])
    sigTrinityBear = conf & is_matrix_number & ~sigFAUNABear & (df["close"] < df["open"])

    # FoxTrot
    sigFoxtrotBull = conf & sigFAUNABull & _nz_b(sigFAUNABull.shift(1)) & _nz_b(sigFAUNABull.shift(2)) & _nz_b(sigFAUNABull.shift(3))
    sigFoxtrotBear = conf & sigFAUNABear & _nz_b(sigFAUNABear.shift(1)) & _nz_b(sigFAUNABear.shift(2)) & _nz_b(sigFAUNABear.shift(3))

    # Long/Short (engine 11) — STUBBED: requires tv_ta.relativeVolume(reg)+(cum)
    ls_regRatio = df.attrs.get("ls_regRatio", pd.Series(np.nan, index=df.index))
    ls_cumRatio = df.attrs.get("ls_cumRatio", pd.Series(np.nan, index=df.index))
    ls_bodyRat = ((df["close"] - df["open"]).abs() / (df["high"] - df["low"]).replace(0, np.nan)).fillna(0.0)
    sigLong1 = conf & (ls_regRatio > p["ls_reg1"]) & (ls_cumRatio > p["ls_cum1"]) & (df["close"] > df["open"]) & (ls_bodyRat >= p["ls_body1"])
    sigShort1 = conf & (ls_regRatio > p["ls_reg1"]) & (ls_cumRatio > p["ls_cum1"]) & (df["close"] < df["open"]) & (ls_bodyRat >= p["ls_body1"])
    sigLong2 = conf & (ls_regRatio > p["ls_reg2"]) & (ls_cumRatio > p["ls_cum2"]) & (df["close"] > df["open"]) & (ls_bodyRat >= p["ls_body2"])
    sigShort2 = conf & (ls_regRatio > p["ls_reg2"]) & (ls_cumRatio > p["ls_cum2"]) & (df["close"] < df["open"]) & (ls_bodyRat >= p["ls_body2"])

    # Combo Sets
    cs_bp1 = ((df["close"].shift(1) - df["open"].shift(1)).abs() /
              (df["high"].shift(1) - df["low"].shift(1)).replace(0, np.nan)).fillna(0.0)
    cs_vb = cs_bp1 >= p["cs_bodyPct_FVG"]
    comboSet1_Bull = conf & cs_vb & (gz_bullHV | gz_bullGZI) & (_nz_b(sigSAAB.shift(1)) | _nz_b(sigBullRVOL1x.shift(1)) | _nz_b(sigGrandSlam.shift(1)))
    comboSet1_Bear = conf & cs_vb & (gz_bearHV | gz_bearGZI) & (_nz_b(sigKratos.shift(1)) | _nz_b(sigBearRVOL1x.shift(1)) | _nz_b(sigMOAB.shift(1)))
    pent_b1 = bool(p["cs_inc_pentagon_FVG"]) and True
    comboSet2_Bull = conf & cs_vb & (gz_bullHV | gz_bullGZI) & (
        ((sigPentagon.shift(1) if pent_b1 else pd.Series(False, index=df.index)).fillna(False).astype(bool)) |
        _nz_b(sigWTC.shift(1)) | _nz_b(sigHiroshima.shift(1)) | _nz_b(sigNagasaki.shift(1)))
    comboSet2_Bear = conf & cs_vb & (gz_bearHV | gz_bearGZI) & (
        ((sigPentagon.shift(1) if pent_b1 else pd.Series(False, index=df.index)).fillna(False).astype(bool)) |
        _nz_b(sigWTC.shift(1)) | _nz_b(sigHiroshima.shift(1)) | _nz_b(sigNagasaki.shift(1)))
    cs_vm = ls_bodyRat >= p["cs_bodyPct_MAT"]
    matrix_any_bull = sigNeoBull | sigTrinityBull | (sigNeoBull & (sigLong1 | sigLong2)) | (sigTrinityBull & (sigLong1 | sigLong2))
    matrix_any_bear = sigNeoBear | sigTrinityBear | (sigNeoBear & (sigShort1 | sigShort2)) | (sigTrinityBear & (sigShort1 | sigShort2))
    comboSet3_Bull = cs_vm & matrix_any_bull & (sigSAAB | sigBullRVOL1x | sigGrandSlam)
    comboSet3_Bear = cs_vm & matrix_any_bear & (sigKratos | sigBearRVOL1x | sigMOAB)
    pent_b2 = bool(p["cs_inc_pentagon_MAT"])
    comboSet4_Bull = cs_vm & matrix_any_bull & (
        ((sigPentagon if pent_b2 else pd.Series(False, index=df.index)).astype(bool)) |
        sigWTC | sigHiroshima | sigNagasaki)
    comboSet4_Bear = cs_vm & matrix_any_bear & (
        ((sigPentagon if pent_b2 else pd.Series(False, index=df.index)).astype(bool)) |
        sigWTC | sigHiroshima | sigNagasaki)
    csNew1_Bull = comboSet1_Bull | comboSet2_Bull
    csNew1_Bear = comboSet1_Bear | comboSet2_Bear
    csNew2_Bull = comboSet3_Bull | comboSet4_Bull
    csNew2_Bear = comboSet3_Bear | comboSet4_Bear
    # NB: drift here — THE_ONLY_ONE uses same-bar AND, NOT csNew2.shift(1).
    csNew3_Bull = csNew1_Bull & csNew2_Bull
    csNew3_Bear = csNew1_Bear & csNew2_Bear

    # Floor / Roof / 2F / Pent
    nag_dir_bull = sigBullRVOL1x | sigGrandSlam | sigFAUNABull | sigDISPBull | sigBullPBJ | sigPUP | gz_bullHV | gz_bullGZI
    nag_dir_bear = sigBearRVOL1x | sigMOAB | sigFAUNABear | sigDISPBear | sigBearPBJ | sigPPD | gz_bearHV | gz_bearGZI
    bull_hw_slot = sigBullRVOL1x | sigGrandSlam | sigWTC | sigHiroshima | (sigNagasaki & nag_dir_bull)
    bear_hw_slot = sigBearRVOL1x | sigMOAB | sigWTC | sigHiroshima | (sigNagasaki & nag_dir_bear)
    anyBullFloor = conf & bull_pp & sigBullPBJ & bull_hw_slot
    anyBull2nd = conf & bull_pp & sigBullPB & bull_hw_slot
    anyBearRoof = conf & bear_pp & sigBearPBJ & bear_hw_slot
    anyBearPent = conf & bear_pp & sigBearPB & bear_hw_slot

    # HW
    hwBull = (df["close"] > df["open"]) & disp5_bull & sigBullPBJ & (sigGrandSlam | sigWTC | sigHiroshima | (sigNagasaki & nag_dir_bull)) & (anyBullFloor | anyBull2nd)
    hwBear = (df["close"] < df["open"]) & disp5_bear & sigBearPBJ & (sigMOAB | sigWTC | sigHiroshima | (sigNagasaki & nag_dir_bear)) & (anyBearRoof | anyBearPent)

    # Super / SD
    super_hw_bull = sigBullRVOL1x | sigGrandSlam | sigWTC | sigHiroshima | sigNagasaki
    super_hw_bear = sigBearRVOL1x | sigMOAB | sigWTC | sigHiroshima | sigNagasaki
    super_comboAny_bull = csNew1_Bull | csNew2_Bull
    super_comboAny_bear = csNew1_Bear | csNew2_Bear
    superBull = conf & sigBullPBJ & sigDISPBull & (sigFAUNABull | sigLong1) & super_hw_bull & ((super_comboAny_bull & sigPUP) | (anyBullFloor | anyBull2nd))
    superBear = conf & sigBearPBJ & sigDISPBear & (sigFAUNABear | sigShort1) & super_hw_bear & ((super_comboAny_bear & sigPPD) | (anyBearRoof | anyBearPent))
    sduperBull = conf & (anyBullFloor | anyBull2nd) & sigBullPBJ & super_hw_bull & super_comboAny_bull & sigPUP & sigDISPBull & (sigFAUNABull | sigLong1)
    sduperBear = conf & (anyBearRoof | anyBearPent) & sigBearPBJ & super_hw_bear & super_comboAny_bear & sigPPD & sigDISPBear & (sigFAUNABear | sigShort1)

    # OD
    od_fvg_bull = gz_bullGZI | comboSet1_Bull | comboSet2_Bull | comboSet3_Bull | comboSet4_Bull
    od_fvg_bear = gz_bearGZI | comboSet1_Bear | comboSet2_Bear | comboSet3_Bear | comboSet4_Bear
    sigODBull = conf & (sessionBarCount <= int(p["od_max_bars"])) & od_fvg_bull & disp_prevDisp & sigPUP & sigBullPBJ
    sigODBear = conf & (sessionBarCount <= int(p["od_max_bars"])) & od_fvg_bear & disp_prevDisp & sigPPD & sigBearPBJ

    # HV size flags
    sigHV75 = conf & (df["volume"] >= _highest(df["volume"], 75).shift(1))
    sigHV150 = conf & (df["volume"] >= _highest(df["volume"], int(p["hv150_len"])).shift(1))
    sigHV500 = conf & (df["volume"] >= _highest(df["volume"], 500).shift(1))
    sigHV1000 = conf & (df["volume"] >= _highest(df["volume"], 1000).shift(1))

    # Golf / PAF
    sigGolfBull = conf & sigDISPBull & _nz_b(sigFAUNABull.shift(1)) & _nz_b(sigPUP.shift(1)) & _nz_b(sigDISPBull.shift(1)) & _nz_b(sigFAUNABull.shift(2)) & _nz_b(sigPUP.shift(2))
    sigGolfBear = conf & sigDISPBear & _nz_b(sigFAUNABear.shift(1)) & _nz_b(sigPPD.shift(1)) & _nz_b(sigDISPBear.shift(1)) & _nz_b(sigFAUNABear.shift(2)) & _nz_b(sigPPD.shift(2))
    sigPAFBull = conf & sigPUP & sigFAUNABull & _nz_b(sigPUP.shift(1)) & _nz_b(sigFAUNABull.shift(1))
    sigPAFBear = conf & sigPPD & sigFAUNABear & _nz_b(sigPPD.shift(1)) & _nz_b(sigFAUNABear.shift(1))

    # DispCons2/3 — uses current sigFAUNA (drift point relative to siblings)
    sigDispConsBull2 = sigDISP2Bull & (disp2_bullStreak >= 2) & sigFAUNABull & _nz_b(sigFAUNABull.shift(1))
    sigDispConsBear2 = sigDISP2Bear & (disp2_bearStreak >= 2) & sigFAUNABear & _nz_b(sigFAUNABear.shift(1))
    sigDispConsBull3 = sigDISP3Bull & (disp3_bullStreak >= 3) & sigFAUNABull & _nz_b(sigFAUNABull.shift(1)) & _nz_b(sigFAUNABull.shift(2))
    sigDispConsBear3 = sigDISP3Bear & (disp3_bearStreak >= 3) & sigFAUNABear & _nz_b(sigFAUNABear.shift(1)) & _nz_b(sigFAUNABear.shift(2))

    # Combo Chain (CC) — stateful; computed bar-by-bar
    cc_min_hits = int(p["cc_min_hits"])
    cc_window = int(p["cc_window"])
    def _cc_active(comboSet1, comboSet2, comboSet3, comboSet4, sigPBJ_a, sigPB_a):
        c1 = _nz_b(comboSet1).to_numpy()
        c2 = _nz_b(comboSet2).to_numpy()
        c3 = _nz_b(comboSet3).to_numpy()
        c4 = _nz_b(comboSet4).to_numpy()
        pj = _nz_b(sigPBJ_a).to_numpy()
        pb = _nz_b(sigPB_a).to_numpy()
        out = np.zeros(len(c1), dtype=bool)
        active = False
        for i in range(len(c1)):
            win = 0
            seen_pbj = False
            for k in range(cc_window):
                idx = i - k
                if idx < 0:
                    continue
                hv2 = c3[idx] or c4[idx]
                if k >= 1:
                    if c1[idx - 1 if idx - 1 >= 0 else idx] or c2[idx - 1 if idx - 1 >= 0 else idx]:
                        hv2 = True
                if hv2:
                    win += 1
                if pj[idx] or pb[idx]:
                    seen_pbj = True
            if not (c3[i] or c4[i]):
                active = False
            elif not active and win >= cc_min_hits and seen_pbj:
                active = True
            out[i] = active
        return pd.Series(out, index=df.index)
    cc_bull_active = _cc_active(comboSet1_Bull, comboSet2_Bull, comboSet3_Bull, comboSet4_Bull, sigBullPBJ, sigBullPB)
    cc_bear_active = _cc_active(comboSet1_Bear, comboSet2_Bear, comboSet3_Bear, comboSet4_Bear, sigBearPBJ, sigBearPB)
    sigCCBull = conf & cc_bull_active
    sigCCBear = conf & cc_bear_active

    # LS Chain
    lsc_L1 = conf & (ls_regRatio > p["lsc_reg1"]) & (ls_cumRatio > p["lsc_cum1"]) & (df["close"] > df["open"]) & (ls_bodyRat >= p["lsc_body1"])
    lsc_S1 = conf & (ls_regRatio > p["lsc_reg1"]) & (ls_cumRatio > p["lsc_cum1"]) & (df["close"] < df["open"]) & (ls_bodyRat >= p["lsc_body1"])
    lsc_L2 = conf & (ls_regRatio > p["lsc_reg2"]) & (ls_cumRatio > p["lsc_cum2"]) & (df["close"] > df["open"]) & (ls_bodyRat >= p["lsc_body2"])
    lsc_S2 = conf & (ls_regRatio > p["lsc_reg2"]) & (ls_cumRatio > p["lsc_cum2"]) & (df["close"] < df["open"]) & (ls_bodyRat >= p["lsc_body2"])
    lsc_min_hits = int(p["lsc_min_hits"])
    lsc_window = int(p["lsc_window"])
    def _lsc_active(L1, L2, sigPBJ_a, sigPB_a):
        a1 = _nz_b(L1).to_numpy(); a2 = _nz_b(L2).to_numpy()
        pj = _nz_b(sigPBJ_a).to_numpy(); pb = _nz_b(sigPB_a).to_numpy()
        out = np.zeros(len(a1), dtype=bool); active = False
        for i in range(len(a1)):
            wb = 0; seen = False
            for k in range(lsc_window):
                idx = i - k
                if idx < 0:
                    continue
                if a1[idx] or a2[idx]:
                    wb += 1
                if pj[idx] or pb[idx]:
                    seen = True
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

    # AlphaStrike day-tracker — firstOfDay turns False after any "big" detection
    # fires that day. We compute it after we know all the components; rather
    # than re-running, mark True until first day-detection then False.
    big_bull = (sigP21BullUUUU | sigP21BearUUUU | sigP21BullUUU | sigP21BearUUU |
                sigUUBull | sigUUBear | sigUSubBull | sigUSubBear |
                # alpha (not yet) | foxtrot | omega | OD | dispCons | csNew | floor/2nd/roof/pent | hw | super | sduper | cc | lsc | golf | paf
                sigFoxtrotBull | sigFoxtrotBear | sigODBull | sigODBear |
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

    # AlphaStrike (THE_ONLY_ONE flavor: includes (sigBullPBJ or sigBullPB))
    as_fauna_bull = sigFAUNABull | sigLong1 | sigDISPBull | sigPUP | sigWTC | sigHiroshima | sigNagasaki
    as_fauna_bear = sigFAUNABear | sigShort1 | sigDISPBear | sigPPD | sigWTC | sigHiroshima | sigNagasaki
    sigAlphaStrikeBull = conf & firstOfDay & bull_pp & (sigGrandSlam | sigBullRVOL1x) & (sigBullPBJ | sigBullPB) & as_fauna_bull
    sigAlphaStrikeBear = conf & firstOfDay & bear_pp & (sigMOAB | sigBearRVOL1x) & (sigBearPBJ | sigBearPB) & as_fauna_bear

    # Boom Hunter / Omega — STUBBED. Caller may inject sigOmegaLong / sigShortPlusPress.
    sigOmegaLong = _attr_or_false("sigOmegaLong")
    sigShortPlusPress = _attr_or_false("sigShortPlusPress")

    # ─── PIPELINE C: fire_* outputs (gated by show_*) ───
    def _g(name, sig):
        return sig & bool(p.get(f"show_{name}", True))

    fire = {
        "fire_BullUUUU": _g("BullUUUU", sigP21BullUUUU),
        "fire_BullUUU": _g("BullUUU", sigP21BullUUU),
        "fire_BullUU": _g("BullUU", sigUUBull),
        "fire_BullUSub": _g("BullUSub", sigUSubBull),
        "fire_AlphaStrikeB": _g("AlphaStrikeB", sigAlphaStrikeBull),
        "fire_FoxtrotB": _g("FoxtrotB", sigFoxtrotBull),
        "fire_OmegaLong": _g("OmegaLong", sigOmegaLong),
        "fire_ODBull": _g("ODBull", sigODBull),
        "fire_DispConsBull2": _g("DispConsBull2", sigDispConsBull2),
        "fire_DispConsBull3": _g("DispConsBull3", sigDispConsBull3),
        "fire_GolfBull": _g("GolfBull", sigGolfBull),
        "fire_PAFBull": _g("PAFBull", sigPAFBull),
        "fire_CS1B": _g("CS1B", csNew1_Bull),
        "fire_CS2B": _g("CS2B", csNew2_Bull),
        "fire_CS3B": _g("CS3B", csNew3_Bull),
        "fire_CCBull": _g("CCBull", sigCCBull),
        "fire_LSCBull": _g("LSCBull", sigLSCBull),
        "fire_BullFloor": _g("BullFloor", anyBullFloor),
        "fire_Bull2ndFloor": _g("Bull2ndFloor", anyBull2nd),
        "fire_HWBull": _g("HWBull", hwBull),
        "fire_SuperBull": _g("SuperBull", superBull),
        "fire_SDuperBull": _g("SDuperBull", sduperBull),
        "fire_BearUUUU": _g("BearUUUU", sigP21BearUUUU),
        "fire_BearUUU": _g("BearUUU", sigP21BearUUU),
        "fire_BearUU": _g("BearUU", sigUUBear),
        "fire_BearUSub": _g("BearUSub", sigUSubBear),
        "fire_AlphaStrikeR": _g("AlphaStrikeR", sigAlphaStrikeBear),
        "fire_FoxtrotR": _g("FoxtrotR", sigFoxtrotBear),
        "fire_ODBear": _g("ODBear", sigODBear),
        "fire_DispConsBear2": _g("DispConsBear2", sigDispConsBear2),
        "fire_DispConsBear3": _g("DispConsBear3", sigDispConsBear3),
        "fire_GolfBear": _g("GolfBear", sigGolfBear),
        "fire_PAFBear": _g("PAFBear", sigPAFBear),
        "fire_CS1R": _g("CS1R", csNew1_Bear),
        "fire_CS2R": _g("CS2R", csNew2_Bear),
        "fire_CS3R": _g("CS3R", csNew3_Bear),
        "fire_CCBear": _g("CCBear", sigCCBear),
        "fire_LSCBear": _g("LSCBear", sigLSCBear),
        "fire_BearRooftop": _g("BearRooftop", anyBearRoof),
        "fire_BearPent": _g("BearPenthouse", anyBearPent),
        "fire_HWBear": _g("HWBear", hwBear),
        "fire_SuperBear": _g("SuperBear", superBear),
        "fire_SDuperBear": _g("SDuperBear", sduperBear),
    }

    # Pipeline B: HV+D + PB / PBJ co-occurrence (gated)
    hvd_pb_bull = hvd_fire_bull & _nz_b(sigBullPB.shift(1))
    hvd_pbj_bull = hvd_fire_bull & _nz_b(sigBullPBJ.shift(1))
    hvd_pb_bear = hvd_fire_bear & _nz_b(sigBearPB.shift(1))
    hvd_pbj_bear = hvd_fire_bear & _nz_b(sigBearPBJ.shift(1))

    # Pipeline D: USE-any + triple AND
    use_any_bull = (sigP21BullUUUU | sigP21BullUUU | sigUUBull | sigUSubBull |
                    sigAlphaStrikeBull | sigFoxtrotBull | sigOmegaLong | sigODBull |
                    sigDispConsBull2 | sigDispConsBull3 | sigGolfBull | sigPAFBull |
                    csNew1_Bull | csNew2_Bull | csNew3_Bull | sigCCBull | sigLSCBull |
                    anyBullFloor | anyBull2nd | hwBull | superBull | sduperBull)
    use_any_bear = (sigP21BearUUUU | sigP21BearUUU | sigUUBear | sigUSubBear |
                    sigAlphaStrikeBear | sigFoxtrotBear | sigODBear |
                    sigDispConsBear2 | sigDispConsBear3 | sigGolfBear | sigPAFBear |
                    csNew1_Bear | csNew2_Bear | csNew3_Bear | sigCCBear | sigLSCBear |
                    anyBearRoof | anyBearPent | hwBear | superBear | sduperBear)
    co_bull_pbj = hvd_fire_bull & bool(p["co_en_bullPBJ"]) & _nz_b(sigBullPBJ.shift(1)) & _nz_b(use_any_bull.shift(1))
    co_bull_pb = hvd_fire_bull & bool(p["co_en_bullPB"]) & _nz_b(sigBullPB.shift(1)) & _nz_b(use_any_bull.shift(1))
    co_bear_pbj = hvd_fire_bear & bool(p["co_en_bearPBJ"]) & _nz_b(sigBearPBJ.shift(1)) & _nz_b(use_any_bear.shift(1))
    co_bear_pb = hvd_fire_bear & bool(p["co_en_bearPB"]) & _nz_b(sigBearPB.shift(1)) & _nz_b(use_any_bear.shift(1))
    co_any = co_bull_pbj | co_bull_pb | co_bear_pbj | co_bear_pb

    # B2B HV+D
    b2b_bull_raw = hvd_fire_bull & _nz_b(hvd_fire_bull.shift(1))
    b2b_bear_raw = hvd_fire_bear & _nz_b(hvd_fire_bear.shift(1))
    b2b_bull_pbj = b2b_bull_raw & (_nz_b(sigBullPBJ.shift(1)) | _nz_b(sigBullPBJ.shift(2)))
    b2b_bear_pbj = b2b_bear_raw & (_nz_b(sigBearPBJ.shift(1)) | _nz_b(sigBearPBJ.shift(2)))
    b2b_bull_pb = b2b_bull_raw & (_nz_b(sigBullPB.shift(1)) | _nz_b(sigBullPB.shift(2))) & ~b2b_bull_pbj
    b2b_bear_pb = b2b_bear_raw & (_nz_b(sigBearPB.shift(1)) | _nz_b(sigBearPB.shift(2))) & ~b2b_bear_pbj
    b2b_bull_nopb = b2b_bull_raw & ~b2b_bull_pbj & ~b2b_bull_pb
    b2b_bear_nopb = b2b_bear_raw & ~b2b_bear_pbj & ~b2b_bear_pb

    cache.update({
        # Pipeline A
        "hvd_fire_bull": hvd_fire_bull, "hvd_fire_bear": hvd_fire_bear,
        # Pipeline B
        "sigBullPBJ": sigBullPBJ, "sigBullPB": sigBullPB,
        "sigBearPBJ": sigBearPBJ, "sigBearPB": sigBearPB,
        "hvd_pb_bull": hvd_pb_bull, "hvd_pbj_bull": hvd_pbj_bull,
        "hvd_pb_bear": hvd_pb_bear, "hvd_pbj_bear": hvd_pbj_bear,
        # Pipeline C engines
        "sigDISPBull": sigDISPBull, "sigDISPBear": sigDISPBear,
        "disp5_bull": disp5_bull, "disp5_bear": disp5_bear,
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
        "sigP21BullUUUU": sigP21BullUUUU, "sigP21BearUUUU": sigP21BearUUUU,
        "sigP21BullUUU": sigP21BullUUU, "sigP21BearUUU": sigP21BearUUU,
        "sigUUBull": sigUUBull, "sigUUBear": sigUUBear,
        "sigUSubBull": sigUSubBull, "sigUSubBear": sigUSubBear,
        "sigFoxtrotBull": sigFoxtrotBull, "sigFoxtrotBear": sigFoxtrotBear,
        "sigODBull": sigODBull, "sigODBear": sigODBear,
        "sigGolfBull": sigGolfBull, "sigGolfBear": sigGolfBear,
        "sigPAFBull": sigPAFBull, "sigPAFBear": sigPAFBear,
        "sigCCBull": sigCCBull, "sigCCBear": sigCCBear,
        "sigLSCBull": sigLSCBull, "sigLSCBear": sigLSCBear,
        "sigAlphaStrikeBull": sigAlphaStrikeBull, "sigAlphaStrikeBear": sigAlphaStrikeBear,
        "sigOmegaLong": sigOmegaLong, "sigShortPlusPress": sigShortPlusPress,
        "comboSet1_Bull": comboSet1_Bull, "comboSet1_Bear": comboSet1_Bear,
        "comboSet2_Bull": comboSet2_Bull, "comboSet2_Bear": comboSet2_Bear,
        "comboSet3_Bull": comboSet3_Bull, "comboSet3_Bear": comboSet3_Bear,
        "comboSet4_Bull": comboSet4_Bull, "comboSet4_Bear": comboSet4_Bear,
        "csNew1_Bull": csNew1_Bull, "csNew1_Bear": csNew1_Bear,
        "csNew2_Bull": csNew2_Bull, "csNew2_Bear": csNew2_Bear,
        "csNew3_Bull": csNew3_Bull, "csNew3_Bear": csNew3_Bear,
        "anyBullFloor": anyBullFloor, "anyBull2nd": anyBull2nd,
        "anyBearRoof": anyBearRoof, "anyBearPent": anyBearPent,
        "hwBull": hwBull, "hwBear": hwBear,
        "superBull": superBull, "superBear": superBear,
        "sduperBull": sduperBull, "sduperBear": sduperBear,
        "bull_pp": bull_pp, "bear_pp": bear_pp,
        # Pipeline D + B2B
        "co_bull_pbj": co_bull_pbj, "co_bull_pb": co_bull_pb,
        "co_bear_pbj": co_bear_pbj, "co_bear_pb": co_bear_pb,
        "co_any": co_any,
        "use_any_bull": use_any_bull, "use_any_bear": use_any_bear,
        "b2b_bull_raw": b2b_bull_raw, "b2b_bear_raw": b2b_bear_raw,
        "b2b_bull_pbj": b2b_bull_pbj, "b2b_bear_pbj": b2b_bear_pbj,
        "b2b_bull_pb": b2b_bull_pb, "b2b_bear_pb": b2b_bear_pb,
        "b2b_bull_nopb": b2b_bull_nopb, "b2b_bear_nopb": b2b_bear_nopb,
        # Fire dict
        **fire,
    })
    return cache


# ============================================================================
# Public detection functions — every plot in THE_ONLY_ONE.pine has one.
# ============================================================================

def _wrap(name: str) -> Callable[[pd.DataFrame, Optional[Dict]], pd.Series]:
    def _fn(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
        eng = _ensure_engines(df, _p(params))
        s = eng[name]
        # Pipeline-A and Pipeline-D plots are drawn at offset=-1 in Pine,
        # i.e. the fire on bar N describes bar N-1. Detection-plot consumers
        # typically want "did this plot land on bar X?" — for offset=-1 plots
        # we shift +0 here (pure fire bar) and let the validator align on its
        # own. Keeping offset semantics in this output preserves drift checks.
        return s.fillna(False).astype(bool)
    _fn.__name__ = f"detect_{name}"
    return _fn


# ─── HV+D (Pipeline A) ───
detect_hvd_bull = _wrap("hvd_fire_bull")
detect_hvd_bear = _wrap("hvd_fire_bear")
# ─── HV+D + PBJ / PB (Pipeline A x B) ───
detect_pb_bull = _wrap("hvd_pb_bull")
detect_pb_bear = _wrap("hvd_pb_bear")
detect_pbj_bull = _wrap("hvd_pbj_bull")
detect_pbj_bear = _wrap("hvd_pbj_bear")
# ─── USE Bull plots ───
detect_BullUUUU = _wrap("fire_BullUUUU")
detect_BullUUU = _wrap("fire_BullUUU")
detect_BullUU = _wrap("fire_BullUU")
detect_BullUSub = _wrap("fire_BullUSub")
detect_AlphaStrikeBull = _wrap("fire_AlphaStrikeB")
detect_FoxtrotBull = _wrap("fire_FoxtrotB")
detect_OmegaLong = _wrap("fire_OmegaLong")
detect_ODBull = _wrap("fire_ODBull")
detect_DispConsBull2 = _wrap("fire_DispConsBull2")
detect_DispConsBull3 = _wrap("fire_DispConsBull3")
detect_GolfBull = _wrap("fire_GolfBull")
detect_PAFBull = _wrap("fire_PAFBull")
detect_CS1B = _wrap("fire_CS1B")
detect_CS2B = _wrap("fire_CS2B")
detect_CS3B = _wrap("fire_CS3B")
detect_CCBull = _wrap("fire_CCBull")
detect_LSCBull = _wrap("fire_LSCBull")
detect_BullFloor = _wrap("fire_BullFloor")
detect_Bull2ndFloor = _wrap("fire_Bull2ndFloor")
detect_HWBull = _wrap("fire_HWBull")
detect_SuperBull = _wrap("fire_SuperBull")
detect_SDuperBull = _wrap("fire_SDuperBull")
# ─── USE Bear plots ───
detect_BearUUUU = _wrap("fire_BearUUUU")
detect_BearUUU = _wrap("fire_BearUUU")
detect_BearUU = _wrap("fire_BearUU")
detect_BearUSub = _wrap("fire_BearUSub")
detect_AlphaStrikeBear = _wrap("fire_AlphaStrikeR")
detect_FoxtrotBear = _wrap("fire_FoxtrotR")
detect_ODBear = _wrap("fire_ODBear")
detect_DispConsBear2 = _wrap("fire_DispConsBear2")
detect_DispConsBear3 = _wrap("fire_DispConsBear3")
detect_GolfBear = _wrap("fire_GolfBear")
detect_PAFBear = _wrap("fire_PAFBear")
detect_CS1R = _wrap("fire_CS1R")
detect_CS2R = _wrap("fire_CS2R")
detect_CS3R = _wrap("fire_CS3R")
detect_CCBear = _wrap("fire_CCBear")
detect_LSCBear = _wrap("fire_LSCBear")
detect_BearRooftop = _wrap("fire_BearRooftop")
detect_BearPent = _wrap("fire_BearPent")
detect_HWBear = _wrap("fire_HWBear")
detect_SuperBear = _wrap("fire_SuperBear")
detect_SDuperBear = _wrap("fire_SDuperBear")
# ─── Pipeline D (CO triple-AND) ───
detect_co_bull_pbj = _wrap("co_bull_pbj")
detect_co_bull_pb = _wrap("co_bull_pb")
detect_co_bear_pbj = _wrap("co_bear_pbj")
detect_co_bear_pb = _wrap("co_bear_pb")
# ─── Back-to-Back HV+D ───
detect_b2b_bull_nopb = _wrap("b2b_bull_nopb")
detect_b2b_bull_pbj = _wrap("b2b_bull_pbj")
detect_b2b_bull_pb = _wrap("b2b_bull_pb")
detect_b2b_bear_nopb = _wrap("b2b_bear_nopb")
detect_b2b_bear_pbj = _wrap("b2b_bear_pbj")
detect_b2b_bear_pb = _wrap("b2b_bear_pb")


# ============================================================================
# Stubbed detections — Pine-only intrinsics required.
# Keys are detection names; values list the Pine intrinsics needed.
# Caller may inject pre-computed series via df.attrs[<name>].
# ============================================================================
STUBBED: Dict[str, str] = {
    # tv_ta.relativeVolume (regular + cumulative). Inject via df.attrs:
    #   relVolRatio (regular ratio)
    #   ls_regRatio, ls_cumRatio (engine 11 long/short)
    "_rel_vol_engine": "tv_ta.relativeVolume not reproduced; inject relVolRatio/ls_regRatio/ls_cumRatio via df.attrs",
    # PBJ engine: full landing-zone state machine + Supertrend dir-flips.
    # Inject via df.attrs: sigBullPBJ, sigBullPB, sigBearPBJ, sigBearPB.
    "_pbj_engine": "PBJ landing-zone array + Supertrend dir requires bar-by-bar state; inject via df.attrs",
    # Ping-Pong SR engine: pivot levels with line objects, regime tracking.
    # Inject bull_pp / bear_pp via df.attrs.
    "_pp_engine": "Ping-Pong SR pivots not reproduced; inject bull_pp/bear_pp via df.attrs",
    # GZ1/HV FVG engine: array of fvg_struct + per-bar removal.
    # Inject gz_bullGZI, gz_bearGZI, gz_bullHV, gz_bearHV via df.attrs.
    "_gz_engine": "GZ1 FVG structs not reproduced; inject gz_bullGZI/gz_bearGZI/gz_bullHV/gz_bearHV",
    # Boom Hunter / Omega — Ehlers filter chain + wavetrend pivots.
    # Inject sigOmegaLong / sigShortPlusPress via df.attrs.
    "_bh_engine": "Boom Hunter filter chain not reproduced; inject sigOmegaLong/sigShortPlusPress",
    # Multi-TF HV (htf1/htf2) currently treated as same-TF lookup; real Pine
    # uses request.security on h1From/h1To windows.
    "_htf_security": "htf1/htf2 use current TF volume; real Pine uses request.security",
}


# ============================================================================
# State machines — exposed for the harness; they read from df.attrs.
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


STATE_MACHINES: Dict[str, type] = {
    "ComboChain": ComboChainState,
    "LSChain": LSChainState,
    "FirstOfDay": FirstOfDayState,
}


# ============================================================================
# DETECTIONS registry — name → detect_* function.
# Names mirror Pine plot identifiers (text/title) so the harness can
# round-trip with the validator.
# ============================================================================
DETECTIONS: Dict[str, Callable] = {
    # Pipeline A
    "HV+D Bull": detect_hvd_bull,
    "HV+D Bear": detect_hvd_bear,
    # Pipeline A x B
    "PB Bull": detect_pb_bull,
    "PB Bear": detect_pb_bear,
    "PBJ Bull": detect_pbj_bull,
    "PBJ Bear": detect_pbj_bear,
    # USE Bull
    "Bull UUUU": detect_BullUUUU,
    "Bull UUU": detect_BullUUU,
    "Bull UU": detect_BullUU,
    "Bull U-Sub": detect_BullUSub,
    "AlphaStrike Bull": detect_AlphaStrikeBull,
    "Foxtrot Bull": detect_FoxtrotBull,
    "Omega Long": detect_OmegaLong,
    "OD Bull": detect_ODBull,
    "DispCons Bull 2": detect_DispConsBull2,
    "DispCons Bull 3": detect_DispConsBull3,
    "Golf Bull": detect_GolfBull,
    "PAF Bull": detect_PAFBull,
    "CS1 FVG Bull": detect_CS1B,
    "CS2 MAT Bull": detect_CS2B,
    "Combo Bull (CS3)": detect_CS3B,
    "CC Bull": detect_CCBull,
    "LSC Bull": detect_LSCBull,
    "Floor": detect_BullFloor,
    "2nd Floor": detect_Bull2ndFloor,
    "HW Bull": detect_HWBull,
    "Super Bull": detect_SuperBull,
    "SDuper Bull": detect_SDuperBull,
    # USE Bear
    "Bear UUUU": detect_BearUUUU,
    "Bear UUU": detect_BearUUU,
    "Bear UU": detect_BearUU,
    "Bear D-Sub": detect_BearUSub,
    "AlphaStrike Bear": detect_AlphaStrikeBear,
    "Foxtrot Bear": detect_FoxtrotBear,
    "OD Bear": detect_ODBear,
    "DispCons Bear 2": detect_DispConsBear2,
    "DispCons Bear 3": detect_DispConsBear3,
    "Golf Bear": detect_GolfBear,
    "PAF Bear": detect_PAFBear,
    "CS1 FVG Bear": detect_CS1R,
    "CS2 MAT Bear": detect_CS2R,
    "Combo Bear (CS3)": detect_CS3R,
    "CC Bear": detect_CCBear,
    "LSC Bear": detect_LSCBear,
    "Rooftop": detect_BearRooftop,
    "Penthouse": detect_BearPent,
    "HW Bear": detect_HWBear,
    "Super Bear": detect_SuperBear,
    "SDuper Bear": detect_SDuperBear,
    # Pipeline D: CO triple-AND
    "CO HV+D+PBJ+USE Bull": detect_co_bull_pbj,
    "CO HV+D+PB+USE Bull": detect_co_bull_pb,
    "CO HV+D+PBJ+USE Bear": detect_co_bear_pbj,
    "CO HV+D+PB+USE Bear": detect_co_bear_pb,
    # B2B HV+D
    "B2B HV+D Bull": detect_b2b_bull_nopb,
    "B2B HV+D+PBJ Bull": detect_b2b_bull_pbj,
    "B2B HV+D+PB Bull": detect_b2b_bull_pb,
    "B2B HV+D Bear": detect_b2b_bear_nopb,
    "B2B HV+D+PBJ Bear": detect_b2b_bear_pbj,
    "B2B HV+D+PB Bear": detect_b2b_bear_pb,
}


if __name__ == "__main__":
    print(f"DETECTIONS: {len(DETECTIONS)}")
    print(f"STUBBED engine notes: {len(STUBBED)}")
    print(f"STATE_MACHINES: {len(STATE_MACHINES)}")
    print("First 5 detection names:")
    for n in list(DETECTIONS)[:5]:
        print("  ", n)
