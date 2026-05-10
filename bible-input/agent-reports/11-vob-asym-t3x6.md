# VOB Asym T3×6 v8 — extraction report (compact)

Source: `vob/versions/VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine` · 1473 lines · Pine v6 · title `"VOB Asym T3 ×6 + MutEx Lines + Claude"` · overlay

## Summary

Six independent VOB engines (sensitivities A-F, EMA len 2500/2250/2000/1500/1250/1000) detect Volume Order Block zones from EMA fast/slow crossovers (slow = fast + 13 hardcoded). Each engine produces bull (lower) and bear (upper) zone arrays, accumulated volume pools, and a T3 "super" signal. A Mutually-Exclusive (MutEx) overlap engine renders the highest-sensitivity tier in full (top/bot/mid+fill) and degrades overlapping lower-tier zones to single mid-only lines (priorities 0/1/2/3+).

Counts: 25 plotshapes (12 T3 + 12 zone-creation + Nagasaki), 0 plot(), 2 alertcondition (`any_t3`, `any_zone`), 14 alert() calls, 3 tables, dynamic line.new for zone rendering.

## Roots (all defined-here, 100% self-contained — zero imports, zero `request.security`)

| Canonical | Source | Plain-English |
|---|---|---|
| `vob-asym::VOB_CROSS` (EMA fast/slow trigger) | 562-569 | Bullish: `ta.crossover(ema(close,len1), ema(close,len1+13))`. Bearish: `ta.crossunder`. Each crossover spawns one VOB zone candidate. `len1 ∈ {2500/2250/2000/1500/1250/1000}` per tier A-F. **`len2 = len1 + 13` hardcoded.** |
| `vob-asym::BULL_ZONE_PUSH` (lower_lvl) | 571-581 | On bullish cross, find lowest low in lookback window (len2 bars), accumulate volume from swing-low bar to cross bar, build zone bounded by [lowest_low, max(open[i],close[i]) clamped ≥ lowest+atr_adj*0.5]. Pushed to `lower_X` array. |
| `vob-asym::BEAR_ZONE_PUSH` (upper_lvl) | 583-593 | Symmetric: highest high in lookback, accumulate volume swing-bar→cross-bar, push to `upper_X`. |
| `vob-asym::ZONE_INVALIDATION` (close-through) | 595-620 | Bull zone invalidated when `close < lower`; bear zone invalidated when `close > upper`. Plus dedup-nuke when `mid` within `atr_proximity = ATR(200,200-highest)*3` of previous zone. Array hard-cap of 15 zones per tier per direction. |
| `vob-asym::NAGASAKI` | 750-754 | `volume[1] > running maxVolEver`. (Same primitive as `heavy-pentagon::NAGASAKI` but defined-here.) Plotshape line 848, **offset=-1**, gated by `barstate.isconfirmed`. |
| `vob-asym::T3_SUPER_BUY` / `T3_SUPER_SELL` (per-tier) | 622-679 | T3 buy fires when (1) exactly ONE active bull zone (`bc==1`), (2) opposing bear pool > 0, (3) bull zone volume > bear pool × `super_mult`, (4) close inside dominant bull zone. Symmetric for sell. `super_mult=1.5`, `cooldown_bars=100`. **Per-tier independent — 6 instances A-F.** |

## Composites

| Composite | Tier | Source | Composition |
|---|---|---|---|
| `vob-asym::T3_LADDER` (sensitivity ladder) | 3 | 562-679 (engine), 692-697 (instantiation) | Six parallel T3 super-signal engines, indexed A (highest sens, len1=2500) through F (lowest, len1=1000). Each engine emits independent (T3 buy, T3 sell, bull_pool, bear_pool) tuple via `f_vob`. |
| `vob-asym::MUTEX_OVERLAP_RENDER` | visual/rendering | 1020-1086 | Processing order A→F. Priority 0 = full draw (top+bot+mid+fill), Priority 1 = single solid mid, Priority 2 = single dotted mid, Priority 3+ = thin dotted mid. Determined by `f_zones_overlap` (`lo1<hi2 AND hi1>lo2`). |
| `vob-asym::ZONE_CREATION_MARKER_BULL/BEAR` × 6 tiers | 2 | 685-705, 910-946, 1002-1014 | Per-bar `nzb_X` (new zone bull) / `nzs_X` (new zone bear) detect array-size delta this bar; gated by `en_zone_X` toggle and per-bar cooldown. 12 plotshapes: ZoneBull A-F, ZoneBear A-F. |
| `vob-asym::PANCAKE_ASSESSMENT` | emission/heuristic | 734-744, 1275-1285 | Bull pancake = (`stk_bull≥3 AND bull_gap≥30%`); Bear symmetric; partial if stack≥3 but gap<30; else NO. Used in emission table. |

## Plots

12 T3 plotshapes (lines 834-846): T3a/b/c/d/e/f Buy + T3a/b/c/d/e/f Sell at varied locations.
12 Zone-creation plotshapes (lines 1002-1014): ZoneBull A-F / ZoneBear A-F.
1 Nagasaki plotshape (line 848, offset=-1).
0 `plot()` calls (budget exhausted; emission via labels/tables/logs/alerts/lines).

## Alerts

`any_t3` alertcondition (line 861) — "Any T3 Signal or Nagasaki".
`any_zone` alertcondition (line 1136) — "Any Zone Formation".
14 `alert()` calls (lines 875-904 + 1138-1164) emitting Bloomberg-format pipe-delimited payload `T3_SIGNAL|TICKER:..|TF:..|SIGNAL:..|TIER:..|...|SLOPE:..` per T3 firing + Nagasaki + zone-formation aggregator.

## Caveats

- 100% self-contained: zero `import`, zero `request.security`, no Supertrend/OKE/Zoo/EMA-cross indicator references / FVG geometry.
- "T3" here = Tier 3 super signal, NOT Tilson T3 moving average.
- "Asym" in title = `asym_threshold=99.0` input declared but UNUSED (reserved for future Tier 1 signals per tooltip).
- EMA pair offset hardcoded `len2 = len1 + 13` — part of VOB primitive identity, not a tunable.
- **Bullish→`lower_X` array**, **Bearish→`upper_X` array** — naming convention is inverted from intuition (lower=bull because zone forms at swing LOW; upper=bear because at swing HIGH). All downstream identifiers follow this convention.
- Zone array hard cap = 15 per tier per direction. Old zones silently shifted off when full.
- File header line 559: "*** THIS FUNCTION IS PRESERVED EXACTLY FROM THE ORIGINAL — DO NOT MODIFY ***" — strong provenance signal that core VOB+T3 logic was inherited from a parent file; v8 changes are emission-layer scaffolding.
- Apex break / Failed-Apex flip / Long1/Long2/Short1/Short2 / Boom Hunter Omega names from earlier briefs DO NOT appear in this file.
- Nagasaki uses `volume[1]` (prior-bar volume) and `offset=-1` so marker lands on the bar that produced the ATH event.
