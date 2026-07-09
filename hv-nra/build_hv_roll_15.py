#!/usr/bin/env python3
"""
HV ROLL v2 -- 15 CUMULATIVE rolling-window high-volume cluster detectors.

WHY THIS FILE EXISTS
  The prior "HV ROLLING CLUSTERS" study counted "only" bands -- e.g. "500 only
  (not 1000+)", "150-or-250", "250 only". That answers "how many events landed
  in this narrow slice", which is the WRONG question: a 500-only detector goes
  QUIET exactly when a stock gets stronger and its highs graduate to 1000+.
  This rebuild replaces every band with a CUMULATIVE ">= threshold" class:
      4000+, 3000+, 2000+, 1000+, ... , 50+
  A "1000+" window counts every 1000-bar high OR RARER (including all-time
  highs). Strength never leaks out of a bucket -- a bigger high still counts in
  every smaller-or-equal window. This is exactly the user's spec:
  "4,000 and above, 3,000 and above, 2,000 and above, 1,000 and above ...
   not only 1,000 or only 500."

  Raw tier material is the full 50-step -> 4K mega ladder from
  HV_NRA_50step_ladder_v2 (50,100,...,1000,1500,2000,2500,3000,4000 + HEV).

THE 15 WINDOWS (rarest -> most common), all CUMULATIVE ">=":
  W1  HEV (all-time-high vol / Nagasaki)   W9   400+
  W2  4000+                                W10  300+
  W3  3000+                                W11  250+
  W4  2000+                                W12  200+
  W5  1500+                                W13  150+
  W6  1000+                                W14  100+
  W7  750+                                 W15  50+
  W8  500+

  CUMULATIVE BY CONSTRUCTION: is{N}Bar == "volume[1] is the max of the last N
  closed bars", which is TRUE whenever the bar is an N-bar high OR anything
  rarer (a 4000-bar high is automatically a 50-bar high). So the raw nested tier
  flag IS the ">=" class -- NO "not is{bigger}Bar" subtraction anywhere. That
  subtraction is precisely what created the old "only" bands; its absence is
  what makes every window cumulative.

DERIVATIVE / CALCULUS -> WINDOW SIZING (the default BARS per window)
  Model each ">= N" class as a near-Poisson point process. On a roughly
  stationary series the probability that any given closed bar is a NEW N-bar
  high is ~ 1/N (it is the argmax of N bars), so the class fires on average once
  every N bars (expected inter-arrival = N).

  The rolling count n_t = moving SUM of the event indicator over a trailing
  window of W bars -- a discrete INTEGRAL of the event stream. Under the null
  (purely random arrivals) its expected value is
        E[n] = W * (1/N) = W / N.
  Its first difference dn/dt is the clustering VELOCITY; the second difference
  is the ACCELERATION -- bursts. A cluster "fires" when n_t >= COUNT.

  To make a fire mean "events are arriving DENSER than random" -- i.e. real
  MOTION, not noise -- pick W so the firing count is a fixed multiple D of the
  random baseline:
        COUNT = D * E[n] = D * (W / N)   =>   W = round(COUNT * N / D).
  We ship D = 2 for EVERY window: a fire == events packed at ~2x the random
  rate. Same excess-density bar across all 15 scales; only the window length
  scales with tier rarity (W proportional to COUNT * N).

  "The more tightly bunched, the more motion": shrinking a window's BARS (or
  raising its COUNT) demands a higher local density -> a sharper derivative ->
  fires only on tighter, faster bursts. Every window's COUNT and BARS is a live
  input, so this is the exact knob the user tunes.

NON-REPAINTING (NRA) + CONSTITUTIONAL ROLLING WINDOWS -- kept verbatim:
  * Every tier compares the PRIOR CLOSED bar: volume[1] == ta.highest(volume,N)[1]
    -> value can never change once the bar closes.
  * Counting is gated on barstate.isconfirmed (closed bars only).
  * Each window is a TRUE SLIDING trailing-N moving sum (math.sum) -- O(1) per
    bar, NOT an anchored "wait N bars then reset" window (passes
    check_no_fixed_windows.sh).
  * Fire = LEADING EDGE of (n >= COUNT):  cond and not cond[1]  -- fires once
    when the cluster completes, then re-arms.
  * Plot and alert for each window share ONE boolean -> 1:1, can never desync.
  * Markers plot offset=-1 onto the closed bar that completed the cluster.

ASCII-ONLY output (TradingView's Pine lexer rejects non-ASCII punctuation).

Repetitive per-window blocks are GENERATED here -- one source of truth, zero
hand-typing drift -- exactly like build_hv_ladder.py in this same folder.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "versions" / "HV_ROLL_15_cumulative_50-4K_v1_2026-07-09.pine"
OUT.parent.mkdir(parents=True, exist_ok=True)

DENSITY = 2  # required events-per-window / random-baseline ratio (fire = 2x random density)


def wbars(count, tier):
    """Calculus-derived default window: W = round(COUNT * N / D), capped [30, 5000]."""
    w = round(count * tier / DENSITY)
    return max(30, min(5000, w))


# (idx, threshold_N or None=HEV, COUNT default, group/desc, short on-chart text)
# COUNT rises as tiers get MORE common: rare tiers have few events (COUNT 2),
# common tiers demand a bigger genuine cluster (COUNT up to 5). BARS is derived.
_SPEC = [
    (1,  None, 2, "HEV / Nagasaki (all-time-high vol)",   "HEV"),
    (2,  4000, 2, "4000-bar high or greater",             "4K+"),
    (3,  3000, 2, "3000-bar high or greater",             "3K+"),
    (4,  2000, 2, "2000-bar high or greater",             "2K+"),
    (5,  1500, 2, "1500-bar high or greater",             "1.5K+"),
    (6,  1000, 2, "1000-bar high or greater",             "1K+"),
    (7,  750,  2, "750-bar high or greater",              "750+"),
    (8,  500,  3, "500-bar high or greater",              "500+"),
    (9,  400,  3, "400-bar high or greater",              "400+"),
    (10, 300,  3, "300-bar high or greater",              "300+"),
    (11, 250,  3, "250-bar high or greater",              "250+"),
    (12, 200,  4, "200-bar high or greater",              "200+"),
    (13, 150,  4, "150-bar high or greater",              "150+"),
    (14, 100,  4, "100-bar high or greater",              "100+"),
    (15, 50,   5, "50-bar high or greater",               "50+"),
]

# Build full window records with derived default BARS. HEV window is set to 1000
# (two record-volume bars within 1000 bars = a real regime shift; N is unbounded
# so the formula does not apply -- documented explicitly).
WINDOWS = []
for idx, tier, count, desc, txt in _SPEC:
    bars = 1000 if tier is None else wbars(count, tier)
    WINDOWS.append(dict(idx=idx, tier=tier, count=count, bars=bars, desc=desc, txt=txt))

# Unique tier lookbacks we must compute is{N}Bar for (HEV handled separately).
TIER_NS = sorted({w["tier"] for w in WINDOWS if w["tier"] is not None})


def ramp(rank):
    """rank in [0,1]; 0 = most common (blue) -> 1 = rarest (red)."""
    R = int(round(40 + 215 * rank)); G = 45; B = int(round(255 - 215 * rank))
    return f"color.rgb({R}, {G}, {B}, 0)"


def size_for(tier):
    if tier is None or tier >= 2000:
        return "size.large"
    if tier >= 750:
        return "size.normal"
    if tier >= 250:
        return "size.small"
    return "size.tiny"


# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
HEADER = '''//@version=5
// ============================================================================
// HV ROLL v2  --  15 CUMULATIVE rolling-window high-volume cluster detectors
// ============================================================================
// WHAT CHANGED vs the old "HV ROLLING CLUSTERS"
//   Every "only" band ("500 only", "250-or-500", "150 only") is REPLACED with a
//   CUMULATIVE ">= threshold" class. A "1000+" window counts every 1000-bar
//   high OR RARER (up to all-time). Strength never leaks out of a bucket: a
//   bigger high still counts in every smaller-or-equal window. Raw tiers come
//   from the full 50-step -> 4K mega ladder (50..1000 step 50, then
//   1500/2000/3000/4000, plus HEV all-time).
//
// THE 15 WINDOWS (all CUMULATIVE ">="; rarest -> most common)
//   W1  HEV (all-time-high vol / Nagasaki)   W9   400+
//   W2  4000+                                W10  300+
//   W3  3000+                                W11  250+
//   W4  2000+                                W12  200+
//   W5  1500+                                W13  150+
//   W6  1000+                                W14  100+
//   W7  750+                                 W15  50+
//   W8  500+
//   CUMULATIVE BY CONSTRUCTION: is{N}Bar == "volume[1] is the max of the last N
//   closed bars" is TRUE for an N-bar high OR anything rarer, so the raw nested
//   tier flag IS the ">=" class. NO "not is{bigger}Bar" subtraction (that is
//   what made the old "only" bands). Each window: "at least COUNT events of its
//   class within the last BARS bars?"  COUNT and BARS are inputs on EVERY window.
//
// DERIVATIVE / CALCULUS -> default window sizing
//   Model each ">= N" class as ~Poisson: P(a closed bar is a new N-bar high) ~ 1/N,
//   so it fires ~ once per N bars. The rolling count n_t is the moving SUM (a
//   discrete INTEGRAL) of that event stream; its 1st difference is clustering
//   VELOCITY, its 2nd difference is ACCELERATION (bursts). Random baseline in a
//   W-bar window is E[n] = W/N. Requiring a fire to mean "events D-times denser
//   than random" gives  W = round(COUNT * N / D).  Shipped D = 2 for all 15:
//   every fire == ~2x random density. Only the window length scales with tier
//   rarity. TIGHTER window / higher COUNT -> sharper derivative -> more motion.
//
// NON-REPAINTING (NRA) + CONSTITUTIONAL ROLLING WINDOWS
//   * Tiers compare the PRIOR CLOSED bar: volume[1] == ta.highest(volume,N)[1].
//   * Counting gated on barstate.isconfirmed (closed bars only).
//   * Each window is a TRUE SLIDING trailing-N moving sum (math.sum, O(1)/bar) --
//     NOT an anchored wait-N-then-reset window (passes check_no_fixed_windows.sh).
//   * Fire = LEADING EDGE of (n >= COUNT):  cond and not cond[1]  -> fires once,
//     then re-arms. Plot and alert share ONE boolean (1:1, can never desync).
//   * Markers plot offset=-1 onto the closed bar that completed the cluster.
//
// GENERATED by hv-nra/build_hv_roll_15.py -- edit the generator, not this file.
// ASCII-only source (TradingView's Pine lexer rejects non-ASCII punctuation).
// ============================================================================

indicator("HV ROLL 15 (cumulative >= 50-4K ladder) NRA", shorttitle="HV ROLL 15", overlay=true, max_bars_back=5000)

// --- Rolling SLIDING count: TRUE events over the trailing `len` bars (O(1)/bar,
// --- not anchored). nz() keeps early bars at 0 instead of na.
f_roll_count(cond, len) => nz(math.sum(cond ? 1.0 : 0.0, math.max(1, len)))
'''


def inputs_block():
    lines = ["", "// ============================================================================",
             "// === INPUTS -- per window: Enable + COUNT (events) + within BARS (window) ===",
             "// ============================================================================",
             "// Defaults derive from W = round(COUNT * N / 2) (fire == ~2x random density).",
             "// Tune freely: smaller BARS or larger COUNT = tighter/faster = more motion."]
    for w in WINDOWS:
        i = w["idx"]
        grp = f'grp{i}  = "W{i}: {w["desc"]}"'
        lines.append(grp)
        lines.append(f'w{i}_on  = input.bool(true, "Enable W{i} {w["txt"]}", group=grp{i})')
        lines.append(f'w{i}_cnt = input.int({w["count"]}, "Count (events)", minval=1, inline="w{i}", group=grp{i})')
        lines.append(f'w{i}_win = input.int({w["bars"]}, "within Bars", minval=1, maxval=5000, inline="w{i}", group=grp{i})')
        lines.append("")
    return "\n".join(lines)


def tiers_block():
    lines = ["// ============================================================================",
             "// === RAW TIER FLAGS (counting material only -- no own plot/alert) ===",
             "// ============================================================================",
             "// volume[1] == ta.highest(volume,N)[1] on the PRIOR CLOSED bar -> can never",
             "// change once the bar closes (non-repainting). Each flag is already the",
             "// CUMULATIVE \">= N\" class (an N-bar high implies every shorter-tier high)."]
    for n in TIER_NS:
        lines.append(f"bool is{n}Bar = volume[1] == ta.highest(volume, {n})[1]")
    lines += ["",
              "// All-time-high volume (HEV == Nagasaki) -- running max over CONFIRMED bars only.",
              "var float maxVolEver = 0.0",
              "bool isHEV = false",
              "if volume[1] > maxVolEver",
              "    maxVolEver := volume[1]",
              "    isHEV := true",
              "bool isNagasaki = isHEV"]
    return "\n".join(lines)


def events_block():
    lines = ["", "// ============================================================================",
             "// === CLASS EVENTS (confirmed bars only) -- raw material each window counts ===",
             "// ============================================================================",
             "bool conf = barstate.isconfirmed"]
    for w in WINDOWS:
        i = w["idx"]
        if w["tier"] is None:
            expr = "conf and isHEV"
        else:
            expr = f"conf and is{w['tier']}Bar"
        lines.append(f'bool evt_W{i} = {expr}   // W{i}  {w["txt"]} (>=)')
    return "\n".join(lines)


def detections_block():
    lines = ["", "// ============================================================================",
             "// === ROLLING-WINDOW CLUSTER DETECTIONS (sliding trailing-N, leading-edge) ===",
             "// ============================================================================",
             "// nN = events of class in trailing winN bars.  cN = nN >= countN.",
             "// fire_WN = leading edge of cN (fires once when the cluster completes)."]
    for w in WINDOWS:
        i = w["idx"]
        lines.append(f"float n{i} = f_roll_count(evt_W{i}, w{i}_win)")
    lines.append("")
    for w in WINDOWS:
        i = w["idx"]
        lines.append(f"bool c{i} = n{i} >= w{i}_cnt")
    lines.append("")
    for w in WINDOWS:
        i = w["idx"]
        lines.append(f"bool fire_W{i} = w{i}_on and c{i} and not c{i}[1]")
    return "\n".join(lines)


def plots_block():
    lines = ["", "// ============================================================================",
             "// === PLOTS -- 15 cumulative detectors (offset=-1 -> lands on the closed bar",
             "// === that completed the cluster). Windows are independent: several scales",
             "// === can light up on the same bar -- that overlap IS the multi-scale motion.",
             "// ============================================================================"]
    n_win = len(WINDOWS)
    for k, w in enumerate(WINDOWS):
        i = w["idx"]
        # rarity rank: W1 (HEV) rarest -> 1.0 ; W15 (50+) most common -> 0.0
        rank = (n_win - k - 1) / (n_win - 1)
        loc = "location.top" if i <= 8 else "location.bottom"
        if i == 1:
            shape = "shape.diamond"; col = "color.new(color.purple, 0)"
        elif i <= 8:
            shape = "shape.circle"; col = ramp(rank)
        elif i <= 12:
            shape = "shape.triangledown"; col = ramp(rank)
        else:
            shape = "shape.cross"; col = ramp(rank)
        sz = size_for(w["tier"])
        lines.append(
            f'plotshape(fire_W{i}, "W{i} {w["txt"]} cumulative", {shape}, {loc}, {col}, '
            f'size={sz}, text="{w["txt"]}", textcolor=color.white, offset=-1)'
        )
    lines += ["", "// Numeric counts (data-window only -- helps tune COUNT/BARS)."]
    for w in WINDOWS:
        i = w["idx"]
        lines.append(f'plot(n{i}, "W{i} count ({w["txt"]})", display=display.data_window)')
    return "\n".join(lines)


def motion_block():
    lines = ["", "// ============================================================================",
             "// === MOTION READOUTS (the calculus, on tap) -- data-window only ===",
             "// ============================================================================",
             "// clusterLoad = how many of the 15 scales are CURRENTLY in an active cluster",
             "// state (c1..c15). Its 1st difference is motion VELOCITY, 2nd is ACCELERATION.",
             "// When many scales light up together, that is strong coordinated motion."]
    cload = "int clusterLoad = " + " + ".join(f"(c{w['idx']} ? 1 : 0)" for w in WINDOWS)
    afire = "int activeWindows = " + " + ".join(f"(fire_W{w['idx']} ? 1 : 0)" for w in WINDOWS)
    lines += [
        cload,
        afire,
        "float motionVel = ta.change(clusterLoad)        // d(clusterLoad)/dbar  -- velocity",
        "float motionAcc = ta.change(motionVel)          // d2(clusterLoad)/dbar2 -- acceleration",
        'plot(clusterLoad,   "clusterLoad (0..15)",   color=color.white,  display=display.data_window)',
        'plot(activeWindows, "activeWindows (0..15)", color=color.aqua,   display=display.data_window)',
        'plot(motionVel,     "motion velocity",       color=color.lime,   display=display.data_window)',
        'plot(motionAcc,     "motion acceleration",   color=color.orange, display=display.data_window)',
    ]
    return "\n".join(lines)


def alerts_block():
    lines = ["", "// ============================================================================",
             "// === ALERTS -- per-window (1:1 with plots), plus ANY + any-call() ===",
             "// ============================================================================"]
    for w in WINDOWS:
        i = w["idx"]
        lines.append(
            f'alertcondition(fire_W{i}, "W{i} {w["txt"]} cumulative", '
            f'"W{i}: {w["txt"]} (>=) cluster on {{{{ticker}}}}")'
        )
    lines.append("")
    any_expr = " or ".join(f"fire_W{w['idx']}" for w in WINDOWS)
    lines.append(f"bool any_fire = {any_expr}")
    lines.append('alertcondition(any_fire, "ANY HV cumulative cluster", "ANY HV cumulative rolling cluster fired on {{ticker}}")')
    lines += ["",
              "// any-call alert() function: set ONE TradingView alert to \"Any alert() function",
              "// call\" and it catches every window. Payload names which windows fired this bar.",
              "if any_fire and conf",
              '    string m = ""']
    for w in WINDOWS:
        i = w["idx"]
        lines.append(f'    m := fire_W{i} ? m + "{w["txt"]} " : m')
    lines.append('    alert("HV_ROLL15|TICKER:" + syminfo.ticker + "|TF:" + timeframe.period + "|FIRED:" + m, alert.freq_once_per_bar_close)')
    return "\n".join(lines)


def exports_block():
    tiers = ", ".join(f"is{n}Bar" for n in TIER_NS)
    lines = ["", "// ============================================================================",
             "// === EXPORTS (for combination / fire-matrix consumers) ===",
             "// ============================================================================",
             f"// Raw tiers (bool, cumulative >=): {tiers}, isHEV (== isNagasaki)",
             "// Window fires (bool):   fire_W1 .. fire_W15",
             "// Window counts (float): n1 .. n15",
             "// Motion (int/float):    clusterLoad(0..15), activeWindows(0..15), motionVel, motionAcc"]
    return "\n".join(lines)


def main():
    parts = [
        HEADER,
        inputs_block(),
        tiers_block(),
        events_block(),
        detections_block(),
        plots_block(),
        motion_block(),
        alerts_block(),
        exports_block(),
        "",
    ]
    src = "\n".join(parts)
    # ASCII gate: TradingView's lexer rejects non-ASCII punctuation.
    src.encode("ascii")
    OUT.write_text(src)
    # Echo the derived default schedule so the calculus is auditable.
    print(f"WROTE {OUT}  ({len(src.splitlines())} lines)")
    print("  W  class(>=)  COUNT  BARS   baseline(W/N)  density(COUNT*N/W)")
    for w in WINDOWS:
        if w["tier"] is None:
            print(f"  W{w['idx']:<2} {'HEV':<9} {w['count']:>5}  {w['bars']:>5}   (all-time -- formula n/a)")
        else:
            base = w["bars"] / w["tier"]
            dens = w["count"] * w["tier"] / w["bars"]
            print(f"  W{w['idx']:<2} {str(w['tier'])+'+':<9} {w['count']:>5}  {w['bars']:>5}   {base:>10.2f}   {dens:>6.2f}x")


if __name__ == "__main__":
    main()
