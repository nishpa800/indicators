# Heavy PENTAGON ⭐

**Canonical RVOL engine for the entire indicator suite.** Every other
indicator that references SAAB / Kratos / RVOL_1X / Grand Slam / MOAB /
Pentagon / WTC / Hiroshima / Nagasaki traces back to this file.

`heavy-combo-toggles/` lifts its 5 base combos and 15 directional combo
booleans verbatim (Stage-1 byte-diff verified).

## Standalone detections (10 roots)

- **Pipeline 1 (Standard RVOL — `bb_normalizedPrice` spike)**
  SAAB, Kratos, RVOL 1× bull/bear, Grand Slam, MOAB
- **Pipeline 2 (Reg@Time RVOL — `relVolRatio`)**
  Pentagon, WTC, Hiroshima
- **Pipeline 3 (All-Time High Volume — vs running max)**
  Nagasaki (HEV)

## Heavy Combo composites (15 tier-1)

Stage-5 post-plot co-occurrence, gated by an internal displacement
classifier (`dispBull` / `dispBear` / `noDisp`) into Bull/Bear/Neutral
buckets:

- Heavy Yin-Yang (P1 + P2) × 3
- Heavy Nagasaki (P3 + P1) × 3
- Heavy Nagasaki Vol (P3 + P2) × 3
- Heavy Trident (P1 + P2 + P3) × 3
- Neutral Heavy x2 (P2 × P2) × 3

## Phantom toggles (no logic connected)

FAUNA bull/bear, DISP A/B/C bull/bear, LONG 1/2, SHORT 1/2, HV 75/150/250/500/1000,
Hot Spot — placeholders for future engines.

## Files

- `versions/HEAVY_PENTAGON_v1.pine` — canonical (25.2 KB, Pine v5).

## Bible

- `bible-input/extract-heavy-pentagon.yaml` — full extraction (10 roots, 15 composites)
- `docs/lineage/heavy-pentagon__*.md` — lineage cards for each Heavy Combo
- `test-indicators/versions/ROOTS_VOLUME_TEST_v1.pine` — Stage-2 test rig

## Branch provenance

Lives on `claude/add-txt-indicator-format-b4FUu` — not on `main` as of bible
Stage 1.
