# Heavy Combo Toggles v1 — extraction report (compact)

Source: `heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine` · 268 lines · Pine v5 · title `"Heavy Combo Toggles"` (shorttitle `"HCT"`)

## Verbatim claim VERIFIED

CHANGELOG: "the Heavy / RVOL engine that `heavy-combo-toggles` lifts its 5 base combos and 15 directional combo booleans from verbatim". Byte-equivalent diff confirms 100% — only whitespace/alignment differs from `heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine`.

## Roots referenced (all cross-refs to `heavy-pentagon::*`)

10 RVOL roots + 1 displacement engine, all verbatim copies of Heavy Pentagon's. Source lines 147-228 mirror Heavy Pentagon's threshold tables, Pipeline 1/2/3 stacks, displacement engine.

**SAAB and Kratos are dead code in this file.** They are computed (lines 147-148) but never feed any base combo (groupA_Bull/Bear deliberately exclude them per Heavy Pentagon Stage-5 doctrine), so they cannot influence the 3 master plots. Bible should flag as "computed-but-orphaned" cross-refs.

## Composites — 5 base + 15 directional (all verbatim cross-refs)

5 base combos: `baseYinYang`, `baseNagasaki`, `baseNagasakiV`, `baseTrident`, `baseNHx2` (lines 217-221) — verbatim from Heavy Pentagon.

15 directional combo booleans `sigHYY{Bull,Bear,Neutral}`, `sigHN{...}`, `sigHNV{...}`, `sigHT{...}`, `sigNHx2{...}` (lines 226-244) — verbatim from Heavy Pentagon.

## NEW signals (only original signals in this file)

3 master OR-gates with eligibility checkboxes:

```
hct::masterBull = (en_HYYBull AND sigHYYBull) OR (en_HNBull AND sigHNBull) OR (en_HNVBull AND sigHNVBull) OR (en_HTBull AND sigHTBull) OR (en_NHx2Bull AND sigNHx2Bull)
hct::masterBear = (mirror)
hct::masterNeutral = (mirror)
```

Plotshapes (3 only): `hct::S1_HEAVY_COMBO_BULL` (offset=-1, line 258), `hct::S2_HEAVY_COMBO_BEAR` (offset=-1, line 259), `hct::S3_HEAVY_COMBO_NEUTRAL` (offset=0, line 260).

Alertconditions (3): "S1: Heavy Combo Bull" / "S2: Heavy Combo Bear" / "S3: Heavy Combo Neutral" (lines 265-267).

15 input.bool eligibility gates `en_*` (lines 55-73, all default true).

## Behavioural difference from Heavy Pentagon (intentional, not drift)

- Bull/Bear master plots use `offset=-1` (visual on bar[1] displacement candle).
- Neutral master uses default `offset=0` (no displacement candle).
- Heavy Pentagon plots individual combos at default `offset=0`.

Per file header lines 34-39, this matches "Verification Protocol v3.2 Part 5 Rule 2".

Heavy Pentagon's 25 individual plotshapes + 25 alertconditions are **dropped**; the 15 `show_*` toggles, phantom toggles, and the 10 standalone RVOL plots are all dropped. This file collapses Heavy Pentagon's downstream emissions into 3 master OR-gates.
