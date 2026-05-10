# Ultra Combo v57 — extraction report (compact)

Source: `ultra-combo/versions/ULTRA_COMBO_v57_pine6.pine` · 1147 lines · Pine v6 (sibling `ULTRA_COMBO_v57_pine5.pine` is verified 1:1 logic) · title `"Ultra Combo v57"` (shorttitle `"ULTRA v57"`) · imports `TradingView/ta/7`

## Summary

Aggregator overlay re-implementing primitive signal definitions from PBJ/PB, F2/E3/FC cluster, RVOL Heavy Weapon, PUP/PPD, TB/Foster, ROC + LazyBear WaveTrend, displacement, FAUNA, GZ1/HV FVG, then composing ~30+ tier-2/tier-3 combos. Drives 30 plotshapes, 19 `alert()` calls, 15 `alertcondition()` calls.

## Roots

| Canonical | Source | Notes |
|---|---|---|
| `ultra-combo::MB` / `RE` / `TA` (FAUNA cores) | 99-101 (bull), 104-106 (bear); FAUNA copies 717-737 | Same primitives as `squarify::*` and `hvdpbjppd::*` — cross-ref. Defaults: ATR(14), body mult 1.6, range mult 2.2, body/range 0.7, vol mult 1.8 over SMA(volume,20). |
| `ultra-combo::GG` / `TR` / `ES` / `GDR` (FAUNA exclusions) | 722-730 (bull), 740-746 (bear) | Same exclusion family. |
| `ultra-combo::F2` | 209 (bull) / 296 (bear) | `sessBar==2 AND MB[0] AND MB[1]`. **NEW root in this file** per CHANGELOG. |
| `ultra-combo::E3` | 208 / 295 | `sessBar==3 AND ev[0]&[1]&[2]` where `ev = MB OR RE OR TA`. **NEW root.** |
| `ultra-combo::FC` (F2/E3 Cluster overlap) | 124-206 (bull) / 211-293 (bear) | "2-of-3 cluster indicators" align with overlapping price ranges in 20-bar window. **NEW root.** |
| `ultra-combo::TB` | 587-612 | After ≥5 consecutive bullPass days, 2-bar window opens; first bear-direction trigger fires TB / TB-PBJ / TB-PB. **NEW root.** Cross-ref candidate `hvdpbjppd::TB` if Anish TB Foster v6 indicator exists. |
| `ultra-combo::FOSTER` | 617-642 | Mirror of TB after ≥5 consecutive bearPass days. **NEW root.** |
| `ultra-combo::ROC` (sigROCBull/Bear) | 647-690 | Composite trigger: PBJ AND ROC-EMA + LazyBear WaveTrend conditions AND HW-hit AND directional close. Per CHANGELOG treated as single named root. **NEW root.** Internal mechanics (LazyBear WT, EMA crosses) are NOT roots. |
| Cross-refs (re-implemented locally): | | |
| `heavy-pentagon::*` (RVOL 1x, GS, MOAB, WTC, Hiroshima, Nagasaki) | 339-364 | Same threshold tables. |
| `hvdpbjppd::PBJ` / `PB` | 386-519 | Header line 367: "EXACT COPY FROM ANISH TB FOSTER v6". |
| `hv-fvg-gz1-og::GZI` / `HV_FVG` | 764-823 | Same 7-bar overlap, 5000/252/63 HV. |
| `b2b-pup::PUP` / `PPD` / `B2B_PUP` / `B2B_PPD` / `superPup` / `superPPD` | 539-579 | 3% body + 10-bar opp-color volume + Anish stack gating for Super flavors. |
| `hvdpbjppd::DISPLACEMENT` (sigDISPBull/Bear) | 692-698 | Range > 5σ stdev(100) AND directional FVG. |

## FAUNA (locked formula confirmed)

`FAUNA = (MB OR RE OR TA) AND NOT (GG OR TR OR ES OR GDR)`. Bull line 732, bear line 748. FAUNA defines its own `fMB_b`, `fRE_b`, `fTA_b` parallel copies (mathematically equivalent to root MB/RE/TA — flagged for redundancy review).

## Composites (selected — full list in agent transcript)

| Composite | Tier | Source | Composition | Plot offset |
|---|---|---|---|---|
| `ultra-combo::OPENER_BULL/BEAR` | 4 | 891-892 | `sessBar==1 AND (GZ1 OR HV) AND (HW-set OR PBJ OR ROC OR (1stPUP AND superPUP))` | default |
| `ultra-combo::THREE_BAR_BULL/BEAR` | 3 | 894-906 | `PBJ-in-3 AND (B2B-PUP-in-3 OR ≥2 PUPs-in-3)` | default |
| `ultra-combo::MEGA_BULL/BEAR` (gz1Mega, hvMega, gz1hvMega) | 4 | 884-889 | `(GZ1 OR HV OR both) AND anySuperBull AND PUP/PPD AND FAUNA AND DISP` | -1 |
| `ultra-combo::SUPER_B2B_DAYS_BULL/BEAR` | 4 | 916-918 | `anySuperBull AND f_hadSignalYesterday(anySuperBull)` | default |
| `ultra-combo::comboPBJ_F2_BULL/BEAR` | 2 | 828, 831 | `PBJ AND F2` | default |
| `ultra-combo::comboPBJ_E3_BULL/BEAR` | 2 | 829, 832 | `PBJ AND E3` | default |
| `ultra-combo::comboPBJ_CLUSTER_BULL/BEAR` | 2 | 830, 833 | `PBJ AND FC` | default |
| `ultra-combo::comboF2_CLUSTER_E3_BULL/BEAR` | 3 | 842-843 | `F2[1] AND FC[1] AND E3` | default |
| `ultra-combo::comboHW_ANYBULL/BEAR` | 3 | 873-874 | `anyHW AND (F2 OR E3 OR FC)` | default |
| `ultra-combo::comboGZHV_ANYBULL/BEAR` | 3 | 1038-1039 | `(HV OR GZ1) AND (sAnyBull or sAnyBull[1])` | -1 |
| `ultra-combo::FOSTER_HEAVY_BULL` / `TB_HEAVY_BEAR` | 3 | 908-911 | `anyFoster AND (ROC OR HW-set OR Super)` | default |
| `ultra-combo::scanTrigger` | 4 | 920 | `Super-PBJ OR Super-PB OR GS OR MOAB` | (alert-only) |

## v5 vs v6 verification

CHANGELOG claims 1:1 — VERIFIED. Differences are mechanical: `//@version` directive; `tv_ta.relativeVolume` import vs inline `ta.sma`; comma-chain split; method-style array calls. Critical signal lines byte-equivalent (sBullFC, sBullE3, sBullF2, sigBullPBJ, sigROCBull, sigFAUNABull, openerBull, threeBar_Bull all checked).

## Caveats

- Anish Stage 2/4 EMA stack (line 524-532) classified INTERNAL_MECHANIC here — never plotted/alerted standalone, only feeds superPup/superPPD/TB/Foster gating. Cross-indicator review required.
- Gap Up/Down NOT present as named root signals; only fGG_b/fGG_r exists as FAUNA exclusion.
- LazyBear WaveTrend internal to ROC root; do not promote.
- 4 PUP-family roots in this file: PUP, B2B PUP, superPUP/1stPUP, FAUNA-internal — bible should disambiguate.
