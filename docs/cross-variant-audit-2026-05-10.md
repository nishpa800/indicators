# Cross-Variant Audit Report — HVD/PBJ/PPD & VOB-Asym Families
**Date:** 2026-05-10  
**Ingestion Event:** Master Directory sync (two new hvd-pbj-ppd variants + one new vob-asym variant)  
**Scope:** Structural delta analysis across three sibling families

---

## Executive Summary

Three new sibling variants were ingested from Anish's Master Directory on 2026-05-10:

| Indicator | Variant | Lines | Source | Delta vs. Reference |
|-----------|---------|-------|--------|---------------------|
| hvd-pbj-ppd | 1939 | 1939 | MASTERDIR | +172 vs. THE_ONLY_ONE (1767); Tier-1 defaults flipped |
| hvd-pbj-ppd | 2246 | 2246 | MASTERDIR | +479 vs. THE_ONLY_ONE (1767); largest variant |
| vob-asym | ummmm | 1473 | MASTERDIR | Identical line count to v8 but plotshape shapes/locations changed |

**Key Finding:** These variants are NOT simple aliases. Each exhibits structural differences in input defaults, feature enablement, or visual presentation. The audit enumerates per-variant deltas and flags items requiring TradingView verification.

---

## Family: hvd-pbj-ppd (Three Variants)

### Reference: HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine (1767 lines)

**Roots Count:** 42  
**Composites Count:** 23  
**Tier-1 Defaults (Reference):**
- d2_mult: 2.5
- h1On (HTF Profile 1): false
- h2On (HTF Profile 2): false
- h2From: "3 Hour"

---

### Variant A: HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine (1939 lines)

| Attribute | Variant 1939 | THE_ONLY_ONE (1767) | Delta |
|-----------|-------------|-------------------|-------|
| **Lines** | 1939 | 1767 | +172 (+9.7%) |
| **d2_mult** | 4.0 | 2.5 | Tier-1 default **FLIPPED** (increase stdev threshold) |
| **h1On** | true | false | HTF Profile 1 **ENABLED** |
| **uh1_5, uh1_10** | false, false | true, true | HTF Profile 1 lower-tier bars **DISABLED** |
| **h2On** | true | false | HTF Profile 2 **ENABLED** |
| **h2From** | "2 Hour" | "3 Hour" | HTF Profile 2 start timeframe **LOWERED** |
| **Tier-1 Signal** | show_BullUSub | show_OmegaLongA | Signal type **DIFFERS** |

**Structural Assessment:**
- Roots/composites visible in input section appear identical to THE_ONLY_ONE (42 roots, 23 composites inferred)
- Extra 172 lines likely in Pipeline C signal detections or expanded composite logic
- HTF Profile enablement is a major calibration shift — changes which volume-rank tiers participate in HV+D decisions
- d2_mult increase (4.0 vs 2.5) requires a STRONGER displacement signal (5% stdev multiplier instead of 2.5%)

**Status:** Intermediate variant; appears to be a tuning variant with higher displacement thresholds and enabled HTF profiling.

---

### Variant B: HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine (2246 lines)

| Attribute | Variant 2246 | THE_ONLY_ONE (1767) | Delta |
|-----------|-------------|-------------------|-------|
| **Lines** | 2246 | 1767 | +479 (+27.1%) |
| **File Size** | 133 KB | (smaller) | **LARGEST** variant |
| **d2_mult** | 2.5 | 2.5 | Same (matches reference) |
| **h1On** | true | false | HTF Profile 1 **ENABLED** |
| **h1_5, h1_10** | false, false | true, true | HTF Profile 1 lower bars **DISABLED** |
| **h2On** | true | false | HTF Profile 2 **ENABLED** |
| **h2From** | "2 Hour" | "3 Hour" | HTF Profile 2 start **LOWERED** |
| **Tier-1 Signal** | show_OmegaLongA | show_OmegaLong | Omega variant **RENAMED** |

**Structural Assessment:**
- Roots/composites counts appear to match THE_ONLY_ONE (42 roots, 23 composites visible in inputs)
- Extra 479 lines are NOT in new named roots/composites — likely in Pipeline C expansion, state machines, or emission tables
- Candidates for expansion:
  - Additional RVOL tier detections (Pipeline C Engine 1)
  - Expanded emission table rows or logging (log.info streams, label.new metadata)
  - New state machine logic for advanced confluences (e.g., Combo Chain variants, Nagasaki co-detection)
  - Performance optimizations or caching
- **Positioning:** This appears to be the "production-ready" expanded version with all optional features enabled (HTF Profiles 1 & 2)

**Status:** Full-featured variant; likely intended for live trading with comprehensive signal coverage.

---

### Tier-1 Input Defaults — Summary Table

| Input | THE_ONLY_ONE | 1939 Variant | 2246 Variant | Impact |
|-------|-------------|-------------|-------------|--------|
| d2_mult | 2.5 | **4.0** | 2.5 | 1939 requires higher displacement; 2246 matches reference |
| h1On | false | **true** | **true** | 1939 & 2246 both enable HTF Profile 1 |
| h2On | false | **true** | **true** | 1939 & 2246 both enable HTF Profile 2 |
| h2From | "3 Hour" | **"2 Hour"** | **"2 Hour"** | 1939 & 2246 shift HTF Profile 2 start from 3H to 2H |
| uh1_5 / uh1_10 | true / true | **false / false** | **false / false** | 1939 & 2246 disable shortest HTF bars |

**Observation:** The 1939 and 2246 variants share the same HTF Profile strategy (enabled + modified tier selection) but diverge on d2_mult. The 2246 version "normalizes" back to THE_ONLY_ONE's d2_mult while keeping HTF changes.

---

### Plotshape Analysis — All Three Variants

All three hvd-pbj-ppd variants maintain **59 plotshapes** (no visual changes detected in spot checks).

---

## Family: vob-asym (Two Variants)

### Reference: VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine (1473 lines)

**Roots Count:** 25 (12 zone-creation + 12 T3 + 1 Nagasaki)  
**Composites Count:** 9  
**Engine:** Volume Order Block (VOB) with six-tier sensitivity ladder (A..F) + mutually-exclusive (MutEx) zone-line drawing

---

### Variant: VOB_Asym_T3x6_FROM_MASTERDIR_ummmm_2026-05-10.pine (1473 lines)

| Attribute | ummmm Variant | v8 Reference (2026-05-02) | Delta |
|-----------|---|---|---|
| **Lines** | 1473 | 1473 | **IDENTICAL** |
| **Title** | "Claude ummmm" | "Claude v8" | Suffix changed (development label?) |
| **Roots** | 25 (inferred same) | 25 | Same |
| **Composites** | 9 (inferred same) | 9 | Same |
| **Core Engine (f_vob)** | Identical | Identical | No logic changes |
| **MutEx Engine** | Identical | Identical | No logic changes |

**CRITICAL DELTA: Plotshape Definitions**

All 12 T3 buy/sell signals changed shape and/or location in ummmm vs v8:

#### T3 Buy Signals (Bullish)

| Signal | v8 Shape | v8 Location | ummmm Shape | ummmm Location | Delta |
|--------|----------|-------------|------------|------------|-------|
| T3a | circle | top | circle | **belowbar** | Location: top → belowbar |
| T3b | circle | abovebar | circle | **belowbar** | Location: abovebar → belowbar |
| T3c | circle | belowbar | circle | belowbar | (no change) |
| T3d | circle | bottom | circle | **belowbar** | Location: bottom → belowbar |
| T3e | **arrowdown** | abovebar | **circle** | **belowbar** | Shape: arrowdown → circle; Location: abovebar → belowbar; Size: huge → large |
| T3f | **arrowup** | belowbar | **circle** | belowbar | Shape: arrowup → circle; Size: huge → large |

#### T3 Sell Signals (Bearish)

| Signal | v8 Shape | v8 Location | ummmm Shape | ummmm Location | Delta |
|--------|----------|-------------|------------|------------|-------|
| T3a | xcross | top | **circle** | **abovebar** | Shape: xcross → circle; Location: top → abovebar |
| T3b | xcross | abovebar | **circle** | abovebar | Shape: xcross → circle; Location unchanged |
| T3c | xcross | belowbar | **circle** | **abovebar** | Shape: xcross → circle; Location: belowbar → abovebar |
| T3d | xcross | bottom | **circle** | **abovebar** | Shape: xcross → circle; Location: bottom → abovebar |
| T3e | cross | abovebar | **circle** | abovebar | Shape: cross → circle; Location unchanged |
| T3f | cross | belowbar | **circle** | **abovebar** | Shape: cross → circle; Location: belowbar → abovebar |

#### Unified Visual Pattern in ummmm

**Buy Signals (T3a..T3f):**
- All shapes → circle
- All locations → belowbar
- Size for T3e/T3f: huge → large

**Sell Signals (T3a..T3f):**
- All shapes → circle
- All locations → abovebar
- Sizes unchanged (or as specified)

**Summary:** ummmm flattens the v8 tier-specific visual hierarchy (mixed shapes and locations per tier) into a unified bull/bear binary (all buys below, all sells above, all circles).

---

## Structural Delta Summary by Family

### hvd-pbj-ppd Family

| Variant | Key Structural Delta | Assessment |
|---------|-------------------|------------|
| 1939 | +172 lines; d2_mult=4.0; h1On/h2On enabled; show_BullUSub visible | **Intermediate tuning variant** — higher displacement threshold + HTF profiling enabled |
| 2246 | +479 lines (133 KB); d2_mult=2.5; h1On/h2On enabled; show_OmegaLongA visible | **Full-featured production variant** — normalizes d2_mult but expands body code (likely Pipeline C + emission layers) |
| THE_ONLY_ONE | Reference (1767 lines) | **Reference streamlined build** — disabled HTF profiles, original d2_mult |

**Cross-Variant Relationship:**
- 2246 appears to be an evolved version of THE_ONLY_ONE with additional Pipeline C detections and enabled HTF profiling
- 1939 appears to be an alternative tuning path (higher displacement threshold) but also enables HTF profiles
- None should be labeled "canonical" — all are variants of the same root architecture

---

### vob-asym Family

| Variant | Key Structural Delta | Assessment |
|---------|-------------------|------------|
| ummmm | Identical line count/logic; plotshapes unified (all circles, bull→belowbar, bear→abovebar) | **UI/UX simplification variant** — zero logic changes, pure visual refactoring |
| v8 | Reference with tier-specific plotshape visual hierarchy | **Reference detailed-feedback variant** — mixed shapes (arrows, crosses) per tier for visual differentiation |

**Cross-Variant Relationship:**
- ummmm and v8 are functionally identical — no signal logic changes
- The ummmm title ("Claude ummmm") suggests work-in-progress or placeholder naming
- Suggests ummmm is either (1) a UI refinement iteration, or (2) a development checkpoint

---

## Uncertain Items & TradingView Verification Checklist

### HVD-PBJ-PPD Family

| Item | Severity | Action Required |
|------|----------|-----------------|
| 1939: d2_mult=4.0 vs. 2246/THE_ONLY_ONE=2.5 | HIGH | Verify on TradingView which default is user's current calibration (does 4.0 produce better HV+D filters?) |
| 1939: show_BullUSub visible but THE_ONLY_ONE shows show_OmegaLongA | HIGH | Clarify whether these are mutually exclusive or renamed. Are they in the same slot in Tier-1 inputs? |
| 2246: 479-line delta but same visible root/composite count | HIGH | Run full diff(THE_ONLY_ONE, 2246) to identify new Pipeline C detections, state machines, or emission logic |
| HTF Profile defaults (h1On/h2On=true in 1939 & 2246 vs. false in THE_ONLY_ONE) | MEDIUM | Is THE_ONLY_ONE canonical ("streamlined reference"), or are 1939/2246 the intended production builds with HTF enabled? |
| All three variants show identical Tier-1 composite roots (Floor, Rooftop, HW, SUPER, SD Bull/Bear) | INFO | Confirms architectural parity; differences are in inputs and body expansion, not root set |

### VOB-Asym Family

| Item | Severity | Action Required |
|------|----------|-----------------|
| ummmm plotshapes unified vs. v8 tier-specific | MEDIUM | Verify on TradingView which visual design is correct/intended. Does unified shape reduce trader usability? |
| "Claude ummmm" title placeholder | MEDIUM | Confirm final naming. Is this a development label or user-facing version name? |
| Zero logic delta between ummmm and v8 | INFO | Confirms that all 1473 lines are shared logic; only visual layer differs |

---

## File Locations (Output Extract YAMLs)

- `/Users/anishpatel/code/indicators/bible-input/extract-hvd-pbj-ppd-1939-masterdir.yaml`
- `/Users/anishpatel/code/indicators/bible-input/extract-hvd-pbj-ppd-2246-masterdir.yaml`
- `/Users/anishpatel/code/indicators/bible-input/extract-vob-asym-ummmm-masterdir.yaml`

---

## Recommendations

1. **Do not label any variant as canonical.** All three hvd-pbj-ppd variants are valid siblings; TradingView live testing will determine which calibration suits the user's strategy.

2. **For hvd-pbj-ppd 2246:** Run `diff -u <(sed -n '1,1767p' THE_ONLY_ONE.pine) <(sed -n '1,1767p' 2246.pine)` followed by `diff -u <(tail -n +1768 THE_ONLY_ONE.pine) <(tail -n +1768 2246.pine)` to isolate the 479-line delta and identify new composite logic.

3. **For vob-asym ummmm:** Verify the plotshape unification on TradingView (live chart comparison between v8 and ummmm). If traders rely on tier-specific arrows/crosses for visual cues, this is a usability regression.

4. **TradingView Verification Priority:**
   - Load all four variants side-by-side on the same chart/timeframe
   - Compare alert firing frequency and timing
   - Compare visual marker placement (especially for vob-asym)
   - Document any signal count or timing differences

---

## Audit Metadata

| Field | Value |
|-------|-------|
| **Audit Date** | 2026-05-10 |
| **Ingestion Source** | Master Directory (iCloud sync) |
| **Total Variants Analyzed** | 4 (3 hvd-pbj-ppd + 1 vob-asym) |
| **Total Roots Identified** | 42 (hvd-pbj-ppd) + 25 (vob-asym) |
| **Total Composites Identified** | 23 (hvd-pbj-ppd) + 9 (vob-asym) |
| **Plotshape Deltas Detected** | 12 (vob-asym ummmm vs v8) |
| **Tier-1 Input Deltas Detected** | 5 (hvd-pbj-ppd d2_mult, h1On, h2On, h2From, signal type) |
