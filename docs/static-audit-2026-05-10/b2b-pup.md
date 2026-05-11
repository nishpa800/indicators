# Static Audit — b2b-pup — 2026-05-10

## Summary
- Composites audited: 20 (B2B_PUP, B2B_PPD, B2B_HVD_BULL, B2B_HVD_BEAR, B2B_HVDPBJ_BULL, B2B_HVDPBJ_BEAR, B2B_NAPALM_BULL, B2B_NAPALM_BEAR, S1–S20)
- ✅ matched: 17
- ⚠️ drift: 3 (S3 composition, S8 composition, S11 composition)
- ❓ unclear: 0

---

## Per-composite findings

### b2b-pup::B2B_PUP
- YAML composition: AND_LAGGED — `det_PUP AND nz(det_PUP[1])`
- Pine source: L978: `bool det_b2bPUP=det_PUP and nz(det_PUP[1])`
- Pine plot: L1047: `plotshape(fire_S1_bull,"B2B Bull",shape.diamond,location.belowbar,color.new(#4CAF50,0),text="B2B",textcolor=color.white,size=size.normal)` — no `offset=` parameter (offset=0 implied)
- Verdict: ✅ MATCH

### b2b-pup::B2B_PPD
- YAML composition: AND_LAGGED — `det_PPD AND nz(det_PPD[1])`
- Pine source: L978: `bool det_b2bPPD=det_PPD and nz(det_PPD[1])`
- Pine plot: L1048: `plotshape(fire_S1_bear,"B2B Bear",shape.diamond,location.abovebar,color.new(#E91E63,0),text="B2B",textcolor=color.white,size=size.normal)` — no offset param (offset=0 implied)
- Verdict: ✅ MATCH

### b2b-pup::B2B_HVD_BULL
- YAML composition: AND_LAGGED — `det_HVDBull AND nz(det_HVDBull[1])`, offset=-1
- Pine source: L328: `bool det_B2BHVDBull=det_HVDBull and nz(det_HVDBull[1])`
- Pine plot: feeds S17; S17 plot at L1077 `offset=-1` confirmed
- Verdict: ✅ MATCH

### b2b-pup::B2B_HVD_BEAR
- YAML composition: AND_LAGGED — `det_HVDBear AND nz(det_HVDBear[1])`, offset=-1
- Pine source: L329: `bool det_B2BHVDBear=det_HVDBear and nz(det_HVDBear[1])`
- Verdict: ✅ MATCH

### b2b-pup::B2B_HVDPBJ_BULL
- YAML composition: AND_OR — `B2B_HVD_BULL AND (PBJBull[-1] OR PBJBull[-2])`, offset=-1
- Pine source: L330: `bool det_B2BHVDPBJBull=det_B2BHVDBull and (nz(det_PBJBull[1]) or nz(det_PBJBull[2]))`
- Verdict: ✅ MATCH

### b2b-pup::B2B_HVDPBJ_BEAR
- YAML composition: AND_OR — `B2B_HVD_BEAR AND (PBJBear[-1] OR PBJBear[-2])`, offset=-1
- Pine source: L331: `bool det_B2BHVDPBJBear=det_B2BHVDBear and (nz(det_PBJBear[1]) or nz(det_PBJBear[2]))`
- Verdict: ✅ MATCH

### b2b-pup::B2B_NAPALM_BULL
- YAML composition: AND_LAGGED — `(Napalm_BULL OR Charge_BULL) AND (Napalm_BULL OR Charge_BULL)[-1]`, offset=0
- Pine source: L695-L697: `bool det_bullNapCons=det_bullNapalm or det_bullCharge` (L695), `bool det_b2bBullNapalm=det_bullNapCons and nz(det_bullNapCons[1])` (L697)
- Verdict: ✅ MATCH — YAML uses Napalm/Charge pair; Pine implements as consolidated `det_bullNapCons`, semantically identical

### b2b-pup::B2B_NAPALM_BEAR
- YAML: mirror of B2B_NAPALM_BULL bear side
- Pine source: L696, L698: `bool det_bearNapCons=det_bearNapalm or det_bearCharge`, `bool det_b2bBearNapalm=det_bearNapCons and nz(det_bearNapCons[1])`
- Verdict: ✅ MATCH

### b2b-pup::S1
- YAML composition: PLOT_OF — `B2B_PUP / B2B_PPD`, offset=0
- Pine source: L1023: `bool fire_S1_bull=en_S1 and det_b2bPUP and g01 and masterGate`
- Pine plot: L1047-L1048 — no offset param (offset=0 implied, confirmed)
- YAML plot_call exactly matches Pine L1047-L1048
- Verdict: ✅ MATCH

### b2b-pup::S2
- YAML composition: AND — `B2B_PUP AND FAUNA_BULL[0] AND FAUNA_BULL[-1]`, offset=0
- Pine source: L979: `bool det_S2_bull=det_b2bPUP and det_FAUNABull and nz(det_FAUNABull[1])`
- Pine plot: L1049-L1050 — no offset param (offset=0)
- YAML plot_call exactly matches L1049-L1050
- Verdict: ✅ MATCH

### b2b-pup::S3
- YAML composition: `PUP[-1] AND PUP[-2] AND (DISPBull OR HVDBull) on bar[0] AND (DISPBull OR HVDBull) on bar[-1]`, offset=-1
- Pine source: L980-L982:
  - `bool det_S3_bull=nz(det_PUP[1]) and nz(det_PUP[2]) and det_DISPBull and nz(det_DISPBull[1])`
  - `bool det_S3d_bull=nz(det_PUP[1]) and nz(det_PUP[2]) and det_HVDBull and nz(det_HVDBull[1])`
  - `bool det_S3_any_bull=det_S3_bull or det_S3d_bull`
- Pine plot: L1051: `plotshape(fire_S3_bull,...,offset=-1)` — confirmed offset=-1
- YAML plot_call exactly matches L1051-L1052
- Verdict: ⚠️ DRIFT — YAML describes "DISP or HVD" as a single combined OR operand (implying they can mix within one bar), but Pine implements two DISJOINT paths: `det_S3_bull` (DISP only) and `det_S3d_bull` (HVD only) that are then OR'd via `det_S3_any_bull`. The result is that you cannot have one bar fire DISP and the other fire HVD — each path requires the SAME type on both bars. YAML phrasing is misleading and should be updated to reflect the two distinct paths.

### b2b-pup::S4
- YAML composition: `B2B PUP+FAUNA (S2-style) AND (DISPBull OR HVDBull) x2`, offset=-1
- Pine source: L983-L987: implements two parallel paths — `det_S4_bull` (DISP) and `det_S4d_bull` (HVD) combined via `det_S4_any_bull`
- Pine plot: L1053-L1054 confirmed `offset=-1`
- Verdict: ⚠️ DRIFT — same structural issue as S3: Pine enforces same-type on both bars (DISP path OR HVD path), not a free mix. YAML implies free mixing. Update YAML to match Pine's two-path architecture.

### b2b-pup::S5
- YAML composition: `B2B_PUP AND directional RVOL on both bars (with neutral allowed as "other" side)`, offset=0
- Pine source: L988-L992: complex directional + neutral gating (saab_dir_b, saab_neut, etc.) — exact logic matches YAML description
- Pine plot: L1055-L1056 — no offset param (offset=0)
- Verdict: ✅ MATCH

### b2b-pup::S6
- YAML composition: `any B2B chain AND (PBJBull/Bear or HVDPBJBull/Bear on bar[0/1/2])`, offset=-1
- Pine source: L994-L995: complex multi-clause (anyB2B_nd_bull, det_S3_any_bull, det_S4_any_bull paths all covered)
- Pine plot: L1057-L1058 confirmed `offset=-1`
- Verdict: ✅ MATCH

### b2b-pup::S8
- YAML composition: `(B2B_PUP OR S3-chain) AND UnifiedBull (current or [-1])`, offset=-1
- Pine source: L996: `bool det_S8_bull=(det_b2bPUP and det_UnifiedBull) or (det_S3_any_bull and (det_UnifiedBull or nz(det_UnifiedBull[1])))`
- Pine plot: L1059-L1060 confirmed `offset=-1`
- Verdict: ⚠️ DRIFT — YAML says `B2B_PUP` path also allows `UnifiedBull[-1]` (current or prior), but Pine's `B2B_PUP` arm requires `det_UnifiedBull` (current bar only, no lag). Only the `S3-chain` arm allows `UnifiedBull or nz(UnifiedBull[1])`. Anish needs to decide: should the B2B_PUP arm also accept UC on bar[-1] (update Pine) or should the YAML be corrected to reflect the tighter S8 B2B_PUP arm?

### b2b-pup::S9
- YAML composition: `(B2B_PUP OR S3-chain) AND (UC2 OR FMU current or lagged)`, offset=-1
- Pine source: L999-L1003: s9_combo_bull = det_UC2Bull or det_FMUBull; full multi-clause expression
- Pine plot: L1061-L1062 confirmed `offset=-1`
- Verdict: ✅ MATCH

### b2b-pup::S10
- YAML composition: `Long1 x2 AND (B2B_PUP current or [-1])`, offset=0
- Pine source: L1005: `bool det_S10_bull=(det_Long1 and nz(det_Long1[1])) and (det_b2bPUP or nz(det_b2bPUP[1]))`
- Pine plot: L1063-L1064 — no offset param (offset=0)
- Verdict: ✅ MATCH

### b2b-pup::S11
- YAML composition: `B2B_PUP AND (CS1Bull OR Long1 current or [-1])`, offset=-1
- Pine source: L1007: `bool det_S11_bull=det_b2bPUP and (det_CS1Bull or det_Long1 or nz(det_Long1[1]))`
- Pine plot: L1065-L1066 confirmed `offset=-1`
- Verdict: ⚠️ DRIFT — YAML says `CS1Bull OR Long1 (current or [-1])` but Pine has `det_CS1Bull or det_Long1 or nz(det_Long1[1])` — CS1Bull does NOT have a `[1]` lag option in Pine. Only `Long1` gets the `[-1]` lag. YAML implies CS1Bull can also lag by 1, which is incorrect. Update YAML: CS1Bull is current-bar only; Long1 accepts current-or-prior.

### b2b-pup::S12
- YAML composition: `B2B_PUP AND (UU OR UUU OR UUUU current or [-1])`, offset=0
- Pine source: L1010: `bool det_S12_bull=det_b2bPUP and (anyUU_bull or nz(anyUU_bull[1]))`
- Pine plot: L1067-L1068 — no offset param (offset=0)
- Verdict: ✅ MATCH

### b2b-pup::S13
- YAML composition: `B2B_PUP AND B2B_NAPALM_BULL (current or [-1])`, offset=0
- Pine source: L1011: `bool det_S13_bull=det_b2bPUP and (det_b2bBullNapalm or nz(det_b2bBullNapalm[1]))`
- Pine plot: L1069-L1070 — no offset param (offset=0)
- Verdict: ✅ MATCH

### b2b-pup::S14
- YAML composition: `B2B_PUP AND CONT_BULL (current or [-1])`, offset=0
- Pine source: L1012: `bool det_S14_bull=det_b2bPUP and (det_contBull or nz(det_contBull[1]))`
- Pine plot: L1071-L1072 — no offset param (offset=0)
- Verdict: ✅ MATCH

### b2b-pup::S15
- YAML composition: `B2B_PUP AND TNT_CONS_BULL (current or [-1])`, offset=0
- Pine source: L1013: `bool det_S15_bull=det_b2bPUP and (det_bullTNT or nz(det_bullTNT[1]))`
- Pine plot: L1073-L1074 — no offset param (offset=0)
- Verdict: ✅ MATCH

### b2b-pup::S16
- YAML composition: `B2B_PUP AND (Napalm_BULL OR Charge_BULL current or [-1])`, offset=-1
- Pine source: L1014: `bool det_S16_bull=det_b2bPUP and (det_bullNapCons or nz(det_bullNapCons[1]))`
- Pine plot: L1075-L1076 confirmed `offset=-1`
- Verdict: ✅ MATCH

### b2b-pup::S17
- YAML composition: `B2B_PUP AND B2B_HVD_BULL (current or [-1])`, offset=-1
- Pine source: L1015: `bool det_S17_bull=det_b2bPUP and (det_B2BHVDBull or nz(det_B2BHVDBull[1]))`
- Pine plot: L1077-L1078 confirmed `offset=-1`
- Verdict: ✅ MATCH

### b2b-pup::S18
- YAML composition: `B2B_PUP AND B2B_HVDPBJ_BULL (current or [-1])`, offset=-1
- Pine source: L1016: `bool det_S18_bull=det_b2bPUP and (det_B2BHVDPBJBull or nz(det_B2BHVDPBJBull[1]))`
- Pine plot: L1079-L1080 confirmed `offset=-1`
- Verdict: ✅ MATCH

### b2b-pup::S19_UC2
- YAML composition: COUNT_GE — count of UnifiedBull bars in [1, uc2_window], offset=-1
- Pine source: L803-L816 (det_UC2Bull logic); L1040: `bool fire_UC2_bull=en_UC2 and det_UC2Bull and (g01 or gd) and masterGate`
- Pine plot: L1083-L1084 confirmed `offset=-1`
- Verdict: ✅ MATCH

### b2b-pup::S20_FMU
- YAML composition: COUNT_GE — count of CS1Bull OR CS2Bull bars, offset=-1
- Pine source: L825-L841 (det_FMUBull logic); L1041: `bool fire_FMU_bull=en_FMU and det_FMUBull and (g01 or gd) and masterGate`
- Pine plot: L1086-L1087 confirmed `offset=-1`
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

1. **S3 / S4 composition** — YAML says `(DISPBull OR HVDBull) on bar[0] AND (DISPBull OR HVDBull) on bar[-1]` implying free-mix. Pine enforces two separate paths: DISP-only path OR HVD-only path (no mixing). **Recommend: update YAML** to describe the two disjoint paths (`det_S3_bull OR det_S3d_bull`). No Pine change needed unless Anish wants free-mixing.

2. **S8 bull arm** — YAML says both `B2B_PUP` and `S3-chain` accept `UnifiedBull (current or [-1])`. Pine: `B2B_PUP` arm requires `det_UnifiedBull` (current bar only); only `S3-chain` arm allows `UnifiedBull[-1]`. **Anish decision required**: should `B2B_PUP` arm also accept `UC[-1]` (tighten YAML or loosen Pine)?

3. **S11 CS1Bull lag** — YAML implies `CS1Bull` may lag by 1. Pine: `CS1Bull` is current-bar only; only `Long1` has `[1]` lag. **Recommend: update YAML** to clarify CS1Bull is bar[0] only.
