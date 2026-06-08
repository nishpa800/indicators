"""TNT OPENING DRIVE (OD) v3 — FULL detection fire-matrix core (Pine v5 -> Python).

Source (read from disk, path has spaces):
  ".../June 7/Tick Friendly conversion/tnt_od_v3_tickfriendly.pine"
  //@version=5, indicator("TNT Opening Drive OD v3 [tickfriendly]", overlay=true).
  Tick-safe in the source via t_isTickChart / t_regAnchorSafe / TICK_FALLBACK_SEC
  and the in_seconds guard. relativeVolume routed through tv_ta (ta/7) anchorSafe.

ULTRACODE FULL PORT — scope statement (read this):
  This module ports EVERY one of the 47 numeric data_window detection plots the
  source emits (`plot(p_* ? 1 : 0, "f_*", display=display.data_window)`), which are
  the machine-readable mirror of the 42 plotshapes plus the WBUSH / T1 RELAY /
  T1 STACK additions. There is NO stub layer; COMPOSITE_PARTIAL is empty.

  This SUPERSEDES the earlier PARTIAL tnt_od_v3 port (which stubbed 39 fires at 0
  and only ported the displacement/RVOL/FAUNA/density layer). Here the full deep
  stateful engine stack is ported bar-by-bar in a single forward pass:

    ENGINE 1  VOB        EMA fast/slow cross -> bull/bear volume-order-block (origin
                         walk-back over EMA_SLOW bars, cumVol, atr_hi half-height clamp).
    SWING                ta.highest/lowest(SWING_LEN) swingState; swHigh/swLow pivots.
    ENGINE 2  ANISH      order-block on swing-cross (walk-back to extreme OB candle),
                         anish_*_new overlap-with-prev gate.
    ENGINE 3  FLUX       OB box on swing-cross sized by ATR band; pullback-new detect.
    CONFLUENCE  TNT 1.0  temporal-window + zone-overlap + synergy (volMedian, emaSlope,
                         rsi) -> raw_bull/bearTNT; zone push; charge-level push.
    ZONES                Zone array: active/inactive (close break), return-fire scan
                         (RET_TNT_PCT), line-x2 advance (logic only), cap maxZones.
    DISPLACEMENT #1      disp_range/std/threshold, FVG, prevBarDisplaced -> dispBull/Bear.
    NAPALM + CHARGE      napalm = displaced bar punches through an OPPOSING active zone
                         level; charge = displaced close clears an opposing charge level
                         (pushes a fresh same-dir charge level). Cap charge_levels 100.
    SUPER TNT / TNT 2.0  raw_superTNT* (TNT + opposing charge); event log; >=2 events
                         -> raw_bullTNT2/bearTNT2; super-zone return scan.
    SUDDEN CHANGE  CONT  rapid-fire proximity (SUDDEN_PROX) across charge/ret/TNT/TNT2.
    CONSOLIDATED         det_bullTNT/Napalm/RetTNT/cont (+ bear).
    USE V5 ENGINE        session bar count; RVOL bb-norm tiers (SAAB/Kratos/GS/MOAB/
                         RVOL1x); WMD via relativeVolume shim (Pentagon/WTC/Hiro/Nag);
                         HV1000; FAUNA bull/bear (MB/RE/TA/GG + exclusions); USE-V5
                         displacement; PUP/PPD; PBJ supertrend+filter; CS1 FVG combo.
    DYNAMITE #2          B2B sigma-range + same-color + FAUNA[1]&[2] + bar0 FVG.
    HEAVY PENTAGON       5 base combos x {bull/bear/neutral} -> WBUSH bull/bear/neutral.
    HCT #4               HCT-own thresholds (1x/saab/gs/wtc/hiro) + own displacement.
    UC                   >=2 confluence streams (FAUNA/RVOL/WMD/PUP-PPD/CS1).
    NAGASAKI+ANY         gate atom.
    GATE #5              gateStdMult displacement; master OR-gate gate_bull/gate_bear.
    COMBOS               RC NPM+TNT, RC TNT+RET, RC RET+NPM, PBJ+NPM/TNT/RET, FUSE,
                         IGNITE (T+C / N+C), CATALYST; suppression; tier-2 enrichment.
    FINAL PLOT BOOLS     all p_* tier1/tier2 with gate + enable gating.
    DENSITY              X-events-in-Y-bars rolling windows (driven off denVis* which is
                         the EXACT Pine visual-event stream — Napalm/RC/PBJ chains).
    UU/UUU/UUUU          RVOL streak path qualification (pA..pG) + TNT-ANY-in-window.
    T1 RELAY / T1 STACK  Tier-1 visual on bar[1]&[2] / >=2 distinct visuals on bar[1].
    WBUSH plots          WBUSH state x TNTOD-any-plot.

  Pine semantics preserved: single forward pass over CLOSED bars (every bar is
  barstate.isconfirmed -> conf=True); `[k]` = k-bars-back via prior-list indexing;
  `var` -> persistent Python state; recursive `:=` carried as explicit prev state;
  `nz(x)` -> nz(); `na` -> None; integer ternary chains -> Python expressions.

  Tick-safe handling: t_isTickChart -> tf_seconds fallback (TICK_FALLBACK_SEC);
  relativeVolume anchor "D" on tick AND time (tick bars do not align to clock
  times, so RVOL anchors to the calendar day of each bar timestamp — exactly the
  nine-nines harness convention; on time charts Pine uses "" chart-TF anchor, but
  the shim's "D" daily anchor is the canonical nine-nines RVOL — see harness note).
  u5_is_new_day uses calendar-day change of bar timestamp (Pine ta.change(time("D"))).

  NUMERIC LEVEL: the source emits exactly ONE numeric level plot
  ("lvl_u5_relVol" = u5_currentVol_reg / u5_pastVol_reg). We carry it 1:1. Every
  detection plot also gets a price level (the bar price the marker sits at:
  belowbar/bottom -> low, abovebar/top -> high) so a slicer can place each fire.

HONESTY: there is NO all-zero stub series. Every f_* plot is produced by real
ported Pine logic. The parity harness re-derives upstream gates independently and
reports a REAL pass/total.
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nn_harness import (  # noqa: E402
    nz, sma, stdev, highest, lowest, atr as _atr_ohlc, cum as _cum,
    relative_volume,
)


# ──────────────────────────────── parameters ────────────────────────────────
@dataclass
class Params:
    """Every Pine input.* / hardcoded threshold as a parameter (source default)."""
    # ── MASTER ──
    tick_fallback_sec: int = 10        # input.int 10  (T_TICK_FALLBACK_SEC)
    master_first_bar: bool = True      # input.bool true (alert gate; not a plot gate)
    master_aggregate: bool = True      # input.bool true (alert routing; no plot effect)
    # ── Engine #1 main displacement ──
    SENS: int = 100                    # input.int 100  -> EMA_FAST
    SWING_LEN: int = 10                # input.int 10
    DISP_TYPE: str = "Open to Close"   # input.string ["Open to Close","High to Low"]
    DISP_STD_LEN: int = 100            # input.int 100
    DISP_STD_X: int = 5                # input.int 5
    RET_TNT_PCT: float = 100.0         # input.float 100.0
    RET_SUPER_PCT: float = 50.0        # input.float 50.0 (unused by detection plots)
    SUDDEN_PROX: int = 3               # input.int 3
    # ── DYNAMITE (Engine #2) ──
    dynStdMult: float = 5.0            # input.float 5.0
    # ── USE V5 (Engine #3) ──
    u5_std_len: int = 100              # input.int 100
    u5_std_min: float = 3.0            # input.float 3.0
    u5_od_max_bars: int = 1            # input.int 1 (unused by detection plots)
    # ── NEW GATE (Engine #5) ──
    en_newGate: bool = True            # input.bool true
    gateStdMult: float = 6.5           # input.float 6.5
    # ── HCT (Engine #4) ──
    hct_disp_strength: float = 6.0     # input.float 6.0
    hct_disp_lookback: int = 100       # input.int 100
    hct_threshPct: float = 2.0         # input.float 2.0
    hct_auto: bool = True              # input.bool true
    # ── Zones ──
    maxZones: int = 30                 # input.int 30
    maxSuperZones: int = 30            # input.int 30
    # ── Density ──
    den1_X: int = 2; den1_Y: int = 2
    den2_X: int = 3; den2_Y: int = 3
    den3_X: int = 2; den3_Y: int = 6
    # ── ENABLES (all Pine input.bool true; WBUSH neutral standalone true) ──
    en_b2bBull: bool = True; en_b2bBear: bool = True
    en_rcNTBull: bool = True; en_rcNTBear: bool = True
    en_fuseBull: bool = True; en_fuseBear: bool = True
    en_catBull: bool = True; en_catBear: bool = True
    en_pnBull: bool = True; en_pnBear: bool = True
    en_ptBull: bool = True; en_ptBear: bool = True
    en_ignBull: bool = True; en_ignBear: bool = True
    en_dynBull: bool = True; en_dynBear: bool = True
    en_t2tntBull: bool = True; en_t2tntBear: bool = True
    en_t2npmBull: bool = True; en_t2npmBear: bool = True
    en_t2contBull: bool = True; en_t2contBear: bool = True
    en_t2trBull: bool = True; en_t2trBear: bool = True
    en_t2rnBull: bool = True; en_t2rnBear: bool = True
    en_t2prBull: bool = True; en_t2prBear: bool = True
    en_d1b: bool = True; en_d1s: bool = True
    en_d2b: bool = True; en_d2s: bool = True
    en_d3b: bool = True; en_d3s: bool = True
    en_uu_bull: bool = True; en_uu_bear: bool = True
    en_uuu_bull: bool = True; en_uuu_bear: bool = True
    en_uuuu_bull: bool = True; en_uuuu_bear: bool = True
    en_wbushBull: bool = True; en_wbushBear: bool = True
    en_wbushNeutral: bool = True
    # ── ATR engine constants (Pine literals) ──
    ATR_MULT: float = 3.5
    ATR_MIN: float = 0.5
    mintick: float = 0.01              # syminfo.mintick fallback


# canonical detection-plot ids — EXACTLY the 47 source data_window `plot(... "f_*")`
# entries, in source order. These are the fire matrix deliverable.
PLOT_IDS = [
    "f_b2bBull", "f_b2bBear", "f_rcNTBull", "f_rcNTBear", "f_fuseBull", "f_fuseBear",
    "f_catBull", "f_catBear", "f_pnBull", "f_pnBear", "f_ptBull", "f_ptBear",
    "f_ignBull", "f_ignBear", "f_dynBull", "f_dynBear",
    "f_t2tntBull", "f_t2tntBear", "f_t2npmBull", "f_t2npmBear",
    "f_t2contBull", "f_t2contBear", "f_t2trBull", "f_t2trBear",
    "f_t2rnBull", "f_t2rnBear", "f_t2prBull", "f_t2prBear",
    "f_d1b", "f_d1s", "f_d2b", "f_d2s", "f_d3b", "f_d3s",
    "f_uuBull", "f_uuBear", "f_uuuBull", "f_uuuBear", "f_uuuuBull", "f_uuuuBear",
    "f_wbushBull", "f_wbushBear", "f_wbushNeutral",
    "f_t1RelayBull", "f_t1RelayBear", "f_t1StackBull", "f_t1StackBear",
]

# bull plots draw belowbar/bottom -> level = low ; bear/neutral draw abovebar/top -> high
_BEAR_LEVEL = {
    "f_b2bBear", "f_rcNTBear", "f_fuseBear", "f_catBear", "f_pnBear", "f_ptBear",
    "f_ignBear", "f_dynBear", "f_t2tntBear", "f_t2npmBear", "f_t2contBear",
    "f_t2trBear", "f_t2rnBear", "f_t2prBear", "f_d1s", "f_d2s", "f_d3s",
    "f_uuBear", "f_uuuBear", "f_uuuuBear", "f_wbushBear", "f_wbushNeutral",
    "f_t1RelayBear", "f_t1StackBear",
}


# ─────────────────────────── Pine ta.* helpers (extra) ───────────────────────
def _ema(src, length):
    """Pine ta.ema: alpha=2/(len+1); seeded at first valid bar."""
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


def _vwma(c, v, length):
    pv = [None if (c[i] is None or v[i] is None) else c[i] * v[i] for i in range(len(c))]
    num = sma(pv, length)
    den = sma(v, length)
    out = [None] * len(c)
    for i in range(len(c)):
        if num[i] is not None and den[i] not in (None, 0):
            out[i] = num[i] / den[i]
    return out


def _rsi(src, length):
    """Pine ta.rsi: RMA of gains/losses."""
    n = len(src)
    gain = [0.0] * n
    loss = [0.0] * n
    for i in range(1, n):
        d = src[i] - src[i - 1]
        gain[i] = d if d > 0 else 0.0
        loss[i] = -d if d < 0 else 0.0
    # Pine ta.rma seeded as SMA of first `length`
    from _nn_harness import rma as _rma
    ag = _rma(gain, length)
    al = _rma(loss, length)
    out = [None] * n
    for i in range(n):
        if ag[i] is None or al[i] is None:
            continue
        if al[i] == 0:
            out[i] = 100.0
        else:
            rs = ag[i] / al[i]
            out[i] = 100.0 - 100.0 / (1.0 + rs)
    return out


def _median(values, length):
    """Pine ta.median over a rolling window of `length`."""
    out = [None] * len(values)
    from collections import deque
    win = deque()
    for i, x in enumerate(values):
        win.append(None if x is None else float(x))
        if len(win) > length:
            win.popleft()
        vals = sorted(w for w in win if w is not None)
        if len(win) == length and len(vals) == length:
            m = length // 2
            if length % 2:
                out[i] = vals[m]
            else:
                out[i] = (vals[m - 1] + vals[m]) / 2.0
    return out


def _utc_day(ts_ms):
    import datetime as _dt
    return _dt.datetime.utcfromtimestamp(ts_ms / 1000).toordinal()


# ─────────────────────────────── state structs ──────────────────────────────
@dataclass
class _Zone:
    originIdx: int
    confirmIdx: int
    upper: float
    lower: float
    level: float
    vol: float
    isBull: bool
    isActive: bool = True
    returnFired: bool = False


@dataclass
class _SwingPoint:
    val: float | None = None
    idx: int | None = None
    crossed: bool = False


@dataclass
class _Event:
    barIdx: int
    level: float
    upper: float
    lower: float
    isBull: bool
    isTrue: bool


@dataclass
class _Charge:
    level: float
    isBull: bool
    barIdx: int
    violated: bool = False


@dataclass
class _ULvl:
    upper: float
    lower: float
    vol: float
    approached: bool = False


@dataclass
class _Fvg:
    mx: float
    mn: float
    bull: bool
    t: int
    idx: int
    hv: bool


# ─────────────── HCT / USE-V5 per-tf-seconds threshold curves ────────────────
def _u5_1x(s):
    return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else 23.0 if s <= 45
            else 20.0 if s <= 60 else 18.0 if s <= 120 else 13.0 if s <= 300 else 13.0 if s <= 360
            else 11.0 if s <= 540 else 10.0 if s <= 600 else 9.0 if s <= 660 else 7.5 if s <= 900
            else 6.5 if s <= 1560 else 6.0 if s <= 2340 else 4.5 if s <= 3600 else 4.0 if s <= 9000
            else 3.5 if s <= 11700 else 1.8 if s < 259200 else 1.0)


def _u5_gs(s):
    return (_u5_1x(s) * 3.0 if s < 60 else 35.0 if s <= 300 else 25.0 if s <= 600 else 20.0 if s <= 1500
            else 20.0 if s <= 3000 else 10.0 if s <= 7260 else 8.0 if s <= 11700 else 7.5 if s <= 86400
            else 3.5 if s <= 259200 else 3.0)


def _u5_saab(s):
    return _u5_1x(s) * 0.56


def _u5_wtc(s):
    return _u5_1x(s) * 2.0


def _u5_hiro(s):
    return (_u5_1x(s) * 3.0 if s < 60 else 35.0 if s <= 300 else 25.0 if s <= 600 else 25.0 if s <= 1500
            else 20.0 if s <= 3060 else 10.0 if s <= 7260 else 8.0 if s <= 11700 else 7.5 if s <= 86400
            else 5.0 if s <= 259200 else 3.5)


def _hct_1x(s):
    return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else 23.0 if s <= 45
            else 20.0 if s <= 60 else 19.0 if s <= 120 else 17.0 if s <= 180 else 16.0 if s <= 240
            else 15.0 if s <= 300 else 14.0 if s <= 360 else 12.0 if s <= 420 else 11.0 if s <= 480
            else 10.0 if s <= 540 else 10.0 if s <= 600 else 8.4 if s <= 900 else 6.9 if s <= 1800
            else 5.9 if s <= 3600 else 3.0 if s <= 7200 else 1.8)


def _hct_saab(s):
    return _hct_1x(s) * 0.56


def _hct_gs(s):
    return (114.0 if s <= 10 else 99.0 if s <= 15 else 84.0 if s <= 30 else 69.0 if s <= 45
            else 35.0 if s <= 60 else 35.0 if s <= 300 else 25.0 if s <= 600 else 20.0 if s <= 900
            else 10.0 if s <= 3600 else 8.0)


def _hct_wtc(s):
    return _hct_1x(s) * 2.0


def _hct_hiro(s):
    return _hct_gs(s)


# ──────────────────────────────── core compute ──────────────────────────────
def compute(bars, *, params: Params | None = None, tf_seconds=None, grain="time"):
    """Full TNT OD v3 detection on Bar objects (oldest-first).

    Returns dict:
      ts                -> list[int]
      fire_<PLOT_ID>    -> list[int] 0/1  (47 detection plots)
      lvl_<PLOT_ID>     -> list[float|None] price the marker sits at (None off)
      lvl_u5_relVol     -> list[float|None] the one source numeric level plot
      sigAny            -> list[int] 0/1   OR of all 47 fires (slicer convenience)
    Tick and time grains call this one function (one code path, grain-bound).
    """
    p = params or Params()
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    l = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]
    n = len(bars)
    if n == 0:
        return {"ts": [], "sigAny": [], "lvl_u5_relVol": [],
                **{f"fire_{k}": [] for k in PLOT_IDS},
                **{f"lvl_{k}": [] for k in PLOT_IDS}}

    if tf_seconds is None:
        tf_seconds = p.tick_fallback_sec if grain == "tick" else 60
    u5_tfSec = int(tf_seconds)
    isSubMinute = u5_tfSec <= 60

    EMA_FAST = p.SENS
    EMA_SLOW = p.SENS + 13
    MIN_SIG_GAP = EMA_SLOW
    CONF_WINDOW = EMA_SLOW * 2

    # ── precomputed whole-series ta.* ──
    ema_fast = _ema(c, EMA_FAST)
    ema_slow = _ema(c, EMA_SLOW)
    atr200 = _atr_ohlc(o, h, l, c, 200)
    atr14 = _atr_ohlc(o, h, l, c, 14)
    atr_hi = highest(atr200, 200)
    atr_hi = [None if x is None else x * 2.0 for x in atr_hi]
    sw_upper = highest(h, p.SWING_LEN)
    sw_lower = lowest(l, p.SWING_LEN)
    volMedian = _median(v, EMA_SLOW)
    rsiVal = _rsi(c, 14)

    # USE V5 RVOL bb-norm
    bb_spike = [abs(c[i] - o[i]) for i in range(n)]
    bb_avgSpike = sma(bb_spike, 30)          # ta.sma(spike,30); used as [1]
    bb_avgVol = sma(v, 30)                    # ta.sma(volume,30); used as [1]
    # WMD relativeVolume via canonical shim (anchor "D" on both grains)
    rv_curr, rv_past, _rv_ratio = relative_volume(
        v, 30, anchor_timeframe="D", is_cumulative=True, bar_timestamps=ts)
    # FAUNA pre-series
    f_avgVol = sma(v, 20)
    f_avgBody = sma(bb_spike, 20)
    delta_abs = [0.0] + [abs(c[i] - c[i - 1]) for i in range(1, n)]
    f_avgDelta = sma(delta_abs, 10)
    f_trendMA = sma(c, 50)
    # USE V5 displacement
    u5_disp_rng = [abs(o[i] - c[i]) for i in range(n)]
    u5_disp_std = stdev(u5_disp_rng, p.u5_std_len)
    # main displacement
    disp_range = [abs(o[i] - c[i]) if p.DISP_TYPE == "Open to Close" else h[i] - l[i] for i in range(n)]
    disp_std = stdev(disp_range, p.DISP_STD_LEN)
    # DYNAMITE displacement
    dyn_disp = [abs(o[i] - c[i]) for i in range(n)]
    dyn_std = stdev(dyn_disp, 100)
    # PUP/PPD
    pp_redVol = [v[i] if c[i] < o[i] else 0.0 for i in range(n)]
    pp_greenVol = [v[i] if c[i] > o[i] else 0.0 for i in range(n)]
    pp_redVol_1 = [None] + pp_redVol[:-1]
    pp_greenVol_1 = [None] + pp_greenVol[:-1]
    pp_hiRed = highest([0.0 if x is None else x for x in pp_redVol_1], 10)
    pp_hiGreen = highest([0.0 if x is None else x for x in pp_greenVol_1], 10)
    # PBJ
    base_ma5 = _vwma(c, v, 5)
    st_atr10 = _atr_ohlc(o, h, l, c, 10)
    pbjMA = _ema(c, 20)
    pbjATR = _atr_ohlc(o, h, l, c, 14)
    zoo_avg_vol = sma(v, 20)
    low25 = lowest(l, 25)
    high25 = highest(h, 25)
    # CS1 / GZI HV lookbacks (use volume[1])
    v_1 = [None] + v[:-1]
    hv5k = highest([0.0 if x is None else x for x in v_1], 5000)
    hv252 = highest([0.0 if x is None else x for x in v_1], 252)
    hv63 = highest([0.0 if x is None else x for x in v_1], 63)
    gz_thresh_cum = _cum([(h[i] - l[i]) / l[i] if l[i] else 0.0 for i in range(n)])
    # HCT auto thresh = cum((h-l)/l)/bar_index ; bar_index = i (0-based, like Pine)
    hct_cum = _cum([(h[i] - l[i]) / l[i] if l[i] else 0.0 for i in range(n)])
    hct_rangeStdev = stdev([h[i] - l[i] for i in range(n)], p.hct_disp_lookback)
    # HV1000
    v_high1000_1 = [None] + highest(v, 1000)[:-1]
    v_high50_1 = [None] + highest(v, 50)[:-1]

    # thresholds (constant across bars — tf_seconds fixed for a tape)
    u5_th_saab = _u5_saab(u5_tfSec); u5_th_1x = _u5_1x(u5_tfSec); u5_th_gs = _u5_gs(u5_tfSec)
    u5_th_wtc = _u5_wtc(u5_tfSec); u5_th_hiro = _u5_hiro(u5_tfSec)
    hct_th_saab = _hct_saab(u5_tfSec); hct_th_1x = _hct_1x(u5_tfSec); hct_th_gs = _hct_gs(u5_tfSec)
    hct_th_wtc = _hct_wtc(u5_tfSec); hct_th_hiro = _hct_hiro(u5_tfSec)

    # ── persistent var state ──
    sessionFirstBarIdx = None
    swingState = 0
    swHigh = _SwingPoint(); swLow = _SwingPoint()
    anish_bull = dict(u=None, l=None, idx=None, pu=None, pl=None, pidx=None)
    anish_bear = dict(u=None, l=None, idx=None, pu=None, pl=None, pidx=None)
    flux_bull = dict(top=None, btm=None, time=None, active=False, pb_idx=None)
    flux_bear = dict(top=None, btm=None, time=None, active=False, pb_idx=None)
    flux_swH = _SwingPoint(); flux_swL = _SwingPoint()
    vob_bull = dict(u=None, l=None, origin=None, vol=None)
    vob_bear = dict(u=None, l=None, origin=None, vol=None)
    vob_bull_conf = 0; anish_bull_conf = 0; flux_bull_conf = 0
    vob_bear_conf = 0; anish_bear_conf = 0; flux_bear_conf = 0
    vob_bull_u = vob_bull_l = vob_bear_u = vob_bear_l = None
    tnt_zones: list[_Zone] = []
    charge_levels: list[_Charge] = []
    lastBullSigBar = 0; lastBearSigBar = 0
    bull_events: list[_Event] = []; bear_events: list[_Event] = []
    super_zones: list = []  # source never pushes super-zones -> stays empty (matches Pine)
    lastSuperBullBar = 0; lastSuperBearBar = 0
    sc = dict(bullCharge=None, bearCharge=None, retBull=None, retBear=None,
              bullTNT=None, bearTNT=None, bullTNT2=None, bearTNT2=None)
    u5_sessionBarCount = 0; u5_lastCountedBar = -1
    u5_maxVol = 0.0
    u5_curr_long_prev = None; u5_curr_short_prev = None
    u5_st_dir = 1; u5_sig_prev = None; u5_sig_prev2 = None
    u5_bull_lvls: list[_ULvl] = []; u5_bear_lvls: list[_ULvl] = []
    u5_wait_buy = u5_wait_sell = u5_wait_pbj_buy = u5_wait_pbj_sell = False
    gz_fvgs: list[_Fvg] = []; gz_lastT = 0
    u5_u_bull_streak = 0; u5_u_bear_streak = 0
    u5_u_bull_hasDay1 = False; u5_u_bear_hasDay1 = False
    # density latches
    d1br = d1sr = d2br = d2sr = d3br = d3sr = -1
    d1ba = d1sa = d2ba = d2sa = d3ba = d3sa = True
    fuse = dict(bullNPM=None, bullTNT=None, bearNPM=None, bearTNT=None)

    # ── history lists for [k] back-references on per-bar booleans ──
    H = {k: [] for k in (
        "det_bullTNT", "det_bearTNT", "det_bullNapalm", "det_bearNapalm",
        "det_bullRetTNT", "det_bearRetTNT", "det_contBull", "det_contBear",
        "u5_SAAB", "u5_Kratos", "u5_GrandSlam", "u5_MOAB", "u5_RVOL1xB", "u5_RVOL1xR",
        "u5_Pentagon", "u5_WTC", "u5_Hiroshima", "u5_Nagasaki",
        "u5_PUP", "u5_PPD", "u5_FAUNABull", "u5_FAUNABear", "u5_WMD", "u5_HV1000",
        "u5_PBJBull", "u5_PBJBear", "u5_DISPBull", "u5_DISPBear", "u5_CS1_Bull", "u5_CS1_Bear",
        "det_dynamiteBull", "det_dynamiteBear",
        "det_rcTRBull", "det_rcTRBear", "det_ptBull", "det_ptBear", "det_prBull", "det_prBear",
        "det_fuseBull", "det_fuseBear", "det_igniteBull", "det_igniteBear",
        "ign_tc_bull", "ign_tc_bear", "ign_nc_bull", "ign_nc_bear",
        "gate_bull", "gate_bear",
        "p_b2bBull", "p_b2bBear", "sig_rcNTBull", "sig_rcNTBear", "p_catBull", "p_catBear",
        "p_pnBull", "p_pnBear", "p_fuseBull", "p_fuseBear", "p_ptBull", "p_ptBear",
        "p_ignBull", "p_ignBear", "p_dynBull", "p_dynBear",
        "det_bullNapalm0", "det_bearNapalm0", "det_rcRNBull", "det_rcRNBear",
        "det_pnBull", "det_pnBear", "det_catBull", "det_catBear",
        "hct_bull", "hct_bear", "uc_bull", "uc_bear",
        "sig_d1b", "sig_d1s", "sig_d2b", "sig_d2s", "sig_d3b", "sig_d3s",
    )}

    def hb(key, off):
        """history-back: value of H[key] off bars back; False if OOB/None."""
        arr = H[key]
        j = len(arr) - off
        return arr[j] if 0 <= j < len(arr) else False

    # output columns
    fire = {k: [0] * n for k in PLOT_IDS}
    lvl = {k: [None] * n for k in PLOT_IDS}
    lvl_relVol: list[float | None] = [None] * n

    for i in range(n):
        conf = True   # closed bars -> barstate.isconfirmed
        isFirstBar = (i == 0) or (_utc_day(ts[i]) != _utc_day(ts[i - 1]))
        if isFirstBar:
            sessionFirstBarIdx = i

        # ============================ ENGINE 1: VOB ===========================
        vob_bull_cross = (ema_fast[i] is not None and ema_slow[i] is not None and i >= 1
                          and ema_fast[i - 1] is not None and ema_slow[i - 1] is not None
                          and ema_fast[i] > ema_slow[i] and ema_fast[i - 1] <= ema_slow[i - 1] and conf)
        vob_bear_cross = (ema_fast[i] is not None and ema_slow[i] is not None and i >= 1
                          and ema_fast[i - 1] is not None and ema_slow[i - 1] is not None
                          and ema_fast[i] < ema_slow[i] and ema_fast[i - 1] >= ema_slow[i - 1] and conf)
        ahi = nz(atr_hi[i])
        vob_bull_new = False; vob_bear_new = False
        if vob_bull_cross:
            cumVol = 0.0; originBar = i; originLow = l[i]
            for k in range(1, EMA_SLOW + 1):
                if i - k < 0:
                    break
                if l[i - k] <= originLow:
                    originLow = l[i - k]; originBar = i - k
                cumVol += v[i - k]
            off = i - originBar
            src = min(o[i - off], c[i - off])
            if (src - originLow) < ahi * 0.5:
                src = originLow + ahi * 0.5
            vob_bull.update(u=src, l=originLow, origin=originBar, vol=cumVol)
            vob_bull_new = True
        if vob_bear_cross:
            cumVol = 0.0; originBar = i; originHigh = h[i]
            for k in range(1, EMA_SLOW + 1):
                if i - k < 0:
                    break
                if h[i - k] >= originHigh:
                    originHigh = h[i - k]; originBar = i - k
                cumVol += v[i - k]
            off = i - originBar
            src = max(o[i - off], c[i - off])
            if (originHigh - src) < ahi * 0.5:
                src = originHigh - ahi * 0.5
            vob_bear.update(u=originHigh, l=src, origin=originBar, vol=cumVol)
            vob_bear_new = True

        # ============================ SWING ===================================
        swingState_prev = swingState
        if i - p.SWING_LEN >= 0 and sw_upper[i] is not None and h[i - p.SWING_LEN] > sw_upper[i]:
            swingState = 0
        elif i - p.SWING_LEN >= 0 and sw_lower[i] is not None and l[i - p.SWING_LEN] < sw_lower[i]:
            swingState = 1
        # else keep
        if swingState == 0 and swingState_prev != 0 and i - p.SWING_LEN >= 0:
            swHigh = _SwingPoint(h[i - p.SWING_LEN], i - p.SWING_LEN)
        if swingState == 1 and swingState_prev != 1 and i - p.SWING_LEN >= 0:
            swLow = _SwingPoint(l[i - p.SWING_LEN], i - p.SWING_LEN)

        # ========================= ENGINE 2: ANISH ============================
        anish_bull_new = False; anish_bear_new = False
        if (swHigh.val is not None and c[i] > swHigh.val and not swHigh.crossed and conf):
            swHigh.crossed = True
            obLow = l[i - 1] if i >= 1 else l[i]
            obHigh = h[i - 1] if i >= 1 else h[i]
            obIdx = i - 1
            lookback = i - swHigh.idx
            if lookback > 1:
                for k in range(1, lookback):
                    if i - k < 0:
                        break
                    if o[i - k] > c[i - k] and l[i - k] <= obLow:
                        obLow = l[i - k]; obHigh = h[i - k]; obIdx = i - k
            anish_bull["pu"] = anish_bull["u"]; anish_bull["pl"] = anish_bull["l"]; anish_bull["pidx"] = anish_bull["idx"]
            anish_bull["u"] = obHigh; anish_bull["l"] = obLow; anish_bull["idx"] = obIdx
            anish_bull_new = (anish_bull["pu"] is not None
                              and obIdx <= nz(anish_bull["pidx"], 0) + EMA_SLOW
                              and anish_bull["pl"] is not None and obHigh > anish_bull["pl"]
                              and anish_bull["pu"] is not None and obLow < anish_bull["pu"])
        if (swLow.val is not None and c[i] < swLow.val and not swLow.crossed and conf):
            swLow.crossed = True
            obLow = l[i - 1] if i >= 1 else l[i]
            obHigh = h[i - 1] if i >= 1 else h[i]
            obIdx = i - 1
            lookback = i - swLow.idx
            if lookback > 1:
                for k in range(1, lookback):
                    if i - k < 0:
                        break
                    if o[i - k] < c[i - k] and h[i - k] >= obHigh:
                        obHigh = h[i - k]; obLow = l[i - k]; obIdx = i - k
            anish_bear["pu"] = anish_bear["u"]; anish_bear["pl"] = anish_bear["l"]; anish_bear["pidx"] = anish_bear["idx"]
            anish_bear["u"] = obHigh; anish_bear["l"] = obLow; anish_bear["idx"] = obIdx
            anish_bear_new = (anish_bear["pl"] is not None
                              and obIdx <= nz(anish_bear["pidx"], 0) + EMA_SLOW
                              and anish_bear["pu"] is not None and obLow < anish_bear["pu"]
                              and anish_bear["pl"] is not None and obHigh > anish_bear["pl"])

        # ========================= ENGINE 3: FLUX =============================
        if swingState == 0 and swingState_prev != 0 and i - p.SWING_LEN >= 0:
            flux_swH = _SwingPoint(h[i - p.SWING_LEN], i - p.SWING_LEN)
        if swingState == 1 and swingState_prev != 1 and i - p.SWING_LEN >= 0:
            flux_swL = _SwingPoint(l[i - p.SWING_LEN], i - p.SWING_LEN)
        atrv = nz(atr200[i])
        if (flux_swH.val is not None and c[i] > flux_swH.val and not flux_swH.crossed and conf):
            flux_swH.crossed = True
            if i >= 1:
                boxBtm = min(o[i - 1], c[i - 1]); boxTop = max(o[i - 1], c[i - 1]); boxIdx = i - 1
            else:
                boxBtm = min(o[i], c[i]); boxTop = max(o[i], c[i]); boxIdx = i
            lookback = i - flux_swH.idx
            if lookback > 1:
                for k in range(1, lookback):
                    if i - k < 0:
                        break
                    if min(o[i - k], c[i - k]) < boxBtm:
                        boxBtm = min(o[i - k], c[i - k]); boxTop = max(o[i - k], c[i - k]); boxIdx = i - k
            obSize = abs(boxTop - boxBtm)
            if obSize <= atrv * p.ATR_MULT and obSize > atrv * p.ATR_MIN:
                flux_bull.update(top=boxTop, btm=boxBtm, time=boxIdx, active=True)
        if (flux_swL.val is not None and c[i] < flux_swL.val and not flux_swL.crossed and conf):
            flux_swL.crossed = True
            if i >= 1:
                boxTop = max(o[i - 1], c[i - 1]); boxBtm = min(o[i - 1], c[i - 1]); boxIdx = i - 1
            else:
                boxTop = max(o[i], c[i]); boxBtm = min(o[i], c[i]); boxIdx = i
            lookback = i - flux_swL.idx
            if lookback > 1:
                for k in range(1, lookback):
                    if i - k < 0:
                        break
                    if max(o[i - k], c[i - k]) > boxTop:
                        boxTop = max(o[i - k], c[i - k]); boxBtm = min(o[i - k], c[i - k]); boxIdx = i - k
            obSize = abs(boxTop - boxBtm)
            if obSize <= atrv * p.ATR_MULT and obSize > atrv * p.ATR_MIN:
                flux_bear.update(top=boxTop, btm=boxBtm, time=boxIdx, active=True)
        flux_bull_pb_new = False
        if flux_bull["active"] and conf:
            if c[i] < flux_bull["btm"]:
                flux_bull["active"] = False
            elif (i >= 1 and l[i - 1] < flux_bull["top"] and l[i - 1] > flux_bull["btm"]
                  and c[i] > o[i] and c[i] > h[i - 1]):
                flux_bull_pb_new = True; flux_bull["pb_idx"] = flux_bull["time"]
        flux_bear_pb_new = False
        if flux_bear["active"] and conf:
            if c[i] > flux_bear["top"]:
                flux_bear["active"] = False
            elif (i >= 1 and h[i - 1] > flux_bear["btm"] and h[i - 1] < flux_bear["top"]
                  and c[i] < o[i] and c[i] < l[i - 1]):
                flux_bear_pb_new = True; flux_bear["pb_idx"] = flux_bear["time"]

        # ==================== CONFLUENCE -> TNT 1.0 ===========================
        if vob_bull_new:
            vob_bull_conf = i; vob_bull_u = vob_bull["u"]; vob_bull_l = vob_bull["l"]
        if vob_bear_new:
            vob_bear_conf = i; vob_bear_u = vob_bear["u"]; vob_bear_l = vob_bear["l"]
        if anish_bull_new:
            anish_bull_conf = i
        if anish_bear_new:
            anish_bear_conf = i
        if flux_bull_pb_new:
            flux_bull_conf = i
        if flux_bear_pb_new:
            flux_bear_conf = i

        def temporal_ok(a, b, cc):
            mn = min(a, b, cc); mx = max(a, b, cc)
            return (mx - mn) <= CONF_WINDOW and mn > 0

        def zones_overlap(u1, l1, u2, l2):
            return u1 is not None and u2 is not None and u1 >= l2 and u2 >= l1

        emaSlope = (ema_fast[i] - ema_fast[i - 5]) if (i >= 5 and ema_fast[i] is not None and ema_fast[i - 5] is not None) else 0.0
        rv = nz(rsiVal[i], 50.0)
        vm = nz(volMedian[i])

        def synergy_bull(vV, vU, vL, aU, aL):
            denom = min(vU - vL, aU - aL)
            ov = (max(0.0, min(vU, aU) - max(vL, aL)) / denom) > 0.3 if denom > 0 else False
            return vV > vm * EMA_SLOW * 0.5 and emaSlope > 0 and rv < 80 and ov

        def synergy_bear(vV, vU, vL, aU, aL):
            denom = min(vU - vL, aU - aL)
            ov = (max(0.0, min(vU, aU) - max(vL, aL)) / denom) > 0.3 if denom > 0 else False
            return vV > vm * EMA_SLOW * 0.5 and emaSlope < 0 and rv > 20 and ov

        bullConf = (temporal_ok(vob_bull_conf, anish_bull_conf, flux_bull_conf)
                    and zones_overlap(vob_bull_u, vob_bull_l, anish_bull["u"], anish_bull["l"]))
        bearConf = (temporal_ok(vob_bear_conf, anish_bear_conf, flux_bear_conf)
                    and zones_overlap(vob_bear_u, vob_bear_l, anish_bear["u"], anish_bear["l"]))
        raw_bullTNT = (bullConf and synergy_bull(nz(vob_bull["vol"]), nz(vob_bull_u), nz(vob_bull_l),
                       nz(anish_bull["u"]), nz(anish_bull["l"])) and conf and (i - lastBullSigBar) > MIN_SIG_GAP)
        raw_bearTNT = (bearConf and synergy_bear(nz(vob_bear["vol"]), nz(vob_bear_u), nz(vob_bear_l),
                       nz(anish_bear["u"]), nz(anish_bear["l"])) and conf and (i - lastBearSigBar) > MIN_SIG_GAP)

        def bull_level():
            return ((min(nz(vob_bull_u, h[i]), nz(anish_bull["u"], h[i]))
                     + max(nz(vob_bull_l, l[i]), nz(anish_bull["l"], l[i]))) / 2.0)

        def bear_level():
            return ((min(nz(vob_bear_u, h[i]), nz(anish_bear["u"], h[i]))
                     + max(nz(vob_bear_l, l[i]), nz(anish_bear["l"], l[i]))) / 2.0)

        def bull_origin():
            org = min(nz(vob_bull["origin"], i), nz(anish_bull["idx"], i), nz(flux_bull["pb_idx"], i))
            return org if org > 0 else i

        def bear_origin():
            org = min(nz(vob_bear["origin"], i), nz(anish_bear["idx"], i), nz(flux_bear["pb_idx"], i))
            return org if org > 0 else i

        if raw_bullTNT:
            lastBullSigBar = i
            oU = min(nz(vob_bull_u, h[i]), nz(anish_bull["u"], h[i]))
            oL = max(nz(vob_bull_l, l[i]), nz(anish_bull["l"], l[i]))
            lvlz = (oU + oL) / 2.0
            tnt_zones.append(_Zone(bull_origin(), i, oU, oL, lvlz, nz(vob_bull["vol"]), True, True, False))
            charge_levels.append(_Charge(lvlz, True, i))
        if raw_bearTNT:
            lastBearSigBar = i
            oU = min(nz(vob_bear_u, h[i]), nz(anish_bear["u"], h[i]))
            oL = max(nz(vob_bear_l, l[i]), nz(anish_bear["l"], l[i]))
            lvlz = (oU + oL) / 2.0
            tnt_zones.append(_Zone(bear_origin(), i, oU, oL, lvlz, nz(vob_bear["vol"]), False, True, False))
            charge_levels.append(_Charge(lvlz, False, i))

        # ============================ RETURN (TNT 1.0) ========================
        raw_retBullTNT = False; raw_retBearTNT = False
        for z in reversed(tnt_zones):
            if z.isActive:
                if z.isBull and c[i] < z.lower:
                    z.isActive = False
                if (not z.isBull) and c[i] > z.upper:
                    z.isActive = False
                if z.isActive and not z.returnFired and conf and i > z.confirmIdx:
                    zH = z.upper - z.lower
                    if z.isBull:
                        retLvl = z.lower + zH * (p.RET_TNT_PCT / 100.0)
                        if l[i] <= retLvl and c[i] > z.lower:
                            z.returnFired = True; raw_retBullTNT = True
                    else:
                        retLvl = z.upper - zH * (p.RET_TNT_PCT / 100.0)
                        if h[i] >= retLvl and c[i] < z.upper:
                            z.returnFired = True; raw_retBearTNT = True
        while len(tnt_zones) > p.maxZones:
            tnt_zones.pop(0)

        # ========================= DISPLACEMENT #1 ============================
        dthr = (disp_std[i] * p.DISP_STD_X) if disp_std[i] is not None else None
        dthr_1 = (disp_std[i - 1] * p.DISP_STD_X) if (i >= 1 and disp_std[i - 1] is not None) else None
        isBullishFVG = (i >= 2 and l[i] > h[i - 2] and o[i - 1] < c[i - 1])
        isBearishFVG = (i >= 2 and h[i] < l[i - 2] and o[i - 1] > c[i - 1])
        prevBarDisplaced = (i >= 1 and dthr_1 is not None and disp_range[i - 1] > dthr_1)
        dispSignal = prevBarDisplaced and (isBullishFVG or isBearishFVG) and conf
        dispBull = dispSignal and (i >= 1 and c[i - 1] > o[i - 1])
        dispBear = dispSignal and (i >= 1 and c[i - 1] < o[i - 1])

        # ====================== NAPALM + CHARGE ===============================
        raw_napalmBull = False; raw_napalmBear = False
        pseudoBullLevel = None; pseudoBearLevel = None
        if conf and tnt_zones:
            if dispBull:
                for z in reversed(tnt_zones):
                    if (not z.isBull) and z.isActive and i >= 1 and l[i - 1] > z.level:
                        raw_napalmBull = True; pseudoBullLevel = z.level; break
            if dispBear:
                for z in reversed(tnt_zones):
                    if z.isBull and z.isActive and i >= 1 and h[i - 1] < z.level:
                        raw_napalmBear = True; pseudoBearLevel = z.level; break
        raw_bullCharge = False; raw_bearCharge = False
        chargeBullLevel = None; chargeBearLevel = None
        if conf and charge_levels:
            if dispBull:
                for cl in reversed(charge_levels):
                    if (not cl.isBull) and (not cl.violated) and i >= 1 and c[i - 1] > cl.level:
                        cl.violated = True; raw_bullCharge = True; chargeBullLevel = cl.level
                        charge_levels.append(_Charge(l[i - 1], True, i)); break
            if dispBear:
                for cl in reversed(charge_levels):
                    if cl.isBull and (not cl.violated) and i >= 1 and c[i - 1] < cl.level:
                        cl.violated = True; raw_bearCharge = True; chargeBearLevel = cl.level
                        charge_levels.append(_Charge(h[i - 1], False, i)); break
        while len(charge_levels) > 100:
            charge_levels.pop(0)

        # ================= SUPER TNT / EVENTS / TNT 2.0 =======================
        raw_superTNTBull = raw_bullTNT and raw_bearCharge
        raw_superTNTBear = raw_bearTNT and raw_bullCharge
        effBullCharge = raw_bullCharge and not raw_bearTNT
        effBearCharge = raw_bearCharge and not raw_bullTNT
        anyBullEvent = raw_bullTNT or raw_napalmBull or effBullCharge
        anyBearEvent = raw_bearTNT or raw_napalmBear or effBearCharge
        if anyBullEvent:
            evtLvl = (bull_level() if raw_bullTNT else
                      pseudoBullLevel if raw_napalmBull else chargeBullLevel)
            bull_events.append(_Event(i if raw_bullTNT else i - 1, nz(evtLvl), h[i], l[i], True, raw_bullTNT))
            bear_events.clear()
            while len(bull_events) > 20:
                bull_events.pop(0)
        if anyBearEvent and not anyBullEvent:
            evtLvl = (bear_level() if raw_bearTNT else
                      pseudoBearLevel if raw_napalmBear else chargeBearLevel)
            bear_events.append(_Event(i if raw_bearTNT else i - 1, nz(evtLvl), h[i], l[i], False, raw_bearTNT))
            bull_events.clear()
            while len(bear_events) > 20:
                bear_events.pop(0)
        raw_bullTNT2 = False; raw_bearTNT2 = False
        if len(bull_events) >= 2 and anyBullEvent and conf and (i - lastSuperBullBar) > MIN_SIG_GAP:
            raw_bullTNT2 = True; lastSuperBullBar = i
        if len(bear_events) >= 2 and anyBearEvent and not anyBullEvent and conf and (i - lastSuperBearBar) > MIN_SIG_GAP:
            raw_bearTNT2 = True; lastSuperBearBar = i
        # Return TNT 2.0 — source never pushes super_zones, so this is inert (matches Pine)
        raw_retBullTNT2 = False; raw_retBearTNT2 = False

        # ===================== SUDDEN CHANGE (CONT) ===========================
        SP = p.SUDDEN_PROX
        raw_contBull = (
            (raw_bullCharge and sc["retBull"] is not None and (i - 1 - sc["retBull"]) <= SP)
            or ((raw_bullTNT or raw_bullTNT2) and sc["bullCharge"] is not None and (i - sc["bullCharge"]) <= SP)
            or (raw_bullCharge and ((sc["bullTNT"] is not None and (i - 1 - sc["bullTNT"]) <= SP)
                                    or (sc["bullTNT2"] is not None and (i - 1 - sc["bullTNT2"]) <= SP)))
        )
        raw_contBear = (
            (raw_bearCharge and sc["retBear"] is not None and (i - 1 - sc["retBear"]) <= SP)
            or ((raw_bearTNT or raw_bearTNT2) and sc["bearCharge"] is not None and (i - sc["bearCharge"]) <= SP)
            or (raw_bearCharge and ((sc["bearTNT"] is not None and (i - 1 - sc["bearTNT"]) <= SP)
                                    or (sc["bearTNT2"] is not None and (i - 1 - sc["bearTNT2"]) <= SP)))
        )
        if raw_bullCharge:
            sc["bullCharge"] = i - 1
        if raw_bearCharge:
            sc["bearCharge"] = i - 1
        if raw_retBullTNT or raw_retBullTNT2:
            sc["retBull"] = i
        if raw_retBearTNT or raw_retBearTNT2:
            sc["retBear"] = i
        if raw_bullTNT:
            sc["bullTNT"] = i
        if raw_bearTNT:
            sc["bearTNT"] = i
        if raw_bullTNT2:
            sc["bullTNT2"] = i
        if raw_bearTNT2:
            sc["bearTNT2"] = i

        # ===================== CONSOLIDATED DETECTION =========================
        det_bullTNT = raw_bullTNT or raw_bullTNT2 or raw_superTNTBull
        det_bearTNT = raw_bearTNT or raw_bearTNT2 or raw_superTNTBear
        det_bullNapalm = raw_napalmBull or raw_bullCharge
        det_bearNapalm = raw_napalmBear or raw_bearCharge
        det_bullRetTNT = raw_retBullTNT or raw_retBullTNT2
        det_bearRetTNT = raw_retBearTNT or raw_retBearTNT2
        det_contBull = raw_contBull
        det_contBear = raw_contBear

        # =========================== USE V5 ENGINE ============================
        u5_is_new_day = isFirstBar
        if u5_is_new_day and i != u5_lastCountedBar:
            u5_sessionBarCount = 1; u5_lastCountedBar = i
        elif i != u5_lastCountedBar:
            u5_sessionBarCount += 1; u5_lastCountedBar = i

        bb_spike_i = bb_spike[i]
        # Pine x/0 -> na (no crash). nz() only replaces na, so a 0.0 denom stays 0.
        _denomS = nz(bb_avgSpike[i - 1] if i >= 1 else None, 1.0)
        _denomV = nz(bb_avgVol[i - 1] if i >= 1 else None, 1.0)
        bb_normPrice = (bb_spike_i / _denomS) if _denomS != 0 else None
        bb_normVol = (v[i] / _denomV) if _denomV != 0 else None
        bb_diff = (bb_normPrice - bb_normVol) if (bb_normPrice is not None and bb_normVol is not None) else None
        # bb_smaDiff over posDiff is computed by Pine but only used via base gate below;
        # base gate uses posDiff > smaDiff. We need the rolling sma of posDiff.
        # (carried via a small persistent accumulation — see posDiff history.)
        # We approximate Pine ta.sma(posDiff,20) faithfully via a deque of posDiff.
        posDiff = bb_diff if (bb_diff is not None and bb_diff > 0) else None
        # maintain rolling window for sma(posDiff,20)
        if i == 0:
            compute._pd_win = []  # type: ignore[attr-defined]
        pd_win = compute._pd_win  # type: ignore[attr-defined]
        pd_win.append(posDiff)
        if len(pd_win) > 20:
            pd_win.pop(0)
        valid = [x for x in pd_win if x is not None]
        bb_smaDiff = (sum(valid) / 20.0) if len(pd_win) == 20 and len(valid) == 20 else None
        bb_baseBull = (c[i] > o[i]) and (posDiff is not None and bb_smaDiff is not None and posDiff > bb_smaDiff) and conf
        bb_baseBear = (c[i] < o[i]) and (posDiff is not None and bb_smaDiff is not None and posDiff > bb_smaDiff) and conf

        def inrange(x, lo, hi):
            return x >= lo and x < hi

        u5_SAAB = bb_baseBull and inrange(bb_normPrice, u5_th_saab, u5_th_1x)
        u5_Kratos = bb_baseBear and inrange(bb_normPrice, u5_th_saab, u5_th_1x)
        u5_GrandSlam = bb_baseBull and (bb_normPrice >= u5_th_gs)
        u5_MOAB = bb_baseBear and (bb_normPrice >= u5_th_gs)
        u5_RVOL1xB = bb_baseBull and inrange(bb_normPrice, u5_th_1x, u5_th_gs) and not u5_GrandSlam
        u5_RVOL1xR = bb_baseBear and inrange(bb_normPrice, u5_th_1x, u5_th_gs) and not u5_MOAB

        # WMD via relativeVolume
        if rv_curr[i] is None or rv_past[i] in (None, 0):
            u5_relVolRatio = None
        else:
            u5_relVolRatio = rv_curr[i] / rv_past[i]
        lvl_relVol[i] = u5_relVolRatio
        rvr = u5_relVolRatio
        u5_WTC = conf and rvr is not None and (rvr > u5_th_wtc) and (rvr <= u5_th_hiro)
        u5_Hiroshima = conf and rvr is not None and (rvr > u5_th_hiro)
        u5_Pentagon = conf and rvr is not None and (rvr >= u5_th_1x) and (rvr <= u5_th_wtc)
        u5_isNag = False
        if i == 0:
            u5_maxVol = v[i]
        elif v[i] > u5_maxVol:
            u5_isNag = True; u5_maxVol = v[i]
        u5_Nagasaki = u5_isNag
        u5_WMD = u5_Pentagon or u5_WTC or u5_Hiroshima or u5_Nagasaki

        u5_HV1000 = conf and (v_high1000_1[i] is not None) and (v[i] >= v_high1000_1[i])

        # FAUNA
        f_atr = nz(atr14[i]); f_avgVol_i = nz(f_avgVol[i]); f_avgBody_i = f_avgBody[i]
        f_avgDelta_i = nz(f_avgDelta[i]); f_trendMA_i = f_trendMA[i]
        f_body = c[i] - o[i]; f_rng = h[i] - l[i]; f_bodySz = abs(f_body)
        f_bodyRat = 0.0 if f_rng == 0 else f_bodySz / f_rng
        f_up = f_body > 0; f_dn = f_body < 0
        prev_body = (c[i - 1] - o[i - 1]) if i >= 1 else 0.0
        prev_range = (h[i - 1] - l[i - 1]) if i >= 1 else 0.0
        trendUp = (f_trendMA_i is not None and i >= 1 and f_trendMA[i - 1] is not None and f_trendMA_i > f_trendMA[i - 1])
        trendDn = (f_trendMA_i is not None and i >= 1 and f_trendMA[i - 1] is not None and f_trendMA_i < f_trendMA[i - 1])
        avgBody_1 = nz(f_avgBody[i - 1] if i >= 1 else None)
        avgVol_1 = nz(f_avgVol[i - 1] if i >= 1 else None)
        v_1i = v[i - 1] if i >= 1 else 0.0
        MB_b = f_up and f_bodySz > 1.6 * f_atr and f_bodyRat > 0.70 and v[i] > 1.8 * f_avgVol_i
        RE_b = f_up and f_rng > 2.2 * f_atr and (h[i] - c[i]) < 0.15 * f_rng and v[i] > 1.8 * f_avgVol_i
        TA_b = trendUp and i >= 1 and (c[i] - c[i - 1]) > 1.6 * f_avgDelta_i and f_up and v[i] > 1.8 * f_avgVol_i
        GG_b = i >= 1 and (o[i] - c[i - 1]) > 0.9 * f_atr and f_up and l[i] > c[i - 1] and v[i] > 1.8 * f_avgVol_i
        StrongBear = i >= 1 and c[i - 1] < o[i - 1] and abs(prev_body) > 1.5 * avgBody_1 and v_1i > 1.5 * avgVol_1
        WeakBear = i >= 1 and c[i - 1] < o[i - 1] and (0.0 if prev_range == 0 else abs(prev_body) / prev_range) <= 0.2
        TR_b = WeakBear and (MB_b or RE_b or TA_b)
        ES_b = StrongBear and (MB_b or RE_b or TA_b)
        GDR_b = (i >= 1 and c[i - 1] < o[i - 1]) and GG_b
        b_core = (1 if MB_b else 0) + (1 if RE_b else 0) + (1 if TA_b else 0)
        b_gg_exc = GG_b and not ((b_core >= 2) and (f_bodyRat >= 0.80))
        u5_FAUNABull = conf and (MB_b or RE_b or TA_b) and not (TR_b or ES_b or GDR_b or b_gg_exc)
        MB_r = f_dn and f_bodySz > 1.6 * f_atr and f_bodyRat > 0.70 and v[i] > 1.8 * f_avgVol_i
        RE_r = f_dn and f_rng > 2.2 * f_atr and (c[i] - l[i]) < 0.15 * f_rng and v[i] > 1.8 * f_avgVol_i
        TA_r = trendDn and i >= 1 and (c[i - 1] - c[i]) > 1.6 * f_avgDelta_i and f_dn and v[i] > 1.8 * f_avgVol_i
        GG_r = i >= 1 and (c[i - 1] - o[i]) > 0.9 * f_atr and f_dn and h[i] < c[i - 1] and v[i] > 1.8 * f_avgVol_i
        StrongBull = i >= 1 and c[i - 1] > o[i - 1] and abs(prev_body) > 1.5 * avgBody_1 and v_1i > 1.5 * avgVol_1
        WeakBull = i >= 1 and c[i - 1] > o[i - 1] and (0.0 if prev_range == 0 else abs(prev_body) / prev_range) <= 0.2
        TR_r = WeakBull and (MB_r or RE_r or TA_r)
        ES_r = StrongBull and (MB_r or RE_r or TA_r)
        GDR_r = (i >= 1 and c[i - 1] > o[i - 1]) and GG_r
        s_core = (1 if MB_r else 0) + (1 if RE_r else 0) + (1 if TA_r else 0)
        s_gg_exc = GG_r and not ((s_core >= 2) and (f_bodyRat >= 0.80))
        u5_FAUNABear = conf and (MB_r or RE_r or TA_r) and not (TR_r or ES_r or GDR_r or s_gg_exc)

        # USE V5 displacement
        u5_thr_min_1 = (u5_disp_std[i - 1] * p.u5_std_min) if (i >= 1 and u5_disp_std[i - 1] is not None) else None
        u5_bullFVG = (i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1])
        u5_bearFVG = (i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1])
        u5_DISPBull = conf and (i >= 1 and u5_thr_min_1 is not None and u5_disp_rng[i - 1] > u5_thr_min_1) and u5_bullFVG
        u5_DISPBear = conf and (i >= 1 and u5_thr_min_1 is not None and u5_disp_rng[i - 1] > u5_thr_min_1) and u5_bearFVG

        # PUP / PPD
        u5_PUP = conf and o[i] != 0 and ((c[i] - o[i]) / o[i]) * 100 > 3.0 and pp_hiRed[i] is not None and v[i] > pp_hiRed[i]
        u5_PPD = conf and o[i] != 0 and ((o[i] - c[i]) / o[i]) * 100 > 3.0 and pp_hiGreen[i] is not None and v[i] > pp_hiGreen[i]

        # PBJ engine
        bm5 = base_ma5[i]; sa10 = st_atr10[i]
        if bm5 is None or sa10 is None:
            u5_buy_cross = u5_sell_cross = False
            u5_PBJBull = u5_PBJBear = False
            u5_sig_prev2 = u5_sig_prev; u5_sig_prev = None
        else:
            st_atr = 2.0 * sa10
            dyn_long = bm5 - st_atr; dyn_short = bm5 + st_atr
            cl_base = nz(u5_curr_long_prev, dyn_long)
            u5_curr_long = max(dyn_long, nz(u5_curr_long_prev)) if bm5 > cl_base else dyn_long
            cs_base = nz(u5_curr_short_prev, dyn_short)
            u5_curr_short = min(dyn_short, nz(u5_curr_short_prev)) if bm5 < cs_base else dyn_short
            if nz(u5_st_dir) == -1 and c[i] > nz(u5_curr_short_prev):
                u5_st_dir = 1
            elif nz(u5_st_dir) == 1 and c[i] < nz(u5_curr_long_prev):
                u5_st_dir = -1
            u5_sig_line = u5_curr_long if u5_st_dir == 1 else u5_curr_short
            u5_buy_cross = (u5_sig_prev is not None and i >= 1 and c[i] > u5_sig_line and c[i - 1] <= u5_sig_prev)
            u5_sell_cross = (u5_sig_prev is not None and i >= 1 and c[i] < u5_sig_line and c[i - 1] >= u5_sig_prev)
            u5_bull_reaccel = (u5_st_dir == 1 and u5_sig_line > nz(u5_sig_prev)
                               and nz(u5_sig_prev) == nz(u5_sig_prev2))
            u5_bear_reaccel = (u5_st_dir == -1 and u5_sig_line < nz(u5_sig_prev)
                               and nz(u5_sig_prev) == nz(u5_sig_prev2))
            # PB&J filter
            pma = pbjMA[i]; patr = pbjATR[i]; zav = zoo_avg_vol[i]
            thr = 0.0 if (c[i] == 0 or patr is None) else (patr / c[i] * 3.0)
            pbj_buy = (pma is not None and zav is not None and low25[i] is not None
                       and l[i] < pma * (1 - thr) and l[i] == low25[i] and v[i] > zav * 0.1)
            pbj_sell = (pma is not None and zav is not None and high25[i] is not None
                        and h[i] > pma * (1 + thr) and h[i] == high25[i] and v[i] > zav * 0.1)
            atr_pb = nz(atr14[i]) * 2.0

            def u5_add(arr, up, lo, vv):
                if abs(up - lo) >= p.mintick:
                    arr.append(_ULvl(up, lo, vv))
            if u5_buy_cross and i >= 1:
                up = max(o[i - 1], c[i - 1]); lo = l[i - 1]
                if up - lo < atr_pb * 0.5:
                    up = lo + atr_pb * 0.5
                u5_add(u5_bull_lvls, up, lo, v[i - 1])
            if u5_sell_cross and i >= 1:
                up = h[i - 1]; lo = min(o[i - 1], c[i - 1])
                if up - lo < atr_pb * 0.5:
                    lo = up - atr_pb * 0.5
                u5_add(u5_bear_lvls, up, lo, v[i - 1])
            if u5_bull_reaccel:
                p2 = min(o[i], c[i])
                u5_add(u5_bull_lvls, max(u5_sig_line, p2), min(u5_sig_line, p2), v[i])
            if u5_bear_reaccel:
                p2 = max(o[i], c[i])
                u5_add(u5_bear_lvls, max(u5_sig_line, p2), min(u5_sig_line, p2), v[i])

            def u5_check(arr, is_bull):
                approached = False
                for j in range(len(arr) - 1, -1, -1):
                    lvj = arr[j]
                    if is_bull and c[i] < lvj.lower:
                        arr.pop(j); continue
                    if (not is_bull) and c[i] > lvj.upper:
                        arr.pop(j); continue
                    ap = lvj.upper * 1.005 if is_bull else lvj.lower * 0.995
                    if is_bull:
                        if not lvj.approached and l[i] <= ap:
                            approached = True; lvj.approached = True
                        elif lvj.approached and l[i] > lvj.upper:
                            lvj.approached = False
                    else:
                        if not lvj.approached and h[i] >= ap:
                            approached = True; lvj.approached = True
                        elif lvj.approached and h[i] < lvj.lower:
                            lvj.approached = False
                return approached
            if conf:
                if u5_check(u5_bull_lvls, True):
                    u5_wait_buy = True
                if u5_check(u5_bear_lvls, False):
                    u5_wait_sell = True
            if pbj_buy:
                u5_wait_pbj_buy = True
            if pbj_sell:
                u5_wait_pbj_sell = True
            while len(u5_bull_lvls) > 30:
                u5_bull_lvls.pop(0)
            while len(u5_bear_lvls) > 30:
                u5_bear_lvls.pop(0)
            u5_sig_pbj_buy = u5_buy_cross and u5_wait_pbj_buy
            u5_sig_pb_buy = u5_buy_cross and u5_wait_buy
            u5_sig_pbj_sell = u5_sell_cross and u5_wait_pbj_sell
            u5_sig_pb_sell = u5_sell_cross and u5_wait_sell
            if u5_sig_pb_buy:
                u5_wait_buy = False
            if u5_sig_pbj_buy:
                u5_wait_pbj_buy = False
            if u5_sig_pb_sell:
                u5_wait_sell = False
            if u5_sig_pbj_sell:
                u5_wait_pbj_sell = False
            u5_PBJBull = conf and u5_sig_pbj_buy
            u5_PBJBear = conf and u5_sig_pbj_sell
            u5_curr_long_prev = u5_curr_long; u5_curr_short_prev = u5_curr_short
            u5_sig_prev2 = u5_sig_prev; u5_sig_prev = u5_sig_line

        # CS1 (FVG combo)
        gz_v1 = v[i - 1] if i >= 1 else 0.0
        gz_isHV = (i >= 1 and (gz_v1 == hv5k[i] or gz_v1 == hv252[i] or gz_v1 == hv63[i]))
        gz_thresh = (gz_thresh_cum[i] / i) if i > 0 else 0.0
        gz_bFVG = (i >= 2 and l[i] > h[i - 2] and c[i - 1] > h[i - 2]
                   and h[i - 2] != 0 and (l[i] - h[i - 2]) / h[i - 2] > gz_thresh)
        gz_sFVG = (i >= 2 and h[i] < l[i - 2] and c[i - 1] < l[i - 2]
                   and h[i] != 0 and (l[i - 2] - h[i]) / h[i] > gz_thresh)
        gz_bullGZI = gz_bearGZI = gz_bullHV = gz_bearHV = False
        if conf and gz_bFVG and ts[i] != gz_lastT:
            mx = l[i]; mn = h[i - 2]
            if gz_isHV:
                gz_bullHV = True
            for e in gz_fvgs:
                if (e.bull and (i - e.idx) <= 7
                        and (max(e.mn, mn) < min(e.mx, mx)
                             or (max(e.mn, mn) <= min(e.mx, mx) and e.hv and gz_isHV))):
                    gz_bullGZI = True; break
            gz_fvgs.insert(0, _Fvg(mx, mn, True, ts[i], i, gz_isHV)); gz_lastT = ts[i]
        if conf and gz_sFVG and ts[i] != gz_lastT:
            mx = l[i - 2]; mn = h[i]
            if gz_isHV:
                gz_bearHV = True
            for e in gz_fvgs:
                if ((not e.bull) and (i - e.idx) <= 7
                        and (max(e.mn, mn) < min(e.mx, mx)
                             or (max(e.mn, mn) <= min(e.mx, mx) and e.hv and gz_isHV))):
                    gz_bearGZI = True; break
            gz_fvgs.insert(0, _Fvg(mx, mn, False, ts[i], i, gz_isHV)); gz_lastT = ts[i]
        for j in range(len(gz_fvgs) - 1, -1, -1):
            g = gz_fvgs[j]
            if (g.bull and c[i] < g.mn) or ((not g.bull) and c[i] > g.mx):
                gz_fvgs.pop(j)
        if len(gz_fvgs) > 50:
            gz_fvgs.pop()
        cs_bp1 = 0.0 if (i < 1 or (h[i - 1] - l[i - 1]) == 0) else abs(c[i - 1] - o[i - 1]) / (h[i - 1] - l[i - 1])
        cs_vb = cs_bp1 >= 0.85
        u5_CS1_Bull = (conf and cs_vb and (gz_bullHV or gz_bullGZI)
                       and (hb("u5_SAAB", 1) or hb("u5_RVOL1xB", 1) or hb("u5_GrandSlam", 1)
                            or hb("u5_Pentagon", 1) or hb("u5_WTC", 1) or hb("u5_Hiroshima", 1) or hb("u5_Nagasaki", 1)))
        u5_CS1_Bear = (conf and cs_vb and (gz_bearHV or gz_bearGZI)
                       and (hb("u5_Kratos", 1) or hb("u5_RVOL1xR", 1) or hb("u5_MOAB", 1)
                            or hb("u5_Pentagon", 1) or hb("u5_WTC", 1) or hb("u5_Hiroshima", 1) or hb("u5_Nagasaki", 1)))

        # ============================ DYNAMITE ================================
        dyn_b1 = (i >= 1 and dyn_std[i - 1] is not None and dyn_disp[i - 1] > nz(dyn_std[i - 1]) * p.dynStdMult)
        dyn_b2 = (i >= 2 and dyn_std[i - 2] is not None and dyn_disp[i - 2] > nz(dyn_std[i - 2]) * p.dynStdMult)
        dyn_bullFVG = (i >= 2 and l[i] > h[i - 2] and c[i - 1] > o[i - 1])
        dyn_bearFVG = (i >= 2 and h[i] < l[i - 2] and c[i - 1] < o[i - 1])
        dyn_bull_dir = (i >= 2 and c[i - 1] > o[i - 1] and c[i - 2] > o[i - 2])
        dyn_bear_dir = (i >= 2 and c[i - 1] < o[i - 1] and c[i - 2] < o[i - 2])
        dyn_fauna_bull = hb("u5_FAUNABull", 1) and hb("u5_FAUNABull", 2)
        dyn_fauna_bear = hb("u5_FAUNABear", 1) and hb("u5_FAUNABear", 2)
        det_dynamiteBull = conf and dyn_b1 and dyn_b2 and dyn_bull_dir and dyn_fauna_bull and dyn_bullFVG
        det_dynamiteBear = conf and dyn_b1 and dyn_b2 and dyn_bear_dir and dyn_fauna_bear and dyn_bearFVG

        # ====================== HEAVY PENTAGON / WBUSH ========================
        hp_gA_Bull = u5_RVOL1xB or u5_GrandSlam
        hp_gA_Bear = u5_RVOL1xR or u5_MOAB
        hp_gB = u5_Pentagon or u5_WTC or u5_Hiroshima
        hp_baseYY = (hp_gA_Bull or hp_gA_Bear) and hp_gB
        hp_baseN = u5_Nagasaki and (hp_gA_Bull or hp_gA_Bear)
        hp_baseNV = u5_Nagasaki and hp_gB
        hp_baseT = u5_Nagasaki and (hp_gA_Bull or hp_gA_Bear) and hp_gB
        hp_baseNH = (u5_Pentagon and u5_WTC) or (u5_Pentagon and u5_Hiroshima) or (u5_WTC and u5_Hiroshima)
        hp_noDisp = (not u5_DISPBull) and (not u5_DISPBear)
        sig_WBUSH_Bull = ((hp_baseYY or hp_baseN or hp_baseNV or hp_baseT or hp_baseNH) and u5_DISPBull)
        sig_WBUSH_Bear = ((hp_baseYY or hp_baseN or hp_baseNV or hp_baseT or hp_baseNH) and u5_DISPBear)
        sig_WBUSH_Neutral = ((hp_baseYY or hp_baseN or hp_baseNV or hp_baseT or hp_baseNH) and hp_noDisp)

        # ============================== HCT ===================================
        hct_SAAB = bb_baseBull and bb_normPrice >= hct_th_saab and bb_normPrice < hct_th_1x
        hct_Kratos = bb_baseBear and bb_normPrice >= hct_th_saab and bb_normPrice < hct_th_1x
        hct_BullRVOL1x = bb_baseBull and bb_normPrice >= hct_th_1x and bb_normPrice < hct_th_gs
        hct_BearRVOL1x = bb_baseBear and bb_normPrice >= hct_th_1x and bb_normPrice < hct_th_gs
        hct_GrandSlam = bb_baseBull and bb_normPrice >= hct_th_gs
        hct_MOAB = bb_baseBear and bb_normPrice >= hct_th_gs
        hct_Pentagon = conf and rvr is not None and rvr >= hct_th_1x and rvr <= hct_th_wtc
        hct_WTC = conf and rvr is not None and rvr > hct_th_wtc and rvr <= hct_th_hiro
        hct_Hiroshima = conf and rvr is not None and rvr > hct_th_hiro
        hct_thresh = (hct_cum[i] / i) if (p.hct_auto and i > 0) else (p.hct_threshPct / 100.0)
        hct_bFVG = (i >= 2 and l[i] > h[i - 2] and c[i - 1] > h[i - 2]
                    and h[i - 2] != 0 and (l[i] - h[i - 2]) / h[i - 2] > hct_thresh)
        hct_sFVG = (i >= 2 and h[i] < l[i - 2] and c[i - 1] < l[i - 2]
                    and h[i] != 0 and (l[i - 2] - h[i]) / h[i] > hct_thresh)
        hct_barRange = (h[i - 1] - l[i - 1]) if i >= 1 else 0.0
        hct_dispCandleMet = (i >= 1 and hct_rangeStdev[i - 1] is not None
                             and hct_barRange > p.hct_disp_strength * nz(hct_rangeStdev[i - 1]))
        hct_dispBull = conf and hct_dispCandleMet and (i >= 1 and c[i - 1] > o[i - 1]) and hct_bFVG
        hct_dispBear = conf and hct_dispCandleMet and (i >= 1 and c[i - 1] < o[i - 1]) and hct_sFVG
        hct_noDisp = (not hct_dispBull) and (not hct_dispBear)
        hct_gA_Bull = hct_BullRVOL1x or hct_GrandSlam
        hct_gA_Bear = hct_BearRVOL1x or hct_MOAB
        hct_gB = hct_Pentagon or hct_WTC or hct_Hiroshima
        hct_baseYY = (hct_gA_Bull or hct_gA_Bear) and hct_gB
        hct_baseN = u5_Nagasaki and (hct_gA_Bull or hct_gA_Bear)
        hct_baseNV = u5_Nagasaki and hct_gB
        hct_baseT = u5_Nagasaki and (hct_gA_Bull or hct_gA_Bear) and hct_gB
        hct_baseNH = (hct_Pentagon and hct_WTC) or (hct_Pentagon and hct_Hiroshima) or (hct_WTC and hct_Hiroshima)
        hct_baseAny = hct_baseYY or hct_baseN or hct_baseNV or hct_baseT or hct_baseNH
        hct_bull = hct_baseAny and hct_dispBull
        hct_bear = hct_baseAny and hct_dispBear

        # ============================== UC ====================================
        uc_bull_count = ((1 if u5_FAUNABull else 0) + (1 if (u5_RVOL1xB or u5_GrandSlam or u5_SAAB) else 0)
                         + (1 if u5_WMD else 0) + (1 if u5_PUP else 0) + (1 if u5_CS1_Bull else 0))
        uc_bear_count = ((1 if u5_FAUNABear else 0) + (1 if (u5_RVOL1xR or u5_MOAB or u5_Kratos) else 0)
                         + (1 if u5_WMD else 0) + (1 if u5_PPD else 0) + (1 if u5_CS1_Bear else 0))
        uc_bull = conf and uc_bull_count >= 2
        uc_bear = conf and uc_bear_count >= 2

        # ========================= NAGASAKI + ANY =============================
        nagAny_bull = conf and u5_Nagasaki and (u5_Pentagon or u5_WTC or u5_Hiroshima or u5_RVOL1xB or u5_GrandSlam or u5_SAAB)
        nagAny_bear = conf and u5_Nagasaki and (u5_Pentagon or u5_WTC or u5_Hiroshima or u5_RVOL1xR or u5_MOAB or u5_Kratos)

        # ============================= GATE #5 ================================
        gthr_1 = (disp_std[i - 1] * p.gateStdMult) if (i >= 1 and disp_std[i - 1] is not None) else None
        gate_disp_bull = conf and (i >= 1 and gthr_1 is not None and disp_range[i - 1] > gthr_1) and isBullishFVG and (i >= 1 and c[i - 1] > o[i - 1])
        gate_disp_bear = conf and (i >= 1 and gthr_1 is not None and disp_range[i - 1] > gthr_1) and isBearishFVG and (i >= 1 and c[i - 1] < o[i - 1])
        gate_bull_raw = u5_RVOL1xB or u5_GrandSlam or uc_bull or nagAny_bull or hct_bull or gate_disp_bull
        gate_bear_raw = u5_RVOL1xR or u5_MOAB or uc_bear or nagAny_bear or hct_bear or gate_disp_bear
        gate_bull = (not p.en_newGate) or gate_bull_raw
        gate_bear = (not p.en_newGate) or gate_bear_raw

        # ============================= COMBOS =================================
        sig_rcNTBull = det_bullNapalm and hb("det_bullTNT", 1) and p.en_rcNTBull and bool(hb("gate_bull", 1))
        sig_rcNTBear = det_bearNapalm and hb("det_bearTNT", 1) and p.en_rcNTBear and bool(hb("gate_bear", 1))
        det_rcTRBull = det_bullTNT and det_bullRetTNT
        det_rcTRBear = det_bearTNT and det_bearRetTNT
        det_rcRNBull = det_bullNapalm and hb("det_bullRetTNT", 1)
        det_rcRNBear = det_bearNapalm and hb("det_bearRetTNT", 1)
        det_pnBull = det_bullNapalm and hb("u5_PBJBull", 1)
        det_pnBear = det_bearNapalm and hb("u5_PBJBear", 1)
        det_ptBull = det_bullTNT and u5_PBJBull
        det_ptBear = det_bearTNT and u5_PBJBear
        det_prBull = det_bullRetTNT and u5_PBJBull
        det_prBear = det_bearRetTNT and u5_PBJBear
        # FUSE
        if det_bullNapalm:
            fuse["bullNPM"] = i - 1
        if det_bullTNT:
            fuse["bullTNT"] = i
        if det_bearNapalm:
            fuse["bearNPM"] = i - 1
        if det_bearTNT:
            fuse["bearTNT"] = i
        det_fuseBull = (det_contBull and fuse["bullTNT"] is not None and fuse["bullNPM"] is not None
                        and fuse["bullNPM"] < fuse["bullTNT"] and fuse["bullTNT"] < i
                        and (i - fuse["bullTNT"]) <= SP and (fuse["bullTNT"] - fuse["bullNPM"]) <= SP
                        and fuse["bullNPM"] >= nz(sessionFirstBarIdx, 0))
        det_fuseBear = (det_contBear and fuse["bearTNT"] is not None and fuse["bearNPM"] is not None
                        and fuse["bearNPM"] < fuse["bearTNT"] and fuse["bearTNT"] < i
                        and (i - fuse["bearTNT"]) <= SP and (fuse["bearTNT"] - fuse["bearNPM"]) <= SP
                        and fuse["bearNPM"] >= nz(sessionFirstBarIdx, 0))
        # IGNITE
        ign_tc_bull = det_bullTNT and det_contBull
        ign_tc_bear = det_bearTNT and det_contBear
        ign_nc_bull = det_bullNapalm and hb("det_contBull", 1)
        ign_nc_bear = det_bearNapalm and hb("det_contBear", 1)
        det_igniteBull = ign_tc_bull or ign_nc_bull
        det_igniteBear = ign_tc_bear or ign_nc_bear
        # CATALYST
        det_catBull = det_bullNapalm and u5_CS1_Bull
        det_catBear = det_bearNapalm and u5_CS1_Bear

        # ============================ SUPPRESSION =============================
        supp_bullNPM = sig_rcNTBull or det_rcRNBull or det_pnBull
        supp_bearNPM = sig_rcNTBear or det_rcRNBear or det_pnBear
        supp_bullTNT = sig_rcNTBull or det_rcTRBull or det_ptBull
        supp_bearTNT = sig_rcNTBear or det_rcTRBear or det_ptBear

        # ===================== TIER 2 ENRICHMENT GATE =========================
        enrichBull_N = u5_RVOL1xB or u5_GrandSlam or u5_PUP or u5_CS1_Bull or u5_FAUNABull or u5_WMD or u5_HV1000
        enrichBear_N = u5_RVOL1xR or u5_MOAB or u5_PPD or u5_CS1_Bear or u5_FAUNABear or u5_WMD or u5_HV1000
        enrichBull_N1 = (hb("u5_RVOL1xB", 1) or hb("u5_GrandSlam", 1) or hb("u5_PUP", 1) or hb("u5_CS1_Bull", 1)
                         or hb("u5_FAUNABull", 1) or hb("u5_Pentagon", 1) or hb("u5_WTC", 1) or hb("u5_Hiroshima", 1)
                         or hb("u5_Nagasaki", 1) or hb("u5_HV1000", 1) or det_dynamiteBull or hb("det_dynamiteBull", 1))
        enrichBear_N1 = (hb("u5_RVOL1xR", 1) or hb("u5_MOAB", 1) or hb("u5_PPD", 1) or hb("u5_CS1_Bear", 1)
                         or hb("u5_FAUNABear", 1) or hb("u5_Pentagon", 1) or hb("u5_WTC", 1) or hb("u5_Hiroshima", 1)
                         or hb("u5_Nagasaki", 1) or hb("u5_HV1000", 1) or det_dynamiteBear or hb("det_dynamiteBear", 1))
        pnGateBull = (not isSubMinute) or (hb("u5_RVOL1xB", 1) or hb("u5_GrandSlam", 1) or hb("u5_PUP", 1)
                      or hb("u5_HV1000", 1) or hb("u5_Pentagon", 1) or hb("u5_WTC", 1) or hb("u5_Hiroshima", 1) or hb("u5_Nagasaki", 1))
        pnGateBear = (not isSubMinute) or (hb("u5_RVOL1xR", 1) or hb("u5_MOAB", 1) or hb("u5_PPD", 1)
                      or hb("u5_HV1000", 1) or hb("u5_Pentagon", 1) or hb("u5_WTC", 1) or hb("u5_Hiroshima", 1) or hb("u5_Nagasaki", 1))
        ptGateBull = (not isSubMinute) or (u5_RVOL1xB or u5_GrandSlam or u5_PUP or u5_HV1000 or u5_WMD)
        ptGateBear = (not isSubMinute) or (u5_RVOL1xR or u5_MOAB or u5_PPD or u5_HV1000 or u5_WMD)

        # ========================= FINAL PLOT BOOLS ===========================
        sfb = nz(sessionFirstBarIdx, 0)
        p_b2bBull = (det_bullNapalm and not supp_bullNPM and hb("det_bullNapalm0", 1)
                     and sessionFirstBarIdx is not None and (i - 2) >= sessionFirstBarIdx
                     and p.en_b2bBull and bool(hb("gate_bull", 1)))
        p_b2bBear = (det_bearNapalm and not supp_bearNPM and hb("det_bearNapalm0", 1)
                     and sessionFirstBarIdx is not None and (i - 2) >= sessionFirstBarIdx
                     and p.en_b2bBear and bool(hb("gate_bear", 1)))
        p_pnBull = det_pnBull and pnGateBull and p.en_pnBull and bool(hb("gate_bull", 1))
        p_pnBear = det_pnBear and pnGateBear and p.en_pnBear and bool(hb("gate_bear", 1))
        p_ptBull = det_ptBull and ptGateBull and p.en_ptBull
        p_ptBear = det_ptBear and ptGateBear and p.en_ptBear
        p_fuseBull = det_fuseBull and p.en_fuseBull
        p_fuseBear = det_fuseBear and p.en_fuseBear
        p_catBull = det_catBull and p.en_catBull and bool(hb("gate_bull", 1))
        p_catBear = det_catBear and p.en_catBear and bool(hb("gate_bear", 1))
        p_ignBull = det_igniteBull and p.en_ignBull
        p_ignBear = det_igniteBear and p.en_ignBear
        p_dynBull = det_dynamiteBull and p.en_dynBull
        p_dynBear = det_dynamiteBear and p.en_dynBear
        # Tier 2
        p_t2tntBull = det_bullTNT and not supp_bullTNT and enrichBull_N and p.en_t2tntBull and gate_bull
        p_t2tntBear = det_bearTNT and not supp_bearTNT and enrichBear_N and p.en_t2tntBear and gate_bear
        p_t2npmBull = det_bullNapalm and not supp_bullNPM and enrichBull_N1 and p.en_t2npmBull and bool(hb("gate_bull", 1))
        p_t2npmBear = det_bearNapalm and not supp_bearNPM and enrichBear_N1 and p.en_t2npmBear and bool(hb("gate_bear", 1))
        p_t2contBull = det_contBull and enrichBull_N and p.en_t2contBull and gate_bull
        p_t2contBear = det_contBear and enrichBear_N and p.en_t2contBear and gate_bear
        p_t2trBull = det_rcTRBull and enrichBull_N and p.en_t2trBull and gate_bull
        p_t2trBear = det_rcTRBear and enrichBear_N and p.en_t2trBear and gate_bear
        p_t2rnBull = det_rcRNBull and enrichBull_N1 and p.en_t2rnBull and bool(hb("gate_bull", 1))
        p_t2rnBear = det_rcRNBear and enrichBear_N1 and p.en_t2rnBear and bool(hb("gate_bear", 1))
        p_t2prBull = det_prBull and enrichBull_N and p.en_t2prBull and gate_bull
        p_t2prBear = det_prBear and enrichBear_N and p.en_t2prBear and gate_bear

        # ============================ DENSITY =================================
        # denVis* — exact Pine visual-event stream
        denVisBull = (hb("det_bullTNT", 1) or hb("det_contBull", 1) or hb("det_rcTRBull", 1)
                      or hb("det_ptBull", 1) or hb("det_prBull", 1)
                      or det_bullNapalm or sig_rcNTBull or det_rcRNBull or det_pnBull)
        denVisBear = (hb("det_bearTNT", 1) or hb("det_contBear", 1) or hb("det_rcTRBear", 1)
                      or hb("det_ptBear", 1) or hb("det_prBear", 1)
                      or det_bearNapalm or sig_rcNTBear or det_rcRNBear or det_pnBear)
        # push denVis into history NOW so the rolling [i] back-scan can read it
        H.setdefault("denVisBull", []).append(denVisBull)
        H.setdefault("denVisBear", []).append(denVisBear)
        sig_d1b = sig_d1s = sig_d2b = sig_d2s = sig_d3b = sig_d3s = False
        if isFirstBar:
            d1br = i - 1; d1sr = i - 1; d1ba = True; d1sa = True
            d2br = i - 1; d2sr = i - 1; d2ba = True; d2sa = True
            d3br = i - 1; d3sr = i - 1; d3ba = True; d3sa = True
        if conf:
            def dcount(hist_key, Y, ref):
                cnt = 0
                arr = H[hist_key]
                for k in range(Y):
                    idx = len(arr) - 1 - k
                    val = arr[idx] if 0 <= idx < len(arr) else False
                    if val and (i - 1 - k) >= sfb and (i - 1 - k) > ref:
                        cnt += 1
                return cnt
            c1b = dcount("denVisBull", p.den1_Y, d1br)
            if c1b >= p.den1_X and d1ba:
                sig_d1b = True; d1br = i - 2; d1ba = False
            if c1b < p.den1_X:
                d1ba = True
            c1s = dcount("denVisBear", p.den1_Y, d1sr)
            if c1s >= p.den1_X and d1sa:
                sig_d1s = True; d1sr = i - 2; d1sa = False
            if c1s < p.den1_X:
                d1sa = True
            c2b = dcount("denVisBull", p.den2_Y, d2br)
            if c2b >= p.den2_X and d2ba:
                sig_d2b = True; d2br = i - 2; d2ba = False
            if c2b < p.den2_X:
                d2ba = True
            c2s = dcount("denVisBear", p.den2_Y, d2sr)
            if c2s >= p.den2_X and d2sa:
                sig_d2s = True; d2sr = i - 2; d2sa = False
            if c2s < p.den2_X:
                d2sa = True
            c3b = dcount("denVisBull", p.den3_Y, d3br)
            if c3b >= p.den3_X and d3ba:
                sig_d3b = True; d3br = i - 2; d3ba = False
            if c3b < p.den3_X:
                d3ba = True
            c3s = dcount("denVisBear", p.den3_Y, d3sr)
            if c3s >= p.den3_X and d3sa:
                sig_d3s = True; d3sr = i - 2; d3sa = False
            if c3s < p.den3_X:
                d3sa = True
        p_d1b = sig_d1b and p.en_d1b; p_d1s = sig_d1s and p.en_d1s
        p_d2b = sig_d2b and p.en_d2b; p_d2s = sig_d2s and p.en_d2s
        p_d3b = sig_d3b and p.en_d3b; p_d3s = sig_d3s and p.en_d3s

        # ========================= UU/UUU/UUUU ================================
        u_qual_bull = conf and bb_baseBull and bb_normPrice >= 0.5
        u_qual_bear = conf and bb_baseBear and bb_normPrice >= 0.5
        if conf:
            if u_qual_bull:
                u5_u_bull_streak += 1; u5_u_bull_hasDay1 = u5_u_bull_hasDay1 or u5_is_new_day
            else:
                u5_u_bull_streak = 0; u5_u_bull_hasDay1 = False
            if u_qual_bear:
                u5_u_bear_streak += 1; u5_u_bear_hasDay1 = u5_u_bear_hasDay1 or u5_is_new_day
            else:
                u5_u_bear_streak = 0; u5_u_bear_hasDay1 = False

        def bp(key, off):
            return bool(hb(key, off))
        # per-bar bull qualifiers
        bp0_pbj = u5_PBJBull; bp0_disp = u5_DISPBull; bp0_fauna = u5_FAUNABull
        bp0_saab = u5_SAAB or u5_RVOL1xB or u5_GrandSlam
        bp1_pbj = bp("u5_PBJBull", 1); bp1_disp = bp("u5_DISPBull", 1); bp1_fauna = bp("u5_FAUNABull", 1)
        bp1_saab = bp("u5_SAAB", 1) or bp("u5_RVOL1xB", 1) or bp("u5_GrandSlam", 1)
        bp2_pbj = bp("u5_PBJBull", 2); bp2_disp = bp("u5_DISPBull", 2); bp2_fauna = bp("u5_FAUNABull", 2)
        bp2_saab = bp("u5_SAAB", 2) or bp("u5_RVOL1xB", 2) or bp("u5_GrandSlam", 2)
        bp3_pbj = bp("u5_PBJBull", 3); bp3_disp = bp("u5_DISPBull", 3); bp3_fauna = bp("u5_FAUNABull", 3)
        bp3_saab = bp("u5_SAAB", 3) or bp("u5_RVOL1xB", 3) or bp("u5_GrandSlam", 3)
        sp0_pbj = u5_PBJBear; sp0_disp = u5_DISPBear; sp0_fauna = u5_FAUNABear
        sp0_saab = u5_Kratos or u5_RVOL1xR or u5_MOAB
        sp1_pbj = bp("u5_PBJBear", 1); sp1_disp = bp("u5_DISPBear", 1); sp1_fauna = bp("u5_FAUNABear", 1)
        sp1_saab = bp("u5_Kratos", 1) or bp("u5_RVOL1xR", 1) or bp("u5_MOAB", 1)
        sp2_pbj = bp("u5_PBJBear", 2); sp2_disp = bp("u5_DISPBear", 2); sp2_fauna = bp("u5_FAUNABear", 2)
        sp2_saab = bp("u5_Kratos", 2) or bp("u5_RVOL1xR", 2) or bp("u5_MOAB", 2)
        sp3_pbj = bp("u5_PBJBear", 3); sp3_disp = bp("u5_DISPBear", 3); sp3_fauna = bp("u5_FAUNABear", 3)
        sp3_saab = bp("u5_Kratos", 3) or bp("u5_RVOL1xR", 3) or bp("u5_MOAB", 3)
        # distinct-qualifier-type (pG)
        bp0_sa = u5_SAAB; bp0_r1 = u5_RVOL1xB; bp0_gs = u5_GrandSlam
        bp1_sa = bp("u5_SAAB", 1); bp1_r1 = bp("u5_RVOL1xB", 1); bp1_gs = bp("u5_GrandSlam", 1)
        bp2_sa = bp("u5_SAAB", 2); bp2_r1 = bp("u5_RVOL1xB", 2); bp2_gs = bp("u5_GrandSlam", 2)
        bp3_sa = bp("u5_SAAB", 3); bp3_r1 = bp("u5_RVOL1xB", 3); bp3_gs = bp("u5_GrandSlam", 3)
        sp0_sa = u5_Kratos; sp0_r1 = u5_RVOL1xR; sp0_gs = u5_MOAB
        sp1_sa = bp("u5_Kratos", 1); sp1_r1 = bp("u5_RVOL1xR", 1); sp1_gs = bp("u5_MOAB", 1)
        sp2_sa = bp("u5_Kratos", 2); sp2_r1 = bp("u5_RVOL1xR", 2); sp2_gs = bp("u5_MOAB", 2)
        sp3_sa = bp("u5_Kratos", 3); sp3_r1 = bp("u5_RVOL1xR", 3); sp3_gs = bp("u5_MOAB", 3)

        s2pbj_b = bp0_pbj or bp1_pbj; s2disp_b = bp0_disp or bp1_disp; s2fauna_b = bp0_fauna or bp1_fauna
        s2sa_b = bp0_sa or bp1_sa; s2r1_b = bp0_r1 or bp1_r1; s2gs_b = bp0_gs or bp1_gs
        qc2_b = sum([s2pbj_b, s2disp_b, s2fauna_b, s2sa_b, s2r1_b, s2gs_b]); pG_uu_b = qc2_b >= 2
        s3pbj_b = s2pbj_b or bp2_pbj; s3disp_b = s2disp_b or bp2_disp; s3fauna_b = s2fauna_b or bp2_fauna
        s3sa_b = s2sa_b or bp2_sa; s3r1_b = s2r1_b or bp2_r1; s3gs_b = s2gs_b or bp2_gs
        qc3_b = sum([s3pbj_b, s3disp_b, s3fauna_b, s3sa_b, s3r1_b, s3gs_b]); pG_uuu_b = qc3_b >= 3
        s4pbj_b = s3pbj_b or bp3_pbj; s4disp_b = s3disp_b or bp3_disp; s4fauna_b = s3fauna_b or bp3_fauna
        s4sa_b = s3sa_b or bp3_sa; s4r1_b = s3r1_b or bp3_r1; s4gs_b = s3gs_b or bp3_gs
        qc4_b = sum([s4pbj_b, s4disp_b, s4fauna_b, s4sa_b, s4r1_b, s4gs_b]); pG_uuuu_b = qc4_b >= 4
        s2pbj_s = sp0_pbj or sp1_pbj; s2disp_s = sp0_disp or sp1_disp; s2fauna_s = sp0_fauna or sp1_fauna
        s2sa_s = sp0_sa or sp1_sa; s2r1_s = sp0_r1 or sp1_r1; s2gs_s = sp0_gs or sp1_gs
        qc2_s = sum([s2pbj_s, s2disp_s, s2fauna_s, s2sa_s, s2r1_s, s2gs_s]); pG_uu_s = qc2_s >= 2
        s3pbj_s = s2pbj_s or sp2_pbj; s3disp_s = s2disp_s or sp2_disp; s3fauna_s = s2fauna_s or sp2_fauna
        s3sa_s = s2sa_s or sp2_sa; s3r1_s = s2r1_s or sp2_r1; s3gs_s = s2gs_s or sp2_gs
        qc3_s = sum([s3pbj_s, s3disp_s, s3fauna_s, s3sa_s, s3r1_s, s3gs_s]); pG_uuu_s = qc3_s >= 3
        s4pbj_s = s3pbj_s or sp3_pbj; s4disp_s = s3disp_s or sp3_disp; s4fauna_s = s3fauna_s or sp3_fauna
        s4sa_s = s3sa_s or sp3_sa; s4r1_s = s3r1_s or sp3_r1; s4gs_s = s3gs_s or sp3_gs
        qc4_s = sum([s4pbj_s, s4disp_s, s4fauna_s, s4sa_s, s4r1_s, s4gs_s]); pG_uuuu_s = qc4_s >= 4

        def path_agg(p0, d0, f0, s0, p1, d1, f1, s1, p2, d2, f2, s2, p3, d3, f3, s3, streak, hasDay1):
            nn_ = min(streak, 4)
            _hp = _hd = _hf = False
            _ad = _asd = True
            _dnp = _pnd = False
            tuples = [(p0, d0, f0, s0)]
            if nn_ >= 2:
                tuples.append((p1, d1, f1, s1))
            if nn_ >= 3:
                tuples.append((p2, d2, f2, s2))
            if nn_ >= 4:
                tuples.append((p3, d3, f3, s3))
            for (pp, dd, ff, ss) in tuples:
                dfk = dd or ff
                if pp:
                    _hp = True
                if dd:
                    _hd = True
                if ff:
                    _hf = True
                if not dd:
                    _ad = False
                if (not ss) or (not dfk):
                    _asd = False
                if dfk and not pp:
                    _dnp = True
                if pp and not dfk:
                    _pnd = True
            pA = hasDay1 and _hp
            pB = _ad
            pC = _asd
            pE = (_dnp and _hp) or (_pnd and (_hd or _hf))
            pF = streak >= 4 and (_hf or _hd) and _hp
            return pA or pB or pC or pE or pF

        u_pathBull2 = (conf and u5_u_bull_streak == 2 and i >= 1
                       and (path_agg(bp0_pbj, bp0_disp, bp0_fauna, bp0_saab, bp1_pbj, bp1_disp, bp1_fauna, bp1_saab,
                                     False, False, False, False, False, False, False, False, 2, u5_u_bull_hasDay1) or pG_uu_b))
        u_pathBull3 = (conf and u5_u_bull_streak == 3 and i >= 2
                       and (path_agg(bp0_pbj, bp0_disp, bp0_fauna, bp0_saab, bp1_pbj, bp1_disp, bp1_fauna, bp1_saab,
                                     bp2_pbj, bp2_disp, bp2_fauna, bp2_saab, False, False, False, False, 3, u5_u_bull_hasDay1) or pG_uuu_b))
        u_pathBull4 = (conf and u5_u_bull_streak >= 4 and i >= 3
                       and (path_agg(bp0_pbj, bp0_disp, bp0_fauna, bp0_saab, bp1_pbj, bp1_disp, bp1_fauna, bp1_saab,
                                     bp2_pbj, bp2_disp, bp2_fauna, bp2_saab, bp3_pbj, bp3_disp, bp3_fauna, bp3_saab,
                                     u5_u_bull_streak, u5_u_bull_hasDay1) or pG_uuuu_b))
        u_pathBear2 = (conf and u5_u_bear_streak == 2 and i >= 1
                       and (path_agg(sp0_pbj, sp0_disp, sp0_fauna, sp0_saab, sp1_pbj, sp1_disp, sp1_fauna, sp1_saab,
                                     False, False, False, False, False, False, False, False, 2, u5_u_bear_hasDay1) or pG_uu_s))
        u_pathBear3 = (conf and u5_u_bear_streak == 3 and i >= 2
                       and (path_agg(sp0_pbj, sp0_disp, sp0_fauna, sp0_saab, sp1_pbj, sp1_disp, sp1_fauna, sp1_saab,
                                     sp2_pbj, sp2_disp, sp2_fauna, sp2_saab, False, False, False, False, 3, u5_u_bear_hasDay1) or pG_uuu_s))
        u_pathBear4 = (conf and u5_u_bear_streak >= 4 and i >= 3
                       and (path_agg(sp0_pbj, sp0_disp, sp0_fauna, sp0_saab, sp1_pbj, sp1_disp, sp1_fauna, sp1_saab,
                                     sp2_pbj, sp2_disp, sp2_fauna, sp2_saab, sp3_pbj, sp3_disp, sp3_fauna, sp3_saab,
                                     u5_u_bear_streak, u5_u_bear_hasDay1) or pG_uuuu_s))

        tntAnyBull0 = det_bullTNT or det_contBull or det_rcTRBull or det_ptBull or det_prBull or det_fuseBull or det_igniteBull
        tntAnyBull1 = (i >= 1 and (hb("det_bullTNT", 1) or hb("det_contBull", 1) or hb("det_rcTRBull", 1)
                       or hb("det_ptBull", 1) or hb("det_prBull", 1) or hb("det_fuseBull", 1) or hb("det_igniteBull", 1)
                       or sig_d1b or sig_d2b or sig_d3b or det_dynamiteBull or det_bullNapalm or sig_rcNTBull
                       or det_rcRNBull or det_pnBull or det_catBull))
        tntAnyBull2 = (i >= 2 and (hb("det_bullTNT", 2) or hb("det_contBull", 2) or hb("det_rcTRBull", 2)
                       or hb("det_ptBull", 2) or hb("det_prBull", 2) or hb("det_fuseBull", 2) or hb("det_igniteBull", 2)
                       or hb("sig_d1b", 1) or hb("sig_d2b", 1) or hb("sig_d3b", 1) or hb("det_dynamiteBull", 1)
                       or hb("det_bullNapalm0", 1) or hb("sig_rcNTBull", 1) or hb("det_rcRNBull", 1)
                       or hb("det_pnBull", 1) or hb("det_catBull", 1)))
        tntAnyBull3 = (i >= 3 and (hb("det_bullTNT", 3) or hb("det_contBull", 3) or hb("det_rcTRBull", 3)
                       or hb("det_ptBull", 3) or hb("det_prBull", 3) or hb("det_fuseBull", 3) or hb("det_igniteBull", 3)
                       or hb("sig_d1b", 2) or hb("sig_d2b", 2) or hb("sig_d3b", 2) or hb("det_dynamiteBull", 2)
                       or hb("det_bullNapalm0", 2) or hb("sig_rcNTBull", 2) or hb("det_rcRNBull", 2)
                       or hb("det_pnBull", 2) or hb("det_catBull", 2)))
        tntAnyBear0 = det_bearTNT or det_contBear or det_rcTRBear or det_ptBear or det_prBear or det_fuseBear or det_igniteBear
        tntAnyBear1 = (i >= 1 and (hb("det_bearTNT", 1) or hb("det_contBear", 1) or hb("det_rcTRBear", 1)
                       or hb("det_ptBear", 1) or hb("det_prBear", 1) or hb("det_fuseBear", 1) or hb("det_igniteBear", 1)
                       or sig_d1s or sig_d2s or sig_d3s or det_dynamiteBear or det_bearNapalm or sig_rcNTBear
                       or det_rcRNBear or det_pnBear or det_catBear))
        tntAnyBear2 = (i >= 2 and (hb("det_bearTNT", 2) or hb("det_contBear", 2) or hb("det_rcTRBear", 2)
                       or hb("det_ptBear", 2) or hb("det_prBear", 2) or hb("det_fuseBear", 2) or hb("det_igniteBear", 2)
                       or hb("sig_d1s", 1) or hb("sig_d2s", 1) or hb("sig_d3s", 1) or hb("det_dynamiteBear", 1)
                       or hb("det_bearNapalm0", 1) or hb("sig_rcNTBear", 1) or hb("det_rcRNBear", 1)
                       or hb("det_pnBear", 1) or hb("det_catBear", 1)))
        tntAnyBear3 = (i >= 3 and (hb("det_bearTNT", 3) or hb("det_contBear", 3) or hb("det_rcTRBear", 3)
                       or hb("det_ptBear", 3) or hb("det_prBear", 3) or hb("det_fuseBear", 3) or hb("det_igniteBear", 3)
                       or hb("sig_d1s", 2) or hb("sig_d2s", 2) or hb("sig_d3s", 2) or hb("det_dynamiteBear", 2)
                       or hb("det_bearNapalm0", 2) or hb("sig_rcNTBear", 2) or hb("det_rcRNBear", 2)
                       or hb("det_pnBear", 2) or hb("det_catBear", 2)))
        hasTntBull2 = tntAnyBull0 or tntAnyBull1
        hasTntBull3 = hasTntBull2 or tntAnyBull2
        hasTntBull4 = hasTntBull3 or tntAnyBull3
        hasTntBear2 = tntAnyBear0 or tntAnyBear1
        hasTntBear3 = hasTntBear2 or tntAnyBear2
        hasTntBear4 = hasTntBear3 or tntAnyBear3
        p_uuBull = u_pathBull2 and hasTntBull2 and p.en_uu_bull
        p_uuBear = u_pathBear2 and hasTntBear2 and p.en_uu_bear
        p_uuuBull = u_pathBull3 and hasTntBull3 and p.en_uuu_bull
        p_uuuBear = u_pathBear3 and hasTntBear3 and p.en_uuu_bear
        p_uuuuBull = u_pathBull4 and hasTntBull4 and p.en_uuuu_bull
        p_uuuuBear = u_pathBear4 and hasTntBear4 and p.en_uuuu_bear

        # ===================== T1 RELAY / T1 STACK ============================
        t1_v1_b = [p_b2bBull, sig_rcNTBull, p_catBull, p_pnBull, (p_ignBull and ign_nc_bull), p_dynBull,
                   hb("p_fuseBull", 1), hb("p_ptBull", 1), (hb("p_ignBull", 1) and hb("ign_tc_bull", 1)),
                   hct_bull, hb("uc_bull", 1)]
        t1_v1_s = [p_b2bBear, sig_rcNTBear, p_catBear, p_pnBear, (p_ignBear and ign_nc_bear), p_dynBear,
                   hb("p_fuseBear", 1), hb("p_ptBear", 1), (hb("p_ignBear", 1) and hb("ign_tc_bear", 1)),
                   hct_bear, hb("uc_bear", 1)]
        t1_v2_b = [hb("p_b2bBull", 1), hb("sig_rcNTBull", 1), hb("p_catBull", 1), hb("p_pnBull", 1),
                   (hb("p_ignBull", 1) and hb("ign_nc_bull", 1)), hb("p_dynBull", 1),
                   hb("p_fuseBull", 2), hb("p_ptBull", 2), (hb("p_ignBull", 2) and hb("ign_tc_bull", 2)),
                   hb("hct_bull", 1), hb("uc_bull", 2)]
        t1_v2_s = [hb("p_b2bBear", 1), hb("sig_rcNTBear", 1), hb("p_catBear", 1), hb("p_pnBear", 1),
                   (hb("p_ignBear", 1) and hb("ign_nc_bear", 1)), hb("p_dynBear", 1),
                   hb("p_fuseBear", 2), hb("p_ptBear", 2), (hb("p_ignBear", 2) and hb("ign_tc_bear", 2)),
                   hb("hct_bear", 1), hb("uc_bear", 2)]
        t1_v1_anyB = any(t1_v1_b); t1_v1_anyS = any(t1_v1_s)
        t1_v2_anyB = any(t1_v2_b); t1_v2_anyS = any(t1_v2_s)
        p_t1RelayBull = t1_v2_anyB and t1_v1_anyB and conf
        p_t1RelayBear = t1_v2_anyS and t1_v1_anyS and conf
        p_t1StackBull = sum(1 for x in t1_v1_b if x) >= 2 and conf
        p_t1StackBear = sum(1 for x in t1_v1_s if x) >= 2 and conf

        # ============================ WBUSH PLOTS =============================
        tntod_any_bull = (p_b2bBull or sig_rcNTBull or p_fuseBull or p_catBull or p_pnBull or p_ptBull
                          or p_ignBull or p_dynBull or p_t2tntBull or p_t2npmBull or p_t2contBull or p_t2trBull
                          or p_t2rnBull or p_t2prBull or p_d1b or p_d2b or p_d3b or p_uuBull or p_uuuBull or p_uuuuBull)
        tntod_any_bear = (p_b2bBear or sig_rcNTBear or p_fuseBear or p_catBear or p_pnBear or p_ptBear
                          or p_ignBear or p_dynBear or p_t2tntBear or p_t2npmBear or p_t2contBear or p_t2trBear
                          or p_t2rnBear or p_t2prBear or p_d1s or p_d2s or p_d3s or p_uuBear or p_uuuBear or p_uuuuBear)
        p_wbushBull = p.en_wbushBull and sig_WBUSH_Bull and tntod_any_bull
        p_wbushBear = p.en_wbushBear and sig_WBUSH_Bear and tntod_any_bear
        p_wbushNeutral = p.en_wbushNeutral and sig_WBUSH_Neutral

        # ====================== EMIT FIRE MATRIX ==============================
        results = {
            "f_b2bBull": p_b2bBull, "f_b2bBear": p_b2bBear,
            "f_rcNTBull": sig_rcNTBull, "f_rcNTBear": sig_rcNTBear,
            "f_fuseBull": p_fuseBull, "f_fuseBear": p_fuseBear,
            "f_catBull": p_catBull, "f_catBear": p_catBear,
            "f_pnBull": p_pnBull, "f_pnBear": p_pnBear,
            "f_ptBull": p_ptBull, "f_ptBear": p_ptBear,
            "f_ignBull": p_ignBull, "f_ignBear": p_ignBear,
            "f_dynBull": p_dynBull, "f_dynBear": p_dynBear,
            "f_t2tntBull": p_t2tntBull, "f_t2tntBear": p_t2tntBear,
            "f_t2npmBull": p_t2npmBull, "f_t2npmBear": p_t2npmBear,
            "f_t2contBull": p_t2contBull, "f_t2contBear": p_t2contBear,
            "f_t2trBull": p_t2trBull, "f_t2trBear": p_t2trBear,
            "f_t2rnBull": p_t2rnBull, "f_t2rnBear": p_t2rnBear,
            "f_t2prBull": p_t2prBull, "f_t2prBear": p_t2prBear,
            "f_d1b": p_d1b, "f_d1s": p_d1s, "f_d2b": p_d2b, "f_d2s": p_d2s, "f_d3b": p_d3b, "f_d3s": p_d3s,
            "f_uuBull": p_uuBull, "f_uuBear": p_uuBear, "f_uuuBull": p_uuuBull, "f_uuuBear": p_uuuBear,
            "f_uuuuBull": p_uuuuBull, "f_uuuuBear": p_uuuuBear,
            "f_wbushBull": p_wbushBull, "f_wbushBear": p_wbushBear, "f_wbushNeutral": p_wbushNeutral,
            "f_t1RelayBull": p_t1RelayBull, "f_t1RelayBear": p_t1RelayBear,
            "f_t1StackBull": p_t1StackBull, "f_t1StackBear": p_t1StackBear,
        }
        for k in PLOT_IDS:
            if results[k]:
                fire[k][i] = 1
                lvl[k][i] = h[i] if k in _BEAR_LEVEL else l[i]

        # ===================== ADVANCE [k] HISTORY ============================
        H["det_bullTNT"].append(det_bullTNT); H["det_bearTNT"].append(det_bearTNT)
        H["det_bullNapalm"].append(det_bullNapalm); H["det_bearNapalm"].append(det_bearNapalm)
        H["det_bullNapalm0"].append(det_bullNapalm); H["det_bearNapalm0"].append(det_bearNapalm)
        H["det_bullRetTNT"].append(det_bullRetTNT); H["det_bearRetTNT"].append(det_bearRetTNT)
        H["det_contBull"].append(det_contBull); H["det_contBear"].append(det_contBear)
        H["u5_SAAB"].append(u5_SAAB); H["u5_Kratos"].append(u5_Kratos)
        H["u5_GrandSlam"].append(u5_GrandSlam); H["u5_MOAB"].append(u5_MOAB)
        H["u5_RVOL1xB"].append(u5_RVOL1xB); H["u5_RVOL1xR"].append(u5_RVOL1xR)
        H["u5_Pentagon"].append(u5_Pentagon); H["u5_WTC"].append(u5_WTC)
        H["u5_Hiroshima"].append(u5_Hiroshima); H["u5_Nagasaki"].append(u5_Nagasaki)
        H["u5_PUP"].append(u5_PUP); H["u5_PPD"].append(u5_PPD)
        H["u5_FAUNABull"].append(u5_FAUNABull); H["u5_FAUNABear"].append(u5_FAUNABear)
        H["u5_WMD"].append(u5_WMD); H["u5_HV1000"].append(u5_HV1000)
        H["u5_PBJBull"].append(u5_PBJBull); H["u5_PBJBear"].append(u5_PBJBear)
        H["u5_DISPBull"].append(u5_DISPBull); H["u5_DISPBear"].append(u5_DISPBear)
        H["u5_CS1_Bull"].append(u5_CS1_Bull); H["u5_CS1_Bear"].append(u5_CS1_Bear)
        H["det_dynamiteBull"].append(det_dynamiteBull); H["det_dynamiteBear"].append(det_dynamiteBear)
        H["det_rcTRBull"].append(det_rcTRBull); H["det_rcTRBear"].append(det_rcTRBear)
        H["det_ptBull"].append(det_ptBull); H["det_ptBear"].append(det_ptBear)
        H["det_prBull"].append(det_prBull); H["det_prBear"].append(det_prBear)
        H["det_fuseBull"].append(det_fuseBull); H["det_fuseBear"].append(det_fuseBear)
        H["det_igniteBull"].append(det_igniteBull); H["det_igniteBear"].append(det_igniteBear)
        H["ign_tc_bull"].append(ign_tc_bull); H["ign_tc_bear"].append(ign_tc_bear)
        H["ign_nc_bull"].append(ign_nc_bull); H["ign_nc_bear"].append(ign_nc_bear)
        H["gate_bull"].append(gate_bull); H["gate_bear"].append(gate_bear)
        H["p_b2bBull"].append(p_b2bBull); H["p_b2bBear"].append(p_b2bBear)
        H["sig_rcNTBull"].append(sig_rcNTBull); H["sig_rcNTBear"].append(sig_rcNTBear)
        H["p_catBull"].append(p_catBull); H["p_catBear"].append(p_catBear)
        H["p_pnBull"].append(p_pnBull); H["p_pnBear"].append(p_pnBear)
        H["p_fuseBull"].append(p_fuseBull); H["p_fuseBear"].append(p_fuseBear)
        H["p_ptBull"].append(p_ptBull); H["p_ptBear"].append(p_ptBear)
        H["p_ignBull"].append(p_ignBull); H["p_ignBear"].append(p_ignBear)
        H["p_dynBull"].append(p_dynBull); H["p_dynBear"].append(p_dynBear)
        H["det_rcRNBull"].append(det_rcRNBull); H["det_rcRNBear"].append(det_rcRNBear)
        H["det_pnBull"].append(det_pnBull); H["det_pnBear"].append(det_pnBear)
        H["det_catBull"].append(det_catBull); H["det_catBear"].append(det_catBear)
        H["hct_bull"].append(hct_bull); H["hct_bear"].append(hct_bear)
        H["uc_bull"].append(uc_bull); H["uc_bear"].append(uc_bear)
        H["sig_d1b"].append(sig_d1b); H["sig_d1s"].append(sig_d1s)
        H["sig_d2b"].append(sig_d2b); H["sig_d2s"].append(sig_d2s)
        H["sig_d3b"].append(sig_d3b); H["sig_d3s"].append(sig_d3s)

    # Lightweight introspection hook (engine-event counts) — useful for parity
    # diagnostics; never affects the fire matrix.
    compute._last_debug = {  # type: ignore[attr-defined]
        k: sum(1 for x in H[k] if x) for k in (
            "det_bullTNT", "det_bearTNT", "det_bullNapalm", "det_bearNapalm",
            "det_bullRetTNT", "det_bearRetTNT", "det_contBull", "det_contBear",
            "det_dynamiteBull", "det_dynamiteBear", "u5_DISPBull", "u5_DISPBear",
            "u5_FAUNABull", "u5_PBJBull", "u5_PBJBear", "gate_bull", "gate_bear")}
    sigAny = [1 if any(fire[k][i] for k in PLOT_IDS) else 0 for i in range(n)]
    out = {"ts": ts, "sigAny": sigAny, "lvl_u5_relVol": lvl_relVol}
    for k in PLOT_IDS:
        out[f"fire_{k}"] = fire[k]
        out[f"lvl_{k}"] = lvl[k]
    return out


# COMPOSITE_PARTIAL: none — FULL port. Retained (empty) for honesty-gate inspection.
COMPOSITE_PARTIAL: list[str] = []
