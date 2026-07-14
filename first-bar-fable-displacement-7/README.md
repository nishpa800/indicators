# First Bar Fable Displacement 7

Variant of [First Bar Fable v2](../first-bar-fable/) with the **"Displacement 9" engine
default σ-multiplier = 7** (the input stays adjustable on the chart). Everything else is
byte-identical to the base — same S1–S27 plot keys, same engines, same offsets, same
defaults — so cross-study comparison stays clean. Ordered by Anish 2026-07-13.

- **Current version: v1** — `versions/FIRST_BAR_FABLE_DISPLACEMENT_7_v1.pine`
- Chart title `First Bar Fable Displacement 7`, shorttitle `1st BAR FABLE D7`.
- The σ default drives S1, S2, S9, S10, S15, S18, S19, S22/S23, S24/S25 through the single
  `i_d9_mult` input (no hardcoded 9σ exists anywhere in the code — census-verified).
- All OTHER displacement engines untouched: HV+D σ=5 · DYNAMITE σ=5 · TNT OD σ=5 ·
  TNT Napalm σ=5 · HCT σ=6 · Gate σ=6.5.

## Load into Pine editor

Raw code (copy-paste):
<https://raw.githubusercontent.com/nishpa800/indicators/claude/first-bar-fable-indicator-eorleb/first-bar-fable-displacement-7/versions/FIRST_BAR_FABLE_DISPLACEMENT_7_v1.pine>

Or locally: `pbcopy < first-bar-fable-displacement-7/versions/FIRST_BAR_FABLE_DISPLACEMENT_7_v1.pine`
→ TradingView → Pine Editor → Cmd+A → Cmd+V → Cmd+S → Add to chart.

## Change control

Every edit to this study runs through a W-INDSTUDY transform manifest (lake:
`validation/wrappers/indicator_study_gate.py`): declared base sha256 + enumerated edits,
machine-verified diff == manifest, rolling-windows / RE10023 / 64-output gates, CHANGELOG
entry, same-turn GitHub push. New version = new file in `versions/`, never overwritten.
