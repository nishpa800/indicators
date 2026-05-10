# HV FVG GZ1 OG — extraction report

Source: `hv-fvg-gz1-og/versions/HV_FVG_GZ1_OG_v1.pine` · 253 lines · Pine v5 · title `"HV FVG GZ1 OG THIS No tables"` (shorttitle `"HV FVG GZ1 OG"`)

## Summary

Single-pass overlay. Detects raw bullish/bearish FVGs from a 3-bar gap pattern, tags each FVG with milestone-volume (HV) flag from 5000/252/63-bar volume highs, stores them in an array of `fvg` UDT records, and emits two derived signals on new-FVG creation: HV (formation-volume) and GZI (same-polarity overlap with a prior FVG within `gziProximity` bars, with adjacent-touch allowance when both are HV). Boxes extend `n+480` bars; mitigation removes boxes when `close` breaches the FVG.

Counts: 4 plotshapes (all `offset=-1`), 10 alertconditions, 1 UDT (`fvg`).

## Roots (6, all defined-here)

| Canonical | Source line | Plotted | Plain-English |
|---|---|---|---|
| `hv-fvg-gz1-og::FVG_BULL_RAW` | 70 (raw); 73 (HTF via `request.security`) | no — drives `box.new` only; alert `'Bullish FVG'` line 240 | Bar 0 low > bar 2 high, bar 1 close > bar 2 high, gap-size/bar2.high > threshold |
| `hv-fvg-gz1-og::FVG_BEAR_RAW` | 71 (raw); 73 (HTF) | no; alert `'Bearish FVG'` line 241 | Bar 0 high < bar 2 low, bar 1 close < bar 2 low, gap-size/bar0.high > threshold |
| `hv-fvg-gz1-og::HV_BULL` | 53-63 (`isFormationHV`); 132-134; plot 231-232 | yes, **`offset=-1`**, `location.belowbar`, `shape.flag` | Fires on creation of a new bullish FVG whose formation-bar volume = `ta.highest(volume[1], 5000/252/63)` |
| `hv-fvg-gz1-og::HV_BEAR` | 53-63; 172-174; plot 234-235 | yes, **`offset=-1`**, `location.belowbar`, `shape.flag` | Fires on creation of a new bearish FVG whose formation-bar volume = highest of 5000/252/63 |
| `hv-fvg-gz1-og::GZI_BULL` | 108-130; plot 225-226 | yes, **`offset=-1`**, `location.top`, `shape.flag` | Fires on creation of a new bullish FVG that price-overlaps a prior bullish FVG within `gziProximity` bars; adjacent-touch counts when both are HV |
| `hv-fvg-gz1-og::GZI_BEAR` | 150-170; plot 228-229 | yes, **`offset=-1`**, `location.top`, `shape.flag` | Symmetric bear |

Parameters: `thresholdPer=1.0`, `auto=true` (auto threshold = cumulative `((high-low)/low)/bar_index`), `tf=""`, `showHV=true`, `showGZI=true`, `gziProximity=6` (min 1, max 200). HV lookbacks `HVE=5000`, `HVY=252`, `HVQ=63` are hardcoded (no input) — parameters of HV, NOT separate roots.

## Composites

None at source level. Trigger flags `bullGZI_trigger`, `bearGZI_trigger`, `bullHV_trigger`, `bearHV_trigger` ARE the canonical roots GZI_BULL/BEAR and HV_BULL/BEAR — they don't compose other named roots. The `'Any GZI'` and `'Any HV FVG'` alerts (lines 247, 251) are inline OR expressions, not named composite variables.

## Cross-indicator references

None. This file is canonical / OG.

## Plots & alerts

**Plotshapes (4)** — all `offset=-1`:
- L225-226 `bullGZI_trigger` "Bullish GZI" flag/top/`gziBullCss`
- L228-229 `bearGZI_trigger` "Bearish GZI" flag/top/`gziBearCss`
- L231-232 `bullHV_trigger` "Bullish HV" flag/belowbar/`hvBullCss`
- L234-235 `bearHV_trigger` "Bearish HV" flag/belowbar/`hvBearCss`

**Alertconditions (10)**:
- L240 'Bullish FVG' (`bull_count > bull_count[1]`)
- L241 'Bearish FVG' (`bear_count > bear_count[1]`)
- L242 'Bullish FVG Mitigation' (`bull_mitigated > bull_mitigated[1]`)
- L243 'Bearish FVG Mitigation' (`bear_mitigated > bear_mitigated[1]`)
- L245 'Bullish GZI' (`bullGZI_trigger`)
- L246 'Bearish GZI' (`bearGZI_trigger`)
- L247 'Any GZI' (`bullGZI_trigger or bearGZI_trigger`)
- L249 'Bullish HV FVG' (`bullHV_trigger`)
- L250 'Bearish HV FVG' (`bearHV_trigger`)
- L251 'Any HV FVG' (`bullHV_trigger or bearHV_trigger`)

## Caveats

- HV roots fire only on bar of FVG creation, not on every milestone-volume bar.
- HV lookbacks 5000/252/63 are parameter-locked at runtime (no inputs).
- Adjacent-HV rule: when both FVGs are HV, `overlap_bottom <= overlap_top` qualifies; otherwise strict `<`.
- Cross-polarity GZI is impossible by design (same-polarity branch enforced separately for bull/bear).
- `lastTime` deduplication suppresses simultaneous bull+bear creation for same `fvg_time`.
- Box right-edge offset `extend=480`.
