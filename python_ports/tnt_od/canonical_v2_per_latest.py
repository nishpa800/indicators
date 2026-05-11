"""
Python port of TNT_Opening_Drive_OD_v3_2026-05-04.pine (1802 lines).

NOTE on naming: This file is filename-tagged "v3" in the repo but is
INTERNALLY v2 per the existing audit
``docs/validation/2026-05-10-tnt-od-v2-v3.md`` and VETTING.md. The
``tnt-od/versions/LATEST.txt`` pointer points at this file as the
current canonical, but it lacks the true v3 features (T1 RELAY, T1
STACK, conditional gate). Hence the module name reflects "v2 per
LATEST" (not v3).

Source Pine: tnt-od/versions/TNT_Opening_Drive_OD_v3_2026-05-04.pine
True v3 (with T1 RELAY / T1 STACK / gate features) lives in
``v3.py`` (pending Anish vet per tnt-od/VETTING.md).

Re-implements every named detection plot in the source as a vectorized
pandas function, suitable for replaying against a bar-history DataFrame.

Conventions (mirror hvd_pbj_ppd/the_only_one.py):
  - df is expected to have columns: open, high, low, close, volume.
    Index should be a monotonic int (bar index) or DatetimeIndex; bar order
    must be ascending.
  - Each detection function returns a pd.Series[bool] aligned to df.index.
  - IPSF (input.*) parameters live in DEFAULTS and may be overridden via the
    ``params`` dict passed to every detection.
  - Hardcoded Pine constants (NOT input.*) stay hardcoded here so future
    edits do not silently introduce drift.
  - Stateful detections (session tracker, B2B walker, Density X-in-Y window
    walker) are built into _ensure_engines bar-by-bar; the wrapper classes
    in STATE_MACHINES expose them by name.
  - Upstream raw detections that require Pine-only state machines (the TNT
    zone array, Napalm/Charge zone scanner, Return-to-TNT, CONT cluster,
    Supertrend-based PBJ, WBUSH state, Heavy combo direction engine,
    tv_ta.relativeVolume) are STUBBED. Caller MUST inject these series via
    df.attrs[<name>] before calling any composite. Each STUBBED key is
    listed in STUBBED.

This module is import-only safe; it does NOT contain tests. The harness
runs validation tests separately.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional
import weakref

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

    # --- Density 1/2/3 (grpD1/D2/D3) ---
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

    # --- Bar timeframe in seconds (caller supplies; defaults to 60s) ---
    "tfSec": 60,

    # --- Alerts (not used in detection but mirrored for completeness) ---
    "masterFirstBar": True,
    "masterAggregate": True,
    "en_nagAlert": False,
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
    """Pine ``barstate.isconfirmed`` — for historical bars True everywhere."""
    return pd.Series(True, index=df.index)


def _shift(s: pd.Series, n: int) -> pd.Series:
    return s.shift(n)


def _nz_b(s: pd.Series) -> pd.Series:
    return s.fillna(False).astype(bool)


def _nz_f(s: pd.Series, fill: float = 0.0) -> pd.Series:
    return s.fillna(fill)


def _highest(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=1).max()


def _lowest(s: pd.Series, length: int) -> pd.Series:
    return s.rolling(length, min_periods=1).min()


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


# --- USE V5 RVOL threshold tables — copied verbatim from u5_* helpers ---
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


def _streak(series: pd.Series) -> pd.Series:
    a = series.fillna(False).to_numpy()
    out = np.zeros(len(a), dtype=int)
    c = 0
    for i, v in enumerate(a):
        c = c + 1 if v else 0
        out[i] = c
    return pd.Series(out, index=series.index)


# ============================================================================
# _ensure_engines — compute everything once and cache.
# ============================================================================
def _attr_or_false(df: pd.DataFrame, name: str) -> pd.Series:
    s = df.attrs.get(name)
    if s is None:
        return pd.Series(False, index=df.index)
    return s.reindex(df.index).fillna(False).astype(bool)


def _ensure_engines(df: pd.DataFrame, params: Dict) -> Dict[str, pd.Series]:
    cache = _ENGINE_CACHE.setdefault(id(df), {})
    cache_key = ("v2", id(df),
                 tuple(sorted((k, v) for k, v in params.items()
                              if isinstance(v, (int, float, str, bool)))))
    if cache.get("_key") == cache_key and "p_b2bBull" in cache:
        return cache
    cache.clear()
    cache["_key"] = cache_key

    p = params
    conf = _conf(df)
    n = len(df)
    tfSec = float(p["tfSec"])

    # ------------------------------------------------------------------
    # Raw upstream detection signals (STUBBED — must be injected by caller).
    # These come from the TNT zone state machine, Napalm/Charge scanner,
    # Return-to-TNT, CONT cluster, PBJ supertrend, WBUSH heavy-combo, etc.
    # ------------------------------------------------------------------
    det_bullTNT = _attr_or_false(df, "det_bullTNT")
    det_bearTNT = _attr_or_false(df, "det_bearTNT")
    det_bullNapalm = _attr_or_false(df, "det_bullNapalm")
    det_bearNapalm = _attr_or_false(df, "det_bearNapalm")
    det_bullRetTNT = _attr_or_false(df, "det_bullRetTNT")
    det_bearRetTNT = _attr_or_false(df, "det_bearRetTNT")
    det_contBull = _attr_or_false(df, "det_contBull")
    det_contBear = _attr_or_false(df, "det_contBear")

    # PBJ supertrend reversal (Pine: requires Supertrend state machine).
    det_pbjBull = _attr_or_false(df, "det_pbjBull")
    det_pbjBear = _attr_or_false(df, "det_pbjBear")

    # WBUSH heavy combo state.
    sig_WBUSH_Bull = _attr_or_false(df, "sig_WBUSH_Bull")
    sig_WBUSH_Bear = _attr_or_false(df, "sig_WBUSH_Bear")
    sig_WBUSH_Neutral = _attr_or_false(df, "sig_WBUSH_Neutral")

    # CS1 FVG combo (HV-FVG / TNT zone overlap).
    det_cs1_Bull = _attr_or_false(df, "det_cs1_Bull")
    det_cs1_Bear = _attr_or_false(df, "det_cs1_Bear")

    # Session first-bar index (state tracker).
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

    # ------------------------------------------------------------------
    # Composite Tier 1 detections — all rebuilt from raw det_* signals.
    # ------------------------------------------------------------------
    # det_rcRNBull/Bear (Return + Napalm) and det_rcTRBull/Bear (TNT+Return)
    # — same-bar AND between det_bullRetTNT and det_bullNapalm/TNT.
    det_rcRNBull = det_bullRetTNT & _nz_b(det_bullNapalm.shift(-1).fillna(False)) | (det_bullRetTNT.shift(1).fillna(False).astype(bool) & det_bullNapalm)
    det_rcRNBear = det_bearRetTNT & _nz_b(det_bearNapalm.shift(-1).fillna(False)) | (det_bearRetTNT.shift(1).fillna(False).astype(bool) & det_bearNapalm)
    # The above is an approximation; canonical Pine uses bar-aligned RET[1] + NPM.
    # Allow caller to override.
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

    # det_pnBull/Bear = PBJ + Napalm; det_ptBull/Bear = PBJ + TNT
    det_pnBull = det_pbjBull & det_bullNapalm
    det_pnBear = det_pbjBear & det_bearNapalm
    det_ptBull = det_pbjBull & det_bullTNT
    det_ptBear = det_pbjBear & det_bearTNT
    # PBJ + Return (Tier 2 RC)
    det_prBull = det_pbjBull & det_bullRetTNT
    det_prBear = det_pbjBear & det_bearRetTNT

    # pnGate / ptGate — Pine uses these to suppress when over-correlated;
    # caller may inject via df.attrs[...]. Default = True (passthrough).
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

    # det_fuseBull/Bear — Napalm → TNT → CONT within SUDDEN_PROX bars.
    # Allow injection; default = simple proximity scan on raw det signals.
    def _fuse(npm: pd.Series, tnt: pd.Series, cont: pd.Series, prox: int) -> pd.Series:
        a_npm = _nz_b(npm).to_numpy()
        a_tnt = _nz_b(tnt).to_numpy()
        a_cnt = _nz_b(cont).to_numpy()
        out = np.zeros(n, dtype=bool)
        for i in range(n):
            if not a_cnt[i]:
                continue
            # Look back up to prox bars for TNT, then back further for NPM.
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

    # det_catBull/Bear — Napalm AND CS1 on same bar.
    det_catBull = det_bullNapalm & det_cs1_Bull
    det_catBear = det_bearNapalm & det_cs1_Bear

    # det_igniteBull/Bear & ign_tc / ign_nc sub-flavors.
    ign_tc_bull = det_bullTNT & det_contBull
    ign_tc_bear = det_bearTNT & det_contBear
    ign_nc_bull = det_bullNapalm & det_contBull
    ign_nc_bear = det_bearNapalm & det_contBear
    det_igniteBull = ign_tc_bull | ign_nc_bull
    det_igniteBear = ign_tc_bear | ign_nc_bear

    # det_dynamiteBull/Bear — B2B displacement + FAUNA on bar[1] AND bar[2]
    # + bullish/bearish FVG on current bar.
    # Uses dynStdMult.
    disp_rng = _disp_range(df, p["DISP_TYPE"])
    disp_std = _stdev(disp_rng, int(p["DISP_STD_LEN"]))
    dyn_thresh = disp_std * float(p["dynStdMult"])
    dyn_disp_b1 = disp_rng.shift(1) > dyn_thresh.shift(1)
    dyn_disp_b2 = disp_rng.shift(2) > dyn_thresh.shift(2)
    # Same-direction bull color: close[1] > open[1] AND close[2] > open[2]
    bull_b1 = df["close"].shift(1) > df["open"].shift(1)
    bull_b2 = df["close"].shift(2) > df["open"].shift(2)
    bear_b1 = df["close"].shift(1) < df["open"].shift(1)
    bear_b2 = df["close"].shift(2) < df["open"].shift(2)
    bull_fvg = _bull_fvg(df)
    bear_fvg = _bear_fvg(df)
    # FAUNA (USE V5 flavor) computed below in u5_* block; for now stub
    # with df.attrs override or compute inline.
    # We compute FAUNA in the u5 block but DYNAMITE uses it on shifted bars.
    # ---- USE V5 (u5_*) engine (Engine 5) ----
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

    # tv_ta.relativeVolume — STUBBED, inject via df.attrs.
    u5_relVolRatio = df.attrs.get("u5_relVolRatio")
    if u5_relVolRatio is None:
        u5_relVolRatio = pd.Series(np.nan, index=df.index)
    u5_WTC = conf & (u5_relVolRatio > u5_th_wtc) & (u5_relVolRatio <= u5_th_hiro)
    u5_Hiroshima = conf & (u5_relVolRatio > u5_th_hiro)
    u5_Pentagon = conf & (u5_relVolRatio >= u5_th_1x) & (u5_relVolRatio <= u5_th_wtc)

    # Nagasaki — streaming ATH volume (NOT shifted).
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

    # u5_DISP (Engine 5 displacement w/ FVG)
    u5_disp_rng = (df["open"] - df["close"]).abs()
    u5_disp_std = _stdev(u5_disp_rng, int(p["u5_std_len"]))
    u5_disp_thresh_min = u5_disp_std * float(p["u5_std_min"])
    u5_disp_bullFVG = (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["open"].shift(1))
    u5_disp_bearFVG = (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["open"].shift(1))
    u5_DISPBull = conf & (u5_disp_rng.shift(1) > u5_disp_thresh_min.shift(1)) & u5_disp_bullFVG
    u5_DISPBear = conf & (u5_disp_rng.shift(1) > u5_disp_thresh_min.shift(1)) & u5_disp_bearFVG

    # u5_PUP / u5_PPD
    u5_pp_redVol = df["volume"].where(df["close"] < df["open"], 0.0)
    u5_pp_greenVol = df["volume"].where(df["close"] > df["open"], 0.0)
    u5_pp_hiRedVol = _highest(u5_pp_redVol.shift(1), 10)
    u5_pp_hiGreenVol = _highest(u5_pp_greenVol.shift(1), 10)
    u5_PUP = conf & (((df["close"] - df["open"]) / df["open"]) * 100 > 3.0) & (df["volume"] > u5_pp_hiRedVol)
    u5_PPD = conf & (((df["open"] - df["close"]) / df["open"]) * 100 > 3.0) & (df["volume"] > u5_pp_hiGreenVol)

    # u5_CS1 (FVG combo subset) — defaults to det_cs1_*
    u5_CS1_Bull = det_cs1_Bull
    u5_CS1_Bear = det_cs1_Bear

    # ---- DYNAMITE (FAUNA on bar[1] AND bar[2] required + B2B displacement) ----
    fauna_bull_b1 = _nz_b(u5_FAUNABull.shift(1))
    fauna_bull_b2 = _nz_b(u5_FAUNABull.shift(2))
    fauna_bear_b1 = _nz_b(u5_FAUNABear.shift(1))
    fauna_bear_b2 = _nz_b(u5_FAUNABear.shift(2))
    det_dynamiteBull = conf & dyn_disp_b1 & dyn_disp_b2 & bull_b1 & bull_b2 & fauna_bull_b1 & fauna_bull_b2 & bull_fvg
    det_dynamiteBear = conf & dyn_disp_b1 & dyn_disp_b2 & bear_b1 & bear_b2 & fauna_bear_b1 & fauna_bear_b2 & bear_fvg

    # ------------------------------------------------------------------
    # sig_rcNTBull / sig_rcNTBear — RC NPM+TNT
    # Pine: det_bullNapalm AND det_bullTNT[1]
    # ------------------------------------------------------------------
    sig_rcNTBull = det_bullNapalm & _nz_b(det_bullTNT.shift(1)) & bool(p["en_rcNTBull"])
    sig_rcNTBear = det_bearNapalm & _nz_b(det_bearTNT.shift(1)) & bool(p["en_rcNTBear"])

    # supp_bullNPM / supp_bullTNT — used to suppress duplicate fires.
    supp_bullNPM = sig_rcNTBull | det_rcRNBull | det_pnBull
    supp_bullTNT = sig_rcNTBull | det_rcTRBull | det_ptBull
    supp_bearNPM = sig_rcNTBear | det_rcRNBear | det_pnBear
    supp_bearTNT = sig_rcNTBear | det_rcTRBear | det_ptBear

    # ------------------------------------------------------------------
    # Tier 1 plots (NO gate in v2 LATEST — that's a v3 feature)
    # ------------------------------------------------------------------
    # Need: prev-bar Napalm + bar_index-2 >= sessionFirstBarIdx.
    bar_idx_s = pd.Series(bar_idx, index=df.index)
    b2b_session_ok = (bar_idx_s - 2) >= sessionFirstBarIdx
    p_b2bBull = det_bullNapalm & ~supp_bullNPM & _nz_b(det_bullNapalm.shift(1)) & b2b_session_ok & bool(p["en_b2bBull"])
    p_b2bBear = det_bearNapalm & ~supp_bearNPM & _nz_b(det_bearNapalm.shift(1)) & b2b_session_ok & bool(p["en_b2bBear"])

    p_pnBull = det_pnBull & pnGateBull & bool(p["en_pnBull"])
    p_pnBear = det_pnBear & pnGateBear & bool(p["en_pnBear"])
    p_ptBull = det_ptBull & ptGateBull & bool(p["en_ptBull"])
    p_ptBear = det_ptBear & ptGateBear & bool(p["en_ptBear"])
    p_fuseBull = det_fuseBull & bool(p["en_fuseBull"])
    p_fuseBear = det_fuseBear & bool(p["en_fuseBear"])
    p_catBull = det_catBull & bool(p["en_catBull"])
    p_catBear = det_catBear & bool(p["en_catBear"])
    p_ignBull = det_igniteBull & bool(p["en_ignBull"])
    p_ignBear = det_igniteBear & bool(p["en_ignBear"])
    p_dynBull = det_dynamiteBull & bool(p["en_dynBull"])
    p_dynBear = det_dynamiteBear & bool(p["en_dynBear"])

    # IGNITE TNT+CONT / NPM+CONT sub-flavors as plotted in Pine.
    p_ign_tc_bull = p_ignBull & ign_tc_bull
    p_ign_tc_bear = p_ignBear & ign_tc_bear
    p_ign_nc_bull = p_ignBull & ign_nc_bull
    p_ign_nc_bear = p_ignBear & ign_nc_bear

    # ------------------------------------------------------------------
    # Tier 2 (Enriched) plots — raw det + ≥ 1 enrichment co-signal.
    # ------------------------------------------------------------------
    enrich_set_bull = u5_RVOL1xB | u5_GrandSlam | u5_PUP | det_cs1_Bull | u5_FAUNABull | u5_WMD | u5_HV1000 | det_dynamiteBull
    enrich_set_bear = u5_RVOL1xR | u5_MOAB | u5_PPD | det_cs1_Bear | u5_FAUNABear | u5_WMD | u5_HV1000 | det_dynamiteBear
    # _N variants are bar[0] same-bar, _N1 variants are bar[1].
    enrichBull_N = enrich_set_bull
    enrichBear_N = enrich_set_bear
    enrichBull_N1 = _nz_b(enrich_set_bull.shift(1))
    enrichBear_N1 = _nz_b(enrich_set_bear.shift(1))

    p_t2tntBull = det_bullTNT & ~supp_bullTNT & enrichBull_N & bool(p["en_t2tntBull"])
    p_t2tntBear = det_bearTNT & ~supp_bearTNT & enrichBear_N & bool(p["en_t2tntBear"])
    p_t2npmBull = det_bullNapalm & ~supp_bullNPM & enrichBull_N1 & bool(p["en_t2npmBull"])
    p_t2npmBear = det_bearNapalm & ~supp_bearNPM & enrichBear_N1 & bool(p["en_t2npmBear"])
    p_t2contBull = det_contBull & enrichBull_N & bool(p["en_t2contBull"])
    p_t2contBear = det_contBear & enrichBear_N & bool(p["en_t2contBear"])
    p_t2trBull = det_rcTRBull & enrichBull_N & bool(p["en_t2trBull"])
    p_t2trBear = det_rcTRBear & enrichBear_N & bool(p["en_t2trBear"])
    p_t2rnBull = det_rcRNBull & enrichBull_N1 & bool(p["en_t2rnBull"])
    p_t2rnBear = det_rcRNBear & enrichBear_N1 & bool(p["en_t2rnBear"])
    p_t2prBull = det_prBull & enrichBull_N & bool(p["en_t2prBull"])
    p_t2prBear = det_prBear & enrichBear_N & bool(p["en_t2prBear"])

    # ------------------------------------------------------------------
    # Density 1/2/3 — X visual events in Y bars with no overlap window
    # (re-arm tracker). Pine walker uses sessionFirstBarIdx and per-side
    # last-fired-bar (d?br/d?sr) gates.
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
        """X distinct visual events in Y bars; tracker prevents overlap."""
        vis = _nz_b(visual).to_numpy()
        out = np.zeros(n, dtype=bool)
        last_used_bar = -1  # last "bar - 1 - i" used as a visual event
        for i in range(n):
            if (bar_idx[i] - 2) < session_first_bar[i]:
                continue
            count = 0
            used = -1
            for k in range(Y):
                idx = bar_idx[i] - 1 - k
                if idx < session_first_bar[i] or idx < 0:
                    break
                if vis[idx] and idx > last_used_bar:
                    count += 1
                    if count == 1:
                        used = idx
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
    # UU / UUU / UUUU + TNT ANY — RVOL streak + TNTOD signal in window.
    # ------------------------------------------------------------------
    # u_path_* uses paths pA/pB/pC/pE plus pG (≥N distinct qualifiers).
    # We approximate pG with the simple streak length on u5_bb_baseBull/Bear
    # qualified by normPrice ≥ 1x.
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

    # tntAnyBullN/N1/N2 = any TNTOD bull signal in window.
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
    tntAnyBull1 = tntAny_bull_atK(1)
    tntAnyBull2 = tntAny_bull_atK(1) | tntAny_bull_atK(2)
    tntAnyBull3 = tntAnyBull2 | tntAny_bull_atK(3)
    tntAnyBull4 = tntAnyBull3 | tntAny_bull_atK(4)
    tntAnyBear1 = tntAny_bear_atK(1)
    tntAnyBear2 = tntAnyBear1 | tntAny_bear_atK(2)
    tntAnyBear3 = tntAnyBear2 | tntAny_bear_atK(3)
    tntAnyBear4 = tntAnyBear3 | tntAny_bear_atK(4)

    p_uuBull = u_pathBull2 & tntAnyBull2 & bool(p["en_uu_bull"])
    p_uuBear = u_pathBear2 & tntAnyBear2 & bool(p["en_uu_bear"])
    p_uuuBull = u_pathBull3 & tntAnyBull3 & bool(p["en_uuu_bull"])
    p_uuuBear = u_pathBear3 & tntAnyBear3 & bool(p["en_uuu_bear"])
    p_uuuuBull = u_pathBull4 & tntAnyBull4 & bool(p["en_uuuu_bull"])
    p_uuuuBear = u_pathBear4 & tntAnyBear4 & bool(p["en_uuuu_bear"])

    # ------------------------------------------------------------------
    # WBUSH composites.
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
        # Tier 2 Enriched
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
        # UU/UUU/UUUU
        "p_uuBull": p_uuBull, "p_uuBear": p_uuBear,
        "p_uuuBull": p_uuuBull, "p_uuuBear": p_uuuBear,
        "p_uuuuBull": p_uuuuBull, "p_uuuuBear": p_uuuuBear,
        # WBUSH
        "p_wbushBull": p_wbushBull, "p_wbushBear": p_wbushBear,
        "p_wbushNeutral": p_wbushNeutral,
        # Aggregates (useful for downstream)
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


# ============================================================================
# Stubbed inputs — Pine-only intrinsics required. Caller must inject these
# pre-computed series via ``df.attrs[<name>]`` before calling any detection.
# ============================================================================
STUBBED: Dict[str, str] = {
    # ---- TNT zone scanner (state machine over price/zone arrays) ----
    "det_bullTNT": "Raw TNT bullish detection from TNT 1.0/2.0 zone arrays + super-TNT. Pine: lines 690-695. Inject via df.attrs.",
    "det_bearTNT": "Raw TNT bearish detection. Inject via df.attrs.",
    "det_bullNapalm": "Raw Napalm/Charge bullish detection from TNT zone scanner. Pine: line 692. Inject via df.attrs.",
    "det_bearNapalm": "Raw Napalm/Charge bearish detection. Inject via df.attrs.",
    "det_bullRetTNT": "Raw Return-to-TNT (and TNT 2.0 super) bullish. Inject via df.attrs.",
    "det_bearRetTNT": "Raw Return-to-TNT bearish. Inject via df.attrs.",
    "det_contBull": "Raw Continuous-cluster bullish detection. Inject via df.attrs.",
    "det_contBear": "Raw Continuous-cluster bearish detection. Inject via df.attrs.",
    # ---- PBJ Supertrend reversal ----
    "det_pbjBull": "PBJ supertrend reversal (bull). Requires bar-by-bar Supertrend state. Inject via df.attrs.",
    "det_pbjBear": "PBJ supertrend reversal (bear). Inject via df.attrs.",
    # ---- CS1 (FVG combo / HV-FVG) ----
    "det_cs1_Bull": "CS1 FVG combo bullish (HV-FVG / TNT zone overlap). Pine: external from HVD module. Inject via df.attrs.",
    "det_cs1_Bear": "CS1 FVG combo bearish. Inject via df.attrs.",
    # ---- WBUSH heavy combo state ----
    "sig_WBUSH_Bull": "WBUSH bullish state (any of 5 Heavy Combo Bulls). Pine: external heavy-combo module. Inject via df.attrs.",
    "sig_WBUSH_Bear": "WBUSH bearish state. Inject via df.attrs.",
    "sig_WBUSH_Neutral": "WBUSH neutral state. Inject via df.attrs.",
    # ---- tv_ta.relativeVolume (Engine 5) ----
    "u5_relVolRatio": "tv_ta.relativeVolume(reg) ratio used by u5_WTC/u5_Hiroshima/u5_Pentagon. Inject via df.attrs.",
    # ---- Optional explicit overrides for composite raw signals ----
    "det_rcTRBull": "Optional override for RC TNT+RET bull (default: det_bullTNT & det_bullRetTNT).",
    "det_rcTRBear": "Optional override for RC TNT+RET bear.",
    "det_rcRNBull_override": "Optional override for RC RET+NPM bull (default: det_bullRetTNT & det_bullNapalm).",
    "det_rcRNBear_override": "Optional override for RC RET+NPM bear.",
    "det_fuseBull": "Optional override for FUSE bull (default: sequential proximity scan).",
    "det_fuseBear": "Optional override for FUSE bear.",
    "pnGateBull": "Optional PBJ+NPM gate (default True).",
    "pnGateBear": "Optional PBJ+NPM gate (default True).",
    "ptGateBull": "Optional PBJ+TNT gate (default True).",
    "ptGateBear": "Optional PBJ+TNT gate (default True).",
}


# ============================================================================
# State machines — built into _ensure_engines; exposed here as wrappers.
# ============================================================================
@dataclass
class SessionTracker:
    """sessionFirstBarIdx tracker — built into _ensure_engines."""
    name: str = "SessionTracker"


@dataclass
class B2BWalker:
    """B2B Napalm bar-by-bar walker (uses session-first-bar gate)."""
    name: str = "B2BWalker"


@dataclass
class DensityWalker:
    """Density 1/2/3 X-in-Y window walker with overlap re-arm."""
    name: str = "DensityWalker"


STATE_MACHINES: Dict[str, type] = {
    "SessionTracker": SessionTracker,
    "B2BWalker": B2BWalker,
    "DensityWalker": DensityWalker,
}


# ============================================================================
# DETECTIONS registry — name → detect_* function.
# Names mirror Pine plot titles (text/title) so the harness can round-trip
# with the validator.
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
}


if __name__ == "__main__":
    print(f"DETECTIONS: {len(DETECTIONS)}")
    print(f"STUBBED engine notes: {len(STUBBED)}")
    print(f"STATE_MACHINES: {len(STATE_MACHINES)}")
    print("First 5 detection names:")
    for nname in list(DETECTIONS)[:5]:
        print("  ", nname)
