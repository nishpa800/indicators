#!/bin/zsh
# Pull latest Pine source for the 5 canonical indicators from TradingView
# and save to local versioned files. Runs via Claude Code with TradingView MCP active.
#
# Usage: ask Claude to "run sync_from_tradingview.sh" or invoke from /loop
#
# This script doesn't actually call MCP — it documents the procedure. The real
# extraction is done by Claude using:
#   mcp__tradingview__pine_open(name)
#   mcp__tradingview__pine_get_source()
# The MCP saves to a tool-results file when source > 25KB; the helper Python
# block below reads that file and writes to the canonical local path.
#
# For each of the 5 indicators below, the procedure is:
#   1. pine_open with the listed name
#   2. pine_get_source — captures the tool-results filepath
#   3. Read JSON from that filepath, extract `source`, write to target path
#   4. Update CHANGELOG.md with date + version
#
# Sources of truth (last updated 2026-05-06):

cat <<'TARGETS'
1. HVD/PBJ/PPD
   TV name:   HV+D ↔ PBJ ↔ 4.26.1244am added PPD UC RVOL 1x w/HV+D and +PBJ 4
   TV ID:     USER;e522e285d4fb4113b9995465e7c48304
   Local:     hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_<DATE>.pine

2. Squarify 46 v2
   TV name:   SQUARIFY 46 v2 1
   TV ID:     USER;577c3c8fe465425ca6a20e764edd4722
   Local:     squarify/versions/SQUARIFY_46_v2_<DATE>.pine

3. B2B PUP v4.32
   TV name:   B2B PUP Combined 4.32
   TV ID:     USER;90274942c02040c08506d1cc3e312951
   Local:     b2b-pup/versions/B2B_PUP_Combined_v4.32_<DATE>.pine

4. TNT OD v3
   TV name:   TNT Opening Drive OD v3
   TV ID:     USER;b8a25ccc8142483b962c77e623bf0ac0
   Local:     tnt-od/versions/TNT_Opening_Drive_OD_v3_<DATE>.pine

5. VOB Asym T3 ×6 + MutEx Lines + Claude
   TV name:   VOB Asym T3 ×6 + MutEx Lines + Table CLAUDE CODE
   TV ID:     USER;5688210f0ebb4e1a8e3dd17bcb1a23b2
   Local:     vob/versions/VOB_Asym_T3x6_MutEx_Claude_v8_<DATE>.pine

To sync any time, ask Claude:
  "Run the indicator sync — extract all 5 latest TV versions, save versioned local copies, update CHANGELOG, commit + push."
TARGETS
