# Ultra Combo

Aggregator firing combo signals across PBJ/PB, F2/E3/FC cluster, B2B
PUP/PPD, Heavy Weapon (RVOL family), GZ1/HV FVG, FAUNA (MB+RE+TA core with
GG/TR/ES/GDR exclusion), displacement, ROC + LazyBear WaveTrend, TB/Foster,
Opener, 3-Bar, Mega, Super B2B Days.

## Locks the FAUNA composition

`FAUNA = (MB OR RE OR TA) AND NOT (GG OR TR OR ES OR GDR)` — at L730-L732
(bull) and L746-L748 (bear). All 7 components are roots; FAUNA itself is a
composite.

## Files

Two parallel Pine v5 / v6 files with **logic 1:1 identical**:

- `versions/ULTRA_COMBO_v57_pine6.pine` — original Pine v6 source
  (`Ultra Combo v57`)
- `versions/ULTRA_COMBO_v57_pine5.pine` — Pine v5 port
  (`Ultra Combo v57 (v5)`). Use this on charts where PBJ / OKEH / Zoo
  engines need v5 to match.

Differences (mechanical only, no behaviour change):
- `//@version=5` vs `//@version=6`
- `import TradingView/ta/7 as tv_ta` and the `relativeVolume(...)` call
  replaced with inline `volume / ta.sma(volume[1], 30)` (the `ta/7`
  library version requires Pine v6)
- Comma-chained `array.shift(...)` calls split onto separate lines
- Method-style array calls (`fvgs.size()`, `fvgs.unshift(...)`) rewritten
  function-style (`array.size(fvgs)`, etc.) for v5 parser tolerance

All thresholds, signal definitions, plotshape colors / locations / offsets,
alerts, and alertconditions are 1:1 between the two files.

## Counts (per Stage-1 extraction)

- 26 roots — including FAUNA components MB/RE/TA/GG/TR/ES/GDR (bull+bear),
  F2/E3/FC bull+bear, ROC bull/bear primitives, LazyBear WaveTrend cross,
  TB / Foster state machines
- 38 composites — including FAUNA bull/bear, ROC bull/bear, DISP bull/bear,
  4 SUPER variants, 6 PBJ/PB×F2/E3/Cluster, 4 sequential, 4 consecutive-day,
  Mega aggregations, Opener, 3-Bar, etc.

## Bible

- `bible-input/extract-ultra-combo.yaml` — full extraction with explicit
  `fauna_decomposition` section
- `docs/lineage/ultra-combo__*.md` — lineage cards for top-level composites
- `test-indicators/versions/ROOTS_FAUNA_TEST_v1.pine` — Stage-2 test rig
  for the FAUNA components

## Branch provenance

Lives on `claude/add-txt-indicator-format-b4FUu` — not on `main` as of bible
Stage 1.
