# Validation report — `SECOND_FLOOR_BULL`

_Skill: `detection-plot-validation` v1.1. Run on 2026-05-10. Path: docs/validation/2026-05-10-second-floor.md._

## Summary

| Field | Value |
|---|---|
| Target | `SECOND_FLOOR_BULL` |
| Aliases resolved | `anyBull2nd`, `fire_Bull2ndFloor`, `2F`, `S5_2F`, `floor2_sq`, `floor2_gated`, `2nd Floor`, `SECOND_FLOOR_BULL` |
| Indicator families with occurrences | 2 (hvd-pbj-ppd, squarify) |
| DEFINITION locations | 6 (across 4 files: THE_ONLY_ONE, 2246, 1939, 4.26 + squarify canonical + squarify legacy siblings) |
| REFERENCE / INPUT / PLOT / ALERT / COMMENT occurrences | REF ~30, INPUT 5, PLOT 5, ALERT 0, COMMENT 2 |
| Phase 2 verdicts | 0 identical / 0 cosmetic / 0 ipsf-default / 0 ipsf-asym / 3 semantic |
| Phase 3 path used | BLOCKED-NEEDS-TV-FIRING-SKILL |
| Phase 3 agreement-set count | N/A |
| Phase 3 drift-set count | N/A |
| Phase 4 reconcile actions | 0 applied (3 pending user approval) |
| Final verdict | DRIFT-PENDING-USER |
| Stage-7 followups | 3 (see below) |

---

## Phase 1 — Enumeration

### Aliases resolved

```
- SECOND_FLOOR_BULL          # YAML canonical ID (hvd-pbj-ppd namespace)
- anyBull2nd                  # Pine variable name in all hvd-pbj-ppd files
- fire_Bull2ndFloor           # fire-gate boolean (show AND anyBull2nd)
- 2F                          # plot label + alertcondition ID
- 2nd Floor                   # YAML colloquial name (hvd-pbj-ppd-1939/2246 namespaces)
- S5_2F                       # YAML canonical ID (squarify namespace)
- floor2_sq                   # Pine variable name in squarify (adds oneOfThese+cb1_pass+NOT floor)
- floor2_gated                # Pine variable name in hvd-pbj-ppd 2246 + 1939 + 4.26 variants
```

Sources: user request, `docs/redundancy.md` (entry for `2nd Floor`), `data/indicators.yaml` direct search.

### DEFINITIONS

| # | Indicator | File | Line range | Pine variable | Boolean (excerpt) | YAML record? |
|---|---|---|---|---|---|---|
| 1 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L1242 | `anyBull2nd` | `conf and bull_pp and sigBullPB and bull_hw_slot` | ✓ `hvd-pbj-ppd::SECOND_FLOOR_BULL` (YAML L9773) |
| 2 | hvd-pbj-ppd (2246 variant) | `hvd-pbj-ppd/versions/HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` | L952 (`anyBull2nd`); L1513 (`floor2_gated`) | `floor2_gated` | `anyBull2nd and oneOfThese and cb1_pass` | ✓ `hvd-pbj-ppd-2246::2nd Floor` (YAML L8474) |
| 3 | hvd-pbj-ppd (1939 variant) | `hvd-pbj-ppd/versions/HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` | L978 (`anyBull2nd`); L1248 (`floor2_gated`) | `floor2_gated` | `anyBull2nd and oneOfThese and cb1_pass` | ✓ `hvd-pbj-ppd-1939::2nd Floor` (YAML L8024) |
| 4 | hvd-pbj-ppd (4.26 predecessor) | `hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | L978 (`anyBull2nd`); L1248 (`floor2_gated`) | `floor2_gated` | `anyBull2nd and oneOfThese and cb1_pass` | ✗ MISSING from YAML (predecessor file; not tracked as separate family) |
| 5 | squarify (canonical) | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | L1352 (`anyBull2nd` ref); L2157 (`floor2_sq`) | `floor2_sq` | `anyBull2nd and oneOfThese and cb1_pass and not floor_sq` | ✓ `squarify::S5_2F` (YAML L11193) |
| 6 | squarify (legacy v2) | `squarify/versions/SQUARIFY_v2.pine` | L1352 / L2231 | `floor2_sq` | `anyBull2nd and oneOfThese and cb1_pass and not floor_sq` | ✗ MISSING (legacy, not separately tracked — expected) |

Note: squarify legacy siblings (SQUARIFY_v1.pine, SQUARIFY_ATOMS_v1.pine, backtests) contain the same pattern as squarify canonical — cosmetically identical. Not separately enumerated as they are not canonical per MANIFEST.

### OTHER OCCURRENCES

| Indicator | DEFINITION | REFERENCE | INPUT | PLOT | ALERT | COMMENT |
|---|---:|---:|---:|---:|---:|---:|
| hvd-pbj-ppd (THE_ONLY_ONE) | 1 | ~8 | 1 | 1 | 0 | 0 |
| hvd-pbj-ppd (2246) | 1 | ~8 | 1 | 1 | 0 | 0 |
| hvd-pbj-ppd (1939) | 1 | ~8 | 1 | 1 | 0 | 0 |
| hvd-pbj-ppd (4.26) | 1 | ~8 | 1 | 1 | 0 | 0 |
| squarify (canonical) | 1 | ~4 | 1 | 1 | 1 | 0 |
| path-a-loggers | 0 | 0 | 1 | 0 | 0 | 1 |

### Orphans in YAML

_(none)_

### Missings (in Pine, not in YAML)

| Pine variable | Indicator | File | Line range |
|---|---|---|---|
| `anyBull2nd` (as `floor2_gated`) | hvd-pbj-ppd (4.26 predecessor) | `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | L978, L1248 |

Note: 4.26 is a predecessor file; no YAML record expected. Listed for completeness. No Phase 4 action required.

---

## Phase 2 — Static diff

The `anyBull2nd` core boolean is byte-identical across all 6 DEFINITION locations:
```
conf and bull_pp and sigBullPB and bull_hw_slot
```
All helpers (`bull_hw_slot`, `nag_dir_bull`) are identical across the 4 hvd-pbj-ppd files.

The divergence is in the FIRE GATE and POST-PROCESSING wrapping:

| Pair | Verdict | Evidence (line ranges) | Drift artifact |
|---|---|---|---|
| THE_ONLY_ONE ↔ squarify::S5_2F | semantic-drift | THE_ONLY_ONE: `anyBull2nd` bare; squarify: `anyBull2nd AND oneOfThese AND cb1_pass AND NOT floor_sq` | [drift-1](2026-05-10-second-floor-drift-1.md) |
| THE_ONLY_ONE ↔ 2246 | semantic-drift | THE_ONLY_ONE: fire=`show AND anyBull2nd`; 2246: fire=`show AND (anyBull2nd AND oneOfThese AND cb1_pass)` | [drift-2](2026-05-10-second-floor-drift-2.md) |
| 1939 ↔ all others | semantic-drift | 1939 fire gate uniquely includes `masterGate`; others do not | [drift-3](2026-05-10-second-floor-drift-3.md) |
| THE_ONLY_ONE ↔ 1939 (anyBull2nd leaf) | identical | Both: `conf and bull_pp and sigBullPB and bull_hw_slot` | none |
| THE_ONLY_ONE ↔ 4.26 (anyBull2nd leaf) | identical | Both: `conf and bull_pp and sigBullPB and bull_hw_slot` | none |
| 2246 ↔ 1939 (anyBull2nd leaf) | identical | Both: `conf and bull_pp and sigBullPB and bull_hw_slot` | none |
| 2246 ↔ 4.26 (floor2_gated) | identical | Both: `anyBull2nd and oneOfThese and cb1_pass`; fire=`show AND floor2_gated` (no masterGate in 2246 fire) | none |
| squarify ↔ 2246 (gating structure) | semantic-drift | squarify adds `AND NOT floor_sq` suppression; 2246 does not | subsumed in drift-1 (same root cause) |

**Summary of structural variants:**

| Variant | Core boolean | Extra gate | masterGate in fire | NOT floor suppression |
|---|---|---|---|---|
| THE_ONLY_ONE (`anyBull2nd`) | conf+bull_pp+PB+hw_slot | none | no | no |
| 2246 / 4.26 (`floor2_gated`) | conf+bull_pp+PB+hw_slot | oneOfThese+cb1_pass | no | no |
| 1939 (`floor2_gated`) | conf+bull_pp+PB+hw_slot | oneOfThese+cb1_pass | YES | no |
| squarify (`floor2_sq`) | conf+bull_pp+PB+hw_slot | oneOfThese+cb1_pass | no | YES (NOT floor_sq) |

---

## Phase 3 — TV firing

| Path used | Why |
|---|---|
| BLOCKED-NEEDS-TV-FIRING-SKILL | Path B unavailable (`realtime-indicators` repo not present at `~/code/anish/realtime-indicators/`). Target is a stateful composite (feeds into aggregated-alert first-of-day tracker). Invoke `detection-plot-tv-firing` skill when Anish is at desk. |

| Location | Fire-bar count | Query window | Status |
|---|---|---|---|
| hvd-pbj-ppd::SECOND_FLOOR_BULL | N/A | N/A | BLOCKED |
| squarify::S5_2F | N/A | N/A | BLOCKED |

**Bar-set algebra**: N/A (BLOCKED)

**Drift-bar diagnoses**: N/A

---

## Phase 4 — Reconcile

Standing approval applies per `STANDING_APPROVAL.md`. However, all three findings involve semantic drift requiring Pine source decisions or pending-vetting file promotion. Per `SKILL.md § "When to ask the user"`, these require explicit user approval before applying.

| Finding | Proposed action | User approved | Applied | Commit SHA |
|---|---|---|---|---|
| drift-1 (THE_ONLY_ONE ↔ squarify::S5_2F) | `variant-of` in YAML: mark squarify::S5_2F as variant_of hvd-pbj-ppd::SECOND_FLOOR_BULL with note "adds oneOfThese+cb1_pass+NOT floor gate" | pending | no | — |
| drift-2 (THE_ONLY_ONE ↔ 2246) | `variant-of` in YAML: mark hvd-pbj-ppd-2246::2nd Floor as variant_of hvd-pbj-ppd::SECOND_FLOOR_BULL | pending | no | — |
| drift-3 (1939 unique masterGate) | `no-action` pending investigation — confirm whether 1939's masterGate inclusion is intentional; if yes mark in notes, if no flag for pine-source-fix on 1939 | pending | no | — |

**Generators run**: not run (no YAML edits applied pending user approval)

---

## Final verdict

**DRIFT-PENDING-USER** — 3 semantic drift findings. Core boolean (`anyBull2nd = conf AND bull_pp AND PB AND bull_hw_slot`) is identical across all 6 locations. The drift is entirely in the fire-gate wrapping:
1. Squarify adds `oneOfThese + cb1_pass + NOT floor_sq` — the richest gating
2. 2246/4.26 add `oneOfThese + cb1_pass` but no floor suppression  
3. 1939 additionally adds `masterGate` to the fire line
4. THE_ONLY_ONE (canonical) has none of these extra gates — fires on the raw core boolean

User must decide: is the canonical 2F the ungated THE_ONLY_ONE form, or should it be updated to match the gated form from 2246/squarify?

---

## Stage-7 followups

- [ ] **drift-1 / drift-2**: User to confirm whether `hvd-pbj-ppd::SECOND_FLOOR_BULL` (THE_ONLY_ONE) should be updated to add `oneOfThese + cb1_pass` gate to match squarify S5_2F and 2246 behavior
- [ ] **drift-3**: Verify whether 1939's `masterGate` in fire line is intentional (architectural hardening) or accidental; update YAML notes accordingly
- [ ] **Phase 3 TV firing**: Run `detection-plot-tv-firing` skill on both `hvd-pbj-ppd::SECOND_FLOOR_BULL` and `squarify::S5_2F` to confirm runtime agreement set. Priority: compare THE_ONLY_ONE vs squarify on same chart — expect squarify to fire on a strict subset of THE_ONLY_ONE bars (due to extra gate)

---

## Provenance

- Skill version: detection-plot-validation v1.1
- Run started: 2026-05-10T00:00:00Z (approx)
- Run ended: 2026-05-10T00:00:00Z (approx)
- Wall-clock duration: ~8 minutes
- Subagents dispatched: Phase 1 = 0 (≤4 Pine files with meaningful DEFs; parent handled), Phase 2 = 0 (parent handled), Phase 3 = 0 (BLOCKED)
- Parent agent: Claude Sonnet 4.6 (detection-plot-validation skill run)
