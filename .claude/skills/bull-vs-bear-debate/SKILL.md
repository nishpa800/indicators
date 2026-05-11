---
name: bull-vs-bear-debate
description: Use when a Plot Owner needs to evaluate a single fire of an owned detection plot. Runs the Heaven-vs-Hell debate (angel case + devil case) and emits the 4-square confidence matrix per SD-007. Plot Owners invoke this skill on every fire of their owned plot.
---

# Bull-vs-Bear ("Heaven vs Hell") Debate Skill — v1.0.0

This skill codifies the per-fire debate procedure that every Plot Owner runs
on every fire of their owned plot. Output: a structured 4-square confidence
matrix payload appended to the plot's debate log.

## When to invoke

- A new fire of a Plot-Owned detection plot enters the system (real-time
  Path-M event OR a back-test re-evaluation OR a manual Anish-driven query)
- Required input: the fire's full context (symbol, TF, bar timestamp,
  preceding 5 bars, concurrent plot fires, the operands' raw values per the
  active IPSF settings)

Not for:
- Aggregate / multi-fire calibration (use `calibration-rollup` skill —
  deferred)
- Indicator-Owner-level direction debates that don't reduce to a single
  named plot fire (those happen in chat)

## Standing approval

This skill operates under the same UNLIMITED APPROVAL block as
`detection-plot-validation`:

- ANY file write, ANY directory create, ANY tool use is permitted
- ONE hard restriction: NO file deletion (per SD-004)
- Standing decisions in `docs/agentic-os/STANDING_DECISIONS.md` apply

## Procedure (non-skippable)

### Step 1 — Collect evidence

Pull, in order:
1. Bar context: `(symbol, tf, bar_ts, ohlcv)` for the firing bar AND the
   preceding 5 bars
2. Concurrent plot fires: every other detection plot that fired on the same
   bar. Group by family.
3. Operand-level breakdown: for the Plot-Owned plot, what was the value of
   EACH operand on this bar? E.g. for csNew3: was Pentagon firing? Which
   of the 5 OR-confluence operands of comboSet3 fired? Was the FAUNA bar
   strong or weak?
4. IPSF settings snapshot: the current `DEFAULTS` of the plot's canonical
   Python port (so the debate is reproducible later if defaults change)
5. Historical analogues: prior fires of this same plot on this same symbol
   over the last 90 days, with their post-fire outcome (5-bar return,
   10-bar return, eventual reversal flag). If no history, mark as
   "no-prior".

### Step 2 — Angel case (direction-of-fire)

Write a paragraph arguing this fire is "true" — i.e. the firing direction
is the actual market direction. Required structure:

```
ANGEL CASE (P(TRUE_<DIR>) high):
  Summary: <one sentence on why this fire is genuine>
  Supporting facts:
    - <operand X fired strongly: value Y, threshold Z>
    - <concurrent plot ABC also firing: confirms confluence>
    - <historical analogue: bar TS in the past, same operand mix, +N% in 5 bars>
    - <continuation pattern in preceding 5 bars: e.g. higher highs and lows>
  Confidence (angel): <0.0 - 1.0>
```

### Step 3 — Devil case (opposite-of-fire)

Write a paragraph arguing this fire is a TRAP — i.e. the OPPOSITE direction
is the actual market direction. Required structure:

```
DEVIL CASE (P(<OPPOSITE>_DRESSED_AS_<DIR>) high):
  Summary: <one sentence on why this fire is a trap / order block / reversal>
  Supporting facts:
    - <contradicting plot DEF firing in opposite direction>
    - <hidden gate G would have suppressed this fire if active: rationale>
    - <historical anti-analogue: bar TS in the past, same operand mix, REVERSED in 5 bars>
    - <preceding 5 bars showing exhaustion / over-extension / divergence>
    - <FVG / order-block context: this fire might be the smart-money fade>
  Confidence (devil): <0.0 - 1.0>
```

### Step 4 — Adjudicate

`angel_confidence + devil_confidence = 1.0` (within the row of the firing
direction). Use prior calibration if PO has accumulated ≥30 fires:

```
if prior_calibration_available:
    base_angel = prior[fire_dir][TRUE]   # historical P(true | this dir fired)
    adjustment = (per-fire-evidence delta from baseline, in [-0.3, +0.3])
    angel_confidence = clip(base_angel + adjustment, 0.05, 0.95)
else:
    # cold-start: 60/40 in favor of angel as default prior
    angel_confidence = 0.60 + adjustment_from_per_fire_evidence
```

The 0.05 and 0.95 clip is intentional — never claim certainty, never claim
impossibility. The market always surprises.

### Step 5 — Emit the 4-square payload

Write the per-fire payload to:
`docs/agentic-os/debates/<plot_id>/<bar_ts_iso>-<symbol>-<tf>-<dir>.md`

Schema:

```yaml
# Header
plot: <e.g. csNew3 — Unified Combo>
plot_owner: <e.g. PO::unified-combo>
fire_id: <symbol>-<tf>-<bar_ts>-<plot>-<direction>
debate_run_at: <iso>
schema_version: 1

# Context
context:
  symbol: <ticker>
  tf: <timeframe>
  bar_ts: <iso>
  bar_ohlcv: [O, H, L, C, V]
  preceding_5_bars: [...]
  concurrent_plots_firing:
    - {plot: <name>, family: <indicator>, direction: <bull|bear>}
  operand_breakdown:
    <operand_name>: <value or boolean>
  ipsf_snapshot:
    <param_name>: <value>
  historical_analogues_n: <count of prior matches>

# The debate
debate:
  angel_case:
    summary: <one paragraph>
    supporting_facts: [<facts>]
    confidence: <0.0 - 1.0>
  devil_case:
    summary: <one paragraph>
    supporting_facts: [<facts>]
    confidence: <0.0 - 1.0>

# The 4-square (only firing-direction row populated for this fire)
matrix:
  P_true_angel: <if fire_dir == bull, set to angel_confidence; else null>
  P_devil_dressed_as_angel: <if fire_dir == bull, set to devil_confidence; else null>
  P_angel_dressed_as_devil: <if fire_dir == bear, set to devil_confidence; else null>
  P_true_devil: <if fire_dir == bear, set to angel_confidence; else null>

# Notes
notes: <free-form one paragraph from the Plot Owner>

# For the long-run calibration rollup
calibration_inputs:
  fire_direction: <bull | bear>
  evidence_strength: <weak | moderate | strong>
  outcome_known: false   # set true after N bars when actual direction is observable
  outcome: null           # filled by calibration-rollup skill at fire+10-bar mark
```

### Step 6 — Append to the rolling debate log

In addition to the per-fire YAML, append a one-line summary to:
`docs/agentic-os/debates/<plot_id>/INDEX.md`

```
| <bar_ts> | <symbol> | <tf> | <dir> | angel_conf | devil_conf | notes_one_line |
```

## Inputs the skill expects

- `plot_id` (e.g. `csNew3`)
- `plot_owner_id` (e.g. `PO::unified-combo`)
- `fire_id` (the unique fire identifier — must be reproducible)
- `bar_context` (a dict with the symbol/TF/bar_ts/ohlcv/preceding-5-bars)
- `concurrent_fires` (list of {plot, family, direction})
- `operand_breakdown` (dict of operand → value)
- `ipsf_snapshot` (dict of IPSF parameter → value)
- `prior_calibration` (optional dict; if present, used in step 4)

Where the inputs come from depends on the invocation path:
- Real-time Path-M pipeline → fires arrive with full context attached
- Manual / back-test → Plot Owner runs the data assembly via TV firing
  skill or Phase-M Python ports

## Outputs

1. `docs/agentic-os/debates/<plot_id>/<fire_id>.md` — the per-fire payload
2. Append to `docs/agentic-os/debates/<plot_id>/INDEX.md` — one-line summary
3. (Optional) Append to `docs/agentic-os/calibration/<plot_id>.md` if the
   Plot Owner rolls calibration inline rather than via a separate skill

## Hard guardrails

- NO file deletion (SD-004)
- NO modification of Pine source files
- NO modification of canonical Python ports (those are SD-002 / SD-006
  controlled — only Plot Owner can authorize a new versioned canonical
  port)
- NEVER skip the devil case. The angel case alone is rubber-stamping.
  If you think the angel case is overwhelming, your devil case should
  STILL include the strongest counter-argument you can construct, even
  if you score it 0.05.

## What NOT to do

- Do NOT pause to ask Anish for confirmation on the angel/devil scores.
  Standing approval is on; emit your best estimate and let calibration
  correct it over time.
- Do NOT wait for outcome data before emitting the matrix. The matrix is
  a per-fire prior; outcome data updates the long-run calibration table
  separately.
- Do NOT re-run the debate on the same fire_id unless the IPSF snapshot
  changed or new evidence (concurrent fires that came in late) requires
  reconsideration. Idempotency: same fire_id + same IPSF + same evidence
  → same matrix.

## How a Plot Owner uses this skill

In a Plot Owner chat thread:

```
You (Anish or parent agent): "csNew3 just fired bull on TSLA 5m at
2026-05-11T14:30:00. Run the debate."

Plot Owner (e.g. PO::unified-combo): invokes this skill with the assembled
context. Skill emits the per-fire payload + index update. Plot Owner
returns a one-paragraph summary of the matrix to you.
```

In a real-time pipeline:

```
Path-M fires csNew3 bull → Path-M emits a fire-event JSON →
PO::unified-combo's listener picks it up → skill runs → payload written
→ PO::unified-combo's chat thread receives a notification with the
matrix summary
```

## v1.0 scope (what's IN today, what's deferred)

IN:
- The 6-step procedure
- The per-fire payload schema
- Append-only debate log + index
- Standing decisions inheritance (SD-001 through SD-007)

DEFERRED to future skills:
- `calibration-rollup` — nightly aggregation of per-fire payloads into the
  4-square long-run table
- `outcome-stamping` — at fire+10-bars, stamp the actual direction on the
  payload's `outcome` field
- `cross-plot-debate` — when 2+ Plot-Owned plots fire on the same bar,
  run a meta-debate that integrates their individual matrices

## Provenance

Authored 2026-05-11 alongside `docs/agentic-os/ARCHITECTURE.md`. References
SD-005, SD-006, SD-007 in `docs/agentic-os/STANDING_DECISIONS.md`.

Sister skills:
- `.claude/skills/detection-plot-validation/` — Stage 4 validation; runs
  before a Plot Owner is hired (drift discovery)
- `.claude/skills/detection-plot-tv-firing/` — Path A chart-side TV firing;
  used by Plot Owners when they need fire-bar truth for calibration
