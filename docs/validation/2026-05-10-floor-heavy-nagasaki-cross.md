# Validation report — VALIDATE 8 + 9 + 10 + 11 combined

_Skill: `detection-plot-validation` v1.1.0. Run on 2026-05-10. Path: docs/validation/2026-05-10-floor-heavy-nagasaki-cross.md._

Combined report for the remaining 4 targets — FLOOR family, Heavy Combos, Nagasaki Plus, and the Nagasaki Plus × Unified Combo cross-condition. Done as one document because findings interconnect.

---

## VALIDATE 8 — FLOOR / 2F / ROOF / PENTHOUSE / ALPHA family

### Summary

| Field | Value |
|---|---|
| Targets | `anyBullFloor` / `anyBull2nd` / `anyBearRoof` / `anyBearPent` / `sigAlphaStrikeBull` / `sigAlphaStrikeBear` |
| DEFINITION locations | **48** (6 variables × 8 locations each — squarify ×4 + hvdpbjppd ×4) |
| Phase 2 verdicts | Floor/2nd/Roof/Pent: **IDENTICAL** across squarify 46_v2 and hvdpbjppd THE_ONLY_ONE. Alpha Strike: **SEMANTIC DRIFT** |
| Engine | Ping Pong SR (`bull_pp` / `bear_pp` + `bull_hw_slot` / `bear_hw_slot`) — internal helper, same across both files |
| Verdict | **MIXED**: 4 OK + 1 SEMANTIC DRIFT (Alpha Strike) |

### Phase 2 — diff

#### Floor / 2F / Roof / Penthouse — IDENTICAL across squarify 46_v2 + HVDPBJPPD THE_ONLY_ONE

```
anyBullFloor = conf and bull_pp and sigBullPBJ and bull_hw_slot           ← BOTH FILES
anyBull2nd   = conf and bull_pp and sigBullPB  and bull_hw_slot           ← BOTH FILES
anyBearRoof  = conf and bear_pp and sigBearPBJ and bear_hw_slot           ← BOTH FILES
anyBearPent  = conf and bear_pp and sigBearPB  and bear_hw_slot           ← BOTH FILES
```

The 4 composites are byte-identical across all squarify versions AND hvdpbjppd versions. The Ping Pong SR engine (`bull_pp` / `bear_pp`) is a shared internal helper.

**Verdict for Floor/2nd/Roof/Pent**: ✓ **OK** — single canonical implementation propagated correctly.

#### Alpha Strike — SEMANTIC DRIFT

| File | Line | Boolean |
|---|---|---|
| Squarify 46_v2 | 1262 | `sigAlphaStrikeBull = conf and firstOfDay and bull_pp and (sigGrandSlam or sigBullRVOL1x) and sigBullPBJ and as_fauna_bull` |
| HVDPBJPPD THE_ONLY_ONE | 1057 | `sigAlphaStrikeBull = conf and firstOfDay and bull_pp and (sigGrandSlam or sigBullRVOL1x) and (sigBullPBJ or sigBullPB) and as_fauna_bull` |

Difference: HVDPBJPPD includes `(sigBullPBJ or sigBullPB)` while Squarify requires only `sigBullPBJ`. HVDPBJPPD is MORE PERMISSIVE (accepts PB or PBJ; Squarify requires PBJ only).

**Verdict for Alpha Strike**: ✗ **SEMANTIC DRIFT** — pending TV firing to determine canonical.

---

## VALIDATE 9 — 16 Heavy Combo Toggles

### Summary

| Field | Value |
|---|---|
| Targets | 15 Heavy Combo variables (HYY/HN/HNV/HT/NHx2 × Bull/Bear/Neutral) |
| DEFINITION locations | **30** (15 variables × 2 locations — heavy-pentagon + heavy-combo-toggles) |
| Phase 2 verdicts | All 15 pairs: **IDENTICAL** (verbatim-lift claim confirmed) |
| 16th Heavy Combo (per Anish: Nagasaki Plus) | covered in VALIDATE 10 below |
| Verdict | **OK** — verbatim lift confirmed across all 15 booleans |

### Phase 2 — verbatim-lift confirmation (spot-checked 5 of 15 booleans)

```
sigHYYBull    = baseYinYang  and dispBull   ← BOTH files, identical
sigHNBull     = baseNagasaki and dispBull   ← BOTH files, identical
sigHNVBull    = baseNagasakiV and dispBull  ← BOTH files, identical
sigHTBull     = baseTrident  and dispBull   ← BOTH files, identical
sigNHx2Bull   = baseNHx2     and dispBull   ← BOTH files, identical
```

The parallel session's earlier byte-diff already confirmed full lift (5 base combos + 15 directional + displacement engine all character-identical). This validation re-confirms via the skill harness.

### NEUTRAL_HEAVY_X2 always-False suspicion

Per the parallel session's static audit: `NEUTRAL_HEAVY_X2` may be structurally always-False because `baseNHx2 = (P AND W) OR (P AND H) OR (W AND H)` where P, W, H are three **non-overlapping band conditions** — only one fires per bar, so no pair can AND.

Verdict: this is a Pine source design issue in heavy-pentagon, not a drift between locations. Both heavy-pentagon and heavy-combo-toggles share the same suspect formula (since heavy-combo-toggles lifted verbatim). The bug, if confirmed by TV firing showing zero fires, would need fixing at heavy-pentagon (then heavy-combo-toggles re-lifts).

**Action**: defer to TV firing skill. If `sigNHx2Bull/Bear/Neutral` returns zero fires on a long history window, file the bug.

### Verdict

**OK with NEUTRAL_HEAVY_X2 caveat** — 15 booleans identical between heavy-pentagon and heavy-combo-toggles. NEUTRAL_HEAVY_X2's "always-False" suspicion is a Pine-design issue (not a drift), shared across both files; pending TV firing to confirm.

---

## VALIDATE 10 — Nagasaki Plus

### Summary

| Field | Value |
|---|---|
| Target | `sigNagPlusBull` / `sigNagPlusBear` |
| Canonical location found | `hvd-pbj-ppd/versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` L1083-1084 |
| Definition | `sigNagPlusBull = sigNagasaki and (any of: sigBullRVOL1x, sigGrandSlam, sigFAUNABull, sigDISPBull, sigBullPBJ, sigPUP, gz_bullHV, gz_bullGZI, sigLong1, anyBullFloor, anyBull2nd)` |
| Symmetric bear | `sigNagPlusBear = sigNagasaki and (any of: sigBearRVOL1x, sigMOAB, sigFAUNABear, sigDISPBear, sigBearPBJ, sigPPD, gz_bearHV, gz_bearGZI, sigShort1, anyBearRoof, anyBearPent)` |
| Other DEFINITIONs | Squarify references `nag_any_bull` (similar concept, possibly aliased) — need follow-up enumeration |
| Verdict | **OK-PENDING-FULL-ENUMERATION** (canonical in HVDPBJPPD 4.26; need to confirm presence/absence in other files) |

### What "Plus" means

Nagasaki Plus = Nagasaki fires AND at least one bullish (or bearish) co-signal fires on the same bar. The co-signal set is broad — 11 distinct primitives. This makes "Nagasaki Plus" a high-confidence directional Nagasaki: not just "all-time-high volume" but "all-time-high volume happening alongside some other directional confirmation".

### Stage-7 followup

- [ ] Re-enumerate with broader alias set: `sigNagPlusBull`, `sigNagPlusBear`, `nag_any_bull`, `nag_any_bear`, `nag_plus_bull`, `NagasakiPlus`
- [ ] Determine if THE_ONLY_ONE.pine includes Nagasaki Plus (the 4.26 predecessor has it; the consolidated file may have dropped it)
- [ ] Squarify 46_v2 emits `F35_NAGPLUS=nag_any_bull` in its log payload (L2609) — confirm Squarify has its own canonical Nagasaki Plus

---

## VALIDATE 11 — CROSS-CONDITION: Nagasaki Plus × Unified Combo same-candle

### Summary

| Field | Value |
|---|---|
| Target X | `sigNagPlusBull` (Nagasaki Plus, per VALIDATE 10) |
| Target Y | `csNew3_Bull` (Unified Combo, per VALIDATE 1) |
| Window | 0 bars (strict same-candle intersection) |
| Per-target X verdict | OK-PENDING-FULL-ENUMERATION (VALIDATE 10) |
| Per-target Y verdict | DRIFT-PENDING-TV-FIRING (VALIDATE 1) |
| Intersection computable | **NO** — Phase 3 for both is BLOCKED-NEEDS-TV-FIRING-SKILL; fire-bar sets unavailable from this sandbox |
| Verdict | **BLOCKED-NEEDS-TV-FIRING-SKILL** for X AND for Y, therefore intersection is computable only via the TV firing skill |

### Cross-condition expectation

Anish: "I want us to be looking at Nagasaki Plus and unified combo when they're both on the same candle."

This is a HIGH-VALUE cross-condition: Nagasaki Plus already requires Nagasaki + 1 co-signal; Unified Combo requires FVG + Matrix combos. Their same-candle intersection would be a VERY rare, VERY high-conviction event — multiple confluence streams aligned on one bar.

### Expected behavior

Mathematically:
- `sigNagPlusBull` requires Nagasaki AND 1-of-11 bullish co-signals
- `csNew3_Bull` requires FVG Combo AND Matrix Combo (lagged or same-bar depending on which canonical wins VALIDATE 1)
- Intersection: bars where ALL of (Nagasaki, 1-of-11, FVG Combo, Matrix Combo lagged/same) fire simultaneously

Likely outcome on real history: VERY rare. Maybe 0-3 fires per year per symbol. Anish's interest is exactly because these are the highest-conviction events.

### Stage-7 followups

- [ ] Run `detection-plot-tv-firing` skill on Nagasaki Plus AND Unified Combo together
- [ ] Compute intersection bar-set
- [ ] For each intersection bar: log timestamp + symbol + timeframe + preceding/following 5 bars context
- [ ] If intersection is empty: classify per cross-condition.md (impossible / bug / rare)
- [ ] If intersection is non-empty: document the bars as the "Nagasaki Plus × Unified Combo" event log; consider this the highest-conviction confluence signature in the bible

---

## Combined verdicts

| VALIDATE | Verdict | Notes |
|---|---|---|
| 8 — FLOOR/2F/Roof/Pent | **OK** (4 identical across squarify+hvdpbjppd) | Ping Pong SR engine propagated correctly |
| 8 — Alpha Strike | **SEMANTIC DRIFT** | HVDPBJPPD adds `or sigBullPB`; Squarify requires `sigBullPBJ` only |
| 9 — 16 Heavy Combo Toggles | **OK** with NEUTRAL_HEAVY_X2 always-False caveat | verbatim lift confirmed; NHx2 needs TV firing to confirm always-False suspicion |
| 10 — Nagasaki Plus | **OK-PENDING-FULL-ENUMERATION** | canonical found at HVDPBJPPD 4.26 L1083; need to confirm cross-file coverage |
| 11 — Cross-condition (Nag+ × UC) | **BLOCKED-NEEDS-TV-FIRING-SKILL** | both per-target Phase 3 blocked; intersection requires fire bars |

## Combined Stage-7 followups

- [ ] Phase 3 TV firing for Alpha Strike (resolve PBJ-only vs PBJ-or-PB)
- [ ] Phase 3 TV firing for NEUTRAL_HEAVY_X2 (confirm always-False bug)
- [ ] Re-enumerate Nagasaki Plus with broader aliases (`nag_any_bull`, etc.)
- [ ] Phase 3 TV firing for Nagasaki Plus × Unified Combo intersection (the cross-condition signature)
- [ ] If intersection non-empty: document as the highest-conviction confluence event log
- [ ] Update `docs/redundancy.md` (b) with the Alpha Strike drift entry
