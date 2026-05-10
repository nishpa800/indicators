# Redundancy / Drift Table

Two kinds of entries:

**(a) Composition drift / namespace collisions** — same name, different composition or definition across indicators.

**(b) Internal-implementation drift** — same name, same composition, different internal Pine math. Detected by byte-diffing root function definitions across files.

YAML mirror: `data/indicators.yaml` `redundancy:` section.

---

## (a) Composition drift / namespace collisions

### FLOOR

| Where | Composition |
|---|---|
| `hvdpbjppd::FLOOR_BULL` (`anyBullFloor`) | `bull_pp AND PBJ AND HW-slot` (HW-slot = RVOL1x OR GS OR WTC OR Hiro OR (Naga AND nag_dir_bull)) |
| `squarify::S4_FLOOR` | `anyBullFloor AND oneOfThese AND cb1_pass_floor` |

**Verdict:** drifted (Squarify wraps HVDPBJPPD's anyBullFloor with additional `oneOfThese` callback gate).
**Stage 6 recommendation:** document as legitimate Squarify-specific gate, not drift.

### PENTAGON / Pent (NAMESPACE COLLISION)

| Where | Concept |
|---|---|
| `heavy-pentagon::PENTAGON` | RVOL P2 tier (cumulative relativeVolume bin in `[th_1x, th_wtc]`) |
| `hvdpbjppd::PENTHOUSE_BEAR` (`anyBearPent`) | Bear platform (mirror of Floor with PB instead of PBJ) |

**Verdict:** namespace collision — same naming root, completely different concepts.
**Stage 6 recommendation:** **HIGH PRIORITY.** Rename `anyBearPent` → `anyBear2F` to free up the "Pentagon" namespace. This collision was the original frustration trigger for the bible project.

### Unified Combo (csNew3) composition (CRITICAL SEMANTIC DRIFT)

| Where | Composition |
|---|---|
| `hvdpbjppd::UNIFIED_COMBO_BULL` (line 1052 of THE_ONLY_ONE) | `csNew1 AND csNew2` **same-bar AND** |
| `squarify::UC` (line 1257) | `csNew1 AND csNew2[1]` **1-bar lagged AND** |
| `b2b-pup::CS3_UNIFIED_COMBO_BULL` | `det_CS1 AND det_CS2[1]` **1-bar lagged AND** |
| `hvdpbjppd predecessor (4.26.1244am)` | `csNew1 AND nz(csNew2[1])` **lagged-AND** |

**Verdict:** drifted_semantic. Canonical THE_ONLY_ONE is same-bar AND; everything else is lagged-AND.
**Stage 6 recommendation:** **CRITICAL.** Anish must decide: same-bar (more selective, tighter visual alignment) or lagged (catches the displacement bar one bar earlier). Likely canonical is HVDPBJPPD's same-bar. Reconcile Squarify and B2B PUP to match.

### GZI proximity (gziProximity / gz1_dist)

| Where | Default |
|---|---|
| `hv-fvg-gz1-og::GZI_BULL` (canonical) | `gziProximity=6` |
| `proximity-gzi-hv::GZI_BULL` | `gziProximity=6` (verbatim of OG) |
| `b2b-pup::gz_bullGZI` | `gz1_dist=7` |
| `hvdpbjppd::gz_bullGZI` (canonical) | `gz1_dist=7` (was 12 in predecessor) |
| `squarify::gz_bullGZI` | `gz1_dist=7` |

**Verdict:** drifted_parameter. Canonical OG uses 6; downstream consumers all use 7.
**Stage 6 recommendation:** Reconcile. Likely canonical should be 6 (smaller window = more selective signals). Update HVDPBJPPD/Squarify/B2B PUP to 6 OR update OG to 7 — pick one.

### DISP / Displacement σ-multiplier

| Where | Default |
|---|---|
| `hvdpbjppd::DISP_BULL` (canonical THE_ONLY_ONE) | `i_std_min=3.0` (was 6.0 in predecessor) |
| `b2b-pup::det_DISPBull` | `disp_mult=5.0` |
| `squarify::DISP_BULL` | `i_std_min=3.0` |
| `tnt-od::DISP` | `DISP_STD_X=5` |
| `ultra-combo::DISP` | `5σ stdev(100)` |

**Verdict:** drifted_parameter. HVDPBJPPD canonical loosened from 6.0 → 3.0 (and Squarify followed); B2B PUP, TNT-OD, Ultra Combo still use 5.0.
**Stage 6 recommendation:** Reconcile. Anish must decide canonical σ-mult; B2B PUP/TNT-OD/Ultra Combo probably need to match HVDPBJPPD 3.0 to align with the loosening, or vice versa.

### F2 / E3 / FC (Squarify vs Ultra Combo definition site)

Both indicators define F2/E3/FC inline with the same compositions. Per Ultra Combo CHANGELOG these are NEW roots in this file. Squarify references the same names. This is distributed-definition redundancy similar to FAUNA.

**Stage 6 recommendation:** Designate one canonical owner (Ultra Combo per CHANGELOG, OR a standalone `cluster-f2-e3-fc/` indicator). All others become cross-refs.

### FAUNA implementations (DISTRIBUTED ROOT)

Same MB/RE/TA/GG/TR/ES/GDR formula appears verbatim in:
- `heavy-pentagon::USE_V5_FAUNA` (USE V5 block inside Heavy Pentagon)
- `hvdpbjppd::FAUNA_BULL` (Engine 2)
- `squarify::FAUNA_BULL` (Engine 2)
- `ultra-combo::FAUNA` (uses parallel `fMB_b/fRE_b/fTA_b` copies, mathematically equivalent to root MB/RE/TA)
- `tnt-od::u5_FAUNABull` (USE V5 inline port)
- `b2b-pup::det_FAUNABull` (re-implemented L85-114)

**Verdict:** distributed_root.
**Stage 6 recommendation:** Designate one canonical FAUNA owner. Options:
1. Heavy Pentagon's USE V5 block.
2. HVDPBJPPD's Engine 2.
3. Extract to dedicated `fauna/` indicator (cleanest).
All others become cross-refs.

---

## (b) Internal-implementation drift inside a root

These are the highest-risk drift cases — the root name is identical everywhere but the internal Pine math may have diverged silently.

### RVOL ladder (SAAB / Kratos / RVOL1x / GS / MOAB / Pentagon / WTC / Hiroshima / Nagasaki)

| Where | Notes |
|---|---|
| `heavy-pentagon::*` (canonical) | Threshold tables `f_rvol_1x_threshold`, `f_saab_kratos_threshold`, `f_gs_moab_threshold`, `f_wtc_threshold`, `f_hiroshima_threshold`. |
| `heavy-combo-toggles::*` (cross-ref) | **VERIFIED VERBATIM** from heavy-pentagon. |
| `b2b-pup::sig_*` | "Pre Mythos thresholds" comment (L276) — drift candidate. |
| `hvdpbjppd::sig*` | Re-implemented inline (Engine 1). |
| `squarify::sig*` | Re-implemented inline. |
| `tnt-od::u5_*` | USE V5 inline port. |
| `ultra-combo::sig*` | Re-implemented inline. |

**Verdict:** drifted_internal. Some implementations (especially B2B PUP's per its comment) likely diverge from heavy-pentagon canonical.
**Stage 6 recommendation:** Byte-diff threshold tables and normalisation logic across all 7 indicators. Heavy Pentagon is canonical. Mirror everywhere; lock implementations with a SHA checksum in `data/indicators.yaml`.

### PBJ internal mechanics (Supertrend / VWMA / EMA crosses)

| Where | Notes |
|---|---|
| `hvdpbjppd::PBJ_BULL` (THE_ONLY_ONE) | Canonical. Lines 622-761. Zoo MA + Supertrend + PB&J wick filter. |
| `b2b-pup::det_PBJBull` | Re-implemented L134-261 — full sub-engine. |
| `squarify::sigBullPBJ` | Re-implemented (Engine 6). Lines 621-744. |
| `tnt-od::u5_PBJBull` | USE V5 inline port. Lines 725-823. |
| `ultra-combo::sigBullPBJ` | Header line 367: "EXACT COPY FROM ANISH TB FOSTER v6". Lines 386-519. |

**Verdict:** drifted_internal_likely. Anish has flagged this as the concrete corruption risk — past line-consolidation efforts may have changed internal Supertrend or VWMA in one indicator and not another. The root name "PBJ" stays identical everywhere, but the actual boolean output may differ across indicators on the same input data.
**Stage 6 recommendation:** Byte-diff PBJ implementations across all 5 indicators. Compare:
1. Zoo MA function (`zoo_ma_type`, `zoo_ma_len`).
2. Supertrend implementation (period, multiplier, ATR formula).
3. Wick threshold logic (`pbj_atr_mult`, EMA reference period).
4. Volume confirmation (`vol_period`, `vol_mult`).
Designate one canonical implementation. Mirror everywhere. Lock with checksum.

### PB internal mechanics (same Zoo engine as PBJ)

Same drift risk as PBJ — PB is the non-PBJ branch of the same Zoo engine. Reconcile in same Stage 6 pass as PBJ.

### Anish Stage 2/4 EMA stack (`bullPass`/`bearPass`)

| Where | Defined? |
|---|---|
| `anish-50-1st-combo::ANISH_BULL_PASS` | Defined inline (lines 29-46). |
| `ultra-combo::bullPass` | Defined inline (lines 524-532). |

**Verdict:** drift_candidate. Need byte-diff to confirm whether the two definitions are identical.
**Stage 6 recommendation:** Byte-diff. If identical, designate `anish-50-1st-combo` as canonical (oldest definition site). If not identical, reconcile.

### Nagasaki implementations

| Where | Implementation |
|---|---|
| `heavy-pentagon::NAGASAKI` (canonical) | `volume > maxVol; maxVol := volume` since `bar_index 0`. |
| `vob-asym::isNagasaki` (re-implemented) | `volume[1] > maxVolEver`. **Note: uses `volume[1]` (prior-bar volume) and `offset=-1` plot.** |
| `hvdpbjppd::sigNagasaki` | Same as canonical. |
| `b2b-pup::sig_Nagasaki`, `squarify::sigNagasaki`, `tnt-od::u5_Nagasaki`, `ultra-combo::sigNagasaki` | All re-implementations. Need byte-diff. |

**Verdict:** drifted_internal — VOB Asym uses `volume[1]` instead of `volume`, distinct semantic.
**Stage 6 recommendation:** Reconcile. The `volume` vs `volume[1]` choice changes which bar gets the marker. VOB Asym's `volume[1]` + `offset=-1` is internally consistent; canonical Heavy Pentagon's `volume` + `offset=0` is also consistent. Pick one convention and mirror.

---

## File-system / version-control issues (mirrors `docs/version-control-diagnosis.md`)

### B2B PUP v4.32 line-ending duplicates

`B2B_PUP_v4.32.pine` (LF) vs `B2B_PUP_Combined_v4.32_2026-05-04.pine` (CRLF) — byte-identical post `tr -d '\r'`. md5 differs. **Stage 6:** delete one. Keep one with consistent line endings.

### TNT-OD v2/v3 file-naming collision

- `TNT_OD_v2.pine` (123 KB, internally v2) — same SHA as date-stamped file.
- `TNT_Opening_Drive_OD_v3_2026-05-04.pine` (123 KB, internally v2 despite v3-named).
- `TNT_OD_v3.pine` (148 KB, internally v3, dated 2026-05-08, has T1 RELAY/T1 STACK/HCT engine).

**Stage 6:** rename date-stamped file to `TNT_OD_v2_2026-05-04.pine`; delete byte-identical pair.

### `proximity-gzi-hv` is alias of `hv-fvg-gz1-og`

`diff` returns exactly 1 line of difference (`indicator()` declaration). Otherwise byte-identical. **Stage 6:** tag as `mirror-of: hv-fvg-gz1-og::v1`. Consider deletion or symlink.

### `vob/` folder mixes 2 distinct indicators

VOB Asym T3×6 (zone overlay) + VOB Ladder Watch (escalation watcher). Different concepts. **Stage 6:** split into `vob/zone_engine/` and `vob/ladder_watch/`, OR hoist shared `f_bull_vob` engine to `vob/_shared/`.

---

## Summary of Stage 6 actions, prioritised

1. **HIGH PRIORITY:** Rename `anyBearPent` → `anyBear2F` (Pentagon namespace collision).
2. **CRITICAL:** Reconcile Unified Combo composition (same-bar vs lagged AND).
3. **HIGH:** Byte-diff PBJ internal implementations across 5 indicators; designate canonical.
4. **HIGH:** Byte-diff RVOL ladder threshold tables across 7 indicators; designate canonical (heavy-pentagon).
5. **MEDIUM:** Reconcile GZI proximity (6 vs 7).
6. **MEDIUM:** Reconcile DISP σ-multiplier (3.0 vs 5.0 vs 6.0).
7. **MEDIUM:** Designate canonical FAUNA owner.
8. **LOW:** Reconcile Nagasaki `volume` vs `volume[1]` semantic.
9. **LOW:** File-system cleanup (line-ending dupes, TNT-OD naming, VOB folder split, proximity-gzi-hv alias decision).
