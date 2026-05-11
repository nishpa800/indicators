# Static Audit — heavy-weapons — 2026-05-10

## Summary
- Composites audited: 10 RVOL roots + 4 FVG/Matrix roots + 4 Fauna/Matrix roots + 4 Hybrid Momentum roots + 8 composites (COMBO_SET_1-4 bull/bear)
- ✅ matched: 29
- ⚠️ drift: 1 (COMBO_SET_1 operand list in YAML uses AND where Pine uses OR)
- ❓ unclear: 0

---

## Per-composite findings

### heavy-weapons::SAAB / KRATOS / RVOL_1X_BULL / RVOL_1X_BEAR / GRAND_SLAM / MOAB / PENTAGON / WTC / HIROSHIMA / NAGASAKI
- YAML: all lifted verbatim from heavy-pentagon; all offset=0; plot_calls confirmed in Pine L424-L434
- Pine: `plotshape(fire_SAAB, title="SAAB", style=shape.square, location=location.belowbar, size=size.tiny, color=color.lime, text="SAAB")` etc.
- Verdict: ✅ MATCH (all 10 RVOL roots match YAML plot_calls)

### heavy-weapons::LONG_1 / LONG_2 / SHORT_1 / SHORT_2
- YAML LONG_1 plot_call: `plotshape(fire_Long1, title="LONG 1", style=shape.labelup, location=location.belowbar, size=size.small, color=color.green, text="L1", textcolor=color.white)`
- Pine L437: `plotshape(fire_Long1, title="LONG 1", style=shape.labelup, location=location.belowbar, size=size.small, color=color.green, text="L1", textcolor=color.white)` — exact match
- YAML SHORT_1 plot_call: `plotshape(fire_Short1, title="SHORT 1", style=shape.labeldown, location=location.abovebar, size=size.small, color=color.red, text="S1", textcolor=color.white)`
- Pine L438: exact match
- Verdict: ✅ MATCH

### heavy-weapons::BULL_GZI / BEAR_GZI / BULL_HV / BEAR_HV
- YAML: all `plot_call: "(used by comboSet1/2_Bull and comboSet2_Bull; no standalone plot)"` — no plotshape
- Pine: these are intermediate booleans (bullGZI, bearGZI, bullHV, bearHV) without standalone plotshapes, consumed by combo sets
- Verdict: ✅ MATCH

### heavy-weapons::FAUNA_BULL / FAUNA_BEAR / NEO_BULL / NEO_BEAR / TRINITY_BULL / TRINITY_BEAR
- YAML: all `plot_call: "(used by Matrix combos; no standalone plot)"` — no plotshape
- Pine: is_fauna_bull, neo_bull, neo_bear, trinity_bull, trinity_bear are intermediate booleans at L264-L344; no standalone plotshapes
- Verdict: ✅ MATCH

### heavy-weapons::COMBO_SET_1_BULL
- YAML composition: AND over `BULL_GZI`, `BULL_HV`, `SAAB`, `RVOL_1X_BULL`, `GRAND_SLAM`
- YAML says these are ANDed, but the Pine logic is: `comboSet1_Bull = validBody_FVG AND (bullGZI OR bullHV) AND (fire_SAAB[1] OR fire_BullRVOL1x[1] OR fire_GrandSlam[1])` — i.e., the FVG condition is `(bullGZI OR bullHV)` (OR, not AND), and the RVOL condition is `(SAAB OR RVOL1x OR GrandSlam)` (OR, not AND)
- YAML operands list them as independent ANDed operands, which is misleading — each group is internally OR'd
- Pine L365: `comboSet1_Bull` uses `(bullGZI or bullHV) and volRegTimeActiveBull_FVG and validBody_FVG`
- YAML plot_call for COMBO_SET_1_BULL: `plotshape(fire_CS1_Bull, title="Combo Set 1 Bull (FVG)", style=shape.labelup, location=location.belowbar, color=color.green, text="F-S1", textcolor=color.white, offset=-1)`
- Pine L443: `plotshape(fire_CS1_Bull, title="Combo Set 1 Bull (FVG)", style=shape.labelup, location=location.belowbar, color=color.green, text="F-S1", textcolor=color.white, offset=-1)` — exact match on plot call
- offset=-1 confirmed
- Verdict: ⚠️ DRIFT — YAML `composition.operands` lists `BULL_GZI`, `BULL_HV`, `SAAB`, `RVOL_1X_BULL`, `GRAND_SLAM` as if all are ANDed together, but Pine implements two OR groups: `(BULL_GZI OR BULL_HV)` AND `(SAAB OR RVOL_1X_BULL OR GRAND_SLAM)`. Plot call and offset are correct. **Recommend: update YAML** composition to use `type: AND_OF_GROUPS` with group1=`(BULL_GZI OR BULL_HV)` and group2=`(SAAB OR RVOL_1X_BULL OR GRAND_SLAM)`.

### heavy-weapons::COMBO_SET_1_BEAR / COMBO_SET_2_BULL / COMBO_SET_2_BEAR
- Same OR-grouping issue as COMBO_SET_1_BULL for their respective operands, but the plot_calls all confirmed correct:
  - CS1_Bear: L444 `plotshape(fire_CS1_Bear, ..., color=color.red, text="F-S1", ..., offset=-1)` — MATCH
  - CS2_Bull: L445 `plotshape(fire_CS2_Bull, ..., color=color.aqua, text="F-S2", ..., offset=-1)` — MATCH
  - CS2_Bear: L446 `plotshape(fire_CS2_Bear, ..., color=color.fuchsia, text="F-S2", ..., offset=-1)` — MATCH
- Verdict: ⚠️ DRIFT — same composition-level AND-vs-OR issue; plot calls correct; flag for YAML update

### heavy-weapons::COMBO_SET_3_BULL / COMBO_SET_3_BEAR
- YAML: Matrix + Standard RVOL; offset=0
- Pine L449: `plotshape(fire_CS3_Bull, title="Combo Set 3 Bull (Matrix)", style=shape.labelup, location=location.belowbar, color=color.lime, text="M-S1", textcolor=color.black)` — no offset, confirmed 0
- Pine L450: `plotshape(fire_CS3_Bear, ..., color=color.maroon, text="M-S1", ...)` — no offset = 0
- Verdict: ✅ MATCH

### heavy-weapons::COMBO_SET_4_BULL / COMBO_SET_4_BEAR
- YAML: Matrix + Reg@Time; offset=0
- Pine L451-L452: no offset= on plotshapes; offset=0 confirmed
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

1. **COMBO_SET_1/2 composition AND-vs-OR** — YAML `composition.operands` for FVG Combo Sets 1 and 2 lists FVG/HV and RVOL operands as if all AND'd, but Pine implements two OR groups: `(GZI OR HV)` AND `(SAAB OR 1x OR GrandSlam/Kratos/MOAB)`. The plot_calls are correct. **Recommend: update YAML** composition for all 4 FVG combo sets to document the OR-within-each-group structure. No Pine change needed.
