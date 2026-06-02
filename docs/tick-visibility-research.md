# Tick-Level Visibility on TradingView: Why Indicators Fail and How to Fix Them

Scope: Why Squarify (B2B), HVD+PBJ+PPD, B2B-PUP, and similarly structured indicators in this
repository do NOT render meaningfully on tick-based charts (1T / 10T / 100T / 1000T)
on TradingView, even when the "Ticks" checkbox in the Visibility tab is enabled.

This document is a research artifact — no Pine code is being changed. The intent is
forward-looking: to give us a comprehensive diagnostic framework so that when we
download our own tick-level data for every ticker (and tick-level options data), we
can guarantee parity between TradingView and our own indicator implementations.

---

## 1. Master Chart — Every Known Reason an Indicator Misbehaves at Tick Resolution

The "Ticks" visibility checkbox is necessary but not sufficient. It controls
*whether the indicator is allowed to draw* on a tick interval; it does not control
*whether the math inside the indicator is meaningful* at tick resolution. The
failure modes group into four categories.

| # | Category | Reason | Underlying Mechanism | How It Presents on a Tick Chart |
|---|---|---|---|---|
| R1 | Data model | Bars are constructed from a fixed **count of trades**, not a fixed slice of time | Each 1T/10T/100T/1000T bar closes after N transactions, regardless of elapsed seconds. `time` jumps non-uniformly between bars. | Anything that assumes "1 bar ≈ X seconds" silently becomes wrong; spacing of plots looks normal but represents non-uniform time. |
| R2 | Data model | `timeframe.in_seconds()` is ill-defined for tick intervals | A tick bar has no canonical duration; the helper either returns `na` or a placeholder. | Any branch like `if tfSec >= 60 …` collapses; gates intended for "1m and above" misfire and the indicator silently disables itself. |
| R3 | Data model | `bid` / `ask` built-ins are populated **only on 1T**; they return `na` on 10T, 100T, 1000T | TradingView only resolves quote-level data at single-tick resolution; aggregated tick bars drop the inside quote. | Spread / micro-structure overlays render on 1T but vanish at 10T+ even though the box says "Ticks" is enabled. |
| R4 | Data model | Tick data unavailable for the symbol class (indices w/o volume, options, TVC: yields, EOD-only symbols) | TradingView grays the tick intervals out entirely for these classes; even if you switch programmatically you get nothing. | This is the most relevant one for our roadmap: **options tick data is not native to TradingView**, so any options-tick parity work has to be on our side, not theirs. |
| R5 | Data model | Continuous futures expose tick data only for current + previous contract | Backfill stops at the prior contract roll. | Long historical lookbacks (50/100/500/1000 bars) on continuous futures hit a wall earlier than they would on a 1-minute chart. |
| R6 | Time-based math | `session.isfirstbar`, `session.isfirstbar_regular`, anchored VWAP, daily/RTH resets fire on a *bar* boundary, not a *clock* boundary | A tick bar can straddle the open/close edge for a moment, or fall inside a single second that includes a session boundary. | Daily VWAP / opening-range / "session high" anchors drift by a tick's worth of trades; HVD/PBJ/PPD's `isFirstBar` resets land in slightly wrong places. |
| R7 | Time-based math | `request.security(syminfo.tickerid, "D", …)` from a tick chart requests an HTF that is many orders of magnitude larger than chart resolution | Each tick bar repeatedly requests the same daily/4H value; the data alignment uses the lookahead model designed for time bars. | HTF overlays appear flat for long stretches and then jump; "VWAP from 1H" looks staircased; some calls return `na` until the first historical sync. |
| R8 | Time-based math | Rolling windows like `ta.highest(volume, 500)` are denominated in **bars**, not minutes | On a 5-minute chart, 500 bars ≈ 41 hours. On a 100T chart of a thin name, 500 bars can be 8 hours; on a liquid name, 12 minutes. | "Highest volume in 250 bars" — Squarify's core test — fires either constantly or never, depending on the symbol's tick rate. The threshold is no longer comparable across instruments or time-of-day. |
| R9 | Volume semantics | `volume` on a tick bar is the sum of the N ticks' sizes, not a time-window aggregate | Volume per bar is mechanically a function of trade-size distribution, not market intensity. | Volume-percentile tests degenerate: on 1T every bar's "volume" equals its trade size, so HVD's `volume == ta.highest(volume, 500)` reduces to "is this the biggest single trade in the last 500 trades?" — a very different question. |
| R10 | Volume semantics | Relative-volume (RVOL) baselines like `ta.sma(volume, 20)` assume time-equivalent comparison | The 20-bar SMA of volume on a 5-minute chart is "average 5 minutes of volume"; on a 100T chart it's "average 100-trade chunk", which is a constant if size distribution is stationary. | RVOL collapses toward 1.0 across most bars and spikes only on size-outlier trades; the "1.8x AvgVol" gate in B2B-PUP rarely qualifies the way it does on 5m. |
| R11 | Volatility semantics | `ta.atr(14)`, body-size vs ATR ratios assume the bar's range is a sample of *recent volatility per unit time* | On tick bars, range is a sample of *price travel per N trades*. Two adjacent 100T bars can have nearly identical ranges even when underlying volatility doubled, because the bar count auto-throttles. | B2B's "body > 1.6 × ATR14" and "range > 2.2 × ATR" gates fire on inappropriate price moves; squeezes look like expansions and vice-versa. |
| R12 | Execution model | Real-time tick bars update on **every incoming trade**; historical tick bars are pre-grouped | Same bar can be re-evaluated many times in real time before it closes, and `barstate.isconfirmed` is the only reliable gate. | Indicators that latch state on `barstate.islast` or that draw labels mid-bar flicker, redraw, and look noisy; B2B's `conf`-gated triggers may fire and un-fire repeatedly. |
| R13 | Execution model | Pine has script-execution-time limits (20s basic / 40s paid) per full historical pass | A 25k-bar Expert plan loaded as 1T = 25k ticks, but as 1000T = 25k × ~1000 trades evaluated upstream. Complex indicators can exceed the budget. | Indicator silently fails to load, or partially loads and stops; the chart shows the script title with no plots. |
| R14 | Execution model | `max_bars_back` defaults to ~300 but Squarify/HVD ask for `ta.highest(volume, 1000)` on bar 1 | Pine has to satisfy the largest backward reference in any series. On dense tick charts this works; on thin symbols where 1000 ticks don't exist yet, the series is `na`. | Plots are blank for the entire visible range on illiquid tickers / pre-market / new listings. |
| R15 | Platform | Bar Replay, deep-backtest, and server-side alerts don't work on tick intervals | TradingView platform restriction. | We cannot validate or alert on tick-chart logic the same way we do on time bars — testing parity must move off-platform. |
| R16 | Platform | Tick intervals don't exist on mobile and aren't available for non-Expert/Elite/Ultimate plans | Subscription / surface gating. | An indicator that "works on tick" on desktop is not a portable deliverable; field testing requires the same plan. |
| R17 | Platform | Public ideas, Renko/Kagi/Line-break/PnF chart styles, and embedded broker charts strip tick support | Out-of-scope for ideas and alt chart types. | Anything we publish or embed loses tick fidelity even if the source indicator is tick-aware. |
| R18 | Plot rendering | Extreme y-axis values from a single mis-scaled tick can push the auto-scale off-screen | Tick bars can include outlier prints (off-book, late, error trades); one bad print and the whole pane's autoscale blows out. | "The indicator isn't showing" — actually it is, but the visible range was pushed thousands of pixels away by one tick. |
| R19 | Plot rendering | Object-tree visibility, status-line toggles, eye-icon off, and template state corruption | Standard TradingView display gotchas, orthogonal to tick logic. | Same as on any chart, but easier to misattribute to the tick switch when both happen at once. |
| R20 | Plot rendering | `max_bars_back`, `max_lines_count`, `max_labels_count`, `max_boxes_count` limits hit faster on dense tick charts | Liquid names produce 1000T bars every few seconds — boxes/labels per-bar pile up. | Drawings stop appearing past a certain point in history; oldest labels disappear silently as new ones push them out. |

---

## 2. Three Qualitative Supporting Rationale

These are the conceptual arguments for *why* the failures above happen — they
hold regardless of which symbol or timeframe we test.

**Q1. Tick bars break the implicit "bar = time" contract that every legacy indicator embeds.**
Every classical TA primitive — RSI, ATR, SMA-of-volume, Bollinger bands,
"highest in N bars" — was authored on the assumption that the x-axis is uniform
time. A "20-period" lookback is a stand-in for "the last hour" or "the last
day". On a tick chart this contract is silently violated: 20 bars on AAPL at
the open might be 4 seconds; 20 bars on AAPL at lunch might be 4 minutes. The
indicator's threshold is no longer interpretable, even though the code runs
without error. Squarify, HVD, PBJ, PPD, and B2B-PUP all encode multiple
hard-coded lookback constants (50, 75, 100, 150, 200, 250, 300, 500, 1000)
that were calibrated against time bars. The visibility checkbox lets them draw;
it cannot rescale their meaning.

**Q2. Tick aggregation discards the very micro-structure information that a tick chart purports to expose.**
The reason a trader switches to a tick chart is to see flow — the cadence of
trades, the size of prints, the bid/ask context. But once you aggregate to 10T
or 100T, TradingView throws away the bid/ask side, throws away
trade-by-trade timestamps, and presents you with an OHLCV bar that looks
identical in shape to a 1-minute bar. The volume number you see is a
trade-size sum, not a participation measure. Indicators built on the
assumption that `volume` is a proxy for *crowd participation* (which is true
on time bars, where many traders contribute to one candle) are now reading
*size of recent trades*, which can be dominated by a single block. The
indicator hasn't changed; the noun underneath one of its variables has.

**Q3. Tick charts are a hybrid of historical aggregation and real-time tick streaming, and Pine's execution model handles those two regimes asymmetrically.**
A historical 100T bar was assembled server-side from already-recorded trades
and is delivered as a complete OHLCV row. A real-time 100T bar is being
assembled trade-by-trade in your browser and is re-evaluated on every print.
Indicators that depend on `barstate.isconfirmed`, on `[1]` references, or on
session-anchored state behave one way during the historical pass and another
way live. The visual result is plots that "look right" on the historical
section and then start flickering, repainting, or going blank as you approach
the live edge. This is not a bug in the indicator — it is the indicator
sampling two different data-generating processes.

---

## 3. Three Quantitative Supporting Rationale

These are the numbers / measurable thresholds we can point to.

**N1. Effective lookback window collapses by 1–3 orders of magnitude.**
A 250-bar volume lookback on a 5-minute chart of a liquid name spans roughly
250 × 5 = 1,250 minutes ≈ 20.8 hours of trading (≈3 RTH days).
The same 250-bar lookback on a 100T chart of AAPL at midday — where AAPL
prints roughly 5–10 trades per second — spans 250 × 100 / 7.5 ≈ 3,333
seconds ≈ 55 minutes. At the open, the same 250 bars cover under
10 minutes. Squarify's `ta.highest(volume, 250)` therefore tests against a
window that varies from ~10 minutes (open) to ~3 hours (afterhours) on a
single symbol, on a single day. The "this is the highest in 250 bars" gate
is no longer a stable condition.

**N2. Volume distribution per bar is non-stationary by construction.**
On a 100T bar, the bar's `volume` equals the sum of 100 trade sizes. The
expected value of that sum is 100 × E[size]. On AAPL E[size] is roughly
50–200 shares for retail flow, but a single block print of 50,000 shares
inside the same 100-tick window makes `volume` ≈ 60,000 — a 300× outlier.
On a 5-minute time bar, that same block is one of perhaps 5,000 prints, and
contributes ~30% to the bar's total volume. On a tick bar, it dominates 100%.
This is why `ta.sma(volume, 20)` on tick is dominated by a tiny number of
prints and why RVOL multipliers like "1.8 × AvgVol" rarely qualify the way
they do on time bars: the SMA is being dragged around by the same kind of
outlier the rule is trying to detect.

**N3. Pine resource budget per chart is fixed, but tick charts increase the per-bar real-time evaluation rate.**
TradingView budgets ~20 seconds (basic) / 40 seconds (Pro+) for a single
historical pass and ~500ms for any one loop. Real-time, each new trade can
trigger a full top-down re-execution of the script. On a 1T chart of a stock
printing 10 trades/second, the script is being re-evaluated 600 times per
minute; on a 1-minute chart it is re-evaluated 60 times per *hour* (once per
new bar plus updates). Heavy indicators like HVD+PBJ+PPD that pre-compute
17 different volume rankings, a session-anchored max, and an RVOL panel are
performing roughly the same arithmetic 600× faster — and the per-pass time
budget is unchanged. Indicators that "work on 5m" can hit the cap on 1T.

---

## 4. Three Ways to Overcome the Problem

These are architectural — they do not require us to rewrite any one
indicator before we use it, but they define the engineering standard we
should apply when porting or authoring tick-compatible indicators.

**M1. Re-denominate every lookback from "bars" to "intent units" and resolve the unit at runtime.**
Wherever an indicator currently says `ta.highest(volume, 250)`, it really
means one of: (a) "highest in the last N minutes", (b) "highest in the last
N trades", or (c) "highest since session open". We pick one, and then we
*compute* the right `len` argument from `timeframe.period`,
`timeframe.in_seconds()`, `timeframe.isticks`, the chart's tick multiplier,
and an estimate of trades-per-second for the symbol. Concretely: an indicator
parameter exposed as `lookback_minutes` is translated to `lookback_minutes
* 60 / tfSec` on time charts, and to `lookback_minutes * E[trades/sec] /
tickMultiplier` on tick charts. The indicator's *intent* is now stable
across timeframes; only the bar-count is variable. This is what gives us
parity between our own tick data and TradingView.

**M2. Branch the indicator's data plane on `timeframe.isticks` and substitute volume / volatility primitives that are scale-invariant.**
Inside any indicator that runs on both time and tick bars, we define a small
abstraction layer:

- `vol_intensity()` — on time bars returns `volume / tfSec` (volume per
  second); on tick bars returns `volume * tradesPerSecond / N` (size flow
  rate). Both numbers are in shares-per-second.
- `range_volatility()` — on time bars returns `ta.atr(14)`; on tick bars
  returns a price-travel-per-second analog, computed from
  `(high − low) × tradesPerSecond / N`.
- `session_anchor()` — wraps `session.isfirstbar` on time bars and uses
  `change(dayofweek)` or a UTC-time delta on tick bars to avoid the
  drift described in R6.

The body of the indicator (Squarify's "volume rank + displacement"; HVD's
"volume rank + range + FVG") never refers to raw `volume` or raw `atr` again.
This is the lowest-friction structural change we can make and it is the
one that buys parity.

**M3. Build a diagnostic harness off-platform that replays the same logic against our own tick feed, and gate every indicator on a parity score before we trust it on a tick chart.**
TradingView's own platform forbids us from validating tick logic via Bar
Replay or deep-backtest (R15). So the validation has to happen against our
own data. The harness: for each indicator we want to certify, dump the
signal series from TradingView (export-as-CSV from the data window) on a
known historical day at 5m, 1m, 100T, and 1T; recompute the same indicator
locally against our tick database; produce a parity report that scores
(a) signal count delta, (b) timestamp drift in seconds, and (c) value
RMSE. An indicator scores ≥0.95 parity across the four timeframes before
it earns a "tick-safe" label. This becomes the gate before we ship any
indicator that is meant to consume our future tick-level dataset.

---

## 5. Application to the Specific Indicators in This Repo

| Indicator | Files | Why It Will Fail on Tick | Worst-Case Failure |
|---|---|---|---|
| Squarify (B2B) | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | Uses `ta.highest(volume, N)` for N ∈ {50…1000} (R8, N1), `ta.sma(volume, 20)` (R10, N2), body-vs-ATR ratios (R11), `timeframe.in_seconds(timeframe.period)` as a gating constant (R2). | Volume-rank gates fire constantly on liquid names at the open and never on illiquid names — exact opposite of intent. |
| HVD + PBJ + PPD | `hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | Same volume-rank dependency at 17 different lookback lengths (R8, R9), `session.isfirstbar` for resets (R6), RVOL panel built on `ta.sma(volume, …)` (R10), `tfSec` gate (R2). | "First bar of session" anchor drifts; HV+D detector fires on single block prints rather than on participation; PPD/PBJ thresholds become non-comparable across symbols. |
| B2B-PUP | `b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine` | Five-length volume rank (50/100/200/500/1000), `session.isfirstbar`, ATR-normalized body and range gates, `tfSec`. | Same as above. PUP/PPD "high red/green vol" anchors swing wildly depending on whether a block lands inside the 1000-tick window. |

---

## 6. Forward Diagnostic Checklist (Use Before Certifying Any Indicator as Tick-Safe)

1. Does it call `timeframe.in_seconds()` and branch on the result? → R2.
2. Does it use `ta.highest(volume, N)`, `ta.lowest`, `ta.sma(volume, N)`, or any rolling window where N is a bar count? → R8, R10, N1, N2.
3. Does it use `ta.atr`, body-vs-ATR, range-vs-ATR, or anything calibrated to per-bar volatility? → R11.
4. Does it use `session.isfirstbar`, `session.isfirstbar_regular`, or anchor anything to "first bar of session"? → R6.
5. Does it call `request.security(..., "D", ...)` or any HTF other than ≥ the chart? → R7.
6. Does it depend on `bid` / `ask`? → If yes, it works *only* on 1T (R3).
7. Does it expect Bar Replay / deep backtest / server-side alerts? → R15.
8. Does it draw labels/boxes per-bar without capping `max_labels_count`? → R20.
9. Does it touch options, indices without volume, TVC: yields, or continuous futures? → R4, R5.
10. Does it latch state on `barstate.islast` vs `barstate.isconfirmed`? → R12.

If any of 1–5 is true, the indicator needs the M1+M2 retrofit before it
should be trusted at tick resolution — regardless of whether the Visibility
"Ticks" checkbox is enabled.

---

## Sources

- TradingView, "What are tick-based intervals" — https://www.tradingview.com/support/solutions/43000709225-what-are-tick-based-intervals/
- TradingView Pine Script docs, "Concepts / Timeframes" — https://www.tradingview.com/pine-script-docs/concepts/timeframes/
- TradingView Pine Script docs, "Writing / Limitations" — https://www.tradingview.com/pine-script-docs/writing/limitations/
- TradingView Pine Script docs, "Concepts / Other timeframes and data" — https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/
- TradingView Blog, "Expanded tick chart support" — https://www.tradingview.com/blog/en/expanded-tick-chart-support-52342/
- TradersPost, "Pine Script bid-ask spread monitor for tick charts" — https://blog.traderspost.io/article/pine-script-bid-ask-variables
- Pineify, "What are ticks in TradingView" — https://pineify.app/resources/blog/what-are-ticks-in-tradingview-a-comprehensive-guide
- Pineify, "Indicators not showing on TradingView" — https://pineify.app/resources/blog/indicators-not-showing-on-tradingview-causes-fixes-and-pro-tips
