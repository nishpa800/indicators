# HVD+PBJ+PPD delta — file: HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine

Audited file: `hvd-pbj-ppd/versions/HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine` (1939 lines)
Compared against:
- `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` (1939 lines — byte-near-twin)
- `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` (1767 lines)
- `HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine` (2246 lines)

## Section 0 — Byte-near-twin check vs HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine
- Equal? **near** (line counts match exactly: 1939 == 1939)
- `diff -u | wc -l`: **221**
- Diff hunks (`@@`): **10**
- Notable changed regions (line numbers reference 1939_FROM_MASTERDIR file):
  - Lines 324–386 — Tier-1 detection toggle defaults (`show_*` IPSF flips, mostly bear-side `true→false`, e.g. `show_BearUUUU`, `show_BearUUU`, `show_OmegaLongA`, `show_AlphaStrike{B,R}`, `show_FoxtrotR`, `show_OmegaLong`, `show_ODBear`, `show_DispConsBear2`, `show_BullFloor/Bull2ndFloor/BearRooftop/BearPenthouse`, `show_HWBear`, `show_SuperBull/Bear`, `show_SDuperBear`, `show_CS{1B,1R,2B,2R,3R}`, `show_CCBear`, `show_LSCBull/Bear`).
  - Line 397 — `i_std_min` default: 1939=`4.5`, 4.26=`6.0`.
  - Line 397 — `i_disp3_std_min` default: 1939=`3.0`, 4.26=`4.0`.
  - Line 426 — `p21_pbj_dist` default: 1939=`4`, 4.26=`1`.
  - Line 435 — momentum-1 defaults: `ls_reg1` 7.0→10.0, `ls_cum1` 3.5→5.0.
  - Line 437 — momentum-2 defaults: `ls_reg2` 5.0→8.0, `ls_cum2` 2.5→4.0.
  - Line 440 — combo-set body% defaults: `cs_bodyPct_FVG` 0.69→0.74, `cs_bodyPct_MAT` 0.69→0.74.
  - Line 451 — LSC mom-1: `lsc_reg1` 7.0→10.0, `lsc_cum1` 3.5→5.0, `lsc_body1` 0.69→0.74.
  - Line 453 — LSC mom-2: `lsc_reg2` 5.0→8.0, `lsc_cum2` 2.5→4.0, `lsc_body2` 0.69→0.79.
  - Lines 1387–1392 — Pipeline-C `en_hvd_*` enable flags (all `true→false` in 4.26).
  - Lines 1484–1487 — Pipeline-D `co_en_*` enable flags (all `true→false` in 4.26).
  - Lines 1510–1515 — B2B enable flags (bull stay true; bear flip `true→false` in 4.26).
  - Lines 1577–1586 — `en_hvdm_*` co-occurrence enable flags (bear flips `true→false` in 4.26).

**Verdict:** every diffing line is an `input.bool/int/float` *default* — no body, no operand, no offset, no gate change. Per spec these are NOT real drift. Files are semantic-equivalent under matching defaults.

## Summary

The 1939_FROM_MASTERDIR variant is byte-near-identical to 4.26.1244am (only IPSF default flips). Against THE_ONLY_ONE (1767) and 2246 (2246) it carries multiple genuine semantic drifts, concentrated in:

1. **Engine 8 (UU/UUU/UUUU pathways)** — completely different qualifier and decision body vs THE_ONLY_ONE; subset of paths vs 2246's expanded paths A–H.
2. **DispConsBull/Bear N+** — offset shift (lag-1+lag-2 vs lag-0+lag-1) vs THE_ONLY_ONE.
3. **csNew3 (Unified Combo)** — uses `nz(csNew2[1])` (lag) here, current-bar AND in THE_ONLY_ONE.
4. **CC chain reset** — broader sustain set (all 4 comboSets) vs THE_ONLY_ONE (only MAT sets 3 & 4).
5. **Floor/2ndFloor gating** — extra `floor_gated`/`floor2_gated` chain absent in THE_ONLY_ONE.
6. **Alpha Strike** — drops `or sigBullPB`, drops `as_disp_bull` gate (vs THE_ONLY_ONE / 2246 respectively).
7. **`as_fauna_bull/bear`** — different OR-list (includes `hvd_fire_bull/bear` here; THE_ONLY_ONE drops it; 2246 drops both `sigDISPBull` and `hvd_fire_bull`, adds `sigNagPlusBull`).
8. **Master gate wrapper** — every `fire_*` here is `…and masterGate`; THE_ONLY_ONE has none, 2246 has none. Default-enabled-on so equivalent under defaults but constitutes an added gate.
9. **Exclusive detections in 1939** — `sigOmegaLongA` / `fire_OmegaLongA` exist in 1939 (and 2246, 4.26) but NOT in THE_ONLY_ONE. Conversely THE_ONLY_ONE has `sigUSubBull/Bear` & `fire_BullUSub/BearUSub`, absent here. (Different scope, not drift of a same-named root.)
10. **`uu_gated_bull` wrapper** — `fire_BullUU` here is `show_BullUU and uu_gated_bull` where `uu_gated_bull = sigUUBull and oneOfThese_forUU`. THE_ONLY_ONE: `fire_BullUU = show_BullUU and sigUUBull` (no extra OR-gate).

## REAL-drift table

Notation: line numbers are file-local. "1939" = HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine; "ONLY" = HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine; "2246" = HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine.

| Detection plot | This file (line) | Sibling file (line) | Diff kind | One-line semantic difference |
|---|---|---|---|---|
| `sigDispConsBull2` | 1939: L570 — `sigDISP2Bull and disp2_bullStreak>=2 and nz(sigFAUNABull[1]) and nz(sigFAUNABull[2])` | ONLY: L1011 — `… and sigFAUNABull and nz(sigFAUNABull[1])` | DIFFERENT OFFSET | 1939 references FAUNA at lag-1+lag-2 (bar N-1 & N-2); ONLY references current bar + lag-1. Same vs 2246 / 4.26. |
| `sigDispConsBear2` | 1939: L571 | ONLY: L1012 | DIFFERENT OFFSET | Mirror of above. Same vs 2246 / 4.26. |
| `sigDispConsBull3` | 1939: L587 — `… and nz(sigFAUNABull[1]) and nz(sigFAUNABull[2]) and nz(sigFAUNABull[3])` | ONLY: L1029 — `… and sigFAUNABull and nz(sigFAUNABull[1]) and nz(sigFAUNABull[2])` | DIFFERENT OFFSET | 1939 lag-1+lag-2+lag-3; ONLY current+lag-1+lag-2. Same vs 2246 / 4.26. |
| `sigDispConsBear3` | 1939: L588 | ONLY: L1030 | DIFFERENT OFFSET | Mirror. Same vs 2246 / 4.26. |
| `csNew3_Bull` | 1939: L968 — `csNew1_Bull and nz(csNew2_Bull[1])` | ONLY: L1083 — `csNew1_Bull and csNew2_Bull` | DIFFERENT OFFSET | 1939 requires CS1 now AND CS2 on prior bar; ONLY requires both same bar. Same vs 2246 / 4.26. |
| `csNew3_Bear` | 1939: L968 | ONLY: L1083 | DIFFERENT OFFSET | Mirror. Same vs 2246 / 4.26. |
| `sigAlphaStrikeBull` | 1939: L1238 — `firstOfDay and bull_pp and (sigGrandSlam or sigBullRVOL1x) and sigBullPBJ and as_fauna_bull` | ONLY: L1230 — `… and (sigBullPBJ or sigBullPB) and as_fauna_bull` | DIFFERENT INCLUSION | ONLY accepts PB as substitute for PBJ; 1939 requires PBJ. |
| `sigAlphaStrikeBull` | 1939: L1238 | 2246 — `sessionBarCount<=od_max_bars and bull_pp and (sigGrandSlam or sigBullRVOL1x) and sigBullPBJ and as_disp_bull and as_fauna_bull` | DIFFERENT CONDITIONS | 2246 replaces `firstOfDay` with `sessionBarCount<=od_max_bars` AND adds extra `as_disp_bull` gate. |
| `sigAlphaStrikeBear` | 1939: L1239 | ONLY / 2246 mirror lines | DIFFERENT INCLUSION / CONDITIONS | Mirror of bull. |
| `as_fauna_bull` | 1939: L1236 — `sigFAUNABull or sigLong1 or sigDISPBull or hvd_fire_bull or sigPUP or sigWTC or sigHiroshima or sigNagasaki` | ONLY — drops `hvd_fire_bull`. 2246 — drops `sigDISPBull` AND `hvd_fire_bull`, ADDS `sigNagPlusBull`. | DIFFERENT INCLUSION | Internal helper consumed by AlphaStrike. Different ORed operand sets. |
| `as_fauna_bear` | 1939: L1237 | ONLY / 2246 | DIFFERENT INCLUSION | Mirror. |
| `sigP21BullUUUU` | 1939: L1172 + body L1173-1181 — uses `f_uu_bull_scan(min(streak,4))` returning 9 flags; final = `(pA∨pB∨pC∨pD∨pE∨pF) ∧ _ok`; qualifier `u_qual_bull = bb_baseBullish ∧ bb_normalizedPrice≥0.5` | ONLY: L945 — `conf and u4_bull_streak>=4 and u4_bull_hasDay1 and u4_pbj_bull and u4_disp_bull`; qualifier `u4_qual_bull = close>open` | DIFFERENT BOOLEAN DEFINITION + DIFFERENT INCLUSION | Completely different decision logic and bar-qualification predicate. |
| `sigP21BullUUUU` | 1939: L1172-1181 | 2246: L1083-1152 — same qualifier (`u_qual_bull ≥0.5`) but body adds paths G & H (`pG=_heavy_cnt>=3`, `pH=_has_d2p ∨ _has_d3p`), adds `_disp_gate` requirement (`_gate=_disp_gate ∨ _nagp`), adds `_struct_cnt>=3` alternative, adds `_pathF_cnt>=3` for path F (vs `(hf or hd) and hp` here), adds NagPlus future-bar look-ahead | DIFFERENT BOOLEAN DEFINITION | Fewer paths + simpler gate here vs 2246; gating semantics also differ (no `_disp_gate` requirement). |
| `sigP21BearUUUU` | 1939: L1208-1212 | ONLY: L946 / 2246: L1289+ | DIFFERENT BOOLEAN DEFINITION | Mirror of bull drift. |
| `sigP21BullUUU` | 1939: L1184-1193 | ONLY: L979 / 2246: L1155-1219 | DIFFERENT BOOLEAN DEFINITION | Same kinds of differences as UUUU. |
| `sigP21BearUUU` | 1939: L1215-1219 | ONLY: L980 / 2246: L1361+ | DIFFERENT BOOLEAN DEFINITION | Mirror. |
| `sigUUBull` | 1939: L1196-1205 | ONLY: L989 — `conf and p21_bull_streak==2 and p21_bull_sum>=th_1x and ((uu_pbj_bull and uu_disp_bull) or uu_excA_bull or uu_excC_bull)`; 2246: L1222+ adds path G/H/`_disp_gate` | DIFFERENT BOOLEAN DEFINITION + DIFFERENT INCLUSION | All three definitions are mutually distinct. |
| `sigUUBear` | 1939: L1222-1226 | ONLY: L990 / 2246: L1428+ | DIFFERENT BOOLEAN DEFINITION | Mirror. |
| `fire_BullUU` | 1939: L1360 — `show_BullUU and uu_gated_bull and masterGate` (where `uu_gated_bull = sigUUBull and oneOfThese_forUU`) | ONLY: L1271 — `show_BullUU and sigUUBull` | DIFFERENT GATE (added) | 1939 wraps `sigUUBull` with extra OR-of-many guard; ONLY does not. (Same body as 2246 except masterGate.) |
| `fire_BullFloor` | 1939: L1368 — `show_BullFloor and floor_gated and masterGate` (where `floor_gated = anyBullFloor and oneOfThese and cb1_pass_floor`) | ONLY: L1276 — `show_BullFloor and anyBullFloor` | DIFFERENT GATE (added) | 1939 adds two extra AND-conditions before firing; ONLY uses raw `anyBullFloor`. |
| `fire_Bull2ndFloor` | 1939: L1368 — `show_Bull2ndFloor and floor2_gated and masterGate` | ONLY: L1276 — `show_Bull2ndFloor and anyBull2nd` | DIFFERENT GATE (added) | Same kind as Floor. |
| All other `fire_*` (UUUU, UUU, AlphaStrike, Foxtrot, OD, DispCons, Golf, PAF, CS1/2/3, CC, LSC, HW, Super, SDuper, BearRooftop, BearPent, etc.) | 1939: L1359-1381 — `… and masterGate` appended | ONLY: L1265-1290 — no masterGate; 2246 — also no masterGate | DIFFERENT GATE (added) | 1939 (and 4.26 twin) prepend a single `masterGate` (= true unless `en_firstBarOnly` IPSF flipped). Default-equivalent but adds a gate. |
| `cc_bull_active` (state machine reset condition) | 1939: L1037 — `if not (comboSet1_Bull or comboSet2_Bull or comboSet3_Bull or comboSet4_Bull): cc_bull_active:=false` | ONLY: L1102 — `if not (comboSet3_Bull or comboSet4_Bull): cc_bull_active:=false` | DIFFERENT INTERNAL HELPER BODY | 1939 keeps CC alive while ANY of the 4 combo sets fire; ONLY only sustains on MAT (sets 3&4) — FVG sets fail to keep CC alive. Drives `sigCCBull` directly. (Same vs 2246 / 4.26.) |
| `cc_bear_active` | 1939: L1042 | ONLY: L1107 | DIFFERENT INTERNAL HELPER BODY | Mirror of above. |
| `sigOmegaLongA` / `fire_OmegaLongA` | 1939: L1336 / L1362 (defined) | ONLY: ABSENT | NEW DETECTION (this file vs ONLY) | Not a same-name drift; this is an exclusive detection in the 1939 family. Same as 2246 / 4.26. |
| `fire_BullUSub` / `fire_BearUSub` | 1939: ABSENT | ONLY: L1272 (defined) | DETECTION ABSENT (this file vs ONLY) | THE_ONLY_ONE has a U-Sub family root absent here. Counterpart of OmegaLongA's exclusivity. Listed for completeness. |

## Internal-helper drift

Helpers whose bodies were diffed even when wrapper signals match.

| Helper | This file (line) | Sibling | Diff |
|---|---|---|---|
| `as_fauna_bull` / `as_fauna_bear` | L1236-1237 | ONLY drops `hvd_fire_bull/bear`; 2246 drops `sigDISPBull/Bear` AND `hvd_fire_bull/bear` AND adds `sigNagPlusBull/Bear` | Different OR-set composition; affects every consumer of Alpha Strike's FAUNA slot. |
| `cc_bull_active` / `cc_bear_active` reset clause | L1037 / L1042 | ONLY: only sets 3 & 4 sustain (`if not (comboSet3 or comboSet4)`); here all four sustain | Affects sigCCBull/Bear emissions in low-MAT regimes. |
| `f_uu_bull_scan` / `f_uu_bear_scan` (this file's UU body engine, L1112-1169) | L1112-1169 | ONLY: no equivalent function — uses inline u4_*/u3_*/uu_* path-A logic only; 2246: no function — inlines an expanded loop with paths A–H, struct_cnt, heavy_cnt, pathF_cnt, _disp_gate, NagPlus look-ahead | Helper exclusive to 1939 (and 2246-shape-different); semantically governs all UU-family emissions. |
| `oneOfThese` / `oneOfThese_forUU` / `cb1_pass_floor` / `cb1_pass` / `floor_gated` / `floor2_gated` / `uu_gated_bull` (extra gating layer) | L1228-1248 | ONLY: ALL ABSENT; 2246: present (same expressions as 1939) | Extra AND-of-many gates between root signals and fire_*; absent in ONLY entirely. |
| `super_hw_bull/bear`, `super_comboAny_bull/bear`, `superBull/Bear`, `sduperBull/Bear`, `hwBull/Bear`, `anyBullFloor/anyBull2nd/anyBearRoof/anyBearPent`, `bull_hw_slot/bear_hw_slot`, `sigGolfBull/Bear`, `sigPAFBull/Bear`, `sigODBull/Bear`, `sigPUP/sigPPD`, `sigBullPBJ/sigBullPB/sigBearPBJ/sigBearPB`, `sigDISPBull/Bear`, `sigDISP2Bull/Bear`, `sigDISP3Bull/Bear`, `sigSAAB/sigKratos/sigGrandSlam/sigMOAB/sigBullRVOL1x/sigBearRVOL1x/sigWTC/sigHiroshima/sigPentagon/sigNagasaki`, `sigFoxtrotBull/Bear`, `sigLong1/Short1/Long2/Short2`, `sigNeoBull/Bear`, `sigTrinityBull/Bear`, `sigCCBull/Bear` (RHS only), `sigLSCBull/Bear` (RHS only), `sigOmegaLong`, `sigNagPlusBull/Bear`, `bull_pp/bear_pp` | L477-999 etc. | identical across all 4 files | NO DRIFT — bodies match byte-for-byte (modulo whitespace in some). |

## Hardcoded thresholds in this file (sorted by line)

Values appearing as numeric literals in body code (not `input.*` defaults):

| Line | Threshold | Value | Context |
|---|---|---|---|
| 75  | `atr14` lookback | `14` | shared ATR period |
| 96  | First-bar HV ranks tested | `50,75,100,150,200,250,300,350,400,450,500,550,600,650,700,750,1000` | masterGate gate |
| 118-135 | tfSec mapping table | `60..7776000` | timeframe constants |
| 322 | `fauna_gg_master`, `fauna_gg_body` | `true`, `0.80` | FAUNA Granny-Smith body floor |
| 411 | `pp_barSize`, `pp_lookback` | `3.0`, `10` | PUP/PPD bar % and high-vol-of-opposite lookback |
| 416 | `pp_trust_mode`, `pp_min_count` | `"Trusted Only"`, `3` | Ping-Pong SR trust-mode and min-count |
| 412-414 | Zoo MA / Supertrend constants | `zoo_ma_len=5`, `zoo_st_period=10`, `zoo_st_mult=2.0` | PBJ/PB engine |
| 510 | FAUNA helpers | `ta.sma(volume,20)`, `ta.sma(...,20)`, `ta.sma(...,10)`, `ta.sma(close,50)` | FAUNA window lengths |
| 517-520 | FAUNA bull-core thresholds | `1.6×atr`, `0.70` body ratio, `1.8×avgVol`, `2.2×atr` rng, `0.15×rng` upper-wick, `1.6×avgDelta`, `0.9×atr` (GG) | FAUNA NRA core (MB/RE/TA/GG) |
| 521-522 | FAUNA bear-context | `1.5×avgBody`, `1.5×avgVol`, `0.2` weak-body ratio | FAUNA prev-bar context |
| 530-535 | FAUNA bear-core thresholds | mirror of 517-522 | FAUNA bear |
| 552 | `disp5_thresh` | `disp_std*5.0` | HW disp5 trigger |
| 666 | `atr_pb` | `atr14*2.0` | PB lander box sizing |
| 1008 | sigHV75 lookback | `75` (literal) | HV ranking |
| 1009 | sigHV500 / sigHV1000 lookbacks | `500`, `1000` | HV ranking |
| 1244 | `cb_disp9` multiplier | `9.0` | Floor gate disp-9x escape clause |
| 1251-1255 | Boom Hunter / SuperSmoother constants | `0.707`, `1.414`, `2*math.asin(1)`, etc. | bh DSP filter coefficients |

(Constants under 50/100/200/500/1000 in HTF rank lookbacks are present everywhere — these match across the four files. Thresholds shown above all appear with the same numeric literal in 1939, 2246, 4.26, and (where present) THE_ONLY_ONE — no hardcoded-threshold drift detected within the family.)

## Notes for the cross-agent delta-table compiler

- The 1939_FROM_MASTERDIR file is the IPSF-default-flipped twin of 4.26.1244am (10 hunks, 221 raw diff lines, zero body changes between them). Treat them as a single semantic class for emission comparisons.
- Vs THE_ONLY_ONE: real drift in DispCons offsets, csNew3 offset, AlphaStrike inclusion, CC chain reset condition, Floor/2ndFloor gate added, UU family completely re-architected (different qualifier, different decision body, different OR-set).
- Vs 2246: shares the qualifier (`u_qual_bull = bb_baseBullish and bb_normalizedPrice>=0.5`), shares Floor/2ndFloor/UU gate names, shares AlphaStrike's `firstOfDay` (vs 2246's `sessionBarCount<=od_max_bars`), but lacks 2246's expanded UU paths G/H, lacks `_disp_gate` UU requirement, lacks AlphaStrike `as_disp_bull` gate, and lacks 2246's 700+ extra body lines (see 2246 sibling report for the additional composites).
- Exclusive to 1939 (vs THE_ONLY_ONE): `sigOmegaLongA`, `fire_OmegaLongA`, `sigNagPlusBull/Bear`, `fire_NagPlusBull`, all `floor_gated`/`floor2_gated`/`uu_gated_bull` gating helpers, `oneOfThese`/`cb1_pass*`/`cb_uu_any`/`cb_disp9`, `f_uu_bull_scan`/`f_uu_bear_scan` helper functions, `masterGate`/`en_firstBarOnly` first-bar restriction.
- Absent from 1939 (vs THE_ONLY_ONE): `sigUSubBull/Bear`, `fire_BullUSub/BearUSub`, `u4_*`/`u3_*` separate-streak helpers, `uu_excA_bull/bear`/`uu_excC_bull/bear` exception clauses, `p21_qual_bull/bear`.
- The detection-plot identity table for this variant should be drawn from `bible-input/extract-hvd-pbj-ppd-1939-masterdir.yaml` (42 roots + 23 composites) — that's authoritative for plot enumeration. The drift table above covers every plot whose underlying boolean differs from at least one sibling.

## Phase 2 / Phase 3 — Python port log

- Output: `python_ports/hvd_pbj_ppd/v_1939_masterdir.py`
- `python3 -c "import python_ports.hvd_pbj_ppd.v_1939_masterdir as m; print(len(m.DETECTIONS), 'detections,', len(m.STUBBED), 'stubbed')"` → **15 detections, 104 stubbed**
- 1 STATE_MACHINES entry (`UStreak`).
- Ported leaf detections (no engine deps): `sigPUP`, `sigPPD`, `sigDISPBull`, `sigDISPBear`, `disp5_bull`, `disp5_bear`, `sigDispConsBull2/3`, `sigDispConsBear2/3` (streak portion only — full body requires `sigFAUNABull` which is stubbed), `sigHV75`, `sigHV150`, `sigHV500`, `sigHV1000`, plus `pp_pct_gate` convenience.
- All other detections are stubbed with reasons; primary blockers are: FAUNA NRA core, Ping-Pong SR engine, PB&J Supertrend lander, GZ1 FVG bookkeeper, Boom Hunter omega DSP cascade, Matrix-number engine, RVOL/Pentagon/Nagasaki tfSec threshold tables, the U-streak path A..F decision body (`f_uu_bull_scan`/`f_uu_bear_scan`), and CC/LSC chain FSMs.
- Smoke test against synthetic OHLCV (200 bars, seed=0): all 15 detection callables and the `UStreak` state machine return correctly-shaped Series/DataFrame; no exceptions.

## Phase 4 — completion note

Audit complete for `HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine`. Section 0 confirms the file is a byte-near-twin of `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` (only IPSF defaults differ; zero body changes). Real semantic drift exists vs THE_ONLY_ONE (1767) and 2246 across: DispCons offset shifts, csNew3 lag, Alpha Strike inclusion/condition deltas, CC chain reset clause, the entire UU/UUU/UUUU body decision logic, the as_fauna_bull/bear OR-set, multiple added Floor/2nd/UU gating layers, and the masterGate first-bar wrapper. Python port file written, imports cleanly, smoke-tested. No `.pine` files modified, no files deleted.
