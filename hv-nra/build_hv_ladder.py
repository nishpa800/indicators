#!/usr/bin/env python3
"""
HV NRA — densify the volume-high lookback ladder to a full 50-bar step:
  50, 100, 150, 200, ... 900, 950, 1000  (20 tiers)
replacing the original sparse 50/150/250/500/1000.

Repetitive tier blocks are GENERATED (one source of truth, no hand-typing drift).
HEV running-max, Hot-Spot calendar, and the non-repainting architecture
(volume[1] + ta.highest(...)[1] + offset=-1, plot==alert 1:1) are kept VERBATIM.

Tiers are NESTED: a 1000-bar high is automatically a high at every shorter tier,
so exactly ONE marker prints per bar (the highest tier reached) via the
`not is{N+50}Bar` priority chain — same single-marker behavior as the original.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "versions" / "HV_NRA_50step_ladder_v2_2026-06-13.pine"
OUT.parent.mkdir(parents=True, exist_ok=True)

TIERS = list(range(50, 1001, 50))          # [50,100,...,1000] -> 20 tiers
assert len(TIERS) == 20 and TIERS[-1] == 1000


def ramp(i):
    """blue (small tier) -> red (large tier)."""
    r = i / (len(TIERS) - 1)
    R = int(round(40 + 215 * r)); G = 45; B = int(round(255 - 215 * r))
    return f"color.rgb({R}, {G}, {B}, 0)"


def size(n):
    return "size.normal" if n >= 600 else ("size.small" if n >= 250 else "size.tiny")


HEADER = '''//@version=5
indicator("HV(50-1000 step50 / HEV / HS) NRA", overlay=true)

// ============================================
// === NON-REPAINTING ARCHITECTURE ===
// ============================================
// PROBLEM 1 — LIVE BAR REPAINTING:
//   `volume == ta.highest(volume, N)` evaluates on every tick.
//   Volume accumulates intra-bar, so the condition can flip true->false
//   or false->true dozens of times before bar close. Signals appear,
//   disappear, and move to different bars after the fact.
//
// PROBLEM 2 — ALERT / PLOT DESYNC:
//   Original plotshapes used priority filtering (e.g. `not isHEV`)
//   but alertcondition() did NOT use the same filters.
//
// FIX — ALL signals now:
//   1. Use [1] (prior confirmed bar) for ALL volume comparisons
//      so values can NEVER change once printed.
//   2. Plot and alert conditions use IDENTICAL boolean expressions
//      stored in named variables — one source of truth, zero drift.
//   3. Every plotshape and every alertcondition references the SAME
//      `plot_*` variable so a plot can never exist without its alert.
//
// LADDER CHANGE (this version): the lookback tiers are now a FULL
//   50-bar step ladder — 50, 100, 150, 200, ... 900, 950, 1000 (20 tiers) —
//   replacing the original sparse 50/150/250/500/1000.
//   Tiers are NESTED (a 1000-bar high is also a 50-bar high), so exactly
//   ONE marker prints per bar: the highest tier reached.
// ============================================
'''

# ----- INPUTS -----
inputs = ["", "// ============================================",
          "// === INPUTS ===", "// ============================================"]
for n in TIERS:
    inputs.append(f'use{n:<4} = input.bool(true, "Show {n}-Bar High Vol")')
inputs.append('useHEV  = input.bool(true, "Show All-Time High Vol (HEV)")')
inputs.append('useHS   = input.bool(true, "Show Hot Spot Signals")')

# ----- VOLUME CALCS (verbatim architecture comment) + 20 tiers + HEV verbatim -----
calcs = ["", "// ============================================",
         "// === VOLUME HIGH CALCULATIONS (CONFIRMED BARS ONLY) ===",
         "// ============================================",
         "// All comparisons use [1] (prior CLOSED bar). volume[1] == ta.highest(volume,N)[1]",
         "// can never change once the bar closes. Markers land on the [1] bar via offset=-1.", ""]
for i, n in enumerate(TIERS, 1):
    calcs.append(f"bool is{n}Bar = volume[1] == ta.highest(volume, {n})[1]")
calcs += ["",
          "// All-Time High Volume (HEV) — running max over CONFIRMED bars only.",
          "var float maxVolEver = 0.0",
          "bool isHEV = false",
          "if volume[1] > maxVolEver",
          "    maxVolEver := volume[1]",
          "    isHEV := true"]

# ----- HOT SPOT calendar (verbatim) -----
hotspot = '''
// ============================================
// === HOT SPOT — CALENDAR-BASED SIGNALS ===
// ============================================
// Fires 3-5 trading days BEFORE ~20 known recurring high-volume events/year.
// Calendar flags use [1] bar's date so the flag matches the drawn bar.

// --- A) Monthly OpEx (3rd Friday = dayofmonth 15-21) ---
opExWindow = dayofmonth[1] >= 10 and dayofmonth[1] <= 17 and dayofweek[1] >= dayofweek.monday and dayofweek[1] <= dayofweek.wednesday
// --- B) Quarter-End Rebalancing ---
qtrEndWindow = (month[1] == 3 or month[1] == 6 or month[1] == 9 or month[1] == 12) and dayofmonth[1] >= 23 and dayofmonth[1] <= 27
// --- C) Russell Reconstitution (last Friday of June) ---
russellWindow = month[1] == 6 and dayofmonth[1] >= 19 and dayofmonth[1] <= 24
// --- D) Tax-Loss Selling (peaks last days of Dec) ---
taxLossWindow = month[1] == 12 and dayofmonth[1] >= 21 and dayofmonth[1] <= 26
// --- E) January Effect (early-Jan buying surge) ---
janEffectWindow = month[1] == 12 and dayofmonth[1] >= 27 and dayofmonth[1] <= 30
// --- F) Hedge Fund Redemption Notices (~May 15 & Nov 15) ---
hfRedemptionWindow = (month[1] == 5 or month[1] == 11) and dayofmonth[1] >= 10 and dayofmonth[1] <= 13

bool isHotSpot = opExWindow or qtrEndWindow or russellWindow or taxLossWindow or janEffectWindow or hfRedemptionWindow
'''

# ----- UNIFIED plot_* (nesting priority: show only the highest tier) -----
plotvars = ["", "// ============================================",
            "// === UNIFIED PLOT+ALERT CONDITIONS ===",
            "// ============================================",
            "// Tiers are nested -> show ONLY the highest tier reached per bar:",
            "//   plot_N fires only if is{N}Bar AND the next tier up (N+50) did NOT fire.",
            "//   Priority: HEV > 1000 > 950 > ... > 100 > 50.   Hot Spot is independent.", ""]
plotvars.append("bool plot_HEV  = useHEV  and isHEV")
plotvars.append("bool plot_1000 = use1000 and is1000Bar and not isHEV")
for i in range(len(TIERS) - 2, -1, -1):           # 950 down to 50
    n = TIERS[i]; up = TIERS[i + 1]
    plotvars.append(f"bool plot_{n:<4} = use{n:<4} and is{n}Bar and not is{up}Bar")
plotvars.append("bool plot_HS   = useHS   and isHotSpot")

# ----- PLOTTING -----
plots = ["", "// ============================================",
         "// === PLOTTING (offset=-1 to land on confirmed bar) ===",
         "// ============================================",
         'plotshape(plot_HEV, "HEV", shape.diamond, location.top, color.new(color.purple, 0), size=size.normal, text="HEV", textcolor=color.purple, offset=-1)']
for i, n in enumerate(TIERS):
    plots.append(
        f'plotshape(plot_{n}, "{n}-Bar High", shape.circle, location.top, {ramp(i)}, '
        f'size={size(n)}, text="{n}", textcolor=color.white, offset=-1)')
plots.append('plotshape(plot_HS, "Hot Spot", shape.cross, location.bottom, color.new(color.red, 0), size=size.tiny, offset=-1)')

# ----- ALERTS (1:1 with plot_*) -----
alerts = ["", "// ============================================",
          "// === ALERTS (same variables as plots — guaranteed 1:1) ===",
          "// ============================================",
          'alertcondition(plot_HEV, "Vol: HEV", "All-Time High Volume Detected (confirmed)")']
for n in TIERS:
    alerts.append(f'alertcondition(plot_{n}, "Vol: {n}-Bar", "{n}-Bar High Volume Detected (confirmed)")')
alerts.append('alertcondition(plot_HS, "Hot Spot", "Approaching Known High-Volume Date (confirmed)")')

# ----- AGGREGATION / EXPORTS -----
agg = ["", "// ============================================",
       "// === SIGNAL AGGREGATION (For Combination Studies) ===",
       "// ============================================",
       "// activeVolSignals = how deep into the ladder this bar fired (0..20), + HEV.",
       "int activeVolSignals = " + " + ".join(f"(is{n}Bar ? 1 : 0)" for n in TIERS) + " + (isHEV ? 1 : 0)",
       "",
       f"var array<bool> signalStates = array.new_bool({len(TIERS) + 2}, false)"]
for i, n in enumerate(TIERS):
    agg.append(f"array.set(signalStates, {i}, is{n}Bar)")
agg.append(f"array.set(signalStates, {len(TIERS)}, isHEV)")
agg.append(f"array.set(signalStates, {len(TIERS) + 1}, isHotSpot)")
agg += ["",
        "// ============================================",
        "// === EXPORTS (For Combination Indicator Studies) ===",
        "// ============================================",
        "// Individual tiers (bool):  is50Bar .. is1000Bar (step 50), isHEV, isHotSpot",
        "// Plot/alert conditions:    plot_HEV, plot_1000 .. plot_50, plot_HS",
        "// Aggregations (int):       activeVolSignals (0..21)",
        "// Collections (array<bool>): signalStates[22]  // [0..19]=tiers, [20]=HEV, [21]=HotSpot"]

doc = "\n".join([HEADER] + inputs + calcs + [hotspot] + plotvars + plots + alerts + agg) + "\n"
OUT.write_text(doc)
print(f"wrote {OUT}")
print(f"tiers={len(TIERS)}  lines={len(doc.splitlines())}")
