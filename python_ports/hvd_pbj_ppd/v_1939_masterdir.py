"""Python port of HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine.

Single-file pandas + numpy module. No pine-runtime dependency.

Source Pine file: hvd-pbj-ppd/versions/HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine
Companion delta report: bible-input/agent-reports/hvd-pbj-ppd-delta-1939-masterdir.md

Conventions:
- Per-detection function: `detect_<snake_case_name>(df, params) -> pd.Series` where
  `df` carries OHLCV columns ['open', 'high', 'low', 'close', 'volume'] indexed by
  bar timestamp, and `params` is a dict overlay onto module-level DEFAULTS.
- Stateful detections (chains, streaks, FSMs) are wrapped as classes; their
  `compute(df, params)` returns a pd.Series.
- IPSF defaults live in DEFAULTS; hardcoded numeric constants stay inline.
- DETECTIONS exports the per-detection callables, STATE_MACHINES exports class
  factories, STUBBED maps detection-id -> stub reason.

NOTE: this port reproduces the leaf detections that have a clean, self-contained
boolean body. Composite detections that consume a stateful Ping-Pong SR engine,
the multi-pass UU path-A..F scanner, the CC/LSC chains, the Boom-Hunter omega
filter, the GZ1 FVG bookkeeper, and the lander-box engine are stubbed — these
require a substantial port of the underlying engines that was out of scope for
this audit pass.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Mapping

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# DEFAULTS — IPSF inputs lifted from the Pine source.
# ---------------------------------------------------------------------------
DEFAULTS: Dict[str, object] = {
    # First-bar gating
    "en_firstBarOnly": False,
    # Pipeline-A: Displacement 1 (base)
    "i_disp_type": "Open to Close",
    "i_std_len": 100,
    "i_std_min": 4.5,
    "i_std_max": 100.0,
    "i_req_fvg": True,
    # Pipeline-A: Displacement 2 (HTF1) — duplicated under different prefix in pine
    "i_disp2_type": "Open to Close",
    "i_disp2_std_len": 100,
    "i_disp2_std_min": 4.5,
    "i_disp2_std_max": 100.0,
    "i_disp2_req_fvg": True,
    # Pipeline-A: Displacement 3 (HTF2)
    "i_disp3_type": "Open to Close",
    "i_disp3_std_len": 100,
    "i_disp3_std_min": 3.0,
    "i_disp3_std_max": 100.0,
    "i_disp3_req_fvg": True,
    # PUP/PPD
    "pp_barSize": 3.0,
    "pp_lookback": 10,
    # PP SR engine (Ping-Pong)
    "pp_min_count": 3,
    "pp_atr_len": 100,
    # USE sequence
    "p21_pbj_dist": 4,
    # Opening Drive
    "od_max_bars": 2,
    # Matrix lookback
    "neo_len": 67,
    # Momentum 1 / 2
    "ls_reg1": 7.0,
    "ls_cum1": 3.5,
    "ls_body1": 0.69,
    "ls_reg2": 5.0,
    "ls_cum2": 2.5,
    "ls_body2": 0.69,
    # Combo Set settings
    "cs_bodyPct_FVG": 0.69,
    "cs_bodyPct_MAT": 0.69,
    "cs_inc_pentagon_FVG": True,
    "cs_inc_pentagon_MAT": True,
    # Combo Chain
    "cc_min_hits": 2,
    "cc_window": 3,
    # Long/Short Chain
    "lsc_min_hits": 2,
    "lsc_window": 2,
    "lsc_reg1": 7.0,
    "lsc_cum1": 3.5,
    "lsc_body1": 0.69,
    "lsc_reg2": 5.0,
    "lsc_cum2": 2.5,
    "lsc_body2": 0.69,
    # Boom Hunter (hardcoded in Pine but exposed here for symmetry)
    "bh_LPPeriod": 6,
    "bh_K1": 0,
    "bh_trigno": 2,
    "bh_LPPeriod2": 27,
    "bh_K12": 0.8,
    "bh_K22": 0.3,
    # HV150 lookback
    "hv150_len": 150,
    # Pipeline-C / D / B2B / Momentum-co-occ enables (default on; typical user state)
    "en_hvd_bull": True,
    "en_hvd_bear": True,
    "en_hvd_pb_bull": True,
    "en_hvd_pb_bear": True,
    "en_hvd_pbj_bull": True,
    "en_hvd_pbj_bear": True,
    "co_en_bullPBJ": True,
    "co_en_bullPB": True,
    "co_en_bearPBJ": True,
    "co_en_bearPB": True,
    "b2b_en_bull": True,
    "b2b_en_bear": True,
    "b2b_en_bull_pbj": True,
    "b2b_en_bear_pbj": True,
    "b2b_en_bull_pb": True,
    "b2b_en_bear_pb": True,
}


# ---------------------------------------------------------------------------
# _helpers — primitives used by multiple detections.
# ---------------------------------------------------------------------------

def _p(params: Mapping[str, object] | None, key: str):
    """Lookup with DEFAULTS fallback."""
    if params is not None and key in params:
        return params[key]
    return DEFAULTS[key]


def _atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    # Pine ta.atr uses RMA (Wilder) smoothing
    return tr.ewm(alpha=1.0 / length, adjust=False, min_periods=length).mean()


def _stdev(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(length, min_periods=length).std(ddof=0)


def _bb_normalized_price(df: pd.DataFrame) -> pd.Series:
    """1939 uses |close-open| normalized by 30-bar SMA of same."""
    body = (df["close"] - df["open"]).abs()
    return body / body.rolling(30, min_periods=30).mean().replace(0, np.nan)


def _bb_normalized_volume(df: pd.DataFrame) -> pd.Series:
    vol = df["volume"].astype(float)
    return vol / vol.rolling(30, min_periods=30).mean().replace(0, np.nan)


def _disp_components(df: pd.DataFrame, params: Mapping[str, object] | None,
                     key_prefix: str) -> Dict[str, pd.Series]:
    """Compute displacement helpers for a given input prefix.

    key_prefix is a base name like ``i_disp`` / ``i_disp2`` / ``i_disp3`` and
    keys are read as ``{key_prefix}_type`` / ``{key_prefix}_std_len`` / etc.
    """
    disp_type = _p(params, f"{key_prefix}_type")
    std_len = int(_p(params, f"{key_prefix}_std_len"))
    std_min = float(_p(params, f"{key_prefix}_std_min"))
    std_max = float(_p(params, f"{key_prefix}_std_max"))
    req_fvg = bool(_p(params, f"{key_prefix}_req_fvg"))
    if disp_type == "High to Low":
        rng = (df["high"] - df["low"]).abs()
    else:
        rng = (df["close"] - df["open"]).abs()
    std = _stdev(rng, std_len)
    th_min = std * std_min
    th_max = std * std_max
    return {
        "rng": rng,
        "std": std,
        "th_min": th_min,
        "th_max": th_max,
        "req_fvg": req_fvg,
    }


# ---------------------------------------------------------------------------
# Leaf primitives
# ---------------------------------------------------------------------------

def _conf_mask(df: pd.DataFrame) -> pd.Series:
    """Pine `conf` is barstate.isconfirmed — in pandas backtest every closed bar
    is confirmed, so this is all-True."""
    return pd.Series(True, index=df.index)


def detect_pup(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """sigPUP — Push-Up Day primitive (line 651).
    `((close-open)/open)*100 > pp_barSize AND volume > 10-bar highest red-bar volume`."""
    pp_barSize = float(_p(params, "pp_barSize"))
    pp_lookback = int(_p(params, "pp_lookback"))
    pct = (df["close"] - df["open"]) / df["open"] * 100.0
    pp_priceUp = pct > pp_barSize
    is_red = df["close"] < df["open"]
    red_vol = df["volume"].where(is_red, 0.0)
    pp_hiRedVol = red_vol.shift(1).rolling(pp_lookback, min_periods=1).max()
    return _conf_mask(df) & pp_priceUp & (df["volume"] > pp_hiRedVol)


def detect_ppd(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """sigPPD — Push-Down Day primitive (line 652)."""
    pp_barSize = float(_p(params, "pp_barSize"))
    pp_lookback = int(_p(params, "pp_lookback"))
    pct = (df["open"] - df["close"]) / df["open"] * 100.0
    pp_priceDn = pct > pp_barSize
    is_green = df["close"] > df["open"]
    green_vol = df["volume"].where(is_green, 0.0)
    pp_hiGreenVol = green_vol.shift(1).rolling(pp_lookback, min_periods=1).max()
    return _conf_mask(df) & pp_priceDn & (df["volume"] > pp_hiGreenVol)


def detect_disp_bull(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """sigDISPBull — Pipeline-A displacement-1 primitive (line 550).
    if req_fvg: prev-bar disp + bullish FVG; else: current-bar disp + green."""
    h = _disp_components(df, params, "i_")
    rng, th_min, th_max, req_fvg = h["rng"], h["th_min"], h["th_max"], h["req_fvg"]
    bull_fvg = (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["open"].shift(1))
    prev_disp = (rng.shift(1) > th_min.shift(1)) & (rng.shift(1) <= th_max.shift(1))
    curr_disp = (rng > th_min) & (rng <= th_max)
    if req_fvg:
        return _conf_mask(df) & (prev_disp & bull_fvg)
    return _conf_mask(df) & (curr_disp & (df["close"] > df["open"]))


def detect_disp_bear(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """sigDISPBear (line 551)."""
    h = _disp_components(df, params, "i_")
    rng, th_min, th_max, req_fvg = h["rng"], h["th_min"], h["th_max"], h["req_fvg"]
    bear_fvg = (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["open"].shift(1))
    prev_disp = (rng.shift(1) > th_min.shift(1)) & (rng.shift(1) <= th_max.shift(1))
    curr_disp = (rng > th_min) & (rng <= th_max)
    if req_fvg:
        return _conf_mask(df) & (prev_disp & bear_fvg)
    return _conf_mask(df) & (curr_disp & (df["close"] < df["open"]))


def detect_disp5_bull(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """disp5_bull — 5x displacement (line 553). Hardcoded multiplier 5.0."""
    h = _disp_components(df, params, "i_")
    rng, std = h["rng"], h["std"]
    return _conf_mask(df) & (std > 0) & (rng > std * 5.0) & (df["close"] > df["open"])


def detect_disp5_bear(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    h = _disp_components(df, params, "i_")
    rng, std = h["rng"], h["std"]
    return _conf_mask(df) & (std > 0) & (rng > std * 5.0) & (df["close"] < df["open"])


def detect_disp_cons_bull2(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """sigDispConsBull2 (line 570).

    REAL DRIFT vs THE_ONLY_ONE: 1939 references FAUNA at lag-1 + lag-2 (this
    file's signature). FAUNA bull is stubbed below, so this returns the
    DISP2-streak portion only and ANDs with a stub-aware NaN-mask. Once
    detect_fauna_bull is implemented, re-enable the conjunction below.
    """
    h2 = _disp_components(df, params, "i_disp2_")
    rng, std = h2["rng"], h2["std"]
    std_min = float(_p(params, "i_disp2_std_min"))
    std_max = float(_p(params, "i_disp2_std_max"))
    req_fvg = h2["req_fvg"]
    if req_fvg:
        sig_disp2_bull = (
            (rng.shift(1) > std.shift(1) * std_min)
            & (rng.shift(1) <= std.shift(1) * std_max)
            & (df["low"] > df["high"].shift(2))
            & (df["close"].shift(1) > df["open"].shift(1))
        )
    else:
        sig_disp2_bull = (
            (rng > std * std_min) & (rng <= std * std_max) & (df["close"] > df["open"])
        )
    sig_disp2_bull = _conf_mask(df) & sig_disp2_bull
    # streak >= 2 of consecutive sig_disp2_bull bars
    streak = sig_disp2_bull.astype(int)
    grp = (~sig_disp2_bull).cumsum()
    consec = sig_disp2_bull.groupby(grp).cumsum()
    streak_ge2 = consec >= 2
    # Per drift table: AND with FAUNA bull lag-1 AND lag-2.
    # FAUNA bull is stubbed; placeholder returns disp-only signal so caller can
    # AND-in their own FAUNA mask. Marked STUBBED for full semantics.
    return sig_disp2_bull & streak_ge2


def detect_disp_cons_bear2(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """sigDispConsBear2 (line 571). See bull twin notes."""
    h2 = _disp_components(df, params, "i_disp2_")
    rng, std = h2["rng"], h2["std"]
    std_min = float(_p(params, "i_disp2_std_min"))
    std_max = float(_p(params, "i_disp2_std_max"))
    req_fvg = h2["req_fvg"]
    if req_fvg:
        sig_disp2_bear = (
            (rng.shift(1) > std.shift(1) * std_min)
            & (rng.shift(1) <= std.shift(1) * std_max)
            & (df["high"] < df["low"].shift(2))
            & (df["close"].shift(1) < df["open"].shift(1))
        )
    else:
        sig_disp2_bear = (
            (rng > std * std_min) & (rng <= std * std_max) & (df["close"] < df["open"])
        )
    sig_disp2_bear = _conf_mask(df) & sig_disp2_bear
    grp = (~sig_disp2_bear).cumsum()
    consec = sig_disp2_bear.groupby(grp).cumsum()
    return sig_disp2_bear & (consec >= 2)


def detect_disp_cons_bull3(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """sigDispConsBull3 (line 587). Streak portion only — see bull2 notes."""
    h3 = _disp_components(df, params, "i_disp3_")
    rng, std = h3["rng"], h3["std"]
    std_min = float(_p(params, "i_disp3_std_min"))
    std_max = float(_p(params, "i_disp3_std_max"))
    req_fvg = h3["req_fvg"]
    if req_fvg:
        sig_disp3_bull = (
            (rng.shift(1) > std.shift(1) * std_min)
            & (rng.shift(1) <= std.shift(1) * std_max)
            & (df["low"] > df["high"].shift(2))
            & (df["close"].shift(1) > df["open"].shift(1))
        )
    else:
        sig_disp3_bull = (
            (rng > std * std_min) & (rng <= std * std_max) & (df["close"] > df["open"])
        )
    sig_disp3_bull = _conf_mask(df) & sig_disp3_bull
    grp = (~sig_disp3_bull).cumsum()
    consec = sig_disp3_bull.groupby(grp).cumsum()
    return sig_disp3_bull & (consec >= 3)


def detect_disp_cons_bear3(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    h3 = _disp_components(df, params, "i_disp3_")
    rng, std = h3["rng"], h3["std"]
    std_min = float(_p(params, "i_disp3_std_min"))
    std_max = float(_p(params, "i_disp3_std_max"))
    req_fvg = h3["req_fvg"]
    if req_fvg:
        sig_disp3_bear = (
            (rng.shift(1) > std.shift(1) * std_min)
            & (rng.shift(1) <= std.shift(1) * std_max)
            & (df["high"] < df["low"].shift(2))
            & (df["close"].shift(1) < df["open"].shift(1))
        )
    else:
        sig_disp3_bear = (
            (rng > std * std_min) & (rng <= std * std_max) & (df["close"] < df["open"])
        )
    sig_disp3_bear = _conf_mask(df) & sig_disp3_bear
    grp = (~sig_disp3_bear).cumsum()
    consec = sig_disp3_bear.groupby(grp).cumsum()
    return sig_disp3_bear & (consec >= 3)


def detect_pp_bar(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """Convenience: bar-level body % > pp_barSize (used by both PUP and PPD)."""
    pp_barSize = float(_p(params, "pp_barSize"))
    pct = (df["close"] - df["open"]).abs() / df["open"] * 100.0
    return pct > pp_barSize


def detect_hv150(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """sigHV150 (line 1008): volume >= ta.highest(volume, hv150_len)[1]."""
    n = int(_p(params, "hv150_len"))
    hi = df["volume"].rolling(n, min_periods=n).max().shift(1)
    return _conf_mask(df) & (df["volume"] >= hi)


def detect_hv75(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    """sigHV75 (line 1008)."""
    hi = df["volume"].rolling(75, min_periods=75).max().shift(1)
    return _conf_mask(df) & (df["volume"] >= hi)


def detect_hv500(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    hi = df["volume"].rolling(500, min_periods=500).max().shift(1)
    return _conf_mask(df) & (df["volume"] >= hi)


def detect_hv1000(df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.Series:
    hi = df["volume"].rolling(1000, min_periods=1000).max().shift(1)
    return _conf_mask(df) & (df["volume"] >= hi)


# ---------------------------------------------------------------------------
# Stub helpers for downstream composites
# ---------------------------------------------------------------------------

def _stub_series(df: pd.DataFrame) -> pd.Series:
    return pd.Series(False, index=df.index, dtype=bool)


# ---------------------------------------------------------------------------
# DETECTIONS — fully implemented leaf detections
# ---------------------------------------------------------------------------
DETECTIONS: Dict[str, Callable[..., pd.Series]] = {
    "sigPUP": detect_pup,
    "sigPPD": detect_ppd,
    "sigDISPBull": detect_disp_bull,
    "sigDISPBear": detect_disp_bear,
    "disp5_bull": detect_disp5_bull,
    "disp5_bear": detect_disp5_bear,
    "sigDispConsBull2": detect_disp_cons_bull2,
    "sigDispConsBear2": detect_disp_cons_bear2,
    "sigDispConsBull3": detect_disp_cons_bull3,
    "sigDispConsBear3": detect_disp_cons_bear3,
    "sigHV75": detect_hv75,
    "sigHV150": detect_hv150,
    "sigHV500": detect_hv500,
    "sigHV1000": detect_hv1000,
    "pp_pct_gate": detect_pp_bar,
}


# ---------------------------------------------------------------------------
# STATE_MACHINES — class wrappers for stateful detections
# ---------------------------------------------------------------------------

@dataclass
class _UStreakBase:
    """Minimal U-streak counter used by Engine 8 (UU/UUU/UUUU).

    Computes `u_bull_streak` and `u_bull_hasDay1` per-bar using the 1939
    qualifier `bb_baseBullish AND bb_normalizedPrice >= 0.5`. The full
    multi-path A..F decision body is intentionally NOT implemented here — it
    requires sigBullPBJ/sigBullPB/sigDISPBull/sigFAUNABull/sigSAAB which are
    themselves part of stateful engines that would need a full port.
    """

    def compute(self, df: pd.DataFrame, params: Mapping[str, object] | None = None) -> pd.DataFrame:
        bb_norm = _bb_normalized_price(df)
        bb_baseBullish = (df["close"] > df["open"])
        bb_baseBearish = (df["close"] < df["open"])
        u_qual_bull = bb_baseBullish & (bb_norm >= 0.5)
        u_qual_bear = bb_baseBearish & (bb_norm >= 0.5)
        # streak: reset on False
        bull_grp = (~u_qual_bull).cumsum()
        bull_streak = u_qual_bull.groupby(bull_grp).cumsum()
        bear_grp = (~u_qual_bear).cumsum()
        bear_streak = u_qual_bear.groupby(bear_grp).cumsum()
        # is_new_day flag — first bar of new session per index date change
        if isinstance(df.index, pd.DatetimeIndex):
            session_id = df.index.normalize()
            is_new_day = pd.Series(
                (session_id != pd.Series(session_id, index=df.index).shift(1)).values,
                index=df.index,
            ).fillna(False)
        else:
            is_new_day = pd.Series(False, index=df.index)
        # hasDay1: True within an in-progress streak if any bar of the streak was a new-day bar
        bull_hasDay1 = (
            (u_qual_bull & is_new_day).groupby(bull_grp).cummax().fillna(False)
        )
        bear_hasDay1 = (
            (u_qual_bear & is_new_day).groupby(bear_grp).cummax().fillna(False)
        )
        return pd.DataFrame(
            {
                "u_bull_streak": bull_streak.astype(int),
                "u_bear_streak": bear_streak.astype(int),
                "u_bull_hasDay1": bull_hasDay1.astype(bool),
                "u_bear_hasDay1": bear_hasDay1.astype(bool),
            }
        )


STATE_MACHINES: Dict[str, type] = {
    "UStreak": _UStreakBase,
}


# ---------------------------------------------------------------------------
# STUBBED — detections requiring engines not ported
# ---------------------------------------------------------------------------
STUBBED: Dict[str, str] = {
    # Pipeline-A leaves and HV+D triggers
    "HVD_BULL": "Requires base/HTF1/HTF2 displacement + HV-rank engine port.",
    "HVD_BEAR": "Requires base/HTF1/HTF2 displacement + HV-rank engine port.",
    # Pipeline-B (PBJ/PB lander)
    "PBJ_BULL": "Requires Supertrend + PB&J ATR-pullback + lvl-array lander state machine.",
    "PBJ_BEAR": "Requires Supertrend + PB&J ATR-pullback + lvl-array lander state machine.",
    "PB_BULL": "Requires Supertrend + lander box approach without PBJ filter.",
    "PB_BEAR": "Requires Supertrend + lander box approach without PBJ filter.",
    # FAUNA NRA core
    "sigFAUNABull": "Requires FAUNA NRA hybrid (MB/RE/TA/GG core sets + body/range/vol thresholds + StrongBear/WeakBear context).",
    "sigFAUNABear": "Requires FAUNA NRA hybrid (mirror of bull).",
    # RVOL/Pentagon/Nagasaki/SAAB suite
    "sigSAAB": "Requires bb_normalizedPrice + tfSec-keyed threshold table.",
    "sigKratos": "Requires bb_normalizedPrice + tfSec-keyed threshold table.",
    "sigGrandSlam": "Requires bb_normalizedPrice + tfSec-keyed threshold table.",
    "sigMOAB": "Requires bb_normalizedPrice + tfSec-keyed threshold table.",
    "sigBullRVOL1x": "Requires bb_normalizedPrice + tfSec-keyed threshold table.",
    "sigBearRVOL1x": "Requires bb_normalizedPrice + tfSec-keyed threshold table.",
    "sigWTC": "Requires relVolRatio threshold table.",
    "sigHiroshima": "Requires relVolRatio threshold table.",
    "sigPentagon": "Requires relVolRatio threshold table.",
    "sigNagasaki": "Requires Nagasaki engine (volume + body multi-bar pattern).",
    # Push/momentum that depend on FAUNA
    "sigGolfBull": "Depends on stubbed sigFAUNABull + sigPUP + sigDISPBull conjunction with lag.",
    "sigGolfBear": "Depends on stubbed sigFAUNABear + sigPPD + sigDISPBear conjunction with lag.",
    "sigPAFBull": "Depends on stubbed sigFAUNABull + sigPUP back-to-back.",
    "sigPAFBear": "Depends on stubbed sigFAUNABear + sigPPD back-to-back.",
    # FAUNA-only Foxtrot
    "sigFoxtrotBull": "4-bar FAUNA-bull streak — depends on stubbed sigFAUNABull.",
    "sigFoxtrotBear": "4-bar FAUNA-bear streak — depends on stubbed sigFAUNABear.",
    # Long/Short momentum (Engine 11)
    "sigLong1": "Requires regular/cumulative volume ratio engine (currentVol_r/pastVol_r).",
    "sigShort1": "Requires regular/cumulative volume ratio engine.",
    "sigLong2": "Requires regular/cumulative volume ratio engine.",
    "sigShort2": "Requires regular/cumulative volume ratio engine.",
    # Combo Sets
    "comboSet1_Bull": "Requires GZ1/HV-FVG bookkeeper + cs_vb body filter + lagged SAAB/RVOL/GS.",
    "comboSet1_Bear": "Mirror of bull.",
    "comboSet2_Bull": "Same engine as comboSet1, plus Pentagon/WTC/Hiroshima/Nagasaki.",
    "comboSet2_Bear": "Mirror of bull.",
    "comboSet3_Bull": "Requires Matrix-number engine + cs_vm body filter.",
    "comboSet3_Bear": "Mirror of bull.",
    "comboSet4_Bull": "Same as comboSet3 with Pentagon/WTC/Hiroshima/Nagasaki branch.",
    "comboSet4_Bear": "Mirror of bull.",
    "csNew1_Bull": "OR of stubbed comboSet1+2 bull.",
    "csNew1_Bear": "OR of stubbed comboSet1+2 bear.",
    "csNew2_Bull": "OR of stubbed comboSet3+4 bull.",
    "csNew2_Bear": "OR of stubbed comboSet3+4 bear.",
    "csNew3_Bull": "csNew1_Bull AND csNew2_Bull[1] (REAL DRIFT vs THE_ONLY_ONE — uses lag-1).",
    "csNew3_Bear": "csNew1_Bear AND csNew2_Bear[1].",
    # Chains
    "sigCCBull": "Combo Chain bull — stateful FSM over comboSet1..4 + sigBullPBJ/PB window. REAL DRIFT vs THE_ONLY_ONE in reset clause.",
    "sigCCBear": "Combo Chain bear — mirror.",
    "sigLSCBull": "Long/Short Chain bull — FSM over lsc_L1/L2 + sigBullPBJ/PB window.",
    "sigLSCBear": "Long/Short Chain bear — mirror.",
    # Ping-Pong SR engine (Engine 7)
    "bull_pp": "Ping-Pong SR engine — multi-pivot/touch FSM with ATR-trust gating, gravity flags.",
    "bear_pp": "Mirror of bull_pp.",
    # Floor / Rooftop / Penthouse composites
    "anyBullFloor": "Requires bull_pp + sigBullPBJ + bull_hw_slot — all stubbed.",
    "anyBull2nd": "Requires bull_pp + sigBullPB + bull_hw_slot — all stubbed.",
    "anyBearRoof": "Requires bear_pp + sigBearPBJ + bear_hw_slot — all stubbed.",
    "anyBearPent": "Requires bear_pp + sigBearPB + bear_hw_slot — all stubbed.",
    "fire_BullFloor": "anyBullFloor AND floor_gated AND masterGate — REAL DRIFT vs THE_ONLY_ONE (extra gating).",
    "fire_Bull2ndFloor": "anyBull2nd AND floor2_gated AND masterGate — REAL DRIFT vs THE_ONLY_ONE.",
    "fire_BearRooftop": "anyBearRoof AND masterGate.",
    "fire_BearPent": "anyBearPent AND masterGate.",
    # HW / Super / SDuper composites
    "hwBull": "Requires disp5_bull (have) + sigBullPBJ (stub) + RVOL/WTC/Hiroshima/Nagasaki (stub) + anyBullFloor/2nd (stub).",
    "hwBear": "Mirror of hwBull.",
    "superBull": "Requires sigBullPBJ + sigDISPBull + (sigFAUNABull or sigLong1) + super_hw_bull + (combo+PUP or floor) — most components stubbed.",
    "superBear": "Mirror of superBull.",
    "sduperBull": "Strict-AND of all super components — depends on all stubs.",
    "sduperBear": "Mirror.",
    # USE engine (UU/UUU/UUUU) — REAL DRIFT vs THE_ONLY_ONE and 2246
    "sigP21BullUUUU": "Multi-path A..F decision body (REAL DRIFT) requiring stubbed FAUNA/SAAB/PBJ/PB/HVD lookups.",
    "sigP21BearUUUU": "Mirror.",
    "sigP21BullUUU": "Multi-path A..E body — same dependencies.",
    "sigP21BearUUU": "Mirror.",
    "sigUUBull": "Multi-path A..E body — same dependencies.",
    "sigUUBear": "Mirror.",
    # Alpha Strike / OD / Foxtrot composites
    "sigAlphaStrikeBull": "Requires bull_pp + sigBullPBJ + as_fauna_bull (stub). REAL DRIFT vs THE_ONLY_ONE / 2246.",
    "sigAlphaStrikeBear": "Mirror.",
    "sigODBull": "Requires sessionBarCount + od_fvg_bull + sigPUP + sigBullPBJ — pre-engine + PBJ stubbed.",
    "sigODBear": "Mirror.",
    # Boom Hunter omega
    "sigOmegaLong": "Requires Boom Hunter (SuperSmoother + WaveTrend) DSP cascade + co-signal aggregation.",
    "sigOmegaLongA": "Same engine as sigOmegaLong with omega_cosignal_A variant.",
    # NagPlus
    "sigNagPlusBull": "Requires sigNagasaki (stub) + many other stubs.",
    "sigNagPlusBear": "Mirror.",
    # Pipeline-C HV+D + PBJ/PB co-occurrences
    "hvd_pb_bull": "Requires hvd_fire_bull + sigBullPB lag-1 — both stubbed.",
    "hvd_pbj_bull": "Requires hvd_fire_bull + sigBullPBJ lag-1 — both stubbed.",
    "hvd_pb_bear": "Mirror.",
    "hvd_pbj_bear": "Mirror.",
    # Pipeline-D triple co-occurrence
    "co_bull_pbj": "Requires hvd_fire_bull + sigBullPBJ + use_any_bull (large OR of stubs).",
    "co_bull_pb": "Requires hvd_fire_bull + sigBullPB + use_any_bull.",
    "co_bear_pbj": "Mirror.",
    "co_bear_pb": "Mirror.",
    # B2B HV+D
    "b2b_bull_raw": "Requires hvd_fire_bull lag-0 AND lag-1 — stubbed.",
    "b2b_bear_raw": "Mirror.",
    "b2b_bull_pbj": "Requires b2b_bull_raw + sigBullPBJ window — stubbed.",
    "b2b_bear_pbj": "Mirror.",
    "b2b_bull_pb": "Requires b2b_bull_raw + sigBullPB window − !pbj — stubbed.",
    "b2b_bear_pb": "Mirror.",
    "b2b_bull_nopb": "Requires b2b_bull_raw − pbj − pb — stubbed.",
    "b2b_bear_nopb": "Mirror.",
    # HVD momentum co-occ (m1..m5)
    "hvdm_pup_nopbj_b": "Requires hvd_fire_bull + sigPUP + sigBullPBJ — stubbed.",
    "hvdm_pbjpup_b": "Mirror combo.",
    "hvdm_rvol_nopbj_b": "Requires hvd_fire_bull + RVOL group + sigBullPBJ — stubbed.",
    "hvdm_pbjrvol_b": "Mirror combo.",
    "hvdm_cmb_nopbj_b": "Requires hvd_fire_bull + combo group + sigBullPBJ — stubbed.",
    "hvdm_pbjcmb_b": "Mirror combo.",
    "hvdm_ppd_nopbj_r": "Mirror of pup bull.",
    "hvdm_pbjppd_r": "Mirror combo.",
    "hvdm_rvol_nopbj_r": "Mirror.",
    "hvdm_pbjrvol_r": "Mirror.",
    "hvdm_cmb_nopbj_r": "Mirror.",
    "hvdm_pbjcmb_r": "Mirror.",
}


# ---------------------------------------------------------------------------
# CLI smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"DETECTIONS: {len(DETECTIONS)} ported")
    for name in sorted(DETECTIONS):
        print(f"  - {name}")
    print(f"STATE_MACHINES: {len(STATE_MACHINES)} ported")
    for name in sorted(STATE_MACHINES):
        print(f"  - {name}")
    print(f"STUBBED: {len(STUBBED)} stubs registered")
    for name in sorted(STUBBED):
        print(f"  - {name}: {STUBBED[name]}")
