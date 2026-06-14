# HUB_1020_1153am — BEARISH STRUCTURAL MIRROR — Manifest

**Label:** `Pine is a Pine Editor bearish mirror`
**Built:** 2026-06-13
**Builder:** deterministic transformer `build_bear_mirror.py` (reproducible; re-runnable)

## Lineage / source of truth

| | path | md5 |
|---|---|---|
| BULL source (tick-friendly, **canonical**) | `../tick_friendly/HUB_1020_1153am_Hub102011a_v20260604_tick_friendly.pine` | `360c9e1a74ac0eb11f71fcab7b4e0d04` |
| BEAR mirror (this artifact) | `./HUB_1020_1153am_BEAR_Hub1020-Bear_v20260613_bearish_mirror.pine` | `8ad1e0b1b37551d40318f72141007ddd` |

**Adopt-newer event:** the source Anish pasted was **newer** than the committed
tick-friendly file — it carried the RE10023 session guard
`time((str.endswith(timeframe.period, "T") ? "1" : timeframe.period), …)` on the 3
`isWithinSession` calls (fc_s3 / e3 / ftmb); the committed copy still had bare
`time(timeframe.period, …)`. Per the bullish→bearish skill, the newer paste was
adopted into the repo bull **first** (3 session calls guarded), then mirrored. The
guard is an INVARIANT and is preserved verbatim in the bear.

## Inputs → Processing → Outputs

```
Inputs : canonical BULL Pine v5 (Signal Hub: 25 detection plots + 10 composites
         + Mango Swings + PB&J + global alert multiplexer)
Processing: classify every construct FLIP (directional) vs INVARIANT
         (magnitude/temporal/count) -> apply 70 surgical anchored ops, each
         count-asserted -> scoped visual reflection on detection-plot lines only
Outputs: BEAR Pine v5 mirror (new study, bullish original byte-preserved) +
         this manifest + the transformer + structural verification proof
```

## FLIP decision log (directional constructs — reflected about the price axis)

| # | bull construct | bear mirror | sites |
|---|---|---|---|
| 1 | `X_body_up = X_body > 0` | `X_body_down = X_body < 0` | 8 defs / 27 refs |
| 2 | RE close-near-high `(high - close) < ε·range` | close-near-low `(close - low) < ε·range` | 6 |
| 3 | `up_trend = TrendMA > TrendMA[1]` | `down_trend = TrendMA < TrendMA[1]` | 5 defs / 10 refs |
| 4 | TA price-rose `(close - close[1]) > θ·AvgΔ` | price-fell `(close[1] - close) > θ·AvgΔ` | 5 |
| 5 | RVOL base gate `close > open` | `close < open` | 5 |
| 6 | `*_MB_bull/_RE_bull/_TA_bull` | `*_MB_bear/_RE_bear/_TA_bear` | 39 |
| 7 | `baseBull` | `baseBear` | 12 |
| 8 | seq/zone anchor `seqStartLow := low` (up-move origin) | `seqStartHigh := high` (down-move origin) — OW ote, OW super, OoOC | 15 |
| 9 | OoOC meta lookahead extreme `high[lookahead]` + anchor low | `low[lookahead]` + anchor high | 4 |
| 10 | Mango export `sSwingBottom = ms_swing_bottom_event` | `sSwingTop = ms_swing_top_event` | engine already computes both |
| 11 | PB&J `ta.crossover(ohlc4, line)` | `ta.crossunder(ohlc4, line)` | 1 |
| 12 | PB&J `low == ta.lowest(low,25)` | `high == ta.highest(high,25)` | 1 |
| 13 | PB&J `low < ma·(1 - thr)` | `high > ma·(1 + thr)` | 1 |
| 14 | semantics: RVOL `U>Th`→`D>Th`, `Bullish`→`Bearish`, `Swing Bottom`→`Swing Top`, `Follow-up Buy`→`Follow-up Sell`, buy→sell ids | display + ids | — |
| 15 | detection-plot visuals: up-shapes→down (triangleup→triangledown), bull colors (white/lime/green/teal/aqua)→red/maroon | scoped to `plotshape`/`plotchar` lines | 26 lines |

## INVARIANTS preserved (verified EQUAL bull vs bear, code-only)

`volume`=51 · `ta.atr`=10 · `ta.sma`=35 · `ta.ema`=3 · `ta.vwma`=1 ·
`math.abs`=18 · `timeframe.period`=6 · `str.endswith` tick guard=3 ·
`input.*`=540 · `ta.pivothigh`=1 · `ta.pivotlow`=1 · all lengths/periods/thresholds/
sessions/padding multipliers unchanged. RVOL `spike = math.abs(close - open)` (unsigned)
unchanged. Overlap/cluster geometry (`loA<=hiB and loB<=hiA`, BFS, bounding-box
`math.max/min`) is symmetric → unchanged; only the hi/lo **slot feeds** flip.

## One intentional non-pure-reflection (flagged, not hidden)

The tick-friendly bull still contained ONE surviving `label.new` graphic object for
the Swing Bottom export (line 1015). Anish's standing product rule is **NO
`label.new` graphic objects — use detection plots**. So the bear replaces that one
label with a machine-readable `plotshape` swing-top detection plot
(`location.abovebar, shape.labeldown, red, text="ST"`). The 14 remaining Mango
`label.new` are debug visuals gated behind `ms_showInternalPlots` (default OFF), part
of the symmetric structure-labeling engine, and are left byte-identical to the bull.

## Verification (all green — byte-level, on the real files)

- v5 enforced (`^//@version=5` ×1), zero v6.
- ZERO leftover bull-directional tokens (`_body_up`, `_up_trend`, `_MB_bull`,
  `baseBull`, `seqStartLow`, `close > open`, `(high - close) <`, `(close - close[1]) >`,
  `sSwingBottom_raw`, `sPBJFollowupBuy_raw`, `pbj_lander_buy_signal`, `ta.crossover`,
  `ta.lowest`, `_bullish`).
- bear tokens present (`_body_down`, `baseBear`, `seqStartHigh`, `close < open`,
  `(close - low) <`, `(close[1] - close) >`, `sSwingTop_raw`, `sPBJFollowupSell_raw`,
  `ta.crossunder`, `ta.highest(high, 25)`).
- every invariant count EQUAL bull vs bear (list above).
- Mango debug engine byte-identical (HH label unchanged: green/style_label_down).
- bracket fingerprint identical to the compiling bull: `( delta=-3`, `[ delta=0`.
- bullish original untouched except the sanctioned adopt-newer session-guard fix.

## Routing

Verified Pine v5 bearish mirror → ready for the three-output conversion skills
(`pine-editor-to-pine-tick-friendly` already satisfied; next:
`pine-editor-to-python-tick-based`, `pine-editor-to-python-time-based`).

## Follow-ups (not done — out of scope this turn)

- Base `versions/` (time-chart) file does not yet carry the session guard; it is a
  no-op there (str.endswith=false on time charts), so behavior is unchanged. Add for
  consistency if desired.
- Live TV compile not run: loading 1781 lines via `pine_set_source` requires
  reproducing the file verbatim in a tool param, which would test the reproduction
  rather than the on-disk bytes; the byte-level structural+syntax gate is the
  stronger proof for this type-preserving transform. Paste the file into the Pine
  editor to confirm in-app if desired.
