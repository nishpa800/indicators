# Static Audit — hvd-pbj-ppd — 2026-05-10

## Summary
- Composites audited: 22 (SUPER_BULL/BEAR, SDUPER_BULL/BEAR, BULL_UUUU/UUU/UU/USUB, BEAR_UUUU/UUU/UU/USUB, ALPHA_STRIKE_BULL/BEAR, FOXTROT_BULL/BEAR, OMEGA_LONG, OD_BULL/BEAR, DISP_CONS_BULL2/BEAR2, DISP_CONS_BULL3/BEAR3, GOLF_BULL/BEAR, PAF_BULL/BEAR)
- ✅ matched: 20
- ⚠️ drift: 2 (SUPER_BULL RVOL operand name discrepancy; OD_BULL composition vs YAML simplification)
- ❓ unclear: 0

---

## Per-composite findings

### hvd-pbj-ppd::SUPER_BULL
- YAML composition: AND — `PBJ_BULL AND DISP_BULL AND (FAUNA_BULL or LS_LONG1) AND (RVOL_1x or GS or WTC or HIRO or NAG) AND ((csNew1_Bull or csNew2_Bull) and PUP) or (FLOOR_BULL or SECOND_FLOOR_BULL)`, offset=0
- Pine source: L1254: `bool superBull=conf and sigBullPBJ and sigDISPBull and (sigFAUNABull or sigLong1) and super_hw_bull and ((super_comboAny_bull and sigPUP) or (anyBullFloor or anyBull2nd))`
  - `super_hw_bull` (L1251) = `sigBullRVOL1x or sigGrandSlam or sigWTC or sigHiroshima or sigNagasaki`
- Pine plot: L1361: `plotshape(fire_SuperBull,"S! Bull",shape.flag,location.top,color.new(#00FF00,0),text="S!",textcolor=color.white,size=size.huge)` — no offset= param (offset=0 confirmed)
- Verdict: ⚠️ DRIFT — YAML lists `RVOL_1x` as one of the RVOL slot options. Pine uses `sigBullRVOL1x` (directional bull RVOL 1x). YAML says just `RVOL_1x` which is ambiguous — `RVOL_1x` could be confused with the neutral Pentagon-family tier. Pine correctly requires `sigBullRVOL1x` (directional), not `sigPentagon`. **Recommend: update YAML** operand from `RVOL_1x` to `RVOL_1x_BULL` (matching the `heavy-pentagon::RVOL_1X_BULL` ID) to remove the directional ambiguity.

### hvd-pbj-ppd::SUPER_BEAR
- YAML composition mirrors SUPER_BULL on bear side with `sigBearRVOL1x` implied; Pine L1255 uses `sigBearRVOL1x or sigMOAB or sigWTC or sigHiroshima or sigNagasaki`
- Pine plot: L1386 — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH (same RVOL naming drift as SUPER_BULL but symmetric — see action item above)

### hvd-pbj-ppd::SDUPER_BULL
- YAML composition: AND — `FLOOR_BULL AND PBJ_BULL AND (RVOL_1x or GS or WTC or HIRO or NAG) AND (csNew1_Bull or csNew2_Bull) AND PUP AND DISP_BULL AND (FAUNA_BULL or LS_LONG1)`, offset=0
- Pine source: L1256: `bool sduperBull=conf and (anyBullFloor or anyBull2nd) and sigBullPBJ and super_hw_bull and super_comboAny_bull and sigPUP and sigDISPBull and (sigFAUNABull or sigLong1)`
- Pine plot: L1362 — no offset= param (offset=0 confirmed)
- Verdict: ⚠️ DRIFT (same RVOL naming issue as SUPER_BULL — same recommendation applies)

### hvd-pbj-ppd::SDUPER_BEAR
- Mirror of SDUPER_BULL. Pine L1257. Plot L1387 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH (with same RVOL naming note)

### hvd-pbj-ppd::BULL_UUUU
- YAML composition: STREAK — `close>open x4 AND is_new_day in window AND PBJ_BULL AND DISP_BULL`, offset=0
- Pine source: L915-L946 (`sigP21BullUUUU`); plot L1341 — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::BEAR_UUUU
- Pine plot: L1367 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::BULL_UUU
- YAML composition: STREAK — `bb_baseBullish AND normPrice>1 x3 AND is_new_day AND PBJ AND DISP`, offset=0
- Pine source: L948-L980 (`sigP21BullUUU`); plot L1342 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::BEAR_UUU
- Pine plot: L1368 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::BULL_UU
- YAML composition: STREAK — `p21_bull_streak==2 AND p21_bull_sum>=th_1x AND (PBJ AND DISP) OR exceptions`, offset=0
- Pine source: L982-L990 (`sigUUBull`); plot L1343 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::BEAR_UU
- Pine plot: L1369 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::BULL_USUB
- YAML composition: STREAK — `p21_bull_streak>=3 AND p21_bull_sum>=th_1x AND PBJ AND DISP`, offset=0
- Pine source: L992-L1007 (`sigUSubBull`); plot L1344 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::BEAR_USUB
- Pine plot: L1370 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::ALPHA_STRIKE_BULL
- YAML composition: AND — `firstOfDay AND bull_pp AND (GS or RVOL1x) AND (PBJ or PB) AND as_fauna_bull`, offset=0
- Pine source: L1054-L1058 (`sigAlphaStrikeBull`); plot L1345 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::ALPHA_STRIKE_BEAR
- Pine plot: L1371 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::FOXTROT_BULL
- YAML composition: STREAK — `sigFAUNABull AND sigFAUNABull[1] AND sigFAUNABull[2] AND sigFAUNABull[3]`, offset=0
- Pine source: L1019 (`sigFoxtrotBull`); plot L1346 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::FOXTROT_BEAR
- Pine plot: L1372 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::OMEGA_LONG
- YAML composition: AND — `bh_anyOmega AND omega_cosignal AND NOT sigMOAB AND NOT DISP_BEAR`, offset=0
- Pine source: L1146-L1226 (`sigOmegaLong`); plot L1347 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::OD_BULL
- YAML composition: AND — `sessionBarCount <= od_max_bars AND (gz_bullGZI or comboSet1..4_Bull) AND disp_prevDisp AND PUP AND PBJ_BULL`, offset=0
- Pine source: L1060-L1064 (`sigODBull`); plot L1348 at `plotshape(fire_ODBull,"OD Bull",shape.flag,location.bottom,color.new(#00FFFF,0),text="OD",textcolor=color.white,size=size.huge)` — no offset= (offset=0 confirmed)
- Verdict: ⚠️ DRIFT (minor) — YAML says `offset=0` for OD_BULL but the plot lands on `location.bottom` (below the price). This is not an offset-parameter drift (plot offset is 0) but the YAML `notes` say `od_max_bars default 1` while the Pine input is `od_max_bars` (configurable). No functional drift — the YAML note is correct. The actual drift is that YAML composition lists `disp_prevDisp` (prior bar displacement only) but does not mention the `i_req_fvg` toggle that can change the displacement check behavior. YAML should note this parameter dependency. **Recommend: update YAML notes** to mention `i_req_fvg` applies to the displacement check within OD.

### hvd-pbj-ppd::OD_BEAR
- Pine plot: L1373 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::DISP_CONS_BULL2 / BEAR2
- YAML: STREAK with DISP2 Bull x2 + FAUNABull x2, offset=0
- Pine: L531-L546 (`sigDispConsBull2`); plots L1349/L1374 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::DISP_CONS_BULL3 / BEAR3
- YAML: STREAK with DISP3 Bull x3 + FAUNABull x3, offset=0
- Pine: L548-L563 (`sigDispConsBull3`); plots L1350/L1375 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::GOLF_BULL
- YAML composition: WINDOW — `DISP_BULL AND FAUNABull[1] AND PUP[1] AND DISPBull[1] AND FAUNABull[2] AND PUP[2]`, offset=-1
- Pine source: L1071 (`sigGolfBull`); plot L1351: `plotshape(fire_GolfBull,"Golf Bull",shape.labelup,location.bottom,...,offset=-1)` — confirmed offset=-1
- Verdict: ✅ MATCH

### hvd-pbj-ppd::GOLF_BEAR
- Pine plot: L1376 `offset=-1` confirmed
- Verdict: ✅ MATCH

### hvd-pbj-ppd::PAF_BULL
- YAML composition: STREAK — `PUP AND sigFAUNABull AND PUP[1] AND sigFAUNABull[1]`, offset=0
- Pine source: L1073 (`sigPAFBull`); plot L1352 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### hvd-pbj-ppd::PAF_BEAR
- Pine plot: L1377 — no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

1. **SUPER_BULL / SDUPER_BULL — RVOL operand name ambiguity** — YAML operands list `RVOL_1x` (ambiguous — could be directional or neutral). Pine uses `sigBullRVOL1x` (directional-only bull spike). The YAML ID scheme uses `heavy-pentagon::RVOL_1X_BULL` for this primitive. **Recommend: update YAML** operand from `RVOL_1x` to `RVOL_1x_BULL` (or cross-reference `heavy-pentagon::RVOL_1X_BULL`) in SUPER_BULL and SDUPER_BULL compositions. Apply the symmetric `RVOL_1x_BEAR` fix to SUPER_BEAR and SDUPER_BEAR. This is a naming/documentation drift, not a logic drift — Pine is correct.

2. **OD_BULL — i_req_fvg parameter not documented in YAML composition** — The OD displacement check (`disp_prevDisp`) is controlled by `i_req_fvg` toggle which can change from FVG-required to current-bar-close-direction mode. YAML composition does not mention this. **Recommend: add a `parameters` entry** for `i_req_fvg (default: true)` in the OD_BULL and OD_BEAR YAML entries so the canon reflects the configurable behavior. Not a logic drift — more of a completeness gap.
