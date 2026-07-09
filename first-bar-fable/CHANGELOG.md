# First Bar Fable — Changelog

Newest first. Each version = one file in `versions/`.

---

## v2 — 2026-07-09
**File:** `versions/FIRST_BAR_FABLE_v2.pine` — chart title **"First Bar Fable v2"**,
shorttitle **"1st BAR FABLE v2"** (v1 kept as `versions/FIRST_BAR_FABLE_v1.pine`,
title "First Bar Fable v1", so there's no version confusion on the chart).

Added detections requested by Anish. Every new displacement engine is adjustable
and grouped; the file header carries a DISPLACEMENT MAP stating which engine
drives which plots.

**New detection plots:**
| Plot | Logic | Source |
|---|---|---|
| S18 / S19 | B2B PUP / B2B PPD **+ Disp9** on one of the two pattern bars | B2B PUP v5.4 + Disp9 |
| S20 / S21 | **B2B FC Cluster** Bull/Bear (FC cluster on two consecutive bars) — **ALWAYS fires on any bar; OVERRIDES the First Bar Master** even when first-bar mode is ON (loud tooltip + no first-bar gate) | Ultra v57 FC cluster |
| S22 / S23 | **D9 Bull/Bear Study**: disp ≥ 9σ AND (RVOL 1x OR GS/MOAB) AND (HV500 OR HV1000 OR Nagasaki), all same confirmed bar; HV500/HV1000 are raw current-bar rolling highest-volume checks | HW v3 spec |
| S24 / S25 | **Unified Combo** Bull/Bear **+ Disp9** (csNew3 AND displacement-9) | HVD PBJ PPD |
| HVD Pipeline D | CO HV+D+PBJ / HV+D+PB co-occurrence (bull+bear) | HVD PBJ PPD |
| HVD Back-to-Back | B2B HV+D / +PBJ / +PB (bull+bear) | HVD PBJ PPD |
| HVD Momentum | HV+D+PUP/PPD, +RVOL, +CMB, +PBJ variants, 2of3, 3of3 (bull+bear) | HVD PBJ PPD |

53 plotshapes total (under Pine's 64-output cap). Each checkbox gates both plot
and alert (static alertcondition for S1–S25 + grouped HVD alertconditions +
dynamic alert() aggregator for every fired detection).

**No-fixed-windows compliance (Anish's hard rule):**
- HVD **Group 1 (CO)**: the source's `use_any_*` gate pulled in FIXED-session-window
  signals (Opening Drive `sessionBarCount`, Alpha Strike `firstOfDay`, U-streak
  day flags). Those are **dropped**; `use_any_*` is rebuilt from First Bar Fable's
  own ROLLING detections. Deliberate rolling-only deviation. (A few disjuncts —
  e.g. Typhoon — internally reference a session *anchor* `is_new_sess`, not a
  fixed bar-count window; on non-first bars they are simply always-false, and the
  CO plots are fb1-gated regardless, so the rolling-only intent holds.)
- **B2B FC Cluster**: uses `sBullFC and sBullFC[1]` (two consecutive bars), NOT the
  source's `f_hadSignalYesterday` (`barsPerDay*2` fixed-window scan).
- Every other new lookback is rolling (`ta.highest/lowest/sma/stdev/atr`) or
  expanding running-state (HEV/Nagasaki all-time max, cumulative FVG threshold),
  never a fixed intraday bar-count window.

**Ports & parity notes:**
- HV+D displacement engine (σ=5, len=100 adjustable) drives every HVD plot.
- PBJ engine extended with the **PB level-approach path** (omitted in v1) — needed
  for the HVD `+PB` plots; PBJ latch output unchanged.
- Unified Combo (`csNew3`) ports the full FVG/matrix/Pentagon/Long-Short chain;
  its GZ FVG uses HVD params (adds 63-day HV tier, dist=12) under an `hgz_` prefix
  so it doesn't share array state with Musashi's GZ engine.
- Matrix Neo/Trinity reuse the u5 FAUNA variant (softened GG exclusion), matching
  HVD's FAUNA; Long/Short ratios reuse the hybrid-momentum relativeVolume ratios.
- FC cluster ported verbatim (`fc_` prefix), preserving its two bull/bear
  asymmetries (`fc_b4_neg` extra bodyDn guard; bear seq threshold 0.5 vs bull 0.1);
  its intrinsic day-reset (ind2) and RTH `inSession` mask (ind3) are kept as part
  of the canonical FC definition, not fixed bar-count windows.
- All HVD plots + Unified Combo render at offset −1 (gated by fb1); B2B PUP/PPD at
  offset 0 (fb01); D9 studies at offset 0 (fb0); B2B FC at offset 0 (no gate).

---

## v1 — 2026-07-08
**File:** `versions/FIRST_BAR_FABLE_v1.pine` — new composite study, named in homage of Fable.

**Master behavior:**
- `★ FIRST BAR MASTER ★` checkbox, **default ON** = every detection requires its
  reference bar (honoring plot offset) to be the first bar of the session
  (`ta.change(time("D")) != 0`, the fauna/squarify anchor). Two-bar B2B patterns
  pass when the pair touches the first bar (B2B PUP `g01` semantics). OFF = any bar.
- One checkbox per detection plot; the checkbox gates **both the plot and the alert**.
- Alerts: static `alertcondition()` per plot + dynamic `alert()` Bloomberg format
  `DIRECTION | FIRST !!!/FIRST XXX/NOT !!! | names`, aggregate or individual.

**Detection plots (all engines VERBATIM ports; sources annotated in file header):**
| Plot | Logic | Source |
|---|---|---|
| S1 | Bull (RVOL 1X or Grand Slam) + Disp9 + PBJ Bull | RVOL: B2B PUP v5.4 Engine E; Disp9: SQUARIFY v3 |
| S2 | Bear (RVOL 1X or MOAB) + Disp9 + PBJ Bear | same |
| S3/S4 | Typhoon Bull/Bear | 1st PUP FAUNA (exact) |
| S5/S6 | Musashi Bull/Bear | 1st PUP FAUNA (exact, raw-FVG/aligned-legs asymmetry preserved) |
| S7/S8 | Whale+PUP / Whale+PPD | 1st PUP FAUNA (exact) |
| S9 | B2B KRATOS (B2B PUP v5.4 S5 bear) + Disp9 on one of the two pattern bars | B2B PUP v5.4 + new constraint |
| S10 | B2B SAAB (B2B PUP v5.4 S5 bull) + Disp9 on one of the two pattern bars | B2B PUP v5.4 + new constraint |
| S11/S12 | Dynamite Bull/Bear | TNT OD v3 (exact, dedicated 100-bar σ engine) |
| S13/S14 | Ignite Bull/Bear (T+C offset 0, N+C offset −1) | TNT OD v3 (exact, full TNT core ported under `tod_` prefix) |
| S15 | Nagasaki + any of (LONG 1-5, PBJ Bull, Disp9, Bull RVOL 1X, Grand Slam) on the first bar | Nagasaki: SQUARIFY v3; LONG 1-5: Heavy Weapons Singles v2 hybrid momentum |
| S16/S17 | B2B Napalm Bull/Bear | B2B PUP v5.4 Engine G (exact, `tnt_` prefix) |

**Interpretations flagged for Anish review:**
1. S9/S10 "one of the first two bars must be displacement 9" read as: Disp9
   (matching direction) on bar[0] or bar[1] — the two bars of the B2B pattern.
2. S15 "on the first bar" is baked into the signal (fires only on session first
   bar even when the master toggle is OFF) — same pattern as fauna's Typhoon.
3. "long (1-5)" = Hybrid Momentum LONG 1–5 tiers from Heavy Weapons Singles v2
   (the only 5-tier long ladder in the suite; Squarify has only Long 1/2).
4. Disp9 bear side is the natural mirror of SQUARIFY's bull-only `d9_bull`
   (multiplier exposed as input, default 9.0).

**Parity notes:**
- Both zone engines ported separately: TNT OD v3 core (for Ignite — VOB `src`
  reads the origin bar, single mixed zone array) and B2B PUP Engine G (for B2B
  Napalm — current-bar `src`, split bull/bear arrays). They are cousins, NOT
  identical; each detection uses its own canonical engine.
- Visual-only members (line/label/box) stripped from ported zone types; state
  logic and intra-bar mutation order preserved exactly.
- `tv_ta.relativeVolume` calls (WTC/Hiroshima + LONG tiers) routed through the
  SQUARIFY v3 `reg_anchorSafe` guard — time-chart parity preserved, no raw `""`
  anchor (RE10023 gate passes). Study is non-tick per spec.
- PBJ engine ports the PBJ latch path only; fauna's PB level-approach machinery
  is independent state with zero effect on PBJ outputs and was omitted.
- TNT OD v3's `super_zones` array has no constructor in the source (dead code);
  kept verbatim for parity.
