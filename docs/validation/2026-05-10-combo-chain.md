# Validation report — `Combo Chain`

_Skill: `detection-plot-validation` v1.1.0. Run on 2026-05-10. Path: docs/validation/2026-05-10-combo-chain.md._

## Summary

| Field | Value |
|---|---|
| Target | `sigCCBull` / `sigCCBear` (Combo Chain) — wraps stateful `cc_bull_active` / `cc_bear_active` |
| Aliases resolved | COMBO_CHAIN_BULL, COMBO_CHAIN_BEAR, ComboChain, comboChain, combo_chain, CC, sigCCBull, sigCCBear, etc. |
| Indicator families with occurrences | 2 primary (squarify, hvd-pbj-ppd) |
| DEFINITION locations | **8 wrappers + 8 state-machine bodies** (the wrappers are identical; the state-machine bodies have **3 distinct semantic groups**) |
| Phase 2 verdicts | wrapper-only: 28 pairs `identical`. State-machine body: **TRIPLE SEMANTIC DRIFT** (Group A vs B vs C) |
| Phase 3 path used | BLOCKED-NEEDS-TV-FIRING-SKILL (Path B requires `realtime-indicators` repo not pushed) |
| Phase 4 reconcile actions | YAML annotation; no Pine source modification |
| Final verdict | **DRIFT-PENDING-TV-FIRING** — three distinct implementations of "Combo Chain active" condition |

## Phase 1 — Enumeration

8 DEFINITION locations of `sigCCBull` / `sigCCBear` (wrapper). All identical wrappers around `cc_bull_active` / `cc_bear_active` state vars. The state-machine logic IS the actual implementation.

Per failure-mode F2.1 (`references/failure-modes.md`), Phase 2 drilled into the immediate helper `cc_bull_active`.

## Phase 2 — Static diff

### Wrapper diff (top-level booleans)

All 8 locations: `bool sigCCBull = conf and cc_bull_active`. Identical.

### State-machine body diff (where the drift lives)

Three distinct semantic groups detected at the `cc_bull_active :=` reset condition:

| Group | Locations | Reset condition (clears `cc_bull_active`) | Operand count |
|---|---|---|---|
| **A — Squarify** | SQUARIFY_46_v2 L1303 · SQUARIFY_v1 L1229 · SQUARIFY_v2 L1303 · SQUARIFY_ATOMS_v1 L1311 | `if not (csNew1_Bull or csNew2_Bull)` | **2** (CS1 + CS2 only) |
| **B — HVDPBJPPD THE_ONLY_ONE** | THE_ONLY_ONE.pine L1102 | `if not (comboSet3_Bull or comboSet4_Bull)` | **2** (CS3 + CS4 only — different from A!) |
| **C — HVDPBJPPD legacy** | HVDPBJPPD_1939 L1037 · HVDPBJPPD_2246 L1011 · HVDPBJPPD_4.26.1244am L1037 | `if not (comboSet1_Bull or comboSet2_Bull or comboSet3_Bull or comboSet4_Bull)` | **4** (CS1 + CS2 + CS3 + CS4 — widest) |

### What the drift means

- **Group A (Squarify, 4 versions)**: Combo Chain stays active as long as either CS1 (FVG combo) OR CS2 (Matrix combo) is still firing on some recent bar. Narrowest of the three because csNew naming suggests it only watches the first two combo streams.
- **Group B (THE_ONLY_ONE only — 1 version)**: Combo Chain stays active as long as either CS3 (Unified combo) OR CS4 (whatever CS4 is in HVDPBJPPD) is still firing. **Different operands** from Group A entirely.
- **Group C (HVDPBJPPD legacy, 3 versions)**: Combo Chain stays active as long as ANY of CS1-CS4 is still firing. Widest — most permissive.

THE_ONLY_ONE.pine, the file currently designated canonical, has the NARROWEST and most idiosyncratic clear condition (only CS3/CS4). The legacy 3 versions are the widest. Squarify is between (operates on FVG+Matrix combos, the named primitives that feed CS3 anyway).

### Drift finding

See `docs/validation/2026-05-10-combo-chain-drift-1.md` (to be written separately; verdict for now: needs Anish's domain decision).

## Phase 3 — TV firing

**Status**: BLOCKED-NEEDS-TV-FIRING-SKILL.

**Why**: Combo Chain is STATEFUL (`var bool cc_bull_active = false`; updates `:=` on every bar). Path B Python ports return zero on stateful composites per Phase M state-threading limitation. Even if `realtime-indicators` repo were accessible, this target would BLOCK.

Path A (chart-side TV MCP via the spinout skill) is required for runtime verification. Anish runs that when at his desk.

## Phase 4 — Reconcile

No Pine modification. YAML annotation: marking THE_ONLY_ONE's `cc_bull_active` as `variant_kind: semantic-drift-narrowest-operands`; marking HVDPBJPPD legacy versions as `variant_kind: semantic-drift-widest-operands`; marking Squarify as the most-consistent group (4 versions agree) with `variant_kind: semantic-drift-csNew-naming`.

Anish's domain knowledge determines which is canonical:
- Is "Combo Chain" supposed to track ALL four combo streams (Group C)?
- Or just the unified-combo end (Group B)?
- Or just FVG + Matrix combos (Group A)?

## Final verdict

**DRIFT-PENDING-TV-FIRING** with **3 distinct implementations**. This is worse than Unified Combo (which had 2). Combo Chain has the highest drift load in the bible.

## Stage-7 followups

- [ ] Run `detection-plot-tv-firing` skill on `sigCCBull` / `sigCCBear` — confirm which operand set fires on Anish's expected bars
- [ ] Decide canonical: A (Squarify narrowest), B (THE_ONLY_ONE narrowest-different-operands), C (HVDPBJPPD legacy widest)
- [ ] Resolve csNew1/csNew2 vs comboSet1/comboSet2 naming — are they aliases for the same primitives or genuinely different?
- [ ] Update `docs/redundancy.md` (b) with this 3-way drift entry
- [ ] Create a new versioned Pine file for the chosen canonical (per standing-approval mantra)
