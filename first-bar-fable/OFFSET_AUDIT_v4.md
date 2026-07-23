# FIRST BAR FABLE v4 — DETECTION PLOT OFFSET AUDIT

Vocabulary: `bar[N]` only. **det bar** = the bar on which the boolean evaluates
true at close. **Visual/anchor bar** = the bar the shape must sit on. **Offset**
= plotshape/label offset that moves the shape from det bar[0] to the anchor bar.
Doctrine: *back-to-back = the VISUAL plots are back-to-back; a detection whose
event happened on det bar[1] is a -1 visual.*

Verified adversarially: every row below was independently re-derived by 3
verification lenses (pure code trace / companion-source parity / refuter) —
see CHANGELOG "Audit". Verdicts marked ✅ CONFIRMED, 🔧 FIXED-IN-v4, 🚩 FLAG.

## S1–S17 (v1 rows)

| Row | Legs → bar[N] | Anchor | Offset | FB gate | Verdict |
|---|---|---|---|---|---|
| S1 Bull RVOL1X/GS+D9+PBJ | RVOL tier[0], d9_bull[0], PBJ[0] | bar[0] | 0 | fb0 | ✅ |
| S2 Bear RVOL1X/MOAB+D9+PBJ | RVOL tier[0], d9_bear[0], PBJ[0] | bar[0] | 0 | fb0 | ✅ |
| S3 Typhoon Bull | pivot = bar[yyR]; FAUNA/PUP/Whale/PBJ/first-bar all read [yyR] | pivot bar | -yy_rightBars | fbs = sess[yyR] | ✅ |
| S4 Typhoon Bear | same, bear legs | pivot bar | -yy_rightBars | fbs | ✅ |
| S5 Musashi Bull | aligned PUP/Whale/PBJ read [moff]; GZ FVG legs raw [0] (fauna asymmetry, documented) | bar[moff] | -moff | fbm = sess[moff] | ✅ |
| S6 Musashi Bear | same, bear legs | bar[moff] | -moff | fbm | ✅ |
| S7 Whale+PUP Bull | pivot/HV/PUP/PBJ all [0] | bar[0] | 0 | fb0 | ✅ |
| S8 Whale+PPD Bear | all [0] | bar[0] | 0 | fb0 | ✅ |
| S9 B2B KRATOS+D9 | PPD pair [0],[1]; RVOL both bars; d9 on [0] or [1] | bar[0] (2nd pattern bar) | 0 | fb01 (pair touch) | ✅ |
| S10 B2B SAAB+D9 | PUP pair [0],[1] | bar[0] | 0 | fb01 | ✅ |
| S11 Dynamite Bull | disp bars [1],[2]; FAUNA [1],[2]; FVG completes [0] | bar[1] (2nd disp bar) | -1 (TNT OD v3 parity) | fb1 | ✅ offset · 🚩 gate: pair=[1],[2], pair-touch law ⇒ fb12; fb1 = v2/source behavior, unchanged |
| S12 Dynamite Bear | same, bear | bar[1] | -1 | fb1 | ✅ offset · 🚩 gate (same) |
| S13 Ignite Bull T+C | TNT[0]+CONT[0] | bar[0] | 0 | fb0 | ✅ |
| S13 Ignite Bull N+C | NPM event [1], CONT[1] | bar[1] | -1 | fb1 | ✅ |
| S14 Ignite Bear T+C / N+C | same, bear | bar[0] / bar[1] | 0 / -1 | fb0 / fb1 | ✅ |
| S15 Nagasaki 1stBar+ | NAG[0] + qualifier[0], first-bar baked | bar[0] | 0 | fb0 (+baked) | ✅ |
| S16 B2B Napalm Bull | NapCons det [0],[1]; each event = det−1 ⇒ **visual pair [1],[2]** | bar[1] (2nd visual) | **-1** (v3 had 0 — wrong) | **fb12** (v3 had fb01) | 🔧 FIXED |
| S17 B2B Napalm Bear | same, bear | bar[1] | **-1** | **fb12** | 🔧 FIXED |

## S18–S27 (v2 rows)

| Row | Legs → bar[N] | Anchor | Offset | FB gate | Verdict |
|---|---|---|---|---|---|
| S18 B2B PUP+D9 | PUP pair [0],[1] (PUP = same-bar visual); d9 on [0] or [1] | bar[0] | 0 | fb01 | ✅ |
| S19 B2B PPD+D9 | PPD pair [0],[1] | bar[0] | 0 | fb01 | ✅ |
| S20 B2B FC Bull | FC pair [0],[1] (FC = same-bar visual) | bar[0] | 0 | NONE (override, documented) | ✅ |
| S21 B2B FC Bear | same | bar[0] | 0 | NONE | ✅ |
| S22 D9 Bull Study | d9[0], RVOL[0], HV[0] | bar[0] | 0 | fb0 | ✅ |
| S23 D9 Bear Study | same | bar[0] | 0 | fb0 | ✅ |
| S24 UC Bull+D9 | csNew3[0] is a **-1 visual** (HVD source plots CS3 at offset=-1) ⇒ UC visual = bar[1]; d9 leg is [0] (det-time) | UC visual bar[1] | -1 (HVD parity) | fb1 | ✅ |
| S25 UC Bear+D9 | same | bar[1] | -1 | fb1 | ✅ |
| S26 ENR B2B same-bar | TNT ENR visual [0] + NPM ENR visual [1] | bar[0] | 0 | fb01 | ✅ |
| S26 ENR B2B tnt-first | TNT visual [2] + NPM visual [1] | bar[1] | -1 | fb12 | ✅ |
| S27 (both cases) | same, bear | bar[0]/bar[1] | 0 / -1 | fb01 / fb12 | ✅ |

## HVD groups (all offset -1)

`hvd_fire_*` det bar[0] ⇒ **event bar[1]**: the rolling-HV bar (`volume[1] ==
highest[1]` tiers / HEV) that is ALSO the displacement bar (`d1_rng[1] >
d1_thresh[1]`), FVG-completed by bar[0].

| Row | Legs → bar[N] | Anchor | Offset | FB gate | Verdict |
|---|---|---|---|---|---|
| CO HV+D+PBJ+USE Bull / Bear | HVD event [1] + PBJ[1] + USE[1] | bar[1] | -1 | fb1 | ✅ |
| CO HV+D+PB+USE Bull / Bear | HVD event [1] + PB[1] + USE[1] | bar[1] | -1 | fb1 | ✅ |
| B2B HV+D Bull / Bear (no PB) | HVD det [0],[1] ⇒ visual pair [1],[2] | bar[1] (2nd visual) | -1 | fb1 | ✅ offset · 🚩 gate: pair-touch law ⇒ fb12; fb1 = v2 behavior, unchanged |
| B2B HV+D+PBJ Bull / Bear | pair [1],[2] + PBJ on [1] or [2] | bar[1] | -1 | fb1 | ✅ offset · 🚩 gate (same) |
| B2B HV+D+PB Bull / Bear | pair [1],[2] + PB on [1] or [2], PBJ absent | bar[1] | -1 | fb1 | ✅ offset · 🚩 gate (same) |
| HVD+PUP Bull / HVD+PPD Bear | event [1] + PUP/PPD[1] + **PBJ[1] ABSENT** | bar[1] | -1 | fb1 | ✅ |
| HVD+RVOL Bull / Bear | event [1] + RVOL1x-GS/MOAB[1] + PBJ absent | bar[1] | -1 | fb1 | ✅ |
| HVD+CMB Bull / Bear | event [1] + csNew3[0] (**UC = -1 visual ⇒ lands on bar[1]** — verbatim HVD source `_m_cb1b = csNew3_Bull`) + PBJ absent | bar[1] | -1 | fb1 | ✅ |
| HVD+PBJ+PUP / +PPD | event [1] + PBJ[1] + PUP/PPD[1], suppressed by 2of3_raw | bar[1] | -1 | fb1 | ✅ |
| HVD+PBJ+RVOL Bull / Bear | event [1] + PBJ[1] + RVOL[1], suppressed by 2of3_raw | bar[1] | -1 | fb1 | ✅ |
| HVD+PBJ+CMB Bull / Bear | event [1] + PBJ[1] + CMB, suppressed by 2of3_raw | bar[1] | -1 | fb1 | ✅ |
| HV+D+PBJ 2of3 Bull / Bear | event [1] + **PBJ[1] REQUIRED** + ≥2 of {PUP/PPD[1], RVOL[1], CMB}; suppressed by 3of3 | bar[1] | -1 | fb1 | ✅ |
| HV+D+PBJ 3of3 Bull / Bear | event [1] + PBJ[1] + all 3 legs | bar[1] | -1 | fb1 | ✅ |

**Adjudication of the operator's observed case** (HVD+CMB Bear + HVD+PPD Bear
fired, 2of3 Bear silent): the two fired rows are the **no-PBJ** variants — each
requires `not sigBearPBJ[1]`. The 2of3 row requires `sigBearPBJ[1]` **present**.
Two triangles co-firing therefore *proves* PBJ was absent, and 2of3 is
definitionally impossible on that bar. Working as coded — and as coded in the
HVD source. The rows' full names are "HV+D+**PBJ** 2of3 / 3of3"; v4 tooltips now
spell the PBJ requirement out.

## S28–S35 (v3 label rows) and S36–S39 (v4)

| Row | Legs → bar[N] | Anchor | Offset | FB gate | Verdict |
|---|---|---|---|---|---|
| S28/S29 4K+ANY | HV4K[0] + ANY union[0] (det-time union, documented) | bar[0] | 0 | fb0 | ✅ |
| S30/S31 NAG+ANY | NAG[0] + ANY[0] | bar[0] | 0 | fb0 | ✅ |
| S32/S33 OPEN1±+ANY | opener[0] (first-bar baked) + ANY[0] | bar[0] | 0 | baked | ✅ |
| S34/S35 DYN+ANY | dynamite event [1] + ANY[0] | bar[1] | -1 (`bar_index-1` label) | fb1 | ✅ |
| S36/S37 PBJ+D9+HV3K/NAG | PBJ[0] + d9[0] + (HV3K[0] or NAG[0]) | bar[0] | 0 | fb0 | ✅ |
| S38 Swing Low+ANY FABLE | pivot = bar[swR]; ANY FABLE read [swR] | pivot bar | -sw_rightBars | fbsw = sess[swR] | ✅ |
| S39 Swing High+ANY FABLE | same | pivot bar | -sw_rightBars | fbsw | ✅ |

## Flags (behavior deliberately unchanged — operator call)

1. **S11/S12 Dynamite gate**: visual pair [1],[2] gated fb1 (bar[1] only). The
   header's pair-touch law would give fb12. fb1 preserved (TNT OD v3/v2 parity).
2. **B2B HV+D group gates**: same shape — pair [1],[2], gate fb1. Preserved.

Both flags widen firing if changed to fb12 (a pattern whose FIRST visual bar is
the session's first bar would start passing). Say the word and they flip.
