# PB & PBJ ⭐

**Canonical isolated PB / PBJ engine for the indicator suite.** Pine v5,
overlay. Extracted from Yin Yang + Displacement + PBJ (YY+D+PBJ) source —
this is the cleanest, most-isolated implementation of the OKEH Zoo +
PB&J Filter + Supertrend pipeline that produces the four PB/PBJ
detections.

## Roots (4)

All `offset = 0`. All gated by `barstate.isconfirmed`. All alerts use
`alert.freq_once_per_bar_close` for non-repainting 1:1 parity with
plotted signals.

| Canonical | Pine bool | Plot |
|---|---|---|
| `pb-pbj::PB_BULL`  | `sigBullPB`  | `shape.labelup` belowbar, aqua |
| `pb-pbj::PBJ_BULL` | `sigBullPBJ` | `shape.diamond` belowbar, yellow |
| `pb-pbj::PB_BEAR`  | `sigBearPB`  | `shape.labeldown` abovebar, orange |
| `pb-pbj::PBJ_BEAR` | `sigBearPBJ` | `shape.labeldown` abovebar, red |

PB and PBJ are **mutually exclusive on the same direction**:
- `sigBullPB = isconfirmed AND sig_pb_buy AND NOT sig_pbj_buy`
- `sigBearPB = isconfirmed AND sig_pb_sell AND NOT sig_pbj_sell`

A bullish bar that satisfies both filters is classified as PBJ (the
stronger signal); the PB plot is suppressed.

## Engine internals (NOT roots — per the bible's STOP rule)

The OKEH pipeline is internal mechanics of PB/PBJ, not separate roots:

- **Zoo Engine**: `f_ma()` switch over VWMA/EMA/SMA/WMA/HMA, default VWMA(close, 5)
- **PB&J Filter**: ATR-banded EMA wick test — `low/high` outside `pbj_ma ± thresh`, with HH/LL lookback (25) and volume gate (vol > avg_vol × 0.1)
- **Supertrend**: ATR(10) × 2.0 trailing-stop, drives `st_dir`, used as the cross signal
- **Level management**: per-direction zone arrays (`bull_lvls`, `bear_lvls`) tracking landing-box approach via `f_check_approach()`

Per `docs/glossary.md` "Root vs composite": PB and PBJ are roots. Zoo MA,
Supertrend, and the PB&J filter are internal helpers documented in the
extraction YAML's `internal_helpers:` section.

## Files

- `versions/PB_PBJ_v1.pine` — canonical (Pine v5, overlay)

## Bible

- `bible-input/extract-pb-pbj.yaml` — full extraction (4 roots, 0 composites)
- `docs/lineage/pb-pbj__*.md` — lineage cards for the 4 alerting signals
- `docs/redundancy.md` — relates `pb-pbj::*` to `hvd-pbj-ppd::PBJ_BULL/BEAR`
  / `hvd-pbj-ppd::PB_BULL/BEAR` (the PBJ Engine 6 outputs in HVDPBJPPD).
  Stage 7 byte-diff will determine whether they're identical or drifted.

## Multiplexer

The indicator includes an Alert Multiplexer input (9 selections) that
routes a single `alert()` call to fire only for user-chosen signal
combinations: All / Bull-only / Bear-only / PB-only / PBJ-only / per-signal.

## Branch provenance

Added to `claude/organize-indicators-hierarchy-8JDw1` in Stage 7. Pending
PR merge to `main`.

## Why this lives in its own indicator

Per Anish: "the original pbj and pb engine just those so they are roots".
Isolating PB/PBJ in their own Pine file makes them tractable for Stage 2
test-indicator coverage (the 110 KB HVDPBJPPD canonical was too complex
to verbatim-copy for `ROOTS_CANDLE_TEST_v1.pine` — Engine 6's stateful
landing-box arrays were deferred). With `pb-pbj::*` as the canonical,
the test indicator can now mirror this file directly in a future
Stage-2 update.
