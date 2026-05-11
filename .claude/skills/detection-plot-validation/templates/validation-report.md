# Validation report — `<canonical-name>`

_Skill: `detection-plot-validation` v<version>. Run on <YYYY-MM-DD>. Path: docs/validation/<date>-<target-slug>.md._

## Summary

| Field | Value |
|---|---|
| Target | `<canonical-name>` |
| Aliases resolved | `<comma-separated-list>` |
| Indicator families with occurrences | `<count>` |
| DEFINITION locations | `<count>` |
| REFERENCE / INPUT / PLOT / ALERT / COMMENT occurrences | `<count>` |
| Phase 2 verdicts | `<n identical / m cosmetic / k ipsf-default / j ipsf-asym / i semantic>` |
| Phase 3 path used | Path A / Path B / Manual / BLOCKED |
| Phase 3 agreement-set count | `<int>` |
| Phase 3 drift-set count | `<int>` |
| Phase 4 reconcile actions | `<count, or "none required">` |
| Final verdict | `OK / DRIFT-RECONCILED / DRIFT-PENDING-USER / BLOCKED` |
| Stage-7 followups | `<list, or "none">` |

## Phase 1 — Enumeration

See `templates/enumeration-table.md` for shape.

<table goes here>

**Orphans (in YAML, not in Pine)**: <list or none>
**Missings (in Pine, not in YAML)**: <list or none>

## Phase 2 — Static diff

| Pair | Verdict | Evidence (line ranges) | Drift artifact |
|---|---|---|---|
| <A> ↔ <B> | <identical / cosmetic / ipsf-default / ipsf-asym / semantic> | <line refs> | <link or none> |
| ... | ... | ... | ... |

**Drift findings** (one entry per non-`identical` verdict): see `docs/validation/<date>-<target-slug>-drift-<n>.md` per `templates/drift-finding.md`.

## Phase 3 — TV firing

| Path used | Why |
|---|---|
| Path A / Path B / Manual / BLOCKED | <reason> |

| Location | Fire-bar count | Query window | Status |
|---|---|---|---|
| <indicator>::<variable> | <int> | <symbol + tf + bars> | COMPLETE / BLOCKED |
| ... | ... | ... | ... |

**Bar-set algebra**:

- Agreement set (every location fired): `<int>` bars
- Drift set (some but not all): `<int>` bars
- Total bars scanned: `<int>`

**Drift-bar diagnoses** (one entry per drift-set bar):

| Bar timestamp | Symbol | TF | Locations that fired | Locations that didn't | Diagnosis |
|---|---|---|---|---|---|
| <ts> | <sym> | <tf> | <list> | <list> | offset / drift / namespace / parameter / other |

## Phase 4 — Reconcile

| Finding | Proposed action | User approved | Applied | Commit SHA |
|---|---|---|---|---|
| <drift-id> | <canonical-decision-summary> | yes / no / pending | yes / no | <sha> |

See `docs/validation/<date>-<target-slug>-canonical-decision.md` per `templates/canonical-decision.md` for full proposals.

**Generators run**:

- `python3 tools/merge_extracts.py` — ✓ / ✗
- `python3 tools/build_lineage_cards.py` — ✓ / ✗
- `python3 tools/build_docs.py` — ✓ / ✗
- YAML == JSON byte-equivalent — ✓ / ✗

## Final verdict

State one of:

- **OK** — every location identical or only cosmetic-drift; no action required.
- **DRIFT-RECONCILED** — drift found AND fixed in this run.
- **DRIFT-PENDING-USER** — drift found; user-side decision required (Pine rename, semantic drift, etc.). Listed in "Stage-7 followups" below.
- **BLOCKED** — Phase 3 couldn't complete (e.g. no Path A logger + Path B stateful limitation). Listed in "Stage-7 followups".

## Stage-7 followups

If anything remains:

- [ ] <followup item 1>
- [ ] <followup item 2>

## Provenance

- Skill version: detection-plot-validation v<n.m.k>
- Run started: <ISO timestamp>
- Run ended: <ISO timestamp>
- Wall-clock duration: <minutes>
- Subagents dispatched: Phase 1 = <n>, Phase 2 = <m>, Phase 3 = <k>
- Parent agent: <Claude session id or "manual">
