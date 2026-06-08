# HV (100→1K / HEV / Hot Spot) and NAGASAKI — definitions as they stand today

Source of truth (verbatim, read 2026-06-08):
- HV: `Pine Indicators NOT transformed yet/June 7/hv to 1k_06_07_124pm.txt`
- NAGASAKI: `Pine Indicators NOT transformed yet/June 7/vob 11.txt` (lines 749–757)

## 1. HV — `HV(100/200/.../1K/HEV/HS) NRA`

### What each plot actually tests
Every tier is a **RANK-1** test on the prior **confirmed** bar:

```
isNBar  =  volume[1] == ta.highest(volume, N)[1]      // N = 100,200,...,1000
```

- It fires **only when the just-closed bar's volume equals the single highest volume across the last N bars.** It is a binary "is this THE max in the window" test — there is no notion of *how much* bigger it is.
- **HEV (all-time high):** a running max over confirmed bars:
  ```
  var float maxVolEver = 0.0
  isHEV = false
  if volume[1] > maxVolEver
      maxVolEver := volume[1]
      isHEV := true
  ```
- **Hot Spot (HS):** calendar windows 3–5 trading days before ~20 known recurring high-volume events (monthly OpEx 3rd Friday, quarter-end rebalancing, Russell reconstitution, tax-loss selling, January effect, hedge-fund 45-day redemption notices). Pure date logic, not volume.
- **Priority filter:** `HEV > 1000 > 900 > ... > 100` — only the single highest active tier paints (no stacking).
- **NRA (Non-Repainting Architecture):** all comparisons use `[1]`; plots use `offset=-1`; plot and alert share one `plot_*` boolean so they can never desync.

### The structural limitation (the gap Anish identified)
- **No magnitude.** A bar 10× the median is invisible if one larger bar exists anywhere in the last N bars. "Clearly one of the biggest of the quarter, but didn't get HEV" gets **nothing**, because RANK-1 only rewards the single max.
- **No cross-horizon percentile.** It cannot say "99.9th percentile over a year but not all-time."
- **No small-cap → large-cap normalization.** Raw share count only; as a name re-rates, the meaning of "1K-bar high" drifts.
- **Reference range:** outputs are pure booleans (0/1) per tier + the HEV/HS booleans. No numeric anomaly score is emitted.

## 2. NAGASAKI — all-time-high volume (inside VOB v11, Squarify, Jumbo CIA, etc.)

```
var float maxVolEver = 0.0
bool isNagasaki = false
if volume[1] > maxVolEver
    maxVolEver := volume[1]
    isNagasaki := true
```

- **Nagasaki ≡ HEV.** It is the *same* all-time-high-volume test (previous bar's volume exceeds all prior volume ever seen on this ticker/timeframe), just named "Nagasaki" inside the combo indicators.
- Same limitation: it is the single all-time max only. The "huge but not all-time" anomaly is exactly what it cannot see.

## 3. How NOVA VOLUME closes the gap (see `NOVA_VOLUME_v1.pine`)
- **Magnitude:** robust sigma `z = (volume - p50) / (p84 - p50)` (median + percentile spread, immune to the heavy tail) → tiers σ3/σ5/σ8/σ12, plus ratio `volume / median` → X2/X4/X8/X16.
- **Cross-horizon percentile:** `ta.percentrank` over month / quarter / year windows → MONTH/QUARTER/YEAR-EXTREME tiers that fire even when **not** all-time.
- **SLEEPER:** `year-extreme AND not all-time-high` — the precise bar HV/HEV/Nagasaki miss.
- **Small→large-cap normalization:** optional dollar-volume track (`volume × hlc3`) scored the same robust way.
- **"Does it justice":** the raw magnitude (`robust_z`, `ratio_to_median`, `pct_rank_year/quarter/month`, `dollar_vol_z`) is emitted as **numbers**, so the offline fire matrix stores *how* extreme, not just a 0/1.
- The legacy HV indicator is **left untouched** per instruction; NOVA is a separate, additive study.
