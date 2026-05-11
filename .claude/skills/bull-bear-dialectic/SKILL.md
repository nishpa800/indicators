---
name: bull-bear-dialectic
description: Knowledge-worker skill. Runs the POST-SETUP OUTCOME dialectic — given a confirmed diagnosis card, both sides accept the setup direction and debate whether the market will FOLLOW it (compliance) or DEFY it (the "magical" reversal cell per SD-010). Output is a dialectic transcript consumed by four-square-matrix. Neutral language per SD-008.
---

# Bull-Bear Dialectic Skill — v1.1.0 (corrected per SD-010)

> **CRITICAL FRAMING (SD-010)**: The dialectic does NOT debate whether
> the setup is real. The setup is OBJECTIVELY confirmed by the diagnosis
> card. Both sides ACCEPT the setup direction. They debate **outcome
> alignment** — will the market follow the setup, or defy it?
>
> Example: a bar closes with all-bearish operands (RVOL bear, PPD, PB,
> DISP bear, FAUNA bear). Diagnosis card: BEAR SETUP, confirmed. The
> dialectic asks: over the next N bars, will the market move bear
> (setup followed) or bull (setup defied — the order-block / divine-
> reversal case)? Both sides accept the bear setup as truth; they
> disagree on what the market will do next.

The knowledge-worker skill at the heart of the agentic OS. It runs the
DIALECTIC: a structured conversation between a bull-case agent and a
bear-case agent over a single fire's diagnosis card.

> Anish 2026-05-11: "Then we're getting into the conversation of hell
> versus heaven. That's a different skill."

This skill SUPERSEDES the v1.0 monolithic `bull-vs-bear-debate` skill.
The previous skill remains in `.claude/skills/bull-vs-bear-debate/` for
traceability per SD-002 but should not be invoked for new work.

## What this skill is NOT

- It does NOT produce the 4-square confidence matrix (that's
  `four-square-matrix`'s job)
- It does NOT diagnose what fired (that's `detection-plot-diagnosis`'s
  job)
- It does NOT execute trades or recommend position sizes
- It does NOT use moralistic framing (good / evil / angel / devil) in
  its output. Per SD-008, the dialectic is BALANCE — bull-case and
  bear-case are equally valid and equally necessary.

## Inputs

- `diagnosis_card_path` (required): path to the card produced by
  `detection-plot-diagnosis`
- `situational_context_packet` (optional): bundle of contextual data
  from `situational-context-share` skill (TBD); contains earnings
  windows, vol-footprint reads, 4-satellite-triangulation, etc.
- `prior_calibration` (optional): if the Plot Owner has accumulated ≥30
  prior matrices for this plot/symbol/TF, the rolling priors. Used to
  anchor confidence scoring.

## Procedure

### Step 0 — Inherit the diagnosis

Read the diagnosis card. Verify:
- It exists
- It was diagnosed within the last 24 hours (otherwise stale; re-run
  diagnosis first)
- The IPSF snapshot matches the active canonical port's DEFAULTS

If any check fails, abort and emit a marker for the Plot Owner.

### Step 1 — Compliance case construction (setup-direction outcome)

Read the diagnosis card. Note the SETUP DIRECTION (bull or bear). The
COMPLIANCE-case agent argues the market WILL FOLLOW the setup direction
over the outcome window. Required structure:

```
COMPLIANCE-CASE (setup_direction = <bull|bear>, outcome = same)
  Summary: <one sentence: why the market will follow the setup direction>
  Supporting facts (about the setup's strength — diagnosis-derived):
    - <operand X fired strongly — signal magnitude high>
    - <concurrent plot ABC fired in same direction — confluence supports compliance>
  Supporting facts (about market behavior — situational context):
    - <session position favorable: e.g. mid-session trend continuation>
    - <historical analogue: same operand mix on this symbol → compliance >70% N times>
    - <4-satellite triangulation: high-conviction zone agrees with setup>
    - <regime / data-source context: e.g. ETF rotation aligned with setup>
  Self-confidence: <0.0 - 1.0>
  Strongest counter-argument (acknowledgment of defiance-case):
    <one sentence — what condition would make the market defy this setup>
```

Hard requirement: the compliance-case agent MUST write the
`Strongest counter-argument` field. A compliance-case at 0.95 that says
"no plausible defiance" is wrong by construction — the market always
can surprise.

### Step 2 — Defiance case construction (the magical reversal)

The DEFIANCE-case agent reads the same diagnosis card AND the compliance
case's writing (full transparency) and argues the market WILL DEFY the
setup direction — i.e. move OPPOSITE to what the operands predict.

This is the "order block / divine reversal" case Anish describes: the
bearish setup that is actually a smart-money accumulation zone; the
bullish setup that is the distribution top. Per SD-010, this cell is
where the "magical trait" lives — recognizing when a confirmed bear
setup is the bullish entry.

```
DEFIANCE-CASE (setup_direction = <bull|bear>, outcome = opposite)
  Summary: <one sentence: why the market will move OPPOSITE to the setup>
  Supporting facts (location / structural reasons setup-direction-defies):
    - <bar location is at a known OB / supply zone / S-R level → reversal probable>
    - <volume profile context: this level has been the bottom in N prior touches>
    - <session position: setup formed at session-open — common fakeout window>
    - <higher-TF context: setup is bear but daily trend is firmly bull>
  Supporting facts (situational context — data sources):
    - <Benzinga: catalyst about to break in opposite direction (earnings T-1)>
    - <13F: institutional positioning skewed opposite to setup direction>
    - <historical anti-analogue: same exact operand mix here → reversed N% of last M>
  Self-confidence: <0.0 - 1.0>
  Strongest counter-argument (acknowledgment of compliance-case):
    <one sentence — what condition would make the market follow the setup>
```

Same hard requirement: defiance-case writes the compliance acknowledgment.

NOTE: Both agents ACCEPT the diagnosis card as truth. They do NOT debate
whether the bull/bear operands really fired — that's diagnosis's job and
the canonical Python port computes it deterministically. They debate
ONLY market outcome over the configured `outcome_window` (e.g. next 5
bars, next session, next confirmation cycle).

### Step 3 — Reconciliation pass

Both cases are read together by the dialectic process (the same skill
invocation, no third agent). The reconciliation:

1. Verify each side's `Strongest counter-argument` is non-trivial — if
   either side wrote "no plausible counter-argument", flag the dialectic
   as incomplete and re-run that side.
2. Sum the self-confidences. If sum > 1.05 or sum < 0.95, the
   dialectic is mis-calibrated — note it and proceed (the matrix
   skill's calibration step will normalize).
3. Identify points of agreement (facts both sides cite without dispute)
   and points of disagreement (facts each side interprets oppositely).

### Step 4 — Emit the dialectic transcript

Write to:
`docs/agentic-os/dialectics/<plot_id>/<bar_ts_iso>-<symbol>-<tf>-<dir>.md`

Schema:

```yaml
schema_version: 1
fire_id: <from diagnosis card>
diagnosed_at: <from diagnosis card>
dialectic_run_at: <iso>
dialectic_skill: bull-bear-dialectic@v1.0.0

# Inputs
diagnosis_card: <relative path>
situational_context_packet: <relative path or null>
prior_calibration:
  observations: <N>
  bull_case_baseline: <0.0 - 1.0>
  bear_case_baseline: <0.0 - 1.0>

# Bull-case
bull_case:
  summary: |
    <one sentence>
  supporting_facts_diagnosis:
    - <fact>
  supporting_facts_context:
    - <fact>
  self_confidence: 0.65
  strongest_counter_argument: |
    <one sentence>

# Bear-case
bear_case:
  summary: |
    <one sentence>
  supporting_facts_diagnosis:
    - <fact>
  supporting_facts_context:
    - <fact>
  self_confidence: 0.35
  strongest_counter_argument: |
    <one sentence>

# Reconciliation
reconciliation:
  confidence_sum: 1.00
  calibration_status: ok | over | under
  points_of_agreement:
    - <fact>
  points_of_disagreement:
    - <fact, with each side's interpretation>

# Notes
notes_freeform: |
  <one paragraph from the dialectic process. Neutral language per SD-008.>
```

### Step 5 — Append to dialectic index

Append a one-line summary to:
`docs/agentic-os/dialectics/<plot_id>/INDEX.md`

```
| <bar_ts> | <symbol> | <tf> | <dir> | bull_conf | bear_conf | calibration | notes |
```

## Standing approval

Per agentic-OS standing approval. NO file deletion (SD-004). Standing
decisions inherited.

## Composition

```
detection-plot-diagnosis (grunt) → produces diagnosis card
        ↓
bull-bear-dialectic (knowledge — THIS SKILL) → produces dialectic transcript
        ↓
four-square-matrix (output) → produces per-fire payload
```

## Idempotency

Same diagnosis card + same situational context + same prior calibration
→ should produce a STRUCTURALLY equivalent dialectic (same supporting
facts cited; same direction of reasoning; confidences within ±0.05). If
two runs diverge wildly, something non-deterministic in the agent's
reasoning is happening — flag for review.

Per SD-002, never overwrite. Re-runs go to `<fire_id>__rev2.md`.

## Hard guardrails

- NO file deletion (SD-004)
- NO modification of the diagnosis card (it's input, not workspace)
- NO use of moralistic language (good / evil / angel / devil / God /
  Satan / heaven / hell) in any output. Per SD-008.
- NO confidence above 0.95 or below 0.05 — never claim certainty,
  never claim impossibility. The market always surprises.
- BOTH bull-case and bear-case MUST be written, even if one is much
  stronger than the other. The weak side's strongest argument is still
  written.

## Why this skill is split from diagnosis and four-square-matrix

Per Anish's worker-tier guidance: each skill does ONE thing. This
skill REASONS. It doesn't tabulate (diagnosis does that). It doesn't
calibrate-against-priors-and-emit-the-final-matrix (the matrix skill
does that). Splitting the skills lets a Plot Owner re-run JUST the
dialectic on a fire when the situational context changes, without
re-doing the diagnosis or the matrix calibration.

## What NOT to do

- Do NOT execute the four-square-matrix step inline. Emit the
  dialectic transcript and let the matrix skill consume it.
- Do NOT seek "the right answer" — both cases get serious construction
  even when one feels obviously stronger. The matrix skill will weight.
- Do NOT skip the strongest-counter-argument step. It's the only
  enforcement of intellectual honesty in the OS.
- Do NOT pause to ask Anish for confirmation. Standing approval is on.
