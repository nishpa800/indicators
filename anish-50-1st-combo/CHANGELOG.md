# Anish 50% 1st Combo — CHANGELOG

## v1 — 2026-05-10

Initial drop. Pine v6, non-repainting. Combines Pocket Pivot (PUP/PPD) +
Anish Stage 2/4 EMA stack + optional Gap Up/Down + Super PUP/PPD same-bar
confluence + TB / Foster transition signals (X consecutive Anish bars then
Y follow-up bars of opposing PP).

- All signal generation gated by `barstate.isconfirmed`.
- All `var`-state updates (TB/Foster counters) gated by confirmed bar to
  prevent mid-bar state corruption.
- Plots and alerts share the same `fire_*` booleans → 1:1 parity.
- Inputs: % Change (Barsize), PP Lookback Days, Gap-Up/Down toggles, Gap
  Value %, Min Anish Bars (X), Follow-up PP Bars (Y).
