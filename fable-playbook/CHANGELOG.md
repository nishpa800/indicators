# Fable Playbook — Changelog

Newest first. Each version = one file in `versions/`.

---

## v1 — 2026-07-14

**File:** `versions/FABLE_PLAYBOOK_v1.pine` — chart title **"Fable Playbook v1"**,
shorttitle **"FABLE PLAYS v1"**.

- New study housing the Fable Playbook v1 play triggers (S1–S16 families ↔ play IDs
  BL-01..25 / BR-01..25 in contracts/playbook_v1.json).
- MASS ladder with adjustable floor input (default 2000; 1000/1500/1750/4000) + fixed
  hv1000/2000/4000 flags; Displacement σ main/secondary inputs (9/7); RVOL Pre-Mythos
  tiers; PUP/PPD; FAUNA — engine blocks verbatim-adapted from FIRST_BAR_FABLE_v2 @ 0859d60.
- Opening-window master (first N bars of session, default 3) gates every play plot.
- Evidence lineage: pre-registered H1 scan (2026-07-14), 22 MEASURED plays with integers;
  gates: no-fixed-windows PASS · no relativeVolume (tick-safe) · Pine v5 · outputs ≤ 64.
