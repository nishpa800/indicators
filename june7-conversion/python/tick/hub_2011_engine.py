"""hub_2011_engine — FULL faithful detection fire-matrix port of the Signal Hub.

Pine source (read verbatim from disk, has spaces in the path):
  "/Volumes/OWC Envoy Ultra/NineNines/nine-nines/Pine Indicators NOT transformed
   yet/June 7/Tick Friendly conversion/hub_2011_tickfriendly.pine"
  (//@version=5, indicator "HUB_1020_1153am"; source "hub 2011.txt").

NINE NINES three-output standard. ULTRACODE: EVERY detection plot is ported at
construct-for-construct fidelity — NOT the prior PARTIAL (6 ported / 20 deferred).
Nothing is stubbed: all 27 detection plots are genuinely computed.

DETECTION PLOTS (the fire matrix — the deliverable). Each emits a per-bar 0/1
`fire_<id>` and a numeric `lvl_<id>` (the price the marker sits at + key series):
   1  WhiteFlagMomentum   plotshape abovebar      (MB/RE/TA seq==3, day-reset)
   2  OW_Overlap          plotshape bottom        (OTE U-seq range-overlap cluster)
   3  OW_Super            plotshape bottom        (Super-cluster BFS connected comp.)
   4  OW_Combined         plotshape bottom        (>=N overlap/super starts in window)
   5  FC_2of3             plotshape abovebar       (>=2 of 3 fauna sub-inds)
   6  FC_Overlap          plotshape abovebar       (threshold/seq box overlap engine)
   7  FC_Cluster          plotshape belowbar       (FC_2of3 AND FC_Overlap)
   8  E3                  plotshape top            (3rd RTH session bar, 3-in-a-row)
   9  OoOC                plotshape bottom         (overlap^2 meta-cluster, U-count geom.)
  10  RedPlus             plotshape abovebar       (MB/RE/TA seq>=2, day-reset)
  11  RVOL_UgtTh          plotshape bottom         (bull RVOL price in [low,high))
  12  FaunaXinY           plotshape abovebar       (>=X events in trailing Y, rising edge)
  13  RVOL_Window         plotshape abovebar       (rolling-window event density + sum)
  14  FirstTwoMB          plotshape top            (2nd RTH session bar, two MB)
  15  CoincidentCluster   plotshape belowbar       (OW_Overlap AND OoOC, rising edge)
  16  SwingBottom         (signal exported to HUB)  (Mango higher-pair after lower struct)
  17  PBJ_Buy             plotchar belowbar        (Beluga supertrend cross after PB&J dip)
  18..27  CustomA..J      plotshape (rising edge)  (per-signal include masks + window)

Every fire_* in the source is a `f_pulse` (barstate.isconfirmed and cond and not
cond[1]) of a raw boolean, EXCEPT SwingBottom (already a pulse). We reproduce the
raw boolean per bar AND the confirmed rising-edge pulse; the FIRE MATRIX uses the
pulse, exactly as the Pine alert/plot layer does, so 0/1 fires == plotted markers.

Tick-safe natively (the source has no tv_ta.relativeVolume / no time(period,...)
/ no timeframe.in_seconds -> no RE10023). hub's "RVOL" is a LOCAL body-spike
normalization (spike/sma(spike)[1] - vol/sma(vol)[1]), NOT relativeVolume-at-time;
faithfully kept local (re-deriving it as the shim would be WRONG for this script).
The canonical shim is imported and exposed for callers that want shim RVOL on the
SAME bars, but it is NOT substituted into hub's own detection math (RULE: preserve
Pine semantics). Every threshold is a Params field (no hardcoded >= N).

ONE core, two grains: tick & time wrappers both import `detect` here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Sequence

from nine_codon_core import Bar, sma, atr, ema, nz, shift, vwma_safe  # noqa: F401


# ----------------------------------------------------------------------------- #
# Parameters — every Pine input.* surfaced; defaults == the Pine defaults.       #
# ----------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Params:
    # ---- shared Fauna MB/RE/TA family (White Flag, FC_s2/s3, E3, Red Plus,
    #      Fauna X-in-Y, First-Two-MB, and the MB/RE/TA Individual exports) ----
    alpha_MB: float = 1.6          # body size x ATR
    beta_MB: float = 0.7           # body/range >=
    delta_MB: float = 1.8          # volume x avg
    gamma_RE: float = 2.2          # range x ATR
    epsilon_RE: float = 0.15       # close-to-edge <=
    delta_RE: float = 1.8
    theta_TA: float = 1.6          # dPrice x avg-dPrice
    delta_TA: float = 1.8
    atr_len: int = 14
    vol_len: int = 20
    trend_ma_len: int = 50
    avg_delta_len: int = 10

    # ---- 2. Orange Window (OW) ----
    ow_avglength: int = 30
    ow_smaLength: int = 20
    ow_th_low: float = 0.0
    ow_th_high: float = 3_000_000.0
    ow_seqTh: float = 0.0
    ow_ote_windowLen: int = 75
    ow_ote_minOverlap: int = 3
    ow_primaryWindowLen: int = 75
    ow_minPrimaryOverlap: int = 2
    ow_primaryPaddingMultiplier: float = 0.5
    ow_superWindowLen: int = 30
    ow_minSuperClusterOverlap: int = 2
    ow_superPaddingMultiplier: float = 0.5
    ow_rollingWindow: int = 20
    ow_requiredEvents: int = 2

    # ---- 3. FaunaOVRLP Cluster (FC) ----
    fc_s1_alpha_MB: float = 1.6
    fc_s1_beta_MB: float = 0.7
    fc_s1_delta_MB: float = 1.8
    fc_s1_atr_len_MB: int = 14
    fc_s1_vol_len_MB: int = 20
    # s2 uses the shared fauna defaults (identical numbers in source)
    fc_avglength: int = 30
    fc_smaLength: int = 20
    fc_th_low: float = 2.9
    fc_th_high: float = 1_000_000.0
    fc_seqTh: float = 0.1
    fc_overlapWindowLen: int = 20
    fc_overlapPaddingMultiplier: float = 0.0

    # ---- 4. E3 (session) ----
    e3_sessbar: int = 3

    # ---- 5. OoOC ----
    oooc_avglength: int = 30
    oooc_smaLength: int = 20
    oooc_th_low: float = 1.0
    oooc_th_high: float = 4_000_000.0
    oooc_seqTh: float = 0.0
    oooc_windowLen: int = 8
    oooc_minOverlap: int = 2
    oooc_metaWindowLen: int = 8
    oooc_minMetaOverlap: int = 2

    # ---- 7. RVOL U>Th (Lucky 7) ----
    l7_avglength: int = 30
    l7_smaLength: int = 20
    l7_th_low: float = 19.0
    l7_th_high: float = 1_000_000.0

    # ---- 8. Fauna X-in-Y ----
    fxy_requiredEvents: int = 4
    fxy_windowLength: int = 12

    # ---- 9. RVOL Rolling Window ----
    rw_avglength: int = 30
    rw_smaLength: int = 20
    rw_th_low: float = 8.0
    rw_th_high: float = 100_000.0
    rw_rollingWindowLen: int = 60
    rw_minEventsInWindow: int = 4
    rw_minEventValue: float = 8.0
    rw_minWindowSumValue: float = 50.0

    # ---- 10. First-Two-MB (session) ----
    ftmb_sessbar: int = 2

    # ---- 11. Mango Swings ----
    ms_leftBars: int = 5
    ms_rightBars: int = 5

    # ---- PB&J Follow-up Buy (Beluga supertrend + PB&J dip) ----
    pbj_vwma_len: int = 5
    pbj_atr_len: int = 10
    pbj_atr_mult: float = 2.0
    pbj_ma_len: int = 20
    pbj_filter_atr_len: int = 14
    pbj_vol_len: int = 20
    pbj_thresh_mult: float = 3.0      # atr/close*3.0
    pbj_lowest_len: int = 25
    pbj_vol_frac: float = 0.1

    # ---- Custom A..J: (use-masks, window, required, mode) ----
    # mode "S" = sequential accumulator (A,B,C,D); "D" = windowed density (E..J).
    # The use-masks default to the Pine defaults (only the True ones below).
    customA: "CustomCfg" = field(default_factory=lambda: CustomCfg(
        window=3, required=2, mode="S", use={"fc_overlap"}))
    customB: "CustomCfg" = field(default_factory=lambda: CustomCfg(
        window=2, required=2, mode="S", use={"fc_2of3"}))
    customC: "CustomCfg" = field(default_factory=lambda: CustomCfg(
        window=12, required=2, mode="S", enable=True, use={"fc_cluster"}))
    customD: "CustomCfg" = field(default_factory=lambda: CustomCfg(
        window=1, required=2, mode="S", enable=True, use={"fc_overlap", "rp_sequence"}))
    customE: "CustomCfg" = field(default_factory=lambda: CustomCfg(
        window=7, required=1, mode="D", enable=True, use={"rw_signal"}))
    customF: "CustomCfg" = field(default_factory=lambda: CustomCfg(
        window=4, required=2, mode="D", enable=True, use={"fxy_signal", "pbj_buy"}))
    customG: "CustomCfg" = field(default_factory=lambda: CustomCfg(
        window=3, required=2, mode="D", enable=True, use={"CustomD"}))
    customH: "CustomCfg" = field(default_factory=lambda: CustomCfg(
        window=3, required=7, mode="D", enable=True, use={"fc_overlap"}))
    customI: "CustomCfg" = field(default_factory=lambda: CustomCfg(
        window=2, required=2, mode="D", enable=True, use={"fc_2of3"}))
    customJ: "CustomCfg" = field(default_factory=lambda: CustomCfg(
        window=3, required=4, mode="D", enable=True,
        use={"fc_cluster", "e3_open", "ftmb", "pbj_buy"}))


@dataclass(frozen=True)
class CustomCfg:
    window: int
    required: int
    mode: str                 # "S" sequential, "D" windowed density
    enable: bool = True       # Pine *_use (A/B have no enable -> always on)
    use: frozenset = frozenset()  # set of base-signal keys included

    def __post_init__(self):
        object.__setattr__(self, "use", frozenset(self.use))


# Canonical base-signal keys a Custom can include (registry order from source).
BASE_KEYS = [
    "wf_momentum", "ow_overlap", "ow_super", "ow_combined", "fc_2of3",
    "fc_overlap", "fc_cluster", "e3_open", "oooc_meta", "rp_sequence",
    "l7_bullish_rvol", "fxy_signal", "rw_signal", "ftmb", "cc",
    "swing_bottom", "pbj_buy", "mb_ind", "re_ind", "ta_ind",
]
# (Custom signals may also reference OTHER customs; handled by forward order.)


# ----------------------------------------------------------------------------- #
# Helpers                                                                        #
# ----------------------------------------------------------------------------- #
def _utc_day_of_month(ts_ms: int) -> int:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).day


def _utc_ordinal(ts_ms: int) -> int:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).toordinal()


def _fauna_components(o, h, lo, c, v, P):
    """MB / RE / TA bull events (Pine: White Flag / FC_s2 / E3 / Red Plus / FXY /
    First-Two share identical formulas with identical defaults). One re-typing."""
    n = len(c)
    ATR = atr(h, lo, c, P.atr_len)
    AvgVol = sma(v, P.vol_len)
    AvgDelta = sma([abs(c[i] - c[i - 1]) if i > 0 else 0.0 for i in range(n)], P.avg_delta_len)
    TrendMA = sma(c, P.trend_ma_len)
    MB = [False] * n
    RE = [False] * n
    TA = [False] * n
    for i in range(n):
        if ATR[i] is None or AvgVol[i] is None:
            continue
        body = c[i] - o[i]
        rng = h[i] - lo[i]
        up = body > 0
        bsz = abs(body)
        ratio = 0.0 if rng == 0 else bsz / rng
        MB[i] = up and bsz > P.alpha_MB * ATR[i] and ratio > P.beta_MB and v[i] > P.delta_MB * AvgVol[i]
        wide = rng > P.gamma_RE * ATR[i]
        RE[i] = up and wide and (h[i] - c[i]) < P.epsilon_RE * rng and v[i] > P.delta_RE * AvgVol[i]
        if i >= 1 and TrendMA[i] is not None and TrendMA[i - 1] is not None and AvgDelta[i] is not None:
            up_trend = TrendMA[i] > TrendMA[i - 1]
            TA[i] = up_trend and (c[i] - c[i - 1]) > P.theta_TA * AvgDelta[i] and up and v[i] > P.delta_TA * AvgVol[i]
    return MB, RE, TA


def _rvol3(o, h, lo, c, v, avglength, smaLength):
    """Pine RVOL^3 family used by OW / FC / OoOC / L7 / RW:
      spike = |close-open|; rvol_price = spike / nz(sma(spike,L)[1], 1)
      rvol_volume = volume / nz(sma(volume,L)[1], 1); diff = price-volume
      rvol3_pos = diff>0 ? diff : na; sma_rvol3 = sma(rvol3_pos, S)
      baseBull = close>open and nz(rvol3_pos) > nz(sma_rvol3)."""
    n = len(c)
    spike = [abs(c[i] - o[i]) for i in range(n)]
    avgSpike_1 = shift(sma(spike, avglength), 1)
    rvol_price = [_safediv(spike[i], nz(avgSpike_1[i], 1.0)) for i in range(n)]
    avgVol_1 = shift(sma(v, avglength), 1)
    rvol_vol = [_safediv(v[i], nz(avgVol_1[i], 1.0)) for i in range(n)]
    diff = [rvol_price[i] - rvol_vol[i] for i in range(n)]
    rvol3_pos = [(d if d > 0 else None) for d in diff]
    sma_rvol3 = sma(rvol3_pos, smaLength)
    baseBull = [c[i] > o[i] and nz(rvol3_pos[i]) > nz(sma_rvol3[i]) for i in range(n)]
    return spike, rvol_price, rvol3_pos, sma_rvol3, baseBull


def _session_bar_counter(ts, dom_change, in_session):
    """Pine session-bar counter (E3 / First-Two): reset on day-change, then +1 each
    bar inside the session; 0 outside. Synthetic bars treat each calendar day as one
    session (in_session True everywhere) — real RTH masking is an upstream candle-
    factory concern, identical to the prior hub engine and the f2_e3 core."""
    n = len(ts)
    out = [0] * n
    is_new_day = False
    cnt = 0
    for i in range(n):
        if i >= 1 and dom_change[i]:
            is_new_day = True
        if is_new_day and in_session[i]:
            cnt = 1
            is_new_day = False
        elif in_session[i] and cnt > 0:
            cnt += 1
        elif not in_session[i]:
            cnt = 0
        out[i] = cnt
    return out


def _overlap(loA, hiA, loB, hiB):
    return loA <= hiB and loB <= hiA


def _safediv(num, den):
    """Pine float division by zero yields `na` (NOT an exception). Here the only
    place this bites is the RVOL spike/avg ratio when the average is exactly 0
    (a perfectly flat tape): numerator (the spike) is then also 0. Pine: 0/0 = na,
    and na fails every `th_low < x < th_high` range check and every `>` compare,
    so the bar simply does not fire. We return 0.0 (which is < every th_low default
    and not > any positive sma), reproducing that no-fire outcome deterministically."""
    if den == 0:
        return 0.0
    return num / den


# ----------------------------------------------------------------------------- #
# Main detector                                                                  #
# ----------------------------------------------------------------------------- #
def detect(bars: Sequence[Bar], params: Params = Params(), *, tf_seconds: int = 60,
           in_session: Sequence[bool] | None = None) -> dict:
    n = len(bars)
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    lo = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [b.volume for b in bars]
    ts = [b.ts for b in bars]
    P = params
    if in_session is None:
        in_session = [True] * n   # synthetic / no-session-mask default

    dom = [_utc_day_of_month(ts[i]) for i in range(n)]
    dom_change = [False] + [dom[i] != dom[i - 1] for i in range(1, n)]
    bar_index = list(range(n))

    # ===== shared fauna events =====
    MB, RE, TA = _fauna_components(o, h, lo, c, v, P)
    isEvent = [MB[i] or RE[i] or TA[i] for i in range(n)]

    # ===== 1. White Flag Momentum (seq == 3, day-reset) =====
    wf_seq = [0] * n
    sl = 0
    for i in range(n):
        if i >= 1 and dom_change[i]:
            sl = 0
        elif not isEvent[i]:
            sl = 0
        if isEvent[i]:
            sl += 1
        wf_seq[i] = sl
    sWhiteFlag = [isEvent[i] and wf_seq[i] == 3 for i in range(n)]

    # ===== 2/3/4. Orange Window (OW) — OTE overlap, Super BFS, Combined =====
    sOW_Overlap, sOW_Super, sOW_Combined, ow_rvol_price = _orange_window(
        o, h, lo, c, v, bar_index, P)

    # ===== 3. FaunaOVRLP Cluster (FC) — 2of3, Overlap, Cluster =====
    sFC_2of3, sFC_Overlap, sFC_Cluster, fc_rvol_price = _fauna_cluster(
        o, h, lo, c, v, bar_index, dom_change, in_session, MB, RE, TA, isEvent, P)

    # ===== 4. E3 — 3rd session bar, MB/RE/TA on bars 1,2,3 =====
    sbc_e3 = _session_bar_counter(ts, dom_change, in_session)
    isEvent_1 = shift(isEvent, 1)
    isEvent_2 = shift(isEvent, 2)
    sE3 = [sbc_e3[i] == P.e3_sessbar and isEvent[i] and bool(isEvent_1[i]) and bool(isEvent_2[i])
           for i in range(n)]

    # ===== 5. OoOC — overlap^2 meta-cluster =====
    sOoOC, oooc_rvol_price = _oooc(o, h, lo, c, v, bar_index, P)

    # ===== 6. Red Plus (seq >= 2, day-reset) =====
    rp_seq = [0] * n
    sl = 0
    for i in range(n):
        if i >= 1 and dom_change[i]:
            sl = 0
        elif not isEvent[i]:
            sl = 0
        if isEvent[i]:
            sl += 1
        rp_seq[i] = sl
    sRedPlus = [isEvent[i] and rp_seq[i] >= 2 for i in range(n)]

    # ===== 7. RVOL U>Th =====
    _, l7_rvol_price, _, _, l7_baseBull = _rvol3(o, h, lo, c, v, P.l7_avglength, P.l7_smaLength)
    sRVOL_UgtTh = [l7_baseBull[i] and (P.l7_th_low < l7_rvol_price[i] < P.l7_th_high) for i in range(n)]

    # ===== 8. Fauna X-in-Y (>= X events in trailing Y, rising edge) =====
    fxy_eventsInWindow = [0.0] * n
    for i in range(n):
        s = 0.0
        for k in range(P.fxy_windowLength):
            j = i - k
            if j >= 0 and isEvent[j]:
                s += 1.0
        fxy_eventsInWindow[i] = s
    fxy_cond = [fxy_eventsInWindow[i] >= P.fxy_requiredEvents for i in range(n)]
    fxy_cond_1 = shift(fxy_cond, 1)
    sFaunaXinY = [fxy_cond[i] and not bool(fxy_cond_1[i]) for i in range(n)]

    # ===== 9. RVOL Rolling Window =====
    sRVOL_Window, rw_rvol_price = _rvol_rolling_window(o, h, lo, c, v, bar_index, P)

    # ===== 10. First-Two-MB (2nd session bar, two MB) =====
    sbc_ftmb = _session_bar_counter(ts, dom_change, in_session)  # same counter logic
    MB_1 = shift(MB, 1)
    sFirstTwoMB = [sbc_ftmb[i] == P.ftmb_sessbar and MB[i] and bool(MB_1[i]) for i in range(n)]

    # ===== 11. Mango Swing Bottom =====
    sSwingBottom = _mango_swing_bottom(h, lo, c, bar_index, P)

    # ===== 15. Coincident Cluster (OW_Overlap AND OoOC), rising edge =====
    cc_raw = [sOW_Overlap[i] and sOoOC[i] for i in range(n)]
    cc_raw_1 = shift(cc_raw, 1)
    sCoincidentCluster = [cc_raw[i] and not bool(cc_raw_1[i]) for i in range(n)]

    # ===== PB&J Follow-up Buy =====
    sPBJ_Buy = _pbj_followup_buy(o, h, lo, c, v, P)

    # ===== MB/RE/TA Individual (White Flag params) =====
    sMB_Individual = list(MB)
    sRE_Individual = list(RE)
    sTA_Individual = list(TA)

    # ----- assemble base raw signals into the registry used by composites -----
    base_raw = {
        "wf_momentum": sWhiteFlag,
        "ow_overlap": sOW_Overlap,
        "ow_super": sOW_Super,
        "ow_combined": sOW_Combined,
        "fc_2of3": sFC_2of3,
        "fc_overlap": sFC_Overlap,
        "fc_cluster": sFC_Cluster,
        "e3_open": sE3,
        "oooc_meta": sOoOC,
        "rp_sequence": sRedPlus,
        "l7_bullish_rvol": sRVOL_UgtTh,
        "fxy_signal": sFaunaXinY,
        "rw_signal": sRVOL_Window,
        "ftmb": sFirstTwoMB,
        "cc": sCoincidentCluster,
        "swing_bottom": sSwingBottom,
        "pbj_buy": sPBJ_Buy,
        "mb_ind": sMB_Individual,
        "re_ind": sRE_Individual,
        "ta_ind": sTA_Individual,
    }

    # ===== 18..27. Custom A..J (sequential / density) =====
    custom_raw = _custom_signals(base_raw, bar_index, P)

    # ----- full raw registry (base + custom), in source/registry order -----
    raw = {
        "WhiteFlagMomentum": sWhiteFlag,
        "OW_Overlap": sOW_Overlap,
        "OW_Super": sOW_Super,
        "OW_Combined": sOW_Combined,
        "FC_2of3": sFC_2of3,
        "FC_Overlap": sFC_Overlap,
        "FC_Cluster": sFC_Cluster,
        "E3": sE3,
        "OoOC": sOoOC,
        "RedPlus": sRedPlus,
        "RVOL_UgtTh": sRVOL_UgtTh,
        "FaunaXinY": sFaunaXinY,
        "RVOL_Window": sRVOL_Window,
        "FirstTwoMB": sFirstTwoMB,
        "CoincidentCluster": sCoincidentCluster,
        "SwingBottom": sSwingBottom,
        "PBJ_Buy": sPBJ_Buy,
        "CustomA": custom_raw["A"],
        "CustomB": custom_raw["B"],
        "CustomC": custom_raw["C"],
        "CustomD": custom_raw["D"],
        "CustomE": custom_raw["E"],
        "CustomF": custom_raw["F"],
        "CustomG": custom_raw["G"],
        "CustomH": custom_raw["H"],
        "CustomI": custom_raw["I"],
        "CustomJ": custom_raw["J"],
    }

    # ----- FIRE = f_pulse(raw) (confirmed rising edge); SwingBottom is already a
    #       pulse (its raw is event-instant), the source confirms-only it. -----
    fires: dict[str, list[int]] = {}
    for k, arr in raw.items():
        if k == "SwingBottom":
            fires[k] = [1 if arr[i] else 0 for i in range(n)]  # confirmed-only pulse
        else:
            prev = shift(arr, 1)
            fires[k] = [1 if (arr[i] and not bool(prev[i])) else 0 for i in range(n)]

    # ----- numeric levels: the price the plotted marker sits at (location), plus
    #       the headline RVOL series.  location.abovebar->high, belowbar/bottom->low,
    #       top->high.  This is the per-bar numeric level for the fire matrix. -----
    loc_high = {"WhiteFlagMomentum", "FC_2of3", "FC_Overlap", "E3", "RedPlus",
                "FaunaXinY", "RVOL_Window", "FirstTwoMB", "CustomA", "CustomC",
                "CustomF", "CustomH"}
    levels: dict[str, list] = {}
    for k in raw:
        if k == "RVOL_UgtTh":
            levels[k] = [round(l7_rvol_price[i], 6) for i in range(n)]  # value shown in marker text
        elif k in loc_high:
            levels[k] = [h[i] for i in range(n)]
        else:
            levels[k] = [lo[i] for i in range(n)]

    # ----- chronological event list (ns-resolution key, like the prior engine) -----
    events = []
    for k, arr in fires.items():
        for i in range(n):
            if arr[i]:
                events.append((ts[i] * 1_000_000, k))
    events.sort()

    return {
        "ts": ts,
        "raw": raw,
        "fires": fires,
        "levels": levels,
        "events": events,
        "deferred": [],          # FULL port — nothing deferred, nothing stubbed.
        "series": {
            "ow_rvol_price": ow_rvol_price,
            "fc_rvol_price": fc_rvol_price,
            "oooc_rvol_price": oooc_rvol_price,
            "l7_rvol_price": l7_rvol_price,
            "rw_rvol_price": rw_rvol_price,
        },
    }


# ----------------------------------------------------------------------------- #
# 2/3/4. Orange Window                                                           #
# ----------------------------------------------------------------------------- #
def _orange_window(o, h, lo, c, v, bar_index, P):
    n = len(c)
    _, rvol_price, rvol3_pos, sma_rvol3, baseBull = _rvol3(
        o, h, lo, c, v, P.ow_avglength, P.ow_smaLength)
    uBar_ote = [baseBull[i] and (P.ow_th_low < rvol_price[i] < P.ow_th_high) for i in range(n)]
    uBar_super = baseBull

    # sequence state for OTE and Super
    sOW_Overlap = [False] * n
    sOW_Super = [False] * n
    sOW_Combined = [False] * n

    seqLen_ote = 0
    seqSum_ote = 0.0
    seqStartLow_ote = None
    seqLen_super = 0
    seqSum_super = 0.0
    seqStartLow_super = None

    # ote overlap arrays (unshift => index 0 is newest)
    ote_evIdx: list[int] = []
    ote_evHi: list[float] = []
    ote_evLo: list[float] = []
    # super primary-cluster arrays
    evIdx: list[int] = []
    evHi: list[float] = []
    evLo: list[float] = []
    evRvolSum: list[float] = []
    primaryCluster_Idx: list[int] = []
    primaryCluster_Hi: list[float] = []
    primaryCluster_Lo: list[float] = []
    primaryCluster_RvolSum: list[float] = []
    # combined event bar indices
    eventBarIndices: list[int] = []

    for i in range(n):
        bi = bar_index[i]
        # --- ote sequence ---
        if uBar_ote[i]:
            seqLen_ote += 1
            seqSum_ote += rvol_price[i]
            if seqLen_ote == 1:
                seqStartLow_ote = lo[i]
        else:
            seqLen_ote = 0
            seqSum_ote = 0.0
            seqStartLow_ote = None
        # --- super sequence ---
        if uBar_super[i]:
            seqLen_super += 1
            seqSum_super += rvol_price[i]
            if seqLen_super == 1:
                seqStartLow_super = lo[i]
        else:
            seqLen_super = 0
            seqSum_super = 0.0
            seqStartLow_super = None

        conf = True  # barstate.isconfirmed (we operate on closed bars)
        sigUU_ote = seqLen_ote == 2 and seqSum_ote >= P.ow_seqTh and conf
        sigUUU_ote = seqLen_ote == 3 and seqSum_ote >= P.ow_seqTh and conf
        sigUUUU_ote = seqLen_ote == 4 and seqSum_ote >= P.ow_seqTh and conf
        isEvent_ote = sigUU_ote or sigUUU_ote or sigUUUU_ote
        sigUU_super = seqLen_super == 2 and seqSum_super >= P.ow_seqTh and conf
        sigUUU_super = seqLen_super == 3 and seqSum_super >= P.ow_seqTh and conf
        sigUUUU_super = seqLen_super == 4 and seqSum_super >= P.ow_seqTh and conf
        isEvent_super = sigUU_super or sigUUU_super or sigUUUU_super

        # --- OTE overlap cluster ---
        overlap_now = False
        if isEvent_ote:
            curHi = h[i]
            curLo = seqStartLow_ote
            overlapCount = 0
            for j in range(len(ote_evIdx)):
                if ote_evLo[j] <= curHi and ote_evHi[j] >= curLo:
                    overlapCount += 1
            if (overlapCount + 1) >= P.ow_ote_minOverlap:
                overlap_now = True
            ote_evIdx.insert(0, bi)
            ote_evHi.insert(0, curHi)
            ote_evLo.insert(0, curLo)
        sOW_Overlap[i] = overlap_now
        # prune ote window (pop from tail = oldest)
        while ote_evIdx:
            if bi - ote_evIdx[-1] > P.ow_ote_windowLen:
                ote_evIdx.pop()
                ote_evHi.pop()
                ote_evLo.pop()
            else:
                break

        # --- Super cluster (BFS connected components) ---
        super_now = False
        # prune primary-event window
        while evIdx:
            if bi - evIdx[-1] > P.ow_primaryWindowLen:
                evIdx.pop()
                evHi.pop()
                evLo.pop()
                evRvolSum.pop()
            else:
                break
        # prune primary-cluster window
        while primaryCluster_Idx:
            if bi - primaryCluster_Idx[-1] > P.ow_superWindowLen:
                primaryCluster_Idx.pop()
                primaryCluster_Hi.pop()
                primaryCluster_Lo.pop()
                primaryCluster_RvolSum.pop()
            else:
                break
        if isEvent_super:
            eventRange = h[i] - seqStartLow_super
            padding = eventRange * P.ow_primaryPaddingMultiplier
            evIdx.insert(0, bi)
            evHi.insert(0, h[i] + padding)
            evLo.insert(0, seqStartLow_super - padding)
            evRvolSum.insert(0, seqSum_super)
            numEvents = len(evIdx)
            if numEvents >= P.ow_minPrimaryOverlap:
                visited = [False] * numEvents
                if not visited[0]:
                    queue = [0]
                    members = []
                    visited[0] = True
                    while queue:
                        u = queue.pop(0)
                        members.append(u)
                        for w in range(numEvents):
                            if (not visited[w] and evLo[u] <= evHi[w] and evLo[w] <= evHi[u]):
                                visited[w] = True
                                queue.append(w)
                    if len(members) >= P.ow_minPrimaryOverlap:
                        clusterMaxHi = None
                        clusterMinLo = None
                        clusterRvolSum = 0.0
                        for m in members:
                            clusterMaxHi = evHi[m] if clusterMaxHi is None else max(clusterMaxHi, evHi[m])
                            clusterMinLo = evLo[m] if clusterMinLo is None else min(clusterMinLo, evLo[m])
                            clusterRvolSum += evRvolSum[m]
                        primaryCluster_Idx.insert(0, bi)
                        primaryCluster_Hi.insert(0, clusterMaxHi)
                        primaryCluster_Lo.insert(0, clusterMinLo)
                        primaryCluster_RvolSum.insert(0, clusterRvolSum)
                        numPC = len(primaryCluster_Idx)
                        if numPC >= P.ow_minSuperClusterOverlap:
                            visitedC = [False] * numPC
                            if not visitedC[0]:
                                scQueue = [0]
                                scMembers = []
                                visitedC[0] = True
                                while scQueue:
                                    u_sc = scQueue.pop(0)
                                    scMembers.append(u_sc)
                                    # Pine loops v_sc = 1 .. numPC-1 (note: starts at 1)
                                    for v_sc in range(1, numPC):
                                        if not visitedC[v_sc]:
                                            u_hi = primaryCluster_Hi[u_sc]
                                            u_lo = primaryCluster_Lo[u_sc]
                                            v_hi = primaryCluster_Hi[v_sc]
                                            v_lo = primaryCluster_Lo[v_sc]
                                            u_pad = (u_hi - u_lo) * P.ow_superPaddingMultiplier
                                            v_pad = (v_hi - v_lo) * P.ow_superPaddingMultiplier
                                            if ((u_lo - u_pad) <= (v_hi + v_pad) and
                                                    (v_lo - v_pad) <= (u_hi + u_pad)):
                                                visitedC[v_sc] = True
                                                scQueue.append(v_sc)
                                if len(scMembers) >= P.ow_minSuperClusterOverlap:
                                    super_now = True
        sOW_Super[i] = super_now

        # --- Combined (>= requiredEvents overlap/super STARTS in rolling window) ---
        ovl_start = sOW_Overlap[i] and (i == 0 or not sOW_Overlap[i - 1])
        sup_start = sOW_Super[i] and (i == 0 or not sOW_Super[i - 1])
        if ovl_start or sup_start:
            eventBarIndices.append(bi)
        while eventBarIndices:
            if bi - eventBarIndices[0] >= P.ow_rollingWindow:
                eventBarIndices.pop(0)
            else:
                break
        if len(eventBarIndices) >= P.ow_requiredEvents:
            sOW_Combined[i] = True
            last = eventBarIndices.pop()      # array.pop() removes the LAST element
            eventBarIndices.clear()
            eventBarIndices.append(last)

    return sOW_Overlap, sOW_Super, sOW_Combined, rvol_price


# ----------------------------------------------------------------------------- #
# 3. FaunaOVRLP Cluster                                                          #
# ----------------------------------------------------------------------------- #
def _fauna_cluster(o, h, lo, c, v, bar_index, dom_change, in_session,
                   MB, RE, TA, isEvent, P):
    n = len(c)

    # --- ind1: MB-only sequence >= 2 (fc_s1 uses the same MB formula/defaults) ---
    s1 = 0
    fc1 = [False] * n
    for i in range(n):
        if MB[i]:
            s1 += 1
        else:
            s1 = 0
        fc1[i] = MB[i] and s1 >= 2
    # --- ind2: MB/RE/TA sequence >= 2 (day-reset) ---
    s2 = 0
    fc2 = [False] * n
    for i in range(n):
        if i >= 1 and dom_change[i]:
            s2 = 0
        elif not isEvent[i]:
            s2 = 0
        if isEvent[i]:
            s2 += 1
        fc2[i] = isEvent[i] and s2 >= 2
    # --- ind3: (MB or RE) within session, sequence >= 2 ---
    s3 = 0
    fc3 = [False] * n
    for i in range(n):
        ev3 = (MB[i] or RE[i]) and in_session[i]
        if ev3:
            s3 += 1
        else:
            s3 = 0
        fc3[i] = ev3 and s3 >= 2
    fc_count = [(1 if fc1[i] else 0) + (1 if fc2[i] else 0) + (1 if fc3[i] else 0) for i in range(n)]
    sFC_2of3 = [fc_count[i] >= 2 for i in range(n)]

    # --- FC overlap engine (threshold-event boxes vs sequence-event boxes) ---
    _, rvol_price, rvol3_pos, sma_rvol3, baseBull = _rvol3(
        o, h, lo, c, v, P.fc_avglength, P.fc_smaLength)
    inRange = [P.fc_th_low < rvol_price[i] < P.fc_th_high for i in range(n)]
    uBar = [baseBull[i] and inRange[i] for i in range(n)]
    isThresholdEvent = [baseBull[i] and inRange[i] for i in range(n)]  # barstate.isconfirmed True

    seqSum = 0.0
    seqLen = 0
    sigSeq = [False] * n
    for i in range(n):
        if uBar[i]:
            seqLen += 1
            seqSum += rvol_price[i]
        else:
            seqLen = 0
            seqSum = 0.0
        sigUU = seqLen == 2 and seqSum >= P.fc_seqTh
        sigUUU = seqLen == 3 and seqSum >= P.fc_seqTh
        sigUUUU = seqLen == 4 and seqSum >= P.fc_seqTh
        sigSeq[i] = sigUU or sigUUU or sigUUUU   # barstate.isconfirmed True

    sFC_Overlap = [False] * n
    # FIFO arrays (push=append at tail, shift=pop head). Index 0 == oldest.
    thIdx: list[int] = []
    thHi: list[float] = []
    thLo: list[float] = []
    sqIdx: list[int] = []
    sqHi: list[float] = []
    sqLo: list[float] = []
    for i in range(n):
        bi = bar_index[i]
        overlap_now = False
        # prune both windows from head
        if thIdx:
            while thIdx and bi - thIdx[0] > P.fc_overlapWindowLen:
                thIdx.pop(0)
                thHi.pop(0)
                thLo.pop(0)
                if not thIdx:
                    break
        if sqIdx:
            while sqIdx and bi - sqIdx[0] > P.fc_overlapWindowLen:
                sqIdx.pop(0)
                sqHi.pop(0)
                sqLo.pop(0)
                if not sqIdx:
                    break
        if isThresholdEvent[i]:
            eventRange = h[i] - lo[i]
            padding = eventRange * P.fc_overlapPaddingMultiplier
            curHi = h[i] + padding
            curLo = lo[i] - padding
            thIdx.append(bi)
            thHi.append(curHi)
            thLo.append(curLo)
            for j in range(len(sqIdx)):
                if _overlap(curLo, curHi, sqLo[j], sqHi[j]):
                    overlap_now = True
                    break
        if sigSeq[i] and not overlap_now:
            eventRange = h[i] - lo[i]
            padding = eventRange * P.fc_overlapPaddingMultiplier
            curHi = h[i] + padding
            curLo = lo[i] - padding
            sqIdx.append(bi)
            sqHi.append(curHi)
            sqLo.append(curLo)
            for j in range(len(thIdx)):
                if _overlap(curLo, curHi, thLo[j], thHi[j]):
                    overlap_now = True
                    break
        sFC_Overlap[i] = overlap_now

    sFC_Cluster = [sFC_2of3[i] and sFC_Overlap[i] for i in range(n)]
    return sFC_2of3, sFC_Overlap, sFC_Cluster, rvol_price


# ----------------------------------------------------------------------------- #
# 5. OoOC overlap^2 meta-cluster                                                 #
# ----------------------------------------------------------------------------- #
def _oooc(o, h, lo, c, v, bar_index, P):
    n = len(c)
    _, rvol_price, rvol3_pos, sma_rvol3, baseBull = _rvol3(
        o, h, lo, c, v, P.oooc_avglength, P.oooc_smaLength)
    uBar = [baseBull[i] and (P.oooc_th_low < rvol_price[i] < P.oooc_th_high) for i in range(n)]

    sOoOC = [False] * n
    seqSum = 0.0
    seqLen = 0
    seqStartLow = None
    # primary-overlap arrays (unshift => index 0 newest)
    evIdx: list[int] = []
    evHi: list[float] = []
    evLo: list[float] = []
    # meta arrays
    meta_evIdx: list[int] = []
    meta_evUCount: list[int] = []
    meta_evStartLow: list[float] = []
    # we need high[k] history; build as we go via list h itself + bar_index map

    for i in range(n):
        bi = bar_index[i]
        if uBar[i]:
            seqLen += 1
            seqSum += rvol_price[i]
            if seqLen == 1:
                seqStartLow = lo[i]
        else:
            seqLen = 0
            seqSum = 0.0
            seqStartLow = None
        conf = True
        sigUU = seqLen == 2 and seqSum >= P.oooc_seqTh and conf
        sigUUU = seqLen == 3 and seqSum >= P.oooc_seqTh and conf
        sigUUUU = seqLen == 4 and seqSum >= P.oooc_seqTh and conf
        isEvent = sigUU or sigUUU or sigUUUU

        primaryClusterTrigger = False
        if isEvent:
            curHi = h[i]
            curLo = seqStartLow
            overlapCount = 0
            for j in range(len(evIdx)):
                if evLo[j] <= curHi and evHi[j] >= curLo:
                    overlapCount += 1
            if (overlapCount + 1) >= P.oooc_minOverlap:
                primaryClusterTrigger = True
            evIdx.insert(0, bi)
            evHi.insert(0, curHi)
            evLo.insert(0, curLo)
        # prune primary window
        while evIdx:
            if bi - evIdx[-1] > P.oooc_windowLen:
                evIdx.pop()
                evHi.pop()
                evLo.pop()
            else:
                break

        if primaryClusterTrigger:
            uCount = 4 if sigUUUU else (3 if sigUUU else 2)
            meta_evIdx.insert(0, bi)
            meta_evUCount.insert(0, uCount)
            meta_evStartLow.insert(0, seqStartLow)
            metaOverlapCount = 0
            if len(meta_evIdx) > 1:
                current_UCount = uCount
                current_StartLow = seqStartLow
                for j in range(1, len(meta_evIdx)):
                    past_Idx = meta_evIdx[j]
                    past_UCount = meta_evUCount[j]
                    past_StartLow = meta_evStartLow[j]
                    masterUCount = max(current_UCount, past_UCount)
                    currentHighBarLookahead = masterUCount - current_UCount
                    pastHighBarOffset = bi - (past_Idx - (past_UCount - 1) + (masterUCount - 1))
                    # bar_index >= offsets: indices into history must be valid
                    if bi >= currentHighBarLookahead and bi >= pastHighBarOffset:
                        # high[currentHighBarLookahead] and high[pastHighBarOffset]
                        idx_cur = i - currentHighBarLookahead
                        idx_past = i - pastHighBarOffset
                        if 0 <= idx_cur < n and 0 <= idx_past < n:
                            currentRangeHigh = h[idx_cur]
                            currentRangeLow = current_StartLow
                            pastRangeHigh = h[idx_past]
                            pastRangeLow = past_StartLow
                            if (pastRangeLow <= currentRangeHigh and
                                    pastRangeHigh >= currentRangeLow):
                                metaOverlapCount += 1
            if (metaOverlapCount + 1) >= P.oooc_minMetaOverlap:
                sOoOC[i] = True
        # prune meta window
        while meta_evIdx:
            if bi - meta_evIdx[-1] > P.oooc_metaWindowLen:
                meta_evIdx.pop()
                meta_evUCount.pop()
                meta_evStartLow.pop()
            else:
                break

    return sOoOC, rvol_price


# ----------------------------------------------------------------------------- #
# 9. RVOL Rolling Window                                                         #
# ----------------------------------------------------------------------------- #
def _rvol_rolling_window(o, h, lo, c, v, bar_index, P):
    n = len(c)
    spike = [abs(c[i] - o[i]) for i in range(n)]
    avgSpike_1 = shift(sma(spike, P.rw_avglength), 1)
    rvol_price = [_safediv(spike[i], nz(avgSpike_1[i], 1.0)) for i in range(n)]
    avgVol_1 = shift(sma(v, P.rw_avglength), 1)
    rvol_vol = [_safediv(v[i], nz(avgVol_1[i], 1.0)) for i in range(n)]
    rvol_diff = [rvol_price[i] - rvol_vol[i] for i in range(n)]
    rvolPos = [(d if d > 0 else None) for d in rvol_diff]
    smaPos_1 = shift(sma(rvolPos, 20), 1)   # source hardcodes 20 here
    baseBull = [c[i] > o[i] and rvol_diff[i] > 0 and nz(rvolPos[i]) > nz(smaPos_1[i]) for i in range(n)]
    isEvent = [baseBull[i] and (P.rw_th_low < rvol_price[i] < P.rw_th_high) for i in range(n)]

    sRVOL_Window = [False] * n
    windowStartBar = None
    eventCount = 0
    windowEventValues: list[float] = []
    for i in range(n):
        bi = bar_index[i]
        if eventCount > 0 and windowStartBar is not None and bi - windowStartBar >= P.rw_rollingWindowLen:
            eventCount = 0
            windowStartBar = None
            windowEventValues = []
        if isEvent[i]:
            if eventCount == 0:
                windowStartBar = bi
                eventCount = 1
                windowEventValues = [rvol_price[i]]
            else:
                eventCount += 1
                windowEventValues.append(rvol_price[i])
            if eventCount >= P.rw_minEventsInWindow:
                hasHighValue = any(val >= P.rw_minEventValue for val in windowEventValues)
                meetsSum = sum(windowEventValues) >= P.rw_minWindowSumValue
                if hasHighValue and meetsSum:
                    sRVOL_Window[i] = True
                    windowStartBar = bi
                    eventCount = 1
                    windowEventValues = [rvol_price[i]]
    return sRVOL_Window, rvol_price


# ----------------------------------------------------------------------------- #
# 11. Mango Swing Bottom                                                         #
# ----------------------------------------------------------------------------- #
def _pivot_high(src, left, right):
    """Pine ta.pivothigh: confirmed `right` bars later; value placed at the
    confirmation bar (so it's non-repainting) aligned to the current index."""
    n = len(src)
    out = [None] * n
    for i in range(n):
        p = i - right
        if p - left < 0 or p < 0 or i >= n:
            continue
        pivot = src[p]
        ok = True
        for k in range(1, left + 1):
            if not (src[p - k] < pivot):
                ok = False
                break
        if ok:
            for k in range(1, right + 1):
                if not (src[p + k] <= pivot):
                    ok = False
                    break
        if ok:
            out[i] = pivot
    return out


def _pivot_low(src, left, right):
    n = len(src)
    out = [None] * n
    for i in range(n):
        p = i - right
        if p - left < 0 or p < 0 or i >= n:
            continue
        pivot = src[p]
        ok = True
        for k in range(1, left + 1):
            if not (src[p - k] > pivot):
                ok = False
                break
        if ok:
            for k in range(1, right + 1):
                if not (src[p + k] >= pivot):
                    ok = False
                    break
        if ok:
            out[i] = pivot
    return out


def _mango_swing_bottom(h, lo, c, bar_index, P):
    n = len(c)
    swingHigh = _pivot_high(h, P.ms_leftBars, P.ms_rightBars)
    swingLow = _pivot_low(lo, P.ms_leftBars, P.ms_rightBars)

    sSwingBottom = [False] * n
    lastHighPrice = None
    lastHighBar = None
    prevHighPrice = None
    lastLowPrice = None
    lastLowBar = None
    prevLowPrice = None
    marketStructure = 0
    have_resistance = False
    resistanceLevel = None
    have_support = False
    supportLevel = None

    for i in range(n):
        bi = bar_index[i]
        # reset per-bar event flag (only swing_bottom is exported)
        swing_bottom_event = False

        # --- swing high branch ---
        if swingHigh[i] is not None:
            sh = swingHigh[i]
            # pair analysis (lower pair): needs lastLowBar < bar_index[ms_rightBars]
            if (lastLowPrice is not None and prevLowPrice is not None and
                    prevHighPrice is not None and lastLowBar is not None and
                    lastLowBar < bi - P.ms_rightBars):
                isLowerPair = sh < prevHighPrice and lastLowPrice < prevLowPrice
                if isLowerPair:
                    if marketStructure == 1:
                        have_resistance = True
                        resistanceLevel = prevHighPrice
                    marketStructure = -1
            prevHighPrice = lastHighPrice
            lastHighPrice = sh
            lastHighBar = bi - P.ms_rightBars

        # --- swing low branch ---
        if swingLow[i] is not None:
            slw = swingLow[i]
            if (lastHighPrice is not None and prevHighPrice is not None and
                    prevLowPrice is not None and lastHighBar is not None and
                    lastHighBar < bi - P.ms_rightBars):
                isHigherPair = lastHighPrice > prevHighPrice and slw > prevLowPrice
                if isHigherPair:
                    if marketStructure == -1:
                        swing_bottom_event = True   # <-- the exported signal
                        have_support = True
                        supportLevel = prevLowPrice
                    marketStructure = 1
            prevLowPrice = lastLowPrice
            lastLowPrice = slw
            lastLowBar = bi - P.ms_rightBars

        # --- breakout / breakdown (clears the active line; no fire exported) ---
        if have_resistance and resistanceLevel is not None and c[i] > resistanceLevel:
            have_resistance = False
            resistanceLevel = None
        if have_support and supportLevel is not None and c[i] < supportLevel:
            have_support = False
            supportLevel = None

        sSwingBottom[i] = swing_bottom_event
    return sSwingBottom


# ----------------------------------------------------------------------------- #
# PB&J Follow-up Buy (Beluga supertrend cross after PB&J dip)                    #
# ----------------------------------------------------------------------------- #
def _pbj_followup_buy(o, h, lo, c, v, P):
    n = len(c)
    ohlc4 = [(o[i] + h[i] + lo[i] + c[i]) / 4.0 for i in range(n)]
    base_ma = vwma_safe(ohlc4, v, P.pbj_vwma_len)
    atr_st = atr(h, lo, c, P.pbj_atr_len)
    longStop = [None] * n
    shortStop = [None] * n
    for i in range(n):
        if base_ma[i] is not None and atr_st[i] is not None:
            longStop[i] = base_ma[i] - P.pbj_atr_mult * atr_st[i]
            shortStop[i] = base_ma[i] + P.pbj_atr_mult * atr_st[i]

    cur_long = [0.0] * n
    cur_short = [0.0] * n
    direction = [1] * n
    prev_dir = 1
    for i in range(n):
        # current_long_ST := base_ma > nz(cur_long[1], longStop) ? max(longStop, nz(cur_long[1])) : longStop
        prev_cl = cur_long[i - 1] if i > 0 else None
        prev_cs = cur_short[i - 1] if i > 0 else None
        bm = base_ma[i]
        ls = longStop[i] if longStop[i] is not None else 0.0
        ss = shortStop[i] if shortStop[i] is not None else 0.0
        if bm is None:
            bm = 0.0
        if bm > nz(prev_cl, ls):
            cur_long[i] = max(ls, nz(prev_cl, 0.0))
        else:
            cur_long[i] = ls
        if bm < nz(prev_cs, ss):
            cur_short[i] = min(ss, nz(prev_cs, 0.0))
        else:
            cur_short[i] = ss
        # direction update (uses prev dir and prev stop)
        prev_short_1 = cur_short[i - 1] if i > 0 else ss
        prev_long_1 = cur_long[i - 1] if i > 0 else ls
        if prev_dir == -1 and ohlc4[i] > nz(prev_short_1, 0.0):
            direction[i] = 1
        elif prev_dir == 1 and ohlc4[i] < nz(prev_long_1, 0.0):
            direction[i] = -1
        else:
            direction[i] = prev_dir
        prev_dir = direction[i]

    ma_signal = [cur_long[i] if direction[i] == 1 else cur_short[i] for i in range(n)]
    # crossover(ohlc4, ma_signal)
    lander_buy = [False] * n
    for i in range(1, n):
        if (ohlc4[i] > ma_signal[i] and ohlc4[i - 1] <= ma_signal[i - 1]):
            lander_buy[i] = True

    # PB&J filter: EMA(20), atr(14), sma(volume,20)
    ma_value = ema(c, P.pbj_ma_len)
    atr_value = atr(h, lo, c, P.pbj_filter_atr_len)
    buy_avg_vol = sma(v, P.pbj_vol_len)
    buy_condition = [False] * n
    for i in range(n):
        if ma_value[i] is None or atr_value[i] is None or buy_avg_vol[i] is None:
            continue
        thr = 0.0 if c[i] == 0 else (atr_value[i] / c[i] * P.pbj_thresh_mult)
        price_cond = lo[i] < ma_value[i] * (1 - thr)
        # ta.lowest(low, 25) at this bar
        if i + 1 >= P.pbj_lowest_len:
            ll = min(lo[i - P.pbj_lowest_len + 1: i + 1])
            ll_cond = lo[i] == ll
        else:
            ll_cond = False
        vol_cond = v[i] > buy_avg_vol[i] * P.pbj_vol_frac
        buy_condition[i] = price_cond and ll_cond and vol_cond

    sPBJ = [False] * n
    waiting = False
    for i in range(n):
        if buy_condition[i]:
            waiting = True
        fire = lander_buy[i] and waiting
        sPBJ[i] = fire
        if fire:
            waiting = False
    return sPBJ


# ----------------------------------------------------------------------------- #
# 18..27. Custom A..J                                                            #
# ----------------------------------------------------------------------------- #
def _custom_signals(base_raw, bar_index, P):
    """Sequential (S) and windowed-density (D) composites. Customs may reference
    other customs; the source declares them in order A..J and forward-references
    are initialized False then overwritten — so a custom that includes a LATER
    custom sees its bar-by-bar value as it is computed in the same forward pass.
    We replicate Pine exactly: per bar, compute A,B,...,J in order, each reading
    the CURRENT bar's already-computed earlier customs and the PRIOR bar's later
    customs (var arrays carry [1])."""
    n = len(bar_index)
    cfgs = {
        "A": P.customA, "B": P.customB, "C": P.customC, "D": P.customD,
        "E": P.customE, "F": P.customF, "G": P.customG, "H": P.customH,
        "I": P.customI, "J": P.customJ,
    }
    order = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

    out = {k: [False] * n for k in order}
    # sequential accumulators
    win_start = {k: None for k in order}
    ev_count = {k: 0 for k in order}

    def base_count(cfg: CustomCfg, i):
        """count of included base+custom signals firing on bar i."""
        cnt = 0.0
        for key in cfg.use:
            if key in base_raw:
                if base_raw[key][i]:
                    cnt += 1.0
            elif key.startswith("Custom"):
                ck = key[-1]
                if out[ck][i]:
                    cnt += 1.0
        return cnt

    for i in range(n):
        bi = bar_index[i]
        for k in order:
            cfg = cfgs[k]
            if cfg.mode == "S":
                # sequential accumulator (A,B,C,D semantics)
                if ev_count[k] > 0 and win_start[k] is not None and bi - win_start[k] >= cfg.window:
                    ev_count[k] = 0
                    win_start[k] = None
                bc = base_count(cfg, i)
                fired = False
                if bc > 0 and cfg.enable:
                    if ev_count[k] == 0:
                        win_start[k] = bi
                        ev_count[k] = int(bc)
                    else:
                        ev_count[k] += int(bc)
                    if ev_count[k] >= cfg.required:
                        fired = True
                        win_start[k] = bi
                        ev_count[k] = int(bc)
                out[k][i] = fired
            else:
                # windowed density (E..J): rolling sum over `window` of per-bar counts
                if cfg.enable:
                    s = 0.0
                    for d in range(cfg.window):
                        j = i - d
                        if j >= 0:
                            s += base_count(cfg, j)
                    out[k][i] = s >= cfg.required
                else:
                    out[k][i] = False
    return out
