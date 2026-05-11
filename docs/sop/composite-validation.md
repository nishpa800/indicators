# SOP — Composite Validation

**When to use**: every time a composite is added, edited, or implicated in an
unexpected firing (or non-firing). Goal: walk the lineage card top-down to
find the failing level.

## Inputs

- A composite canonical name, e.g. `squarify::S27_CO_BULL`.
- Its lineage card at `docs/lineage/<canonical>__<name>.md`.
- The Pine source for the composite's indicator (per
  `bible-input/MANIFEST.md`).
- A test chart on TradingView with the indicator loaded.
- The composite's row in `docs/composites.md` for tier + composition summary.

## Procedure

### 1. Open the lineage card

`docs/lineage/<provenance>__<NAME>.md` — for example
`docs/lineage/squarify__S27_CO_BULL.md`. Read top-to-bottom:

- **Top-level metadata**: tier, lifecycle stage, offset, one-line definition.
- **Dependency expansion** (the ASCII tree).
- **Root inventory** — the deduplicated leaves the composite ultimately depends on.
- **Offset ledger** — every level's offset top-down.
- **Decoupling proof** — confirms no composite reads root internals.
- **Common failure modes** — the 3-5 likely culprits.

### 2. Pick a candidate bar

Find a bar in TradingView's history where ALL the roots in the inventory fired
(per the offset ledger — `offset=0` roots fire on the same bar; `offset=-1`
roots fire one bar back).

If you can't find such a bar in recent history, expand the lookback. If still
nothing, the composite may have a structurally rare composition — note in the
log and pick a synthetic test on bar replay.

### 3. Confirm the composite fires (or doesn't) on that bar

- **If it fires** → the composite is working at that bar. Repeat with 2-3 more
  candidate bars to build confidence.
- **If it does NOT fire** despite all roots aligning → drop into diagnosis.

### 4. Diagnose — walk top-down

Open the lineage card's dependency expansion. For each tier, read the offset
ledger and confirm the operand fired on the expected bar. The first
discrepancy is the bug. Common patterns:

#### Offset mismatch
- Top-level says `offset=-1` but a tier-1 child says `offset=0`. Tier-1's
  boolean is `true` on bar N, top-level expects it on bar N-1 (because of its
  own −1 shift). Check Pine source for the offset annotations on each plot.
- Fix: align offsets. Document in `docs/redundancy.md` (b) if an internal
  drift caused the mismatch.

#### Definition drift
- A child operand's definition changed in the canonical indicator but the
  composite's lineage card cites the older definition.
- Fix: update the canonical name reference in the YAML; re-run generators.

#### Cross-indicator drift
- A composite references `b2b-pup::PUP` but the local file actually uses a
  drifted local copy (different threshold, etc.).
- Fix: jump to `drift-triage.md`.

#### Callback gate
- A Squarify-v2-era composite added a callback gate that v1 didn't have. The
  bare boolean fires; the gate suppresses the plot.
- Fix: read the source for the callback gate condition; confirm or update the
  composite's record.

### 5. Document the diagnosis

In `docs/validation-log/<YYYY-MM-DD>-composites.md`:

```markdown
### <provenance>::<composite> — diagnosed <YYYY-MM-DD>

- Chart: <symbol> <timeframe>
- Candidate bar: <timestamp>
- Expected: composite fires (all N roots aligned per offset ledger)
- Observed: composite did/did-not fire
- Diagnosis: <which level failed and why>
- Fix applied: <yes/no, what>
- Drift table updated: <yes/no>
```

### 6. Apply fix (if any)

- Source-level fix (rare): edit the Pine. Make the change, commit, push, run
  generators.
- YAML-level fix (more common): edit the composite's record in
  `data/indicators.yaml`, re-run generators, verify the lineage card now
  matches reality.

## Time budget

A focused composite diagnosis takes 10-30 minutes. Squarify's S27_CO_BULL
(tier 3, depends on tier-2 Unified Combo + FVG Combo + tier-1 callback gate)
is at the high end. Heavy Combo Toggles' 3 tier-1 composites are at the low end.

## Failure modes

| Symptom | Likely cause | Next SOP |
|---|---|---|
| Composite fires but lineage card says "shouldn't" | YAML composition is wrong | Update YAML, re-gen |
| Composite doesn't fire when all roots align | Offset / drift / gate | This SOP, step 4 |
| Multiple composites with same name disagree | Namespace collision | `drift-triage.md` |
| Composite offset feels off by exactly N bars | Offset cascade through tiers | `offset-triage.md` |
