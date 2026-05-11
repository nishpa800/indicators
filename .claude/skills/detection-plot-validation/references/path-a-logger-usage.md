# Reference: Path A logger usage

Path A is the primary TV-firing verification mechanism. Path A is non-destructive: a separate logger Pine reads the source indicator's plot values via `input.source()` and emits one `label.new()` per fire. The labels become queryable via `data_get_pine_labels` (TradingView MCP).

## Setup (Anish does this once per chart layout)

1. **Load the source indicator** on the chart (e.g. `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` or whatever the target's canonical is)
2. **Load the matching Path A logger** (one of the 5 logger Pines in `path-a-loggers/versions/`):
   - `LOGGER_HCT.pine` → for heavy-combo-toggles
   - `LOGGER_B2B_PUP.pine` → for b2b-pup
   - `LOGGER_HVDPBJPPD.pine` → for hvd-pbj-ppd
   - `LOGGER_TNT_OD.pine` → for tnt-od
   - `LOGGER_SQUARIFY.pine` → for squarify
3. **Point each `Source: ...` input on the logger** at the corresponding plot of the source indicator. Pine's `input.source()` shows a dropdown of the source indicator's plots.
4. **Save the layout** in TradingView so the configuration persists.

Once set up, the logger runs in real-time and on history; each fire produces a label that survives chart reloads (TradingView keeps the last ~500 labels per indicator).

## Querying via MCP (in a validation skill run)

The MCP tool — typical name `data_get_pine_labels` or `mcp__tradingview__data_get_pine_labels` (exact name depends on which MCP server Anish has installed) — takes:

- `indicator_id` (or `indicator_title`) — selects which loaded indicator's labels to return
- `symbol` (optional — defaults to active chart symbol)
- `timeframe` (optional — defaults to active chart timeframe)
- `limit` (optional — default 100)
- `since` (optional — ISO timestamp; default = all available)

Returns a list of label records with `{x, y, text, color, timestamp, bar_index, ...}`.

## Reading the labels

Logger labels follow a standard naming convention:

```
<canonical-name> | <indicator> | <bar_index> | <timestamp>
```

Example label text: `SAAB | heavy-pentagon | 8347 | 2026-05-08T14:35:00Z`.

Parse the label text to extract:
- `canonical_name` = first field
- `indicator` = second field
- `bar_index` = third field
- `timestamp` = fourth field

The PARENT agent of a Phase-3 subagent batches these into the fire-bar set.

## Subagent contract

A Phase-3 subagent receives ONE location + ONE logger, and returns the fire-bar set for that location. See `references/multi-agent-orchestration.md § Phase 3` for the full prompt template.

## Troubleshooting

### "Logger returns zero labels"

1. Is the logger loaded on the chart? (`/mcp` to check; the indicator should be in the list)
2. Is the `Source: ...` input pointing at the right plot of the source indicator? (dropdown shows the available plots from indicators on the chart)
3. Is the source indicator actually plotting that boolean? (some Tier-2 / aggregated alerts don't expose per-composite plots — see "Aggregated alert exception" below)
4. Has the chart loaded enough history? (5000-bar lookback is plenty for most validations; if the target fires rarely, query a longer window)

### "Logger plots labels but `data_get_pine_labels` returns empty"

1. Is the TradingView MCP connected? (`/mcp` should show "connected")
2. Is the `indicator_id` parameter correct? (some MCPs use the `shorttitle` field, some use the full title)
3. Are you querying the right symbol + timeframe? (labels are per-chart; if you queried a different chart, the result is empty)

### "Aggregated alert exception"

Some indicators (e.g. `heavy-uncap`) use a SINGLE aggregated `alert()` call that fires once per bar with a multi-target message. The individual composites don't have `alertcondition()` calls.

In these cases:
- The logger must read each composite's BOOLEAN directly (not its alert), via `input.source()` pointed at a `plot(<bool>, ..., display=display.none)` if the source indicator hides it
- If the source indicator doesn't expose the boolean at all, the validation must use Path B (Python ports) or manual fallback

This is a known limitation. Path A loggers work best for indicators that expose per-composite plots/alerts. Indicators that only expose aggregated alerts need source-indicator changes to add per-composite plots before Path A can validate them.

## Output schema

```yaml
target: <canonical-name>
location:
  indicator: <e.g. heavy-pentagon>
  variable: <e.g. sigSAAB>
fire_bars:
  - timestamp: 2026-05-08T14:35:00Z
    bar_index: 8347
    symbol: ES1!
    timeframe: 5m
  - ...
fire_count: <integer>
query_window:
  symbol: ES1!
  timeframe: 5m
  bars_available: 5000
status: COMPLETE | BLOCKED
blocked_reason: <if BLOCKED — see Troubleshooting>
```

This shape is what Phase 3 parent expects from each subagent.
