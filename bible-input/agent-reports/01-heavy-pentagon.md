# Heavy PENTAGON — extraction report

Source: `heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine` · 444 lines · Pine v5 · overlay=true · max_labels_count=500 · max_bars_back=5000

## Summary

Three sealed RVOL pipelines (P1 Standard / P2 Reg@Time / P3 All-Time HV) feed 10 terminal root booleans. A separate displacement engine produces internal classifiers `dispBull`/`dispBear`/`noDisp` (NOT a root). Stage 5 builds 5 base co-occurrence combos (`baseYinYang`, `baseNagasaki`, `baseNagasakiV`, `baseTrident`, `baseNHx2`), each fanned into Bull/Bear/Neutral via the displacement classifier → 15 Heavy Combo terminals. Each terminal gates through a global `show_*` checkbox into a `fire_*` boolean used 1:1 by plotshape and alertcondition.

Counts: 0 `plot()`, 25 `plotshape()` (10 standalone + 15 Heavy Combo), 25 `alertcondition()` (1:1).

## Roots (10, all defined-here, all `offset=0`)

| Canonical | Source line | Plain-English |
|---|---|---|
| `heavy-pentagon::SAAB` | 185 | Bullish RVOL spike whose normalised price magnitude sits in the SAAB/Kratos band (between `th_saab_kratos` and `th_1x`) — early-tier bull volume push on a green candle. |
| `heavy-pentagon::KRATOS` | 186 | Bearish RVOL spike whose normalised price magnitude sits in the SAAB/Kratos band — early-tier bear volume push on a red candle. |
| `heavy-pentagon::BULL_RVOL_1X` | 187 | Bullish base candle with normalised price spike in the 1x band (`th_1x` to `th_gs_moab`) — standard-magnitude bull RVOL event. |
| `heavy-pentagon::BEAR_RVOL_1X` | 188 | Bearish base candle with normalised price spike in the 1x band — standard-magnitude bear RVOL event. |
| `heavy-pentagon::GRAND_SLAM` | 189 | Bullish base candle whose normalised price spike exceeds `th_gs_moab` — top-tier bull RVOL event. |
| `heavy-pentagon::MOAB` | 190 | Bearish base candle whose normalised price spike exceeds `th_gs_moab` — top-tier bear RVOL event. |
| `heavy-pentagon::PENTAGON` | 208 | Time-regularised relative-volume ratio (`relVolRatio`) sits between `th_1x` and `th_wtc` — entry-tier neutral heavy event from the Reg@Time pipeline. |
| `heavy-pentagon::WTC` | 209 | Reg@Time `relVolRatio` above `th_wtc` but ≤ `th_hiroshima` — middle-tier neutral heavy. |
| `heavy-pentagon::HIROSHIMA` | 210 | Reg@Time `relVolRatio` strictly above `th_hiroshima` — top-tier neutral heavy Reg@Time. |
| `heavy-pentagon::NAGASAKI` | 218-229 | Raw bar volume sets a new all-time high vs running `maxVol` since `bar_index 0` — Highest-Ever-Volume (HEV) event. |

Common parameters: `bb_avgLength=30`, `bb_smaLength=20`. Reg@Time: `reg_anchorTimeframe=""` (chart), `reg_length=30`, `reg_calculationMode="Cumulative"`, `reg_adjustRealtime=true`. All gated by `barstate.isconfirmed`. Threshold tables: `f_rvol_1x_threshold(tfSec)`, `f_saab_kratos_threshold = f_rvol_1x_threshold * 0.56`, `f_gs_moab_threshold(tfSec)`, `th_wtc = th_1x * 2.0`, `th_hiroshima = f_gs_moab_threshold(tfSec)`.

## Internal direction classifier (NOT a root)

`dispBull`, `dispBear`, `noDisp` (lines 236-256). Source comment: "Building Block only — no standalone plotshape." Consumed only by Stage 5.

## Composites (15 Heavy Combo terminals, all tier-1, all `offset=0`)

All composites gate through their own `show_*` checkbox via `fire_<name> = show_<name> AND sig<name>`.

| Composite | Source line | Composition |
|---|---|---|
| `heavy-pentagon::HEAVY_YIN_YANG_BULL` | 293 | `baseYinYang AND dispBull` where `baseYinYang = (groupA_Bull OR groupA_Bear) AND groupB`, `groupA_Bull = BULL_RVOL_1X OR GRAND_SLAM`, `groupA_Bear = BEAR_RVOL_1X OR MOAB`, `groupB = PENTAGON OR WTC OR HIROSHIMA` |
| `heavy-pentagon::HEAVY_YIN_YANG_BEAR` | 294 | `baseYinYang AND dispBear` |
| `heavy-pentagon::HEAVY_YIN_YANG_NEUTRAL` | 295 | `baseYinYang AND noDisp` |
| `heavy-pentagon::HEAVY_NAGASAKI_BULL` | 298 | `baseNagasaki AND dispBull` where `baseNagasaki = NAGASAKI AND (groupA_Bull OR groupA_Bear)` |
| `heavy-pentagon::HEAVY_NAGASAKI_BEAR` | 299 | `baseNagasaki AND dispBear` |
| `heavy-pentagon::HEAVY_NAGASAKI_NEUTRAL` | 300 | `baseNagasaki AND noDisp` |
| `heavy-pentagon::HEAVY_NAGASAKI_VOL_BULL` | 303 | `baseNagasakiV AND dispBull` where `baseNagasakiV = NAGASAKI AND groupB` |
| `heavy-pentagon::HEAVY_NAGASAKI_VOL_BEAR` | 304 | `baseNagasakiV AND dispBear` |
| `heavy-pentagon::HEAVY_NAGASAKI_VOL_NEUTRAL` | 305 | `baseNagasakiV AND noDisp` |
| `heavy-pentagon::HEAVY_TRIDENT_BULL` | 308 | `baseTrident AND dispBull` where `baseTrident = NAGASAKI AND (groupA_Bull OR groupA_Bear) AND groupB` |
| `heavy-pentagon::HEAVY_TRIDENT_BEAR` | 309 | `baseTrident AND dispBear` |
| `heavy-pentagon::HEAVY_TRIDENT_NEUTRAL` | 310 | `baseTrident AND noDisp` |
| `heavy-pentagon::NEUTRAL_HEAVY_X2_BULL` | 313 | `baseNHx2 AND dispBull` where `baseNHx2 = (PENTAGON AND WTC) OR (PENTAGON AND HIROSHIMA) OR (WTC AND HIROSHIMA)` |
| `heavy-pentagon::NEUTRAL_HEAVY_X2_BEAR` | 314 | `baseNHx2 AND dispBear` |
| `heavy-pentagon::NEUTRAL_HEAVY_X2_NEUTRAL` | 315 | `baseNHx2 AND noDisp` |

The 5 base intermediaries (`baseYinYang`, `baseNagasaki`, `baseNagasakiV`, `baseTrident`, `baseNHx2`) are unnamed plumbing — not plotted, not alerted, no human-facing canonical name.

## Phantom toggles (reserved, no engine — not roots)

FAUNA Bull/Bear, DISP A/B/C Bull/Bear, LONG 1/2, SHORT 1/2, HV 75/150/250/500/1000, Hot Spot (lines 61-83). Source header comment: "PHANTOM TOGGLES (reserved — no engine connected)".

## Plotshapes inventory (all `offset=0`)

10 root plotshapes (lines 363-372): SAAB, Kratos, Bull RVOL 1x, Bear RVOL 1x, Grand Slam, MOAB, Pentagon, WTC, Hiroshima, Nagasaki (HEV).
15 composite plotshapes (lines 381-403): three each of Heavy Yin-Yang, Heavy Nagasaki, Heavy Nagasaki Vol, Heavy Trident, Neutral Heavy x2 (Bull/Bear/Neutral).

## Alertconditions inventory (all `offset=0`)

25 alertconditions (lines 410-444), one per plotshape, condition is the matching `fire_*` boolean.

## Caveats

- Plot title `"Nagasaki (HEV)"` — canonical name is `NAGASAKI`; `(HEV)` appears only in the title.
- `f_*_threshold` functions are timeframe-conditional internal mechanics, not roots.
- `tv_ta.relativeVolume` (TradingView/ta/7 lib) is the Pipeline-2 volume engine — internal mechanic.
