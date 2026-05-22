# 00 — Master Read Order

Canonical order the COT reads at the top of every response. Read top to
bottom. Stop reading when the operator's input is sufficiently grounded
to act on — but never skip the first three.

## Tier 0 — Always (every response, no exception)

1. `COT/NORTH_STAR.md`
2. `COT/instructions/16_anti_shortcut.md`
3. `COT/instructions/00_master.md` (this file)

## Tier 1 — Identity + Hard Constraints

4. `COT/instructions/15_no_diagnostic_labels.md`
5. `COT/instructions/14_no_friction.md`
6. `COT/wiki/wishes/GENIE_MANIFESTO.md`
7. `COT/wiki/wishes/GENIE_RESPONSIBILITIES.md`

## Tier 2 — Operational Vocabulary

8. `COT/wiki/SYNONYMS.md`
9. `COT/wiki/STRAIGHT_LINE.md`

## Tier 3 — Diagnostic Routines

10. `COT/routines/on_frustration_detected.routine.md`

## Tier 4 — Open Slots (populate as authored)

- `COT/wiki/PROBLEM_STATEMENT.md`
- `COT/wiki/PIPELINE.md`
- `COT/wiki/ANALOGIES.md`
- `COT/wiki/wishes/WISH_LEDGER.md`
- `COT/wiki/FAILURE_MODES.md`
- `COT/wiki/PATTERNS.md`
- `COT/skills/` (key skills directory)
- `COT/routines/` (other routines)

## Response shape (after reading)

Every response begins with:

```
ACTIVE NODE: <where we are in the work>
LAST DECISION: <what was just decided / committed>
NEXT CHUNK: <one concrete next thing>
```

Then resolves operator noun-phrases through `SYNONYMS.md`. Then either:
- diagnoses frustration via the three-trunk tree, OR
- proceeds directly to the file diff.

Every response ends with one `NEXT:` line.
