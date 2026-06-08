"""PB & PBJ — 4 Signals — FULL detection fire-matrix core (Pine v5 -> Python).

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/pbj_only_4_signals_tickfriendly.pine"
  //@version=5, indicator("PB & PBJ 4 Signals [tickfriendly]", shorttitle="PBJ TF",
  overlay=true). ALREADY tick-safe in the source: no `import TradingView/...`, no
  `tv_ta.relativeVolume`, no `timeframe.in_seconds()`, no per-TF threshold table,
  no `time(timeframe.period,...)`. Engines are bar-grain agnostic, so the SAME
  core runs identically on N-tick bars and on wall-clock time bars.

ULTRACODE FULL PORT — scope statement (read this):
  This module ports EVERY one of the 4 detection plots in the source (4
  `plotshape(...)` detection signals + the same logic that drives the
  alertcondition()/alert() outputs), 1:1, directly from OHLCV. There is NO stub
  layer. COMPOSITE_PARTIAL is empty.

  The 4 detection plots (PLOT_IDS — exactly the source plotshapes):
    Sig#1  sigBullPB   belowbar  labelup    aqua    (PB,  bull)
    Sig#2  sigBullPBJ  belowbar  diamond    yellow  (PBJ, bull)
    Sig#3  sigBearPB   abovebar  labeldown  orange  (PB,  bear)
    Sig#4  sigBearPBJ  abovebar  diamond    red     (PBJ, bear)
  (The Pine also exposes f_sigAny as a 5th data_window numeric; we carry it as the
   derived aggregate "sigAny" — OR of the four — so a slicer can read it, but the
   four PLOT_IDS are the canonical detection plots.)

  EVERY sub-engine in the Pine is ported (no stub layer):
    ENGINE  Zoo MA          f_ma switch (VWMA/EMA/SMA/WMA/HMA), default VWMA len5
    ENGINE  Supertrend      st_atr/dyn_long/dyn_short, recursive curr_long/curr_short,
                            st_dir flip, sig_line (zoo_use_st default true)
    ENGINE  Crossovers      ta.crossover/crossunder(price, sig_line);
                            is_rising/is_falling; bull_reaccel/bear_reaccel
    ENGINE  PB&J filter     ema/atr/sma(volume), HH/LL extreme, vol gate
                            -> pbj_buy / pbj_sell
    ENGINE  Level mgmt      type lvl{upper,lower,vol,approached}; landers from
                            buy_cross/sell_cross (prev-bar OHLC banded by atr_pb);
                            reaccel landers from sig_line; f_check_approach removes
                            broken zones, sets/clears `approached`, returns hit;
                            wait_buy/wait_sell latches; cap arrays at 30
    ENGINE  PB&J latches    pbj_buy/sell -> wait_pbj_buy/sell latches
    ENGINE  Raw signals     sig_pb_buy/sig_pbj_buy/sig_pb_sell/sig_pbj_sell with
                            consume-on-fire (wait_* := false)
    ENGINE  Final 4 bools   barstate.isconfirmed gate; sigBullPB = pb_buy and not
                            pbj_buy; sigBullPBJ = pbj_buy; bear mirror.

  Pine semantics preserved: single forward pass; `[k]` = k-bars-back; `nz(x[1])`
  fallbacks; recursive `:=` series carried as explicit state; `var` -> persistent
  Python state. On a batch of CLOSED bars every bar is confirmed, so
  barstate.isconfirmed == True for all i (modelled explicitly as conf=True).

  NUMERIC LEVEL per detection plot = the price the marker sits at on the chart:
    bull plots (location.bottom / belowbar): level = bar low  (where PB/PBJ marks)
    bear plots (location.top    / abovebar): level = bar high (where PB/PBJ marks)
  level is float where fire==1, else None — exactly aligned with the fire column.

HONESTY: there is NO all-zero stub series in this module. Every plot in PLOT_IDS
is produced by real ported Pine logic. If a plot reads 0 on a tape it is because
the source logic produced 0 on those bars. The parity harness re-derives the
engines independently and reports a REAL pass/total.

Cosmetic / non-detection Pine objects intentionally NOT ported as plots:
  - the alert() / alertcondition() message strings and the multiplexer (mux) — they
    are derived from the same four fires (we expose sigAny so a slicer can read the
    ANY-signal flag); porting the human-readable strings adds no detection signal.
  - PB zones themselves are tracked as `type lvl` state (never drawn) — ported as
    logic, consistent with the source which also never draws them.
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nn_harness import (  # noqa: E402
    Bar, nz, sma, atr as _atr_ohlc, highest, lowest,
)


# ──────────────────────────────── parameters ────────────────────────────────
@dataclass
class Params:
    """Every Pine input.* / hardcoded threshold as a parameter (source default)."""
    # OKEH — Zoo Engine
    zoo_ma_type: str = "VWMA"          # input.string default
    zoo_ma_len: int = 5               # input.int 5
    # OKEH — PB&J Filter
    pbj_ma_period: int = 20           # input.int 20
    pbj_atr_period: int = 14          # input.int 14
    pbj_hh_ll: int = 25               # input.int 25
    pbj_atr_mult: float = 3.0         # input.float 3.0
    pbj_vol_period: int = 20          # input.int 20
    pbj_vol_mult: float = 0.1         # input.float 0.1
    # OKEH — Supertrend
    use_st: bool = True               # input.bool true
    st_period: int = 10               # input.int 10
    st_mult: float = 2.0              # input.float 2.0
    # PB zone band (Pine: atr_pb = ta.atr(14) * 2.0) — the 14 and 2.0 are params
    pb_atr_period: int = 14
    pb_atr_mult: float = 2.0
    pb_band_frac: float = 0.5         # Pine `atr_pb * 0.5` minimum zone half-height
    # Approach proximity bands (Pine: upper*1.005 / lower*0.995)
    approach_up_frac: float = 1.005
    approach_dn_frac: float = 0.995
    # zone array cap (Pine: while size > 30)
    max_zones: int = 30
    # syminfo.mintick fallback (cents) — zones below this are not added (Pine guard)
    mintick: float = 0.01
    # plot toggles (Pine input.bool, all ON by default)
    show_BullPB: bool = True
    show_BullPBJ: bool = True
    show_BearPB: bool = True
    show_BearPBJ: bool = True


# canonical detection-plot ids (exactly the four source plotshapes), stable order.
PLOT_IDS = ["sigBullPB", "sigBullPBJ", "sigBearPB", "sigBearPBJ"]


@dataclass
class _Lvl:
    upper: float
    lower: float
    vol: float
    approached: bool = False


# ─────────────────────────── Pine ta.* MA variants ──────────────────────────
def _ema(src, length):
    """Pine ta.ema: alpha = 2/(len+1); seeded from the first non-None value
    (Pine seeds EMA at its first valid bar, no SMA warmup)."""
    out = [None] * len(src)
    alpha = 2.0 / (length + 1.0)
    prev = None
    for i, x in enumerate(src):
        if x is None:
            out[i] = prev
            continue
        x = float(x)
        prev = x if prev is None else (alpha * x + (1 - alpha) * prev)
        out[i] = prev
    return out


def _wma(src, length):
    out = [None] * len(src)
    if length < 1:
        return out
    w = list(range(1, length + 1))
    sw = float(sum(w))
    for i in range(len(src)):
        if i + 1 < length:
            continue
        win = src[i - length + 1: i + 1]
        if any(x is None for x in win):
            continue
        out[i] = sum(win[j] * w[j] for j in range(length)) / sw
    return out


def _hma(src, length):
    half = max(1, length // 2)
    sq = max(1, int(round(math.sqrt(length))))
    w1 = _wma(src, half)
    w2 = _wma(src, length)
    diff = [None if (w1[i] is None or w2[i] is None) else 2 * w1[i] - w2[i]
            for i in range(len(src))]
    base = [0.0 if d is None else d for d in diff]
    h = _wma(base, sq)
    return [None if diff[i] is None else h[i] for i in range(len(src))]


def _vwma(c, v, length):
    """Pine ta.vwma = sma(close*volume,len)/sma(volume,len)."""
    pv = [None if (c[i] is None or v[i] is None) else c[i] * v[i] for i in range(len(c))]
    num = sma(pv, length)
    den = sma(v, length)
    out = [None] * len(c)
    for i in range(len(c)):
        if num[i] is not None and den[i] not in (None, 0):
            out[i] = num[i] / den[i]
    return out


def _base_ma(c, v, p: Params):
    t, ln = p.zoo_ma_type, p.zoo_ma_len
    if t == "EMA":
        return _ema(c, ln)
    if t == "SMA":
        return sma(c, ln)
    if t == "WMA":
        return _wma(c, ln)
    if t == "HMA":
        return _hma(c, ln)
    if t == "VWMA":
        return _vwma(c, v, ln)
    return sma(c, ln)


# ──────────────────────────────── core compute ──────────────────────────────
def compute(bars, *, params: Params | None = None):
    """Run the full PB/PBJ detection on Bar objects (oldest-first).

    Returns a dict:
      ts                -> list[int]            (bar open timestamps)
      fire_<PLOT_ID>    -> list[int] 0/1        (one per detection plot)
      lvl_<PLOT_ID>     -> list[float|None]     (price the marker sits at; None off)
      sigAny            -> list[int] 0/1        (Pine f_sigAny aggregate)
    Tick and time grains call this same function (one code path).
    """
    p = params or Params()
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    l = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]
    n = len(bars)

    # ── precomputed series (Pine ta.* are whole-series; we index by bar) ──
    base_ma = _base_ma(c, v, p)
    st_atr_s = _atr_ohlc(o, h, l, c, p.st_period)
    pbj_ma = _ema(c, p.pbj_ma_period)
    pbj_atr = _atr_ohlc(o, h, l, c, p.pbj_atr_period)
    avg_vol = sma(v, p.pbj_vol_period)
    atr_pb_s = _atr_ohlc(o, h, l, c, p.pb_atr_period)
    low_hh = lowest(l, p.pbj_hh_ll)
    high_hh = highest(h, p.pbj_hh_ll)

    # ── supertrend recursive state (Pine var st_dir; nz(prev) carries) ──
    st_dir = 1
    curr_long_prev = None
    curr_short_prev = None
    sig_line_prev = None
    sig_line_prev2 = None

    # ── level arrays + wait latches (Pine var) ──
    bull_lvls: list[_Lvl] = []
    bear_lvls: list[_Lvl] = []
    wait_buy = wait_sell = wait_pbj_buy = wait_pbj_sell = False

    # ── output detection columns ──
    fireBullPB = [0] * n
    fireBullPBJ = [0] * n
    fireBearPB = [0] * n
    fireBearPBJ = [0] * n
    lvlBullPB: list[float | None] = [None] * n
    lvlBullPBJ: list[float | None] = [None] * n
    lvlBearPB: list[float | None] = [None] * n
    lvlBearPBJ: list[float | None] = [None] * n

    def add_lvl(arr, up, lo, vol):
        # Pine f_add_lvl: only if |up-lo| >= mintick
        if abs(up - lo) >= p.mintick:
            arr.append(_Lvl(up, lo, vol))

    def check_approach(arr, is_bull, cc, ll, hh):
        # Pine f_check_approach: iterate high->low, prune broken zones, set/clear
        # `approached`, return whether any zone was newly approached this bar.
        approached = False
        for i in range(len(arr) - 1, -1, -1):
            lv = arr[i]
            if is_bull and cc < lv.lower:
                arr.pop(i)
                continue
            if (not is_bull) and cc > lv.upper:
                arr.pop(i)
                continue
            ap = lv.upper * p.approach_up_frac if is_bull else lv.lower * p.approach_dn_frac
            if is_bull:
                if not lv.approached and ll <= ap:
                    approached = True
                    lv.approached = True
                elif lv.approached and ll > lv.upper:
                    lv.approached = False
            else:
                if not lv.approached and hh >= ap:
                    approached = True
                    lv.approached = True
                elif lv.approached and hh < lv.lower:
                    lv.approached = False
        return approached

    for i in range(n):
        bm = base_ma[i]
        sa = st_atr_s[i]
        conf = True  # barstate.isconfirmed on closed bars

        if bm is None or sa is None:
            # warmup: still advance the sig_line history skeleton so that, once
            # warm, prev/prev2 reference the correct prior bars (they stay None
            # here -> crossovers can't fire until two warm bars exist, matching
            # Pine where ta.crossover needs a defined [1]).
            sig_line_prev2 = sig_line_prev
            sig_line_prev = None
            continue

        st_atr = p.st_mult * sa
        dyn_long = bm - st_atr
        dyn_short = bm + st_atr

        # Pine: curr_long := base_ma > nz(curr_long[1], dyn_long) ? max(dyn_long, nz(curr_long[1])) : dyn_long
        cl_base = nz(curr_long_prev, dyn_long)
        curr_long = max(dyn_long, nz(curr_long_prev)) if bm > cl_base else dyn_long
        cs_base = nz(curr_short_prev, dyn_short)
        curr_short = min(dyn_short, nz(curr_short_prev)) if bm < cs_base else dyn_short

        if p.use_st:
            # Pine flips read PRIOR-bar curr_short/curr_long (curr_short[1])
            if st_dir == -1 and c[i] > nz(curr_short_prev):
                st_dir = 1
            elif st_dir == 1 and c[i] < nz(curr_long_prev):
                st_dir = -1
            sig_line = curr_long if st_dir == 1 else curr_short
        else:
            sig_line = bm

        # crossovers (ta.crossover/crossunder of price vs sig_line)
        buy_cross = (sig_line_prev is not None and i >= 1
                     and c[i] > sig_line and c[i - 1] <= sig_line_prev)
        sell_cross = (sig_line_prev is not None and i >= 1
                      and c[i] < sig_line and c[i - 1] >= sig_line_prev)
        is_rising = sig_line > nz(sig_line_prev)
        is_falling = sig_line < nz(sig_line_prev)
        bull_reaccel = (st_dir == 1 and is_rising
                        and nz(sig_line_prev) == nz(sig_line_prev2))
        bear_reaccel = (st_dir == -1 and is_falling
                        and nz(sig_line_prev) == nz(sig_line_prev2))

        # ── PB&J filter ──
        if c[i] == 0 or pbj_atr[i] is None:
            thresh = 0.0
        else:
            thresh = pbj_atr[i] / c[i] * p.pbj_atr_mult
        pbj_buy = (pbj_ma[i] is not None and avg_vol[i] is not None
                   and low_hh[i] is not None
                   and l[i] < pbj_ma[i] * (1 - thresh)
                   and l[i] == low_hh[i]
                   and v[i] > avg_vol[i] * p.pbj_vol_mult)
        pbj_sell = (pbj_ma[i] is not None and avg_vol[i] is not None
                    and high_hh[i] is not None
                    and h[i] > pbj_ma[i] * (1 + thresh)
                    and h[i] == high_hh[i]
                    and v[i] > avg_vol[i] * p.pbj_vol_mult)

        # ── level landers (Pine f_add_lander uses prev-bar OHLC, needs i>=1) ──
        atrpb = (atr_pb_s[i] or 0.0) * p.pb_atr_mult
        if buy_cross and i >= 1:
            up = max(o[i - 1], c[i - 1])
            lo = l[i - 1]
            if up - lo < atrpb * p.pb_band_frac:
                up = lo + atrpb * p.pb_band_frac
            add_lvl(bull_lvls, up, lo, v[i - 1])
        if sell_cross and i >= 1:
            up = h[i - 1]
            lo = min(o[i - 1], c[i - 1])
            if up - lo < atrpb * p.pb_band_frac:
                lo = up - atrpb * p.pb_band_frac
            add_lvl(bear_lvls, up, lo, v[i - 1])
        # ── reaccel landers (Pine f_add_reaccel uses sig_line + current OHLC) ──
        if bull_reaccel:
            p1 = sig_line
            p2 = min(o[i], c[i])
            add_lvl(bull_lvls, max(p1, p2), min(p1, p2), v[i])
        if bear_reaccel:
            p1 = sig_line
            p2 = max(o[i], c[i])
            add_lvl(bear_lvls, max(p1, p2), min(p1, p2), v[i])

        # ── approach (Pine gates this with barstate.isconfirmed) ──
        if conf:
            if check_approach(bull_lvls, True, c[i], l[i], h[i]):
                wait_buy = True
            if check_approach(bear_lvls, False, c[i], l[i], h[i]):
                wait_sell = True

        if pbj_buy:
            wait_pbj_buy = True
        if pbj_sell:
            wait_pbj_sell = True

        # ── cap zone arrays (Pine while size > 30: array.shift) ──
        while len(bull_lvls) > p.max_zones:
            bull_lvls.pop(0)
        while len(bear_lvls) > p.max_zones:
            bear_lvls.pop(0)

        # ── raw signal bools + consume-on-fire latches ──
        spb = buy_cross and wait_buy
        spjb = buy_cross and wait_pbj_buy
        sps = sell_cross and wait_sell
        spjs = sell_cross and wait_pbj_sell
        if spb:
            wait_buy = False
        if spjb:
            wait_pbj_buy = False
        if sps:
            wait_sell = False
        if spjs:
            wait_pbj_sell = False

        # ── final four detection bools (barstate.isconfirmed gate) ──
        sigBullPB = conf and spb and not spjb
        sigBullPBJ = conf and spjb
        sigBearPB = conf and sps and not spjs
        sigBearPBJ = conf and spjs

        if sigBullPB:
            fireBullPB[i] = 1
            lvlBullPB[i] = l[i]          # location.bottom / belowbar -> bar low
        if sigBullPBJ:
            fireBullPBJ[i] = 1
            lvlBullPBJ[i] = l[i]
        if sigBearPB:
            fireBearPB[i] = 1
            lvlBearPB[i] = h[i]          # location.top / abovebar -> bar high
        if sigBearPBJ:
            fireBearPBJ[i] = 1
            lvlBearPBJ[i] = h[i]

        # advance recursive history
        curr_long_prev = curr_long
        curr_short_prev = curr_short
        sig_line_prev2 = sig_line_prev
        sig_line_prev = sig_line

    sigAny = [1 if (fireBullPB[i] or fireBullPBJ[i] or fireBearPB[i] or fireBearPBJ[i])
              else 0 for i in range(n)]

    out = {
        "ts": ts,
        "fire_sigBullPB": fireBullPB,
        "fire_sigBullPBJ": fireBullPBJ,
        "fire_sigBearPB": fireBearPB,
        "fire_sigBearPBJ": fireBearPBJ,
        "lvl_sigBullPB": lvlBullPB,
        "lvl_sigBullPBJ": lvlBullPBJ,
        "lvl_sigBearPB": lvlBearPB,
        "lvl_sigBearPBJ": lvlBearPBJ,
        "sigAny": sigAny,
    }
    return out
