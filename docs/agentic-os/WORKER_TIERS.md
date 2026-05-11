# Worker Tiers

_Authored 2026-05-11. Companion to ARCHITECTURE.md and THESIS.md._

The agentic OS has three worker classes. Clear contract between them.
Grunt workers don't opine; knowledge workers don't tabulate; owners
don't do either.

## Tier 0 — Grunt Workers (calculation + tabulation)

What they do: turn raw data into structured facts. Mechanical,
verifiable, deterministic.

What they DON'T do: opine, advocate, reason about market direction,
score confidence.

Their skills (each a separate `.claude/skills/<name>/`):

| Skill | Job |
|---|---|
| `detection-plot-diagnosis` | Given a fire, extract: what plot fired, what operand values were active, what offset was applied, what concurrent fires happened. Output: structured "diagnosis card." Bread and butter. |
| `offset-application` | Apply a declared offset (commonly 0 or -1) to a boolean stream. Confirm the alert fires on the present bar even when the confluence is on a prior bar. Pure mechanics. |
| `candle-confluence-counter` | Given a bar timestamp, count how many named plots fired on that bar across an indicator family. Output: count + list. |
| `operand-breakdown` | Given a composite plot's fire, decompose into per-operand truth values. Used by diagnosis. |
| `pine-source-byte-diff` | Given two .pine files, compute the byte-level diff for a named identifier's RHS. Used by audit task workers. |
| `python-port-smoke-test` | Given a Python port module, import it and verify DETECTIONS / STUBBED / STATE_MACHINES counts match the audit report. |
| `yaml-extract-merge` | Run tools/merge_extracts.py and assert YAML==JSON. Used after any extract-*.yaml edit. |

Pattern: each skill takes structured input, produces structured output,
no judgment. They are trivially callable from any owner or knowledge
worker.

Future grunt-worker skills (deferred):

- `bar-context-fetch` — pull OHLCV + preceding 5 bars for a given (symbol, TF, timestamp).
- `historical-analogue-search` — find prior bars with similar operand mix on the same symbol/TF.
- `data-source-ingest` — pull from Benzinga / 13F / options / ETF rotation feeds and normalize.

## Tier 1 — Knowledge Workers (strategy + reasoning)

What they do: consume grunt-worker output, reason over it, produce
strategic conclusions and confidence scores.

What they DON'T do: re-tabulate (they trust the grunt-worker output),
make execution decisions (those happen at Owner level).

Their skills:

| Skill | Job |
|---|---|
| `bull-bear-dialectic` | Given a diagnosis card, run the bull-case AND bear-case agents in dialogue. Each writes its strongest argument with confidence. Output: dialectic transcript. Per SD-008, neutral language only. |
| `four-square-matrix` | Given a dialectic transcript + the firing direction, collapse to the 2x2 confidence matrix. Apply long-run prior calibration if available. Output: per-fire payload per SD-007. |
| `situational-context-share` | Given a fire context, pull recent context from data-source pairs (Benzinga, 13F, etc.), summarize, and inject into the dialectic input. |
| `dialectic-self-review` (TBD) | Weekly per Plot Owner. Reads the past N matrices for one plot, identifies systematic biases (e.g. bear-case agent over-confident at session open), proposes adjustments to its own reasoning. |
| `cross-plot-debate` (TBD) | When 2+ Plot-Owned plots fire on the same bar, run a meta-dialectic that integrates their individual matrices. |
| `long-run-calibration` (TBD) | Nightly per Plot Owner. Aggregates per-fire payloads into the long-run 4-square calibration table. |

Pattern: each skill takes grunt-worker output (or another knowledge
worker's output), produces a structured reasoning artifact. The dialectic
skill is the only one that has free-form reasoning text; everything else
is structured.

## Tier 2 — Owners (orchestration)

What they do: persistent chat threads (one per Indicator family bull/bear,
one per Plot Owner). They receive events, decide which grunt + knowledge
workers to invoke, sequence the calls, accumulate context across days.

What they DON'T do: tabulate or reason directly. They assemble.

Owner skills (the meta-level):

| Skill | Job |
|---|---|
| `owner-event-triage` (TBD) | Given an incoming event (TV firing, drift report, fire from realtime), classify and route. |
| `owner-handoff` (TBD) | When the Indicator Owner needs Plot Owner authority on a cross-family plot question, write to the Plot Owner's inbox file. |
| `owner-memory-update` | Append today's findings to the owner's persistent memory file (`docs/agentic-os/memory/<role>__<name>.md`). |

Owners are the only tier with conversational persistence. They are the
"chat threads" Anish opens to talk about a specific indicator or plot.

## The contract

| Tier | Inputs | Outputs | Has free-form reasoning? |
|---|---|---|---|
| 0 (grunt) | raw data + structured request | structured facts | NO |
| 1 (knowledge) | structured facts (from grunt) | structured reasoning + confidence | YES (in dialectic only) |
| 2 (owner) | events + tier-0/1 outputs | sequenced workflow + memory updates | YES (in owner memory) |

Violations:
- A grunt worker that opines → reclassify as knowledge worker.
- A knowledge worker that re-tabulates → use the grunt-worker output
  instead; don't duplicate.
- An owner that tabulates or reasons directly → dispatch to the right
  worker; if a worker doesn't exist for the task, that's a missing
  skill — author it.

## Why three tiers (not two, not five)

Two tiers (worker + owner) loses the grunt-vs-knowledge distinction
which is THE distinction Anish drew explicitly: "calculating and
tabulating, that is literally the easiest thing in the world. But when
you do it in scale, that's a skill."

Five tiers (microservice-style decomposition) over-engineers a problem
that doesn't need it. Anish: "if we simplify it, we'll keep getting
better, and I think we should simplify it, really."

Three is the minimum that lets us ENFORCE the contract. Mechanical work
is offloaded to grunts; reasoning is concentrated in the dialectic;
orchestration sits with owners. Each tier is the right level of
delegation for its concern.

## Cost model implication

Grunt workers are TINY token consumers — structured in, structured out,
no reasoning. They run frequently and cheaply. Knowledge workers are
heavier — the dialectic is the most token-intensive single act in the
system. Owners run rarely (per-event, not per-fire) and accumulate
context over days.

For Max-plan budgeting:
- ~100-200 fires/day × ~3K tokens per dialectic = 300K-600K tokens/day
  on knowledge workers
- ~20K tokens/day per owner × ~30 owners = 600K tokens/day on owners
- Grunt workers: ~10K tokens per invocation × ~500 invocations/day =
  5M tokens/day on grunt workers (the heaviest consumer at scale, but
  they're the most parallelizable and the most cacheable)

Total: roughly 6M tokens/day at full deployment. Fits comfortably in
Max with headroom. Concrete budgets per role TBD when first owners go
live.
