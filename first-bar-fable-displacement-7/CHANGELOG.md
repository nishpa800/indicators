# First Bar Fable Displacement 7 — Changelog

Newest first. Each version = one file in `versions/`.

---

## v3 — 2026-07-15: STYLE LAYER — white text · 50% transparency · size tiers (L-49 W-INDSTUDY three-pack wave)

**Files:** `versions/FIRST_BAR_FABLE_DISPLACEMENT_7_v3.pine` (time) + `versions/FIRST_BAR_FABLE_DISPLACEMENT_7_NTS_v3.pine` (NTS twin, A7 pair).
plotshape() STYLE layer ONLY — 57 plotshape calls per file retextured; zero engine / alert / checkbox / plot-title / plot-count changes. The `First Bar Fable Displacement 7` engine and every alert are byte-identical to the prior version; the per-line diff is EXACTLY the 57 plotshape lines (byte-verified, D=0).

- **White label text:** every plotshape `textcolor` is now `color.white` (57/57). The 5 previously-black labels (S10 B2B SAAB, S16 B2B Napalm Bull, S18 B2B PUP, HV+D+PBJ 3of3 Bull, HV+D+PBJ 3of3 Bear) flipped to white; the other 52 were already white.
- **50% transparency shape colors:** every plotshape shape color is wrapped to `color.new(<hue>, 50)` (57/57) — hues UNCHANGED (bull/bear color audit preserved). Named colors, hex literals, and color variables alike now carry transparency 50; no bare shape colors and no other transparency value remain.
- **Size tiers — normal / large / huge:**
  - **HUGE (12 — BOSS, the heaviest multi-condition composites):** CO HV+D+PBJ/PB+USE Bull/Bear (×4), B2B HV+D+PBJ Bull/Bear, S24/S25 Unified Combo Bull/Bear + Disp9, S26/S27 B2B TNT/NPM ENR Bull/Bear incl. their (T1st) variants.
  - **NORMAL (5 — lightest singles):** S11/S12 Dynamite Bull/Bear, S22/S23 D9 Bull/Bear Study, S15 Nagasaki 1stBar+.
  - **LARGE (40):** every other plotshape.
- Exact per-title tier assignment recorded in `validation/indstudy/fbf_size_tiers_v1.json`; gated by `validation/wrappers/indicator_study_gate.py` (D=0) plus a dedicated style-check with an anti-fixture.

---

## v2 — 2026-07-15: ALERT GRAMMAR v3 (L-49 W-INDSTUDY wave)

**Files:** `versions/FIRST_BAR_FABLE_DISPLACEMENT_7_v2.pine` (time) + `versions/FIRST_BAR_FABLE_DISPLACEMENT_7_NTS_v2.pine` (NTS twin, A7 pair).
Alert-layer ONLY — no plot, checkbox, or engine logic changed; the `First Bar Fable Displacement 7` engine and all plotshapes are byte-identical to the prior version (helper block + ALERTS block are the sole diffs).

- **Plot-key-first grammar:** every alert message now leads with the canonical semantic plot key (TYPHOON, MUSASHI, WHALE+PUP, DYNAMITE, IGNITE, NAG, B2B_NPM, B2B_PUP+D9, UC+D9, B2B_ENR, HVD_MOMENTUM, …) then `Bull`/`Bear` once (never the S-ordinal; `S13`-style tokens are banned from messages), then `| {{ticker}} {{interval}} |` metadata `FB=Y/N`.
- **Measured Displacement:** d9 signals carry `D=` = the measured σ ratio (`d9_rng/d9_std`, or `max(bar0,bar1)` for `or[1]` signals), one decimal.
- **RVOL:** SAAB/KRATOS/GS/MOAB/RVOL1X signals carry `RVOL=` = `rv_normPrice`, one decimal.
- **VRANK:** tick-safe calendar record-high flag `ATH/YH/QH/MH/WH` (trackers key off bar time only — no anchored windows, no bar_index).
- **NTH:** Nagasaki (side-less) carries `NTH=Y#,Q#,M#` all-time-record ordinals + `DIR=NONE`.
- **CO co-fires:** every message appends ` CO=<other canonical keys firing this bar>` when non-empty.
- **Checkbox biconditional preserved:** each alert keeps its EXACT `en_*`/`fire_*`/first-bar guard — an unchecked plot can never alert; a checked + firing plot must alert. No alert added or removed (35 alert() calls, same as base).
- No raw volume in any message; no commas inside numbers; one decimal everywhere.

---

## v1-NTS — 2026-07-14: non-tick-friendly twin per L-49 TWIN MANDATE; sole deltas = tfSec guard removed + raw relativeVolume anchor + NTS title; T-NTS: identical on time intervals; never load on tick charts.

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
