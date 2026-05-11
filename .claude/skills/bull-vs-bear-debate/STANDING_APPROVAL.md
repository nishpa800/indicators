# Standing Approval — bull-vs-bear-debate skill

This skill inherits the same UNLIMITED APPROVAL block as
`detection-plot-validation` and `detection-plot-tv-firing`.

## Anish's standing approval (verbatim, 2026-05-10 / restated 2026-05-11)

> "make sure that the permissions are completely completely uninhibited,
> one hundred percent, can do anything, any writing. Don't don't give it
> any single one restriction. Only thing it can do is it cannot delete
> things."

## What this means for the debate skill

Permitted (no confirmation required):
- Write to ANY path (per-fire payloads, debate logs, index updates,
  calibration tables, agentic-os memory updates)
- Create directories
- Read any file in the repo
- Run shell commands (search, grep, parse pine, etc.)
- Invoke other skills (TV firing, validation, future calibration-rollup)
- Append to STANDING_DECISIONS.md (only when a new SD is being authored
  by Plot Owner authority)

NOT permitted (hard guardrails — the only ones):
- DELETE any file (no rm, no git rm, no overwrite via mv, no truncate)
- Drop databases (we don't have any but for completeness)
- Hit rate-limited APIs >100x in 5 minutes
- Mass-rename Pine files (per SD-002)

## Standing decisions inherited

The debate skill operates under all standing decisions in
`docs/agentic-os/STANDING_DECISIONS.md`. Notably:

- SD-001: Always include Pentagon (in canonical-port-derived operand values)
- SD-002: Never modify, always new-version (per-fire payloads are
  appended; never overwritten)
- SD-003: IPSF defaults are not drift (snapshot the active settings; don't
  flag default differences)
- SD-004: No file deletion ever
- SD-005: Bull and bear are separate Indicator Owners (debate happens
  inside ONE Plot Owner; the structural separation is at Tier-A, not
  Tier-B)
- SD-006: Plot Owners hold both bull and bear in one context
- SD-007: 4-square confidence matrix is the per-fire output

## Escalation protocol

The debate skill never blocks on Anish. If a debate is impossible to score
(e.g. zero historical analogues + zero concurrent fires + zero operand
breakdown — i.e. the input context is empty), emit a
`P_undetermined: 1.0` payload with notes explaining why, and continue.
Anish reviews undetermined payloads in batch via the Plot Owner thread.
