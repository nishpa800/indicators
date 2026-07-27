# Heavy Weapons Single v3 — Changelog

Newest first.

---

## v3 tick-friendly — 2026-06-13
**Files:**
- `versions/HEAVY_WEAPONS_SINGLE_v3.pine` — as-received (verbatim, = the pasted v3 / repo import).
- `tick_friendly/HEAVY_WEAPONS_SINGLE_v3_tick_friendly.pine` — **load this on tick charts.**
- (DR copy: `dateroll/HEAVY_WEAPONS_SINGLE_v3_DR.pine`, shorttitle `HW Single v3 DR`.)

**Two tick-safety fixes (logic otherwise untouched; 45 plots, 0 data-window — gate PASS):**
1. **RE10023 anchor.** All 3 `tv_ta.relativeVolume(...)` calls used `reg_anchorTimeframe`
   (`input.timeframe("")` → blank = chart TF → `timeframe.change()` throws on tick bar 0). Now
   routed through `reg_anchorSafe` (`"D"` on tick, `""` on time = parity).
2. **`tfSec` guard.** `tfSec = timeframe.in_seconds(timeframe.period)` is na/0/unreliable on tick,
   which kills the per-TF RVOL threshold table. Guarded via `str.endswith(timeframe.period,"T")`
   with a 10s fallback.

**Not present (checked):** no `time(timeframe.period, …)` session calls (RE10023 #2), no bar-scan
"yesterday" loop (RE10008), plot count 45 ≤ 64. Live TradingView compile not performed here —
status is 🟡 (fixed in code, awaiting your load) in TICK_FRIENDLY_INDEX.md.
