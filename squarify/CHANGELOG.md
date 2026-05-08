# Squarify — Changelog

Newest first. Each version = one file in `versions/`.

---

## v3 VERIFY — 2026-05-08 (verification mode — additive only, no logic change)
**File:** `versions/SQUARIFY_v3_VERIFY_2026-05-08.pine` (2935 lines, 46 main plots + ~80 atomic plots)

**Purpose:** bottom-up verification. v2 reads the same engines; v3 adds individual ATOMIC DETECTION PLOTS so each atomic SKU can be visually cross-checked against the original-source indicator (RVOL, FAUNA, B2B PUP, TNT OD, etc.) on a second chart. Same-candle alignment = atomic verified.

**Method:** v2 source copied byte-for-byte. Then:
1. Indicator name updated to `SQUARIFY v3 VERIFY` (`shorttitle="SQ46v3"`).
2. Header note added explaining the additive nature + Floor/2F/Roof/Penthouse RAW definitions (so they don't drift again).
3. New `★ ATOMIC PLOTS — VERIFY ★` input group added at the bottom of the inputs panel — ~80 toggle inputs, ALL DEFAULT FALSE.
4. ~80 new `plotshape()` calls after the existing 46 main plots — each gated by `_masterGate AND a_<name> AND <atomic-variable>`. Visual styling small/subtle (size.tiny / size.small) to avoid clutter when toggled on.

**Atoms exposed (alphabetical within group):**
- HV ranks (M3 — describe bar[1]): HV50/75/100/150/200/250/300/350/400/450/500/550/600/650/700/750/1000 + HEV.
- RVOL price-spike: SAAB, Kratos, RVOL1x bull/bear, GrandSlam, MOAB.
- RVOL cumulative: WTC, Hiroshima, Pentagon.
- All-time vol: Nagasaki.
- PBJ/PB: Bull/Bear PBJ, Bull/Bear PB.
- PUP/PPD.
- FAUNA Bull/Bear (synthesized after exclusions).
- Displacement: sigDISPBull/Bear (FVG-confirmed, offset -1), disp5_bull/bear (5x std no-FVG, offset 0).
- FVG events: gz_bullGZI/bearGZI, gz_bullHV/bearHV.
- Matrix: is_matrix_number raw, sigNeoBull/Bear, sigTrinityBull/Bear.
- Long/Short: L1, L2, S1, S2.
- U streak qualifier: u_qual_bull/bear.
- Ping-Pong: bull_pp, bear_pp.
- Boom Hunter: bh_anyOmega.
- TNT engine: raw_bullTNT/bearTNT, raw_napalmBull/Bear, raw_bullCharge/bearCharge.
- TIER 1: hvd_fire_bull/bear, det_bullNapalmCons / det_bearNapalmCons.
- TIER 2: comboSet1-4 Bull/Bear, FVG COMBO (csNew1) Bull/Bear, MAT COMBO (csNew2) Bull/Bear, UNIFIED COMBO (csNew3) Bull/Bear.
- TIER 2 RAW Floor / 2F / Rooftop / Penthouse (anyBullFloor / anyBull2nd / anyBearRoof / anyBearPent — RAW, no oneOfThese gate, no checkbox).
- TIER 2: HW raw, Foxtrot Bull/Bear, F2 Bull/Bear, E3 Bull/Bear, FAUNA Cluster Bull/Bear, B2B PUP, B2B Napalm Bull/Bear.

**Floor / 2F / Roof / Penthouse — frozen definitions:**
- `Floor RAW   = bull_pp AND sigBullPBJ AND bull_hw_slot`
- `2F RAW      = bull_pp AND sigBullPB  AND bull_hw_slot`
- `Roof RAW    = bear_pp AND sigBearPBJ AND bear_hw_slot`
- `Pent RAW    = bear_pp AND sigBearPB  AND bear_hw_slot`
- `bull_hw_slot = sigBullRVOL1x OR sigGrandSlam OR sigWTC OR sigHiroshima OR (sigNagasaki AND nag_dir_bull)`
- `bear_hw_slot = sigBearRVOL1x OR sigMOAB     OR sigWTC OR sigHiroshima OR (sigNagasaki AND nag_dir_bear)`
- Plotted FLOOR (#4) and 2F (#5) wrap RAW with `oneOfThese` confluence gate AND `cb1_pass_floor` / `cb1_pass` checkbox set.

**Logic preserved:** v2's 46 plots, alert aggregator, stats engine, Tier 1/2 OPENING CONFLUENCE alerts — ZERO behavioral changes. The 4 offset bugs from `SQ46_v2_AUDIT_2026-05-08.md` (signals 31, 39, 41, 42) are NOT fixed in v3 — that's a separate change pending Anish's go-ahead.

**Removal plan:** v3 atom plots are temporary. Once verification is complete, atoms get folded back out (revert to v2 logic) or kept for production diagnostics — Anish's call.

---

## v2 — 2026-05-04 (current)
**File:** `versions/SQUARIFY_v2.pine` (2398 lines, 46 plots)

**Triggers:**
- User noticed Super / SDuper never firing
- Audit found Napalm bug (used `raw_napalmBull` instead of consolidated NPM)
- 18 plots overlap with B2B PUP indicator → cleanup
- WMD → WBUSH upgrade per Anish's spec

**Changes from v1:**

1. **Napalm bug fix.** v1 used `raw_napalmBull/Bear` (raw napalm only) in 19+ detection plots — silent under-firing because Charge events weren't counted as Napalm. v2 uses `det_bull/bearNapalmCons` (= raw_napalm OR raw_Charge). Same bug pattern as B2B PUP v4.32 fix, except in Squarify the charge ladder push WAS already present; it was the consolidation that wasn't being used.

2. **SUPER + SDUPER redefined** per Anish (old "perfect-storm" definitions never fired):
   - **SUPER** = UC (Unified Combo, csNew3) + Napalm (consolidated NPM)
   - **SDUPER** = UC + Napalm + PUP

3. **UC NAGASAKI added.** New plots #45 (Bull) and #46 (Bear). Definition: Unified Combo (csNew3) + Nagasaki on same visual bar. Offset = -1.

4. **WMD ripped out, replaced by WBUSH.** New plots #41 (Bull), #42 (Bear), #43 (Neutral). WBUSH = HEAVY PENTAGON's 5 Heavy Combo families (Yin-Yang, Nagasaki, Nagasaki Vol, Trident, Neutral Heavy x2) × 3 directions = 15 sub-signals OR'd by direction. Direction classification follows displacement engine. `sigWMD` aliased to `sig_WBUSH_Bull` for backward-compat in internal references.

5. **CO restructured.** Now requires UC OR FVG Combo Set (`csNew3 OR csNew1`) instead of broad `use_any_bull[1]` gate. CO no longer fires on any random bullish signal — must be UC or FVG combo set.

6. **UU / UUU / UUUU + new path pG.** Counts distinct qualifier types in streak from {PBJ, DISP, FAUNA, SAAB, RVOL1x, GS}. UU=2, UUU=3, UUUU=4. Qualifiers can stack on same bar. ORs into existing pA/pB/pC/pD/pE/pF — additive. Same definition as TNT OD v2 (except Squarify also has pD = HV+D path since it has the HV+D engine).

7. **22 signals removed:**
   - **Reserved:** en_25, en_40
   - **B2B PUP overlaps** (kept GOLF — distinct 3-bar pattern): en_14 (B2B+F+D), en_15 (B2B+F), en_16 (B2B+D), en_17 (B2B+SAAB), en_18 (B2B), en_19 (B2B+PBJ), en_20 (UC+B2B), en_21 (CC+B2B), en_22 (UU+B2B), en_23 (NPM²+B2B), en_24 (B2B+TNT/NPM), en_26 (CONT+B2B), en_27 (HVD+PBJ+B2B), en_31 (F2CL+B2B), en_32 (B2B+F2), en_57 (B2B+NPM+PBJ), en_58 (B2B+F2E3), en_62 (L1²+B2B)
   - **CONT:** en_59 (per Anish — overlaps TNT OD's CONT)
   - **WMD:** en_61 (replaced by WBUSH)
   - **WMD+BULL:** en_64 (covered by WBUSH+ANY)

8. **Renumbered 1-46 contiguously.** No reserved IDs, no gaps in user-facing labels.

9. **Tooltips updated** to reflect new definitions.

**Plot count:** 46 / 64 limit.
**Indicator title:** "SQUARIFY 46 v2", short title "SQ46 v2".

---

## v1 — pasted 2026-05-04 baseline
**File:** `versions/SQUARIFY_v1.pine` (2319 lines, 64 plots)
**Source:** Anish's Squarify 5.4.523am.txt. Original 64-plot aggregator.
