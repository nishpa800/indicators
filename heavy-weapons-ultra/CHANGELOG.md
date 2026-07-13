# Heavy Weapons ULTRA — Changelog

Newest first.

---

## v1 tick-friendly — 2026-06-12
**Files:**
- `versions/HEAVY_WEAPONS_ULTRA_v1.pine` — as-received original (verbatim).
- `tick_friendly/HEAVY_WEAPONS_ULTRA_v1_tick_friendly.pine` — **load this on tick charts.**

**Trigger:** the as-received build carries the same two tick landmines that crash the
suite's other studies with RE10023 on bar 0 of a tick chart.

**Two tick-safety fixes (logic otherwise untouched — verified parity: 28 plots, 1
alert, 3 RVOL calls, 0 `label.new` in both files):**

1. **RE10023 anchor.** All 3 `tv_ta.relativeVolume(...)` calls passed
   `reg_anchorTimeframe`, an `input.timeframe("")` that defaults to blank = chart TF.
   On a tick chart that is tick-based and the library's internal `timeframe.change()`
   throws on bar 0. The calls now route through `reg_anchorSafe`:

   ```pine
   string reg_anchorSafe = ((reg_anchorTimeframe == "" and (str.endswith(timeframe.period, "T") or na(timeframe.in_seconds(timeframe.period)) or timeframe.in_seconds(timeframe.period) <= 0)) or str.endswith(reg_anchorTimeframe, "T")) ? "D" : reg_anchorTimeframe
   ```

   On time charts a blank anchor stays `""` (chart-TF rel-vol parity preserved); on
   tick charts it becomes `"D"`. An explicitly tick anchor is also coerced to `"D"`.

2. **`chartSec` guard.** `int chartSec = timeframe.in_seconds(timeframe.period)` is
   na/0/unreliable on tick, which silently kills every RVOL threshold (`na -> false`)
   and the `isSubMinute` / `isSub2Min` gates. Guarded with a tick fallback:

   ```pine
   int  TICK_FALLBACK_SEC = input.int(10, "Tick fallback seconds (sub-minute bucket)", minval=1, group=grp_tf)
   bool isTickChart       = str.endswith(timeframe.period, "T") or na(timeframe.in_seconds(timeframe.period)) or timeframe.in_seconds(timeframe.period) <= 0
   int  chartSec          = isTickChart ? TICK_FALLBACK_SEC : timeframe.in_seconds(timeframe.period)
   ```

   On tick the chart reads as sub-minute (10s bucket) so thresholds resolve to the
   most-sensitive tier and HTF profiles auto-disable (intended).

**Tick detection** keys off `str.endswith(timeframe.period, "T")` — the authoritative
signal per the suite postmortem (`timeframe.in_seconds("1000T")` can return a positive
number, so the na/`<=0` test alone is not enough).

**Verification:**
- Strict call-site gate (comments excluded) returns nothing:
  `grep -nE 'relativeVolume\([^,]+,\s*""' <file> | grep -vE '^[0-9]+:\s*//'` → empty.
- `reg_anchorTimeframe` survives only in its input def + the `reg_anchorSafe` def —
  never at a call site.
- No unguarded `timeframe.in_seconds` downstream; all usage flows through `chartSec`.
- Indicator title/shorttitle left unchanged → drop-in replacement (no alert-routing
  or layout disruption). Live TradingView compile not performed in this environment.
