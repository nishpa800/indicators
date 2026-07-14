# First Bar Fable Displacement 7 — Changelog

Newest first. Each version = one file in `versions/`.

---

## v1 — 2026-07-13

**File:** `versions/FIRST_BAR_FABLE_DISPLACEMENT_7_v1.pine` — chart title
**"First Bar Fable Displacement 7"**, shorttitle **"1st BAR FABLE D7"**.

- Operator order (Anish, 2026-07-13): new study identical to First Bar Fable v2 with the
  **"Displacement 9" engine default σ-multiplier set to 7**.
- **Base:** `first-bar-fable/versions/FIRST_BAR_FABLE_v2.pine` @ commit `5ec5ef9`,
  sha256 `d412ff6a59edd958ca4b99cff377098d2dc1584ddd364492570cd792d46add00`. The base is
  byte-identical (modulo trailing newline) to the operator's Desktop original
  "Fabe 2 original needs 5 and 7 and a lot more.txt"
  (sha256 `cfb03981ef582489757ebddc36bbf69f1b1a0386794917d1152c1a3aa91c9e36`, exported 2026-07-13 19:42 CT).
- **Exactly 3 diff hunks vs base (machine-verified, transform-manifest built):**
  1. comment-only VARIANT header at top of file;
  2. `indicator()` title/shorttitle;
  3. `i_d9_mult` default `9.0 → 7.0` + label `"(7 strength)"`.
- The σ default propagates to S1, S2, S9, S10, S15, S18, S19, S22/S23, S24/S25 via the
  single `i_d9_mult` input — displacement census confirmed **no hardcoded 9σ in code**
  (only comments/tooltips, which the VARIANT header corrects for this study).
- All other displacement engines UNTOUCHED: HV+D σ=5 · DYNAMITE σ=5 · TNT OD σ=5 ·
  TNT Napalm σ=5 · HCT σ=6 · Gate σ=6.5 (operator: "don't change anything I did not
  tell you to change").
- **Gates:** no-fixed-windows PASS · RE10023 anchor-grep clean (0 hits) · 57/64 plot
  outputs (incl. alertconditions) · `//@version=5`.
- **Compile:** delta vs base is compile-neutral by token class (comments / string
  literals / one float literal); base compiles (operator's live-chart export same day).
  Live TV compile gate pending (TV desktop CDP down at build time).
- Output sha256: `80ddbd0c5cfa8d7ecc961d7a11940e06c2faeb0541722aa6394294c8d2afa52d`.
