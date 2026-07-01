# Heavy Weapons ULTRA — COMPLETE GATE REFERENCE

Every detection **spot** (visual plot) and every **alert** line, with its **full underlying gate**.
All gates require `conf = barstate.isconfirmed` (bar closed → non-repainting). `[1]` = previous bar.

---

## 0. THRESHOLDS (depend on chart timeframe; examples below)

| TF | `th_1x` | `th_saab_kratos`=0.56×1x | `th_gs_moab`=`th_hiroshima` | `th_wtc`=2×1x |
|--|--|--|--|--|
| 1 min | 20.0 | 11.2 | 35.0 | 40.0 |
| 5 min | 15.0 | 8.4 | 35.0 | 30.0 |
| 15 min | 8.4 | 4.7 | 20.0 | 16.8 |
| 1 hour | 5.9 | 3.3 | 10.0 | 11.8 |

`bb_normalizedPrice = |close−open| / SMA(|close−open|,30)[1]`
`bb_baseBullish = close>open AND bb_positiveDiff>SMA(bb_positiveDiff,20)`  (Bearish = close<open, same)
`relVolRatio` = `tv_ta.relativeVolume(30, anchor, Cumulative)` current/past ratio.

---

## 1. ATOMIC SIGNAL GLOSSARY (the building-block gates)

| Signal | Dir | Full gate |
|--|--|--|
| `SAAB` | Bull | `bb_baseBullish AND th_saab_kratos ≤ bb_normalizedPrice < th_1x` |
| `Kratos` | Bear | `bb_baseBearish AND th_saab_kratos ≤ bb_normalizedPrice < th_1x` |
| `BullRVOL1x` | Bull | `bb_baseBullish AND th_1x ≤ bb_normalizedPrice < th_gs_moab` |
| `BearRVOL1x` | Bear | `bb_baseBearish AND th_1x ≤ bb_normalizedPrice < th_gs_moab` |
| `GrandSlam` | Bull | `bb_baseBullish AND bb_normalizedPrice ≥ th_gs_moab` |
| `MOAB` | Bear | `bb_baseBearish AND bb_normalizedPrice ≥ th_gs_moab` |
| `Pentagon` | Neutral | `th_1x ≤ relVolRatio ≤ th_wtc` |
| `WTC` | Neutral | `th_wtc < relVolRatio ≤ th_hiroshima` |
| `Hiroshima` | Neutral | `relVolRatio > th_hiroshima` |
| `Nagasaki` | Neutral | `enableNagasaki AND volume is a new running max (ATH volume)` |
| `Long N` (1–5) | Bull | `hybRegRatio>RegN_Eff AND hybCumRatio>CumN_Eff AND close>open AND hybBodyRat≥BodyN_Eff` |
| `Short 1/2` | Bear | `hybRegRatio>Reg{1,2}_Eff AND hybCumRatio>Cum{1,2}_Eff AND close<open AND hybBodyRat≥Body{1,2}_Eff` |
| `sig_bull_UU/UUU/UUUU` | Bull | 2/3/4 consecutive `bb_baseBullish` bars, each `bb_normalizedPrice∈(th_low,50)`, sum≥seqTh |
| `sig_bear_DD/DDD/DDDD` | Bear | 2/3/4 consecutive `bb_baseBearish` bars, same range/sum rule |
| `2x SAAB / Kratos / Bull1x / Bear1x` | dir of base | `sigX[1] AND sigX` (same signal two bars running) |
| `B2B Mid Bull` | Bull | `(SAAB[1]·BullRVOL1x) OR (BullRVOL1x[1]·SAAB)`, excl. the 2x cases |
| `B2B Mid Bear` | Bear | `(Kratos[1]·BearRVOL1x) OR (BearRVOL1x[1]·Kratos)`, excl. the 2x cases |
| `DispBull` | Bull | `range[1]∈(stdev×i_std_min, stdev×i_std_max] AND low>high[2] AND open[1]<close[1]` |
| `DispBear` | Bear | `range[1]∈(…] AND high<low[2] AND open[1]>close[1]` |
| `CDispBull/Bear 2+/3+` | dir | DispBull/Bear with streak ≥2 / ≥3 |
| `sigBullPBJ` | (gate) | `crossover(src, supertrend_line) AND a prior pocket-pivot armed it` (pbj_buy: `low<EMA20·(1−atrThr) AND low=lowest(low,25) AND volume>SMA(vol,20)·0.1`) |
| `sigBearPBJ` | (gate) | `crossunder(src, supertrend_line) AND prior pbj_sell armed it` |
| `effBullPBJ_onBar` | (gate) | `isSub2Min ? hvdpbj_floored_bull : sigBullPBJ` (sub-2min adds HV+disp floor) |
| `pbjOnBar / pbjOn2/3/4` | (window) | PBJ on this bar / within last 2 / 3 / 4 bars |
| `is{75,150,250,500,1000}Bar` | Neutral | `volume[1] == highest(volume, f_hvLen(N))[1]` (f_hvLen ×2.5 on sub-minute) |
| `hvd_bull` | Bull | `base_hv_hit AND range[1]>stdev(range,100)[1]·5.0 AND low>high[2] AND close[1]>open[1]` |
| `hvd_bear` | Bear | `base_hv_hit AND range[1]>thresh AND high<low[2] AND close[1]<open[1]` |
| `base_hv_hit` | Neutral | `HEV(volume[1] new ATH) OR (a selected base tier 50–1000 hit AND not HEV)` |
| `hvdpbj_bull/bear` | dir | `hvd_bull/bear AND sigBullPBJ[1] / sigBearPBJ[1]` |
| `sigCS1Bull` | Bull | `cs_validBody(body%[1]≥0.85) AND (gzi_bullHV OR gzi_bullGZI) AND (SAAB[1] OR BullRVOL1x[1] OR GrandSlam[1])` |
| `sigCS2Bull` | Bull | `cs_validBody AND (gzi_bullHV OR gzi_bullGZI) AND (Pentagon[1] OR WTC[1] OR Hiroshima[1] OR Nagasaki[1])` |
| `sigCS12Bull` | Bull | `sigCS1Bull AND sigCS2Bull` |
| `sigPUP` | Bull | `(close−open)/open·100 > 3% AND volume>highest(redVol,10d) AND EMA50>EMA150≥EMA200 AND close≥0.75·52wHi AND close>1.30·52wLo` |

---

## 2. DETECTION SPOTS (visual plots) — full gate

| # | Spot (title / marker) | Dir | Full visual-plot gate | Offset |
|--|--|--|--|--|
| 1 | PBJ+Any (yellow ◆ below) | Neutral | `show_PBJplusAny AND pbjAnyFired` | 0 |
| 2 | B2B PBJ+Any (orange ◆ below) | Neutral | `show_B2B_PBJplusAny AND pbjAnyFired AND pbjAnyFired[1]` | 0 |
| 3 | PBJ+Long (gold ▲ below) | Bull | `show_PBJplusLong AND effBullPBJ_onBar AND (≥1 Long1–5)` | 0 |
| 4 | PBJ+Short+HV (orange ▼ above) | Bear | `show_PBJplusShortHV AND effBearPBJ_onBar AND (is500Bar OR is1000Bar) AND (Short1 OR Short2)` | 0 |
| 5 | Long+HV (blue ▲ below) | Bull | `show_LongPlusHV AND (is500Bar OR is1000Bar) AND (≥1 Long1–5 on [1])` | −1 |
| 6 | HVD+PBJ+Any (purple ◆ below) | **Mixed⚠** | `show_HVDplusPBJany AND (hvdpbj_bull OR hvdpbj_bear)` — one marker both dirs | −1 |
| 7 | HV+D+Any (green ▲ below) | **Mixed🐞** | `show_HVplusDany AND (hvd_bull OR hvd_bear) AND ≥1 co-signal[1]` — **always green even on bear** | −1 |
| 8 | Nagasaki (purple ⚑ top) | Neutral | `sigNagasaki` (no toggle) | 0 |
| 9 | Nag+Strong (magenta ▲) | Mixed | `show_NagStrong AND sigNagasaki AND (≥1 of Long1–5/GrandSlam/WTC/Hiroshima/MOAB/HV1000)` | 0 |
| 10 | Nag+HV+D (magenta ▲) | Bull | `show_NagStrong AND hvd_bull AND sigNagasaki[1]` | −1 |
| 11 | HV+D Bull (green ▲ below) | Bull | `hvd_bull` (no toggle) | −1 |
| 12 | HV+D Bear (red ▼ above) | Bear | `hvd_bear` (no toggle) | −1 |
| 13 | HVD+PBJ Bull (purple ◆ below) | Bull | `hvdpbj_bull` (no toggle) | −1 |
| 14 | HVD+PBJ Bear (purple ◆ above) | Bear | `hvdpbj_bear` (no toggle) | −1 |
| 15 | LONG 1 (blue ▲ below) | Bull | `show_Long1 AND sigAddLong1` | 0 |
| 16 | LONG 2 (teal ▲ below) | Bull | `show_Long2 AND sigAddLong2` | 0 |
| 17 | LONG 3 (purple ▲ below) | Bull | `show_Long3 AND sigAddLong3 AND curBarIsHV500or1K` | 0 |
| 18 | LONG 4 (orange ▲ below) | Bull | `show_Long4 AND sigAddLong4 AND curBarIsHV500or1K` | 0 |
| 19 | LONG 5 (fuchsia ▲ below) | Bull | `show_Long5 AND sigAddLong5 AND curBarIsHV500or1K` | 0 |
| 20 | HV 1000 (blue ● top) | Neutral | `show_HV1000 AND is1000Bar AND (≥1 Long1–5 on [1])` | −1 |
| 21 | HV 500 (red ● top) | Neutral | `show_HV500 AND is500Bar AND not is1000Bar AND (≥1 Long1–5 on [1])` | −1 |
| 22 | HV 250 (yellow ● top) | Neutral | `show_HV250 AND is250Bar AND not higher AND pbjOn2` | −1 |
| 23 | HV 150 (aqua ▼ bottom) | Neutral | `show_HV150 AND is150Bar AND not higher AND pbjOn2` | −1 |
| 24 | HV 75 (purple ▼ bottom) | Neutral | `show_HV75 AND is75Bar AND not higher AND pbjOn2` | −1 |
| 25 | CS1 Bull (green ▲ below) | Bull | `show_CS1Bull AND sigCS1Bull` | −1 |
| 26 | CS2 Bull (aqua ▲ below) | Bull | `show_CS2Bull AND sigCS2Bull` | −1 |
| 27 | CS1+CS2 Bull (blue ▲ below) | Bull | `show_CS12Bull AND sigCS1Bull AND sigCS2Bull` | −1 |
| 28 | PUP (lime ▲ below) | Bull | `show_PUP AND sigPUP` | 0 |

---

## 3. ALERTS — full gate (one alert per bar; lines joined with " | ")

The single `alert()` fires once per closed bar if ANY line below is non-empty. Tiers stack into one message.

| Tier | Alert line text | Full alert gate |
|--|--|--|
| 0 | `NAGASAKI \| …co-firers` | `sigNagasaki` (always) |
| 0 | `★★★ NAGASAKI+STRONG: …` | `show_NagStrong AND sigNagasaki AND (≥1 strong: Long1–5/GrandSlam/WTC/Hiroshima/MOAB/HV1000)` |
| 0 | `★★★ NAGASAKI+STRONG: HVx+D…` | `show_NagStrong AND hvd_bull AND sigNagasaki[1]` |
| 1 | `PBJ+LONG: …` | `show_PBJplusLong AND effBullPBJ_onBar AND (≥1 Long1–5)` |
| 1 | `PBJ+SHORT+HVx: …` | `show_PBJplusShortHV AND effBearPBJ_onBar AND (is500/1000Bar) AND (Short1/2)` |
| 1 | `B2B PBJ+ANY \| now:… \| prev:…` | `show_B2B_PBJplusAny AND pbjAnyFired AND pbjAnyFired[1]` |
| 1 | `PBJ+…` (single) | `show_PBJplusAny AND pbjAnyFired AND NOT (B2B fired)` |
| 2 | `HVx+D+PBJ+… Bull/Bear` | `show_HVDplusPBJany AND (hvdpbj_bull OR hvdpbj_bear)` (direction in text) |
| 2 | `HVx+D+… Bull/Bear` | `show_HVplusDany AND (hvd_bull OR hvd_bear) AND ≥1 co-signal[1]` |
| 3 | `LONG+HVx: …` | `show_LongPlusHV AND (is500/1000Bar) AND (≥1 Long1–5 on [1])` |
| 4 | `LONG 1` / `LONG 2` | `show_Long{1,2} AND sigAddLong{1,2}` |
| 5 | `LONG 3+HV` / `4+HV` / `5+HV` | `show_Long{3,4,5} AND sigAddLong{3,4,5} AND curBarIsHV500or1K` |
| 6 | `HVx+D Bull` | `hvd_bull AND NOT hvdAnyFired` |
| 6 | `HVx+D Bear` | `hvd_bear AND NOT hvdAnyFired` |
| 6 | `HVD+PBJ Bull` | `hvdpbj_bull AND NOT hvdpbjAnyFired` |
| 6 | `HVD+PBJ Bear` | `hvdpbj_bear AND NOT hvdpbjAnyFired` |

### ❌ Detections that PLOT but have NO standalone alert (only alert if PBJ/HV+D/Nagasaki coincide)
`HV 75 / 150 / 250 / 500 / 1000`, `CS1`, `CS2`, `CS1+CS2`, `PUP`, and the raw single signals
(`SAAB, Kratos, Bull/Bear RVOL1x, GrandSlam, MOAB, WTC, Hiroshima, UU/DD…, Disp…`) — these reach
the alert **only** inside a `PBJ+Any` / `HV+D+Any` / `Nagasaki` co-list, never on their own.
