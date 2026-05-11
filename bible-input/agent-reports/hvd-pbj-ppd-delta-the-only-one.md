# HVD+PBJ+PPD delta — file: HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine

Source: `/home/user/indicators/hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` (1767 lines)

Siblings compared:
- S1 = `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` (1939 lines)
- S2 = `HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine`     (1939 lines)
- S3 = `HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine`     (2246 lines)

## Summary
- Detection-plot count in this file: 53 plotshapes (HV+D=2; PBJ/PB=4; USE Bull=22; USE Bear=21; CO=4; B2B=6 — minus 6 wrappers double-counted gives 53 effective fired surfaces)
- REAL-drift entries vs siblings: 12 root-level drifts touching ~17 detections
- Skipped (identical / cosmetic / ipsf-default): hundreds of input.* defaults, comments, plot colors, group strings — not enumerated

## REAL-drift table

| Detection plot | This file (line) | Sibling file (line) | Diff kind | One-line semantic difference |
|---|---|---|---|---|
| `sigDispConsBull2` (fire_DispConsBull2) | 545 | S1:570, S2:570, S3:544 | semantic-drift (offset) | THE_ONLY_ONE uses `sigFAUNABull and nz(sigFAUNABull[1])` (current+prev FAUNA bars). Siblings use `nz(sigFAUNABull[1]) and nz(sigFAUNABull[2])` (prev+prev2 FAUNA bars — shifted -1). |
| `sigDispConsBear2` | 546 | S1:571, S2:571, S3:545 | semantic-drift (offset) | Same shift as Bull2 (uses current FAUNA, siblings use [1]/[2]). |
| `sigDispConsBull3` (fire_DispConsBull3) | 562 | S1:587, S2:587, S3:561 | semantic-drift (offset) | THE_ONLY_ONE: `sigFAUNABull and nz(sigFAUNABull[1]) and nz(sigFAUNABull[2])`. Siblings: `nz(sigFAUNABull[1]) and nz(sigFAUNABull[2]) and nz(sigFAUNABull[3])`. |
| `sigDispConsBear3` | 563 | S1:588, S2:588, S3:562 | semantic-drift (offset) | Same shift as Bull3. |
| `csNew3_Bull` (fire_CS3B) | 1052 | S1:968, S2:968, S3:942 | semantic-drift (offset) | THE_ONLY_ONE: `csNew1_Bull and csNew2_Bull` (same-bar AND). Siblings: `csNew1_Bull and nz(csNew2_Bull[1])` (current AND previous bar of csNew2). |
| `csNew3_Bear` (fire_CS3R) | 1052 | S1:968, S2:968, S3:942 | semantic-drift (offset) | Same as Bull3 — siblings use `nz(csNew2_Bear[1])`. |
| `sigP21BullUUUU` (fire_BullUUUU) | 945 | S1:1172-1181, S2:1172-1181, S3:1083-1153 | semantic-drift (different body) | THE_ONLY_ONE: `conf and u4_bull_streak>=4 and u4_bull_hasDay1 and u4_pbj_bull and u4_disp_bull` (4-AND). Siblings compute via `f_uu_bull_scan(...)` returning 9 flags then OR many `pA..pF` clauses gated by `_ok=tfSec>120 or (_s>=th_saab_kratos and (_s>=th_1x or _p))`. S3 adds further `_sub2min_pass and _gate` filtering. Different boolean definition AND hardcoded thresholds (`th_saab_kratos`, `th_1x`, `tfSec>120`). |
| `sigP21BullUUU` (fire_BullUUU) | 979 | S1:1184-1193, S2:1184-1193, S3:1155-1219 | semantic-drift (different body) | Same kind of drift as UUUU above (3-bar variant). |
| `sigUUBull` (fire_BullUU) | 989 | S1:1196-1205, S2:1196-1205, S3:1222-1286 | semantic-drift (different body) | THE_ONLY_ONE uses `p21_bull_streak==2 and p21_bull_sum>=th_1x and ((uu_pbj_bull and uu_disp_bull) or uu_excA_bull or uu_excC_bull)`. Siblings use the f_uu_bull_scan-based `pA..pE` OR with the same `_ok` gate as UUUU. |
| `sigP21BearUUUU` / `UUU` / `sigUUBear` | 946,980,990 | S1:1208-1226, S2:1208-1226, S3:1289-1428 | semantic-drift (different body) | Bear mirrors of three above. |
| `sigAlphaStrikeBull` (fire_AlphaStrikeB) | 1057 | S1:1238, S2:1238, S3:1503 | semantic-drift (inclusion) | THE_ONLY_ONE accepts `(sigBullPBJ or sigBullPB)`. S1+S2 require `sigBullPBJ` only (no PB). S3 *also* requires `sigBullPBJ` only AND adds `sessionBarCount<=od_max_bars` session gate AND `as_disp_bull` (=sigDISPBull or hvd_fire_bull) gate. THE_ONLY_ONE has neither extra gate. |
| `sigAlphaStrikeBear` | 1058 | S1:1239, S2:1239, S3:1504 | semantic-drift (inclusion) | Bear mirror of AlphaStrikeBull. |
| `as_fauna_bull` (helper used in sigAlphaStrikeBull) | 1055 | S1:1236, S2:1236, S3:1501 | semantic-drift (inclusion) | THE_ONLY_ONE: `sigFAUNABull or sigLong1 or sigDISPBull or sigPUP or sigWTC or sigHiroshima or sigNagasaki`. S1+S2 add `hvd_fire_bull` to the OR. S3 drops `sigDISPBull` AND adds `sigNagPlusBull` (which doesn't exist in THE_ONLY_ONE) — and S3 splits disp into a separate `as_disp_bull` AND-gate. |
| `as_fauna_bear` | 1056 | S1:1237, S2:1237, S3 | semantic-drift (inclusion) | Bear mirror of as_fauna_bull. |
| `use_any_bull` (Pipeline D consumer) | 1427 | S1:1489, S2:1489, S3:1746 | semantic-drift (inclusion + body-of-component) | THE_ONLY_ONE references `sigP21BullUUUU/UUU/UUBull` (the strict-bodied versions). Siblings reference the `_indep` variants (which don't exist in THE_ONLY_ONE). Siblings ALSO include `sigOmegaLongA` term which has no analog in THE_ONLY_ONE (no second omega flavor, no `omega_cosignal_A` helper). Siblings drop `sigUSubBull` (THE_ONLY_ONE includes it). |
| `use_any_bear` | 1428 | S1:1490, S2:1490, S3:1747 | semantic-drift (inclusion) | Bear mirror of use_any_bull. |

## Internal-helper drift

### `sigP21Bull/BearUUUU/UUU/UU` family — wrapper name same, body radically different
- THE_ONLY_ONE 4U/3U/2U bodies are tight 3- to 4-AND chains using `p21_bull_streak`/`u4_bull_streak`/`u3_bull_streak` counters and pre-scanned `u4_pbj_bull`/`u3_pbj_bull`/`uu_pbj_bull` accumulators.
- All 3 siblings define `f_uu_bull_scan(_n)` (and bear) returning a 9-tuple `[_hp,_hpb,_hh,_hd,_hf,_ad,_asd,_dnp,_pnd]` and combine `pA..pF` clauses gated by `_ok` involving `tfSec`, `th_saab_kratos`, `th_1x`, and a recent-PBJ check `_p`. S3 adds further `_sub2min_pass` & `_gate` clauses.
- Siblings additionally publish `_indep` variants (e.g. `sigP21BullUUUU_indep := (pA or pB or pC or pE or pF) and _ok` — drops pD), used downstream by `use_any_bull` only. THE_ONLY_ONE has no `_indep` parallel.

### `sigOmegaLong` — same body across all 4 files (no drift). But siblings ALSO declare `sigOmegaLongA` using `omega_cosignal_A` (a tighter co-signal set). THE_ONLY_ONE has neither A-flavor nor cosignal_A. Pipeline D / `use_any_bull` in siblings includes `sigOmegaLongA`; THE_ONLY_ONE cannot.

### `sigNagPlusBull/Bear` — exists in S1/S2/S3, absent in THE_ONLY_ONE. THE_ONLY_ONE never plots it, so no missing detection plot. But it's referenced by S3's `as_fauna_bull` (semantic-drift row above).

## Hardcoded thresholds in this file (sorted by line)

| Line | Constant | Used in |
|---|---|---|
| 293 | `bb_avgLength = 30, bb_smaLength = 20` | RVOL normalization (engine 1) |
| 294 | `reg_length = 30, reg_calculationMode = "Cumulative", reg_adjustRealtime = true` | tv_ta.relativeVolume call |
| 296 | `fauna_gg_master = true, fauna_gg_body = 0.80` | FAUNA core-count gate |
| 386 | `pp_barSize=3.0, pp_lookback=10` | PUP/PPD body-% threshold + lookback |
| 387 | `zoo_ma_type="VWMA", zoo_ma_len=5, enable_PB=true` | PBJ engine MA |
| 388 | `zoo_pbj_ma_period=20, zoo_pbj_atr_period=14, zoo_pbj_hh_ll=25, zoo_pbj_atr_mult=3.0, zoo_pbj_vol_period=20, zoo_pbj_vol_mult=0.1` | PBJ engine thresholds (NOT user-tunable) |
| 389 | `zoo_use_st=true, zoo_st_period=10, zoo_st_mult=2.0` | PBJ Supertrend |
| 390-391 | `pp_min_candles=2, pp_buffer_ticks=10, pp_atr_mult=2.0, pp_trend_cnt=1, pp_max_levels=50, pp_min_count=3` | Ping-Pong SR engine |
| 431-433 | `bh_LPPeriod=6, bh_K1=0, bh_trigno=2, bh_LPPeriod2=27, bh_K12=0.8, bh_K22=0.3, bh_LPPeriod3=11, bh_n1=9, bh_n2=6, bh_n3=3, bh_n4=21, bh_n5=0, bh_lsmaline=200, bh_leftBars=1, bh_rightBars=1, bh_leftBars2=5, bh_rightBars2=5, bh_greyDist=30` | Boom Hunter / Omega thresholds |
| 444-448 | `f_rvol_1x_threshold` table (38, 33, 28, 23, 20, 18, 13, 13, 11, 10, 9, 7.5, 6.5, 6, 4.5, 4, 3.5, 1.8, 1.0) | RVOL 1x by tfSec |
| 444-448 | `f_gs_moab_threshold`, `f_saab_kratos_threshold`, `f_wtc_threshold`, `f_hiroshima_threshold` tables | Per-tier RVOL thresholds |
| 492-498, 505-511 | FAUNA constants `1.6*atr`, `0.70`, `1.8*avgVol`, `2.2*atr`, `0.15*rng`, `1.6*avgDelta`, `0.9*atr`, `1.5*avgBody`, `1.5*avgVol`, `0.2` body-rat | FAUNA core conditions |
| 528 | `disp5_thresh = disp_std*5.0` | disp5 hardcoded 5x mult |
| 574 | `_hv5000`, `_hv252`, `_hv63` | gz_isHV thresholds |
| 619 | `gz_fvgs.size()>50` | FVG cap |
| 641 | `atr_pb=atr14*2.0` | PB landing-zone half-width seed |
| 686/691 | `atr_pb*0.5` | PB landing-zone min half-height |
| 710 | `1.005`, `0.995` | PB approach proximity (bull/bear) |
| 738/740 | `bull_lvls > 30`, `bear_lvls > 30` | level cap |
| 901-902 | `bb_normalizedPrice>=2.0` | p21_qual ≥2x |
| 949-950 | `bb_normalizedPrice>1.0` | u3_qual >1x |
| 1067-1068 | `ta.highest(volume,75)[1]`, `..., 500)[1]`, `..., 1000)[1]` | sigHV75/500/1000 (NOT input) |
| 1146-1213 | Boom Hunter Q-thresholds: `-0.9`, `0.9`, `0.991`, `0.025`, `100`, `50`, `60`, `0.9999`, `20`, `80`, `99`, etc. | All hardcoded throughout BH |
| 1233 | `tfSec<=1800?2:tfSec<=3000?1:0` | TF gate min-confirms (1800s, 3000s buckets) |

## Notes for the cross-agent delta-table compiler

**Most important findings (3):**

1. **The UU-family bodies in THE_ONLY_ONE are a *different design* from siblings.** All three 1939/1939/2246 siblings use a unified `f_uu_bull_scan(_n)` helper returning 9 derived flags and combine them through 5–7 `pA..pH` clauses with an `_ok` TF/RVOL gate. THE_ONLY_ONE replaces this with hand-rolled streak counters + per-bar PBJ accumulators. The two will fire on materially different bars in many sessions, especially around session opens (`_ok` gate) and partial-PBJ sequences (`pE`/`pF` paths). This is the largest cluster of drift.

2. **`sigDispConsBull2/3` and `sigDispConsBear2/3` have a 1-bar offset drift** that affects every single fire of these four detections. THE_ONLY_ONE checks current+lagged FAUNA; siblings check lagged-by-1+lagged-by-2 (and -by-3 for the 3-variant). This is a small structural change but it shifts WHICH bar fires by exactly one.

3. **`csNew3_Bull/Bear` offset drift on the second leg** — THE_ONLY_ONE requires same-bar `csNew1 AND csNew2`, siblings require `csNew1 AND csNew2[1]` (csNew2 must have fired the *previous* bar). This is an architectural choice about whether the "Combo" requires a 2-bar pair vs. a single-bar coincidence. Affects every fire of fire_CS3B/fire_CS3R.

Secondary cluster: **`sigAlphaStrikeBull/Bear` inclusion drift** (PBJ-only in siblings vs PBJ-or-PB in THE_ONLY_ONE) plus the `as_fauna_bull` slot composition (THE_ONLY_ONE missing `hvd_fire_bull` term that S1/S2 include; S3 differs further by adding `sigNagPlusBull` and removing `sigDISPBull` then folding disp into a separate gate).

Tertiary: **Pipeline D `use_any_bull/bear` inclusion drift** — siblings rely on `_indep` variants of UU-family that don't exist in THE_ONLY_ONE, plus include `sigOmegaLongA` which is absent. The current THE_ONLY_ONE wires the gated UU-bool versions directly; siblings pre-strip the `pD` clause via `_indep` to allow Pipeline D to trigger more freely.

## Completion note (Phase 4)

Ported THE_ONLY_ONE.pine to `python_ports/hvd_pbj_ppd/the_only_one.py`. **59 detections registered** (HV+D=2; HV+D x PB/PBJ=4; USE Bull=22; USE Bear=21; Pipeline-D CO=4; B2B HV+D=6). **6 engine-level stubs** (registered in `STUBBED`): tv_ta.relativeVolume (regular + cumulative), full PBJ landing-zone state machine, Ping-Pong SR pivot/regime engine, GZ1 FVG-struct array engine, Boom Hunter / Omega Ehlers-filter chain, and request.security multi-TF HTF1/HTF2 lookup. Caller may inject pre-computed series for these via `df.attrs[<name>]` and the rest of the detections will compose them correctly. **15 distinct REAL-drift entries** vs the 3 sibling files (3 of which are the highest-impact: the UU-family body redesign in siblings, the DispCons2/3 1-bar offset shift, and the csNew3 same-bar vs prev-bar AND). Module imports cleanly (`python3 -c "import ...; print(len(m.DETECTIONS))"` returns 59). Smoke test on 200 random bars exercised all 59 detections without error. **No blockers**; downstream harness can now run drift cross-checks against the other three sibling ports as they come online.


