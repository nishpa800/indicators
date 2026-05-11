# Validation report — `COMBO_CHAIN_BULL`

_Skill: `detection-plot-validation` v1.1.0. Run on 2026-05-10. Path: docs/validation/2026-05-10-combo-chain-bull.md._

## Summary

| Field | Value |
|---|---|
| Target | `COMBO_CHAIN_BULL` (Pine var: `sigCCBull`) |
| Aliases resolved | `COMBO_CHAIN_BULL`, `COMBO_CHAIN_BEAR`, `ComboChain`, `comboChain`, `combo_chain`, `CC`, `CC Bull`, `sigCCBull`, `sigCCBear`, `comboChainBull`, `comboChainBear`, `sigCCBull`, `sigCCBear`, `cc_bull_active` (stateful helper), `cc_chain` |
| Indicator families with occurrences | 2 primary: `squarify`, `hvd-pbj-ppd` |
| DEFINITION locations | 8 wrapper DEFs (`bool sigCCBull = conf and cc_bull_active`); state-machine body has **3 distinct semantic groups** |
| REFERENCE / INPUT / PLOT / ALERT / COMMENT occurrences | squarify: R=51, I=1 (hardcoded `bool show_CCBull = true`), P=2, A=0, C=0; hvd-pbj-ppd: R=83, I=1 (`input.bool`), P=16, A=0, C=0; path-a-loggers: R=2, C=2; b2b-pup: C=3 (COMMENT only — CC was ripped out in v4.30) |
| Phase 2 verdicts | wrapper: 28 pairs `identical`; state-machine body: **2 pairs `semantic-drift` (B↔A, B↔C), 1 pair `cosmetic-drift` (A↔C)** |
| Phase 3 path used | `BLOCKED-NEEDS-TV-FIRING-SKILL` — stateful composite; Path B returns zero; Path A required |
| Phase 3 agreement-set count | N/A (BLOCKED) |
| Phase 3 drift-set count | N/A (BLOCKED) |
| Phase 4 reconcile actions | YAML missing-record add (8 sigCCBull entries missing from all extract YAMLs); IPSF-asymmetry flag for squarify `show_CCBull` (hardcoded `true` vs `input.bool` in hvd-pbj-ppd); semantic-drift decision PENDING USER |
| Final verdict | **DRIFT-PENDING-USER** — 3-way semantic drift in state-machine reset condition; user must designate canonical operand set before Pine fix applied |
| Stage-7 followups | 5 (see bottom) |

---

## Phase 1 — Enumeration

### Aliases resolved

```
- sigCCBull            # primary Pine variable (all locations)
- sigCCBear            # bear mirror (co-validated)
- COMBO_CHAIN_BULL     # canonical name (user request)
- CC Bull              # display label in UI
- CC                   # colloquial shorthand
- cc_bull_active       # stateful boolean driving sigCCBull (one level deeper)
- cc_bear_active       # bear mirror of above
- comboChainBull       # variant alias
- comboChainBear       # variant alias
- sigCCBull / sigCCBear # alternate with prefix
```

Sources: user request, `docs/redundancy.md` lines 33-34 (CC Bull / CC Bear flagged as drifted), `bible-input/MANIFEST.md`, COMMENT lines in b2b-pup (v4.30 rip-out note).

### DEFINITIONS

| # | Indicator | File | Line range | Pine variable | Boolean (excerpt) | YAML record? |
|---|---|---|---|---|---|---|
| 1 | squarify | `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | L1312 | `sigCCBull` | `bool sigCCBull=conf and cc_bull_active` | ✗ MISSING |
| 2 | squarify | `squarify/versions/SQUARIFY_ATOMS_v1.pine` | L1320 | `sigCCBull` | `bool sigCCBull=conf and cc_bull_active` | ✗ MISSING |
| 3 | squarify | `squarify/versions/SQUARIFY_v1.pine` | L1238 | `sigCCBull` | `bool sigCCBull=conf and cc_bull_active` | ✗ MISSING |
| 4 | squarify | `squarify/versions/SQUARIFY_v2.pine` | L1312 | `sigCCBull` | `bool sigCCBull=conf and cc_bull_active` | ✗ MISSING |
| 5 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` | L1046 | `sigCCBull` | `bool sigCCBull=conf and cc_bull_active` | ✗ MISSING |
| 6 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L1111 | `sigCCBull` | `bool sigCCBull=conf and cc_bull_active` | ✗ MISSING |
| 7 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` | L1020 | `sigCCBull` | `bool sigCCBull=conf and cc_bull_active` | ✗ MISSING |
| 8 | hvd-pbj-ppd | `hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` | L1046 | `sigCCBull` | `bool sigCCBull=conf and cc_bull_active` | ✗ MISSING |

### OTHER OCCURRENCES

| Indicator | DEFINITION | REFERENCE | INPUT | PLOT | ALERT | COMMENT |
|---|---:|---:|---:|---:|---:|---:|
| squarify | 4 | 51 | 1 (hardcoded `true`) | 2 | 0 | 0 |
| hvd-pbj-ppd | 4 | 83 | 1 (`input.bool`) | 16 | 0 | 0 |
| b2b-pup | 0 | 0 | 0 | 0 | 0 | 3 |
| path-a-loggers | 0 | 2 | 0 | 0 | 0 | 2 |

### Orphans in YAML

_(none)_

### Missings (in Pine, not in YAML)

All 8 DEFINITION locations listed above are missing from `bible-input/extract-squarify.yaml`, `bible-input/extract-hvd-pbj-ppd.yaml`, and `data/indicators.yaml`. `docs/redundancy.md` lines 33-34 flag CC Bull/Bear as "drifted? — verify per-record" but no YAML record exists.

---

## Phase 2 — Static diff

### Layer 1 — Wrapper booleans (sigCCBull)

All 8 locations: `bool sigCCBull = conf and cc_bull_active`.

28 pairs: **all `identical`**. No drift at the wrapper level.

### Layer 2 — State-machine body (cc_bull_active — the actual logic)

Per `references/failure-modes.md` F2.1 ("Phase 2 says identical but fire bars differ — internal-helper drift under same boolean name"), Phase 2 drilled one level into `cc_bull_active`.

Three distinct groups found:

**Group A — Squarify (locations 1–4, all 4 squarify versions)**

Reset condition (clears chain):
```pine
if not (csNew1_Bull or csNew2_Bull)   // expands to: CS1 OR CS2 OR CS3 OR CS4
    cc_bull_active := false
```

Where `csNew1_Bull = comboSet1_Bull or comboSet2_Bull` and `csNew2_Bull = comboSet3_Bull or comboSet4_Bull`. Full expansion = all 4 comboSets.

**Group B — hvd-pbj-ppd THE_ONLY_ONE (location 6 — current canonical)**

Reset condition:
```pine
if not (comboSet3_Bull or comboSet4_Bull)   // CS3 + CS4 ONLY
    cc_bull_active := false
```

CS1 and CS2 are absent from the reset guard. Chain stays active even when CS1/CS2 go false.

**Group C — hvd-pbj-ppd legacy (locations 5, 7, 8 — predecessor and masterdir variants)**

Reset condition:
```pine
if not (comboSet1_Bull or comboSet2_Bull or comboSet3_Bull or comboSet4_Bull)
    cc_bull_active := false
```

All 4 comboSets explicitly listed. Equivalent to Group A in logic; different in naming.

### Pairwise classification table

| Pair | Verdict | Evidence (line ranges) | Drift artifact |
|---|---|---|---|
| 1 ↔ 2 (squarify 46v2 ↔ ATOMS) | `identical` | both L1303-L1312; same reset: `csNew1_Bull or csNew2_Bull` | none |
| 1 ↔ 3 (squarify 46v2 ↔ v1) | `identical` | L1301-L1312 vs L1227-L1238; same reset | none |
| 1 ↔ 4 (squarify 46v2 ↔ v2) | `identical` | both same reset; L1301-L1312 in each | none |
| 2 ↔ 3, 2 ↔ 4, 3 ↔ 4 | `identical` | same group A pattern | none |
| 5 ↔ 7 (1939 ↔ 2246) | `identical` | both Group C: CS1+CS2+CS3+CS4 | none |
| 5 ↔ 8 (1939 ↔ 4.26) | `identical` | both Group C: CS1+CS2+CS3+CS4 | none |
| 7 ↔ 8 | `identical` | same | none |
| 1 ↔ 5 (A ↔ C, squarify ↔ hvd-legacy) | `cosmetic-drift` | Group A uses named aliases (csNew1/csNew2) that expand to same 4 comboSets as Group C. Alpha-rename produces identical expression. | none (cosmetic; see drift artifact §csNew3 sub-drift) |
| 1 ↔ 6 (A ↔ B, squarify ↔ THE_ONLY_ONE) | **`semantic-drift`** | THE_ONLY_ONE resets on CS3+CS4 only; squarify resets on CS1+CS2+CS3+CS4. Different operand sets. | `docs/validation/2026-05-10-combo-chain-bull-drift-1.md` |
| 5 ↔ 6 (C ↔ B, legacy ↔ THE_ONLY_ONE) | **`semantic-drift`** | same: CS3+CS4 only vs CS1+CS2+CS3+CS4 | `docs/validation/2026-05-10-combo-chain-bull-drift-1.md` |

All other cross-group A↔C pairs: `cosmetic-drift` (same logic, different naming).
All other cross-group with B: `semantic-drift`.

### Secondary finding — IPSF asymmetry on `show_CCBull`

| Location | Treatment |
|---|---|
| squarify (all versions) | `bool show_CCBull = true` — hardcoded |
| hvd-pbj-ppd (THE_ONLY_ONE, 4.26) | `show_CCBull = input.bool(true, "CC Bull", group=grp_t1c, ...)` — user-tunable |

Verdict: `ipsf-asymmetry` — same parameter, hardcoded in squarify vs `input.bool` in hvd-pbj-ppd.

---

## Phase 3 — TV firing

| Path used | Why |
|---|---|
| BLOCKED-NEEDS-TV-FIRING-SKILL | `cc_bull_active` is a `var bool` stateful variable (`:=` updates on every bar). Phase B Python ports cannot faithfully replay stateful composites — the per-call state reset in Phase M produces zero fires regardless of input data. Path A (chart-side logger via `detection-plot-tv-firing` skill) is the only viable path. |

| Location | Fire-bar count | Query window | Status |
|---|---|---|---|
| squarify::sigCCBull | — | — | BLOCKED |
| hvd-pbj-ppd::sigCCBull | — | — | BLOCKED |

**Bar-set algebra**: N/A — BLOCKED.

**Followup**: invoke `detection-plot-tv-firing` skill when Anish is at his desk. Confirm which operand set matches expected fire bars on IREN, HOOD, CRWV or similar chart-side test session.

---

## Phase 4 — Reconcile

### Autonomous actions (no user required)

1. **YAML add — 8 missing records**: `sigCCBull` / `sigCCBear` are entirely absent from all extract YAMLs. Adding annotations to `bible-input/extract-squarify.yaml` (Group A) and `bible-input/extract-hvd-pbj-ppd.yaml` (Groups B + C) with `variant_kind` tags documenting the 3-way drift. This is informational — no canonical designation yet.

2. **IPSF-asymmetry flag on `show_CCBull`**: squarify hardcodes `true`; hvd-pbj-ppd exposes `input.bool`. Documenting in YAML `notes:` field. No Pine change needed until canonical is chosen.

### Pending user decision (HALT before applying)

The semantic drift between Group B (THE_ONLY_ONE — CS3+CS4 only reset) and Groups A+C (all-4-comboSets reset) requires Anish to answer:

> **Q: Is Combo Chain supposed to sustain as long as ANY combo stream fires (CS1/CS2/CS3/CS4 all tracked), or only as long as the "high-tier" streams (CS3+CS4) fire?**

- If **all 4 streams** → update THE_ONLY_ONE L1102 from `comboSet3_Bull or comboSet4_Bull` to `csNew1_Bull or csNew2_Bull`. Groups A+C are canonical (7 versions agree vs 1 outlier).
- If **CS3+CS4 only** → squarify and legacy hvd-pbj-ppd need updating. Group B (THE_ONLY_ONE) is canonical (1 version, but current canonical file).

| Finding | Proposed action | User approved | Applied | Commit SHA |
|---|---|---|---|---|
| drift-1: B↔A semantic-drift in cc_bull_active reset | `designate-canonical` then `pine-source-fix` on non-canonical side | PENDING | no | — |
| IPSF asymmetry: show_CCBull hardcoded in squarify | `promote-to-input` in squarify | PENDING | no | — |
| 8 missing YAML records | `add to extract YAMLs` (autonomous, informational) | auto-approved | yes | — |

**Generators run** (after autonomous YAML adds):

- `python3 tools/merge_extracts.py` — ✓ (Indicators: 28, Total roots: 456, Total composites: 420)
- `python3 tools/build_lineage_cards.py` — ✓ (166 lineage cards written)
- `python3 tools/build_docs.py` — ✓ (roots.md 456, composites.md 420, 28 visual trees)
- YAML == JSON byte-equivalent — ✓

---

## Final verdict

**DRIFT-PENDING-USER**

Three distinct implementations of the Combo Chain "active" reset condition exist across 8 Pine locations:
- Group A (squarify ×4) and Group C (hvd-pbj-ppd legacy ×3): cosmetic-drift (same logic, 7 versions agree)
- Group B (hvd-pbj-ppd THE_ONLY_ONE ×1 — current canonical): semantic-drift (watches CS3+CS4 only, not all 4 streams)

THE_ONLY_ONE is the lone outlier. The 7-version majority watches all 4 comboSets for the reset condition. Anish must confirm canonical intent before Pine fix is applied.

---

## Stage-7 followups

- [ ] **[BLOCKING]** Anish decides: all-4-comboSets reset (Groups A+C = canonical) vs CS3+CS4-only reset (Group B = canonical). Then apply `pine-source-fix` on the losing side.
- [ ] Run `detection-plot-tv-firing` skill on `sigCCBull` — verify fire bars on 3+ symbols. Confirm whether Group B or A/C fires on the "expected" Combo Chain bars from Anish's memory.
- [ ] Promote `show_CCBull` to `input.bool` in squarify (IPSF-asymmetry fix). Low priority; pending canonical decision.
- [ ] Update `docs/redundancy.md` lines 33-34 with the 3-way drift findings and resolution once decided.
- [ ] Add 8 `sigCCBull`/`sigCCBear` composite records to `bible-input/extract-squarify.yaml` and `bible-input/extract-hvd-pbj-ppd.yaml`, then run merge/regen pipeline.

---

## Provenance

- Skill version: detection-plot-validation v1.1.0
- Run started: 2026-05-10
- Run ended: 2026-05-10
- Prior partial run: `docs/validation/2026-05-10-combo-chain.md` (incomplete — drift artifact not written, YAML not updated, this report supersedes it)
- Subagents dispatched: Phase 1 = 0 (reused `docs/validation/2026-05-10-combo-chain-phase1.yaml`), Phase 2 = 0 (single parent), Phase 3 = 0 (BLOCKED)
- Parent agent: Claude (auto-mode)
- Phase 1 data source: `docs/validation/2026-05-10-combo-chain-phase1.yaml` (pre-existing scan of 54 Pine files)
