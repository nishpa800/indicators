# CHANGELOG — indicator suite

## 2026-07-13 — FULL tick-friendly coverage: every study now has Original ↔ Tick build

`TICK_FRIENDLY_INDEX.md` rewritten as the complete matrix — **every** indicator study in the
repo (not just the 14 from the keen-faraday session) now has both a non-tick original and a
tick-friendly build, each linked with one-click raw URLs. Merged the keen-faraday branch
(14 tick builds, dateroll A/B set, plot-budget gate) into this branch first.

**19 new tick-friendly builds** (RE10023 anchor guard / session-time guard / tfSec 10s fallback,
per the house doctrine; zero logic changes, minimal auditable diffs):
B2B PUP 4.32 ×2 · SQUARIFY 64, 46 v2 early snapshot, ATOMS v1, HTF v1, v2 BT strategy ·
TNT OD v1, v2 · VOB v8, v9.1, Ladder Watch · HCT v1, v2 · HV NRA 50-step ladder v2 ·
HVD PBJ PPD 4.26.1244am · Nova Volume v1 · Proximity GZI HV v1 (also fixes a
request.security-on-tick crash) · Anish TB Foster Fix · Displacement 4x.

**3 reconstructed non-tick originals** (tick build was the only committed source):
`COMBO_CHAIN_BINARY_FIX_v1` · `PBJ_ONLY_4_SIGNALS_v1` · `HV_TO_1K_NRA_v1` (the june7 file
turned out to be an unconverted original parked in the tick folder).

Dedup findings recorded in the index (TNT "OD v3 2026-05-04" = v2; SQUARIFY v2_STATS = 46 v2;
the two B2B 4.32 originals differ only in line endings). Known-defect ledger added: HCT v2
alert() blocks reference undeclared `f_*` identifiers (pre-existing, carried verbatim, needs a
v2.1 decision). Suite-wide `tools/check_plot_budget.sh`: PASS.

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
