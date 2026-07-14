# CHANGELOG — indicator suite

## 2026-07-13 — First Bar Fable Displacement 5 + Displacement 7 (new studies)

Operator order (Anish): two new studies derived from `first-bar-fable/versions/FIRST_BAR_FABLE_v2.pine`
@ `5ec5ef9` — identical except the "Displacement 9" engine default σ-multiplier:

| Study | Folder | σ default | File |
|---|---|---|---|
| First Bar Fable Displacement 5 | `first-bar-fable-displacement-5/` | **5** | `versions/FIRST_BAR_FABLE_DISPLACEMENT_5_v1.pine` |
| First Bar Fable Displacement 7 | `first-bar-fable-displacement-7/` | **7** | `versions/FIRST_BAR_FABLE_DISPLACEMENT_7_v1.pine` |

Each variant = exactly 3 diff hunks vs base (comment header · indicator() title ·
`i_d9_mult` default), machine-verified via transform manifest; gates run: no-fixed-windows
PASS, RE10023 anchor-grep clean, 57/64 outputs, Pine v5. Also backfilled
`first-bar-fable/CHANGELOG.md` v2.2 entry for commits `db8a182`/`be1fdf9`/`5ec5ef9` which
had landed without log entries. Details: each folder's CHANGELOG.md.

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
