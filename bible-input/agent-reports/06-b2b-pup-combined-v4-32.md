# B2B PUP Combined v4.32 — extraction report

Source: `b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine` · 1259 lines · Pine v5 · title `"B2B PUP Combined 4.32"` · imports `TradingView/ta/7 as tv_ta`

## Summary

Monolithic overlay that locally re-implements 8 detection engines (A: PUP/PPD, B: FAUNA, C: Displacement, D: PBJ, E: RVOL/Pentagon, F: HV+D, G: TNT/Napalm/Charge/CONT, H: Combo Sets / Long1 / UU). Engines feed a "DETECTION COMBINATION LAYER" that builds 18 numbered B2B-PUP composites (S1–S18) plus 2 standalone combo-density plots (S19/S20). Master gate `First Bar Only`, aggregator alerts, 38 plotshapes terminate the pipeline.

Counts: 17+ root cross-refs, 20 numbered composites (S1–S20, no S7), 38 plotshapes (19 bull + 19 bear), 38 `alert()` calls (no `alertcondition`).

## Roots (all locally re-implemented; provenance is OTHER indicators)

All roots in this file are **cross-refs** — re-implemented for self-contained use but provenance lies elsewhere:

| Local name | Canonical owner | Source line | Plain-English |
|---|---|---|---|
| `det_PUP` / `det_PPD` | `pocket-pivot::*` (likely Anish 50% 1st Combo or HVDPBJPPD) | 73-79 | Pocket Pivot up/down: % up-move > threshold AND volume > highest opposite-color volume in lookback. Defaults: `pp_barSize=3.0%`, `pp_lookback=10`. |
| `det_FAUNABull` / `det_FAUNABear` | `squarify::FAUNA` (canonical root has dedicated atom) | 85-114 | Composite of 7 hardcoded family rules (MB/RE/GG/TA + exclusions TR/ES/GDR). Hardcoded thresholds 1.6×ATR, 2.2×ATR, 0.7 body-ratio, 1.8×AvgVol. |
| `det_DISPBull` / `det_DISPBear` | `hvdpbjppd::DISPLACEMENT` | 119-128 | Prior-bar range > N×stdev with 3-bar FVG on bar[0]. Defaults: `disp_type="Open to Close"`, `disp_len=100`, `disp_mult=5.0`. Engine offset documented as -1. |
| `det_PBJBull` / `det_PBJBear` | `hvdpbjppd::PBJ` (likely THE_ONLY_ONE) | 134-261 (full sub-engine) | Lowest-low (or highest-high) over lookback breaks EMA-based ATR band with volume confirmation, after base-MA cross sets approached level. Defaults: VWMA len=5, Supertrend ATR=10/mult=2.0, MA=20, ATR=14, HH/LL=25, ATR mult=3.0, vol period=20, vol mult=0.1. **Internal Supertrend/VWMA/EMA crosses are mechanics, not roots.** |
| `det_PBBull` / `det_PBBear` | `hvdpbjppd::PB` | 262-263 | Cross-after-approach of bull/bear level created by PBJ engine (non-PBJ branch). |
| `sig_SAAB`, `sig_Kratos`, `sig_RVOL1xB`, `sig_RVOL1xR`, `sig_GS`, `sig_MOAB`, `sig_Pentagon`, `sig_WTC`, `sig_Hiroshima`, `sig_Nagasaki` | `heavy-pentagon::*` | 268-301 | RVOL-tier classifications using normalised price + TradingView relativeVolume against TF-conditional thresholds (saab/1x/gs/wtc/hiro). Nagasaki = new ATH volume. Defaults: `rv_avgLen=30`, `rv_smaLen=20`. **CHANGELOG comment "Pre Mythos thresholds" L276** suggests potential drift vs heavy-pentagon canonical — flag for byte-diff. |
| `det_HVDBull` / `det_HVDBear` | `hvdpbjppd::HVD` | 306-325 | HV-rank bar (volume[1] tied for highest over 50/100/200/500/1000 OR new max ever) coincident with Displacement. Engine offset -1. |
| `det_bullTNTraw` / `det_bearTNTraw` | `tnt-od::TNT_RAW` | 343-494 | Token-coincidence (volume-cross + swing-cross + finer-swing zones) inside confirmed overlap with RSI/EMA-slope filters. Defaults: `tnt_SENS=100`, `tnt_SWING_LEN=10`, `tnt_DISP_STD_X=5`, `tnt_SUDDEN_PROX=3`, `tnt_MAX_ZONES=30`, `tnt_RET_PCT=100.0`. |
| `det_bullNapalm` / `det_bearNapalm` | `tnt-od::NAPALM` | 569-585 | TNT-internal-displacement bar that occurs while at least one active opposing TNT zone has its level beyond prior bar's wick. |
| `det_bullCharge` / `det_bearCharge` | `tnt-od::CHARGE` | 587-624 | TNT-internal-displacement bar violating active opposing ChargeLevel; v4.32 fix pushes new same-direction ChargeLevel (low[1] for bull, high[1] for bear) to maintain alternating ladder. |
| `det_retBullTNT` / `det_retBearTNT` | `tnt-od::RETURN_TO_TNT` | 539-562 | First retrace into previously-confirmed TNT zone by `tnt_RET_PCT` depth, with close re-protecting level. |
| `det_bullTNT2` / `det_bearTNT2` (TNT 2.0) | `tnt-od::TNT_2` | 626-666 | ≥2 same-direction TNT-family events (raw/Napalm/effective-Charge) within event log. |
| `det_superTNTbull` / `det_superTNTbear` | `tnt-od::SUPER_TNT` | 626-666 | Raw TNT same bar as opposing Charge. |
| `det_Long1` / `det_Short1` | `squarify::LONG1` / `SHORT1` | 786-790 | TV relativeVolume both regular (>7) and cumulative (>3.5) with directional body and ≥0.60 body ratio. |
| `gz_bullHV` / `gz_bullGZI` / `gz_bearHV` / `gz_bearGZI` | `hv-fvg-gz1-og::*` | 704-753 | FVG with gap > running avg pct gap; HV when volume[1] ties 252 or 63-bar high; GZI when overlapping prior FVG within 7 bars. **Note: 7-bar overlap window vs. canonical OG's `gziProximity=6` — drift candidate.** |
| `bullMatrix_neo` / `bullMatrix_trinity` (and bear) | `squarify::MATRIX_NEO` / `MATRIX_TRINITY` | 772-775 | Matrix bar = `volume == ta.highest(volume, 67)`. Neo = matrix bar with FAUNA same direction. Trinity = matrix bar without FAUNA but directional body. |

## Composites (S1–S20, no S7; plus intermediate CS1/CS2/CS3, B2B HV+D, B2B Napalm, CONT, UU/UUU/UUUU)

Defined intermediates (used as operands for S-numbered composites):

| Composite | Tier | Source | Composition |
|---|---|---|---|
| `b2b-pup::B2B_PUP` (`det_b2bPUP`) | 1 | 978 | `det_PUP AND nz(det_PUP[1])` |
| `b2b-pup::B2B_PPD` (`det_b2bPPD`) | 1 | 978 | `det_PPD AND nz(det_PPD[1])` |
| `b2b-pup::CS1_BULL` (FVG Combo) | 2 | 756-767 | `(gz_bullHV OR gz_bullGZI) AND body% AND (SAAB[1] OR RVOL1xB[1] OR GS[1] OR Pentagon[1] OR WTC[1] OR Hiro[1] OR Naga[1])` |
| `b2b-pup::CS2_BULL` (Matrix Combo) | 2 | 770-780 | `matrix_any AND body% AND (SAAB OR RVOL1xB OR GS OR Pentagon OR WTC OR Hiro OR Naga)` |
| `b2b-pup::CS3_UNIFIED_COMBO_BULL` | 3 | 783 | `det_CS1 AND det_CS2[1]` — FVG-combo this bar AND Matrix-combo prior bar |
| `b2b-pup::B2B_HVD_BULL` (`det_B2BHVDBull`) | 2 | 328 | `HVDBull AND HVDBull[1]` |
| `b2b-pup::B2B_HVD_PBJ_BULL` (`det_B2BHVDPBJBull`) | 3 | 330 | `B2BHVDBull AND (PBJBull[1] OR PBJBull[2])` |
| `b2b-pup::B2B_NAPALM_BULL` (`det_b2bBullNapalm`) | 2 | 697 | `bullNapCons AND bullNapCons[1]` where `bullNapCons = Napalm OR Charge` |
| `b2b-pup::CONT_BULL` (`det_contBull`) | 3 | 674 | 3-clause OR: Charge after Return; raw/2.0 TNT after recent Charge; Charge after recent TNT/TNT2 — gated by `tnt_SUDDEN_PROX=3` |
| `b2b-pup::UU` / `UUU` / `UUUU` (and DD/DDD/DDDD) | 3 | 846-951 | 2/3/4-bar streak of qualifying RVOL bars with at least one of A-F Squarify pathways hitting plus _ok TF/threshold gate |

S1–S20 numbered composites (all with bull and bear variants; only bull listed for brevity):

| ID | Tier | Source | Plot offset | Composition |
|---|---|---|---|---|
| `b2b-pup::S1_B2B_PUP_BULL` | 1 | 1023; plot 1047 | 0 | `det_b2bPUP AND gates` |
| `b2b-pup::S2_BULL` (B2B+FAUNA) | 2 | 1024; plot 1049 | 0 | `det_b2bPUP AND FAUNA[0] AND FAUNA[1]` |
| `b2b-pup::S3_BULL` (B2B+DISP/HVD) | 2 | 1025; plot 1051 | -1 | `(det_PUP[1] AND det_PUP[2]) AND ((DISPBull AND DISPBull[1]) OR (HVDBull AND HVDBull[1]))` |
| `b2b-pup::S4_BULL` (B2B+FAU+DISP/HVD) | 3 | 1026; plot 1053 | -1 | `S3 AND FAUNA[1] AND FAUNA[2]` |
| `b2b-pup::S5_BULL` (B2B+SAAB) | 2 | 1027; plot 1055 | 0 | `det_b2bPUP AND directional-RVOL combo` |
| `b2b-pup::S6_BULL` (Any B2B+PBJ) | 3 | 1028; plot 1057 | -1 | `(anyB2B_nd AND (PBJ[0] OR PBJ[1] OR HVDPBJ)) OR (S3_any AND PBJ[1..2] OR HVDPBJ[1]) OR (S4_any AND ...)` |
| (S7 intentionally absent) | – | – | – | – |
| `b2b-pup::S8_BULL` (UC+B2B PUP) | 3 | 1029; plot 1059 | -1 | `(det_b2bPUP AND det_UnifiedBull) OR (S3_any AND (UnifiedBull[0] OR [1]))` |
| `b2b-pup::S9_BULL` (Uni Combo + B2B PUP) | 3 | 1030; plot 1061 | -1 | `(det_b2bPUP AND (s9_combo[0] OR [1])) OR (S3_any AND (s9_combo[1] OR [2]))` where `s9_combo = det_UC2 OR det_FMU` |
| `b2b-pup::S10_BULL` (L1 B2B + B2B PUP) | 2 | 1031; plot 1063 | 0 | `(Long1 AND Long1[1]) AND (det_b2bPUP OR det_b2bPUP[1])` |
| `b2b-pup::S11_BULL` (FVG/L1 + B2B PUP) | 2 | 1032; plot 1065 | -1 | `det_b2bPUP AND (det_CS1Bull OR det_Long1 OR det_Long1[1])` |
| `b2b-pup::S12_BULL` (UU + B2B PUP) | 3 | 1033; plot 1067 | 0 | `det_b2bPUP AND (anyUU OR anyUU[1])` where `anyUU = UU OR UUU OR UUUU` |
| `b2b-pup::S13_BULL` (B2B Napalm + B2B PUP) | 3 | 1034; plot 1069 | 0 | `det_b2bPUP AND (det_b2bBullNapalm OR det_b2bBullNapalm[1])` |
| `b2b-pup::S14_BULL` (CONT + B2B PUP) | 3 | 1035; plot 1071 | 0 | `det_b2bPUP AND (det_contBull OR det_contBull[1])` |
| `b2b-pup::S15_BULL` (TNT + B2B PUP) | 3 | 1036; plot 1073 | 0 | `det_b2bPUP AND (det_bullTNT OR det_bullTNT[1])` |
| `b2b-pup::S16_BULL` (NPM + B2B PUP) | 2 | 1037; plot 1075 | -1 | `det_b2bPUP AND (det_bullNapCons OR det_bullNapCons[1])` |
| `b2b-pup::S17_BULL` (B2B HV+D + B2B PUP) | 3 | 1038; plot 1077 | -1 | `det_b2bPUP AND (det_B2BHVDBull OR det_B2BHVDBull[1])` |
| `b2b-pup::S18_BULL` (B2B HV+D+PBJ + B2B PUP) | 4 | 1039; plot 1079 | -1 | `det_b2bPUP AND (det_B2BHVDPBJBull OR det_B2BHVDPBJBull[1])` |
| `b2b-pup::S19_UC2_BULL` | 4 | 1040; plot 1083 | -1 | `≥2 Unified-Combo hits (FVG-combo AND Matrix-combo same visual bar) within 2 bars` |
| `b2b-pup::S20_FMU_BULL` | 4 | 1041; plot 1086 | -1 | `≥2 hits of (FVG-combo OR Matrix-combo OR Unified) within 2 bars` |

## Drift vs `B2B_PUP_v4.32.pine` (sibling)

**Zero signal-level drift.** Normalised diff (`tr -d '\r'`) is empty. Only difference: line endings (CRLF in Combined, LF in v4.32). md5 differs (`9327c895` vs `9151c531`) but content is byte-identical post-normalisation. Stage 6 should delete one and keep one with consistent line endings.

## Caveats

- No `alertcondition()` calls — uses Pine `alert()` runtime calls (38 of them, lines 1175-1259) in Bloomberg-style `BULL|<flag>|<+joined tags>` aggregator path or per-fired-Sx individual messages.
- S7 is intentionally absent in numbering.
- 7-bar GZI overlap window here vs canonical OG's `gziProximity=6` — drift candidate; reconcile.
- "Pre Mythos thresholds" comment on RVOL block — drift vs heavy-pentagon canonical possible.
