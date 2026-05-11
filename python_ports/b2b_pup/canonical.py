"""
Python port of B2B_PUP_Combined_v4.32_2026-05-04.pine (1259 lines).

Source Pine: b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine
Predecessor (cross-check only, NOT ported): b2b-pup/versions/B2B_PUP_v4.32.pine

Re-implements every named detection plot in the source as a vectorized
pandas function. Conventions mirror python_ports/hvd_pbj_ppd/the_only_one.py:

  - df is expected to have columns: open, high, low, close, volume.
    Bar order ascending; index may be int or DatetimeIndex.
  - Each detection function returns pd.Series[bool] aligned to df.index.
  - IPSF defaults live in DEFAULTS and may be overridden via the `params`
    dict; per SD-003, IPSF defaults are preserved and NOT flagged as drift.
  - Stateful machinery (TNT zones, Charge ladder, PBJ landing-zone array,
    GZ1 FVG struct array, UU streak counters) are folded into the shared
    _ensure_engines() pass; representative state-machine classes are
    exposed via STATE_MACHINES.
  - Detections that require Pine-only intrinsics (tv_ta.relativeVolume,
    request.security, line/label objects) are STUBBED and registered in
    STUBBED. Callers may inject pre-computed series via df.attrs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd

# ============================================================================
# IPSF DEFAULTS — mirror Pine input.* defaults exactly (SD-003: preserved).
# ============================================================================
DEFAULTS: Dict = {
    # MASTER
    "en_firstBarOnly": False,
    "en_aggregate": True,
    # Pocket Pivot (PUP / PPD)
    "pp_barSize": 3.0,
    "pp_lookback": 10,
    # Displacement (engine C)
    "disp_type": "Open to Close",
    "disp_len": 100,
    "disp_mult": 5.0,
    # PBJ Engine (engine D / "zoo")
    "zoo_ma_type": "VWMA",
    "zoo_ma_len": 5,
    "zoo_use_st": True,
    "zoo_st_period": 10,
    "zoo_st_mult": 2.0,
    "zoo_pbj_ma_period": 20,
    "zoo_pbj_atr_period": 14,
    "zoo_pbj_hh_ll": 25,
    "zoo_pbj_atr_mult": 3.0,
    "zoo_pbj_vol_period": 20,
    "zoo_pbj_vol_mult": 0.1,
    # RVOL (engine E)
    "rv_avgLen": 30,
    "rv_smaLen": 20,
    # HV+D (engine F)
    "hvd_type": "Open to Close",
    "hvd_len": 100,
    "hvd_mult": 5.0,
    # TNT (engine G)
    "tnt_SENS": 100,
    "tnt_SWING_LEN": 10,
    "tnt_DISP_STD_X": 5,
    "tnt_SUDDEN_PROX": 3,
    "tnt_MAX_ZONES": 30,
    "tnt_RET_PCT": 100.0,
    # Combo Set (engine H)
    "cs_bodyPct_FVG": 0.69,
    "cs_bodyPct_MAT": 0.69,
    "cs_inc_pent_FVG": True,
    "cs_inc_pent_MAT": True,
    # Plot A / S19 — Unified Combo x2
    "uc2_min_hits": 2,
    "uc2_window": 2,
    # Plot B / S20 — FVG/MAT/Uni Combo x2
    "fmu_min_hits": 2,
    "fmu_window": 2,
    # S1-S18 enable flags
    "en_S1": True, "en_S2": True, "en_S3": True, "en_S4": True,
    "en_S5": True, "en_S6": True, "en_S8": True, "en_S9": True,
    "en_S10": True, "en_S11": True, "en_S12": True, "en_S13": True,
    "en_S14": True, "en_S15": True, "en_S16": True, "en_S17": True,
    "en_S18": True, "en_UC2": True, "en_FMU": True,
    # Bar timeframe in seconds (caller may supply via df.attrs["tfSec"])
    "tfSec": 60,
}


# ============================================================================
# _helpers — utilities used by many detections
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


def _wma(s: pd.Series, length: int) -> pd.Series:
    weights = np.arange(1, length + 1)
    return s.rolling(length).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)


def _vwma(price: pd.Series, vol: pd.Series, length: int) -> pd.Series:
    num = (price * vol).rolling(length, min_periods=length).sum()
    den = vol.rolling(length, min_periods=length).sum()
    return num / den.replace(0, np.nan)


def _hma(s: pd.Series, length: int) -> pd.Series:
    half = max(1, length // 2)
    sqrt_len = max(1, int(np.sqrt(length)))
    return _wma(2 * _wma(s, half) - _wma(s, length), sqrt_len)


def _ma(s: pd.Series, length: int, kind: str, vol: Optional[pd.Series] = None) -> pd.Series:
    if kind == "EMA":
        return _ema(s, length)
    if kind == "SMA":
        return _sma(s, length)
    if kind == "WMA":
        return _wma(s, length)
    if kind == "HMA":
        return _hma(s, length)
    if kind == "VWMA":
        if vol is None:
            return _sma(s, length)
        return _vwma(s, vol, length)
    return _sma(s, length)


def _atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([(h - l), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / length, adjust=False, min_periods=length).mean()


def _nz_b(s: pd.Series) -> pd.Series:
    return s.fillna(False).astype(bool)


def _nz_f(s: pd.Series, fill: float = 0.0) -> pd.Series:
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
    return pd.Series(True, index=df.index)


# RVOL threshold tables — mirror Pine f_th_* functions
def _th_1x(s: float) -> float:
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


def _th_gs(s: float) -> float:
    if s < 60: return _th_1x(s) * 3.0
    if s <= 300: return 35.0
    if s <= 600: return 25.0
    if s <= 1500: return 20.0
    if s <= 3000: return 20.0
    if s <= 7260: return 10.0
    if s <= 11700: return 8.0
    if s <= 86400: return 7.5
    if s <= 259200: return 3.5
    return 3.0


def _th_saab(s: float) -> float:
    return _th_1x(s) * 0.56


def _th_wtc(s: float) -> float:
    return _th_1x(s) * 2.0


def _th_hiro(s: float) -> float:
    if s < 60: return _th_1x(s) * 3.0
    if s <= 300: return 35.0
    if s <= 600: return 25.0
    if s <= 1500: return 25.0
    if s <= 3060: return 20.0
    if s <= 7260: return 10.0
    if s <= 11700: return 8.0
    if s <= 86400: return 7.5
    if s <= 259200: return 5.0
    return 3.5


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


# ============================================================================
# _engines — vectorized + stateful building blocks. Cached on df.attrs.
# ============================================================================
def _ensure_engines(df: pd.DataFrame, params: Dict) -> Dict[str, pd.Series]:
    cache = df.attrs.setdefault("_b2b_pup_eng", {})
    cache_key = (
        "v1", id(df),
        tuple(sorted((k, v) for k, v in params.items() if isinstance(v, (int, float, str, bool)))),
    )
    if cache.get("_key") == cache_key and "fire_S1_bull" in cache:
        return cache
    cache.clear()
    cache["_key"] = cache_key

    p = params
    conf = _conf(df)
    tfSec = float(p.get("tfSec", df.attrs.get("tfSec", 60)))
    is_new_day = df.attrs.get("is_new_day")
    if is_new_day is None:
        if isinstance(df.index, pd.DatetimeIndex):
            norm = pd.Series(df.index.normalize(), index=df.index)
            is_new_day = (norm != norm.shift(1)).fillna(True)
        else:
            tmp = np.zeros(len(df), dtype=bool); tmp[0] = True
            is_new_day = pd.Series(tmp, index=df.index)

    # ── Engine A: PUP / PPD (Offset 0) ──────────────────────────────────────
    pp_redVol = df["volume"].where(df["close"] < df["open"], 0.0)
    pp_greenVol = df["volume"].where(df["close"] > df["open"], 0.0)
    pp_hiRedVol = _highest(pp_redVol.shift(1), int(p["pp_lookback"]))
    pp_hiGreenVol = _highest(pp_greenVol.shift(1), int(p["pp_lookback"]))
    pp_priceUp = ((df["close"] - df["open"]) / df["open"]) * 100 > p["pp_barSize"]
    pp_priceDn = ((df["open"] - df["close"]) / df["open"]) * 100 > p["pp_barSize"]
    det_PUP = conf & pp_priceUp & (df["volume"] > pp_hiRedVol)
    det_PPD = conf & pp_priceDn & (df["volume"] > pp_hiGreenVol)

    # ── Engine B: FAUNA (Offset 0) ──────────────────────────────────────────
    atr14 = _atr(df, 14)
    f_AvgVol = _sma(df["volume"], 20)
    f_AvgBody = _sma((df["close"] - df["open"]).abs(), 20)
    f_AvgDelta = _sma((df["close"] - df["close"].shift(1)).abs(), 10)
    f_TrendMA = _sma(df["close"], 50)
    f_body = df["close"] - df["open"]
    f_rng = df["high"] - df["low"]
    f_bodySz = f_body.abs()
    f_bodyRat = (f_bodySz / f_rng.replace(0, np.nan)).fillna(0.0)
    f_up = f_body > 0
    f_dn = f_body < 0
    MB_b = f_up & (f_bodySz > 1.6 * atr14) & (f_bodyRat > 0.70) & (df["volume"] > 1.8 * f_AvgVol)
    MB_r = f_dn & (f_bodySz > 1.6 * atr14) & (f_bodyRat > 0.70) & (df["volume"] > 1.8 * f_AvgVol)
    RE_b = f_up & (f_rng > 2.2 * atr14) & ((df["high"] - df["close"]) < 0.15 * f_rng) & (df["volume"] > 1.8 * f_AvgVol)
    RE_r = f_dn & (f_rng > 2.2 * atr14) & ((df["close"] - df["low"]) < 0.15 * f_rng) & (df["volume"] > 1.8 * f_AvgVol)
    GG_b = ((df["open"] - df["close"].shift(1)) > 0.9 * atr14) & f_up & (df["low"] > df["close"].shift(1)) & (df["volume"] > 1.8 * f_AvgVol)
    GG_r = ((df["close"].shift(1) - df["open"]) > 0.9 * atr14) & f_dn & (df["high"] < df["close"].shift(1)) & (df["volume"] > 1.8 * f_AvgVol)
    TA_b = (f_TrendMA > f_TrendMA.shift(1)) & ((df["close"] - df["close"].shift(1)) > 1.6 * f_AvgDelta) & f_up & (df["volume"] > 1.8 * f_AvgVol)
    TA_r = (f_TrendMA < f_TrendMA.shift(1)) & ((df["close"].shift(1) - df["close"]) > 1.6 * f_AvgDelta) & f_dn & (df["volume"] > 1.8 * f_AvgVol)
    prev_body = df["close"].shift(1) - df["open"].shift(1)
    prev_rng = df["high"].shift(1) - df["low"].shift(1)
    StrongBear = (df["close"].shift(1) < df["open"].shift(1)) & (prev_body.abs() > 1.5 * f_AvgBody.shift(1)) & (df["volume"].shift(1) > 1.5 * f_AvgVol.shift(1))
    WeakBear = (df["close"].shift(1) < df["open"].shift(1)) & ((prev_body.abs() / prev_rng.replace(0, np.nan)).fillna(0.0) <= 0.2)
    StrongBull = (df["close"].shift(1) > df["open"].shift(1)) & (prev_body.abs() > 1.5 * f_AvgBody.shift(1)) & (df["volume"].shift(1) > 1.5 * f_AvgVol.shift(1))
    WeakBull = (df["close"].shift(1) > df["open"].shift(1)) & ((prev_body.abs() / prev_rng.replace(0, np.nan)).fillna(0.0) <= 0.2)
    TR_b = WeakBear & (MB_b | RE_b | TA_b)
    ES_b = StrongBear & (MB_b | RE_b | TA_b)
    GDR_b = (df["close"].shift(1) < df["open"].shift(1)) & GG_b
    TR_r = WeakBull & (MB_r | RE_r | TA_r)
    ES_r = StrongBull & (MB_r | RE_r | TA_r)
    GDR_r = (df["close"].shift(1) > df["open"].shift(1)) & GG_r
    b_core = MB_b.astype(int) + RE_b.astype(int) + TA_b.astype(int)
    s_core = MB_r.astype(int) + RE_r.astype(int) + TA_r.astype(int)
    excl_bull = TR_b | ES_b | GDR_b | (GG_b & ~((b_core >= 2) & (f_bodyRat >= 0.80)))
    excl_bear = TR_r | ES_r | GDR_r | (GG_r & ~((s_core >= 2) & (f_bodyRat >= 0.80)))
    det_FAUNABull = conf & (MB_b | RE_b | TA_b) & ~excl_bull
    det_FAUNABear = conf & (MB_r | RE_r | TA_r) & ~excl_bear

    # ── Engine C: Displacement (Offset -1) ──────────────────────────────────
    disp_rng = _disp_range(df, p["disp_type"])
    disp_std = _stdev(disp_rng, int(p["disp_len"]))
    disp_thr = disp_std * p["disp_mult"]
    disp_prevDisp = disp_rng.shift(1) > disp_thr.shift(1)
    disp_bullFVG = _bull_fvg(df)
    disp_bearFVG = _bear_fvg(df)
    det_DISPBull = conf & disp_prevDisp & disp_bullFVG
    det_DISPBear = conf & disp_prevDisp & disp_bearFVG

    # ── Engine D: PBJ — full landing-zone state machine ─────────────────────
    # MA + Supertrend signal line
    base_ma = _ma(df["close"], int(p["zoo_ma_len"]), p["zoo_ma_type"], vol=df["volume"])
    st_atr = p["zoo_st_mult"] * _atr(df, int(p["zoo_st_period"]))
    dyn_long = base_ma - st_atr
    dyn_short = base_ma + st_atr

    n = len(df)
    bm = base_ma.to_numpy()
    dl = dyn_long.to_numpy()
    ds = dyn_short.to_numpy()
    close_arr = df["close"].to_numpy()
    open_arr = df["open"].to_numpy()
    high_arr = df["high"].to_numpy()
    low_arr = df["low"].to_numpy()
    vol_arr = df["volume"].to_numpy()

    cur_long = np.full(n, np.nan)
    cur_short = np.full(n, np.nan)
    st_dir = np.ones(n, dtype=int)
    sig_line = np.full(n, np.nan)
    use_st = bool(p["zoo_use_st"])

    prev_long = np.nan
    prev_short = np.nan
    prev_dir = 1
    for i in range(n):
        # curr_long = base_ma>nz(curr_long[1],dyn_long)?math.max(dyn_long,nz(curr_long[1])):dyn_long
        ref_long = prev_long if not np.isnan(prev_long) else dl[i]
        if not np.isnan(bm[i]) and bm[i] > ref_long:
            cur_long[i] = max(dl[i], ref_long) if not (np.isnan(dl[i]) or np.isnan(ref_long)) else dl[i]
        else:
            cur_long[i] = dl[i]
        ref_short = prev_short if not np.isnan(prev_short) else ds[i]
        if not np.isnan(bm[i]) and bm[i] < ref_short:
            cur_short[i] = min(ds[i], ref_short) if not (np.isnan(ds[i]) or np.isnan(ref_short)) else ds[i]
        else:
            cur_short[i] = ds[i]
        if use_st:
            dprev = prev_dir
            if dprev == -1 and not np.isnan(prev_short) and close_arr[i] > prev_short:
                st_dir[i] = 1
            elif dprev == 1 and not np.isnan(prev_long) and close_arr[i] < prev_long:
                st_dir[i] = -1
            else:
                st_dir[i] = dprev
            sig_line[i] = cur_long[i] if st_dir[i] == 1 else cur_short[i]
        else:
            st_dir[i] = 1
            sig_line[i] = bm[i]
        prev_long = cur_long[i]
        prev_short = cur_short[i]
        prev_dir = st_dir[i]

    sig_series = pd.Series(sig_line, index=df.index)
    # crossovers
    buy_cross = (df["close"] > sig_series) & (df["close"].shift(1) <= sig_series.shift(1))
    sell_cross = (df["close"] < sig_series) & (df["close"].shift(1) >= sig_series.shift(1))
    buy_cross = _nz_b(buy_cross)
    sell_cross = _nz_b(sell_cross)

    # reaccel = same direction + sig rising/falling with previous-equal
    sig_prev1 = sig_series.shift(1)
    sig_prev2 = sig_series.shift(2)
    bull_reaccel = (pd.Series(st_dir, index=df.index) == 1) & (sig_series > sig_prev1) & (sig_prev1 == sig_prev2)
    bear_reaccel = (pd.Series(st_dir, index=df.index) == -1) & (sig_series < sig_prev1) & (sig_prev1 == sig_prev2)
    bull_reaccel = _nz_b(bull_reaccel)
    bear_reaccel = _nz_b(bear_reaccel)

    # PBJ buy/sell candidates (HH/LL based)
    pbj_ma = _ema(df["close"], int(p["zoo_pbj_ma_period"]))
    pbj_atr = _atr(df, int(p["zoo_pbj_atr_period"]))
    avg_vol = _sma(df["volume"], int(p["zoo_pbj_vol_period"]))
    zoo_thresh = (pbj_atr / df["close"].replace(0, np.nan) * p["zoo_pbj_atr_mult"]).fillna(0.0)
    pbj_buy = (df["low"] < pbj_ma * (1 - zoo_thresh)) & (df["low"] == _lowest(df["low"], int(p["zoo_pbj_hh_ll"]))) & (df["volume"] > avg_vol * p["zoo_pbj_vol_mult"])
    pbj_sell = (df["high"] > pbj_ma * (1 + zoo_thresh)) & (df["high"] == _highest(df["high"], int(p["zoo_pbj_hh_ll"]))) & (df["volume"] > avg_vol * p["zoo_pbj_vol_mult"])

    # Landing-zone arrays — bar-by-bar state walker
    atr_pb_arr = (atr14 * 2.0).to_numpy()
    buy_arr = buy_cross.to_numpy()
    sell_arr = sell_cross.to_numpy()
    bull_re_arr = bull_reaccel.to_numpy()
    bear_re_arr = bear_reaccel.to_numpy()
    sig_arr = sig_series.to_numpy()
    pbj_buy_arr = _nz_b(pbj_buy).to_numpy()
    pbj_sell_arr = _nz_b(pbj_sell).to_numpy()

    sig_pb_buy = np.zeros(n, dtype=bool)
    sig_pbj_buy = np.zeros(n, dtype=bool)
    sig_pb_sell = np.zeros(n, dtype=bool)
    sig_pbj_sell = np.zeros(n, dtype=bool)

    bull_lvls: list = []   # list of [upper, lower, vol, approached]
    bear_lvls: list = []
    wait_buy = False
    wait_sell = False
    wait_pbj_buy = False
    wait_pbj_sell = False

    def _push_lander(arr, up, lo, v):
        if abs(up - lo) >= 1e-12:
            arr.append([up, lo, v, False])

    for i in range(n):
        # f_add_lander on cross — uses bar[1] OHLC
        if buy_arr[i] and i >= 1:
            up = max(open_arr[i - 1], close_arr[i - 1])
            lo = low_arr[i - 1]
            apb = atr_pb_arr[i] if not np.isnan(atr_pb_arr[i]) else 0.0
            if up - lo < apb * 0.5:
                up = lo + apb * 0.5
            _push_lander(bull_lvls, up, lo, vol_arr[i - 1])
        if sell_arr[i] and i >= 1:
            up = high_arr[i - 1]
            lo = min(open_arr[i - 1], close_arr[i - 1])
            apb = atr_pb_arr[i] if not np.isnan(atr_pb_arr[i]) else 0.0
            if up - lo < apb * 0.5:
                lo = up - apb * 0.5
            _push_lander(bull_lvls if False else bear_lvls, up, lo, vol_arr[i - 1])
        # f_add_reaccel
        if bull_re_arr[i] and not np.isnan(sig_arr[i]):
            p1 = sig_arr[i]
            p2 = min(open_arr[i], close_arr[i])
            _push_lander(bull_lvls, max(p1, p2), min(p1, p2), vol_arr[i])
        if bear_re_arr[i] and not np.isnan(sig_arr[i]):
            p1 = sig_arr[i]
            p2 = max(open_arr[i], close_arr[i])
            _push_lander(bear_lvls, max(p1, p2), min(p1, p2), vol_arr[i])

        # check_approach
        approached_bull = False
        if bull_lvls:
            for j in range(len(bull_lvls) - 1, -1, -1):
                lvl = bull_lvls[j]
                up, lo, vv, ap = lvl
                if close_arr[i] < lo:
                    bull_lvls.pop(j)
                    continue
                a = up * 1.005
                if not ap and low_arr[i] <= a:
                    approached_bull = True
                    lvl[3] = True
                elif ap and low_arr[i] > up:
                    lvl[3] = False
        approached_bear = False
        if bear_lvls:
            for j in range(len(bear_lvls) - 1, -1, -1):
                lvl = bear_lvls[j]
                up, lo, vv, ap = lvl
                if close_arr[i] > up:
                    bear_lvls.pop(j)
                    continue
                a = lo * 0.995
                if not ap and high_arr[i] >= a:
                    approached_bear = True
                    lvl[3] = True
                elif ap and high_arr[i] < lo:
                    lvl[3] = False
        if approached_bull:
            wait_buy = True
        if approached_bear:
            wait_sell = True
        if pbj_buy_arr[i]:
            wait_pbj_buy = True
        if pbj_sell_arr[i]:
            wait_pbj_sell = True
        # cap list growth
        while len(bull_lvls) > 30:
            bull_lvls.pop(0)
        while len(bear_lvls) > 30:
            bear_lvls.pop(0)

        sig_pb_buy[i] = bool(buy_arr[i] and wait_buy)
        sig_pbj_buy[i] = bool(buy_arr[i] and wait_pbj_buy)
        sig_pb_sell[i] = bool(sell_arr[i] and wait_sell)
        sig_pbj_sell[i] = bool(sell_arr[i] and wait_pbj_sell)
        if sig_pb_buy[i]:
            wait_buy = False
        if sig_pbj_buy[i]:
            wait_pbj_buy = False
        if sig_pb_sell[i]:
            wait_sell = False
        if sig_pbj_sell[i]:
            wait_pbj_sell = False

    det_PBJBull = pd.Series(sig_pbj_buy, index=df.index)
    det_PBJBear = pd.Series(sig_pbj_sell, index=df.index)
    det_PBBull = pd.Series(sig_pb_buy, index=df.index) & ~det_PBJBull
    det_PBBear = pd.Series(sig_pb_sell, index=df.index) & ~det_PBJBear

    # ── Engine E: RVOL ─────────────────────────────────────────────────────
    rv_spike = (df["close"] - df["open"]).abs()
    rv_avgSpike = _sma(rv_spike, int(p["rv_avgLen"])).shift(1)
    rv_normPrice = rv_spike / _nz_f(rv_avgSpike, 1.0)
    rv_avgVol = _sma(df["volume"], int(p["rv_avgLen"])).shift(1)
    rv_normVol = df["volume"] / _nz_f(rv_avgVol, 1.0)
    rv_diff = rv_normPrice - rv_normVol
    rv_posDiff = rv_diff.where(rv_diff > 0, np.nan)
    rv_smaDiff = _sma(rv_posDiff, int(p["rv_smaLen"]))
    rv_baseBull = (df["close"] > df["open"]) & (rv_posDiff > rv_smaDiff) & conf
    rv_baseBear = (df["close"] < df["open"]) & (rv_posDiff > rv_smaDiff) & conf

    th_saab = _th_saab(tfSec)
    th_1x = _th_1x(tfSec)
    th_gs = _th_gs(tfSec)
    th_wtc = _th_wtc(tfSec)
    th_hiro = _th_hiro(tfSec)

    det_SAAB = rv_baseBull & (rv_normPrice >= th_saab) & (rv_normPrice < th_1x)
    det_Kratos = rv_baseBear & (rv_normPrice >= th_saab) & (rv_normPrice < th_1x)
    det_RVOL1xB = rv_baseBull & (rv_normPrice >= th_1x) & (rv_normPrice < th_gs)
    det_RVOL1xR = rv_baseBear & (rv_normPrice >= th_1x) & (rv_normPrice < th_gs)
    det_GrandSlam = rv_baseBull & (rv_normPrice >= th_gs)
    det_MOAB = rv_baseBear & (rv_normPrice >= th_gs)

    # tv_ta.relativeVolume → STUBBED via attrs
    rv_relVolRatio = _attr_or_nan(df, "rv_relVolRatio")
    det_Pentagon = conf & (rv_relVolRatio >= th_1x) & (rv_relVolRatio <= th_wtc)
    det_WTC = conf & (rv_relVolRatio > th_wtc) & (rv_relVolRatio <= th_hiro)
    det_Hiroshima = conf & (rv_relVolRatio > th_hiro)

    # Nagasaki — streaming ATH volume (not shifted)
    nag = np.zeros(n, dtype=bool)
    cur_max = -np.inf
    for i, v in enumerate(vol_arr):
        if i == 0:
            cur_max = v if not np.isnan(v) else -np.inf
            continue
        if not np.isnan(v) and v > cur_max:
            nag[i] = True
            cur_max = v
    det_Nagasaki = pd.Series(nag, index=df.index)

    # ── Engine F: HV+D ─────────────────────────────────────────────────────
    hvd_rng = _disp_range(df, p["hvd_type"])
    hvd_std = _stdev(hvd_rng, int(p["hvd_len"]))
    hvd_thr = hvd_std * p["hvd_mult"]
    hvd_prevDisp = hvd_rng.shift(1) > hvd_thr.shift(1)
    hvd_bullFVG = (df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["open"].shift(1))
    hvd_bearFVG = (df["high"] < df["low"].shift(2)) & (df["close"].shift(1) < df["open"].shift(1))
    hvd_dispBull = conf & hvd_prevDisp & hvd_bullFVG
    hvd_dispBear = conf & hvd_prevDisp & hvd_bearFVG
    vsh = df["volume"].shift(1)
    hv_is50 = vsh == _highest(df["volume"], 50).shift(1)
    hv_is100 = vsh == _highest(df["volume"], 100).shift(1)
    hv_is200 = vsh == _highest(df["volume"], 200).shift(1)
    hv_is500 = vsh == _highest(df["volume"], 500).shift(1)
    hv_is1000 = vsh == _highest(df["volume"], 1000).shift(1)
    # streaming hv_isHEV using shifted volume
    hev = np.zeros(n, dtype=bool)
    cur_max = -np.inf
    vsh_arr = vsh.to_numpy()
    for i, v in enumerate(vsh_arr):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            continue
        if v > cur_max:
            cur_max = v
            hev[i] = True
    hv_isHEV = pd.Series(hev, index=df.index)
    hv_base_hit = hv_isHEV | _nz_b(hv_is1000) | _nz_b(hv_is500) | _nz_b(hv_is200) | _nz_b(hv_is100) | _nz_b(hv_is50)
    det_HVDBull = hv_base_hit & hvd_dispBull
    det_HVDBear = hv_base_hit & hvd_dispBear
    det_HVDPBJBull = det_HVDBull & _nz_b(det_PBJBull.shift(1))
    det_HVDPBJBear = det_HVDBear & _nz_b(det_PBJBear.shift(1))
    det_B2BHVDBull = det_HVDBull & _nz_b(det_HVDBull.shift(1))
    det_B2BHVDBear = det_HVDBear & _nz_b(det_HVDBear.shift(1))
    det_B2BHVDPBJBull = det_B2BHVDBull & (_nz_b(det_PBJBull.shift(1)) | _nz_b(det_PBJBull.shift(2)))
    det_B2BHVDPBJBear = det_B2BHVDBear & (_nz_b(det_PBJBear.shift(1)) | _nz_b(det_PBJBear.shift(2)))

    # ── Engine G: TNT / Napalm / Charge / CONT ──────────────────────────────
    # Stateful + cross-bar pivot logic. We faithfully port the Pine loop.
    tnt_SENS = int(p["tnt_SENS"])
    tnt_SWING_LEN = int(p["tnt_SWING_LEN"])
    tnt_DISP_STD_X = int(p["tnt_DISP_STD_X"])
    tnt_SUDDEN_PROX = int(p["tnt_SUDDEN_PROX"])
    tnt_MAX_ZONES = int(p["tnt_MAX_ZONES"])
    tnt_RET_PCT = float(p["tnt_RET_PCT"])

    tnt_EMA_FAST = tnt_SENS
    tnt_EMA_SLOW = tnt_SENS + 13
    tnt_ATR_VAL = _atr(df, 200)
    tnt_ATR_MULT = 3.5
    tnt_ATR_MIN = 0.5
    tnt_MIN_SIG_GAP = tnt_EMA_SLOW
    tnt_CW = tnt_EMA_SLOW * 2
    tnt_ef = _ema(df["close"], tnt_EMA_FAST)
    tnt_es = _ema(df["close"], tnt_EMA_SLOW)

    tnt_vbc = ((tnt_ef > tnt_es) & (tnt_ef.shift(1) <= tnt_es.shift(1))).fillna(False) & conf
    tnt_vsc = ((tnt_ef < tnt_es) & (tnt_ef.shift(1) >= tnt_es.shift(1))).fillna(False) & conf

    ahi = _highest(tnt_ATR_VAL, 200) * 2.0
    ef_arr = tnt_ef.to_numpy()
    es_arr = tnt_es.to_numpy()
    atrv_arr = tnt_ATR_VAL.to_numpy()
    ahi_arr = ahi.to_numpy()
    vbc_arr = tnt_vbc.to_numpy()
    vsc_arr = tnt_vsc.to_numpy()

    tnt_vbu = np.full(n, np.nan); tnt_vbl = np.full(n, np.nan); tnt_vbv = np.full(n, np.nan)
    tnt_vbn = np.zeros(n, dtype=bool)
    tnt_vsu = np.full(n, np.nan); tnt_vsl = np.full(n, np.nan); tnt_vsv = np.full(n, np.nan)
    tnt_vsn = np.zeros(n, dtype=bool)

    last_vbu = np.nan; last_vbl = np.nan; last_vbv = np.nan
    last_vsu = np.nan; last_vsl = np.nan; last_vsv = np.nan
    for i in range(n):
        if vbc_arr[i]:
            cv = 0.0
            ol = low_arr[i]
            steps = min(tnt_EMA_SLOW, i)
            for k in range(1, steps + 1):
                if low_arr[i - k] <= ol:
                    ol = low_arr[i - k]
                cv += vol_arr[i - k]
            s = min(open_arr[i], close_arr[i])
            apb = ahi_arr[i] if not np.isnan(ahi_arr[i]) else 0.0
            if (s - ol) < apb * 0.5:
                s = ol + apb * 0.5
            last_vbu = s; last_vbl = ol; last_vbv = cv
            tnt_vbn[i] = True
        if vsc_arr[i]:
            cv = 0.0
            oh = high_arr[i]
            steps = min(tnt_EMA_SLOW, i)
            for k in range(1, steps + 1):
                if high_arr[i - k] >= oh:
                    oh = high_arr[i - k]
                cv += vol_arr[i - k]
            s = max(open_arr[i], close_arr[i])
            apb = ahi_arr[i] if not np.isnan(ahi_arr[i]) else 0.0
            if (oh - s) < apb * 0.5:
                s = oh - apb * 0.5
            last_vsu = oh; last_vsl = s; last_vsv = cv
            tnt_vsn[i] = True
        tnt_vbu[i] = last_vbu; tnt_vbl[i] = last_vbl; tnt_vbv[i] = last_vbv
        tnt_vsu[i] = last_vsu; tnt_vsl[i] = last_vsl; tnt_vsv[i] = last_vsv

    # swing pivot tracking (tnt_SP for swH / swL)
    swU = _highest(df["high"], tnt_SWING_LEN).to_numpy()
    swLL = _lowest(df["low"], tnt_SWING_LEN).to_numpy()
    swSt = np.zeros(n, dtype=int)
    cur_state = 0
    for i in range(n):
        if i >= tnt_SWING_LEN and high_arr[i - tnt_SWING_LEN] > swU[i]:
            cur_state = 0
        elif i >= tnt_SWING_LEN and low_arr[i - tnt_SWING_LEN] < swLL[i]:
            cur_state = 1
        swSt[i] = cur_state

    # swH/swL stored values
    swH_val = np.full(n, np.nan); swH_idx = np.full(n, -1, dtype=int); swH_crossed = np.zeros(n, dtype=bool)
    swL_val = np.full(n, np.nan); swL_idx = np.full(n, -1, dtype=int); swL_crossed = np.zeros(n, dtype=bool)
    last_swH_val = np.nan; last_swH_idx = -1; last_swH_crossed = False
    last_swL_val = np.nan; last_swL_idx = -1; last_swL_crossed = False
    # Pivot levels for advanced zones
    tnt_abu = np.full(n, np.nan); tnt_abl = np.full(n, np.nan); tnt_abi = np.full(n, -1, dtype=int)
    tnt_abn = np.zeros(n, dtype=bool)
    tnt_asu = np.full(n, np.nan); tnt_asl = np.full(n, np.nan); tnt_asi = np.full(n, -1, dtype=int)
    tnt_asn = np.zeros(n, dtype=bool)
    last_abu = np.nan; last_abl = np.nan; last_abi = -1
    last_apu = np.nan; last_apl = np.nan; last_api = -1
    last_asu = np.nan; last_asl = np.nan; last_asi = -1
    last_aspu = np.nan; last_aspl = np.nan; last_aspi = -1
    # Fast-pivot zone tracking (tnt_fbu/fbl/fa, etc.)
    tnt_fbu_arr = np.full(n, np.nan); tnt_fbl_arr = np.full(n, np.nan)
    tnt_fsu_arr = np.full(n, np.nan); tnt_fsl_arr = np.full(n, np.nan)
    tnt_fba_arr = np.zeros(n, dtype=bool); tnt_fsa_arr = np.zeros(n, dtype=bool)
    tnt_fbpn = np.zeros(n, dtype=bool); tnt_fspn = np.zeros(n, dtype=bool)
    last_fbu = np.nan; last_fbl = np.nan; last_fba = False
    last_fsu = np.nan; last_fsl = np.nan; last_fsa = False
    last_fswH_val = np.nan; last_fswH_idx = -1; last_fswH_crossed = False
    last_fswL_val = np.nan; last_fswL_idx = -1; last_fswL_crossed = False
    tnt_vcb = np.zeros(n, dtype=int); tnt_acb = np.zeros(n, dtype=int); tnt_fcb = np.zeros(n, dtype=int)
    tnt_vcs = np.zeros(n, dtype=int); tnt_acs = np.zeros(n, dtype=int); tnt_fcs = np.zeros(n, dtype=int)
    tnt_vcu_arr = np.full(n, np.nan); tnt_vcl_arr = np.full(n, np.nan)
    tnt_vdu_arr = np.full(n, np.nan); tnt_vdl_arr = np.full(n, np.nan)
    last_vcb = 0; last_acb = 0; last_fcb = 0
    last_vcs = 0; last_acs = 0; last_fcs = 0
    last_vcu = np.nan; last_vcl = np.nan
    last_vdu = np.nan; last_vdl = np.nan

    for i in range(n):
        # swH/swL update on swSt change
        if swSt[i] == 0 and (i == 0 or swSt[i - 1] != 0):
            idx_back = i - tnt_SWING_LEN
            if 0 <= idx_back < n:
                last_swH_val = high_arr[idx_back]
                last_swH_idx = idx_back
                last_swH_crossed = False
        if swSt[i] == 1 and (i == 0 or swSt[i - 1] != 1):
            idx_back = i - tnt_SWING_LEN
            if 0 <= idx_back < n:
                last_swL_val = low_arr[idx_back]
                last_swL_idx = idx_back
                last_swL_crossed = False
        swH_val[i] = last_swH_val; swH_idx[i] = last_swH_idx; swH_crossed[i] = last_swH_crossed
        swL_val[i] = last_swL_val; swL_idx[i] = last_swL_idx; swL_crossed[i] = last_swL_crossed
        # fast swH/swL
        if swSt[i] == 0 and (i == 0 or swSt[i - 1] != 0):
            idx_back = i - tnt_SWING_LEN
            if 0 <= idx_back < n:
                last_fswH_val = high_arr[idx_back]; last_fswH_idx = idx_back; last_fswH_crossed = False
        if swSt[i] == 1 and (i == 0 or swSt[i - 1] != 1):
            idx_back = i - tnt_SWING_LEN
            if 0 <= idx_back < n:
                last_fswL_val = low_arr[idx_back]; last_fswL_idx = idx_back; last_fswL_crossed = False

        # advanced pivot block — bull cross
        if not np.isnan(last_swH_val) and close_arr[i] > last_swH_val and not last_swH_crossed and i > 0:
            last_swH_crossed = True
            oL = low_arr[i - 1]; oH = high_arr[i - 1]; oI = i - 1
            lb = i - last_swH_idx
            if lb > 1:
                for k in range(1, lb):
                    if i - k >= 0 and open_arr[i - k] > close_arr[i - k] and low_arr[i - k] <= oL:
                        oL = low_arr[i - k]; oH = high_arr[i - k]; oI = i - k
            last_apu = last_abu; last_apl = last_abl; last_api = last_abi
            last_abu = oH; last_abl = oL; last_abi = oI
            tnt_abn[i] = (not np.isnan(last_apu)) and (oI <= (last_api if last_api >= 0 else 0) + tnt_EMA_SLOW) and (oH > (last_apl if not np.isnan(last_apl) else -np.inf)) and (oL < (last_apu if not np.isnan(last_apu) else np.inf))
        # advanced pivot block — bear cross
        if not np.isnan(last_swL_val) and close_arr[i] < last_swL_val and not last_swL_crossed and i > 0:
            last_swL_crossed = True
            oL = low_arr[i - 1]; oH = high_arr[i - 1]; oI = i - 1
            lb = i - last_swL_idx
            if lb > 1:
                for k in range(1, lb):
                    if i - k >= 0 and open_arr[i - k] < close_arr[i - k] and high_arr[i - k] >= oH:
                        oH = high_arr[i - k]; oL = low_arr[i - k]; oI = i - k
            last_aspu = last_asu; last_aspl = last_asl; last_aspi = last_asi
            last_asu = oH; last_asl = oL; last_asi = oI
            tnt_asn[i] = (not np.isnan(last_aspl)) and (oI <= (last_aspi if last_aspi >= 0 else 0) + tnt_EMA_SLOW) and (oL < (last_aspu if not np.isnan(last_aspu) else np.inf)) and (oH > (last_aspl if not np.isnan(last_aspl) else -np.inf))

        tnt_abu[i] = last_abu; tnt_abl[i] = last_abl; tnt_abi[i] = last_abi
        tnt_asu[i] = last_asu; tnt_asl[i] = last_asl; tnt_asi[i] = last_asi

        # fast-pivot block — bull cross
        if not np.isnan(last_fswH_val) and close_arr[i] > last_fswH_val and not last_fswH_crossed and i > 0:
            last_fswH_crossed = True
            bB = min(open_arr[i - 1], close_arr[i - 1])
            bT = max(open_arr[i - 1], close_arr[i - 1])
            lb = i - last_fswH_idx
            if lb > 1:
                for k in range(1, lb):
                    if i - k >= 0 and min(open_arr[i - k], close_arr[i - k]) < bB:
                        bB = min(open_arr[i - k], close_arr[i - k]); bT = max(open_arr[i - k], close_arr[i - k])
            osz = abs(bT - bB)
            av = atrv_arr[i] if not np.isnan(atrv_arr[i]) else 0.0
            if osz <= av * tnt_ATR_MULT and osz > av * tnt_ATR_MIN:
                last_fbu = bT; last_fbl = bB; last_fba = True
        # fast-pivot block — bear cross
        if not np.isnan(last_fswL_val) and close_arr[i] < last_fswL_val and not last_fswL_crossed and i > 0:
            last_fswL_crossed = True
            bT = max(open_arr[i - 1], close_arr[i - 1])
            bB = min(open_arr[i - 1], close_arr[i - 1])
            lb = i - last_fswL_idx
            if lb > 1:
                for k in range(1, lb):
                    if i - k >= 0 and max(open_arr[i - k], close_arr[i - k]) > bT:
                        bT = max(open_arr[i - k], close_arr[i - k]); bB = min(open_arr[i - k], close_arr[i - k])
            osz = abs(bT - bB)
            av = atrv_arr[i] if not np.isnan(atrv_arr[i]) else 0.0
            if osz <= av * tnt_ATR_MULT and osz > av * tnt_ATR_MIN:
                last_fsu = bT; last_fsl = bB; last_fsa = True

        # fast bull/bear pn — uses bar[1]
        fbpn = False; fspn = False
        if last_fba and i > 0:
            if close_arr[i] < last_fbl:
                last_fba = False
            elif low_arr[i - 1] < last_fbu and low_arr[i - 1] > last_fbl and close_arr[i] > open_arr[i] and close_arr[i] > high_arr[i - 1]:
                fbpn = True
        if last_fsa and i > 0:
            if close_arr[i] > last_fsu:
                last_fsa = False
            elif high_arr[i - 1] > last_fsl and high_arr[i - 1] < last_fsu and close_arr[i] < open_arr[i] and close_arr[i] < low_arr[i - 1]:
                fspn = True
        tnt_fbpn[i] = fbpn
        tnt_fspn[i] = fspn
        tnt_fbu_arr[i] = last_fbu; tnt_fbl_arr[i] = last_fbl; tnt_fba_arr[i] = last_fba
        tnt_fsu_arr[i] = last_fsu; tnt_fsl_arr[i] = last_fsl; tnt_fsa_arr[i] = last_fsa

        # bar index trackers
        if tnt_vbn[i]:
            last_vcb = i; last_vcu = tnt_vbu[i]; last_vcl = tnt_vbl[i]
        if tnt_vsn[i]:
            last_vcs = i; last_vdu = tnt_vsu[i]; last_vdl = tnt_vsl[i]
        if tnt_abn[i]:
            last_acb = i
        if tnt_asn[i]:
            last_acs = i
        if fbpn:
            last_fcb = i
        if fspn:
            last_fcs = i
        tnt_vcb[i] = last_vcb; tnt_acb[i] = last_acb; tnt_fcb[i] = last_fcb
        tnt_vcs[i] = last_vcs; tnt_acs[i] = last_acs; tnt_fcs[i] = last_fcs
        tnt_vcu_arr[i] = last_vcu; tnt_vcl_arr[i] = last_vcl
        tnt_vdu_arr[i] = last_vdu; tnt_vdl_arr[i] = last_vdl

    # Token (3-of-3 within window)
    def _tok(a, b, c):
        mn = np.minimum(np.minimum(a, b), c)
        mx = np.maximum(np.maximum(a, b), c)
        return ((mx - mn) <= tnt_CW) & (mn > 0)

    # zone overlap
    def _zov(u1, l1, u2, l2):
        return (~np.isnan(u1)) & (~np.isnan(u2)) & (u1 >= l2) & (u2 >= l1)

    bConf = _tok(tnt_vcb, tnt_acb, tnt_fcb) & _zov(tnt_vcu_arr, tnt_vcl_arr, tnt_abu, tnt_abl)
    sConf = _tok(tnt_vcs, tnt_acs, tnt_fcs) & _zov(tnt_vdu_arr, tnt_vdl_arr, tnt_asu, tnt_asl)

    # supporting stats
    tnt_vMed = df["volume"].rolling(tnt_EMA_SLOW, min_periods=1).median().to_numpy()
    tnt_eSl = (tnt_ef - tnt_ef.shift(5)).fillna(0.0).to_numpy()
    # RSI 14
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = (100 - 100 / (1 + rs)).fillna(50.0).to_numpy()

    bull_TNT_raw = np.zeros(n, dtype=bool)
    bear_TNT_raw = np.zeros(n, dtype=bool)
    last_BSB = 0
    last_SSB = 0
    bull_lvls_w = []
    bear_lvls_w = []
    # zone lists
    bull_tnt_zones: list = []   # [confirmIdx, upper, lower, level, isActive, returnFired]
    bear_tnt_zones: list = []
    charge_lvls: list = []       # [level, isBull, barIdx, violated]
    bull_events: list = []       # (barIdx, isTrue)
    bear_events: list = []
    last_bull2_bar = 0
    last_bear2_bar = 0

    # CONT bar trackers
    sc_lastBullChargeBar = -1; sc_lastBearChargeBar = -1
    sc_lastRetBullBar = -1; sc_lastRetBearBar = -1
    sc_lastBullTNTBar = -1; sc_lastBearTNTBar = -1
    sc_lastBullTNT2Bar = -1; sc_lastBearTNT2Bar = -1

    det_bullTNT_raw_arr = np.zeros(n, dtype=bool)
    det_bearTNT_raw_arr = np.zeros(n, dtype=bool)
    det_bullTNT2_arr = np.zeros(n, dtype=bool)
    det_bearTNT2_arr = np.zeros(n, dtype=bool)
    det_superBullTNT_arr = np.zeros(n, dtype=bool)
    det_superBearTNT_arr = np.zeros(n, dtype=bool)
    det_bullNapalm_arr = np.zeros(n, dtype=bool)
    det_bearNapalm_arr = np.zeros(n, dtype=bool)
    det_bullCharge_arr = np.zeros(n, dtype=bool)
    det_bearCharge_arr = np.zeros(n, dtype=bool)
    det_retBullTNT_arr = np.zeros(n, dtype=bool)
    det_retBearTNT_arr = np.zeros(n, dtype=bool)
    det_contBull_arr = np.zeros(n, dtype=bool)
    det_contBear_arr = np.zeros(n, dtype=bool)

    # TNT internal displacement
    tnt_dr = (df["open"] - df["close"]).abs()
    tnt_ds = _stdev(tnt_dr, 100)
    tnt_dt = (tnt_ds * tnt_DISP_STD_X).to_numpy()
    tnt_dr_arr = tnt_dr.to_numpy()
    tnt_dBull_arr = np.zeros(n, dtype=bool); tnt_dBear_arr = np.zeros(n, dtype=bool)
    for i in range(n):
        if i >= 1 and not np.isnan(tnt_dt[i - 1]) and tnt_dr_arr[i - 1] > tnt_dt[i - 1]:
            if i >= 2 and low_arr[i] > high_arr[i - 2] and close_arr[i - 1] > open_arr[i - 1]:
                tnt_dBull_arr[i] = True
            if i >= 2 and high_arr[i] < low_arr[i - 2] and close_arr[i - 1] < open_arr[i - 1]:
                tnt_dBear_arr[i] = True

    def _sb(vv, vu, vl, au, al, esl, rsi_):
        if vv is None or np.isnan(vv): return False
        mn1 = vu - vl
        mn2 = au - al
        if mn1 <= 0 and mn2 <= 0: return False
        minrng = min(mn1, mn2) if (mn1 > 0 and mn2 > 0) else max(mn1, mn2)
        if minrng <= 0:
            ratio = 0
        else:
            ratio = max(0, min(vu, au) - max(vl, al)) / minrng
        return vv > 0 and esl > 0 and rsi_ < 80 and ratio > 0.3

    def _ss(vv, vu, vl, au, al, esl, rsi_):
        if vv is None or np.isnan(vv): return False
        mn1 = vu - vl
        mn2 = au - al
        if mn1 <= 0 and mn2 <= 0: return False
        minrng = min(mn1, mn2) if (mn1 > 0 and mn2 > 0) else max(mn1, mn2)
        if minrng <= 0:
            ratio = 0
        else:
            ratio = max(0, min(vu, au) - max(vl, al)) / minrng
        return vv > 0 and esl < 0 and rsi_ > 20 and ratio > 0.3

    for i in range(n):
        b_ok = bool(bConf[i])
        s_ok = bool(sConf[i])
        vbv_i = tnt_vbv[i] if i < n and not np.isnan(tnt_vbv[i]) else 0.0
        vsv_i = tnt_vsv[i] if i < n and not np.isnan(tnt_vsv[i]) else 0.0
        vMed_i = tnt_vMed[i] if not np.isnan(tnt_vMed[i]) else 0.0
        vol_threshold = vMed_i * tnt_EMA_SLOW * 0.5
        # Pine: vV>vMed*EMA_SLOW*0.5 is the check inside f_tnt_sb. We replicate inline.
        sb_pass = b_ok and vbv_i > vol_threshold and _sb(vbv_i,
                                                          tnt_vcu_arr[i] if not np.isnan(tnt_vcu_arr[i]) else 0,
                                                          tnt_vcl_arr[i] if not np.isnan(tnt_vcl_arr[i]) else 0,
                                                          tnt_abu[i] if not np.isnan(tnt_abu[i]) else 0,
                                                          tnt_abl[i] if not np.isnan(tnt_abl[i]) else 0,
                                                          tnt_eSl[i], rsi[i])
        ss_pass = s_ok and vsv_i > vol_threshold and _ss(vsv_i,
                                                          tnt_vdu_arr[i] if not np.isnan(tnt_vdu_arr[i]) else 0,
                                                          tnt_vdl_arr[i] if not np.isnan(tnt_vdl_arr[i]) else 0,
                                                          tnt_asu[i] if not np.isnan(tnt_asu[i]) else 0,
                                                          tnt_asl[i] if not np.isnan(tnt_asl[i]) else 0,
                                                          tnt_eSl[i], rsi[i])
        if sb_pass and (i - last_BSB) > tnt_MIN_SIG_GAP:
            det_bullTNT_raw_arr[i] = True
            last_BSB = i
        if ss_pass and (i - last_SSB) > tnt_MIN_SIG_GAP:
            det_bearTNT_raw_arr[i] = True
            last_SSB = i

        # zone push
        if det_bullTNT_raw_arr[i]:
            oU = min(
                tnt_vcu_arr[i] if not np.isnan(tnt_vcu_arr[i]) else high_arr[i],
                tnt_abu[i] if not np.isnan(tnt_abu[i]) else high_arr[i],
            )
            oL = max(
                tnt_vcl_arr[i] if not np.isnan(tnt_vcl_arr[i]) else low_arr[i],
                tnt_abl[i] if not np.isnan(tnt_abl[i]) else low_arr[i],
            )
            lvl = (oU + oL) / 2.0
            bull_tnt_zones.append([i, oU, oL, lvl, True, False])
            charge_lvls.append([lvl, True, i, False])
        if det_bearTNT_raw_arr[i]:
            oU = min(
                tnt_vdu_arr[i] if not np.isnan(tnt_vdu_arr[i]) else high_arr[i],
                tnt_asu[i] if not np.isnan(tnt_asu[i]) else high_arr[i],
            )
            oL = max(
                tnt_vdl_arr[i] if not np.isnan(tnt_vdl_arr[i]) else low_arr[i],
                tnt_asl[i] if not np.isnan(tnt_asl[i]) else low_arr[i],
            )
            lvl = (oU + oL) / 2.0
            bear_tnt_zones.append([i, oU, oL, lvl, True, False])
            charge_lvls.append([lvl, False, i, False])

        # invalidate zones whose levels close has broken
        for z in bull_tnt_zones:
            if z[4] and close_arr[i] < z[2]:
                z[4] = False
        for z in bear_tnt_zones:
            if z[4] and close_arr[i] > z[1]:
                z[4] = False
        while len(bull_tnt_zones) > tnt_MAX_ZONES:
            bull_tnt_zones.pop(0)
        while len(bear_tnt_zones) > tnt_MAX_ZONES:
            bear_tnt_zones.pop(0)

        # Return to TNT
        for z in bull_tnt_zones:
            if z[4] and not z[5] and i > z[0]:
                zH = z[1] - z[2]
                retLvl = z[2] + zH * (tnt_RET_PCT / 100.0)
                if low_arr[i] <= retLvl and close_arr[i] > z[2]:
                    z[5] = True
                    det_retBullTNT_arr[i] = True
        for z in bear_tnt_zones:
            if z[4] and not z[5] and i > z[0]:
                zH = z[1] - z[2]
                retLvl = z[1] - zH * (tnt_RET_PCT / 100.0)
                if high_arr[i] >= retLvl and close_arr[i] < z[1]:
                    z[5] = True
                    det_retBearTNT_arr[i] = True

        # Napalm — scan all active opposing zones, uses tnt_dBull/Bear on this bar
        if tnt_dBull_arr[i] and bear_tnt_zones:
            for z in reversed(bear_tnt_zones):
                if z[4] and i >= 1 and low_arr[i - 1] > z[3]:
                    det_bullNapalm_arr[i] = True
                    break
        if tnt_dBear_arr[i] and bull_tnt_zones:
            for z in reversed(bull_tnt_zones):
                if z[4] and i >= 1 and high_arr[i - 1] < z[3]:
                    det_bearNapalm_arr[i] = True
                    break

        # Charge — violations
        if tnt_dBull_arr[i] and charge_lvls:
            for cl in reversed(charge_lvls):
                if (not cl[1]) and (not cl[3]) and i >= 1 and close_arr[i - 1] > cl[0]:
                    cl[3] = True
                    det_bullCharge_arr[i] = True
                    charge_lvls.append([low_arr[i - 1], True, i, False])
                    break
        if tnt_dBear_arr[i] and charge_lvls:
            for cl in reversed(charge_lvls):
                if cl[1] and (not cl[3]) and i >= 1 and close_arr[i - 1] < cl[0]:
                    cl[3] = True
                    det_bearCharge_arr[i] = True
                    charge_lvls.append([high_arr[i - 1], False, i, False])
                    break
        while len(charge_lvls) > 100:
            charge_lvls.pop(0)

        # Super TNT (raw + opposing Charge same bar)
        det_superBullTNT_arr[i] = det_bullTNT_raw_arr[i] and det_bearCharge_arr[i]
        det_superBearTNT_arr[i] = det_bearTNT_raw_arr[i] and det_bullCharge_arr[i]

        # TNT 2.0 event log
        effBullCharge = det_bullCharge_arr[i] and not det_bearTNT_raw_arr[i]
        effBearCharge = det_bearCharge_arr[i] and not det_bullTNT_raw_arr[i]
        anyBullEvt = det_bullTNT_raw_arr[i] or det_bullNapalm_arr[i] or effBullCharge
        anyBearEvt = det_bearTNT_raw_arr[i] or det_bearNapalm_arr[i] or effBearCharge
        if anyBullEvt:
            evtBar = i if det_bullTNT_raw_arr[i] else i - 1
            bull_events.append((evtBar, det_bullTNT_raw_arr[i]))
            bear_events.clear()
            while len(bull_events) > 20:
                bull_events.pop(0)
        if anyBearEvt and not anyBullEvt:
            evtBar = i if det_bearTNT_raw_arr[i] else i - 1
            bear_events.append((evtBar, det_bearTNT_raw_arr[i]))
            bull_events.clear()
            while len(bear_events) > 20:
                bear_events.pop(0)
        if len(bull_events) >= 2 and anyBullEvt and (i - last_bull2_bar) > tnt_MIN_SIG_GAP:
            det_bullTNT2_arr[i] = True
            last_bull2_bar = i
        if len(bear_events) >= 2 and anyBearEvt and (not anyBullEvt) and (i - last_bear2_bar) > tnt_MIN_SIG_GAP:
            det_bearTNT2_arr[i] = True
            last_bear2_bar = i

        # CONT — 3-clause logic
        contBull = False
        contBear = False
        if det_bullCharge_arr[i] and sc_lastRetBullBar >= 0 and (i - 1 - sc_lastRetBullBar) <= tnt_SUDDEN_PROX:
            contBull = True
        if (det_bullTNT_raw_arr[i] or det_bullTNT2_arr[i]) and sc_lastBullChargeBar >= 0 and (i - sc_lastBullChargeBar) <= tnt_SUDDEN_PROX:
            contBull = True
        if det_bullCharge_arr[i] and (
            (sc_lastBullTNTBar >= 0 and (i - 1 - sc_lastBullTNTBar) <= tnt_SUDDEN_PROX)
            or (sc_lastBullTNT2Bar >= 0 and (i - 1 - sc_lastBullTNT2Bar) <= tnt_SUDDEN_PROX)
        ):
            contBull = True
        if det_bearCharge_arr[i] and sc_lastRetBearBar >= 0 and (i - 1 - sc_lastRetBearBar) <= tnt_SUDDEN_PROX:
            contBear = True
        if (det_bearTNT_raw_arr[i] or det_bearTNT2_arr[i]) and sc_lastBearChargeBar >= 0 and (i - sc_lastBearChargeBar) <= tnt_SUDDEN_PROX:
            contBear = True
        if det_bearCharge_arr[i] and (
            (sc_lastBearTNTBar >= 0 and (i - 1 - sc_lastBearTNTBar) <= tnt_SUDDEN_PROX)
            or (sc_lastBearTNT2Bar >= 0 and (i - 1 - sc_lastBearTNT2Bar) <= tnt_SUDDEN_PROX)
        ):
            contBear = True
        det_contBull_arr[i] = contBull
        det_contBear_arr[i] = contBear

        # update bar trackers (these update AFTER CONT, mirroring Pine line order)
        if det_bullCharge_arr[i]:
            sc_lastBullChargeBar = i - 1
        if det_bearCharge_arr[i]:
            sc_lastBearChargeBar = i - 1
        if det_retBullTNT_arr[i]:
            sc_lastRetBullBar = i
        if det_retBearTNT_arr[i]:
            sc_lastRetBearBar = i
        if det_bullTNT_raw_arr[i]:
            sc_lastBullTNTBar = i
        if det_bearTNT_raw_arr[i]:
            sc_lastBearTNTBar = i
        if det_bullTNT2_arr[i]:
            sc_lastBullTNT2Bar = i
        if det_bearTNT2_arr[i]:
            sc_lastBearTNT2Bar = i

    det_bullTNT_raw = pd.Series(det_bullTNT_raw_arr, index=df.index)
    det_bearTNT_raw = pd.Series(det_bearTNT_raw_arr, index=df.index)
    det_bullTNT2 = pd.Series(det_bullTNT2_arr, index=df.index)
    det_bearTNT2 = pd.Series(det_bearTNT2_arr, index=df.index)
    det_superBullTNT = pd.Series(det_superBullTNT_arr, index=df.index)
    det_superBearTNT = pd.Series(det_superBearTNT_arr, index=df.index)
    det_bullNapalm = pd.Series(det_bullNapalm_arr, index=df.index)
    det_bearNapalm = pd.Series(det_bearNapalm_arr, index=df.index)
    det_bullCharge = pd.Series(det_bullCharge_arr, index=df.index)
    det_bearCharge = pd.Series(det_bearCharge_arr, index=df.index)
    det_retBullTNT = pd.Series(det_retBullTNT_arr, index=df.index)
    det_retBearTNT = pd.Series(det_retBearTNT_arr, index=df.index)
    det_contBull = pd.Series(det_contBull_arr, index=df.index)
    det_contBear = pd.Series(det_contBear_arr, index=df.index)

    det_bullTNT = det_bullTNT_raw | det_bullTNT2 | det_superBullTNT
    det_bearTNT = det_bearTNT_raw | det_bearTNT2 | det_superBearTNT
    det_bullNapCons = det_bullNapalm | det_bullCharge
    det_bearNapCons = det_bearNapalm | det_bearCharge
    det_b2bBullNapalm = det_bullNapCons & _nz_b(det_bullNapCons.shift(1))
    det_b2bBearNapalm = det_bearNapCons & _nz_b(det_bearNapCons.shift(1))

    # ── Engine H: GZ1 / HV FVG — STUBBED (struct array per bar). Inject via df.attrs. ──
    gz_bullGZI = _attr_or_false(df, "gz_bullGZI")
    gz_bearGZI = _attr_or_false(df, "gz_bearGZI")
    gz_bullHV = _attr_or_false(df, "gz_bullHV")
    gz_bearHV = _attr_or_false(df, "gz_bearHV")

    # ── Combo Sets ──
    cs_bp1 = ((df["close"].shift(1) - df["open"].shift(1)).abs() /
              (df["high"].shift(1) - df["low"].shift(1)).replace(0, np.nan)).fillna(0.0)
    cs_vb = cs_bp1 >= p["cs_bodyPct_FVG"]
    comboSet1_Bull = conf & cs_vb & (gz_bullHV | gz_bullGZI) & (
        _nz_b(det_SAAB.shift(1)) | _nz_b(det_RVOL1xB.shift(1)) | _nz_b(det_GrandSlam.shift(1))
    )
    comboSet1_Bear = conf & cs_vb & (gz_bearHV | gz_bearGZI) & (
        _nz_b(det_Kratos.shift(1)) | _nz_b(det_RVOL1xR.shift(1)) | _nz_b(det_MOAB.shift(1))
    )
    pent_b1 = bool(p["cs_inc_pent_FVG"])
    pent_prev = _nz_b(det_Pentagon.shift(1)) if pent_b1 else pd.Series(False, index=df.index)
    comboSet2_Bull = conf & cs_vb & (gz_bullHV | gz_bullGZI) & (
        pent_prev | _nz_b(det_WTC.shift(1)) | _nz_b(det_Hiroshima.shift(1)) | _nz_b(det_Nagasaki.shift(1))
    )
    comboSet2_Bear = conf & cs_vb & (gz_bearHV | gz_bearGZI) & (
        pent_prev | _nz_b(det_WTC.shift(1)) | _nz_b(det_Hiroshima.shift(1)) | _nz_b(det_Nagasaki.shift(1))
    )
    det_CS1Bull = comboSet1_Bull | comboSet2_Bull
    det_CS1Bear = comboSet1_Bear | comboSet2_Bear

    ls_bodyRat = (f_bodySz / f_rng.replace(0, np.nan)).fillna(0.0)
    cs_vm = ls_bodyRat >= p["cs_bodyPct_MAT"]
    is_matrix_number = df["volume"] == _highest(df["volume"], 67)
    det_NeoBull = conf & is_matrix_number & det_FAUNABull
    det_NeoBear = conf & is_matrix_number & det_FAUNABear
    det_TrinityBull = conf & is_matrix_number & ~det_FAUNABull & (df["close"] > df["open"])
    det_TrinityBear = conf & is_matrix_number & ~det_FAUNABear & (df["close"] < df["open"])
    matrix_any_bull = det_NeoBull | det_TrinityBull
    matrix_any_bear = det_NeoBear | det_TrinityBear
    comboSet3_Bull = cs_vm & matrix_any_bull & (det_SAAB | det_RVOL1xB | det_GrandSlam)
    comboSet3_Bear = cs_vm & matrix_any_bear & (det_Kratos | det_RVOL1xR | det_MOAB)
    pent_b2 = bool(p["cs_inc_pent_MAT"])
    pent_cur = det_Pentagon if pent_b2 else pd.Series(False, index=df.index)
    comboSet4_Bull = cs_vm & matrix_any_bull & (pent_cur | det_WTC | det_Hiroshima | det_Nagasaki)
    comboSet4_Bear = cs_vm & matrix_any_bear & (pent_cur | det_WTC | det_Hiroshima | det_Nagasaki)
    det_CS2Bull = comboSet3_Bull | comboSet4_Bull
    det_CS2Bear = comboSet3_Bear | comboSet4_Bear
    det_UnifiedBull = det_CS1Bull & _nz_b(det_CS2Bull.shift(1))
    det_UnifiedBear = det_CS1Bear & _nz_b(det_CS2Bear.shift(1))

    # Long1 / Short1 — RVOL ratios STUBBED (caller injects via df.attrs)
    ls_regRatio = _attr_or_nan(df, "ls_regRatio")
    ls_cumRatio = _attr_or_nan(df, "ls_cumRatio")
    det_Long1 = conf & (ls_regRatio > 7.0) & (ls_cumRatio > 3.5) & (df["close"] > df["open"]) & (ls_bodyRat >= 0.60)
    det_Short1 = conf & (ls_regRatio > 7.0) & (ls_cumRatio > 3.5) & (df["close"] < df["open"]) & (ls_bodyRat >= 0.60)

    # ── Plot A (S19): Unified Combo x2 — window scan ────────────────────────
    uc2_window = int(p["uc2_window"])
    uc2_min_hits = int(p["uc2_min_hits"])
    cs1b = _nz_b(comboSet1_Bull) | _nz_b(comboSet2_Bull)
    cs2b_b = _nz_b(comboSet3_Bull) | _nz_b(comboSet4_Bull)
    cs1r = _nz_b(comboSet1_Bear) | _nz_b(comboSet2_Bear)
    cs2r_b = _nz_b(comboSet3_Bear) | _nz_b(comboSet4_Bear)
    cs1b_arr = cs1b.to_numpy(); cs2b_arr = cs2b_b.to_numpy()
    cs1r_arr = cs1r.to_numpy(); cs2r_arr = cs2r_b.to_numpy()
    uc2_bull = np.zeros(n, dtype=bool); uc2_bear = np.zeros(n, dtype=bool)
    fmu_bull = np.zeros(n, dtype=bool); fmu_bear = np.zeros(n, dtype=bool)
    fmu_window = int(p["fmu_window"])
    fmu_min_hits = int(p["fmu_min_hits"])
    for i in range(n):
        cnt_b = 0; cnt_r = 0
        cnt_b_f = 0; cnt_r_f = 0
        for V in range(1, uc2_window + 1):
            v0 = i - (V - 1)
            v1 = i - V
            if v0 < 0 or v1 < 0:
                continue
            cs1_v = cs1b_arr[v0]
            cs2_v = cs2b_arr[v1]
            if cs1_v and cs2_v:
                cnt_b += 1
            cs1_v_r = cs1r_arr[v0]
            cs2_v_r = cs2r_arr[v1]
            if cs1_v_r and cs2_v_r:
                cnt_r += 1
        for V in range(1, fmu_window + 1):
            v0 = i - (V - 1)
            v1 = i - V
            if v0 < 0 or v1 < 0:
                continue
            if cs1b_arr[v0] or cs2b_arr[v1]:
                cnt_b_f += 1
            if cs1r_arr[v0] or cs2r_arr[v1]:
                cnt_r_f += 1
        uc2_bull[i] = cnt_b >= uc2_min_hits
        uc2_bear[i] = cnt_r >= uc2_min_hits
        fmu_bull[i] = cnt_b_f >= fmu_min_hits
        fmu_bear[i] = cnt_r_f >= fmu_min_hits
    det_UC2Bull = conf & pd.Series(uc2_bull, index=df.index)
    det_UC2Bear = conf & pd.Series(uc2_bear, index=df.index)
    det_FMUBull = conf & pd.Series(fmu_bull, index=df.index)
    det_FMUBear = conf & pd.Series(fmu_bear, index=df.index)

    # ── UU / UUU / UUUU streak engine ───────────────────────────────────────
    u_qual_bull = (conf & rv_baseBull & (rv_normPrice >= 0.5)).fillna(False)
    u_qual_bear = (conf & rv_baseBear & (rv_normPrice >= 0.5)).fillna(False)
    qb_arr = u_qual_bull.to_numpy()
    qr_arr = u_qual_bear.to_numpy()
    nd_arr = is_new_day.fillna(False).to_numpy()
    u_bull_streak = np.zeros(n, dtype=int)
    u_bear_streak = np.zeros(n, dtype=int)
    u_bull_d1 = np.zeros(n, dtype=bool)
    u_bear_d1 = np.zeros(n, dtype=bool)
    sb = 0; sr = 0; hd_b = False; hd_r = False
    for i in range(n):
        if qb_arr[i]:
            sb += 1; hd_b = hd_b or nd_arr[i]
        else:
            sb = 0; hd_b = False
        if qr_arr[i]:
            sr += 1; hd_r = hd_r or nd_arr[i]
        else:
            sr = 0; hd_r = False
        u_bull_streak[i] = sb; u_bear_streak[i] = sr
        u_bull_d1[i] = hd_b; u_bear_d1[i] = hd_r

    pbjbull_arr = _nz_b(det_PBJBull).to_numpy()
    pbbull_arr = _nz_b(det_PBBull).to_numpy()
    pbjbear_arr = _nz_b(det_PBJBear).to_numpy()
    pbbear_arr = _nz_b(det_PBBear).to_numpy()
    hvdbull_arr = _nz_b(det_HVDBull).to_numpy()
    hvdbear_arr = _nz_b(det_HVDBear).to_numpy()
    dispbull_arr = _nz_b(det_DISPBull).to_numpy()
    dispbear_arr = _nz_b(det_DISPBear).to_numpy()
    faunabull_arr = _nz_b(det_FAUNABull).to_numpy()
    faunabear_arr = _nz_b(det_FAUNABear).to_numpy()
    saab_arr = _nz_b(det_SAAB).to_numpy()
    rvol1xb_arr = _nz_b(det_RVOL1xB).to_numpy()
    gs_arr = _nz_b(det_GrandSlam).to_numpy()
    krat_arr = _nz_b(det_Kratos).to_numpy()
    rvol1xr_arr = _nz_b(det_RVOL1xR).to_numpy()
    moab_arr = _nz_b(det_MOAB).to_numpy()
    rv_np_arr = _nz_f(rv_normPrice).to_numpy()

    def _scan_bull(i, _n):
        hp = hpb = hh = hd = hf = False
        ad = asd = True
        dnp = pnd = False
        for k in range(_n):
            idx = i - k
            if idx < 0:
                ad = False; asd = False
                continue
            bpbj = pbjbull_arr[idx]; bpb = pbbull_arr[idx]
            bhvd = hvdbull_arr[idx - 1] if (k >= 1 and idx - 1 >= 0) else False
            bdisp = dispbull_arr[idx] or bhvd
            bfauna = faunabull_arr[idx]
            bsaab = saab_arr[idx] or rvol1xb_arr[idx] or gs_arr[idx]
            bdf = bdisp or bfauna
            hp = hp or bpbj
            hpb = hpb or bpb
            hh = hh or bhvd
            hd = hd or bdisp
            hf = hf or bfauna
            if not bdisp:
                ad = False
            if (not bsaab) or (not bdf):
                asd = False
            if bdf and not bpbj:
                dnp = True
            if bpbj and not bdf:
                pnd = True
        return hp, hpb, hh, hd, hf, ad, asd, dnp, pnd

    def _scan_bear(i, _n):
        hp = hpb = hh = hd = hf = False
        ad = asd = True
        dnp = pnd = False
        for k in range(_n):
            idx = i - k
            if idx < 0:
                ad = False; asd = False
                continue
            bpbj = pbjbear_arr[idx]; bpb = pbbear_arr[idx]
            bhvd = hvdbear_arr[idx - 1] if (k >= 1 and idx - 1 >= 0) else False
            bdisp = dispbear_arr[idx] or bhvd
            bfauna = faunabear_arr[idx]
            bsaab = krat_arr[idx] or rvol1xr_arr[idx] or moab_arr[idx]
            bdf = bdisp or bfauna
            hp = hp or bpbj
            hpb = hpb or bpb
            hh = hh or bhvd
            hd = hd or bdisp
            hf = hf or bfauna
            if not bdisp:
                ad = False
            if (not bsaab) or (not bdf):
                asd = False
            if bdf and not bpbj:
                dnp = True
            if bpbj and not bdf:
                pnd = True
        return hp, hpb, hh, hd, hf, ad, asd, dnp, pnd

    det_UUBull_arr = np.zeros(n, dtype=bool)
    det_UUUBull_arr = np.zeros(n, dtype=bool)
    det_UUUUBull_arr = np.zeros(n, dtype=bool)
    det_UUBear_arr = np.zeros(n, dtype=bool)
    det_UUUBear_arr = np.zeros(n, dtype=bool)
    det_UUUUBear_arr = np.zeros(n, dtype=bool)

    for i in range(n):
        if u_bull_streak[i] >= 4:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _scan_bull(i, min(u_bull_streak[i], 4))
            s_ = rv_np_arr[i] + (rv_np_arr[i - 1] if i >= 1 else 0) + (rv_np_arr[i - 2] if i >= 2 else 0) + (rv_np_arr[i - 3] if i >= 3 else 0)
            p_ = pbjbull_arr[i] or (pbjbull_arr[i - 1] if i >= 1 else False) or (pbjbull_arr[i - 2] if i >= 2 else False) or (pbjbull_arr[i - 3] if i >= 3 else False)
            ok = tfSec > 120 or (s_ >= th_saab and (s_ >= th_1x or p_))
            det_UUUUBull_arr[i] = ((u_bull_d1[i] and hp) or ad or asd or hh or ((dnp and hp) or (pnd and (hd or hf))) or ((hf or hd) and hp)) and ok
        if u_bull_streak[i] == 3:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _scan_bull(i, 3)
            s_ = rv_np_arr[i] + (rv_np_arr[i - 1] if i >= 1 else 0) + (rv_np_arr[i - 2] if i >= 2 else 0)
            p_ = pbjbull_arr[i] or (pbjbull_arr[i - 1] if i >= 1 else False) or (pbjbull_arr[i - 2] if i >= 2 else False)
            ok = tfSec > 120 or (s_ >= th_saab and (s_ >= th_1x or p_))
            det_UUUBull_arr[i] = ((u_bull_d1[i] and hp) or ad or asd or hh or ((dnp and hp) or (pnd and (hd or hf)))) and ok
        if u_bull_streak[i] == 2:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _scan_bull(i, 2)
            s_ = rv_np_arr[i] + (rv_np_arr[i - 1] if i >= 1 else 0)
            p_ = pbjbull_arr[i] or (pbjbull_arr[i - 1] if i >= 1 else False)
            ok = tfSec > 120 or (s_ >= th_saab and (s_ >= th_1x or p_))
            det_UUBull_arr[i] = ((u_bull_d1[i] and hp) or ad or asd or (hh and (hpb or hp)) or ((dnp and hp) or (pnd and (hd or hf)))) and ok

        if u_bear_streak[i] >= 4:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _scan_bear(i, min(u_bear_streak[i], 4))
            det_UUUUBear_arr[i] = (u_bear_d1[i] and hp) or ad or asd or hh or ((dnp and hp) or (pnd and (hd or hf))) or ((hf or hd) and hp)
        if u_bear_streak[i] == 3:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _scan_bear(i, 3)
            det_UUUBear_arr[i] = (u_bear_d1[i] and hp) or ad or asd or hh or ((dnp and hp) or (pnd and (hd or hf)))
        if u_bear_streak[i] == 2:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = _scan_bear(i, 2)
            det_UUBear_arr[i] = (u_bear_d1[i] and hp) or ad or asd or (hh and (hpb or hp)) or ((dnp and hp) or (pnd and (hd or hf)))

    det_UUBull = pd.Series(det_UUBull_arr, index=df.index)
    det_UUUBull = pd.Series(det_UUUBull_arr, index=df.index)
    det_UUUUBull = pd.Series(det_UUUUBull_arr, index=df.index)
    det_UUBear = pd.Series(det_UUBear_arr, index=df.index)
    det_UUUBear = pd.Series(det_UUUBear_arr, index=df.index)
    det_UUUUBear = pd.Series(det_UUUUBear_arr, index=df.index)

    # ── Detection combination layer (S1-S18) ────────────────────────────────
    det_b2bPUP = det_PUP & _nz_b(det_PUP.shift(1))
    det_b2bPPD = det_PPD & _nz_b(det_PPD.shift(1))
    det_S2_bull = det_b2bPUP & det_FAUNABull & _nz_b(det_FAUNABull.shift(1))
    det_S2_bear = det_b2bPPD & det_FAUNABear & _nz_b(det_FAUNABear.shift(1))
    det_S3_bull = _nz_b(det_PUP.shift(1)) & _nz_b(det_PUP.shift(2)) & det_DISPBull & _nz_b(det_DISPBull.shift(1))
    det_S3_bear = _nz_b(det_PPD.shift(1)) & _nz_b(det_PPD.shift(2)) & det_DISPBear & _nz_b(det_DISPBear.shift(1))
    det_S3d_bull = _nz_b(det_PUP.shift(1)) & _nz_b(det_PUP.shift(2)) & det_HVDBull & _nz_b(det_HVDBull.shift(1))
    det_S3d_bear = _nz_b(det_PPD.shift(1)) & _nz_b(det_PPD.shift(2)) & det_HVDBear & _nz_b(det_HVDBear.shift(1))
    det_S3_any_bull = det_S3_bull | det_S3d_bull
    det_S3_any_bear = det_S3_bear | det_S3d_bear
    det_S4_bull = _nz_b(det_PUP.shift(1)) & _nz_b(det_PUP.shift(2)) & _nz_b(det_FAUNABull.shift(1)) & _nz_b(det_FAUNABull.shift(2)) & det_DISPBull & _nz_b(det_DISPBull.shift(1))
    det_S4_bear = _nz_b(det_PPD.shift(1)) & _nz_b(det_PPD.shift(2)) & _nz_b(det_FAUNABear.shift(1)) & _nz_b(det_FAUNABear.shift(2)) & det_DISPBear & _nz_b(det_DISPBear.shift(1))
    det_S4d_bull = _nz_b(det_PUP.shift(1)) & _nz_b(det_PUP.shift(2)) & _nz_b(det_FAUNABull.shift(1)) & _nz_b(det_FAUNABull.shift(2)) & det_HVDBull & _nz_b(det_HVDBull.shift(1))
    det_S4d_bear = _nz_b(det_PPD.shift(1)) & _nz_b(det_PPD.shift(2)) & _nz_b(det_FAUNABear.shift(1)) & _nz_b(det_FAUNABear.shift(2)) & det_HVDBear & _nz_b(det_HVDBear.shift(1))
    det_S4_any_bull = det_S4_bull | det_S4d_bull
    det_S4_any_bear = det_S4_bear | det_S4d_bear

    saab_dir_b = det_SAAB | det_RVOL1xB | det_GrandSlam
    saab_neut = det_WTC | det_Hiroshima
    saab_dir_b1 = _nz_b(det_SAAB.shift(1)) | _nz_b(det_RVOL1xB.shift(1)) | _nz_b(det_GrandSlam.shift(1))
    saab_neut1 = _nz_b(det_WTC.shift(1)) | _nz_b(det_Hiroshima.shift(1))
    det_S5_bull = det_b2bPUP & ((saab_dir_b & (saab_dir_b1 | saab_neut1)) | ((saab_dir_b | saab_neut) & saab_dir_b1))
    krat_dir = det_Kratos | det_RVOL1xR | det_MOAB
    krat_dir1 = _nz_b(det_Kratos.shift(1)) | _nz_b(det_RVOL1xR.shift(1)) | _nz_b(det_MOAB.shift(1))
    det_S5_bear = det_b2bPPD & ((krat_dir & (krat_dir1 | saab_neut1)) | ((krat_dir | saab_neut) & krat_dir1))

    anyB2B_nd_bull = det_b2bPUP | det_S2_bull | det_S5_bull
    anyB2B_nd_bear = det_b2bPPD | det_S2_bear | det_S5_bear
    det_S6_bull = (anyB2B_nd_bull & (det_PBJBull | _nz_b(det_PBJBull.shift(1)) | det_HVDPBJBull)) | \
                  (det_S3_any_bull & (_nz_b(det_PBJBull.shift(1)) | _nz_b(det_PBJBull.shift(2)) | _nz_b(det_HVDPBJBull.shift(1)))) | \
                  (det_S4_any_bull & (_nz_b(det_PBJBull.shift(1)) | _nz_b(det_PBJBull.shift(2)) | _nz_b(det_HVDPBJBull.shift(1))))
    det_S6_bear = (anyB2B_nd_bear & (det_PBJBear | _nz_b(det_PBJBear.shift(1)) | det_HVDPBJBear)) | \
                  (det_S3_any_bear & (_nz_b(det_PBJBear.shift(1)) | _nz_b(det_PBJBear.shift(2)) | _nz_b(det_HVDPBJBear.shift(1)))) | \
                  (det_S4_any_bear & (_nz_b(det_PBJBear.shift(1)) | _nz_b(det_PBJBear.shift(2)) | _nz_b(det_HVDPBJBear.shift(1))))

    det_S8_bull = (det_b2bPUP & det_UnifiedBull) | (det_S3_any_bull & (det_UnifiedBull | _nz_b(det_UnifiedBull.shift(1))))
    det_S8_bear = (det_b2bPPD & det_UnifiedBear) | (det_S3_any_bear & (det_UnifiedBear | _nz_b(det_UnifiedBear.shift(1))))

    s9_combo_bull = det_UC2Bull | det_FMUBull
    s9_combo_bear = det_UC2Bear | det_FMUBear
    det_S9_bull = (det_b2bPUP & (s9_combo_bull | _nz_b(s9_combo_bull.shift(1)))) | \
                  (det_S3_any_bull & (_nz_b(s9_combo_bull.shift(1)) | _nz_b(s9_combo_bull.shift(2))))
    det_S9_bear = (det_b2bPPD & (s9_combo_bear | _nz_b(s9_combo_bear.shift(1)))) | \
                  (det_S3_any_bear & (_nz_b(s9_combo_bear.shift(1)) | _nz_b(s9_combo_bear.shift(2))))

    det_S10_bull = (det_Long1 & _nz_b(det_Long1.shift(1))) & (det_b2bPUP | _nz_b(det_b2bPUP.shift(1)))
    det_S10_bear = (det_Short1 & _nz_b(det_Short1.shift(1))) & (det_b2bPPD | _nz_b(det_b2bPPD.shift(1)))
    det_S11_bull = det_b2bPUP & (det_CS1Bull | det_Long1 | _nz_b(det_Long1.shift(1)))
    det_S11_bear = det_b2bPPD & (det_CS1Bear | det_Short1 | _nz_b(det_Short1.shift(1)))
    anyUU_bull = det_UUUUBull | det_UUUBull | det_UUBull
    anyUU_bear = det_UUUUBear | det_UUUBear | det_UUBear
    det_S12_bull = det_b2bPUP & (anyUU_bull | _nz_b(anyUU_bull.shift(1)))
    det_S12_bear = det_b2bPPD & (anyUU_bear | _nz_b(anyUU_bear.shift(1)))
    det_S13_bull = det_b2bPUP & (det_b2bBullNapalm | _nz_b(det_b2bBullNapalm.shift(1)))
    det_S13_bear = det_b2bPPD & (det_b2bBearNapalm | _nz_b(det_b2bBearNapalm.shift(1)))
    det_S14_bull = det_b2bPUP & (det_contBull | _nz_b(det_contBull.shift(1)))
    det_S14_bear = det_b2bPPD & (det_contBear | _nz_b(det_contBear.shift(1)))
    det_S15_bull = det_b2bPUP & (det_bullTNT | _nz_b(det_bullTNT.shift(1)))
    det_S15_bear = det_b2bPPD & (det_bearTNT | _nz_b(det_bearTNT.shift(1)))
    det_S16_bull = det_b2bPUP & (det_bullNapCons | _nz_b(det_bullNapCons.shift(1)))
    det_S16_bear = det_b2bPPD & (det_bearNapCons | _nz_b(det_bearNapCons.shift(1)))
    det_S17_bull = det_b2bPUP & (det_B2BHVDBull | _nz_b(det_B2BHVDBull.shift(1)))
    det_S17_bear = det_b2bPPD & (det_B2BHVDBear | _nz_b(det_B2BHVDBear.shift(1)))
    det_S18_bull = det_b2bPUP & (det_B2BHVDPBJBull | _nz_b(det_B2BHVDPBJBull.shift(1)))
    det_S18_bear = det_b2bPPD & (det_B2BHVDPBJBear | _nz_b(det_B2BHVDPBJBear.shift(1)))

    # Master gate — defaults to True (en_firstBarOnly=False)
    if not bool(p["en_firstBarOnly"]):
        master_gate = pd.Series(True, index=df.index)
        g01 = pd.Series(True, index=df.index)
        gd = pd.Series(True, index=df.index)
    else:
        # When first-bar-only is engaged, we approximate: True only on session-first bar
        # (and the prior bar / 2-prior bar via f_touches2). This matches Pine semantics.
        first_idx_arr = np.zeros(n, dtype=int)
        cur_first = -1
        nd2 = is_new_day.to_numpy()
        for i in range(n):
            if nd2[i]:
                cur_first = i
            first_idx_arr[i] = cur_first
        g01_arr = np.zeros(n, dtype=bool)
        gd_arr = np.zeros(n, dtype=bool)
        for i in range(n):
            cf = first_idx_arr[i]
            g01_arr[i] = (i == cf) or (i - 1 == cf)
            gd_arr[i] = (i - 1 == cf) or (i - 2 == cf)
        # Also any-HV gate on bar[0]
        anyHV = (
            (df["volume"] == _highest(df["volume"], 50)) |
            (df["volume"] == _highest(df["volume"], 100)) |
            (df["volume"] == _highest(df["volume"], 200)) |
            (df["volume"] == _highest(df["volume"], 500)) |
            (df["volume"] == _highest(df["volume"], 1000))
        )
        isFirst = pd.Series([i == first_idx_arr[i] for i in range(n)], index=df.index)
        master_gate = isFirst & anyHV
        g01 = pd.Series(g01_arr, index=df.index)
        gd = pd.Series(gd_arr, index=df.index)

    def _en(name):
        return bool(p.get(name, True))

    # Fire booleans — match Pine plotshape gating
    fire_S1_bull = _en("en_S1") & det_b2bPUP & g01 & master_gate
    fire_S1_bear = _en("en_S1") & det_b2bPPD & g01 & master_gate
    fire_S2_bull = _en("en_S2") & det_S2_bull & g01 & master_gate
    fire_S2_bear = _en("en_S2") & det_S2_bear & g01 & master_gate
    fire_S3_bull = _en("en_S3") & det_S3_any_bull & gd & master_gate
    fire_S3_bear = _en("en_S3") & det_S3_any_bear & gd & master_gate
    fire_S4_bull = _en("en_S4") & det_S4_any_bull & gd & master_gate
    fire_S4_bear = _en("en_S4") & det_S4_any_bear & gd & master_gate
    fire_S5_bull = _en("en_S5") & det_S5_bull & g01 & master_gate
    fire_S5_bear = _en("en_S5") & det_S5_bear & g01 & master_gate
    fire_S6_bull = _en("en_S6") & det_S6_bull & (g01 | gd) & master_gate
    fire_S6_bear = _en("en_S6") & det_S6_bear & (g01 | gd) & master_gate
    fire_S8_bull = _en("en_S8") & det_S8_bull & (g01 | gd) & master_gate
    fire_S8_bear = _en("en_S8") & det_S8_bear & (g01 | gd) & master_gate
    fire_S9_bull = _en("en_S9") & det_S9_bull & (g01 | gd) & master_gate
    fire_S9_bear = _en("en_S9") & det_S9_bear & (g01 | gd) & master_gate
    fire_S10_bull = _en("en_S10") & det_S10_bull & g01 & master_gate
    fire_S10_bear = _en("en_S10") & det_S10_bear & g01 & master_gate
    fire_S11_bull = _en("en_S11") & det_S11_bull & g01 & master_gate
    fire_S11_bear = _en("en_S11") & det_S11_bear & g01 & master_gate
    fire_S12_bull = _en("en_S12") & det_S12_bull & g01 & master_gate
    fire_S12_bear = _en("en_S12") & det_S12_bear & g01 & master_gate
    fire_S13_bull = _en("en_S13") & det_S13_bull & g01 & master_gate
    fire_S13_bear = _en("en_S13") & det_S13_bear & g01 & master_gate
    fire_S14_bull = _en("en_S14") & det_S14_bull & g01 & master_gate
    fire_S14_bear = _en("en_S14") & det_S14_bear & g01 & master_gate
    fire_S15_bull = _en("en_S15") & det_S15_bull & g01 & master_gate
    fire_S15_bear = _en("en_S15") & det_S15_bear & g01 & master_gate
    fire_S16_bull = _en("en_S16") & det_S16_bull & g01 & master_gate
    fire_S16_bear = _en("en_S16") & det_S16_bear & g01 & master_gate
    fire_S17_bull = _en("en_S17") & det_S17_bull & g01 & master_gate
    fire_S17_bear = _en("en_S17") & det_S17_bear & g01 & master_gate
    fire_S18_bull = _en("en_S18") & det_S18_bull & g01 & master_gate
    fire_S18_bear = _en("en_S18") & det_S18_bear & g01 & master_gate
    fire_UC2_bull = _en("en_UC2") & det_UC2Bull & (g01 | gd) & master_gate
    fire_UC2_bear = _en("en_UC2") & det_UC2Bear & (g01 | gd) & master_gate
    fire_FMU_bull = _en("en_FMU") & det_FMUBull & (g01 | gd) & master_gate
    fire_FMU_bear = _en("en_FMU") & det_FMUBear & (g01 | gd) & master_gate

    cache.update({
        # Root primitives
        "det_PUP": det_PUP, "det_PPD": det_PPD,
        "det_b2bPUP": det_b2bPUP, "det_b2bPPD": det_b2bPPD,
        "det_FAUNABull": det_FAUNABull, "det_FAUNABear": det_FAUNABear,
        "det_DISPBull": det_DISPBull, "det_DISPBear": det_DISPBear,
        "det_PBJBull": det_PBJBull, "det_PBJBear": det_PBJBear,
        "det_PBBull": det_PBBull, "det_PBBear": det_PBBear,
        "det_SAAB": det_SAAB, "det_Kratos": det_Kratos,
        "det_RVOL1xB": det_RVOL1xB, "det_RVOL1xR": det_RVOL1xR,
        "det_GrandSlam": det_GrandSlam, "det_MOAB": det_MOAB,
        "det_Pentagon": det_Pentagon, "det_WTC": det_WTC,
        "det_Hiroshima": det_Hiroshima, "det_Nagasaki": det_Nagasaki,
        "det_HVDBull": det_HVDBull, "det_HVDBear": det_HVDBear,
        "det_HVDPBJBull": det_HVDPBJBull, "det_HVDPBJBear": det_HVDPBJBear,
        "det_B2BHVDBull": det_B2BHVDBull, "det_B2BHVDBear": det_B2BHVDBear,
        "det_B2BHVDPBJBull": det_B2BHVDPBJBull, "det_B2BHVDPBJBear": det_B2BHVDPBJBear,
        "det_bullTNT_raw": det_bullTNT_raw, "det_bearTNT_raw": det_bearTNT_raw,
        "det_bullTNT2": det_bullTNT2, "det_bearTNT2": det_bearTNT2,
        "det_superBullTNT": det_superBullTNT, "det_superBearTNT": det_superBearTNT,
        "det_bullTNT": det_bullTNT, "det_bearTNT": det_bearTNT,
        "det_bullNapalm": det_bullNapalm, "det_bearNapalm": det_bearNapalm,
        "det_bullCharge": det_bullCharge, "det_bearCharge": det_bearCharge,
        "det_retBullTNT": det_retBullTNT, "det_retBearTNT": det_retBearTNT,
        "det_contBull": det_contBull, "det_contBear": det_contBear,
        "det_bullNapCons": det_bullNapCons, "det_bearNapCons": det_bearNapCons,
        "det_b2bBullNapalm": det_b2bBullNapalm, "det_b2bBearNapalm": det_b2bBearNapalm,
        "det_NeoBull": det_NeoBull, "det_NeoBear": det_NeoBear,
        "det_TrinityBull": det_TrinityBull, "det_TrinityBear": det_TrinityBear,
        "det_CS1Bull": det_CS1Bull, "det_CS1Bear": det_CS1Bear,
        "det_CS2Bull": det_CS2Bull, "det_CS2Bear": det_CS2Bear,
        "det_UnifiedBull": det_UnifiedBull, "det_UnifiedBear": det_UnifiedBear,
        "det_Long1": det_Long1, "det_Short1": det_Short1,
        "det_UUBull": det_UUBull, "det_UUUBull": det_UUUBull, "det_UUUUBull": det_UUUUBull,
        "det_UUBear": det_UUBear, "det_UUUBear": det_UUUBear, "det_UUUUBear": det_UUUUBear,
        "det_UC2Bull": det_UC2Bull, "det_UC2Bear": det_UC2Bear,
        "det_FMUBull": det_FMUBull, "det_FMUBear": det_FMUBear,
        # S-detection booleans
        "det_S2_bull": det_S2_bull, "det_S2_bear": det_S2_bear,
        "det_S3_any_bull": det_S3_any_bull, "det_S3_any_bear": det_S3_any_bear,
        "det_S4_any_bull": det_S4_any_bull, "det_S4_any_bear": det_S4_any_bear,
        "det_S5_bull": det_S5_bull, "det_S5_bear": det_S5_bear,
        "det_S6_bull": det_S6_bull, "det_S6_bear": det_S6_bear,
        "det_S8_bull": det_S8_bull, "det_S8_bear": det_S8_bear,
        "det_S9_bull": det_S9_bull, "det_S9_bear": det_S9_bear,
        "det_S10_bull": det_S10_bull, "det_S10_bear": det_S10_bear,
        "det_S11_bull": det_S11_bull, "det_S11_bear": det_S11_bear,
        "det_S12_bull": det_S12_bull, "det_S12_bear": det_S12_bear,
        "det_S13_bull": det_S13_bull, "det_S13_bear": det_S13_bear,
        "det_S14_bull": det_S14_bull, "det_S14_bear": det_S14_bear,
        "det_S15_bull": det_S15_bull, "det_S15_bear": det_S15_bear,
        "det_S16_bull": det_S16_bull, "det_S16_bear": det_S16_bear,
        "det_S17_bull": det_S17_bull, "det_S17_bear": det_S17_bear,
        "det_S18_bull": det_S18_bull, "det_S18_bear": det_S18_bear,
        # Fire booleans (plot outputs)
        "fire_S1_bull": fire_S1_bull, "fire_S1_bear": fire_S1_bear,
        "fire_S2_bull": fire_S2_bull, "fire_S2_bear": fire_S2_bear,
        "fire_S3_bull": fire_S3_bull, "fire_S3_bear": fire_S3_bear,
        "fire_S4_bull": fire_S4_bull, "fire_S4_bear": fire_S4_bear,
        "fire_S5_bull": fire_S5_bull, "fire_S5_bear": fire_S5_bear,
        "fire_S6_bull": fire_S6_bull, "fire_S6_bear": fire_S6_bear,
        "fire_S8_bull": fire_S8_bull, "fire_S8_bear": fire_S8_bear,
        "fire_S9_bull": fire_S9_bull, "fire_S9_bear": fire_S9_bear,
        "fire_S10_bull": fire_S10_bull, "fire_S10_bear": fire_S10_bear,
        "fire_S11_bull": fire_S11_bull, "fire_S11_bear": fire_S11_bear,
        "fire_S12_bull": fire_S12_bull, "fire_S12_bear": fire_S12_bear,
        "fire_S13_bull": fire_S13_bull, "fire_S13_bear": fire_S13_bear,
        "fire_S14_bull": fire_S14_bull, "fire_S14_bear": fire_S14_bear,
        "fire_S15_bull": fire_S15_bull, "fire_S15_bear": fire_S15_bear,
        "fire_S16_bull": fire_S16_bull, "fire_S16_bear": fire_S16_bear,
        "fire_S17_bull": fire_S17_bull, "fire_S17_bear": fire_S17_bear,
        "fire_S18_bull": fire_S18_bull, "fire_S18_bear": fire_S18_bear,
        "fire_UC2_bull": fire_UC2_bull, "fire_UC2_bear": fire_UC2_bear,
        "fire_FMU_bull": fire_FMU_bull, "fire_FMU_bear": fire_FMU_bear,
    })
    return cache


# ============================================================================
# Public detection functions — every named plot in Pine maps to one.
# ============================================================================
def _wrap(name: str) -> Callable[[pd.DataFrame, Optional[Dict]], pd.Series]:
    def _fn(df: pd.DataFrame, params: Optional[Dict] = None) -> pd.Series:
        eng = _ensure_engines(df, _p(params))
        s = eng[name]
        return s.fillna(False).astype(bool)
    _fn.__name__ = f"detect_{name}"
    return _fn


# Root primitives (named building blocks, not directly plotted as S-shapes but
# exposed because validators commonly probe them)
detect_PUP = _wrap("det_PUP")
detect_PPD = _wrap("det_PPD")
detect_b2bPUP = _wrap("det_b2bPUP")
detect_b2bPPD = _wrap("det_b2bPPD")
detect_FAUNABull = _wrap("det_FAUNABull")
detect_FAUNABear = _wrap("det_FAUNABear")
detect_DISPBull = _wrap("det_DISPBull")
detect_DISPBear = _wrap("det_DISPBear")
detect_PBJBull = _wrap("det_PBJBull")
detect_PBJBear = _wrap("det_PBJBear")
detect_PBBull = _wrap("det_PBBull")
detect_PBBear = _wrap("det_PBBear")
detect_HVDBull = _wrap("det_HVDBull")
detect_HVDBear = _wrap("det_HVDBear")
detect_HVDPBJBull = _wrap("det_HVDPBJBull")
detect_HVDPBJBear = _wrap("det_HVDPBJBear")
detect_B2BHVDBull = _wrap("det_B2BHVDBull")
detect_B2BHVDBear = _wrap("det_B2BHVDBear")
detect_B2BHVDPBJBull = _wrap("det_B2BHVDPBJBull")
detect_B2BHVDPBJBear = _wrap("det_B2BHVDPBJBear")
detect_SAAB = _wrap("det_SAAB")
detect_Kratos = _wrap("det_Kratos")
detect_RVOL1xB = _wrap("det_RVOL1xB")
detect_RVOL1xR = _wrap("det_RVOL1xR")
detect_GrandSlam = _wrap("det_GrandSlam")
detect_MOAB = _wrap("det_MOAB")
detect_Nagasaki = _wrap("det_Nagasaki")
detect_bullTNT_raw = _wrap("det_bullTNT_raw")
detect_bearTNT_raw = _wrap("det_bearTNT_raw")
detect_bullTNT = _wrap("det_bullTNT")
detect_bearTNT = _wrap("det_bearTNT")
detect_bullNapalm = _wrap("det_bullNapalm")
detect_bearNapalm = _wrap("det_bearNapalm")
detect_bullCharge = _wrap("det_bullCharge")
detect_bearCharge = _wrap("det_bearCharge")
detect_contBull = _wrap("det_contBull")
detect_contBear = _wrap("det_contBear")
detect_b2bBullNapalm = _wrap("det_b2bBullNapalm")
detect_b2bBearNapalm = _wrap("det_b2bBearNapalm")
detect_CS1Bull = _wrap("det_CS1Bull")
detect_CS1Bear = _wrap("det_CS1Bear")
detect_CS2Bull = _wrap("det_CS2Bull")
detect_CS2Bear = _wrap("det_CS2Bear")
detect_UnifiedBull = _wrap("det_UnifiedBull")
detect_UnifiedBear = _wrap("det_UnifiedBear")
detect_NeoBull = _wrap("det_NeoBull")
detect_NeoBear = _wrap("det_NeoBear")
detect_TrinityBull = _wrap("det_TrinityBull")
detect_TrinityBear = _wrap("det_TrinityBear")
detect_UUBull = _wrap("det_UUBull")
detect_UUUBull = _wrap("det_UUUBull")
detect_UUUUBull = _wrap("det_UUUUBull")
detect_UUBear = _wrap("det_UUBear")
detect_UUUBear = _wrap("det_UUUBear")
detect_UUUUBear = _wrap("det_UUUUBear")

# Named plot detections (S1-S6, S8-S20). Names mirror Pine plot titles.
detect_S1_bull = _wrap("fire_S1_bull")
detect_S1_bear = _wrap("fire_S1_bear")
detect_S2_bull = _wrap("fire_S2_bull")
detect_S2_bear = _wrap("fire_S2_bear")
detect_S3_bull = _wrap("fire_S3_bull")
detect_S3_bear = _wrap("fire_S3_bear")
detect_S4_bull = _wrap("fire_S4_bull")
detect_S4_bear = _wrap("fire_S4_bear")
detect_S5_bull = _wrap("fire_S5_bull")
detect_S5_bear = _wrap("fire_S5_bear")
detect_S6_bull = _wrap("fire_S6_bull")
detect_S6_bear = _wrap("fire_S6_bear")
detect_S8_bull = _wrap("fire_S8_bull")
detect_S8_bear = _wrap("fire_S8_bear")
detect_S9_bull = _wrap("fire_S9_bull")
detect_S9_bear = _wrap("fire_S9_bear")
detect_S10_bull = _wrap("fire_S10_bull")
detect_S10_bear = _wrap("fire_S10_bear")
detect_S11_bull = _wrap("fire_S11_bull")
detect_S11_bear = _wrap("fire_S11_bear")
detect_S12_bull = _wrap("fire_S12_bull")
detect_S12_bear = _wrap("fire_S12_bear")
detect_S13_bull = _wrap("fire_S13_bull")
detect_S13_bear = _wrap("fire_S13_bear")
detect_S14_bull = _wrap("fire_S14_bull")
detect_S14_bear = _wrap("fire_S14_bear")
detect_S15_bull = _wrap("fire_S15_bull")
detect_S15_bear = _wrap("fire_S15_bear")
detect_S16_bull = _wrap("fire_S16_bull")
detect_S16_bear = _wrap("fire_S16_bear")
detect_S17_bull = _wrap("fire_S17_bull")
detect_S17_bear = _wrap("fire_S17_bear")
detect_S18_bull = _wrap("fire_S18_bull")
detect_S18_bear = _wrap("fire_S18_bear")
detect_S19_UC2_bull = _wrap("fire_UC2_bull")
detect_S19_UC2_bear = _wrap("fire_UC2_bear")
detect_S20_FMU_bull = _wrap("fire_FMU_bull")
detect_S20_FMU_bear = _wrap("fire_FMU_bear")


# ============================================================================
# Stubbed detections — Pine-only intrinsics required.
# ============================================================================
STUBBED: Dict[str, str] = {
    # tv_ta.relativeVolume (regular + cumulative). Inject via df.attrs:
    #   rv_relVolRatio (engine E Pentagon/WTC/Hiroshima)
    #   ls_regRatio, ls_cumRatio (Long1/Short1)
    "_rel_vol_engine": (
        "tv_ta.relativeVolume not reproduced; "
        "inject rv_relVolRatio / ls_regRatio / ls_cumRatio via df.attrs"
    ),
    # GZ1 / HV FVG: array<gz_fvg_s> walker with per-bar push/remove.
    # Inject gz_bullGZI / gz_bearGZI / gz_bullHV / gz_bearHV via df.attrs.
    "_gz_engine": (
        "GZ1 FVG struct array not reproduced; "
        "inject gz_bullGZI/gz_bearGZI/gz_bullHV/gz_bearHV via df.attrs"
    ),
    # Pentagon / WTC / Hiroshima ratio-driven detections (engine E)
    "det_Pentagon": "raise NotImplementedError('STUBBED: requires tv_ta.relativeVolume — inject rv_relVolRatio')",
    "det_WTC": "raise NotImplementedError('STUBBED: requires tv_ta.relativeVolume — inject rv_relVolRatio')",
    "det_Hiroshima": "raise NotImplementedError('STUBBED: requires tv_ta.relativeVolume — inject rv_relVolRatio')",
    # Long1 / Short1 (rely on tv_ta.relativeVolume(reg) + (cum))
    "det_Long1": "raise NotImplementedError('STUBBED: requires tv_ta.relativeVolume — inject ls_regRatio + ls_cumRatio')",
    "det_Short1": "raise NotImplementedError('STUBBED: requires tv_ta.relativeVolume — inject ls_regRatio + ls_cumRatio')",
}


# ============================================================================
# State machines — the Pine source folds several stateful walkers into one
# pass. We expose them as classes for harness introspection. Each is computed
# inside _ensure_engines(); these classes are markers only.
# ============================================================================
@dataclass
class PBJLandingZoneState:
    """Bull/bear landing-zone arrays + wait_buy/wait_sell + supertrend dir."""
    name: str = "PBJLandingZone"


@dataclass
class TNTZoneState:
    """Bull/bear TNT zone arrays + return-fired tracking + max-zones cap."""
    name: str = "TNTZone"


@dataclass
class ChargeLadderState:
    """Charge level ladder — opposing-violation pushes new same-direction lvl."""
    name: str = "ChargeLadder"


@dataclass
class TNTEventLogState:
    """bull_events / bear_events arrays for TNT 2.0 detection."""
    name: str = "TNTEventLog"


@dataclass
class GZ1FVGState:
    """gz_fvgs struct array — STUBBED engine, exposed for completeness."""
    name: str = "GZ1FVG"


@dataclass
class UUStreakState:
    """u_bull_streak / u_bear_streak + has-Day1 flag for UU/UUU/UUUU."""
    name: str = "UUStreak"


@dataclass
class SuperTrendState:
    """st_dir / curr_long / curr_short ladder driving PBJ engine signal line."""
    name: str = "SuperTrend"


STATE_MACHINES: Dict[str, type] = {
    "PBJLandingZone": PBJLandingZoneState,
    "TNTZone": TNTZoneState,
    "ChargeLadder": ChargeLadderState,
    "TNTEventLog": TNTEventLogState,
    "GZ1FVG": GZ1FVGState,
    "UUStreak": UUStreakState,
    "SuperTrend": SuperTrendState,
}


# ============================================================================
# DETECTIONS registry — name → detect_* function.
# Names mirror Pine plotshape titles so the harness can round-trip with the
# validator.
# ============================================================================
DETECTIONS: Dict[str, Callable] = {
    # Root primitives
    "PUP": detect_PUP,
    "PPD": detect_PPD,
    "b2b PUP": detect_b2bPUP,
    "b2b PPD": detect_b2bPPD,
    "FAUNA Bull": detect_FAUNABull,
    "FAUNA Bear": detect_FAUNABear,
    "DISP Bull": detect_DISPBull,
    "DISP Bear": detect_DISPBear,
    "PBJ Bull": detect_PBJBull,
    "PBJ Bear": detect_PBJBear,
    "PB Bull": detect_PBBull,
    "PB Bear": detect_PBBear,
    "HV+D Bull": detect_HVDBull,
    "HV+D Bear": detect_HVDBear,
    "HV+D+PBJ Bull": detect_HVDPBJBull,
    "HV+D+PBJ Bear": detect_HVDPBJBear,
    "B2B HV+D Bull": detect_B2BHVDBull,
    "B2B HV+D Bear": detect_B2BHVDBear,
    "B2B HV+D+PBJ Bull": detect_B2BHVDPBJBull,
    "B2B HV+D+PBJ Bear": detect_B2BHVDPBJBear,
    "SAAB": detect_SAAB,
    "Kratos": detect_Kratos,
    "RVOL 1x Bull": detect_RVOL1xB,
    "RVOL 1x Bear": detect_RVOL1xR,
    "Grand Slam": detect_GrandSlam,
    "MOAB": detect_MOAB,
    "Nagasaki": detect_Nagasaki,
    "TNT Bull Raw": detect_bullTNT_raw,
    "TNT Bear Raw": detect_bearTNT_raw,
    "TNT Bull": detect_bullTNT,
    "TNT Bear": detect_bearTNT,
    "Napalm Bull": detect_bullNapalm,
    "Napalm Bear": detect_bearNapalm,
    "Charge Bull": detect_bullCharge,
    "Charge Bear": detect_bearCharge,
    "CONT Bull": detect_contBull,
    "CONT Bear": detect_contBear,
    "B2B Napalm Bull": detect_b2bBullNapalm,
    "B2B Napalm Bear": detect_b2bBearNapalm,
    "CS1 Bull": detect_CS1Bull,
    "CS1 Bear": detect_CS1Bear,
    "CS2 Bull": detect_CS2Bull,
    "CS2 Bear": detect_CS2Bear,
    "Unified Bull": detect_UnifiedBull,
    "Unified Bear": detect_UnifiedBear,
    "Neo Bull": detect_NeoBull,
    "Neo Bear": detect_NeoBear,
    "Trinity Bull": detect_TrinityBull,
    "Trinity Bear": detect_TrinityBear,
    "UU Bull": detect_UUBull,
    "UUU Bull": detect_UUUBull,
    "UUUU Bull": detect_UUUUBull,
    "UU Bear": detect_UUBear,
    "UUU Bear": detect_UUUBear,
    "UUUU Bear": detect_UUUUBear,
    # Named plot detections (S1-S6, S8-S18, S19, S20)
    "S1 B2B Bull": detect_S1_bull,
    "S1 B2B Bear": detect_S1_bear,
    "S2 B2B+FAU Bull": detect_S2_bull,
    "S2 B2B+FAU Bear": detect_S2_bear,
    "S3 B2B+DISP Bull": detect_S3_bull,
    "S3 B2B+DISP Bear": detect_S3_bear,
    "S4 B2B+F+D Bull": detect_S4_bull,
    "S4 B2B+F+D Bear": detect_S4_bear,
    "S5 B2B+SAAB Bull": detect_S5_bull,
    "S5 B2B+KRAT Bear": detect_S5_bear,
    "S6 B2B+PBJ Bull": detect_S6_bull,
    "S6 B2B+PBJ Bear": detect_S6_bear,
    "S8 UC+B2B Bull": detect_S8_bull,
    "S8 UC+B2B Bear": detect_S8_bear,
    "S9 Uni+B2B Bull": detect_S9_bull,
    "S9 Uni+B2B Bear": detect_S9_bear,
    "S10 L1 B2B Bull": detect_S10_bull,
    "S10 S1 B2B Bear": detect_S10_bear,
    "S11 FVG/L1 Bull": detect_S11_bull,
    "S11 FVG/S1 Bear": detect_S11_bear,
    "S12 UU+B2B Bull": detect_S12_bull,
    "S12 DD+B2B Bear": detect_S12_bear,
    "S13 B2BNPM Bull": detect_S13_bull,
    "S13 B2BNPM Bear": detect_S13_bear,
    "S14 CONT Bull": detect_S14_bull,
    "S14 CONT Bear": detect_S14_bear,
    "S15 TNT+B2B Bull": detect_S15_bull,
    "S15 TNT+B2B Bear": detect_S15_bear,
    "S16 NPM Bull": detect_S16_bull,
    "S16 NPM Bear": detect_S16_bear,
    "S17 HVD+B2B Bull": detect_S17_bull,
    "S17 HVD+B2B Bear": detect_S17_bear,
    "S18 HVDPBJ Bull": detect_S18_bull,
    "S18 HVDPBJ Bear": detect_S18_bear,
    "S19 UC x2 Bull": detect_S19_UC2_bull,
    "S19 UC x2 Bear": detect_S19_UC2_bear,
    "S20 FMU x2 Bull": detect_S20_FMU_bull,
    "S20 FMU x2 Bear": detect_S20_FMU_bear,
}


if __name__ == "__main__":
    print(f"DETECTIONS: {len(DETECTIONS)}")
    print(f"STUBBED engine notes: {len(STUBBED)}")
    print(f"STATE_MACHINES: {len(STATE_MACHINES)}")
    print("First 5 detection names:")
    for n in list(DETECTIONS)[:5]:
        print("  ", n)
