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
| 6 | hv-fvg-gz1-og ⭐   | `hv-fvg-gz1-og/versions/HV_FVG_GZ1_OG_v1.pine`                                          | b4FUu only                               | 10,811  | **Canonical HV/GZI/FVG engine.** proximity-gzi-hv is a stripped variant |
| 7 | hvd-pbj-ppd        | `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine`                           | b4FUu only                               | 109,787 | **PBJ/PPD/PB/Displacement** (Engine 6 implementation). pb-pbj is the isolated PB/PBJ canonical |
| 8 | pb-pbj ⭐          | `pb-pbj/versions/PB_PBJ_v1.pine`                                                        | this branch only                         | ~10,000 | **Canonical isolated PB/PBJ engine** (extracted from YY+D+PBJ). 4 roots all offset=0; OKEH Zoo + PB&J Filter + Supertrend |
| 9 | proximity-gzi-hv   | `proximity-gzi-hv/versions/PROXIMITY_GZI_HV_v1.pine`                                    | both                                     | 10,796  | Stripped variant of hv-fvg-gz1-og; parity-check target               |
| 10 | squarify (current) | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine`                                      | both                                     | 153,431 | 46 numbered composites; `SQUARIFY_ATOMS_v1` companion is sibling     |
| 11 | tnt-od             | `tnt-od/versions/TNT_Opening_Drive_OD_v3_2026-05-04.pine`                               | both                                     | 122,995 | Current per CHANGELOG; internally titled v2; predecessor renamed to `TNT_OD_v3_LEGACY_PRE_CONSOLIDATION.pine` in Stage 6.4 |
| 12 | ultra-combo       | `ultra-combo/versions/ULTRA_COMBO_v57_pine6.pine`                                       | b4FUu only                               | 49,013  | Pine v6 original; v5 port (`pine5`) kept as 1:1 logic mirror         |
| 13 | vob-asym          | `vob-asym/versions/VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine`                            | both                                     | 112,709 | VOB Asym T3×6 mutex                                                  |
| 14 | vob-ladder-watch  | `vob-ladder-watch/versions/VOB_LADDER_WATCH_v1.pine`                                                 | both                                     | 12,209  | Distinct from vob-asym; split into its own dir in Stage 6.5 |

**Total canonical Pine source**: ~720 KB across 14 files (12 original + pb-pbj + disp-4x added in Stage 7).

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
- `tnt-od/versions/TNT_OD_v3_LEGACY_PRE_CONSOLIDATION.pine` (148,437 — older despite v3 name)
- `tnt-od/versions/TNT_OD_v2.pine` (122,995 — same SHA as current)
- `tnt-od/versions/TNT_OD_v1.pine` (99,921 — legacy)
- `ultra-combo/versions/ULTRA_COMBO_v57_pine5.pine` (49,367 — v5 port, logic 1:1 with v6)

## Extraction outputs

Each Stage 1.1 agent writes its YAML chunk to `bible-input/extract-<family>.yaml`.
Stage 1.7 merges them all into `data/indicators.yaml`.
