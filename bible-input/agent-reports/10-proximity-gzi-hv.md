# Proximity GZI HV v1 — extraction report (compact)

Source: `proximity-gzi-hv/versions/PROXIMITY_GZI_HV_v1.pine` · 253 lines · Pine v5 · title `"Proximity GZI HV"` (shorttitle `"Prox GZ HV"`)

## Verdict: ALIAS / RE-SKIN of HV FVG GZ1 OG

`diff` against `hv-fvg-gz1-og/versions/HV_FVG_GZ1_OG_v1.pine` returns **exactly one line** of difference — the `indicator()` declaration (title + shorttitle). Lines 3-253 byte-identical. Detection logic, plots, alerts, parameters all 100% identical.

CHANGELOG claim that "dashboard / acceleration / tables removed" — those layers don't exist in `HV_FVG_GZ1_OG_v1.pine` either (OG title is itself "HV FVG GZ1 OG THIS No tables"). The strip described in CHANGELOG must refer to a pre-v1 ancestor, not the OG v1 file in repo.

## Roots referenced (all cross-refs to `hv-fvg-gz1-og::*`)

| Cross-ref | Verbatim? | Plot offset |
|---|---|---|
| `hv-fvg-gz1-og::FVG_BULL_RAW` / `FVG_BEAR_RAW` | yes | not plotted; alert line 240/241 |
| `hv-fvg-gz1-og::GZI_BULL` / `GZI_BEAR` | yes | offset=-1 (lines 225-229) |
| `hv-fvg-gz1-og::HV_BULL` / `HV_BEAR` | yes | offset=-1 (lines 231-235) |

## Composites: NONE

This file defines no composites. It is a pure cross-ref consumer of OG roots.

## Plots & alerts (4 + 10 verbatim from OG)

Plotshapes: `bullGZI_trigger` (-1), `bearGZI_trigger` (-1), `bullHV_trigger` (-1), `bearHV_trigger` (-1).

Alertconditions: 'Bullish FVG', 'Bearish FVG', 'Bullish FVG Mitigation', 'Bearish FVG Mitigation', 'Bullish GZI', 'Bearish GZI', 'Any GZI', 'Bullish HV FVG', 'Bearish HV FVG', 'Any HV FVG'.

## Recommendation for Stage 6

Tag in bible as `mirror-of: hv-fvg-gz1-og::v1`. Any future edit to GZI/HV/FVG_RAW semantics in OG must be mirrored here or the alias relationship breaks. Consider deletion or symlink in Stage 6 file-system reorg.

`max_bull_fvg`/`min_bull_fvg`/`max_bear_fvg`/`min_bear_fvg` declared (lines 78-83) but never assigned or read — dead state, identical in both files. Janitorial flag.
