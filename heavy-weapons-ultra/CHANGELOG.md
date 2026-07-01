# Heavy Weapons ULTRA — CHANGELOG

## Naming ontology + 1:1 parity + master toggles + info buttons (both builds) — adversarially verified
- **1:1 parity**: alert rewritten so each fired detection emits EXACTLY one record whose `det=` name is
  the same string literal as the plot title (and the DB name). 40 visual plots ↔ 40 alert records.
  Schema `det=<Name>|dir=<bull|bear>|off=<0|-1>`. No name drift across plot / alert / database.
- **Master toggle on every detection plot**: added `show_HVDstd`, `show_HVDPBJstd`, `show_NagStd`,
  `show_PPD`; each gates its plot AND its alert record identically (parity preserved).
- **Info buttons**: human-readable required-gate `tooltip=` on every detection toggle.
- **PPD** 52-week band made a clean structural mirror of PUP.
- **Adversarial audit**: both builds pass with ZERO DEFECTS (compile, parity, naming, offsets,
  non-repainting, rolling windows, tick-safety on the tick build).

## Bull/Bear split — NO mixed, NO neutral detection plots (both builds)
- Split the 5 direction-mixed composite plots into separate bull/bear markers:
  `PBJ+Any`, `B2B PBJ+Any`, `HVD+PBJ+Any`, `HV+D+Any`, `Nag+Strong` → each now Bull (green, below)
  and Bear (red, above). Fixes the green-arrow-on-bear bug on `HV+D+Any`.
- Formerly-neutral plots (`Nagasaki`, `HV 75/150/250/500/1000`) are no longer neutral: they inherit
  direction from the **directional anchors on the same candle** (`barDirBull`), tiebreak by candle color.
- Added **directional anchors**: directional RVOL (SAAB/Bull1x/GrandSlam vs Kratos/Bear1x/MOAB),
  Long/Short, PBJ bull/bear, displacement bull/bear, FAUNA bull/bear, PUP, PPD, CS.
- Added **PPD (Pocket Pivot Down)** — bearish structural mirror of PUP (new bear anchor + plot + DB atom U2).
- 40 plots per build (≤ 64). Alert DB unchanged in structure (atoms already carry explicit `dir`).

## Variants tracked (time vs tick) — kept separate, not merged
- **Added the TICK build to the repo:** `tick_friendly/HEAVY_WEAPONS_ULTRA_tickfriendly_b2b1.pine`
  (`shorttitle="HW ULTRA b2b1"`), verbatim — no logic changes. Previously it lived nowhere
  version-controlled.
- **Added `VARIANTS.md`** documenting the two intentionally-separate builds and their 4 material
  differences: (1) tick-safety guard, (2) hybrid Long/Short floors (Hiroshima-derived vs hard-coded
  5.0/3.0/0.65), (3) alert layer (queryable per-atom vs OR-collapsed tier), (4) FAUNA emitted vs not.
- All other atomic gate formulas are identical between the two (see `GATES_REFERENCE.md`).
- Per user decision: **keep both separate**; no merge performed.

## v1 — Queryable alert layer (atomic deconstruction)
- **Replaced the OR-collapsed tier-based alert with a queryable per-atom emitter.** The single
  `alert()` per closed bar now carries a bar header plus **one self-describing record per fired atom**
  (66 atoms across engines R/T/N/M/Q/B/D/V/P/H/K/G/C/U/F):
  `atom=<ID>|name=<NAME>|eng=<ENGINE>|dir=<bull|bear|neutral>|val=<metric>`.
  Output is now a database feed — every detection is individually queryable with an explicit direction;
  composites are reconstructed downstream by joining records on the shared `t`.
- **FAUNA (F1–F14) surfaced** — previously computed internally but never emitted; now queryable.
- Emitted regardless of `show_*` visual toggles, so the DB always has the data.
- Plots unchanged in this pass (visual dir-split for `HV+D+Any`/`HVD+PBJ+Any` is the next phase).
- New docs: `ATOM_REGISTRY.md` (the wire/DB contract), `GATES_REFERENCE.md`, `DETECTION_PLOT_INVENTORY.md`.

## v1
- Initial repo copy of **Heavy Weapons ULTRA** (`shorttitle="HW ULTRA"`) composite architecture.
- **Added `B2B PBJ + Any`** — the back-to-back form of the existing `PBJ + Any` detection.
  Fires only when `PBJ + Any` prints on **two consecutive confirmed bars**, mirroring how
  `2x SAAB` / `B2B Mid Bull` are the consecutive-bar forms of their singles.
  - New toggle: `B2B PBJ + Any (2 bars)` in **★ GLOBAL TOGGLES — COMPOSITES ★** (default ON).
  - New plot: orange `B2B\nPBJ+` diamond below the bar (stacks under the yellow `PBJ+`).
  - New alert tier: emitted in TIER 1; when it fires it subsumes the single `PBJ+Any` line
    (`B2B PBJ+ANY | now: … | prev: …`).
  - Purely additive + independently toggleable — existing `PBJ+Any` behavior is unchanged.
- **Long/Short 1–5 floors now AUTO-DERIVE from the Hiroshima threshold** (matches **HW Single v3**).
  Replaces the hard-coded per-tier inputs (`5.0` Reg / `3.0` Cum / `0.65` Body) with v3's ladder:
  - Reg: `M1 = th_hiroshima × 2.85`, `M5 = th_hiroshima × 1.1875`, M2–M4 linearly interpolated.
  - Cum: `(1.398 × 1.33) × √(ln(RegN))` per tier.
  - Body: `0.69 / 0.72 / 0.75 / 0.78 / 0.81` for M1–M5.
  - New global override inputs `Reg Floor %` / `Cum Floor %` / `Body Ratio %` (default `100`) scale all
    five tiers uniformly — replacing the 15 removed per-tier inputs.
  - **Behavioral note:** Reg floors are now much higher (e.g. ~100 on a 1-min chart vs the old 5.0),
    so Long/Short 1–5 fire on genuinely Hiroshima-grade momentum. Dial down via `Reg Floor %` if needed.
