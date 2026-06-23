# CHANGELOG — AP Bounce Pro

## 2026-06-23 — v2.0 (initial commit of stripped + extended rebuild)

Rebuilt from source `AP Bounce Pro v1.022` (Pine v5). The source was a ~30-plot
kitchen-sink oscillator (EOT 1/2/3, LSMA Wave Trend, S/R breaks, long/short
entries, bar colors, fib lines, ~16 alertcondition()s). v2.0 keeps **only** the two
bounce detections and adds four rolling / confluence detections, a checkbox-gated
visual layer, and one non-repainting "Any alert() function call" alert.

`versions/AP_BOUNCE_PRO_v2.pine`

### Kept (verbatim) from source
- **Bounce Up** `ta.barssince(ta.crossunder(wt2,20)) <= 1 and ta.crossover(wt2,20)`
- **Bounce Down** `ta.barssince(ta.crossover(wt2,80)) <= 1 and ta.crossunder(wt2,80)`
- The `wt2` engine (`tradition`/`tci`/`mf` → `ta.sma(wt1,6)`) and its inputs
  `WT master` (9) / `Time 1` (6) / `Time 2` (3).

### 8 detection plots (each = one boolean → drives BOTH its plotshape and the alert)
| # | Signal | Plot offset / range candle |
|---|--------|----------------------------|
| S1 | Bullish Bounce Up | 0 / bar[0] |
| S2 | Bearish Bounce Down | 0 / bar[0] |
| S3 | Bullish Window — ≥X bounce-ups sharing a price level within rolling Y bars | 0 / bar[0] |
| S4 | Bearish Window — ≥X bounce-downs sharing a price level within rolling Y bars | 0 / bar[0] |
| S5 | Bull Bounce + Displacement/High-Vol on the same candle | −1 / bar[1] |
| S6 | Bear Bounce + Displacement/High-Vol on the same candle | −1 / bar[1] |
| S7 | Bull Bounce + Bullish Order Block within ±P bars | −(periods+1) / OB candle |
| S8 | Bear Bounce + Bearish Order Block within ±P bars | −(periods+1) / OB candle |

### Window logic (S3/S4) — rolling, non-anchored
- Per-direction buffers remember the last **N** (default 10) bounce candles.
- Fires once when a newly-confirmed bounce becomes the **X**-th (default 3) bounce
  sharing a common price level (inclusive interval overlap / "stabbing") among
  buffered bounces within the trailing **Y** (default 100) bars. Non-consecutive
  is fine; opposite-direction bounces are ignored (separate buffers).
- Passes the repo `check_no_fixed_windows.sh` gate (rolling trailing lookback, no
  `var int …StartBar` / `bar_index - …Start >= len` anchor).

### Confluence (S5/S6, S7/S8)
- **High volume** = `volume[1] == ta.highest(volume, hvLook)[1]` (default lookback 50;
  ported from the HV ladder ≥-tier). **Displacement** = single std-dev + FVG engine
  ported from "Displacement 4x" (default len 100, mult 5.0). Both anchor on bar[1]
  (the displaced candle), so S5/S6 mark the bounce candle at offset −1.
- **Order Block** detection ported from the v6 "OBF" study to v5 (detection only —
  no boxes/channels/panel). OB candle = bar[periods+1]; fires at OB discovery when a
  same-direction bounce is within ±P (default 5) bars of the OB candle. Drawn at
  offset −(periods+1) — the OB candle.

### Alerts
- Replaced ~16 `alertcondition()`s with ONE `alert(..., alert.freq_once_per_bar_close)`.
  Set one TradingView alert with condition **"Any alert() function call."** The message
  is `ticker | tf | <SIGNAL NAME(S)> (L-H low-high) …` — only signals whose **Global
  Alerts** checkbox is on are included; each names itself + its candle's low–high range.

### Non-repaint + parity
- Every signal is gated on `barstate.isconfirmed`; each plotshape and its alert range
  use the SAME offset, so marker and alert always describe the identical closed candle.
- Visibility gated by the 8 **Visual Plots** checkboxes; alert inclusion by the 8
  **Global Alerts** checkboxes.

### Notes / flagged assumptions
- S5/S6 use offset −1 per the Displacement 4x code/header ("compare against bar[1]"),
  not 0 — the only non-repainting way to put displacement on the bounce candle.
- "High volume ≥ 50" interpreted as the 50-bar volume-high tier (lookback is an input).
- Displacement uses a single engine at mult 5.0 (loosest ⇒ ≈ "any" of DISP 4x's tiers).
- relativeVolume is not used here, so the tick-chart RE10023 doctrine does not apply.
