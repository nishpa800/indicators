# kc-combo CHANGELOG

## v3 — 2026-07-25
- FIX OF RECORD (P-019): v2 REFUSED by TV for exceeding 64 outputs. Root cause was
  NEVER the IPSF inputs (inputs generate ZERO plot counts — TV docs + P-019 law):
  v2 carried (a) 46 computed plot colors `color.new(color.rgb(..), 0)` — each
  non-bare-const color arg costs +1 unit AND hides the Style-tab picker (P-017) —
  and (b) 47 alertcondition() calls at +1 unit each ("All plot*() calls and
  alertcondition() calls count towards the plot count" — official docs, CONFIRMED).
  v2 worst-case = 46 + 46 + 47 = 139/64.
- UNIT LAW SOLVED EXACTLY (gate v1.5, P-019): units = plot calls + dynamic-color
  args + alertconditions; text= is FREE. Reproduces BOTH vendor refusal integers:
  VOB v10.1 "78" = 39+24+15 and VOB v10.4 RE10140 "100" = 28+56+16. The P-011
  model (text=2u, ac=0u) fit 78 by numerical coincidence and is REFUTED.
- v3 = 46 dp plotshapes (bare #RRGGBB const colors → Style-tab picker restored on
  every row, zero unit cost) + 1 ANY alertcondition = 47/64. All 46 dp, all 184
  IPSF inputs, 46 ALERT checkboxes + consolidated alert() emission preserved.
- Gates: indicator_study_gate v1.5 PROVED D_bytes=0 (47/64) · pane_label D_cs1=0
  (graphic objects: 0) · fbf_111 D_111=0 (46 lanes). Anti battery 23/23 incl. new
  T-ACBUDGET / T-DYNCOLOR. Tick sibling owed: pair_debt due 2026-07-27 (L-49.1).


## v1 — 2026-07-24
- BORN: KC COMBO BULL + BEAR pair (+ TICK twins). 23 dp per study = the MAIN-list
  side-pure re-entry-anchored combos (every combo contains R-S; R-C-only bucket =
  PARKING LOT HTF, deferred by operator order). Enumeration of record:
  docs/2026-07-24_TV-TickBar-RE_PBJConsol-NoSinglesComboEnumeration_v3.2.md.
- Engines ported verbatim from PBJ PB CONSOL (operator Desktop source): OKEH Zoo /
  Supertrend / PB&J filter / level zones, KC Rev 8 re-entry family, Pocket Pivot,
  Displacement S11/S12 FVG member engine. Deviations disclosed in-file: source
  master toggles (re-entry / PUP-PPD / disp show) removed — per-dp VP checkboxes
  are the only visibility control.
- IPSF (operator acronym, glossary LAW row 2026-07-24): 92 per study — 23 VP
  checkboxes ⊥ 23 alert checkboxes (fully independent sections) · 23 displacement
  gate strengths (default 3.0, 0 = not required) · 23 HV dropdowns (Not required |
  50..4000 step 50 | Nagasaki; inclusive ≥ semantics — N passes N-or-deeper incl.
  Nagasaki; construction = HV_NRA 50-step ladder rank-1 test + FBF 4K rung).
- Budget law: 23 text plotshapes × 2 (P-011) = 46/64 per study; pair split is the
  L-61 lawful design (46 text-vp in one study = 92 > 64, TV refuses).
- L-61 graphic-object inventory: ZERO (no label/line/box/table/polyline).

## v2 — 2026-07-24 (ONE SOURCE CODE — operator order)
- MERGED: the v1 BULL/BEAR pair collapses into ONE study (KC_COMBO_v2 + TICK twin), all
  46 dp. Unit law honored inside one file (P-011: text plotshape=2u): 42 textless +
  4 texted pentas = 50/64. 46 text-vp would be 92/64 (TV refusal; VOB v10.1@78 exhibit).
- IDENTITY WITHOUT TEXT: tier→shape (2 ● · 3 ▲/▼ · 4 ◆ · 5 label+text), side→location
  (BULL belowbar / BEAR abovebar), each combo its OWN const color (46 distinct; Style-tab
  row per combo, P-017 pickers); Data Window + all alerts carry exact combo names.
- IPSF now 184 in one panel: 46 VP ⊥ 46 ALERT checkboxes · 46 disp strengths (3.0/0=off) ·
  46 HV dropdowns (Not required | 50..4000 | Nagasaki).
- v1 pair moved to superseded/ (history preserved; ledger lists v2 only).
