# ⭐ `dateroll/` — date-roll recut of every tick build (A/B test set)

Parallel copies of all 13 tick-friendly builds, each with its indicator **shorttitle suffixed
` DR`** so you can load them on the **same chart** as your current builds without a name
collision. Purpose: see whether the date-roll approach yields better results.

## What "date-roll" (DR) means
"Did signal X fire **yesterday**?" used to be answered by scanning backwards bar-by-bar
(`for i = 1 to … : sig[i]`). On tick/second charts that reaches thousands of bars back →
either **RE10008** (ULTRA 57's `barsPerDay*2` scan) or it silently never reaches yesterday
(SQUARIFY's `for i=1 to 500` cap — a tick day is far more than 500 bars). DR replaces that
with **`f_firedPrevDay()`**: O(1) state (`firedToday` / `firedPrev`) rolled at the day
boundary via `ta.change(dayofmonth)`. **Zero historical bar references** → can't hit the
5000-bar limit, and it's correct on every timeframe.

## What changed where
- **Date-roll applied (3):** `ULTRA_COMBO_v57_DR`, `SQUARIFY_46_v2_DR`, `SQUARIFY_46_v3.1_DR`
  — these were the only builds doing multi-day lookback. Their B2B-days / consecutive-day
  combos now use `f_firedPrevDay` and will actually fire on tick.
- **Renamed copies (10):** B2B PUP, TNT OD, VOB×2, HVD×3, Heavy Weapons NRA/ULTRA, HUB — no
  multi-day lookback to convert, so these are logic-identical to their `tick_friendly/`
  counterparts, just relabeled ` DR` for side-by-side testing.

All 13 pass `tools/check_plot_budget.sh` (≤64 plot-objects, zero `display.data_window` plots).

## Load these (raw → paste into the Pine editor)

| Build | Chart label | Raw |
|---|---|---|
| ULTRA Combo v57 | `ULTRA v57 TF DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/ULTRA_COMBO_v57_DR.pine) |
| SQUARIFY 46 v2 | `SQ46 v2 DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/SQUARIFY_46_v2_DR.pine) |
| SQUARIFY 46 v3.1 | `SQ46 v3.1 TF DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/SQUARIFY_46_v3.1_DR.pine) |
| HVD↔PBJ↔PPD Bearish | `HVD PBJ BEAR TF DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HVD_PBJ_PPD_BEARISH_v1_DR.pine) |
| HVD↔PBJ↔PPD Bullish | `HVD PBJ BULL TF DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HVD_PBJ_PPD_BULLISH_v1_DR.pine) |
| HVD Combo Chain | `CC FIX TICK DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HVD_COMBO_CHAIN_DR.pine) |
| B2B PUP v5.4 | `B2B PUP 5.4* DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/B2B_PUP_v5.4_DR.pine) |
| TNT OD v3 | `TNT OD v3 TF DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/TNT_OD_v3_DR.pine) |
| VOB v11 FULL | `VOB v11 FULL DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/VOB_v11_FULL_DR.pine) |
| VOB v11 MULTIPLES | `VOB v11 MULT DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/VOB_v11_MULTIPLES_DR.pine) |
| Heavy Weapons NRA v1 | `RVOL NRAFR x2 DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HEAVY_WEAPONS_NRA_v1_DR.pine) |
| Heavy Weapons ULTRA v1 | `HW ULTRA b2b1 DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HEAVY_WEAPONS_ULTRA_v1_DR.pine) |
| HUB 1020 1153am | `Hub102011a DR` | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HUB_1020_1153am_v20260604_DR.pine) |

> Only the 3 date-roll builds differ in logic from `tick_friendly/`; the rest are renamed
> copies. If the experiment wins, these become the canonical set; if not, delete the folder.
