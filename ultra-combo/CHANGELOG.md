# Ultra Combo — CHANGELOG

## v57 — 2026-05-10

Initial drop. Aggregator that fires combo signals across PBJ/PB, F2/E3/FC
cluster, B2B PUP/PPD, Heavy Weapon (RVOL 1x / Grand Slam / MOAB / WTC /
Hiroshima / Nagasaki), GZ1/HV FVG, FAUNA (MB+RE+TA core with GG/TR/ES/GDR
exclusion), displacement, ROC + LazyBear WaveTrend, TB/Foster, Opener,
3-Bar, Mega, and Super B2B Days.

Two parallel files in `versions/`:

- `ULTRA_COMBO_v57_pine6.pine` — original Pine v6 source as authored.
  Title: `Ultra Combo v57`.
- `ULTRA_COMBO_v57_pine5.pine` — Pine v5 port. Logic identical. Title:
  `Ultra Combo v57 (v5)`. Use this on charts where PBJ / OKEH / Zoo
  engines need v5 to match. Differences from the v6 file:
  - `//@version=5`
  - `import TradingView/ta/7 as tv_ta` and the `relativeVolume(...)` call
    replaced with inline `volume / ta.sma(volume[1], 30)` — that library
    version requires Pine v6.
  - Comma-chained `array.shift(...)` calls split onto separate lines
    (mechanical, no behavior change).
  - Method-style array calls on the `fvgs` array (`fvgs.size()`,
    `fvgs.unshift(...)`, `fvgs.get(i)`, `fvgs.remove(i)`) rewritten as
    function-style (`array.size(fvgs)`, etc.) for v5 parser tolerance.

All thresholds, signal definitions, plotshape colors/locations/offsets,
alerts, and alertconditions are 1:1 between the two files.
