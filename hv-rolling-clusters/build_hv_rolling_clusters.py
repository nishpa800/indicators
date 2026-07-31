#!/usr/bin/env python3
"""
HV ROLLING CLUSTERS NRA -- rolling-window high-volume CLUSTER detectors, one per
rung of a clean "N-bar-high AND ABOVE" ladder, extended to 4000, plus Nagasaki.

WHY THIS REBUILD
  The previous rolling-clusters build mixed three kinds of window classes:
    - "or greater"  (500+, 1000+)      -- a ladder rung
    - "only"        (500-only, 250-only, 150-only, 50-only)
    - "A or B band" (250-or-500, 150-or-250)
  The "only" and "band" classes are arbitrary -- why single out "150 to 250"
  instead of just "150 and above"? So they are ELIMINATED. Every window is now
  a pure ladder rung: "at least COUNT bars in the last BARS were an N-bar-high
  OR RARER." Because the tier flags are NESTED (is1000Bar => is500Bar => ...),
  the raw is{N}Bar flag already MEANS "N and above" -- no subtraction needed.

  The ladder is also extended past 1000 to match the expanded HV detection set:
    50, 150, 250, 500, 1000, 1500, 2000, 2500, 3000, 4000  (10 rungs)
  plus Nagasaki (all-time-high volume == HEV), the rarest "and above". 11 windows.

  Hot Spot (calendar) is REMOVED entirely (it was computed-but-never-plotted dead
  weight in the prior build, and is not wanted).

REPETITIVE PER-WINDOW BLOCKS ARE GENERATED (one source of truth, no drift). The
non-repainting architecture and the sliding-window/leading-edge mechanics are
kept VERBATIM from the prior build.

  python3 build_hv_rolling_clusters.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "versions" / "HV_ROLLING_CLUSTERS_ladder_50-4000_2026-07-04.pine"
OUT.parent.mkdir(parents=True, exist_ok=True)

# The ladder (ascending). Each rung's window counts "is{N}Bar and above" events.
LADDER = [50, 150, 250, 500, 1000, 1500, 2000, 2500, 3000, 4000]
# Per-rung default (COUNT events, within BARS window). Sensible starting points:
# rarer rungs -> smaller count / longer window; common rungs -> higher count /
# shorter window. All are user inputs, so these are just defaults.
DEFAULTS = {50: (4, 30), 150: (3, 50), 250: (3, 75), 500: (2, 100), 1000: (2, 150),
            1500: (2, 150), 2000: (2, 175), 2500: (2, 200), 3000: (2, 200), 4000: (2, 250)}
NAG_DEFAULT = (2, 250)


def color_for(tier):
    """Cool (common, small N) -> hot (rare, large N) across the ladder."""
    i = LADDER.index(tier)
    r = i / (len(LADDER) - 1)
    R = int(round(40 + 215 * r)); G = 45; B = int(round(255 - 215 * r))
    return f"color.rgb({R}, {G}, {B}, 0)"


def size_for(tier):
    if tier <= 250:
        return "size.tiny"
    if tier <= 1000:
        return "size.small"
    if tier <= 2500:
        return "size.normal"
    return "size.large"


# Windows in DISPLAY / numbering order: rarest first (W1 = Nagasaki), like the
# prior build. Each entry: (key, event_var, event_expr, tier_or_None, short, desc,
# cnt, win, shape, color, size).
WINDOWS = []
WINDOWS.append(("nag", "evt_nag", "isHEV", None, "NAG",
                "Nagasaki / all-time-high volume", NAG_DEFAULT[0], NAG_DEFAULT[1],
                "shape.diamond", "color.new(color.purple, 0)", "size.normal"))
for tier in reversed(LADDER):                       # 4000, 3000, ... , 50
    cnt, win = DEFAULTS[tier]
    desc = f"{tier}-bar high and above" + (" (any HV tier)" if tier == 50 else "")
    WINDOWS.append((str(tier), f"evt_{tier}", f"is{tier}Bar", tier, str(tier),
                    desc, cnt, win, "shape.circle", color_for(tier), size_for(tier)))

TICK = "{{ticker}}"   # emitted literally into Pine alertcondition messages

HEADER = f'''//@version=5
// ============================================================================
// HV ROLLING CLUSTERS NRA  --  rolling-window high-volume CLUSTER detectors
// ============================================================================
// WHAT THIS IS
//   Rolling-window CLUSTER detectors over a clean "N-bar-high AND ABOVE" ladder.
//   The individual volume tiers (50/150/250/500/1000/1500/2000/2500/3000/4000-bar
//   highs, and the all-time high = Nagasaki/HEV) are STILL computed -- they are
//   the raw material the windows count -- but they no longer paint per-tier
//   markers or fire per-tier alerts. ONLY the {len(WINDOWS)} cluster windows plot and alert.
//
//   Each window answers one question:
//     "Did at least <COUNT> events of <CLASS> occur within the last <BARS> bars?"
//   COUNT (events) and BARS (window length) are user inputs on EVERY window.
//
// THE LADDER  (every window is a pure "N and above" rung -- no "only"/"band")
//   W1  Nagasaki    all-time-high volume (== HEV; the rarest "and above")
//   W2  4000+       a 4000-bar volume high or rarer
//   W3  3000+       a 3000-bar high or rarer
//   W4  2500+       a 2500-bar high or rarer
//   W5  2000+       a 2000-bar high or rarer
//   W6  1500+       a 1500-bar high or rarer
//   W7  1000+       a 1000-bar high or rarer
//   W8  500+        a 500-bar high or rarer
//   W9  250+        a 250-bar high or rarer
//   W10 150+        a 150-bar high or rarer
//   W11 50+         a 50-bar high or rarer (ANY high-volume tier)
//
//   NESTING makes "N and above" trivial: a 1000-bar high is automatically a
//   500/250/150/50-bar high, so the raw is{{N}}Bar flag ALREADY means "N or rarer".
//   No "only"/"band" subtraction anywhere -- that arbitrary logic is gone.
//
// NON-REPAINTING (NRA) + CONSTITUTIONAL ROLLING WINDOWS
//   * Every tier compares the PRIOR CLOSED bar: volume[1] == ta.highest(volume,N)[1].
//   * Each window is a TRUE SLIDING trailing-N count via f_sum_true(), with the
//     base event gated on barstate.isconfirmed (closed bars only). No anchored
//     "wait N bars then reset" window anywhere.
//   * Fire = LEADING EDGE of (count >= COUNT):  cond and not cond[1]  -- fires once
//     when the cluster completes, then re-arms automatically.
//   * Plot and alert for each window share ONE boolean -> 1:1, can never desync.
//   * Markers plot with offset=-1 onto the closed bar that completed the cluster.
//
// ALERTS
//   * One alertcondition per window ({len(WINDOWS)}), plus one "ANY" alertcondition, plus one
//     alert() function call (the "any-call") whose payload names which windows fired.
//
// (Hot Spot calendar signals were REMOVED in this build.)
// ASCII-ONLY source (TradingView's Pine lexer rejects non-ASCII punctuation).
// ============================================================================

indicator("HV ROLLING CLUSTERS (Nagasaki + 50-4000 ladder) NRA", shorttitle="HV ROLL", overlay=true, max_bars_back=5000)

// --- Canonical suite helper: count TRUE over a trailing SLIDING window of len bars.
f_sum_true(cond, len) =>
    float s = 0.0
    int L = math.max(1, len)
    for i = 0 to L - 1
        s += (cond[i] ? 1.0 : 0.0)
    s
'''

# ----- INPUTS -----
inputs = ["", "// ============================================================================",
          "// === INPUTS -- per window: Enable + COUNT (events) + within BARS (window) ===",
          "// ============================================================================"]
for k, w in enumerate(WINDOWS, 1):
    key, evar, eexpr, tier, short, desc, cnt, win, shp, col, sz = w
    grp = f"W{k}: {desc}"
    inputs.append(f'grp{k}  = "{grp}"')
    inputs.append(f'w{k}_on  = input.bool(true, "Enable W{k} {short}", group=grp{k})')
    inputs.append(f'w{k}_cnt = input.int({cnt}, "Count (events)", minval=1, inline="w{k}", group=grp{k})')
    inputs.append(f'w{k}_win = input.int({win}, "within Bars", minval=1, maxval=5000, inline="w{k}", group=grp{k})')
    inputs.append("")

# ----- TIER CALCULATIONS (kept for counting only) -----
calcs = ["// ============================================================================",
         "// === INDIVIDUAL TIER CALCULATIONS  (kept for COUNTING only -- no own plot/alert)",
         "// ============================================================================",
         "// All comparisons use [1] (prior CLOSED bar): volume[1] == ta.highest(volume,N)[1]",
         "// can never change once the bar closes -> non-repainting by construction."]
for tier in LADDER:
    calcs.append(f"bool is{tier}Bar = volume[1] == ta.highest(volume, {tier})[1]")
calcs += ["",
          "// All-time-high volume (HEV) -- running max over CONFIRMED bars only.",
          "// HEV == Nagasaki (the Heavy Weapons all-time-high-volume signal).",
          "var float maxVolEver = 0.0",
          "bool isHEV = false",
          "if volume[1] > maxVolEver",
          "    maxVolEver := volume[1]",
          "    isHEV := true",
          "bool isNagasaki = isHEV"]

# ----- CLASS EVENTS -----
events = ["", "// ============================================================================",
          "// === CLASS EVENTS (confirmed bars only) -- the raw material each window counts",
          "// ============================================================================",
          "// Every class is a pure ladder rung: the raw is{N}Bar flag == \"N and above\".",
          "bool conf = barstate.isconfirmed"]
for w in WINDOWS:
    key, evar, eexpr, tier, short, desc, cnt, win, shp, col, sz = w
    events.append(f"bool {evar} = conf and {eexpr}")

# ----- ROLLING COUNTS / CONDITIONS / FIRES -----
roll = ["", "// ============================================================================",
        "// === ROLLING-WINDOW CLUSTER DETECTIONS (sliding trailing-N, leading-edge fire)",
        "// ============================================================================",
        "// nN = events of the class in trailing winN bars.  condN = nN >= countN.",
        "// fire_WN = leading edge of condN (fires once when the cluster completes)."]
for k, w in enumerate(WINDOWS, 1):
    roll.append(f"float n{k} = f_sum_true({w[1]}, w{k}_win)")
roll.append("")
for k in range(1, len(WINDOWS) + 1):
    roll.append(f"bool c{k} = n{k} >= w{k}_cnt")
roll.append("")
for k in range(1, len(WINDOWS) + 1):
    roll.append(f"bool fire_W{k} = w{k}_on and c{k} and not c{k}[1]")

# ----- PLOTS -----
plots = ["", "// ============================================================================",
         "// === PLOTS -- the cluster detection plots (offset=-1 -> lands on the closed bar",
         "// === that completed the cluster). No individual-tier shapes anymore.",
         "// ============================================================================"]
for k, w in enumerate(WINDOWS, 1):
    key, evar, eexpr, tier, short, desc, cnt, win, shp, col, sz = w
    plots.append(f'plotshape(fire_W{k}, "W{k} {short} cluster", {shp}, location.top, {col}, size={sz}, text="{short}", textcolor=color.white, offset=-1)')
plots.append("")
plots.append("// Numeric counts (data-window only -- helps tune COUNT/BARS; no chart clutter).")
for k, w in enumerate(WINDOWS, 1):
    plots.append(f'plot(n{k}, "W{k} count ({w[4]})", display=display.data_window)')

# ----- ALERTS -----
alerts = ["", "// ============================================================================",
          "// === ALERTS -- per-window (1:1 with plots), plus ANY alertcondition + any-call()",
          "// ============================================================================"]
for k, w in enumerate(WINDOWS, 1):
    short = w[4]; desc = w[5]
    alerts.append(f'alertcondition(fire_W{k}, "W{k} {short} cluster", "W{k}: {desc} cluster on {TICK}")')
alerts.append("")
any_expr = " or ".join(f"fire_W{k}" for k in range(1, len(WINDOWS) + 1))
alerts.append(f"bool any_fire = {any_expr}")
alerts.append(f'alertcondition(any_fire, "ANY HV rolling cluster", "ANY HV rolling-window cluster fired on {TICK}")')

# ----- ANY-CALL alert() -----
anycall = ["", "// any-call alert(): set ONE TradingView alert to \"Any alert() function call\"",
           "// and it catches every window. Payload names which windows fired this bar.",
           "if any_fire and conf",
           '    string m = ""']
for k, w in enumerate(WINDOWS, 1):
    anycall.append(f'    m := fire_W{k} ? m + "{w[4]} " : m')
anycall.append('    alert("HV_ROLL|TICKER:" + syminfo.ticker + "|TF:" + timeframe.period + "|FIRED:" + m, alert.freq_once_per_bar_close)')

# ----- EXPORTS -----
tier_list = ", ".join(f"is{t}Bar" for t in LADDER)
exports = ["", "// ============================================================================",
           "// === EXPORTS (for combination / fire-matrix consumers)",
           "// ============================================================================",
           f"// Individual tiers (bool): {tier_list},",
           "//                          isHEV (== isNagasaki)   (calc/export only)",
           f"// Window fires (bool):     fire_W1 .. fire_W{len(WINDOWS)}",
           f"// Window counts (float):   n1 .. n{len(WINDOWS)}",
           f"// Aggregate:               activeWindows = how many windows fired this bar (0..{len(WINDOWS)})"]
active_expr = "+".join(f"(fire_W{k}?1:0)" for k in range(1, len(WINDOWS) + 1))
exports.append(f"int activeWindows = {active_expr}")
exports.append(f'plot(activeWindows, "activeWindows (0..{len(WINDOWS)})", color=color.white, display=display.data_window)')

doc = "\n".join([HEADER] + inputs + calcs + events + roll + plots + alerts + anycall + exports) + "\n"

# ASCII-ONLY guard (Pine lexer rejects non-ASCII punctuation).
doc = (doc.replace("—", "-").replace("–", "-")
          .replace("‘", "'").replace("’", "'")
          .replace("“", '"').replace("”", '"'))
bad = [(i + 1, repr(ch)) for i, ln in enumerate(doc.splitlines())
       for ch in ln if ord(ch) > 0x7F]
if bad:
    raise SystemExit(f"NON-ASCII REMAINS (Pine will reject): {bad[:10]}")

OUT.write_text(doc)
print(f"wrote {OUT}")
print(f"windows={len(WINDOWS)}  ladder={LADDER}  lines={len(doc.splitlines())}")
