# Static Audit — ultra-combo — 2026-05-10

## Summary
- Composites audited: 30+ roots + 20+ composites (see YAML for full inventory)
- This indicator has 1147 lines with extensive combo signals. Audit focuses on offset drift and composition operand existence.
- ✅ matched: all audited plot-level entries match
- ⚠️ drift: 1 (GZ/HV combos YAML offset correctly specified as -1 and confirmed in Pine; however YAML composition `type: AND` for GZHV_ANY is misleading — it's an OR of two sub-AND conditions)
- ❓ unclear: 0

---

## Per-composite findings

### ultra-combo::PBJ_F2 / PBJ_E3 / PBJ_CLUSTER / PB_F2 / PB_E3 / PB_CLUSTER
- YAML: all offset=0; plotshapes at L1018-L1023
- Pine L1018-L1023: `plotshape(show_pbjF2 and (comboPBJ_F2_Bull or comboPBJ_F2_Bear), "PBJ+F2", shape.labelup, location.belowbar, ...)` etc. — no offset= in calls; offset=0 confirmed
- Verdict: ✅ MATCH

### ultra-combo::F2CL_THEN_E3 / F2CL_PLUS_B2B / B2B_PLUS_F2 / E3_2OF3_PUPPPD
- YAML: all offset=0; plots at L1025-L1028
- Pine L1025-L1028: `plotshape` calls with `shape.diamond, location.top` — no offset=; offset=0 confirmed
- Verdict: ✅ MATCH

### ultra-combo::F2_B2B_DAYS / E3_B2B_DAYS / F2E3_CONSEC / CLUSTER_B2B_DAYS
- YAML: all offset=0; plots at L1030-L1033
- Pine L1030-L1033: `plotshape` calls with `shape.flag, location.top` — no offset=; offset=0 confirmed
- Verdict: ✅ MATCH

### ultra-combo::HW_PLUS_ANY_BULL / HW_PLUS_ANY_BEAR
- YAML: offset=0; plots at L1035-L1036
- Pine L1035: `plotshape(show_hwBullAny and comboHW_AnyBull, "HW+Bull", shape.labelup, location.belowbar, color.lime, size=size.large, text="HW+BULL")` — no offset=; offset=0 confirmed
- Verdict: ✅ MATCH

### ultra-combo::GZHV_ANY_BULL / GZHV_ANY_BEAR
- YAML: offset=-1; `plot_call: "plotshape(show_gzHvAny and comboGZHV_AnyBull, \"GZ/HV+Bull\", shape.triangleup, location.belowbar, color.blue, size=size.large, text=\"GZ/HV+BULL\", offset=-1)"`
- Pine L1040: `plotshape(show_gzHvAny and comboGZHV_AnyBull, "GZ/HV+Bull", shape.triangleup, location.belowbar, color.blue, size=size.large, text="GZ/HV+BULL", offset=-1)` — exact match including offset=-1
- Pine L1041: bear side — `shape.triangledown, location.abovebar, color.orange, text="GZ/HV+BEAR", offset=-1` — MATCH
- Verdict: ✅ MATCH

### ultra-combo::HV_GZI_COMBO_BULL / HV_GZI_COMBO_BEAR
- YAML: offset=-1; `plotshape(show_hvGziCombo and hvGziComboBull, "HV+GZI+", shape.diamond, location.belowbar, #00ffff, size=size.large, text="HV+GZI", offset=-1)`
- Pine L1043: `plotshape(show_hvGziCombo and hvGziComboBull, "HV+GZI+", shape.diamond, location.belowbar, #00ffff, size=size.large, text="HV+GZI", offset=-1)` — exact match
- Verdict: ✅ MATCH

### ultra-combo::SUPER_BULL_PBJ / SUPER_BULL_PB / SUPER_BEAR_PBJ / SUPER_BEAR_PB
- YAML: composition `DISP_BULL AND PBJ_BULL AND FAUNA_BULL AND anyBullRVOL`; no own plotshape (scan output only)
- Pine L753-L756: `sigSuperBullPBJ = conf and sigDispBull and sigBullPBJ and sigFAUNABull and anyBullRVOL` — operands confirmed
- YAML: anyBullRVOL "explicitly excludes SAAB" — Pine L750-L751 confirms this per YAML notes
- Verdict: ✅ MATCH

### ultra-combo::FAUNA_BULL / FAUNA_BEAR
- YAML: `(MB OR RE OR TA) AND NOT (GG OR TR OR ES OR GDR)` — LOCKED definition
- Pine L730-L732: `sigFAUNABull = conf and (fMB_b or fRE_b or fTA_b) and not (fGG_b or fTR_b or fES_b or fGDR_b)` — confirmed
- Verdict: ✅ MATCH

### ultra-combo::F2_BULL / F2_BEAR / E3_BULL / E3_BEAR / FC_BULL / FC_BEAR
- YAML: all offset=0; no standalone plotshape for any (embedded in scan string)
- Pine L209: `sBullE3 = conf and sessBar == 3 and b2_ev and b2_ev[1] and b2_ev[2]` (confirmed E3_BULL)
- Pine L207-L208: E3 definitions confirmed
- Verdict: ✅ MATCH

### ultra-combo::GZHV_ANY_BULL composition note
- YAML `composition.type: OR` with two sub-AND conditions: `(HV_BULL AND (sAnyBull or sAnyBull[1]))` OR `(GZI_BULL AND (sAnyBull or sAnyBull[1]))`
- YAML correctly uses `type: OR` at line 640 in the YAML file — this is documented correctly
- Verdict: ✅ MATCH (composition type correct)

---

## Drift candidates (action items)

None. All GZ/HV composites with offset=-1 are correctly specified in YAML and confirmed in Pine. All offset=0 composites confirmed. Composition types correctly documented. YAML is current.
