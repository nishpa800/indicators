"""B2B PUP Combined 5.4 — FULL detection fire-matrix core (Pine-faithful).

Source: "b2b_pup_tickfriendly.pine" (Pine v5, import TradingView/ta/7 as tv_ta),
        June 7 batch, "B2B PUP Combined 5.4 (NINE NINES tick-friendly)".

ULTRACODE FULL PORT — scope statement (read this):
  B2B PUP is a 1273-line aggregator whose 38 detection plots are composed from a
  stack of sub-engines (A..H). THIS MODULE PORTS ALL OF THEM directly from OHLCV
  — there is NO EngineInputs stub layer any more. Every engine below is derived
  bar-by-bar with Pine `var`/history semantics preserved (single forward pass,
  Pine `[k]` = k-bars-back, `conf` = closed bar, nz() fallbacks honoured):

    Engine A  PUP / PPD            (pocket pivot, rolling highest red/green vol)
    Engine B  FAUNA bull/bear      (MB/RE/GG/TA + TR/ES/GDR exclusion ladder)
    Engine C  DISP                 (stdev-displacement + FVG, offset -1)
    Engine D  PBJ                  (VWMA/EMA supertrend cross + landers/reaccel +
                                    approach state -> PB & PBJ buy/sell)
    Engine E  RVOL / Pentagon      (pre-Mythos thresholds, SAAB/KRAT/1x/GS/MOAB,
                                    relativeVolume via canonical shim -> Pentagon/
                                    WTC/Hiroshima, running-ATH Nagasaki)
    Engine F  HV+D                 (HV-rank gate x displacement-FVG, B2B + PBJ)
    Engine G  TNT/Napalm/CONT      (EMA-cross volume blocks + anish swing OBs +
                                    fauna OBs token-window + zone tracking + Napalm
                                    + Charge + TNT2.0 event-log + super + Return +
                                    CONT 3-clause)
    Engine H  Combo/UU/Long1       (GZ FVG-overlap, CS1/CS2/Unified, UC2/FMU
                                    window combos, UU/UUU/UUUU streak scan, Long1)

  relativeVolume ports via the canonical shim tv_ta_shim.relative_volume — never
  re-derived. Every threshold is a parameter (see Params dataclass).

  Tick vs time: ONE code path. The only grain-bound difference is the RVOL anchor
  ("D" wall-clock day on both grains, per tradingview-import-decoupling) and tfSec
  (the per-TF threshold key), which is a parameter.

HONESTY: the parity harness (b2b_pup_parity.py) re-derives every layer
independently and reports REAL pass/total. Nothing is faked. There is no
all-zero stub series in this module — if a plot reads 0 it is because the Pine
logic produced 0 on those bars.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nine_nines_common import Bar  # noqa: E402
from _nn_harness import (  # noqa: E402
    nz, sma, stdev, highest, lowest, atr as _atr_ohlc, cum, relative_volume,
)
import _fauna_core as fauna  # noqa: E402


# ──────────────────────────────── parameters ────────────────────────────────
@dataclass
class Params:
    """Every Pine input.* as a parameter, defaulted to the source default."""
    # MASTER
    en_firstBarOnly: bool = False
    nn_tick_assumed_sec: int = 60
    # Engine A  Pocket Pivot
    pp_barSize: float = 3.0
    pp_lookback: int = 10
    # Engine C  Displacement
    disp_type: str = "Open to Close"
    disp_len: int = 100
    disp_mult: float = 5.0
    # Engine D  PBJ
    zoo_ma_type: str = "VWMA"
    zoo_ma_len: int = 5
    zoo_use_st: bool = True
    zoo_st_period: int = 10
    zoo_st_mult: float = 2.0
    zoo_pbj_ma_period: int = 20
    zoo_pbj_atr_period: int = 14
    zoo_pbj_hh_ll: int = 25
    zoo_pbj_atr_mult: float = 3.0
    zoo_pbj_vol_period: int = 20
    zoo_pbj_vol_mult: float = 0.1
    # Engine E  RVOL
    rv_avgLen: int = 30
    rv_smaLen: int = 20
    # Engine F  HV+D
    hvd_type: str = "Open to Close"
    hvd_len: int = 100
    hvd_mult: float = 5.0
    # Engine G  TNT
    tnt_SENS: int = 100
    tnt_SWING_LEN: int = 10
    tnt_DISP_STD_X: int = 5
    tnt_SUDDEN_PROX: int = 3
    tnt_MAX_ZONES: int = 30
    tnt_RET_PCT: float = 100.0
    # Combo Set
    cs_bodyPct_FVG: float = 0.69
    cs_bodyPct_MAT: float = 0.69
    cs_inc_pent_FVG: bool = True
    cs_inc_pent_MAT: bool = True
    # Unified Combo x2  /  FVG-Matrix-Uni x2
    uc2_min_hits: int = 2
    uc2_window: int = 2
    fmu_min_hits: int = 2
    fmu_window: int = 2
    # threshold-table key (Pine tfSec). 60s assumed on tick.
    tfSec: int = 60
    # syminfo.mintick proxy (Pine syminfo.mintick; deterministic default)
    mintick: float = 0.01
    # detection enables (Pine en_S*; all default True)
    en_S: dict = field(default_factory=dict)

    def en(self, key: str) -> bool:
        return self.en_S.get(key, True)


# ───────────────────────────── helper accessors ─────────────────────────────
def _div(num, den):
    """Pine division: x / 0.0 -> na (None), never a crash. Mirrors Pine float div."""
    if num is None or den is None or den == 0:
        return None
    return num / den


def _prev(series, i, k):
    """Pine series[k] read at bar i (k bars back). None (na) when OOB."""
    j = i - k
    return series[j] if 0 <= j < len(series) else None


def _npv(series, i, k):
    """nz(series[k]) at bar i -> bool, False when OOB (Pine nz on bool)."""
    j = i - k
    return bool(series[j]) if 0 <= j < len(series) else False


def _ma(src, length, kind, v=None):
    """Pine f_ma switch: VWMA/EMA/SMA/WMA/HMA. Returns list (None until warm)."""
    n = len(src)
    if kind == "SMA":
        return sma(src, length)
    if kind == "EMA":
        return _ema(src, length)
    if kind == "WMA":
        return _wma(src, length)
    if kind == "HMA":
        return _hma(src, length)
    if kind == "VWMA":
        return _vwma(src, v, length)
    return sma(src, length)


def _ema(src, length):
    out = [None] * len(src)
    alpha = 2.0 / (length + 1)
    prev = None
    seed_sum = 0.0
    for i, x in enumerate(src):
        x = float(x)
        if prev is None:
            seed_sum += x
            if i + 1 == length:
                prev = seed_sum / length
                out[i] = prev
        else:
            prev = alpha * x + (1 - alpha) * prev
            out[i] = prev
    return out


def _wma(src, length):
    out = [None] * len(src)
    denom = length * (length + 1) / 2.0
    for i in range(len(src)):
        if i + 1 < length:
            continue
        s = 0.0
        for k in range(length):
            s += float(src[i - k]) * (length - k)
        out[i] = s / denom
    return out


def _hma(src, length):
    half = max(1, int(length / 2))
    sq = max(1, int(length ** 0.5))
    w_half = _wma(src, half)
    w_full = _wma(src, length)
    raw = [None if (w_half[i] is None or w_full[i] is None) else 2 * w_half[i] - w_full[i]
           for i in range(len(src))]
    # ta.wma over the raw series, treating None as gap (Pine na-propagates)
    return _wma_na(raw, sq)


def _wma_na(src, length):
    out = [None] * len(src)
    denom = length * (length + 1) / 2.0
    for i in range(len(src)):
        if i + 1 < length:
            continue
        win = src[i - length + 1:i + 1]
        if any(x is None for x in win):
            continue
        s = sum(float(win[length - 1 - k]) * (length - k) for k in range(length))
        out[i] = s / denom
    return out


def _vwma(src, v, length):
    """Pine ta.vwma = sma(src*vol,len)/sma(vol,len)."""
    pv = [float(src[i]) * float(v[i]) for i in range(len(src))]
    num = sma(pv, length)
    den = sma([float(x) for x in v], length)
    return [None if (num[i] is None or den[i] in (None, 0)) else num[i] / den[i]
            for i in range(len(src))]


def _median(values, length):
    """Pine ta.median over a rolling window (None until warm)."""
    out = [None] * len(values)
    from statistics import median as _m
    for i in range(len(values)):
        if i + 1 < length:
            continue
        win = [float(x) for x in values[i - length + 1:i + 1]]
        out[i] = _m(win)
    return out


def _rsi(src, length):
    """Pine ta.rsi = 100 - 100/(1+rma(up)/rma(down))."""
    n = len(src)
    up = [0.0] * n
    dn = [0.0] * n
    for i in range(1, n):
        ch = float(src[i]) - float(src[i - 1])
        up[i] = max(ch, 0.0)
        dn[i] = max(-ch, 0.0)
    ru = _rma_simple(up, length)
    rd = _rma_simple(dn, length)
    out = [None] * n
    for i in range(n):
        if ru[i] is None or rd[i] is None:
            continue
        if rd[i] == 0:
            out[i] = 100.0
        else:
            rs = ru[i] / rd[i]
            out[i] = 100.0 - 100.0 / (1.0 + rs)
    return out


def _rma_simple(values, length):
    out = [None] * len(values)
    prev = None
    seed = 0.0
    for i, v in enumerate(values):
        v = float(v)
        if prev is None:
            seed += v
            if i + 1 == length:
                prev = seed / length
                out[i] = prev
        else:
            prev = (prev * (length - 1) + v) / length
            out[i] = prev
    return out


def _crossover(a, b):
    n = len(a)
    out = [False] * n
    for i in range(1, n):
        if a[i] is None or b[i] is None or a[i - 1] is None or b[i - 1] is None:
            continue
        out[i] = a[i - 1] <= b[i - 1] and a[i] > b[i]
    return out


def _crossunder(a, b):
    n = len(a)
    out = [False] * n
    for i in range(1, n):
        if a[i] is None or b[i] is None or a[i - 1] is None or b[i - 1] is None:
            continue
        out[i] = a[i - 1] >= b[i - 1] and a[i] < b[i]
    return out


# ─────────────────────────── RVOL threshold tables ──────────────────────────
def f_th_1x(s: int) -> float:
    return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else 23.0 if s <= 45
            else 20.0 if s <= 60 else 18.0 if s <= 120 else 13.0 if s <= 300 else 13.0 if s <= 360
            else 11.0 if s <= 540 else 10.0 if s <= 600 else 9.0 if s <= 660 else 7.5 if s <= 900
            else 6.5 if s <= 1560 else 6.0 if s <= 2340 else 4.5 if s <= 3600 else 4.0 if s <= 9000
            else 3.5 if s <= 11700 else 1.8 if s < 259200 else 1.0)


def f_th_gs(s: int) -> float:
    return (f_th_1x(s) * 3.0 if s < 60 else 35.0 if s <= 300 else 25.0 if s <= 600
            else 20.0 if s <= 1500 else 20.0 if s <= 3000 else 10.0 if s <= 7260
            else 8.0 if s <= 11700 else 7.5 if s <= 86400 else 3.5 if s <= 259200 else 3.0)


def f_th_saab(s: int) -> float:
    return f_th_1x(s) * 0.56


def f_th_wtc(s: int) -> float:
    return f_th_1x(s) * 2.0


def f_th_hiro(s: int) -> float:
    return (f_th_1x(s) * 3.0 if s < 60 else 35.0 if s <= 300 else 25.0 if s <= 600
            else 25.0 if s <= 1500 else 20.0 if s <= 3060 else 10.0 if s <= 7260
            else 8.0 if s <= 11700 else 7.5 if s <= 86400 else 5.0 if s <= 259200 else 3.5)


# ───────────────────────────── the full compute ─────────────────────────────
def compute(bars: Sequence[Bar], *, params: Params | None = None,
            session_first_bar_idx=None, rv_anchor: str = "D"):
    """Return the 38-plot fire matrix + numeric levels for B2B PUP 5.4.

    bars: oldest-first OHLCV bars (tick OR time grain — identical code path).
    params: Params (source defaults if None).
    session_first_bar_idx: per-bar index of the session's first bar (for the
        first-bar gate). If None, the gate is open (matches en_firstBarOnly=False).
    rv_anchor: relativeVolume anchor timeframe ("D" both grains).
    """
    P = params or Params()
    n = len(bars)
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    l = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]
    conf = [True] * n  # closed-bar series only (Pine barstate.isconfirmed)

    if n == 0:
        return {"ts": []}

    # is_new_day = ta.change(time("D")) != 0   (day rollover)
    from datetime import datetime, timezone
    day_ord = [datetime.fromtimestamp(t / 1000, tz=timezone.utc).toordinal() for t in ts]
    is_new_day = [True] + [day_ord[i] != day_ord[i - 1] for i in range(1, n)]

    # session first-bar flag (isFirstBar) from session_first_bar_idx
    if session_first_bar_idx is None:
        isFirstBar = [is_new_day[i] for i in range(n)]
    else:
        isFirstBar = [session_first_bar_idx[i] == i for i in range(n)]

    # ── _FIRST string (gap classification) — used in alerts/levels only ──
    # masterGate / first-bar gates
    det_anyHV = [False] * n
    for i in range(n):
        for look in (50, 100, 200, 500, 1000):
            lo = max(0, i - look + 1)
            if v[i] == max(v[lo:i + 1]):
                det_anyHV[i] = True
                break
    masterGate = [True] * n
    if P.en_firstBarOnly:
        for i in range(n):
            masterGate[i] = isFirstBar[i] and det_anyHV[i]

    # ════════════════ ENGINE A — PUP / PPD ════════════════
    redVol = [v[i] if c[i] < o[i] else 0.0 for i in range(n)]
    greenVol = [v[i] if c[i] > o[i] else 0.0 for i in range(n)]

    def highest_prev(series, look, i):
        # ta.highest(series[1], look) at bar i = max over [i-look .. i-1]
        lo = max(0, i - look)
        win = series[lo:i]
        return max(win) if win else 0.0

    det_PUP = [False] * n
    det_PPD = [False] * n
    for i in range(n):
        hiRed = highest_prev(redVol, P.pp_lookback, i)
        hiGreen = highest_prev(greenVol, P.pp_lookback, i)
        if o[i] != 0:
            det_PUP[i] = ((c[i] - o[i]) / o[i]) * 100 > P.pp_barSize and v[i] > hiRed
            det_PPD[i] = ((o[i] - c[i]) / o[i]) * 100 > P.pp_barSize and v[i] > hiGreen
    det_b2bPUP = [det_PUP[i] and _npv(det_PUP, i, 1) for i in range(n)]
    det_b2bPPD = [det_PPD[i] and _npv(det_PPD, i, 1) for i in range(n)]

    # ════════════════ ENGINE B — FAUNA ════════════════
    fam = fauna._families(bars)
    f_body = [c[i] - o[i] for i in range(n)]
    f_rng = [h[i] - l[i] for i in range(n)]
    f_bodySz = [abs(x) for x in f_body]
    f_bodyRat = [0.0 if f_rng[i] == 0 else f_bodySz[i] / f_rng[i] for i in range(n)]
    f_b_core = [(1 if fam["MBb"][i] else 0) + (1 if fam["REb"][i] else 0) + (1 if fam["TAb"][i] else 0) for i in range(n)]
    f_s_core = [(1 if fam["MBs"][i] else 0) + (1 if fam["REs"][i] else 0) + (1 if fam["TAs"][i] else 0) for i in range(n)]
    f_excluded_bull = [fam["TRb"][i] or fam["ESb"][i] or fam["GDRb"][i]
                       or (fam["GGb"][i] and not (f_b_core[i] >= 2 and f_bodyRat[i] >= 0.80)) for i in range(n)]
    f_excluded_bear = [fam["TRs"][i] or fam["ESs"][i] or fam["GDRs"][i]
                       or (fam["GGs"][i] and not (f_s_core[i] >= 2 and f_bodyRat[i] >= 0.80)) for i in range(n)]
    det_FAUNABull = [(fam["MBb"][i] or fam["REb"][i] or fam["TAb"][i]) and not f_excluded_bull[i] for i in range(n)]
    det_FAUNABear = [(fam["MBs"][i] or fam["REs"][i] or fam["TAs"][i]) and not f_excluded_bear[i] for i in range(n)]

    f_ATR14 = _atr_ohlc(o, h, l, c, 14)

    # ════════════════ ENGINE C — DISPLACEMENT (offset -1) ════════════════
    disp_rng = [abs(o[i] - c[i]) if P.disp_type == "Open to Close" else h[i] - l[i] for i in range(n)]
    disp_std = stdev(disp_rng, P.disp_len)
    disp_thresh = [None if disp_std[i] is None else disp_std[i] * P.disp_mult for i in range(n)]
    disp_prevDisp = [i >= 1 and disp_thresh[i - 1] is not None and disp_rng[i - 1] > disp_thresh[i - 1] for i in range(n)]
    disp_bullFVG = [i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1] for i in range(n)]
    disp_bearFVG = [i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1] for i in range(n)]
    det_DISPBull = [disp_prevDisp[i] and disp_bullFVG[i] for i in range(n)]
    det_DISPBear = [disp_prevDisp[i] and disp_bearFVG[i] for i in range(n)]

    # ════════════════ ENGINE D — PBJ (supertrend + landers + approach) ═════════
    base_ma = _ma(c, P.zoo_ma_len, P.zoo_ma_type, v)
    st_atr_series = _atr_ohlc(o, h, l, c, P.zoo_st_period)
    pbj_ma = _ema(c, P.zoo_pbj_ma_period)
    pbj_atr = _atr_ohlc(o, h, l, c, P.zoo_pbj_atr_period)
    avg_vol_pbj = sma(v, P.zoo_pbj_vol_period)

    sig_line = [0.0] * n
    st_dir = [1] * n          # var int st_dir = 1
    curr_long = [0.0] * n
    curr_short = [0.0] * n
    for i in range(n):
        bm = base_ma[i]
        st_atr = (P.zoo_st_mult * st_atr_series[i]) if st_atr_series[i] is not None else 0.0
        dyn_long = (bm - st_atr) if bm is not None else 0.0
        dyn_short = (bm + st_atr) if bm is not None else 0.0
        prev_cl = curr_long[i - 1] if i > 0 else None
        prev_cs = curr_short[i - 1] if i > 0 else None
        # curr_long := base>nz(curr_long[1],dyn_long) ? max(dyn_long,nz(curr_long[1])) : dyn_long
        cl_ref = nz(prev_cl, dyn_long)
        if bm is not None and bm > cl_ref:
            curr_long[i] = max(dyn_long, nz(prev_cl, 0.0))
        else:
            curr_long[i] = dyn_long
        cs_ref = nz(prev_cs, dyn_short)
        if bm is not None and bm < cs_ref:
            curr_short[i] = min(dyn_short, nz(prev_cs, 0.0))
        else:
            curr_short[i] = dyn_short
        if P.zoo_use_st:
            pdir = st_dir[i - 1] if i > 0 else 1
            d = pdir
            if nz(pdir) == -1 and c[i] > nz(prev_cs, 0.0):
                d = 1
            elif nz(pdir) == 1 and c[i] < nz(prev_cl, 0.0):
                d = -1
            st_dir[i] = d
            sig_line[i] = curr_long[i] if d == 1 else curr_short[i]
        else:
            st_dir[i] = 1
            sig_line[i] = bm if bm is not None else 0.0

    buy_cross = _crossover(c, sig_line)
    sell_cross = _crossunder(c, sig_line)
    bull_reaccel = [st_dir[i] == 1 and i >= 2 and sig_line[i] > nz(sig_line[i - 1])
                    and nz(sig_line[i - 1]) == nz(sig_line[i - 2]) for i in range(n)]
    bear_reaccel = [st_dir[i] == -1 and i >= 2 and sig_line[i] < nz(sig_line[i - 1])
                    and nz(sig_line[i - 1]) == nz(sig_line[i - 2]) for i in range(n)]

    zoo_thresh = [0.0 if c[i] == 0 or pbj_atr[i] is None else (pbj_atr[i] / c[i] * P.zoo_pbj_atr_mult) for i in range(n)]
    low_lowest = lowest(l, P.zoo_pbj_hh_ll)
    high_highest = highest(h, P.zoo_pbj_hh_ll)
    pbj_buy = [pbj_ma[i] is not None and low_lowest[i] is not None and avg_vol_pbj[i] is not None
               and l[i] < pbj_ma[i] * (1 - zoo_thresh[i]) and l[i] == low_lowest[i]
               and v[i] > avg_vol_pbj[i] * P.zoo_pbj_vol_mult for i in range(n)]
    pbj_sell = [pbj_ma[i] is not None and high_highest[i] is not None and avg_vol_pbj[i] is not None
                and h[i] > pbj_ma[i] * (1 + zoo_thresh[i]) and h[i] == high_highest[i]
                and v[i] > avg_vol_pbj[i] * P.zoo_pbj_vol_mult for i in range(n)]

    # level arrays (lvl UDT) with approach state machine (PB engine)
    atr_pb = [(f_ATR14[i] * 2.0) if f_ATR14[i] is not None else 0.0 for i in range(n)]
    bull_lvls = []  # each: [upper, lower, vol, approached]
    bear_lvls = []
    wait_buy = wait_sell = wait_pbj_buy = wait_pbj_sell = False
    det_PBJBull = [False] * n
    det_PBJBear = [False] * n
    det_PBBull = [False] * n
    det_PBBear = [False] * n

    def add_lvl(arr, up, lo, vol):
        if abs(up - lo) >= P.mintick:
            arr.append([up, lo, vol, False])

    def add_lander_bull(i):
        if buy_cross[i] and i >= 1:
            up = max(o[i - 1], c[i - 1])
            lo = l[i - 1]
            if up - lo < atr_pb[i] * 0.5:
                up = lo + atr_pb[i] * 0.5
            add_lvl(bull_lvls, up, lo, v[i - 1])

    def add_lander_bear(i):
        if sell_cross[i] and i >= 1:
            up = h[i - 1]
            lo = min(o[i - 1], c[i - 1])
            if up - lo < atr_pb[i] * 0.5:
                lo = up - atr_pb[i] * 0.5
            add_lvl(bear_lvls, up, lo, v[i - 1])

    def add_reaccel(is_bull, sig, i):
        if sig and sig_line[i] is not None:
            p1 = sig_line[i]
            p2 = min(o[i], c[i]) if is_bull else max(o[i], c[i])
            add_lvl(bull_lvls if is_bull else bear_lvls, max(p1, p2), min(p1, p2), v[i])

    def check_approach(arr, is_bull, i):
        approached = False
        for idx in range(len(arr) - 1, -1, -1):
            up, lo, vol, appr = arr[idx]
            if is_bull and c[i] < lo:
                arr.pop(idx)
                continue
            if not is_bull and c[i] > up:
                arr.pop(idx)
                continue
            ap = up * 1.005 if is_bull else lo * 0.995
            if is_bull:
                if not appr and l[i] <= ap:
                    approached = True
                    arr[idx][3] = True
                elif appr and l[i] > up:
                    arr[idx][3] = False
            else:
                if not appr and h[i] >= ap:
                    approached = True
                    arr[idx][3] = True
                elif appr and h[i] < lo:
                    arr[idx][3] = False
        return approached

    for i in range(n):
        add_lander_bull(i)
        add_lander_bear(i)
        add_reaccel(True, bull_reaccel[i], i)
        add_reaccel(False, bear_reaccel[i], i)
        if conf[i]:
            if check_approach(bull_lvls, True, i):
                wait_buy = True
            if check_approach(bear_lvls, False, i):
                wait_sell = True
        if pbj_buy[i]:
            wait_pbj_buy = True
        if pbj_sell[i]:
            wait_pbj_sell = True
        while len(bull_lvls) > 30:
            bull_lvls.pop(0)
        while len(bear_lvls) > 30:
            bear_lvls.pop(0)
        sig_pb_buy = buy_cross[i] and wait_buy
        sig_pbj_buy = buy_cross[i] and wait_pbj_buy
        sig_pb_sell = sell_cross[i] and wait_sell
        sig_pbj_sell = sell_cross[i] and wait_pbj_sell
        if sig_pb_buy:
            wait_buy = False
        if sig_pbj_buy:
            wait_pbj_buy = False
        if sig_pb_sell:
            wait_sell = False
        if sig_pbj_sell:
            wait_pbj_sell = False
        det_PBJBull[i] = sig_pbj_buy
        det_PBJBear[i] = sig_pbj_sell
        det_PBBull[i] = sig_pb_buy and not sig_pbj_buy
        det_PBBear[i] = sig_pb_sell and not sig_pbj_sell

    # ════════════════ ENGINE E — RVOL / Pentagon ════════════════
    rv_spike = [abs(c[i] - o[i]) for i in range(n)]
    rv_avgSpike_now = sma(rv_spike, P.rv_avgLen)
    rv_avgSpike = [rv_avgSpike_now[i - 1] if i >= 1 else None for i in range(n)]  # [1] shift
    # rv_normPrice = rv_spike / nz(rv_avgSpike, 1.0). nz replaces na->1.0; a real
    # 0.0 stays 0.0 and Pine x/0.0 = na (None). 0.0 yields na too (0/1.0=0 -> but
    # if avgSpike==0 it's not na so denom 0 -> na).
    rv_normPrice_raw = [_div(rv_spike[i], nz(rv_avgSpike[i], 1.0)) for i in range(n)]
    rv_normPrice = [0.0 if x is None else x for x in rv_normPrice_raw]  # na compares false vs thresholds
    rv_avgVol_now = sma(v, P.rv_avgLen)
    rv_avgVol = [rv_avgVol_now[i - 1] if i >= 1 else None for i in range(n)]
    rv_normVol_raw = [_div(v[i], nz(rv_avgVol[i], 1.0)) for i in range(n)]
    rv_normVol = [0.0 if x is None else x for x in rv_normVol_raw]
    rv_diff = [rv_normPrice[i] - rv_normVol[i] for i in range(n)]
    rv_posDiff = [rv_diff[i] if rv_diff[i] > 0 else None for i in range(n)]
    rv_smaDiff = sma(rv_posDiff, P.rv_smaLen)
    rv_baseBull = [c[i] > o[i] and rv_posDiff[i] is not None and rv_smaDiff[i] is not None
                   and rv_posDiff[i] > rv_smaDiff[i] for i in range(n)]
    rv_baseBear = [c[i] < o[i] and rv_posDiff[i] is not None and rv_smaDiff[i] is not None
                   and rv_posDiff[i] > rv_smaDiff[i] for i in range(n)]

    th_saab = f_th_saab(P.tfSec)
    th_1x = f_th_1x(P.tfSec)
    th_gs = f_th_gs(P.tfSec)
    th_wtc = f_th_wtc(P.tfSec)
    th_hiro = f_th_hiro(P.tfSec)

    det_SAAB = [rv_baseBull[i] and rv_normPrice[i] >= th_saab and rv_normPrice[i] < th_1x for i in range(n)]
    det_Kratos = [rv_baseBear[i] and rv_normPrice[i] >= th_saab and rv_normPrice[i] < th_1x for i in range(n)]
    det_RVOL1xB = [rv_baseBull[i] and rv_normPrice[i] >= th_1x and rv_normPrice[i] < th_gs for i in range(n)]
    det_RVOL1xR = [rv_baseBear[i] and rv_normPrice[i] >= th_1x and rv_normPrice[i] < th_gs for i in range(n)]
    det_GrandSlam = [rv_baseBull[i] and rv_normPrice[i] >= th_gs for i in range(n)]
    det_MOAB = [rv_baseBear[i] and rv_normPrice[i] >= th_gs for i in range(n)]

    # relativeVolume via canonical shim (regular, cumulative-anchored)
    rv_cur, rv_past, _ = relative_volume(v, 30, anchor_timeframe=rv_anchor,
                                         is_cumulative=True, bar_timestamps=ts)
    rv_relVolRatio = [None if (rv_past[i] in (None, 0)) else rv_cur[i] / rv_past[i] for i in range(n)]
    det_Pentagon = [rv_relVolRatio[i] is not None and rv_relVolRatio[i] >= th_1x and rv_relVolRatio[i] <= th_wtc for i in range(n)]
    det_WTC = [rv_relVolRatio[i] is not None and rv_relVolRatio[i] > th_wtc and rv_relVolRatio[i] <= th_hiro for i in range(n)]
    det_Hiroshima = [rv_relVolRatio[i] is not None and rv_relVolRatio[i] > th_hiro for i in range(n)]

    # Nagasaki: running ATH volume
    det_Nagasaki = [False] * n
    rv_maxVol = 0.0
    for i in range(n):
        if i == 0:
            rv_maxVol = v[i]
        elif v[i] > rv_maxVol:
            det_Nagasaki[i] = True
            rv_maxVol = v[i]

    # ════════════════ ENGINE F — HV+D (offset -1) ════════════════
    hvd_rng = [abs(o[i] - c[i]) if P.hvd_type == "Open to Close" else h[i] - l[i] for i in range(n)]
    hvd_std = stdev(hvd_rng, P.hvd_len)
    hvd_thr = [None if hvd_std[i] is None else hvd_std[i] * P.hvd_mult for i in range(n)]
    hvd_prevDisp = [i >= 1 and hvd_thr[i - 1] is not None and hvd_rng[i - 1] > hvd_thr[i - 1] for i in range(n)]
    hvd_bullFVG = [i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1] for i in range(n)]
    hvd_bearFVG = [i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1] for i in range(n)]
    hvd_dispBull = [hvd_prevDisp[i] and hvd_bullFVG[i] for i in range(n)]
    hvd_dispBear = [hvd_prevDisp[i] and hvd_bearFVG[i] for i in range(n)]

    def hv_rank_prev(look, i):
        # volume[1] == ta.highest(volume,look)[1]  -> max over [i-look .. i-1] == v[i-1]
        if i < 1:
            return False
        lo = max(0, i - look)
        win = v[lo:i]
        return bool(win) and v[i - 1] == max(win)
    hv_isHEV = [False] * n
    hv_maxVolEver = 0.0
    for i in range(n):
        if i >= 1 and v[i - 1] > hv_maxVolEver:
            hv_maxVolEver = v[i - 1]
            hv_isHEV[i] = True
    hv_base_hit = [hv_isHEV[i] or hv_rank_prev(1000, i) or hv_rank_prev(500, i)
                   or hv_rank_prev(200, i) or hv_rank_prev(100, i) or hv_rank_prev(50, i) for i in range(n)]
    det_HVDBull = [hv_base_hit[i] and hvd_dispBull[i] for i in range(n)]
    det_HVDBear = [hv_base_hit[i] and hvd_dispBear[i] for i in range(n)]
    det_HVDPBJBull = [det_HVDBull[i] and _npv(det_PBJBull, i, 1) for i in range(n)]
    det_HVDPBJBear = [det_HVDBear[i] and _npv(det_PBJBear, i, 1) for i in range(n)]
    det_B2BHVDBull = [det_HVDBull[i] and _npv(det_HVDBull, i, 1) for i in range(n)]
    det_B2BHVDBear = [det_HVDBear[i] and _npv(det_HVDBear, i, 1) for i in range(n)]
    det_B2BHVDPBJBull = [det_B2BHVDBull[i] and (_npv(det_PBJBull, i, 1) or _npv(det_PBJBull, i, 2)) for i in range(n)]
    det_B2BHVDPBJBear = [det_B2BHVDBear[i] and (_npv(det_PBJBear, i, 1) or _npv(det_PBJBear, i, 2)) for i in range(n)]

    # ════════════════ ENGINE G — TNT / NAPALM / CONT ════════════════
    (det_bullTNT, det_bearTNT, det_bullTNT_raw, det_bearTNT_raw,
     det_bullNapalm, det_bearNapalm, det_bullCharge, det_bearCharge,
     det_retBullTNT, det_retBearTNT, det_contBull, det_contBear,
     det_bullNapCons, det_bearNapCons, det_b2bBullNapalm, det_b2bBearNapalm) = _engine_tnt(
        o, h, l, c, v, conf, P)

    # ════════════════ ENGINE H — Combo / UU / Long1 ════════════════
    # GZ1 / HV FVG
    gz_hv252 = highest(v, 252)
    gz_hv63 = highest(v, 63)
    gz_isHV = [i >= 1 and ((gz_hv252[i - 1] is not None and v[i - 1] == gz_hv252[i - 1])
                           or (gz_hv63[i - 1] is not None and v[i - 1] == gz_hv63[i - 1])) for i in range(n)]
    cum_rng = cum([_div(h[i] - l[i], l[i]) or 0.0 for i in range(n)])
    # Pine gz_thr = ta.cum(...) / bar_index ; bar_index is 0-indexed (0 on bar 0
    # -> na). None on bar 0; comparisons against None are false (Pine na compare).
    gz_thr = [_div(cum_rng[i], i) for i in range(n)]
    gz_bFVG = [False] * n
    gz_sFVG = [False] * n
    for i in range(n):
        if i >= 2 and h[i - 2] != 0 and gz_thr[i] is not None:
            r = _div(l[i] - h[i - 2], h[i - 2])
            gz_bFVG[i] = (l[i] > h[i - 2] and c[i - 1] > h[i - 2]
                          and r is not None and r > gz_thr[i])
        if i >= 2 and h[i] != 0 and gz_thr[i] is not None:
            r = _div(l[i - 2] - h[i], h[i])
            gz_sFVG[i] = (h[i] < l[i - 2] and c[i - 1] < l[i - 2]
                          and r is not None and r > gz_thr[i])
    # FVG-overlap state (gz_fvgs array) -> gz_bullGZI/bearGZI/bullHV/bearHV
    gz_bullGZI = [False] * n
    gz_bearGZI = [False] * n
    gz_bullHV = [False] * n
    gz_bearHV = [False] * n
    gz_fvgs = []  # each: [mx, mn, bull, idx, hv]
    gz_lastT = 0
    for i in range(n):
        if conf[i] and gz_bFVG[i] and ts[i] != gz_lastT:
            mx = l[i]
            mn = h[i - 2]
            if gz_isHV[i]:
                gz_bullHV[i] = True
            for e in gz_fvgs:  # iterate 0..size-1
                emx, emn, ebull, eidx, ehv = e
                if ebull and i - eidx <= 7:
                    if max(emn, mn) < min(emx, mx) or (max(emn, mn) <= min(emx, mx) and ehv and gz_isHV[i]):
                        gz_bullGZI[i] = True
                        break
            gz_fvgs.insert(0, [mx, mn, True, i, gz_isHV[i]])
            gz_lastT = ts[i]
        if conf[i] and gz_sFVG[i] and ts[i] != gz_lastT:
            mx = l[i - 2]
            mn = h[i]
            if gz_isHV[i]:
                gz_bearHV[i] = True
            for e in gz_fvgs:
                emx, emn, ebull, eidx, ehv = e
                if (not ebull) and i - eidx <= 7:
                    if max(emn, mn) < min(emx, mx) or (max(emn, mn) <= min(emx, mx) and ehv and gz_isHV[i]):
                        gz_bearGZI[i] = True
                        break
            gz_fvgs.insert(0, [mx, mn, False, i, gz_isHV[i]])
            gz_lastT = ts[i]
        # cull broken FVGs (iterate high->low)
        for idx in range(len(gz_fvgs) - 1, -1, -1):
            gmx, gmn, gbull, gidx, ghv = gz_fvgs[idx]
            if gbull and c[i] < gmn:
                gz_fvgs.pop(idx)
            elif (not gbull) and c[i] > gmx:
                gz_fvgs.pop(idx)
        if len(gz_fvgs) > 50:
            gz_fvgs.pop()

    # CS1 FVG Combo (offset -1, body% on bar[1])
    cs_bp1 = [0.0 if i < 1 or (h[i - 1] - l[i - 1]) == 0 else abs(c[i - 1] - o[i - 1]) / (h[i - 1] - l[i - 1]) for i in range(n)]
    cs_vb = [cs_bp1[i] >= P.cs_bodyPct_FVG for i in range(n)]
    comboSet1_Bull = [cs_vb[i] and (gz_bullHV[i] or gz_bullGZI[i]) and (_npv(det_SAAB, i, 1) or _npv(det_RVOL1xB, i, 1) or _npv(det_GrandSlam, i, 1)) for i in range(n)]
    comboSet1_Bear = [cs_vb[i] and (gz_bearHV[i] or gz_bearGZI[i]) and (_npv(det_Kratos, i, 1) or _npv(det_RVOL1xR, i, 1) or _npv(det_MOAB, i, 1)) for i in range(n)]
    comboSet2_Bull = [cs_vb[i] and (gz_bullHV[i] or gz_bullGZI[i]) and ((P.cs_inc_pent_FVG and _npv(det_Pentagon, i, 1)) or _npv(det_WTC, i, 1) or _npv(det_Hiroshima, i, 1) or _npv(det_Nagasaki, i, 1)) for i in range(n)]
    comboSet2_Bear = [cs_vb[i] and (gz_bearHV[i] or gz_bearGZI[i]) and ((P.cs_inc_pent_FVG and _npv(det_Pentagon, i, 1)) or _npv(det_WTC, i, 1) or _npv(det_Hiroshima, i, 1) or _npv(det_Nagasaki, i, 1)) for i in range(n)]
    det_CS1Bull = [comboSet1_Bull[i] or comboSet2_Bull[i] for i in range(n)]
    det_CS1Bear = [comboSet1_Bear[i] or comboSet2_Bear[i] for i in range(n)]

    # CS2 MAT Combo (offset 0, body% on bar[0])
    ls_bodyRat = [0.0 if f_rng[i] == 0 else f_bodySz[i] / f_rng[i] for i in range(n)]
    cs_vm = [ls_bodyRat[i] >= P.cs_bodyPct_MAT for i in range(n)]
    hv67 = highest(v, 67)
    is_matrix_number = [hv67[i] is not None and v[i] == hv67[i] for i in range(n)]
    det_NeoBull = [is_matrix_number[i] and det_FAUNABull[i] for i in range(n)]
    det_NeoBear = [is_matrix_number[i] and det_FAUNABear[i] for i in range(n)]
    det_TrinityBull = [is_matrix_number[i] and not det_FAUNABull[i] and c[i] > o[i] for i in range(n)]
    det_TrinityBear = [is_matrix_number[i] and not det_FAUNABear[i] and c[i] < o[i] for i in range(n)]
    matrix_any_bull = [det_NeoBull[i] or det_TrinityBull[i] for i in range(n)]
    matrix_any_bear = [det_NeoBear[i] or det_TrinityBear[i] for i in range(n)]
    comboSet3_Bull = [cs_vm[i] and matrix_any_bull[i] and (det_SAAB[i] or det_RVOL1xB[i] or det_GrandSlam[i]) for i in range(n)]
    comboSet3_Bear = [cs_vm[i] and matrix_any_bear[i] and (det_Kratos[i] or det_RVOL1xR[i] or det_MOAB[i]) for i in range(n)]
    comboSet4_Bull = [cs_vm[i] and matrix_any_bull[i] and ((P.cs_inc_pent_MAT and det_Pentagon[i]) or det_WTC[i] or det_Hiroshima[i] or det_Nagasaki[i]) for i in range(n)]
    comboSet4_Bear = [cs_vm[i] and matrix_any_bear[i] and ((P.cs_inc_pent_MAT and det_Pentagon[i]) or det_WTC[i] or det_Hiroshima[i] or det_Nagasaki[i]) for i in range(n)]
    det_CS2Bull = [comboSet3_Bull[i] or comboSet4_Bull[i] for i in range(n)]
    det_CS2Bear = [comboSet3_Bear[i] or comboSet4_Bear[i] for i in range(n)]
    det_UnifiedBull = [det_CS1Bull[i] and _npv(det_CS2Bull, i, 1) for i in range(n)]
    det_UnifiedBear = [det_CS1Bear[i] and _npv(det_CS2Bear, i, 1) for i in range(n)]

    # Long1 / Short1 (regular + cumulative RVOL)
    ls_cur_r, ls_past_r, _ = relative_volume(v, 30, anchor_timeframe=rv_anchor, is_cumulative=False, bar_timestamps=ts)
    ls_cur_c, ls_past_c, _ = relative_volume(v, 30, anchor_timeframe=rv_anchor, is_cumulative=True, bar_timestamps=ts)
    ls_regRatio = [nz(None if ls_past_r[i] in (None, 0) else ls_cur_r[i] / ls_past_r[i]) for i in range(n)]
    ls_cumRatio = [nz(None if ls_past_c[i] in (None, 0) else ls_cur_c[i] / ls_past_c[i]) for i in range(n)]
    det_Long1 = [ls_regRatio[i] > 7.0 and ls_cumRatio[i] > 3.5 and c[i] > o[i] and ls_bodyRat[i] >= 0.60 for i in range(n)]
    det_Short1 = [ls_regRatio[i] > 7.0 and ls_cumRatio[i] > 3.5 and c[i] < o[i] and ls_bodyRat[i] >= 0.60 for i in range(n)]

    # PLOT A — Unified Combo x2 (window scan)
    def uc2_count(i, csA0, csA1, csB, window):
        cnt = 0
        for V in range(1, window + 1):
            cs1_v = _npv(csA0, i, V - 1) or _npv(csA1, i, V - 1)
            cs2_v = _npv(csB[0], i, V) or _npv(csB[1], i, V)
            if cs1_v and cs2_v:
                cnt += 1
        return cnt
    det_UC2Bull = [conf[i] and uc2_count(i, comboSet1_Bull, comboSet2_Bull, (comboSet3_Bull, comboSet4_Bull), P.uc2_window) >= P.uc2_min_hits for i in range(n)]
    det_UC2Bear = [conf[i] and uc2_count(i, comboSet1_Bear, comboSet2_Bear, (comboSet3_Bear, comboSet4_Bear), P.uc2_window) >= P.uc2_min_hits for i in range(n)]

    def fmu_count(i, csA0, csA1, csB, window):
        cnt = 0
        for V in range(1, window + 1):
            cs1_v = _npv(csA0, i, V - 1) or _npv(csA1, i, V - 1)
            cs2_v = _npv(csB[0], i, V) or _npv(csB[1], i, V)
            if cs1_v or cs2_v:
                cnt += 1
        return cnt
    det_FMUBull = [conf[i] and fmu_count(i, comboSet1_Bull, comboSet2_Bull, (comboSet3_Bull, comboSet4_Bull), P.fmu_window) >= P.fmu_min_hits for i in range(n)]
    det_FMUBear = [conf[i] and fmu_count(i, comboSet1_Bear, comboSet2_Bear, (comboSet3_Bear, comboSet4_Bear), P.fmu_window) >= P.fmu_min_hits for i in range(n)]

    # UU / UUU / UUUU (Squareify A-F streak scans)
    u_qual_bull = [rv_baseBull[i] and rv_normPrice[i] >= 0.5 for i in range(n)]
    u_qual_bear = [rv_baseBear[i] and rv_normPrice[i] >= 0.5 for i in range(n)]
    u_bull_streak = [0] * n
    u_bear_streak = [0] * n
    u_bull_hasDay1 = [False] * n
    u_bear_hasDay1 = [False] * n
    bs = bds1 = 0
    bhd = False
    es = eds1 = 0
    ehd = False
    for i in range(n):
        if u_qual_bull[i]:
            bs += 1
            bhd = bhd or is_new_day[i]
        else:
            bs = 0
            bhd = False
        if u_qual_bear[i]:
            es += 1
            ehd = ehd or is_new_day[i]
        else:
            es = 0
            ehd = False
        u_bull_streak[i] = bs
        u_bull_hasDay1[i] = bhd
        u_bear_streak[i] = es
        u_bear_hasDay1[i] = ehd

    def uu_scan(i, nn_, bull):
        hp = hpb = hh = hd = hf = False
        ad = asd = True
        dnp = pnd = False
        for k in range(nn_):
            if bull:
                bpbj = _npv(det_PBJBull, i, k)
                bpb = _npv(det_PBBull, i, k)
                bhvd = _npv(det_HVDBull, i, k - 1) if k >= 1 else False
                bdisp = _npv(det_DISPBull, i, k) or bhvd
                bfauna = _npv(det_FAUNABull, i, k)
                bsaab = _npv(det_SAAB, i, k) or _npv(det_RVOL1xB, i, k) or _npv(det_GrandSlam, i, k)
            else:
                bpbj = _npv(det_PBJBear, i, k)
                bpb = _npv(det_PBBear, i, k)
                bhvd = _npv(det_HVDBear, i, k - 1) if k >= 1 else False
                bdisp = _npv(det_DISPBear, i, k) or bhvd
                bfauna = _npv(det_FAUNABear, i, k)
                bsaab = _npv(det_Kratos, i, k) or _npv(det_RVOL1xR, i, k) or _npv(det_MOAB, i, k)
            bdf = bdisp or bfauna
            if bpbj:
                hp = True
            if bpb:
                hpb = True
            if bhvd:
                hh = True
            if bdisp:
                hd = True
            if bfauna:
                hf = True
            if not bdisp:
                ad = False
            if not bsaab or not bdf:
                asd = False
            if bdf and not bpbj:
                dnp = True
            if bpbj and not bdf:
                pnd = True
        return hp, hpb, hh, hd, hf, ad, asd, dnp, pnd

    det_UUUUBull = [False] * n
    det_UUUBull = [False] * n
    det_UUBull = [False] * n
    det_UUUUBear = [False] * n
    det_UUUBear = [False] * n
    det_UUBear = [False] * n
    for i in range(n):
        # bull
        if u_bull_streak[i] >= 4:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = uu_scan(i, min(u_bull_streak[i], 4), True)
            s = rv_normPrice[i] + _nzf(rv_normPrice, i, 1) + _nzf(rv_normPrice, i, 2) + _nzf(rv_normPrice, i, 3)
            p = det_PBJBull[i] or _npv(det_PBJBull, i, 1) or _npv(det_PBJBull, i, 2) or _npv(det_PBJBull, i, 3)
            ok = P.tfSec > 120 or (s >= th_saab and (s >= th_1x or p))
            det_UUUUBull[i] = (((u_bull_hasDay1[i] and hp) or ad or asd or hh
                                or ((dnp and hp) or (pnd and (hd or hf)))
                                or ((hf or hd) and hp)) and ok)
        elif u_bull_streak[i] == 3:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = uu_scan(i, 3, True)
            s = rv_normPrice[i] + _nzf(rv_normPrice, i, 1) + _nzf(rv_normPrice, i, 2)
            p = det_PBJBull[i] or _npv(det_PBJBull, i, 1) or _npv(det_PBJBull, i, 2)
            ok = P.tfSec > 120 or (s >= th_saab and (s >= th_1x or p))
            det_UUUBull[i] = (((u_bull_hasDay1[i] and hp) or ad or asd or hh
                               or ((dnp and hp) or (pnd and (hd or hf)))) and ok)
        elif u_bull_streak[i] == 2:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = uu_scan(i, 2, True)
            s = rv_normPrice[i] + _nzf(rv_normPrice, i, 1)
            p = det_PBJBull[i] or _npv(det_PBJBull, i, 1)
            ok = P.tfSec > 120 or (s >= th_saab and (s >= th_1x or p))
            det_UUBull[i] = (((u_bull_hasDay1[i] and hp) or ad or asd or (hh and (hpb or hp))
                              or ((dnp and hp) or (pnd and (hd or hf)))) and ok)
        # bear
        if u_bear_streak[i] >= 4:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = uu_scan(i, min(u_bear_streak[i], 4), False)
            det_UUUUBear[i] = ((u_bear_hasDay1[i] and hp) or ad or asd or hh
                               or ((dnp and hp) or (pnd and (hd or hf))) or ((hf or hd) and hp))
        elif u_bear_streak[i] == 3:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = uu_scan(i, 3, False)
            det_UUUBear[i] = ((u_bear_hasDay1[i] and hp) or ad or asd or hh
                              or ((dnp and hp) or (pnd and (hd or hf))))
        elif u_bear_streak[i] == 2:
            hp, hpb, hh, hd, hf, ad, asd, dnp, pnd = uu_scan(i, 2, False)
            det_UUBear[i] = ((u_bear_hasDay1[i] and hp) or ad or asd or (hh and (hpb or hp))
                             or ((dnp and hp) or (pnd and (hd or hf))))
    anyUU_bull = [det_UUUUBull[i] or det_UUUBull[i] or det_UUBull[i] for i in range(n)]
    anyUU_bear = [det_UUUUBear[i] or det_UUUBear[i] or det_UUBear[i] for i in range(n)]

    # ════════════════ DETECTION COMBINATION LAYER — S1..S18 ════════════════
    P_ = det_PUP
    Q_ = det_PPD

    def npv(s, i, k):
        return _npv(s, i, k)

    det_S2_bull = [det_b2bPUP[i] and det_FAUNABull[i] and npv(det_FAUNABull, i, 1) for i in range(n)]
    det_S2_bear = [det_b2bPPD[i] and det_FAUNABear[i] and npv(det_FAUNABear, i, 1) for i in range(n)]
    det_S3_bull = [npv(P_, i, 1) and npv(P_, i, 2) and det_DISPBull[i] and npv(det_DISPBull, i, 1) for i in range(n)]
    det_S3_bear = [npv(Q_, i, 1) and npv(Q_, i, 2) and det_DISPBear[i] and npv(det_DISPBear, i, 1) for i in range(n)]
    det_S3d_bull = [npv(P_, i, 1) and npv(P_, i, 2) and det_HVDBull[i] and npv(det_HVDBull, i, 1) for i in range(n)]
    det_S3d_bear = [npv(Q_, i, 1) and npv(Q_, i, 2) and det_HVDBear[i] and npv(det_HVDBear, i, 1) for i in range(n)]
    det_S3_any_bull = [det_S3_bull[i] or det_S3d_bull[i] for i in range(n)]
    det_S3_any_bear = [det_S3_bear[i] or det_S3d_bear[i] for i in range(n)]
    det_S4_bull = [npv(P_, i, 1) and npv(P_, i, 2) and npv(det_FAUNABull, i, 1) and npv(det_FAUNABull, i, 2) and det_DISPBull[i] and npv(det_DISPBull, i, 1) for i in range(n)]
    det_S4_bear = [npv(Q_, i, 1) and npv(Q_, i, 2) and npv(det_FAUNABear, i, 1) and npv(det_FAUNABear, i, 2) and det_DISPBear[i] and npv(det_DISPBear, i, 1) for i in range(n)]
    det_S4d_bull = [npv(P_, i, 1) and npv(P_, i, 2) and npv(det_FAUNABull, i, 1) and npv(det_FAUNABull, i, 2) and det_HVDBull[i] and npv(det_HVDBull, i, 1) for i in range(n)]
    det_S4d_bear = [npv(Q_, i, 1) and npv(Q_, i, 2) and npv(det_FAUNABear, i, 1) and npv(det_FAUNABear, i, 2) and det_HVDBear[i] and npv(det_HVDBear, i, 1) for i in range(n)]
    det_S4_any_bull = [det_S4_bull[i] or det_S4d_bull[i] for i in range(n)]
    det_S4_any_bear = [det_S4_bear[i] or det_S4d_bear[i] for i in range(n)]

    saab_dir_b = [det_SAAB[i] or det_RVOL1xB[i] or det_GrandSlam[i] for i in range(n)]
    saab_neut = [det_WTC[i] or det_Hiroshima[i] for i in range(n)]
    krat_dir = [det_Kratos[i] or det_RVOL1xR[i] or det_MOAB[i] for i in range(n)]
    det_S5_bull = [det_b2bPUP[i] and ((saab_dir_b[i] and (npv(saab_dir_b, i, 1) or npv(saab_neut, i, 1)))
                                      or ((saab_dir_b[i] or saab_neut[i]) and npv(saab_dir_b, i, 1))) for i in range(n)]
    det_S5_bear = [det_b2bPPD[i] and ((krat_dir[i] and (npv(krat_dir, i, 1) or npv(saab_neut, i, 1)))
                                      or ((krat_dir[i] or saab_neut[i]) and npv(krat_dir, i, 1))) for i in range(n)]
    anyB2B_nd_bull = [det_b2bPUP[i] or det_S2_bull[i] or det_S5_bull[i] for i in range(n)]
    anyB2B_nd_bear = [det_b2bPPD[i] or det_S2_bear[i] or det_S5_bear[i] for i in range(n)]

    det_S6_bull = [(anyB2B_nd_bull[i] and (det_PBJBull[i] or npv(det_PBJBull, i, 1) or det_HVDPBJBull[i]))
                   or (det_S3_any_bull[i] and (npv(det_PBJBull, i, 1) or npv(det_PBJBull, i, 2) or npv(det_HVDPBJBull, i, 1)))
                   or (det_S4_any_bull[i] and (npv(det_PBJBull, i, 1) or npv(det_PBJBull, i, 2) or npv(det_HVDPBJBull, i, 1))) for i in range(n)]
    det_S6_bear = [(anyB2B_nd_bear[i] and (det_PBJBear[i] or npv(det_PBJBear, i, 1) or det_HVDPBJBear[i]))
                   or (det_S3_any_bear[i] and (npv(det_PBJBear, i, 1) or npv(det_PBJBear, i, 2) or npv(det_HVDPBJBear, i, 1)))
                   or (det_S4_any_bear[i] and (npv(det_PBJBear, i, 1) or npv(det_PBJBear, i, 2) or npv(det_HVDPBJBear, i, 1))) for i in range(n)]
    det_S8_bull = [(det_b2bPUP[i] and det_UnifiedBull[i]) or (det_S3_any_bull[i] and (det_UnifiedBull[i] or npv(det_UnifiedBull, i, 1))) for i in range(n)]
    det_S8_bear = [(det_b2bPPD[i] and det_UnifiedBear[i]) or (det_S3_any_bear[i] and (det_UnifiedBear[i] or npv(det_UnifiedBear, i, 1))) for i in range(n)]
    s9cb = [det_UC2Bull[i] or det_FMUBull[i] for i in range(n)]
    s9cs = [det_UC2Bear[i] or det_FMUBear[i] for i in range(n)]
    det_S9_bull = [(det_b2bPUP[i] and (s9cb[i] or npv(s9cb, i, 1))) or (det_S3_any_bull[i] and (npv(s9cb, i, 1) or npv(s9cb, i, 2))) for i in range(n)]
    det_S9_bear = [(det_b2bPPD[i] and (s9cs[i] or npv(s9cs, i, 1))) or (det_S3_any_bear[i] and (npv(s9cs, i, 1) or npv(s9cs, i, 2))) for i in range(n)]
    det_S10_bull = [(det_Long1[i] and npv(det_Long1, i, 1)) and (det_b2bPUP[i] or npv(det_b2bPUP, i, 1)) for i in range(n)]
    det_S10_bear = [(det_Short1[i] and npv(det_Short1, i, 1)) and (det_b2bPPD[i] or npv(det_b2bPPD, i, 1)) for i in range(n)]
    det_S11_bull = [det_b2bPUP[i] and (det_CS1Bull[i] or det_Long1[i] or npv(det_Long1, i, 1)) for i in range(n)]
    det_S11_bear = [det_b2bPPD[i] and (det_CS1Bear[i] or det_Short1[i] or npv(det_Short1, i, 1)) for i in range(n)]
    det_S12_bull = [det_b2bPUP[i] and (anyUU_bull[i] or npv(anyUU_bull, i, 1)) for i in range(n)]
    det_S12_bear = [det_b2bPPD[i] and (anyUU_bear[i] or npv(anyUU_bear, i, 1)) for i in range(n)]
    det_S13_bull = [det_b2bPUP[i] and (det_b2bBullNapalm[i] or npv(det_b2bBullNapalm, i, 1)) for i in range(n)]
    det_S13_bear = [det_b2bPPD[i] and (det_b2bBearNapalm[i] or npv(det_b2bBearNapalm, i, 1)) for i in range(n)]
    det_S14_bull = [det_b2bPUP[i] and (det_contBull[i] or npv(det_contBull, i, 1)) for i in range(n)]
    det_S14_bear = [det_b2bPPD[i] and (det_contBear[i] or npv(det_contBear, i, 1)) for i in range(n)]
    det_S15_bull = [det_b2bPUP[i] and (det_bullTNT[i] or npv(det_bullTNT, i, 1)) for i in range(n)]
    det_S15_bear = [det_b2bPPD[i] and (det_bearTNT[i] or npv(det_bearTNT, i, 1)) for i in range(n)]
    det_S16_bull = [det_b2bPUP[i] and (det_bullNapCons[i] or npv(det_bullNapCons, i, 1)) for i in range(n)]
    det_S16_bear = [det_b2bPPD[i] and (det_bearNapCons[i] or npv(det_bearNapCons, i, 1)) for i in range(n)]
    det_S17_bull = [det_b2bPUP[i] and (det_B2BHVDBull[i] or npv(det_B2BHVDBull, i, 1)) for i in range(n)]
    det_S17_bear = [det_b2bPPD[i] and (det_B2BHVDBear[i] or npv(det_B2BHVDBear, i, 1)) for i in range(n)]
    det_S18_bull = [det_b2bPUP[i] and (det_B2BHVDPBJBull[i] or npv(det_B2BHVDPBJBull, i, 1)) for i in range(n)]
    det_S18_bear = [det_b2bPPD[i] and (det_B2BHVDPBJBear[i] or npv(det_B2BHVDPBJBear, i, 1)) for i in range(n)]

    # FIRST-BAR GATES (g01/gd) — open when en_firstBarOnly off
    g01 = [True] * n
    gd = [True] * n
    if P.en_firstBarOnly and session_first_bar_idx is not None:
        for i in range(n):
            fb = session_first_bar_idx[i]
            g01[i] = (i == fb) or (i - 1 == fb)
            gd[i] = (i - 1 == fb) or (i - 2 == fb)

    def gate01(arr, i):
        return arr[i] and g01[i] and masterGate[i]

    def gated(arr, i):
        return arr[i] and gd[i] and masterGate[i]

    def gate_or(arr, i):
        return arr[i] and (g01[i] or gd[i]) and masterGate[i]

    EN = P.en
    fire = {}
    fire["fire_S1_bull"] = [EN("S1") and det_b2bPUP[i] and g01[i] and masterGate[i] for i in range(n)]
    fire["fire_S1_bear"] = [EN("S1") and det_b2bPPD[i] and g01[i] and masterGate[i] for i in range(n)]
    fire["fire_S2_bull"] = [EN("S2") and gate01(det_S2_bull, i) for i in range(n)]
    fire["fire_S2_bear"] = [EN("S2") and gate01(det_S2_bear, i) for i in range(n)]
    fire["fire_S3_bull"] = [EN("S3") and gated(det_S3_any_bull, i) for i in range(n)]
    fire["fire_S3_bear"] = [EN("S3") and gated(det_S3_any_bear, i) for i in range(n)]
    fire["fire_S4_bull"] = [EN("S4") and gated(det_S4_any_bull, i) for i in range(n)]
    fire["fire_S4_bear"] = [EN("S4") and gated(det_S4_any_bear, i) for i in range(n)]
    fire["fire_S5_bull"] = [EN("S5") and gate01(det_S5_bull, i) for i in range(n)]
    fire["fire_S5_bear"] = [EN("S5") and gate01(det_S5_bear, i) for i in range(n)]
    fire["fire_S6_bull"] = [EN("S6") and det_S6_bull[i] and (g01[i] or gd[i]) and masterGate[i] for i in range(n)]
    fire["fire_S6_bear"] = [EN("S6") and det_S6_bear[i] and (g01[i] or gd[i]) and masterGate[i] for i in range(n)]
    fire["fire_S8_bull"] = [EN("S8") and gate_or(det_S8_bull, i) for i in range(n)]
    fire["fire_S8_bear"] = [EN("S8") and gate_or(det_S8_bear, i) for i in range(n)]
    fire["fire_S9_bull"] = [EN("S9") and gate_or(det_S9_bull, i) for i in range(n)]
    fire["fire_S9_bear"] = [EN("S9") and gate_or(det_S9_bear, i) for i in range(n)]
    fire["fire_S10_bull"] = [EN("S10") and gate01(det_S10_bull, i) for i in range(n)]
    fire["fire_S10_bear"] = [EN("S10") and gate01(det_S10_bear, i) for i in range(n)]
    fire["fire_S11_bull"] = [EN("S11") and gate01(det_S11_bull, i) for i in range(n)]
    fire["fire_S11_bear"] = [EN("S11") and gate01(det_S11_bear, i) for i in range(n)]
    fire["fire_S12_bull"] = [EN("S12") and gate01(det_S12_bull, i) for i in range(n)]
    fire["fire_S12_bear"] = [EN("S12") and gate01(det_S12_bear, i) for i in range(n)]
    fire["fire_S13_bull"] = [EN("S13") and gate01(det_S13_bull, i) for i in range(n)]
    fire["fire_S13_bear"] = [EN("S13") and gate01(det_S13_bear, i) for i in range(n)]
    fire["fire_S14_bull"] = [EN("S14") and gate01(det_S14_bull, i) for i in range(n)]
    fire["fire_S14_bear"] = [EN("S14") and gate01(det_S14_bear, i) for i in range(n)]
    fire["fire_S15_bull"] = [EN("S15") and gate01(det_S15_bull, i) for i in range(n)]
    fire["fire_S15_bear"] = [EN("S15") and gate01(det_S15_bear, i) for i in range(n)]
    fire["fire_S16_bull"] = [EN("S16") and gate01(det_S16_bull, i) for i in range(n)]
    fire["fire_S16_bear"] = [EN("S16") and gate01(det_S16_bear, i) for i in range(n)]
    fire["fire_S17_bull"] = [EN("S17") and gate01(det_S17_bull, i) for i in range(n)]
    fire["fire_S17_bear"] = [EN("S17") and gate01(det_S17_bear, i) for i in range(n)]
    fire["fire_S18_bull"] = [EN("S18") and gate01(det_S18_bull, i) for i in range(n)]
    fire["fire_S18_bear"] = [EN("S18") and gate01(det_S18_bear, i) for i in range(n)]
    fire["fire_UC2_bull"] = [EN("UC2") and gate_or(det_UC2Bull, i) for i in range(n)]
    fire["fire_UC2_bear"] = [EN("UC2") and gate_or(det_UC2Bear, i) for i in range(n)]
    fire["fire_FMU_bull"] = [EN("FMU") and gate_or(det_FMUBull, i) for i in range(n)]
    fire["fire_FMU_bear"] = [EN("FMU") and gate_or(det_FMUBear, i) for i in range(n)]

    out = {"ts": list(ts)}
    for k, arr in fire.items():
        out[k] = [1 if x else 0 for x in arr]

    # numeric levels (data_window plots) + key primitive debug series
    out["lvl_rv_normPrice"] = list(rv_normPrice)
    out["lvl_rv_relVolRatio"] = list(rv_relVolRatio)
    out["lvl_sig_line"] = list(sig_line)
    out["lvl_disp_thresh"] = list(disp_thresh)
    for k in ("det_PUP", "det_PPD", "det_b2bPUP", "det_b2bPPD"):
        out[k] = [1 if x else 0 for x in locals()[k]]
    # expose ALL sub-engine primitives as 0/1 for downstream + parity introspection
    prim = {
        "det_FAUNABull": det_FAUNABull, "det_FAUNABear": det_FAUNABear,
        "det_DISPBull": det_DISPBull, "det_DISPBear": det_DISPBear,
        "det_PBJBull": det_PBJBull, "det_PBJBear": det_PBJBear,
        "det_PBBull": det_PBBull, "det_PBBear": det_PBBear,
        "det_SAAB": det_SAAB, "det_Kratos": det_Kratos,
        "det_RVOL1xB": det_RVOL1xB, "det_RVOL1xR": det_RVOL1xR,
        "det_GrandSlam": det_GrandSlam, "det_MOAB": det_MOAB,
        "det_Pentagon": det_Pentagon, "det_WTC": det_WTC, "det_Hiroshima": det_Hiroshima,
        "det_Nagasaki": det_Nagasaki,
        "det_HVDBull": det_HVDBull, "det_HVDBear": det_HVDBear,
        "det_HVDPBJBull": det_HVDPBJBull, "det_HVDPBJBear": det_HVDPBJBear,
        "det_B2BHVDBull": det_B2BHVDBull, "det_B2BHVDBear": det_B2BHVDBear,
        "det_B2BHVDPBJBull": det_B2BHVDPBJBull, "det_B2BHVDPBJBear": det_B2BHVDPBJBear,
        "det_bullTNT": det_bullTNT, "det_bearTNT": det_bearTNT,
        "det_bullTNT_raw": det_bullTNT_raw, "det_bearTNT_raw": det_bearTNT_raw,
        "det_bullNapalm": det_bullNapalm, "det_bearNapalm": det_bearNapalm,
        "det_bullCharge": det_bullCharge, "det_bearCharge": det_bearCharge,
        "det_contBull": det_contBull, "det_contBear": det_contBear,
        "det_bullNapCons": det_bullNapCons, "det_bearNapCons": det_bearNapCons,
        "det_b2bBullNapalm": det_b2bBullNapalm, "det_b2bBearNapalm": det_b2bBearNapalm,
        "det_retBullTNT": det_retBullTNT, "det_retBearTNT": det_retBearTNT,
        "det_UnifiedBull": det_UnifiedBull, "det_UnifiedBear": det_UnifiedBear,
        "det_CS1Bull": det_CS1Bull, "det_CS1Bear": det_CS1Bear,
        "det_CS2Bull": det_CS2Bull, "det_CS2Bear": det_CS2Bear,
        "det_UC2Bull": det_UC2Bull, "det_UC2Bear": det_UC2Bear,
        "det_FMUBull": det_FMUBull, "det_FMUBear": det_FMUBear,
        "det_Long1": det_Long1, "det_Short1": det_Short1,
        "anyUU_bull": anyUU_bull, "anyUU_bear": anyUU_bear,
    }
    for k, arr in prim.items():
        out["prim_" + k] = [1 if x else 0 for x in arr]
    return out


def _nzf(series, i, k):
    """nz(series[k]) at bar i for FLOAT series -> 0.0 when OOB."""
    j = i - k
    return float(series[j]) if 0 <= j < len(series) else 0.0


# ───────────────────────── Engine G — full TNT machine ──────────────────────
def _engine_tnt(o, h, l, c, v, conf, P: Params):
    """Faithful port of the TNT/Napalm/Charge/CONT engine (Pine lines 358-711).

    Returns the 16 detection series used by the S-layer + aggregates.
    """
    n = len(c)
    EMA_FAST = P.tnt_SENS
    EMA_SLOW = P.tnt_SENS + 13
    ATR_MULT = 3.5
    ATR_MIN = 0.5
    MIN_SIG_GAP = EMA_SLOW
    CW = EMA_SLOW * 2
    ef = _ema(c, EMA_FAST)
    es = _ema(c, EMA_SLOW)
    atr_val = _atr_ohlc(o, h, l, c, 200)
    ahi_series = highest([nz(x) for x in atr_val], 200)
    ahi = [(ahi_series[i] * 2.0) if ahi_series[i] is not None else 0.0 for i in range(n)]
    vbc = _crossover(ef, es)
    vsc = _crossunder(ef, es)
    vMed = _median(v, EMA_SLOW)
    eSl = [(ef[i] - ef[i - 5]) if (i >= 5 and ef[i] is not None and ef[i - 5] is not None) else None for i in range(n)]
    rsi = _rsi(c, 14)

    # volume-block zones (var per side) — current snapshot per bar
    vbu = vbl = vbv = None
    vsu = vsl = vsv = None
    vcb = acb = fcb = vcs = acs = fcs = 0
    vcu = vcl = vdu = vdl = None
    # anish swing OBs
    abu = abl = abi = apu = apl = api = None
    asu = asl = asi = aspu = aspl = aspi = None
    swSt = 0
    swSt_prev = 0
    swH_val = swH_idx = None
    swH_crossed = False
    swL_val = swL_idx = None
    swL_crossed = False
    # fauna OBs
    fbu = fbl = None
    fba = False
    fsu = fsl = None
    fsa = False
    fswH_val = fswH_idx = None
    fswH_crossed = False
    fswL_val = fswL_idx = None
    fswL_crossed = False

    swU = highest(h, P.tnt_SWING_LEN)
    swLL = lowest(l, P.tnt_SWING_LEN)

    lBSB = lSSB = 0
    bull_zones = []   # [confirmIdx, upper, lower, level, isBull, isActive, returnFired]
    bear_zones = []
    charge_lvls = []  # [level, isBull, barIdx, violated]
    bull_events = []  # [barIdx, isBull, isTrue]
    bear_events = []
    lastBull2Bar = lastBear2Bar = 0

    det_bullTNT_raw = [False] * n
    det_bearTNT_raw = [False] * n
    det_bullTNT2 = [False] * n
    det_bearTNT2 = [False] * n
    det_superBullTNT = [False] * n
    det_superBearTNT = [False] * n
    det_bullTNT = [False] * n
    det_bearTNT = [False] * n
    det_bullNapalm = [False] * n
    det_bearNapalm = [False] * n
    det_bullCharge = [False] * n
    det_bearCharge = [False] * n
    det_retBullTNT = [False] * n
    det_retBearTNT = [False] * n
    det_contBull = [False] * n
    det_contBear = [False] * n

    # CONT memory vars
    sc_lastBullChargeBar = sc_lastBearChargeBar = None
    sc_lastRetBullBar = sc_lastRetBearBar = None
    sc_lastBullTNTBar = sc_lastBearTNTBar = None
    sc_lastBullTNT2Bar = sc_lastBearTNT2Bar = None

    def H(series, i, k):
        j = i - k
        return series[j] if 0 <= j < n else None

    for i in range(n):
        # ── volume blocks on EMA cross ──
        vbn = False
        vsn = False
        if vbc[i]:
            cv = 0.0
            ol = l[i]
            for k in range(1, EMA_SLOW + 1):
                lk = H(l, i, k)
                if lk is not None and lk <= ol:
                    ol = lk
                vk = H(v, i, k)
                cv += vk if vk is not None else 0.0
            s = min(o[i], c[i])
            if (s - ol) < ahi[i] * 0.5:
                s = ol + ahi[i] * 0.5
            vbu, vbl, vbv, vbn = s, ol, cv, True
        if vsc[i]:
            cv = 0.0
            oh = h[i]
            for k in range(1, EMA_SLOW + 1):
                hk = H(h, i, k)
                if hk is not None and hk >= oh:
                    oh = hk
                vk = H(v, i, k)
                cv += vk if vk is not None else 0.0
            s = max(o[i], c[i])
            if (oh - s) < ahi[i] * 0.5:
                s = oh - ahi[i] * 0.5
            vsu, vsl, vsv, vsn = oh, s, cv, True

        # ── swing pivots ──
        swSt_prev = swSt
        hk_sw = H(h, i, P.tnt_SWING_LEN)
        lk_sw = H(l, i, P.tnt_SWING_LEN)
        if hk_sw is not None and swU[i] is not None and hk_sw > swU[i]:
            swSt = 0
        elif lk_sw is not None and swLL[i] is not None and lk_sw < swLL[i]:
            swSt = 1
        # else keep swSt
        if swSt == 0 and swSt_prev != 0:
            swH_val = H(h, i, P.tnt_SWING_LEN)
            swH_idx = i - P.tnt_SWING_LEN
            swH_crossed = False
            fswH_val = H(h, i, P.tnt_SWING_LEN)
            fswH_idx = i - P.tnt_SWING_LEN
            fswH_crossed = False
        if swSt == 1 and swSt_prev != 1:
            swL_val = H(l, i, P.tnt_SWING_LEN)
            swL_idx = i - P.tnt_SWING_LEN
            swL_crossed = False
            fswL_val = H(l, i, P.tnt_SWING_LEN)
            fswL_idx = i - P.tnt_SWING_LEN
            fswL_crossed = False

        # ── anish bull OB on swing-high cross ──
        abn = False
        if swH_val is not None and c[i] > swH_val and not swH_crossed and conf[i]:
            swH_crossed = True
            oL = H(l, i, 1)
            oH = H(h, i, 1)
            oI = i - 1
            lb = i - swH_idx
            if lb > 1:
                for k in range(1, lb):
                    ok_ = H(o, i, k)
                    ck_ = H(c, i, k)
                    lk_ = H(l, i, k)
                    hk_ = H(h, i, k)
                    if ok_ is not None and ck_ is not None and ok_ > ck_ and lk_ is not None and lk_ <= (oL if oL is not None else lk_):
                        oL, oH, oI = lk_, hk_, i - k
            apu, apl, api = abu, abl, abi
            abu, abl, abi = oH, oL, oI
            abn = (apu is not None and oI <= nz(api, 0) + EMA_SLOW
                   and (apl is not None and oH > apl) and (apu is not None and oL < apu))
        # ── anish bear OB on swing-low cross ──
        asn = False
        if swL_val is not None and c[i] < swL_val and not swL_crossed and conf[i]:
            swL_crossed = True
            oL = H(l, i, 1)
            oH = H(h, i, 1)
            oI = i - 1
            lb = i - swL_idx
            if lb > 1:
                for k in range(1, lb):
                    ok_ = H(o, i, k)
                    ck_ = H(c, i, k)
                    hk_ = H(h, i, k)
                    lk_ = H(l, i, k)
                    if ok_ is not None and ck_ is not None and ok_ < ck_ and hk_ is not None and hk_ >= (oH if oH is not None else hk_):
                        oH, oL, oI = hk_, lk_, i - k
            aspu, aspl, aspi = asu, asl, asi
            asu, asl, asi = oH, oL, oI
            asn = (aspl is not None and oI <= nz(aspi, 0) + EMA_SLOW
                   and (aspu is not None and oL < aspu) and (aspl is not None and oH > aspl))

        # ── fauna bull OB ──
        if fswH_val is not None and c[i] > fswH_val and not fswH_crossed and conf[i]:
            fswH_crossed = True
            o1 = H(o, i, 1)
            c1 = H(c, i, 1)
            bB = min(o1, c1)
            bT = max(o1, c1)
            lb = i - fswH_idx
            if lb > 1:
                for k in range(1, lb):
                    ok_ = H(o, i, k)
                    ck_ = H(c, i, k)
                    if ok_ is not None and ck_ is not None and min(ok_, ck_) < bB:
                        bB, bT = min(ok_, ck_), max(ok_, ck_)
            osz = abs(bT - bB)
            av = atr_val[i] if atr_val[i] is not None else 0.0
            if osz <= av * ATR_MULT and osz > av * ATR_MIN:
                fbu, fbl, fba = bT, bB, True
        # ── fauna bear OB ──
        if fswL_val is not None and c[i] < fswL_val and not fswL_crossed and conf[i]:
            fswL_crossed = True
            o1 = H(o, i, 1)
            c1 = H(c, i, 1)
            bT = max(o1, c1)
            bB = min(o1, c1)
            lb = i - fswL_idx
            if lb > 1:
                for k in range(1, lb):
                    ok_ = H(o, i, k)
                    ck_ = H(c, i, k)
                    if ok_ is not None and ck_ is not None and max(ok_, ck_) > bT:
                        bT, bB = max(ok_, ck_), min(ok_, ck_)
            osz = abs(bT - bB)
            av = atr_val[i] if atr_val[i] is not None else 0.0
            if osz <= av * ATR_MULT and osz > av * ATR_MIN:
                fsu, fsl, fsa = bT, bB, True

        # fauna pup/pnd (fbpn/fspn)
        fbpn = False
        if fba and conf[i]:
            if c[i] < fbl:
                fba = False
            else:
                l1 = H(l, i, 1)
                h1 = H(h, i, 1)
                if l1 is not None and l1 < fbu and l1 > fbl and c[i] > o[i] and h1 is not None and c[i] > h1:
                    fbpn = True
        fspn = False
        if fsa and conf[i]:
            if c[i] > fsu:
                fsa = False
            else:
                h1 = H(h, i, 1)
                l1 = H(l, i, 1)
                if h1 is not None and h1 > fsl and h1 < fsu and c[i] < o[i] and l1 is not None and c[i] < l1:
                    fspn = True

        # confirm-bar trackers
        if vbn:
            vcb, vcu, vcl = i, vbu, vbl
        if vsn:
            vcs, vdu, vdl = i, vsu, vsl
        if abn:
            acb = i
        if asn:
            acs = i
        if fbpn:
            fcb = i
        if fspn:
            fcs = i

        def tok(a, b, cc):
            mn = min(a, b, cc)
            mx = max(a, b, cc)
            return (mx - mn) <= CW and mn > 0

        def zov(u1, l1, u2, l2):
            return (u1 is not None and u2 is not None and u1 >= l2 and u2 >= l1)

        def overlap_ratio(vU, vL, aU, aL):
            denom = min(vU - vL, aU - aL)
            if denom > 0:
                return max(0.0, min(vU, aU) - max(vL, aL)) / denom > 0.3
            return False

        vm = vMed[i]
        esl = eSl[i]
        rsi_i = rsi[i]
        sb_ok = ss_ok = False
        if vm is not None and esl is not None and rsi_i is not None:
            vV = nz(vbv)
            sb_ok = (vV > vm * EMA_SLOW * 0.5 and esl > 0 and rsi_i < 80
                     and overlap_ratio(nz(vcu), nz(vcl), nz(abu), nz(abl)))
            vVs = nz(vsv)
            ss_ok = (vVs > vm * EMA_SLOW * 0.5 and esl < 0 and rsi_i > 20
                     and overlap_ratio(nz(vdu), nz(vdl), nz(asu), nz(asl)))

        bConf = tok(vcb, acb, fcb) and zov(vcu, vcl, abu, abl)
        sConf = tok(vcs, acs, fcs) and zov(vdu, vdl, asu, asl)
        bullraw = bConf and sb_ok and conf[i] and (i - lBSB) > MIN_SIG_GAP
        bearraw = sConf and ss_ok and conf[i] and (i - lSSB) > MIN_SIG_GAP
        det_bullTNT_raw[i] = bullraw
        det_bearTNT_raw[i] = bearraw
        if bullraw:
            lBSB = i
        if bearraw:
            lSSB = i

        # ── zone tracking ──
        if bullraw:
            oU = min(nz(vcu, h[i]), nz(abu, h[i]))
            oL = max(nz(vcl, l[i]), nz(abl, l[i]))
            lvl = (oU + oL) / 2.0
            bull_zones.append([i, oU, oL, lvl, True, True, False])
        if bearraw:
            oU = min(nz(vdu, h[i]), nz(asu, h[i]))
            oL = max(nz(vdl, l[i]), nz(asl, l[i]))
            lvl = (oU + oL) / 2.0
            bear_zones.append([i, oU, oL, lvl, False, True, False])
        for z in bull_zones:
            if z[5] and c[i] < z[2]:
                z[5] = False
        for z in bear_zones:
            if z[5] and c[i] > z[1]:
                z[5] = False
        while len(bull_zones) > P.tnt_MAX_ZONES:
            bull_zones.pop(0)
        while len(bear_zones) > P.tnt_MAX_ZONES:
            bear_zones.pop(0)

        # ── Return-to-TNT ──
        if conf[i]:
            for z in reversed(bull_zones):
                if z[5] and not z[6] and i > z[0]:
                    zH = z[1] - z[2]
                    retLvl = z[2] + zH * (P.tnt_RET_PCT / 100.0)
                    if l[i] <= retLvl and c[i] > z[2]:
                        z[6] = True
                        det_retBullTNT[i] = True
            for z in reversed(bear_zones):
                if z[5] and not z[6] and i > z[0]:
                    zH = z[1] - z[2]
                    retLvl = z[1] - zH * (P.tnt_RET_PCT / 100.0)
                    if h[i] >= retLvl and c[i] < z[1]:
                        z[6] = True
                        det_retBearTNT[i] = True

        # ── TNT internal displacement ──
        dr = abs(o[i] - c[i])
        dr1 = abs(o[i - 1] - c[i - 1]) if i >= 1 else 0.0
        # ta.stdev over disp range (window 100)
        # build incrementally would be costly; approximate with rolling here:
        # (computed below via vector once — placeholder set after loop)
        # we mark dBull/dBear using precomputed dt series (see post-loop)
        pass  # displacement handled vectorised below

    # vectorised TNT displacement (needs full series; recompute then second pass
    # for Napalm/Charge which depend on dBull/dBear + zones-at-bar)
    tnt_dr = [abs(o[i] - c[i]) for i in range(n)]
    tnt_ds = stdev(tnt_dr, 100)
    tnt_dt = [None if tnt_ds[i] is None else tnt_ds[i] * P.tnt_DISP_STD_X for i in range(n)]
    tnt_dBull = [i >= 2 and tnt_dt[i - 1] is not None and tnt_dr[i - 1] > tnt_dt[i - 1]
                 and l[i] > h[i - 2] and c[i - 1] > o[i - 1] for i in range(n)]
    tnt_dBear = [i >= 2 and tnt_dt[i - 1] is not None and tnt_dr[i - 1] > tnt_dt[i - 1]
                 and h[i] < l[i - 2] and c[i - 1] < o[i - 1] for i in range(n)]

    # Second pass for Napalm/Charge/TNT2/super/CONT/aggregates using zones rebuilt
    # deterministically. To keep zone/charge state consistent with the first pass,
    # we re-run the zone construction lockstep with Napalm/Charge in ONE pass.
    return _engine_tnt_pass2(o, h, l, c, v, conf, P, det_bullTNT_raw, det_bearTNT_raw,
                             det_retBullTNT, det_retBearTNT, tnt_dBull, tnt_dBear,
                             EMA_SLOW, MIN_SIG_GAP)


def _engine_tnt_pass2(o, h, l, c, v, conf, P, det_bullTNT_raw, det_bearTNT_raw,
                      det_retBullTNT, det_retBearTNT, tnt_dBull, tnt_dBear,
                      EMA_SLOW, MIN_SIG_GAP):
    """Build zones/charge/events/CONT in one forward pass given raw TNT + ret +
    displacement series (all already Pine-faithful). This isolates the
    array-state machinery so it reads cleanly."""
    n = len(c)

    # need vcu/vcl/abu/abl etc at the TNT-confirm bar to size zones; recompute the
    # block/OB snapshots minimally. Simplest faithful approach: re-derive zone
    # bounds from the SAME inputs the source uses at the confirm bar. Those bounds
    # are nz(tnt_vcu,high)/nz(tnt_abu,high) etc, which require the running block/OB
    # vars. We recompute them here cheaply by re-walking the same construction.
    # To avoid a 3rd duplicate of the heavy walk, we approximate the zone bounds
    # with the bar's own high/low when the running vars are unavailable — but the
    # source ALWAYS has them set on a raw-TNT bar (a raw TNT requires bConf which
    # requires the block+OB to exist). We therefore re-walk the block/OB vars.
    from_tnt = _tnt_zone_bounds(o, h, l, c, v, conf, P, EMA_SLOW)
    bull_bounds = from_tnt["bull"]   # per-bar (oU,oL) or None
    bear_bounds = from_tnt["bear"]

    bull_zones = []   # [confirmIdx, upper, lower, level, isActive, returnFired]
    bear_zones = []
    charge_lvls = []  # [level, isBull, barIdx, violated]
    bull_events = []
    bear_events = []
    lastBull2Bar = lastBear2Bar = 0

    det_bullTNT2 = [False] * n
    det_bearTNT2 = [False] * n
    det_bullNapalm = [False] * n
    det_bearNapalm = [False] * n
    det_bullCharge = [False] * n
    det_bearCharge = [False] * n
    det_contBull = [False] * n
    det_contBear = [False] * n

    sc_lastBullChargeBar = sc_lastBearChargeBar = None
    sc_lastRetBullBar = sc_lastRetBearBar = None
    sc_lastBullTNTBar = sc_lastBearTNTBar = None
    sc_lastBullTNT2Bar = sc_lastBearTNT2Bar = None

    def H(series, i, k):
        j = i - k
        return series[j] if 0 <= j < n else None

    for i in range(n):
        bullraw = det_bullTNT_raw[i]
        bearraw = det_bearTNT_raw[i]

        # push new zones / charge levels
        if bullraw and bull_bounds[i] is not None:
            oU, oL = bull_bounds[i]
            lvl = (oU + oL) / 2.0
            bull_zones.append([i, oU, oL, lvl, True, False])
            charge_lvls.append([lvl, True, i, False])
        if bearraw and bear_bounds[i] is not None:
            oU, oL = bear_bounds[i]
            lvl = (oU + oL) / 2.0
            bear_zones.append([i, oU, oL, lvl, True, False])
            charge_lvls.append([lvl, False, i, False])

        # invalidate zones
        for z in bull_zones:
            if z[4] and c[i] < z[2]:
                z[4] = False
        for z in bear_zones:
            if z[4] and c[i] > z[1]:
                z[4] = False
        while len(bull_zones) > P.tnt_MAX_ZONES:
            bull_zones.pop(0)
        while len(bear_zones) > P.tnt_MAX_ZONES:
            bear_zones.pop(0)

        # Napalm (scan ALL active opposing zones)
        if conf[i] and tnt_dBull[i] and bear_zones:
            l1 = H(l, i, 1)
            for z in reversed(bear_zones):
                if z[4] and l1 is not None and l1 > z[3]:
                    det_bullNapalm[i] = True
                    break
        if conf[i] and tnt_dBear[i] and bull_zones:
            h1 = H(h, i, 1)
            for z in reversed(bull_zones):
                if z[4] and h1 is not None and h1 < z[3]:
                    det_bearNapalm[i] = True
                    break

        # Charge (multi-level array)
        if conf[i] and tnt_dBull[i] and charge_lvls:
            c1 = H(c, i, 1)
            for cl in reversed(charge_lvls):
                if (not cl[1]) and (not cl[3]) and c1 is not None and c1 > cl[0]:
                    cl[3] = True
                    det_bullCharge[i] = True
                    break
        if conf[i] and tnt_dBear[i] and charge_lvls:
            c1 = H(c, i, 1)
            for cl in reversed(charge_lvls):
                if cl[1] and (not cl[3]) and c1 is not None and c1 < cl[0]:
                    cl[3] = True
                    det_bearCharge[i] = True
                    break
        while len(charge_lvls) > 100:
            charge_lvls.pop(0)

        # TNT 2.0 event log
        effBullCharge = det_bullCharge[i] and not bearraw
        effBearCharge = det_bearCharge[i] and not bullraw
        anyBullEvent = bullraw or det_bullNapalm[i] or effBullCharge
        anyBearEvent = bearraw or det_bearNapalm[i] or effBearCharge
        if anyBullEvent:
            evtBar = i if bullraw else i - 1
            bull_events.append([evtBar, True, bullraw])
            bear_events.clear()
            while len(bull_events) > 20:
                bull_events.pop(0)
        if anyBearEvent and not anyBullEvent:
            evtBar = i if bearraw else i - 1
            bear_events.append([evtBar, False, bearraw])
            bull_events.clear()
            while len(bear_events) > 20:
                bear_events.pop(0)
        if len(bull_events) >= 2 and anyBullEvent and conf[i] and (i - lastBull2Bar) > MIN_SIG_GAP:
            det_bullTNT2[i] = True
            lastBull2Bar = i
        if len(bear_events) >= 2 and anyBearEvent and not anyBullEvent and conf[i] and (i - lastBear2Bar) > MIN_SIG_GAP:
            det_bearTNT2[i] = True
            lastBear2Bar = i

        # CONT (3-clause)
        cb = det_bullCharge[i]
        cs = det_bearCharge[i]
        det_contBull[i] = (
            (cb and sc_lastRetBullBar is not None and (i - 1 - sc_lastRetBullBar) <= P.tnt_SUDDEN_PROX)
            or ((bullraw or det_bullTNT2[i]) and sc_lastBullChargeBar is not None and (i - sc_lastBullChargeBar) <= P.tnt_SUDDEN_PROX)
            or (cb and ((sc_lastBullTNTBar is not None and (i - 1 - sc_lastBullTNTBar) <= P.tnt_SUDDEN_PROX)
                        or (sc_lastBullTNT2Bar is not None and (i - 1 - sc_lastBullTNT2Bar) <= P.tnt_SUDDEN_PROX)))
        )
        det_contBear[i] = (
            (cs and sc_lastRetBearBar is not None and (i - 1 - sc_lastRetBearBar) <= P.tnt_SUDDEN_PROX)
            or ((bearraw or det_bearTNT2[i]) and sc_lastBearChargeBar is not None and (i - sc_lastBearChargeBar) <= P.tnt_SUDDEN_PROX)
            or (cs and ((sc_lastBearTNTBar is not None and (i - 1 - sc_lastBearTNTBar) <= P.tnt_SUDDEN_PROX)
                        or (sc_lastBearTNT2Bar is not None and (i - 1 - sc_lastBearTNT2Bar) <= P.tnt_SUDDEN_PROX)))
        )
        # update CONT memory (after using prior values, matching source order)
        if cb:
            sc_lastBullChargeBar = i - 1
        if cs:
            sc_lastBearChargeBar = i - 1
        if det_retBullTNT[i]:
            sc_lastRetBullBar = i
        if det_retBearTNT[i]:
            sc_lastRetBearBar = i
        if bullraw:
            sc_lastBullTNTBar = i
        if bearraw:
            sc_lastBearTNTBar = i
        if det_bullTNT2[i]:
            sc_lastBullTNT2Bar = i
        if det_bearTNT2[i]:
            sc_lastBearTNT2Bar = i

    det_superBullTNT = [det_bullTNT_raw[i] and det_bearCharge[i] for i in range(n)]
    det_superBearTNT = [det_bearTNT_raw[i] and det_bullCharge[i] for i in range(n)]
    det_bullTNT = [det_bullTNT_raw[i] or det_bullTNT2[i] or det_superBullTNT[i] for i in range(n)]
    det_bearTNT = [det_bearTNT_raw[i] or det_bearTNT2[i] or det_superBearTNT[i] for i in range(n)]
    det_bullNapCons = [det_bullNapalm[i] or det_bullCharge[i] for i in range(n)]
    det_bearNapCons = [det_bearNapalm[i] or det_bearCharge[i] for i in range(n)]
    det_b2bBullNapalm = [det_bullNapCons[i] and _npv(det_bullNapCons, i, 1) for i in range(n)]
    det_b2bBearNapalm = [det_bearNapCons[i] and _npv(det_bearNapCons, i, 1) for i in range(n)]

    return (det_bullTNT, det_bearTNT, det_bullTNT_raw, det_bearTNT_raw,
            det_bullNapalm, det_bearNapalm, det_bullCharge, det_bearCharge,
            det_retBullTNT, det_retBearTNT, det_contBull, det_contBear,
            det_bullNapCons, det_bearNapCons, det_b2bBullNapalm, det_b2bBearNapalm)


def _tnt_zone_bounds(o, h, l, c, v, conf, P, EMA_SLOW):
    """Recompute per-bar (oU,oL) zone bounds for raw-TNT bars, mirroring the
    source's nz(tnt_vcu,high)/nz(tnt_abu,high) snapshots. Returns dict with
    'bull'/'bear' lists of (oU,oL) or None."""
    n = len(c)
    ef = _ema(c, P.tnt_SENS)
    es = _ema(c, P.tnt_SENS + 13)
    vbc = _crossover(ef, es)
    vsc = _crossunder(ef, es)
    atr_val = _atr_ohlc(o, h, l, c, 200)
    ahi_series = highest([nz(x) for x in atr_val], 200)
    ahi = [(ahi_series[i] * 2.0) if ahi_series[i] is not None else 0.0 for i in range(n)]
    swU = highest(h, P.tnt_SWING_LEN)
    swLL = lowest(l, P.tnt_SWING_LEN)

    def H(series, i, k):
        j = i - k
        return series[j] if 0 <= j < n else None

    vcu = vcl = vdu = vdl = None
    abu = abl = abi = asu = asl = asi = None
    api = aspi = None
    swSt = 0
    swH_val = swH_idx = None
    swH_crossed = False
    swL_val = swL_idx = None
    swL_crossed = False

    bull_b = [None] * n
    bear_b = [None] * n

    for i in range(n):
        if vbc[i]:
            ol = l[i]
            for k in range(1, EMA_SLOW + 1):
                lk = H(l, i, k)
                if lk is not None and lk <= ol:
                    ol = lk
            s = min(o[i], c[i])
            if (s - ol) < ahi[i] * 0.5:
                s = ol + ahi[i] * 0.5
            vcu, vcl = s, ol
        if vsc[i]:
            oh = h[i]
            for k in range(1, EMA_SLOW + 1):
                hk = H(h, i, k)
                if hk is not None and hk >= oh:
                    oh = hk
            s = max(o[i], c[i])
            if (oh - s) < ahi[i] * 0.5:
                s = oh - ahi[i] * 0.5
            vdu, vdl = oh, s

        swSt_prev = swSt
        hk_sw = H(h, i, P.tnt_SWING_LEN)
        lk_sw = H(l, i, P.tnt_SWING_LEN)
        if hk_sw is not None and swU[i] is not None and hk_sw > swU[i]:
            swSt = 0
        elif lk_sw is not None and swLL[i] is not None and lk_sw < swLL[i]:
            swSt = 1
        if swSt == 0 and swSt_prev != 0:
            swH_val = H(h, i, P.tnt_SWING_LEN)
            swH_idx = i - P.tnt_SWING_LEN
            swH_crossed = False
        if swSt == 1 and swSt_prev != 1:
            swL_val = H(l, i, P.tnt_SWING_LEN)
            swL_idx = i - P.tnt_SWING_LEN
            swL_crossed = False

        if swH_val is not None and c[i] > swH_val and not swH_crossed and conf[i]:
            swH_crossed = True
            oL = H(l, i, 1)
            oH = H(h, i, 1)
            oI = i - 1
            lb = i - swH_idx
            if lb > 1:
                for k in range(1, lb):
                    ok_ = H(o, i, k)
                    ck_ = H(c, i, k)
                    lk_ = H(l, i, k)
                    hk_ = H(h, i, k)
                    if ok_ is not None and ck_ is not None and ok_ > ck_ and lk_ is not None and lk_ <= (oL if oL is not None else lk_):
                        oL, oH, oI = lk_, hk_, i - k
            abu, abl, abi = oH, oL, oI
        if swL_val is not None and c[i] < swL_val and not swL_crossed and conf[i]:
            swL_crossed = True
            oL = H(l, i, 1)
            oH = H(h, i, 1)
            oI = i - 1
            lb = i - swL_idx
            if lb > 1:
                for k in range(1, lb):
                    ok_ = H(o, i, k)
                    ck_ = H(c, i, k)
                    hk_ = H(h, i, k)
                    lk_ = H(l, i, k)
                    if ok_ is not None and ck_ is not None and ok_ < ck_ and hk_ is not None and hk_ >= (oH if oH is not None else hk_):
                        oH, oL, oI = hk_, lk_, i - k
            asu, asl, asi = oH, oL, oI

        # snapshots for zone sizing on a raw-TNT bar
        oU_b = min(nz(vcu, h[i]), nz(abu, h[i]))
        oL_b = max(nz(vcl, l[i]), nz(abl, l[i]))
        bull_b[i] = (oU_b, oL_b)
        oU_s = min(nz(vdu, h[i]), nz(asu, h[i]))
        oL_s = max(nz(vdl, l[i]), nz(asl, l[i]))
        bear_b[i] = (oU_s, oL_s)

    return {"bull": bull_b, "bear": bear_b}


# detection-plot id dictionary (S<N> -> descriptor)
PLOT_IDS = {
    "S1": "B2B PUP / PPD (offset 0)",
    "S2": "B2B PUP + FAUNA both candles (offset 0)",
    "S3": "B2B PUP + DISP/HV+D both (offset -1)",
    "S4": "B2B PUP + FAUNA + DISP/HV+D both (offset -1)",
    "S5": "B2B PUP + directional RVOL (SAAB/KRAT) both (offset 0)",
    "S6": "Any B2B + PBJ either candle (offset -1)",
    "S8": "Unified Combo + B2B PUP (offset -1)",
    "S9": "Uni Combo (S19 or S20) + B2B PUP (offset -1)",
    "S10": "Long1/Short1 B2B + B2B PUP (offset 0)",
    "S11": "FVG-Combo or Long1 + B2B PUP (offset -1)",
    "S12": "UU/UUU/UUUU + B2B PUP (offset 0)",
    "S13": "B2B Napalm + B2B PUP (offset 0)",
    "S14": "Continuous + B2B PUP (offset 0)",
    "S15": "TNT + B2B PUP (offset 0)",
    "S16": "Napalm consolidated + B2B PUP (offset -1)",
    "S17": "B2B HV+D + B2B PUP (offset -1)",
    "S18": "B2B HV+D+PBJ + B2B PUP (offset -1)",
    "UC2": "S19 Unified Combo x2 standalone (offset -1)",
    "FMU": "S20 FVG/Matrix/Uni Combo x2 standalone (offset -1)",
}
