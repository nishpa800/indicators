---
name: axis-decomposition
description: Decompose a fire event or strategy proposal along the 12 canonical axes the OS uses (timeframe, direction, structure, momentum, volume, regime, session position, catalyst, institutional positioning, options skew, ETF rotation, GPS satellite agreement). Output a structured axis-card — pure tabulation, no judgment. Grunt-tier skill, the structured prefix to every diagnosis card.
when_to_use: Invoke at the start of every per-fire chain BEFORE detection-plot-diagnosis. Also invoke at the start of every strategy review chain (Krishna + Shiva + Premortem + Inversion + Pareto). Anywhere we need to ensure a thing is being analyzed along multiple independent dimensions instead of one collapsed view.
tier: grunt
---

# Axis Decomposition

**Tier**: grunt-worker (calculation + tabulation; no opining).

**Purpose**: Force every analyzed object — a fire, a setup proposal, a strategy review — to be decomposed along 12 canonical axes. The axes are independent. The output is a structured key-value map that downstream knowledge workers consume.

## Input

```yaml
object:
  type: fire | setup | strategy | new_plot_proposal
  fire_id: <optional — required when type=fire>
  symbol: <ticker>
  tf: <timeframe>
  bar_ts: <iso>
  plot_name: <optional — required when type=fire>
  setup_summary: <optional — required when type=setup|strategy|new_plot_proposal>
```

## Output — the axis-card

```yaml
axis_card:
  timeframe:            "1m" | "5m" | "15m" | "1h" | "1d"
  direction:            "bull" | "bear" | "neutral"
  structure:            "floor" | "second_floor" | "rooftop" | "penthouse" | "unconstrained"
  momentum:             "disp_on_bull" | "disp_on_bear" | "off"
  volume_tier:          "HV" | "HV1000" | "HV150" | "off"
  regime:               "trend" | "range" | "gap_up" | "gap_down" | "inside_day"
  session_position:     "pre_market" | "open_30" | "mid" | "power_hour" | "after_hours"
  catalyst:             "earnings_window" | "news_window" | "none"
  institutional:        "top_quartile_13f" | "bottom_quartile_13f" | "no_data"
  options_skew:         "heavy_call" | "heavy_put" | "balanced" | "unavailable"
  etf_rotation:         "sector_inflow" | "sector_outflow" | "neutral"
  satellite_agreement:  0 | 1 | 2 | 3 | 4
  satellite_direction:  "bull" | "bear" | "mixed" | "unavailable"
```

## Procedure

1. **Timeframe / direction / plot-derived axes** — read directly from input. No inference.
2. **Structure axis** — query the Pine source's plot lineage. If the fire is on Floor/2F/Rooftop/Penthouse, record verbatim. Else `unconstrained`.
3. **Momentum / volume / regime axes** — query the indicator port's `STATE_MACHINES` and `DETECTIONS` registries at the fire bar.
4. **Session position axis** — derive from `bar_ts` against the symbol's session calendar. Pre-market <09:30 ET; open_30 09:30–10:00; mid 10:00–14:30; power_hour 14:30–16:00; after_hours >16:00.
5. **Catalyst axis** — query the Benzinga DS pair grunt for events within (bar_ts - 24h, bar_ts + 24h). If earnings_window: -1 trading day to +1 trading day around earnings release. If news_window: any Benzinga news in (bar_ts - 4h, bar_ts).
6. **Institutional axis** — query the WhaleWisdom 13-F DS pair grunt for the symbol's most recent quarter. Quartile rank derived from net-buy quantity across reporting institutions.
7. **Options skew axis** — query the options DS pair grunt for current 30-day put/call ratio + skew (25-delta put vs 25-delta call IV).
8. **ETF rotation axis** — query the etf-rotation DS pair grunt for the symbol's sector ETF; classify by 5-day flow direction.
9. **Satellite axes** — invoke the `four-satellite-triangulator` grunt skill for `bar_ts` on `symbol/tf`. Record N-of-4 agreement count and dominant direction.

## Hard rules

- This skill does NOT opine. No confidence scores. No "should we trade this." Pure tabulation.
- If any axis data is unavailable, the value is the explicit "unavailable" / "no_data" / "neutral" sentinel. NEVER guess.
- The axis-card is the structured prefix to every diagnosis card. Order matters: axis-card always comes FIRST in the per-fire payload.

## Output destination

Per-fire: appended as `axis_card` field in the per-fire payload at `docs/agentic-os/debates/<plot>/<date>-<fire_id>.md`.

Strategy review: written to `docs/agentic-os/strategy-reviews/<date>-<setup-slug>/axis-card.yaml`.

## Why 12 axes (not 5, not 20)

Five collapses axes that have separate predictive value (e.g. structure ≠ regime). Twenty over-fits and creates co-variance illusion. Twelve is the minimum that preserves the independent dimensions Anish names as load-bearing. New axes may be added in future SD entries; existing axes never get removed (per SD-002, SD-004).

## Cross-references

- Pillar definition: `docs/agentic-os/strategy/2026-05-11-agentic-os-full-build-spec.html` §2 Pillar 1.
- Consumed by: `detection-plot-diagnosis`, `bull-bear-dialectic` (via diagnosis card), `krishna-steelman`, `shiva-redteam`, `premortem`.
- Depends on: `four-satellite-triangulator` (G3, TODO), Benzinga DS pair (Stage 4), WhaleWisdom DS pair (Stage 4).
