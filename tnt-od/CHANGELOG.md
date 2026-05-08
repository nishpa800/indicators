# TNT OD — Changelog

Newest first.

---

## v3 — 2026-05-08 (current)
**File:** `versions/TNT_OD_v3.pine`
**Triggers:** Anish 2026-05-08 ask — gate the 4 NPM-family Tier 1 plots (B2B NAPALM, RC NPM+TNT, CATALYST, PBJ+NPM) and all 12 Tier 2 plots behind a 6-condition OR-gate; add two new combo plots (T1 RELAY = consecutive Tier 1 visual bars; T1 STACK = ≥ 2 Tier 1 visuals on same visual bar); clarify all displacement engines (yes, DYNAMITE has its own dedicated one).

**Changes from v2:**

1. **NEW CONDITIONAL GATE** on the 4 NPM-family Tier 1 plots and all 12 Tier 2 plots. Each plot now ALSO requires ANY of:
   - RVOL 1x (`u5_RVOL1xB` / `u5_RVOL1xR`)
   - Grand Slam (bull) / MOAB (bear)
   - Unified Combo (`uc_bull` / `uc_bear` — placeholder, replaceable)
   - Nagasaki + Any (Nagasaki AND any of P2/P1 tier signals)
   - HCT (inline-ported using HCT's OWN thresholds per Indicator Trust Rules)
   - Displacement ≥ adjustable σ-mult (NEW input `gateStdMult`, default 6.5)
   Master toggle: `en_newGate` default ON. Bear mirrors with bear-side atoms. Offset-aware: offset -1 plots use `gate_bull[1]` / `gate_bear[1]`; offset 0 plots use `gate_bull` / `gate_bear`.

2. **NEW PLOT — T1 RELAY** (bull/bear). Fires when ANY Tier 1 visual landed on bar[2] AND ANY Tier 1 visual on bar[1]. Same direction only (bull-bull or bear-bear). Same Tier 1 type counts (catalyst→catalyst valid). Pool: B2B NAPALM, RC NPM+TNT, FUSE, CATALYST, PBJ+NPM, PBJ+TNT, IGNITE T+C, IGNITE N+C, DYNAMITE, **HCT** (inline), **UC** (inline). Boolean true on bar[0]; plot offset = -1 → visual lands on bar[1] (the second of the two consecutive bars).

3. **NEW PLOT — T1 STACK** (bull/bear). Fires when ≥ 2 distinct Tier 1 visual plots landed on the SAME visual bar. Same Tier 1 pool (10 candidates including HCT and UC). Boolean true on bar[0]; plot offset = -1 → visual lands on bar[1].

4. **DISPLACEMENT ENGINE CLARIFICATION** (no behavior change, only tooltip text). There are now FIVE engines:
   - **Engine #1** — Main TNT OD: `DISP_STD_LEN=100`, `DISP_STD_X=5`. Drives Napalm, Charge, B2B Napalm, Catalyst, RC NPM+TNT, sudden-change, CONT, IGNITE NPM+CONT.
   - **Engine #2** — DYNAMITE (dedicated): `dynStdMult=5.0`, hard-coded 100-bar stdev. Used by DYNAMITE plot ONLY. Yes, DYNAMITE has its own.
   - **Engine #3** — USE V5 enrichment: `u5_std_len=100`, `u5_std_min=3.0`. Drives `u5_DISPBull/Bear` → Tier 2 enrichment gate, WBUSH direction.
   - **Engine #4** — HCT (NEW v3): `hct_disp_strength=6.0`, `hct_disp_lookback=100`, `hct_threshPct=2.0`, `hct_auto=true`. Drives `hct_dispBull/Bear` → `hct_bull/bear` for new gate.
   - **Engine #5** — Gate (NEW v3): `gateStdMult=6.5`. Reuses `DISP_STD_LEN` for lookback. Drives `gate_disp_bull/bear` for new gate ONLY.

5. **Inline-ported HCT engine** — uses HCT's own threshold curves (different from TNT OD's u5_* at 60s–600s timeframes) per Indicator Trust Rules. Produces `hct_bull` / `hct_bear` / `hct_neutral`. Neutral computed but NOT plotted in TNT OD.

6. **Inline-ported UC engine (placeholder)** — Unified Combo defined as ≥ 2 distinct streams from {FAUNA, RVOL tier, WMD, PUP/PPD, CS1}. Clearly marked in code as replaceable; paste real Squarify v2 UC engine in if desired.

**Plotshape count:** 49 / 64 (was 45, +4 for T1 RELAY × 2 + T1 STACK × 2).

---

## v2 — 2026-05-04
**File:** `versions/TNT_OD_v2.pine` (1802 lines)
**Triggers:** Verification Protocol v3.2 audit findings + WBUSH integration ask.

**Changes from v1:**

1. **DYNAMITE — FVG check now MANDATORY.** v1 was a stdev-range filter calling itself "displacement" without FVG. Verification Protocol Rule 1 violation: *"FVG is NEVER optional. If there is no FVG requirement, it is NOT displacement."* Restructured per Example 10 (D2+ pattern):
   - bar[1] AND bar[2] both exceed range threshold (consecutive displaced candles)
   - Both same color (matched direction)
   - FAUNA on bar[1] AND bar[2] (Rule 4: per-candle qualifiers on displacement candles, NOT confirmation bar)
   - bar[0] confirms FVG (`low > high[2]` bull / `high < low[2]` bear)
   - Boolean true on bar[0]; visual moves to bar[1] (offset = -1).
   - Cascading: enrichBull_N removed DYNAMITE (no longer visual bar 0); tntAnyBull/Bear references shifted by 1; alert uses `alertOK_N1` / `firstStatus_N1`.

2. **UU / UUU / UUUU — added new qualification path "pG".** Counts distinct qualifier types from {PBJ, DISP, FAUNA, SAAB, RVOL1x, GrandSlam} present anywhere in the streak. Requires k ≥ streak-size:
   - UU: ≥ 2 distinct
   - UUU: ≥ 3 distinct
   - UUUU: ≥ 4 distinct
   Qualifiers can stack on the same bar (no per-bar requirement). ORs into existing pA/pB/pC/pE/pF — additive, does not remove existing paths. (HV+D path pD intentionally skipped: TNT OD has no HV+D engine; per Anish's direction, not adding the engine here.)

3. **Density 1/2/3 — plotshape offset 0 → -1.** Chain touches Napalm which has displacement+FVG. Per Verification Protocol Rule 2 strict reading, offset must be -1. Alerts also moved to alertOK_N1 / firstStatus_N1.

4. **UU/UUU/UUUU + TNT ANY — plotshape offset 0 → -1.** Same Rule 2 reason. Alerts moved to N1.

5. **WBUSH detections added.** Ports HEAVY PENTAGON's 5 Heavy Combo classifications using TNT OD's existing USE V5 pipeline outputs:
   - Heavy Yin-Yang (P1 + P2)
   - Heavy Nagasaki (P3 + P1)
   - Heavy Nagasaki Vol (P3 + P2)
   - Heavy Trident (P1 + P2 + P3)
   - Neutral Heavy x2 (P2 × 2)
   Each with bull/bear/neutral via u5_DISPBull/Bear classification. WBUSH = any of the 15 fired.
   Three new plots:
   - **WBUSH+TNTOD ANY Bull** — WBUSH-bull state AND any TNTOD bullish detection plot fired
   - **WBUSH+TNTOD ANY Bear** — WBUSH-bear state AND any TNTOD bearish detection plot fired
   - **WBUSH Neutral** — WBUSH-neutral state, standalone alert (significant volume event)

6. **NAGASAKI alert — now checkbox-gated, default OFF.** Was always-on; floods alerts. New "★ NAGASAKI ALERT ★" UI group at bottom. When OFF, no Nagasaki alert fires.

7. **Max TNT 1.0 Zones default 15 → 30.** Max TNT 2.0 Zones 8 → 30. Matches B2B PUP scan-depth preference.

8. **Tooltips added** to every Tier 1, Tier 2, Density, UU, WBUSH input.bool() and the new Max Zones inputs. Hover in TradingView settings now explains each detection.

**Plotshape count:** 45 / 64 (was 42, +3 WBUSH).

---

## v1 — 2026-05-04 (superseded same session by v2)
**File:** `versions/TNT_OD_v1.pine`
**Source:** Pasted by Anish in chat 2026-05-04 as the canonical reference for Napalm / TNT / CONT definitions. Also used as the audit baseline that produced B2B PUP v4.30/v4.31/v4.32.

---

## How to read this changelog
- **Plain English recall:** "Did TNT OD have CATALYST in v1?" → check this file and the v1 README.
- **Cross-check:** when auditing a downstream indicator (e.g., B2B PUP) for Napalm/TNT/CONT correctness, diff against the latest TNT OD version here.
