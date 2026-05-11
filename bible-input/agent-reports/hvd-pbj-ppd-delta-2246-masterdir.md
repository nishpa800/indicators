# HVD+PBJ+PPD delta — file: HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine

Sibling files audited against:
- `T1` = HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine (1767 lines)
- `S39` = HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine (1939 lines)
- `S26` = HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine (1939 lines)

The two 1939-line siblings (`S39`, `S26`) are byte-for-byte siblings on every detection
boolean inspected — the only differences are inside the input wiring around `masterGate`
(`en_firstBarOnly`) and a few cosmetic input defaults. They therefore appear as a single
column "S39/S26" everywhere in the tables below.

## Summary
- Detection-plot count in this file: **62** (43 USE plotshapes + 2 standalone HV+D + 4 PBJ co-occurrence + 4 Pipeline-D triple-CO + 6 B2B HV+D + 1 NAG+ + 12 HVDM labels = 62 visual emitters; 56 distinct named `fire_*`/`co_*`/`b2b_*`/`hvdm_*`/`hvd_*` boolean plots)
- REAL-drift entries vs siblings: **8** (counting only non-IPSF, non-cosmetic pipeline-changing differences)
- UNIQUE-to-this-file entries: **0** (all 2246 detections are also present in S39 and S26 — zero detections live only in 2246; the largest-file status comes from extra **alert/aggregator/payload code** at the tail, not new detections)
- Skipped (identical / cosmetic / ipsf-default): the great majority — every Pipeline-A primitive (`d1/d2/d3_bull/bear`, `is50..is1000`, `isHEV`, `htfNActive`, `baseRank/h1Rank/h2Rank`, `base_combo_bull/bear`, `htfN_combo_bull/bear`, `hvd_fire_bull/bear`), every USE engine boolean (`sigSAAB`, `sigKratos`, `sigGrandSlam`, `sigMOAB`, `sigBullRVOL1x`, `sigBearRVOL1x`, `sigWTC`, `sigHiroshima`, `sigPentagon`, `sigNagasaki`, `sigFAUNABull/Bear`, `sigDISPBull/Bear`, `disp5_bull/bear`, `sigDISP2Bull/Bear`, `sigDispConsBull2/Bear2`, `sigDISP3Bull/Bear`, `sigDispConsBull3/Bear3`, `gz_bullGZI/HV`, `gz_bearGZI/HV`, `sigPUP`, `sigPPD`, `sigBullPBJ/PB`, `sigBearPBJ/PB`, `bull_pp/bear_pp`, `sigNeoBull/Bear`, `sigTrinityBull/Bear`, `sigFoxtrotBull/Bear`, `sigLong1/2`, `sigShort1/2`, `comboSet1..4_Bull/Bear`, `csNew1/2_Bull/Bear`, `nag_dir_bull/bear`, `bull_hw_slot/bear_hw_slot`, `anyBullFloor/2nd`, `anyBearRoof/Pent`, `hwBull/Bear`, `super_hw_bull/bear`, `super_comboAny_bull/bear`, `superBull/Bear`, `sduperBull/Bear`, `sigGolfBull/Bear`, `sigPAFBull/Bear`, `sigODBull/Bear`, `sigHV75/150/500/1000`, `sigCCBull/Bear`, `sigLSCBull/Bear`, `sigNagPlusBull/Bear`, `bh_anyOmega`, `sigShortPlusPress`, `sigOmegaLong`, `sigOmegaLongA`, the entire `sigP21BullUUUU/UUU`, `sigUUBull/Bear` block (with `_indep` variants), `sigAlphaStrikeBull/Bear`, the Pipeline-D `co_bull_pbj/pb`, `co_bear_pbj/pb`, the entire `b2b_*` block, and the HVDM 2of3/3of3 cascade) — all match `S39`/`S26` byte for byte. Versus `T1` they all match semantically except where called out in the drift table.

## UNIQUE-to-this-file detection plots
| Detection plot | Line | Boolean (one-line) | Why probably added |
|---|---|---|---|
| _(none)_ | — | — | The 2246 file shares its full detection set with `S39`/`S26`. The 307-line delta vs `S39` and the 479-line delta vs `T1` are all post-detection: extra alert lines, the per-bar consolidated USE Aggregator (lines 2088–2246), the verbose Pipeline-D `co_use_list` payload (lines 1989–2086), and a wider HV+D/HV+D+PBJ alert fan (six dedicated `alert(...)` calls lines 1673–1684 and the per-direction HVDM alert block lines 1939–1986). No new fire boolean exists. |

> *Caveat:* `Omega-A` / `sigOmegaLongA` and `floor_gated`/`floor2_gated` ARE absent in `T1` but are present in BOTH `S39` and `S26`, so they fail the "absent in ALL 3 siblings" UNIQUE test. They are reported below as drift vs `T1` only.

## REAL-drift table (vs the 3 siblings)

| Detection plot | This file (line) | Sibling file (line) | Diff kind | One-line semantic difference |
|---|---|---|---|---|
| `Omega-A` (`fire_OmegaLongA = show_OmegaLongA and sigOmegaLongA`) | 1619 | T1: not present at all | UNIQUE-to-this-vs-T1 (also in S39/S26) | T1 has only `Omega Long`; 2246/S39/S26 add a parallel `Omega-A` channel using the high-confidence `omega_cosignal_A` slot list. |
| `Bull U-Sub` / `Bear D-Sub` (`fire_BullUSub = show_BullUSub and sigUSubBull`) | not in 2246 | T1:1269,1280 (`fire_BullUSub`, `fire_BearUSub`) | DROPPED detection vs T1 | T1 emits a separate "U-Sub" plot fired by `sigUSubBull = u_streak>=3 + p21_pbj_sub_bull + usub_disp`. 2246 collapses U-Sub into the `UU` aggregator alert ("UU" appends "U-SUB" string) but no longer plots it as a distinct fire boolean. |
| `Bull UU` (`fire_BullUU`) | 1617 (`fire_BullUU = show_BullUU and uu_gated_bull`) | T1:1269 (`fire_BullUU = show_BullUU and sigUUBull`) | Different gate inserted | 2246 adds an `oneOfThese_forUU` OR-gate (line 1495–1496) so UU only fires if a confluence partner is present; T1 fires raw `sigUUBull`. |
| `Floor` (`fire_BullFloor`) | 1625 (`= show_BullFloor and floor_gated`) | T1:1276 (`= show_BullFloor and anyBullFloor`) | Extra confluence gate vs T1 | 2246 ANDs an additional `oneOfThese and cb1_pass_floor` gate (lines 1507–1512), where `cb_disp9 = disp_rng > disp_std*9.0`. T1 plots `anyBullFloor` directly. S39/S26 match 2246. |
| `2nd Floor` (`fire_Bull2ndFloor`) | 1625 (`= show_Bull2ndFloor and floor2_gated`) | T1:1276 (`= show_Bull2ndFloor and anyBull2nd`) | Extra confluence gate vs T1 | Same pattern: 2246 requires `oneOfThese and cb1_pass`; T1 fires raw `anyBull2nd`. S39/S26 match 2246. |
| `sigP21BullUUUU` / `UUU` / `sigUUBull` (and bear mirrors) | 1078–1492 (huge multi-path block with paths A/B/C/D/E/F/G/H + `_disp_gate or _nagp` master gate + `_sub2min_pass` TF-floor) | T1:945 / 979 / 989 (one-line definitions: `streak>=4 and hasDay1 and pbj_bull and disp_bull` etc.) | INTERNAL BODY DRIFT vs T1 (semantic-class change) | T1 uses a single AND-of-four-conditions definition; 2246 (and S39/S26) replace it with a 100+-line multi-path "any-of-eight-paths + sub-2-min RVOL/struct floor + disp-or-nagp gate" pipeline. Same fire-name, very different math. |
| `sigDispConsBull2` / `sigDispConsBear2` | 544 (uses `nz(sigFAUNABull[1]) and nz(sigFAUNABull[2])`) | T1:545 (uses bare `sigFAUNABull and nz(sigFAUNABull[1])` — current bar required) | OPERAND DIFFERENCE vs T1 | T1's "consecutive disp" requires FAUNA on bar [0]+[1]; 2246/S39/S26 require FAUNA on bars [1]+[2] only — i.e. the FAUNA-confluence window is shifted back one bar. |
| `sigDispConsBull3` / `sigDispConsBear3` | 561 (`nz(sigFAUNABull[1..3])`) | T1:562 (`sigFAUNABull and nz(sigFAUNABull[1..2])`) | OPERAND DIFFERENCE vs T1 | Same window-shift pattern as Disp 2+. |
| `sigAlphaStrikeBull` / `sigAlphaStrikeBear` | 1503 (`sessionBarCount<=od_max_bars and bull_pp and (sigGrandSlam or sigBullRVOL1x) and sigBullPBJ and as_disp_bull and as_fauna_bull`) | T1:1057 (`firstOfDay and bull_pp and (sigGrandSlam or sigBullRVOL1x) and (sigBullPBJ or sigBullPB) and as_fauna_bull`) | GATE + OPERAND DIFFERENCE vs T1 | Three semantic deltas vs T1: (1) "first signal" gate `firstOfDay` → "first N session bars" gate `sessionBarCount<=od_max_bars`; (2) PBJ-only required (no `or sigBullPB`); (3) extra `as_disp_bull` gate added. S39/S26 match 2246. |
| `csNew3_Bull` / `csNew3_Bear` (Unified Combo) | 942 (`csNew1_Bull and nz(csNew2_Bull[1])`) | T1:1052 (`csNew1_Bull and csNew2_Bull` — same bar) | OFFSET DIFFERENCE vs T1 | T1 requires CS1 and CS2 on the same bar; 2246/S39/S26 require CS1 on bar 0 AND CS2 on bar [1] (a one-bar lag, "CS2 first then CS1"). |
| `omega_cosignal` (Omega Long input list) | 1597 (TF-gated mega-OR with `tfSec>=45?(sigSAAB or sigPentagon):false` etc.) | T1:1225 (un-gated mega-OR) | INTERNAL HELPER DRIFT vs T1 | T1's `omega_cosignal` is a flat OR with no TF gates and includes `bull_pp`. 2246/S39/S26 wrap most slots in TF-second guards (`tfSec>=45/60/120/300`) and drop `bull_pp` from the slot list. Direct effect on `sigOmegaLong` firing on small TFs. |
| `sigODBull` Opening Drive Bull | 978 (`sessionBarCount<=od_max_bars and od_fvg_bull and disp_prevDisp and sigPUP and sigBullPBJ`) | identical in T1/S39/S26 | identical | No drift; included to show OD Bull has SAME definition across all 4 — only `Alpha Strike` was changed. |
| `use_any_bull` / `use_any_bear` (Pipeline-D OR menu) | 1746 (`sigP21BullUUUU_indep or sigP21BullUUU_indep or sigUUBull_indep or … or sigOmegaLongA or …`) | T1:1427 (`sigP21BullUUUU or sigP21BullUUU or sigUUBull or sigUSubBull or … or sigOmegaLong` — no `_indep`, no `Omega-A`, plus `USub`) | OPERAND-LIST DIFFERENCE vs T1 | 2246/S39/S26 use the `_indep` (no `_disp_gate or _nagp`) versions of the U-streak signals so the AND-gate downstream isn't double-gated, and they include `sigOmegaLongA`. T1 uses gated U-streak signals and includes `sigUSubBull/Bear` instead of Omega-A. |
| `_m_cb1b` / `_m_cb1r` (HVDM CMB component) | 1850 (`nz(csNew3_Bull[1])`) | S39:1593 / S26:1593 (`csNew3_Bull` — bar 0) | OFFSET DIFFERENCE vs S39/S26 (and T1 has no HVDM block) | The HVDM 2of3/3of3 cascade in 2246 reads CMB at lag-1 (`csNew3_Bull[1]`), while S39/S26 read it at lag-0. Visible bar shift in CMB component of HVDM 2of3 / 3of3 fires. |

> Where a row says "S39/S26 match 2246", I verified the boolean expression is byte-identical. Drift exists only vs T1 except for the last row, which is drift vs S39/S26 (not vs T1, which lacks the HVDM block entirely).

## Internal-helper drift

| Helper | This file | Sibling state | Note |
|---|---|---|---|
| `bull_pp` / `bear_pp` (Ping-Pong gravity) | 896–897 (`bull_cnt>=pp_min_count and bull_has_floor_gravity and bull_state>0`) | identical to S39/S26/T1 | No drift. The whole Engine 7 SR engine is byte-identical. |
| `super_hw_bull` / `super_hw_bear` | 961–962 | identical to S39/S26/T1 | `sigBullRVOL1x or sigGrandSlam or sigWTC or sigHiroshima or sigNagasaki` (same in all 4). |
| `super_comboAny_bull` / `_bear` | 963 | identical (== `csNew1 or csNew2`) | No drift. |
| `comboSet1..4_Bull/Bear` | 928–938 | identical to S39/S26/T1 | No drift. |
| `csNew1_Bull/Bear`, `csNew2_Bull/Bear` | 940–941 | identical to S39/S26/T1 | No drift. |
| `csNew3_Bull/Bear` | 942 (`csNew1 and nz(csNew2[1])`) | T1:1052 (`csNew1 and csNew2`) | DRIFT vs T1 (1-bar offset on CS2 leg). |
| `cc_bull_active` / `cc_bear_active` (Combo Chain state) | 1009–1019 | identical to S39/S26/T1 | No drift; same `cc_min_hits`, same `cc_window`, same look-back loop. |
| `det_bullNapalm*` / similar | not present in this file | not present in any sibling | N/A |
| `bb_baseBullish` / `bb_baseBearish` | 439 | identical to S39/S26/T1 | No drift. |
| `f_rvol_1x_threshold` and `f_gs_moab_threshold` step ladders | 443–447 | identical to S39/S26/T1 | No drift; the entire RVOL ladder is shared verbatim. |
| Boom Hunter Omega (`bh_*`) | 1515–1593 | identical to S39/S26/T1 | No drift. |
| `omega_cosignal` (TF-gated mega-OR) | 1597 | DRIFT vs T1 (T1 has un-gated, `bull_pp` included) | See drift table. |
| `omega_cosignal_A` (Omega-A slot) | 1600 | identical to S39/S26; not present in T1 | Adds the Omega-A channel. |
| `oneOfThese`, `cb_uu_any`, `cb_disp9`, `cb1_pass_floor`, `cb1_pass`, `floor_gated`, `floor2_gated` | 1507–1513 | identical to S39/S26; absent in T1 | Adds the Floor / 2F additional confluence gate. |
| `oneOfThese_forUU`, `uu_gated_bull` | 1495–1496 | identical to S39/S26; absent in T1 | Adds the UU confluence gate. |

## Hardcoded thresholds in this file (sorted by line)

| Line | Constant | Context |
|---|---|---|
| 246 | `0.0` | `var float maxVolEver = 0.0` (HEV seed) |
| 293 | `bb_avgLength = 30` | RVOL normalization SMA length |
| 293 | `bb_smaLength = 20` | RVOL diff SMA length |
| 294 | `reg_length = 30` | TradingView relativeVolume length |
| 296 | `fauna_gg_master = true` | FAUNA GG path master |
| 296 | `fauna_gg_body = 0.80` | FAUNA GG body-ratio floor |
| 385 | `pp_barSize = 3.0` | PUP/PPD body-% threshold (3 %) |
| 385 | `pp_lookback = 10` | PUP/PPD lookback bars |
| 386 | `zoo_ma_type = "VWMA"` | Zoo MA type |
| 386 | `zoo_ma_len = 5` | Zoo MA length |
| 387 | `zoo_pbj_ma_period = 20` | PB&J EMA length |
| 387 | `zoo_pbj_atr_period = 14` | PB&J ATR length |
| 387 | `zoo_pbj_hh_ll = 25` | PB&J highest-low / lowest-high lookback |
| 387 | `zoo_pbj_atr_mult = 3.0` | PB&J ATR multiplier |
| 387 | `zoo_pbj_vol_period = 20` | PB&J volume SMA |
| 387 | `zoo_pbj_vol_mult = 0.1` | PB&J volume multiplier |
| 388 | `zoo_st_period = 10`, `zoo_st_mult = 2.0` | Zoo Supertrend |
| 389 | `pp_min_candles = 2`, `pp_buffer_ticks = 10`, `pp_atr_mult = 2.0`, `pp_trend_cnt = 1`, `pp_max_levels = 50` | Ping-Pong SR |
| 390 | `pp_trust_mode = "Trusted Only"`, `pp_min_count = 3` | Ping-Pong gravity |
| 430–432 | `bh_LPPeriod = 6`, `bh_K1 = 0`, `bh_trigno = 2`, `bh_LPPeriod2 = 27`, `bh_K12 = 0.8`, `bh_K22 = 0.3`, `bh_LPPeriod3 = 11`, `bh_n1=9, n2=6, n3=3, n4=21, n5=0`, `bh_lsmaline = 200`, `bh_leftBars = 1`, `bh_rightBars = 1`, `bh_leftBars2 = 5`, `bh_rightBars2 = 5`, `bh_greyDist = 30` | Boom Hunter (entire constant block) |
| 443 | RVOL 1x ladder: 38 / 33 / 28 / 23 / 20 / 18 / 13 / 13 / 11 / 10 / 9 / 7.5 / 6.5 / 6.0 / 4.5 / 4.0 / 3.5 / 1.8 / 1.0 | TF-second→threshold mapping |
| 444 | GS/MOAB ladder: 35 / 25 / 20 / 20 / 10 / 8 / 7.5 / 3.5 / 3.0 (with sub-60s → `1x*3.0`) | TF-second→threshold mapping |
| 445 | `f_saab_kratos = f_rvol_1x * 0.56` | SAAB/Kratos multiplier |
| 446 | `f_wtc = f_rvol_1x * 2.0` | WTC multiplier |
| 447 | Hiroshima ladder: 35 / 25 / 25 / 20 / 10 / 8 / 7.5 / 5 / 3.5 (with sub-60s → `1x*3.0`) | TF-second→threshold mapping |
| 491–509 | FAUNA constants: body / range / vol multipliers `1.6 * atr`, `2.2 * atr`, `0.70` body-ratio gate, `1.8 * avgVol`, `0.15 * range` upper-wick cap, `0.9 * atr` GG, `1.5 * avgBody`, `1.5 * avgVol`, `0.2` weak-bear ratio | FAUNA NRA scoring |
| 526 | `disp5_thresh = disp_std * 5.0` | HW disp gate |
| 575 | `gz_thresh = ...` (with `gz1_auto`) — when manual: divides input by 100 | GZ1 FVG |
| 640 | `atr_pb = atr14 * 2.0` | PB lander box width |
| 670 | `pbj_ma = ta.ema(close, zoo_pbj_ma_period)` (period from line 387) | PBJ MA |
| 685, 689 | `atr_pb * 0.5` | PB lander minimum half-range |
| 709 | approach factors `1.005`, `0.995` (lvl.upper * 1.005 etc.) | PB lander approach |
| 1061–1062 | `bb_normalizedPrice >= 0.5` | UU/UUU/UUUU per-bar qualifier |
| 1149, 1216, 1283, 1355, 1422, 1489 | `tfSec > 120` | UU sub-2-min floor gate |
| 1147–1148 / 1199–1201 / 1265–1267 etc. | `_heavy_cnt >= 3` (UUUU) and `>=2` (UUU/UU) | path-G threshold |
| 1509 | `disp_rng > disp_std * 9.0` | `cb_disp9` (Floor confluence) |
| 1516 | `bh_K2 = 0.3` | Boom Hunter |
| 1555 | `bh_Quotient5 = (bh_X3 + 0.9999) / (0.9999*bh_X3 + 1)` | Boom Hunter |
| 1564–1565 | `bounceUp` / `bounceDown` thresholds 20 / 80 with `barssince(...) <= 1` | Boom Hunter |
| 1571 | `ta.crossunder(bh_Quotient2, -0.9)` | bh_entry |
| 1582–1593 | thresholds `-0.9`, `0.9`, `barssince(...) <= 7`, `bh_q1 <= 20`, `barssince(crossover(q1,20)) <= 21`, `<= 5`, `<= 11`, `>= 80`, `>= 99` | Boom Hunter Omega path predicates |
| 1597 | TF gates in `omega_cosignal`: 45 / 60 / 120 / 300 | Omega Long slot guards |
| 1604 | `tf_req = tfSec<=1800?2:tfSec<=3000?1:0` | TF Gate confluence floor |

> All thresholds above are SHARED with `S39`/`S26` byte-for-byte. Vs `T1`, the only NEW hardcoded thresholds are `cb_disp9`'s `9.0`, the UU `bb_normalizedPrice>=0.5` qualifier, the UU `tfSec>120` floor, and the TF guards inside `omega_cosignal`. (T1 has none of those.)

## Notes for the cross-agent delta-table compiler

1. **2246 is a strict superset of S39/S26 in DETECTION SET.** Detection-wise these three files are the *same* engine. The only line-level deltas between 2246 and S39/S26 are inside the alert/aggregator tail (lines 1939–2246 of 2246 vs the much shorter alert tail of S39/S26). No new fire booleans, no new state machines, no new helpers exist in 2246.
2. **vs T1, 2246 is an *evolution* with two name additions and three semantic rewrites.** The added detections (Omega-A, Floor-gating, UU-gating) and rewritten detections (UUUU/UUU/UU multi-path, Alpha Strike, csNew3 lag, DispCons window-shift) are all already present in S39/S26. **None are unique to 2246.**
3. **`fire_BullUSub` / `fire_BearUSub`** — present in T1, dropped in 2246/S39/S26. The cross-compiler should treat U-Sub as a T1-only legacy plot. The string "U-SUB" still appears inside the aggregator alert payload of 2246 (lines 2127–2128 and 2195–2196) but no longer drives a plot.
4. **`Omega-A` (`fire_OmegaLongA`)** — absent in T1, present in 2246/S39/S26. Should be considered a "post-T1, pre-1939" addition.
5. **`floor_gated` / `floor2_gated`** — gating added vs T1; identical in 2246/S39/S26.
6. **`uu_gated_bull`** — gating added vs T1; identical in 2246/S39/S26.
7. **`csNew3` offset** — vs T1 the offset on CS2 leg is shifted by 1 bar; identical in 2246/S39/S26.
8. **`sigDispConsBull2/3` window** — vs T1 the FAUNA-confluence window is shifted back by 1 bar; identical in 2246/S39/S26.
9. **`sigAlphaStrikeBull/Bear`** — vs T1 the trigger window is changed (`firstOfDay` → `sessionBarCount<=od_max_bars`), the leg requirement is tightened (`PBJ or PB` → `PBJ` only), and an `as_disp_bull` gate is added; identical in 2246/S39/S26.
10. **HVDM CMB lag (`_m_cb1b/_m_cb1r`)** — 2246 uses `nz(csNew3_Bull[1])`, S39/S26 use `csNew3_Bull` (bar 0). One-bar offset difference inside the HVDM 2of3/3of3 cascade. T1 has no HVDM block at all. **THIS is the only true 2246-vs-(S39/S26) detection drift in the entire file.**
11. **Pipeline-A (HV+D)** is byte-identical across all 4 files (`hvd_fire_bull/bear` is the same expression).
12. **Pipeline-B (PBJ/PB)** is byte-identical across all 4 files (`sigBullPBJ/PB`, `sigBearPBJ/PB`).
13. **Pipeline-D (CO HV+D + PBJ/PB + USE)** is identical in expression — only the contributing `use_any_bull/bear` slot list differs (see drift table row).
14. **`masterGate` / `en_firstBarOnly`** are present in S39 and S26 but ABSENT from 2246 and T1. Therefore 2246's fire booleans do NOT have the `… and masterGate` suffix. This is an inclusion difference vs S39/S26 but does NOT change the boolean computation when the user leaves `en_firstBarOnly = false` (default).
15. **Aggregator alert (lines 2088–2246) is unique to 2246.** It is not a detection but a per-bar consolidated alert that lists every active fire boolean. Sibling files use the inline alerts only.

---

## COMPLETION NOTE — UNIQUE-to-2246 features (post-audit)

After full enumeration of `fire_*`, `co_*`, `b2b_*`, `hvdm_*`, and `hvd_*` boolean
emitters across all 4 files, the audit confirms:

- **Zero new detection-plot booleans are unique to 2246.** Every plotted
  detection (43 USE plotshapes, 2 standalone HV+D, 4 PBJ co-occurrence,
  4 Pipeline-D triple-CO, 6 B2B HV+D, 1 NAG+, 12 HVDM labels) is also
  defined byte-for-byte in `S39` and `S26`.
- **The 307-line surplus vs `S39`/`S26` is entirely post-detection wiring:**
  1. The verbose `co_use_list` payload builder (lines 1989–2086) — extends
     the Pipeline-D alert string to enumerate every USE channel that
     co-fired (FLOOR / 2F / UUUU / OMEGA / OD / D2+ / GOLF / FVG / MAT /
     CC / LSC, plus bear mirrors). S39/S26 only tag the direction.
  2. The per-bar consolidated USE Aggregator alert (lines 2088–2246) — a
     priority-sorted alert listing all active bull and bear fire booleans
     in one line plus `first1..first4` session-novelty flags. Absent in
     S39/S26.
  3. Six dedicated HV+D / HV+D+PBJ / HV+D+PB inline `alert(...)` lines
     (1673–1684) and twelve HVDM cascade alerts (1939–1986) — these are
     present in S39/S26 too, but with shorter payload strings.
- **One real semantic-drift entry vs `S39`/`S26`:** the HVDM CMB component
  reads `nz(csNew3_Bull[1])` in 2246 but `csNew3_Bull` (bar 0) in S39/S26.
  This causes a one-bar offset on the CMB leg of the HVDM 2of3 / 3of3
  cascade.
- **Multiple semantic-drift entries vs `T1`** (all also present in
  S39/S26 — i.e. T1 is the older/simpler engine):
  Floor/2F gating, UU oneOfThese gating, csNew3 1-bar offset, DispCons
  window-shift, AlphaStrike rewrite, UU/UUU/UUUU multi-path rewrite,
  Omega-A channel, dropping of `fire_BullUSub`/`fire_BearUSub`.

**Phase 2 python port:** `python_ports/hvd_pbj_ppd/v_2246_masterdir.py`
- 37 pure-pandas detect_* functions registered in `DETECTIONS`
- 8 state-machine classes registered in `STATE_MACHINES` (PBJEngine fully
  implemented; the 7 others are stub skeletons for the parent compiler)
- 74 stubbed entries in `STUBBED` representing detections that depend on
  the GZ1 FVG list / PingPong SR / Combo Chain / LS Chain / Alpha Strike /
  UU multi-path / Boom Hunter Omega state machines (these will be wired in
  by the cross-agent compiler once the shared state-machine library is
  ready)
- All 37 pure-pandas detections executed cleanly on a 200-bar synthetic
  OHLCV frame; no `NaN` propagation errors or shape mismatches
- The `# UNIQUE_TO_2246` marker is left in the file as a single comment
  block with no associated detect_* function (because no detection is
  unique to this file). Pointed at the Aggregator alert as the only
  unique 2246 contribution.

