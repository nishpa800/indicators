# Squarify 46 v2 — extraction report (compact)

Source: `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` · 2622 lines · Pine v5 · title `"SQUARIFY 46 v2"` (shorttitle `"SQ46 v2"`) · overlay

## Summary

Top-level fund signal. 4 explicit pipelines: Pipeline A (HV+D, volume rank × disp+FVG, 3 disp profiles); Pipelines B+C ("USE Alarm 1293" — Engines 1-11: RVOL, FAUNA, USE-Disp, GZ1/HV-FVG, PUP/PPD, PBJ, Ping-Pong SR, UU/UUU/UUUU, Session+AlphaStrike, LongShort); Pipeline D (TripleCo + B2B HV+D + UC fusion). On top: TNT propulsion (Napalm/Charge/B2B/B2BNPM/NPM+TNT), Boom Hunter Omega, Heavy Pentagon → WBUSH, **46 numbered top-level composites S1-S46**, Tier-1/Tier-2 opening confluence, stats logger.

Counts: 0 `plot()`, 48 `plotshape()`, 2 `alertcondition()` (T1+T2 opening confluence), 4 `alert()` (BULL/BEAR aggregator + T1/T2 JSON).

## Atoms catalog (60+ entries; comprehensive list in agent transcript)

**Pure roots in Squarify (canonical or cross-ref):**

| Root | Source | Provenance |
|---|---|---|
| `squarify::SAAB`, `KRATOS`, `BULL_RVOL_1X`, `BEAR_RVOL_1X`, `GRAND_SLAM`, `MOAB`, `WTC`, `HIROSHIMA`, `PENTAGON`, `NAGASAKI` | 442-462 | Cross-ref to `heavy-pentagon::*` — re-implemented |
| `squarify::MB_B/MB_R`, `RE_B/RE_R`, `TA_B/TA_R`, `GG_B/GG_R`, `TR/ES/GDR_B/R` | 482-498 | FAUNA core/exclusion atoms |
| `squarify::PUP` / `PPD` | 614-619 | Cross-ref to `b2b-pup::*` or canonical here |
| `squarify::DISP_BULL` / `DISP_BEAR` (USE Displacement) | 508-516 | Cross-ref to `hvdpbjppd::DISPLACEMENT` |
| `squarify::DISP5_BULL/BEAR` | 517-519 | Internal-only 5x disp (no FVG) — used inside HW |
| `squarify::DISP2_BULL/BEAR`, `DISP3_BULL/BEAR` | 521-525, 540-543 | DISP-family streak primitives |
| `squarify::GZ_BULL_GZI` / `GZ_BEAR_GZI`, `GZ_BULL_HV` / `GZ_BEAR_HV` | 557-602 | Cross-ref to `hv-fvg-gz1-og::*` |
| `squarify::PBJ_BULL/BEAR`, `PB_BULL/BEAR` | 621-745 | Cross-ref to `hvdpbjppd::PBJ` / `PB` |
| `squarify::PING_PONG_BULL/BEAR` (`bull_pp`/`bear_pp`) | 747-882 | Cross-ref to `hvdpbjppd::PING_PONG_*` |
| `squarify::UU/UUU/UUUU` (raw streaks) | 884-910 | Streak primitives (use bb_baseBullish AND normalizedPrice≥0.5) |
| `squarify::MATRIX_NUMBER` | 1214 | Cross-ref to `hvdpbjppd::MATRIX_NUMBER` |
| `squarify::LONG1/LONG2/SHORT1/SHORT2` | 1227-1235 | Cross-ref to `hvdpbjppd::LONG1`/etc. |
| `squarify::HV75/HV150/HV500/HV1000` | 1271-1273 | Cross-ref |
| `squarify::BOOM_HUNTER_OMEGA` | 1693-1764 | Cross-ref |
| `squarify::TNT_RAW_BULL/BEAR` | 1360-1536 | TNT propulsion engine — vob+aggressive+fauxbox token confluence |
| `squarify::NAPALM_RAW_BULL/BEAR` | 1582-1595 | Cross-ref to `tnt-od::NAPALM` |
| `squarify::CHARGE_RAW_BULL/BEAR` | 1597-1614 | Cross-ref to `tnt-od::CHARGE` |

**Atoms reclassified as composites per Anish's strict rule (compose other named atoms):**

- `squarify::FAUNA_BULL/BEAR` (line 474-506) — composite tier-1: `(MB OR RE OR TA) AND NOT (TR OR ES OR GDR OR GG-excl)`.
- `squarify::DISPCONS2_BULL/BEAR`, `DISPCONS3_BULL/BEAR` — composite tier-1.
- `squarify::NEO_BULL/BEAR`, `TRINITY_BULL/BEAR` — composite tier-1.
- `squarify::FOXTROT_BULL/BEAR` — composite tier-1 (4-bar FAUNA streak).
- `squarify::COMBOSET1-4_BULL/BEAR` — composite tier-1.
- `squarify::sigP21BullUUUU/UUU`, `sigUUBull` — composite tier-2.
- `squarify::ALPHA_STRIKE_BULL/BEAR`, `OD_BULL/BEAR`, `GOLF_BULL/BEAR`, `PAF_BULL/BEAR` — composite tier-2.

## 46 numbered composites (selected; full table in agent transcript)

| ID | Tier | Composition | Plot offset |
|---|---|---|---|
| `squarify::S1_SDUPER_BULL` | 4 | `csNew3 AND det_bullNapalmCons AND sigPUP[1]` | -1 |
| `squarify::S2_SUPER_BULL` | 3 | `csNew3 AND det_bullNapalmCons` | -1 |
| `squarify::S3_HW_BULL` | 3 | `(close>open) AND disp5 AND PBJ AND HW-slot AND (Floor OR 2F)` | 0 |
| `squarify::S4_FLOOR` | 3 | `anyBullFloor AND oneOfThese AND cb1_pass_floor` | 0 |
| `squarify::S5_2F` | 3 | `anyBull2nd AND oneOfThese AND cb1_pass` | 0 |
| `squarify::S6_UUUU` | 2 | `sigP21BullUUUU` | 0 |
| `squarify::S7_UUU` | 2 | `sigP21BullUUU AND NOT UUUU` | 0 |
| `squarify::S8_UU` | 3 | `sigUUBull AND oneOfThese_forUU AND NOT UUU AND NOT UUUU` | 0 |
| `squarify::S9_ALPHA_STRIKE` | 3 | `firstOfDay AND bull_pp AND (GS OR RVOL1x) AND PBJ AND as_fauna_expanded` | 0 |
| `squarify::S10_OMEGA_A` | 3 | `bh_anyOmega AND omega_cosignal_A AND NOT MOAB AND NOT DISP_BEAR` | 0 |
| `squarify::S11_FOX` | 3 | `Foxtrot AND (hvd_pbj_bull OR oneOfThese)` | 0 |
| `squarify::S12_OD` | 2 | `sigODBull` | -1 |
| `squarify::S13_GOLF` | 2 | `sigGolfBull` | -1 |
| `squarify::S14_PBJ_F2_E3` | 2 | `PBJ AND (sBullF2 OR sBullE3)` | 0 |
| `squarify::S15_PBJ_CL` | 2 | `PBJ AND sBullFC` | 0 |
| `squarify::S16_F2CL_E3` | 2 | `sBullF2[1] AND sBullFC[1] AND sBullE3` | 0 |
| `squarify::S17_E3_2of3PP` | 2 | `sBullE3 AND pupCntE3≥2` | 0 |
| `squarify::S18_F2_2D` / `S19_E3_2D` / `S21_CL_2D` | 2 | day-over-day F2/E3/FC | 0 |
| `squarify::S20_F2E3_SEQ` | 2 | `sBullE3 today AND sBullF2 yesterday` | 0 |
| `squarify::S22_NPM_PLUS` | 4 | `det_bullNapalmCons AND ((PBJ[1] AND (csNew3 OR HW[1] OR sigWMD[1])) OR sigWMD[1])` | -1 |
| `squarify::S23_NPM12` / `S24_NPM3` | 3 | `det_bullNapalmCons AND (cb1_pass_npm OR cb2_pass_npm OR cb3_pass_npm)` | -1 |
| `squarify::S25_B2BNPM` | 2 | `det_b2bBullNapalm` | -1 |
| `squarify::S26_NPM_TNT` | 2 | `raw_napalmBull AND raw_bullTNT[1]` | -1 |
| `squarify::S27_CO` | 3 | `hvd_fire_bull AND PBJ[1] AND (csNew3 OR csNew1)` | -1 |
| `squarify::S28_HVD_PBJ` | 2 | `hvd_pbj_bull AND NOT co_bull_pbj` | -1 |
| `squarify::S29_B2BHVD_PBJ` | 2 | `b2b_bull_pbj` | -1 |
| `squarify::S30_B2BHVD` | 2 | `b2b_bull_nopb AND NOT b2b_bull_pbj` | -1 |
| `squarify::S31_UU_UC` | 3 | `uu_any AND csNew3` | -1 |
| `squarify::S32_GRAIL` | 4 | `det_bullNapalmCons AND PBJ[1] AND PUP[1] AND csNew3` | -1 |
| `squarify::S33_FLR_NPM` | 4 | `anyBullFloor[1] AND det_bullNapalmCons` | -1 |
| `squarify::S34_NPM_PBJ_PUP` | 3 | `det_bullNapalmCons AND PBJ[1] AND PUP[1] AND NOT GRAIL` | -1 |
| `squarify::S35_NAG_PLUS` | 2 | `sigNagasaki AND (RVOL1x OR GS OR FAUNA OR DISP OR PBJ OR PUP OR HV-FVG OR GZI)` | 0 |
| `squarify::S36_UU_HVD` / `S37_UU_NPM` | 3 | `(UUUU[1] OR UUU[1] OR UU[1]) AND (hvd_pbj_bull / det_bullNapalmCons)` | -1 |
| `squarify::S38_FLR_UU` | 4 | `(anyBullFloor OR anyBull2nd) AND uu_any` | 0 |
| `squarify::S39_FOS_PUP_1X` | 2 | `fosterPBJSignal AND PUP AND (RVOL1x OR det_bullNapalmCons)` | 0 |
| `squarify::S40_NPM_UC` / `S44_NPM_UC_PBJ` | 3 | `det_bullNapalmCons AND csNew3 (AND PBJ[1])` | -1 |
| `squarify::S41_WBUSH_BULL` | 3 | `sig_WBUSH_Bull = HYY OR HN OR HNV OR HT OR NHx2 (bull-classified)` | 0 |
| `squarify::S42_WBUSH_BEAR` | 3 | mirror | 0 |
| `squarify::S43_WBUSH_NEUTRAL` | 3 | mirror with noDisp | 0 |
| `squarify::S45_UC_NAGASAKI_BULL` / `S46_UC_NAGASAKI_BEAR` | 3 | `csNew3 AND sigNagasaki[1]` | -1 |

T1 OPENING CONFLU (line 2486, alertcondition 2491): `sessBar==1 AND disp_std_mult≥t1_disp_thresh AND csNew3 AND hvd_fire_bull AND sigBullRVOL1x`. Tier 4. Offset 0.

T2 OPENING CONFLU (line 2514, alertcondition 2519): `sessBar∈[1,2] AND det_b2bPUP AND uu_any`. Tier 4. Offset 0.

## Other key composites (intermediates)

- `csNew1=FVG_COMBO` = `comboSet1 OR comboSet2`.
- `csNew2=MATRIX_COMBO` = `comboSet3 OR comboSet4`.
- `csNew3=UNIFIED_COMBO` = **`csNew1 AND csNew2[1]`** (line 1257) — **NOTE: 1-bar lagged AND in Squarify, but same-bar AND in HVDPBJPPD canonical. DRIFT to flag.**
- `anyBullFloor` / `anyBull2nd` / `anyBearRoof` / `anyBearPent` (Floor/2F/Roof/Penthouse cores).
- `superBull` / `sduperBull` (raw — used by S1/S2).
- `cc_bull_active` (Combo Chain — latched).
- `lsc_bull_active` (Long/Short Chain — latched).
- `WBUSH_BULL/BEAR/NEUTRAL` = OR over 5 Heavy Pentagon family bases × directional classifier.

## Offset bug observations (for redundancy diagnostic)

- All TNT/NPM/Charge fusions correctly offset=-1.
- HV+D fusions all offset=-1.
- **S35 NAG+** uses sigDISPBull (FVG-bearing) but plotted offset=0 — **potential offset inconsistency** vs S22 NPM+ which uses offset=-1.
- **WBUSH (S41/42/43)** plotted offset=0 but uses sigDISPBull — **same potential inconsistency**.
- T1/T2 opening confluence offset=0 (uses bar-current operands).

## Caveats

- S7 (UUU) is intentionally absent in plot numbering on B2B PUP but PRESENT in Squarify (B2B PUP has "no S7"; Squarify has S7=UUU).
- 41 of 46 numbered plots are bull-only on chart; bear computed but only used in aggregator alert.
- `sigOmegaLong` (full Omega) computed but only `sigOmegaLongA` (high-conf) plotted as S10.
- `b2b_*` family (lines 2085-2107) defined but not bound to plots in v2 — leftover from B2B-overlap removal cycle.
- `csNew3` lagged-AND in Squarify vs same-bar-AND in HVDPBJPPD = **CRITICAL drift to reconcile**.
