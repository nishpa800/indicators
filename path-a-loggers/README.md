# Path A — Logger Pine Indicators

Per `/Users/anishpatel/code/indicators/UNLIMITED_APPROVAL.md` Stage-3
verification, these are minimal Pine scripts that **read other indicators'
plot values via `input.source()` and emit one `label.new()` per fire**.
The labels are then read in bulk via the TradingView MCP's
`data_get_pine_labels(study_filter=...)` so we can pull hundreds of
historical fires per composite per timeframe in a single MCP call.

## Non-destructive

Loggers do NOT modify the source indicator's state. They subscribe to its
plot values via `input.source()` (which TradingView already exposes through
the data window) and write their own labels. Adding/removing a logger
does NOT touch the source indicator.

## Setup workflow

1. Make sure the source indicator (e.g. "Heavy Combo Toggles") is loaded on
   your TradingView chart.
2. Load the matching logger script (e.g. `LOGGER_HEAVY_COMBO_TOGGLES_v1.pine`).
3. In the logger's Inputs panel, point each "Source: ..." dropdown at the
   corresponding plot from the source indicator.
4. Done — labels appear automatically across all visible bars. Switch
   timeframes freely; labels regenerate per TF.

## Reading the labels via MCP

```
mcp__tradingview__data_get_pine_labels(
  study_filter="LOGGER Heavy Combo Toggles",
  max_labels=500,
  verbose=true,
)
```

Returns `{text, price, time, color, ...}` per label. Bucket by `text`
prefix to get per-composite fire counts. Run with different
`chart_set_timeframe(...)` between calls to sweep 9 TFs.

## Loggers in this directory

| Logger | Targets |
|---|---|
| `LOGGER_HEAVY_COMBO_TOGGLES_v1.pine` | S1/S2/S3 Heavy Combo Bull/Bear/Neutral (the 16→3 master OR-gates) |
| `LOGGER_B2B_PUP_v1.pine` | All 37 B2B PUP composites + roots (B2B, B2B+FAU, B2B+DISP, Uni+B2B, S19 UC×2, S20 FMU×2, etc.) |
| `LOGGER_HVDPBJPPD_v1.pine` | Floor / 2F / Rooftop / Penthouse + CS3 Unified Combo + CC + LSC + Tier-1 UU/UUU/UUUU/A★/FOX |

## Adding more loggers

Same pattern. Pick a source indicator, list its plots, add `input.source()`
inputs per plot, emit `label.new()` per fire. Use a short text tag (≤8
chars) so the labels stay visually compact on the chart.
