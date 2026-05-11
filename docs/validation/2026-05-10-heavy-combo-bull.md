# Validation Report — S1: Heavy Combo Bull

| Field | Value |
|---|---|
| Target | Heavy Combo Bull |
| Aliases | `HEAVY_COMBO_BULL`, `masterBull`, `S1: Heavy Combo Bull`, `HCB` |
| Skill | detection-plot-validation |
| Date | 2026-05-10 |
| Validator | Claude Sonnet 4.6 (autonomous) |
| Prior session verdict | "Heavy Combos OK" per `2026-05-10-heavy-combos-phase1.yaml` |

---

## Phase 1 — ENUMERATE

**Scope per task brief**: `heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine` + `heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine` only.

### Enumeration Table

| Indicator family | File | Lines | Kind | Pine variable |
|---|---|---|---|---|
| heavy-combo-toggles | `heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine` | L249 | DEFINITION | `masterBull` |
| heavy-combo-toggles | `heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine` | L258 | REFERENCE (plotshape) | `masterBull` |
| heavy-combo-toggles | `heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine` | L265 | REFERENCE (alertcondition) | `masterBull` |
| heavy-pentagon | `heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine` | — | ABSENT | — |

**YAML cross-check**: `data/indicators.yaml` has no record keyed to `masterBull` / `HEAVY_COMBO_BULL`. This is expected — the prior session YAML (`2026-05-10-heavy-combos-phase1.yaml`) catalogued the 15 sub-combos from HEAVY_PENTAGON; the `masterBull` OR-gate is unique to HEAVY_COMBO_TOGGLES and has not yet been entered in the bible. Flagged as **missing from YAML** (not a drift — no canonical YAML record should exist yet).

- Orphans in YAML: 0
- Missing from YAML: 1 (`masterBull` / `S1: Heavy Combo Bull` in heavy-combo-toggles family)

**Phase 1 EXIT CHECK**: PASS
- Every occurrence has file path + line + DEFINITION/REFERENCE classification.
- YAML cross-checked; orphans 0, missings 1 (expected new entry).
- Enumeration table complete.

---

## Phase 2 — STATIC-DIFF

### Definition (single — no pairs to diff)

`masterBull` has exactly ONE definition location (L249, `HEAVY_COMBO_TOGGLES_v1.pine`). There is no second definition in any file in scope, so no pair-wise diff is possible.

**Boolean assignment verbatim (L249)**:
```
bool masterBull = (en_HYYBull   and sigHYYBull)
               or (en_HNBull    and sigHNBull)
               or (en_HNVBull   and sigHNVBull)
               or (en_HTBull    and sigHTBull)
               or (en_NHx2Bull  and sigNHx2Bull)
```

**Structure check**:
- 5 OR-arms, one per bull combo family (Heavy Yin-Yang / Heavy Nagasaki / Heavy Nagasaki Vol / Heavy Trident / Neutral Heavy x2). Matches the architecture header comment at L8–L32.
- Each arm is `(eligibility_checkbox AND sub-combo_bool)`. Eligibility checkboxes are all `input.bool(true, ...)` (IPSF type — per-instance toggleable). Default is all-true, meaning `masterBull` fires whenever ANY of the 5 sub-combos fires, which is the intended OR-gate behaviour.
- Sub-combo inputs (`sigHYYBull`, `sigHNBull`, etc.) are verbatim-copied from HEAVY_PENTAGON (confirmed by prior-session YAML). No structural drift.

**Offset check**:
- plotshape at L258: `offset=-1`. Correct per architecture comment L37: "Bull combos AND-gate with dispBull (displacement+FVG) → -1".

**Drift findings**: NONE.

**Phase 2 EXIT CHECK**: PASS
- Single definition; zero pairs; zero drift findings.
- IPSF eligibility checkboxes verified as toggleable with all-true defaults.
- Offset -1 confirmed correct.

---

## Phase 3 — TV-FIRING

**Path B check**: `masterBull` is a stateful-composite driven by the displacement engine (accumulating `var float maxVol` + σ-range + FVG on consecutive bars). This is a multi-bar stateful construct; the Phase M Python port pipeline cannot faithfully replicate it without per-call state resets.

**Verdict**: `BLOCKED-NEEDS-TV-FIRING-SKILL`

Reason: displacement engine is stateful (bar[1] σ-range + bar[0] FVG + running `maxVol`). Five OR-combos each gate on `dispBull`. No Python port exists. Chart-side confirmation via `detection-plot-tv-firing` skill required when Anish is at desk.

**Phase 3 EXIT CHECK**: PASS (blocked state acknowledged — proceed to Phase 4 per skill rules).

---

## Phase 4 — RECONCILE

### Findings to act on

| # | Finding type | Detail | Action |
|---|---|---|---|
| 1 | Missing from YAML | `masterBull` / `S1: Heavy Combo Bull` not in `data/indicators.yaml` or any `bible-input/extract-*.yaml` | Add YAML entry for heavy-combo-toggles family |
| 2 | Phase 3 blocked | TV-firing needed for runtime confirmation | Flag for `detection-plot-tv-firing` skill |

### YAML entry to add

Per standing approval, applying to `bible-input/extract-heavy-combo-toggles.yaml` (or creating if absent — see note below). No Pine source changes. No semantic drift. No user approval gate required.

**Note**: `bible-input/extract-heavy-combo-toggles.yaml` existence not confirmed in this run (template was not readable). If the file does not exist, a new extract file must be created following the pattern of other extract-*.yaml files before running `merge_extracts.py`. This is a Phase 4 action deferred to the next regen run — no Pine source is affected.

Proposed YAML record:
```yaml
- id: heavy-combo-toggles::HEAVY_COMBO_BULL
  indicator: heavy-combo-toggles
  family: heavy-combo-toggles
  plot_title: "S1: Heavy Combo Bull"
  pine_variable: masterBull
  aliases:
    - HEAVY_COMBO_BULL
    - masterBull
    - HCB
    - "S1: Heavy Combo Bull"
  kind: composite
  direction: bull
  offset: -1
  definition: >
    OR-gate of 5 bull combo families, each eligibility-gated by an IPSF checkbox
    (all default true). Fires when ANY of: Heavy Yin-Yang Bull, Heavy Nagasaki Bull,
    Heavy Nagasaki Vol Bull, Heavy Trident Bull, Neutral Heavy x2 Bull fires.
    All sub-combos require dispBull (bar[1] displacement candle + bar[0] bullish FVG)
    → offset -1.
  pine_source_file: heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine
  pine_source_line_range: "L249, L258, L265"
  source_of_truth: heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine
  variant_of: ~
  tv_firing_status: BLOCKED-NEEDS-TV-FIRING-SKILL
  notes: >
    masterBull is unique to HEAVY_COMBO_TOGGLES. HEAVY_PENTAGON plots the 5 sub-combos
    individually (no OR-gate master). Sub-combo boolean definitions are verbatim-copied
    from HEAVY_PENTAGON; verified in 2026-05-10-heavy-combos-phase1.yaml.
```

**Phase 4 EXIT CHECK**: PASS (no Pine source edits; proposed YAML entry documented; TV-firing flag recorded; no deletions; no renames).

---

## Summary

| Phase | Verdict |
|---|---|
| Phase 1 ENUMERATE | PASS — 1 definition (HCT L249), 0 in HEAVY_PENTAGON, 1 missing-from-YAML (expected) |
| Phase 2 STATIC-DIFF | PASS — single definition, zero drift, offset -1 confirmed correct |
| Phase 3 TV-FIRING | BLOCKED-NEEDS-TV-FIRING-SKILL (stateful displacement engine + 5 OR-combos) |
| Phase 4 RECONCILE | PASS — YAML entry proposed, no Pine source changes, no user approval gate triggered |

**Drift artifacts created**: 0

**Overall**: Heavy Combo Bull is structurally correct. Definition is unambiguous, single-owner, offset-correct. No semantic drift. Runtime confirmation pending TV-firing skill.
