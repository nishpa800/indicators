# Anish 50% 1st Combo — extraction report

Source: `anish-50-1st-combo/versions/ANISH_50_1ST_COMBO_v1.pine` · 182 lines · Pine v6 · title `"Anish 50% 1st Combo (NR)"` (NR = Non-Repainting) · overlay

## Summary

Two parallel signal families on confirmed bars only:
1. Anish Stage 2/4 EMA-stack regime filter (`bullPass`/`bearPass`)
2. Pocket Pivot bull/bear (`sPPBull`/`sPPBear`)

Combined into Super PUP/PPD (same-bar confluence), All-Three (PP + Gap + Anish), and stateful TB/Foster transition signals tracked via `var` counters. Every signal fires through a `conf`-gated `fire_*` boolean used 1:1 by plot and alertcondition.

Counts: 10 plotshapes, 10 alertconditions, all `offset=0`.

## Roots

| Canonical | Source | Plain-English | Parameters |
|---|---|---|---|
| `anish-50-1st-combo::PUP` (cross-ref candidate) | 49-60 | Pocket Pivot Bull: bar percent body change > `barSize` AND volume > highest opposite-color volume of prior `ppLookback` bars; bullish requires up-bar | `barSize=3.0%`, `ppLookback=10` |
| `anish-50-1st-combo::PPD` (cross-ref candidate) | 49-60 | Pocket Pivot Bear: symmetric mirror | same |
| `anish-50-1st-combo::ANISH_BULL_PASS` | 29-46 | Anish Stage 2 (uptrend): price stacked above 50/150/200 EMA cascade; 200 EMA rising vs ~1 month ago; price within band of 52-week range. Plot label "Anish Bull". Treated as named root despite EMA-stack internals (humans refer to this as one named thing). | EMA 50/150/200 hardcoded; 21-bar lookback for `ema200_1m`; 252-bar 52-week H/L; bull bands 1.30/0.75 |
| `anish-50-1st-combo::ANISH_BEAR_PASS` | 29-46 | Anish Stage 4 (downtrend): symmetric mirror; bear bands 0.70/1.25 | same |

PUP/PPD provenance — likely root-of-truth here AND in `b2b-pup` AND in `hvd-pbj-ppd`. Stage-1 byte-diff resolves canonical owner.

## Composites

| Composite | Tier | Source | Composition | Plotted (offset=0) |
|---|---|---|---|---|
| `anish-50-1st-combo::SUPER_PUP` | 1 | 74 | `sPPBull AND bullPass` | yes — labelup belowbar lime "S-PUP" |
| `anish-50-1st-combo::SUPER_PPD` | 1 | 73 | `sPPBear AND bearPass` | yes — labeldown abovebar maroon "S-PPD" |
| `anish-50-1st-combo::GAP_UP_SIG` | 1 | 63, 65 | `gapUpEnabled AND gapUp` where `gapUp = open > close[1] * (1 + gapValue/100)` | no |
| `anish-50-1st-combo::GAP_DN_SIG` | 1 | 64, 66 | `gapDownEnabled AND gapDn` | no |
| `anish-50-1st-combo::ALL_THREE_BULL` | 2 | 69 | `sPPBull AND gapUpSig AND bullPass` | yes — circle abovebar yellow |
| `anish-50-1st-combo::ALL_THREE_BEAR` | 2 | 70 | `sPPBear AND gapDnSig AND bearPass` | yes — circle belowbar fuchsia |
| `anish-50-1st-combo::TB_SELL` | 2 (stateful FSM) | 78-108 | After ≥`minAnishBars` consecutive Anish-Bull bars, fires one-bar pulse once `followUpBars` consecutive bars print PPD without Anish-Bull | yes — labeldown abovebar purple "TB" |
| `anish-50-1st-combo::FOSTER_BUY` | 2 (stateful FSM) | 112-142 | Symmetric mirror | yes — labelup belowbar aqua "FOSTER" |

## Caveats

- All `var`-state mutations gated by `conf = barstate.isconfirmed` (lines 83, 117) — non-repainting design.
- Gap toggles default OFF (`gapUpEnabled=false`, `gapDownEnabled=false`); All-Three composites are opt-in.
- TB/Foster fire as one-bar pulses with explicit reset.
- No `offset=` arguments anywhere — current-confirmed-bar only.
- Anish Stage 2/4 hardcoded magic numbers (1.30, 0.75, 0.70, 1.25, 21, 252, EMA 50/150/200) — if a canonical Anish-Stage-2-4 indicator exists elsewhere with these as inputs, that file is provenance.
- `barSize` default 3.0% — "50%" in filename does not appear as numeric input. Naming inconsistency flagged.
