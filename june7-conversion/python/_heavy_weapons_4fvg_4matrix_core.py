"""heavy_weapons_4fvg_4matrix — detection core (Pine-faithful, runtime-grain agnostic).

ULTRACODE FULL PORT — every detection plot is ported 1:1; nothing is stubbed.

Source (read from disk, quoted exactly):
  "/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT transformed
   yet/June 7/Tick Friendly conversion/heavy_weapons_4fvg_4matrix_tickfriendly.pine"
  Pine v5, indicator
  "Heavy Weapons NRA + GZI/FVG + Matrix Combos 2 bodies not 1 NRAFR"
  (shorttitle "RVOL NRAFR x2"), source file "heavy weapons with 4 fvg 4 matrix.txt".
  `import TradingView/ta/7 as tv_ta` (only tv_ta.relativeVolume used).

THE 22 DETECTION PLOTS (every plotshape in the Pine PLOTS block, L437-465):
  RVOL/Bull-Bear normalized-price band:
    SAAB       belowbar  (bull, [th_saab_kratos, th_1x))
    Kratos     abovebar  (bear, [th_saab_kratos, th_1x))
    BullRVOL1x belowbar  (bull, [th_1x, th_gs_moab))
    BearRVOL1x abovebar  (bear, [th_1x, th_gs_moab))
    GrandSlam  belowbar  (bull, >= th_gs_moab)
    MOAB       abovebar  (bear, >= th_gs_moab)
  Reg @ Time RVOL ratio band:
    Pentagon   top  ([th_1x, th_wtc])
    WTC        top  ((th_wtc, th_hiroshima])
    Hiroshima  top  (> th_hiroshima)
    Nagasaki   top  (new running-max volume — HEV)
  Hybrid Momentum (reg + cum RVOL floors + body ratio):
    Long1 / Short1 / Long2 / Short2  (below/abovebar)
  GZI / HV FVG combos (offset = -1):
    CS1_Bull / CS1_Bear  (FVG/GZI + Standard RVOL[1])
    CS2_Bull / CS2_Bear  (FVG/GZI + Reg@Time[1])
  Matrix (Neo/Trinity) combos (offset = 0):
    CS3_Bull / CS3_Bear  (Matrix + Standard RVOL)
    CS4_Bull / CS4_Bear  (Matrix + Reg@Time)

PINE-SEMANTICS PRESERVED (1:1, not approximated):
  * tv_ta.relativeVolume(ta/7)  -> canonical shim via _nine_nines_common.relative_volume
                                   (RVOL-at-time; NEVER volume/sma(volume,N)). RE10023
                                   fix: anchor is daily "D" always (tick bars never align
                                   to clock times, so RVOL keys off each bar's calendar day).
  * ta.sma / ta.atr / ta.highest -> _nine_nines_common mirrors (na-warmup faithful).
  * ta.cum((high-low)/low)/bar_index -> auto threshold (i==0 guarded like Pine bar_index 0).
  * var float maxVol / isNagasaki -> explicit forward-walk state (new running-max).
  * var fvgs = array.new<fvg>() with unshift/remove gated by barstate.isconfirmed ->
    explicit list-of-dict, mutated only on closed bars (offline = every bar closed),
    with the SAME insert-at-front (unshift) + reverse-walk mitigation removal.
  * The Fauna/Matrix Neo/Trinity exclusion ladder ported constant-for-constant.
  * `[1]` look-backs -> shift(...) (None before the start, Pine na).
  * nz(x, repl)  -> repl only when x is na (None); NOT when x == 0.
  * barstate.isconfirmed -> always True (we score CLOSED bars only).
  * Pine `offset=-1` on the FVG combo plots -> applied_ts paints one real bar back.

DETECTION = per-bar 0/1 fires + numeric debug levels in the returned dict.
No graphic objects (the Pine is plotshape + alertcondition only; header certifies
no label.new — line.new exists ONLY inside the mitLvl cosmetic branch which is a
drawing, not a detection plot, and is intentionally excluded as cosmetic).

EVERY THRESHOLD IS A PARAMETER (Params dataclass) — none hardcoded inline.
This is the ONE core path. The tick wrapper and the time wrapper both call
`compute(bars, ...)` / `fire_matrix(bars, ...)`; the only difference is the grain
of the Bar list and the tf_seconds row selected from the per-TF threshold tables.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Shared NineNines harness (ONE core dependency): Bar + Pine ta.* mirrors that are
# na-propagating (sma over an na-gated series, highest, shift, nz, atr) PLUS the
# canonical tv_ta.relativeVolume shim re-export. Do NOT re-derive relativeVolume.
from _nn_harness import (  # noqa: E402
    Bar, sma, highest as _highest, shift as _shift, nz as _nz, atr as _atr_cols,
    relative_volume,
)


# ───────────────────────── detection-plot registry ──────────────────────────
# id -> (descriptor, location, shape, offset). offset matches the Pine plotshape
# `offset=` arg: FVG combos paint offset=-1 (one real bar back); all else offset=0.
# Same-named signals across other indicators are NOT equivalent; scoped to this study.
PLOT_IDS: dict[str, tuple[str, str, str, int]] = {
    "SAAB":       ("SAAB (bull, normPrice in [0.56x,1x))",                "belowbar", "square",       0),
    "Kratos":     ("Kratos (bear, normPrice in [0.56x,1x))",             "abovebar", "square",       0),
    "BullRVOL1x": ("Bull RVOL 1x (bull, normPrice in [1x,gs))",          "belowbar", "xcross",       0),
    "BearRVOL1x": ("Bear RVOL 1x (bear, normPrice in [1x,gs))",          "abovebar", "xcross",       0),
    "GrandSlam":  ("Grand Slam (bull, normPrice >= gs/moab)",            "belowbar", "triangleup",   0),
    "MOAB":       ("MOAB (bear, normPrice >= gs/moab)",                  "abovebar", "triangledown", 0),
    "Pentagon":   ("Pentagon (relVol in [1x, wtc])",                     "top",      "diamond",      0),
    "WTC":        ("WTC (relVol in (wtc, hiroshima])",                   "top",      "diamond",      0),
    "Hiroshima":  ("Hiroshima (relVol > hiroshima)",                     "top",      "diamond",      0),
    "Nagasaki":   ("Nagasaki HEV (new running-max volume)",              "top",      "flag",         0),
    "Long1":      ("LONG 1 (hyb reg>floor & cum>floor & bull body)",     "belowbar", "labelup",      0),
    "Short1":     ("SHORT 1 (hyb reg>floor & cum>floor & bear body)",    "abovebar", "labeldown",    0),
    "Long2":      ("LONG 2 (hyb reg>floor & cum>floor & bull body)",     "belowbar", "labelup",      0),
    "Short2":     ("SHORT 2 (hyb reg>floor & cum>floor & bear body)",    "abovebar", "labeldown",    0),
    "CS1_Bull":   ("Combo Set 1 Bull (FVG/GZI + Standard RVOL[1])",      "belowbar", "labelup",     -1),
    "CS1_Bear":   ("Combo Set 1 Bear (FVG/GZI + Standard RVOL[1])",      "abovebar", "labeldown",   -1),
    "CS2_Bull":   ("Combo Set 2 Bull (FVG/GZI + Reg@Time[1])",           "belowbar", "labelup",     -1),
    "CS2_Bear":   ("Combo Set 2 Bear (FVG/GZI + Reg@Time[1])",           "abovebar", "labeldown",   -1),
    "CS3_Bull":   ("Combo Set 3 Bull (Matrix + Standard RVOL)",          "belowbar", "labelup",      0),
    "CS3_Bear":   ("Combo Set 3 Bear (Matrix + Standard RVOL)",          "abovebar", "labeldown",    0),
    "CS4_Bull":   ("Combo Set 4 Bull (Matrix + Reg@Time)",               "belowbar", "labelup",      0),
    "CS4_Bear":   ("Combo Set 4 Bear (Matrix + Reg@Time)",               "abovebar", "labeldown",    0),
}

# No detection plot is stubbed: this is a FULL faithful port. Every plot above is
# genuinely computed (pure OHLCV math + canonical RVOL shim). The honesty gate in
# the parity harness verifies STUB_IDS is empty AND that a 0 fire means "no signal".
STUB_IDS: tuple[str, ...] = ()


@dataclass(frozen=True)
class Params:
    # RVOL Bull/Bear (normalized price/volume)
    bb_avgLength: int = 30
    bb_smaLength: int = 20
    # Reg @ Time RVOL
    reg_length: int = 30
    reg_cumulative: bool = True           # "Cumulative" option
    reg_anchor: str = "D"                  # RE10023 fix: daily anchor ALWAYS
    reg_adjustRealtime: bool = True        # irrelevant (closed bars only)
    # Matrix
    matrix_len: int = 67
    # combos
    comboBodyPct_FVG: float = 0.85
    comboBodyPct_MAT: float = 0.85
    inc_pentagon_FVG: bool = True
    inc_pentagon_MAT: bool = True
    # GZI / HV FVG base
    threshPct: float = 2.0
    auto_thresh: bool = True               # "Auto"
    gziDist: int = 7
    # Hybrid momentum
    hyb_addReg1: float = 5.0
    hyb_addCum1: float = 3.0
    hyb_bodyRat1: float = 0.65
    hyb_addReg2: float = 5.0
    hyb_addCum2: float = 3.0
    hyb_bodyRat2: float = 0.65
    # Fauna/Matrix constants (Pine `const` block — exposed as params; defaults = source)
    atr_len: int = 14
    vol_len: int = 20
    gg_body_th: float = 0.85
    # bull fauna
    b_alpha_MB: float = 1.6; b_beta_MB: float = 0.70; b_delta_MB: float = 1.8
    b_gamma_RE: float = 2.2; b_epsilon_RE: float = 0.15; b_delta_RE: float = 1.8
    b_theta_TA: float = 1.6; b_delta_TA: float = 1.8
    b_trend_len: int = 50; b_delta_len: int = 10
    b_zeta_GG: float = 0.9; b_delta_GG: float = 1.8
    b_alpha_SB: float = 1.5; b_delta_SB: float = 1.5; b_weak_rat: float = 0.2
    b_body_len: int = 20
    # bear fauna (source uses identical constants)
    s_alpha_MB: float = 1.6; s_beta_MB: float = 0.70; s_delta_MB: float = 1.8
    s_gamma_RE: float = 2.2; s_epsilon_RE: float = 0.15; s_delta_RE: float = 1.8
    s_theta_TA: float = 1.6; s_delta_TA: float = 1.8
    s_trend_len: int = 50; s_delta_len: int = 10
    s_zeta_GG: float = 0.9; s_delta_GG: float = 1.8
    s_alpha_SB: float = 1.5; s_delta_SB: float = 1.5; s_weak_rat: float = 0.2
    s_body_len: int = 20
    # tick fallback seconds (Pine TICK_FALLBACK_SEC) — used by the tick wrapper.
    tick_fallback_sec: int = 10
    # GLOBAL show toggles — default to the Pine source's defaults so the fire matrix
    # matches the shipped indicator out of the box. Setting all True exposes every plot.
    show_SAAB: bool = False
    show_Kratos: bool = False
    show_BullRVOL1x: bool = False
    show_BearRVOL1x: bool = False
    show_GrandSlam: bool = True
    show_MOAB: bool = True
    show_Pentagon: bool = False
    show_WTC: bool = True
    show_Hiroshima: bool = True
    show_Nagasaki: bool = True
    show_Long1: bool = False
    show_Short1: bool = False
    show_Long2: bool = False
    show_Short2: bool = False
    show_CS1_Bull: bool = True
    show_CS1_Bear: bool = True
    show_CS2_Bull: bool = True
    show_CS2_Bear: bool = True
    show_CS3_Bull: bool = True
    show_CS3_Bear: bool = True
    show_CS4_Bull: bool = True
    show_CS4_Bear: bool = True


# ───────────────────────── per-TF threshold tables (exact from Pine) ─────────
def _f_rvol_1x(s: float) -> float:
    """Pine f_rvol_1x_threshold(_tfSec) — line-for-line."""
    return (38.0 if s <= 10 else 33.0 if s <= 15 else 28.0 if s <= 30 else 23.0 if s <= 45
            else 20.0 if s <= 60 else 19.0 if s <= 120 else 17.0 if s <= 180 else 16.0 if s <= 240
            else 15.0 if s <= 300 else 14.0 if s <= 360 else 12.0 if s <= 420 else 11.0 if s <= 480
            else 10.0 if s <= 540 else 10.0 if s <= 600 else 8.4 if s <= 900 else 6.9 if s <= 1800
            else 5.9 if s <= 3600 else 3.0 if s <= 7200 else 1.8)


def _f_gs_moab(s: float) -> float:
    """Pine f_gs_moab_threshold(_tfSec) — line-for-line."""
    return (114.0 if s <= 10 else 99.0 if s <= 15 else 84.0 if s <= 30 else 69.0 if s <= 45
            else 35.0 if s <= 60 else 35.0 if s <= 300 else 25.0 if s <= 600 else 20.0 if s <= 900
            else 10.0 if s <= 3600 else 8.0)


def _div_na(num, den):
    """Pine float division semantics: x/0 == na (returned as None), never a crash.
    None operands also propagate to None."""
    if num is None or den is None or den == 0:
        return None
    return num / den


def _highest_shift1(series, length):
    """Pine ta.highest(series, length)[1] — highest over `length` ending at i-1.
    Uses the shared na-warmup `highest` then shifts back one bar."""
    return _shift(_highest(series, length), 1)


# ───────────────────────── the one core compute ─────────────────────────────
def compute(bars: Sequence[Bar], params: Params | None = None, *, tf_seconds: int) -> dict:
    """Return the full signal dict for the heavy-weapons fire matrix.

    `tf_seconds` selects the per-TF threshold row (tick wrapper passes the tick
    fallback seconds; time wrapper passes the real bar seconds). RVOL is ALWAYS
    daily-anchored regardless of grain (Pine reg_anchorSafe -> "D").
    Output keys mirror every intermediate the parity harness needs plus the final
    sig* booleans for each of the 22 detection plots.
    """
    P = params or Params()
    n = len(bars)
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    lo = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]

    # --- thresholds (per-TF) ---
    th_1x = _f_rvol_1x(tf_seconds)
    th_saab_kratos = th_1x * 0.56
    th_wtc = th_1x * 2.0
    th_gs_moab = _f_gs_moab(tf_seconds)
    th_hiroshima = th_gs_moab

    # offline batch scores closed bars only -> barstate.isconfirmed == True.
    conf = [True] * n

    # ---------- RVOL Bull/Bear (normalized price / volume) ----------
    # Pine float division: x/0 == na (NOT a crash). We mirror na as None so it
    # propagates faithfully through the band comparisons (na vs threshold -> false).
    bb_spike = [abs(c[i] - o[i]) for i in range(n)]
    sma_spike = sma(bb_spike, P.bb_avgLength)
    sma_spike_1 = _shift(sma_spike, 1)                       # ta.sma(...)[1]
    bb_np = [_div_na(bb_spike[i], _nz(sma_spike_1[i], 1.0)) for i in range(n)]
    sma_vol = sma(v, P.bb_avgLength)
    sma_vol_1 = _shift(sma_vol, 1)
    bb_nv = [_div_na(v[i], _nz(sma_vol_1[i], 1.0)) for i in range(n)]
    bb_diff = [(None if (bb_np[i] is None or bb_nv[i] is None) else bb_np[i] - bb_nv[i]) for i in range(n)]
    bb_posdiff = [(d if (d is not None and d > 0) else None) for d in bb_diff]  # na when <=0 or na
    bb_smadiff = sma(bb_posdiff, P.bb_smaLength)             # na-propagating

    def _pos_gt_sma(i):
        return (bb_posdiff[i] is not None and bb_smadiff[i] is not None
                and bb_posdiff[i] > bb_smadiff[i])

    bull_base = [(c[i] > o[i]) and _pos_gt_sma(i) for i in range(n)]
    bear_base = [(c[i] < o[i]) and _pos_gt_sma(i) for i in range(n)]

    def _in_rng(x, lo_t, hi_t):
        return x is not None and x >= lo_t and x < hi_t        # na -> false (Pine)

    def _ge(x, t):
        return x is not None and x >= t

    sigSAAB = [conf[i] and bull_base[i] and _in_rng(bb_np[i], th_saab_kratos, th_1x) for i in range(n)]
    sigKratos = [conf[i] and bear_base[i] and _in_rng(bb_np[i], th_saab_kratos, th_1x) for i in range(n)]
    sigBull1x = [conf[i] and bull_base[i] and _in_rng(bb_np[i], th_1x, th_gs_moab) for i in range(n)]
    sigBear1x = [conf[i] and bear_base[i] and _in_rng(bb_np[i], th_1x, th_gs_moab) for i in range(n)]
    sigGrandSlam = [conf[i] and bull_base[i] and _ge(bb_np[i], th_gs_moab) for i in range(n)]
    sigMOAB = [conf[i] and bear_base[i] and _ge(bb_np[i], th_gs_moab) for i in range(n)]

    # ---------- Reg @ Time RVOL (daily anchor — RE10023 fix) ----------
    # relVolRatio = currentVolume_reg / pastVolume_reg ; na -> comparisons false.
    reg_curr, reg_past, reg_ratio = relative_volume(
        v, P.reg_length, anchor_timeframe=P.reg_anchor,
        is_cumulative=P.reg_cumulative, bar_timestamps=ts)
    relVol = [(reg_ratio[i] if reg_ratio[i] is not None else 0.0) for i in range(n)]
    rv_valid = [reg_ratio[i] is not None for i in range(n)]

    sigPentagon = [conf[i] and rv_valid[i] and (relVol[i] >= th_1x) and (relVol[i] <= th_wtc) for i in range(n)]
    sigWTC = [conf[i] and rv_valid[i] and (relVol[i] > th_wtc) and (relVol[i] <= th_hiroshima) for i in range(n)]
    sigHiroshima = [conf[i] and rv_valid[i] and (relVol[i] > th_hiroshima) for i in range(n)]

    # ---------- Nagasaki: new running-max volume (var float maxVol) ----------
    sigNagasaki = [False] * n
    maxVol = 0.0
    for i in range(n):
        if not conf[i]:
            continue
        if i == 0:
            maxVol = v[i]
        elif v[i] > maxVol:
            sigNagasaki[i] = True
            maxVol = v[i]

    # ---------- Hybrid momentum ----------
    # hybRegRatio = relVolRatio (the same cumulative reg ratio above).
    hybRegRatio = relVol
    # hybCum = relativeVolume(reg_length, anchorSafe, true, adjustRealtime) -> cumulative.
    hyb_curr, hyb_past, hyb_ratio = relative_volume(
        v, P.reg_length, anchor_timeframe=P.reg_anchor,
        is_cumulative=True, bar_timestamps=ts)
    hybCumRatio = [(hyb_ratio[i] if hyb_ratio[i] is not None else 0.0) for i in range(n)]
    hybCum_valid = [hyb_ratio[i] is not None for i in range(n)]
    body = [abs(c[i] - o[i]) for i in range(n)]
    rng = [h[i] - lo[i] for i in range(n)]
    bodyRat = [(0.0 if rng[i] == 0 else body[i] / rng[i]) for i in range(n)]

    def _hyb_mom(i, reg_floor, cum_floor):
        # conf and hybRegRatio>floor and hybCumRatio>floor ; na -> false (rv_valid gate).
        return (conf[i] and rv_valid[i] and hybCum_valid[i]
                and hybRegRatio[i] > reg_floor and hybCumRatio[i] > cum_floor)

    hybConvict1 = [bodyRat[i] >= P.hyb_bodyRat1 for i in range(n)]
    hybConvict2 = [bodyRat[i] >= P.hyb_bodyRat2 for i in range(n)]
    sigLong1 = [_hyb_mom(i, P.hyb_addReg1, P.hyb_addCum1) and (c[i] > o[i]) and hybConvict1[i] for i in range(n)]
    sigShort1 = [_hyb_mom(i, P.hyb_addReg1, P.hyb_addCum1) and (c[i] < o[i]) and hybConvict1[i] for i in range(n)]
    sigLong2 = [_hyb_mom(i, P.hyb_addReg2, P.hyb_addCum2) and (c[i] > o[i]) and hybConvict2[i] for i in range(n)]
    sigShort2 = [_hyb_mom(i, P.hyb_addReg2, P.hyb_addCum2) and (c[i] < o[i]) and hybConvict2[i] for i in range(n)]

    # ---------- GZI / HV FVG (array-stateful, conf-gated) ----------
    v1 = _shift(v, 1)                                        # volume[1]
    hv5000 = _highest_shift1(v, 5000)                        # ta.highest(volume,5000)[1]
    hv252 = _highest_shift1(v, 252)
    hv63 = _highest_shift1(v, 63)

    def _is_hv(i):
        if v1[i] is None:
            return False
        return ((hv5000[i] is not None and v1[i] == hv5000[i]) or
                (hv252[i] is not None and v1[i] == hv252[i]) or
                (hv63[i] is not None and v1[i] == hv63[i]))

    bullGZI = [False] * n
    bearGZI = [False] * n
    bullHV = [False] * n
    bearHV = [False] * n
    fvgs: list[dict] = []
    lastT = 0
    cum_range = 0.0
    for i in range(n):
        # thresh = auto ? ta.cum((high-low)/low)/bar_index : threshPct/100
        cum_range += ((h[i] - lo[i]) / lo[i]) if lo[i] != 0 else 0.0
        if P.auto_thresh:
            thresh = (cum_range / i) if i > 0 else cum_range  # Pine bar_index 0 -> /0 = inf;
            # at bar 0 there is no [2] so bFVG/sFVG are false regardless. cum_range/i is the
            # exact Pine ta.cum/bar_index from bar 1 onward.
        else:
            thresh = P.threshPct / 100.0
        hv_i = _is_hv(i)
        bFVG = (i >= 2 and lo[i] > h[i - 2] and c[i - 1] > h[i - 2]
                and ((lo[i] - h[i - 2]) / h[i - 2] > thresh if h[i - 2] != 0 else False))
        sFVG = (i >= 2 and h[i] < lo[i - 2] and c[i - 1] < lo[i - 2]
                and ((lo[i - 2] - h[i]) / h[i] > thresh if h[i] != 0 else False))
        if not conf[i]:
            continue
        if bFVG and ts[i] != lastT:
            mx, mn = lo[i], h[i - 2]
            if hv_i:
                bullHV[i] = True
            for e in fvgs:
                if e["bull"] and (i - e["idx"]) <= P.gziDist:
                    ob = max(e["mn"], mn)
                    ot = min(e["mx"], mx)
                    if ob < ot or (ob <= ot and e["hv"] and hv_i):
                        bullGZI[i] = True
                        break
            fvgs.insert(0, {"mx": mx, "mn": mn, "bull": True, "idx": i, "hv": hv_i})
            lastT = ts[i]
        if sFVG and ts[i] != lastT:
            mx, mn = lo[i - 2], h[i]
            if hv_i:
                bearHV[i] = True
            for e in fvgs:
                if (not e["bull"]) and (i - e["idx"]) <= P.gziDist:
                    ob = max(e["mn"], mn)
                    ot = min(e["mx"], mx)
                    if ob < ot or (ob <= ot and e["hv"] and hv_i):
                        bearGZI[i] = True
                        break
            fvgs.insert(0, {"mx": mx, "mn": mn, "bull": False, "idx": i, "hv": hv_i})
            lastT = ts[i]
        # mitigation removal: close beyond zone (reverse-walk in Pine; order-independent
        # for a pure survivor filter). Affects FUTURE GZI overlap checks.
        survivors = []
        for g in fvgs:
            if g["bull"] and c[i] < g["mn"]:
                continue
            if (not g["bull"]) and c[i] > g["mx"]:
                continue
            survivors.append(g)
        fvgs = survivors

    # ---------- Matrix / Fauna (Neo/Trinity exclusion ladder) ----------
    ATR = _atr_cols(o, h, lo, c, P.atr_len)   # Pine ta.atr(14) = rma(true_range,14)
    AvgVol = sma(v, P.vol_len)
    hv_mat = _highest(v, P.matrix_len)
    is_matrix = [hv_mat[i] is not None and v[i] == hv_mat[i] for i in range(n)]

    def _fauna_side(bull: bool):
        a_MB = P.b_alpha_MB if bull else P.s_alpha_MB
        be_MB = P.b_beta_MB if bull else P.s_beta_MB
        d_MB = P.b_delta_MB if bull else P.s_delta_MB
        g_RE = P.b_gamma_RE if bull else P.s_gamma_RE
        e_RE = P.b_epsilon_RE if bull else P.s_epsilon_RE
        d_RE = P.b_delta_RE if bull else P.s_delta_RE
        th_TA = P.b_theta_TA if bull else P.s_theta_TA
        d_TA = P.b_delta_TA if bull else P.s_delta_TA
        trend_len = P.b_trend_len if bull else P.s_trend_len
        delta_len = P.b_delta_len if bull else P.s_delta_len
        z_GG = P.b_zeta_GG if bull else P.s_zeta_GG
        d_GG = P.b_delta_GG if bull else P.s_delta_GG
        a_SB = P.b_alpha_SB if bull else P.s_alpha_SB
        d_SB = P.b_delta_SB if bull else P.s_delta_SB
        weak = P.b_weak_rat if bull else P.s_weak_rat
        body_len = P.b_body_len if bull else P.s_body_len

        AvgBody = sma([abs(c[i] - o[i]) for i in range(n)], body_len)
        AvgDelta = sma([abs(c[i] - c[i - 1]) if i > 0 else 0.0 for i in range(n)], delta_len)
        TrendMA = sma(c, trend_len)
        out = [False] * n
        for i in range(n):
            if ATR[i] is None or AvgVol[i] is None or i < 1:
                continue
            body_up = c[i] > o[i]
            body_dn = c[i] < o[i]
            bs = abs(c[i] - o[i])
            rb = h[i] - lo[i]
            ratio = 0.0 if rb == 0 else bs / rb
            dir_ok = body_up if bull else body_dn
            MB = dir_ok and bs > a_MB * ATR[i] and ratio > be_MB and v[i] > d_MB * AvgVol[i]
            if bull:
                RE = body_up and rb > g_RE * ATR[i] and (h[i] - c[i]) < e_RE * rb and v[i] > d_RE * AvgVol[i]
                TA = (TrendMA[i] is not None and TrendMA[i - 1] is not None and TrendMA[i] > TrendMA[i - 1]
                      and AvgDelta[i] is not None and (c[i] - c[i - 1]) > th_TA * AvgDelta[i]
                      and body_up and v[i] > d_TA * AvgVol[i])
                GG = (o[i] - c[i - 1]) > z_GG * ATR[i] and body_up and lo[i] > c[i - 1] and v[i] > d_GG * AvgVol[i]
            else:
                RE = body_dn and rb > g_RE * ATR[i] and (c[i] - lo[i]) < e_RE * rb and v[i] > d_RE * AvgVol[i]
                TA = (TrendMA[i] is not None and TrendMA[i - 1] is not None and TrendMA[i] < TrendMA[i - 1]
                      and AvgDelta[i] is not None and (c[i - 1] - c[i]) > th_TA * AvgDelta[i]
                      and body_dn and v[i] > d_TA * AvgVol[i])
                GG = (c[i - 1] - o[i]) > z_GG * ATR[i] and body_dn and h[i] < c[i - 1] and v[i] > d_GG * AvgVol[i]
            prev_body = c[i - 1] - o[i - 1]
            prev_rng = h[i - 1] - lo[i - 1]
            ab_prev = AvgBody[i - 1] if AvgBody[i - 1] is not None else 0.0
            av_prev = AvgVol[i - 1] if AvgVol[i - 1] is not None else 0.0
            if bull:
                StrBear = c[i - 1] < o[i - 1] and abs(prev_body) > a_SB * ab_prev and v[i - 1] > d_SB * av_prev
                WeakBear = c[i - 1] < o[i - 1] and (0.0 if prev_rng == 0 else abs(prev_body) / prev_rng) <= weak
                TR = WeakBear and (MB or RE or TA)
                ES = StrBear and (MB or RE or TA)
                GDR = c[i - 1] < o[i - 1] and GG
            else:
                StrBull = c[i - 1] > o[i - 1] and abs(prev_body) > a_SB * ab_prev and v[i - 1] > d_SB * av_prev
                WeakBull = c[i - 1] > o[i - 1] and (0.0 if prev_rng == 0 else abs(prev_body) / prev_rng) <= weak
                TR = WeakBull and (MB or RE or TA)
                ES = StrBull and (MB or RE or TA)
                GDR = c[i - 1] > o[i - 1] and GG
            core_cnt = (1 if MB else 0) + (1 if RE else 0) + (1 if TA else 0)
            gg_pass = (core_cnt >= 2) and (ratio >= P.gg_body_th)   # gg_master_on=true
            hard_exc = TR or ES or GDR
            gg_exc = GG and not gg_pass
            excluded = hard_exc or gg_exc
            out[i] = (MB or RE or TA) and not excluded
        return out

    fauna_bull = _fauna_side(True)
    fauna_bear = _fauna_side(False)

    neo_bull = [conf[i] and is_matrix[i] and fauna_bull[i] for i in range(n)]
    neo_bear = [conf[i] and is_matrix[i] and fauna_bear[i] for i in range(n)]
    trin_bull = [conf[i] and is_matrix[i] and (not fauna_bull[i]) and (c[i] > o[i]) for i in range(n)]
    trin_bear = [conf[i] and is_matrix[i] and (not fauna_bear[i]) and (c[i] < o[i]) for i in range(n)]

    neo_bull_al = [neo_bull[i] and (sigLong1[i] or sigLong2[i]) for i in range(n)]
    neo_bear_al = [neo_bear[i] and (sigShort1[i] or sigShort2[i]) for i in range(n)]
    trin_bull_al = [trin_bull[i] and (sigLong1[i] or sigLong2[i]) for i in range(n)]
    trin_bear_al = [trin_bear[i] and (sigShort1[i] or sigShort2[i]) for i in range(n)]

    # ---------- Combination signals ----------
    # FVG/GZI body eval on bar [1]
    body1 = [abs(c[i - 1] - o[i - 1]) if i >= 1 else 0.0 for i in range(n)]
    rng1 = [(h[i - 1] - lo[i - 1]) if i >= 1 else 0.0 for i in range(n)]
    bodyPct1 = [(0.0 if rng1[i] == 0 else body1[i] / rng1[i]) for i in range(n)]
    validBody_FVG = [bodyPct1[i] >= P.comboBodyPct_FVG for i in range(n)]
    validBody_MAT = [bodyRat[i] >= P.comboBodyPct_MAT for i in range(n)]

    sigSAAB_1 = _shift(sigSAAB, 1); sigBull1x_1 = _shift(sigBull1x, 1); sigGS_1 = _shift(sigGrandSlam, 1)
    sigKr_1 = _shift(sigKratos, 1); sigBear1x_1 = _shift(sigBear1x, 1); sigMOAB_1 = _shift(sigMOAB, 1)
    sigPent_1 = _shift(sigPentagon, 1); sigWTC_1 = _shift(sigWTC, 1)
    sigHiro_1 = _shift(sigHiroshima, 1); sigNaga_1 = _shift(sigNagasaki, 1)

    def _b(x, i):
        return bool(x[i]) if x[i] is not None else False

    cs1_bull = [conf[i] and validBody_FVG[i] and (bullHV[i] or bullGZI[i])
                and (_b(sigSAAB_1, i) or _b(sigBull1x_1, i) or _b(sigGS_1, i)) for i in range(n)]
    cs1_bear = [conf[i] and validBody_FVG[i] and (bearHV[i] or bearGZI[i])
                and (_b(sigKr_1, i) or _b(sigBear1x_1, i) or _b(sigMOAB_1, i)) for i in range(n)]
    # volRegTimeActiveBull_FVG == volRegTimeActiveBear_FVG in the Pine source.
    volRegTimeActive_FVG = [((P.inc_pentagon_FVG and _b(sigPent_1, i)) or _b(sigWTC_1, i)
                             or _b(sigHiro_1, i) or _b(sigNaga_1, i)) for i in range(n)]
    cs2_bull = [conf[i] and validBody_FVG[i] and (bullHV[i] or bullGZI[i]) and volRegTimeActive_FVG[i] for i in range(n)]
    cs2_bear = [conf[i] and validBody_FVG[i] and (bearHV[i] or bearGZI[i]) and volRegTimeActive_FVG[i] for i in range(n)]

    matrix_any_bull = [neo_bull[i] or trin_bull[i] or neo_bull_al[i] or trin_bull_al[i] for i in range(n)]
    matrix_any_bear = [neo_bear[i] or trin_bear[i] or neo_bear_al[i] or trin_bear_al[i] for i in range(n)]
    cs3_bull = [validBody_MAT[i] and matrix_any_bull[i] and (sigSAAB[i] or sigBull1x[i] or sigGrandSlam[i]) for i in range(n)]
    cs3_bear = [validBody_MAT[i] and matrix_any_bear[i] and (sigKratos[i] or sigBear1x[i] or sigMOAB[i]) for i in range(n)]
    # volRegTimeActiveBull_MAT == volRegTimeActiveBear_MAT in the Pine source.
    volRegTimeActive_MAT = [((P.inc_pentagon_MAT and sigPentagon[i]) or sigWTC[i] or sigHiroshima[i] or sigNagasaki[i]) for i in range(n)]
    cs4_bull = [validBody_MAT[i] and matrix_any_bull[i] and volRegTimeActive_MAT[i] for i in range(n)]
    cs4_bear = [validBody_MAT[i] and matrix_any_bear[i] and volRegTimeActive_MAT[i] for i in range(n)]

    sig = {
        "SAAB": sigSAAB, "Kratos": sigKratos, "BullRVOL1x": sigBull1x, "BearRVOL1x": sigBear1x,
        "GrandSlam": sigGrandSlam, "MOAB": sigMOAB,
        "Pentagon": sigPentagon, "WTC": sigWTC, "Hiroshima": sigHiroshima, "Nagasaki": sigNagasaki,
        "Long1": sigLong1, "Short1": sigShort1, "Long2": sigLong2, "Short2": sigShort2,
        "CS1_Bull": cs1_bull, "CS1_Bear": cs1_bear, "CS2_Bull": cs2_bull, "CS2_Bear": cs2_bear,
        "CS3_Bull": cs3_bull, "CS3_Bear": cs3_bear, "CS4_Bull": cs4_bull, "CS4_Bear": cs4_bear,
    }

    return {
        "ts": ts,
        "sig": sig,
        # numeric level series referenced by combos / debug / parity:
        "bb_np": bb_np,
        "relVol": relVol,
        "hybCumRatio": hybCumRatio,
        "bodyRat": bodyRat,
        "reg_ratio": reg_ratio,
        "thresholds": {
            "th_1x": th_1x, "th_saab_kratos": th_saab_kratos, "th_wtc": th_wtc,
            "th_gs_moab": th_gs_moab, "th_hiroshima": th_hiroshima,
        },
        # internal intermediates the parity harness re-derives independently:
        "_internal": {
            "bull_base": bull_base, "bear_base": bear_base, "rv_valid": rv_valid,
            "bullGZI": bullGZI, "bearGZI": bearGZI, "bullHV": bullHV, "bearHV": bearHV,
            "is_matrix": is_matrix, "fauna_bull": fauna_bull, "fauna_bear": fauna_bear,
            "matrix_any_bull": matrix_any_bull, "matrix_any_bear": matrix_any_bear,
            "validBody_FVG": validBody_FVG, "validBody_MAT": validBody_MAT,
        },
    }


def _level_for(pid: str, res: dict, i: int) -> float:
    """Numeric level for a detection plot at bar i (data-window value). None (Pine
    na) -> 0.0 so the level series stays numeric for the warehouse."""
    if pid in ("SAAB", "Kratos", "BullRVOL1x", "BearRVOL1x", "GrandSlam", "MOAB"):
        x = res["bb_np"][i]                            # normalized-price magnitude
        return float(x) if x is not None else 0.0
    if pid in ("Pentagon", "WTC", "Hiroshima", "Nagasaki"):
        return float(res["relVol"][i])                 # reg@time RVOL ratio
    if pid in ("Long1", "Short1", "Long2", "Short2"):
        return float(res["hybCumRatio"][i])            # cumulative RVOL ratio
    # combos: report body ratio of the firing bar (the gating magnitude)
    return float(res["bodyRat"][i])


def fire_matrix(bars: Sequence[Bar], params: Params | None = None, *, tf_seconds: int,
                confirmed_only: bool = True) -> dict:
    """FULL NINE NINES fire matrix: per-bar 0/1 fire + numeric level for EVERY
    detection plot in PLOT_IDS, plus the offset-applied coordinate events.

    One code path; grain-bound by the caller (the tick wrapper feeds N-tick bars,
    the time wrapper feeds time bars). Returns:
      ts                          : bar open timestamps (epoch ms)
      fire_<id>   (per plot)      : 0/1 fire (show-toggle AND signal), at the
                                    COMPUTE bar (offset NOT applied — raw matrix)
      level_<id>  (per plot)      : numeric level at the compute bar
      events                      : offset-applied coordinate events (FireEvent)
                                    honoring the Pine plotshape offset (-1 for FVG combos)
    """
    P = params or Params()
    res = compute(bars, P, tf_seconds=tf_seconds)
    n = len(bars)
    ts = res["ts"]
    sig = res["sig"]

    show = {
        "SAAB": P.show_SAAB, "Kratos": P.show_Kratos, "BullRVOL1x": P.show_BullRVOL1x,
        "BearRVOL1x": P.show_BearRVOL1x, "GrandSlam": P.show_GrandSlam, "MOAB": P.show_MOAB,
        "Pentagon": P.show_Pentagon, "WTC": P.show_WTC, "Hiroshima": P.show_Hiroshima,
        "Nagasaki": P.show_Nagasaki, "Long1": P.show_Long1, "Short1": P.show_Short1,
        "Long2": P.show_Long2, "Short2": P.show_Short2,
        "CS1_Bull": P.show_CS1_Bull, "CS1_Bear": P.show_CS1_Bear,
        "CS2_Bull": P.show_CS2_Bull, "CS2_Bear": P.show_CS2_Bear,
        "CS3_Bull": P.show_CS3_Bull, "CS3_Bear": P.show_CS3_Bear,
        "CS4_Bull": P.show_CS4_Bull, "CS4_Bear": P.show_CS4_Bear,
    }

    out: dict = {"ts": list(ts)}
    fires: dict[str, list[int]] = {}
    for pid in PLOT_IDS:
        arr = [1 if (show[pid] and sig[pid][i]) else 0 for i in range(n)]
        fires[pid] = arr
        out["fire_" + pid] = arr
        out["level_" + pid] = [(_level_for(pid, res, i) if arr[i] else 0.0) for i in range(n)]

    # offset-applied coordinate events (Pine offset=-1 paints one real bar back)
    events: list[FireEvent] = []
    for pid, (_desc, loc, shape, off) in PLOT_IDS.items():
        arr = fires[pid]
        for i in range(n):
            if arr[i]:
                j = i + off
                if 0 <= j < n:
                    events.append(FireEvent(
                        computed_ts_ms=ts[i], applied_ts_ms=ts[j],
                        plot_id=pid, location=loc, shape=shape,
                        level=out["level_" + pid][i]))
    events.sort(key=lambda e: (e.applied_ts_ms, e.plot_id))
    out["events"] = events
    out["fires"] = fires
    return out


@dataclass(frozen=True, slots=True)
class FireEvent:
    computed_ts_ms: int      # bar whose close computed the signal (epoch ms)
    applied_ts_ms: int       # bar the shape paints on after Pine `offset`
    plot_id: str
    location: str
    shape: str
    level: float
