# Validation report — `B2B PUP` + `B2B Napalm` (combined VALIDATE 5 + 6)

_Skill: `detection-plot-validation` v1.1.0. Run on 2026-05-10. Path: docs/validation/2026-05-10-b2b-pup-b2b-napalm.md._

## VALIDATE 5 — B2B PUP

### Summary

| Field | Value |
|---|---|
| Target | `det_b2bPUP` / `det_b2bPPD` (B2B PUP) |
| Canonical location | `b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine` L978 |
| Definition | `bool det_b2bPUP = det_PUP and nz(det_PUP[1])` (lagged AND — current bar PUP + previous bar PUP) |
| Symmetric bear | `bool det_b2bPPD = det_PPD and nz(det_PPD[1])` |
| Other DEFINITIONs | (none — B2B PUP is uniquely defined in b2b-pup) |
| Verdict | **OK** — single canonical location; no drift possible by definition |

### Composition tree

```
det_b2bPUP                                                       (L978)
├── det_PUP                                                       (L78, b2b-pup) — bullish ≥3% body + opposite-color volume
└── nz(det_PUP[1])                                                 (same boolean, lagged 1 bar)
```

The `nz(...)` wraps the shift to default to false for the first bar (where bar-history isn't yet available). Identical pattern to Squarify's Unified Combo (which uses lagged AND for csNew2_Bull).

### S-plot consumers (B2B PUP is used in)

| S-plot | Composition |
|---|---|
| S1 (B2B PUP) | `fire_S1_bull = en_S1 and det_b2bPUP and g01 and masterGate` |
| S2 (B2B PUP + FAUNA) | `det_b2bPUP and FAUNA on both candles` |
| S3 (B2B PUP + DISP) | `det_b2bPUP and DISP/HV+D on both` (lagged) |
| S4 (B2B PUP + FAUNA + DISP) | combined |
| S5 (B2B PUP + SAAB) | `det_b2bPUP and directional RVOL on both candles` |
| S6 (Any B2B + PBJ) | OR-chain |
| S8 (UC + B2B PUP) | `det_b2bPUP and Unified Combo` |
| S9 (Uni Combo + B2B PUP) | `det_b2bPUP and (S19 or S20)` |
| S10 (L1 B2B + B2B PUP) | `det_b2bPUP and Long 1 B2B` |
| S11-S15 | various B2B PUP + other-signal combos |

20+ numbered S-plots in b2b-pup depend on B2B PUP. The integrity of every one of them hinges on `det_b2bPUP` being correctly implemented. Phase 2 verdict for the wrapper: ✓ correct.

### Phase 2 — Static diff

Single location. No pairs to diff. Verdict: **OK** (single canonical implementation; the bible's b2b-pup family designates this file as canonical).

### Phase 3 — TV firing

BLOCKED-NEEDS-TV-FIRING-SKILL (Path B inaccessible). The b2b_pup Python pack covers all 37 S-plots per the parallel session's handoff (52/52 tests pass for the stateless ones; stateful stubbed). When run via TV firing skill, the agreement set across S1-S15 will reveal whether `det_b2bPUP` fires on the bars Anish expects.

### Phase 4 — Reconcile

No action — single canonical location, no drift.

### Verdict

**OK-PENDING-TV-FIRING** — clean single-location definition; runtime confirmation via TV firing skill recommended.

---

## VALIDATE 6 — B2B Napalm

### Summary

| Field | Value |
|---|---|
| Target | `p_b2bBull` / `p_b2bBear` (B2B Napalm) |
| DEFINITION locations | 4 (TNT_OD_v1.pine, TNT_OD_v2.pine, TNT_OD_v3.pine, TNT_Opening_Drive_OD_v3_2026-05-04.pine) |
| Phase 2 verdicts | 3 of 6 pairs `identical` (v1↔v2, v1↔2026-05-04, v2↔2026-05-04); 3 pairs are v3 vs the others — v3 adds `nz(gate_bull[1])` per documented CHANGELOG enhancement (NOT drift). |
| Verdict | **OK** (no drift; v3 enhancement is intended per CHANGELOG) |

### DEFINITIONs

| File | Line | Boolean (full) |
|---|---|---|
| `tnt-od/versions/TNT_OD_v1.pine` | 915 | `det_bullNapalm and not supp_bullNPM and (det_bullNapalm[1] == true) and not na(sessionFirstBarIdx) and (bar_index - 2) >= sessionFirstBarIdx and en_b2bBull` |
| `tnt-od/versions/TNT_OD_v2.pine` | 1030 | (identical to v1) |
| `tnt-od/versions/TNT_Opening_Drive_OD_v3_2026-05-04.pine` | 1030 | (identical to v1) |
| `tnt-od/versions/TNT_OD_v3.pine` | 1247 | (identical to v1) **+ `and nz(gate_bull[1])`** |

### Phase 2 verdict

**OK with documented enhancement** — v1/v2/2026-05-04 are byte-identical (3 pairs `identical`). v3 differs only by adding `and nz(gate_bull[1])` per the documented TNT-OD v3 CHANGELOG entry #1: "B2B NAPALM ... now ALSO requires ANY of: RVOL 1x / Grand Slam / Unified Combo / Nagasaki+Any / HCT / Displacement ≥ gateStdMult." This is INTENDED, not drift.

### Phase 3 — TV firing

BLOCKED-NEEDS-TV-FIRING-SKILL. Path B `tnt_od` pack covers B2B Napalm (per parallel session's 42 detections + 48 tests). Phase 3 confirms whether the v3 gate addition actually filters as expected.

### Phase 4 — Reconcile

No action — no drift detected; v3 enhancement properly localised.

### Verdict

**OK** — B2B Napalm is clean across all 4 TNT-OD versions. v3 enhancement properly localised. TV firing recommended for runtime verification of gate behaviour.

---

## Combined Stage-7 followups

- [ ] Run `detection-plot-tv-firing` skill on `det_b2bPUP` / `det_b2bPPD` — confirm fire bars match Anish's expectations across S1-S15 consumers
- [ ] Run `detection-plot-tv-firing` skill on `p_b2bBull` / `p_b2bBear` — confirm v3 gate enhancement filters NPM-family Tier 1 as the CHANGELOG specifies
- [ ] Cross-reference: when B2B PUP fires on bar N, does B2B Napalm tend to fire on the same N or N-1? (Cross-condition style — informational, not a validation requirement)
