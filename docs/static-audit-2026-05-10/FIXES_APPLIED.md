# YAML Drift Fixes Applied — 2026-05-10

Based on Path B static audit findings. All fixes update YAML to match Pine (canonical source).
No Pine files were modified.

---

## Files Modified (8 total)

### 1. `bible-input/extract-hv-ladder-50-to-1k.yaml`
**Drifts fixed: 3 plot locations**
- `hv-ladder-50-to-1k::HV50` — `location: belowbar` → `location: bottom`
- `hv-ladder-50-to-1k::HV150` — `location: belowbar` → `location: bottom`
- `hv-ladder-50-to-1k::HotSpot` — `location: belowbar` → `location: bottom`

Pine source: `HV_LADDER_50_TO_1K_v1.pine` uses `location.bottom` for all three plotshapes. YAML had `belowbar` (wrong enum value — `belowbar` and `bottom` are distinct Pine constants).

---

### 2. `bible-input/extract-hv-ladder-100-to-1k.yaml`
**Drifts fixed: 3 plot locations**
- `hv-ladder-100-to-1k::HV100` — `location: belowbar` → `location: bottom`
- `hv-ladder-100-to-1k::HV200` — `location: belowbar` → `location: bottom`
- `hv-ladder-100-to-1k::HotSpot` — `location: belowbar` → `location: bottom`

Same fix as 50-to-1k variant. Pine uses `location.bottom`.

---

### 3. `bible-input/extract-heavy-weapons.yaml`
**Drifts fixed: 4 composite compositions**
- `COMBO_SET_1_BULL` — restructured from flat AND of 5 operands to nested `(BULL_GZI OR BULL_HV) AND (SAAB OR RVOL_1X_BULL OR GRAND_SLAM)`
- `COMBO_SET_1_BEAR` — restructured from flat AND of 5 operands to nested `(BEAR_GZI OR BEAR_HV) AND (KRATOS OR RVOL_1X_BEAR OR MOAB)`
- `COMBO_SET_2_BULL` — restructured from flat AND of 6 operands to nested `(BULL_GZI OR BULL_HV) AND (PENTAGON OR WTC OR HIROSHIMA OR NAGASAKI)`
- `COMBO_SET_2_BEAR` — restructured from flat AND of 6 operands to nested `(BEAR_GZI OR BEAR_HV) AND (PENTAGON OR WTC OR HIROSHIMA OR NAGASAKI)`

Pine: these combos are `(GZI OR HV) AND (SAAB OR 1x OR GrandSlam)` — the GZI/HV operands are OR'd, and the RVOL operands are OR'd. A flat AND of all operands would mean EVERY operand must fire simultaneously, which is wrong.

---

### 4. `bible-input/extract-anish-tb-foster.yaml`
**Drift status: Already correct in YAML**
The task specified changing `BearPBJ` shape from `diamond` to `labeldown`. The current YAML already had `shape: labeldown` at line 251. Audit report caught a historical state; the YAML was already correct. No change made to avoid introducing a regression.

---

### 5. `bible-input/extract-heavy-uncap.yaml`
**Drifts fixed: 1 line range**
- `heavy-uncap::HOT_SPOT` — `pine_source_line_range` changed from `"L590-L601"` to `"L651-L665 (def), L746 (plot)"`

Verified by grepping `HEAVY_UNCAP_v1.pine`: calendar window definitions are at L651-L665, plotshape at L746.

---

### 6. `bible-input/extract-yin-yang-displacement-pbj.yaml`
**Drifts fixed: 2 roots (mutex gate + textcolor)**
- `yin-yang-displacement-pbj::ResistanceRejection` — added `and not breakdownDetected` mutex gate to definition; added `textcolor: color.blue` to plot block
- `yin-yang-displacement-pbj::SupportRejection` — added `and not breakoutDetected` mutex gate to definition; added `textcolor: color.purple` to plot block

Pine L111/L112: both plotshapes gate with mutex to prevent co-firing when a structural break is simultaneously detected on the same bar. YAML previously omitted both the gate condition and the textcolor parameter.

---

### 7. `bible-input/extract-b2b-pup.yaml`
**Drifts fixed: 3 composite compositions**

**S3 (Fix #6):** Changed from free-mix AND_OR to two disjoint OR paths:
- DISP path: `PUP[-1] AND PUP[-2] AND DISPBull AND DISPBull[-1]`
- HVD path: `PUP[-1] AND PUP[-2] AND HVDBull AND HVDBull[-1]`
Pine implements `det_S3_bull` (DISP-only) and `det_S3d_bull` (HVD-only) as separate booleans, OR'd via `det_S3_any_bull`. Cross-type mixing (DISP on one bar, HVD on other) is silently disallowed.

**S4 (Fix #6):** Same disjoint-path restructure as S3, now also requiring FAUNA:
- DISP path: PUP+FAUNA on both bars AND DISPBull on both bars
- HVD path: PUP+FAUNA on both bars AND HVDBull on both bars

**S8 (Fix #7):** Corrected the B2B_PUP arm UC lag rule:
- B2B_PUP arm: `det_b2bPUP AND det_UnifiedBull` (current bar ONLY — no `[-1]`)
- S3-chain arm: `det_S3_any_bull AND (det_UnifiedBull OR det_UnifiedBull[-1])` (current or prior)
YAML previously implied both arms accept UC on bar[-1]. Pine L996 shows only the S3-chain arm uses `nz(det_UnifiedBull[1])`.

---

### 8. `bible-input/extract-heavy-pentagon.yaml`
**Drifts fixed: 6 composite compositions**

**HEAVY_YIN_YANG (Bull/Bear/Neutral):** Changed from flat AND of 7 operands to `(groupA OR groupB)`:
- groupA = any P1 directional: `RVOL_1X_BULL OR GRAND_SLAM OR RVOL_1X_BEAR OR MOAB`
- groupB = any P2 neutral: `PENTAGON OR WTC OR HIROSHIMA`
Structure: `groupA AND groupB`. Pine: `baseYinYang = (groupA_Bull or groupA_Bear) and groupB`. Flat AND would require ALL 7 to fire simultaneously — impossible in practice.

**NEUTRAL_HEAVY_X2 (Bull/Bear/Neutral):** Changed from AND-of-3 P2 tiers to 2-of-3 OR structure:
- `(PENTAGON AND WTC) OR (PENTAGON AND HIROSHIMA) OR (WTC AND HIROSHIMA)`
Pine: `baseNHx2 = (sigPentagon and sigWTC) or (sigPentagon and sigHiroshima) or (sigWTC and sigHiroshima)`. YAML AND-of-3 would require all three to fire simultaneously.

---

### 9. `bible-input/extract-hvd-pbj-ppd.yaml`
**Drifts fixed: 6 entries**

**CS1_FVG_BULL / CS1_FVG_BEAR — composition offset (Fix #9):**
- Both changed from `offset: 0` to `offset: -1` in both the top-level field and inline within the composition map
- Pine plot_call already had `offset=-1`; the composition.offset was the mismatching field

**SUPER_BULL / SDUPER_BULL — RVOL operand name (Fix #11):**
- `RVOL_1x` → `RVOL_1X_BULL` in SUPER_BULL composition
- `RVOL_1x` → `RVOL_1X_BULL` in SDUPER_BULL composition

**SUPER_BEAR / SDUPER_BEAR — RVOL operand name (Fix #11):**
- `RVOL_1x_bear` → `RVOL_1X_BEAR` in SUPER_BEAR composition
- `RVOL_1x_bear` → `RVOL_1X_BEAR` in SDUPER_BEAR composition

Pine uses `sigBullRVOL1x` / `sigBearRVOL1x` (directional). YAML previously used `RVOL_1x` which is ambiguous and could be confused with the neutral Pentagon-family tier (sigPentagon). Updated to match the declared `heavy-pentagon::RVOL_1X_BULL/BEAR` IDs.

---

### 10. `bible-input/extract-squarify.yaml`
**Drifts fixed: 2 composite entries**

**S1_SD_BANG — PUP operand semantics (Fix #10):**
- `squarify::PUP[1]` → `sigPUP[1]`
- Added `composition_note` documenting that Pine uses `nz(sigPUP[1])` where `sigPUP` is the raw single-bar PUP atom, not `det_b2bPUP` (the B2B composite). This prevents downstream tooling from incorrectly resolving the operand to the B2B version.

**S3_HW — operand names (Fix #10):**
- `squarify::ANY_FLOOR` → `squarify::S4_FLOOR`
- `squarify::ANY_2F` → `squarify::S5_2F`
`ANY_FLOOR` and `ANY_2F` are not declared roots in the YAML schema. The actual Pine variables `floor_sq`/`floor2_sq` correspond to the S4/S5 composites. Using declared composite IDs makes cross-references unambiguous and verifiable.

---

## Build Pipeline Results

All four pipeline steps ran cleanly after fixes:

```
python3 tools/merge_extracts.py
  Indicators: 28 | Roots: 456 | Composites: 418 | YAML == JSON: True

python3 tools/build_lineage_cards.py
  166 top-level composites/chains → 166 lineage cards + INDEX.md

python3 tools/build_docs.py
  docs/roots.md (456 roots)
  docs/composites.md (418 composites)
  docs/redundancy.md
  28 visual trees → docs/visual-trees/
  INDICATORS_INDEX.md

python3 tools/build_commonality_table.py
  docs/cross-variant-commonality.md
  Shared roots: 123 | Unique roots: 173 | Shared composites: 49
```

---

## Drifts NOT Fixed (requires Anish decision)

Per the caller's instructions, the following drifts were intentionally left flagged and not fixed:
- e3-f2-cluster bull/bear threshold asymmetry (0.1 vs 0.5)
- e3-f2-cluster bear double-gate
- vob-single-sens-with-tables filename mismatch
- heavy-pentagon HEAVY_YIN_YANG Bull-accepts-bearish-RVOL (confirm intentional)
- heavy-uncap any other line ranges beyond HOT_SPOT
