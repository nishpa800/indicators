# ⭐ INDICATOR INDEX — the one place. Load ONLY from here.

**Read this first:** I cannot run TradingView in this environment. Every "fixed" below is
**code-level (static)**. A build is only truly trusted once **you** load it and it compiles
clean. TradingView **caches the old source** — when a build is updated you MUST re-paste the
raw file, or you'll keep seeing the old error.

### Status legend
- ✅ **CONFIRMED** — you loaded it, no error.
- 🟡 **FIXED IN CODE, NOT CONFIRMED** — known errors patched in source; awaiting your live load.
- ❌ **BROKEN / UNRESOLVED** — known error not yet fixed. Do **not** rely on it. (none right now)

### Hard rules
- Load **only** from the tables below. **Never** load anything under `imports/` or `versions/` —
  those are originals and still carry the RE10023 / RE10140 / RE10008 bugs.
- Hit an error? Paste me the trace. I'll flip that row to ❌, quarantine it, and not present it
  as working until it's actually fixed + you confirm.

Branch: `claude/keen-faraday-mzq2i2`. "Raw" = one-click plain text to paste into the Pine editor.

---

## SET A — tick-safe builds (`tick_friendly/`)

| Study | Chart label | Status | Raw |
|---|---|---|---|
| **ULTRA Combo v57** | `ULTRA v57 TF` | 🟡 RE10023 + RE10140 + RE10008 all fixed in code (`f833541`). **Re-paste the raw — TV cached the old one.** | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/ultra-combo/tick_friendly/ULTRA_COMBO_v57_tick_friendly.pine) |
| SQUARIFY 46 v2 | `SQ46 v2` | 🟡 RE10023 (anchor **+ time-session**) + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/squarify/tick_friendly/SQUARIFY_46_v2_tick_friendly.pine) |
| SQUARIFY 46 v3.1 | `SQ46 v3.1 TF` | 🟡 RE10023 + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/squarify/tick_friendly/SQUARIFY_46_v3.1_tick_friendly.pine) |
| HVD↔PBJ↔PPD Bearish | `HVD PBJ BEAR TF` | 🟡 RE10023 + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine) |
| HVD↔PBJ↔PPD Bullish | `HVD PBJ BULL TF` | 🟡 RE10023 + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BULLISH_v1_tick_friendly.pine) |
| HVD Combo Chain | `CC FIX TICK` | 🟡 RE10023 + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/hvd-pbj-ppd/tick_friendly/COMBO_CHAIN_FIXED_tick_friendly.pine) |
| B2B PUP v5.4 | `B2B PUP 5.4*` | 🟡 RE10023 + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/b2b-pup/tick_friendly/B2B_PUP_Combined_v5.4_tick_friendly.pine) |
| TNT OD v3 | `TNT OD v3 TF` | 🟡 RE10023 + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/tnt-od/tick_friendly/TNT_OD_v3_tick_friendly.pine) |
| VOB v11 FULL | (long title) | 🟡 RE10023 + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/vob/tick_friendly/VOB_v11_FULL_TICKFRIENDLY_2026-06-04.pine) |
| VOB v11 MULTIPLES | (long title) | 🟡 RE10023 + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/vob/tick_friendly/VOB_v11_MULTIPLES_TICKFRIENDLY_2026-06-04.pine) |
| Heavy Weapons NRA v1 | `RVOL NRAFR x2` | 🟡 RE10023 + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/heavy-weapons-nra/tick_friendly/HEAVY_WEAPONS_NRA_v1_tick_friendly.pine) |
| Heavy Weapons ULTRA v1 | `HW ULTRA b2b1` | 🟡 RE10023 + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/heavy-weapons-ultra/tick_friendly/HEAVY_WEAPONS_ULTRA_v1_tick_friendly.pine) |
| Heavy Weapons Single v3 | `HW Single v3` | 🟡 RE10023 (anchor) + tfSec fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/heavy-weapons-single/tick_friendly/HEAVY_WEAPONS_SINGLE_v3_tick_friendly.pine) |
| HUB 1020 1153am | `Hub102011a` | 🟡 RE10023 (**time-session**) fixed | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/hub-1020-1153am/tick_friendly/HUB_1020_1153am_Hub102011a_v20260604_tick_friendly.pine) |

## SET B — date-roll experimental (`dateroll/`, shorttitle ` DR`)
Same builds, relabeled ` DR` so they load **beside** Set A for A/B. The 3 marked **DR-logic** answer "fired yesterday?" with day-rolled state (works on tick, no RE10008); the other 10 are logic-identical copies of Set A.

| Study | Chart label | Status | Raw |
|---|---|---|---|
| **ULTRA Combo v57** | `ULTRA v57 TF DR` | 🟡 DR-logic + all 3 RE fixes | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/ULTRA_COMBO_v57_DR.pine) |
| **SQUARIFY 46 v2** | `SQ46 v2 DR` | 🟡 DR-logic | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/SQUARIFY_46_v2_DR.pine) |
| **SQUARIFY 46 v3.1** | `SQ46 v3.1 TF DR` | 🟡 DR-logic | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/SQUARIFY_46_v3.1_DR.pine) |
| HVD↔PBJ↔PPD Bearish | `HVD PBJ BEAR TF DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HVD_PBJ_PPD_BEARISH_v1_DR.pine) |
| HVD↔PBJ↔PPD Bullish | `HVD PBJ BULL TF DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HVD_PBJ_PPD_BULLISH_v1_DR.pine) |
| HVD Combo Chain | `CC FIX TICK DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HVD_COMBO_CHAIN_DR.pine) |
| B2B PUP v5.4 | `B2B PUP 5.4* DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/B2B_PUP_v5.4_DR.pine) |
| TNT OD v3 | `TNT OD v3 TF DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/TNT_OD_v3_DR.pine) |
| VOB v11 FULL | `VOB v11 FULL DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/VOB_v11_FULL_DR.pine) |
| VOB v11 MULTIPLES | `VOB v11 MULT DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/VOB_v11_MULTIPLES_DR.pine) |
| Heavy Weapons NRA v1 | `RVOL NRAFR x2 DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HEAVY_WEAPONS_NRA_v1_DR.pine) |
| Heavy Weapons ULTRA v1 | `HW ULTRA b2b1 DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HEAVY_WEAPONS_ULTRA_v1_DR.pine) |
| Heavy Weapons Single v3 | `HW Single v3 DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HEAVY_WEAPONS_SINGLE_v3_DR.pine) |
| HUB 1020 1153am | `Hub102011a DR` | 🟡 copy of Set A | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/keen-faraday-mzq2i2/dateroll/HUB_1020_1153am_v20260604_DR.pine) |

## Errors tracked so far
| Error | What it was | Where | Status |
|---|---|---|---|
| RE10023 | blank `relativeVolume` anchor crashes `timeframe.change` on tick | all builds | fixed in code (anchor → `"D"` on tick) |
| RE10023 #2 | `time(timeframe.period, session)` crashes on tick (session detection) — MISSED in the first pass | SQUARIFY v2 + HUB | fixed in code (resolution → `"1"` on tick) |
| RE10140 | >64 plot-objects (data-window matrix) | ULTRA 57 only | fixed in code (matrix removed → 50) |
| RE10008 | `f_hadSignalYesterday` scanned `sig[i]` past 5000 bars | ULTRA 57 only | fixed in code (`f_firedPrevDay` date-roll, `f833541`) |
| RE10008 (watch) | `ta.highest(volume,5000)[1]` sits at the 5000-bar boundary | ULTRA 57 + others | not changed — report if it recurs at ~5000 and I'll harden |

The gate `tools/check_plot_budget.sh` enforces the ≤64-plot / no-data-window rule on every build in both sets.
