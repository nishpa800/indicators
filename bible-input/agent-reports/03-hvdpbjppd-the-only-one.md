# HVDPBJPPD THE_ONLY_ONE — extraction report (compact)

Source: `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` · 1767 lines · Pine v5 · title `"HV+D ↔ PBJ ↔ USE THIS IS THE ONLY FUCKING ONE"` · `overlay=true`, `max_*_count=500`, `max_bars_back=1100`, imports `TradingView/ta/7`

## Summary

Four formally-decoupled pipelines (enforced by code comments). Pipeline A = HV+D (volume rank × stdev-displacement × FVG, 3 disp profiles). Pipeline B = PB/PBJ (Zoo MA + Supertrend, isolated). Pipeline C = USE Alarm 1293 (11 internal "engines" producing ~45+ raw signals). Pipeline D = Triple AND CO + B2B HV+D + UC fusion (consumes only terminal booleans from A/B/C). 53 plotshapes, 16 `alert()`, 0 `alertcondition()`.

## Roots (canonical for this family)

| Canonical | Source | Plain-English |
|---|---|---|
| `hvdpbjppd::HVD_BULL` / `HVD_BEAR` | 112-273 | Volume-rank hit (50/75/100…1000-bar highest, or HEV all-time-high, or HTF1/HTF2 ranks) co-occurring with stdev-displacement candle that opens a directional FVG. Defaults: `d1_type="Open to Close"`, `d1_len=100`, `d1_mult=5.0`, `d2_mult=2.5` (HTF1, **was 4.0 in predecessor**), `d3_mult=1.5` (HTF2, **was 2.5**), `h1On=false`, `h2On=false` (**both true in predecessor**), HTF1 15min→2h, HTF2 3h→3M (**3h was 2h in predecessor**). Plot offset=-1. |
| `hvdpbjppd::PBJ_BULL` / `PBJ_BEAR` | 622-761 | Zoo MA + Supertrend cross confirmed by PB&J wick filter. `zoo_ma_type="VWMA"`, `zoo_ma_len=5`, MA period=20, ATR period=14, HH/LL=25, ATR mult=3.0, vol period=20, vol mult=0.1, ST period=10, ST mult=2.0. |
| `hvdpbjppd::PB_BULL` / `PB_BEAR` | 728-761 | Zoo cross approached by lander reaccel level (without PBJ wick); only fires if PBJ did not fire same cross. |
| `hvdpbjppd::PUP` / `PPD` | 622-627 (Engine 5) | Body up/down >3% AND volume > 10-bar highest opposite-color volume. |
| `hvdpbjppd::DISP_BULL` / `DISP_BEAR` | 518-563 (Engine 3) | Range > N×stdev in `[i_std_min, i_std_max]` band, with directional FVG when Require FVG ON. **Defaults relaxed: `i_std_min=3.0` (was 6.0)**, `i_std_max=100.0`, `i_req_fvg=true`. |
| `hvdpbjppd::DISP2_BULL/BEAR` | 521-525 | DISP with `i_disp2_std_min=3.0` (**was 5.0**) — used for "consecutive disp" streak gating. |
| `hvdpbjppd::DISP3_BULL/BEAR` | 540-543 | DISP with `i_disp3_std_min=3.0` (**was 4.0**) — used for D3+ streak. |
| `hvdpbjppd::GZI_BULL` / `GZI_BEAR` | 565-602 (Engine 4) | FVG zone overlapping recent same-direction FVG within `gz1_dist=7` bars (**was 12**). |
| `hvdpbjppd::HV_FVG_BULL` / `HV_FVG_BEAR` | 565-602 | FVG whose creating bar set 5000/252/63 volume high. |
| `hvdpbjppd::MATRIX_NUMBER` | 1009 (Engine 8) | `volume == ta.highest(volume, 67)`. |
| `hvdpbjppd::LONG1` / `SHORT1` (Tier 1 momentum) | 1023-1028 (Engine 11) | Regular & cumulative RVOL ratios > floors AND body ≥ floor AND directional. **Defaults loosened: `ls_reg1=7.0` (was 10), `ls_cum1=3.5` (was 5), `ls_body1=0.60` (was 0.69)**. |
| `hvdpbjppd::LONG2` / `SHORT2` | 1029-1030 | Same with **`ls_reg2=5.0` (was 8), `ls_cum2=2.5` (was 4), `ls_body2=0.75` (was 0.69)**. |
| `hvdpbjppd::BOOM_HUNTER_OMEGA` | 1145-1220 | Ehlers HP/Filt/Peak quotient stack: enter3∧enter5∧enter7, lone-lime, or wt2 oversold/overbought bounces. |
| `hvdpbjppd::HV75/HV150/HV500/HV1000` | 1066-1068 | Volume ≥ highest in 75/150/500/1000-bar lookback. |
| `hvdpbjppd::NAGASAKI` | 465-472 | New all-time-high volume bar. |
| `hvdpbjppd::SAAB`, `KRATOS`, `RVOL1X_BULL/BEAR`, `GRAND_SLAM`, `MOAB`, `WTC`, `HIROSHIMA`, `PENTAGON` | 443-463 (Engine 1) | RVOL ladder per TF threshold tables; same primitives as `heavy-pentagon::*` but inline-ported. **Cross-ref to `heavy-pentagon` — byte-diff parameters; "Pre Mythos thresholds" comment in B2B PUP suggests drift candidate.** |
| `hvdpbjppd::FAUNA_BULL` / `FAUNA_BEAR` | 484-516 (Engine 2) | NRA pattern: (MB OR RE OR TA OR GG-cores) AND NOT (TR OR ES OR GDR exclusions). Same pattern as `squarify::FAUNA` and `ultra-combo::FAUNA`. |
| `hvdpbjppd::PING_PONG_BULL` (`bull_pp`) / `PING_PONG_BEAR` (`bear_pp`) | 763-898 (Engine 7) | Pivot-based S/R level engine; counts pivots/regimes/bounces; declares bull/bear regime by counted state ≥3 with floor/ceiling gravity flag. |

## Key composites (canonical for this family)

Tier-1: `B2B_HVD_BULL/BEAR_RAW` (HVD bull AND HVD bull[1]), Neo (`MATRIX_NUMBER AND FAUNA`), Trinity (`MATRIX_NUMBER AND NOT FAUNA AND directional`), Foxtrot (4 consec FAUNA), PAF (PUP+FAUNA two bars).

Tier-2: `MATRIX_ANY_BULL` (`Neo OR Trinity OR aligned-with-Long1/2`), `comboSet1` (FVG+RVOL low), `comboSet2` (FVG+Pentagon-tier), `comboSet3` (Matrix+RVOL low), `comboSet4` (Matrix+Pentagon-tier), `csNew1=FVG_COMBO` (cs1∨cs2), `csNew2=MATRIX_COMBO` (cs3∨cs4), Floor (`bull_pp AND PBJ AND HW-slot`), 2F (`bull_pp AND PB AND HW-slot`), Roof (mirror PBJ-bear), Penthouse (mirror PB-bear), Alpha Strike, OD (Opening Drive), Golf, DispCons2/3, sigUUBull/UUUBull/UUUUBull (each is the qualified streak — uses paths over PBJ/DISP/FAUNA/SAAB/RVOL/GS/etc.), U-Sub.

**Tier-3 critical**: 
- `csNew3 = UNIFIED_COMBO` (line 1052) = **`csNew1 AND csNew2` SAME-BAR AND** (predecessor used `csNew1 AND nz(csNew2[1])` lagged AND — **drift: same-bar in canonical**).
- `co_bull_pbj` (line 1431-1434) = `hvd_fire_bull AND nz(sigBullPBJ[1]) AND nz(use_any_bull[1])` — Triple AND, offset=-1.
- `HW_BULL` = `(close>open) AND disp5_bull AND PBJ AND HW-slot AND (Floor OR 2F)`.
- `SUPER_BULL` = `PBJ AND DISP AND (FAUNA OR Long1) AND HW-slot AND ((Combo AND PUP) OR (Floor OR 2F))`.
- `SDUPER_BULL` = `(Floor OR 2F) AND PBJ AND HW-slot AND Combo AND PUP AND DISP AND (FAUNA OR Long1)`.
- `Combo Chain` (`sigCCBull`) = latched while csNew2 active AND ≥cc_min_hits Matrix combo in window AND PBJ/PB. **Reset gate tightened: predecessor reset on no-cs1-2-3-4; canonical resets on no-cs3-4-only**.
- `LSC_BULL`, `OmegaLong` (huge OR-list cosignal — TF gates removed in canonical).

## Matrix family resolution (CONFIRMED from source)

- `is_matrix_number` = `volume == ta.highest(volume, 67)`.
- `Neo = is_matrix_number AND FAUNA(direction)`.
- `Trinity = is_matrix_number AND NOT FAUNA(direction) AND directional bar`. **Mutually exclusive with Neo on same bar.**
- `matrix_any = Neo OR Trinity OR Neo-aligned (with Long1/2) OR Trinity-aligned`.
- `MATRIX_COMBO` = `comboSet3 OR comboSet4` (matrix_any wrapped with body% AND RVOL/Pentagon-slot). **NOT just Neo, NOT exactly "Trinity OR Neo" alone.**
- `FVG_COMBO` = `comboSet1 OR comboSet2`.
- `UNIFIED_COMBO` = `FVG_COMBO AND MATRIX_COMBO` same-bar (canonical) — **predecessor was 1-bar-lagged AND**.

## Drift vs predecessor (HVDPBJPPD_4.26.1244am) — semantic changes only

- HV+D HTF1 mult 4.0→2.5; HTF2 mult 2.5→1.5; HTF1/HTF2 enables true→false.
- USE Disp `i_std_min` 6.0→3.0; DISP2 5.0→3.0; DISP3 4.0→3.0.
- GZI proximity 12→7 bars.
- Long1 thresholds 10/5/0.69→7/3.5/0.60. Long2 8/4/0.69→5/2.5/0.75.
- ComboSet body% 0.74→0.85.
- LSC thresholds tightened similarly.
- `csNew3` = same-bar AND (was lagged).
- D2/D3 FAUNA confirmation now requires CURRENT bar FAUNA + prior bars (was only prior bars).
- UU streak engine simplified — A-F pathway scan removed; Pipeline-A leak (`hvd_fire_bull` referenced inside Pipeline C UU) removed.
- Removed: Master gate, Nagasaki Plus, Omega-A, UU `_indep` branches, floor_gated, cb-disp9 gating, `cc_has_fvg_bull/bear`, `floor2_gated`.
- Added: U-Sub Bull/Bear (sigUSubBull/Bear).
- Many show_* default flips (cosmetic).

## Plots (53 total)

Pipeline A: HV+D Bull/Bear (1311-1312), HV+D+PB Bull/Bear (1317/1319), HV+D+PBJ Bull/Bear (1318/1320). All offset=-1.
USE bull (22) at 1341-1362: UUUU, UUU, UU, U-Sub, A★, FOX, Omega, OD, D2+, D3+, Golf, PAF+, CS1 FVG, CS2 MAT, Combo Bull (CS3), CC, LSC, Floor, 2F, HW, Super, SDUPER. Most offset=0; CS1 and Golf offset=-1.
USE bear (21) at 1367-1387: mirror set; D-Sub, Rooftop, Penthouse instead of Floor/2F.
Pipeline D: CO PBJ/PB Bull/Bear (1439-1442), B2B Bull/Bear/+PBJ/+PB (1484-1489). All offset=-1.

## Caveats

- Title is intentionally profane: "HV+D ↔ PBJ ↔ USE THIS IS THE ONLY FUCKING ONE". File is canonical PBJ/PPD/PB/Displacement source.
- `tf_bull_ok` / `tf_bear_ok` defined but not consumed (legacy).
- `p21_pbj_dist` input exists but not referenced in simplified streak code.
- Roots PUP/PPD/Long1/Long2/Short1/Short2/Matrix/HV*/RVOL ladder/FAUNA/GZI/HV+FVG/PingPong are NEVER plotted standalone in this file — only consumed by composites.
- `tnt-od` references this file's PB/PBJ comment "EXACT COPY FROM ANISH TB FOSTER v6" — implies separate Anish TB Foster v6 indicator may exist.
