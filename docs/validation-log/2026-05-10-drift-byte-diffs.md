# Drift byte-diff log — 2026-05-10

Stage 6.8 fact-finding pass. Byte-diffs the most-likely-drift candidates per
`docs/redundancy.md` (b) — internal-implementation drift inside roots.

**Method**: grep canonical primitives across every Pine file that names them;
compare boolean assignments line-by-line.

## 1. RVOL family — VERIFIED VERBATIM

`heavy-pentagon` is canonical. `heavy-combo-toggles` lifts the entire
RVOL-threshold ladder verbatim (per its CHANGELOG; verified by Stage-1
extraction agent and re-confirmed here).

```
$ diff <(grep -A 1 "f_saab_kratos_threshold\|th_saab_kratos\b" \
            heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine | head -10) \
       <(grep -A 1 "f_saab_kratos_threshold\|th_saab_kratos\b" \
            heavy-combo-toggles/versions/HEAVY_COMBO_TOGGLES_v1.pine | head -10)
(empty diff = identical)
```

**Verdict**: identical. No drift. No action.

## 2. PUP definitions across consumers — semantically equivalent, different names

| File | Line | Variable name | Boolean assignment |
|---|---|---|---|
| `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L626 | `sigPUP` | `conf and pp_priceUp and volume > pp_hiRedVol` |
| `b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine` | L78 | `det_PUP` | `conf and ((close-open)/open)*100 > pp_barSize and volume > pp_hiRedVol` |

`pp_priceUp` in hvd-pbj-ppd L625 expands to `((close-open)/open)*100 > pp_barSize`.
**Booleans are byte-identical after the inlining — drift is naming only.**

**Verdict**: cosmetic drift (variable name differs: `sigPUP` vs `det_PUP`).
Both consumers use the same threshold (`pp_barSize=3.0`) and the same
volume gate (`pp_hiRedVol = ta.highest(pp_redVol[1], pp_lookback=10)`).

**Recommendation**: bible already designates `b2b-pup::PUP` as canonical
(per Stage-1 extraction). Consider Stage-7 normalisation to unify the
variable name across both files (`sigPUP` on both, or `det_PUP` on both).

## 3. GZI proximity defaults — CONFIRMED DRIFT (6 vs 7)

| File | Line | Parameter name | Default |
|---|---|---|---|
| `hv-fvg-gz1-og/versions/HV_FVG_GZ1_OG_v1.pine` (canonical) | L21 | `gziProximity` | **6** |
| `proximity-gzi-hv/versions/PROXIMITY_GZI_HV_v1.pine` (variant) | L21 | `gziProximity` | 6 |
| `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L380 | `gz1_dist` | **7** |

**Verdict**: real numeric drift. `gz1_dist=7` in HVDPBJPPD's local copy
diverges from the canonical `gziProximity=6` by 1 bar.

**Recommendation**: Anish to decide whether HVDPBJPPD's GZI window should
align to canonical 6 or whether the +1 was intentional (e.g. to capture an
edge case the canonical misses). Until decided, the bible records both
values as the actual defaults; `data/indicators.yaml` annotates the
parameter on each indicator's GZI-related composite.

## 4. DISP σ-multiplier defaults — CONFIRMED DRIFT (3.0 vs 6.0)

| File | Line | Parameter name | Default |
|---|---|---|---|
| `heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine` | L237 | `disp_strength` | **6.0** |
| `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L358 | `i_std_min` | **3.0** |
| `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | L351 | `i_std_min` | **3.0** |

`b2b-pup`, `tnt-od`, `ultra-combo` did not surface a top-level DISP
σ-multiplier input under either name — they likely use hardcoded
multipliers inline or alternative parameter names. Followup grep needed.

**Verdict**: real semantic drift. heavy-pentagon's `disp_strength=6.0` is
2× the HVDPBJPPD/Squarify `i_std_min=3.0` for what is conceptually the
same gate (bar range exceeds N stdevs of recent ranges).

The handoff comment on PR #2 reported "5.0 elsewhere" but the search did
not corroborate that; either the 5.0 reference is a hardcoded constant
inside displacement helpers (not exposed as input) or my search missed a
parameter alias.

**Recommendation**: This is likely an INTENTIONAL difference — heavy-pentagon's
displacement engine is internal to its 15 Heavy Combo composites and
operates as a stricter gate (6×); HVDPBJPPD's Engine 3 is the displacement
primitive that feeds dozens of downstream composites and runs at 3×.
Bible records both defaults faithfully. No source change recommended
without Anish's call.

## 5. anyBearPent — namespace flag re-evaluated

The Stage-6.1 plan recommended renaming `anyBearPent` → `anyBear2F` to
free the `Pent` prefix from `heavy-pentagon::PENTAGON`. Re-examining the
source confirms:

- `anyBull2nd` (L1352 squarify canonical) = bull "2nd Floor" composite.
- `anyBearPent` (L1354 squarify canonical) = bear "Penthouse" composite.

These are DELIBERATELY ASYMMETRIC names (Floor/2F for bull, Penthouse for
bear), reflecting a domain convention. Renaming `anyBearPent → anyBear2F`
would erase the Penthouse concept and break the asymmetry.

**Better target**: `anyBearPent → anyBearPenthouse`. Frees the `Pent`
prefix while preserving the bull/bear naming asymmetry. Six-letter delta
(`enthouse`).

**Affected files** (5):

- `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` (canonical)
- `squarify/versions/SQUARIFY_v1.pine` (legacy)
- `squarify/backtests/SQUARIFY_v2_BT.pine`
- `squarify/backtests/SQUARIFY_v2_STATS.pine`
- `bible-input/extract-hvd-pbj-ppd.yaml` (one cross-reference note)

**Recommendation**: defer to Anish. The rename is mechanical (`sed -i
's/\banyBearPent\b/anyBearPenthouse/g'` across the 5 files) but should not
be applied without confirming it doesn't break alerts or anything that
references the old name externally.

## Summary table

| # | Candidate | Verdict | Action |
|---|---|---|---|
| 1 | RVOL ladder (heavy-pentagon → heavy-combo-toggles) | identical | none |
| 2 | PUP (hvd-pbj-ppd vs b2b-pup) | cosmetic-drift | optional Stage-7 name unification |
| 3 | GZI proximity (6 vs 7) | semantic drift | Anish decision |
| 4 | DISP σ-multiplier (3.0 vs 6.0) | semantic drift, likely intentional | Anish decision |
| 5 | anyBearPent rename target | plan correction | rename to `anyBearPenthouse` not `anyBear2F` |

Pending byte-diffs (not run this session — would extend the file beyond
useful bounds):

- PBJ Engine 6 internals (Zoo MA + Supertrend + PB&J filter) across
  hvd-pbj-ppd / b2b-pup / squarify / tnt-od / ultra-combo. ~140 lines per
  file; needs a dedicated session.
- FAUNA component definitions (MB/RE/TA) — ultra-combo locks the formula;
  consumers may have drifted internal helpers.
- Combo Chain (rolling 4-bar window for ≥2 hits) across hvd-pbj-ppd /
  squarify.

These three are now scheduled as Stage-7 follow-ups and called out in the
PR handoff comment.
