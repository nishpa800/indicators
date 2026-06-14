# CHANGELOG — indicator suite

## 2026-06-14 — Fair Value Gap: tick-friendly + non-repainting build

New `fvg/` folder (first appearance of the "Fair Value Gap (Anish)" study in the suite):
- `fvg/versions/FAIR_VALUE_GAP_v1.pine` — the V1, 2022.4.12 original, ingested verbatim.
- `fvg/tick_friendly/FAIR_VALUE_GAP_v1_tick_friendly.pine` — tick-friendly, **non-repainting** derivative.
- `fvg/CHANGELOG.md` — full detail.

Non-repaint fix: every box/line/label create, mutate and delete is gated on
`conf = barstate.isconfirmed` (v1 mutated its `var` drawing-arrays on every intrabar
tick → orphan boxes / destructive intrabar fills). History is byte-identical to v1;
only the live bar now commits at close. Tick-safety: new `i_tfSafe` coerces an empty
or tick (`"…T"`) MTF anchor to `"D"` before it reaches `request.security()`/`time()`
(no `relativeVolume`/`timeframe.change` here, so no RE10023 vector). `lookahead_on`
HTF requests kept verbatim — they are the canonical non-repaint idiom, not a leak.

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
