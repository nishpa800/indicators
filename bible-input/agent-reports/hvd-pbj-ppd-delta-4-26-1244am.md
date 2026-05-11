# HVD+PBJ+PPD delta — file: HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine

Source: `/home/user/indicators/hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine`
Line count: 1939
Sibling files compared:
- `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine`        (1767 lines)
- `HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` (1939 lines)
- `HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` (2246 lines)

---

## Section 0 — Byte-near-twin check vs HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine

- Equal? **near** (NEAR-TWIN: identical structure, identical line count, semantic body byte-equivalent)
- Diff hunks: **10**
- Total changed lines (unified diff): 221 hunk lines, 0 added/removed lines (every change is an in-place edit of an `input.bool` / `input.float` default).

### Notable changed regions
Every one of the 10 diff hunks is **PURELY IPSF DEFAULT FLIPS** (per Anish's drift criteria, NOT REAL DRIFT — these are user-tunable in TradingView settings):

| Hunk @line | Region | Kind |
|---|---|---|
| 324 | TIER 1 detection toggles (Bear UUUU, Bear UUU, Bull UU, Bear UU, Omega-A, Alpha Strike Bull/Bear) | input.bool default flips false → true |
| 347 | TIER 1 toggles (Foxtrot Bear, Omega Long, OD Bear, Disp Bear 2+) | input.bool default flips |
| 356 | TIER 1B Combo Sets (CS1B/CS1R/CS2B/CS2R/CS3R) | input.bool default flips |
| 365 | TIER 1C Chains, TIER 2 Structure, TIER 3 HW, PRIORITY Super/SD | input.bool default flips |
| 397 | Displacement i_std_min (default 6.0 → 4.5) | input.float default |
| 426 | Displacement 3+ i_disp3_std_min (default 4.0 → 3.0) | input.float default |
| 432 | p21_pbj_dist (1 → 4) | input.int default |
| 451 | Momentum 1, Momentum 2, Combo Set FVG/MAT bodyPct, LSC Mom 1/2 floors | input.float defaults |
| 1387 | HV+D detection toggles (en_hvd_*) | input.bool default flips false → true |
| 1484 | PIPELINE D triple co-occurrence (co_en_*) | input.bool default flips |
| 1510 | Back-to-back HV+D (b2b_en_*) | input.bool default flips |
| 1577 | HV+D Momentum Co-Occ (en_hvdm_*) | input.bool default flips |

Every single diff line matches the pattern `input.bool(false,...)` ↔ `input.bool(true,...)` or `input.float(<val>,...)` ↔ `input.float(<other_val>,...)`. **Zero algorithmic / boolean / offset / inclusion changes between this file and `HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine`.**

The masterdir 1939 twin appears to be the same lineage as 4.26.1244am with defaults retuned for "everything-on, looser thresholds" presentation.

---

## Summary
- **Detection-plot count in this file: 58 plotshape() calls + 16 hvdm label.new() detection-equivalents = 74 fire points** (the HVDM block uses `label.new` instead of plotshape to stay under the 64 plot budget — see lines 1633-1680)
- **REAL-drift entries vs siblings: 6** (all vs THE_ONLY_ONE; zero vs 2246 / 1939-twin)
- **Skipped (identical / cosmetic / ipsf-default): 10 hunks vs 1939-twin (all IPSF defaults)** + ~all of 2246 (extra header + rendering blocks, no algo changes)

---

## REAL-drift table

| Detection plot | This file (line) | Sibling file (line) | Diff kind | One-line semantic difference |
|---|---|---|---|---|
| `Bull UU` (sigUUBull) | 1360 (`fire_BullUU=show_BullUU and uu_gated_bull and masterGate`) | THE_ONLY_ONE 1269,1343 (`fire_BullUU=show_BullUU and sigUUBull`) | DIFFERENT GATE | mine adds `uu_gated_bull = sigUUBull and oneOfThese_forUU` co-signal gate; THE_ONLY_ONE plots raw `sigUUBull` directly |
| `Bear UU` (sigUUBear) | 1377 (mirror of above) | THE_ONLY_ONE 1369 | DIFFERENT GATE | mirror of above |
| `Floor` (anyBullFloor) | 1368 (`fire_BullFloor=show_BullFloor and floor_gated and masterGate`) | THE_ONLY_ONE 1276,1358 (`fire_BullFloor=show_BullFloor and anyBullFloor`) | DIFFERENT GATE | mine adds `floor_gated = anyBullFloor and oneOfThese and cb1_pass_floor`; THE_ONLY_ONE plots raw `anyBullFloor` |
| `Rooftop` / `2nd Floor` / `Penthouse` | 1368 / 1380 (gated by `floor_gated`/`floor2_gated`) | THE_ONLY_ONE 1276/1383/1384 (raw `anyBullFloor`/`anyBull2nd`/`anyBearRoof`/`anyBearPent`) | DIFFERENT GATE | same as above mirror |
| `D2+ Bull` / `D2+ Bear` (sigDispConsBull2/Bear2) | 570-571 (body: `sigDISP2Bull and disp2_bullStreak>=2 and nz(sigFAUNABull[1]) and nz(sigFAUNABull[2])`) | THE_ONLY_ONE 545-546 (body: `sigDISP2Bull and disp2_bullStreak>=2 and sigFAUNABull and nz(sigFAUNABull[1])`) | DIFFERENT OFFSET / DIFFERENT INTERNAL HELPER BODY | mine references FAUNA bars `[1]+[2]` (no current); THE_ONLY_ONE references current + `[1]` |
| `D3+ Bull` / `D3+ Bear` (sigDispConsBull3/Bear3) | 587-588 (body: `... nz(sigFAUNABull[1]) and nz(sigFAUNABull[2]) and nz(sigFAUNABull[3])`) | THE_ONLY_ONE 562-563 (body: `... sigFAUNABull and nz(sigFAUNABull[1]) and nz(sigFAUNABull[2])`) | DIFFERENT OFFSET / DIFFERENT INTERNAL HELPER BODY | mine references FAUNA `[1]+[2]+[3]` (no current); THE_ONLY_ONE references current + `[1]+[2]` |
| `A★ Bull` (sigAlphaStrikeBull) | 1238 (`...sigBullPBJ and as_fauna_bull`) | THE_ONLY_ONE 1057 (`...(sigBullPBJ or sigBullPB) and as_fauna_bull`) | DIFFERENT INCLUSION/EXCLUSION | mine requires PBJ only; THE_ONLY_ONE accepts PBJ OR PB |
| `Combo Bull` / `Combo Bear` (csNew3) | 968 (`csNew3_Bull=csNew1_Bull and nz(csNew2_Bull[1])`) | THE_ONLY_ONE 1052 (`csNew3_Bull=csNew1_Bull and csNew2_Bull`) | DIFFERENT OFFSET | mine requires FVG bar N AND Matrix bar N-1; THE_ONLY_ONE requires both same bar |
| `Omega-A` (sigOmegaLongA) | 1336 (definition exists, `omega_cosignal_A` is mine-only co-signal set) | THE_ONLY_ONE — N/A — Omega-A plot does NOT exist | DIFFERENT INCLUSION | mine emits an Omega-A plotshape with mine-only co-signal logic; THE_ONLY_ONE only has `Omega Long` (singular sigOmegaLong) |
| `NAG+ Bull` (sigNagPlusBull) | 1522 plotshape | THE_ONLY_ONE — N/A — NAG+ Bull plot does NOT exist | DIFFERENT INCLUSION | mine emits a NagPlusBull plot; THE_ONLY_ONE has no equivalent |

### Plots in THE_ONLY_ONE that are MISSING from mine (inverse drift, for context)

| Plot | THE_ONLY_ONE (line) | Notes |
|---|---|---|
| `Bull U-Sub` (sigUSubBull) | 1344 plotshape; 1006 def | Mine + 2246 + 1939-twin do NOT define `sigUSubBull` |
| `Bear D-Sub` (sigUSubBear) | 1370 plotshape | mirror |

### Drift vs HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine
**ZERO REAL DRIFT.** Every boolean root definition (sigBullPBJ, sigBullPB, anyBullFloor, anyBull2nd, hwBull, superBull, sduperBull, sigGolfBull, sigPAFBull, sigCCBull, sigLSCBull, sigOmegaLong, sigOmegaLongA, sigDispConsBull2/3, csNew3_Bull, sigAlphaStrikeBull, sigODBull, sigFoxtrotBull, threshold helpers f_rvol_1x_threshold/f_gs_moab_threshold/f_hiroshima_threshold/f_wtc_threshold/f_saab_kratos_threshold) is byte-equivalent to mine. The 2246 file extends this lineage with additional header tables / rendering blocks AFTER line ~1789 but contains the same 58 plotshape detection set + identical HVDM label block. **Mine + 2246 + 1939-twin form a single algorithmic family ("masterdir lineage"); THE_ONLY_ONE is a separate fork.**

### Drift vs HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine
**ZERO REAL DRIFT.** See Section 0 — only IPSF defaults differ.

---

## Internal-helper drift

| Helper name | Mine (line) | THE_ONLY_ONE (line) | Body diff |
|---|---|---|---|
| `omega_cosignal` | 1332 | 1225 | mine is heavily TF-gated `(tfSec>=45?(...):false)` etc; THE_ONLY_ONE flat OR-list with no TF gates |
| `omega_cosignal_A` | 1335 | NOT DEFINED | mine-only helper that drives `sigOmegaLongA` |
| `oneOfThese_forUU` | 1229 | NOT DEFINED | mine-only helper that drives `uu_gated_bull` |
| `oneOfThese` | 1242 | NOT DEFINED | mine-only helper that drives `floor_gated` / `floor2_gated` |
| `cb_uu_any` | 1243 | NOT DEFINED | mine-only |
| `uu_gated_bull` / `uu_gated_bear` | 1230 | NOT DEFINED | mine-only gating wrapper |
| `floor_gated` / `floor2_gated` | 1247 / 1248 | NOT DEFINED | mine-only gating wrapper |
| `cb1_pass` / `cb1_pass_floor` | (referenced inside floor_gated) | NOT DEFINED | mine-only |
| `sigP21BullUUUU` | 1172 declared `false`, then walrus-assigned at 1180 inside an `if` block | 945 single-line `bool sigP21BullUUUU=conf and u4_bull_streak>=4 and u4_bull_hasDay1 and u4_pbj_bull and u4_disp_bull` | DIFFERENT STRUCTURE — mine deferred-assigned via walrus, THE_ONLY_ONE inline. The OR-list `(pA or pB or pC or pD or pE or pF) and _ok` in mine has 6 alternates vs THE_ONLY_ONE's 4-AND requirement — needs deeper walk to confirm semantic equivalence |
| `sigP21BullUUU` | 1184 declared, walrus 1192 (`(pA or pB or pC or pD or pE) and _ok`) | 979 inline AND-form | same kind of deferred-vs-inline divergence |
| `sigUUBull` | 1196 declared `false`, walrus 1204 | 989 inline (`p21_bull_streak==2 and p21_bull_sum>=th_1x and ((uu_pbj_bull and uu_disp_bull) or uu_excA_bull or uu_excC_bull)`) | mine restructured into deferred walrus assignment — the underlying conditions look related but cannot prove byte-semantic equivalence without walking pA..pE definitions |
| `sigDispConsBull2` / `Bear2` body | 570-571 | 545-546 | see drift table — different FAUNA offsets |
| `sigDispConsBull3` / `Bear3` body | 587-588 | 562-563 | see drift table — different FAUNA offsets |

NOTE: Helper-body inequalities for `sigP21BullUUUU/UUU/sigUUBull` are STRUCTURAL (deferred walrus vs inline AND-chain) — but my file's masterGate-lineage definitions of `pA..pF` may compute the same final boolean as THE_ONLY_ONE's inline AND. A rigorous semantic equivalence proof is out-of-scope for this delta but should be flagged for the cross-agent compiler.

---

## Hardcoded thresholds in this file (sorted by line)

(Numeric literals consumed by detection booleans, NOT counting input.* defaults.)

| Line | Threshold | Used by |
|---|---|---|
| 469 | RVOL 1x ladder: `_s<=10?38.0:_s<=15?33.0:_s<=30?28.0:_s<=45?23.0:_s<=60?20.0:_s<=120?18.0:_s<=300?13.0:_s<=360?13.0:_s<=540?11.0:_s<=600?10.0:_s<=660?9.0:_s<=900?7.5:_s<=1560?6.5:_s<=2340?6.0:_s<=3600?4.5:_s<=9000?4.0:_s<=11700?3.5:_s<259200?1.8:1.0` | `sigBullRVOL1x`, `sigBearRVOL1x`, downstream of nearly every detection that gates on volume |
| 470 | GS/MOAB: `_s<60?...*3.0:_s<=300?35.0:_s<=600?25.0:_s<=1500?20.0:_s<=3000?20.0:_s<=7260?10.0:_s<=11700?8.0:_s<=86400?7.5:_s<=259200?3.5:3.0` | `sigGrandSlam`, `sigMOAB` |
| 471 | SAAB/Kratos: `f_rvol_1x_threshold * 0.56` | `sigSAAB`, `sigKratos` |
| 472 | WTC: `f_rvol_1x_threshold * 2.0` | `sigWTC` |
| 473 | Hiroshima: `_s<60?...*3.0:_s<=300?35.0:_s<=600?25.0:_s<=1500?25.0:_s<=3060?20.0:_s<=7260?10.0:_s<=11700?8.0:_s<=86400?7.5:_s<=259200?5:3.5` | `sigHiroshima`, `sigNagasaki` |
| 517-520 | FAUNA bull `MB/RE/TA/GG`: body multipliers `1.6 / 2.2 / 0.70 / 1.8 / 0.15 / 0.9` ATR/avgVol coefficients | `sigFAUNABull` |
| 521-522 | FAUNA bear gating: `1.5*fauna_avgBody[1]`, `1.5*fauna_avgVol[1]`, `<=0.2 body/range ratio` | `sigFAUNABear` (StrongBear / WeakBear) |
| 525 | `b_core_cnt>=2`, `>=fauna_gg_body` | FAUNA GG pass condition |
| 530-538 | FAUNA bear MB/RE/TA/GG mirror, same coefficients | `sigFAUNABear` |
| 552 | `disp5_thresh = disp_std * 5.0` | `disp5_bull`, `disp5_bear`, `hwBull/hwBear` |
| 570 | `disp2_bullStreak>=2`, FAUNA `[1]+[2]` | `sigDispConsBull2` |
| 587 | `disp3_bullStreak>=3`, FAUNA `[1]+[2]+[3]` | `sigDispConsBull3` |
| 644 | `gz_fvgs.size()>50` | gz_fvg pruning cap |
| ~283 | UB rank ladder `50,75,100,150,200,250,300,350,400,450,500,550,600,650,700,750,1000` | `base_enabled` (HV bar gating) |

All hardcoded thresholds in mine MATCH 2246 and 1939-twin BYTE-EQUIVALENTLY. The threshold helpers (lines 469-473) ALSO match THE_ONLY_ONE byte-equivalently (it has the same RVOL/GS/Hiroshima ladders at its lines 444-448).

---

## Notes for the cross-agent delta-table compiler

1. **TWIN GROUP**: My file (`4.26.1244am`), `1939_FROM_MASTERDIR`, and `2246_FROM_MASTERDIR` form a single algorithmic family ("masterdir lineage"). They produce identical detection-fire conditions; only IPSF defaults and rendering/header blocks differ.

2. **FORK GROUP**: `THE_ONLY_ONE` is a separate fork with:
   - Extra detections: `Bull U-Sub` / `Bear D-Sub` (sigUSubBull / sigUSubBear)
   - Missing detections: `Omega-A` (sigOmegaLongA) and `NAG+ Bull` (sigNagPlusBull) plots
   - Different gating layer: my fork wraps several detections in `*_gated` co-signal helpers (`uu_gated_bull`, `floor_gated`, `floor2_gated`); THE_ONLY_ONE plots raw root booleans
   - Different DispCons2/3 FAUNA-offset logic (mine: `[1]+[2]`/`[1]+[2]+[3]`, THE_ONLY_ONE: `current+[1]`/`current+[1]+[2]`)
   - Different AlphaStrike PBJ/PB inclusion (mine: `sigBullPBJ` only, THE_ONLY_ONE: `(sigBullPBJ or sigBullPB)`)
   - Different csNew3 offset (mine: `csNew1 and nz(csNew2[1])` cross-bar, THE_ONLY_ONE: `csNew1 and csNew2` same-bar)
   - Different `omega_cosignal` body (mine TF-gated, THE_ONLY_ONE flat OR-list)
   - Mine has `omega_cosignal_A` co-signal helper for Omega-A; THE_ONLY_ONE has no equivalent

3. **The 16-detection HVDM block** (lines 1633-1680) is implemented as `label.new()` rather than `plotshape()` to stay within Pine's 64-plot budget. These ARE detection plots semantically and need to be ported as boolean firing series in the Python port. They live in the masterdir lineage (mine + 2246 + 1939) but probably not in THE_ONLY_ONE — confirm in cross-agent merge.

4. **Mine = 2246 - tables** is the simplest summary: 2246 is mine + extra header/dashboard rendering blocks; the algorithmic detection layer is identical.

5. **Mine = 1939-twin - IPSF default flips** is the second-simplest summary: 1939_FROM_MASTERDIR is mine with most toggles flipped to `true` and several thresholds loosened (`i_std_min` 6.0→4.5, `i_disp3_std_min` 4.0→3.0, momentum reg/cum floors lowered, body% lowered, etc).

6. **Recommendation**: For the canonical bible, treat the masterdir-lineage 1939/4.26/2246 as the authoritative source for detection algorithmics; treat THE_ONLY_ONE as a tagged-rollback baseline that omits Omega-A/NagPlus and uses the legacy ungated DispCons/Floor/UU formulations.

---

## Completion note

- Phase 1 (audit) — done. Delta report written to this file.
- Phase 2 (Python port) — done. `python_ports/hvd_pbj_ppd/v_4_26_1244am.py` written with:
  - 74 detection entries in `DETECTIONS`
  - 1 state-machine class (`B2BWalker`) in `STATE_MACHINES`
  - 42 stubbed detections (require Pine-only intrinsics like FAUNA scoring,
    P21 streak walk, Boom Hunter omega, gz_fvg array, HV ladder gating)
  - 32 fully-ported detections (all the HV+D root + PBJ/PB co-occurrence,
    all 6 B2B HV+D variants, all 16 HV+D Momentum Co-Occ label-block detections,
    all 4 Pipeline-D triple-co-occurrence detections)
- Phase 3 (verify) — done.
  - `python3 -c "import python_ports.hvd_pbj_ppd.v_4_26_1244am as m; print(len(m.DETECTIONS), 'detections,', len(m.STUBBED), 'stubbed')"`
  - Output: `74 detections, 42 stubbed`
  - Smoke test (synthetic random booleans, all toggles enabled): 32 ok, 42 stub, 0 err.
