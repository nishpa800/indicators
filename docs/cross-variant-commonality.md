# Cross-Variant Commonality Table — 2026-05-10

Auto-generated from `data/indicators.yaml` after the Master Directory ingest (Stage 7.5). For every root or composite NAME (the suffix after `<provenance>::`), this table shows which indicator families define it as a root/composite and which reference it as a cross-indicator dependency.

**Reading the table**:

- **Owners ≥ 2** = the same name is defined in multiple families. It is a likely common denominator (same underlying detection across the suite) — but each definition still needs visual TV verification to confirm they fire on the same bar.
- **Owners = 1** = defined by exactly one family. Either a family-specific primitive (expected) or a drift candidate (if the name LOOKS shared but only one owner exists).
- **Cross-Indicator Deps** = families that reference the name without defining it. High value: confirms inheritance edges across the family graph.

**Canonical determination is NOT done here.** This table surfaces candidates for visual verification on TradingView. Per Anish (2026-05-10), labelling a variant canonical is the OUTPUT of TV verification, not the input.

## Roots — Common Denominators

### Defined in multiple families (sorted by owner count desc)

| Root name | # Owners | Owner families | Also referenced by |
|---|---:|---|---|
| `PBJ_BEAR` | 5 | fauna-shifu, hvd-pbj-ppd, hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir, pb-pbj | squarify, ultra-combo |
| `PBJ_BULL` | 5 | fauna-shifu, hvd-pbj-ppd, hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir, pb-pbj | squarify, ultra-combo |
| `PB_BEAR` | 5 | fauna-shifu, hvd-pbj-ppd, hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir, pb-pbj | squarify, ultra-combo |
| `PB_BULL` | 5 | fauna-shifu, hvd-pbj-ppd, hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir, pb-pbj | squarify, ultra-combo |
| `PPD` | 5 | b2b-pup, fauna-shifu, hvd-pbj-ppd, hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | anish-50-1st-combo, squarify, ultra-combo |
| `PUP` | 5 | b2b-pup, fauna-shifu, hvd-pbj-ppd, hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | anish-50-1st-combo, squarify, ultra-combo |
| `HVD_BEAR` | 4 | hvd-pbj-ppd, hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir, squarify | — |
| `HVD_BULL` | 4 | hvd-pbj-ppd, hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir, squarify | — |
| `MOAB` | 4 | b2b-pup, fauna-shifu, heavy-pentagon, heavy-weapons-8fvg-matrix | squarify |
| `NAGASAKI` | 4 | fauna-shifu, heavy-pentagon, heavy-weapons-8fvg-matrix, hvd-pbj-ppd | squarify |
| `SAAB` | 4 | b2b-pup, fauna-shifu, heavy-pentagon, heavy-weapons-8fvg-matrix | squarify |
| `AnishBear` | 3 | anish-50-1st-combo, anish-tb-foster, fauna-shifu | — |
| `AnishBull` | 3 | anish-50-1st-combo, anish-tb-foster, fauna-shifu | — |
| `FAUNA_BEAR` | 3 | b2b-pup, fauna-shifu, heavy-weapons-8fvg-matrix | — |
| `FAUNA_BULL` | 3 | b2b-pup, fauna-shifu, heavy-weapons-8fvg-matrix | — |
| `HEV` | 3 | hv-ladder-100-to-1k, hv-ladder-50-to-1k, hvd-pbj-ppd | — |
| `HV1000` | 3 | hv-ladder-100-to-1k, hv-ladder-50-to-1k, hvd-pbj-ppd | — |
| `HV500` | 3 | hv-ladder-100-to-1k, hv-ladder-50-to-1k, hvd-pbj-ppd | — |
| `Nagasaki` | 3 | b2b-pup, vob-asym, vob-asym-ummmm-masterdir | — |
| `WTC` | 3 | b2b-pup, heavy-pentagon, heavy-weapons-8fvg-matrix | squarify |
| `Alpha Strike Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Alpha Strike Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Bear UU` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Bear UUU` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Bear UUUU` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `BearPB` | 2 | anish-tb-foster, yin-yang-displacement-pbj | — |
| `BearPBJ` | 2 | anish-tb-foster, yin-yang-displacement-pbj | — |
| `Breakdown` | 2 | yin-yang-displacement-pbj, yin-yang-og-mofo | — |
| `Breakout` | 2 | yin-yang-displacement-pbj, yin-yang-og-mofo | — |
| `Bull UU` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Bull UUU` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Bull UUUU` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `BullPB` | 2 | anish-tb-foster, yin-yang-displacement-pbj | — |
| `BullPBJ` | 2 | anish-tb-foster, yin-yang-displacement-pbj | — |
| `CC Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `CC Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `CS1 FVG Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `CS1 FVG Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `CS2 MAT Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `CS2 MAT Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `CS3 Unified Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `CS3 Unified Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Disp Bear 2+` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Disp Bear 3+` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Disp Bull 2+` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Disp Bull 3+` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `E3_BEAR` | 2 | squarify, ultra-combo | — |
| `E3_BULL` | 2 | squarify, ultra-combo | — |
| `F2_BEAR` | 2 | squarify, ultra-combo | — |
| `F2_BULL` | 2 | squarify, ultra-combo | — |
| `FC_BEAR` | 2 | squarify, ultra-combo | — |
| `FC_BULL` | 2 | squarify, ultra-combo | — |
| `FVG_BEAR_RAW` | 2 | hv-fvg-gz1-og, proximity-gzi-hv | — |
| `FVG_BULL_RAW` | 2 | hv-fvg-gz1-og, proximity-gzi-hv | — |
| `Foxtrot Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Foxtrot Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `GRAND_SLAM` | 2 | heavy-pentagon, heavy-weapons-8fvg-matrix | squarify |
| `GZI_BEAR` | 2 | hv-fvg-gz1-og, proximity-gzi-hv | squarify, ultra-combo |
| `GZI_BULL` | 2 | hv-fvg-gz1-og, proximity-gzi-hv | squarify, ultra-combo |
| `Golf Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Golf Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `GrandSlam` | 2 | b2b-pup, fauna-shifu | — |
| `HIROSHIMA` | 2 | heavy-pentagon, heavy-weapons-8fvg-matrix | squarify |
| `HV150` | 2 | hv-ladder-50-to-1k, hvd-pbj-ppd | — |
| `HV_BEAR` | 2 | hv-fvg-gz1-og, proximity-gzi-hv | squarify |
| `HV_BULL` | 2 | hv-fvg-gz1-og, proximity-gzi-hv | squarify |
| `HotSpot` | 2 | hv-ladder-100-to-1k, hv-ladder-50-to-1k | — |
| `KRATOS` | 2 | heavy-pentagon, heavy-weapons-8fvg-matrix | squarify |
| `Kratos` | 2 | b2b-pup, fauna-shifu | — |
| `LONG_1` | 2 | heavy-uncap, heavy-weapons-8fvg-matrix | — |
| `LONG_2` | 2 | heavy-uncap, heavy-weapons-8fvg-matrix | — |
| `LSC Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `LSC Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `NEO_BEAR` | 2 | heavy-weapons-8fvg-matrix, squarify | — |
| `NEO_BULL` | 2 | heavy-weapons-8fvg-matrix, squarify | — |
| `OD Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `OD Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `Omega Long` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `PAF PPD B2B` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `PAF PUP B2B` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir | — |
| `PENTAGON` | 2 | heavy-pentagon, heavy-weapons-8fvg-matrix | squarify |
| `PPBear` | 2 | anish-50-1st-combo, anish-tb-foster | — |
| `PPBull` | 2 | anish-50-1st-combo, anish-tb-foster | — |
| `RVOL_1X_BEAR` | 2 | heavy-pentagon, heavy-weapons-8fvg-matrix | — |
| `RVOL_1X_BULL` | 2 | heavy-pentagon, heavy-weapons-8fvg-matrix | — |
| `ResistanceRejection` | 2 | yin-yang-displacement-pbj, yin-yang-og-mofo | — |
| `SHORT_1` | 2 | heavy-uncap, heavy-weapons-8fvg-matrix | — |
| `SHORT_2` | 2 | heavy-uncap, heavy-weapons-8fvg-matrix | — |
| `SupportRejection` | 2 | yin-yang-displacement-pbj, yin-yang-og-mofo | — |
| `SwingHigh` | 2 | yin-yang-displacement-pbj, yin-yang-og-mofo | — |
| `SwingLow` | 2 | yin-yang-displacement-pbj, yin-yang-og-mofo | — |
| `T1-buy` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables | — |
| `T1-sell` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables | — |
| `T2-buy` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables | — |
| `T2-sell` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables | — |
| `T3-buy` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables | — |
| `T3-sell` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables | — |
| `T3a-buy` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3a-sell` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3b-buy` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3b-sell` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3c-buy` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3c-sell` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3d-buy` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3d-sell` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3e-buy` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3e-sell` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3f-buy` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `T3f-sell` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `TRINITY_BEAR` | 2 | heavy-weapons-8fvg-matrix, squarify | — |
| `TRINITY_BULL` | 2 | heavy-weapons-8fvg-matrix, squarify | — |
| `zA-bear` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zA-bull` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zB-bear` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zB-bull` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zC-bear` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zC-bull` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zD-bear` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zD-bull` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zE-bear` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zE-bull` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zF-bear` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |
| `zF-bull` | 2 | vob-asym, vob-asym-ummmm-masterdir | — |

**123 shared root names across the suite.**

### Defined by exactly one family (alphabetical)

| Root name | Owner family | Referenced by |
|---|---|---|
| `AVALANCHE` | fauna-shifu | — |
| `B2B_DAYS_TRACKER` | squarify | — |
| `B2B_PPD` | squarify | ultra-combo |
| `B2B_PUP` | squarify | ultra-combo |
| `BEAR_GZI` | heavy-weapons-8fvg-matrix | — |
| `BEAR_HV` | heavy-weapons-8fvg-matrix | — |
| `BULL_GZI` | heavy-weapons-8fvg-matrix | — |
| `BULL_HV` | heavy-weapons-8fvg-matrix | — |
| `Bear U-Sub` | hvd-pbj-ppd-1939-masterdir | — |
| `BearishDisplacement` | yin-yang-displacement-pbj | — |
| `Bull U-Sub` | hvd-pbj-ppd-1939-masterdir | — |
| `BullishDisplacement` | yin-yang-displacement-pbj | — |
| `C10_KC_PIVOT_BEAR` | fauna-shifu | — |
| `C7_PIVOT_BULL` | fauna-shifu | — |
| `C8_PIVOT_BEAR` | fauna-shifu | — |
| `C9_KC_PIVOT_BULL` | fauna-shifu | — |
| `CONT_BEAR` | b2b-pup | — |
| `CONT_BULL` | b2b-pup | — |
| `CS1Bear` | b2b-pup | — |
| `CS1Bull` | b2b-pup | — |
| `CS2Bear` | b2b-pup | — |
| `CS2Bull` | b2b-pup | — |
| `Charge` | tnt-od | — |
| `Charge_BEAR` | b2b-pup | — |
| `Charge_BULL` | b2b-pup | — |
| `Continuous` | tnt-od | — |
| `D1_BEAR` | disp-4x | — |
| `D1_BULL` | disp-4x | — |
| `D2_BEAR` | disp-4x | — |
| `D2_BULL` | disp-4x | — |
| `D3_BEAR` | disp-4x | — |
| `D3_BULL` | disp-4x | — |
| `D4_BEAR` | disp-4x | — |
| `D4_BULL` | disp-4x | — |
| `DANTES_PEAK` | fauna-shifu | — |
| `DD` | heavy-uncap | — |
| `DDD` | heavy-uncap | — |
| `DDDD` | heavy-uncap | — |
| `DISP5_BEAR` | hvd-pbj-ppd | — |
| `DISP5_BULL` | hvd-pbj-ppd | — |
| `DISPBear` | b2b-pup | — |
| `DISPBull` | b2b-pup | — |
| `DISPLACEMENT_BEAR` | fauna-shifu | — |
| `DISPLACEMENT_BULL` | fauna-shifu | — |
| `DISP_BEAR` | hvd-pbj-ppd | squarify |
| `DISP_BULL` | hvd-pbj-ppd | squarify |
| `Density1` | tnt-od | — |
| `Density2` | tnt-od | — |
| `Density3` | tnt-od | — |
| `Dynamite` | tnt-od | — |
| `ES_BEAR` | ultra-combo | — |
| `ES_BULL` | ultra-combo | — |
| `FOSTER` | ultra-combo | — |
| `FOSTER_PBJ_WINDOW` | squarify | — |
| `GDR_BEAR` | ultra-combo | — |
| `GDR_BULL` | ultra-combo | — |
| `GG_BEAR` | ultra-combo | — |
| `GG_BULL` | ultra-combo | — |
| `GZ1_BEAR_FVG` | fauna-shifu | — |
| `GZ1_BULL_FVG` | fauna-shifu | — |
| `GapDown` | anish-50-1st-combo | — |
| `GapUp` | anish-50-1st-combo | — |
| `HOT_SPOT` | heavy-uncap | — |
| `HV100` | hv-ladder-100-to-1k | — |
| `HV200` | hv-ladder-100-to-1k | — |
| `HV250` | hv-ladder-50-to-1k | — |
| `HV300` | hv-ladder-100-to-1k | — |
| `HV400` | hv-ladder-100-to-1k | — |
| `HV50` | hv-ladder-50-to-1k | — |
| `HV5K` | hvd-pbj-ppd | — |
| `HV600` | hv-ladder-100-to-1k | — |
| `HV700` | hv-ladder-100-to-1k | — |
| `HV75` | hvd-pbj-ppd | — |
| `HV800` | hv-ladder-100-to-1k | — |
| `HV900` | hv-ladder-100-to-1k | — |
| `HVDBear` | b2b-pup | — |
| `HVDBull` | b2b-pup | — |
| `HVDPBJBear` | b2b-pup | — |
| `HVDPBJBull` | b2b-pup | — |
| `HVQ` | hvd-pbj-ppd | — |
| `HVY` | hvd-pbj-ppd | — |
| `HV_MILESTONE` | fauna-shifu | — |
| `Hiroshima` | b2b-pup | — |
| `KC_BREAKDOWN_LOWER` | fauna-shifu | — |
| `KC_BREAKOUT_UPPER` | fauna-shifu | — |
| `KC_CROSS_ABOVE_BASIS` | fauna-shifu | — |
| `KC_CROSS_BELOW_BASIS` | fauna-shifu | — |
| `LBWT_BEAR_CROSS` | ultra-combo | — |
| `LBWT_BULL_CROSS` | ultra-combo | — |
| `LONG_3` | heavy-uncap | — |
| `LONG_4` | heavy-uncap | — |
| `LONG_5` | heavy-uncap | — |
| `Long1` | b2b-pup | — |
| `MB_BEAR` | ultra-combo | — |
| `MB_BULL` | ultra-combo | — |
| `MOMENTUM1_LONG` | fauna-shifu | — |
| `MOMENTUM1_SHORT` | fauna-shifu | — |
| `NPM_CONS_BEAR` | squarify | — |
| `NPM_CONS_BULL` | squarify | — |
| `Napalm` | tnt-od | — |
| `Napalm_BEAR` | b2b-pup | — |
| `Napalm_BULL` | b2b-pup | — |
| `Omega-A` | hvd-pbj-ppd-2246-masterdir | — |
| `PBBear` | b2b-pup | — |
| `PBBull` | b2b-pup | — |
| `PBJBear` | b2b-pup | — |
| `PBJBull` | b2b-pup | — |
| `Pentagon` | b2b-pup | — |
| `RE_BEAR` | ultra-combo | — |
| `RE_BULL` | ultra-combo | — |
| `ROC_BEAR_PRIMITIVE` | ultra-combo | — |
| `ROC_BULL_PRIMITIVE` | ultra-combo | — |
| `RVOL1xBear` | b2b-pup | — |
| `RVOL1xBull` | b2b-pup | — |
| `RVOL1x_BEAR` | fauna-shifu | squarify |
| `RVOL1x_BULL` | fauna-shifu | squarify |
| `RVOLBear` | anish-tb-foster | — |
| `RVOLBull` | anish-tb-foster | — |
| `RetBearTNT` | b2b-pup | — |
| `RetBullTNT` | b2b-pup | — |
| `Return` | tnt-od | — |
| `Short1` | b2b-pup | — |
| `SuperTNT_BEAR` | b2b-pup | — |
| `SuperTNT_BULL` | b2b-pup | — |
| `TA_BEAR` | ultra-combo | — |
| `TA_BULL` | ultra-combo | — |
| `TB` | ultra-combo | — |
| `TIER1_OPENING_CONFLU_BULL` | squarify | — |
| `TIER2_OPENING_CONFLU_BULL` | squarify | — |
| `TNT` | tnt-od | — |
| `TNT2` | tnt-od | — |
| `TNT2_BEAR` | b2b-pup | — |
| `TNT2_BULL` | b2b-pup | — |
| `TNT_CONS_BEAR` | b2b-pup | — |
| `TNT_CONS_BULL` | b2b-pup | — |
| `TNT_RAW_BEAR` | b2b-pup | — |
| `TNT_RAW_BULL` | b2b-pup | — |
| `TR_BEAR` | ultra-combo | — |
| `TR_BULL` | ultra-combo | — |
| `UNIFIED_COMBO_BEAR` | squarify | — |
| `UNIFIED_COMBO_BULL` | squarify | — |
| `UU` | heavy-uncap | — |
| `UUBear` | b2b-pup | — |
| `UUBull` | b2b-pup | — |
| `UUU` | heavy-uncap | — |
| `UUUBear` | b2b-pup | — |
| `UUUBull` | b2b-pup | — |
| `UUUU` | heavy-uncap | — |
| `UUUUBear` | b2b-pup | — |
| `UUUUBull` | b2b-pup | — |
| `UnifiedBear` | b2b-pup | — |
| `UnifiedBull` | b2b-pup | — |
| `WBUSH_BEAR` | squarify | — |
| `WBUSH_BULL` | squarify | — |
| `WBUSH_NEUTRAL` | squarify | — |
| `WHALE_BEAR` | fauna-shifu | — |
| `WHALE_BULL` | fauna-shifu | — |
| `YY_BREAKDOWN` | fauna-shifu | — |
| `YY_BREAKOUT` | fauna-shifu | — |
| `YY_VALIDHIGH_SWING` | fauna-shifu | — |
| `YY_VALIDLOW_SWING` | fauna-shifu | — |
| `bear_MB` | e3-f2-cluster | — |
| `bear_RE` | e3-f2-cluster | — |
| `bear_TA` | e3-f2-cluster | — |
| `bull_MB` | e3-f2-cluster | — |
| `bull_RE` | e3-f2-cluster | — |
| `bull_TA` | e3-f2-cluster | — |
| `zA` | vob-ladder-watch | — |
| `zB` | vob-ladder-watch | — |
| `zC` | vob-ladder-watch | — |
| `zD` | vob-ladder-watch | — |
| `zE` | vob-ladder-watch | — |
| `zF` | vob-ladder-watch | — |

**173 root names defined by exactly one family.**

## Composites — Common Denominators

### Defined in multiple families (sorted by owner count desc)

| Composite name | # Owners | Owner families |
|---|---:|---|
| `2nd Floor` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `Aggregated Alert` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `FAUNA_BEAR` | 2 | heavy-uncap, ultra-combo |
| `FAUNA_BULL` | 2 | heavy-uncap, ultra-combo |
| `FOXTROT_BEAR` | 2 | fauna-shifu, hvd-pbj-ppd |
| `FOXTROT_BULL` | 2 | fauna-shifu, hvd-pbj-ppd |
| `Floor` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `Foster` | 2 | anish-50-1st-combo, anish-tb-foster |
| `GOLF_BEAR` | 2 | fauna-shifu, hvd-pbj-ppd |
| `GOLF_BULL` | 2 | fauna-shifu, hvd-pbj-ppd |
| `HW Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `HW Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `PAF_BEAR` | 2 | fauna-shifu, hvd-pbj-ppd |
| `PAF_BULL` | 2 | fauna-shifu, hvd-pbj-ppd |
| `Penthouse` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `Rooftop` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `SD Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `SD Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `SUPER Bear` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `SUPER Bull` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `SuperPPD` | 2 | anish-50-1st-combo, anish-tb-foster |
| `SuperPup` | 2 | anish-50-1st-combo, anish-tb-foster |
| `T3_bloomberg_alert` | 2 | vob-asym, vob-asym-ummmm-masterdir |
| `TB` | 2 | anish-50-1st-combo, anish-tb-foster |
| `Triple AND (Pipeline D)` | 2 | hvd-pbj-ppd-1939-masterdir, hvd-pbj-ppd-2246-masterdir |
| `VolumeHierarchy` | 2 | hv-ladder-100-to-1k, hv-ladder-50-to-1k |
| `ZONE_FORMATION_bloomberg_alert` | 2 | vob-asym, vob-asym-ummmm-masterdir |
| `alert_tier1_buy_payload` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `alert_tier1_sell_payload` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `alert_tier2_buy_payload` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `alert_tier2_sell_payload` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `alert_tier3_buy_payload` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `alert_tier3_sell_payload` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `any_t3` | 2 | vob-asym, vob-asym-ummmm-masterdir |
| `any_t3_alert` | 2 | vob-asym, vob-asym-ummmm-masterdir |
| `any_zone` | 2 | vob-asym, vob-asym-ummmm-masterdir |
| `any_zone_alert` | 2 | vob-asym, vob-asym-ummmm-masterdir |
| `bear_pool_total` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `bull_count / bear_count` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `bull_pool_total` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `comprehensive_emission_table` | 2 | vob-asym, vob-asym-ummmm-masterdir |
| `dom_bear_vol / dom_bear_pct` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `dom_bull_vol / dom_bull_pct` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `ema_trend_shadow` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `mutex_zone_lines` | 2 | vob-asym, vob-asym-ummmm-masterdir |
| `price_at_bull / price_at_bear` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `raw_tier_flags` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `zone_drawing_bear` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |
| `zone_drawing_bull` | 2 | vob-single-sens-no-tables, vob-single-sens-with-tables |

**49 shared composite names across the suite.**

## Per-family root/composite counts (sanity check)

| Family id | # Roots | # Composites | # Cross-indicator deps |
|---|---:|---:|---:|
| `anish-50-1st-combo` | 6 | 6 | 2 |
| `anish-tb-foster` | 10 | 14 | 3 |
| `b2b-pup` | 54 | 27 | 4 |
| `disp-4x` | 8 | 0 | 0 |
| `e3-f2-cluster` | 6 | 8 | 0 |
| `fauna-shifu` | 40 | 42 | 4 |
| `heavy-combo-toggles` | 0 | 3 | 31 |
| `heavy-pentagon` | 10 | 15 | 0 |
| `heavy-uncap` | 14 | 12 | 3 |
| `heavy-weapons-8fvg-matrix` | 24 | 8 | 10 |
| `hv-fvg-gz1-og` | 6 | 0 | 0 |
| `hv-ladder-100-to-1k` | 12 | 1 | 0 |
| `hv-ladder-50-to-1k` | 7 | 1 | 0 |
| `hvd-pbj-ppd` | 21 | 57 | 0 |
| `hvd-pbj-ppd-1939-masterdir` | 41 | 12 | 0 |
| `hvd-pbj-ppd-2246-masterdir` | 40 | 12 | 0 |
| `pb-pbj` | 4 | 0 | 0 |
| `proximity-gzi-hv` | 6 | 0 | 0 |
| `squarify` | 25 | 48 | 39 |
| `tnt-od` | 10 | 21 | 4 |
| `ultra-combo` | 26 | 49 | 26 |
| `vob-asym` | 25 | 18 | 3 |
| `vob-asym-ummmm-masterdir` | 25 | 9 | 0 |
| `vob-ladder-watch` | 6 | 9 | 2 |
| `vob-single-sens-no-tables` | 6 | 16 | 3 |
| `vob-single-sens-with-tables` | 6 | 16 | 3 |
| `yin-yang-displacement-pbj` | 12 | 14 | 4 |
| `yin-yang-og-mofo` | 6 | 0 | 0 |

**Total indicators: 28.** Source: `data/indicators.yaml` (regenerated by `tools/merge_extracts.py`).
