#!/usr/bin/env python3
"""
HV NRA generator - v3 "magnitude ladder".

WHY v3 EXISTS (the design flaw v2 had)
--------------------------------------
v2's only output was the DEEPEST nested lookback tier a bar reached
(50,100,...,1000). That label answers ONE question:
    "how long since volume was this high?"  (a RECENCY / rarity measure)
It says NOTHING about MAGNITUDE - how big the bar actually was. Two bars both
stamped "1000" can have wildly different absolute volume, and a genuinely huge
bar can wear a small "400" sticker purely because one bigger bar happens to sit
401-450 bars back (so it is a 400-high but not a 450-high). So the on-chart
label was sorting signals on the wrong axis.

v3 keeps the recency ladder but bolts on a MAGNITUDE-IN-CONTEXT layer:
  * pop          = volume[1] / sma(volume, popBaseLen)  -> "X times the recent
                   average". A single short baseline so it is comparable across
                   tiers and immune to drought-inflation (a 1000-high in a quiet
                   stretch has small volume AND small recent avg -> low pop).
                   NOTE: this is a plain rolling ratio, NOT the suite's sacred
                   session-anchored tv_ta.relativeVolume() - different metric,
                   deliberately named 'pop' to avoid any confusion.
  * per-tier ring buffers (the user's "keep the last K N-highs") -> memory of
                   prior highs of each window. Depth grows as the window shrinks
                   (top=10, 4000=15, 3000=20, 2000=25, 1000=30, smaller=more).
  * relVsPriorHighs = volume[1] / median(prior K N-highs) -> "this 1k vs prior
                   1ks". Answers whether THIS high stands out among its peers.
  * record flags  = "highest N-high in memory" (recRecent) and per-tier all-time
                   max (recEver). (recEver for the very top tier converges to
                   HEV by definition; recRecent is the genuinely useful one.)
  * rank          = position of this high among its ring buffer (1 = biggest).
  * ALL of it stamped into a dynamic alert() message (alertcondition() messages
                   are const-only, so the rich metadata rides the alert()
                   function; legacy per-tier alertcondition()s are kept with
                   {{plot("...")}} placeholders so they carry the values too).

LADDER (v3): fine 50-step 50..1000 (20 tiers) + coarse 2000/3000/4000/4999
  (4 tiers). Top tier is 4999 (not 5000) on purpose: ta.highest(volume,N)[1]
  references N+1 bars back, and Pine's max_bars_back ceiling is 5000, so 4999
  keeps the deepest reference at exactly 5000. Tiers stay NESTED (a 4999-high is
  a high at every shorter window too) so exactly ONE tier marker prints per bar:
  the deepest reached. Markers are COLORED BY pop (magnitude) by default so an
  impressive high glows hot regardless of which window labeled it.

The whole file is GENERATED so the 24 repetitive tier blocks stay DRY.
Non-repainting architecture is preserved verbatim: volume[1] + ...[1] +
offset=-1, and plot==alert via shared plot_* booleans.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "versions" / "HV_NRA_magnitude_ladder_v3_2026-06-29.pine"
OUT.parent.mkdir(parents=True, exist_ok=True)

FINE = list(range(50, 1001, 50))          # [50,100,...,1000] -> 20 tiers
COARSE = [2000, 3000, 4000, 4999]         # coarse top -> 4 tiers
TIERS = FINE + COARSE                      # 24 tiers, ascending
assert TIERS == sorted(TIERS) and len(TIERS) == 24 and TIERS[-1] == 4999


def mem_default(n):
    """Ring-buffer depth default. Bigger window -> rarer event -> keep fewer;
    smaller window -> fires often -> keep more (user's 10/15/20/25/30 scheme)."""
    explicit = {4999: 10, 4000: 15, 3000: 20, 2000: 25, 1000: 30}
    if n in explicit:
        return explicit[n]
    return 30 + (1000 - n) // 50           # 950->31 ... 50->49


def tier_ramp(i):
    """Fallback blue->red ramp (used only when 'color by magnitude' is OFF)."""
    r = i / (len(TIERS) - 1)
    R = int(round(40 + 215 * r)); G = 45; B = int(round(255 - 215 * r))
    return f"color.rgb({R}, {G}, {B}, 0)"


def dot_size(n):
    return "size.normal" if n >= 600 else ("size.small" if n >= 250 else "size.tiny")


# ===================================================================
HEADER = '''//@version=5
indicator("HV Magnitude Ladder (50..4999 / HEV / HS) NRA", overlay=true, max_bars_back=5000, max_labels_count=500)

// ============================================
// === NON-REPAINTING ARCHITECTURE ===
// ============================================
// All volume comparisons use [1] (prior CLOSED bar): volume[1] == ta.highest(volume,N)[1]
// can never change once the bar closes. Markers land on the [1] bar via offset=-1.
// Plot and alert conditions share the SAME plot_* booleans -> zero plot/alert drift.
//
// ============================================
// === v3: RECENCY (which tier) vs MAGNITUDE (how big) ===
// ============================================
// The tier label (50..4999) answers "how long since volume was this high?" - a
// RECENCY measure. It does NOT say how big the bar was: a quiet-stretch dud can
// be a "1000-high", and a monster can wear a "400" sticker if a bigger bar sits
// 401-450 bars back. v3 adds a MAGNITUDE layer so every high carries how big it
// actually was, in context:
//   pop              = volume[1] / sma(volume, popBaseLen)   (X * recent average)
//   relVsPriorHighs  = volume[1] / median(last K N-bar highs) (this 1k vs prior 1ks)
//   recRecent/recEver= is this the biggest N-high in memory / ever
//   rank             = place among the ring buffer (1 = biggest)
// Markers are colored by pop by default (impressive highs glow hot). Full metadata
// is emitted on the dynamic alert() message AND via {{plot(...)}} placeholders on
// the legacy alertcondition()s.
//
// pop is a PLAIN rolling ratio - NOT the suite's session-anchored
// tv_ta.relativeVolume(). Different metric, deliberately named 'pop'.
//
// LADDER: fine 50-step 50..1000 + coarse 2000/3000/4000/4999. Top=4999 keeps the
// deepest ...[1] reference at exactly the 5000 max_bars_back ceiling. Tiers are
// NESTED -> exactly ONE tier marker per bar (the deepest reached).
// ============================================
'''

# ----- INPUTS: tier toggles -----
inputs = ["", "// ============================================",
          "// === INPUTS: TIER TOGGLES ===", "// ============================================"]
for n in TIERS:
    inputs.append(f'use{n:<5} = input.bool(true, "Show {n}-Bar High Vol", group="Tiers")')
inputs.append('useHEV   = input.bool(true, "Show All-Time High Vol (HEV)", group="Tiers")')
inputs.append('useHS    = input.bool(true, "Show Hot Spot Signals", group="Tiers")')

# ----- INPUTS: magnitude -----
inputs += ["", "// === INPUTS: MAGNITUDE LAYER ===",
           'popBaseLen = input.int(50, "pop baseline length (X * avg of last N)", minval=2, group="Magnitude")',
           'colByPop   = input.bool(true, "Color markers by magnitude (pop)", group="Magnitude")',
           'popExtreme = input.float(8.0, "Extreme-pop star threshold (X avg)", minval=1.0, group="Magnitude")',
           'memMult    = input.float(1.0, "Memory depth multiplier", minval=0.1, group="Magnitude")']

# ----- INPUTS: per-tier memory depth -----
inputs += ["", "// === INPUTS: MEMORY (ring-buffer depth per tier) ===",
           "// Bigger window = rarer = keep fewer; smaller window = frequent = keep more."]
for n in TIERS:
    inputs.append(f'mem{n:<5} = input.int({mem_default(n)}, "{n}-high memory depth", minval=1, group="Memory")')

# ----- VOLUME HIGH CALCS + pop baseline + HEV -----
calcs = ["", "// ============================================",
         "// === VOLUME HIGH CALCULATIONS (CONFIRMED BARS ONLY) ===",
         "// ============================================"]
for n in TIERS:
    calcs.append(f"bool is{n}Bar = volume[1] == ta.highest(volume, {n})[1]")
calcs += ["",
          "// pop = magnitude vs recent average (single short baseline, comparable across tiers).",
          "float popBase = ta.sma(volume, popBaseLen)[1]",
          "float pop     = (na(popBase) or popBase == 0) ? na : volume[1] / popBase",
          "",
          "// All-Time High Volume (HEV) - running max over CONFIRMED bars only.",
          "var float maxVolEver = 0.0",
          "bool isHEV = false",
          "if volume[1] > maxVolEver",
          "    maxVolEver := volume[1]",
          "    isHEV := true"]

# ----- HOT SPOT calendar (verbatim from v2) -----
hotspot = '''
// ============================================
// === HOT SPOT - CALENDAR-BASED SIGNALS ===
// ============================================
// Fires 3-5 trading days BEFORE ~20 known recurring high-volume events/year.
// Calendar flags use [1] bar's date so the flag matches the drawn bar.
opExWindow = dayofmonth[1] >= 10 and dayofmonth[1] <= 17 and dayofweek[1] >= dayofweek.monday and dayofweek[1] <= dayofweek.wednesday
qtrEndWindow = (month[1] == 3 or month[1] == 6 or month[1] == 9 or month[1] == 12) and dayofmonth[1] >= 23 and dayofmonth[1] <= 27
russellWindow = month[1] == 6 and dayofmonth[1] >= 19 and dayofmonth[1] <= 24
taxLossWindow = month[1] == 12 and dayofmonth[1] >= 21 and dayofmonth[1] <= 26
janEffectWindow = month[1] == 12 and dayofmonth[1] >= 27 and dayofmonth[1] <= 30
hfRedemptionWindow = (month[1] == 5 or month[1] == 11) and dayofmonth[1] >= 10 and dayofmonth[1] <= 13
bool isHotSpot = opExWindow or qtrEndWindow or russellWindow or taxLossWindow or janEffectWindow or hfRedemptionWindow
'''

# ----- MEMORY: per-tier ring buffers + rel + record + rank -----
mem = ["", "// ============================================",
       "// === MAGNITUDE MEMORY (per-tier ring buffers) ===",
       "// ============================================",
       "// On each N-bar high: compare volume[1] to the last K N-highs (median/max/rank),",
       "// flag records, then push it into the buffer (capped at the memory-depth input)."]
for n in TIERS:
    # Empty-array calls (array.max/median on []) throw at runtime, and Pine's
    # and/or short-circuit is not safe to rely on -> guard sz>0 with an if/else.
    mem += [
        f"var array<float> hist{n} = array.new_float(0)",
        f"var float ever{n} = 0.0",
        f"float rel{n} = na",
        f"int rank{n} = na",
        f"bool recR{n} = false",
        f"bool recE{n} = false",
        f"if is{n}Bar",
        f"    int sz{n} = array.size(hist{n})",
        f"    if sz{n} > 0",
        f"        rel{n} := volume[1] / array.median(hist{n})",
        f"        recR{n} := volume[1] >= array.max(hist{n})",
        f"        int gt{n} = 0",
        f"        for i = 0 to sz{n} - 1",
        f"            if array.get(hist{n}, i) > volume[1]",
        f"                gt{n} := gt{n} + 1",
        f"        rank{n} := gt{n} + 1",
        f"    else",
        f"        recR{n} := true",
        f"        rank{n} := 1",
        f"    recE{n} := volume[1] > ever{n}",
        f"    ever{n} := math.max(ever{n}, volume[1])",
        f"    array.push(hist{n}, volume[1])",
        f"    if array.size(hist{n}) > math.max(1, int(mem{n} * memMult))",
        f"        array.shift(hist{n})",
    ]

# ----- UNIFIED plot_* (nesting priority: show only the deepest tier) -----
plotvars = ["", "// ============================================",
            "// === UNIFIED PLOT+ALERT CONDITIONS (nested: deepest tier only) ===",
            "// ============================================",
            "bool plot_HEV   = useHEV  and isHEV"]
# top tier down to 50: plot_N fires if is{N}Bar and not the next-bigger tier
desc = list(reversed(TIERS))               # 4999,4000,...,50
plotvars.append(f"bool plot_{desc[0]:<5} = use{desc[0]:<5} and is{desc[0]}Bar and not isHEV")
for i in range(1, len(desc)):
    n = desc[i]; up = desc[i - 1]
    plotvars.append(f"bool plot_{n:<5} = use{n:<5} and is{n}Bar and not is{up}Bar")
plotvars.append("bool plot_HS    = useHS   and isHotSpot")

# ----- DISPLAY SELECT: deepest fired tier -> the metadata that gets surfaced -----
sel = ["", "// ============================================",
       "// === DISPLAYED-TIER SELECTION (deepest fired -> alert metadata) ===",
       "// ============================================",
       "int    dispN    = na",
       "string dispTier = na",
       "float  dispRel  = na",
       "int    dispRank = na",
       "int    dispBuf  = na",
       "bool   dispRecR = false",
       "bool   dispRecE = false"]
# HEV first, then deepest tier down to 50
sel.append("if isHEV")
sel.append('    dispTier := "HEV"')
sel.append(f"    dispN := {TIERS[-1]}")
sel.append(f"    dispRel := rel{TIERS[-1]}")
sel.append(f"    dispRank := rank{TIERS[-1]}")
sel.append(f"    dispBuf := array.size(hist{TIERS[-1]})")
sel.append(f"    dispRecR := recR{TIERS[-1]}")
sel.append(f"    dispRecE := recE{TIERS[-1]}")
for n in desc:                              # 4999 down to 50
    sel.append(f"else if is{n}Bar")
    sel.append(f'    dispTier := "{n}"')
    sel.append(f"    dispN := {n}")
    sel.append(f"    dispRel := rel{n}")
    sel.append(f"    dispRank := rank{n}")
    sel.append(f"    dispBuf := array.size(hist{n})")
    sel.append(f"    dispRecR := recR{n}")
    sel.append(f"    dispRecE := recE{n}")
sel.append("bool anyTierFired = not na(dispN)")

# ----- pop color helper -----
colorfn = '''
// ============================================
// === MAGNITUDE COLOR (pop -> heat) ===
// ============================================
popColor(float p) =>
    color c = color.rgb(120, 120, 120)
    if na(p)
        c := color.new(color.gray, 45)
    else if p >= 12.0
        c := color.rgb(255, 0, 255)
    else if p >= 8.0
        c := color.rgb(255, 0, 0)
    else if p >= 5.0
        c := color.rgb(255, 140, 0)
    else if p >= 3.0
        c := color.rgb(255, 215, 0)
    else if p >= 2.0
        c := color.rgb(180, 180, 60)
    c
'''

# ----- PLOTTING -----
plots = ["", "// ============================================",
         "// === PLOTTING (offset=-1 to land on confirmed bar) ===",
         "// ============================================",
         'plotshape(plot_HEV, "HEV", shape.diamond, location.top, colByPop ? popColor(pop) : color.new(color.purple, 0), size=size.normal, text="HEV", textcolor=color.white, offset=-1)']
for i, n in enumerate(TIERS):
    plots.append(
        f'plotshape(plot_{n}, "{n}-Bar High", shape.circle, location.top, '
        f'colByPop ? popColor(pop) : {tier_ramp(i)}, '
        f'size={dot_size(n)}, text="{n}", textcolor=color.white, offset=-1)')
# extreme-pop star (independent of tier) + per-tier record markers
plots += [
    '// Extreme-magnitude star: any fired high whose pop clears the threshold.',
    'plotshape(anyTierFired and not na(pop) and pop >= popExtreme, "Extreme pop", shape.star, location.top, color.yellow, size=size.small, offset=-1)',
    '// Hollow box under a high that set a new per-tier ALL-TIME record.',
    'plotshape(anyTierFired and dispRecE, "Record-ever", shape.square, location.bottom, color.new(color.aqua, 0), size=size.tiny, offset=-1)',
    'plotshape(plot_HS, "Hot Spot", shape.cross, location.bottom, color.new(color.red, 0), size=size.tiny, offset=-1)',
    '',
    '// Hidden plots so legacy alertcondition() can reference live values via {{plot("...")}}.',
    'plot(pop,     "pop",      display=display.none)',
    'plot(dispRel, "relPrior", display=display.none)',
    'plot(dispN,   "tier",     display=display.none)',
]

# ----- ALERT() dynamic metadata + legacy alertcondition() -----
alerts = ["", "// ============================================",
          "// === ALERTS ===",
          "// ============================================",
          "// (1) Dynamic, metadata-rich alert() - select 'Any alert() function call'.",
          "string popStr = na(pop) ? \"na\" : str.tostring(pop, \"0.0\")",
          "string relStr = na(dispRel) ? \"na\" : str.tostring(dispRel, \"0.00\")",
          "string recStr = dispRecE ? \" | RECORD-EVER\" : (dispRecR ? \" | record-recent\" : \"\")",
          "if anyTierFired",
          "    string msg = \"HV \" + syminfo.ticker + \" | \" + dispTier + \"-bar high\"",
          "    msg := msg + \" | vol \" + str.tostring(volume[1], format.volume)",
          "    msg := msg + \" | \" + popStr + \"x recent avg\"",
          "    msg := msg + (na(dispRel) ? \"\" : \" | \" + relStr + \"x prior \" + dispTier + \"-highs\")",
          "    msg := msg + \" | rank \" + str.tostring(dispRank) + \"/\" + str.tostring(dispBuf)",
          "    msg := msg + recStr",
          "    msg := msg + (isHotSpot ? \" | HOTSPOT\" : \"\")",
          "    alert(msg, alert.freq_once_per_bar_close)",
          "if isHotSpot and not anyTierFired",
          "    alert(\"HV \" + syminfo.ticker + \" | HOTSPOT (approaching known high-volume date)\", alert.freq_once_per_bar_close)",
          "",
          "// (2) Legacy per-tier alertcondition() - const message + {{plot}} placeholders carry the metadata.",
          'alertcondition(plot_HEV, "Vol: HEV", "HEV all-time high vol | pop {{plot(\\"pop\\")}}x | rel {{plot(\\"relPrior\\")}}x")']
for n in TIERS:
    alerts.append(
        f'alertcondition(plot_{n}, "Vol: {n}-Bar", '
        f'"{n}-bar high vol | pop {{{{plot(\\"pop\\")}}}}x | rel {{{{plot(\\"relPrior\\")}}}}x prior {n}-highs")')
alerts.append('alertcondition(plot_HS, "Hot Spot", "Approaching known high-volume date (confirmed)")')

# ----- AGGREGATION / EXPORTS -----
agg = ["", "// ============================================",
       "// === SIGNAL AGGREGATION + EXPORTS (For Combination Studies) ===",
       "// ============================================",
       "// activeVolSignals = how deep into the ladder this bar fired (0.." + str(len(TIERS)) + "), + HEV.",
       "int activeVolSignals = " + " + ".join(f"(is{n}Bar ? 1 : 0)" for n in TIERS) + " + (isHEV ? 1 : 0)",
       "",
       f"var array<bool> signalStates = array.new_bool({len(TIERS) + 2}, false)"]
for i, n in enumerate(TIERS):
    agg.append(f"array.set(signalStates, {i}, is{n}Bar)")
agg.append(f"array.set(signalStates, {len(TIERS)}, isHEV)")
agg.append(f"array.set(signalStates, {len(TIERS) + 1}, isHotSpot)")
agg += ["",
        "// EXPORTS:",
        "//   Tiers (bool):       is50Bar .. is4999Bar (step 50 to 1000, then 2000/3000/4000/4999), isHEV, isHotSpot",
        "//   Plot conditions:    plot_HEV, plot_4999 .. plot_50, plot_HS",
        "//   Magnitude (float):  pop, dispRel; per-tier rel{N}, rank{N}; flags recR{N}/recE{N}",
        "//   Displayed high:     dispN, dispTier, dispRel, dispRank, dispBuf, dispRecR, dispRecE",
        f"//   Aggregations:       activeVolSignals (0..{len(TIERS) + 1}), signalStates[{len(TIERS) + 2}]"]

doc = "\n".join([HEADER] + inputs + calcs + [hotspot] + mem + plotvars + sel
                + [colorfn] + plots + alerts + agg) + "\n"

# ASCII-ONLY guard (TradingView's lexer rejects non-ASCII punctuation in source).
doc = (doc.replace("—", "-").replace("–", "-")
          .replace("‘", "'").replace("’", "'")
          .replace("“", '"').replace("”", '"'))
bad = [(i + 1, repr(ch)) for i, ln in enumerate(doc.splitlines())
       for ch in ln if ord(ch) > 0x7F]
if bad:
    raise SystemExit(f"NON-ASCII REMAINS (Pine will reject): {bad[:10]}")

OUT.write_text(doc)

# Self-report a few invariants for a quick sanity gate.
lines = doc.splitlines()
n_plotshape = sum(1 for l in lines if l.lstrip().startswith("plotshape("))
n_plot = sum(1 for l in lines if l.lstrip().startswith("plot(") and "display=display.none" in l)
n_alertcond = sum(1 for l in lines if l.lstrip().startswith("alertcondition("))
print(f"wrote {OUT}")
print(f"tiers={len(TIERS)}  lines={len(lines)}")
print(f"plotshape calls={n_plotshape}  hidden plot() calls={n_plot}  "
      f"total plot-count outputs={n_plotshape + n_plot}")
print(f"alertcondition calls={n_alertcond}")
print(f"memory depths: " + ", ".join(f"{n}:{mem_default(n)}" for n in TIERS))
