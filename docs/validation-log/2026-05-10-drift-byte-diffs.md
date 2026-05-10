# Drift byte-diff log — 2026-05-10

Stage 6.8 fact-finding pass. Byte-diffs the most-likely-drift candidates per
`docs/redundancy.md` (b) — internal-implementation drift inside roots.

**Method**: grep canonical primitives across every Pine file that names them;
compare boolean assignments line-by-line.

## Taxonomy

Three classes of finding (per `docs/glossary.md` "IPSF vs TRUE DRIFT"):

- **IPSF** — both copies are exposed as `input.*` in their respective files.
  Numeric default may differ but Anish can tune either in TradingView
  settings. **Not corruption.** False-alarm if mis-classified as drift.
- **TRUE DRIFT** — hardcoded constant divergence across files. Source-edit
  required to reconcile. Invisible to the user.
- **IPSF asymmetry** — same parameter is `input.*` in some files but
  hardcoded in others. Numeric values may match today, but tuning is
  asymmetric: changing the input-bound copy is a settings click; changing
  the hardcoded copy is a source edit. Real corruption risk over time.

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

## 3. GZI proximity defaults — IPSF (NOT drift)

| File | Line | Parameter name | Default | Pine binding |
|---|---|---|---|---|
| `hv-fvg-gz1-og/versions/HV_FVG_GZ1_OG_v1.pine` (canonical) | L21 | `gziProximity` | 6 | `input.int(6, "Max Bar Distance", ...)` |
| `proximity-gzi-hv/versions/PROXIMITY_GZI_HV_v1.pine` (variant) | L21 | `gziProximity` | 6 | `input.int(6, "Max Bar Distance", ...)` |
| `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L380 | `gz1_dist` | 7 | `input.int(7, "GZ1 Max Bar Distance", ...)` |

**Verdict: IPSF — both copies are `input.int(...)`.** Anish can change either
to match the other in TradingView settings. The 6-vs-7 default difference
is a packaging choice, not corruption.

**Action**: none required. If Anish wants the defaults to align, he
edits the Pine source's `input.int(...)` default values in source (or
just keeps the running TradingView setting overridden per-chart).
Recorded as informational in `docs/redundancy.md` "IPSF default
variation" subsection.

## 4. DISP σ-multiplier defaults — IPSF (NOT drift)

| File | Line | Parameter name | Default | Pine binding |
|---|---|---|---|---|
| `heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine` | L237 | `disp_strength` | 6.0 | `input.float(6.0, "Strength (σ multiplier)", ...)` |
| `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L358 | `i_std_min` | 3.0 | `input.float(3.0, "Min Mult", ...)` |
| `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | L351 | `i_std_min` | 3.0 | `input.float(3.0, "Min Mult", ...)` |

**Verdict: IPSF — all three copies are `input.float(...)`.** Tunable per
indicator on the TradingView settings panel.

The 6.0 default in heavy-pentagon vs 3.0 in HVDPBJPPD/Squarify is likely
intentional — heavy-pentagon's displacement engine is internal to its 15
Heavy Combo composites and runs at a stricter gate (6×); HVDPBJPPD's
Engine 3 displacement primitive feeds dozens of downstream composites
and runs at 3×.

**Action**: none required. False-alarm if mis-classified as drift.

## 5. pp_barSize / pp_lookback (PUP threshold + lookback) — IPSF ASYMMETRY (TRUE DRIFT-class concern)

| File | Line | Pine binding | Tunability |
|---|---|---|---|
| `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | L386 | `pp_barSize=3.0, pp_lookback=10` | **HARDCODED** — source-edit only |
| `b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine` | L74-L75 | `pp_barSize=input.float(3.0,...), pp_lookback=input.int(10,...)` | **IPSF** — TradingView-tunable |

**Verdict: IPSF asymmetry.** The numeric values match today (`3.0` and `10`),
so PUP fires identically across both indicators right now. But tuning is
asymmetric: changing `pp_barSize` from 3.0 to 2.5 is a settings click in
b2b-pup and a source-edit in HVDPBJPPD. Over time, the values WILL drift if
Anish tunes b2b-pup's input without remembering HVDPBJPPD has the constant
hardcoded.

**Action**: Stage 7 — promote HVDPBJPPD's hardcoded constants to `input.*`
to match b2b-pup, OR add a source comment in HVDPBJPPD pointing at b2b-pup
as the canonical PUP-tuning surface.

## 6. anyBearPent — namespace flag re-evaluated

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
| 2 | PUP boolean (hvd-pbj-ppd vs b2b-pup) | cosmetic name drift (`sigPUP` vs `det_PUP`); booleans byte-identical after inlining | optional Stage-7 unification |
| 3 | GZI proximity (6 vs 7 default) | **IPSF** — both `input.int(...)` | none required; tunable in TV settings |
| 4 | DISP σ-multiplier (6.0 vs 3.0 default) | **IPSF** — all three `input.float(...)` | none required; tunable in TV settings |
| 5 | pp_barSize / pp_lookback (HVDPBJPPD hardcoded vs b2b-pup IPSF) | **IPSF asymmetry** — values match today (3.0, 10) but tuning surfaces are asymmetric | Stage-7 promotion of HVDPBJPPD constants to `input.*` |
| 6 | anyBearPent rename target | plan correction | rename to `anyBearPenthouse` not `anyBear2F` |

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
