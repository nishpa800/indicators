# Displacement 4x — CHANGELOG

## v1 — 2026-05-10

Initial drop. Pine v5, overlay.

`DISP_4X_v1.pine` runs four independent displacement engines (D1, D2, D3,
D4) with different default σ-multipliers (6.5 / 6.0 / 5.5 / 5.0). Each
engine produces a Bull and a Bear plotshape, totalling **8 root detection
plots** in one indicator.

Why: Anish stacks 4 instances of this indicator on his chart for **16
simultaneous displacement-strength views**. Each instance can be tuned
to different multipliers and timeframes, giving him a multi-tier
diagnostic of displacement intensity at every key bar — which strengths
fire alongside which other detection plots, on which timeframes, at
which levels.

All 8 plots use `offset = -1` because FVG confirmation happens on bar[0]
but the displaced candle is bar[1]. Plotting on bar[1] aligns the marker
with the actual displacement bar, so any combo system checking for
co-signals can compare against bar[1] directly.

Per the bible's IPSF rule, every multiplier is `input.float(step=0.1)`
— Anish tunes from TradingView's settings panel; defaults across
instances are packaging choices, not corruption.

Future: may expand to `disp-16x` (15-20 displacement engines per
indicator) using the same `D<n>_BULL` / `D<n>_BEAR` naming pattern.
