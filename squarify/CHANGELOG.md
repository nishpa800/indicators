# Squarify — Changelog

Newest first. Each version = one file in `versions/`.

---

## ATOMS v1 — 2026-05-08 (Tier 0 atomics, separate companion indicator)
**File:** `versions/SQUARIFY_ATOMS_v1.pine` (2524 lines, 60 atomic plots — fits under Pine's 64 cap).

**Purpose:** companion verification indicator. Load alongside SQUARIFY v2 on the same chart. v2 carries the 46 production combo plots + alerts; ATOMS v1 carries 60 individual Tier 0 atomic plots so each atomic SKU can be visually cross-checked against the original-source indicator (RVOL, FAUNA, B2B PUP, TNT OD, etc.) on a second chart pane.

**Method:** v2 source copied byte-for-byte through line 2217 (engines + signal-definition section). Lines 2218→end (46 main plotshapes, alert aggregator, stats engine, T1/T2 OPENING CONFLU plotshapes + alerts) STRIPPED. Indicator name set to `SQUARIFY ATOMS v1`. Header note replaced. Then appended:

1. `★ ATOMIC PLOTS — VERIFY ★` input group with 60 toggles, all default FALSE, every toggle has a `tooltip=` argument with its precise atomic definition (click the (i) icon next to any toggle in the input panel).
2. 60 atomic plotshapes — small subtle markers (size.tiny / size.small).
3. **Atom-fire logger** — one `log.info(...)` per confirmed bar listing every firing atom on that bar. Format: `ATOM_FIRE|TICKER=...|TF=...|TIME=...|BAR=...|FIRES=name1 + name2 + ...`. Read via `mcp__tradingview__pine_get_console` for automated cross-check vs original-source indicators. Logger fires INDEPENDENTLY of plot toggles — every atom is logged whether visually plotted or not, so verification scans don't depend on which toggles Anish has on.

**60 atoms exposed (Tier 0 only — combinations and Tier 1+ NOT included):**
- HV ranks (M3, [1] offset): HV50/75/100/150/200/250/300/350/400/450/500/550/600/650/700/750/1000 + HEV (18)
- RVOL price-spike: SAAB, Kratos, RVOL1x bull/bear, GrandSlam, MOAB (6)
- RVOL cumulative: WTC, Hiroshima, Pentagon (3)
- All-time vol: Nagasaki (1)
- FAUNA Bull/Bear (2) — synthesized after exclusions
- Displacement: sigDISPBull/Bear (FVG, offset -1), disp5_bull/bear (no FVG, offset 0) (4)
- FVG events: gz_bullGZI/bearGZI, gz_bullHV/bearHV (4)
- PUP/PPD (2)
- PBJ/PB Bull/Bear (4)
- Ping-Pong: bull_pp, bear_pp (2)
- U streak qualifier: u_qual_bull/bear (2)
- Matrix Number: is_matrix_number (1)
- Long/Short: L1, L2, S1, S2 (4)
- Boom Hunter: bh_anyOmega (1)
- TNT atomics: raw_bullTNT/bearTNT, raw_napalmBull/Bear, raw_bullCharge/bearCharge (6)

**Why these are the atoms (and not the others):** atomic = single-engine output, no dependency on other detection plots. Tier 1 (HV+D fire = HV ∩ D, det_*NapalmCons = napalm ∪ charge) and Tier 2 (combo sets, FVG/MAT/UC, Floor/2F/Roof/Pent RAW, HW, Foxtrot, F2/E3/FC, B2B PUP/Napalm) are COMBINATIONS of these 60. They're verifiable on screen once the underlying atoms are confirmed correct.

**Plot count:** 60 active. v2 carries 48 (46 main + 2 OPENING CONFLU). Loaded together: 60 + 48 = 108, but they're separate indicators so each compiles under the 64 cap independently.

**Automated cross-check workflow:** see `~/.claude/projects/-Users-anishpatel/memory/SKU_VERIFICATION_AUTOMATION.md`.

---

## v3 VERIFY — 2026-05-08 — RETRACTED (over Pine plot limit)
**File:** DELETED. v3 hit 147 plot calls. Pine v5 hard cap is 64 total plot* calls per indicator. Replaced by ATOMS v1 (above) as a separate companion indicator.

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
