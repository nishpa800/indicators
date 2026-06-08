# Python is a Python tick  /  Python is a Python time-based  (shared substrate)
# =============================================================================
# VOB Asym T3 x6 + MutEx Lines + Claude v10  ->  Python detection fire-matrix CORE
# -----------------------------------------------------------------------------
# Source (read from disk, path has spaces):
#   ".../June 7/Tick Friendly conversion/vob v10_tickfriendly.pine"
#   (Pine v5, tick-friendly: NO relativeVolume / NO per-TF table -> no RE10023.
#    label.new / table.new graphic objects removed; detection stays on plotshape.)
#
# HONEST SCOPE — FULL FAITHFUL PORT, ZERO STUBS.
#   Every one of the 31 Pine plotshape() detection plots is produced here from
#   OHLCV alone. VOB v10 is fully OHLCV-derivable (no relativeVolume, no PB&J, no
#   request.security), so the deep zone engine (f_vob A..F, proximity-dedup,
#   close-through invalidation, T3 volume-pool comparison), Nagasaki, the strict
#   F->A VLB ladder state machine, and the multi-zone same-candle counts are all
#   ported construct-for-construct from the Pine source — NOT stubbed.
#
# THE 31 DETECTION PLOTS (Pine plotshape order):
#   12  T3{a..f} Buy / Sell        (plot_t3_buy_*, plot_t3_sell_*)
#    1  Nagasaki                    (plot_nagasaki)
#   12  ZoneBull/ZoneBear {A..F}    (fire_zb_*, fire_zs_*)
#    2  VLB Bull / VLB Bear         (plot_vlb_bull, plot_vlb_bear)
#    4  Multi-Zone Bull 2/3+, Bear 2/3+ (plot_mz_b2/b3/s2/s3)
#
# Each plot emits a per-bar 0/1 fire AND a numeric level column (lvl_*):
#   * T3 buy/sell  -> close on the firing bar (the price the signal references)
#   * Nagasaki     -> volume[1] (the ATH volume that triggered it)
#   * zone fires   -> the just-pushed zone's midpoint (mid)
#   * VLB          -> the completing A-tier zone midpoint
#   * Multi-Zone   -> the count of same-candle zone fires on that side
#
# Pine v5 SEMANTICS PRESERVED:
#   * ta.ema  : alpha=2/(len+1), seeded by the value at the bar where the SMA seed
#               completes (Pine seeds EMA from SMA of the first `len` values).
#   * ta.atr(200) via Wilder RMA of true range; atr_base = highest(atr(200),200);
#               atr_proximity = atr_base*3 ; atr_adjust = atr_base*2  (source 267-269)
#   * crossover/crossunder gated by barstate.isconfirmed (always true offline).
#   * zone arrays NEVER shrink on invalidation -> Pine sets fields to na and keeps
#               the slot; the array only shifts() when size()>15. So nzb/nzs (the
#               zone-formation booleans) = array.size() grew THIS bar, and an
#               invalidation does NOT change size. Modeled faithfully: invalidated
#               zones become na-zones in place; a push appends a slot.
#   * array.get(i-1) at i=0 -> Pine negative index returns the LAST element
#               (Python-style). Modeled with [-1].
#   * f_cd_ok cooldown : na(last) or (bar_index - last) > cd ; last := bar_index on fire.
#
# Every threshold is a parameter (Params). relativeVolume is NOT used by this
# indicator, so the canonical shim is intentionally absent here (using it would be
# a fabrication). The harness still wires the shim for the batch — VOB simply does
# not call it.
#
# ONE shared core: tick/vob_v10_tick.py and time/vob_v10_time.py both import THIS
# module. The ONLY difference between them is the bar-construction grain fed in
# (N-tick bars vs wall-clock time bars). The detection logic is identical.
# =============================================================================
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from _nine_nines_common import Bar  # noqa: E402  (re-export type)

TIERS = ("a", "b", "c", "d", "e", "f")
_NA = None  # Pine na


def _ge(a, b):
    """Pine `a >= b` with na semantics: na on either side -> False (if-branch
    not taken; the else-branch resets the ladder, matching Pine `if na`)."""
    return (a is not None) and (b is not None) and (a >= b)


def _le(a, b):
    """Pine `a <= b` with na semantics (na -> False)."""
    return (a is not None) and (b is not None) and (a <= b)


# ─────────────────────────────────────────────────────────────────────────────
# PARAMETERS — every Pine input.* threshold, defaulted to the source defaults.
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Params:
    # Sensitivities (EMA fast lengths per tier; slow = fast + ema_slow_offset).
    sens: dict = field(default_factory=lambda: dict(
        a=2500, b=2250, c=2000, d=1500, e=1250, f=1000))
    ema_slow_offset: int = 13          # source: len2 = len1 + 13
    # Signal params (source 161-176).
    super_mult: float = 1.5            # Tier 3 super volume multiplier
    cooldown_bars: int = 100           # f_cd_ok cooldown
    # ATR engine (source 267-269): atr_base = highest(atr(atr_len), atr_hi_len).
    atr_len: int = 200
    atr_hi_len: int = 200
    atr_proximity_mult: float = 3.0    # atr_proximity = atr_base * 3
    atr_adjust_mult: float = 2.0       # atr_adjust   = atr_base * 2
    zone_max: int = 15                 # array shift when size() > 15
    # Per-tier enable toggles (en_zone_*). T3 show_* default True.
    en_zone: dict = field(default_factory=lambda: {t: True for t in TIERS})
    show_t3_buy: dict = field(default_factory=lambda: {t: True for t in TIERS})
    show_t3_sell: dict = field(default_factory=lambda: {t: True for t in TIERS})
    show_nagasaki: bool = True
    show_vlb_bull: bool = True
    show_vlb_bear: bool = True
    show_multi_bull_2: bool = True
    show_multi_bull_3: bool = True
    show_multi_bear_2: bool = True
    show_multi_bear_3: bool = True


# Ordered list of the 31 detection plot ids (stable schema for the fire matrix).
PLOT_IDS: list[str] = (
    [f"t3_buy_{t}" for t in TIERS]
    + [f"t3_sell_{t}" for t in TIERS]
    + ["nagasaki"]
    + [f"zb_{t}" for t in TIERS]
    + [f"zs_{t}" for t in TIERS]
    + ["vlb_bull", "vlb_bear",
       "mz_b2", "mz_b3", "mz_s2", "mz_s3"]
)
assert len(PLOT_IDS) == 31, f"expected 31 detection plots, got {len(PLOT_IDS)}"


# ─────────────────────────────────────────────────────────────────────────────
# Pine ta.ema — alpha = 2/(len+1), seeded from SMA of the first `len` values.
# ─────────────────────────────────────────────────────────────────────────────
def _ema(values, length):
    n = len(values)
    out = [None] * n
    alpha = 2.0 / (length + 1)
    prev = None
    seed_sum = 0.0
    seed_cnt = 0
    for i in range(n):
        x = values[i]
        if x is None:
            out[i] = prev
            continue
        x = float(x)
        if prev is None:
            seed_sum += x
            seed_cnt += 1
            if seed_cnt == length:
                prev = seed_sum / length
                out[i] = prev
        else:
            prev = alpha * x + (1.0 - alpha) * prev
            out[i] = prev
    return out


def _rma(values, length):
    out = [None] * len(values)
    prev = None
    s = 0.0
    cnt = 0
    for i, v in enumerate(values):
        v = float(v)
        if prev is None:
            s += v
            cnt += 1
            if cnt == length:
                prev = s / length
                out[i] = prev
        else:
            prev = (prev * (length - 1) + v) / length
            out[i] = prev
    return out


def _true_range(o, h, l, c):
    n = len(c)
    tr = [0.0] * n
    for i in range(n):
        if i == 0:
            tr[i] = h[i] - l[i]
        else:
            pc = c[i - 1]
            tr[i] = max(h[i] - l[i], abs(h[i] - pc), abs(l[i] - pc))
    return tr


def _atr(o, h, l, c, length):
    return _rma(_true_range(o, h, l, c), length)


def _highest(values, length):
    n = len(values)
    out = [None] * n
    from collections import deque
    win = deque()
    for i in range(n):
        win.append(values[i])
        if len(win) > length:
            win.popleft()
        vals = [w for w in win if w is not None]
        if len(win) == length and vals:
            out[i] = max(vals)
    return out


def _lowest_series(values, length):
    """ta.lowest(len) over a value series (used for ta.lowest(len2) in f_vob)."""
    n = len(values)
    out = [None] * n
    from collections import deque
    win = deque()
    for i in range(n):
        win.append(values[i])
        if len(win) > length:
            win.popleft()
        vals = [w for w in win if w is not None]
        if len(win) == length and vals:
            out[i] = min(vals)
    return out


def _highest_series(values, length):
    return _highest(values, length)


# ─────────────────────────────────────────────────────────────────────────────
# Zone object — mirrors the Pine `level` UDT. na fields == invalidated.
# ─────────────────────────────────────────────────────────────────────────────
class _Level:
    __slots__ = ("indx", "upper", "lower", "mid", "vol", "o", "h", "l", "c")

    def __init__(self, indx, upper, lower, mid, vol, o, h, l, c):
        self.indx = indx
        self.upper = upper
        self.lower = lower
        self.mid = mid
        self.vol = vol
        self.o = o
        self.h = h
        self.l = l
        self.c = c

    @staticmethod
    def na():
        return _Level(_NA, _NA, _NA, _NA, _NA, _NA, _NA, _NA, _NA)


# ─────────────────────────────────────────────────────────────────────────────
# CORE VOB ENGINE per tier — faithful port of f_vob (source 532-649).
# Returns per-bar arrays:
#   t3_buy[], t3_sell[]            (the T3 volume-pool signal, pre-cooldown)
#   nzb[], nzs[]                   (zone-formation booleans: array grew this bar)
#   zb_mid[], zs_mid[]            (midpoint of the just-pushed zone, for levels)
#   last_zone_bull[], last_zone_bear[]  (the _Level pushed this bar, for VLB)
# ─────────────────────────────────────────────────────────────────────────────
def _run_tier(o, h, l, c, v, length, p: Params, atr_prox_arr, atr_adj_arr):
    n = len(c)
    len2 = length + p.ema_slow_offset
    e1 = _ema(c, length)
    e2 = _ema(c, len2)
    lowest = _lowest_series(l, len2)    # ta.lowest(len2) over LOW
    highest = _highest_series(h, len2)  # ta.highest(len2) over HIGH

    t3_buy = [False] * n
    t3_sell = [False] * n
    nzb = [False] * n
    nzs = [False] * n
    zb_mid = [None] * n
    zs_mid = [None] * n
    last_bull = [None] * n
    last_bear = [None] * n

    lo_lvl: list[_Level] = []   # bullish zones (Pine lower_*)
    up_lvl: list[_Level] = []   # bearish zones (Pine upper_*)

    for i in range(n):
        # crossover/crossunder require both EMAs valid this and prior bar.
        ok = (e1[i] is not None and e2[i] is not None
              and e1[i - 1] is not None and e2[i - 1] is not None and i > 0)
        cup = ok and (e1[i - 1] <= e2[i - 1]) and (e1[i] > e2[i])
        cdn = ok and (e1[i - 1] >= e2[i - 1]) and (e1[i] < e2[i])

        atr_adj = atr_adj_arr[i] if atr_adj_arr[i] is not None else 0.0
        atr_prox = atr_prox_arr[i] if atr_prox_arr[i] is not None else 0.0

        sz_lo_before = len(lo_lvl)
        sz_up_before = len(up_lvl)
        pushed_bull_mid = None   # mid of the zone pushed THIS bar (as formed)
        pushed_bear_mid = None

        # ── bullish zone push on crossover (source 541-551) ──────────────────
        # Pine: for i=1 to len2: if low[i]==lowest -> push once (first match).
        if cup and lowest[i] is not None:
            lw = lowest[i]
            for k in range(1, len2 + 1):
                j = i - k
                if j < 0:
                    break
                if l[j] == lw:
                    vol = 0.0
                    for m in range(0, k + 1):
                        jm = i - m
                        if jm >= 0:
                            vol += v[jm]
                    src = min(o[j], c[j])
                    if (src - lw) < atr_adj * 0.5:
                        src = lw + atr_adj * 0.5
                    mid = (src + lw) / 2.0
                    lo_lvl.append(_Level(i, src, lw, mid, vol,
                                         o[j], h[j], l[j], c[j]))
                    pushed_bull_mid = mid   # as-formed mid (marker level)
                    break

        # ── bearish zone push on crossunder (source 553-563) ─────────────────
        if cdn and highest[i] is not None:
            hg = highest[i]
            for k in range(1, len2 + 1):
                j = i - k
                if j < 0:
                    break
                if h[j] == hg:
                    vol = 0.0
                    for m in range(0, k + 1):
                        jm = i - m
                        if jm >= 0:
                            vol += v[jm]
                    src = max(o[j], c[j])
                    if (hg - src) < atr_adj * 0.5:
                        src = hg - atr_adj * 0.5
                    mid = (src + hg) / 2.0
                    up_lvl.append(_Level(i, hg, src, mid, vol,
                                         o[j], h[j], l[j], c[j]))
                    pushed_bear_mid = mid   # as-formed mid (marker level)
                    break

        # ── bullish proximity-dedup + close-through invalidation (566-576) ───
        # Pine keeps slots; invalidation = replace with na-Level. Never shrinks
        # except the size()>15 shift at the end.
        if len(lo_lvl) > 0:
            for idx in range(0, len(lo_lvl)):
                lz = lo_lvl[idx]
                lz1 = lo_lvl[idx - 1]  # Pine get(-1) at idx==0 -> last element
                if (lz.mid is not None and lz1.mid is not None
                        and abs(lz.mid - lz1.mid) < atr_prox):
                    lo_lvl[idx - 1] = _Level.na()
                if lz.lower is not None and c[i] < lz.lower:
                    lo_lvl[idx] = _Level.na()
            if len(lo_lvl) > p.zone_max:
                lo_lvl.pop(0)

        # ── bearish proximity-dedup + close-through invalidation (578-590) ───
        if len(up_lvl) > 0:
            for idx in range(0, len(up_lvl)):
                uz = up_lvl[idx]
                uz1 = up_lvl[idx - 1]
                if (uz.mid is not None and uz1.mid is not None
                        and abs(uz.mid - uz1.mid) < atr_prox):
                    up_lvl[idx - 1] = _Level.na()
                if uz.upper is not None and c[i] > uz.upper:
                    up_lvl[idx] = _Level.na()
            if len(up_lvl) > p.zone_max:
                up_lvl.pop(0)

        # ── T3 volume-pool comparison (source 592-647) ───────────────────────
        # barstate.isconfirmed -> always true offline (closed-bar scoring).
        bp = 0.0   # bull pool
        sp = 0.0   # bear pool
        db_vol = 0.0; db_low = 0.0; db_high = 0.0  # dominant bull zone
        da_vol = 0.0; da_low = 0.0; da_high = 0.0  # dominant bear zone
        bc = 0     # active bull zone count
        ac = 0     # active bear zone count
        for lz in lo_lvl:
            if lz.vol is not None:
                bp += lz.vol
                bc += 1
                if lz.vol > db_vol:
                    db_vol = lz.vol
                    db_low = lz.lower
                    db_high = lz.upper
        for uz in up_lvl:
            if uz.vol is not None:
                sp += uz.vol
                ac += 1
                if uz.vol > da_vol:
                    da_vol = uz.vol
                    da_low = uz.lower
                    da_high = uz.upper

        pat_bull = (c[i] >= db_low) and (c[i] <= db_high)
        pat_bear = (c[i] >= da_low) and (c[i] <= da_high)

        t3_buy[i] = (bc == 1 and sp > 0 and db_vol > sp * p.super_mult and pat_bull)
        t3_sell[i] = (ac == 1 and bp > 0 and da_vol > bp * p.super_mult and pat_bear)

        # ── zone-formation booleans: array grew this bar (source 670-675) ────
        nzb[i] = len(lo_lvl) > sz_lo_before
        nzs[i] = len(up_lvl) > sz_up_before
        if nzb[i]:
            # VLB reads Pine f_last_zone = arr.get(size-1) (post-invalidation,
            # na-safe via _ge/_le); the marker LEVEL is the zone as formed.
            last_bull[i] = lo_lvl[-1]
            zb_mid[i] = pushed_bull_mid
        if nzs[i]:
            last_bear[i] = up_lvl[-1]
            zs_mid[i] = pushed_bear_mid

    return dict(t3_buy=t3_buy, t3_sell=t3_sell, nzb=nzb, nzs=nzs,
                zb_mid=zb_mid, zs_mid=zs_mid,
                last_bull=last_bull, last_bear=last_bear)


# ─────────────────────────────────────────────────────────────────────────────
# Cooldown gate — f_cd_ok + last := bar_index on fire (source 402-403, 730-770).
# ─────────────────────────────────────────────────────────────────────────────
def _cd_gate(sig, cd):
    n = len(sig)
    out = [0] * n
    last = None
    for i in range(n):
        if sig[i] and (last is None or (i - last) > cd):
            out[i] = 1
            last = i
    return out


# ─────────────────────────────────────────────────────────────────────────────
# VLB strict F->A ladder state machine — faithful port (source 1198-1446).
# Bull: state 0=waitF..5=waitA. Any bear-zone-bar resets bull window. Within a
# bull-zone bar, F/E/D/C/B/A processed in order; wrong-tier or price-fail
# (new.high < prior.lower) -> reset. A completing with new.high >= prior.lower
# -> vlb_bull_complete = True; window resets. Bear is the mirror (new.low <= prior.upper).
# ─────────────────────────────────────────────────────────────────────────────
def _vlb_bull(tier_out, n):
    nzb = {t: tier_out[t]["nzb"] for t in TIERS}
    last = {t: tier_out[t]["last_bull"] for t in TIERS}
    complete = [False] * n
    a_mid = [None] * n

    state = 0
    p_lo = None
    p_hi = None
    for i in range(n):
        any_bear = any(tier_out[t]["nzs"][i] for t in TIERS)
        any_bull = any(nzb[t][i] for t in TIERS)
        if any_bear:
            state = 0; p_lo = None; p_hi = None
            continue
        if not any_bull:
            continue
        # F (expects state==0)
        if nzb["f"][i]:
            if state == 0:
                zf = last["f"][i]
                p_lo = zf.lower; p_hi = zf.upper
                state = 1
            else:
                state = 0; p_lo = None; p_hi = None
        # E (expects state==1)
        if nzb["e"][i] and state > 0:
            if state == 1:
                ze = last["e"][i]
                if _ge(ze.upper, p_lo):
                    p_lo = ze.lower; p_hi = ze.upper; state = 2
                else:
                    state = 0; p_lo = None; p_hi = None
            else:
                state = 0; p_lo = None; p_hi = None
        # D (expects state==2)
        if nzb["d"][i] and state > 0:
            if state == 2:
                zd = last["d"][i]
                if _ge(zd.upper, p_lo):
                    p_lo = zd.lower; p_hi = zd.upper; state = 3
                else:
                    state = 0; p_lo = None; p_hi = None
            else:
                state = 0; p_lo = None; p_hi = None
        # C (expects state==3)
        if nzb["c"][i] and state > 0:
            if state == 3:
                zc = last["c"][i]
                if _ge(zc.upper, p_lo):
                    p_lo = zc.lower; p_hi = zc.upper; state = 4
                else:
                    state = 0; p_lo = None; p_hi = None
            else:
                state = 0; p_lo = None; p_hi = None
        # B (expects state==4)
        if nzb["b"][i] and state > 0:
            if state == 4:
                zb = last["b"][i]
                if _ge(zb.upper, p_lo):
                    p_lo = zb.lower; p_hi = zb.upper; state = 5
                else:
                    state = 0; p_lo = None; p_hi = None
            else:
                state = 0; p_lo = None; p_hi = None
        # A (expects state==5) -> completion
        if nzb["a"][i] and state > 0:
            if state == 5:
                za = last["a"][i]
                if _ge(za.upper, p_lo):
                    complete[i] = True
                    a_mid[i] = za.mid
                state = 0; p_lo = None; p_hi = None
            else:
                state = 0; p_lo = None; p_hi = None
    return complete, a_mid


def _vlb_bear(tier_out, n):
    nzs = {t: tier_out[t]["nzs"] for t in TIERS}
    last = {t: tier_out[t]["last_bear"] for t in TIERS}
    complete = [False] * n
    a_mid = [None] * n

    state = 0
    p_lo = None
    p_hi = None
    for i in range(n):
        any_bull = any(tier_out[t]["nzb"][i] for t in TIERS)
        any_bear = any(nzs[t][i] for t in TIERS)
        if any_bull:
            state = 0; p_lo = None; p_hi = None
            continue
        if not any_bear:
            continue
        if nzs["f"][i]:
            if state == 0:
                zf = last["f"][i]
                p_lo = zf.lower; p_hi = zf.upper
                state = 1
            else:
                state = 0; p_lo = None; p_hi = None
        if nzs["e"][i] and state > 0:
            if state == 1:
                ze = last["e"][i]
                if _le(ze.lower, p_hi):
                    p_lo = ze.lower; p_hi = ze.upper; state = 2
                else:
                    state = 0; p_lo = None; p_hi = None
            else:
                state = 0; p_lo = None; p_hi = None
        if nzs["d"][i] and state > 0:
            if state == 2:
                zd = last["d"][i]
                if _le(zd.lower, p_hi):
                    p_lo = zd.lower; p_hi = zd.upper; state = 3
                else:
                    state = 0; p_lo = None; p_hi = None
            else:
                state = 0; p_lo = None; p_hi = None
        if nzs["c"][i] and state > 0:
            if state == 3:
                zc = last["c"][i]
                if _le(zc.lower, p_hi):
                    p_lo = zc.lower; p_hi = zc.upper; state = 4
                else:
                    state = 0; p_lo = None; p_hi = None
            else:
                state = 0; p_lo = None; p_hi = None
        if nzs["b"][i] and state > 0:
            if state == 4:
                zb = last["b"][i]
                if _le(zb.lower, p_hi):
                    p_lo = zb.lower; p_hi = zb.upper; state = 5
                else:
                    state = 0; p_lo = None; p_hi = None
            else:
                state = 0; p_lo = None; p_hi = None
        if nzs["a"][i] and state > 0:
            if state == 5:
                za = last["a"][i]
                if _le(za.lower, p_hi):
                    complete[i] = True
                    a_mid[i] = za.mid
                state = 0; p_lo = None; p_hi = None
            else:
                state = 0; p_lo = None; p_hi = None
    return complete, a_mid


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ENTRY — compute the full 31-plot fire matrix + level columns.
# ─────────────────────────────────────────────────────────────────────────────
def compute(bars, params=None, *, tf_seconds=None, grain=None):
    """Return a dict with:
        ts            : list of bar timestamps
        fire_<id>     : 0/1 per-bar fire for each of the 31 detection plots
        lvl_<id>      : numeric level per bar (the price/quantity the plot refs)
        sigAny        : 1 if ANY detection fired on the bar
    tf_seconds / grain are accepted for a uniform interface (VOB has no per-TF
    table and no RVOL anchor, so they do not change the math)."""
    if params is None:
        p = Params()
    elif isinstance(params, Params):
        p = params
    else:
        p = _params_from_dict(params)

    o = [b.open for b in bars]
    h = [b.high for b in bars]
    l = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]
    n = len(bars)

    # ── ATR engine (source 267-269) ─────────────────────────────────────────
    atr200 = _atr(o, h, l, c, p.atr_len)
    atr_base = _highest(atr200, p.atr_hi_len)
    atr_prox_arr = [(x * p.atr_proximity_mult) if x is not None else None for x in atr_base]
    atr_adj_arr = [(x * p.atr_adjust_mult) if x is not None else None for x in atr_base]

    # ── per-tier zone engine ─────────────────────────────────────────────────
    tier_out = {}
    for t in TIERS:
        tier_out[t] = _run_tier(o, h, l, c, v, p.sens[t], p,
                                atr_prox_arr, atr_adj_arr)

    cd = p.cooldown_bars

    # ── T3 fires (show_* & t3 & cooldown) ────────────────────────────────────
    fire = {}
    lvl = {}
    for t in TIERS:
        tb = [tier_out[t]["t3_buy"][i] and p.show_t3_buy[t] for i in range(n)]
        tsl = [tier_out[t]["t3_sell"][i] and p.show_t3_sell[t] for i in range(n)]
        fire[f"t3_buy_{t}"] = _cd_gate(tb, cd)
        fire[f"t3_sell_{t}"] = _cd_gate(tsl, cd)
        lvl[f"t3_buy_{t}"] = [c[i] if fire[f"t3_buy_{t}"][i] else None for i in range(n)]
        lvl[f"t3_sell_{t}"] = [c[i] if fire[f"t3_sell_{t}"][i] else None for i in range(n)]

    # ── Nagasaki: volume[1] > maxVolEver (source 720-724) ────────────────────
    sig_nag = [False] * n
    lvl_nag_raw = [None] * n
    maxv = 0.0
    for i in range(n):
        v1 = v[i - 1] if i - 1 >= 0 else None
        if v1 is not None and v1 > maxv:
            maxv = v1
            sig_nag[i] = True
            lvl_nag_raw[i] = v1
    nag = [sig_nag[i] and p.show_nagasaki for i in range(n)]
    fire["nagasaki"] = _cd_gate(nag, cd)
    lvl["nagasaki"] = [lvl_nag_raw[i] if fire["nagasaki"][i] else None for i in range(n)]

    # ── zone-formation fires (en_zone & nz & cooldown) ───────────────────────
    for t in TIERS:
        zb_sig = [tier_out[t]["nzb"][i] and p.en_zone[t] for i in range(n)]
        zs_sig = [tier_out[t]["nzs"][i] and p.en_zone[t] for i in range(n)]
        fire[f"zb_{t}"] = _cd_gate(zb_sig, cd)
        fire[f"zs_{t}"] = _cd_gate(zs_sig, cd)
        zbm = tier_out[t]["zb_mid"]
        zsm = tier_out[t]["zs_mid"]
        lvl[f"zb_{t}"] = [zbm[i] if fire[f"zb_{t}"][i] else None for i in range(n)]
        lvl[f"zs_{t}"] = [zsm[i] if fire[f"zs_{t}"][i] else None for i in range(n)]

    # ── Multi-zone same-candle counts (off the gated fire_zb/zs) ─────────────
    mz_bull_cnt = [sum(fire[f"zb_{t}"][i] for t in TIERS) for i in range(n)]
    mz_bear_cnt = [sum(fire[f"zs_{t}"][i] for t in TIERS) for i in range(n)]
    fire["mz_b2"] = _cd_gate([mz_bull_cnt[i] == 2 and p.show_multi_bull_2 for i in range(n)], cd)
    fire["mz_b3"] = _cd_gate([mz_bull_cnt[i] >= 3 and p.show_multi_bull_3 for i in range(n)], cd)
    fire["mz_s2"] = _cd_gate([mz_bear_cnt[i] == 2 and p.show_multi_bear_2 for i in range(n)], cd)
    fire["mz_s3"] = _cd_gate([mz_bear_cnt[i] >= 3 and p.show_multi_bear_3 for i in range(n)], cd)
    lvl["mz_b2"] = [mz_bull_cnt[i] if fire["mz_b2"][i] else None for i in range(n)]
    lvl["mz_b3"] = [mz_bull_cnt[i] if fire["mz_b3"][i] else None for i in range(n)]
    lvl["mz_s2"] = [mz_bear_cnt[i] if fire["mz_s2"][i] else None for i in range(n)]
    lvl["mz_s3"] = [mz_bear_cnt[i] if fire["mz_s3"][i] else None for i in range(n)]

    # ── VLB strict ladder ────────────────────────────────────────────────────
    vlb_b_complete, vlb_b_mid = _vlb_bull(tier_out, n)
    vlb_r_complete, vlb_r_mid = _vlb_bear(tier_out, n)
    fire["vlb_bull"] = _cd_gate([vlb_b_complete[i] and p.show_vlb_bull for i in range(n)], cd)
    fire["vlb_bear"] = _cd_gate([vlb_r_complete[i] and p.show_vlb_bear for i in range(n)], cd)
    lvl["vlb_bull"] = [vlb_b_mid[i] if fire["vlb_bull"][i] else None for i in range(n)]
    lvl["vlb_bear"] = [vlb_r_mid[i] if fire["vlb_bear"][i] else None for i in range(n)]

    # ── assemble output (fire_<id> + lvl_<id> + sigAny) ──────────────────────
    out = {"ts": ts}
    for pid in PLOT_IDS:
        out[f"fire_{pid}"] = fire[pid]
        out[f"lvl_{pid}"] = lvl[pid]
    out["sigAny"] = [1 if any(out[f"fire_{pid}"][i] for pid in PLOT_IDS) else 0
                     for i in range(n)]
    return out


def _params_from_dict(d: dict) -> Params:
    """Build Params from a plain dict (shallow override of dataclass defaults)."""
    p = Params()
    for k, val in d.items():
        if hasattr(p, k):
            setattr(p, k, val)
    return p


# Convenience: a "fires" view (label -> 0/1 list) matching the Pine plot names,
# for terminals/dashboards that key off the human plot ids.
_LABEL = {f"t3_buy_{t}": f"T3{t} Buy" for t in TIERS}
_LABEL.update({f"t3_sell_{t}": f"T3{t} Sell" for t in TIERS})
_LABEL["nagasaki"] = "Nagasaki"
_LABEL.update({f"zb_{t}": f"ZoneBull {t.upper()}" for t in TIERS})
_LABEL.update({f"zs_{t}": f"ZoneBear {t.upper()}" for t in TIERS})
_LABEL.update({"vlb_bull": "VLB Bull (strict F→A)", "vlb_bear": "VLB Bear (strict F→A)",
               "mz_b2": "Multi-Zone Bull 2", "mz_b3": "Multi-Zone Bull 3+",
               "mz_s2": "Multi-Zone Bear 2", "mz_s3": "Multi-Zone Bear 3+"})


def fires_by_label(out: dict) -> dict:
    return {_LABEL[pid]: out[f"fire_{pid}"] for pid in PLOT_IDS}
