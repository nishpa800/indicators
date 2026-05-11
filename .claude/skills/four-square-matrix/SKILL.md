---
name: four-square-matrix
description: Output skill. Given a dialectic transcript from bull-bear-dialectic + the firing direction, collapse to the canonical 2x2 POST-SETUP OUTCOME confidence matrix per SD-010 (compliance vs defiance), apply long-run prior calibration if available, emit the per-fire payload. Final step in the diagnosis → dialectic → matrix chain.
---

# Four-Square Matrix Skill — v1.1.0 (corrected per SD-010)

The output skill that produces the canonical per-fire payload. Last in
the chain.

> SD-010 (CRITICAL): the matrix is OUTCOME prediction, not setup
> validation. Both diagonals represent "setup followed" (compliance);
> both off-diagonals represent "setup defied" (the magical reversal
> cell). Cells renamed from the v1.0 angel/devil terminology.

## What this skill produces

The 2x2 per-fire POST-SETUP OUTCOME matrix per SD-010:

|                       | MARKET MOVES BULL (over outcome window) | MARKET MOVES BEAR |
|-----------------------|---|---|
| **BULL SETUP FIRED**  | `P_bull_compliant` (setup followed) | `P_bull_defied` (magical reversal) |
| **BEAR SETUP FIRED**  | `P_bear_defied` (magical reversal) | `P_bear_compliant` (setup followed) |

For a single fire, only the ROW matching the FIRING SETUP DIRECTION is
populated. The off-diagonals (`P_bull_defied`, `P_bear_defied`) are
the "order block / divine reversal" cells per SD-010.

## Naming per SD-008 + SD-010

Cell labels use NEUTRAL + OUTCOME-EXPLICIT language:
- `P_bull_compliant` — bull setup, bull outcome (replaces `P_true_bull` / `P_true_angel`)
- `P_bull_defied` — bull setup, bear outcome (replaces `P_bear_in_bull_clothing` / `P_devil_dressed_as_angel`)
- `P_bear_defied` — bear setup, bull outcome (replaces `P_bull_in_bear_clothing` / `P_angel_dressed_as_devil`)
- `P_bear_compliant` — bear setup, bear outcome (replaces `P_true_bear` / `P_true_devil`)

The diagonal vs off-diagonal split is the load-bearing distinction.
Diagonal = setup did its job (market complied). Off-diagonal = the
setup was the FAKEOUT and the real move was opposite (the "magical"
cell per Anish's SD-010 framing).

## Inputs

- `dialectic_transcript_path` (required): path produced by
  `bull-bear-dialectic`
- `firing_direction` (required): bull | bear (must match the diagnosis
  card)
- `prior_calibration` (optional): rolling 4-square table for this
  plot/symbol/TF if ≥30 historical observations available

## Procedure

### Step 1 — Read the dialectic

Load the dialectic transcript. Extract:
- `bull_case.self_confidence`
- `bear_case.self_confidence`
- `reconciliation.calibration_status`

### Step 2 — Normalize compliance/defiance confidences

The dialectic transcript provides `compliance_case.self_confidence` and
`defiance_case.self_confidence`. Normalize:

```python
total = compliance_conf + defiance_conf
if abs(total - 1.0) > 0.05:
    compliance_conf = compliance_conf / total
    defiance_conf = defiance_conf / total
```

Now `compliance_conf + defiance_conf == 1.0` exactly.

### Step 3 — Apply prior calibration (if available)

If a prior 2x2 calibration table exists for this plot at this
outcome_window:

```python
# Prior gives historical P(compliance | this setup direction)
prior_p_compliance_for_dir = prior_calibration[firing_setup_direction]['P_compliance']

# Bayesian update: blend dialectic confidence with prior
DIALECTIC_WEIGHT = 0.6
PRIOR_WEIGHT = 0.4

p_compliance = DIALECTIC_WEIGHT * compliance_conf + PRIOR_WEIGHT * prior_p_compliance_for_dir
p_defiance = 1.0 - p_compliance

# Map to the correct matrix cells based on firing setup direction
if firing_setup_direction == 'bull':
    p_bull_compliant = p_compliance
    p_bull_defied = p_defiance
    p_bear_defied = None
    p_bear_compliant = None
else:  # bear setup
    p_bull_compliant = None
    p_bull_defied = None
    p_bear_defied = p_defiance      # market moved bull when setup said bear
    p_bear_compliant = p_compliance  # market moved bear as setup said
```

If no prior available (cold start), use dialectic confidences directly.

### Step 4 — Clip the cells

Never claim certainty:

```python
# Clip every probability to [0.05, 0.95]
p_true_bull = clip(p_true_bull, 0.05, 0.95)
# (and re-normalize the row if necessary)
```

### Step 5 — Build the per-fire payload

Schema (matches SD-007):

```yaml
schema_version: 1
plot_id: <e.g. csNew3_Bull>
plot_owner: <e.g. PO::unified-combo>
fire_id: <symbol>-<tf>-<bar_ts>-<plot>-<direction>
matrix_emitted_at: <iso>
matrix_skill: four-square-matrix@v1.0.0

# Sources
diagnosis_card: <path>
dialectic_transcript: <path>
prior_calibration_used: <yes/no, with N observations>

# The 4-square (firing-direction row populated)
matrix:
  P_true_bull: 0.65          # if firing_direction == bull
  P_bear_in_bull_clothing: 0.35
  P_bull_in_bear_clothing: null   # null because bear row not applicable to this fire
  P_true_bear: null

# Calibration metadata
calibration:
  dialectic_weight: 0.6
  prior_weight: 0.4
  prior_p_true_for_dir: 0.62
  was_normalized: false
  was_clipped: false

# Long-run calibration inputs (filled later)
calibration_inputs:
  fire_direction: bull
  evidence_strength: <weak | moderate | strong>
  outcome_known: false
  outcome: null              # filled by outcome-stamping skill at fire+10-bar mark
  outcome_known_at: null

# Free-form (one paragraph)
notes: |
  <Plot Owner's one-paragraph synthesis of the matrix.
   Neutral language per SD-008.>
```

### Step 6 — Append to the matrix log + index

Write to:
`docs/agentic-os/matrices/<plot_id>/<bar_ts_iso>-<symbol>-<tf>-<dir>.md`

Append summary line to:
`docs/agentic-os/matrices/<plot_id>/INDEX.md`

```
| <bar_ts> | <symbol> | <tf> | <dir> | P_true | P_in_clothing | calibrated | outcome | notes |
```

### Step 7 — Update the rolling 4-square calibration table

The long-run calibration table aggregates per-fire matrices for the
plot. Path: `docs/agentic-os/calibration/<plot_id>.md`

Increment counters:

```yaml
# 4-square long-run calibration for csNew3_Bull (TSLA, 5m, last 90d)
schema_version: 1
plot_id: csNew3_Bull
last_updated: <iso>
fires_observed: <N>

# Each cell: count + average probability + outcome rate
matrix:
  fired_bull_actual_bull:    # P_true_bull cell
    fires_in_cell: <N>
    avg_assigned_probability: <mean of P_true_bull across fires>
    outcome_rate: <% of these fires where actual was bull, when known>
  fired_bull_actual_bear:    # P_bear_in_bull_clothing cell
    fires_in_cell: <N>
    avg_assigned_probability: <mean of P_bear_in_bull_clothing>
    outcome_rate: <%>
  fired_bear_actual_bull:    # P_bull_in_bear_clothing cell
    fires_in_cell: <N>
    avg_assigned_probability: <mean>
    outcome_rate: <%>
  fired_bear_actual_bear:    # P_true_bear cell
    fires_in_cell: <N>
    avg_assigned_probability: <mean>
    outcome_rate: <%>
```

The `outcome_rate` field is filled retroactively by the
`outcome-stamping` skill (TBD) at fire+10-bars. Until then, it shows
the cell's accumulated PRIOR probability without outcome correction.

## Outputs

1. `docs/agentic-os/matrices/<plot_id>/<fire_id>.md` — per-fire matrix
   payload
2. Append to `docs/agentic-os/matrices/<plot_id>/INDEX.md`
3. Update `docs/agentic-os/calibration/<plot_id>.md`

## Standing approval

Inherited. NO file deletion (SD-004).

## Composition

LAST step in the chain:

```
detection-plot-diagnosis (grunt) → diagnosis card
        ↓
bull-bear-dialectic (knowledge) → dialectic transcript
        ↓
four-square-matrix (output — THIS SKILL) → per-fire payload + calibration update
```

## Idempotency

Same dialectic + same firing direction + same prior calibration → same
matrix payload. Re-runs go to `<fire_id>__rev2.md` per SD-002.

## What NOT to do

- Do NOT re-reason about the fire. The dialectic skill did that.
- Do NOT re-tabulate concurrent fires or operand values. The diagnosis
  did that.
- Do NOT use moralistic language (good / evil / angel / devil) per
  SD-008.
- Do NOT skip the prior calibration application when a prior is
  available — that's the whole point of the long-run table.
- Do NOT clip outside [0.05, 0.95]. The market always surprises.
- Do NOT pause to ask Anish for confirmation. Standing approval is on.
