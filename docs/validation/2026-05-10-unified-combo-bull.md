# Validation report — `Unified Combo Bull`

_Skill: `detection-plot-validation` v1.1.0. Run on 2026-05-10. Path: docs/validation/2026-05-10-unified-combo-bull.md._
_Supersedes / extends: `docs/validation/2026-05-10-unified-combo.md` (bull-side isolation + correction of b2b-pup DEFINITION miscount)._

## Summary

| Field | Value |
|---|---|
| Target | `csNew3_Bull` / `det_UnifiedBull` / `squarify::UNIFIED_COMBO_BULL` (Unified Combo Bull) |
| Aliases resolved | `UNIFIED_COMBO_BULL`, `csNew3_Bull`, `UnifiedBull`, `det_UnifiedBull`, `CS3_UNIFIED_BULL`, `Combo Bull`, `UC` (bull direction), `Uni+B2B Bull` |
| Indicator families with occurrences | 4 (squarify, hvd-pbj-ppd, b2b-pup, path-a-loggers) |
| DEFINITION locations (bull) | **9** (prior run found 8 — corrected; b2b-pup L783 is a DEFINITION, not a REFERENCE) |
| REFERENCE / INPUT / PLOT / ALERT / COMMENT occurrences (bull-side) | ~190 / 0 / 12 / 1 / ~60 |
| Phase 2 verdicts | 28 pairs identical + **8 pairs SEMANTIC DRIFT** (all involve either THE_ONLY_ONE same-bar AND, or b2b-pup variable-name alias) |
| Phase 3 path used | BLOCKED-NEEDS-TV-FIRING-SKILL |
| Phase 3 agreement-set count | N/A |
| Phase 3 drift-set count | N/A |
| Phase 4 reconcile actions | YAML annotation (carried forward from parent run); b2b-pup DEFINITION miscount corrected |
| Final verdict | **DRIFT-PENDING-TV-FIRING** |
| Stage-7 followups | TV-firing skill; THE_ONLY_ONE fix if lagged-AND confirmed; b2b-pup YAML line range correction |

---

## Phase 1 — Enumeration

### DEFINITIONS (9, bull direction)

| # | Indicator | File | Line | Pine variable | Boolean (one-line excerpt) | YAML record? |
|---|---|---|---|---|---|---|
| 1 | squarify | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | L1257 | `csNew3_Bull` | `bool csNew3_Bull=csNew1_Bull and nz(csNew2_Bull[1])` | ✓ `squarify::UNIFIED_COMBO_BULL` at L1240-L1257 |
| 2 | squarify | `squarify/versions/SQUARIFY_ATOMS_v1.pine` | L1265 | `csNew3_Bull` | identical to #1 | ✗ MISSING (legacy version) |
| 3 | squarify | `squarify/versions/SQUARIFY_v1.pine` | L1183 | `csNew3_Bull` | identical to #1 | ✗ MISSING (legacy version) |
| 4 | squarify | `squarify/versions/SQUARIFY_v2.pine` | L1257 | `csNew3_Bull` | identical to #1 | ✗ MISSING (alias of canonical 46_v2) |
| 5 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` | L968 | `csNew3_Bull` | identical to #1 | ✗ MISSING |
| 6 | hvd-pbj-ppd | **`hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine`** | **L1052** | `csNew3_Bull` | **`bool csNew3_Bull=csNew1_Bull and csNew2_Bull`** — ⚠️ DRIFTED (same-bar AND, missing `nz(...[1])`) | ✗ MISSING + DRIFTED |
| 7 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` | L942 | `csNew3_Bull` | identical to #1 | ✗ MISSING |
| 8 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | L968 | `csNew3_Bull` | identical to #1 | ✗ MISSING |
| **9** | **b2b-pup** | **`b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine`** | **L783** | **`det_UnifiedBull`** | **`bool det_UnifiedBull=det_CS1Bull and nz(det_CS2Bull[1])`** | ✓ `b2b-pup::UnifiedBull` at L782-L783 — **prior run incorrectly classified as REFERENCE; this is a DEFINITION** |

**Correction note**: The parent run (`2026-05-10-unified-combo.md`) recorded b2b-pup as having 0 DEFINITION occurrences and 3 REFERENCEs. Line 783 is an assignment (`bool det_UnifiedBull = ...`) — it is a DEFINITION. The 3 references it counted were downstream usages (L996, L997 `det_S8_bull`, and the `nz(det_UnifiedBull[1])` usage). This is corrected here.

### OTHER OCCURRENCES (bull-side, count by classification)

| Indicator | DEFINITION | REFERENCE | INPUT | PLOT | ALERT | COMMENT |
|---|---:|---:|---:|---:|---:|---:|
| squarify (4 versions) | 4 | ~180 | 0 | 12 | 0 | ~60 |
| hvd-pbj-ppd (4 versions) | 4 | ~60 | 0 | 4 | 0 | 4 |
| b2b-pup | **1** | 3 | 0 | 3 | 1 | 0 |
| path-a-loggers | 0 | 9 | 0 | 0 | 0 | 0 |

### Orphans in YAML

_(none)_

### Missings (in Pine, not in YAML)

| Pine variable | Indicator | File | Line | Note |
|---|---|---|---|---|
| `csNew3_Bull` | squarify | `SQUARIFY_ATOMS_v1.pine` | L1265 | Legacy — expected missing |
| `csNew3_Bull` | squarify | `SQUARIFY_v1.pine` | L1183 | Legacy — expected missing |
| `csNew3_Bull` | squarify | `SQUARIFY_v2.pine` | L1257 | Alias of canonical 46_v2 |
| `csNew3_Bull` | hvd-pbj-ppd | `HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` | L968 | Needs YAML record |
| `csNew3_Bull` | hvd-pbj-ppd | `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L1052 | ⚠️ Needs YAML + drift annotation |
| `csNew3_Bull` | hvd-pbj-ppd | `HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` | L942 | Needs YAML record |
| `csNew3_Bull` | hvd-pbj-ppd | `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | L968 | Needs YAML record |

### Aliases resolved

```
- csNew3_Bull              # primary Pine variable (squarify, hvd-pbj-ppd)
- det_UnifiedBull          # b2b-pup's alias for the same concept
- squarify::UNIFIED_COMBO_BULL   # YAML canonical id
- b2b-pup::UnifiedBull     # YAML id in b2b-pup family
- hvd-pbj-ppd::CS3_UNIFIED_BULL  # YAML id in hvd-pbj-ppd family
- UC                       # colloquial (user request, CHANGELOG, comments)
- Unified Combo Bull       # human label (plot text, alert strings)
- Combo Bull               # plot text in hvd-pbj-ppd ("COMBO" label)
- CS3_BULL                 # alternative colloquial
- Uni+B2B Bull             # compound form used in b2b-pup plot labels
```

---

## Phase 2 — Static diff

9 DEFINITION locations → 36 pairs. Pairs among #1/#2/#3/#4/#5/#7/#8 are identical (21 pairs). Pairs between #6 and all others are semantic-drift (8 pairs). Pairs between #9 (b2b-pup `det_UnifiedBull`) and #1-#8 are cosmetic-drift (8 pairs — identical lagged-AND logic, different variable names).

| Pair group | Verdict | Evidence |
|---|---|---|
| Locs #1–#5, #7–#8 ↔ each other (21 pairs) | `identical` | All have `csNew3_Bull = csNew1_Bull and nz(csNew2_Bull[1])`. Bytes match after normalization. |
| Loc #6 ↔ locs #1–#5, #7–#9 (8 pairs) | **`semantic-drift`** | #6 has `csNew3_Bull = csNew1_Bull and csNew2_Bull` — same-bar AND. All others use lagged AND `nz(csNew2_Bull[1])`. |
| Loc #9 ↔ locs #1–#5, #7–#8 (7 pairs) | `cosmetic-drift` | `det_UnifiedBull = det_CS1Bull and nz(det_CS2Bull[1])`. Lagged-AND structure matches #1-#5/#7/#8 exactly; only variable names differ (`det_CS1Bull` vs `csNew1_Bull`, `det_CS2Bull` vs `csNew2_Bull`). |
| Loc #9 ↔ loc #6 (1 pair) | **`semantic-drift`** | #9 is lagged-AND; #6 is same-bar AND. |

**Total non-identical pairs**: 15 — 7 cosmetic + 8 semantic.

### Drift findings

- **Drift #1** (critical, semantic): `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` L1052 uses same-bar AND. See `docs/validation/2026-05-10-unified-combo-drift-1.md`.
- **Drift #2** (informational, cosmetic): `b2b-pup` L783 uses `det_CS1Bull`/`det_CS2Bull` variable names instead of `csNew1_Bull`/`csNew2_Bull`. Same logic, different local namespace. No action needed.

---

## Phase 3 — TV firing

| Path used | Why |
|---|---|
| BLOCKED-NEEDS-TV-FIRING-SKILL | Path B (Python realtime-indicators) unavailable in this sandbox. Path A (TV MCP chart-side) belongs to the spinout `detection-plot-tv-firing` skill. |

| Location | Fire-bar count | Query window | Status |
|---|---|---|---|
| All 9 DEFINITION locations | N/A | N/A | BLOCKED |

**Bar-set algebra**: N/A — blocked.

**Drift-bar diagnoses**: pending TV firing skill.

---

## Phase 4 — Reconcile

| Finding | Proposed action | User approved | Applied | Commit SHA |
|---|---|---|---|---|
| Drift #1: THE_ONLY_ONE same-bar AND (semantic-drift) | YAML annotation (`variant_kind: semantic-drift-pending-tv-firing`) — carried from parent run. No Pine modification until TV firing confirms which side is canonical. | Standing approval (autonomous) | Annotated in `extract-hvd-pbj-ppd.yaml` (parent run) | — |
| Drift #2: b2b-pup variable-name cosmetic-drift | No action — `cosmetic-drift` with different local namespace is expected and acceptable. The YAML already records `b2b-pup::UnifiedBull` with correct boolean summary. | Standing approval (no-action) | n/a | — |
| b2b-pup DEFINITION miscount correction | Correct this report's enumeration table (done above). Parent run's table at `2026-05-10-unified-combo.md` should be noted as having the b2b-pup DEFINITION misclassification. | Standing approval (autonomous) | Documented here | — |

**Generators run**: Not required this pass (no new YAML edits beyond the parent run's annotation).

- `python3 tools/merge_extracts.py` — deferred (no extract edit this pass)
- `python3 tools/build_lineage_cards.py` — deferred
- `python3 tools/build_docs.py` — deferred
- YAML == JSON — deferred

---

## Final verdict

**DRIFT-PENDING-TV-FIRING**

- Semantic drift confirmed (Phase 2): `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` L1052 uses same-bar AND; 7-of-8 other DEFINITION locations (plus b2b-pup) use lagged AND (`nz(csNew2_Bull[1])`).
- b2b-pup variable-name cosmetic-drift is informational only.
- Prior run's b2b-pup DEFINITION miscount corrected: b2b-pup L783 (`det_UnifiedBull=det_CS1Bull and nz(det_CS2Bull[1])`) is a DEFINITION, bringing total DEFINITION count from 8 to 9.
- No Pine source modified.
- TV firing blocked pending `detection-plot-tv-firing` skill run at Anish's desk.

---

## Stage-7 followups

- [ ] Run `detection-plot-tv-firing` skill on `csNew3_Bull` to confirm lagged-AND vs same-bar-AND is correct
- [ ] If lagged-AND confirmed: create `HVDPBJPPD_2026-05-10_THE_ONLY_ONE_v2_csNew3_FIX.pine` (per standing-approval version-control mantra); update MANIFEST + CHANGELOG
- [ ] If same-bar-AND confirmed: create `SQUARIFY_46_v3.pine` with same-bar AND fix; document in `squarify/CHANGELOG.md`
- [ ] Add missing hvd-pbj-ppd YAML records (4 versions of csNew3_Bull) to `bible-input/extract-hvd-pbj-ppd.yaml`
- [ ] Flag the parent run `2026-05-10-unified-combo.md` table row for b2b-pup as having a DEFINITION miscount (for record hygiene)

---

## Provenance

- Skill version: detection-plot-validation v1.1.0
- Run started: 2026-05-10
- Run ended: 2026-05-10
- Wall-clock duration: ~8 minutes
- Subagents dispatched: Phase 1 = 0, Phase 2 = 0, Phase 3 = 0 (9 DEFINITIONs below 12-pair subagent threshold after correction)
- Parent agent: Claude (Sonnet 4.6) — bull-side isolation + b2b-pup DEFINITION correction pass
- Based on: `docs/validation/2026-05-10-unified-combo.md` (parent run by Opus 4.7 1M)
- Drift artifacts: `docs/validation/2026-05-10-unified-combo-drift-1.md` (unchanged from parent run)
