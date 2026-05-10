# VOB Ladder Watch v1 — extraction report (compact)

Source: `vob/versions/VOB_LADDER_WATCH_v1.pine` · 215 lines · Pine v5 · title `"VOB Ladder Watch v1"` (shorttitle `"VOB LDR"`)

**Distinct indicator** co-located with VOB Asym T3×6 in the `vob/` folder — flag for Stage 6 file-system reorganisation.

## Summary

Six parallel bull-only VOB zone engines (sensitivities A→F, EMA-cross-anchored) maintain per-tier arrays of active bull zones. Each tier's highest-priced active-zone midpoint is extracted, then a strict ascending walk F→E→D→C→B→A computes a `ladder_depth` (0-6). Escalation transitions on confirmed bars fire labeled plotshapes and tiered alertconditions plus a structured `alert()` payload, with a top-right depth gauge table.

Counts: 5 plotshapes, 5 alertconditions, 1 alert() call, 1 table.

## Roots (defined-here, but mirror VOB Asym T3×6 bull-half engine)

`f_bull_vob` engine (lines 35-85) is per the file's own header line 11 ("same mechanic as VOB Asym T3") and CHANGELOG lines 8-10 a verbatim mirror of `vob-asym::*` bull-half. Pinned to:

| Canonical | Source | Plain-English |
|---|---|---|
| `vob-ladder::Z_A` (sens A — highest) | 35, 51, 87, 106 | EMA len 2500. Most-recent active VOB bull zone at this tier. |
| `vob-ladder::Z_B` | 36, 52, 88, 107 | EMA len 2250. |
| `vob-ladder::Z_C` | 37, 53, 89, 108 | EMA len 2000. |
| `vob-ladder::Z_D` | 38, 54, 90, 109 | EMA len 1500. |
| `vob-ladder::Z_E` | 39, 55, 91, 110 | EMA len 1250. |
| `vob-ladder::Z_F` | 40, 56, 92, 111 | EMA len 1000. **Anchor — must exist for any depth>0.** |

These should be cross-refs to `vob-asym::*` bull-half outputs in canonical bible (rather than separate roots). Per the file header, T3×6 should be treated as canonical; LADDER_WATCH consumes a derivative copy.

## Composites

| Composite | Tier | Source | Composition |
|---|---|---|---|
| `vob-ladder::LADDER_DEPTH` | 1 | 117-135 | Count of consecutive ascending tiers starting from zF walking up to zA. Nested if-cascade over (p_f, p_e, p_d, p_c, p_b, p_a) requiring not-na AND strictly increasing. |
| `vob-ladder::ESCALATED` | 2 (transition flag) | 138-139 | `ladder_depth > prev_depth AND barstate.isconfirmed`. |
| `vob-ladder::DE_ESCALATED` | 2 (UNUSED — dead code candidate) | 140 | `ladder_depth < prev_depth AND barstate.isconfirmed`. Computed but never consumed downstream. |
| `vob-ladder::FIRE_WATCH` | 3 | 151 | `escalated AND ladder_depth == 2`. Plotshape labelup belowbar small "WATCH". Offset 0. |
| `vob-ladder::FIRE_TIER3` | 3 | 152 | `escalated AND ladder_depth == 3`. "LDR3+D". |
| `vob-ladder::FIRE_TIER4` | 3 | 153 | `escalated AND ladder_depth == 4`. "LDR4+C". |
| `vob-ladder::FIRE_TIER5` | 3 | 154 | `escalated AND ladder_depth == 5`. "LDR5+B". |
| `vob-ladder::FIRE_FULL` | 3 (terminal) | 155 | `escalated AND ladder_depth == 6`. shape.flag location.bottom huge "FULL LDR". |

## Escalation logic

State variable `prev_depth` (var int) persists across bars; updated to `ladder_depth` each confirmed bar. Each fire_* boolean isolates the precise level entered (`escalated AND ladder_depth == N`) so a jump from depth 0 to 3 fires only `fire_tier3`, not the intervening levels. Per-step rung condition: depth advances only if next-higher tier price is non-na AND strictly greater than previous tier's price.

Reset: zF zone goes na (engine invalidates when `close < l.lower`), or any rung's tier price goes na, or strict-ascending breaks. On next confirmed bar `prev_depth` rebases.

## Caveats

- Distinct indicator from VOB Asym T3×6 despite folder co-location.
- Stage 6 should split `vob/zone_engine/` (canonical T3×6) and `vob/ladder/` (this file), or hoist shared `f_bull_vob` engine to `vob/_shared/`.
- `de_escalated` is dead code — candidate for removal or wiring to "ladder broken" alert.
- Per-tier price `p_x` is "highest mid among active zones" (line 102 picks max), not "most recent by index" — comment at line 95 says "most recent (highest-priced)" conflating the two; document actual semantics in bible.
- Nested-if cascade makes `ladder_depth` a strict-prefix-ascending count anchored at zF; if zF is na the entire ladder is 0 even if higher tiers ascend — by-design anchor semantics.
- All escalation booleans require `barstate.isconfirmed`; intrabar movement does not fire alerts.
- No request.security, no Supertrend/OKE/Zoo references — self-contained.
