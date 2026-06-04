# Heavy Weapons NRA — CHANGELOG

## v1 — 2026-06-04 (canonical home created)
- First canonical version of "Heavy Weapons NRA + GZI/FVG + Matrix Combos
  2 bodies not 1 NRAFR" (shorttitle "RVOL NRAFR x2").
- Source intake: full Pine v5 pasted from chat.
- Previously only present under `indicators/imports/20260531T103840_indicator_studies/`
  (import SHA `d89c82d48c3bef0d…`). Pasted source is functionally IDENTICAL to that
  import — the only diff is three removed inline comment lines (no logic change),
  so the pasted source is adopted as the canonical v1 and given a real home.
- Three-output conversion produced (see MANIFEST_three_outputs_2026-06-04.md).

## v1 tick-friendly — RE10023 anchor fix — 2026-06-04 (live-verified)
- BUG (caught live on a 1000T tick chart): tv_ta.relativeVolume() calls
  timeframe.change(anchor) internally → throws "RE10023: Cannot call
  timeframe.change with a tick-based timeframe" on bar 0 when the Reg@Time anchor
  resolves to the (tick-based) chart TF. input.timeframe("") = chart TF, so every
  tick-friendly build that left the anchor blank crashed on tick charts.
- FIX: reg_anchorSafe forces anchor "D" ONLY when the chart is tick-based
  (blank-on-tick) or an explicit tick anchor ("…T") is chosen. Time charts keep
  the exact original blank-anchor behavior (byte-identical), so no time-chart
  parity drift. Applied to BOTH relativeVolume calls.
- LIVE VERIFY: full script compiled + RAN on NASDAQ 1000T tick chart, no RE10023,
  real intermediates: relVol=4.11, bb_normPrice=2.21, bb_smaDiff=0.7745, ATR=0.3937.
- SAME FIX applied suite-wide to every other tick-friendly build that calls
  relativeVolume: squarify (SQUARIFY_LTF_v1), tnt-od (TNT_OD_v3), vob (FULL +
  MULTIPLES). 13 call sites across 5 files now tick-safe; 0 raw anchors remain.
