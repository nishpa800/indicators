# Proximity GZI HV — CHANGELOG

## v1 — 2026-05-09

Initial cleanup pass on the source script.

**Removed (per user request):**
- Entire Dashboard group (Show Dashboard / Location / Size inputs).
- Entire Acceleration Periods group (Period 1 / 2 / 3 inputs).
- `table.new` declaration + every `table.cell` call → eliminates the **Tables**
  checkbox under Style → Graphic Objects automatically (TradingView only shows
  Tables when the script creates one).
- `countSignalsInPeriod` helper, all `*_p1`/`*_p2`/`*_p3` and `*_total_*` vars.
- Signal-bar tracking arrays (`gzi_bull_bars`, `gzi_bear_bars`, `hv_bull_bars`,
  `hv_bear_bars`) — they only fed the dashboard.
- Signal counters (`gzi_bull_count`, `gzi_bear_count`, `hv_bull_count`,
  `hv_bear_count`) — dashboard-only.
- `tosolid` color method — dashboard-only.
- Unused `dynamic = false` constant.

**Kept (untouched logic):**
- FVG detection (auto / manual threshold, multi-TF via request.security).
- HV detection (HVE 5000 / HVY 252 / HVQ 63 highest-volume tests).
- GZI overlap logic (price overlap + bar-distance proximity, adjacent-HV rule).
- Mitigation processing (bull/bear mitigated counters retained because alerts
  reference them).
- Unmitigated horizontal lines (showLast).
- 4 plotshapes (Bull/Bear GZI, Bull/Bear HV) — all `offset=-1` per source.
- All 10 alertconditions.
