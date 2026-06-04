# Postmortem — RE10023 in tick-friendly Pine (2026-06-04)

## Symptom
`Runtime error: RE10023 — Cannot call the 'timeframe.change' function with a tick-based
'timeframe' argument` on **bar 0** when a tick-friendly indicator is loaded on a tick chart
(observed live on AMEX:BRF @ **1000T**). Trace: `tv_ta.relativeVolume():346 → #main()`.

## Root cause
`TradingView/ta/7` `relativeVolume()` runs `timeframe.change(anchorTimeframe)` internally (line 346).
The suite passes a blank anchor `""` (TNT OD, B2B PUP) or an input defaulting to `""` (SQUARIFY, VOB,
HVD, HEAVY WEAPONS). A blank anchor resolves to the **chart** timeframe; on a tick chart that is
tick-based, so `timeframe.change` throws on bar 0.

The first tick-friendly pass *attempted* a guard but wired it wrong in all 5 RVOL files:
```pine
// WRONG — shipped 2026-06-04:
((reg_anchorTimeframe == "" and (na(timeframe.in_seconds(timeframe.period)) or timeframe.in_seconds(timeframe.period) <= 0))
  or str.endswith(reg_anchorTimeframe, "T")) ? "D" : reg_anchorTimeframe
```
Two defects:
1. **Wrong tick detector.** `timeframe.in_seconds("1000T")` returns a **positive number** (not na/0) on
   tick charts, so the `na/<=0` branch never fires.
2. **Wrong variable.** `str.endswith(reg_anchorTimeframe, "T")` checks the *anchor* (which is `""` →
   always false), not the *chart* `timeframe.period` (which is `"1000T"`).
Net: blank `""` reached the library → crash. The call-site gate (`grep relativeVolume(... "")`) passed
because the literal `""` was hidden inside the `*anchorSafe` variable definition.

## Fix (all 5 files)
Detect tick by the authoritative signal — the `"T"` suffix on `timeframe.period` — and coerce blank→`"D"`
**only on tick charts** (time-chart behavior unchanged → parity preserved):
```pine
// input-anchor form (SQUARIFY / VOB / HVD / HEAVY WEAPONS):
((reg_anchorTimeframe == "" and (str.endswith(timeframe.period, "T") or na(timeframe.in_seconds(timeframe.period)) or timeframe.in_seconds(timeframe.period) <= 0))
  or str.endswith(reg_anchorTimeframe, "T")) ? "D" : reg_anchorTimeframe
// hardcoded-blank form (TNT OD / B2B PUP):
(str.endswith(timeframe.period, "T") or na(timeframe.in_seconds(timeframe.period)) or timeframe.in_seconds(timeframe.period) <= 0) ? "D" : ""
```

## Files
| File | RVOL calls | Status |
|---|---:|---|
| tnt-od/tick_friendly/TNT_OD_v3_tick_friendly.pine | 1 | FIXED |
| squarify/tick_friendly/SQUARIFY_LTF_v1_tick_friendly.pine | 3 | FIXED |
| vob/tick_friendly/VOB_v11_FULL_TICKFRIENDLY_2026-06-04.pine | 3 | FIXED |
| vob/tick_friendly/VOB_v11_MULTIPLES_TICKFRIENDLY_2026-06-04.pine | 3 | FIXED |
| heavy-weapons-nra/tick_friendly/HEAVY_WEAPONS_NRA_v1_tick_friendly.pine | 4 | FIXED |
| hub-1020-1153am/tick_friendly/HUB_..._tick_friendly.pine | 0 | not affected |
| hvd-pbj-ppd/tick_friendly/COMBO_CHAIN_FIXED_tick_friendly.pine | 0 | not affected |

## Verification
- Static: resolution confirmed `"1000T"` (tv_health_check + chart_get_state). `str.endswith("1000T","T")`
  = true → anchor `"D"` → `timeframe.change("D")` legal on any chart. Deterministic, no guess.
- Gate: all 5 files pass the hardened gate (each `*anchorSafe` def contains
  `str.endswith(timeframe.period, "T")`; zero literal-blank anchors at call sites).
- Live compile on Anish's 1000T chart was NOT performed: his chart holds a curated 38-study stack and the
  immutable-chart rule forbids injecting a study. Self-verify snippet provided separately.

## Durable prevention
Skill `pine-editor-to-pine-tick-friendly` updated: WRONG-vs-RIGHT anchorSafe snippets + a hardened gate
that inspects the `*anchorSafe` DEFINITION (must key off `timeframe.period`), not just the call site.
