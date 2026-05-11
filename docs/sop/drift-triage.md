# SOP — Drift Triage

**When to use**: when the same root or composite name produces different
results across two or more indicators, or when `docs/redundancy.md` flags
a drift candidate that needs to be reconciled.

## Inputs

- The colliding name (root or composite).
- All occurrences listed in `docs/redundancy.md`.
- The Pine source files where each occurrence is defined.

## Two kinds of drift

### (a) Composition drift / namespace collision

Two indicators define the same un-prefixed name (e.g. "FLOOR", "Pentagon")
but with different compositions or different concepts entirely.

### (b) Internal-implementation drift inside a root

Two indicators reference the same root by name (e.g. PBJ) but the
underlying Pine math has diverged — Supertrend, Zoo MA, VWMA, ATR
threshold, σ-multiplier, or some other internal mechanic. The drift is
invisible at the root-name level — both files still say "PBJ" — but
visible at the byte level.

## Procedure

### 1. Identify the kind of drift

Open `docs/redundancy.md`:
- Table (a) handles composition / namespace drift.
- Table (b) handles internal-implementation drift.

### 2. For composition drift (a)

For each occurrence (the table lists them side-by-side):
- Open the Pine source.
- Extract the boolean assignment line(s).
- Normalise (whitespace, parameter names) and compare.
- Determine: identical / drifted / namespace collision (different concept).

Verdicts:
- **Identical** → designate one as canonical, mark others as aliases in
  `data/indicators.yaml` (`aliases: [{in_indicator: foo, name: bar}, ...]`).
- **Drifted** → designate the most recent / most-correct as canonical,
  rename the others, and update consumers.
- **Namespace collision** → rename the colliding name in one indicator
  (e.g. `anyBearPent` → `anyBear2F`).

Apply the rename across:
- The Pine source (Stage 6).
- The YAML.
- Re-run generators (`tools/merge_extracts.py` then
  `tools/build_lineage_cards.py` then `tools/build_docs.py`).

### 3. For internal-implementation drift (b)

For each indicator that names the root:
- Open the Pine source.
- Extract the function definition + every line that contributes to the
  root's boolean.
- Normalise whitespace and parameter names.
- `diff -u` each implementation pair.

Verdicts:
- **identical** → no action; record `parity_check: identical` in YAML.
- **drifted-cosmetic** (only whitespace / variable names differ) → record
  `parity_check: cosmetic_drift` in YAML; consider a Stage-6 normalisation
  pass.
- **drifted-semantic** (different math, different defaults) → designate
  one canonical implementation, mirror it everywhere, lock with a SHA
  checksum in `data/indicators.yaml`. Document the drift in
  `docs/validation-log/<date>-drift-<root>.md` with the diff.

### 4. Update consumers

For every composite that references the colliding/drifting name:
- Confirm the composite uses the canonical form in YAML.
- Re-run lineage card generation; verify the card now reflects the
  canonical reference.

### 5. Log

Append to `docs/validation-log/<YYYY-MM-DD>-drift.md`:

```markdown
### <name> — triaged <YYYY-MM-DD>

- Drift kind: (a) composition / (b) internal-implementation
- Occurrences: <list>
- Verdict: identical / drifted-cosmetic / drifted-semantic / namespace-collision
- Canonical designation: <provenance>
- Action taken: <rename / merge / leave / Stage-6-deferral>
- YAML updated: <yes/no>
- Consumers updated: <yes/no>
- Generators re-run: <yes/no>
```

## Stage-6 vs in-flight

Drift triage during Stage 1-5 is **diagnosis-only**: update YAML, do not
modify Pine sources. Stage 6 is the cleanup phase where Pine renames /
merges / deletes happen as a single coordinated commit.

## Time budget

Composition drift: 5-15 minutes per name (mechanical comparison).
Internal-implementation drift: 30-60 minutes per root (line-by-line diff,
test-bar reasoning).

## Failure modes

| Symptom | Likely cause | Next step |
|---|---|---|
| Two implementations look identical but produce different results | Subtle parameter difference or a `[1]` shift difference | Step 3, line-by-line diff |
| Rename breaks downstream consumers | Forgot to update a composite that referenced the old name | Re-grep for old name across `data/indicators.yaml` and Pine sources |
| Drift fix breaks an existing alert | Threshold or σ-multiplier changed | Document the breakage in changelog; coordinate with anyone using the alert |
