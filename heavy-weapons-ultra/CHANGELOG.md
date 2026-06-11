# Heavy Weapons ULTRA — CHANGELOG

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
