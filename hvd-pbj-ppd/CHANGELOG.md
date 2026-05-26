# HVD-PBJ-PPD — Changelog

Newest first. Each version = one file in `versions/`.

---

## v1.1 — 2026-05-26 — Combo Chain Fix
**File:** `versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine`
**Lines modified:** 1011–1046

---

### What was happening

You're looking at the chart. You see two unified combos land within 3–4 bars of each other. You have combo chain set to "2 hits within 5 bars." Combo chain should fire. It doesn't. You've verified the signals are real. The indicator just isn't detecting them.

---

### Why it was happening — the counting window was lying to you

Combo chain works by scanning a window of recent bars and counting how many FVG combo or Matrix combo events landed inside that window. If the count meets your threshold (e.g., 2 hits), and PBJ is also present, combo chain fires.

The problem: **the indicator was telling you it scanned 5 bars, but for FVG combo events, it actually only scanned 4.**

Here's why. There are two types of combo events:

- **FVG Combo (csNew1)** — requires a Fair Value Gap + high-volume/GZI + an RVOL or WMD-tier signal. This fires on one bar but describes the PREVIOUS bar (offset -1).
- **Matrix Combo (csNew2)** — requires a 67-bar volume high (Neo/Trinity) + an RVOL or WMD-tier signal. This fires on the current bar and describes the current bar (offset 0).

Because FVG combos have this one-bar offset, someone tried to "correct" for it by shifting the FVG lookup inside the counting loop. The intent was to align both types of events to the same visual bar. The execution introduced three problems:

**Problem 1: The first bar in the window was blind to FVG combos.**
The counting loop starts at bar 0 (the most recent confirmed bar) and works backward. At bar 0, it ONLY looked for Matrix combos. FVG combos on bar 0 were skipped entirely — they weren't counted until the next iteration, effectively pushing them one step later.

**Problem 2: The last bar in the window was unreachable for FVG combos.**
If your window is 5 bars, the loop scans bars 0 through 4. But because FVG events were being looked up with a shifted position, the oldest FVG event the loop could actually reach was at bar 3, not bar 4. The 5th bar was invisible.

This means: if you set "within 5 bars," FVG combos only had a 4-bar window. Set "within 2 bars," they only had a 1-bar window.

**Problem 3: Unified combos could be double-counted.**
A Unified Combo (csNew3) is defined as an FVG combo AND a Matrix combo landing on adjacent bars — two events that together describe one signal. The reference version in SQUARIFY accounts for this: when it detects a unified combo, it subtracts 1 from the count so the pair counts as one event, not two. HVD-PBJ-PPD had no such correction. In some configurations this caused over-counting; in others it masked the under-counting from Problems 1 and 2.

---

### The proof — a concrete scenario

You see two FVG combos on the chart, 4 bars apart. Settings: 2 hits within 5 bars.

**What SQUARIFY does (correct):**
- Scans bar 0 → finds the first FVG combo → count = 1
- Scans bar 4 → finds the second FVG combo → count = 2
- 2 ≥ 2 → **combo chain fires**

**What HVD-PBJ-PPD did (broken):**
- Scans bar 0 → skips FVG (Problem 1) → count = 0
- Scans bar 1 → finds the first FVG combo (shifted by one) → count = 1
- Scans bar 4 → tries to find the second FVG combo, but due to the shift (Problem 2), it looks at bar 3 instead of bar 4 → nothing there → count stays at 1
- 1 < 2 → **combo chain does NOT fire**

The second event was within your window. The indicator just couldn't see it.

---

### What was fixed

The counting logic was replaced with the SQUARIFY reference version. Three changes:

**Change 1: Count both event types the same way.**
Instead of treating FVG combos and Matrix combos differently with a shifted lookup, both are now counted at their actual positions in the window. No special handling, no shifting. If an event happened within your window, it's counted.

**Change 2: Add the unified combo correction.**
When a Unified Combo fires (an FVG combo and a Matrix combo on adjacent bars that together form one signal), the count is reduced by 1 so that one event isn't counted as two. This matches SQUARIFY.

**Change 3: Simplify the deactivation condition.**
The logic that resets combo chain when no combo events are present was simplified to use the same unified variables (FVG Combo OR Matrix Combo) instead of listing all four sub-components individually. Functionally identical, just cleaner.

---

### What was verified to be correct and left alone

The underlying signal definitions — the conditions that define what an FVG combo IS, what a Matrix combo IS, what a Unified Combo IS — are identical across SQUARIFY, HVD-PBJ-PPD, and B2B PUP. They were checked line by line. No discrepancies.

| Signal | Definition (same across all three indicators) |
|---|---|
| **FVG Combo** | Confirmed bar + body ≥ threshold + (HV-FVG or GZI clustering) + (SAAB or RVOL 1x or Grand Slam or Pentagon or WTC or Hiroshima or Nagasaki on the prior bar) |
| **Matrix Combo** | Body ≥ threshold + (Neo or Trinity or aligned variants) + (SAAB or RVOL 1x or Grand Slam or Pentagon or WTC or Hiroshima or Nagasaki on the current bar) |
| **Unified Combo** | FVG Combo on the current bar AND Matrix Combo on the prior bar (both describing the same visual bar) |

These definitions were NOT changed. The only thing that changed was **how the combo chain counts events inside its scanning window**.

---

### What's NOT affected

- **B2B PUP** — does not have combo chain logic. Has Unified Combo but no chain counting. Not affected.
- **TNT OD** — does not have combo chain logic. Not affected.
- **SQUARIFY** — already had the correct counting algorithm. This fix brings HVD-PBJ-PPD in line with it.
- **All other HVD-PBJ-PPD pipelines** — HV+D engine, PBJ engine, USE engine, Floor/2F/Rooftop/Penthouse, Opening Drive, Long-Short Chain, everything else — untouched.

---

### How to verify on TradingView

1. Paste the fixed HVD-PBJ-PPD source into TradingView.
2. Load SQUARIFY v2 on the same chart, same ticker, same timeframe.
3. Set both indicators to Min Hits = 2, Within Bars = 5.
4. Combo chain markers should now fire on the same bars in both indicators.
5. Specifically look for: two FVG-only combos separated by 4 bars — this is the scenario that was being missed.

---

## v1 — 2026-05-05 (initial commit)
**File:** `versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine`

Initial cleanup pass from TradingView source (entity 8A6Sm9).

**Removed:** Dashboard, Acceleration Periods, Tables, signal-bar tracking.
**Kept untouched:** FVG, HV, GZI, mitigations, all 4 pipelines (HV+D, PBJ, USE, Triple Co-occurrence).
