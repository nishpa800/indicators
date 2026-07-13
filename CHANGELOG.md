# CHANGELOG — indicator suite

## 2026-07-13 — TICK_FRIENDLY_INDEX now covers EVERY study (original ↔ tick pairs)

- Merged the full tick-friendly suite from `claude/keen-faraday-mzq2i2` (Set A tick builds,
  Set B date-roll, ULTRA/HW-Single/HW-Ultra dirs, `tools/check_plot_budget.sh`) with `main`'s
  HUB Bear mirror + RVOL tier ladder + HV-NRA 50-step ladder onto one branch. The HUB tick
  build now carries BOTH the interval-adaptive rolling RVOL tiers AND the tick-safe
  `time(session)` fix (auto-merge verified: 3/3 tick-safe session calls + tier ladder present).
- Rewrote `TICK_FRIENDLY_INDEX.md`: every one of the 95 non-vendor `.pine` files is on the
  page — each tick-friendly build paired with its original non-tick source (Sections 1–2),
  every original with NO tick build listed as an explicit GAP (Section 3), tick-safe-by-design
  (Section 4), banned/stubs/strategies (Section 5).
- New gate `tools/check_index_coverage.sh` — fails if any non-vendor `.pine` is missing from
  the index, so a study can never silently drop off the page again.

## 2026-05-06 — Sync from TradingView

Pulled latest source for all 5 canonical indicators directly from TradingView via MCP. Findings vs prior local copies:

| Indicator | Local file before | New file from TV | Diff |
|---|---|---|---|
| HVD/PBJ/PPD | `HVDPBJPPD_v1.pine` was 1.1KB STUB ONLY | `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` (1939 lines, 117KB) | **Recovered full source** — local was placeholder |
| Squarify v2 | `SQUARIFY_v2.pine` (May 4 09:31) | `SQUARIFY_46_v2_2026-05-04.pine` (May 4 11:29 TV mod) | 225 diff lines — minor edits since |
| B2B PUP v4.32 | `B2B_PUP_v4.32.pine` (May 4 04:50) | `B2B_PUP_Combined_v4.32_2026-05-04.pine` (May 4 08:52 TV mod) | 2520 diff lines — significant edits since |
| TNT OD | `TNT_OD_v2.pine` (May 4 06:26) | `TNT_Opening_Drive_OD_v3_2026-05-04.pine` (May 4 06:30 TV mod) | **0 diff lines** — TV name says v3 but content identical to local v2 |
| VOB Asym T3 ×6 | NO MATCHING LOCAL (only `VOB_LADDER_WATCH_v1.pine` which is a different/older indicator) | `VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine` (1473 lines, 99KB) | **Recovered missing source** — local was wrong indicator |

Also added:
- `sync_from_tradingview.sh` — documents the canonical TV IDs and procedure for pulling updates.

## Prior commits
- See `git log` for entries before this sync. Last commit before sync: `05453e7` (2026-05-04 11:17).
