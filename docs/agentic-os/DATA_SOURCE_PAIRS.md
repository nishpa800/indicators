# Data Source Pairs

_Authored 2026-05-11. Companion to ARCHITECTURE.md / THESIS.md._

Per Anish 2026-05-11: every external data feed gets a bull-case agent AND
a bear-case agent of its own. Their output is contextual input to Plot
Owner dialectics — situational context that conditions every per-fire
matrix.

> Anish: "We're gonna need a... we're gonna need a two agents for volume
> footprints, two agents — collision barriers, that is. Two agents for
> volume session analysis. Two agents for TPO."

This decision is recorded as SD-009 in `STANDING_DECISIONS.md`.

## Data sources (first-wave roster)

| Data source | Bull-case agent | Bear-case agent | Ingest grunt worker | Status |
|---|---|---|---|---|
| Benzinga news | `DS::benzinga-news::bull` | `DS::benzinga-news::bear` | `gw-benzinga-news-ingest` | not yet hired |
| Benzinga earnings calendar | `DS::benzinga-earnings::bull` | `DS::benzinga-earnings::bear` | `gw-benzinga-earnings-ingest` | not yet hired |
| 13F filings | `DS::13f::bull` | `DS::13f::bear` | `gw-13f-ingest` | not yet hired |
| Options historical | `DS::options-hist::bull` | `DS::options-hist::bear` | `gw-options-hist-ingest` | not yet hired |
| ETF rotation | `DS::etf-rotation::bull` | `DS::etf-rotation::bear` | `gw-etf-rotation-ingest` | not yet hired |
| Volume footprint | `DS::vol-footprint::bull` | `DS::vol-footprint::bear` | `gw-vol-footprint-ingest` | not yet hired |
| Volume session (collision barriers) | `DS::vol-session::bull` | `DS::vol-session::bear` | `gw-vol-session-ingest` | not yet hired |
| TPO | `DS::tpo::bull` | `DS::tpo::bear` | `gw-tpo-ingest` | not yet hired |

= 8 data sources × 2 agents + 8 ingest grunts = 24 agents in the data
layer. Plus the existing 24 Indicator Owners + 4 Plot Owners (current
roster) = 52 total agent identities at full first-wave deployment.

## What each pair owns

A `DS::<source>::<dir>` agent owns:

- **Source mapping**: how raw data from this feed translates to a
  trading-relevant signal in their direction. E.g.
  `DS::benzinga-news::bull` knows: "FDA approval news" or "earnings
  beat" or "buyback announcement" or "guidance raise" → bull-case
  context. `DS::benzinga-news::bear` knows the symmetric set.
- **Memory file**: `docs/agentic-os/memory/DS__<source>__<dir>.md`
  accumulates the agent's running understanding of the source over
  time.
- **Per-event interpretation log**: every event from the source gets
  a one-line interpretation by both bull and bear agents, logged at
  `docs/agentic-os/data-source-events/<source>/<date>.md`.

## How data-source agents feed the dialectic

When a Plot Owner runs a debate via `bull-bear-dialectic`, it invokes
`situational-context-share` (TBD). That skill:

1. Identifies the firing bar's (symbol, TF, timestamp) context window
   (typically -7 days to +0 hours from fire).
2. Queries each data-source pair for events within the window relevant
   to the symbol.
3. Pulls the bull-case AND bear-case interpretation of each event.
4. Bundles into a "situational-context packet" that is appended to the
   dialectic's input.

The bull-case agent of `bull-bear-dialectic` reads the bull-case
interpretations from each data source. The bear-case agent reads the
bear-case interpretations. Each side gets context from the same source
events but each interprets through its own lens.

Critical: the bull-case data-source agent does NOT filter out bear-case
events. It reads the same Benzinga news (e.g. "guidance lowered") that
the bear-case agent reads — but it argues "this might be a clearing
event, the bottom is in." The agents bias toward their direction; they
don't censor the data.

## Initial hiring order (priority)

Hire in this order as the system needs context:

1. `DS::benzinga-earnings::*` — earnings windows are the most
   predictive context for short-term plot reliability.
2. `DS::vol-session::*` (collision barriers) — directly informs the
   plot owner debates because session-level barriers shape every fire.
3. `DS::vol-footprint::*` — bar-level confirmation/disconfirmation of
   the fire's quality.
4. `DS::tpo::*` — structural context (value-area, point-of-control).
5. `DS::etf-rotation::*` — multi-day directional bias for the symbol's
   sector.
6. `DS::options-hist::*` — IV / OI / unusual flow context.
7. `DS::benzinga-news::*` — event-driven catalysts.
8. `DS::13f::*` — quarterly institutional positioning (lowest-frequency
   but largest-position-size context).

## Why bull AND bear for each data source (not one neutral analyst)

Same reasoning as SD-005 (Indicator Owners are split). A neutral
analyst rubber-stamps the headline read. Two adversarial agents
guarantee the bear-case interpretation of "earnings beat" gets
constructed even when it would be inconvenient (e.g. "buy-the-rumor,
sell-the-news" pattern; or "beat-but-guided-down" pattern). Symmetric
on the bull side: an "earnings miss" gets a serious bull-case
construction (e.g. "kitchen-sink-quarter, all-bad-news-out, bottom is
in").

The dialectic skill at the Plot Owner layer THEN consumes both
interpretations and adjudicates per-fire.

## Sustainability

Data-source agents are NOT realtime-streaming. They are ON-DEMAND:

- The bull/bear pair is invoked when `situational-context-share`
  queries them for a specific fire's context window.
- Outside of fire-driven invocations, they run only on a daily
  context-refresh schedule (one invocation per day per pair to
  pre-process recent events).

Daily compute estimate: 16 data-source agents × ~3K tokens per daily
refresh + ~16 × ~1K tokens per fire-time invocation × ~150 fires/day
= ~50K + ~2.4M tokens/day = ~2.5M tokens/day. Fits in Max budget.

## What's NOT built today

- The data-source agents themselves (none hired)
- The `situational-context-share` skill
- The ingest grunt workers
- Connectors to Benzinga / 13F / options / ETF / vol-footprint /
  vol-session / TPO data feeds

Today's deliverable is the architecture and the standing decision
(SD-009). Hiring starts after the first Plot Owner (`PO::unified-combo`)
demonstrates the dialectic skill works end-to-end without external
context, then earnings-calendar context goes in first as the most
high-leverage augmentation.
