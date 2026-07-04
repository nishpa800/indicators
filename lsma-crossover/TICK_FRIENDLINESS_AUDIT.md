# Tick-friendliness audit — LSMA Crossover (2026-07-04)

Method (same static scan as `nova-volume/TICK_FRIENDLINESS_AUDIT.md`; acceptance test = live compile
on a tick chart):

- **Risk calls:** `tv_ta` / `relativeVolume` (RE10023 on ticks), `timeframe.in_seconds()` (0/na on
  ticks → thresholds silently die), `request.security`, `timeframe.change`, session/anchor logic,
  fixed/anchored windows (`bar_index - startBar >= len`).
- **Guards needed:** a file is **tick-safe** if it has either (a) zero risk calls, or (b) every risk
  call paired with a guard.

## Source

- Original (NOT tick-friendly): `originals/LSMA_Crossover_v4_original.txt` (`//@version=4`
  `study(..., resolution="")`) — title `Least Squares Moving Average Crossover`, shorttitle
  `LSMA Crossover` (**plain, unmarked**).
- Tick-friendly build: `tick_friendly/LSMA_Crossover_v5_tick_friendly.pine` (`//@version=5`) —
  title `Least Squares Moving Average Crossover [Tick-Friendly]`, shorttitle `LSMA Crossover TF`
  (**marked in BOTH places** so it can never be confused with the original on the TradingView list).
- Calculation: `d = ta.sma(ta.linreg(src,21,0), 4)` crossing three regressions —
  `ta.linreg(src,21,0)` (LSMA) · `ta.linreg(src,200,0)` (Long) · `ta.linreg(src,1000,0)` (Extra Long).

## Scan result

| File | relVol/tv_ta | in_seconds | req.sec | tf.change / anchor | fixed windows | look-ahead | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| LSMA_Crossover_v5_tick_friendly.pine | 0 | 0 | 0 | 0 | 0 | 0 | **NO-RISK — tick-safe** |

## Findings

- **NO-RISK.** The study computes only `ta.linreg` and `ta.sma` over the price source. Both are
  **rolling** operators keyed on **bar count**, not wall-clock time, so they carry no assumption
  about how long a bar lasts and cannot collapse on a tick interval. There is nothing to guard.
- **RE10023 is not reachable.** RE10023 comes exclusively from `timeframe.change(anchor)` inside
  `TradingView/ta/7`'s `relativeVolume()`. This study never imports `tv_ta` and never calls
  `relativeVolume()`, so the crash path does not exist here (contrast the 5 RVOL files in
  `TICK_FRIENDLY_RE10023_POSTMORTEM_2026-06-04.md`).
- **`resolution=""` → omitted `timeframe`.** The one real tick-hardening: the v4 original exposed a
  "Resolution" dropdown (`resolution=""`) whose default is the chart TF but which can be overridden
  to a non-blank value, forcing an internal HTF request — the class of call that misbehaves on tick
  charts. The v5 build **omits the `timeframe` parameter entirely** (the convention every other
  tick-friendly file in this repo follows), so the study is permanently chart-native: on a tick
  chart it calculates on the N-tick bars; on a time chart, on the time bars. This also matches the
  operator directive that **LSMA must use the chart timeframe**.
- **`max_bars_back=1500`** is set so the length-1000 "Extra Long" regression always has buffer
  (`1000 < 1500`) and never trips *"references too many bars back"* on charts with a short history
  buffer. It does **not** force bars to exist — `ta.linreg(src,1000)` simply returns `na` until 1000
  bars are present, identical on tick and time charts.
- **No look-ahead.** All four plots are continuous MA lines evaluated on the current bar; no `[1]`
  offset or `barstate.isconfirmed` gate is required (there are no discrete detection signals here).
- **Distinct naming (title AND shorttitle).** The tick build is marked `[Tick-Friendly]` in the
  title and `TF` in the shorttitle; the v4 original keeps the plain unmarked names. This is
  mandatory — an unmarked tick build is indistinguishable from the original in the TradingView
  list, and loading the wrong one (tick build on a time chart, or vice-versa) silently corrupts
  downstream use. The distinction must live in BOTH the title and the shorttitle.

## Behavior in a custom tick/time candle engine

The only quantity that changes between a tick feed and a time feed is the **meaning of one bar**.
`length`, `200`, and `1000` are **bar-count** lookbacks — never durations. Feed tick bars and each
lookback spans that many tick bars; feed time bars and it spans that many time bars. The regression
math is identical either way, so the study is deterministic on both and requires no per-mode branch.
(This is the duration-normalization point: a 1000-bar Extra-Long LSMA reaches a different wall-clock
horizon per interval/liquidity, but the computation is unchanged.)

## Gates

- `check_no_fixed_windows.sh tick_friendly/LSMA_Crossover_v5_tick_friendly.pine` → **PASS** (0 hits).
- RE10023 call-site gate `grep -nE 'relativeVolume\([^,]+,\s*""'` → **0 hits** (no `relativeVolume` at all).

## Caveat / acceptance test

Static heuristic. The **authoritative** check is a live compile on a real tick chart (e.g. 100T /
1000T) via the TradingView bridge, confirming no error on bar 0 and clean regression plots. Expect
only the intentional v5→v6 deprecation notice (Pine-v5-only mandate), never a runtime error.
