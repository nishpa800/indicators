# kc-combo CHANGELOG

## v4.4 — 2026-07-27 (BULL + BEAR)
- OPERATOR ORDER 2026-07-27: "no more HV and displacement — remove the dropdowns."
  The per-dp HV/DISP gate machinery is REMOVED IN TOTALITY from both side studies:
  40 per-dp DISP dropdowns + 40 per-dp HV dropdowns (Not required|50..4000|Nagasaki)
  + 14 GATE CASCADE knobs (MASTER disp σ / MASTER HV / 6 GROUP DISP / 6 GROUP HV)
  = 94 inputs per study, plus the 7 gate/resolver functions (f_dispOK, f_hvOK,
  f_deff, f_heff, f_dnum, f_dgrp, f_hgrp) and the two gate conjuncts on all 40
  gated sig lanes. Every lane now fires on raw combo membership alone.
- KEPT (members are not gates): Displacement MEMBER engine (the D/X in combo
  names, S11/S12 FVG), HVD ported engine + Base-HV toggles (H.A lane), isNaga
  ATH-volume atom (NAGASAKI dp), all 44 VP + 44 ALERT checkboxes, all plots,
  consolidated alert() emission. Unit count unchanged: 50/64 (inputs are free).
- Behavior delta (declared, LAW-CANDOR): v4.3 defaults (MASTER disp σ=3.0)
  suppressed every MAIN/HTF lane on any bar lacking a 3σ range candle; v4.4
  fire counts are strictly ≥ v4.3 per lane on any chart.
- Consequence: the W-VPCAL calibrated-gate-defaults debt (v4.3 rigor row, due
  2026-08-02) is VOID for kc-combo — the machinery it calibrated no longer exists.
- Ship: transform manifests (base = v4.3 @ origin/main 09c44d8, 48 declared
  edits/side, D_bytes=0), pane_label D_cs1=0 x2, fbf_111 D_111=0 x2, graphic
  objects: 0. Tick pair_debt carried (owner fable, due 2026-07-28).

## v4.3 pair — 2026-07-26 (context-line default visibility; operator order)
- BULL default-visible context: KC Lower + BULL Combo Count ONLY. BEAR: KC Upper +
  BEAR Combo Count ONLY. KC Basis, Supertrend, and the opposite band ship UNCHECKED
  (display.none — re-checkable per row in the Style tab; hidden plots still count,
  budget unchanged 50/64 x2). Everything else identical to v4.2.
- Gates: study v1.6 PROVED x2 D_bytes=0 · D_vis=0 · D_cs1=0 x2 · D_111=0 x2.


## v4.2 pair — 2026-07-26 (GATE CASCADE + LAW-RIGOR; supersedes v4.1 on UX refusal)
- OPERATOR CHARGE (PROVED): 40 typed per-dp displacement floats = "maniacal". FIX =
  GATE CASCADE: per-dp DROPDOWN -> GROUP (Pairs/Triples/Quads/Pentas/HTF/+ANY) ->
  MASTER. Zero typing anywhere; defaults follow Group->Master so ONE master knob
  moves every gate; out-of-box behavior byte-equivalent to v4.1 semantics (master
  disp 3.0, master HV Not required, +ANY disp group Off). Same cascade for HV.
- LAW-RIGOR (L-62) ENACTED: rigor spectrum R0-R4; new market-meaningful defaults
  (R3) REQUIRE >=1k MC experiments per VP per variable (probability AND
  meaningfulness) or a dated calibration debt. Enforced by indicator_study_gate
  v1.6 axis A12 (anti T-NORIGOR; battery 24/24). Spec:
  docs/2026-07-26_TV-TickBar-RE_W-VPCAL-DetectionCalibration-RigorSpectrum_v1.0.md.
  Templates: T-CALIB v1.0 born; T-VP v1.4 (IPSF cascade law: >=10-lane gate
  families MUST ship as cascades, flat typed floats REFUSED design).
- v4.2 rigor: R3 with calibration debt due 2026-08-02 (W-VPCAL campaign; wave 1
  base rates launched on lake Silver same session). Current defaults = R2
  provenance (operator-dictated 3.0 / Not-required).
- Gates: study v1.6 PROVED x2 D_bytes=0 (50/64) · visual_identity D_vis=0 ·
  CS-1 D_cs1=0 x2 · 1:1:1 D_111=0 x2 · battery 24/24 (58/58 regression).


## v4.1 pair — 2026-07-25 (VISUAL-IDENTITY LAW II; supersedes v4, operator visual refusal)
- OPERATOR CHARGES (all PROVED): bull yellows confusable with bear oranges; every
  bear marker piled abovebar / every bull marker belowbar (unreadable stacks); no
  on-chart language. LAW II enacted + machine-gated:
  visual_identity_gate.py (D_vis = overlap + banned + textless + band-miss; exit 0
  iff 0; selftest 5/5 planted violations refute).
- ZERO cross-side color overlap at family level: BULL cool only (blues/greens/
  cyans — MAIN keeps v3 blue-green gradient, HTF cyan, +ANY royal blue, agg green);
  BEAR hot only (MAIN red gradient — v3 bear tail had drifted green, regenerated —
  HTF pink, +ANY magenta, agg red). YELLOW + ORANGE BANNED both sides.
- WHITE LETTER-CODE on every marker (text=code, textcolor=color.white — FREE under
  P-019): B=PB J=PBJ C=RC S=RS U=PUP D=PPD X=Displacement; combos read as letter
  runs (BS=PB+RS, JCSUX=PBJ+RC+RS+PUP+D); ported members dotted: H.A UC.A CS1.A
  CS2.A M.A CC.A; A=ANY, 2+/3+, N=Naga. Legend in file header; codes also in every
  input label, Style-tab title, and alert payload.
- LOCATION = FAMILY BAND (color carries the side): belowbar=BULL MAIN+BEAR agg ·
  abovebar=BEAR MAIN+BULL agg · bottom=BULL HTF+BEAR +ANY · top=BEAR HTF+BULL +ANY.
- Context lines neutral grays (shared by declaration). Budget unchanged 50/64 x2.
- Gates: study gate v1.5 PROVED x2 D_bytes=0 · visual_identity D_vis=0 · CS-1
  D_cs1=0 x2 · 1:1:1 D_111=0 x2 · battery 23/23 (56/56 regression).


## v4 pair — 2026-07-25 (BULL + BEAR, maxed)
- OPERATOR ORDER: "make a bullish version and max it out and make a bearish version
  and max it out" + add HVD+ANY, UC+ANY, CS1+ANY, CS2+ANY, MAT+ANY, CC+ANY.
- EACH STUDY = 50/64 (P-019 law; 14 spare): 23 MAIN combos (verbatim v3) + 11 HTF
  combos (RC-anchored parking-lot list, unparked by this order) + 6 +ANY lanes
  (member fires same confirmed candle as >=1 of the study's 34 combos) + ANY/2PLUS/
  3PLUS/NAGASAKI aggregates + KC basis/upper/lower + Supertrend + combo-count
  (data window) + 1 ANY alertcondition.
- ENGINES PORTED VERBATIM (deterministic builder scripts/ind/build_kc_v4_pair.py,
  dependency slices in scripts/ind/kc_v4_fragments/): CCC v1 CS1/CS2/MAT/UC/CC
  (back-to-back pair chain law, the only chain law in CCC v1) + HVD BULLISH/BEARISH
  (HV-rank ladder x prior-bar displacement FVG). conf-def deduped; render/q-lane/
  tagBlock/masterGate layers excluded; grp_align def injected — all drops asserted.
- IPSF: combos DISP 3.0 default + HV dropdown (v3 contract); +ANY lanes DISP 0.0 +
  HV Not-required defaults (member engines carry own thresholds — disclosed);
  aggregates VP/ALERT only. Lane numbering global: C01-23/H01-11/A01-06/X01-04 BULL,
  C24-46/H12-22/A07-12/X05-08 BEAR.
- Gates: indicator_study_gate v1.5 PROVED x2 D_bytes=0 (50/64) · pane_label D_cs1=0
  x2 (graphic objects: 0) · fbf_111 D_111=0 x2 (44 lanes each) · battery 23/23
  (T-REGRESSION 54/54 at adjudicated verdicts). Tick siblings owed: pair_debt due
  2026-07-28 x2 (L-49.1). v3 remains the single-study build; the pair is the maxed lane.


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
