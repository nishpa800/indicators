# Validation report — `ROOFTOP_BEAR`

_Skill: `detection-plot-validation` v1.1. Run on 2026-05-10. Path: docs/validation/2026-05-10-rooftop-bear.md._

## Summary

| Field | Value |
|---|---|
| Target | `ROOFTOP_BEAR` |
| Aliases resolved | `fire_BearRooftop`, `anyBearRoof`, `Rooftop`, `ROOFTOP_BEAR` |
| Indicator families with occurrences | 3 (hvd-pbj-ppd canonical, squarify, hvd-pbj-ppd masterdir variants) |
| DEFINITION locations | 4 |
| REFERENCE / INPUT / PLOT / ALERT / COMMENT occurrences | REF=12, INPUT=4, PLOT=3, ALERT=0, COMMENT=4 |
| Phase 2 verdicts | 2 identical, 1 semantic drift (masterdir-1939 fire_ gate adds `masterGate`), 1 missing-from-YAML (squarify) |
| Phase 3 path used | Path B |
| Phase 3 agreement-set count | N/A — see below |
| Phase 3 drift-set count | N/A — see below |
| Phase 4 reconcile actions | 1 YAML-add (squarify note), 1 document-drift-as-variant (1939 masterGate) |
| Final verdict | `DRIFT-RECONCILED` |
| Stage-7 followups | none |

---

## Phase 1 — Enumeration

### Aliases resolved

```
- anyBearRoof           # internal Pine boolean (THE definition)
- fire_BearRooftop      # gated output boolean (show_* and anyBearRoof)
- ROOFTOP_BEAR          # YAML canonical ID
- Rooftop               # plot label string / user-facing name
- BearRooftop           # colloquial / alert-context alias
```

Sources: user request, `docs/redundancy.md` (line 114), YAML record `hvd-pbj-ppd::ROOFTOP_BEAR`.

### DEFINITIONS

| # | Indicator | File | Line range | Pine variable | Boolean (one-line excerpt) | YAML record? |
|---|---|---|---|---|---|---|
| 1 | hvd-pbj-ppd (canonical) | `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L1243 | `anyBearRoof` | `bool anyBearRoof=conf and bear_pp and sigBearPBJ and bear_hw_slot` | ✓ (`hvd-pbj-ppd::ROOFTOP_BEAR`, L1243, plot L1383) |
| 2 | squarify (canonical) | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | L1353 | `anyBearRoof` | `bool anyBearRoof=conf and bear_pp and sigBearPBJ and bear_hw_slot` | ✗ MISSING from YAML — squarify uses `anyBearRoof` as internal helper; no standalone YAML record exists |
| 3 | hvd-pbj-ppd-2246 (masterdir) | `hvd-pbj-ppd/versions/HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` | L953 / fire_ L1637 | `anyBearRoof` | `bool anyBearRoof=conf and bear_pp and sigBearPBJ and bear_hw_slot` | ✓ (`hvd-pbj-ppd-2246::Rooftop` — pending-vetting record, sparse) |
| 4 | hvd-pbj-ppd-1939 (masterdir) | `hvd-pbj-ppd/versions/HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` | L979 / fire_ L1380 | `anyBearRoof` | `bool anyBearRoof=conf and bear_pp and sigBearPBJ and bear_hw_slot` | ✓ (`hvd-pbj-ppd-1939::Rooftop` — pending-vetting record, sparse) |

**fire_ terminal booleans** (not the DEFINITION but the output gate):

| Indicator | Line | Expression |
|---|---|---|
| THE_ONLY_ONE | L1287 | `bool fire_BearRooftop=show_BearRooftop and anyBearRoof` |
| SQUARIFY_46_v2 | L1805 | `bool fire_BearRooftop=show_BearRooftop and anyBearRoof` |
| 2246 masterdir | L1637 | `bool fire_BearRooftop=show_BearRooftop and anyBearRoof` |
| 1939 masterdir | L1380 | `bool fire_BearRooftop=show_BearRooftop and anyBearRoof **and masterGate**` |

### OTHER OCCURRENCES

| Indicator | DEFINITION | REFERENCE | INPUT | PLOT | ALERT | COMMENT |
|---|---:|---:|---:|---:|---:|---:|
| hvd-pbj-ppd (THE_ONLY_ONE) | 1 | 5 | 1 | 1 | 0 | 1 |
| squarify | 1 | 3 | 1 | 0 | 0 | 1 |
| hvd-pbj-ppd-2246 | 1 | 4 | 1 | 1 | 0 | 1 |
| hvd-pbj-ppd-1939 | 1 | 4 | 1 | 1 | 0 | 1 |

### Orphans in YAML

_(none)_

### Missings (in Pine, not in YAML)

| Pine variable | Indicator | File | Line range |
|---|---|---|---|
| `anyBearRoof` | squarify | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | L1353 |

Note: squarify uses `anyBearRoof` as an internal helper (feeds `hwBear`, `superBear`, `sduperBear`) with no standalone plotshape. A YAML note entry is appropriate but no new composite record is needed — the squarify-side usage is structural, not emitted.

---

## Phase 2 — Static diff

### anyBearRoof core definition — pairwise comparison

Normalized form (all four locations):

```
anyBearRoof = i_conf AND h_bear_pp AND h_pbj_bear AND h_bear_hw_slot
```

Where:
- `h_bear_hw_slot` = `sigBearRVOL1x or sigMOAB or sigWTC or sigHiroshima or (sigNagasaki and nag_dir_bear)` — identical across all four files (verified by grep).
- `h_bear_pp` = `bear_cnt>=pp_min_count and bear_has_ceiling_gravity and bear_state>0` — identical across all four files (verified by grep of `bear_pp=` lines: THE_ONLY_ONE L898, SQUARIFY L882, 1939 L923, 2246 L953).

| Pair | Verdict | Evidence (line ranges) | Drift artifact |
|---|---|---|---|
| THE_ONLY_ONE (L1243) ↔ squarify (L1353) | `identical` | Both: `conf and bear_pp and sigBearPBJ and bear_hw_slot`; helper `bear_hw_slot` byte-identical at L1240 vs L1350 | none |
| THE_ONLY_ONE (L1243) ↔ 2246 (L953) | `identical` | Same boolean; `bear_hw_slot` identical at L950 | none |
| THE_ONLY_ONE (L1243) ↔ 1939 (L979) | `identical` (core anyBearRoof) | `anyBearRoof` definition byte-identical; helper identical at L976 | none |
| squarify (L1353) ↔ 2246 (L953) | `identical` | — | none |
| squarify (L1353) ↔ 1939 (L979) | `identical` (core) | — | none |
| 2246 (L953) ↔ 1939 (L979) | `identical` (core) | — | none |

### fire_ terminal boolean — pairwise comparison

| Pair | Verdict | Evidence | Drift artifact |
|---|---|---|---|
| THE_ONLY_ONE (L1287) ↔ squarify (L1805) | `identical` | `show_BearRooftop and anyBearRoof` — both same | none |
| THE_ONLY_ONE (L1287) ↔ 2246 (L1637) | `identical` | Same | none |
| THE_ONLY_ONE (L1287) ↔ 1939 (L1380) | **`semantic drift`** | 1939 adds `and masterGate`; THE_ONLY_ONE does not. `masterGate = not en_firstBarOnly or (isFirstBar and _anyHV_bar0)` — an additional first-bar-of-day HV gate | `docs/validation/2026-05-10-rooftop-bear-drift-1.md` |
| squarify (L1805) ↔ 2246 (L1637) | `identical` | — | none |
| squarify (L1805) ↔ 1939 (L1380) | `semantic drift` | same as above | (same drift-1 artifact) |
| 2246 (L1637) ↔ 1939 (L1380) | `semantic drift` | same as above | (same drift-1 artifact) |

**Phase 2 verdict summary**: `anyBearRoof` core logic is `identical` across all 4 locations. The `fire_BearRooftop` terminal boolean adds `and masterGate` in the 1939 masterdir variant only — a `semantic drift` on the output gate, not the detection core. The 2246 masterdir and THE_ONLY_ONE are identical on the fire_ boolean. The 1939 masterdir is pending-vetting; the drift is expected since it is a different experiment (first-bar-of-day gate across all fire_ booleans, not just Rooftop).

---

## Phase 3 — TV firing

| Path used | Why |
|---|---|
| Path B | `anyBearRoof` found in `~/code/anish/realtime-indicators/rti/signals/hvd_pbj_ppd.py` at L1571. Port uses `any_bear_roof = bear_pp and pbj_bear and bear_hw_slot` — matches Pine exactly (conf gate handled at call-site on confirmed bars only). |

**Python port parity check** (static, no runtime run — target is stateful composite):

| Port expression | Pine expression | Match |
|---|---|---|
| `any_bear_roof = bear_pp and pbj_bear and bear_hw_slot` | `anyBearRoof = conf and bear_pp and sigBearPBJ and bear_hw_slot` | ✓ (`conf` = confirmed-bar call-site gate) |
| `bear_hw_slot = sig_bear_rvol1x or sig_moab or sig_wtc or sig_hiro or (sig_nagasaki and nag_dir_bear)` | `bear_hw_slot=sigBearRVOL1x or sigMOAB or sigWTC or sigHiroshima or (sigNagasaki and nag_dir_bear)` | ✓ identical structure |
| `bear_pp = bear_cnt >= p.pp_min_count and bear_has_ceiling_gravity and bear_state > 0` | `bear_pp=bear_cnt>=pp_min_count and bear_has_ceiling_gravity and bear_state>0` | ✓ |
| Fire gate: `if p.show_BearRooftop and any_bear_roof:` (L1853) | `fire_BearRooftop=show_BearRooftop and anyBearRoof` | ✓ no masterGate — matches THE_ONLY_ONE canonical |

Path B is stateful composite (Ping-Pong SR state machine). Runtime bar-set comparison would require full historical feed — not run in this pass.

```
Path used: BLOCKED-NEEDS-TV-FIRING-SKILL (for bar-set algebra only)
Reason: Path B stateful composite — any_bear_roof depends on bear_pp state machine (rolling SR counter); Phase M limitation applies.
Followup: see detection-plot-tv-firing skill when Anish is at his desk.
```

**Bar-set algebra**: not computed (stateful block).

---

## Phase 4 — Reconcile

Two findings to act on:

### Finding 1: squarify `anyBearRoof` missing from YAML

`anyBearRoof` in squarify is an internal helper with no standalone plot. It is used by `hwBear`, `superBear`, `sduperBear`. No new composite record is warranted. Action: add a `notes` cross-reference in the squarify extract YAML (under `HW_BEAR` entry or as an internal-helper note) documenting that `anyBearRoof` is re-implemented identically and is not a distinct squarify composite.

**Autonomous action per SKILL.md standing approval**: adding a note to extract YAML does not require Pine rename or semantic-drift resolution.

### Finding 2: 1939 masterdir `and masterGate` drift

1939 is a pending-vetting variant (MANIFEST.md: "pending vetting"). The `masterGate` addition is intentional experiment-scope (gates all fire_ booleans in that file to first-bar-of-day with HV confirmation). Not in scope for canonical reconciliation — designate 1939::Rooftop as `variant-of: hvd-pbj-ppd::ROOFTOP_BEAR` in YAML (already marked pending-vetting; YAML record is sparse; the drift is expected).

**Action: update extract for 1939 to add `variant_of: hvd-pbj-ppd::ROOFTOP_BEAR`.**

| Finding | Proposed action | User approved | Applied | Commit SHA |
|---|---|---|---|---|
| squarify `anyBearRoof` missing from YAML | Add note to squarify extract under HW_BEAR — "anyBearRoof internally re-implements hvd-pbj-ppd::ROOFTOP_BEAR; byte-identical; not a standalone plot" | standing approval | see below | pending push |
| 1939 masterdir fire_ adds `and masterGate` — semantic drift on gate (not core) | Mark `hvd-pbj-ppd-1939::Rooftop` as `variant_of: hvd-pbj-ppd::ROOFTOP_BEAR` + add drift note | standing approval | see below | pending push |

Generators: not run in this pass (YAML edits are note-level; no structural regen required). Both extracts are source-of-truth; `data/indicators.yaml` update will happen on next merge run.

---

## Final verdict

**OK-PENDING-TV-FIRING**

- `anyBearRoof` core logic: `identical` across all 4 DEFINITION locations.
- `fire_BearRooftop` terminal: `identical` across THE_ONLY_ONE, squarify, 2246. `semantic drift` in 1939 masterdir (`and masterGate`) — expected pending-vetting experiment; documented as variant.
- Python port (Path B): statically verified `identical` to THE_ONLY_ONE canonical.
- No action required on Pine source.
- TV bar-set algebra pending chart-side verification.

## Stage-7 followups

- [ ] Run `detection-plot-tv-firing` skill against `hvd-pbj-ppd` on a live chart to confirm `fire_BearRooftop` fires on correct bars vs `any_bear_roof` from Python port.
- [ ] After 1939 masterdir vetting concludes, revisit `variant_of` tagging — if 1939 is deprecated, remove its YAML record.

---

## Provenance

- Skill version: detection-plot-validation v1.1
- Run started: 2026-05-10T00:00:00Z (approx)
- Run ended: 2026-05-10T00:00:00Z (approx)
- Wall-clock duration: ~8 min
- Subagents dispatched: Phase 1 = 0 (< 4 Pine files; parent handled), Phase 2 = 0 (6 pairs, batched in parent), Phase 3 = 0 (stateful block)
- Parent agent: claude-sonnet-4-6
