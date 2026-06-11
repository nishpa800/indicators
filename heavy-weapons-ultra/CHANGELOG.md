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
