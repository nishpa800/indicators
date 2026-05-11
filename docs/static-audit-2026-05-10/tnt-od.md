# Static Audit — tnt-od — 2026-05-10

## Summary
- Composites audited: 20 (B2B_Napalm, RC_NPM_TNT, FUSE, Catalyst, PBJ_NPM, PBJ_TNT, Ignite, TNT_Enriched, NPM_Enriched, CONT_Enriched, RC_TNT_RET_Enriched, RC_RET_NPM_Enriched, PBJ_RET_Enriched, UU_TNT_Any, UUU_TNT_Any, UUUU_TNT_Any, WBUSH_Bull, WBUSH_Bear, WBUSH_Neutral, tntod_any_bull/bear aggregators)
- ✅ matched: 18
- ⚠️ drift: 1 (B2B_Napalm session gating stricter than YAML implies)
- ❓ unclear: 1 (Ignite offset handling — dual-plot design needs documentation)

---

## Per-composite findings

### tnt-od::B2B_Napalm
- YAML composition: AND — `det_bullNapalm AND det_bullNapalm[1] AND NOT supp_bullNPM AND session-bound`, offset=-1
- Pine source: L1030: `bool p_b2bBull = det_bullNapalm and not supp_bullNPM and (det_bullNapalm[1] == true) and not na(sessionFirstBarIdx) and (bar_index - 2) >= sessionFirstBarIdx and en_b2bBull`
- Pine plot: L1412: `plotshape(p_b2bBull,"B2B Napalm Bull",...,offset=-1)` — confirmed offset=-1
- Verdict: ✅ MATCH — YAML notes "session-bound"; Pine implements via `(bar_index - 2) >= sessionFirstBarIdx` which means at least 2 bars must have elapsed since session open. This is stricter than "at least 1 bar" but is the correct implementation. YAML adequately describes this.

### tnt-od::RC_NPM_TNT
- YAML composition: AND — `det_bullNapalm AND det_bullTNT[1]`, offset=-1
- Pine source: L962-L963: `sig_rcNTBull` (defined in block around these lines as `det_bullNapalm and det_bullTNT[1] and en_rcNTBull`)
- Pine plot: L1414: `plotshape(sig_rcNTBull,"RC NPM+TNT Bull",...,offset=-1)` — confirmed offset=-1
- Verdict: ✅ MATCH

### tnt-od::FUSE
- YAML composition: SEQUENCE — last NPM bar < last TNT bar < current bar, all gaps <= SUDDEN_PROX, session-bound, offset=0
- Pine source: L975-L986 (det_fuseBull complex sequence logic); L1035: `bool p_fuseBull = det_fuseBull and en_fuseBull`
- Pine plot: L1417: `plotshape(p_fuseBull,"FUSE Bull",...)`  — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### tnt-od::Catalyst
- YAML composition: AND — `det_bullNapalm AND u5_CS1_Bull`, offset=-1
- Pine source: L994-L998 (det_catBull block); L1036: `bool p_catBull = det_catBull and en_catBull`
- Pine plot: L1420: `plotshape(p_catBull,"CATALYST Bull",...,offset=-1)` — confirmed offset=-1
- Verdict: ✅ MATCH

### tnt-od::PBJ_NPM
- YAML composition: AND — `det_bullNapalm AND u5_PBJBull[1] AND pnGateBull`, offset=-1
- Pine source: L969 (det_pnBull); L1032: `bool p_pnBull = det_pnBull and pnGateBull and en_pnBull`
- Pine plot: L1423: `plotshape(p_pnBull,"PBJ+NPM Bull",...,offset=-1)` — confirmed offset=-1
- Verdict: ✅ MATCH

### tnt-od::PBJ_TNT
- YAML composition: AND — `det_bullTNT AND u5_PBJBull AND ptGateBull`, offset=0
- Pine source: L971 (det_ptBull); L1033: `bool p_ptBull = det_ptBull and ptGateBull and en_ptBull`
- Pine plot: L1426: `plotshape(p_ptBull,"PBJ+TNT Bull",...)` — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### tnt-od::Ignite
- YAML composition: OR — `(det_bullTNT AND det_contBull, offset=0) OR (det_bullNapalm AND det_contBull[1], offset=-1)`, dual plotshape
- Pine source: L988-L992 (ign_tc_bull, ign_nc_bull); L1037: `bool p_ignBull = det_igniteBull and en_ignBull`; L1429-L1432: two plotshapes — one for T+C (no offset, offset=0) and one for N+C (offset=-1)
- Pine plots: L1429 `plotshape(p_ignBull and ign_tc_bull,"IGNITE TNT+CONT Bull",...)` no offset; L1431 `plotshape(p_ignBull and ign_nc_bull,"IGNITE NPM+CONT Bull",...,offset=-1)`
- Verdict: ❓ UNCLEAR — YAML correctly describes both paths and their offsets but uses a single composite entry with `plot: [two entries]`. The Pine correctly implements two separate plotshapes with different offsets. The YAML representation is accurate but the dual-plot architecture deserves a `notes` callout in the bible clarifying these are two distinct visual marks (one at bar[0], one at bar[-1]) from the same boolean `p_ignBull`. No action needed unless the bible format requires a 1:1 plot-to-composite rule.

### tnt-od::TNT_Enriched
- YAML composition: AND — `det_bullTNT AND NOT supp_bullTNT AND enrichBull_N`, offset=0
- Pine source: L1041: `bool p_t2tntBull = det_bullTNT and not supp_bullTNT and enrichBull_N and en_t2tntBull`
- Pine plot: L1438: `plotshape(p_t2tntBull,"TNT Enriched Bull",...)` — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### tnt-od::NPM_Enriched
- YAML composition: AND — `det_bullNapalm AND NOT supp_bullNPM AND enrichBull_N1`, offset=-1
- Pine source: L1043: `bool p_t2npmBull = det_bullNapalm and not supp_bullNPM and enrichBull_N1 and en_t2npmBull`
- Pine plot: L1441: `plotshape(p_t2npmBull,"NPM Enriched Bull",...,offset=-1)` — confirmed offset=-1
- Verdict: ✅ MATCH

### tnt-od::CONT_Enriched
- YAML composition: AND — `det_contBull AND enrichBull_N`, offset=0
- Pine source: L1045: `bool p_t2contBull = det_contBull and enrichBull_N and en_t2contBull`
- Pine plot: L1444: `plotshape(p_t2contBull,"CONT Enriched Bull",...)` — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### tnt-od::RC_TNT_RET_Enriched
- YAML composition: AND — `det_bullTNT AND det_bullRetTNT AND enrichBull_N`, offset=0
- Pine source: L1047: `bool p_t2trBull = det_rcTRBull and enrichBull_N and en_t2trBull` (det_rcTRBull = TNT AND RetTNT, defined near L965)
- Pine plot: L1447: `plotshape(p_t2trBull,"RC TNT+RET Enriched Bull",...)` — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### tnt-od::RC_RET_NPM_Enriched
- YAML composition: AND — `det_bullNapalm AND det_bullRetTNT[1] AND enrichBull_N1`, offset=-1
- Pine source: L1048: `bool p_t2rnBull = det_rcRNBull and enrichBull_N1 and en_t2rnBull` (det_rcRNBull = NPM AND RetTNT[1], defined near L967)
- Pine plot: L1450: `plotshape(p_t2rnBull,"RC RET+NPM Enriched Bull",...,offset=-1)` — confirmed offset=-1
- Verdict: ✅ MATCH

### tnt-od::PBJ_RET_Enriched
- YAML composition: AND — `det_bullRetTNT AND u5_PBJBull AND enrichBull_N`, offset=0
- Pine source: L1049: `bool p_t2prBull = det_prBull and enrichBull_N and en_t2prBull` (det_prBull = RetTNT AND PBJ, defined near L973)
- Pine plot: L1453: `plotshape(p_t2prBull,"PBJ+RET Enriched Bull",...)` — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### tnt-od::UU_TNT_Any
- YAML composition: AND — `u_pathBull2 AND hasTntBull2`, offset=-1
- Pine source: L1354: `bool p_uuBull = u_pathBull2 and hasTntBull2 and en_uu_bull`
- Pine plot: L1465: `plotshape(p_uuBull,"UU+TNT ANY Bull",...,offset=-1)` — confirmed offset=-1
- Verdict: ✅ MATCH

### tnt-od::UUU_TNT_Any
- YAML composition: AND — `u_pathBull3 AND hasTntBull3`, offset=-1
- Pine source: L1356: `bool p_uuuBull = u_pathBull3 and hasTntBull3 and en_uuu_bull`
- Pine plot: L1467: `plotshape(p_uuuBull,"UUU+TNT ANY Bull",...,offset=-1)` — confirmed offset=-1
- Verdict: ✅ MATCH

### tnt-od::UUUU_TNT_Any
- YAML composition: AND — `u_pathBull4 AND hasTntBull4`, offset=-1
- Pine source: L1358: `bool p_uuuuBull = u_pathBull4 and hasTntBull4 and en_uuuu_bull`
- Pine plot: L1469: `plotshape(p_uuuuBull,"UUUU+TNT ANY Bull",...,offset=-1)` — confirmed offset=-1
- Verdict: ✅ MATCH

### tnt-od::WBUSH_Bull
- YAML composition: AND — `sig_WBUSH_Bull AND tntod_any_bull`, offset=0
- Pine source: L1371: `bool p_wbushBull = en_wbushBull and sig_WBUSH_Bull and tntod_any_bull`
- Pine plot: L1473: `plotshape(p_wbushBull,"WBUSH+TNTOD ANY Bull",...)` — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### tnt-od::WBUSH_Bear
- YAML composition: AND — `sig_WBUSH_Bear AND tntod_any_bear`, offset=0
- Pine source: L1372: `bool p_wbushBear = en_wbushBear and sig_WBUSH_Bear and tntod_any_bear`
- Pine plot: L1474: `plotshape(p_wbushBear,"WBUSH+TNTOD ANY Bear",...)` — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### tnt-od::WBUSH_Neutral
- YAML composition: PASSTHROUGH — `sig_WBUSH_Neutral` standalone, no TNTOD pairing required, offset=0
- Pine source: L1373: `bool p_wbushNeutral = en_wbushNeutral and sig_WBUSH_Neutral`
- Pine plot: L1475: `plotshape(p_wbushNeutral,"WBUSH Neutral",...)` — no offset= param (offset=0 confirmed)
- Verdict: ✅ MATCH

### tnt-od::tntod_any_bull / tntod_any_bear (aggregator)
- YAML composition: OR of all 20 plot booleans (p_b2bBull, sig_rcNTBull, p_fuseBull, p_catBull, p_pnBull, p_ptBull, p_ignBull, p_dynBull, p_t2tntBull, p_t2npmBull, p_t2contBull, p_t2trBull, p_t2rnBull, p_t2prBull, p_d1b, p_d2b, p_d3b, p_uuBull, p_uuuBull, p_uuuuBull)
- Pine source: L1368-L1369 exactly match this 20-operand OR list
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

1. **B2B_Napalm session gating detail** — Pine requires `(bar_index - 2) >= sessionFirstBarIdx`, meaning the composite cannot fire on session bar 1 or bar 2. YAML says "session-bound" without specifying the 2-bar minimum. **Recommend: update YAML notes** to document the `bar_index - 2` gate explicitly so audit readers know why B2B_Napalm won't fire on the first two bars of a session.

2. **Ignite dual-plot design** — YAML models Ignite as a single composite with two plot entries. Pine implements two distinct `plotshape()` calls with different offsets (T+C at offset=0, N+C at offset=-1) gated by `p_ignBull and ign_tc_bull` vs `p_ignBull and ign_nc_bull`. This is correctly documented in the YAML `plot_label` section. No change required, but the bible should include a note: "Ignite is the only composite in tnt-od that produces two simultaneously-visible marks on the chart (one at bar[0] for T+C, one at bar[-1] for N+C) when both sub-conditions fire."
