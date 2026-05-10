# Displacement 4x

Four independent displacement engines stacked into one indicator. Each
engine has its own σ-multiplier (IPSF, default 6.5 / 6.0 / 5.5 / 5.0), its
own bull/bear plotshape, and its own alertconditions — but they share the
same boolean structure (prev-bar range exceeds σ × stdev gate, plus current
bar's bull/bear FVG confirmation).

## Why this is powerful

Anish stacks **4 instances** of this indicator on a chart, totalling **16
simultaneous displacement strength views**. Each pane can be tuned to a
different timeframe / multiplier set, so at any key bar he can see at a
glance which strength tiers fired, on which timeframes, alongside which
other detection plots.

The multiplier is `step=0.1` — a continuous function of stdev. 4.9 vs 5.0
produces genuinely different thresholds because the comparison is
`d_rng[1] > d_std[1] * mult` directly with no rounding or bucketing.

## Roots (8)

All `offset = -1` (FVG confirms on bar[0], the displaced candle is bar[1] —
plotting on bar[1] aligns the marker with the actual displacement bar). All
gated by `barstate.isconfirmed`.

| Canonical | Mult default | Plot |
|---|---|---|
| `disp-4x::D1_BULL` | 6.5 | `shape.square` top, green |
| `disp-4x::D1_BEAR` | 6.5 | `shape.square` top, red |
| `disp-4x::D2_BULL` | 6.0 | `shape.square` bottom, blue |
| `disp-4x::D2_BEAR` | 6.0 | `shape.square` bottom, magenta |
| `disp-4x::D3_BULL` | 5.5 | `shape.xcross` top, green |
| `disp-4x::D3_BEAR` | 5.5 | `shape.xcross` top, red |
| `disp-4x::D4_BULL` | 5.0 | `shape.cross` bottom, blue |
| `disp-4x::D4_BEAR` | 5.0 | `shape.cross` bottom, magenta |

Layout convention:
- **D1 / D3** plot at TOP (use the squares for D1, xcross for D3)
- **D2 / D4** plot at BOTTOM (squares for D2, cross for D4)
- **Green/red** = bull/bear directional pair for D1, D3
- **Blue/magenta** = bull/bear directional pair for D2, D4

## Engine internals (NOT roots — per the bible STOP rule)

The same Displacement engine pattern is used across all 4 instances:

```
d_rng = type == "Open to Close" ? abs(open - close) : (high - low)
d_std = stdev(d_rng, len=100)
d_thresh = d_std * mult           ← multiplier varies per instance
d_prevDisp = d_rng[1] > d_thresh[1]
d_bullFVG  = low  > high[2] AND close[1] > open[1]
d_bearFVG  = high < low[2]  AND close[1] < open[1]
d_bull = conf AND d_prevDisp AND d_bullFVG
d_bear = conf AND d_prevDisp AND d_bearFVG
```

`stdev`, `range`, and the FVG geometry are internal mechanics — not
separate roots per `docs/glossary.md`. Each instance's multiplier is IPSF
(`input.float`, step 0.1).

## Future expansion

Anish: "we may even expand that to 15-20 displacements in the future." If
this scales to e.g. `Displacement 16x`, the same naming pattern extends:
`disp-16x::D1_BULL` ... `disp-16x::D16_BEAR`.

## Files

- `versions/DISP_4X_v1.pine` — canonical (Pine v5, overlay)

## Bible

- `bible-input/extract-disp-4x.yaml` — full extraction (8 roots, 0 composites)
- `docs/lineage/disp-4x__*.md` — lineage cards for the 8 alerting signals
- See `docs/glossary.md` "σ-multiplier (sigma-multiplier)" for σ-multiplier
  semantics

## Branch provenance

Added to `claude/organize-indicators-hierarchy-8JDw1` in Stage 7.
