# Heavy PENTAGON — CHANGELOG

## v1 — 2026-05-10

Initial drop. Pine v5 source for Heavy PENTAGON — the Heavy / RVOL engine
that `heavy-combo-toggles` lifts its 5 base combos and 15 directional
combo booleans from verbatim.

- 10 standalone detections across 3 sealed pipelines:
  - P1 Standard RVOL: SAAB, Kratos, Bull/Bear RVOL 1x, Grand Slam, MOAB
  - P2 Reg@Time RVOL: Pentagon, WTC, Hiroshima
  - P3 All-Time High Volume: Nagasaki (HEV)
- 15 Heavy Combo detections (Stage 5 post-plot co-occurrence): Heavy
  Yin-Yang, Heavy Nagasaki, Heavy Nagasaki Vol, Heavy Trident, Neutral
  Heavy x2 — each Bull / Bear / Neutral.
- Direction classification via internal displacement engine
  (bar[1] range > σ × strength + bar[0] FVG confirmation). dispBull /
  dispBear / noDisp.
- All signals gated by `barstate.isconfirmed`.
- Plots and alerts share `fire_*` booleans (checkbox AND signal) for 1:1
  parity.
- Phantom toggles reserved for future engines (FAUNA, DISP A/B/C,
  LONG/SHORT, HV tiers, Hot Spot) — visible inputs, no logic connected.
- Library import: `TradingView/ta/7` for `relativeVolume()` in P2.
