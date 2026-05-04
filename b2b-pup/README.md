# B2B PUP Combined

**Current version:** `v4.31` → `versions/B2B_PUP_v4.31.pine`

## What it is

Aggregator Pine indicator. Bundles a lot of detection plots (S1-S20+) into one overlay with non-repainting alerts. Each plot is a back-to-back PUP/PPD-anchored confluence — i.e., "B2B PUP did fire, AND something else also fired in the same window."

## Engines inside

| Engine | What it detects | Offset |
|--------|-----------------|--------|
| A — PUP / PPD | Pocket-pivot day on % move + volume vs. recent opposite-color highs | 0 |
| B — FAUNA | Bull/Bear momentum + range + volume + trend filter (MB/RE/GG/TA + TR/ES/GDR exclusions) | 0 |
| C — Displacement | 3-bar FVG with stdev-mult body on the displacement bar | -1 |
| D — PBJ | VWMA + Supertrend + reaccel level approach + cross | 0 |
| E — RVOL + Pentagon | Threshold ladder (SAAB / 1× / GS / Pentagon / WTC / Hiroshima / Nagasaki / Kratos / MOAB) | 0 |
| F — HV+D | Highest-volume bar (50/100/200/500/1000 + ever-HV) + displacement on bar[1] | -1 |
| G — TNT / Napalm / Cont | VOB+Anish-swing+Flux confluence; Napalm scans all opposing zones; Cont uses 3-clause logic with TNT 2.0 + Return-leg | 0 |
| H — Combos / Long1 / UU | CS1 (FVG combo), CS2 (Matrix combo), CS3 (Unified = both on same bar), L1, UU streaks | mixed |

## Detection plots (S-numbered)

| S# | Name | Anchor |
|----|------|--------|
| S1  | B2B PUP                        | bar[0] |
| S2  | B2B PUP + FAUNA                | bar[0] |
| S3  | B2B PUP + DISP/HV+D            | bar[1] |
| S4  | B2B PUP + FAUNA + DISP/HV+D    | bar[1] |
| S5  | B2B PUP + SAAB-band            | bar[0] |
| S6  | Any-B2B + PBJ                  | bar[1] |
| S8  | Unified Combo + B2B PUP        | bar[1] |
| S9  | Uni Combo + B2B PUP (S19 OR S20 feed) | bar[1] |
| S10 | Long1-B2B + B2B PUP            | bar[0] |
| S11 | (FVG combo or Long1) + B2B PUP | bar[1] |
| S12 | UU/UUU/UUUU + B2B PUP          | bar[0] |
| S13 | B2B Napalm + B2B PUP           | bar[0] |
| S14 | CONT + B2B PUP                 | bar[0] |
| S15 | TNT + B2B PUP                  | bar[0] |
| S16 | Napalm + B2B PUP               | bar[1] |
| S17 | B2B HV+D + B2B PUP             | bar[1] |
| S18 | B2B HV+D-PBJ + B2B PUP         | bar[1] |
| S19 | Unified Combo ×2 (standalone)  | bar[1] |
| S20 | FVG/MAT/Uni Combo ×2 (standalone) | bar[1] |

## Reference indicator

Napalm / TNT / CONT definitions in B2B PUP must stay in sync with **TNT OD** (`../tnt-od/`). When TNT OD updates, audit this file's Engine G against it.

## Deploy

```bash
pbcopy < ~/code/anish/indicators/b2b-pup/versions/B2B_PUP_v4.31.pine
# Then: TradingView Desktop → Pine Editor → Cmd+A → Cmd+V → Cmd+S → Add to Chart
```
