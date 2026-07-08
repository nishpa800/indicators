# First Bar Fable — Changelog

Newest first. Each version = one file in `versions/`.

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
