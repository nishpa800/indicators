# FIRST BAR FABLE — CHANGELOG

## 2026-07-23 — v4: S16/S17 offset fix, S36-S39, full-definition tooltip law

`versions/FIRST_BAR_FABLE_v4.pine` (v3 ingested verbatim alongside as
`versions/FIRST_BAR_FABLE_v3.pine` — provenance copy of the operator's upload).

### FIX — S16/S17 B2B Napalm rendered at the wrong bar (offset 0 → **-1**, gate fb01 → **fb12**)

- **Defect (operator-diagnosed):** v3 plotted S16/S17 at offset 0 with an fb01
  first-bar gate. But raw Napalm/Charge is a **-1 event**: its displacement bar
  is det bar[1] (B2B PUP v5.4 plots raw NPM with `offset=-1`; TNT OD v3 plots
  NPM ENR at -1). `det_b2bBullNapalm = NapCons and NapCons[1]` therefore maps to
  **visual** Napalm bars [1] and [2] — the back-to-back pair on the chart.
- **Law (Anish):** back-to-back means the **visual plots** are back-to-back.
  Measuring the visual plots has to take the offset.
- **Fix:** plot offset -1 (anchor = second visual bar of the pair = bar[1]);
  first-bar gate fb12 (pair passes when bar[1] OR bar[2] is the session's first
  bar). Detection booleans untouched — B2B PUP v5.4 Engine G port is verbatim.
- Note: B2B PUP v5.4 has **no** standalone "B2B Napalm" plot (its S13 is
  B2B NPM **+ B2B PUP**, anchored to the PUP pair at offset 0) — so there was no
  source offset to inherit; v3's 0 was a porter's choice and it contradicted the
  doctrine above.

### NEW — S36/S37: PBJ + Disp9 + HV3K+/NAG (bull/bear)

- `det_S36 = conf and sigBullPBJ and d9_bull and (det_HV3K or sigNagasaki)`
  (S37 = bear equivalents). All legs are bar[0] events → offset 0, gate fb0.
- `det_HV3K = conf and volume >= ta.highest(volume, i_3k_len)[1]` — same
  construction as the 4K test; `i_3k_len` operator-adjustable, **floor 3000**
  ("3,000 or above"). A 4000-bar HV bar is by construction also a 3000-bar HV
  bar (window 3000 ⊆ window 4000), so the 3000 floor includes the 4K rung;
  Nagasaki (all-time-high volume) OR'd in explicitly so charts younger than N
  bars still qualify.
- Tethered to the **"Displacement 9"** engine (σ default 9.0, adjustable) — not
  HV+D/DYNAMITE/TNT displacement.

### NEW — S38/S39: Swing Low + ANY FABLE / Swing High + ANY FABLE

- Swing = **Typhoon's Yin Yang pivot definition** (`ta.pivotlow`/`ta.pivothigh`
  Left/Right bars + ATR-distance filter vs the last valid swing level, highs and
  lows sharing that state) — but a **dedicated engine instance** (`f_swEngine`,
  `sw_` inputs, defaults 75/1/50/3.5) so tuning S38/S39 never disturbs Typhoon
  parity. Own input groups: "Swing (S38/S39) - Lookback / ATR Filter".
- ANY FABLE = `any_BULL or any_BEAR` (the det-time union of the 53 v2 rows,
  independent of every checkbox) evaluated **on the pivot bar**
  (`[sw_rightBars]`). S28-S39 excluded from the union (no recursion).
- Plot offset `-sw_rightBars` (anchors the pivot bar); first-bar gate `fbsw`
  reads `is_new_sess[sw_rightBars]`.

### TOOLTIP LAW — full definitions everywhere

- Every detection toggle now carries its complete definition in the tooltip —
  **no "bearish mirror" shorthand anywhere**. Rewritten: S12, S14, S16, S17,
  S18-S21, S23-S27, S29, S31, S33, S35, RC NPM+TNT Bear.
- The 20 HVD rows (Pipeline D CO ×4, B2B HV+D ×6, HV+D Momentum ×10) had **no
  tooltips at all** in v3 — all 20 now carry full definitions including offsets
  and first-bar gates.
- S3/S4 Typhoon tooltips now spell out the isolated swing high / swing low
  definitions and name the adjustable YY inputs.
- The 2of3/3of3 tooltips state the **PBJ requirement** explicitly: those rows
  require PBJ on bar[1]; the HVD+PUP/RVOL/CMB(/PPD) triangle rows only render
  when PBJ is ABSENT — so two triangles co-firing never implies 2of3 should
  fire (this was the operator's observed "bug"; it is the definition, working
  as coded in the HVD source).

### Audit

- Full adversarial offset audit (3 independent lenses per row-group) recorded in
  `OFFSET_AUDIT_v4.md`. Plot budget 57 → **61 of 64**.

### Flagged, unchanged (operator call needed)

- **S11/S12 Dynamite** and the **B2B HV+D group** are two-bar visual pairs on
  bars [1],[2] gated by `fb1` (bar[1] only). The header's B2B law ("pair touches
  the first bar") would imply `fb12`, as now used by S16/S17 and S26/S27
  (tnt-first). Left at `fb1` = source/v2 behavior; flagged in the audit table.
