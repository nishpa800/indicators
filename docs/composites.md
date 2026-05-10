# Composites Catalog — sorted by tier, then by indicator

Every composite (named signal whose definition uses at least one root or lower-tier composite by name) across the indicator suite. Source of truth: `data/indicators.yaml`.

---

## Tier 1 — composites of roots only

### Pocket Pivot family

- **`anish-50-1st-combo::SUPER_PUP`** — `PUP AND BULL_PASS` same bar. Plot offset 0.
- **`anish-50-1st-combo::SUPER_PPD`** — mirror.
- **`anish-50-1st-combo::GAP_UP_SIG`** — `gapUpEnabled AND (open > close[1] × (1 + gapValue/100))`. Not plotted, only consumed by ALL_THREE_BULL.
- **`anish-50-1st-combo::GAP_DN_SIG`** — mirror.

### B2B family

- **`b2b-pup::B2B_PUP`** (`det_b2bPUP`) — `PUP AND PUP[1]`. Plot offset 0.
- **`b2b-pup::B2B_PPD`** — mirror.
- **`b2b-pup::S1_B2B_PUP_BULL`** — `det_b2bPUP AND gates`. Plot offset 0.
- **`hvdpbjppd::B2B_HVD_BULL`** (`b2b_bull_raw`) — `HVD_BULL AND HVD_BULL[1]`. Plot offset -1.
- **`hvdpbjppd::B2B_HVD_BEAR`** — mirror.
- **`tnt-od::B2B_NAPALM_BULL`** — `NAPALM_BULL AND NAPALM_BULL[1]`. Plot offset -1.
- **`tnt-od::B2B_NAPALM_BEAR`** — mirror.
- **`squarify::DET_B2B_BULL_NAPALM`** (`det_b2bBullNapalm`) — `det_bullNapalmCons AND det_bullNapalmCons[1]`. Used by S25.

### Sequential / co-occurrence

- **`tnt-od::FUSE_BULL`** — sequential cascade NPM → TNT → CONT all within `SUDDEN_PROX=3` bars, in-session. Plot offset 0.
- **`tnt-od::FUSE_BEAR`** — mirror.
- **`tnt-od::CATALYST_BULL`** — `NAPALM AND CS1_BULL` same visual bar. Plot offset -1.
- **`tnt-od::CATALYST_BEAR`** — mirror.
- **`tnt-od::PBJ_NPM_BULL`** — `NAPALM AND PBJ[1] AND pnGateBull`. Plot offset -1.
- **`tnt-od::PBJ_TNT_BULL`** — `TNT AND PBJ AND ptGateBull`. Plot offset 0.
- **`tnt-od::IGNITE_TC_BULL`** — `TNT AND CONT`. Plot offset 0.
- **`tnt-od::IGNITE_NC_BULL`** — `NAPALM AND CONT[1]`. Plot offset -1.
- **`tnt-od::DYNAMITE_BULL`** — bespoke 5σ bar[1]+bar[2] + FAUNA + FVG. Plot offset -1.
- **`tnt-od::RC_NPM_TNT_BULL`** — `NAPALM AND TNT[1]`. Plot offset -1.

### Heavy Pentagon (15 directional combos, all tier-1 with displacement classifier)

All 15 share a base co-occurrence pattern × 3 directions (Bull/Bear/Neutral via `dispBull`/`dispBear`/`noDisp`):

- **`HEAVY_YIN_YANG_*`** = (Pipeline-1 directional event) AND (Pipeline-2 neutral heavy event) AND directional classifier.
- **`HEAVY_NAGASAKI_*`** = `NAGASAKI AND P1-directional AND classifier`.
- **`HEAVY_NAGASAKI_VOL_*`** = `NAGASAKI AND P2-neutral AND classifier`.
- **`HEAVY_TRIDENT_*`** = `NAGASAKI AND P1 AND P2 AND classifier`.
- **`NEUTRAL_HEAVY_X2_*`** = pair of P2 (`(Pent AND WTC) OR (Pent AND Hiro) OR (WTC AND Hiro)`) AND classifier.

All plot offset 0.

### Floor/Roof family (HVDPBJPPD)

- **`hvdpbjppd::FLOOR_BULL`** (`anyBullFloor`) — `bull_pp AND PBJ AND HW_slot` where `HW_slot = RVOL1x OR GS OR WTC OR Hiro OR (NAGASAKI AND nag_dir_bull)`. Tier 2 actually (uses HW-slot which is tier-1 OR), but plotted as platform-level. Plot offset 0.
- **`hvdpbjppd::2F_BULL`** (`anyBull2nd`) — `bull_pp AND PB AND HW_slot`.
- **`hvdpbjppd::ROOF_BEAR`** (`anyBearRoof`) — `bear_pp AND PBJ AND HW_slot_bear`.
- **`hvdpbjppd::PENTHOUSE_BEAR`** (`anyBearPent`) — `bear_pp AND PB AND HW_slot_bear`. **Namespace collision with `heavy-pentagon::PENTAGON` — Stage 6 rename to `anyBear2F`.**

### Matrix family

- **`hvdpbjppd::NEO_BULL`** — `MATRIX_NUMBER AND FAUNA_BULL`. Tier 1 composite.
- **`hvdpbjppd::TRINITY_BULL`** — `MATRIX_NUMBER AND NOT FAUNA_BULL AND directional`. Mutex with NEO_BULL.
- **`hvdpbjppd::NEO_ALIGNED_BULL`** — `NEO_BULL AND (LONG1 OR LONG2)`.
- **`hvdpbjppd::TRINITY_ALIGNED_BULL`** — `TRINITY_BULL AND (LONG1 OR LONG2)`.
- (Bear mirrors identical pattern with `BEAR_PASS`-direction classifications.)

### Streak qualifiers

- **`hvdpbjppd::FOXTROT_BULL`** — 4 consecutive `FAUNA_BULL` bars. Plot offset 0.
- **`hvdpbjppd::PAF_BULL`** — `PUP AND FAUNA_BULL AND PUP[1] AND FAUNA_BULL[1]`.
- **`hvdpbjppd::DISPCONS2_BULL`** — `DISP2_BULL AND streak≥2 AND FAUNA[0..1]`.
- **`hvdpbjppd::DISPCONS3_BULL`** — `DISP3_BULL AND streak≥3 AND FAUNA[0..2]`.
- **`hvdpbjppd::U_QUAL_BULL`** (UU base) — `bb_baseBullish AND bb_normalizedPrice ≥ 0.5`. Streak primitive.

### Visual / structural

- **`vob-ladder::LADDER_DEPTH`** — count of consecutive ascending tiers F→E→D→C→B→A. 0-6 ordinal.

---

## Tier 2 — composites of tier-1

### B2B numbered (Squarify and B2B PUP)

- **`b2b-pup::S2_BULL` (B2B+FAUNA)** — `B2B_PUP AND FAUNA[0] AND FAUNA[1]`. Offset 0.
- **`b2b-pup::S3_BULL` (B2B+DISP/HVD)** — `(PUP[1] AND PUP[2]) AND ((DISP AND DISP[1]) OR (HVD AND HVD[1]))`. Offset -1.
- **`b2b-pup::S5_BULL` (B2B+SAAB)** — `B2B_PUP AND directional-RVOL combo`. Offset 0.
- **`b2b-pup::S10_BULL` (L1 B2B + B2B PUP)** — `(LONG1 AND LONG1[1]) AND (B2B_PUP OR B2B_PUP[1])`. Offset 0.
- **`b2b-pup::S11_BULL`** — `B2B_PUP AND (CS1_BULL OR LONG1 OR LONG1[1])`. Offset -1.

### CS1 / FVG Combo

- **`b2b-pup::CS1_BULL_FVG_COMBO`** — `body% AND (gz_bullHV OR gz_bullGZI) AND (SAAB[1] OR RVOL1xB[1] OR GS[1] OR Pentagon[1] OR WTC[1] OR Hiro[1] OR Naga[1])`. Tier 2.
- **`hvdpbjppd::comboSet1_Bull`** — same shape (`cs_vb body-pct AND HV/GZI AND directional RVOL[1]`).
- **`hvdpbjppd::comboSet2_Bull`** — `cs_vb AND HV/GZI AND (Pent[1] (opt) OR WTC[1] OR Hiro[1] OR Naga[1])`.

### CS2 / Matrix Combo

- **`hvdpbjppd::comboSet3_Bull`** — `cs_vm AND matrix_any AND (SAAB OR RVOL1x OR GS)`.
- **`hvdpbjppd::comboSet4_Bull`** — `cs_vm AND matrix_any AND (Pent (opt) OR WTC OR Hiro OR Naga)`.

### Heavy Combo Toggles master gates

- **`hct::S1_HEAVY_COMBO_BULL`** — OR over 5 eligibility-gated heavy combos. Plot offset -1.
- **`hct::S2_HEAVY_COMBO_BEAR`** — mirror, offset -1.
- **`hct::S3_HEAVY_COMBO_NEUTRAL`** — mirror, offset 0.

### Numbered cluster combos (Ultra Combo + Squarify)

- **`ultra-combo::comboPBJ_F2_BULL/BEAR`** — `PBJ AND F2`.
- **`ultra-combo::comboPBJ_E3_BULL/BEAR`** — `PBJ AND E3`.
- **`ultra-combo::comboPBJ_CLUSTER_BULL/BEAR`** — `PBJ AND FC`.
- **`squarify::S14_PBJ_F2_E3`** — `PBJ AND (F2 OR E3)`. Offset 0.
- **`squarify::S15_PBJ_CL`** — `PBJ AND FC`. Offset 0.

### Streak (UU/UUU/UUUU)

- **`hvdpbjppd::sigUUBull`** — `rawUU AND paths(pA-pG) AND ≥2 distinct quals`. Tier 2.
- **`hvdpbjppd::sigP21BullUUU`** — `rawUUU AND paths`. Tier 2.
- **`hvdpbjppd::sigP21BullUUUU`** — `rawUUUU AND paths AND ≥4 distinct quals`. Tier 2.

### Alpha Strike / OD / Golf / NAG+

- **`hvdpbjppd::ALPHA_STRIKE_BULL`** — `firstOfDay AND bull_pp AND (GS OR RVOL1x) AND (PBJ OR PB) AND as_fauna`.
- **`hvdpbjppd::OD_BULL`** — `sessionBarCount ≤ od_max_bars AND (GZI OR comboSet1..4) AND DISP_prevDisp AND PUP AND PBJ`.
- **`hvdpbjppd::GOLF_BULL`** — `DISP AND FAUNA[1] AND PUP[1] AND DISP[1] AND FAUNA[2] AND PUP[2]` (3-bar pattern).
- **`squarify::S35_NAG_PLUS`** — `NAGASAKI AND (RVOL1x OR GS OR FAUNA OR DISP OR PBJ OR PUP OR HV-FVG OR GZI)`. Offset 0.

### Anish state-machine

- **`anish-50-1st-combo::TB_SELL`** — FSM over `bullPass` (≥5 consec) + `sPPBear` window. Offset 0.
- **`anish-50-1st-combo::FOSTER_BUY`** — mirror.

### VOB

- **`vob-asym::ZONE_CREATION_MARKER`** — per-bar boolean detecting array-size delta this bar.
- **`vob-ladder::ESCALATED`** — `ladder_depth > prev_depth AND barstate.isconfirmed`. Tier 2.

---

## Tier 3 — composites of tier-1 and tier-2

### Unified Combo (csNew3) — KEY DRIFT POINT

- **`hvdpbjppd::UNIFIED_COMBO_BULL`** (`csNew3_Bull`) — `csNew1_Bull AND csNew2_Bull` **same-bar AND** in canonical (`THE_ONLY_ONE`).
- **`squarify::UC` / `csNew3`** — `csNew1 AND csNew2[1]` **1-bar lagged AND**.
- **`b2b-pup::CS3_UNIFIED_COMBO_BULL`** — uses lagged-AND.
- **CRITICAL DRIFT** — Stage 6 must reconcile to one definition. See `docs/redundancy.md`.

### FVG Combo / Matrix Combo aggregators

- **`hvdpbjppd::FVG_COMBO_BULL`** (`csNew1_Bull`) — `comboSet1_Bull OR comboSet2_Bull`. Tier 3.
- **`hvdpbjppd::MATRIX_COMBO_BULL`** (`csNew2_Bull`) — `comboSet3_Bull OR comboSet4_Bull`. Tier 3.

### Triple AND CO

- **`hvdpbjppd::CO_BULL_PBJ`** — `HVD_BULL AND PBJ[1] AND USE_ANY[1]`. Plot offset -1.
- **`hvdpbjppd::CO_BULL_PB`** — `HVD_BULL AND PB[1] AND USE_ANY[1]`. Plot offset -1.
- **`squarify::S27_CO_BULL`** — `HVD_BULL AND PBJ[1] AND (csNew3 OR csNew1)`. Offset -1.

### HW / Combo Chain

- **`hvdpbjppd::HW_BULL`** — `(close>open) AND disp5 AND PBJ AND HW_slot AND (Floor OR 2F)`. Tier 3. Offset 0.
- **`hvdpbjppd::SUPER_BULL`** — `PBJ AND DISP AND (FAUNA OR LONG1) AND HW_slot AND ((Combo AND PUP) OR (Floor OR 2F))`. Tier 3.
- **`hvdpbjppd::SDUPER_BULL`** — `(Floor OR 2F) AND PBJ AND HW_slot AND Combo AND PUP AND DISP AND (FAUNA OR LONG1)`. Tier 3.
- **`squarify::S3_HW_BULL`** — same pattern as `hvdpbjppd::HW_BULL`. Offset 0.

### B2B HV+D variants

- **`hvdpbjppd::B2B_HVD_PBJ_BULL`** — `B2B_HVD_BULL AND (PBJ[1] OR PBJ[2])`. Offset -1.
- **`hvdpbjppd::B2B_HVD_PB_BULL`** — `B2B_HVD_BULL AND (PB[1] OR PB[2]) AND NOT PBJ`. Offset -1.

### Combo Chain (latched)

- **`hvdpbjppd::COMBO_CHAIN_BULL`** (`sigCCBull`) — see `chains` section below.
- **`hvdpbjppd::LSC_BULL`** — see `chains`.

### Heavy + cluster

- **`ultra-combo::comboHW_AnyBull`** — `anyHW AND (F2 OR E3 OR FC)`. Tier 3.
- **`ultra-combo::comboGZ_AnyBull`** — `GZI AND (sAnyBull OR sAnyBull[1])`. Tier 3.
- **`ultra-combo::comboHV_AnyBull`** — `HV AND (sAnyBull OR sAnyBull[1])`. Tier 3.
- **`ultra-combo::comboGZHV_AnyBull`** — `comboHV_AnyBull OR comboGZ_AnyBull`. Tier 3. Offset -1.
- **`ultra-combo::THREE_BAR_BULL`** — `PBJ-in-3 AND (B2B-PUP-in-3 OR ≥2 PUPs-in-3)`. Offset 0.
- **`ultra-combo::fosterHeavyBull`** — `anyFoster AND (ROC OR HW-set OR Super)`. Offset 0.
- **`ultra-combo::tbHeavyBear`** — mirror.
- **`ultra-combo::gzHvHeavyBull`** — `(GZI OR HV) AND (HW OR Super OR ROC)`. Offset -1.

### F2/E3 sequential

- **`ultra-combo::comboF2Cluster_E3_BULL`** — `F2[1] AND FC[1] AND E3`. Tier 3.
- **`ultra-combo::comboF2ClusterB2B_Bull`** — `F2 AND FC AND B2B_PUP`. Tier 3.
- **`ultra-combo::comboB2B_F2_BULL`** — `B2B_PUP AND F2`. Tier 3.
- **`ultra-combo::comboE3_2of3PUP_BULL`** — `E3 AND (PUP count in last 3 ≥ 2)`. Tier 3.
- **`squarify::S16_F2CL_E3`** — same as Ultra's `comboF2Cluster_E3`. Offset 0.

### Numbered Squarify (S22-S46 selected)

- **`squarify::S22_NPM_PLUS`** — `det_bullNapalmCons AND ((PBJ[1] AND (csNew3 OR HW[1] OR sigWMD[1])) OR sigWMD[1])`. Tier 4. Offset -1.
- **`squarify::S26_NPM_TNT`** — `NAPALM AND TNT[1]`. Offset -1.
- **`squarify::S31_UU_UC`** — `uu_any AND csNew3`. Tier 3. Offset -1.
- **`squarify::S36_UU_HVD`** — `(UU OR UUU OR UUUU)[1] AND hvd_pbj_bull`. Tier 3. Offset -1.
- **`squarify::S40_NPM_UC`** — `NAPALM_CONS AND csNew3`. Tier 3. Offset -1.
- **`squarify::S41_WBUSH_BULL`** — Heavy Pentagon family OR (HYY OR HN OR HNV OR HT OR NHx2) classified bull. Tier 3. Offset 0.
- **`squarify::S45_UC_NAGASAKI_BULL`** — `csNew3 AND NAGASAKI[1]`. Tier 3. Offset -1.

### TNT-OD enriched (Tier 2 in TNT-OD's own taxonomy, Tier 3 in bible)

- **`tnt-od::TNT_ENRICHED_BULL`** — `TNT_RAW AND enrichBull_N`. Offset 0.
- **`tnt-od::NPM_ENRICHED_BULL`** — `NAPALM AND enrichBull_N1`. Offset -1.
- **`tnt-od::CONT_ENRICHED_BULL`** — `CONT AND enrichBull_N`. Offset 0.
- **`tnt-od::WBUSH_BULL`** — Heavy Pentagon family AND USE V5 dispBull AND tntod_any_bull. Offset 0.

---

## Tier 4 — top-level fund signals

### Squarify peak

- **`squarify::S1_SDUPER_BULL`** — `csNew3 AND det_bullNapalmCons AND PUP[1]`. Offset -1.
- **`squarify::S2_SUPER_BULL`** — `csNew3 AND det_bullNapalmCons`. Offset -1.
- **`squarify::S32_GRAIL_BULL`** — `det_bullNapalmCons AND PBJ[1] AND PUP[1] AND csNew3`. Offset -1.
- **`squarify::S33_FLR_NPM`** — `anyBullFloor[1] AND det_bullNapalmCons`. Offset -1.
- **`squarify::S38_FLR_UU`** — `(anyBullFloor OR anyBull2nd) AND uu_any`. Offset 0.
- **`squarify::T1_OPENING_CONFLU_BULL`** — `sessBar==1 AND disp_std_mult ≥ t1_disp_thresh AND csNew3 AND HVD_BULL AND BULL_RVOL_1X`. Has alertcondition.
- **`squarify::T2_OPENING_CONFLU_BULL`** — `sessBar∈[1,2] AND B2B_PUP AND uu_any`. Has alertcondition.

### Ultra Combo peak

- **`ultra-combo::OPENER_BULL`** — `sessBar==1 AND (GZI OR HV) AND (HW-set OR PBJ OR ROC OR (1stPUP AND superPUP))`. Tier 4.
- **`ultra-combo::MEGA_BULL`** (`gz1MegaBull`/`hvMegaBull`/`gz1hvMegaBull`) — `(GZI OR HV OR both) AND anySuperBull AND PUP AND FAUNA AND DISP`. Tier 4. Offset -1.
- **`ultra-combo::SUPER_B2B_DAYS_BULL`** — `anySuperBull AND f_hadSignalYesterday(anySuperBull)`. Tier 4.
- **`ultra-combo::scanTrigger`** — `Super-PBJ OR Super-PB OR GS OR MOAB`. Tier 4. Alert-only.

### B2B PUP peak

- **`b2b-pup::S19_UC2_BULL`** — `≥2 Unified-Combo hits within 2 bars`. Tier 4. Offset -1.
- **`b2b-pup::S20_FMU_BULL`** — `≥2 hits of (FVG-Combo OR Matrix-Combo OR Unified) within 2 bars`. Tier 4. Offset -1.

### VOB Ladder Watch peak

- **`vob-ladder::FIRE_FULL`** — `escalated AND ladder_depth == 6`. Tier 3 (per VOB-ladder taxonomy). Has alertcondition.

---

## Chains (state machines / latched composites)

- **`hvdpbjppd::COMBO_CHAIN_BULL`** (`sigCCBull`) — Tier 3 latched. Activates when csNew2 (Matrix combo) is firing AND ≥`cc_min_hits=2` Matrix-combo hits in `cc_window=4` bars AND PBJ/PB inside window. Resets when no cs3-or-cs4 (canonical) — predecessor reset on no-cs1-2-3-4. Plot offset 0.

- **`hvdpbjppd::LSC_BULL`** (`sigLSCBull`) — Tier 2 latched. Activates when ≥`lsc_min_hits` Long1/Long2 hits in `lsc_window` AND PBJ/PB inside window. Resets when no L1/L2.

- **`hvdpbjppd::COMBO_CHAIN_BEAR`**, **`LSC_BEAR`** — symmetric mirrors.

- **`anish-50-1st-combo::TB_SELL`**, **`FOSTER_BUY`** — Tier 2 FSM with var counters; one-bar pulse with explicit reset (see Tier 2 section).

---

## Summary

| Tier | Count |
|---|---|
| Tier 1 | ~38 |
| Tier 2 | ~52 |
| Tier 3 | ~38 |
| Tier 4 | ~10 |
| Chains | 4 |

(Exact YAML count: 57 named composite entries, with bear mirrors compressed into bull entries where symmetric.)
