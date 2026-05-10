# Indicators Bible — Index

Authoritative reference for every named detection plot across the quant-fund indicator suite. Source of truth: `data/indicators.yaml` (with `data/indicators.json` as machine-readable mirror).

## Quick links

- **Master root catalog:** [`docs/roots.md`](docs/roots.md) — every named primitive across 12 indicators (78 roots total).
- **Master composite catalog:** [`docs/composites.md`](docs/composites.md) — every composite by tier (~57 top-level, plus chains).
- **Drift / redundancy table:** [`docs/redundancy.md`](docs/redundancy.md) — composition drift, namespace collisions, internal-implementation drift candidates.
- **Glossary:** [`docs/glossary.md`](docs/glossary.md) — every cross-cutting concept defined exactly once.
- **Version-control diagnosis:** [`docs/version-control-diagnosis.md`](docs/version-control-diagnosis.md) — file-system issues to clean up in Stage 6.
- **Per-indicator visual trees:** [`docs/visual-trees/`](docs/visual-trees/) — ASCII dependency trees, one per indicator.
- **Lineage cards (auto-generated):** [`docs/lineage/`](docs/lineage/) — 35 top-level-composite traceability cards. [`docs/lineage/INDEX.md`](docs/lineage/INDEX.md).
- **YAML / JSON source of truth:** [`data/indicators.yaml`](data/indicators.yaml) | [`data/indicators.json`](data/indicators.json).
- **Lineage card generator:** [`tools/build_lineage_cards.py`](tools/build_lineage_cards.py) — re-emits all cards from YAML.
- **Per-indicator agent extraction reports:** [`bible-input/agent-reports/`](bible-input/agent-reports/) — one report per indicator file.

## Operating model (short version)

- **Root** = the least-common-denominator name humans use to refer to a signal. Calculated independently and decoupled from every other root in lifecycle stage 2. Internal complexity (Supertrend, Zoo MA, EMA crosses, ATR/σ multipliers, raw `highest()`/`lowest()`, FVG geometry) is hidden inside root names and never decomposed.
- **Composite** = a signal whose definition uses at least one root or lower-tier composite by name. Evaluated in lifecycle stage 5. Composites read post-offset boolean outputs of roots; never inspect root internals.
- **Tier** = depth from root. Tier 0 = root; tier 1 = composite-of-roots; tier 2 = composite-of-tier-1; etc.
- **Provenance** = the indicator family that canonically owns the signal. Canonical name format: `<provenance>::<NAME>`.
- **Bar lifecycle** (stages 2 → 3 → 4 → 5 → 6 → 7): see `docs/glossary.md` for full definition.

## Indicator inventory (13 distinct, 12 families)

| # | Family | Title | File | Branch | Lines |
|---|---|---|---|---|---|
| 1 | `anish-50-1st-combo` | Anish 50% 1st Combo (NR) | `anish-50-1st-combo/versions/ANISH_50_1ST_COMBO_v1.pine` | b4FUu | 182 |
| 2 | `b2b-pup` | B2B PUP Combined 4.32 | `b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine` | both | 1259 |
| 3 | `heavy-combo-toggles` | Heavy Combo Toggles | `heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine` | both | 268 |
| 4 | `heavy-pentagon` ⭐ | Heavy PENTAGON (canonical RVOL) | `heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine` | b4FUu | 444 |
| 5 | `hv-fvg-gz1-og` ⭐ | HV FVG GZ1 OG (canonical HV/GZI/FVG) | `hv-fvg-gz1-og/versions/HV_FVG_GZ1_OG_v1.pine` | b4FUu | 253 |
| 6 | `hvdpbjppd` | HVDPBJPPD THE_ONLY_ONE (canonical PBJ/PPD) | `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | b4FUu | 1767 |
| 7 | `proximity-gzi-hv` | Proximity GZI HV (alias of HV FVG GZ1 OG) | `proximity-gzi-hv/versions/PROXIMITY_GZI_HV_v1.pine` | both | 253 |
| 8 | `squarify` | Squarify 46 v2 (top-level fund signal) | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | both | 2622 |
| 9 | `tnt-od` | TNT OD v2 (dated 05-04) / v3 (dated 05-08) | `tnt-od/versions/TNT_Opening_Drive_OD_v3_2026-05-04.pine` + `TNT_OD_v3.pine` | both | 1802 / 2150 |
| 10 | `ultra-combo` | Ultra Combo v57 | `ultra-combo/versions/ULTRA_COMBO_v57_pine6.pine` (+ pine5 port) | b4FUu | 1147 |
| 11 | `vob-asym` | VOB Asym T3×6 v8 | `vob/versions/VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine` | both | 1473 |
| 12 | `vob-ladder` | VOB Ladder Watch v1 | `vob/versions/VOB_LADDER_WATCH_v1.pine` | both | 215 |

## Provenance map (canonical owners)

| Family | Owns canonical roots |
|---|---|
| `heavy-pentagon` ⭐ | SAAB, KRATOS, BULL_RVOL_1X, BEAR_RVOL_1X, GRAND_SLAM, MOAB, PENTAGON, WTC, HIROSHIMA, NAGASAKI; plus 15 Heavy Combo composites (HEAVY_YIN_YANG, HEAVY_NAGASAKI, HEAVY_NAGASAKI_VOL, HEAVY_TRIDENT, NEUTRAL_HEAVY_X2 × Bull/Bear/Neutral) |
| `hv-fvg-gz1-og` ⭐ | FVG_BULL_RAW, FVG_BEAR_RAW, GZI_BULL, GZI_BEAR, HV_BULL, HV_BEAR |
| `hvdpbjppd` | PBJ_BULL/BEAR, PB_BULL/BEAR, DISP_BULL/BEAR (+ DISP2/3 variants), MATRIX_NUMBER, LONG1/2, SHORT1/2, BOOM_HUNTER_OMEGA, PING_PONG_BULL/BEAR, HV75/150/500/1000, HVD_BULL/BEAR |
| `pocket-pivot` (`anish-50-1st-combo` is oldest definition site) | PUP, PPD |
| `anish-50-1st-combo` (tentative — may be cross-ref to standalone Anish-Stage indicator) | ANISH_BULL_PASS, ANISH_BEAR_PASS |
| `tnt-od` | TNT_RAW_BULL/BEAR, OD, NAPALM_BULL/BEAR, CHARGE_BULL/BEAR, RET_BULL_TNT, RET_BEAR_TNT, TNT2_BULL/BEAR, SUPER_TNT_BULL/BEAR, CONT_BULL/BEAR, DISP_BULL_ENGINE_1 |
| `vob-asym` | VOB_CROSS, BULL_ZONE_PUSH, BEAR_ZONE_PUSH, ZONE_INVALIDATION, T3_SUPER_BUY, T3_SUPER_SELL |
| `ultra-combo` | F2, E3, FC, TB, FOSTER, ROC |
| `fauna` (distributed — Stage 6 should designate one canonical) | MB, RE, TA, GG, TR, ES, GDR |

## Critical drifts to reconcile (Stage 6)

1. **HIGH PRIORITY** — `anyBearPent` (Penthouse) collides with `heavy-pentagon::PENTAGON` namespace. Rename to `anyBear2F`.
2. **CRITICAL** — `csNew3` (Unified Combo): same-bar AND in HVDPBJPPD canonical, but **lagged AND** in Squarify and B2B PUP. Pick one definition.
3. **HIGH** — Byte-diff PBJ internal mechanics (Supertrend / VWMA / EMA crosses) across HVDPBJPPD / B2B PUP / Squarify / TNT-OD / Ultra Combo. Designate canonical, mirror everywhere, lock with checksum.
4. **HIGH** — Byte-diff RVOL ladder threshold tables across 7 indicators. `heavy-pentagon` is canonical (verified verbatim by `heavy-combo-toggles`). B2B PUP comment "Pre Mythos thresholds" suggests divergence.
5. **MEDIUM** — Reconcile GZI proximity (`gziProximity=6` canonical vs `gz1_dist=7` in 3 downstream indicators).
6. **MEDIUM** — Reconcile DISP σ-multiplier (`i_std_min=3.0` in HVDPBJPPD canonical and Squarify, `5.0` in B2B PUP / TNT-OD / Ultra Combo).
7. **MEDIUM** — Designate canonical FAUNA owner (currently distributed across 6 indicators).
8. **LOW** — File-system cleanup (line-ending dupes, TNT-OD v2/v3 naming, VOB folder split, proximity-gzi-hv alias decision).

Full drift table with line-level details: [`docs/redundancy.md`](docs/redundancy.md).

## The full arc — staging

| Stage | Output | Status |
|---|---|---|
| **1. Bible of roots & composites** | This commit. Hierarchical inventory across all 13 indicators. Roots, composites, tiers, offsets, provenance, parameter defaults, redundancy table. Human + machine readable. **No Pine code edited.** | ✅ DONE |
| **2. Test indicators built from roots only** | 3-4 lean Pine indicators that plot only roots with `<provenance>::<root>` naming. Each plot includes a comment block linking to the bible entry. | Pending — separate plan |
| **3. Manual TradingView verification** | Run each test indicator on TV via the connected TradingView MCP, visually confirm each root fires when expected. | Pending |
| **4. Composite validation** | When roots align on a bar, confirm the dependent composite fires. When it doesn't, diagnose: offset / threshold drift / definition mismatch. | Pending — recurring during optimisation |
| **5. Diagnostic SOP** | Written `docs/sop/` covering root verification, composite verification, drift triage, offset triage. | Pending — authored alongside Stage 4 cases |
| **6. Treatment** | File rename/move/archive. VOB folder split. Stub deletion. Drift reconciliation (rename `anyBearPent` → `anyBear2F`, etc.). Mirror folder structure to local + iCloud Drive. | Pending — last; only after bible is trusted |

## How the bible was built

1. Pulled 4 b4FUu-only indicators (`anish-50-1st-combo`, `heavy-pentagon`, `hv-fvg-gz1-og`, `ultra-combo`) and the canonical `HVDPBJPPD_THE_ONLY_ONE.pine` into the working branch.
2. Dispatched **12 extraction agents in parallel** — one per indicator family — each producing a structured-markdown extraction report following a strict schema. Reports saved to `bible-input/agent-reports/`.
3. Hand-authored `data/indicators.yaml` from the 12 agent reports (no LLM autogeneration of structured fields).
4. Derived `data/indicators.json` via single Python one-liner; verified `yaml.safe_load(yaml_file) == json.load(json_file)`.
5. Hand-authored `docs/roots.md`, `docs/composites.md`, `docs/redundancy.md`, `docs/version-control-diagnosis.md`, `docs/glossary.md`, and 12 ASCII visual trees in `docs/visual-trees/`.
6. Wrote `tools/build_lineage_cards.py` to auto-generate per-top-level-composite lineage cards from YAML; emitted 35 cards + `docs/lineage/INDEX.md`.
7. Wrote 3 durable preference files to memory: `feedback_dual_output.md`, `feedback_indicator_agent_strategy.md`, `feedback_root_vs_composite.md`.

## Verification

- ✅ YAML parses (`python3 -c "import yaml; yaml.safe_load(open('data/indicators.yaml'))"` exits 0).
- ✅ JSON parses (`python3 -c "import json; json.load(open('data/indicators.json'))"` exits 0).
- ✅ Cross-format equality (`yaml.safe_load(...) == json.load(...)`).
- ✅ Lineage cards regenerable (`python3 tools/build_lineage_cards.py` emits 35 cards + INDEX.md).
- ✅ All 12 agent reports archived in `bible-input/agent-reports/`.
- 13 indicators • 78 roots • 57 composites • 2 chains • 11 redundancy entries.
