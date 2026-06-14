# Fair Value Gap (Anish) — Changelog

Newest first.

---

## v1 tick-friendly / non-repainting — 2026-06-14
**File:** `tick_friendly/FAIR_VALUE_GAP_v1_tick_friendly.pine`
**Source of truth:** `versions/FAIR_VALUE_GAP_v1.pine` (the V1, 2022.4.12 original, ingested verbatim).
**Trigger:** Anish ask — "tick-friendly version of this motherfucker. it's gotta be non-repainting. Mandatory."

Pine v5. Geometry, inputs, colours, labels and the fill/shrink math are **identical
to v1 on every closed bar**. Exactly two classes of change:

### (A) Non-repainting (the mandatory part)
v1 created, mutated and deleted its drawing objects on **every intrabar tick**.
Because `bullishgapholder` / `bearishgapholder` / the mid + label arrays are `var`,
intrabar pushes/removes are **not** rolled back by Pine on the forming bar — so v1:
1. **Current-TF FVG** — `f_gapLogic(close[1],high,high[2],low,low[2],open[1],…)` ran
   every tick off the live `high`/`low`; a gap could be drawn off a transient wick
   and then orphaned in the array when the wick retraced.
2. **HTF FVG** — fired on the **first (intrabar) tick** of a new HTF period via
   `is_newbar()`.
3. **Fill/shrink/delete** — `f_gapCheck(high,low)` deleted or shrank boxes off the
   live `high`/`low`, so an intrabar poke into a gap stayed committed even if price
   retraced (destructive repaint).

**Fix:** one gate — `conf = barstate.isconfirmed` — wraps all three commit points
(both `f_gapLogic` calls + `f_gapCheck`). On a closed bar `high`/`low` are final, so
the committed objects are exactly what v1 produced historically. History is
unchanged; the live bar simply waits for its close before committing.
**Intended trade-off:** a fill is now committed at bar **close**, not mid-bar (on
tick bars that lag is one short tick-bar).

`request.security(… , barmerge.lookahead_on)` with `[1]`/`[2]` offsets is the
**canonical non-repaint idiom** (returns the last *confirmed* HTF value, identical
on history and realtime) and is kept verbatim. It is **not** future-leaking — do
NOT "fix" it by removing `lookahead_on`; that would reintroduce repainting.

### (B) Tick-friendly
This script uses **no** `relativeVolume()` / `timeframe.change()`, so it cannot
throw RE10023. The one tick hazard is the MTF anchor `i_tf` reaching
`request.security()` / `time()`: a tick (`"…T"`) or blank anchor makes the HTF
requests meaningless. New `i_tfSafe` coerces an empty/tick anchor to `"D"`:

```pine
i_tfSafe = (i_tf == "" or str.endswith(i_tf, "T") or na(timeframe.in_seconds(i_tf)) or timeframe.in_seconds(i_tf) <= 0) ? "D" : i_tf
```

`str.endswith(i_tf,"T")` is the **authoritative** tick detector — per the repo's
RE10023 postmortem `timeframe.in_seconds("1000T")` is **positive**, so the `na/<=0`
terms are only a blank/edge fallback, never the tick test. A normal time anchor
(default `"D"`) passes through untouched → **exact time-chart parity** with v1.
`i_tfSafe` is used in all five `request.security` calls, both `is_newbar()` calls,
and the FVG label text.

### Verification
- **Static gates (passed):** no literal-blank/tick anchor at any `request.security`
  call site; no `relativeVolume`/`timeframe.change`; `i_tfSafe` keys off
  `str.endswith(i_tf,"T")`; spaces-only indentation.
- **Repaint proof (simulation of Pine's realtime `var`-array semantics):** on a
  forming bar whose `high` transiently dips below `low[2]` then closes above it,
  v1 leaves **2 orphan boxes**; the conf-gated build leaves **0** (the correct
  closed-bar truth). On a genuine closed-bar gap both produce the **identical** box.
- **Not** live-compiled on TradingView from this environment (no Pine compiler / TV
  MCP here). The change is the same bug-class + same remedy already shipped in
  `heavy-weapons-nra/tick_friendly/HEAVY_WEAPONS_NRA_v1_tick_friendly.pine`
  ("All array mutations … gated by `barstate.isconfirmed` → prevents intrabar state
  corruption"). Recommend a smoke-load on a tick chart (e.g. 1000T) before trusting
  live alerts.

---

## v1 (original) — 2022.4.12
**File:** `versions/FAIR_VALUE_GAP_v1.pine`
**Source:** Pasted by Anish as the canonical reference. Displays the fair value gap
of the current timeframe plus an optional higher timeframe; gaps are drawn as boxes
that shrink as they fill and are removed (or frozen) when fully filled. Ingested
verbatim per the suite "never label canonical prematurely / ingest all variants"
rule (only obvious paste artifacts that block compilation were normalised).
