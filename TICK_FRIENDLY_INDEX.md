# ⭐ INDICATOR INDEX — the one place. Load ONLY from here.

**Every indicator study in this repo is on this page — no exceptions.** Each study has TWO
columns: the **Original** (non-tick build, for time-based charts — minute/hourly/daily) and the
**Tick build** (for tick intervals like 1000T). If a study is missing either one, that is a bug
in this index — say so and it gets fixed.

**Read this first:** I cannot run TradingView in this environment. Every "fixed"/"new" below is
**code-level (static)**. A build is only truly trusted once **you** load it and it compiles
clean. TradingView **caches the old source** — when a build is updated you MUST re-paste the
raw file, or you'll keep seeing the old error.

### Status legend
- ✅ **CONFIRMED** — you loaded it, no error.
- 🟡 **FIXED/BUILT IN CODE, NOT CONFIRMED** — passes every static gate; awaiting your live load.
- ⚠️ **KNOWN DEFECT** — carries a documented pre-existing defect (see Notes). Do not rely on it.
- ❌ **BANNED / NOT LOADABLE** — do not load, ever.

### Hard rules
- **Tick chart (interval ends in T) → load ONLY from the "Tick build" column.** Originals crash
  (RE10023) or silently die (tfSec=0) on tick.
- **Time chart → load the "Original" column** (bit-for-bit parity with what you've always run).
  The tick builds also work on time charts (guards only activate on tick), but originals are
  the parity reference.
- Hit an error? Paste me the trace. That row flips to ❌, gets quarantined, and is not presented
  as working until fixed + you confirm.

Branch: `claude/indicator-tick-friendly-coverage-8kj0x2`. "raw" = one-click plain text to paste
into the Pine editor. Everything gated by `tools/check_plot_budget.sh` (≤64 plots, zero
`display.data_window`, zero RE10023 patterns) — suite-wide PASS as of 2026-07-13.

---

## SET A — the full matrix (every study: Original ↔ Tick build)

### B2B PUP

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| B2B PUP Combined 5.4.439am (canonical, combo-chain fix) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/b2b-pup/versions/B2B_PUP_Combined_v5.4.pine) | `B2B PUP 5.4*` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/b2b-pup/tick_friendly/B2B_PUP_Combined_v5.4_tick_friendly.pine) | 🟡 |
| B2B PUP 5.4 june7 variant ("NINE NINES") | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/imports/20260531T103840_indicator_studies/pine_v5/b2b_pup_combined_5_4_439am_shorttitle_b2b_pup_5_4.pine) (import snapshot) | `B2B PUP NN` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/b2b_pup_tickfriendly.pine) | 🟡 |
| B2B PUP Combined 4.32 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/b2b-pup/versions/B2B_PUP_v4.32.pine) | `B2B PUP TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/b2b-pup/tick_friendly/B2B_PUP_v4.32_tick_friendly.pine) | 🟡 NEW |
| B2B PUP Combined 4.32 (2026-05-04 TV pull — same content, CRLF endings) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine) | `B2B PUP 0504 TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/b2b-pup/tick_friendly/B2B_PUP_Combined_v4.32_2026-05-04_tick_friendly.pine) | 🟡 NEW |

### SQUARIFY

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| SQUARIFY 46 v3.1 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/versions/SQUARIFY_v3_2026-06-04.pine) | `SQ46 v3.1 TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/tick_friendly/SQUARIFY_46_v3.1_tick_friendly.pine) | 🟡 |
| SQUARIFY 46 v2 (canonical 2026-05-04) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/versions/SQUARIFY_46_v2_2026-05-04.pine) | `SQ46 v2` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/tick_friendly/SQUARIFY_46_v2_tick_friendly.pine) | 🟡 |
| SQUARIFY 46 v2 (early snapshot) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/versions/SQUARIFY_v2.pine) | `SQ46 v2e TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/tick_friendly/SQUARIFY_v2_tick_friendly.pine) | 🟡 NEW |
| SQUARIFY 64 (Alpha Strike source-of-truth) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/versions/SQUARIFY_v1.pine) | `SQ64 TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/tick_friendly/SQUARIFY_v1_tick_friendly.pine) | 🟡 NEW |
| SQUARIFY ATOMS v1 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/versions/SQUARIFY_ATOMS_v1.pine) | `SQ ATOMS TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/tick_friendly/SQUARIFY_ATOMS_v1_tick_friendly.pine) | 🟡 NEW |
| SQUARIFY HTF v1 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/versions/SQUARIFY_HTF_v1.pine) | `SQ HTF v1 TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/tick_friendly/SQUARIFY_HTF_v1_tick_friendly.pine) | 🟡 NEW |
| SQUARIFY v2 BT (backtest strategy) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/backtests/SQUARIFY_v2_BT.pine) | `SQ46 v2 BT TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/squarify/tick_friendly/SQUARIFY_v2_BT_tick_friendly.pine) | 🟡 NEW |
| SQUARIFY v2 STATS | byte-identical duplicate of the canonical 46 v2 original (mis-filed under `backtests/`) | → use the `SQ46 v2` tick build above | dup |

### TNT OD

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| TNT OD v3 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/tnt-od/versions/TNT_OD_v3.pine) | `TNT OD v3 TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/tnt-od/tick_friendly/TNT_OD_v3_tick_friendly.pine) | 🟡 |
| TNT OD v3 june7 variant | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/imports/20260531T103840_indicator_studies/pine_v5/tnt_opening_drive_od_v3_tnt_od_v3.pine) (import snapshot) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/tnt_od_v3_tickfriendly.pine) | 🟡 |
| TNT OD v2 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/tnt-od/versions/TNT_OD_v2.pine) (`TNT_Opening_Drive_OD_v3_2026-05-04.pine` is a byte-identical dup — TV named it v3, content is v2) | `TNT OD v2 TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/tnt-od/tick_friendly/TNT_OD_v2_tick_friendly.pine) | 🟡 NEW |
| TNT OD v1 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/tnt-od/versions/TNT_OD_v1.pine) | `TNT OD TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/tnt-od/tick_friendly/TNT_OD_v1_tick_friendly.pine) | 🟡 NEW |

### VOB

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| VOB v11 FULL (HW coincidence) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/versions/VOB_v11_FULL_HWcoincidence_2026-06-04.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/tick_friendly/VOB_v11_FULL_TICKFRIENDLY_2026-06-04.pine) | 🟡 |
| VOB v11 MULTIPLES (HW coincidence) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/versions/VOB_v11_MULTIPLES_HWcoincidence_2026-06-04.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/tick_friendly/VOB_v11_MULTIPLES_TICKFRIENDLY_2026-06-04.pine) · june7 variant [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/vob_11_tickfriendly.pine) | 🟡 |
| VOB Asym T3×6 Claude v10 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/versions/VOB_Asym_T3x6_MutEx_Claude_v10_2026-05-31.pine) (import copy is byte-identical) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/vob%20v10_tickfriendly.pine) | 🟡 |
| VOB Asym T3×6 Claude v9.1 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/versions/VOB_Asym_T3x6_MutEx_Claude_v9_2026-05-12.pine) (source is `//@version=6`) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/tick_friendly/VOB_Asym_T3x6_MutEx_Claude_v9_tick_friendly.pine) (v5 flip, house precedent) | 🟡 NEW |
| VOB Asym T3×6 Claude v8 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/versions/VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine) (source is `//@version=6`) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/tick_friendly/VOB_Asym_T3x6_MutEx_Claude_v8_tick_friendly.pine) (v5 flip) | 🟡 NEW |
| VOB Ladder Watch v1 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/versions/VOB_LADDER_WATCH_v1.pine) | `VOB LDR TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/vob/tick_friendly/VOB_LADDER_WATCH_v1_tick_friendly.pine) | 🟡 NEW |

### Heavy Weapons

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| Heavy Weapons NRA v1 (`RVOL NRAFR x2`) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/heavy-weapons-nra/versions/HEAVY_WEAPONS_NRA_v1_2026-06-04.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/heavy-weapons-nra/tick_friendly/HEAVY_WEAPONS_NRA_v1_tick_friendly.pine) | 🟡 |
| Heavy Weapons NRA import variant (4FVG/4Matrix) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/imports/20260531T103840_indicator_studies/pine_v5/heavy_weapons_nra_gzi_fvg_matrix_combos_2_bodies_not_1_nrafr_shorttitle_rvol_nrafr_x2.pine) (9 lines off the versions copy) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/heavy_weapons_4fvg_4matrix_tickfriendly.pine) | 🟡 |
| Heavy Weapons ULTRA v1 (`HW ULTRA b2b1`) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/heavy-weapons-ultra/versions/HEAVY_WEAPONS_ULTRA_v1.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/heavy-weapons-ultra/tick_friendly/HEAVY_WEAPONS_ULTRA_v1_tick_friendly.pine) | 🟡 |
| Heavy Weapons Single v3 (`HW Single v3`) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/heavy-weapons-single/versions/HEAVY_WEAPONS_SINGLE_v3.pine) (import copy byte-identical) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/heavy-weapons-single/tick_friendly/HEAVY_WEAPONS_SINGLE_v3_tick_friendly.pine) · june7 variant [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/heavy%20weapons%20v3_tickfriendly.pine) | 🟡 |
| Heavy Weapons Singles v2 (saab kratos ×2, `heavy uncap oG`) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/imports/20260531T103840_indicator_studies/pine_v5/heavy_weapons_singles_v2_shorttitle_hw_singles_v2.pine) (the `_2` import file is a byte-identical dup) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/heavy_with_2x_detection_plots_tickfriendly.pine) | 🟡 |

### Heavy Combo Toggles (HCT — replaces deprecated WMD)

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| Heavy Combo Toggles v2 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v2.pine) | `HCT v2 TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/heavy-combo-toggles/tick_friendly/HEAVY_COMBO_TOGGLES_v2_tick_friendly.pine) | ⚠️ see Notes |
| Heavy Combo Toggles v1 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine) | `HCT TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/heavy-combo-toggles/tick_friendly/HEAVY_COMBO_TOGGLES_v1_tick_friendly.pine) | 🟡 NEW |

### HUB 1020 1153am

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| HUB 1020 1153am (bull, v20260604) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hub-1020-1153am/versions/HUB_1020_1153am_Hub102011a_v20260604.pine) (import copy byte-identical) | `Hub102011a` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hub-1020-1153am/tick_friendly/HUB_1020_1153am_Hub102011a_v20260604_tick_friendly.pine) · june7 variant [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/hub_2011_tickfriendly.pine) | 🟡 |
| HUB 1020 BEAR mirror (v20260613) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hub-1020-1153am/bearish/HUB_1020_1153am_BEAR_Hub1020-Bear_v20260613_bearish_mirror.pine) | **same file** — built tick-safe from day one (session `"1"` fallback + RVOL tick override are already inside) | 🟡 |

### HVD ↔ PBJ ↔ PPD family (+ PBJ, Combo Chain)

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| HVD PBJ PPD Bullish v1 (38) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hvd-pbj-ppd/versions/HVD_PBJ_PPD_BULLISH_v1.pine) | `HVD PBJ BULL TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BULLISH_v1_tick_friendly.pine) · june7 variant [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/hvd_pbj_pup_bull_tickfriendly.pine) | 🟡 |
| HVD PBJ PPD Bearish v1 (36) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hvd-pbj-ppd/versions/HVD_PBJ_PPD_BEARISH_v1.pine) | `HVD PBJ BEAR TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine) · june7 variant [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/hvd%20pbj%20ppd%20bear_tickfriendly.pine) | 🟡 |
| HVD PBJ PPD 4.26.1244am (PPD UC RVOL) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine) | `HVD PBJ PPD TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hvd-pbj-ppd/tick_friendly/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_tick_friendly.pine) | 🟡 NEW |
| COMBO CHAIN — BINARY FIX | `CC FIX` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hvd-pbj-ppd/versions/COMBO_CHAIN_BINARY_FIX_v1.pine) (**NEW** — reconstructed; only the tick build had ever been committed) | `CC FIX TICK` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hvd-pbj-ppd/tick_friendly/COMBO_CHAIN_FIXED_tick_friendly.pine) | 🟡 |
| PB & PBJ 4 Signals | `PBJ` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hvd-pbj-ppd/versions/PBJ_ONLY_4_SIGNALS_v1.pine) (**NEW** — reconstructed) | `PBJ TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/pbj_only_4_signals_tickfriendly.pine) | 🟡 |
| HVDPBJPPD_v1 | `hvd-pbj-ppd/versions/HVDPBJPPD_v1.pine` is an **audit placeholder, not loadable source** (full source recovered 2026-05-05 as the 4.26.1244am row above) | — | ❌ not loadable |

### HV NRA ladder

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| HV NRA 50-step ladder v2 (50→1000) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hv-nra/versions/HV_NRA_50step_ladder_v2_2026-06-13.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hv-nra/tick_friendly/HV_NRA_50step_ladder_v2_tick_friendly.pine) | 🟡 NEW |
| HV-to-1K NRA (100→1K predecessor) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/hv-nra/versions/HV_TO_1K_NRA_v1.pine) (**NEW** — recovered; the june7 file was an unconverted original parked in the tick folder) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/hv_to_1k_tickfriendly.pine) (no tick-hostile calls — identical logic) | 🟡 |

### ULTRA Combo

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| **ULTRA Combo v57** | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/imports/20260531T103840_indicator_studies/pine_v5/ultra_combo_v57_shorttitle_ultra_v57.pine) | `ULTRA v57 TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/ultra-combo/tick_friendly/ULTRA_COMBO_v57_tick_friendly.pine) — RE10023 + RE10140 + RE10008 all fixed; **re-paste the raw, TV cached the old one** · june7 variant [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/ultra_57_tickfriendly.pine) | 🟡 |

### One-off studies

| Study | Original (time charts) | Tick build (tick charts) | Status |
|---|---|---|---|
| Fauna Dual Mode 2.0 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/imports/20260531T103840_indicator_studies/pine_v5/fauna_dual_mode.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/fauna_dual_mode_tickfriendly.pine) | 🟡 |
| Jumbo CIA ★ 1st PUP FAUNA | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/imports/20260531T103840_indicator_studies/pine_v5/jumbo_cia_star_first_bar_only_fauna_fixedstar_shorttitle_1st_pup_fauna.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/1st%20pup%20fauna_tickfriendly.pine) | 🟡 |
| e3 f2 cluster (bull/bear 58%) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/imports/20260531T103840_indicator_studies/pine_v5/e3_f2_cluster_this_bull_bear_58_reduction_this.pine) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/june7-conversion/tick_friendly_pine/f2_e3_tickfriendly.pine) | 🟡 |
| Anish TB Foster Fix | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/anish-tb-foster/versions/ANISH_TB_FOSTER_FIX_v1.pine) (promoted from imports, byte-identical) | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/anish-tb-foster/tick_friendly/ANISH_TB_FOSTER_FIX_v1_tick_friendly.pine) | 🟡 NEW |
| Displacement 4x | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/displacement-4x/versions/DISPLACEMENT_4X_v1.pine) (promoted from imports, byte-identical) | `DISP 4x TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/displacement-4x/tick_friendly/DISPLACEMENT_4X_v1_tick_friendly.pine) | 🟡 NEW |
| NOVA VOLUME v1 | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/nova-volume/versions/NOVA_VOLUME_v1.pine) | `NOVAVOL TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/nova-volume/tick_friendly/NOVA_VOLUME_v1_tick_friendly.pine) | 🟡 NEW |
| Proximity GZI HV | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/proximity-gzi-hv/versions/PROXIMITY_GZI_HV_v1.pine) | `Prox GZ HV TF` — [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/proximity-gzi-hv/tick_friendly/PROXIMITY_GZI_HV_v1_tick_friendly.pine) | 🟡 NEW |
| BASE HVD PBJ ("DO NOT USE — BANNED BAD") | `imports/.../base_hv_d_to_pbj_to_ppd_v1_no_htf_shorttitle_base_hvd_pbj.pine` — the file itself is titled BANNED | **none on purpose** — banned studies do not get tick builds | ❌ BANNED |

---

## SET B — date-roll experimental (`dateroll/`, shorttitle ` DR`)
Same builds as the 13 keen-faraday tick entries, relabeled ` DR` so they load **beside** the
main tick builds for A/B. The 3 marked **DR-logic** answer "fired yesterday?" with day-rolled
state (works on tick, no RE10008); the other 10 are logic-identical copies.

| Study | Chart label | Status | Raw |
|---|---|---|---|
| **ULTRA Combo v57** | `ULTRA v57 TF DR` | 🟡 DR-logic + all 3 RE fixes | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/ULTRA_COMBO_v57_DR.pine) |
| **SQUARIFY 46 v2** | `SQ46 v2 DR` | 🟡 DR-logic | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/SQUARIFY_46_v2_DR.pine) |
| **SQUARIFY 46 v3.1** | `SQ46 v3.1 TF DR` | 🟡 DR-logic | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/SQUARIFY_46_v3.1_DR.pine) |
| HVD↔PBJ↔PPD Bearish | `HVD PBJ BEAR TF DR` | 🟡 copy of main tick build | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/HVD_PBJ_PPD_BEARISH_v1_DR.pine) |
| HVD↔PBJ↔PPD Bullish | `HVD PBJ BULL TF DR` | 🟡 copy | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/HVD_PBJ_PPD_BULLISH_v1_DR.pine) |
| HVD Combo Chain | `CC FIX TICK DR` | 🟡 copy | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/HVD_COMBO_CHAIN_DR.pine) |
| B2B PUP v5.4 | `B2B PUP 5.4* DR` | 🟡 copy | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/B2B_PUP_v5.4_DR.pine) |
| TNT OD v3 | `TNT OD v3 TF DR` | 🟡 copy | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/TNT_OD_v3_DR.pine) |
| VOB v11 FULL | `VOB v11 FULL DR` | 🟡 copy | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/VOB_v11_FULL_DR.pine) |
| VOB v11 MULTIPLES | `VOB v11 MULT DR` | 🟡 copy | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/VOB_v11_MULTIPLES_DR.pine) |
| Heavy Weapons NRA v1 | `RVOL NRAFR x2 DR` | 🟡 copy | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/HEAVY_WEAPONS_NRA_v1_DR.pine) |
| Heavy Weapons ULTRA v1 | `HW ULTRA b2b1 DR` | 🟡 copy | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/HEAVY_WEAPONS_ULTRA_v1_DR.pine) |
| Heavy Weapons Single v3 | `HW Single v3 DR` | 🟡 copy | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/HEAVY_WEAPONS_SINGLE_v3_DR.pine) |
| HUB 1020 1153am | `Hub102011a DR` | 🟡 copy | [raw](https://raw.githubusercontent.com/nishpa800/indicators/claude/indicator-tick-friendly-coverage-8kj0x2/dateroll/HUB_1020_1153am_v20260604_DR.pine) |

---

## Notes / known defects

- **⚠️ HCT v2 (both builds):** pre-existing defect carried verbatim from the original — the
  `alert()` blocks reference `f_HYYBull`/`f_HNBull`/`f_HNVBull`/`f_HTBull`/`f_NHx2Bull`
  (+Bear/Neutral variants) which are never declared (the real booleans are `sigHYY*` etc.).
  Expected to throw "Undeclared identifier" in the Pine editor. Needs a v2.1 decision
  (`f_*` → `sig*` rename); NOT silently fixed because that would change committed source.
- **NOVA VOLUME tick build:** the original's 7 numeric-export plots used the banned
  `display.data_window`; the tick build switches them to `display.none` (values unchanged).
  The original keeps them — expect Style-tab junk lines there.
- **VOB v8 / v9.1:** the committed originals are `//@version=6`; their tick builds flip to
  `//@version=5` (same as the existing v11 conversions). One residual: v5 evaluates `and`/`or`
  eagerly vs v6 lazy — no dependency found by audit, but the live compile is the proof.
- **Proximity GZI HV tick build:** original feeds a blank `input.timeframe` into
  `request.security` (crashes on tick). Tick build routes security through a "D" fallback and
  substitutes chart-series values on tick charts; time-chart path unchanged.
- **Byte-identical duplicate ledger:** `TNT_Opening_Drive_OD_v3_2026-05-04.pine` = `TNT_OD_v2.pine` ·
  `SQUARIFY_v2_STATS.pine` = `SQUARIFY_46_v2_2026-05-04.pine` · both `heavy_weapons_singles_v2*` imports ·
  HUB import = HUB versions · VOB v10 import = VOB v10 versions · HW Single v3 import = versions ·
  the two B2B 4.32 originals differ ONLY in line endings (LF vs CRLF).

## Errors tracked so far
| Error | What it was | Where | Status |
|---|---|---|---|
| RE10023 | blank `relativeVolume` anchor crashes `timeframe.change` on tick | suite-wide | fixed in code (anchor → `"D"` on tick) — now in EVERY tick build |
| RE10023 #2 | `time(timeframe.period, session)` crashes on tick | SQUARIFY family + HUB + u57 blocks | fixed in code (resolution → `"1"` on tick) — now in EVERY tick build |
| RE10023 #3 | `request.security` fed a blank/chart TF crashes on tick | Proximity GZI HV | fixed in code (security TF → `"D"` on tick) |
| RE10140 | >64 plot-objects (data-window matrix) | ULTRA 57 | fixed in code (matrix removed → 50) |
| RE10008 | `f_hadSignalYesterday` scanned `sig[i]` past 5000 bars | ULTRA 57 | fixed in code (date-roll `f_firedPrevDay`) |
| RE10008 (watch) | `ta.highest(volume,5000)[1]` sits at the 5000-bar boundary | ULTRA 57 + others | not changed — report if it recurs at ~5000 |
| silent tfSec death | `timeframe.in_seconds()` = 0/na on tick kills threshold tables | most RVOL studies | fixed in code (10s fallback) — now in EVERY tick build |

The gate `tools/check_plot_budget.sh` enforces ≤64 plots / no data_window / no RE10023 patterns
on every tick build. Suite-wide run 2026-07-13: **PASS** (all tick builds incl. dateroll).
