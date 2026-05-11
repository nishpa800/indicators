# Static Audit — squarify — 2026-05-10

## Summary
- Composites audited: 48 (S1–S46 + T1_OPENING_CONFLU + T2_OPENING_CONFLU)
- ✅ matched: 44
- ⚠️ drift: 3 (S1_SD_BANG offset mismatch in YAML plot_call; S2_SUPER offset missing in plot_call; S41/S42 WBUSH offset discrepancy)
- ❓ unclear: 1 (S3_HW YAML cross-indicator operand names ambiguous)

---

## Per-composite findings

### squarify::S1_SD_BANG
- YAML composition: AND — `UNIFIED_COMBO_BULL AND NPM_CONS_BULL AND PUP[1]`, offset=-1
- Pine source: L1689: `bool sduperBull = conf and csNew3_Bull and det_bullNapalmCons and nz(sigPUP[1])`
- Pine plot: L2227: `plotshape(_masterGate and en_1 and sduperBull,"1 SD!",shape.flag,location.bottom,#FFD700,text="SD!",textcolor=color.white,size=size.huge,offset=-1)`
- YAML plot_call matches L2227 exactly including `offset=-1`
- Verdict: ✅ MATCH — composition correct; PUP is `nz(sigPUP[1])` (prior bar) consistent with offset=-1 anchor on displacement bar

### squarify::S2_SUPER
- YAML composition: AND_NOT — `UNIFIED_COMBO_BULL AND NPM_CONS_BULL AND NOT S1_SD_BANG`, offset=-1
- Pine source: L1687: `bool superBull = conf and csNew3_Bull and det_bullNapalmCons`; plot gates `and not sduperBull`
- Pine plot: L2228: `plotshape(_masterGate and en_2 and superBull and not sduperBull,"2 SUPER",shape.flag,location.top,#00FF00,text="SUPER",textcolor=color.white,size=size.huge,offset=-1)`
- YAML plot_call matches L2228 exactly including `offset=-1`
- Verdict: ✅ MATCH

### squarify::S3_HW
- YAML composition: AND — `close>open AND disp5_bull AND hvd-pbj-ppd::PBJ_BULL AND (GS OR WTC OR HIRO OR (NAG AND nag_dir_bull)) AND (ANY_FLOOR OR ANY_2F)`, offset=0
- Pine source: around L1357 (`hwBull` definition); plot L2229: no `offset=` param (offset=0 confirmed)
- Verdict: ❓ UNCLEAR — The YAML references `squarify::ANY_FLOOR` and `squarify::ANY_2F` as if they are named root booleans. In Pine, these correspond to `floor_sq` and `floor2_sq` which are the Squarify-local Ping-Pong composites (S4/S5). The YAML cross-indicator reference `heavy-pentagon::PING_PONG_BULL` is listed as the dependency for Floor/2F but the actual Pine variable names differ. This is a documentation ambiguity, not a logic error. Recommend clarifying in YAML that `ANY_FLOOR` = `floor_sq` (S4) and `ANY_2F` = `floor2_sq` (S5) in the Pine source.

### squarify::S4_FLOOR
- YAML composition: AND — `PING_PONG_BULL AND PBJ_BULL AND bull_hw_slot AND oneOfThese AND cb1_pass_floor`, offset=0
- Pine source: L2151 area (`floor_sq`); plot L2230: no `offset=` param (offset=0 confirmed)
- Verdict: ✅ MATCH — confirmed no offset deviation

### squarify::S5_2F
- YAML composition: AND_NOT — `PING_PONG_BULL AND PB_BULL AND bull_hw_slot AND oneOfThese AND cb1_pass AND NOT S4_FLOOR`, offset=0
- Pine source: L2157 area (`floor2_sq`); plot L2231: no `offset=` param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S6_UUUU
- YAML composition: OR_PATHS — pA/pB/pC/pD/pE/pF/pG, offset=0
- Pine source: L912-L968 region (`sigP21BullUUUU`); plot L2232: no `offset=` param (offset=0 confirmed)
- Verdict: ✅ MATCH — path-OR structure described correctly

### squarify::S7_UUU
- YAML composition: OR_PATHS_AND_NOT — pA-pE/pG AND NOT S6_UUUU, offset=0
- Pine source: L970-L1023 (`sigP21BullUUU`); plot L2233: `and not sigP21BullUUUU`, no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S8_UU
- YAML composition: OR_PATHS_AND_GATE_AND_NOT — pA-pE/pG AND oneOfThese_forUU AND NOT S6/S7, offset=0
- Pine source: L1025-L1078 (`uu_gated`); plot L2234: `and not sigP21BullUUU and not sigP21BullUUUU`, no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S9_ALPHA_STRIKE
- YAML composition: AND — `firstOfDay AND PING_PONG_BULL AND (GS OR RVOL1x) AND PBJ_BULL AND as_fauna_expanded`, offset=0
- Pine source: L2148-L2150 (`sigAlphaStrikeBull_sq`); plot L2235: no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S10_OMEGA_A
- YAML composition: AND_NOT — `bh_anyOmega AND omega_cosignal_A AND NOT MOAB AND NOT sigDISPBear`, offset=0
- Pine source: L1773-L1774 (`sigOmegaLongA`); plot L2236: no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S11_FOX
- YAML composition: AND — `sigFoxtrotBull AND (hvd_pbj_bull OR oneOfThese)`, offset=0
- Pine source: L1224 (`foxtrot_sq`); plot L2237: no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S12_OD
- YAML composition: AND — `sessionBarCount<=od_max+1 AND od_fvg_bull AND disp_prevDisp AND PUP[1] AND PBJ_BULL[1]`, offset=-1
- Pine source: L1266-L1268 (`sigODBull`); plot L2238: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S13_GOLF
- YAML composition: SEQUENCE — `sigDISPBull AND sigFAUNABull[1] AND sigPUP[1] AND sigDISPBull[1] AND sigFAUNABull[2] AND sigPUP[2]`, offset=-1
- Pine source: L1276 (`sigGolfBull`); plot L2239: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S14_PBJ_F2_OR_E3
- YAML composition: OR — `(PBJ_BULL AND F2_BULL) OR (PBJ_BULL AND E3_BULL)`, offset=0
- Pine source: L2002-L2003; plot L2242: no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S15_PBJ_CL
- YAML composition: AND — `PBJ_BULL AND FC_BULL`, offset=0
- Pine source: L2003 (`comboPBJ_Cluster_Bull`); plot L2243: no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S16_F2CL_TO_E3
- YAML composition: SEQUENCE — `F2_BULL[1] AND FC_BULL[1] AND E3_BULL`, offset=0
- Pine source: L2004 (`comboF2Cluster_E3_Bull`); plot L2244: no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S17_E3_TWOTHIRDS_PUP
- YAML composition: AND — `E3_BULL AND pupCntE3>=2`, offset=0
- Pine source: L2009-L2010 (`comboE3_2of3PUP_Bull`); plot L2245: no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S18_F2_TIMES_2D through S21_CL_TIMES_2D
- YAML compositions: B2B-Days tracker combinations (F2_BULL + hadYesterday, E3_BULL + hadYesterday, F2→E3 sequence, FC_BULL + hadYesterday), all offset=0
- Pine plots: L2246-L2249 — none have offset= param (offset=0 confirmed for all 4)
- Verdict: ✅ MATCH (all 4)

### squarify::S22_NPM_PLUS
- YAML composition: AND — `NPM_CONS_BULL AND ((PBJ[1] AND (UC OR HW[1] OR WBUSH[1])) OR WBUSH[1])`, offset=-1
- Pine source: L2173 (`sig38`); plot L2252: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S23_NPM12
- YAML composition: AND — `NPM_CONS_BULL AND (cb1_pass_npm OR cb2_pass_npm)`, offset=-1
- Pine source: L2162 (`npm12`); plot L2253: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S24_NPM3
- YAML composition: AND_NOT — `NPM_CONS_BULL AND cb3_pass_npm AND NOT S23_NPM12`, offset=-1
- Pine source: L2163 (`npm3`); plot L2254: `and not npm12`, `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S25_B2BNPM
- YAML composition: AND — `NPM_CONS_BULL AND NPM_CONS_BULL[1]`, offset=-1
- Pine source: L1663 (`det_b2bBullNapalm`); plot L2255: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S26_NPM_PLUS_TNT
- YAML composition: AND — `raw_napalmBull AND raw_bullTNT[1]`, offset=-1
- Pine source: L1665 (`det_npmTntBull`); plot L2256: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S27_CO
- YAML composition: AND — `HVD_BULL AND PBJ_BULL[1] AND (UC OR csNew1_Bull)`, offset=-1
- Pine source: L1825-L1827 (`co_bull_pbj`); plot L2259: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S28_HVD_PBJ
- YAML composition: AND_NOT — `HVD_BULL AND PBJ_BULL[1] AND (tfSec>=180 OR cb1_pass_npm) AND NOT S27_CO`, offset=-1
- Pine source: L1810 (`hvd_pbj_bull`); plot L2260: `and not co_bull_pbj and (tfSec>=180 or cb1_pass_npm)`, `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S29_B2BHVD_PBJ
- YAML composition: AND — `HVD_BULL AND HVD_BULL[1] AND (PBJ_BULL[1] OR PBJ_BULL[2])`, offset=-1
- Pine source: L1834-L1836 (`b2b_bull_pbj`); plot L2261: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S30_B2BHVD
- YAML composition: AND_NOT — `HVD_BULL AND HVD_BULL[1] AND NOT S29 AND NOT b2b_bull_pb`, offset=-1
- Pine source: L1834-L1840; plot L2262: `and not b2b_bull_pbj`, `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S31_UU_PLUS_UC
- YAML composition: AND — `uu_any AND UNIFIED_COMBO_BULL`, offset=-1
- Pine source: L2209 (`sig_uu_combo`); plot L2263: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S32_GRAIL through S39_FOS_PUP_1X
- YAML compositions match Pine source at L2266-L2273; offsets confirmed:
  - S32 `offset=-1` (L2266), S33 `offset=-1` (L2267), S34 `offset=-1` (L2268), S35 `offset=0` (L2269 no param), S36 `offset=-1` (L2270), S37 `offset=-1` (L2271), S38 `offset=0` (L2272 no param), S39 `offset=0` (L2273 no param)
- Verdict: ✅ MATCH (all 8)

### squarify::S40_NPM_UC
- YAML composition: AND_NOT — `NPM_CONS_BULL AND UC AND NOT S44_NPM_UC_PBJ`, offset=-1
- Pine source: L2203 (`sig_npm_combo`); plot L2276: `and not sig_npm_combo_pbj`, `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S41_WBUSH_BULL
- YAML composition: ALIAS — `WBUSH_BULL`, offset=0
- YAML plot_call: `plotshape(_masterGate and en_wbushBull and sig_WBUSH_Bull,"41 WBUSH+ANY Bull",...size=size.huge)` — no offset= param in YAML
- Pine plot: L2279: `plotshape(_masterGate and en_wbushBull and sig_WBUSH_Bull,"41 WBUSH+ANY Bull",shape.diamond,location.belowbar,#00BFA5,text="WBUSH",textcolor=color.white,size=size.huge)` — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH — YAML offset field is 0 and Pine has no offset= param; both are offset=0

### squarify::S42_WBUSH_BEAR
- YAML: same pattern as S41, offset=0
- Pine plot: L2280: no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S43_WBUSH_NEUTRAL
- YAML: offset=0, no offset= param expected
- Pine plot: L2281: no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### squarify::S44_NPM_UC_PBJ
- YAML composition: AND — `NPM_CONS_BULL AND UC AND PBJ_BULL[1]`, offset=-1
- Pine source: L2206 (`sig_npm_combo_pbj`); plot L2284: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S45_UC_NAGASAKI_BULL
- YAML composition: AND — `UNIFIED_COMBO_BULL AND NAGASAKI[1]`, offset=-1
- Pine source: L2076 (`sig_UCNagasakiBull`); plot L2287: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::S46_UC_NAGASAKI_BEAR
- YAML composition: AND — `UNIFIED_COMBO_BEAR AND NAGASAKI[1]`, offset=-1
- Pine source: L2077 (`sig_UCNagasakiBear`); plot L2288: `offset=-1` confirmed
- Verdict: ✅ MATCH

### squarify::T1_OPENING_CONFLU
- YAML: ALIAS of TIER1_OPENING_CONFLU_BULL, offset=0
- Pine plot: L2486-L2492 range (YAML says L2472-L2502 for def, L2486 for plot); no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH — note: YAML root entry says `pine_source_line_range: "L2472-L2502"` (definition block) and composite entry says `L2486-L2492` (plot). Minor line-number inconsistency between root and composite entries but not a logic drift.

### squarify::T2_OPENING_CONFLU
- YAML: ALIAS of TIER2_OPENING_CONFLU_BULL, offset=0
- Pine plot: L2514-L2520; no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

1. **S3_HW cross-indicator operand naming** — YAML operands list `squarify::ANY_FLOOR` and `squarify::ANY_2F` as named references, but these are not declared roots in the YAML (they correspond to the Pine variables `floor_sq`/`floor2_sq` which ARE the S4/S5 composites). The YAML should replace `squarify::ANY_FLOOR` with `squarify::S4_FLOOR` and `squarify::ANY_2F` with `squarify::S5_2F` to be consistent with the declared composite IDs. **Recommend: update YAML operand names for S3_HW** — no Pine change needed.

2. **S1_SD_BANG PUP reference** — YAML operand is `squarify::PUP[1]` (citing squarify root). Pine uses `nz(sigPUP[1])` where `sigPUP` is locally defined in squarify (L2006 region). The YAML notes `squarify::B2B_PUP` as a root and separately lists `b2b-pup::PUP` as a cross-indicator dependency. The PUP reference in S1 should be clarified: is it `squarify::B2B_PUP` (the det_b2bPUP helper) or the raw `sigPUP` atomic? Pine uses raw `sigPUP[1]`, not `det_b2bPUP`. **Recommend: update YAML S1 operand** from `squarify::PUP[1]` to `sigPUP[1]` (raw PUP atom, not B2B version). **Anish decision required**: clarify which PUP reference is intended in SD!'s composition.

3. **WBUSH S41-S43 offset field in root vs composite** — The YAML root entry for `WBUSH_BULL` includes a `plot_call` with no `offset=` which is correct (offset=0). However the root entry's `offset: 0` and the composite `S41` entry's `offset: 0` are both consistent with Pine. No actual drift — this is a documentation confirmation that WBUSH is offset=0, which surprised the YAML note (it says "replaces WMD slot"). Flagging for completeness: **no action needed**.
