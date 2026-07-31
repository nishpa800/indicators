# LSMA Crossover — Changelog

Newest first.

---

## v5 tick-friendly — 2026-07-04 (current)
**File:** `tick_friendly/LSMA_Crossover_v5_tick_friendly.pine`
**Source of truth:** `originals/LSMA_Crossover_v4_original.txt` (`//@version=4`, `study(..., resolution="")`)
**Trigger:** Anish ask — "I need a tick-friendly version of this indicator study. Right now it only has
the timeframe as the 'chart' and I'm unsure the 'chart' is really accounting for the tick interval; we
are going to have both tick candles and time candles in our own system."

**Tick-safety verdict: NO-RISK** (tick-safe by construction — see `TICK_FRIENDLINESS_AUDIT.md`).
The study computes only `ta.linreg` + `ta.sma`, which are rolling **bar-count** operators. It carries
zero `tv_ta` / `relativeVolume()`, `timeframe.in_seconds()`, `request.security()`, `timeframe.change`,
session/anchor logic, fixed windows, or look-ahead — so none of the suite's RE10023 / tfSec-collapse
failure modes are reachable. Nothing to guard.

**Changes from the v4 original:**

1. **`resolution=""` dropped → chart-native (the real tick fix).** The v4 `study(..., resolution="")`
   exposes a "Resolution" dropdown that defaults to the chart TF but can be overridden to a non-blank
   value, forcing an internal higher-timeframe request — the class of call that misbehaves on tick
   charts. The v5 build **omits the `timeframe` parameter entirely** (the convention every tick-friendly
   file in this repo follows), so the study permanently calculates on the chart's own bars: tick bars on
   a tick chart, time bars on a time chart. Directly answers "is 'chart' accounting for the tick
   interval?" — yes, natively, with no separate resolution layer and no override that could inject an
   HTF request. Also matches the operator directive that LSMA must use the chart timeframe.

2. **v4 → v5 syntax** (calculation numerically identical; time-chart parity preserved):
   `study()`→`indicator()`; `linreg()`→`ta.linreg()`; `sma()`→`ta.sma()`;
   `input(...,type=input.integer)`→`input.int()`; `input(close,...)`→`input.source()`.

3. **`max_bars_back=1500` added.** Guarantees buffer for the length-1000 "Extra Long" regression
   (`1000 < 1500`) so it never trips *"references too many bars back"*. Does not force bars to exist —
   `ta.linreg(src,1000)` returns `na` until 1000 bars are present, identical on tick and time charts.

4. **Distinct naming in BOTH title and shorttitle (mandatory).** The tick build is renamed so it can
   never be confused with the original in the TradingView indicator list — loading the tick build on a
   time chart (or the original on a tick chart) silently corrupts downstream use:
   - title: `Least Squares Moving Average Crossover` → `Least Squares Moving Average Crossover [Tick-Friendly]`
   - shorttitle: `LSMA Crossover` → `LSMA Crossover TF`
   The verbatim v4 original in `originals/` keeps the PLAIN, unmarked names as the "not tick-friendly"
   reference. House convention: `[Tick-Friendly]` in the title, `TF` suffix in the shorttitle.

**Unchanged (faithful to the original):** all inputs and defaults (Length 21, Offset 0, Trigger Length
4, Source `close`); the hardcoded 200/1000 Long/Extra-Long regression lengths; all four plots
(LSMA blue, Trigger yellow, Long white, Extra Long blue), `linewidth=3`, `overlay=true`.

---

## How to read this changelog
- **Plain English recall:** "What made LSMA Crossover tick-friendly?" → dropped the `resolution=""`
  dropdown so it's always chart-native; everything else is a straight v4→v5 port. It was NO-RISK to
  begin with (no relativeVolume / no timeframe math).
- **Which one is tick-friendly?** The one whose title ends `[Tick-Friendly]` and whose shorttitle
  ends `TF`. The plain `Least Squares Moving Average Crossover` / `LSMA Crossover` (in `originals/`)
  is the untouched v4 original.
- **Source of truth:** the verbatim v4 lives in `originals/`; the deliverable lives in `tick_friendly/`.
