"""
Python port of TNT_OD_v3.pine (2150 lines) — the TRUE v3 (per VETTING.md).

Source Pine: tnt-od/versions/TNT_OD_v3.pine

Status: PENDING Anish vet per tnt-od/VETTING.md. ``LATEST.txt`` still points
at the v2-internal snapshot (``TNT_Opening_Drive_OD_v3_2026-05-04.pine``),
which is ported in ``canonical_v2_per_latest.py``. This v3 port mirrors
that file and ADDS the v3-only features:

  - Conditional gate (en_newGate; 6 atoms: RVOL1x, GrandSlam, UC, Nagasaki+Any,
    HCT, gate_disp). When ON, gates the NPM-family Tier 1 + all Tier 2 plots.
  - T1 RELAY (Bull/Bear) — visual on bar[2] AND bar[1], same direction.
  - T1 STACK (Bull/Bear) — ≥ 2 distinct Tier-1 visuals on bar[1], same
    direction.
  - Five distinct displacement engines (Main / DYNAMITE / USE V5 / HCT / Gate).
  - Inline-ported HCT engine (separate RVOL thresholds; dispCandleMet + FVG
    threshold; baseAny over 5 sub-bases).
  - Inline UC engine (≥ 2 distinct from {FAUNA, RVOL tier, WMD, PUP/PPD, CS1}).

Same Pine-only-intrinsic injection points as the v2 port (see STUBBED).

Conventions (mirror hvd_pbj_ppd/the_only_one.py):
  - df has columns: open, high, low, close, volume.
  - Each detection returns a pd.Series[bool] aligned to df.index.
  - IPSF defaults preserved in DEFAULTS (SD-003).
  - Stateful detections built into _ensure_engines bar-by-bar.
  - Upstream raw signals (TNT zones, Napalm, CONT, PBJ, WBUSH, etc.) stubbed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd


# Module-level engine cache keyed by id(df). Kept off ``df.attrs`` to avoid
# pandas' pd.concat ``__finalize__`` comparing attrs (which contain Series
# values) and raising "truth value of a Series is ambiguous".
_ENGINE_CACHE: Dict[int, Dict] = {}


# ============================================================================
# IPSF DEFAULTS — mirror Pine input.* defaults exactly (SD-003).
# ============================================================================
DEFAULTS: Dict = {
    # --- Master alert toggles ---
    "masterFirstBar": True,
    "masterAggregate": True,

    # --- Engine (grpE) ---
    "SENS": 100,
    "SWING_LEN": 10,
    "DISP_TYPE": "Open to Close",
    "DISP_STD_LEN": 100,
    "DISP_STD_X": 5,
    "RET_TNT_PCT": 100.0,
    "RET_SUPER_PCT": 50.0,
    "SUDDEN_PROX": 3,

    # --- DYNAMITE-only displacement engine (grpDyn) ---
    "dynStdMult": 5.0,

    # --- Tier 1 toggles (grpT1) ---
    "en_b2bBull": True, "en_b2bBear": True,
    "en_rcNTBull": True, "en_rcNTBear": True,
    "en_fuseBull": True, "en_fuseBear": True,
    "en_catBull": True, "en_catBear": True,
    "en_pnBull": True, "en_pnBear": True,
    "en_ptBull": True, "en_ptBear": True,
    "en_ignBull": True, "en_ignBear": True,
    "en_dynBull": True, "en_dynBear": True,

    # --- Tier 2 toggles (grpT2) ---
    "en_t2tntBull": True, "en_t2tntBear": True,
    "en_t2npmBull": True, "en_t2npmBear": True,
    "en_t2contBull": True, "en_t2contBear": True,
    "en_t2trBull": True, "en_t2trBear": True,
    "en_t2rnBull": True, "en_t2rnBear": True,
    "en_t2prBull": True, "en_t2prBear": True,

    # --- Density (grpD1/D2/D3) ---
    "den1_X": 2, "den1_Y": 2,
    "den2_X": 3, "den2_Y": 3,
    "den3_X": 2, "den3_Y": 6,
    "en_d1b": True, "en_d1s": True,
    "en_d2b": True, "en_d2s": True,
    "en_d3b": True, "en_d3s": True,

    # --- UU/UUU/UUUU (grpU) ---
    "en_uu_bull": True, "en_uu_bear": True,
    "en_uuu_bull": True, "en_uuu_bear": True,
    "en_uuuu_bull": True, "en_uuuu_bear": True,

    # --- WBUSH (grpWB) ---
    "en_wbushBull": True, "en_wbushBear": True, "en_wbushNeutral": True,

    # --- USE V5 (grpU5) ---
    "u5_std_len": 100,
    "u5_std_min": 3.0,
    "u5_od_max_bars": 1,

    # --- v3 NEW: Conditional gate (grpGate) ---
    "en_newGate": True,
    "gateStdMult": 6.5,

    # --- v3 NEW: HCT (grpHCT) ---
    "hct_disp_strength": 6.0,
    "hct_disp_lookback": 100,
    "hct_threshPct": 2.0,
    "hct_auto": True,

    # --- Bar timeframe in seconds ---
    "tfSec": 60,

    # --- Alerts ---
    "en_nagAlert": False,

    # --- Zones (informational) ---
    "maxZones": 30,
    "maxSuperZones": 30,
}


# ============================================================================
# _helpers
# ============================================================================
def _p(params: Optional[Dict]) -> Dict:
    out = dict(DEFAULTS)
    if params:
        out.update(params)
    return out


def _conf(df: pd.DataFrame) -> pd.Series:
    return pd.Series(True, index=df.index)


def _nz_b(s: pd.Series) -> pd.Series:
    return s.fillna(False).astype(bool)


def _nz_f(s: pd.Series, fill: float = 0.0) -> pd.Series:
    return s.fillna(fill)


def _highest(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=1).max()


def _sma(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=length).mean()


def _stdev(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=length).std(ddof=0)


def _atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([(h - l), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / length, adjust=False, min_periods=length).mean()


def _bull_fvg(df: pd.DataFrame) -> pd.Series:
    return (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["open"].shift(1))


def _bear_fvg(df: pd.DataFrame) -> pd.Series:
    return (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["open"].shift(1))


def _disp_range(df: pd.DataFrame, kind: str) -> pd.Series:
    if kind == "Open to Close":
        return (df["open"] - df["close"]).abs()
    return df["high"] - df["low"]


def _streak(series: pd.Series) -> pd.Series:
    a = series.fillna(False).to_numpy()
    out = np.zeros(len(a), dtype=int)
    c = 0
    for i, v in enumerate(a):
        c = c + 1 if v else 0
        out[i] = c
    return pd.Series(out, index=series.index)


# --- USE V5 RVOL thresholds (same as v2 LATEST u5_*) ---
def _u5_1x(tfsec: float) -> float:
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


def _u5_gs(tfsec: float) -> float:
    s = tfsec
    if s < 60: return _u5_1x(s) * 3.0
    if s <= 300: return 35.0
    if s <= 600: return 25.0
    if s <= 1500: return 20.0
    if s <= 3000: return 20.0
    if s <= 7260: return 10.0
    if s <= 11700: return 8.0
    if s <= 86400: return 7.5
    if s <= 259200: return 3.5
    return 3.0


def _u5_saab(tfsec: float) -> float:
    return _u5_1x(tfsec) * 0.56


def _u5_wtc(tfsec: float) -> float:
    return _u5_1x(tfsec) * 2.0


def _u5_hiro(tfsec: float) -> float:
    s = tfsec
    if s < 60: return _u5_1x(s) * 3.0
    if s <= 300: return 35.0
    if s <= 600: return 25.0
    if s <= 1500: return 25.0
    if s <= 3060: return 20.0
    if s <= 7260: return 10.0
    if s <= 11700: return 8.0
    if s <= 86400: return 7.5
    if s <= 259200: return 5.0
    return 3.5


# --- v3 NEW: HCT threshold tables (different from u5_*) ---
def _hct_1x(tfsec: float) -> float:
    s = tfsec
    if s <= 10: return 38.0
    if s <= 15: return 33.0
    if s <= 30: return 28.0
    if s <= 45: return 23.0
    if s <= 60: return 20.0
    if s <= 120: return 19.0
    if s <= 180: return 17.0
    if s <= 240: return 16.0
    if s <= 300: return 15.0
    if s <= 360: return 14.0
    if s <= 420: return 12.0
    if s <= 480: return 11.0
    if s <= 540: return 10.0
    if s <= 600: return 10.0
    if s <= 900: return 8.4
    if s <= 1800: return 6.9
    if s <= 3600: return 5.9
    if s <= 7200: return 3.0
    return 1.8


def _hct_saab(tfsec: float) -> float:
    return _hct_1x(tfsec) * 0.56


def _hct_gs(tfsec: float) -> float:
    s = tfsec
    if s <= 10: return 114.0
    if s <= 15: return 99.0
    if s <= 30: return 84.0
    if s <= 45: return 69.0
    if s <= 60: return 35.0
    if s <= 300: return 35.0
    if s <= 600: return 25.0
    if s <= 900: return 20.0
    if s <= 3600: return 10.0
    return 8.0


def _hct_wtc(tfsec: float) -> float:
    return _hct_1x(tfsec) * 2.0


def _hct_hiro(tfsec: float) -> float:
    return _hct_gs(tfsec)


# ============================================================================
# _ensure_engines
# ============================================================================
def _attr_or_false(df: pd.DataFrame, name: str) -> pd.Series:
    s = df.attrs.get(name)
    if s is None:
        return pd.Series(False, index=df.index)
    return s.reindex(df.index).fillna(False).astype(bool)


def _ensure_engines(df: pd.DataFrame, params: Dict) -> Dict[str, pd.Series]:
    cache = _ENGINE_CACHE.setdefault(id(df), {})
    cache_key = ("v3", id(df),
                 tuple(sorted((k, v) for k, v in params.items()
                              if isinstance(v, (int, float, str, bool)))))
    if cache.get("_key") == cache_key and "p_t1RelayBull" in cache:
        return cache
    cache.clear()
    cache["_key"] = cache_key

    p = params
    conf = _conf(df)
    n = len(df)
    tfSec = float(p["tfSec"])

    # ------------------------------------------------------------------
    # Raw upstream (STUBBED — inject via df.attrs).
    # ------------------------------------------------------------------
    det_bullTNT = _attr_or_false(df, "det_bullTNT")
    det_bearTNT = _attr_or_false(df, "det_bearTNT")
    det_bullNapalm = _attr_or_false(df, "det_bullNapalm")
    det_bearNapalm = _attr_or_false(df, "det_bearNapalm")
    det_bullRetTNT = _attr_or_false(df, "det_bullRetTNT")
    det_bearRetTNT = _attr_or_false(df, "det_bearRetTNT")
    det_contBull = _attr_or_false(df, "det_contBull")
    det_contBear = _attr_or_false(df, "det_contBear")
    det_pbjBull = _attr_or_false(df, "det_pbjBull")
    det_pbjBear = _attr_or_false(df, "det_pbjBear")
    sig_WBUSH_Bull = _attr_or_false(df, "sig_WBUSH_Bull")
    sig_WBUSH_Bear = _attr_or_false(df, "sig_WBUSH_Bear")
    sig_WBUSH_Neutral = _attr_or_false(df, "sig_WBUSH_Neutral")
    det_cs1_Bull = _attr_or_false(df, "det_cs1_Bull")
    det_cs1_Bear = _attr_or_false(df, "det_cs1_Bear")

    # Session first-bar
    if isinstance(df.index, pd.DatetimeIndex):
        norm = pd.Series(df.index.normalize(), index=df.index)
        is_new_day = (norm != norm.shift(1))
        is_new_day.iloc[0] = True
    else:
        is_new_day_attr = df.attrs.get("is_new_day")
        if is_new_day_attr is not None:
            is_new_day = is_new_day_attr.reindex(df.index).fillna(False).astype(bool)
        else:
            is_new_day = pd.Series(False, index=df.index)
            is_new_day.iloc[0] = True
    nd_arr = is_new_day.to_numpy()
    bar_idx = np.arange(n)
    session_first_bar = np.zeros(n, dtype=int)
    sess_first = 0
    for i, nd in enumerate(nd_arr):
        if nd:
            sess_first = i
        session_first_bar[i] = sess_first
    sessionFirstBarIdx = pd.Series(session_first_bar, index=df.index)
    bar_idx_s = pd.Series(bar_idx, index=df.index)

    # ------------------------------------------------------------------
    # Engine #1: Main displacement (disp_range, disp_std, disp_threshold).
    # ------------------------------------------------------------------
    disp_range = _disp_range(df, p["DISP_TYPE"])
    disp_std = _stdev(disp_range, int(p["DISP_STD_LEN"]))
    disp_threshold = disp_std * float(p["DISP_STD_X"])
    isBullishFVG = (df["low"] > df["high"].shift(2)) & (df["open"].shift(1) < df["close"].shift(1))
    isBearishFVG = (df["high"] < df["low"].shift(2)) & (df["open"].shift(1) > df["close"].shift(1))
    prevBarDisplaced = disp_range.shift(1) > disp_threshold.shift(1)
    dispSignal = prevBarDisplaced & (isBullishFVG | isBearishFVG)

    # ------------------------------------------------------------------
    # Engine #3: USE V5 (same as v2 LATEST u5_* block).
    # ------------------------------------------------------------------
    u5_bb_avgLen = 30
    u5_bb_smaLen = 20
    u5_bb_spike = (df["close"] - df["open"]).abs()
    u5_bb_avgSpikeDenom = _sma(u5_bb_spike, u5_bb_avgLen).shift(1)
    u5_bb_normPrice = u5_bb_spike / _nz_f(u5_bb_avgSpikeDenom, 1.0)
    u5_bb_avgVolDenom = _sma(df["volume"], u5_bb_avgLen).shift(1)
    u5_bb_normVol = df["volume"] / _nz_f(u5_bb_avgVolDenom, 1.0)
    u5_bb_diff = u5_bb_normPrice - u5_bb_normVol
    u5_bb_posDiff = u5_bb_diff.where(u5_bb_diff > 0, np.nan)
    u5_bb_smaDiff = _sma(u5_bb_posDiff, u5_bb_smaLen)
    u5_bb_baseBull = (df["close"] > df["open"]) & (u5_bb_posDiff > u5_bb_smaDiff)
    u5_bb_baseBear = (df["close"] < df["open"]) & (u5_bb_posDiff > u5_bb_smaDiff)

    u5_th_saab = _u5_saab(tfSec)
    u5_th_1x = _u5_1x(tfSec)
    u5_th_gs = _u5_gs(tfSec)
    u5_th_wtc = _u5_wtc(tfSec)
    u5_th_hiro = _u5_hiro(tfSec)

    def _between(s, lo, hi):
        return (s >= lo) & (s < hi)

    u5_SAAB = conf & u5_bb_baseBull & _between(u5_bb_normPrice, u5_th_saab, u5_th_1x)
    u5_Kratos = conf & u5_bb_baseBear & _between(u5_bb_normPrice, u5_th_saab, u5_th_1x)
    u5_GrandSlam = conf & u5_bb_baseBull & (u5_bb_normPrice >= u5_th_gs)
    u5_MOAB = conf & u5_bb_baseBear & (u5_bb_normPrice >= u5_th_gs)
    u5_RVOL1xB = conf & u5_bb_baseBull & _between(u5_bb_normPrice, u5_th_1x, u5_th_gs) & ~u5_GrandSlam
    u5_RVOL1xR = conf & u5_bb_baseBear & _between(u5_bb_normPrice, u5_th_1x, u5_th_gs) & ~u5_MOAB

    u5_relVolRatio = df.attrs.get("u5_relVolRatio")
    if u5_relVolRatio is None:
        u5_relVolRatio = pd.Series(np.nan, index=df.index)
    u5_WTC = conf & (u5_relVolRatio > u5_th_wtc) & (u5_relVolRatio <= u5_th_hiro)
    u5_Hiroshima = conf & (u5_relVolRatio > u5_th_hiro)
    u5_Pentagon = conf & (u5_relVolRatio >= u5_th_1x) & (u5_relVolRatio <= u5_th_wtc)

    # Nagasaki — streaming ATH volume
    nag_arr = np.zeros(n, dtype=bool)
    cur_max = -np.inf
    v_arr = df["volume"].to_numpy()
    for i, v in enumerate(v_arr):
        if i == 0:
            cur_max = v if v is not None and not (isinstance(v, float) and np.isnan(v)) else -np.inf
            continue
        if v is not None and v > cur_max:
            nag_arr[i] = True
            cur_max = v
    u5_Nagasaki = pd.Series(nag_arr, index=df.index)
    u5_WMD = u5_Pentagon | u5_WTC | u5_Hiroshima | u5_Nagasaki
    u5_HV1000 = conf & (df["volume"] >= _highest(df["volume"], 1000).shift(1))

    # FAUNA (USE V5)
    ATR14 = _atr(df, 14)
    u5_f_avgVol = _sma(df["volume"], 20)
    u5_f_avgBody = _sma((df["close"] - df["open"]).abs(), 20)
    u5_f_avgDelta = _sma((df["close"] - df["close"].shift(1)).abs(), 10)
    u5_f_trendMA = _sma(df["close"], 50)
    u5_f_body = df["close"] - df["open"]
    u5_f_rng = df["high"] - df["low"]
    u5_f_bodySz = u5_f_body.abs()
    u5_f_bodyRat = (u5_f_bodySz / u5_f_rng.replace(0, np.nan)).fillna(0.0)
    u5_f_up = u5_f_body > 0
    u5_f_dn = u5_f_body < 0
    u5_f_prev_body = df["close"].shift(1) - df["open"].shift(1)
    u5_f_prev_range = df["high"].shift(1) - df["low"].shift(1)
    u5_MB_b = u5_f_up & (u5_f_bodySz > 1.6 * ATR14) & (u5_f_bodyRat > 0.70) & (df["volume"] > 1.8 * u5_f_avgVol)
    u5_RE_b = u5_f_up & (u5_f_rng > 2.2 * ATR14) & ((df["high"] - df["close"]) < 0.15 * u5_f_rng) & (df["volume"] > 1.8 * u5_f_avgVol)
    u5_TA_b = (u5_f_trendMA > u5_f_trendMA.shift(1)) & ((df["close"] - df["close"].shift(1)) > 1.6 * u5_f_avgDelta) & u5_f_up & (df["volume"] > 1.8 * u5_f_avgVol)
    u5_GG_b = ((df["open"] - df["close"].shift(1)) > 0.9 * ATR14) & u5_f_up & (df["low"] > df["close"].shift(1)) & (df["volume"] > 1.8 * u5_f_avgVol)
    u5_StrongBear = (df["close"].shift(1) < df["open"].shift(1)) & (u5_f_prev_body.abs() > 1.5 * u5_f_avgBody.shift(1)) & (df["volume"].shift(1) > 1.5 * u5_f_avgVol.shift(1))
    u5_WeakBear = (df["close"].shift(1) < df["open"].shift(1)) & ((u5_f_prev_body.abs() / u5_f_prev_range.replace(0, np.nan)).fillna(0.0) <= 0.2)
    u5_TR_b = u5_WeakBear & (u5_MB_b | u5_RE_b | u5_TA_b)
    u5_ES_b = u5_StrongBear & (u5_MB_b | u5_RE_b | u5_TA_b)
    u5_GDR_b = (df["close"].shift(1) < df["open"].shift(1)) & u5_GG_b
    u5_b_core = u5_MB_b.astype(int) + u5_RE_b.astype(int) + u5_TA_b.astype(int)
    u5_b_gg_exc = u5_GG_b & ~((u5_b_core >= 2) & (u5_f_bodyRat >= 0.80))
    u5_FAUNABull = conf & (u5_MB_b | u5_RE_b | u5_TA_b) & ~(u5_TR_b | u5_ES_b | u5_GDR_b | u5_b_gg_exc)
    u5_MB_r = u5_f_dn & (u5_f_bodySz > 1.6 * ATR14) & (u5_f_bodyRat > 0.70) & (df["volume"] > 1.8 * u5_f_avgVol)
    u5_RE_r = u5_f_dn & (u5_f_rng > 2.2 * ATR14) & ((df["close"] - df["low"]) < 0.15 * u5_f_rng) & (df["volume"] > 1.8 * u5_f_avgVol)
    u5_TA_r = (u5_f_trendMA < u5_f_trendMA.shift(1)) & ((df["close"].shift(1) - df["close"]) > 1.6 * u5_f_avgDelta) & u5_f_dn & (df["volume"] > 1.8 * u5_f_avgVol)
    u5_GG_r = ((df["close"].shift(1) - df["open"]) > 0.9 * ATR14) & u5_f_dn & (df["high"] < df["close"].shift(1)) & (df["volume"] > 1.8 * u5_f_avgVol)
    u5_StrongBull = (df["close"].shift(1) > df["open"].shift(1)) & (u5_f_prev_body.abs() > 1.5 * u5_f_avgBody.shift(1)) & (df["volume"].shift(1) > 1.5 * u5_f_avgVol.shift(1))
    u5_WeakBull = (df["close"].shift(1) > df["open"].shift(1)) & ((u5_f_prev_body.abs() / u5_f_prev_range.replace(0, np.nan)).fillna(0.0) <= 0.2)
    u5_TR_r = u5_WeakBull & (u5_MB_r | u5_RE_r | u5_TA_r)
    u5_ES_r = u5_StrongBull & (u5_MB_r | u5_RE_r | u5_TA_r)
    u5_GDR_r = (df["close"].shift(1) > df["open"].shift(1)) & u5_GG_r
    u5_s_core = u5_MB_r.astype(int) + u5_RE_r.astype(int) + u5_TA_r.astype(int)
    u5_s_gg_exc = u5_GG_r & ~((u5_s_core >= 2) & (u5_f_bodyRat >= 0.80))
    u5_FAUNABear = conf & (u5_MB_r | u5_RE_r | u5_TA_r) & ~(u5_TR_r | u5_ES_r | u5_GDR_r | u5_s_gg_exc)

    # u5 DISP / PUP / PPD
    u5_disp_rng = (df["open"] - df["close"]).abs()
    u5_disp_std = _stdev(u5_disp_rng, int(p["u5_std_len"]))
    u5_disp_thresh_min = u5_disp_std * float(p["u5_std_min"])
    u5_disp_bullFVG = (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["open"].shift(1))
    u5_disp_bearFVG = (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["open"].shift(1))
    u5_DISPBull = conf & (u5_disp_rng.shift(1) > u5_disp_thresh_min.shift(1)) & u5_disp_bullFVG
    u5_DISPBear = conf & (u5_disp_rng.shift(1) > u5_disp_thresh_min.shift(1)) & u5_disp_bearFVG

    u5_pp_redVol = df["volume"].where(df["close"] < df["open"], 0.0)
    u5_pp_greenVol = df["volume"].where(df["close"] > df["open"], 0.0)
    u5_pp_hiRedVol = _highest(u5_pp_redVol.shift(1), 10)
    u5_pp_hiGreenVol = _highest(u5_pp_greenVol.shift(1), 10)
    u5_PUP = conf & (((df["close"] - df["open"]) / df["open"]) * 100 > 3.0) & (df["volume"] > u5_pp_hiRedVol)
    u5_PPD = conf & (((df["open"] - df["close"]) / df["open"]) * 100 > 3.0) & (df["volume"] > u5_pp_hiGreenVol)

    u5_CS1_Bull = det_cs1_Bull
    u5_CS1_Bear = det_cs1_Bear

    # ------------------------------------------------------------------
    # Engine #2: DYNAMITE-only displacement (uses dynStdMult).
    # ------------------------------------------------------------------
    dyn_thresh = disp_std * float(p["dynStdMult"])
    dyn_disp_b1 = disp_range.shift(1) > dyn_thresh.shift(1)
    dyn_disp_b2 = disp_range.shift(2) > dyn_thresh.shift(2)
    bull_b1 = df["close"].shift(1) > df["open"].shift(1)
    bull_b2 = df["close"].shift(2) > df["open"].shift(2)
    bear_b1 = df["close"].shift(1) < df["open"].shift(1)
    bear_b2 = df["close"].shift(2) < df["open"].shift(2)
    bull_fvg = _bull_fvg(df)
    bear_fvg = _bear_fvg(df)
    fauna_bull_b1 = _nz_b(u5_FAUNABull.shift(1))
    fauna_bull_b2 = _nz_b(u5_FAUNABull.shift(2))
    fauna_bear_b1 = _nz_b(u5_FAUNABear.shift(1))
    fauna_bear_b2 = _nz_b(u5_FAUNABear.shift(2))
    det_dynamiteBull = conf & dyn_disp_b1 & dyn_disp_b2 & bull_b1 & bull_b2 & fauna_bull_b1 & fauna_bull_b2 & bull_fvg
    det_dynamiteBear = conf & dyn_disp_b1 & dyn_disp_b2 & bear_b1 & bear_b2 & fauna_bear_b1 & fauna_bear_b2 & bear_fvg

    # ------------------------------------------------------------------
    # Engine #4: HCT (inline-ported; separate thresholds + FVG threshold).
    # ------------------------------------------------------------------
    hct_th_saab = _hct_saab(tfSec)
    hct_th_1x = _hct_1x(tfSec)
    hct_th_gs = _hct_gs(tfSec)
    hct_th_wtc = _hct_wtc(tfSec)
    hct_th_hiro = _hct_hiro(tfSec)

    hct_SAAB = u5_bb_baseBull & _between(u5_bb_normPrice, hct_th_saab, hct_th_1x)
    hct_Kratos = u5_bb_baseBear & _between(u5_bb_normPrice, hct_th_saab, hct_th_1x)
    hct_BullRVOL1x = u5_bb_baseBull & _between(u5_bb_normPrice, hct_th_1x, hct_th_gs)
    hct_BearRVOL1x = u5_bb_baseBear & _between(u5_bb_normPrice, hct_th_1x, hct_th_gs)
    hct_GrandSlam = u5_bb_baseBull & (u5_bb_normPrice >= hct_th_gs)
    hct_MOAB = u5_bb_baseBear & (u5_bb_normPrice >= hct_th_gs)
    hct_Pentagon = conf & (u5_relVolRatio >= hct_th_1x) & (u5_relVolRatio <= hct_th_wtc)
    hct_WTC = conf & (u5_relVolRatio > hct_th_wtc) & (u5_relVolRatio <= hct_th_hiro)
    hct_Hiroshima = conf & (u5_relVolRatio > hct_th_hiro)

    # HCT FVG threshold (auto = cumulative avg range%/bar; manual = pct)
    if bool(p["hct_auto"]):
        bar_idx_pl1 = np.arange(1, n + 1, dtype=float)
        hct_pct_arr = ((df["high"] - df["low"]) / df["low"].replace(0, np.nan)).fillna(0.0).cumsum().to_numpy()
        hct_thresh_arr = hct_pct_arr / bar_idx_pl1
        hct_thresh = pd.Series(hct_thresh_arr, index=df.index)
    else:
        hct_thresh = pd.Series(float(p["hct_threshPct"]) / 100.0, index=df.index)
    hct_bFVG = (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["high"].shift(2)) & \
               (((df["low"] - df["high"].shift(2)) / df["high"].shift(2)) > hct_thresh)
    hct_sFVG = (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["low"].shift(2)) & \
               (((df["low"].shift(2) - df["high"]) / df["high"]) > hct_thresh)

    hct_barRange = df["high"].shift(1) - df["low"].shift(1)
    hct_rangeStdev = _stdev((df["high"] - df["low"]), int(p["hct_disp_lookback"]))
    hct_dispCandleMet = hct_barRange > float(p["hct_disp_strength"]) * _nz_f(hct_rangeStdev.shift(1), 0.0)
    hct_dispBull = conf & hct_dispCandleMet & (df["close"].shift(1) > df["open"].shift(1)) & hct_bFVG
    hct_dispBear = conf & hct_dispCandleMet & (df["close"].shift(1) < df["open"].shift(1)) & hct_sFVG
    hct_noDisp = ~hct_dispBull & ~hct_dispBear

    hct_groupA_Bull = hct_BullRVOL1x | hct_GrandSlam
    hct_groupA_Bear = hct_BearRVOL1x | hct_MOAB
    hct_groupB = hct_Pentagon | hct_WTC | hct_Hiroshima
    hct_baseYY = (hct_groupA_Bull | hct_groupA_Bear) & hct_groupB
    hct_baseN = u5_Nagasaki & (hct_groupA_Bull | hct_groupA_Bear)
    hct_baseNV = u5_Nagasaki & hct_groupB
    hct_baseT = u5_Nagasaki & (hct_groupA_Bull | hct_groupA_Bear) & hct_groupB
    hct_baseNH = (hct_Pentagon & hct_WTC) | (hct_Pentagon & hct_Hiroshima) | (hct_WTC & hct_Hiroshima)
    hct_baseAny = hct_baseYY | hct_baseN | hct_baseNV | hct_baseT | hct_baseNH
    hct_bull = hct_baseAny & hct_dispBull
    hct_bear = hct_baseAny & hct_dispBear
    hct_neutral = hct_baseAny & hct_noDisp

    # ------------------------------------------------------------------
    # UC (Unified Combo) — inline placeholder.
    # ------------------------------------------------------------------
    uc_bull_count = (u5_FAUNABull.astype(int) +
                     (u5_RVOL1xB | u5_GrandSlam | u5_SAAB).astype(int) +
                     u5_WMD.astype(int) + u5_PUP.astype(int) + u5_CS1_Bull.astype(int))
    uc_bear_count = (u5_FAUNABear.astype(int) +
                     (u5_RVOL1xR | u5_MOAB | u5_Kratos).astype(int) +
                     u5_WMD.astype(int) + u5_PPD.astype(int) + u5_CS1_Bear.astype(int))
    uc_bull = conf & (uc_bull_count >= 2)
    uc_bear = conf & (uc_bear_count >= 2)

    # ------------------------------------------------------------------
    # Nagasaki + Any (gate atom)
    # ------------------------------------------------------------------
    nagAny_bull = conf & u5_Nagasaki & (u5_Pentagon | u5_WTC | u5_Hiroshima | u5_RVOL1xB | u5_GrandSlam | u5_SAAB)
    nagAny_bear = conf & u5_Nagasaki & (u5_Pentagon | u5_WTC | u5_Hiroshima | u5_RVOL1xR | u5_MOAB | u5_Kratos)

    # ------------------------------------------------------------------
    # Engine #5: Gate displacement (separate σ-mult).
    # ------------------------------------------------------------------
    gate_disp_std = _stdev(disp_range, int(p["DISP_STD_LEN"]))
    gate_disp_threshold = gate_disp_std * float(p["gateStdMult"])
    gate_disp_bull = conf & (disp_range.shift(1) > _nz_f(gate_disp_threshold.shift(1), 0.0)) & isBullishFVG & (df["close"].shift(1) > df["open"].shift(1))
    gate_disp_bear = conf & (disp_range.shift(1) > _nz_f(gate_disp_threshold.shift(1), 0.0)) & isBearishFVG & (df["close"].shift(1) < df["open"].shift(1))

    # ------------------------------------------------------------------
    # Master OR-gate (v3 NEW)
    # ------------------------------------------------------------------
    gate_bull_raw = u5_RVOL1xB | u5_GrandSlam | uc_bull | nagAny_bull | hct_bull | gate_disp_bull
    gate_bear_raw = u5_RVOL1xR | u5_MOAB | uc_bear | nagAny_bear | hct_bear | gate_disp_bear
    en_newGate = bool(p["en_newGate"])
    if not en_newGate:
        gate_bull = pd.Series(True, index=df.index)
        gate_bear = pd.Series(True, index=df.index)
    else:
        gate_bull = gate_bull_raw
        gate_bear = gate_bear_raw

    # ------------------------------------------------------------------
    # Composite raw detections (same as v2 LATEST).
    # ------------------------------------------------------------------
    det_rcTRBull = df.attrs.get("det_rcTRBull")
    det_rcTRBull = (_nz_b(det_rcTRBull.reindex(df.index)) if det_rcTRBull is not None
                    else (det_bullTNT & det_bullRetTNT))
    det_rcTRBear = df.attrs.get("det_rcTRBear")
    det_rcTRBear = (_nz_b(det_rcTRBear.reindex(df.index)) if det_rcTRBear is not None
                    else (det_bearTNT & det_bearRetTNT))
    det_rcRNBull = df.attrs.get("det_rcRNBull_override")
    det_rcRNBull = (_nz_b(det_rcRNBull.reindex(df.index)) if det_rcRNBull is not None
                    else (det_bullRetTNT & det_bullNapalm))
    det_rcRNBear = df.attrs.get("det_rcRNBear_override")
    det_rcRNBear = (_nz_b(det_rcRNBear.reindex(df.index)) if det_rcRNBear is not None
                    else (det_bearRetTNT & det_bearNapalm))

    det_pnBull = det_pbjBull & det_bullNapalm
    det_pnBear = det_pbjBear & det_bearNapalm
    det_ptBull = det_pbjBull & det_bullTNT
    det_ptBear = det_pbjBear & det_bearTNT
    det_prBull = det_pbjBull & det_bullRetTNT
    det_prBear = det_pbjBear & det_bearRetTNT

    pnGateBull = df.attrs.get("pnGateBull")
    pnGateBull = (_nz_b(pnGateBull.reindex(df.index)) if pnGateBull is not None
                  else pd.Series(True, index=df.index))
    pnGateBear = df.attrs.get("pnGateBear")
    pnGateBear = (_nz_b(pnGateBear.reindex(df.index)) if pnGateBear is not None
                  else pd.Series(True, index=df.index))
    ptGateBull = df.attrs.get("ptGateBull")
    ptGateBull = (_nz_b(ptGateBull.reindex(df.index)) if ptGateBull is not None
                  else pd.Series(True, index=df.index))
    ptGateBear = df.attrs.get("ptGateBear")
    ptGateBear = (_nz_b(ptGateBear.reindex(df.index)) if ptGateBear is not None
                  else pd.Series(True, index=df.index))

    def _fuse(npm: pd.Series, tnt: pd.Series, cont: pd.Series, prox: int) -> pd.Series:
        a_npm = _nz_b(npm).to_numpy()
        a_tnt = _nz_b(tnt).to_numpy()
        a_cnt = _nz_b(cont).to_numpy()
        out = np.zeros(n, dtype=bool)
        for i in range(n):
            if not a_cnt[i]:
                continue
            tnt_hit = -1
            for j in range(1, prox + 1):
                if i - j < 0:
                    break
                if a_tnt[i - j]:
                    tnt_hit = i - j
                    break
            if tnt_hit < 0:
                continue
            for k in range(1, prox + 1):
                if tnt_hit - k < 0:
                    break
                if a_npm[tnt_hit - k]:
                    out[i] = True
                    break
        return pd.Series(out, index=df.index)

    det_fuseBull = df.attrs.get("det_fuseBull")
    det_fuseBull = (_nz_b(det_fuseBull.reindex(df.index)) if det_fuseBull is not None
                    else _fuse(det_bullNapalm, det_bullTNT, det_contBull, int(p["SUDDEN_PROX"])))
    det_fuseBear = df.attrs.get("det_fuseBear")
    det_fuseBear = (_nz_b(det_fuseBear.reindex(df.index)) if det_fuseBear is not None
                    else _fuse(det_bearNapalm, det_bearTNT, det_contBear, int(p["SUDDEN_PROX"])))

    det_catBull = det_bullNapalm & det_cs1_Bull
    det_catBear = det_bearNapalm & det_cs1_Bear

    ign_tc_bull = det_bullTNT & det_contBull
    ign_tc_bear = det_bearTNT & det_contBear
    ign_nc_bull = det_bullNapalm & det_contBull
    ign_nc_bear = det_bearNapalm & det_contBear
    det_igniteBull = ign_tc_bull | ign_nc_bull
    det_igniteBear = ign_tc_bear | ign_nc_bear

    # sig_rcNTBull — v3: gated by gate_bull[1]
    sig_rcNTBull = det_bullNapalm & _nz_b(det_bullTNT.shift(1)) & bool(p["en_rcNTBull"]) & _nz_b(gate_bull.shift(1))
    sig_rcNTBear = det_bearNapalm & _nz_b(det_bearTNT.shift(1)) & bool(p["en_rcNTBear"]) & _nz_b(gate_bear.shift(1))

    supp_bullNPM = sig_rcNTBull | det_rcRNBull | det_pnBull
    supp_bullTNT = sig_rcNTBull | det_rcTRBull | det_ptBull
    supp_bearNPM = sig_rcNTBear | det_rcRNBear | det_pnBear
    supp_bearTNT = sig_rcNTBear | det_rcTRBear | det_ptBear

    # ------------------------------------------------------------------
    # Tier 1 plots (v3: gate-conditional for NPM-family; non-gated for fuse/pt/ign/dyn).
    # Per Pine line 1247-1255:
    #   p_b2bBull = ... and en_b2bBull and nz(gate_bull[1])   <-- gated
    #   p_pnBull  = det_pnBull and pnGateBull and en_pnBull and nz(gate_bull[1])  <-- gated
    #   p_ptBull  = det_ptBull and ptGateBull and en_ptBull                      <-- NOT gated
    #   p_fuseBull = det_fuseBull and en_fuseBull                                 <-- NOT gated
    #   p_catBull = det_catBull and en_catBull and nz(gate_bull[1])              <-- gated
    #   p_ignBull = det_igniteBull and en_ignBull                                 <-- NOT gated
    #   p_dynBull = det_dynamiteBull and en_dynBull                               <-- NOT gated
    # ------------------------------------------------------------------
    b2b_session_ok = (bar_idx_s - 2) >= sessionFirstBarIdx
    p_b2bBull = det_bullNapalm & ~supp_bullNPM & _nz_b(det_bullNapalm.shift(1)) & b2b_session_ok & bool(p["en_b2bBull"]) & _nz_b(gate_bull.shift(1))
    p_b2bBear = det_bearNapalm & ~supp_bearNPM & _nz_b(det_bearNapalm.shift(1)) & b2b_session_ok & bool(p["en_b2bBear"]) & _nz_b(gate_bear.shift(1))

    p_pnBull = det_pnBull & pnGateBull & bool(p["en_pnBull"]) & _nz_b(gate_bull.shift(1))
    p_pnBear = det_pnBear & pnGateBear & bool(p["en_pnBear"]) & _nz_b(gate_bear.shift(1))
    p_ptBull = det_ptBull & ptGateBull & bool(p["en_ptBull"])
    p_ptBear = det_ptBear & ptGateBear & bool(p["en_ptBear"])
    p_fuseBull = det_fuseBull & bool(p["en_fuseBull"])
    p_fuseBear = det_fuseBear & bool(p["en_fuseBear"])
    p_catBull = det_catBull & bool(p["en_catBull"]) & _nz_b(gate_bull.shift(1))
    p_catBear = det_catBear & bool(p["en_catBear"]) & _nz_b(gate_bear.shift(1))
    p_ignBull = det_igniteBull & bool(p["en_ignBull"])
    p_ignBear = det_igniteBear & bool(p["en_ignBear"])
    p_dynBull = det_dynamiteBull & bool(p["en_dynBull"])
    p_dynBear = det_dynamiteBear & bool(p["en_dynBear"])

    p_ign_tc_bull = p_ignBull & ign_tc_bull
    p_ign_tc_bear = p_ignBear & ign_tc_bear
    p_ign_nc_bull = p_ignBull & ign_nc_bull
    p_ign_nc_bear = p_ignBear & ign_nc_bear

    # ------------------------------------------------------------------
    # Tier 2 (Enriched) — v3 gates these per Pine line 1260-1268:
    #   gate_bull at bar 0 for offset-0 plots, gate_bull[1] for offset-(-1).
    # ------------------------------------------------------------------
    enrich_set_bull = u5_RVOL1xB | u5_GrandSlam | u5_PUP | det_cs1_Bull | u5_FAUNABull | u5_WMD | u5_HV1000 | det_dynamiteBull
    enrich_set_bear = u5_RVOL1xR | u5_MOAB | u5_PPD | det_cs1_Bear | u5_FAUNABear | u5_WMD | u5_HV1000 | det_dynamiteBear
    enrichBull_N = enrich_set_bull
    enrichBear_N = enrich_set_bear
    enrichBull_N1 = _nz_b(enrich_set_bull.shift(1))
    enrichBear_N1 = _nz_b(enrich_set_bear.shift(1))

    p_t2tntBull = det_bullTNT & ~supp_bullTNT & enrichBull_N & bool(p["en_t2tntBull"]) & gate_bull
    p_t2tntBear = det_bearTNT & ~supp_bearTNT & enrichBear_N & bool(p["en_t2tntBear"]) & gate_bear
    p_t2npmBull = det_bullNapalm & ~supp_bullNPM & enrichBull_N1 & bool(p["en_t2npmBull"]) & _nz_b(gate_bull.shift(1))
    p_t2npmBear = det_bearNapalm & ~supp_bearNPM & enrichBear_N1 & bool(p["en_t2npmBear"]) & _nz_b(gate_bear.shift(1))
    p_t2contBull = det_contBull & enrichBull_N & bool(p["en_t2contBull"]) & gate_bull
    p_t2contBear = det_contBear & enrichBear_N & bool(p["en_t2contBear"]) & gate_bear
    p_t2trBull = det_rcTRBull & enrichBull_N & bool(p["en_t2trBull"]) & gate_bull
    p_t2trBear = det_rcTRBear & enrichBear_N & bool(p["en_t2trBear"]) & gate_bear
    p_t2rnBull = det_rcRNBull & enrichBull_N1 & bool(p["en_t2rnBull"]) & _nz_b(gate_bull.shift(1))
    p_t2rnBear = det_rcRNBear & enrichBear_N1 & bool(p["en_t2rnBear"]) & _nz_b(gate_bear.shift(1))
    p_t2prBull = det_prBull & enrichBull_N & bool(p["en_t2prBull"]) & gate_bull
    p_t2prBear = det_prBear & enrichBear_N & bool(p["en_t2prBear"]) & gate_bear

    # ------------------------------------------------------------------
    # Density 1/2/3 (same logic as v2)
    # ------------------------------------------------------------------
    denVisBull = (_nz_b(det_bullTNT.shift(1)) | _nz_b(det_contBull.shift(1)) |
                  _nz_b(det_rcTRBull.shift(1)) | _nz_b(det_ptBull.shift(1)) |
                  _nz_b(det_prBull.shift(1)) |
                  det_bullNapalm | sig_rcNTBull | det_rcRNBull | det_pnBull)
    denVisBear = (_nz_b(det_bearTNT.shift(1)) | _nz_b(det_contBear.shift(1)) |
                  _nz_b(det_rcTRBear.shift(1)) | _nz_b(det_ptBear.shift(1)) |
                  _nz_b(det_prBear.shift(1)) |
                  det_bearNapalm | sig_rcNTBear | det_rcRNBear | det_pnBear)

    def _density(visual: pd.Series, X: int, Y: int) -> pd.Series:
        vis = _nz_b(visual).to_numpy()
        out = np.zeros(n, dtype=bool)
        last_used_bar = -1
        for i in range(n):
            if (bar_idx[i] - 2) < session_first_bar[i]:
                continue
            count = 0
            for k in range(Y):
                idx = bar_idx[i] - 1 - k
                if idx < session_first_bar[i] or idx < 0:
                    break
                if vis[idx] and idx > last_used_bar:
                    count += 1
            if count >= X:
                out[i] = True
                last_used_bar = bar_idx[i] - 2
        return pd.Series(out, index=df.index)

    sig_d1b = _density(denVisBull, int(p["den1_X"]), int(p["den1_Y"]))
    sig_d1s = _density(denVisBear, int(p["den1_X"]), int(p["den1_Y"]))
    sig_d2b = _density(denVisBull, int(p["den2_X"]), int(p["den2_Y"]))
    sig_d2s = _density(denVisBear, int(p["den2_X"]), int(p["den2_Y"]))
    sig_d3b = _density(denVisBull, int(p["den3_X"]), int(p["den3_Y"]))
    sig_d3s = _density(denVisBear, int(p["den3_X"]), int(p["den3_Y"]))

    p_d1b = sig_d1b & bool(p["en_d1b"])
    p_d1s = sig_d1s & bool(p["en_d1s"])
    p_d2b = sig_d2b & bool(p["en_d2b"])
    p_d2s = sig_d2s & bool(p["en_d2s"])
    p_d3b = sig_d3b & bool(p["en_d3b"])
    p_d3s = sig_d3s & bool(p["en_d3s"])

    # ------------------------------------------------------------------
    # UU/UUU/UUUU + TNT ANY
    # ------------------------------------------------------------------
    u_qual_bull = u5_bb_baseBull & (u5_bb_normPrice >= u5_th_1x)
    u_qual_bear = u5_bb_baseBear & (u5_bb_normPrice >= u5_th_1x)
    u_streak_bull = _streak(u_qual_bull)
    u_streak_bear = _streak(u_qual_bear)
    u_pathBull2 = u_streak_bull >= 2
    u_pathBull3 = u_streak_bull >= 3
    u_pathBull4 = u_streak_bull >= 4
    u_pathBear2 = u_streak_bear >= 2
    u_pathBear3 = u_streak_bear >= 3
    u_pathBear4 = u_streak_bear >= 4

    tntAny_bull_atK = lambda k: (_nz_b(det_bullTNT.shift(k)) | _nz_b(det_contBull.shift(k)) |
                                 _nz_b(det_rcTRBull.shift(k)) | _nz_b(det_ptBull.shift(k)) |
                                 _nz_b(det_prBull.shift(k)) | _nz_b(det_fuseBull.shift(k)) |
                                 _nz_b(det_igniteBull.shift(k)) |
                                 _nz_b(sig_d1b.shift(max(0, k - 1))) | _nz_b(sig_d2b.shift(max(0, k - 1))) | _nz_b(sig_d3b.shift(max(0, k - 1))) |
                                 _nz_b(det_dynamiteBull.shift(max(0, k - 1))) | _nz_b(det_bullNapalm.shift(max(0, k - 1))) |
                                 _nz_b(sig_rcNTBull.shift(max(0, k - 1))) | _nz_b(det_rcRNBull.shift(max(0, k - 1))) |
                                 _nz_b(det_pnBull.shift(max(0, k - 1))) | _nz_b(det_catBull.shift(max(0, k - 1))))
    tntAny_bear_atK = lambda k: (_nz_b(det_bearTNT.shift(k)) | _nz_b(det_contBear.shift(k)) |
                                 _nz_b(det_rcTRBear.shift(k)) | _nz_b(det_ptBear.shift(k)) |
                                 _nz_b(det_prBear.shift(k)) | _nz_b(det_fuseBear.shift(k)) |
                                 _nz_b(det_igniteBear.shift(k)) |
                                 _nz_b(sig_d1s.shift(max(0, k - 1))) | _nz_b(sig_d2s.shift(max(0, k - 1))) | _nz_b(sig_d3s.shift(max(0, k - 1))) |
                                 _nz_b(det_dynamiteBear.shift(max(0, k - 1))) | _nz_b(det_bearNapalm.shift(max(0, k - 1))) |
                                 _nz_b(sig_rcNTBear.shift(max(0, k - 1))) | _nz_b(det_rcRNBear.shift(max(0, k - 1))) |
                                 _nz_b(det_pnBear.shift(max(0, k - 1))) | _nz_b(det_catBear.shift(max(0, k - 1))))
    tntAnyBull2 = tntAny_bull_atK(1) | tntAny_bull_atK(2)
    tntAnyBull3 = tntAnyBull2 | tntAny_bull_atK(3)
    tntAnyBull4 = tntAnyBull3 | tntAny_bull_atK(4)
    tntAnyBear2 = tntAny_bear_atK(1) | tntAny_bear_atK(2)
    tntAnyBear3 = tntAnyBear2 | tntAny_bear_atK(3)
    tntAnyBear4 = tntAnyBear3 | tntAny_bear_atK(4)

    p_uuBull = u_pathBull2 & tntAnyBull2 & bool(p["en_uu_bull"])
    p_uuBear = u_pathBear2 & tntAnyBear2 & bool(p["en_uu_bear"])
    p_uuuBull = u_pathBull3 & tntAnyBull3 & bool(p["en_uuu_bull"])
    p_uuuBear = u_pathBear3 & tntAnyBear3 & bool(p["en_uuu_bear"])
    p_uuuuBull = u_pathBull4 & tntAnyBull4 & bool(p["en_uuuu_bull"])
    p_uuuuBear = u_pathBear4 & tntAnyBear4 & bool(p["en_uuuu_bear"])

    # ------------------------------------------------------------------
    # WBUSH (same as v2)
    # ------------------------------------------------------------------
    tntod_any_bull = (p_b2bBull | sig_rcNTBull | p_fuseBull | p_catBull | p_pnBull |
                      p_ptBull | p_ignBull | p_dynBull | p_t2tntBull | p_t2npmBull |
                      p_t2contBull | p_t2trBull | p_t2rnBull | p_t2prBull |
                      p_d1b | p_d2b | p_d3b | p_uuBull | p_uuuBull | p_uuuuBull)
    tntod_any_bear = (p_b2bBear | sig_rcNTBear | p_fuseBear | p_catBear | p_pnBear |
                      p_ptBear | p_ignBear | p_dynBear | p_t2tntBear | p_t2npmBear |
                      p_t2contBear | p_t2trBear | p_t2rnBear | p_t2prBear |
                      p_d1s | p_d2s | p_d3s | p_uuBear | p_uuuBear | p_uuuuBear)
    p_wbushBull = bool(p["en_wbushBull"]) & sig_WBUSH_Bull & tntod_any_bull
    p_wbushBear = bool(p["en_wbushBear"]) & sig_WBUSH_Bear & tntod_any_bear
    p_wbushNeutral = bool(p["en_wbushNeutral"]) & sig_WBUSH_Neutral

    # ------------------------------------------------------------------
    # T1 RELAY + T1 STACK (v3 NEW)
    # Per Pine lines 1604-1675:
    #   Tier-1 visuals on bar[1] (offset -1 → visual bar 1) :
    #     b2b, rcnt, cat, pn, ignNC, dyn  (these are "current bar booleans"
    #         because the plot itself uses offset -1)
    #     fuse[1], pt[1], ignTC[1]        (those plot at offset 0 → visual
    #         bar 1 means looking back 1 bar)
    #     hct (FVG chain → -1), uc[1]
    #   Tier-1 visuals on bar[2] (visual bar 2) — shift those above by +1.
    # ------------------------------------------------------------------
    # Build the 11 sub-flags for bar 1 (Bull/Bear)
    t1_v1_b_b2b   = p_b2bBull
    t1_v1_b_rcnt  = sig_rcNTBull
    t1_v1_b_cat   = p_catBull
    t1_v1_b_pn    = p_pnBull
    t1_v1_b_ignNC = p_ignBull & ign_nc_bull
    t1_v1_b_dyn   = p_dynBull
    t1_v1_b_fuse  = _nz_b(p_fuseBull.shift(1))
    t1_v1_b_pt    = _nz_b(p_ptBull.shift(1))
    t1_v1_b_ignTC = _nz_b(p_ignBull.shift(1)) & _nz_b(ign_tc_bull.shift(1))
    t1_v1_b_hct   = hct_bull
    t1_v1_b_uc    = _nz_b(uc_bull.shift(1))
    t1_v1_s_b2b   = p_b2bBear
    t1_v1_s_rcnt  = sig_rcNTBear
    t1_v1_s_cat   = p_catBear
    t1_v1_s_pn    = p_pnBear
    t1_v1_s_ignNC = p_ignBear & ign_nc_bear
    t1_v1_s_dyn   = p_dynBear
    t1_v1_s_fuse  = _nz_b(p_fuseBear.shift(1))
    t1_v1_s_pt    = _nz_b(p_ptBear.shift(1))
    t1_v1_s_ignTC = _nz_b(p_ignBear.shift(1)) & _nz_b(ign_tc_bear.shift(1))
    t1_v1_s_hct   = hct_bear
    t1_v1_s_uc    = _nz_b(uc_bear.shift(1))

    # Bar 2 sub-flags (shift bar 1's by +1)
    t1_v2_b_b2b   = _nz_b(p_b2bBull.shift(1))
    t1_v2_b_rcnt  = _nz_b(sig_rcNTBull.shift(1))
    t1_v2_b_cat   = _nz_b(p_catBull.shift(1))
    t1_v2_b_pn    = _nz_b(p_pnBull.shift(1))
    t1_v2_b_ignNC = _nz_b(p_ignBull.shift(1)) & _nz_b(ign_nc_bull.shift(1))
    t1_v2_b_dyn   = _nz_b(p_dynBull.shift(1))
    t1_v2_b_fuse  = _nz_b(p_fuseBull.shift(2))
    t1_v2_b_pt    = _nz_b(p_ptBull.shift(2))
    t1_v2_b_ignTC = _nz_b(p_ignBull.shift(2)) & _nz_b(ign_tc_bull.shift(2))
    t1_v2_b_hct   = _nz_b(hct_bull.shift(1))
    t1_v2_b_uc    = _nz_b(uc_bull.shift(2))
    t1_v2_s_b2b   = _nz_b(p_b2bBear.shift(1))
    t1_v2_s_rcnt  = _nz_b(sig_rcNTBear.shift(1))
    t1_v2_s_cat   = _nz_b(p_catBear.shift(1))
    t1_v2_s_pn    = _nz_b(p_pnBear.shift(1))
    t1_v2_s_ignNC = _nz_b(p_ignBear.shift(1)) & _nz_b(ign_nc_bear.shift(1))
    t1_v2_s_dyn   = _nz_b(p_dynBear.shift(1))
    t1_v2_s_fuse  = _nz_b(p_fuseBear.shift(2))
    t1_v2_s_pt    = _nz_b(p_ptBear.shift(2))
    t1_v2_s_ignTC = _nz_b(p_ignBear.shift(2)) & _nz_b(ign_tc_bear.shift(2))
    t1_v2_s_hct   = _nz_b(hct_bear.shift(1))
    t1_v2_s_uc    = _nz_b(uc_bear.shift(2))

    t1_v1_anyB = (t1_v1_b_b2b | t1_v1_b_rcnt | t1_v1_b_cat | t1_v1_b_pn |
                  t1_v1_b_ignNC | t1_v1_b_dyn | t1_v1_b_fuse | t1_v1_b_pt |
                  t1_v1_b_ignTC | t1_v1_b_hct | t1_v1_b_uc)
    t1_v1_anyS = (t1_v1_s_b2b | t1_v1_s_rcnt | t1_v1_s_cat | t1_v1_s_pn |
                  t1_v1_s_ignNC | t1_v1_s_dyn | t1_v1_s_fuse | t1_v1_s_pt |
                  t1_v1_s_ignTC | t1_v1_s_hct | t1_v1_s_uc)
    t1_v2_anyB = (t1_v2_b_b2b | t1_v2_b_rcnt | t1_v2_b_cat | t1_v2_b_pn |
                  t1_v2_b_ignNC | t1_v2_b_dyn | t1_v2_b_fuse | t1_v2_b_pt |
                  t1_v2_b_ignTC | t1_v2_b_hct | t1_v2_b_uc)
    t1_v2_anyS = (t1_v2_s_b2b | t1_v2_s_rcnt | t1_v2_s_cat | t1_v2_s_pn |
                  t1_v2_s_ignNC | t1_v2_s_dyn | t1_v2_s_fuse | t1_v2_s_pt |
                  t1_v2_s_ignTC | t1_v2_s_hct | t1_v2_s_uc)

    p_t1RelayBull = t1_v2_anyB & t1_v1_anyB & conf
    p_t1RelayBear = t1_v2_anyS & t1_v1_anyS & conf

    t1_v1_count_b = (t1_v1_b_b2b.astype(int) + t1_v1_b_rcnt.astype(int) +
                     t1_v1_b_cat.astype(int) + t1_v1_b_pn.astype(int) +
                     t1_v1_b_ignNC.astype(int) + t1_v1_b_dyn.astype(int) +
                     t1_v1_b_fuse.astype(int) + t1_v1_b_pt.astype(int) +
                     t1_v1_b_ignTC.astype(int) + t1_v1_b_hct.astype(int) +
                     t1_v1_b_uc.astype(int))
    t1_v1_count_s = (t1_v1_s_b2b.astype(int) + t1_v1_s_rcnt.astype(int) +
                     t1_v1_s_cat.astype(int) + t1_v1_s_pn.astype(int) +
                     t1_v1_s_ignNC.astype(int) + t1_v1_s_dyn.astype(int) +
                     t1_v1_s_fuse.astype(int) + t1_v1_s_pt.astype(int) +
                     t1_v1_s_ignTC.astype(int) + t1_v1_s_hct.astype(int) +
                     t1_v1_s_uc.astype(int))
    p_t1StackBull = (t1_v1_count_b >= 2) & conf
    p_t1StackBear = (t1_v1_count_s >= 2) & conf

    cache.update({
        # Tier 1
        "p_b2bBull": p_b2bBull, "p_b2bBear": p_b2bBear,
        "sig_rcNTBull": sig_rcNTBull, "sig_rcNTBear": sig_rcNTBear,
        "p_fuseBull": p_fuseBull, "p_fuseBear": p_fuseBear,
        "p_catBull": p_catBull, "p_catBear": p_catBear,
        "p_pnBull": p_pnBull, "p_pnBear": p_pnBear,
        "p_ptBull": p_ptBull, "p_ptBear": p_ptBear,
        "p_ignBull": p_ignBull, "p_ignBear": p_ignBear,
        "p_ign_tc_bull": p_ign_tc_bull, "p_ign_tc_bear": p_ign_tc_bear,
        "p_ign_nc_bull": p_ign_nc_bull, "p_ign_nc_bear": p_ign_nc_bear,
        "p_dynBull": p_dynBull, "p_dynBear": p_dynBear,
        # Tier 2
        "p_t2tntBull": p_t2tntBull, "p_t2tntBear": p_t2tntBear,
        "p_t2npmBull": p_t2npmBull, "p_t2npmBear": p_t2npmBear,
        "p_t2contBull": p_t2contBull, "p_t2contBear": p_t2contBear,
        "p_t2trBull": p_t2trBull, "p_t2trBear": p_t2trBear,
        "p_t2rnBull": p_t2rnBull, "p_t2rnBear": p_t2rnBear,
        "p_t2prBull": p_t2prBull, "p_t2prBear": p_t2prBear,
        # Density
        "p_d1b": p_d1b, "p_d1s": p_d1s,
        "p_d2b": p_d2b, "p_d2s": p_d2s,
        "p_d3b": p_d3b, "p_d3s": p_d3s,
        # UU
        "p_uuBull": p_uuBull, "p_uuBear": p_uuBear,
        "p_uuuBull": p_uuuBull, "p_uuuBear": p_uuuBear,
        "p_uuuuBull": p_uuuuBull, "p_uuuuBear": p_uuuuBear,
        # WBUSH
        "p_wbushBull": p_wbushBull, "p_wbushBear": p_wbushBear,
        "p_wbushNeutral": p_wbushNeutral,
        # v3 NEW
        "p_t1RelayBull": p_t1RelayBull, "p_t1RelayBear": p_t1RelayBear,
        "p_t1StackBull": p_t1StackBull, "p_t1StackBear": p_t1StackBear,
        # v3 gate features (exposed for downstream consumers)
        "gate_bull": gate_bull, "gate_bear": gate_bear,
        "gate_bull_raw": gate_bull_raw, "gate_bear_raw": gate_bear_raw,
        "hct_bull": hct_bull, "hct_bear": hct_bear, "hct_neutral": hct_neutral,
        "uc_bull": uc_bull, "uc_bear": uc_bear,
        "nagAny_bull": nagAny_bull, "nagAny_bear": nagAny_bear,
        "gate_disp_bull": gate_disp_bull, "gate_disp_bear": gate_disp_bear,
        # Aggregates
        "tntod_any_bull": tntod_any_bull, "tntod_any_bear": tntod_any_bear,
        "sessionFirstBarIdx": sessionFirstBarIdx,
    })
    return cache


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


# ─── Tier 1 ───
detect_B2B_Napalm_Bull = _wrap("p_b2bBull")
detect_B2B_Napalm_Bear = _wrap("p_b2bBear")
detect_RC_NPM_TNT_Bull = _wrap("sig_rcNTBull")
detect_RC_NPM_TNT_Bear = _wrap("sig_rcNTBear")
detect_FUSE_Bull = _wrap("p_fuseBull")
detect_FUSE_Bear = _wrap("p_fuseBear")
detect_CATALYST_Bull = _wrap("p_catBull")
detect_CATALYST_Bear = _wrap("p_catBear")
detect_PBJ_NPM_Bull = _wrap("p_pnBull")
detect_PBJ_NPM_Bear = _wrap("p_pnBear")
detect_PBJ_TNT_Bull = _wrap("p_ptBull")
detect_PBJ_TNT_Bear = _wrap("p_ptBear")
detect_IGNITE_TC_Bull = _wrap("p_ign_tc_bull")
detect_IGNITE_TC_Bear = _wrap("p_ign_tc_bear")
detect_IGNITE_NC_Bull = _wrap("p_ign_nc_bull")
detect_IGNITE_NC_Bear = _wrap("p_ign_nc_bear")
detect_DYNAMITE_Bull = _wrap("p_dynBull")
detect_DYNAMITE_Bear = _wrap("p_dynBear")
# ─── Tier 2 ───
detect_TNT_Enriched_Bull = _wrap("p_t2tntBull")
detect_TNT_Enriched_Bear = _wrap("p_t2tntBear")
detect_NPM_Enriched_Bull = _wrap("p_t2npmBull")
detect_NPM_Enriched_Bear = _wrap("p_t2npmBear")
detect_CONT_Enriched_Bull = _wrap("p_t2contBull")
detect_CONT_Enriched_Bear = _wrap("p_t2contBear")
detect_RC_TR_Enriched_Bull = _wrap("p_t2trBull")
detect_RC_TR_Enriched_Bear = _wrap("p_t2trBear")
detect_RC_RN_Enriched_Bull = _wrap("p_t2rnBull")
detect_RC_RN_Enriched_Bear = _wrap("p_t2rnBear")
detect_PBJ_RET_Enriched_Bull = _wrap("p_t2prBull")
detect_PBJ_RET_Enriched_Bear = _wrap("p_t2prBear")
# ─── Density ───
detect_Density_1_Bull = _wrap("p_d1b")
detect_Density_1_Bear = _wrap("p_d1s")
detect_Density_2_Bull = _wrap("p_d2b")
detect_Density_2_Bear = _wrap("p_d2s")
detect_Density_3_Bull = _wrap("p_d3b")
detect_Density_3_Bear = _wrap("p_d3s")
# ─── UU / UUU / UUUU ───
detect_UU_TNT_ANY_Bull = _wrap("p_uuBull")
detect_UU_TNT_ANY_Bear = _wrap("p_uuBear")
detect_UUU_TNT_ANY_Bull = _wrap("p_uuuBull")
detect_UUU_TNT_ANY_Bear = _wrap("p_uuuBear")
detect_UUUU_TNT_ANY_Bull = _wrap("p_uuuuBull")
detect_UUUU_TNT_ANY_Bear = _wrap("p_uuuuBear")
# ─── WBUSH ───
detect_WBUSH_Bull = _wrap("p_wbushBull")
detect_WBUSH_Bear = _wrap("p_wbushBear")
detect_WBUSH_Neutral = _wrap("p_wbushNeutral")
# ─── v3 NEW: T1 RELAY / T1 STACK ───
detect_T1_RELAY_Bull = _wrap("p_t1RelayBull")
detect_T1_RELAY_Bear = _wrap("p_t1RelayBear")
detect_T1_STACK_Bull = _wrap("p_t1StackBull")
detect_T1_STACK_Bear = _wrap("p_t1StackBear")


# ============================================================================
# Stubbed inputs — Pine-only intrinsics required.
# ============================================================================
STUBBED: Dict[str, str] = {
    # ---- TNT zone scanner ----
    "det_bullTNT": "Raw TNT bull from TNT 1.0/2.0 zone arrays + super-TNT. Inject via df.attrs.",
    "det_bearTNT": "Raw TNT bear. Inject via df.attrs.",
    "det_bullNapalm": "Raw Napalm/Charge bull. Inject via df.attrs.",
    "det_bearNapalm": "Raw Napalm/Charge bear. Inject via df.attrs.",
    "det_bullRetTNT": "Raw Return-to-TNT bull. Inject via df.attrs.",
    "det_bearRetTNT": "Raw Return-to-TNT bear. Inject via df.attrs.",
    "det_contBull": "Raw Continuous-cluster bull. Inject via df.attrs.",
    "det_contBear": "Raw Continuous-cluster bear. Inject via df.attrs.",
    # ---- PBJ ----
    "det_pbjBull": "PBJ Supertrend reversal bull. Inject via df.attrs.",
    "det_pbjBear": "PBJ Supertrend reversal bear. Inject via df.attrs.",
    # ---- CS1 ----
    "det_cs1_Bull": "CS1 FVG combo bull. Inject via df.attrs.",
    "det_cs1_Bear": "CS1 FVG combo bear. Inject via df.attrs.",
    # ---- WBUSH ----
    "sig_WBUSH_Bull": "WBUSH heavy-combo bull state. Inject via df.attrs.",
    "sig_WBUSH_Bear": "WBUSH bear state. Inject via df.attrs.",
    "sig_WBUSH_Neutral": "WBUSH neutral state. Inject via df.attrs.",
    # ---- tv_ta.relativeVolume ----
    "u5_relVolRatio": "tv_ta.relativeVolume(reg) used by u5_WTC/u5_Hiroshima/u5_Pentagon AND HCT atoms. Inject via df.attrs.",
    # ---- Optional overrides ----
    "det_rcTRBull": "Optional override for RC TNT+RET bull.",
    "det_rcTRBear": "Optional override for RC TNT+RET bear.",
    "det_rcRNBull_override": "Optional override for RC RET+NPM bull.",
    "det_rcRNBear_override": "Optional override for RC RET+NPM bear.",
    "det_fuseBull": "Optional override for FUSE bull.",
    "det_fuseBear": "Optional override for FUSE bear.",
    "pnGateBull": "Optional PBJ+NPM internal gate (not the v3 conditional gate).",
    "pnGateBear": "Optional PBJ+NPM internal gate (not the v3 conditional gate).",
    "ptGateBull": "Optional PBJ+TNT internal gate.",
    "ptGateBear": "Optional PBJ+TNT internal gate.",
}


# ============================================================================
# State machines
# ============================================================================
@dataclass
class SessionTracker:
    """sessionFirstBarIdx tracker — built into _ensure_engines."""
    name: str = "SessionTracker"


@dataclass
class B2BWalker:
    """B2B Napalm bar-by-bar walker."""
    name: str = "B2BWalker"


@dataclass
class DensityWalker:
    """Density 1/2/3 X-in-Y window walker with overlap re-arm."""
    name: str = "DensityWalker"


@dataclass
class ConditionalGate:
    """v3 NEW: 6-atom conditional gate (RVOL1x / GS / UC / Nag+Any / HCT / GateDisp)."""
    name: str = "ConditionalGate"


@dataclass
class T1Walker:
    """v3 NEW: T1 RELAY / T1 STACK visual-bar Tier-1 walker."""
    name: str = "T1Walker"


STATE_MACHINES: Dict[str, type] = {
    "SessionTracker": SessionTracker,
    "B2BWalker": B2BWalker,
    "DensityWalker": DensityWalker,
    "ConditionalGate": ConditionalGate,
    "T1Walker": T1Walker,
}


# ============================================================================
# DETECTIONS registry — name → detect_* function.
# Mirrors v2 plus T1 RELAY/STACK.
# ============================================================================
DETECTIONS: Dict[str, Callable] = {
    # ─── Tier 1 ───
    "B2B Napalm Bull": detect_B2B_Napalm_Bull,
    "B2B Napalm Bear": detect_B2B_Napalm_Bear,
    "RC NPM+TNT Bull": detect_RC_NPM_TNT_Bull,
    "RC NPM+TNT Bear": detect_RC_NPM_TNT_Bear,
    "FUSE Bull": detect_FUSE_Bull,
    "FUSE Bear": detect_FUSE_Bear,
    "CATALYST Bull": detect_CATALYST_Bull,
    "CATALYST Bear": detect_CATALYST_Bear,
    "PBJ+NPM Bull": detect_PBJ_NPM_Bull,
    "PBJ+NPM Bear": detect_PBJ_NPM_Bear,
    "PBJ+TNT Bull": detect_PBJ_TNT_Bull,
    "PBJ+TNT Bear": detect_PBJ_TNT_Bear,
    "IGNITE TNT+CONT Bull": detect_IGNITE_TC_Bull,
    "IGNITE TNT+CONT Bear": detect_IGNITE_TC_Bear,
    "IGNITE NPM+CONT Bull": detect_IGNITE_NC_Bull,
    "IGNITE NPM+CONT Bear": detect_IGNITE_NC_Bear,
    "DYNAMITE Bull": detect_DYNAMITE_Bull,
    "DYNAMITE Bear": detect_DYNAMITE_Bear,
    # ─── Tier 2 ───
    "TNT Enriched Bull": detect_TNT_Enriched_Bull,
    "TNT Enriched Bear": detect_TNT_Enriched_Bear,
    "NPM Enriched Bull": detect_NPM_Enriched_Bull,
    "NPM Enriched Bear": detect_NPM_Enriched_Bear,
    "CONT Enriched Bull": detect_CONT_Enriched_Bull,
    "CONT Enriched Bear": detect_CONT_Enriched_Bear,
    "RC TNT+RET Enriched Bull": detect_RC_TR_Enriched_Bull,
    "RC TNT+RET Enriched Bear": detect_RC_TR_Enriched_Bear,
    "RC RET+NPM Enriched Bull": detect_RC_RN_Enriched_Bull,
    "RC RET+NPM Enriched Bear": detect_RC_RN_Enriched_Bear,
    "PBJ+RET Enriched Bull": detect_PBJ_RET_Enriched_Bull,
    "PBJ+RET Enriched Bear": detect_PBJ_RET_Enriched_Bear,
    # ─── Density ───
    "Density 1 Bull": detect_Density_1_Bull,
    "Density 1 Bear": detect_Density_1_Bear,
    "Density 2 Bull": detect_Density_2_Bull,
    "Density 2 Bear": detect_Density_2_Bear,
    "Density 3 Bull": detect_Density_3_Bull,
    "Density 3 Bear": detect_Density_3_Bear,
    # ─── UU / UUU / UUUU ───
    "UU+TNT ANY Bull": detect_UU_TNT_ANY_Bull,
    "UU+TNT ANY Bear": detect_UU_TNT_ANY_Bear,
    "UUU+TNT ANY Bull": detect_UUU_TNT_ANY_Bull,
    "UUU+TNT ANY Bear": detect_UUU_TNT_ANY_Bear,
    "UUUU+TNT ANY Bull": detect_UUUU_TNT_ANY_Bull,
    "UUUU+TNT ANY Bear": detect_UUUU_TNT_ANY_Bear,
    # ─── WBUSH ───
    "WBUSH+TNTOD ANY Bull": detect_WBUSH_Bull,
    "WBUSH+TNTOD ANY Bear": detect_WBUSH_Bear,
    "WBUSH Neutral": detect_WBUSH_Neutral,
    # ─── v3 NEW ───
    "T1 RELAY Bull": detect_T1_RELAY_Bull,
    "T1 RELAY Bear": detect_T1_RELAY_Bear,
    "T1 STACK Bull": detect_T1_STACK_Bull,
    "T1 STACK Bear": detect_T1_STACK_Bear,
}


if __name__ == "__main__":
    print(f"DETECTIONS: {len(DETECTIONS)}")
    print(f"STUBBED engine notes: {len(STUBBED)}")
    print(f"STATE_MACHINES: {len(STATE_MACHINES)}")
    print("First 5 detection names:")
    for nname in list(DETECTIONS)[:5]:
        print("  ", nname)
