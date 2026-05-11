---
name: bull-bear-dialectic
description: Knowledge-worker skill. Given a diagnosis card from detection-plot-diagnosis, run the bull-case AND bear-case dialectic — each side writes its strongest case with confidence. Output is a dialectic transcript consumed by four-square-matrix. Per SD-008, neutral language only (bull-case / bear-case / dialectic; never good/evil).
---

# Bull-Bear Dialectic Skill — v1.0.0

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

### Step 1 — Bull-case construction

The bull-case agent reads the diagnosis card and writes the case that
the firing direction is the actual market direction. Required structure:

```
BULL-CASE
  Summary: <one sentence: why this fire predicts the firing direction>
  Supporting facts (from diagnosis):
    - <operand X fired with value Y, well above threshold Z>
    - <concurrent plot ABC fired in the same direction — confluence>
  Supporting facts (from situational context, if provided):
    - <context source DEF reports recent X consistent with bull case>
    - <4-satellite triangulation: 3 of 4 satellites agree bull>
  Self-confidence: <0.0 - 1.0>
  Strongest counter-argument (acknowledgment of bear-case):
    <one sentence — what would have to be true for bull-case to be wrong>
```

Hard requirement: the bull-case agent MUST write the
`Strongest counter-argument` field. It is the one place where
intellectual honesty is enforced. A bull-case that scores 0.95 and
says "no plausible counter-argument" is wrong by construction —
something always could go wrong; identify it.

### Step 2 — Bear-case construction

Symmetric. The bear-case agent reads the same diagnosis card AND the
bull-case's writing (full transparency — the agents see each other's
work) and writes the case that the firing direction is a TRAP, or that
the OPPOSITE direction is the actual market direction.

```
BEAR-CASE
  Summary: <one sentence: why this fire is a trap or why the opposite is true>
  Supporting facts (from diagnosis):
    - <contradicting concurrent plot DEF firing in opposite direction>
    - <hidden gate G is inactive that would have suppressed this fire>
  Supporting facts (from situational context, if provided):
    - <context source HIJ reports recent X consistent with bear case>
    - <historical analogue: same operand mix on this symbol → reversed>
  Self-confidence: <0.0 - 1.0>
  Strongest counter-argument (acknowledgment of bull-case):
    <one sentence — what would have to be true for bear-case to be wrong>
```

Same hard requirement: bear-case writes the bull-case acknowledgment.

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
