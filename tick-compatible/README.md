## tick-compatible/ — tick-chart safe forks of the indicator suite

TradingView throws `RE10023: Cannot call the 'timeframe.change' / 'time' function with a tick-based 'timeframe' argument` whenever an indicator that calls one of the following lands on a tick chart (100T, 1000T, etc):

- `time("D")` and any other `time(tf)` invocation with a time-based `tf` arg
- `tv_ta.relativeVolume(...)` — the built-in invokes `timeframe.change(tf)` internally (library line 346)

Every indicator in this folder is a 1:1 fork of the canonical version with those two call sites swapped for tick-safe equivalents:

| Original | Replacement |
| --- | --- |
| `time("D")` (inside `ta.change(...)`) | `_dayKey()` — int derived from `year * 10000 + month * 100 + dayofmonth` |
| `tv_ta.relativeVolume(L, A, C, R)` | `_rvol(L, C)` — local impl that anchors on `_dayKey()` change |
| `timeframe.in_seconds(...)` | wrapped with `nz(..., 60)` so RVOL-bucket thresholds don't degenerate to `na` |

### Mapping

Every `.pine` source in the repo is covered. Canonical versions are forked
by hand; non-canonical versions (dated backups, prior versions, backtests) are
forked by `/tmp/tick_safe_fork.py` using the same shim contract.

**Canonical forks** (per CLAUDE.md):

| Source | Tick-safe fork |
| --- | --- |
| `b2b-pup/versions/B2B_PUP_v4.32.pine` | `tick-compatible/b2b-pup/B2B_PUP_v4.32_tick.pine` |
| `tnt-od/versions/TNT_OD_v2.pine` | `tick-compatible/tnt-od/TNT_OD_v2_tick.pine` |
| `squarify/versions/SQUARIFY_v2.pine` | `tick-compatible/squarify/SQUARIFY_v2_tick.pine` |
| `hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | `tick-compatible/hvd-pbj-ppd/HVDPBJPPD_4.26_tick.pine` |
| `heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine` | `tick-compatible/heavy-combo-toggles/HEAVY_COMBO_TOGGLES_v1_tick.pine` |
| `vob/versions/VOB_Asym_T3x6_MutEx_Claude_v9_2026-05-12.pine` | `tick-compatible/vob/VOB_v9_tick.pine` |

**Non-canonical forks** (older / dated / backtest variants — included so every
script in the repo loads on tick charts):

| Source | Tick-safe fork |
| --- | --- |
| `b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine` | `tick-compatible/b2b-pup/B2B_PUP_Combined_v4.32_2026-05-04_tick.pine` |
| `squarify/backtests/SQUARIFY_v2_BT.pine` | `tick-compatible/squarify/SQUARIFY_v2_BT_tick.pine` |
| `squarify/backtests/SQUARIFY_v2_STATS.pine` | `tick-compatible/squarify/SQUARIFY_v2_STATS_tick.pine` |
| `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | `tick-compatible/squarify/SQUARIFY_46_v2_2026-05-04_tick.pine` |
| `squarify/versions/SQUARIFY_ATOMS_v1.pine` | `tick-compatible/squarify/SQUARIFY_ATOMS_v1_tick.pine` |
| `squarify/versions/SQUARIFY_v1.pine` | `tick-compatible/squarify/SQUARIFY_v1_tick.pine` |
| `tnt-od/versions/TNT_OD_v1.pine` | `tick-compatible/tnt-od/TNT_OD_v1_tick.pine` |
| `tnt-od/versions/TNT_OD_v3.pine` | `tick-compatible/tnt-od/TNT_OD_v3_tick.pine` |
| `tnt-od/versions/TNT_Opening_Drive_OD_v3_2026-05-04.pine` | `tick-compatible/tnt-od/TNT_Opening_Drive_OD_v3_2026-05-04_tick.pine` |
| `vob/versions/VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine` | `tick-compatible/vob/VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02_tick.pine` |

**No fork needed** (no `time(tf)` / `tv_ta.relativeVolume()` call sites — load
on tick charts as-is):

| Source | Reason |
| --- | --- |
| `proximity-gzi-hv/versions/PROXIMITY_GZI_HV_v1.pine` | Uses `request.security` with user-supplied `tf`; defaults to chart TF (tick-safe). |
| `vob/versions/VOB_LADDER_WATCH_v1.pine` | Only reads `time` (timestamp, not anchor) and `timeframe.period` (string). |
| `hvd-pbj-ppd/versions/HVDPBJPPD_v1.pine` | Audit stub — no executable code. |

### Behavior notes

- **Day boundary detection** (`_dayKey()`) is exact: the calendar date changes when the bar's UTC timestamp crosses midnight. Same semantic as `time("D")` on cash-session-aligned products.
- **RVOL on tick charts** is an *approximation*. The built-in `tv_ta.relativeVolume()` averages the cumulative-volume-so-far at the same minute-of-session across the past N sessions. The tick-safe `_rvol()` averages the cumulative-volume-so-far across the previous N tick bars instead, because tick bars don't align to a clock. RVOL-gated signals (Pentagon / WTC / Hiroshima / Long 1 / Short 1) will fire differently on tick charts than on minute charts — read them as directional, not literal.
- **All other detections** (PUP/PPD, HV+D, TNT/Napalm/Charge/CONT, FAUNA, Combo Sets, Foxtrot, etc.) are timestamp-independent and behave identically on tick and time charts.

### Why not just edit the originals?

Per `CLAUDE.md`, the canonical versions are reference artifacts for the verification protocol. They get audited and root-extracted as-is. The tick-safe forks are a parallel track — pull from this folder when loading a tick chart, pull from the canonical folder otherwise.
