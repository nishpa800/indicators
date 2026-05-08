# Squarify — Changelog

Newest first. Each version = one file in `versions/`.

---

## v3 VERIFY — 2026-05-08 — RETRACTED (over Pine plot limit)
**File:** DELETED. v3 hit 147 plot calls (46 main + 2 OPENING CONFLU + ~99 atom plotshapes). Pine v5 hard limit is 64 total plot* calls per indicator (plot, plotshape, plotchar, plotcandle, plotbar, plotarrow, bgcolor, fill, hline). The script would not compile on TradingView.

**Lesson:** atom plots cannot be added to SQUARIFY itself within the plot budget. Next attempt: separate `SQUARIFY_ATOMS_*.pine` indicator file(s) — either (a) split atoms across multiple <64-plot files, or (b) use `label.new()` for atoms (which doesn't count toward the 64-plot limit; bounded by max_labels_count=500 instead). Pending design review with Anish.

**Net effect:** v2 remains the production indicator. No usable v3 file at this revision.

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
