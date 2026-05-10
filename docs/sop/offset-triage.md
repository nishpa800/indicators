# SOP — Offset Triage

**When to use**: when a composite fires "one bar off" or fails to align with
its dependencies, or when a plot appears on the wrong bar relative to the
event that caused it.

## Background

Pine's `offset` parameter on `plot` / `plotshape` / `plotchar` shifts ONLY the
visual rendering and the time index the boolean is associated with. It does
NOT cause the calculation to wait or look forward. An `offset=-1` plot
displayed on bar N was actually computed on bar N+1 (i.e. on bar N+1's close,
the boolean evaluated true and got rendered as if belonging to bar N).

Alerts fire at bar close — regardless of plot offset.

## Inputs

- The composite or root in question.
- Its lineage card (composites) or row in `docs/roots.md` (roots).
- The Pine source file.

## Procedure

### 1. Read the offset ledger

For composites: open the lineage card. Find the OFFSET LEDGER section. Note:
- The top-level composite's offset.
- Each tier-N child's offset.
- Each root's offset at the leaves.

For roots: read the `offset:` field directly from `docs/roots.md` or
`data/indicators.yaml`.

### 2. Detect the kind of offset bug

| Pattern | Kind |
|---|---|
| Top-level offset=−1 but a tier-1 child also offset=−1 | DOUBLE SHIFT — composite fires 2 bars to the left of the root that triggered it |
| Top-level offset=0 but tier-1 children all offset=−1 | ALIGNMENT BREAK — composite tries to read tier-1 booleans on bar N but they were already shifted to bar N-1 |
| Top-level offset=−1 with all roots offset=0 | NORMAL — top-level intentionally labels the prior bar as "the trigger" |
| Top-level offset=0 with roots mixed (some 0, some −1) | LIKELY BUG — the −1 roots are out-of-step with the composite expectation |

### 3. Cross-reference with Pine source

Open the Pine source at the line range cited in the YAML. Confirm:
- The plot's `offset=` parameter matches the YAML's `offset:` field.
- The boolean expression doesn't ALSO use `[N]` shifts that would compound
  with the offset.

### 4. Trace through the lifecycle

Walk the bar lifecycle (see `docs/glossary.md` "Bar lifecycle"):

1. Bar N closes & confirms.
2. Roots calculate. Each root that fires has its boolean = true.
3. Each root's offset shifts the *labelling* (e.g. offset=−1 means the boolean
   computed on bar N is treated as if on bar N-1 from this point forward).
4. Plot renders on the (offset-shifted) bar.
5. Composite reads which roots fired AT THE LABELLED BAR. If the composite
   itself is offset=0 but reads roots that are offset=−1, the composite expects
   the root's boolean on bar N to mean "root fired on bar N+1".

So: every level's offset COMPOUNDS for the consumer. A composite offset=−1
that reads a root offset=−1 means the composite renders on bar N-2 from the
bar that originally triggered.

### 5. Fix patterns

#### Pattern A — Composite intends to label the prior bar

```
Root: offset=0 (fires when boolean true on bar N, plot renders on bar N)
Composite: AND(root, root[1]) with plot offset=−1
→ When composite is true on bar N (because root fired on N AND on N-1),
   plot renders on bar N-1, labelling "the start of the back-to-back pattern"
```

This is correct.

#### Pattern B — Mismatched offset

```
Root: offset=−1 (renders one bar back from where boolean is true)
Composite: AND(root, ...) with plot offset=0
→ Composite reads root's plot at bar N. But root's plot was shifted from bar N+1.
   Composite tries to fire at bar N for an event that "actually" happened on N+1.
   This causes the composite to fire on the wrong bar relative to the user's
   mental model.
```

Fix: either align the composite's offset to −1 (so user sees them on the same
labelled bar) OR remove the root's −1 (so they share offset=0 and align).
Document the choice in YAML notes.

#### Pattern C — Mid-tier composite double-shifts

```
Tier-1 composite: offset=−1
Tier-2 composite: AND(tier-1, ...) with offset=−1
→ Tier-2 plot renders 2 bars to the left of the original trigger.
```

Usually a bug — fix tier-2 to offset=0 so it aligns with tier-1's labelling.

### 6. Apply fix

Source fix in the Pine file (Stage 6 if part of a coordinated cleanup,
or hot-fix earlier with a single-line PR). Then update the YAML's `offset:`
field and re-run generators.

### 7. Log

Append to `docs/validation-log/<YYYY-MM-DD>-offset.md`:

```markdown
### <provenance>::<name> — offset triaged <YYYY-MM-DD>

- Pattern: A (intentional label-prior) / B (mismatched) / C (double-shift)
- Old offsets: top=<X>, children=<Y>, roots=<Z>
- New offsets (if changed): top=<X>, children=<Y>, roots=<Z>
- Rationale: <why this offset is correct>
- YAML updated: <yes/no>
- Pine source updated: <yes/no, file/line>
- Lineage card re-generated: <yes/no>
```

## Time budget

5-15 minutes per offset bug. Patterns A and C are usually obvious; pattern B
takes the most reasoning.

## Failure modes

| Symptom | Likely cause | Next step |
|---|---|---|
| Plot looks 1 bar off after a fix | Forgot to re-run lineage card generator → card still shows old offset | Re-run `tools/build_lineage_cards.py` |
| Alert and plot disagree | Alerts fire at bar close regardless of offset; plot offset is just labelling | Confirm with `docs/glossary.md` "Offset" |
| Same composite fires on wrong bar in chart A vs chart B | Different timeframe or session settings altering bar boundaries | Out of scope of bible — TradingView issue |
