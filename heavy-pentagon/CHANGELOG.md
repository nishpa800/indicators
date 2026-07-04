# Heavy PENTAGON — CHANGELOG

## v1 — 2026-07-04 (canonical home created)
- First standalone home for the **Heavy PENTAGON** study (shorttitle "heavy pentagon").
- Source intake: full Pine v5 pasted from chat, adopted verbatim as
  `versions/HEAVY_PENTAGON_v1.pine`.
- Until now Heavy PENTAGON existed only embedded inside TNT OD v3's **WBUSH**
  block (`tnt-od/tick_friendly/TNT_OD_v3_tick_friendly.pine` — "WBUSH = HEAVY
  PENTAGON × TNTOD ANY"), which ports its Stage-5 combo classifications. This
  is the first time the standalone study has its own directory.
- Registry: 10 standalone detections (SAAB, Kratos, Bull/Bear RVOL 1x, Grand
  Slam, MOAB, Pentagon, WTC, Hiroshima, Nagasaki) + 15 Heavy Combo detections
  (Heavy Yin-Yang / Heavy Nagasaki / Heavy Nagasaki Vol / Heavy Trident /
  Neutral Heavy x2 — each Bull/Bear/Neutral) across three sealed RVOL pipelines
  + a displacement direction engine.

## v1 tick-friendly — RE10023 anchor + tfSec guard — 2026-07-04
- `tick_friendly/HEAVY_PENTAGON_v1_tick_friendly.pine`.
- Logic, plots, and alerts are byte-identical to v1 on time charts (parity).
  The diff against `versions/HEAVY_PENTAGON_v1.pine` is exactly two functional
  spots plus additive comments/one input — all 25 detections, every plotshape,
  and every alertcondition are unchanged.
- **FIX 1 — RE10023 (relativeVolume anchor).** `tv_ta.relativeVolume()`
  (`import TradingView/ta/7`) calls `timeframe.change(anchor)` internally, which
  throws *"Cannot call timeframe.change with a tick-based timeframe"* on bar 0
  when the anchor is tick-based. The Reg@Time anchor input defaults to
  `input.timeframe("")`, which resolves to the CHART timeframe — tick-based on a
  tick chart (e.g. 1000T). `reg_anchorSafe` coerces the anchor to `"D"` ONLY when
  the resolved anchor is blank-on-a-tick-chart or itself carries a `"T"` suffix;
  time charts pass their real anchor through unchanged. The single
  `relativeVolume` call site uses `reg_anchorSafe`, never the raw blank input.
- **FIX 2 — tfSec fallback.** `tfSec = timeframe.in_seconds(timeframe.period)`
  feeds both per-TF RVOL threshold tables (`f_rvol_1x_threshold`,
  `f_gs_moab_threshold`). On tick intervals `in_seconds` is na/0 (or a mis-scaled
  positive), which would kill or mis-bucket every RVOL / Reg@Time threshold.
  Guarded via `isTickChart` (authoritative detector = `str.endswith(timeframe.period, "T")`,
  since `in_seconds("1000T")` returns a positive number): on tick charts `tfSec`
  falls back to the tightest sub-minute bucket (10s → 38 / 114). A new
  `★ TICK-FRIENDLY ★` input, *"Tick threshold-bucket seconds (0=auto)"*, lets you
  pin a specific bucket (e.g. 10 / 30 / 60) when >0. The input is inert on time
  charts.
- GATES: `grep -nE 'relativeVolume\([^,]+,\s*""' <file>` returns nothing; the
  `reg_anchorSafe` definition keys off `timeframe.period`; `check_no_fixed_windows.sh`
  passes (Nagasaki uses a `var` running-max, not an anchored start-bar window).
- Idiom matches the shipped siblings `heavy-weapons-nra/tick_friendly/` (identical
  RVOL threshold tables + Pipeline 1/2/3) and `squarify/tick_friendly/SQUARIFY_46_v3.1`
  (hardened `isTickChart`).
