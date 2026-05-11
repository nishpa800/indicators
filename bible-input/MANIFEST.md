# bible-input MANIFEST

Per-file branch provenance for the Stage-1 root/composite extraction. The bible
ingests the **union** of canonical Pine sources from `origin/main` and
`origin/claude/add-txt-indicator-format-b4FUu`, deduplicated by SHA.

The actual Pine sources live at their natural paths in `/home/user/indicators/`
(every b4FUu-only directory was merged into the working tree on this branch).
This manifest is the authoritative pointer to the *canonical* file per
indicator family — the one Stage 1 extracts from.

| # | Indicator family   | Canonical file                                                                          | Branch origin                            | Bytes   | Notes                                                                 |
|---|--------------------|------------------------------------------------------------------------------------------|------------------------------------------|---------|-----------------------------------------------------------------------|
| 1 | anish-50-1st-combo | `anish-50-1st-combo/versions/ANISH_50_1ST_COMBO_v1.pine`                                | b4FUu only                               | 8,543   | Pine v6, non-repainting                                              |
| 2 | b2b-pup            | `b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine`                               | both                                     | 78,589  | Current per CHANGELOG; v4.32 sibling kept for diff                   |
| 3 | disp-4x            | `disp-4x/versions/DISP_4X_v1.pine`                                                      | this branch only                         | ~5,000  | 4 independent displacement engines; 8 roots (D1-D4 × Bull/Bear) all offset=-1; stack 4 panes for 16 strength views |
| 4 | heavy-combo-toggles | `heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine`                              | both                                     | 14,346  | Lifts 5 base + 15 directional combos verbatim from heavy-pentagon    |
| 5 | heavy-pentagon ⭐  | `heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine`                                        | b4FUu only                               | 25,160  | **Canonical RVOL engine.** Owns SAAB/Kratos/RVOL1x/GS/MOAB/Pentagon/WTC/Hiroshima/Nagasaki + 15 Heavy Combo composites |
| 6 | heavy-uncap        | `heavy-uncap/versions/HEAVY_UNCAP_v1.pine`                                              | this branch only                         | ~30,000 | Comprehensive RVOL toolkit — adds 14 new roots (Hybrid Momentum LONG 1-5/SHORT 1-2, RVOL sequences UU/UUU/UUUU/DD/DDD/DDDD, Hot Spot calendar) + 12 new composites (B2B 2x SAAB/Kratos/Bull1x/Bear1x, B2B Mid Bull/Bear, Consec Disp 2+/3+ bull/bear, FAUNA label-based). Locally re-implements heavy-pentagon RVOL ladder (verified byte-identical). |
| 7 | hv-fvg-gz1-og ⭐   | `hv-fvg-gz1-og/versions/HV_FVG_GZ1_OG_v1.pine`                                          | b4FUu only                               | 10,811  | **Canonical HV/GZI/FVG engine.** proximity-gzi-hv is a stripped variant |
| 8 | hvd-pbj-ppd        | `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine`                           | b4FUu only                               | 109,787 | **PBJ/PPD/PB/Displacement** (Engine 6 implementation). pb-pbj is the isolated PB/PBJ canonical |
| 9 | pb-pbj ⭐          | `pb-pbj/versions/PB_PBJ_v1.pine`                                                        | this branch only                         | ~10,000 | **Canonical isolated PB/PBJ engine** (extracted from YY+D+PBJ). 4 roots all offset=0; OKEH Zoo + PB&J Filter + Supertrend |
| 10 | proximity-gzi-hv   | `proximity-gzi-hv/versions/PROXIMITY_GZI_HV_v1.pine`                                    | both                                     | 10,796  | Stripped variant of hv-fvg-gz1-og; parity-check target               |
| 11 | squarify (current) | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine`                                      | both                                     | 153,431 | 46 numbered composites; `SQUARIFY_ATOMS_v1` companion is sibling     |
| 12 | tnt-od             | `tnt-od/versions/TNT_Opening_Drive_OD_v3_2026-05-04.pine`                               | both                                     | 122,995 | Internally titled v2; bible extraction tagged to this file. `versions/TNT_OD_v3.pine` (2150 lines, internally v3 with T1 RELAY/STACK + new gate + HCT/UC inline + 5 disp engines) is **pending vetting** — see `tnt-od/VETTING.md`. Stage 6.4 LEGACY_PRE_CONSOLIDATION rename was wrong and was reverted on 2026-05-10. |
| 13 | ultra-combo       | `ultra-combo/versions/ULTRA_COMBO_v57_pine6.pine`                                       | b4FUu only                               | 49,013  | Pine v6 original; v5 port (`pine5`) kept as 1:1 logic mirror         |
| 14 | vob-asym          | `vob-asym/versions/VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine`                            | both                                     | 112,709 | VOB Asym T3×6 mutex                                                  |
| 15 | vob-ladder-watch  | `vob-ladder-watch/versions/VOB_LADDER_WATCH_v1.pine`                                                 | both                                     | 12,209  | Distinct from vob-asym; split into its own dir in Stage 6.5 |

**Total canonical Pine source**: ~750 KB across 15 files (12 original + pb-pbj + disp-4x + heavy-uncap added in Stage 7).

## 2026-05-10 Master Directory ingest — pending-vetting families + variants

Per `docs/master-directory-delta-2026-05-10.md`. None of these is labelled
"canonical." Stage 1 extraction queued; canonical determination waits on
Stage 3 (TV verification).

### New families (5)

| # | Family            | File                                                                          | Pine | Lines | Status                  |
|---|-------------------|-------------------------------------------------------------------------------|------|------:|-------------------------|
| 16 | `hv-ladder`       | `hv-ladder/versions/HV_LADDER_50_TO_1K_v1.pine`                              | v5   |   196 | pending Stage-1 extract |
| 16 | `hv-ladder`       | `hv-ladder/versions/HV_LADDER_100_TO_1K_v1.pine`                             | v5   |   227 | pending Stage-1 extract |
| 17 | `anish-tb-foster` | `anish-tb-foster/versions/ANISH_TB_FOSTER_AIRBUD_LEPROSY_ENHANCED_v1.pine`   | v5   |   704 | pending Stage-1 extract |
| 18 | `heavy-weapons`   | `heavy-weapons/versions/HEAVY_WEAPONS_8FVG_MATRIX_COMBOS_NO_PENTAGON_v1.pine`| v5   |   489 | pending Stage-1 extract |
| 19 | `fauna-shifu`     | `fauna-shifu/versions/FAUNA_SHIFU_JUMBO_CIA_1ST_PUP_v1.pine`                 | v5   |  2338 | pending Stage-1 extract |
| 20 | `vob-single-sens` | `vob-single-sens/versions/VOB_SINGLE_SENS_WITH_TABLES_v1.pine`               | v6   |   414 | pending Stage-1 extract |
| 20 | `vob-single-sens` | `vob-single-sens/versions/VOB_SINGLE_SENS_NO_TABLES_NO_EMISSION_v1.pine`     | v6   |   415 | pending Stage-1 extract |

### New sibling variants inside existing families (3)

| Family        | Variant file                                                           | Lines | Notes                                                                                                  |
|---------------|------------------------------------------------------------------------|------:|--------------------------------------------------------------------------------------------------------|
| `hvd-pbj-ppd` | `hvd-pbj-ppd/versions/HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine`   |  2246 | 133 KB — larger than current `THE_ONLY_ONE` (109 KB). Pending vetting.                                  |
| `hvd-pbj-ppd` | `hvd-pbj-ppd/versions/HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine`   |  1939 | Same line count as repo's `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` but with Tier-1 input defaults flipped (Bear UUUU/UUU/Bull UU/Omega/Alpha Strike). Pending vetting. |
| `vob-asym`    | `vob-asym/versions/VOB_Asym_T3x6_FROM_MASTERDIR_ummmm_2026-05-10.pine` |  1473 | Title `+ Claude ummmm`; plotshape locations/shapes for T3 buy/sell differ from repo v8. Pending vetting. |

Bible family count after this ingest: **15 → 20**.

## 2026-05-10 secondary ingest — yin-yang + e3-f2-cluster (2 more families)

Three additional Pine sources added later same day. Anish flagged that yin-yang
or ping-pong may have been the lineage ancestor of the "floor / rooftop /
penthouse / 2nd floor" concepts, and that the E3/F2 cluster build was
size-reduced by ~58% and may have root corruption. All three ingested
verbatim; canonical determination still pending TV verification.

### New families (2)

| # | Family            | File                                                                          | Pine | Lines | Status                  | Notes                                                                                                             |
|---|-------------------|-------------------------------------------------------------------------------|------|------:|-------------------------|-------------------------------------------------------------------------------------------------------------------|
| 21 | `yin-yang`       | `yin-yang/versions/YIN_YANG_OG_MOFO_v1.pine`                                  | **v6** |  148 | pending vetting          | **Pine v6 violates v5-only rule** — flagged for migration. 6 roots (SwingHigh/Low, Breakout, Breakdown, S/R Rejection). |
| 21 | `yin-yang`       | `yin-yang/versions/YIN_YANG_DISPLACEMENT_PBJ_v8.pine`                         | v5   |   617 | pending vetting          | YY + Disp + PBJ combo. 10 roots (6 YY + 2 Disp + 2 PBJ); 14 composites (2-way + 3-way Swing/Disp/PBJ combos). PB/PBJ are LOCALLY redefined, NOT pulled from hvd-pbj-ppd. |
| 22 | `e3-f2-cluster`  | `e3-f2-cluster/versions/E3_F2_CLUSTER_BULL_BEAR_58PCT_REDUCTION_v1.pine`      | v5   |   405 | **pending corruption check** | Title says "58% reduction"; suspected root corruption. 6 atomic roots (MB/RE/TA × bull/bear), 8 composites (FC Cluster / E3 / F2 × bull/bear/Any). Asymmetric thresholds (bull 0.1 vs bear 0.5) and bear-side double-gating documented as candidate corruption. |

Bible family count after this ingest: **20 → 22** (28 indicator records including variants).

### "Floor / rooftop / penthouse / 2nd floor" lineage search — NEGATIVE in yin-yang

Anish's recollection: those four concepts may have started in yin-yang or
ping-pong. The extraction agent searched both yin-yang files (148 + 617
lines). **No mention** of "floor", "rooftop", "penthouse", "2nd floor",
"second floor", or "ping pong" as named primitives. The hypothesis stands
but the source isn't yin-yang. Likely candidate: hvd-pbj-ppd or fauna-shifu
(both reference Ping Pong as an internal helper).

## Predecessor / variant files (kept for byte-diff in Stage 1.5)

- `b2b-pup/versions/B2B_PUP_v4.32.pine` — DELETED in Stage 6.3 (was byte-equivalent to Combined except CRLF/LF; verified by md5 after `tr -d '\r'`)
- `hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` (123,396 — predecessor of THE_ONLY_ONE)
- `hvd-pbj-ppd/versions/HVDPBJPPD_v1.pine` — DELETED in Stage 6.2 (was 10-line stub)
- `squarify/versions/SQUARIFY_v2.pine` (141,004 — legacy)
- `squarify/versions/SQUARIFY_v1.pine` (138,138 — legacy)
- `squarify/versions/SQUARIFY_ATOMS_v1.pine` (151,246 — atoms-exposed sibling)
- `squarify/backtests/SQUARIFY_v2_BT.pine` (143,882)
- `squarify/backtests/SQUARIFY_v2_STATS.pine` (153,431 — same SHA as 46_v2)
- `squarify/backtests/parse_stats_logs.py` (7,774 — Python tool, not Pine)
- `tnt-od/versions/TNT_OD_v3.pine` (148,437 — actual v3 with T1 RELAY/STACK + new conditional gate + inline HCT + inline UC + 5 displacement engines; pending vetting before `LATEST.txt` flip)
- `tnt-od/versions/TNT_OD_v2.pine` (122,995 — predecessor of v3)
- `tnt-od/versions/TNT_OD_v1.pine` (99,921 — legacy)
- `ultra-combo/versions/ULTRA_COMBO_v57_pine5.pine` (49,367 — v5 port, logic 1:1 with v6)

## Extraction outputs

Each Stage 1.1 agent writes its YAML chunk to `bible-input/extract-<family>.yaml`.
Stage 1.7 merges them all into `data/indicators.yaml`.
