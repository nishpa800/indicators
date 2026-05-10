# PB & PBJ — CHANGELOG

## v1 — 2026-05-10

Initial drop. Pine v5, overlay.

`PB_PBJ_v1.pine` extracted from the YY+D+PBJ source as the canonical
isolated PB/PBJ engine. Four root detection plots:

- `pb-pbj::PB_BULL`  — `sigBullPB`  (offset = 0, shape.labelup belowbar, aqua)
- `pb-pbj::PBJ_BULL` — `sigBullPBJ` (offset = 0, shape.diamond belowbar, yellow)
- `pb-pbj::PB_BEAR`  — `sigBearPB`  (offset = 0, shape.labeldown abovebar, orange)
- `pb-pbj::PBJ_BEAR` — `sigBearPBJ` (offset = 0, shape.labeldown abovebar, red)

OKEH Zoo + PB&J Filter + Supertrend defaults preserved verbatim from the
parent YY+D+PBJ:

- Zoo MA: VWMA(close, 5)
- PB&J Filter: MA period 20, ATR period 14, HH/LL lookback 25, ATR mult 3.0, vol period 20, vol mult 0.1
- Supertrend: ATR period 10, multiplier 2.0, applied (toggle ON by default)

All settings exposed as Pine `input.*` (IPSF — tunable from TradingView's
settings panel). Per the bible's IPSF taxonomy, default differences across
indicators that name the same primitive are NOT corruption — Anish tunes
in settings.

Mutual exclusion: a bar that satisfies both PB and PBJ on the same
direction is classified as PBJ; the PB plot is suppressed.

Non-repainting guarantee:
- All four signals gated by `barstate.isconfirmed`
- All `alert()` calls use `alert.freq_once_per_bar_close`
- 1:1 parity between plot and alert log

Includes 9-option Alert Multiplexer (`mux_choice` input) routing a single
`alert()` call per user-selected signal combination.
