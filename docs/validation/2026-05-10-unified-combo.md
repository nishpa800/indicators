# Validation report — `Unified Combo`

_Skill: `detection-plot-validation` v1.1.0. Run on 2026-05-10. Path: docs/validation/2026-05-10-unified-combo.md._

## Summary

| Field | Value |
|---|---|
| Target | `csNew3_Bull` / `csNew3_Bear` (Unified Combo) |
| Aliases resolved | UNIFIED_COMBO_BULL, UNIFIED_COMBO_BEAR, csNew3, csNew3_Bull, csNew3_Bear, UC, unifiedComboBull, unifiedComboBear, unified_combo, UNIFIED_COMBO, sigUnifiedComboBull, sigUnifiedComboBear, csNew3Bull, csNew3Bear |
| Indicator families with occurrences | 5 (squarify, hvd-pbj-ppd, b2b-pup, path-a-loggers, fauna-shifu) |
| DEFINITION locations | **8** |
| REFERENCE / INPUT / PLOT / ALERT / COMMENT occurrences | 261 / 0 / 25 / 2 / 99 |
| Phase 2 verdicts | 21 pairs identical + **7 pairs SEMANTIC DRIFT** |
| Phase 3 path used | BLOCKED-NEEDS-TV-FIRING-SKILL (Path B inaccessible from this sandbox — realtime-indicators repo is on Anish's Mac, not pushed) |
| Phase 4 reconcile actions | YAML annotation only (no Pine source modification per standing approval) |
| Final verdict | **DRIFT-PENDING-TV-FIRING** |
| Stage-7 followups | TV-firing skill run to confirm which AND-shift is "true" Unified Combo |

## Phase 1 — Enumeration

### DEFINITIONS (8)

| # | Indicator | File | Line | Pine variable | Boolean (one-line excerpt) | YAML record? |
|---|---|---|---|---|---|---|
| 1 | squarify | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | 1257 | `csNew3_Bull` | `bool csNew3_Bull=csNew1_Bull and nz(csNew2_Bull[1]), bool csNew3_Bear=csNew1_Bear and nz(csNew2_Bear[1])` | ✓ `squarify::UNIFIED_COMBO_BULL/BEAR` at L1240-L1257 |
| 2 | squarify | `squarify/versions/SQUARIFY_ATOMS_v1.pine` | 1265 | `csNew3_Bull` | (identical to #1) | ✗ MISSING |
| 3 | squarify | `squarify/versions/SQUARIFY_v1.pine` | 1183 | `csNew3_Bull` | (identical to #1) | ✗ MISSING |
| 4 | squarify | `squarify/versions/SQUARIFY_v2.pine` | 1257 | `csNew3_Bull` | (identical to #1) | ✗ MISSING |
| 5 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` | 968 | `csNew3_Bull` | (identical to #1) | ✗ MISSING |
| 6 | hvd-pbj-ppd | **`hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine`** | **1052** | `csNew3_Bull` | **`bool csNew3_Bull=csNew1_Bull and csNew2_Bull, bool csNew3_Bear=csNew1_Bear and csNew2_Bear`** | ✗ MISSING — ⚠️ DRIFTED (same-bar AND, missing `nz(...[1])`) |
| 7 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` | 942 | `csNew3_Bull` | (identical to #1) | ✗ MISSING |
| 8 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | 968 | `csNew3_Bull` | (identical to #1) | ✗ MISSING |

### Other occurrences (count by classification)

| Indicator | DEFINITION | REFERENCE | INPUT | PLOT | ALERT | COMMENT |
|---|---:|---:|---:|---:|---:|---:|
| squarify (4 versions) | 4 | 184 | 0 | 19 | 0 | 80 |
| hvd-pbj-ppd (4 versions) | 4 | 65 | 0 | 0 | 0 | 6 |
| b2b-pup | 0 | 3 | 0 | 6 | 2 | 0 |
| path-a-loggers | 0 | 9 | 0 | 0 | 0 | 0 |
| fauna-shifu | 0 | 0 | 0 | 0 | 0 | 13 |

### Orphans in YAML

_(none)_

### Missings (in Pine, not in YAML)

| Pine variable | Indicator | File | Line |
|---|---|---|---|
| `csNew3_Bull/_Bear` | squarify | `SQUARIFY_ATOMS_v1.pine` | 1265 |
| `csNew3_Bull/_Bear` | squarify | `SQUARIFY_v1.pine` | 1183 |
| `csNew3_Bull/_Bear` | squarify | `SQUARIFY_v2.pine` | 1257 |
| `csNew3_Bull/_Bear` | hvd-pbj-ppd | `HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` | 968 |
| `csNew3_Bull/_Bear` | hvd-pbj-ppd | `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | 1052 |
| `csNew3_Bull/_Bear` | hvd-pbj-ppd | `HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` | 942 |
| `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | hvd-pbj-ppd | (same) | 968 |

The squarify versions other than 46_v2 are LEGACY (per bible MANIFEST); their missings are expected. The hvd-pbj-ppd missings reflect that csNew3 isn't yet in the bible YAML extract for that indicator (Stage 1 extracted the canonical's surface plots, not internal helpers like csNew3).

## Phase 2 — Static diff

8 DEFINITION locations → 28 pairs to diff. Result: 21 pairs `identical`, 7 pairs `SEMANTIC DRIFT`. Every drift pair is between location #6 (THE_ONLY_ONE) and one of the other 7 locations.

| Pair group | Verdict | Evidence |
|---|---|---|
| Locations #1, #2, #3, #4, #5, #7, #8 ↔ each other (21 pairs) | `identical` | All seven have `csNew3_Bull = csNew1_Bull and nz(csNew2_Bull[1])`. Bytes match after normalisation. |
| Location #6 ↔ each of #1, #2, #3, #4, #5, #7, #8 (7 pairs) | **`semantic-drift`** | #6 has `csNew3_Bull = csNew1_Bull and csNew2_Bull` — **missing the `nz(csNew2_Bull[1])` shift**. The other 7 use lagged AND (FVG combo on bar[0], Matrix combo on bar[1]); #6 uses same-bar AND. |

### Drift finding #1 (canonical artifact)

See `docs/validation/2026-05-10-unified-combo-drift-1.md` for the full side-by-side.

**Summary**: 7-of-8 majority — the lagged-AND interpretation is the historical implementation (preserved across all 4 squarify versions AND 3 of 4 hvd-pbj-ppd versions). THE_ONLY_ONE.pine — the file currently designated canonical per `tnt-od/VETTING.md` precedent — is the OUTLIER.

The lagged-AND semantics matter: Unified Combo fires when FVG Combo fires on the current bar AND Matrix Combo fired on the PREVIOUS bar. Same-bar AND would require both to fire simultaneously, which is structurally rarer and conceptually different.

## Phase 3 — TV firing

**Path used**: BLOCKED-NEEDS-TV-FIRING-SKILL.

**Reason**: Path B (Python ports via `realtime-indicators` repo) is inaccessible from this sandbox session — the repo lives at `~/code/anish/realtime-indicators` on Anish's Mac and has not been pushed to GitHub (per Anish's 2026-05-10 Stage 7.5-7.8c handoff comment). Path A (chart-side TV MCP) is intentionally not available in this skill per v1.1 (moved to spinout skill `detection-plot-tv-firing`).

**Followup**: when Anish is at his desk with TradingView open and the Path A loggers loaded:

1. Invoke `detection-plot-tv-firing` skill on this target
2. Pull fire-bar sets from each of the 8 DEFINITION locations (load each canonical Pine on a chart; query the logger)
3. Determine which AND-shift behaviour Anish's chart history confirms is correct
4. Update this report's Phase 3 section + Phase 4 reconcile

**Why this isn't a blocker for the bible**: the semantic-drift is already CONFIRMED by Phase 2 static analysis. TV firing only resolves "which of the two implementations is the canonical one" — it doesn't change the fact that drift exists. Phase 4 below proceeds with the YAML annotation regardless.

## Phase 4 — Reconcile (autonomous per standing approval)

Per skill v1.1 `STANDING_APPROVAL.md`: semantic drift no longer pauses for user decision. The skill DOCUMENTS the drift in:

1. **The validation report** (this file)
2. **The drift-finding artifact** (`docs/validation/2026-05-10-unified-combo-drift-1.md`)
3. **`bible-input/extract-hvd-pbj-ppd.yaml`** annotation (adds `csNew3_Bull` and `csNew3_Bear` records with `variant_of: squarify::UNIFIED_COMBO_BULL` and `variant_kind: semantic-drift-pending-tv-firing` for THE_ONLY_ONE.pine specifically; marks the other 3 hvd-pbj-ppd versions as `identical-to: squarify::UNIFIED_COMBO_BULL`)

**No Pine source modification** in this commit. Per the standing approval's version-control mantra: if Anish later confirms the lagged-AND is canonical (via TV firing skill), the fix path is to CREATE A NEW VERSIONED FILE `HVDPBJPPD_2026-05-10_THE_ONLY_ONE_v2_csNew3_FIX.pine` documenting the change — never edit THE_ONLY_ONE in place.

**Generators that will run after this report commits** (auto-regen hooks not yet enabled per `docs/HOOKS_PROPOSAL.md` — running manually):

- `python3 tools/merge_extracts.py` — regen `data/indicators.yaml` + `.json`
- `python3 tools/build_lineage_cards.py` — regen lineage cards
- `python3 tools/build_docs.py` — regen the human docs

## Final verdict

**DRIFT-PENDING-TV-FIRING**

- Semantic drift confirmed (Phase 2): THE_ONLY_ONE.pine has same-bar AND; every other version has lagged AND.
- 7-of-8 majority strongly suggests lagged AND is canonical, but TV firing is the authoritative resolver.
- No Pine source modified per standing approval.
- YAML annotated with `variant_of:` flag.
- Drift-finding artifact written for future TV-firing-skill cross-reference.

## Stage-7 followups

- [ ] Run `detection-plot-tv-firing` skill on `csNew3_Bull` / `csNew3_Bear` when Anish is at his desk
- [ ] If TV firing confirms lagged-AND is canonical: create `HVDPBJPPD_THE_ONLY_ONE_v2_csNew3_FIX.pine` per standing-approval version-control mantra
- [ ] If TV firing confirms same-bar-AND is canonical: file a CHANGELOG entry in `squarify/CHANGELOG.md` documenting the historical drift; create `SQUARIFY_46_v3.pine` with the fix
- [ ] Resolve `b2b-pup` REFERENCEs (3 occurrences) — they reference `csNew3` from somewhere; figure out which DEFINITION they bind to
- [ ] Update `docs/redundancy.md` (b) with this canonical Unified Combo drift entry

## Provenance

- Skill version: detection-plot-validation v1.1.0
- Run started: 2026-05-10T~20:30Z (this session)
- Phase 1 method: `tools/validate_detection_plot.py` (deterministic harness)
- Phase 2 method: pairwise diff of normalized boolean LHS=RHS extractions (no subagents — 8 DEFINITIONs is below the multi-agent threshold)
- Phase 3 method: BLOCKED (Path B inaccessible; Path A intentionally excluded from this skill)
- Phase 4 method: YAML annotation only; no Pine modification
- Parent agent: Claude (Opus 4.7, 1M context) in the sandbox session
