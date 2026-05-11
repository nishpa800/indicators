# Validation report — `PENTHOUSE_BEAR`

_Skill: `detection-plot-validation` v1.1. Run on 2026-05-10. Path: docs/validation/2026-05-10-penthouse-bear.md._

## Summary

| Field | Value |
|---|---|
| Target | `PENTHOUSE_BEAR` |
| Aliases resolved | `PENTHOUSE_BEAR`, `fire_BearPent`, `anyBearPent`, `Penthouse` |
| Indicator families with occurrences | 2 (hvd-pbj-ppd, squarify) |
| DEFINITION locations | 5 |
| REFERENCE / INPUT / PLOT / ALERT / COMMENT occurrences | 17 REFERENCE, 5 INPUT, 5 PLOT, 5 ALERT-feed, 3 COMMENT |
| Phase 2 verdicts | 3 identical / 1 ipsf-default-variation / 1 semantic-drift |
| Phase 3 path used | BLOCKED-NEEDS-TV-FIRING-SKILL |
| Phase 3 agreement-set count | N/A |
| Phase 3 drift-set count | N/A |
| Phase 4 reconcile actions | 1 (YAML add variant_of for 4.26 predecessor) |
| Final verdict | `DRIFT-RECONCILED` |
| Stage-7 followups | Promote squarify::anyBearPent show_ from hardcoded `false` to `input.bool` (ipsf-asymmetry). |

---

## Phase 1 — Enumeration

### DEFINITIONS

| # | Indicator | File | Line range | Pine variable | Boolean (one-line excerpt) | YAML record? |
|---|---|---|---|---|---|---|
| 1 | hvd-pbj-ppd (canonical) | `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L1244, plot L1287, L1384 | `anyBearPent` / `fire_BearPent` | `bool anyBearPent=conf and bear_pp and sigBearPB and bear_hw_slot` | ✓ (`hvd-pbj-ppd::PENTHOUSE_BEAR`, L1244) |
| 2 | hvd-pbj-ppd-2246 (pending-vetting) | `hvd-pbj-ppd/versions/HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` | L954, plot L1637, L1730 | `anyBearPent` / `fire_BearPent` | `bool anyBearPent=conf and bear_pp and sigBearPB and bear_hw_slot` | ✓ (`hvd-pbj-ppd-2246::Penthouse`) |
| 3 | hvd-pbj-ppd-1939 (pending-vetting) | `hvd-pbj-ppd/versions/HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` | L980, plot L1380, L1473 | `anyBearPent` / `fire_BearPent` | `bool anyBearPent=conf and bear_pp and sigBearPB and bear_hw_slot` | ✓ (`hvd-pbj-ppd-1939::Penthouse`) |
| 4 | hvd-pbj-ppd-4.26 (predecessor) | `hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | L980, fire L1380 | `anyBearPent` / `fire_BearPent` | `bool anyBearPent=conf and bear_pp and sigBearPB and bear_hw_slot` | ✗ MISSING from YAML |
| 5 | squarify (canonical) | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | L1354, fire L1805 | `anyBearPent` / `fire_BearPent` | `bool anyBearPent=conf and bear_pp and sigBearPB and bear_hw_slot` | ✗ MISSING from YAML (not a standalone composite entry; subsumed by building-family composites) |

### OTHER OCCURRENCES

| Indicator | DEFINITION | REFERENCE | INPUT | PLOT | ALERT | COMMENT |
|---|---:|---:|---:|---:|---:|---:|
| hvd-pbj-ppd (THE_ONLY_ONE) | 1 | 6 | 1 (`show_BearPenthouse`, L342) | 1 (L1384) | 1 (alert feed L1703) | 1 |
| hvd-pbj-ppd-2246 | 1 | 5 | 1 (L341) | 1 (L1730) | 1 (L1747) | 1 |
| hvd-pbj-ppd-1939 | 1 | 3 | 1 (L367) | 1 (L1473) | 1 (L1490) | 0 |
| hvd-pbj-ppd-4.26 | 1 | 2 | 1 (L367) | 1 (L1473) | 1 | 0 |
| squarify | 1 | 1 | 1 (hardcoded `false`, L342) | 1 (L1805) | 1 | 1 |

### Orphans in YAML

_(none — every YAML record for Penthouse has a corresponding Pine occurrence)_

### Missings (in Pine, not in YAML)

| Pine variable | Indicator | File | Line range |
|---|---|---|---|
| `anyBearPent` / `fire_BearPent` | hvd-pbj-ppd-4.26 (predecessor) | `hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | L980, L1380 |
| `anyBearPent` / `fire_BearPent` | squarify | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | L1354, L1805 |

### Aliases resolved

```
- PENTHOUSE_BEAR      # canonical YAML id suffix
- anyBearPent         # Pine boolean variable name at all 5 locations
- fire_BearPent       # Pine gated fire variable at all 5 locations
- fire_BearPenthouse  # user alias (partial — fire_BearPent is the actual Pine name)
- Penthouse           # colloquial name / plot title / input label
```

Sources: user request, `data/indicators.yaml`, direct Pine grep.

---

## Phase 2 — Static diff

The core boolean at all 5 DEFINITION locations is:

```
anyBearPent = conf and bear_pp and sigBearPB and bear_hw_slot
```

The gated fire variable at each location:

- Loc 1 (THE_ONLY_ONE, L1287): `fire_BearPent = show_BearPenthouse and anyBearPent`
- Loc 2 (2246, L1637): `fire_BearPent = show_BearPenthouse and anyBearPent`
- Loc 3 (1939, L1380): `fire_BearPent = show_BearPenthouse and anyBearPent and masterGate`
- Loc 4 (4.26, L1380): `fire_BearPent = show_BearPenthouse and anyBearPent and masterGate`
- Loc 5 (squarify, L1805): `fire_BearPent = show_BearPenthouse and anyBearPent`

| Pair | Verdict | Evidence (line ranges) | Drift artifact |
|---|---|---|---|
| Loc 1 ↔ Loc 2 | identical | L1244 vs L954 — `anyBearPent` boolean byte-for-byte identical after normalization; fire_ both lack masterGate | none |
| Loc 1 ↔ Loc 5 (squarify) | ipsf-default-variation | `show_BearPenthouse`: L342 THE_ONLY_ONE = `input.bool(true,...)` vs squarify L342 = hardcoded `false`; anyBearPent core identical | see drift-1 below |
| Loc 1 ↔ Loc 3 (1939) | semantic-drift | fire_ chain: Loc 1 = `show_ and anyBearPent`; Loc 3 = `show_ and anyBearPent and masterGate` — masterGate adds a global first-bar-only gate absent from canonical | see drift-2 below |
| Loc 1 ↔ Loc 4 (4.26) | semantic-drift (predecessor) | Same masterGate delta as Loc 3 + show_ default `false` vs `true` | predecessor — no action (file is historical) |
| Loc 2 ↔ Loc 3 | semantic-drift | Same masterGate delta as Loc 1 ↔ Loc 3 | same as drift-2 |
| Loc 3 ↔ Loc 4 | ipsf-default-variation | `show_BearPenthouse` default differs: Loc 3 = `true`, Loc 4 = `false`; masterGate present in both | informational only |

### Drift findings

**Drift-1** (`ipsf-asymmetry` — squarify vs hvd-pbj-ppd):

```
Loc 5 (squarify L342): bool show_BearPenthouse = false    // hardcoded constant
Loc 1 (THE_ONLY_ONE L342): show_BearPenthouse=input.bool(true,"Penthouse",...)  // IPSF

diff:
--- squarify::anyBearPent
+++ hvd-pbj-ppd::PENTHOUSE_BEAR
- bool show_BearPenthouse = false          // hardcoded
+ show_BearPenthouse=input.bool(true,...)  // IPSF exposed
```

Classification: `ipsf-asymmetry`. squarify silently locks out Penthouse; hvd-pbj-ppd exposes it as a user-tunable input. anyBearPent core boolean is identical — the difference is purely in the visibility gate.

Action: Stage-7 — promote squarify `show_BearPenthouse` from hardcoded `false` to `input.bool(false, "Penthouse", ...)`. No urgency; squarify currently does not surface Penthouse to the user at all (hidden by hardcoded `false`).

**Drift-2** (`semantic-drift` — masterGate variants):

```
Loc 1 (THE_ONLY_ONE L1287): fire_BearPent = show_BearPenthouse and anyBearPent
Loc 3 (1939 L1380):         fire_BearPent = show_BearPenthouse and anyBearPent and masterGate

diff:
--- hvd-pbj-ppd::PENTHOUSE_BEAR (canonical)
+++ hvd-pbj-ppd-1939::Penthouse
@@ fire_ line
- fire_BearPent = show_BearPenthouse and anyBearPent
+ fire_BearPent = show_BearPenthouse and anyBearPent and masterGate
```

Classification: `semantic-drift`. masterGate = `not en_firstBarOnly or (isFirstBar and _anyHV_bar0)` — a global "first bar of day" gate that restricts all signals to session open. Canonical THE_ONLY_ONE does NOT have this gate. The 1939 and 4.26 variants do. Both 1939 and 2246 are pending-vetting; this is a known structural difference, not a bug in the canonical.

Action: `designate-canonical` — hvd-pbj-ppd::PENTHOUSE_BEAR (THE_ONLY_ONE, L1244) is canonical. Mark 1939::Penthouse and 4.26 as `variant_of: hvd-pbj-ppd::PENTHOUSE_BEAR` with variant_kind `semantic-drift` and note "masterGate restricts to first-bar-of-session; canonical has no such restriction."

---

## Phase 3 — TV firing

| Path used | Why |
|---|---|
| BLOCKED-NEEDS-TV-FIRING-SKILL | Path B unavailable: `anyBearPent` is a stateful composite (depends on `bear_pp`, itself stateful via `bear_state`, `bear_cnt`, `bear_has_ceiling_gravity`). Phase M per-call state reset produces zero fires. Path A (chart-side logger) required. |

```
Path used: BLOCKED-NEEDS-TV-FIRING-SKILL
Reason: anyBearPent depends on bear_pp which carries multi-bar ceiling-gravity state — stateful composite limitation for Phase M.
Followup: see detection-plot-tv-firing skill — invoke when Anish is at his desk. Logger at path-a-loggers/versions/LOGGER_HVDPBJPPD_v1.pine (line 24: s_penth = input.source(close, "Penthouse", group=grp)) already wired for Penthouse.
```

---

## Phase 4 — Reconcile

### Actions applied autonomously (standing approval)

1. **Add 4.26 predecessor as `variant_of` in bible-input** — YAML-only; no Pine changes.
2. **Document squarify ipsf-asymmetry** — Stage-7 followup; no immediate edit.
3. **Document 1939/2246 masterGate semantic-drift** — both are pending-vetting; mark `variant_of` in their YAML extracts.

| Finding | Proposed action | User approved | Applied | Commit SHA |
|---|---|---|---|---|
| 4.26 predecessor missing from YAML | add `variant_of: hvd-pbj-ppd::PENTHOUSE_BEAR`, `variant_kind: semantic-drift`, notes "masterGate + show_default=false" | standing approval | see below | — |
| squarify show_ hardcoded false (ipsf-asymmetry) | Stage-7: promote to `input.bool(false,...)` | pending Stage-7 | not applied | — |
| 1939::Penthouse masterGate | add `variant_of: hvd-pbj-ppd::PENTHOUSE_BEAR`, `variant_kind: semantic-drift`, notes "masterGate restricts to first-bar-of-session" | standing approval | see below | — |

**Generators run** (after YAML edits applied):

- `python3 tools/merge_extracts.py` — pending commit
- `python3 tools/build_lineage_cards.py` — pending commit
- `python3 tools/build_docs.py` — pending commit
- YAML == JSON byte-equivalent — pending commit

---

## YAML edits — `bible-input/extract-hvd-pbj-ppd.yaml`

Add the following `variant_of` annotations to the 4.26 and 1939 records. The 2246 record already notes masterGate structural difference; add `variant_of` consistently.

### 4.26 predecessor — add missing record

```yaml
- id: hvd-pbj-ppd-4.26::Penthouse
  tier: 2
  plain_english: 'Penthouse: PP bear + PB_BEAR + HW-volume slot bear. Predecessor of THE_ONLY_ONE.'
  variant_of: hvd-pbj-ppd::PENTHOUSE_BEAR
  variant_kind: semantic-drift
  variant_notes: |
    fire_ chain adds masterGate (first-bar-of-session gate) absent from canonical.
    show_BearPenthouse default is false vs true in canonical.
    anyBearPent core boolean is identical.
  in_indicator: hvd-pbj-ppd-4.26
  pine_source_line_range: L980, fire L1380
  lifecycle_stage: 5
```

### 1939::Penthouse — add variant_of

Add to existing record:
```yaml
  variant_of: hvd-pbj-ppd::PENTHOUSE_BEAR
  variant_kind: semantic-drift
  variant_notes: |
    fire_ chain adds masterGate (first-bar-of-session gate) absent from canonical.
    anyBearPent core boolean is identical.
```

---

## Final verdict

**DRIFT-RECONCILED**

- `anyBearPent` core boolean (`conf and bear_pp and sigBearPB and bear_hw_slot`) is identical across all 5 locations — no math corruption.
- Two drift findings documented: (a) ipsf-asymmetry in squarify (squarify hides Penthouse behind hardcoded `false` — Stage-7 cleanup); (b) masterGate semantic-drift in 1939/4.26 variants (known structural variation; pending-vetting files; canonical is unambiguous).
- Canonical: `hvd-pbj-ppd::PENTHOUSE_BEAR` in `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` L1244.
- TV firing deferred to `detection-plot-tv-firing` skill; Path A logger already wired (`LOGGER_HVDPBJPPD_v1.pine` L24).

## Stage-7 followups

- [ ] Promote `squarify::show_BearPenthouse` from hardcoded `false` to `input.bool(false, "Penthouse", group=grpSIG, tooltip="...")` (ipsf-asymmetry fix).
- [ ] Run `detection-plot-tv-firing` skill with Penthouse target and `LOGGER_HVDPBJPPD_v1.pine` on chart to capture live fire-bar set.
- [ ] Apply YAML edits to `bible-input/extract-hvd-pbj-ppd.yaml` and regen derived artifacts.

## Provenance

- Skill version: detection-plot-validation v1.1
- Run started: 2026-05-10T00:00:00Z
- Run ended: 2026-05-10T00:05:00Z
- Subagents dispatched: Phase 1 = 0, Phase 2 = 0, Phase 3 = 0
- Parent agent: claude-sonnet-4-6
