# Fable Playbook — Changelog

Newest first. Each version = one file in `versions/`.

---

## v3 — 2026-07-14 (Fable-authored, triple-verified)
**File:** `versions/FABLE_PLAYBOOK_v3.pine` — title "Fable Playbook v3".
- S18/S19 MASS PURE bull/bear: the AB-01 literature arm (GKM JF 2001 — volume record
  WITHOUT displacement; the configuration the high-volume-premium literature says is
  STRONGER). A/B vs S1/S2 settles on the forward ledger, never by opinion.
- Fable sovereign sign-off: pass 1 machine gates · pass 2 line-read of v2 diff + playbook
  integrity (50 unique IDs, 25/25, all decisiveness fields, 21/21 pine↔playbook refs
  resolve) · pass 3 v3 authored + re-gated + raw-URL byte-verified.

## v2 — 2026-07-14

**File:** `versions/FABLE_PLAYBOOK_v2.pine` — chart title **"Fable Playbook v2"**,
shorttitle **"FABLE PLAYS v2"**.

- Per-play tooltip mapping: every S1–S16 toggle's `tooltip=` now cites its exact play
  ID(s) + status from `contracts/playbook_v1.json` (MEASURED cells carry their integers;
  unmeasured cells are marked CANDIDATE).
- New play **S17: Failed PUP short (BR-24)** — tracks the most recent PUP bar's low over
  a rolling 3-bar age window; fires SHORT if price closes below that low (failed pocket
  pivot). NOT window-gated — the failure can complete after the opening window. Added to
  the `anyBear` alert line.
- Confluence plays (BL-19..21 long / BR-11..13 short, S15/S16) declared **SCANNER-SIDE**:
  the multi-frame cross-tally happens in the lake scanner, not on one chart — tooltips
  updated to say so explicitly.
- v1 file kept at `versions/FABLE_PLAYBOOK_v1.pine`, unmodified.

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
