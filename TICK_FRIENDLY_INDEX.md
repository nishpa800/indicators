# ⭐ TICK-FRIENDLY BUILDS — LOAD THESE ON TICK CHARTS

**The single source of truth for which file to paste into TradingView.**

Every study has two copies:
- `…/versions/…` — the as-received original. Uses a **blank `relativeVolume` anchor** and an
  **unguarded `timeframe.in_seconds`**, so on a **tick** chart it throws **RE10023 on bar 0** and/or
  silently kills thresholds. **Do NOT load these on tick charts.**
- `…/tick_friendly/…` — the corrected build. Routes `relativeVolume` through a forced-time anchor
  (`"D"` on tick, `""` on time = parity preserved) and guards `tfSec` via `str.endswith(timeframe.period, "T")`.
  **Works on BOTH tick and time charts.** ← **load these.**

Links below are on branch **`claude/keen-faraday-mzq2i2`**. "Raw" = one-click plain text to paste into the Pine editor.

| Study | View | Raw (paste into TradingView) |
|---|---|---|
| **Heavy Weapons ULTRA** | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/heavy-weapons-ultra/tick_friendly/HEAVY_WEAPONS_ULTRA_v1_tick_friendly.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/heavy-weapons-ultra/tick_friendly/HEAVY_WEAPONS_ULTRA_v1_tick_friendly.pine) |
| **ULTRA Combo v57** | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/ultra-combo/tick_friendly/ULTRA_COMBO_v57_tick_friendly.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/ultra-combo/tick_friendly/ULTRA_COMBO_v57_tick_friendly.pine) |
| **HVD↔PBJ↔PPD — BEARISH (36)** | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine) |
| **HVD↔PBJ↔PPD — BULLISH** | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BULLISH_v1_tick_friendly.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BULLISH_v1_tick_friendly.pine) |
| HVD — Combo Chain | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/hvd-pbj-ppd/tick_friendly/COMBO_CHAIN_FIXED_tick_friendly.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/hvd-pbj-ppd/tick_friendly/COMBO_CHAIN_FIXED_tick_friendly.pine) |
| B2B PUP v5.4 | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/b2b-pup/tick_friendly/B2B_PUP_Combined_v5.4_tick_friendly.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/b2b-pup/tick_friendly/B2B_PUP_Combined_v5.4_tick_friendly.pine) |
| TNT OD v3 | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/tnt-od/tick_friendly/TNT_OD_v3_tick_friendly.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/tnt-od/tick_friendly/TNT_OD_v3_tick_friendly.pine) |
| SQUARIFY 46 v3.1 | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/squarify/tick_friendly/SQUARIFY_46_v3.1_tick_friendly.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/squarify/tick_friendly/SQUARIFY_46_v3.1_tick_friendly.pine) |
| VOB v11 — FULL | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/vob/tick_friendly/VOB_v11_FULL_TICKFRIENDLY_2026-06-04.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/vob/tick_friendly/VOB_v11_FULL_TICKFRIENDLY_2026-06-04.pine) |
| VOB v11 — MULTIPLES | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/vob/tick_friendly/VOB_v11_MULTIPLES_TICKFRIENDLY_2026-06-04.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/vob/tick_friendly/VOB_v11_MULTIPLES_TICKFRIENDLY_2026-06-04.pine) |
| Heavy Weapons NRA v1 | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/heavy-weapons-nra/tick_friendly/HEAVY_WEAPONS_NRA_v1_tick_friendly.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/heavy-weapons-nra/tick_friendly/HEAVY_WEAPONS_NRA_v1_tick_friendly.pine) |
| HUB 1020 1153am | [view](https://github.com/nishpa800/indicators/blob/claude/keen-faraday-mzq2i2/hub-1020-1153am/tick_friendly/HUB_1020_1153am_Hub102011a_v20260604_tick_friendly.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/hub-1020-1153am/tick_friendly/HUB_1020_1153am_Hub102011a_v20260604_tick_friendly.pine) |

## Gate (run before calling any build "done")
```bash
# must return nothing — no literal blank anchor at a relativeVolume call site:
grep -nE 'relativeVolume\([^,]+,\s*""' <file> | grep -vE '^[0-9]+:\s*//'
```
Tick detection everywhere keys off `str.endswith(timeframe.period, "T")` — the authoritative signal
(`timeframe.in_seconds()` can return a positive value on tick, so na/≤0 alone is not enough).
