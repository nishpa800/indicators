# CHANGELOG — indicator suite

## 2026-07-23 — First Bar Fable v4 (new `first-bar-fable/`)

Ingested First Bar Fable v3 verbatim + shipped v4:
- **S16/S17 B2B Napalm offset FIX** (0 → -1, fb01 → fb12): raw Napalm/Charge is
  a -1 event; the b2b booleans on det bars [0],[1] are visual pair [1],[2].
- **S36/S37** PBJ + Disp9 + HV3K+/NAG (bull/bear), `i_3k_len` floor 3000.
- **S38/S39** Swing Low/High + ANY FABLE (dedicated `sw_` Yin-Yang swing engine,
  Typhoon's pivot definition, own adjustable inputs).
- **Tooltip law**: full definitions on every toggle incl. all 20 HVD rows (had
  none); no "mirror" shorthand anywhere; 2of3/3of3 PBJ requirement spelled out.
- Full adversarial offset audit: `first-bar-fable/OFFSET_AUDIT_v4.md`.

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
