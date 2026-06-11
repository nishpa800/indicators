# Heavy Weapons ULTRA — DETECTION PLOT INVENTORY

**File audited:** `versions/HEAVY_WEAPONS_ULTRA_v1.pine`
**Total `plotshape` detections:** 28 (of TradingView's 64-plot cap)

## How "direction" and "confirm 100%" are established
- **Code-confirmable (✅100%):** the plot's boolean traces directly to candle geometry
  (`close>open`, FVG gap direction) or to an already-directional signal (`sigAddLong*`,
  `sigAddShort*`). No ambiguity.
- **Source-confirmable (✅canon):** the engine is ported from another study in this repo;
  direction verified by diffing against that canonical source.
  - HV+D / HVD+PBJ → `hvd-pbj-ppd/versions/HVD_PBJ_PPD_BULLISH_v1.pine` (FVG logic byte-identical).
  - CS1/CS2 → GZI/HV-FVG (bull-only port). PUP → Anish PUP (bull-only).
- **Neutral:** directionless by construction (volume-rank events, PBJ pocket-pivot gate,
  Nagasaki ATH-volume). Carries no bull/bear claim.

> **Offset note:** `offset=-1` plots render one bar back — they *describe the prior candle*
> (HV+D / HV-tier / CS / Long+HV / HVD+PBJ are offset-aligned).

---

## A. COMPOSITE detections

| # | Plot (title) | Dir | Visual-plot gate | Alert gate | Direction basis | Confirm |
|--|--|--|--|--|--|--|
| 1 | `PBJ+Any` | **Neutral** | `show_PBJplusAny and pbjAnyFired` | TIER 1, suppressed when B2B fires | PBJ pocket-pivot + ANY listed signal (bull+bear mixed in co-list) | ✅100% (neutral by design) |
| 2 | `B2B PBJ+Any` | **Neutral** | `show_B2B_PBJplusAny and b2bPbjAnyFired` | TIER 1 | `pbjAnyFired and pbjAnyFired[1]` (2 consec) | ✅100% |
| 3 | `PBJ+Long` | **Bull** | `show_PBJplusLong and pbjLongFired` | TIER 1 | `effBullPBJ_onBar` + any `sigAddLong1..5` | ✅100% |
| 4 | `PBJ+Short+HV` | **Bear** | `show_PBJplusShortHV and pbjShortHVFired` | TIER 1 | `effBearPBJ_onBar` + Short1/2 + HV500/1K | ✅100% |
| 5 | `Long+HV` (off −1) | **Bull** | `show_LongPlusHV and longHVFired` | TIER 3 | `anyLong[1]` on the HV500/1K candle | ✅100% |
| 6 | `HVD+PBJ+Any` (off −1) | **Mixed⚠** | `show_HVDplusPBJany and hvdpbjAnyFired` | TIER 2 | `hvdpbj_bull OR hvdpbj_bear` — **one purple diamond for BOTH dirs** | ⚠ dir in alert text only, not on marker |
| 7 | `HV+D+Any` (off −1) | **Mixed⚠** | `show_HVplusDany and hvdAnyFired` | TIER 2 | `hvd_bull OR hvd_bear` — **always green ▲, even on bear** | 🐞 **BUG: bear renders bullish marker** |
| 8 | `Nagasaki` | **Neutral** | `nagStandFired` (⚠ no toggle) | TIER 0 | ATH volume; lists co-firers | ✅100% (neutral) |
| 9 | `Nag+Strong` | **Mixed** | `show_NagStrong and nagStrongFired` | TIER 0 | Nagasaki + strong set (GS/Long=bull, MOAB=bear, WTC/Hiro/HV1000=neutral) | ⚠ mixed — no single dir |
| 10 | `Nag+HV+D` (off −1) | **Bull** | `show_NagStrong and nagHVD` | TIER 0 | `hvd_bull and sigNagasaki[1]` (bull-only) | ✅canon |
| 11 | `HV+D Bull` (off −1) | **Bull** | `hvd_bull` (⚠ no toggle) | TIER 6 (if `not hvdAnyFired`) | `base_hv_hit and d1_bull` (gap-UP FVG) | ✅canon (byte-identical) |
| 12 | `HV+D Bear` (off −1) | **Bear** | `hvd_bear` (⚠ no toggle) | TIER 6 | `base_hv_hit and d1_bear` (gap-DOWN FVG) | ✅canon |
| 13 | `HVD+PBJ Bull` (off −1) | **Bull** | `hvdpbj_bull` (⚠ no toggle) | TIER 6 (if `not hvdpbjAnyFired`) | `hvd_bull and sigBullPBJ[1]` | ✅canon |
| 14 | `HVD+PBJ Bear` (off −1) | **Bear** | `hvdpbj_bear` (⚠ no toggle) | TIER 6 | `hvd_bear and sigBearPBJ[1]` | ✅canon |

## B. CONDITIONAL detections

| # | Plot (title) | Dir | Visual-plot gate | Alert gate | Direction basis | Confirm |
|--|--|--|--|--|--|--|
| 15 | `LONG 1` | **Bull** | `show_Long1 and sigAddLong1` | TIER 4 | `hybMom1 and close>open` (now Hiroshima-derived) | ✅100% |
| 16 | `LONG 2` | **Bull** | `show_Long2 and sigAddLong2` | TIER 4 | `hybMom2 and close>open` | ✅100% |
| 17 | `LONG 3` | **Bull** | `show_Long3 and sigAddLong3 and curBarHasHV500or1K` | TIER 5 | `hybMom3 and close>open` + HV500/1K same bar | ✅100% |
| 18 | `LONG 4` | **Bull** | `show_Long4 and sigAddLong4 and curBarHasHV500or1K` | TIER 5 | `hybMom4 and close>open` + HV | ✅100% |
| 19 | `LONG 5` | **Bull** | `show_Long5 and sigAddLong5 and curBarHasHV500or1K` | TIER 5 | `hybMom5 and close>open` + HV | ✅100% |
| 20 | `HV 1000` (off −1) | **Neutral** | `plot_HV1000 and anyLongOnPrev` | ❌ none standalone (co-list only) | highest vol in 1000 bars | ✅100% (neutral) |
| 21 | `HV 500` (off −1) | **Neutral** | `plot_HV500 and anyLongOnPrev` | ❌ none standalone | highest vol in 500 | ✅100% |
| 22 | `HV 250` (off −1) | **Neutral** | `plot_HV250 and pbjOn2` | ❌ none standalone | highest vol in 250 | ✅100% |
| 23 | `HV 150` (off −1) | **Neutral** | `plot_HV150 and pbjOn2` | ❌ none standalone | highest vol in 150 | ✅100% |
| 24 | `HV 75` (off −1) | **Neutral** | `plot_HV75 and pbjOn2` | ❌ none standalone | highest vol in 75 | ✅100% |
| 25 | `CS1 Bull` (off −1) | **Bull** | `show_CS1Bull and sigCS1Bull` | ❌ none standalone (PBJ+Any/HV+D co-list only) | GZI/HV bull-FVG + Std-RVOL[1] | ✅canon (bull-only port) |
| 26 | `CS2 Bull` (off −1) | **Bull** | `show_CS2Bull and sigCS2Bull` | ❌ none standalone | GZI/HV bull-FVG + Reg@Time[1] | ✅canon |
| 27 | `CS1+CS2 Bull` (off −1) | **Bull** | `show_CS12Bull and sigCS12Bull` | ❌ none standalone | CS1 and CS2 same bar | ✅canon |
| 28 | `PUP` | **Bull** | `show_PUP and sigPUP` | ❌ none standalone (co-list only) | pocket-pivot up + EMA stack + vol>red | ✅canon (bull-only) |

---

## C. SUSPECTED BUGS / CORRECTNESS GAPS (for your review — NOT yet changed)

1. **🐞 `HV+D+Any` (#7) draws a green ▲ bullish marker even when the event is `hvd_bear`.**
   `hvdAnyFired = hvd_bull or hvd_bear`, but the single `plotshape` is hard-coded
   `style=shape.triangleup, color=#00E676`. **This is the "HV+D shown bullish when bearish."**
   Fix = split into bull/bear plots (▲ green below / ▼ red above), like the standalone HV+D does.
2. **⚠ `HVD+PBJ+Any` (#6)** same collapse — one purple diamond below bar for both directions.
3. **⚠ No toggle** on #8 `Nagasaki`, #11–14 `HV+D`/`HVD+PBJ` standalones — they always plot
   (can't be turned off independently).
4. **❌ No standalone alert** for HV tiers (#20–24), CS1/2/12 (#25–27), PUP (#28). A lone PUP or
   CS1 **plots but never alerts** unless PBJ / HV+D / Nagasaki coincide. If you want a
   non-repainting alert for *every* detection, these need their own alert lines.
5. **`Nag+Strong` (#9)** mixes bull (GS/Long), bear (MOAB), neutral (WTC/Hiro/HV1000) under one
   marker — direction is not determinable from the plot alone.

## D. Direction verification method (how I confirm 100%)
- Bull/Bear from candle geometry → trace to `close>open` / FVG gap inequality. **Exact.**
- Ported engines (HV+D, HVD+PBJ, CS1/2, PUP) → diff against the canonical repo source; HV+D FVG
  logic confirmed byte-identical to `HVD_PBJ_PPD_BULLISH_v1`.
- Neutral → confirmed directionless (volume rank / pocket-pivot gate / ATH volume).
