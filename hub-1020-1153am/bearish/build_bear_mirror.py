#!/usr/bin/env python3
"""
HUB_1020_1153am  ->  HUB_1020_1153am_BEAR   (Pine Editor bearish mirror)

Deterministic, reproducible vertical-reflection transformer.
Each op asserts its expected hit-count so a missed/over-broad flip fails LOUDLY
instead of silently corrupting an invariant (volume / ATR / RVOL / length / session).

Run:  python3 build_bear_mirror.py
Source of truth  : ../tick_friendly/HUB_1020_1153am_Hub102011a_v20260604_tick_friendly.pine
Output           : ./HUB_1020_1153am_BEAR_Hub1020-Bear_v20260613_bearish_mirror.pine
"""
import hashlib
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "tick_friendly" / "HUB_1020_1153am_Hub102011a_v20260604_tick_friendly.pine"
DST = HERE / "HUB_1020_1153am_BEAR_Hub1020-Bear_v20260613_bearish_mirror.pine"

text = SRC.read_text()
src_md5 = hashlib.md5(text.encode()).hexdigest()
log = []


def rep(old, new, n=None, lo=None):
    """Exact-substring replace. n=exact expected count, lo=minimum expected count."""
    c = text_holder[0].count(old)
    if n is not None and c != n:
        sys.exit(f"FAIL exact [{old[:60]!r}]: expected {n}, got {c}")
    if lo is not None and c < lo:
        sys.exit(f"FAIL min   [{old[:60]!r}]: expected >= {lo}, got {c}")
    if n is None and lo is None and c == 0:
        sys.exit(f"FAIL zero  [{old[:60]!r}]: 0 occurrences")
    text_holder[0] = text_holder[0].replace(old, new)
    log.append((old[:48], new[:48], c))


def rep_re(pat, repl, n):
    s2, c = re.subn(pat, repl, text_holder[0])
    if c != n:
        sys.exit(f"FAIL regex [{pat[:60]!r}]: expected {n}, got {c}")
    text_holder[0] = s2
    log.append((f"re:{pat[:42]}", repl[:42], c))


def swap(a, b):
    P = "\x00SWAP\x00"
    t = text_holder[0]
    t = t.replace(a, P).replace(b, a).replace(P, b)
    text_holder[0] = t
    log.append((f"swap {a[:20]}", b[:20], -1))


text_holder = [text]

# ============================================================================
# PHASE 0 — header + indicator identity
# ============================================================================
rep("//@version=5\n",
    "//@version=5\n"
    "// Pine is a Pine Editor bearish mirror\n"
    "// BEARISH STRUCTURAL MIRROR of HUB_1020_1153am (Signal Hub). Source md5: " + src_md5 + "\n"
    "// Vertical reflection: bull accumulation/launch -> bear distribution/breakdown.\n"
    "// FLIPPED (directional): close>open->close<open, body_up->body_down, RE close-near-high->near-low,\n"
    "//   up_trend->down_trend, (close-close[1])->(close[1]-close), seq anchor low->high, swing bottom->top,\n"
    "//   PB&J buy->sell (crossover->crossunder, lowest->highest, 1- -> 1+).\n"
    "// INVARIANT (NOT flipped): volume, ta.atr/tr, RVOL spike=abs(close-open), length/period,\n"
    "//   timeframe/session/time(), RE10023 tick guard str.endswith(timeframe.period,\"T\").\n"
    "// One intentional non-pure-reflection: surviving Swing label.new -> plotshape detection plot\n"
    "//   (per Anish standing rule: NO label.new graphic objects; use detection plots).\n",
    n=1)

rep('indicator("HUB_1020_1153am", shorttitle="Hub102011a"',
    'indicator("HUB_1020_1153am_BEAR", shorttitle="Hub1020-Bear"', n=1)

# ============================================================================
# PHASE 1 — MB/RE/TA engine + RVOL3 base gate (the directional core)
# Order: rename tokens first, then flip the def RHS operators.
# ============================================================================
rep("_body_up", "_body_down", n=27)          # 8 defs + 19 usages
rep("_up_trend", "_down_trend", n=10)         # 5 defs + 5 usages
rep("_MB_bull", "_MB_bear", n=15)             # exact engine suffixes only (NOT _bullish_rvol)
rep("_RE_bull", "_RE_bear", n=13)
rep("_TA_bull", "_TA_bear", n=11)
rep("baseBull", "baseBear", n=12)             # rvol3 base-direction gate token

# flip the 8 candle-direction defs:  X_body_down = X_body > 0  ->  < 0
rep_re(r"_body_down = ([a-z0-9_]+_body) > 0", r"_body_down = \1 < 0", n=8)
# flip the 5 trend-direction defs:    X_TrendMA > X_TrendMA[1]  ->  <
rep("_TrendMA > ", "_TrendMA < ", n=5)
# flip RE "close near the HIGH" -> "close near the LOW"
rep("(high - close) <", "(close - low) <", n=6)
# flip TA "price rose" -> "price fell"
rep("(close - close[1]) >", "(close[1] - close) >", n=5)
# flip the 5 RVOL3 base-direction gates: close>open -> close<open  (down bar)
rep("close > open", "close < open", n=5)

# ============================================================================
# PHASE 2 — sequence/zone anchors: bull anchors to seq-start LOW (up-move origin);
#           bear anchors to seq-start HIGH (down-move origin). Overlap geometry is
#           symmetric and stays; only the anchor source + hi/lo slot feeds flip.
# ============================================================================
# --- OW "ote" sequence ---
rep("ow_seqStartLow_ote", "ow_seqStartHigh_ote", n=4)
rep("ow_seqStartHigh_ote := low", "ow_seqStartHigh_ote := high", n=1)
rep("ow_currentEventHigh = high, ow_currentEventLow = ow_seqStartHigh_ote",
    "ow_currentEventLow = low, ow_currentEventHigh = ow_seqStartHigh_ote", n=1)

# --- OW "super" sequence ---
rep("ow_seqStartLow_super", "ow_seqStartHigh_super", n=5)
rep("ow_seqStartHigh_super := low", "ow_seqStartHigh_super := high", n=1)
rep("ow_eventRange = high - ow_seqStartHigh_super",
    "ow_eventRange = ow_seqStartHigh_super - low", n=1)
rep("array.unshift(ow_evHi, high + ow_padding), array.unshift(ow_evLo, ow_seqStartHigh_super - ow_padding)",
    "array.unshift(ow_evHi, ow_seqStartHigh_super + ow_padding), array.unshift(ow_evLo, low - ow_padding)", n=1)

# --- OoOC sequence + meta-cluster lookahead ---
rep("oooc_meta_evStartLow", "oooc_meta_evStartHigh", n=4)
rep("oooc_seqStartLow", "oooc_seqStartHigh", n=6)
rep("oooc_seqStartHigh := low", "oooc_seqStartHigh := high", n=1)
rep("currentEventHigh = high, currentEventLow = oooc_seqStartHigh",
    "currentEventLow = low, currentEventHigh = oooc_seqStartHigh", n=1)
rep("current_StartLow", "current_StartHigh", n=2)
rep("past_StartLow", "past_StartHigh", n=2)
rep("currentHighBarLookahead", "currentLowBarLookahead", n=3)
rep("pastHighBarOffset", "pastLowBarOffset", n=3)
# the meta zone: bull tracks HIGH reached over lookahead + anchor low; bear tracks LOW + anchor high
rep("currentRangeHigh = high[currentLowBarLookahead]", "currentRangeLow = low[currentLowBarLookahead]", n=1)
rep("currentRangeLow = current_StartHigh", "currentRangeHigh = current_StartHigh", n=1)
rep("pastRangeHigh = high[pastLowBarOffset]", "pastRangeLow = low[pastLowBarOffset]", n=1)
rep("pastRangeLow = past_StartHigh", "pastRangeHigh = past_StartHigh", n=1)
# overlap test 'pastRangeLow <= currentRangeHigh and pastRangeHigh >= currentRangeLow' is symmetric -> unchanged

# ============================================================================
# PHASE 3 — Mango Swings: export Swing TOP instead of Swing BOTTOM.
#           Replace surviving label.new with a detection plotshape (NO-label rule).
# ============================================================================
# 3a. swap the graphic label block -> detection plot (use ORIGINAL bull strings).
#     BEAR_PLOT marker excludes this final-form line from the scoped Phase-6 visual pass.
rep(
    'if sSwingBottom_raw and show_swing_bottom_plots and barstate.isconfirmed\n'
    '    // FIX: Ensured correct indentation (4 spaces) and use of stored coordinates.\n'
    '    label.new(ms_swingBottomEventBar, ms_swingBottomEventPrice, "Swing Bottom", color=color.new(color.lime, 0), textcolor=color.black, style=label.style_label_up, yloc=yloc.belowbar, size=size.normal)',
    'plotshape(sSwingTop_raw and show_swing_top_plots and barstate.isconfirmed, "Swing Top (Mango)", location=location.abovebar, style=shape.labeldown, color=color.new(color.red, 0), textcolor=color.white, size=size.normal, text="ST")  //BEAR_FINAL',
    n=1)
# 3b. export RHS: swing bottom event -> swing top event (Mango engine already computes both)
rep("bool sSwingBottom_raw = ms_swing_bottom_event",
    "bool sSwingTop_raw = ms_swing_top_event", n=1)
# 3c. global renames of remaining swing-export references
rep("sSwingBottom_raw", "sSwingTop_raw", lo=12)            # composites + alerts + derived
rep("show_swing_bottom_plots", "show_swing_top_plots", lo=1)
rep("fire_swing_bottom", "fire_swing_top", lo=1)
rep("Swing Bottom", "Swing Top", lo=1)                    # display labels
rep("SWING BOTTOM", "SWING TOP", lo=1)                    # comment header

# ============================================================================
# PHASE 4 — PB&J Follow-up: bull bottom-fishing BUY -> bear top-fishing SELL.
#           Supertrend dual-stop engine is symmetric -> kept; only signal+filter flip.
# ============================================================================
rep("pbj_lander_buy_signal", "pbj_lander_sell_signal", lo=2)
rep("pbj_buy_avg_volume", "pbj_sell_avg_volume", lo=2)
rep("pbj_buy_threshold_perc", "pbj_sell_threshold_perc", lo=2)
rep("pbj_price_cond_buy", "pbj_price_cond_sell", lo=2)
rep("pbj_ll_cond_buy", "pbj_hh_cond_sell", lo=2)
rep("pbj_vol_cond_buy", "pbj_vol_cond_sell", lo=2)
rep("pbj_buy_condition", "pbj_sell_condition", lo=2)
rep("pbj_waiting_for_lander_buy", "pbj_waiting_for_lander_sell", lo=3)
rep("sPBJFollowupBuy_raw", "sPBJFollowupSell_raw", lo=12)
rep("fire_pbj_buy", "fire_pbj_sell", lo=2)
rep("show_pbj_buy_plots", "show_pbj_sell_plots", lo=2)
rep("enable_pbj_buy_alerts", "enable_pbj_sell_alerts", lo=2)
rep("_pbj_buy", "_pbj_sell", lo=10)                       # composite input vars use_X_pbj_buy
# logic flips (after renames):
rep("bool pbj_lander_sell_signal = ta.crossover(ohlc4, pbj_ma_signal_line_val)",
    "bool pbj_lander_sell_signal = ta.crossunder(ohlc4, pbj_ma_signal_line_val)", n=1)
rep("bool pbj_price_cond_sell = low < pbj_ma_value * (1 - pbj_sell_threshold_perc)",
    "bool pbj_price_cond_sell = high > pbj_ma_value * (1 + pbj_sell_threshold_perc)", n=1)
rep("bool pbj_hh_cond_sell = low == ta.lowest(low, 25)",
    "bool pbj_hh_cond_sell = high == ta.highest(high, 25)", n=1)
rep("PB&J Follow-up Buy", "PB&J Follow-up Sell", lo=1)

# ============================================================================
# PHASE 5 — display / semantic renames
# ============================================================================
rep("U>Th", "D>Th", lo=1)        # plot/alert/comment display only (var token UgtTh untouched)
rep("Bullish", "Bearish", lo=1)
rep("bullish", "bearish", lo=1)  # incl. composite input var token _l7_bullish_rvol (consistent)

# ============================================================================
# PHASE 6 — visuals SCOPED to detection-plot lines only (plotshape/plotchar).
# The Mango debug engine (label.new/line.new, default-off, symmetric) is left
# byte-identical to the bull. Detection plots: force up-shapes -> down-shapes and
# bull-green fill colors -> red/maroon. Locations are positional (top/bottom pane,
# above/below candle) NOT bull/bear polarity in this hub, so they are preserved.
# The pre-built swing-top plot (//BEAR_FINAL) is already bearish and is skipped.
# ============================================================================
_SHAPE = [("style=shape.triangleup", "style=shape.triangledown"),
          ("style=shape.arrowup", "style=shape.arrowdown"),
          ("style=shape.labelup", "style=shape.labeldown")]
_FILL = [("color=color.new(color.white", "color=color.new(color.red"),
         ("color=color.new(color.lime", "color=color.new(color.red"),
         ("color=color.new(color.green", "color=color.new(color.maroon"),
         ("color=color.new(color.teal", "color=color.new(color.maroon"),
         ("color=color.new(color.aqua", "color=color.new(color.red")]
_lines = text_holder[0].split("\n")
_n_shape = _n_fill = _n_plot = 0
for _i, _ln in enumerate(_lines):
    _s = _ln.lstrip()
    if not (_s.startswith("plotshape(") or _s.startswith("plotchar(")):
        continue
    if "//BEAR_FINAL" in _ln:        # already in final bearish form
        continue
    _n_plot += 1
    for a, b in _SHAPE:
        if a in _ln:
            _ln = _ln.replace(a, b); _n_shape += 1
    for a, b in _FILL:
        if a in _ln:
            _ln = _ln.replace(a, b); _n_fill += 1
    _lines[_i] = _ln
text_holder[0] = "\n".join(_lines)
log.append((f"scoped {_n_plot} plot lines: {_n_shape} shape-flips", f"{_n_fill} color-flips", _n_plot))

# ============================================================================
# WRITE + REPORT
# ============================================================================
out = text_holder[0]
DST.write_text(out)
dst_md5 = hashlib.md5(out.encode()).hexdigest()

print("OPS APPLIED:")
for o, nw, c in log:
    print(f"  {c:>4}  {o:<50} -> {nw}")
print(f"\nsrc lines={len(text.splitlines())}  dst lines={len(out.splitlines())}")
print(f"src md5={src_md5}")
print(f"dst md5={dst_md5}")
print(f"wrote: {DST}")
