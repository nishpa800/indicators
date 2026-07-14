# Fable Playbook — Changelog

Newest first. Each version = one file in `versions/`.

---

## v4 + v4-NTS — 2026-07-14: full info-button play cards GENERATED from playbook_v1.json (single source of truth) — every toggle's tooltip = complete card (IDs, status, trigger, evidence integers, entry/stop/exit, ESTIMATED caveat) + 3 ABOUT inputs (playbook overview, evidence & limits, sizing & liquidity law).

**Files:** `versions/FABLE_PLAYBOOK_v4.pine` ("Fable Playbook v4" / "FABLE PLAYS v4") +
`versions/FABLE_PLAYBOOK_v4_NTS.pine` (non-tick-friendly twin, same T-NTS transform as
v3/v3-NTS: tick guard removed, raw `timeframe.in_seconds`, " NTS" title/alert variants).
- New generator `scripts/alpha/gen_playbook_tooltips.py` (lake root): reads
  `contracts/playbook_v1.json`, maps S1..S19 to their play-id family (S18/S19 map to the
  AB-01 literature arm + its mirror, not a JSON play id), and emits ONE deterministic
  tooltip per S — play ids + status(es), one-line what-it-is, compressed trigger, evidence
  (every MEASURED play in the family, id-prefixed; CANDIDATE families get the honest
  "no n>=50 cell yet" fallback), entry/stop/exit (first-MEASURED-play representative for
  multi-play families), and the required ESTIMATED/VALIDATED-promotion caveat sentence.
  Escapes quotes, collapses whitespace, caps at 900 chars (TRIGGER truncated first, then
  EVIDENCE, then the what-it-is clause — ENTRY/STOP/EXIT and the caveat sentence are never
  truncated). Deterministic: re-running produces a byte-identical `S<N>\t<tooltip>` table.
- Closes the L-54 wrapper-lessons finding: hand-written tooltips (v2/v3) had drifted thin
  vs the playbook JSON. The settings-dialog info button is now the complete play card —
  study UI and playbook cannot drift apart, because both read the one JSON file.
- 3 new read-only "about" toggles (`ab_1`/`ab_2`/`ab_3`) at the top of the PLAY TOGGLES
  group, before S1: playbook overview (50 plays, status ladder, portfolio caps,
  automation gate), evidence & limits (scan design, MASS-divides-trend-from-fade key
  finding, single-window/480-cell-scan limits), sizing & liquidity law (quarter-Kelly risk
  cap, square-root-law ADV cap). `input.bool` — do not count toward the output cap.
- Outputs unchanged at 21 (19 plotshape + 2 alertcondition) on both files, `input.bool`
  count 22 (19 play toggles + 3 about toggles) — inputs do not count toward the ≤64 output
  cap. Gates: no-fixed-windows PASS · `//@version=5` first line · zero `relativeVolume(` ·
  v4/v4-NTS diff = 2 hunks (title+alert lines / tfSec guard block), matching the v3/v3-NTS
  pair's hunk count exactly (same T-NTS transform, mechanically re-applied).

## v3-NTS — 2026-07-14 (TWIN MANDATE + AB-03)
**File:** `versions/FABLE_PLAYBOOK_v3_NTS.pine` — the non-tick-friendly twin (operator law:
every study ships BOTH builds). Sole functional delta: tfSec tick guard removed. THEOREM
T-NTS: identical equations on time intervals (guard inert); on tick charts NTS loses every
RVOL-tier play. AB-03 byte-compare pre-registered; operator hypothesis (NTS better on time
frames) is refuted BY CONSTRUCTION for this study — empirical confirmation queued.

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
