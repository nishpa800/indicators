# Validation report — `FLOOR_BULL`

_Skill: `detection-plot-validation` v1.0.0. Run on 2026-05-10. Path: docs/validation/2026-05-10-floor-bull.md._

## Summary

| Field | Value |
|---|---|
| Target | `FLOOR_BULL` |
| Aliases resolved | `FLOOR_BULL`, `anyBullFloor`, `fire_BullFloor`, `floor_sq`, `S4_FLOOR`, `S4 FLOOR`, `Floor`, `BullFloor` |
| Indicator families with occurrences | 2 (hvd-pbj-ppd, squarify) |
| DEFINITION locations | 2 canonical (anyBullFloor in hvd-pbj-ppd; floor_sq in squarify) + 6 legacy/sibling copies (same boolean) |
| REFERENCE / INPUT / PLOT / ALERT / COMMENT occurrences | REFERENCE: ~327 (hvd-pbj-ppd ≈148, squarify ≈148+31); PLOT: 2; ALERT: 2; INPUT: 2 (show_BullFloor toggles) |
| Phase 2 verdicts | 0 identical (as full S4_FLOOR); 0 cosmetic; 0 ipsf-default; 0 ipsf-asym; **1 semantic drift** (enrichment variant) |
| Phase 3 path used | Path B — partial (hvd-pbj-ppd Python port has `any_bull_floor` implemented; squarify port stubs floor_sq) |
| Phase 3 agreement-set count | N/A — Path B partial; squarify floor_sq blocked |
| Phase 3 drift-set count | N/A |
| Phase 4 reconcile actions | 1 (YAML tag `variant_of` on squarify::S4_FLOOR — pending user approval) |
| Final verdict | **DRIFT-PENDING-USER** |
| Stage-7 followups | (1) User ratifies canonical direction; (2) squarify YAML gets `variant_of:` tag; (3) squarify Python port un-stubs floor_sq after Ping-Pong SR engine is ported |

---

## Phase 1 — Enumeration

Prior Phase-1 YAML exists at `docs/validation/2026-05-10-floor-family-phase1.yaml` (54 Pine files scanned). This report incorporates those findings and extends with Bible YAML cross-check.

### DEFINITIONS

| # | Indicator | File | Line | Pine variable | Boolean (excerpt) | YAML record? |
|---|---|---|---|---|---|---|
| 1 | hvd-pbj-ppd | `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L1239–L1241 | `anyBullFloor` | `conf AND bull_pp AND sigBullPBJ AND bull_hw_slot` | ✓ `hvd-pbj-ppd::FLOOR_BULL` |
| 2 | squarify | `SQUARIFY_46_v2_2026-05-04.pine` | L1349–L1351 (base), L2156 (enriched) | `anyBullFloor` / `floor_sq` | base identical to #1; `floor_sq = anyBullFloor AND oneOfThese AND cb1_pass_floor` | ✓ `squarify::S4_FLOOR` (but missing `variant_of:` tag) |
| 3 | squarify (legacy) | `SQUARIFY_v2.pine` | L1351 | `anyBullFloor` | byte-identical to #1 | ✗ MISSING (legacy file; no separate YAML record needed — points to canonical) |
| 4 | squarify (legacy) | `SQUARIFY_v1.pine` | L1277 | `anyBullFloor` | byte-identical to #1 | ✗ MISSING (legacy; same note) |
| 5 | squarify (sibling) | `SQUARIFY_ATOMS_v1.pine` | L1359 | `anyBullFloor` | byte-identical to #1 | ✗ MISSING (atoms sibling; same note) |
| 6 | hvd-pbj-ppd (masterdir) | `HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` | L977 | `anyBullFloor` | byte-identical to #1 | ✗ MISSING — pending-vetting family |
| 7 | hvd-pbj-ppd (masterdir) | `HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` | L951 | `anyBullFloor` | byte-identical to #1 | ✗ MISSING — pending-vetting family |
| 8 | hvd-pbj-ppd (predecessor) | `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | L977 | `anyBullFloor` | byte-identical to #1 | ✗ MISSING (predecessor; not a canonical family member) |

**Notes on DEFINITION count:** Rows 3–5 are legacy/sibling versions of the squarify family — the anyBullFloor boolean in those files is byte-identical to the canonical SQUARIFY_46_v2 (#2). They do NOT represent a different composition. Rows 6–8 are pending-vetting variants; their boolean is also byte-identical to #1.

### OTHER OCCURRENCES

| Indicator | DEFINITION | REFERENCE | INPUT | PLOT | ALERT | COMMENT |
|---|---:|---:|---:|---:|---:|---:|
| hvd-pbj-ppd (canonical) | 1 | ~148 | 1 (show_BullFloor) | 1 (fire_BullFloor plotshape L1358) | 0 | 4 |
| squarify (canonical) | 2 (base + enriched) | ~148 | 1 (en_4 toggle) | 1 (floor_sq plotshape L2230) | 1 (alertcondition "FLOOR") | 6 |

### Orphans in YAML

_(none)_

### Missings (in Pine, not in YAML)

| Pine variable | Indicator | File | Note |
|---|---|---|---|
| `anyBullFloor` / `floor_sq` | squarify (v2, v1, ATOMS) | legacy versions | Legacy files; canonical record `squarify::S4_FLOOR` covers them. Low priority. |
| `anyBullFloor` | hvd-pbj-ppd-1939, hvd-pbj-ppd-2246, hvd-pbj-ppd predecessor | masterdir / predecessor variants | Pending-vetting families; YAML records will be created at Stage-3 vetting. |

### Aliases resolved

```
- FLOOR_BULL           # canonical YAML id suffix (hvd-pbj-ppd)
- anyBullFloor         # Pine variable name in hvd-pbj-ppd and squarify
- fire_BullFloor       # gated plot variable (show_BullFloor AND anyBullFloor)
- floor_sq             # Squarify enriched composite at plotshape level
- S4_FLOOR             # Squarify label/alert name (plain English label in plot)
- S4 FLOOR             # Squarify display label
- Floor                # plotshape text in hvd-pbj-ppd ("FLOOR") and squarify ("4 FLOOR")
- BullFloor            # colloquial shorthand (user-facing alias in show/enable toggles)
```

Sources: `data/indicators.yaml`, `bible-input/extract-hvd-pbj-ppd.yaml`, `bible-input/extract-squarify.yaml`, user request phrasing, `docs/redundancy.md` line 59.

---

## Phase 2 — Static diff

**Canonical files compared:**
- A: `hvd-pbj-ppd::FLOOR_BULL` — `anyBullFloor` in `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` L1239–L1241
- B: `squarify::S4_FLOOR` — `floor_sq` in `SQUARIFY_46_v2_2026-05-04.pine` L1349–L1351 (base) + L2156 (composite)

**Key helper `bull_hw_slot`** — defined at L1239 in HVDPBJPPD and L1349 in SQUARIFY_46_v2:
```
bool bull_hw_slot = sigBullRVOL1x or sigGrandSlam or sigWTC or sigHiroshima or (sigNagasaki and nag_dir_bull)
```
**Verdict: byte-identical** in both canonical files. No helper drift.

| Pair | Verdict | Evidence (line ranges) | Drift artifact |
|---|---|---|---|
| A (`anyBullFloor`) ↔ B base (`anyBullFloor` in squarify) | **identical** | HVDPBJPPD L1241 vs SQUARIFY_46 L1351 — byte-identical boolean + byte-identical `bull_hw_slot` helper | none |
| A (`anyBullFloor`) ↔ B enriched (`floor_sq`) | **semantic drift** | SQUARIFY_46 L2156 adds `AND oneOfThese AND cb1_pass_floor` gates absent in A | `docs/validation/2026-05-10-floor-bull-drift-1.md` |

**Drift findings:**
- Drift #1: `anyBullFloor` ↔ `floor_sq` — see [`docs/validation/2026-05-10-floor-bull-drift-1.md`](2026-05-10-floor-bull-drift-1.md)
  - Classification: **semantic drift — enrichment variant** (intentional, not corruption)
  - Squarify gates the base with `oneOfThese` (quality OR of UUUU/UUU/UU/OmegaA/NapalCons/B2BNapalm/CS3/CS1-CS2/WMD) and `cb1_pass_floor` (IPSF checkbox filter)
  - `floor_sq` is a strict subset of `anyBullFloor`; every S4_FLOOR fire is also a FLOOR_BULL fire in hvd-pbj-ppd, but NOT vice versa

**YAML composition accuracy check:**

- `hvd-pbj-ppd::FLOOR_BULL` YAML: `composition: { type: AND, operands: [bull_pp, PBJ_BULL, bull_hw_slot] }` — **MATCHES** Pine. `bull_hw_slot` expands to `RVOL1x OR GS OR WTC OR Hiro OR (Nag AND nag_dir_bull)`. YAML plain_english says "RVOL1x or GS or WTC or Hiro or directional Nag" — **CORRECT.**
- `squarify::S4_FLOOR` YAML: `composition: { type: AND, operands: [PING_PONG_BULL, PBJ_BULL, bull_hw_slot, oneOfThese, cb1_pass_floor] }` — **CORRECT** (matches floor_sq = anyBullFloor AND oneOfThese AND cb1_pass_floor).

**YAML defect found:** `hvd-pbj-ppd::FLOOR_BULL` YAML composition lists `[bull_pp, PBJ_BULL, bull_hw_slot]` but does NOT expand `bull_hw_slot` to the RVOL sub-slots. This is a documentation gap (the full expansion is in plain_english text), not a logic error. Minor YAML enhancement recommended in Phase 4.

---

## Phase 3 — TV firing

| Path used | Why |
|---|---|
| Path B — partial | `hvd-pbj-ppd` Python port (`rti/signals/hvd_pbj_ppd.py`) implements `any_bull_floor` (L1569). `squarify` Python port stubs `S4_FLOOR` / `floor_sq` with "STUBBED (Ping-Pong SR engine required)" comment at L1150. |

| Location | Fire-bar count | Query window | Status |
|---|---|---|---|
| `hvd-pbj-ppd::anyBullFloor` (Python port) | not queried (stateful composite — Ping-Pong state machine required) | — | BLOCKED-NEEDS-TV-FIRING-SKILL |
| `squarify::S4_FLOOR` (Python port) | 0 — explicitly stubbed | — | BLOCKED-NEEDS-TV-FIRING-SKILL |

**Bar-set algebra:**
- Agreement set: N/A (both locations blocked)
- Drift set: N/A
- Total bars scanned: 0

**Rationale for BLOCKED:** `anyBullFloor` depends on `bull_pp` which requires the Ping-Pong state machine (`bull_state`, `bull_cnt`, `bull_has_floor_gravity`). This is a stateful engine that does NOT reset cleanly on a per-call basis in the Phase M pipeline. Both the hvd-pbj-ppd port and the squarify port document this explicitly. Path A (chart-side via LOGGER_HVDPBJPPD_v1.pine or LOGGER_SQUARIFY_v1.pine) is required for runtime confirmation.

**Phase 3 flag:** `BLOCKED-NEEDS-TV-FIRING-SKILL`

---

## Phase 4 — Reconcile

| Finding | Proposed action | User approved | Applied | Commit SHA |
|---|---|---|---|---|
| Drift #1: squarify::S4_FLOOR is an enriched variant of hvd-pbj-ppd::FLOOR_BULL | Add `variant_of: hvd-pbj-ppd::FLOOR_BULL` field to `squarify::S4_FLOOR` record in `bible-input/extract-squarify.yaml`; add note "enriched variant: adds oneOfThese quality gate + cb1_pass_floor checkbox filter" | pending | no | — |
| YAML doc gap: hvd-pbj-ppd::FLOOR_BULL composition omits bull_hw_slot expansion | Expand composition operands in `bible-input/extract-hvd-pbj-ppd.yaml` FLOOR_BULL record to list `(RVOL_1X_BULL OR GS OR WTC OR HIRO OR (NAG AND nag_dir_bull))` instead of `bull_hw_slot` shorthand | pending | no | — |

**Generators run** (deferred until user approves YAML edits):
- `python3 tools/merge_extracts.py` — not yet
- `python3 tools/build_lineage_cards.py` — not yet
- `python3 tools/build_docs.py` — not yet
- YAML == JSON byte-equivalent — not yet

---

## Final verdict

**DRIFT-PENDING-USER**

Structural finding: `squarify::S4_FLOOR` is a deliberate enrichment of `hvd-pbj-ppd::FLOOR_BULL` — the base boolean (`anyBullFloor = conf AND bull_pp AND PBJ_BULL AND bull_hw_slot`) is **byte-identical** in both indicators. Squarify adds `oneOfThese` (quality OR) and `cb1_pass_floor` (IPSF checkbox filter) to produce `floor_sq`, making it a strict subset of the base. This is correct-by-design architecture: hvd-pbj-ppd emits all Floor fires; Squarify shows only the quality-gated subset.

No logic corruption found. The drift is intentional enrichment. YAML needs `variant_of:` tag on squarify::S4_FLOOR and a minor composition expansion on hvd-pbj-ppd::FLOOR_BULL. Both require user ratification before YAML edit.

---

## Stage-7 followups

- [ ] User ratifies canonical direction (hvd-pbj-ppd::FLOOR_BULL canonical; squarify::S4_FLOOR variant_of) and approves YAML edits
- [ ] Add `variant_of: hvd-pbj-ppd::FLOOR_BULL` to `squarify::S4_FLOOR` in `bible-input/extract-squarify.yaml`; add enrichment note
- [ ] Expand `hvd-pbj-ppd::FLOOR_BULL` YAML composition to spell out `bull_hw_slot` sub-operands
- [ ] Run generators after YAML edits (merge_extracts → build_lineage_cards → build_docs)
- [ ] Run `detection-plot-tv-firing` skill with Path A logger when Anish is at desk to confirm runtime agreement between hvd-pbj-ppd::anyBullFloor and squarify::floor_sq (expect squarify to be a strict subset)
- [ ] Port Ping-Pong SR state machine to Python in realtime-indicators to un-stub squarify::S4_FLOOR in squarify.py

---

## Provenance

- Skill version: detection-plot-validation v1.0.0
- Run started: 2026-05-10T00:00:00Z (approx)
- Run ended: 2026-05-10T00:00:00Z (approx)
- Wall-clock duration: ~8 minutes
- Subagents dispatched: Phase 1 = 0 (prior YAML reused from 2026-05-10-floor-family-phase1.yaml); Phase 2 = 0 (2 pairs, below 6-pair threshold); Phase 3 = 0 (both blocked)
- Parent agent: claude-sonnet-4-6 (auto mode)
- Prior Phase-1 artifact: `docs/validation/2026-05-10-floor-family-phase1.yaml`
