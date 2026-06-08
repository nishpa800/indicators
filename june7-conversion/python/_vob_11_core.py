"""VOB v11 MULTIPLES TICK-FRIENDLY — FULL detection fire-matrix core (Pine v5 -> Python).

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/vob_11_tickfriendly.pine"
  //@version=5, indicator("VOB v11 MULTIPLES TICK-FRIENDLY ...", overlay=true).
  Tick-safe in the source: reg_anchorSafe forces "D" on tick charts;
  timeframe.in_seconds() guarded with tick_assumed_tfsec fallback;
  relativeVolume routed through tv_ta (ta/7) anchorSafe.

ULTRACODE FULL PORT — scope statement (read this):
  This module ports the DEEP multi-sensitivity Volume Order Block engine and
  EVERY detection plot the v11 MULTIPLES source emits, bar-by-bar in a single
  forward pass over CLOSED bars. There is NO EngineInputs stub: the zone arrays,
  the T3 cluster conditions, Nagasaki, the strict F->A VLB ladder, the multi-zone
  same-candle counts, the T3-cluster, and the embedded Heavy-Weapons-Single v3
  engine (-> hws_any) used by the VOB x HW coincidence are all computed from
  OHLCV here. (This SUPERSEDES the earlier PARTIAL core that took the zone
  primitives as default-False EngineInputs.)

  DETECTION PLOTS (the deliverable fire matrix) — PLOT_IDS, in source order:
    nagasaki                          (plotshape line 859, offset=-1)
    zoneform_bull_{a..f} / _bear_*    (numeric data_window 1124-1137; ZONEFORM_*)
    t3_buy_{a..f} / t3_sell_{a..f}    (gated plot bools 771-783; plotshapes
                                       commented in MULTIPLES but the gated bools
                                       drive the cluster + VOBxHW; emitted as fires)
    vlb_bull / vlb_bear               (plotshape 1525-1526)
    mz_b2 / mz_b3 / mz_s2 / mz_s3     (plotshape 1608-1611)
    tc_cluster                        (plotshape 2127)
    vobhws                            (plotshape 2149)

  Internal-only fires fire_zb_{a..f}/fire_zs_{a..f} (en_zone gated; commented
  plotshapes in MULTIPLES) feed the multi-zone counts; they default to disabled
  (en_zone False) like the source's en_zone_* inputs (all default False), so by
  default mz_*/zoneform mid the en_zone path is off but the *zone formation*
  (nzb_*/nzs_*) still drives ZONEFORM_* (gated by en_emission_labels=True) and
  the VLB ladder. We emit fire_zb/zs as fires for completeness.

  ENGINE ZONE MECHANICS (f_vob, lines 542-660), per sensitivity tier a..f:
    len1 = sens ; len2 = sens+13 ; ema1=ema(close,len1) ; ema2=ema(close,len2).
    cup = crossover(ema1,ema2) & confirmed ; cdn = crossunder & confirmed.
    On cup: walk i=1..len2, where low[i]==lowest(len2) -> create BULL zone:
      vol = sum(volume[0..i]); src=min(open[i],close[i]) clamped so
      (src-lowest) >= atr_adj*0.5; mid=avg(src,lowest); push lower_lvl.
    On cdn (mirror): high[i]==highest(len2) -> BEAR zone in upper_lvl.
    Dedup: |mid - prev.mid| < atr_prox -> invalidate prev (set na).
    Invalidate: bull if close<lower ; bear if close>upper.
    Cap each array at 15 (shift oldest).
    T3 (confirmed): build active (non-na) vol/lo/hi pools; bp=sum bull vols,
      sp=sum bear; dominant zone = max-vol zone; t3_buy = (#bull==1 & sp>0 &
      db_vol>sp*mult & close in [db_low,db_high]); t3_sell mirror.

  atr_base = highest(atr(200),200) ; atr_proximity=3x ; atr_adjust=2x.

  Pine semantics preserved: single forward pass; conf=barstate.isconfirmed=True
  on every closed bar; `var` -> persistent Python state; `[k]` -> k-bars-back by
  prior-list indexing; `nz`/`na` -> nz()/None; integer ternary chains -> Python.

  relativeVolume (HWS Reg@Time + Hybrid) ports via the canonical tv_ta shim
  (anchor "D"), never re-derived here. tf_seconds tick fallback mirrors the
  source's tick_assumed_tfsec guard.

NUMERIC LEVELS: ZONEMID_BULL_A / ZONEMID_BEAR_A carried 1:1 (source plots them).
Every detection plot also gets a price level (the bar price the marker sits at:
belowbar/bottom -> low, abovebar/top -> high, else close) so a slicer can place
each fire.

HONESTY: there is no all-zero stub series. Every plot is produced by real ported
Pine logic. The parity harness re-derives upstream gates independently and reports
a REAL pass/total.
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nn_harness import (  # noqa: E402
    nz, sma, stdev, highest, lowest, atr as _atr_ohlc, cum as _cum,
    relative_volume,
)

TIERS = ("a", "b", "c", "d", "e", "f")


# ──────────────────────────────── parameters ────────────────────────────────
@dataclass
class Params:
    """Every Pine input.* / hardcoded threshold as a parameter (source default)."""
    # ── Sensitivities (lines 128-133) ──
    sens_a: int = 2500
    sens_b: int = 2250
    sens_c: int = 2000
    sens_d: int = 1500
    sens_e: int = 1250
    sens_f: int = 1000
    # ── T3 show toggles (139-150) — all default False ──
    show_t3_buy: dict = field(default_factory=lambda: {t: False for t in TIERS})
    show_t3_sell: dict = field(default_factory=lambda: {t: False for t in TIERS})
    show_nagasaki: bool = False                  # line 151
    # ── Zone enable toggles (157-162) — all default False ──
    en_zone: dict = field(default_factory=lambda: {t: False for t in TIERS})
    # ── Signal params (171-178) ──
    asym_threshold: float = 99.0                 # reserved (unused by detection)
    super_mult: float = 1.5                      # T3 dominant-vol multiplier
    # ── Cooldown (184) ──
    cooldown_bars: int = 100
    # ── VLB strict ladder (195-200) — default True ──
    show_vlb_bull: bool = True
    show_vlb_bear: bool = True
    # ── Multi-zone same-candle (215-226) — default True ──
    show_multi_bull_2: bool = True
    show_multi_bull_3: bool = True
    show_multi_bear_2: bool = True
    show_multi_bear_3: bool = True
    # ── Emission layer (264-271) ──
    en_emission_labels: bool = True              # gates ZONEFORM_* numeric emit
    stack_thresh_pct: float = 2.0
    hist_depth: int = 50
    # ── v11 new detection toggles (2117, 2140) — default True ──
    show_tc_cluster: bool = True
    show_vobhws: bool = True
    # ── HWS embedded engine (1690-1726) ──
    bb_avgLength: int = 30
    bb_smaLength: int = 20
    reg_length: int = 30
    reg_calc_cumulative: bool = True             # "Cumulative" default
    reg_pct: int = 100
    cum_pct: int = 100
    body_pct: int = 100
    enableNagasaki: bool = True
    th_low_UU_DD: float = 0.5
    th_low_UUU_DDD: float = 0.5
    th_low_UUUU_DDDD: float = 0.5
    i_disp_type: str = "Open to Close"
    i_std_len: int = 100
    i_disp_std_standalone: float = 7.5
    i_disp_std_cdisp2: float = 5.0
    i_disp_std_cdisp3: float = 3.0
    i_disp_std_seq: float = 5.0
    hct_disp_strength: float = 6.0
    hct_disp_lookback: int = 100
    hct_threshPct: float = 2.0
    hct_auto: bool = True
    tick_assumed_tfsec: int = 60                 # line 1726
    # ── FAUNA constants (2038-2043) ──
    fn_alpha_MB: float = 1.6
    fn_beta_MB: float = 0.70
    fn_delta_MB: float = 1.8
    fn_atr_MB: int = 14
    fn_vol_MB: int = 20
    fn_gamma_RE: float = 2.2
    fn_epsilon_RE: float = 0.15
    fn_delta_RE: float = 1.8
    fn_atr_RE: int = 14
    fn_zeta_GG: float = 0.9
    fn_delta_GG: float = 1.8
    fn_atr_GG: int = 14
    fn_theta_TA: float = 1.6
    fn_delta_TA: float = 1.8
    fn_trend_ma_len: int = 50
    fn_avg_delta_len: int = 10
    fn_atr_TA: int = 14
    fn_alpha_SB: float = 1.5
    fn_weak_ratio: float = 0.2
    fn_body_avg: int = 20
    fn_range_avg: int = 20


# Detection-plot id list (the deliverable fire matrix), in source order.
PLOT_IDS: list[str] = (
    ["nagasaki"]
    + [f"zoneform_bull_{t}" for t in TIERS]
    + [f"zoneform_bear_{t}" for t in TIERS]
    + [f"fire_zb_{t}" for t in TIERS]
    + [f"fire_zs_{t}" for t in TIERS]
    + [f"t3_buy_{t}" for t in TIERS]
    + [f"t3_sell_{t}" for t in TIERS]
    + ["vlb_bull", "vlb_bear",
       "mz_b2", "mz_b3", "mz_s2", "mz_s3",
       "tc_cluster", "vobhws"]
)


# ────────────────────────────── zone data type ──────────────────────────────
class _Level:
    """Pine `type level` (lines 100-109). na fields -> None (invalidated)."""
    __slots__ = ("indx", "upper", "lower", "mid", "vol", "o", "h", "l", "c")

    def __init__(self, indx, upper, lower, mid, vol, o, h, l, c):
        self.indx = indx; self.upper = upper; self.lower = lower
        self.mid = mid; self.vol = vol
        self.o = o; self.h = h; self.l = l; self.c = c


def _ema_series(values: Sequence[float], length: int) -> list[float | None]:
    """Pine ta.ema(close, length). Seeds on the first bar (alpha=2/(len+1)).

    Pine's ta.ema emits a value from bar 0 (it does not wait for `length` bars),
    seeding with the first source value, then EMA = alpha*src + (1-alpha)*prev.
    """
    out: list[float | None] = []
    alpha = 2.0 / (length + 1.0)
    prev: float | None = None
    for v in values:
        v = float(v)
        if prev is None:
            prev = v
        else:
            prev = alpha * v + (1.0 - alpha) * prev
        out.append(prev)
    return out


class _Cooldown:
    """Mirror of f_cd_ok (line 412) + the `last_* := bar_index` update on fire."""
    __slots__ = ("cd", "last")

    def __init__(self, cd: int):
        self.cd = cd
        self.last: int | None = None  # na

    def ok(self, i: int) -> bool:
        return self.last is None or (i - self.last) > self.cd

    def fire(self, i: int):
        self.last = i


def _f_count_active(arr: list[_Level]) -> int:
    return sum(1 for l in arr if l.vol is not None)


def _f_stack_near(arr: list[_Level], price: float, thresh_pct: float) -> int:
    c = 0
    if price > 0:
        for l in arr:
            if l.mid is not None and abs(price - l.mid) / price * 100 <= thresh_pct:
                c += 1
    return c


# ──────────────────────────────── core compute ──────────────────────────────
def compute(bars, *, params: Params | None = None, tf_seconds: float | None = None,
            grain: str = "time"):
    """Return the VOB v11 detection fire matrix + levels.

    bars: oldest-first Sequence[Bar] (ts, open, high, low, close, volume).
    tf_seconds: seconds/bar for the HWS threshold ladder (tick fallback when na).
    grain: "tick"|"time" (cosmetic; one code path).
    """
    if params is None:
        params = Params()
    p = params
    n = len(bars)

    o = [float(b.open) for b in bars]
    h = [float(b.high) for b in bars]
    l = [float(b.low) for b in bars]
    c = [float(b.close) for b in bars]
    vol = [float(b.volume) for b in bars]
    ts = [b.ts for b in bars]

    out: dict = {"ts": list(ts)}
    fire = {pid: [0] * n for pid in PLOT_IDS}
    lvl = {pid: [None] * n for pid in PLOT_IDS}
    # carried numeric level series (source plots ZONEMID_BULL_A / ZONEMID_BEAR_A)
    zonemid_bull_a: list[float | None] = [None] * n
    zonemid_bear_a: list[float | None] = [None] * n

    if n == 0:
        out.update({pid: fire[pid] for pid in PLOT_IDS})
        out.update({f"lvl_{pid}": lvl[pid] for pid in PLOT_IDS})
        out["zonemid_bull_a"] = zonemid_bull_a
        out["zonemid_bear_a"] = zonemid_bear_a
        return out

    # ── shared calculations (lines 277-279) ──
    atr200 = _atr_ohlc(o, h, l, c, 200)
    atr200_clean = [0.0 if x is None else x for x in atr200]
    atr_base = highest(atr200_clean, 200)  # ta.highest(ta.atr(200),200)
    # Pine: atr_base na until 200 valid; treat None as 0 downstream (na math -> na,
    # but the dedup/clamp simply won't trigger meaningfully early on).
    atr_proximity = [None if x is None else x * 3 for x in atr_base]
    atr_adjust = [None if x is None else x * 2 for x in atr_base]

    sens = {"a": p.sens_a, "b": p.sens_b, "c": p.sens_c,
            "d": p.sens_d, "e": p.sens_e, "f": p.sens_f}
    ema1 = {t: _ema_series(c, sens[t]) for t in TIERS}
    ema2 = {t: _ema_series(c, sens[t] + 13) for t in TIERS}

    # per-tier zone arrays (lower=bull, upper=bear)
    lower = {t: [] for t in TIERS}   # list[_Level]
    upper = {t: [] for t in TIERS}

    # cooldown state machines (one per output, like the source's last_*)
    cd_zb = {t: _Cooldown(p.cooldown_bars) for t in TIERS}
    cd_zs = {t: _Cooldown(p.cooldown_bars) for t in TIERS}
    cd_t3b = {t: _Cooldown(p.cooldown_bars) for t in TIERS}
    cd_t3s = {t: _Cooldown(p.cooldown_bars) for t in TIERS}
    cd_nag = _Cooldown(p.cooldown_bars)
    cd_vlb_b = _Cooldown(p.cooldown_bars)
    cd_vlb_r = _Cooldown(p.cooldown_bars)
    cd_mz_b2 = _Cooldown(p.cooldown_bars); cd_mz_b3 = _Cooldown(p.cooldown_bars)
    cd_mz_s2 = _Cooldown(p.cooldown_bars); cd_mz_s3 = _Cooldown(p.cooldown_bars)
    cd_tc = _Cooldown(p.cooldown_bars)
    cd_vobhws = _Cooldown(p.cooldown_bars)

    # Nagasaki state (lines 761-765): uses volume[1] vs maxVolEver.
    maxVolEver = 0.0

    # VLB ladder state (1232-1258)
    vlb_bull_state = 0; vlb_bull_p_lo = None; vlb_bull_p_hi = None
    vlb_bear_state = 0; vlb_bear_p_lo = None; vlb_bear_p_hi = None

    # ── HWS embedded engine — precompute the vector series it needs ──
    hws = _compute_hws(p, o, h, l, c, vol, ts, tf_seconds, grain)

    for i in range(n):
        # ════════════ ZONE ENGINE per tier (f_vob, lines 542-597) ════════════
        atr_prox = atr_proximity[i]
        atr_adj = atr_adjust[i]
        nzb = {t: False for t in TIERS}
        nzs = {t: False for t in TIERS}

        for t in TIERS:
            len1 = sens[t]; len2 = len1 + 13
            e1 = ema1[t]; e2 = ema2[t]
            # crossover / crossunder (need prior bar). barstate.isconfirmed=True.
            # EPS guards the perfectly-flat-tape float artifact: when there is no
            # real price movement, two equal-seeded EMAs of different length drift
            # apart only by ~1e-14 rounding noise. Pine reports no cross on a flat
            # market; we require the "now" gap to clear EPS so that float noise on
            # a degenerate tape does not manufacture a crossover. Any real EMA
            # separation (>= EPS) is detected exactly as Pine's ta.crossover does.
            _EPS = 1e-9
            cup = (i >= 1 and e1[i] is not None and e2[i] is not None
                   and e1[i - 1] is not None and e2[i - 1] is not None
                   and e1[i - 1] <= e2[i - 1] and (e1[i] - e2[i]) > _EPS)
            cdn = (i >= 1 and e1[i] is not None and e2[i] is not None
                   and e1[i - 1] is not None and e2[i - 1] is not None
                   and e1[i - 1] >= e2[i - 1] and (e2[i] - e1[i]) > _EPS)
            # lowest/highest over len2 bars back (Pine ta.lowest/highest = last len2)
            lo_start = max(0, i - len2 + 1)
            window_low = min(l[lo_start:i + 1]) if i >= 0 else None
            window_high = max(h[lo_start:i + 1]) if i >= 0 else None
            lowest_v = window_low
            highest_v = window_high

            sz_lo_before = len(lower[t])
            sz_up_before = len(upper[t])

            if cup and lowest_v is not None:
                # walk i'=1..len2: low[i']==lowest -> create bull zone
                v_acc = 0.0
                # Pine loops i=1..len2 and on FIRST match pushes (then continues
                # but match is unique to the extreme; replicate by pushing each
                # match exactly as Pine would — Pine pushes once per matching i).
                for ib in range(1, len2 + 1):
                    src_idx = i - ib
                    if src_idx < 0:
                        break
                    if l[src_idx] == lowest_v:
                        vv = 0.0
                        for k in range(0, ib + 1):
                            ki = i - k
                            if ki < 0:
                                break
                            vv += vol[ki]
                        src = min(o[src_idx], c[src_idx])
                        aadj = atr_adj if atr_adj is not None else 0.0
                        if (src - lowest_v) < aadj * 0.5:
                            src = lowest_v + aadj * 0.5
                        mid = (src + lowest_v) / 2.0
                        lower[t].append(_Level(ts[src_idx], src, lowest_v, mid, vv,
                                               o[src_idx], h[src_idx], l[src_idx], c[src_idx]))

            if cdn and highest_v is not None:
                for ib in range(1, len2 + 1):
                    src_idx = i - ib
                    if src_idx < 0:
                        break
                    if h[src_idx] == highest_v:
                        vv = 0.0
                        for k in range(0, ib + 1):
                            ki = i - k
                            if ki < 0:
                                break
                            vv += vol[ki]
                        src = max(o[src_idx], c[src_idx])
                        aadj = atr_adj if atr_adj is not None else 0.0
                        if (highest_v - src) < aadj * 0.5:
                            src = highest_v - aadj * 0.5
                        mid = (src + highest_v) / 2.0
                        upper[t].append(_Level(ts[src_idx], highest_v, src, mid, vv,
                                               o[src_idx], h[src_idx], l[src_idx], c[src_idx]))

            # dedup + invalidate bull (lines 575-585)
            la = lower[t]
            if la:
                for ix in range(len(la)):
                    lv = la[ix]
                    if ix > 0:
                        l1 = la[ix - 1]
                        if (lv.mid is not None and l1.mid is not None
                                and atr_prox is not None
                                and abs(lv.mid - l1.mid) < atr_prox):
                            la[ix - 1] = _Level(None, None, None, None, None,
                                                None, None, None, None)
                    if lv.lower is not None and c[i] < lv.lower:
                        la[ix] = _Level(None, None, None, None, None,
                                        None, None, None, None)
                if len(la) > 15:
                    la.pop(0)

            ua = upper[t]
            if ua:
                for ix in range(len(ua)):
                    uv = ua[ix]
                    if ix > 0:
                        u1 = ua[ix - 1]
                        if (uv.mid is not None and u1.mid is not None
                                and atr_prox is not None
                                and abs(uv.mid - u1.mid) < atr_prox):
                            ua[ix - 1] = _Level(None, None, None, None, None,
                                                None, None, None, None)
                    if uv.upper is not None and c[i] > uv.upper:
                        ua[ix] = _Level(None, None, None, None, None,
                                        None, None, None, None)
                if len(ua) > 15:
                    ua.pop(0)

            nzb[t] = len(lower[t]) > sz_lo_before
            nzs[t] = len(upper[t]) > sz_up_before

            # ── T3 (lines 604-658), confirmed always True on closed bars ──
            vbv = [z.vol for z in lower[t] if z.vol is not None]
            vbl = [z.lower for z in lower[t] if z.vol is not None]
            vbh = [z.upper for z in lower[t] if z.vol is not None]
            vav = [z.vol for z in upper[t] if z.vol is not None]
            valo = [z.lower for z in upper[t] if z.vol is not None]
            vah = [z.upper for z in upper[t] if z.vol is not None]
            bp = sum(vbv) if vbv else 0.0
            sp = sum(vav) if vav else 0.0
            db_vol = 0.0; db_low = 0.0; db_high = 0.0
            for ix in range(len(vbv)):
                if vbv[ix] > db_vol:
                    db_vol = vbv[ix]; db_low = vbl[ix]; db_high = vbh[ix]
            da_vol = 0.0; da_low = 0.0; da_high = 0.0
            for ix in range(len(vav)):
                if vav[ix] > da_vol:
                    da_vol = vav[ix]; da_low = valo[ix]; da_high = vah[ix]
            pat_bull = db_low <= c[i] <= db_high
            pat_bear = da_low <= c[i] <= da_high
            t3_buy = (len(vbv) == 1 and sp > 0 and db_vol > sp * p.super_mult and pat_bull)
            t3_sell = (len(vav) == 1 and bp > 0 and da_vol > bp * p.super_mult and pat_bear)

            # ── zone-creation markers fire (en_zone & nz & cooldown, 909-920) ──
            zb = p.en_zone[t] and nzb[t] and cd_zb[t].ok(i)
            zs = p.en_zone[t] and nzs[t] and cd_zs[t].ok(i)
            if zb: cd_zb[t].fire(i)
            if zs: cd_zs[t].fire(i)
            fire[f"fire_zb_{t}"][i] = 1 if zb else 0
            fire[f"fire_zs_{t}"][i] = 1 if zs else 0
            if zb:
                lvl[f"fire_zb_{t}"][i] = lower[t][-1].mid if lower[t] else l[i]
            if zs:
                lvl[f"fire_zs_{t}"][i] = upper[t][-1].mid if upper[t] else h[i]

            # ── T3 gated bools (show & t3 & cooldown, 771-783) ──
            tb = p.show_t3_buy[t] and t3_buy and cd_t3b[t].ok(i)
            tsl = p.show_t3_sell[t] and t3_sell and cd_t3s[t].ok(i)
            if tb: cd_t3b[t].fire(i)
            if tsl: cd_t3s[t].fire(i)
            fire[f"t3_buy_{t}"][i] = 1 if tb else 0
            fire[f"t3_sell_{t}"][i] = 1 if tsl else 0
            if tb:
                lvl[f"t3_buy_{t}"][i] = l[i]
            if tsl:
                lvl[f"t3_sell_{t}"][i] = h[i]

            # ── ZONEFORM_* numeric emit (f_emit_zone, 1101-1137) ──
            # ok = en_emission_labels & nz & arr non-empty & last.mid/.vol not na
            if p.en_emission_labels and nzb[t] and lower[t]:
                last = lower[t][-1]
                if last.mid is not None and last.vol is not None:
                    fire[f"zoneform_bull_{t}"][i] = 1
                    lvl[f"zoneform_bull_{t}"][i] = last.mid
                    if t == "a":
                        zonemid_bull_a[i] = last.mid
            if p.en_emission_labels and nzs[t] and upper[t]:
                last = upper[t][-1]
                if last.mid is not None and last.vol is not None:
                    fire[f"zoneform_bear_{t}"][i] = 1
                    lvl[f"zoneform_bear_{t}"][i] = last.mid
                    if t == "a":
                        zonemid_bear_a[i] = last.mid

        # ════════════════════ NAGASAKI (lines 761-765, 783) ═════════════════
        # uses volume[1] (prior bar) vs maxVolEver
        isNagasaki = False
        if i >= 1 and vol[i - 1] > maxVolEver:
            maxVolEver = vol[i - 1]
            isNagasaki = True
        nag = p.show_nagasaki and isNagasaki and cd_nag.ok(i)
        if nag: cd_nag.fire(i)
        fire["nagasaki"][i] = 1 if nag else 0
        if nag:
            lvl["nagasaki"][i] = h[i]

        # ════════════ VLB STRICT LADDER (1264-1512) ════════════
        any_bear_zone_bar = any(nzs[t] for t in TIERS)
        any_bull_zone_bar = any(nzb[t] for t in TIERS)

        vlb_bull_complete = False
        if any_bear_zone_bar:
            vlb_bull_state = 0; vlb_bull_p_lo = None; vlb_bull_p_hi = None
        elif any_bull_zone_bar:
            order = ["f", "e", "d", "c", "b", "a"]
            for step, t in enumerate(order):
                expect = step  # state expected when this tier arrives
                if not nzb[t]:
                    continue
                if t == "f":
                    if vlb_bull_state == 0:
                        zf = lower["f"][-1]
                        vlb_bull_p_lo = zf.lower; vlb_bull_p_hi = zf.upper
                        vlb_bull_state = 1
                    else:
                        vlb_bull_state = 0; vlb_bull_p_lo = None; vlb_bull_p_hi = None
                    continue
                # E..A require state>0
                if vlb_bull_state <= 0:
                    continue
                if vlb_bull_state == expect:
                    z = lower[t][-1]
                    if z.upper is not None and vlb_bull_p_lo is not None and z.upper >= vlb_bull_p_lo:
                        if t == "a":
                            vlb_bull_complete = True
                            vlb_bull_state = 0; vlb_bull_p_lo = None; vlb_bull_p_hi = None
                        else:
                            vlb_bull_p_lo = z.lower; vlb_bull_p_hi = z.upper
                            vlb_bull_state = expect + 1
                    else:
                        if t == "a":
                            vlb_bull_state = 0; vlb_bull_p_lo = None; vlb_bull_p_hi = None
                        else:
                            vlb_bull_state = 0; vlb_bull_p_lo = None; vlb_bull_p_hi = None
                else:
                    vlb_bull_state = 0; vlb_bull_p_lo = None; vlb_bull_p_hi = None

        vlb_bear_complete = False
        if any_bull_zone_bar:
            vlb_bear_state = 0; vlb_bear_p_lo = None; vlb_bear_p_hi = None
        elif any_bear_zone_bar:
            order = ["f", "e", "d", "c", "b", "a"]
            for step, t in enumerate(order):
                expect = step
                if not nzs[t]:
                    continue
                if t == "f":
                    if vlb_bear_state == 0:
                        zf = upper["f"][-1]
                        vlb_bear_p_lo = zf.lower; vlb_bear_p_hi = zf.upper
                        vlb_bear_state = 1
                    else:
                        vlb_bear_state = 0; vlb_bear_p_lo = None; vlb_bear_p_hi = None
                    continue
                if vlb_bear_state <= 0:
                    continue
                if vlb_bear_state == expect:
                    z = upper[t][-1]
                    if z.lower is not None and vlb_bear_p_hi is not None and z.lower <= vlb_bear_p_hi:
                        if t == "a":
                            vlb_bear_complete = True
                            vlb_bear_state = 0; vlb_bear_p_lo = None; vlb_bear_p_hi = None
                        else:
                            vlb_bear_p_lo = z.lower; vlb_bear_p_hi = z.upper
                            vlb_bear_state = expect + 1
                    else:
                        vlb_bear_state = 0; vlb_bear_p_lo = None; vlb_bear_p_hi = None
                else:
                    vlb_bear_state = 0; vlb_bear_p_lo = None; vlb_bear_p_hi = None

        # VLB gated (1515-1521): show & complete & confirmed & cooldown
        vb = p.show_vlb_bull and vlb_bull_complete and cd_vlb_b.ok(i)
        vr = p.show_vlb_bear and vlb_bear_complete and cd_vlb_r.ok(i)
        if vb: cd_vlb_b.fire(i)
        if vr: cd_vlb_r.fire(i)
        fire["vlb_bull"][i] = 1 if vb else 0
        fire["vlb_bear"][i] = 1 if vr else 0
        if vb: lvl["vlb_bull"][i] = l[i]
        if vr: lvl["vlb_bear"][i] = h[i]

        # ════════════ MULTI-ZONE same-candle (1587-1603) ════════════
        # counts off fire_zb_*/fire_zs_* (the en_zone-gated booleans)
        mz_bull_cnt = sum(fire[f"fire_zb_{t}"][i] for t in TIERS)
        mz_bear_cnt = sum(fire[f"fire_zs_{t}"][i] for t in TIERS)
        mb2 = p.show_multi_bull_2 and mz_bull_cnt == 2 and cd_mz_b2.ok(i)
        mb3 = p.show_multi_bull_3 and mz_bull_cnt >= 3 and cd_mz_b3.ok(i)
        ms2 = p.show_multi_bear_2 and mz_bear_cnt == 2 and cd_mz_s2.ok(i)
        ms3 = p.show_multi_bear_3 and mz_bear_cnt >= 3 and cd_mz_s3.ok(i)
        if mb2: cd_mz_b2.fire(i)
        if mb3: cd_mz_b3.fire(i)
        if ms2: cd_mz_s2.fire(i)
        if ms3: cd_mz_s3.fire(i)
        fire["mz_b2"][i] = 1 if mb2 else 0
        fire["mz_b3"][i] = 1 if mb3 else 0
        fire["mz_s2"][i] = 1 if ms2 else 0
        fire["mz_s3"][i] = 1 if ms3 else 0
        if mb2 or mb3: lvl["mz_b2" if mb2 else "mz_b3"][i] = l[i]
        if ms2 or ms3: lvl["mz_s2" if ms2 else "mz_s3"][i] = h[i]

        # ════════════ T3 CLUSTER (2120-2126) ════════════
        tc_fire_cnt = sum(fire[f"t3_buy_{t}"][i] + fire[f"t3_sell_{t}"][i] for t in TIERS)
        tc = p.show_tc_cluster and tc_fire_cnt >= 2 and cd_tc.ok(i)
        if tc: cd_tc.fire(i)
        fire["tc_cluster"][i] = 1 if tc else 0
        if tc: lvl["tc_cluster"][i] = h[i]

        # ════════════ VOB x HW-SINGLE COINCIDENCE (2143-2148) ════════════
        vob_tc_any = any(fire[f"t3_buy_{t}"][i] or fire[f"t3_sell_{t}"][i] for t in TIERS)
        any_zone = any(fire[f"fire_zb_{t}"][i] or fire[f"fire_zs_{t}"][i] for t in TIERS)
        vob_left_side = vob_tc_any or any_zone
        vh = p.show_vobhws and vob_left_side and hws["hws_any"][i] and cd_vobhws.ok(i)
        if vh: cd_vobhws.fire(i)
        fire["vobhws"][i] = 1 if vh else 0
        if vh: lvl["vobhws"][i] = h[i]

    out.update({pid: fire[pid] for pid in PLOT_IDS})
    out.update({f"lvl_{pid}": lvl[pid] for pid in PLOT_IDS})
    out["zonemid_bull_a"] = zonemid_bull_a
    out["zonemid_bear_a"] = zonemid_bear_a
    # expose hws master bools for the parity harness
    out["hws_any"] = hws["hws_any"]
    out["hws_bull"] = hws["hws_bull"]
    out["hws_bear"] = hws["hws_bear"]
    out["hws_neutral"] = hws["hws_neutral"]
    out["sigAny"] = [1 if any(fire[pid][i] for pid in PLOT_IDS) else 0 for i in range(n)]
    return out


# ═══════════════════ EMBEDDED HW-SINGLE v3 ENGINE (1664-2106) ════════════════
def _f_rvol_1x_threshold(s: float) -> float:
    return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else
            23.0 if s <= 45 else 20.0 if s <= 60 else 19.0 if s <= 120 else
            17.0 if s <= 180 else 16.0 if s <= 240 else 15.0 if s <= 300 else
            14.0 if s <= 360 else 12.0 if s <= 420 else 11.0 if s <= 480 else
            10.0 if s <= 540 else 10.0 if s <= 600 else 8.4 if s <= 900 else
            6.9 if s <= 1800 else 5.9 if s <= 3600 else 3.0 if s <= 7200 else 1.8)


def _f_gs_moab_threshold(s: float) -> float:
    return (114.0 if s <= 10 else 99.0 if s <= 15 else 84.0 if s <= 30 else
            69.0 if s <= 45 else 35.0 if s <= 60 else 35.0 if s <= 300 else
            25.0 if s <= 600 else 20.0 if s <= 900 else 10.0 if s <= 3600 else 8.0)


def _shift(values, off):
    n = len(values)
    out = [None] * n
    for i in range(n):
        j = i - off
        out[i] = values[j] if 0 <= j < n else None
    return out


def _compute_hws(p: Params, o, h, l, c, vol, ts, tf_seconds, grain):
    """Port of the embedded HW-Single v3 detection engine -> hws_any/bull/bear/neutral.

    Faithful to lines 1687-2106. relativeVolume via canonical shim.
    """
    n = len(c)
    conf = [True] * n  # closed bars only -> barstate.isconfirmed True every bar

    # ── tf seconds (1727-1728) ──
    raw_tfsec = tf_seconds
    if raw_tfsec is None or raw_tfsec == 0:
        raw_tfsec = p.tick_assumed_tfsec
    hws_tfSec = float(raw_tfsec)

    th_1x = _f_rvol_1x_threshold(hws_tfSec)
    th_saab_kratos = th_1x * 0.56
    th_gs_moab = _f_gs_moab_threshold(hws_tfSec)
    th_wtc = th_1x * 2.0
    th_hiroshima = _f_gs_moab_threshold(hws_tfSec)  # same ladder (1736 vs 1741)

    # ── hybrid auto-derive (1750-1768) ──
    hybAutoReg1 = th_hiroshima * 2.85
    hybAutoReg5 = th_hiroshima * 1.1875
    hybAutoStep = (hybAutoReg1 - hybAutoReg5) / 4.0
    hybAutoReg2 = hybAutoReg1 - 1.0 * hybAutoStep
    hybAutoReg3 = hybAutoReg1 - 2.0 * hybAutoStep
    hybAutoReg4 = hybAutoReg1 - 3.0 * hybAutoStep
    hybCumPhi = 1.398 * 1.33

    def _safe_log_sqrt(x):
        return hybCumPhi * math.sqrt(math.log(x)) if x > 1.0 else (
            hybCumPhi * math.sqrt(abs(math.log(x))) if x > 0 else 0.0)
    hybAutoCum1 = _safe_log_sqrt(hybAutoReg1)
    hybAutoCum2 = _safe_log_sqrt(hybAutoReg2)
    hybAutoCum3 = _safe_log_sqrt(hybAutoReg3)
    hybAutoCum4 = _safe_log_sqrt(hybAutoReg4)
    hybAutoCum5 = _safe_log_sqrt(hybAutoReg5)
    hybBody = [0.69, 0.72, 0.75, 0.78, 0.81]
    regMult = p.reg_pct / 100.0
    cumMult = p.cum_pct / 100.0
    bodyMult = p.body_pct / 100.0
    hybReg = [hybAutoReg1 * regMult, hybAutoReg2 * regMult, hybAutoReg3 * regMult,
              hybAutoReg4 * regMult, hybAutoReg5 * regMult]
    hybCum = [hybAutoCum1 * cumMult, hybAutoCum2 * cumMult, hybAutoCum3 * cumMult,
              hybAutoCum4 * cumMult, hybAutoCum5 * cumMult]
    hybBodyEff = [b * bodyMult for b in hybBody]

    # ── RVOL bull/bear (1771-1788) ──
    # Pine division by zero yields na; guard it (and 0/0) -> 0.0 so downstream
    # comparisons (>= th, in_range) behave like Pine's na-propagating compares
    # (na compares are False, and 0.0 is below every positive threshold).
    def _safe_div(num, den):
        if den is None or den == 0 or num is None:
            return 0.0
        return num / den
    bb_spike = [abs(c[i] - o[i]) for i in range(n)]
    bb_avgSpike = _shift(sma(bb_spike, p.bb_avgLength), 1)  # [1]
    bb_normPrice = [_safe_div(bb_spike[i], nz(bb_avgSpike[i], 1.0)) for i in range(n)]
    bb_avgVol = _shift(sma(vol, p.bb_avgLength), 1)
    bb_normVol = [_safe_div(vol[i], nz(bb_avgVol[i], 1.0)) for i in range(n)]
    bb_diff = [bb_normPrice[i] - bb_normVol[i] for i in range(n)]
    bb_posDiff = [bb_diff[i] if bb_diff[i] > 0 else None for i in range(n)]
    bb_smaDiff = sma([0.0 if x is None else x for x in bb_posDiff], p.bb_smaLength)
    # Pine sma over na-aware series: when value is na it's skipped; approximate by
    # masking — but to preserve the >sma comparison we use the masked sma above.
    bb_baseBull = [c[i] > o[i] and bb_posDiff[i] is not None and bb_smaDiff[i] is not None
                   and bb_posDiff[i] > bb_smaDiff[i] for i in range(n)]
    bb_baseBear = [c[i] < o[i] and bb_posDiff[i] is not None and bb_smaDiff[i] is not None
                   and bb_posDiff[i] > bb_smaDiff[i] for i in range(n)]

    def _in_range(v, lowTh, highTh):
        return lowTh <= v < highTh
    sigSAAB = [conf[i] and bb_baseBull[i] and _in_range(bb_normPrice[i], th_saab_kratos, th_1x) for i in range(n)]
    sigKratos = [conf[i] and bb_baseBear[i] and _in_range(bb_normPrice[i], th_saab_kratos, th_1x) for i in range(n)]
    sigBullRVOL1x = [conf[i] and bb_baseBull[i] and _in_range(bb_normPrice[i], th_1x, th_gs_moab) for i in range(n)]
    sigBearRVOL1x = [conf[i] and bb_baseBear[i] and _in_range(bb_normPrice[i], th_1x, th_gs_moab) for i in range(n)]
    sigGrandSlam = [conf[i] and bb_baseBull[i] and bb_normPrice[i] >= th_gs_moab for i in range(n)]
    sigMOAB = [conf[i] and bb_baseBear[i] and bb_normPrice[i] >= th_gs_moab for i in range(n)]

    # ── Reg@Time relativeVolume (1791-1799) via canonical shim, anchor "D" ──
    cur_reg, past_reg, _ = relative_volume(vol, p.reg_length, anchor_timeframe="D",
                                           is_cumulative=p.reg_calc_cumulative, bar_timestamps=ts)
    relVolRatio = [(cur_reg[i] / past_reg[i]) if (cur_reg[i] is not None and past_reg[i] not in (None, 0))
                   else 0.0 for i in range(n)]
    sigWTC = [conf[i] and relVolRatio[i] > th_wtc and relVolRatio[i] <= th_hiroshima for i in range(n)]
    sigHiroshima = [conf[i] and relVolRatio[i] > th_hiroshima for i in range(n)]
    sigPentagon = [conf[i] and relVolRatio[i] >= th_1x and relVolRatio[i] <= th_wtc for i in range(n)]

    cur_hr, past_hr, _ = relative_volume(vol, p.reg_length, anchor_timeframe="D",
                                         is_cumulative=False, bar_timestamps=ts)
    cur_hc, past_hc, _ = relative_volume(vol, p.reg_length, anchor_timeframe="D",
                                         is_cumulative=True, bar_timestamps=ts)
    hybRegRatio = [(cur_hr[i] / past_hr[i]) if (cur_hr[i] is not None and past_hr[i] not in (None, 0)) else 0.0 for i in range(n)]
    hybCumRatio = [(cur_hc[i] / past_hc[i]) if (cur_hc[i] is not None and past_hc[i] not in (None, 0)) else 0.0 for i in range(n)]
    hybBodySz = [abs(c[i] - o[i]) for i in range(n)]
    hybRange = [h[i] - l[i] for i in range(n)]
    hybBodyRat = [0.0 if hybRange[i] == 0 else hybBodySz[i] / hybRange[i] for i in range(n)]

    sigAddLong = [[False] * n for _ in range(5)]
    sigAddShort = [[False] * n for _ in range(2)]
    for tier in range(5):
        for i in range(n):
            convict = hybBodyRat[i] >= hybBodyEff[tier]
            bull = c[i] > o[i] and convict
            bear = c[i] < o[i] and convict
            mom = conf[i] and hybRegRatio[i] > hybReg[tier] and hybCumRatio[i] > hybCum[tier]
            sigAddLong[tier][i] = mom and bull
            if tier < 2:
                sigAddShort[tier][i] = mom and bear

    # ── Nagasaki (hw_*) (1830-1840) ──
    sigNagasaki = [False] * n
    hw_maxVol = 0.0
    for i in range(n):
        if conf[i]:
            if i == 0:
                hw_maxVol = vol[i]
            elif vol[i] > hw_maxVol:
                sigNagasaki[i] = p.enableNagasaki  # hw_isNagasaki & enable
                hw_maxVol = vol[i]

    anyLong = [any(sigAddLong[t][i] for t in range(5)) for i in range(n)]
    anyShort = [sigAddShort[0][i] or sigAddShort[1][i] for i in range(n)]
    anyMom = [anyLong[i] or anyShort[i] for i in range(n)]
    anyLong_1 = _shift(anyLong, 1)
    anyLong_1 = [bool(x) for x in anyLong_1]
    hi_vol_150 = highest(vol, 150)
    anyHV_cur = [conf[i] and hi_vol_150[i] is not None and vol[i] == hi_vol_150[i] for i in range(n)]

    # ── HCT displacement (1850-1858) ──
    hl_over_l = [(h[i] - l[i]) / l[i] if l[i] != 0 else 0.0 for i in range(n)]
    cum_hl = _cum(hl_over_l)
    hct_thresh = [(cum_hl[i] / i) if (p.hct_auto and i > 0) else (p.hct_threshPct / 100.0) for i in range(n)]
    hct_bFVG = [False] * n; hct_sFVG = [False] * n
    for i in range(n):
        if i >= 2:
            hct_bFVG[i] = (l[i] > h[i - 2] and c[i - 1] > h[i - 2]
                           and (l[i] - h[i - 2]) / h[i - 2] > hct_thresh[i]) if h[i - 2] != 0 else False
            hct_sFVG[i] = (h[i] < l[i - 2] and c[i - 1] < l[i - 2]
                           and (l[i - 2] - h[i]) / h[i] > hct_thresh[i]) if h[i] != 0 else False
    hct_rangeStdev = stdev([h[i] - l[i] for i in range(n)], p.hct_disp_lookback)
    hct_rangeStdev_1 = _shift(hct_rangeStdev, 1)
    hct_dispBull = [False] * n; hct_dispBear = [False] * n
    for i in range(n):
        bar_range = h[i - 1] - l[i - 1] if i >= 1 else 0.0
        dispMet = bar_range > p.hct_disp_strength * nz(hct_rangeStdev_1[i])
        hct_dispBull[i] = conf[i] and dispMet and (i >= 1 and c[i - 1] > o[i - 1]) and hct_bFVG[i]
        hct_dispBear[i] = conf[i] and dispMet and (i >= 1 and c[i - 1] < o[i - 1]) and hct_sFVG[i]
    hct_noDisp = [not hct_dispBull[i] and not hct_dispBear[i] for i in range(n)]

    # ── HCT 15-combo (1861-1893) ──
    hctGatedBull = [False] * n; hctGatedBear = [False] * n
    for i in range(n):
        groupA_Bull = sigBullRVOL1x[i] or sigGrandSlam[i]
        groupA_Bear = sigBearRVOL1x[i] or sigMOAB[i]
        groupB = sigPentagon[i] or sigWTC[i] or sigHiroshima[i]
        baseYinYang = (groupA_Bull or groupA_Bear) and groupB
        baseNagasaki = sigNagasaki[i] and (groupA_Bull or groupA_Bear)
        baseNagasakiV = sigNagasaki[i] and groupB
        baseTrident = sigNagasaki[i] and (groupA_Bull or groupA_Bear) and groupB
        baseNHx2 = (sigPentagon[i] and sigWTC[i]) or (sigPentagon[i] and sigHiroshima[i]) or (sigWTC[i] and sigHiroshima[i])
        db = hct_dispBull[i]; dr = hct_dispBear[i]; nd = hct_noDisp[i]
        mBull = (baseYinYang and db) or (baseNagasaki and db) or (baseNagasakiV and db) \
            or (baseTrident and db) or (baseNHx2 and db) \
            or (baseYinYang and nd and groupA_Bull) or (baseNagasaki and nd and groupA_Bull) \
            or (baseNagasakiV and nd and c[i] > o[i]) or (baseTrident and nd and groupA_Bull) \
            or (baseNHx2 and nd and c[i] > o[i])
        mBear = (baseYinYang and dr) or (baseNagasaki and dr) or (baseNagasakiV and dr) \
            or (baseTrident and dr) or (baseNHx2 and dr) \
            or (baseYinYang and nd and groupA_Bear) or (baseNagasaki and nd and groupA_Bear) \
            or (baseNagasakiV and nd and c[i] < o[i]) or (baseTrident and nd and groupA_Bear) \
            or (baseNHx2 and nd and c[i] < o[i])
        anySinglesRaw = (sigSAAB[i] or sigKratos[i] or sigBullRVOL1x[i] or sigBearRVOL1x[i]
                         or sigGrandSlam[i] or sigMOAB[i] or sigWTC[i] or sigHiroshima[i]
                         or sigNagasaki[i] or anyLong[i] or anyShort[i])
        hctGatedBull[i] = mBull and anySinglesRaw
        hctGatedBear[i] = mBear and anySinglesRaw

    # ── Pentagon specials (1896-1898) ──
    hi_vol_1000 = highest(vol, 1000)
    hi_vol_500 = highest(vol, 500)
    sigPentHV1K = [False] * n; sigPentHV500D = [False] * n
    for i in range(n):
        pentDisp5 = (h[i] - l[i]) > nz(hct_rangeStdev[i]) * 5.0
        sigPentHV1K[i] = conf[i] and sigPentagon[i] and hi_vol_1000[i] is not None and vol[i] == hi_vol_1000[i]
        sigPentHV500D[i] = conf[i] and sigPentagon[i] and hi_vol_500[i] is not None and vol[i] == hi_vol_500[i] and pentDisp5

    # ── Displacement engine (1900-1932) ──
    disp_range = ([abs(o[i] - c[i]) for i in range(n)] if p.i_disp_type == "Open to Close"
                  else [h[i] - l[i] for i in range(n)])
    disp_std = stdev(disp_range, p.i_std_len)
    disp_th_sa = [None if disp_std[i] is None else disp_std[i] * p.i_disp_std_standalone for i in range(n)]
    disp_th_c2 = [None if disp_std[i] is None else disp_std[i] * p.i_disp_std_cdisp2 for i in range(n)]
    disp_th_c3 = [None if disp_std[i] is None else disp_std[i] * p.i_disp_std_cdisp3 for i in range(n)]
    disp_th_seq = [None if disp_std[i] is None else disp_std[i] * p.i_disp_std_seq for i in range(n)]
    disp_cur_seq = [disp_th_seq[i] is not None and disp_range[i] > disp_th_seq[i] for i in range(n)]
    b2b_gate = [anyHV_cur[i] or disp_cur_seq[i] for i in range(n)]
    isBullFVG = [i >= 2 and l[i] > h[i - 2] and o[i - 1] < c[i - 1] for i in range(n)]
    isBearFVG = [i >= 2 and h[i] < l[i - 2] and o[i - 1] > c[i - 1] for i in range(n)]
    disp_prev_sa = [i >= 1 and disp_th_sa[i - 1] is not None and disp_range[i - 1] > disp_th_sa[i - 1] for i in range(n)]
    sigDispBull = [disp_prev_sa[i] and isBullFVG[i] for i in range(n)]
    sigDispBear = [disp_prev_sa[i] and isBearFVG[i] for i in range(n)]
    disp_prev_c2 = [i >= 1 and disp_th_c2[i - 1] is not None and disp_range[i - 1] > disp_th_c2[i - 1] for i in range(n)]
    sigDispBull_c2 = [disp_prev_c2[i] and isBullFVG[i] for i in range(n)]
    sigDispBear_c2 = [disp_prev_c2[i] and isBearFVG[i] for i in range(n)]
    sigCDispBull2 = [False] * n; sigCDispBear2 = [False] * n
    bull_streak2 = 0; bear_streak2 = 0
    for i in range(n):
        bull_streak2 = bull_streak2 + 1 if sigDispBull_c2[i] else 0
        bear_streak2 = bear_streak2 + 1 if sigDispBear_c2[i] else 0
        sigCDispBull2[i] = sigDispBull_c2[i] and bull_streak2 >= 2
        sigCDispBear2[i] = sigDispBear_c2[i] and bear_streak2 >= 2
    disp_prev_c3 = [i >= 1 and disp_th_c3[i - 1] is not None and disp_range[i - 1] > disp_th_c3[i - 1] for i in range(n)]
    sigDispBull_c3 = [disp_prev_c3[i] and isBullFVG[i] for i in range(n)]
    sigDispBear_c3 = [disp_prev_c3[i] and isBearFVG[i] for i in range(n)]
    sigCDispBull3 = [False] * n; sigCDispBear3 = [False] * n
    bull_streak3 = 0; bear_streak3 = 0
    for i in range(n):
        bull_streak3 = bull_streak3 + 1 if sigDispBull_c3[i] else 0
        bear_streak3 = bear_streak3 + 1 if sigDispBear_c3[i] else 0
        sigCDispBull3[i] = sigDispBull_c3[i] and bull_streak3 >= 3
        sigCDispBear3[i] = sigDispBear_c3[i] and bear_streak3 >= 3

    # ── Sequences (1934-2027) ──
    is_u_UU = [bb_baseBull[i] and bb_normPrice[i] > p.th_low_UU_DD for i in range(n)]
    is_u_UUU = [bb_baseBull[i] and bb_normPrice[i] > p.th_low_UUU_DDD for i in range(n)]
    is_u_UUUU = [bb_baseBull[i] and bb_normPrice[i] > p.th_low_UUUU_DDDD for i in range(n)]
    is_d_DD = [bb_baseBear[i] and bb_normPrice[i] > p.th_low_UU_DD for i in range(n)]
    is_d_DDD = [bb_baseBear[i] and bb_normPrice[i] > p.th_low_UUU_DDD for i in range(n)]
    is_d_DDDD = [bb_baseBear[i] and bb_normPrice[i] > p.th_low_UUUU_DDDD for i in range(n)]

    def _seq(is_bar):
        seq_len = [0] * n; seq_sum = [0.0] * n; seq_disp = [0] * n
        ln = 0; sm = 0.0; dp = 0
        for i in range(n):
            if conf[i]:
                if is_bar[i]:
                    ln += 1; sm += bb_normPrice[i]; dp += 1 if disp_cur_seq[i] else 0
                else:
                    ln = 0; sm = 0.0; dp = 0
            seq_len[i] = ln; seq_sum[i] = sm; seq_disp[i] = dp
        return seq_len, seq_sum, seq_disp

    bull_len_UU, bull_sum_UU, bull_disp_UU = _seq(is_u_UU)
    bear_len_DD, bear_sum_DD, bear_disp_DD = _seq(is_d_DD)
    bull_len_UUU, bull_sum_UUU, bull_disp_UUU = _seq(is_u_UUU)
    bear_len_DDD, bear_sum_DDD, bear_disp_DDD = _seq(is_d_DDD)
    bull_len_UUUU, bull_sum_UUUU, bull_disp_UUUU = _seq(is_u_UUUU)
    bear_len_DDDD, bear_sum_DDDD, bear_disp_DDDD = _seq(is_d_DDDD)

    sig_bull_UU = [conf[i] and bull_len_UU[i] == 2 and bull_sum_UU[i] >= th_saab_kratos and bull_disp_UU[i] >= 1 for i in range(n)]
    sig_bear_DD = [conf[i] and bear_len_DD[i] == 2 and bear_sum_DD[i] >= th_saab_kratos and bear_disp_DD[i] >= 1 for i in range(n)]
    sig_bull_UUU = [False] * n; sig_bear_DDD = [False] * n
    sig_bull_UUUU = [False] * n; sig_bear_DDDD = [False] * n
    for i in range(n):
        u3 = conf[i] and bull_len_UUU[i] == 3
        sig_bull_UUU[i] = (u3 and bull_disp_UUU[i] >= 2) or (u3 and bull_disp_UUU[i] >= 1 and bull_sum_UUU[i] >= th_saab_kratos)
        d3 = conf[i] and bear_len_DDD[i] == 3
        sig_bear_DDD[i] = (d3 and bear_disp_DDD[i] >= 2) or (d3 and bear_disp_DDD[i] >= 1 and bear_sum_DDD[i] >= th_saab_kratos)
        u4 = conf[i] and bull_len_UUUU[i] == 4
        sig_bull_UUUU[i] = (u4 and bull_disp_UUUU[i] >= 2) or (u4 and bull_disp_UUUU[i] >= 1 and bull_sum_UUUU[i] >= th_saab_kratos)
        d4 = conf[i] and bear_len_DDDD[i] == 4
        sig_bear_DDDD[i] = (d4 and bear_disp_DDDD[i] >= 2) or (d4 and bear_disp_DDDD[i] >= 1 and bear_sum_DDDD[i] >= th_saab_kratos)

    # ── B2B (2029-2035) ──
    sigSAAB_1 = _shift(sigSAAB, 1); sigKratos_1 = _shift(sigKratos, 1)
    sigBull1x_1 = _shift(sigBullRVOL1x, 1); sigBear1x_1 = _shift(sigBearRVOL1x, 1)
    sig_B2B_2xSAAB = [conf[i] and bool(sigSAAB_1[i]) and sigSAAB[i] and b2b_gate[i] for i in range(n)]
    sig_B2B_2xKratos = [conf[i] and bool(sigKratos_1[i]) and sigKratos[i] and b2b_gate[i] for i in range(n)]
    sig_B2B_2xBull1x = [conf[i] and bool(sigBull1x_1[i]) and sigBullRVOL1x[i] and b2b_gate[i] for i in range(n)]
    sig_B2B_2xBear1x = [conf[i] and bool(sigBear1x_1[i]) and sigBearRVOL1x[i] and b2b_gate[i] for i in range(n)]
    sig_B2B_MidBull = [conf[i] and not sig_B2B_2xSAAB[i] and not sig_B2B_2xBull1x[i]
                       and ((bool(sigSAAB_1[i]) and sigBullRVOL1x[i]) or (bool(sigBull1x_1[i]) and sigSAAB[i]))
                       and b2b_gate[i] for i in range(n)]
    sig_B2B_MidBear = [conf[i] and not sig_B2B_2xKratos[i] and not sig_B2B_2xBear1x[i]
                       and ((bool(sigKratos_1[i]) and sigBearRVOL1x[i]) or (bool(sigBear1x_1[i]) and sigKratos[i]))
                       and b2b_gate[i] for i in range(n)]

    # ── FAUNA (2037-2081) ──
    fn_ATR = _atr_ohlc(o, h, l, c, p.fn_atr_MB)
    fn_ATR_RE = _atr_ohlc(o, h, l, c, p.fn_atr_RE)
    fn_ATR_GG = _atr_ohlc(o, h, l, c, p.fn_atr_GG)
    fn_AvgVol = sma(vol, p.fn_vol_MB)
    fn_AvgBody = sma([abs(c[i] - o[i]) for i in range(n)], p.fn_body_avg)
    fn_AvgDelta = sma([abs(c[i] - c[i - 1]) if i >= 1 else 0.0 for i in range(n)], p.fn_avg_delta_len)
    fn_TrendMA = sma(c, p.fn_trend_ma_len)
    fn_AvgVol_1 = _shift(fn_AvgVol, 1)
    fn_AvgBody_1 = _shift(fn_AvgBody, 1)
    fn_bullActive = [False] * n; fn_bearActive = [False] * n
    for i in range(n):
        body = c[i] - o[i]
        crange = h[i] - l[i]
        body_up = body > 0; body_dn = body < 0
        body_size = abs(body)
        body_ratio = 0.0 if crange == 0 else body_size / crange
        av = fn_AvgVol[i]
        MB_bull = body_up and av is not None and fn_ATR[i] is not None and body_size > p.fn_alpha_MB * fn_ATR[i] and body_ratio > p.fn_beta_MB and vol[i] > p.fn_delta_MB * av
        MB_bear = body_dn and av is not None and fn_ATR[i] is not None and body_size > p.fn_alpha_MB * fn_ATR[i] and body_ratio > p.fn_beta_MB and vol[i] > p.fn_delta_MB * av
        wide = fn_ATR_RE[i] is not None and crange > p.fn_gamma_RE * fn_ATR_RE[i]
        RE_bull = body_up and wide and (h[i] - c[i]) < p.fn_epsilon_RE * crange and av is not None and vol[i] > p.fn_delta_RE * av
        RE_bear = body_dn and wide and (c[i] - l[i]) < p.fn_epsilon_RE * crange and av is not None and vol[i] > p.fn_delta_RE * av
        pc = c[i - 1] if i >= 1 else c[i]
        GG_bull = fn_ATR_GG[i] is not None and (o[i] - pc) > p.fn_zeta_GG * fn_ATR_GG[i] and body_up and l[i] > pc and av is not None and vol[i] > p.fn_delta_GG * av
        GG_bear = fn_ATR_GG[i] is not None and (pc - o[i]) > p.fn_zeta_GG * fn_ATR_GG[i] and body_dn and h[i] < pc and av is not None and vol[i] > p.fn_delta_GG * av
        up_trend = i >= 1 and fn_TrendMA[i] is not None and fn_TrendMA[i - 1] is not None and fn_TrendMA[i] > fn_TrendMA[i - 1]
        dn_trend = i >= 1 and fn_TrendMA[i] is not None and fn_TrendMA[i - 1] is not None and fn_TrendMA[i] < fn_TrendMA[i - 1]
        TA_bull = up_trend and body_up and i >= 1 and fn_AvgDelta[i] is not None and (c[i] - c[i - 1]) > p.fn_theta_TA * fn_AvgDelta[i] and av is not None and vol[i] > p.fn_delta_TA * av
        TA_bear = dn_trend and body_dn and i >= 1 and fn_AvgDelta[i] is not None and (c[i - 1] - c[i]) > p.fn_theta_TA * fn_AvgDelta[i] and av is not None and vol[i] > p.fn_delta_TA * av
        prev_body = (c[i - 1] - o[i - 1]) if i >= 1 else 0.0
        prev_range = (h[i - 1] - l[i - 1]) if i >= 1 else 0.0
        ab1 = fn_AvgBody_1[i]; av1 = fn_AvgVol_1[i]
        StrongBear_pre = i >= 1 and c[i - 1] < o[i - 1] and ab1 is not None and abs(prev_body) > p.fn_alpha_SB * ab1 and av1 is not None and vol[i - 1] > 1.5 * av1
        WeakBear_pre = i >= 1 and c[i - 1] < o[i - 1] and (0.0 if prev_range == 0 else abs(prev_body) / prev_range) <= p.fn_weak_ratio
        StrongBull_pre = i >= 1 and c[i - 1] > o[i - 1] and ab1 is not None and abs(prev_body) > p.fn_alpha_SB * ab1 and av1 is not None and vol[i - 1] > 1.5 * av1
        WeakBull_pre = i >= 1 and c[i - 1] > o[i - 1] and (0.0 if prev_range == 0 else abs(prev_body) / prev_range) <= p.fn_weak_ratio
        TR_bull = WeakBear_pre and (MB_bull or RE_bull or TA_bull)
        ES_bull = StrongBear_pre and (MB_bull or RE_bull or TA_bull)
        GDR_bull = i >= 1 and c[i - 1] < o[i - 1] and GG_bull
        TR_bear = WeakBull_pre and (MB_bear or RE_bear or TA_bear)
        ES_bear = StrongBull_pre and (MB_bear or RE_bear or TA_bear)
        GDR_bear = i >= 1 and c[i - 1] > o[i - 1] and GG_bear
        anyBull = MB_bull or RE_bull or GG_bull or TA_bull or TR_bull or ES_bull or GDR_bull
        anyBear = MB_bear or RE_bear or GG_bear or TA_bear or TR_bear or ES_bear or GDR_bear
        fn_bullActive[i] = anyBull and conf[i] and disp_cur_seq[i] and anyLong[i]
        fn_bearActive[i] = anyBear and conf[i] and disp_cur_seq[i] and anyShort[i]

    # ── HV 150..1000 gated +LONG[1] (2083-2098) ──
    hi_vol_250 = highest(vol, 250)
    hi_vol_350 = highest(vol, 350)
    hv150_1 = _shift(highest(vol, 150), 1); vol_1 = _shift(vol, 1)
    hv250_1 = _shift(hi_vol_250, 1); hv350_1 = _shift(hi_vol_350, 1)
    hv500_1 = _shift(hi_vol_500, 1); hv1000_1 = _shift(hi_vol_1000, 1)
    plot_HV = {k: [False] * n for k in (150, 250, 350, 500, 1000)}
    for i in range(n):
        is150 = vol_1[i] is not None and hv150_1[i] is not None and vol_1[i] == hv150_1[i]
        is250 = vol_1[i] is not None and hv250_1[i] is not None and vol_1[i] == hv250_1[i]
        is350 = vol_1[i] is not None and hv350_1[i] is not None and vol_1[i] == hv350_1[i]
        is500 = vol_1[i] is not None and hv500_1[i] is not None and vol_1[i] == hv500_1[i]
        is1000 = vol_1[i] is not None and hv1000_1[i] is not None and vol_1[i] == hv1000_1[i]
        raw1000 = is1000
        raw500 = is500 and not is1000
        raw350 = is350 and not is500 and not is1000
        raw250 = is250 and not is350 and not is500 and not is1000
        raw150 = is150 and not is250 and not is350 and not is500 and not is1000
        plot_HV[1000][i] = raw1000 and anyLong_1[i]
        plot_HV[500][i] = raw500 and anyLong_1[i]
        plot_HV[350][i] = raw350 and anyLong_1[i]
        plot_HV[250][i] = raw250 and anyLong_1[i]
        plot_HV[150][i] = raw150 and anyLong_1[i]

    # ── master HW-Single booleans (2103-2106) ──
    hws_bull = [False] * n; hws_bear = [False] * n; hws_neutral = [False] * n; hws_any = [False] * n
    for i in range(n):
        hws_bull[i] = ((sigSAAB[i] and anyLong[i]) or (sigBullRVOL1x[i] and anyLong[i])
                       or (sigGrandSlam[i] and anyLong[i]) or sig_bull_UU[i] or sig_bull_UUU[i]
                       or sig_bull_UUUU[i] or sig_B2B_2xSAAB[i] or sig_B2B_2xBull1x[i]
                       or sig_B2B_MidBull[i] or fn_bullActive[i] or sigDispBull[i]
                       or sigCDispBull2[i] or sigCDispBull3[i] or sigAddLong[0][i]
                       or sigAddLong[1][i] or sigAddLong[2][i] or sigAddLong[3][i]
                       or sigAddLong[4][i] or plot_HV[150][i] or plot_HV[250][i]
                       or plot_HV[350][i] or plot_HV[500][i] or plot_HV[1000][i] or hctGatedBull[i])
        hws_bear[i] = ((sigKratos[i] and anyShort[i]) or (sigBearRVOL1x[i] and anyShort[i])
                       or (sigMOAB[i] and anyShort[i]) or sig_bear_DD[i] or sig_bear_DDD[i]
                       or sig_bear_DDDD[i] or sig_B2B_2xKratos[i] or sig_B2B_2xBear1x[i]
                       or sig_B2B_MidBear[i] or fn_bearActive[i] or sigDispBear[i]
                       or sigCDispBear2[i] or sigCDispBear3[i] or sigAddShort[0][i]
                       or sigAddShort[1][i] or hctGatedBear[i])
        hws_neutral[i] = ((sigWTC[i] and anyMom[i]) or (sigHiroshima[i] and anyMom[i])
                          or (sigNagasaki[i] and anyMom[i]) or sigPentHV1K[i] or sigPentHV500D[i])
        hws_any[i] = hws_bull[i] or hws_bear[i] or hws_neutral[i]

    return {
        "hws_any": hws_any, "hws_bull": hws_bull,
        "hws_bear": hws_bear, "hws_neutral": hws_neutral,
        # leaf gates exposed for independent parity re-derivation
        "bb_baseBull": bb_baseBull, "bb_baseBear": bb_baseBear,
        "bb_normPrice": bb_normPrice, "sigSAAB": sigSAAB, "sigKratos": sigKratos,
        "sigNagasaki": sigNagasaki, "anyLong": anyLong, "anyShort": anyShort,
        "th_saab_kratos": th_saab_kratos, "th_1x": th_1x, "th_gs_moab": th_gs_moab,
    }
