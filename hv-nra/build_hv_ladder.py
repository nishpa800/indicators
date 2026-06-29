#!/usr/bin/env python3
"""
HV NRA - SAME indicator, with the lookback ladder extended.

This is the existing 50-step ladder (50,100,...,1000) with FOUR coarse tiers
added on top: 2000, 3000, 4000, 4999. Nothing else changes - same non-repainting
architecture, same single-marker-per-bar nesting, same plot/alert pairing,
same HEV all-time-high tier, same exports. Just more tiers.

Top tier is 4999 (not 5000) so ta.highest(volume,N)[1] stays inside Pine's
historical buffer.

The repetitive per-tier blocks are GENERATED so they stay consistent.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "versions" / "HV_NRA_ladder_to_4999_2026-06-29.pine"
OUT.parent.mkdir(parents=True, exist_ok=True)

TIERS = list(range(50, 1001, 50)) + [2000, 3000, 4000, 4999]   # 24 tiers, ascending
assert TIERS == sorted(TIERS) and len(TIERS) == 24 and TIERS[-1] == 4999


def ramp(i):
    """blue (small tier) -> red (large tier)."""
    r = i / (len(TIERS) - 1)
    R = int(round(40 + 215 * r)); G = 45; B = int(round(255 - 215 * r))
    return f"color.rgb({R}, {G}, {B}, 0)"


def size(n):
    return "size.normal" if n >= 600 else ("size.small" if n >= 250 else "size.tiny")


HEADER = '''//@version=5
indicator("HV(50-1000 step50 + 2k/3k/4k/4999 / HEV) NRA", overlay=true)

// ============================================
// === NON-REPAINTING ARCHITECTURE ===
// ============================================
// PROBLEM 1 - LIVE BAR REPAINTING:
//   `volume == ta.highest(volume, N)` evaluates on every tick.
//   Volume accumulates intra-bar, so the condition can flip true->false
//   or false->true dozens of times before bar close. Signals appear,
//   disappear, and move to different bars after the fact.
//
// PROBLEM 2 - ALERT / PLOT DESYNC:
//   Original plotshapes used priority filtering (e.g. `not isHEV`)
//   but alertcondition() did NOT use the same filters.
//
// FIX - ALL signals now:
//   1. Use [1] (prior confirmed bar) for ALL volume comparisons
//      so values can NEVER change once printed.
//   2. Plot and alert conditions use IDENTICAL boolean expressions
//      stored in named variables - one source of truth, zero drift.
//   3. Every plotshape and every alertcondition references the SAME
//      `plot_*` variable so a plot can never exist without its alert.
//
// LADDER (this version): the 50-step ladder (50,100,...,1000) plus four
//   coarse tiers on top - 2000, 3000, 4000, 4999 (24 tiers total).
//   Tiers are NESTED (a 4999-bar high is also a 50-bar high), so exactly
//   ONE marker prints per bar: the highest tier reached.
// ============================================
'''

# ----- INPUTS -----
inputs = ["", "// ============================================",
          "// === INPUTS ===", "// ============================================"]
for n in TIERS:
    inputs.append(f'use{n:<5} = input.bool(true, "Show {n}-Bar High Vol")')
inputs.append('useHEV   = input.bool(true, "Show All-Time High Vol (HEV)")')

# ----- VOLUME HIGH CALCULATIONS -----
calcs = ["", "// ============================================",
         "// === VOLUME HIGH CALCULATIONS (CONFIRMED BARS ONLY) ===",
         "// ============================================",
         "// All comparisons use [1] (prior CLOSED bar). volume[1] == ta.highest(volume,N)[1]",
         "// can never change once the bar closes. Markers land on the [1] bar via offset=-1.", ""]
for n in TIERS:
    calcs.append(f"bool is{n}Bar = volume[1] == ta.highest(volume, {n})[1]")
calcs += ["",
          "// All-Time High Volume (HEV) - running max over CONFIRMED bars only.",
          "var float maxVolEver = 0.0",
          "bool isHEV = false",
          "if volume[1] > maxVolEver",
          "    maxVolEver := volume[1]",
          "    isHEV := true"]

# ----- UNIFIED plot_* (nesting priority: show only the highest tier) -----
plotvars = ["", "// ============================================",
            "// === UNIFIED PLOT+ALERT CONDITIONS ===",
            "// ============================================",
            "// Tiers are nested -> show ONLY the highest tier reached per bar:",
            "//   plot_N fires only if is{N}Bar AND the next tier up did NOT fire.",
            "//   Priority: HEV > 4999 > 4000 > 3000 > 2000 > 1000 > 950 > ... > 50.", ""]
desc = list(reversed(TIERS))                       # 4999,4000,...,50
plotvars.append(f"bool plot_HEV   = useHEV  and isHEV")
plotvars.append(f"bool plot_{desc[0]:<5} = use{desc[0]:<5} and is{desc[0]}Bar and not isHEV")
for i in range(1, len(desc)):
    n = desc[i]; up = desc[i - 1]
    plotvars.append(f"bool plot_{n:<5} = use{n:<5} and is{n}Bar and not is{up}Bar")

# ----- PLOTTING -----
plots = ["", "// ============================================",
         "// === PLOTTING (offset=-1 to land on confirmed bar) ===",
         "// ============================================",
         'plotshape(plot_HEV, "HEV", shape.diamond, location.top, color.new(color.purple, 0), size=size.normal, text="HEV", textcolor=color.purple, offset=-1)']
for i, n in enumerate(TIERS):
    plots.append(
        f'plotshape(plot_{n}, "{n}-Bar High", shape.circle, location.top, {ramp(i)}, '
        f'size={size(n)}, text="{n}", textcolor=color.white, offset=-1)')

# ----- ALERTS (1:1 with plot_*) -----
alerts = ["", "// ============================================",
          "// === ALERTS (same variables as plots - guaranteed 1:1) ===",
          "// ============================================",
          'alertcondition(plot_HEV, "Vol: HEV", "All-Time High Volume Detected (confirmed)")']
for n in TIERS:
    alerts.append(f'alertcondition(plot_{n}, "Vol: {n}-Bar", "{n}-Bar High Volume Detected (confirmed)")')

# ----- AGGREGATION / EXPORTS -----
agg = ["", "// ============================================",
       "// === SIGNAL AGGREGATION (For Combination Studies) ===",
       "// ============================================",
       f"// activeVolSignals = how deep into the ladder this bar fired (0..{len(TIERS)}), + HEV.",
       "int activeVolSignals = " + " + ".join(f"(is{n}Bar ? 1 : 0)" for n in TIERS) + " + (isHEV ? 1 : 0)",
       "",
       f"var array<bool> signalStates = array.new_bool({len(TIERS) + 1}, false)"]
for i, n in enumerate(TIERS):
    agg.append(f"array.set(signalStates, {i}, is{n}Bar)")
agg.append(f"array.set(signalStates, {len(TIERS)}, isHEV)")
agg += ["",
        "// ============================================",
        "// === EXPORTS (For Combination Indicator Studies) ===",
        "// ============================================",
        "// Individual tiers (bool):  is50Bar .. is1000Bar (step 50), is2000/is3000/is4000/is4999, isHEV",
        "// Plot/alert conditions:    plot_HEV, plot_4999 .. plot_50",
        f"// Aggregations (int):       activeVolSignals (0..{len(TIERS) + 1})",
        f"// Collections (array<bool>): signalStates[{len(TIERS) + 1}]  // [0..{len(TIERS) - 1}]=tiers, [{len(TIERS)}]=HEV"]

doc = "\n".join([HEADER] + inputs + calcs + plotvars + plots + alerts + agg) + "\n"

# ASCII-ONLY guard (TradingView's Pine lexer rejects non-ASCII punctuation in source).
doc = (doc.replace("—", "-").replace("–", "-")
          .replace("‘", "'").replace("’", "'")
          .replace("“", '"').replace("”", '"'))
bad = [(i + 1, repr(ch)) for i, ln in enumerate(doc.splitlines())
       for ch in ln if ord(ch) > 0x7F]
if bad:
    raise SystemExit(f"NON-ASCII REMAINS (Pine will reject): {bad[:10]}")

OUT.write_text(doc)
print(f"wrote {OUT}")
print(f"tiers={len(TIERS)}  lines={len(doc.splitlines())}")
