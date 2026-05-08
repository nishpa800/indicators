# Heavy Combo Toggles — CHANGELOG

## v1 — 2026-05-08

Initial version. Collapses Heavy PENTAGON's 15 Heavy-Combo plotshapes into 3
master detection plots: Bull / Bear / Neutral.

- All underlying definitions (P1 RVOL Bull/Bear, P2 Reg@Time RVOL, P3 Nagasaki
  HEV, displacement engine, 5 base combos, 15 directional combo booleans) are
  lifted **verbatim** from Heavy PENTAGON. Nothing changed.
- 15 eligibility checkboxes gate which constituent combos contribute to each
  master OR-gate.
- Offsets per Verification Protocol v3.2 Part 5 Rule 2:
  - Bull master uses `dispBull` (displacement+FVG in chain) → `offset = -1`
  - Bear master uses `dispBear` (displacement+FVG in chain) → `offset = -1`
  - Neutral master uses `noDisp` (= NOT dispBull AND NOT dispBear). No
    displacement candle to mark when noDisp is true → `offset = 0`.
- 3 alertconditions, 1:1 parity with the 3 plotshapes.
- No standalone plots for SAAB / Kratos / RVOL1x / Grand Slam / MOAB / Pentagon
  / WTC / Hiroshima / Nagasaki — they're computed as building blocks only.
- No phantom toggles (FAUNA / DISP / LONG / SHORT / HV / Hot Spot dropped).
