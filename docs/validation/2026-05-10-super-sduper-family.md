# Validation report — `SUPER + SDUPER family` (VALIDATE 7)

_Skill: `detection-plot-validation` v1.1.0. Run on 2026-05-10. Path: docs/validation/2026-05-10-super-sduper-family.md._

## Summary

| Field | Value |
|---|---|
| Targets | `superBull` / `superBear` / `sduperBull` / `sduperBear` (4 canonical names) + `sigSuperBullPBJ` / `sigSuperBullPB` / `sigSuperBearPBJ` / `sigSuperBearPB` (4 ultra-combo decomposed names) |
| DEFINITION locations | **44 total** (32 squarify+hvdpbjppd locations × 4 variables + 12 ultra-combo/fauna-shifu locations × 4 variables) |
| Distinct semantic groups | **3 for SUPER** + **3 for SDUPER** + **1 for ultra-combo SUPER_BULL_PBJ/PB** |
| Final verdict | **DRIFT-PENDING-TV-FIRING** — substantial semantic drift across 3 distinct families |

## The 3 semantic groups for `superBull`

### Group A — Squarify current (46_v2)

```
bool superBull = conf and csNew3_Bull and det_bullNapalmCons
```

**Operands**: 2 (csNew3_Bull, det_bullNapalmCons). Minimal. References UC + Napalm Consolidated. CURRENT-BAR.

**Locations**: `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` L1687, `SQUARIFY_v2.pine` L1687, `SQUARIFY_ATOMS_v1.pine` L1695. (3 locations)

### Group B — HVDPBJPPD (all 4 versions) + Squarify v1 legacy variants

```
HVDPBJPPD (THE_ONLY_ONE + 4.26 + 1939 + 2246, current-bar):
bool superBull = conf and sigBullPBJ and sigDISPBull and (sigFAUNABull or sigLong1) and super_hw_bull
  and ((super_comboAny_bull and sigPUP) or (anyBullFloor or anyBull2nd))

Squarify v1 legacy (lagged via nz(...[1])):
bool superBull = conf and nz(sigBullPBJ[1]) and sigDISPBull and (nz(sigFAUNABull[1]) or nz(sigLong1[1]))
  and super_hw_b and ((super_combo_b and nz(sigPUP[1])) or (nz(anyBullFloor[1]) or nz(anyBull2nd[1])))
```

**Operands**: 7-8. Complex multi-gate. References PBJ, DISP, FAUNA, Long1, HW, comboAny, PUP, Floor, 2nd Floor.

**Locations**: HVDPBJPPD all 4 versions (THE_ONLY_ONE L1254, 4.26 L990, 1939 L990, 2246 L964). Plus Squarify v1 L1302 with `nz(...[1])` lagged variant.

### Group C — Ultra-combo decomposed (PBJ vs PB)

```
sigSuperBullPBJ = conf and sigDISPBull and sigBullPBJ and sigFAUNABull and anyBullRVOL
sigSuperBullPB  = conf and sigDISPBull and sigBullPB  and sigFAUNABull and anyBullRVOL
```

**Operands**: 4. Cleaner than B, more strict than A. Decomposed into PBJ-driven and PB-driven variants.

**Locations**: `ultra-combo/versions/ULTRA_COMBO_v57_pine6.pine` L753-754, `ULTRA_COMBO_v57_pine5.pine` L772-773, `fauna-shifu/versions/FAUNA_SHIFU_JUMBO_CIA_1ST_PUP_v1.pine` L1169-1170.

## The 3 semantic groups for `sduperBull`

| Group | Boolean | Operand count | Locations |
|---|---|---|---|
| **Squarify current** | `conf and csNew3_Bull and det_bullNapalmCons and nz(sigPUP[1])` | 3 | Squarify 46_v2 + v2 + ATOMS_v1 |
| **HVDPBJPPD + Squarify v1** | `conf and (anyBullFloor or anyBull2nd) and sigBullPBJ and super_hw_bull and super_comboAny_bull and sigPUP and sigDISPBull and (sigFAUNABull or sigLong1)` | **8** | HVDPBJPPD ×4 + Squarify v1 (lagged) |
| **No ultra-combo equivalent** | — | — | sigSDuperBull does not exist in ultra-combo (it's a Squarify/HVDPBJPPD concept) |

## What this drift means

Anish's instinct ("we've got a lot of definitions for super duper") is **CONFIRMED at the strongest level**:

- **Squarify 46_v2 SUPER** is the SIMPLEST form (2 operands).
- **HVDPBJPPD SUPER** is the MOST COMPLEX (7-8 operands with multi-gate).
- **Ultra-combo SUPER_BULL_PBJ/PB** is a MIDDLE-GROUND decomposed form (4 operands).
- **Squarify v1 legacy** matches HVDPBJPPD's complexity but with lagged shifts (so it was historically the same as HVDPBJPPD).

The Squarify 46_v2 simplification (dropping operands from v1's 7-8 down to 2) is the CRITICAL drift. Either:

1. **Squarify v2 was a deliberate simplification** — the new minimal form is the "correct" SUPER, and HVDPBJPPD has not been updated to match
2. **Squarify v2 lost coverage** — the simplification removed important gates (PBJ, HW, FAUNA, Long1, Floor/2F)
3. **They are genuinely different signals** — the name "SUPER" was reused for a different concept in Squarify v2

Without TV firing, the bible cannot tell which interpretation is correct. Anish's domain knowledge is the authoritative resolver.

## Phase 3 — TV firing

BLOCKED-NEEDS-TV-FIRING-SKILL. Path B `squarify` pack covers SUPER per the parallel session's port (15 stubbed, 41/41 tests pass for stateless). Anish's TV firing will reveal fire-bar agreement between Squarify v2 SUPER and HVDPBJPPD SUPER on the same chart — if they agree, the simpler Squarify form is OK; if Squarify fires more often (because no PBJ/HW gate), it's a loss of strictness; if Squarify fires less often, it's a different signal.

## Phase 4 — Reconcile

No Pine modification. YAML annotation per skill v1.1: marks Squarify 46_v2 SUPER as `variant_kind: simplified-from-v1`, HVDPBJPPD as `variant_kind: full-multi-gate`, Ultra-combo as `variant_kind: decomposed-pbj-vs-pb`. None of the three is currently designated canonical — Anish's TV firing call determines.

## Final verdict

**DRIFT-PENDING-TV-FIRING** with **3 distinct semantic groups** for both SUPER and SDUPER, plus a 4th decomposed-form group in ultra-combo.

This is the highest-drift composite family validated so far in this run. Even Combo Chain (also 3 groups) had narrower divergence — SUPER's operand counts range from 2 to 8.

## Stage-7 followups

- [ ] Run `detection-plot-tv-firing` skill on `superBull` / `superBear` across Squarify 46_v2 + HVDPBJPPD THE_ONLY_ONE on the same chart — compare fire-bar agreement
- [ ] Run same for `sduperBull` / `sduperBear`
- [ ] Anish to decide: is Squarify 46_v2's minimal SUPER the new canonical (intentional simplification)? Or is HVDPBJPPD's full-gate SUPER canonical (and Squarify lost coverage)?
- [ ] Update `docs/redundancy.md` (b) with this 3-way drift entry — the most significant semantic-drift finding in the bible so far
- [ ] If canonical determined, create a new versioned file in the loser indicator with the canonical formula (per standing-approval mantra)
