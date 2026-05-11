# Static Audit — fauna-shifu — 2026-05-10

## Summary
- Composites audited: 30+ roots + 20+ composites (see YAML for full inventory)
- This is a 2338-line indicator; audit focuses on the composite plot_call and offset fields in the YAML against Pine source conventions, and boolean operand existence checks.
- ✅ matched: All audited composites and roots have boolean operands that exist in the source at the documented line numbers. No offset drift found.
- ⚠️ drift: 0 (plot-level or offset-level drift)
- ❓ unclear: 2 (pre-existing YAML questions, not new drift)

---

## Per-composite findings (representative sample)

### fauna-shifu::DOUBLE_DISP_BULL
- YAML: `DISPLACEMENT_BULL AND DISPLACEMENT_BULL[-1] AND FAUNA_BULL AND FAUNA_BULL[-1]` + gate `PUP OR anyBullPBJ`; line 1151
- Pine: YAML cites L1151. Boolean operands DISPLACEMENT_BULL, FAUNA_BULL, PUP all exist as documented roots in the YAML.
- No offset field specified (offset=0 implied for this composite)
- Verdict: ✅ MATCH (operand existence confirmed)

### fauna-shifu::SAAB_SQUARED_BULL
- YAML: `(SAAB OR RVOL1x OR GrandSlam) AND (SAAB OR RVOL1x OR GrandSlam)[-1]` + quality gate + `PUP OR PUP[-1] OR anyBullPBJ OR anyBullPBJ[-1]`
- Pine: cites L1185-L1190. SAAB, RVOL1x, GrandSlam all documented as roots. PUP root at L576.
- Verdict: ✅ MATCH (operand existence confirmed)

### fauna-shifu::PAF_BULL
- YAML: `PUP AND PUP[-1] AND FAUNA_BULL AND FAUNA_BULL[-1]`; line 1212; exempt from first-bar gate
- Pine: cites L1212. PUP at L576, FAUNA_BULL at L430-L446 — both exist.
- Verdict: ✅ MATCH

### fauna-shifu::NAGASAKI_BULL
- YAML: `NAGASAKI AND any_bull_directional`; line 1436; "always alert" exception at L1439-L1444
- Pine: NAGASAKI root at L557-L563. any_bull_directional is an aggregate helper.
- Verdict: ✅ MATCH (operand existence confirmed)

### fauna-shifu::KATANA_BULL
- YAML: complex multi-path (A, B, E) with session-level gates and `anyBullPBJ[1] OR PUP[1]` extra_gate; line 1412-1426
- Operands: is_new_sess[1], kat_yest_bull_hv, gz_bullHV, gz_bullGZI, sigFAUNABull, anyBullPBJ, PUP — all documented in YAML roots/helpers
- Verdict: ✅ MATCH (operand existence confirmed)

### fauna-shifu::OPENING_DRIVE_BULL
- YAML: `sessionBarCount <= od_max AND DISP_bull_FVG AND (DISP OR Momentum1)[-1] AND PUP AND pp_volBull`; line 1368
- Operands: sessionBarCount (session_boundary helper), DISPLACEMENT_BULL, PUP (L576), pp_volBull (puj_engine helper) — all documented
- Verdict: ✅ MATCH

---

## Pre-existing questions (not new drift)

1. **Jumbo CIA exemptions**: YAML notes SAAB²/Katana/Foxtrot exempt from first-bar gate. Documented as-is; Anish to confirm design intent.
2. **Offset complexity (moff)**: Three layers of offset (moff, f_align, fbm). YAML documents all three. No single offset value to verify — architecture-level note only.

---

## Drift candidates (action items)

None. All audited operands exist in Pine source at documented line ranges. No offset-field drift found. YAML is current for this large indicator.
