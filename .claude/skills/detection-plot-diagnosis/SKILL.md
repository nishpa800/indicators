---
name: detection-plot-diagnosis
description: Grunt-worker skill. Given a fire of any detection plot, extract the structured "diagnosis card" — what plot fired, what operand values were active, what offset was applied, what concurrent fires happened on the same bar. Pure tabulation; NO bull/bear judgment. Bread-and-butter for both bull-case and bear-case agents.
---

# Detection Plot Diagnosis Skill — v1.0.0

The bread-and-butter grunt-worker skill that ALL bull-case and bear-case
agents share. It produces the DIAGNOSIS CARD that the dialectic skill
consumes.

> Anish 2026-05-11: "They need to be good at identifying and diagnosing.
> Like, that's bread and butter. They diagnose."

## Hard rule: NO opinion

This skill produces ONLY descriptive facts. It does NOT:

- Assess whether the fire is bullish or bearish in conviction
- Score confidence
- Compare against historical analogues for "good" or "bad" outcomes
- Make any qualitative judgment

If you find yourself writing words like "strong", "weak", "convincing",
"trap", "real", "fake" — you have crossed into the dialectic skill's
job. Stop, strip those words, and continue.

This skill is the FIRST step. Diagnosis precedes interpretation. Per
the worker-tier contract, grunt workers don't opine.

## Inputs

- `plot_id` (required): the canonical name of the fired plot (e.g.
  `csNew3_Bull`, `det_b2bPUP`, `sigSuperBullPBJ`)
- `fire_context` (required):
  - `symbol` (string)
  - `tf` (timeframe)
  - `bar_ts` (ISO timestamp of the firing bar)
  - `bar_ohlcv` (the [O, H, L, C, V] for that bar)
- `pine_source_path` (optional): path to the canonical .pine file for
  resolving the plot's definition. Defaults to canonical per
  `bible-input/MANIFEST.md`.
- `python_port_path` (optional): path to the canonical Python port
  module for verifying operand values. Defaults to LATEST.txt in the
  family's `python_ports/` directory.

## Procedure

### Step 1 — Resolve the plot's definition

Look up the plot in:

1. The canonical Python port (preferred — it's the executable form)
2. Fallback: parse the canonical .pine file via the validate-detection-plot
   harness

Extract:
- The list of operand identifiers
- The boolean structure (AND/OR/NOT tree)
- The declared offset
- Any structural shifts (`nz([1])`, `nz([2])`, etc.)

### Step 2 — Compute operand values on the firing bar

For each operand:
- Pull its value as of the firing bar (using the same Python port that
  computed the parent fire — these are already cached in the bar's
  context)
- Record: operand name, value (true/false or numeric), the "lag" if any
  (e.g. `sigPentagon[1]` → record value at `bar_ts - 1 bar`)

### Step 3 — Determine offset semantics

Per Anish: "the skill to know that it's an offset of -1 and that you
still alert on the candle that is present even though the confluence
is on one candle before — that's a skill."

Record:
- Declared offset (e.g. -1, 0)
- Where the alert fires (= present candle, regardless of offset)
- Where the visual plot lands (= present candle + offset)
- Where the confluence ACTUALLY HAPPENED (= present candle + offset)

These three locations may diverge. The diagnosis card distinguishes
them clearly.

### Step 4 — Collect concurrent fires

For the same `bar_ts`, query all known canonical Python ports / Pine
sources for any other plot that fired on this bar. Record:
- Plot name
- Family
- Direction (bull / bear / neutral)

Use the candle-confluence-counter grunt-worker skill (TBD) for the
heavy lifting.

### Step 5 — Capture IPSF snapshot

Record the active IPSF parameter values from the canonical Python
port's `DEFAULTS` dict. This makes the diagnosis card REPRODUCIBLE — if
defaults change later, we can re-run the diagnosis with the old
snapshot and confirm idempotency.

### Step 6 — Emit the diagnosis card

Write to: `docs/agentic-os/diagnosis-cards/<plot_id>/<bar_ts_iso>-<symbol>-<tf>.md`

Schema:

```yaml
schema_version: 1
plot_id: <e.g. csNew3_Bull>
fire_id: <symbol>-<tf>-<bar_ts>-<plot_id>
diagnosed_at: <iso>
diagnoser_skill: detection-plot-diagnosis@v1.0.0

# What the plot IS
plot_definition:
  pine_source: <path>:<line>
  python_port: <path>:<function>
  boolean_structure: |
    csNew1_Bull AND csNew2_Bull           # (paste the resolved boolean)
  declared_offset: 0
  structural_shifts:
    - operand: csNew2_Bull
      shift_bars: -1
      reason: "nz(csNew2_Bull[1]) — lagged AND per Group A canonical"

# What the operands DID on this bar
operand_values:
  csNew1_Bull:
    value: true
    bar_ts_used: 2026-05-11T14:30:00Z   # current bar
  csNew2_Bull:
    value: true
    bar_ts_used: 2026-05-11T14:25:00Z   # 1 bar prior (per shift)

# Offset semantics
offset_semantics:
  declared_offset_bars: 0
  alert_fires_at_bar_ts: 2026-05-11T14:30:00Z   # present candle
  visual_plot_at_bar_ts: 2026-05-11T14:30:00Z   # = alert (offset 0)
  confluence_actually_at_bar_ts: 2026-05-11T14:30:00Z

# Context
fire_context:
  symbol: TSLA
  tf: 5m
  bar_ts: 2026-05-11T14:30:00Z
  bar_ohlcv: [O, H, L, C, V]

# Concurrent fires on the same bar
concurrent_fires:
  - {plot: sigBullRVOL1x, family: heavy-pentagon, direction: bull}
  - {plot: det_bullNapalmCons, family: tnt-od, direction: bull}

# IPSF snapshot
ipsf_snapshot:
  matrix_lookback: 67
  rvol_1x_mult: 1.0
  disp_sigma_mult: 6.0
  fauna_lookback: 20

# Provenance
notes_freeform: |
  (One paragraph max. Pure descriptive observations only — NO bull/bear
  judgment. Example: "PUP fired with body% of 4.2% (well above 3%
  threshold). Pentagon was active on this bar, contributing to the
  comboset2 OR branch.")
```

## Outputs

1. `docs/agentic-os/diagnosis-cards/<plot_id>/<fire_id>.md` — the
   per-fire diagnosis card
2. (Optional) Append to `docs/agentic-os/diagnosis-cards/<plot_id>/INDEX.md`

## Standing approval

Per the agentic-OS standing approval block: ANY file write permitted,
NO file deletion (SD-004). Standing decisions in
`docs/agentic-os/STANDING_DECISIONS.md` apply.

## Idempotency

Same `fire_id` + same `pine_source_path` + same `python_port_path` +
same `ipsf_snapshot` → same diagnosis card. If invoked twice, the
second invocation should produce a byte-identical card. If it doesn't,
something changed (port revision, Pine revision) and the diff is
informative.

Per SD-002, never overwrite. If a re-diagnosis is needed, write to
`<fire_id>__rev2.md` and document the supersession in INDEX.md.

## Composition

This skill is FIRST in the chain. The dialectic skill consumes its
output:

```
detection-plot-diagnosis
        ↓ produces diagnosis card
bull-bear-dialectic (consumes card, runs the conversation)
        ↓ produces dialectic transcript
four-square-matrix (consumes transcript, emits the matrix payload)
```

Each skill has a single tier (grunt / knowledge / output) and a single
job. Per the WORKER_TIERS.md contract.

## What NOT to do

- Do NOT score confidence — that's the dialectic skill's job
- Do NOT compare to historical analogues — that's the
  historical-analogue-search grunt skill's job (TBD)
- Do NOT reason about whether this fire is "good" or "bad" — that's
  the dialectic + four-square-matrix skills' job
- Do NOT skip the IPSF snapshot — it makes the card reproducible
- Do NOT use the "good vs evil" / "heaven vs hell" / "angel / devil"
  language anywhere in the card per SD-008. Stay descriptive.
