# Glossary

Cross-cutting concepts referenced throughout the indicator bible. Every other doc links here; nothing redefines.

## Bar lifecycle

The strict order in which signals are evaluated for every confirmed bar. See `~/.claude/projects/-Users-anishpatel/memory/feedback_root_vs_composite.md` for the canonical 7-stage definition. Roots belong to stage 2, composites to stage 5.

## `barstate.isconfirmed`

Pine boolean that is true only on bars whose close is confirmed (i.e. not the realtime ticking bar). Used as the universal `conf` gate. Every root and composite in the bible is evaluated only when `barstate.isconfirmed` is true; intrabar movement does not fire signals.

## Decoupling guarantee

Every root is calculated in its own scope, on the same bar's input data, with no awareness that any other root exists. There is no order-of-evaluation dependency between roots. If 45 roots fire on the same bar, they are 45 independent computations. Composites read root booleans only at stage 5 (post-offset, plot-level), never inspect root internals.

## Offset

Pine `plot()` / `plotshape()` parameter that shifts the visual rendering and the time index a boolean is *associated with*, but does NOT cause the calculation to wait or look forward. Offset values used in this suite are 0 (current bar) and -1 (boolean computed on this bar's close is displayed and tallied as if it belongs to the prior bar). An alert on an `offset=-1` plot still fires at the close of the *current* bar — the offset is a labelling choice, not a delay in detection.

## Rolling window

A range of `N` bars ending at the current bar. Used in composites like Density (rolling Y-bar count of qualifying events) and Combo Chain (rolling 4-bar window for ≥2 hits). When a root or composite references a "rolling window", the window is anchored at the *current* confirmed bar and walks back `N-1` bars.

## Back-to-back (B2B)

Two consecutive same-direction same-named events on adjacent bars. Formal: `EVENT[0] AND EVENT[1]`. Used in B2B PUP (`PUP[0] AND PUP[1]`), B2B PPD, B2B HV+D, B2B Napalm, etc. NOT to be confused with "two events within N bars" (which is a rolling window).

## "Any" / streak semantics

`anyB2B` = OR over multiple B2B variants. `uu_any` = `UU OR UUU OR UUUU`. Streak qualifiers (UU=2 consecutive, UUU=3, UUUU=4) require the same directional gate (`bb_baseBullish AND normalizedPrice ≥ threshold`) on every bar in the streak.

## "Callback gate"

A composite-level gating composition that requires at least one of a set of qualifier composites to fire (e.g. `oneOfThese = UUUU OR UUU OR UU OR OmegaA OR Napalm OR B2BNPM OR UC OR CS1or2 OR WMD`). Used in Squarify's S4-S11 to prevent low-quality firings.

## IPSF (Input Structured Field) vs TRUE DRIFT

A first-class distinction when comparing parameter values across indicators that name the same primitive.

- **IPSF** — the parameter is exposed as a Pine `input.*` (`input.int`, `input.float`, `input.bool`, `input.string`, etc.). Anish can change the value at runtime in TradingView's settings dialog. **Different defaults across indicators are NOT corruption** — they're tunable, and reconciliation is a settings-panel operation, not a source-edit operation.
- **TRUE DRIFT** — the parameter is hardcoded as a Pine constant in source code. Invisible to the user. Reconciliation requires source edit + commit + redeploy on TradingView. Hardcoded values that diverge across indicators are real corruption — they cannot be tuned to align without re-editing every consumer.
- **IPSF asymmetry** — the same parameter is exposed as `input.*` in some indicators but hardcoded as a constant in others. The numeric values may currently match, but tuning is asymmetric — changing the input-bound copy is a settings click; changing the hardcoded copy is a source edit. Logged in `docs/redundancy.md` table (b) as a potential source of future drift.

When `docs/validation-log/<date>-drift-byte-diffs.md` reports parameter-default differences, every entry must classify the finding as IPSF / TRUE DRIFT / IPSF asymmetry. False-alarm "drifts" (both copies are IPSF, just different defaults) get explicitly de-escalated so the redundancy table doesn't bloat with non-issues.

## σ-multiplier (sigma-multiplier)

In Displacement-family roots, the threshold is `bar_range > σ × N × stdev(range, lookback)`, where `σ` is the multiplier (typical values 5.0, 6.0, 9.0 across indicators) and `lookback` is typically 100 bars. The σ-multiplier is INTERNAL MECHANICS of Displacement — not a separate root. Drift in σ-multiplier defaults across indicators is tracked in `redundancy.md`.

## ATR multiplier

In PBJ-family roots, the wick-band threshold is `EMA(close, MA_period) ± ATR(ATR_period) × ATR_mult`. Typical values: MA_period=20, ATR_period=14, ATR_mult=3.0. Internal mechanics of PBJ.

## Zoo MA pullback

In PBJ-family roots, a directional pullback gate that requires `low < ZooMA × pullback_pct` (bull) or `high > ZooMA / pullback_pct` (bear), where `ZooMA = VWMA(close, 5)` and `pullback_pct = 0.97`. Internal mechanics of PBJ.

## RVOL tier

A volume-rank classification produced by Heavy Pentagon's three pipelines:
- **P1 Standard RVOL** (Bollinger-band-style normalised price spike): SAAB, Kratos, RVOL 1x, Grand Slam, MOAB.
- **P2 Reg@Time RVOL** (`tv_ta.relativeVolume(30, "", false, true)`): Pentagon, WTC, Hiroshima.
- **P3 All-Time HV**: Nagasaki (HEV).

## FVG (Fair Value Gap)

A 3-bar price gap pattern. Bull FVG: `low[0] > high[2]` with body confirmation on bar 1. Bear FVG: `high[0] < low[2]` with body confirmation. Auto-threshold = cumulative `((high-low)/low) / bar_index`. Manual threshold = `thresholdPer/100`. FVG is a geometric primitive and NOT a root by itself; it is the atomic building block of GZI and HV-FVG roots.

## Displacement zone

A region of price defined by a Displacement event's bar `[1]` extreme + ATR-derived band. Used by Napalm and Charge to detect zone-piercing displacement on subsequent bars.

## HV (High Volume / Highest-Ever Volume)

Multiple meanings depending on context:
- **HV-rank** (HV75, HV150, HV500, HV1000): `volume[1] >= ta.highest(volume, N)` for N=75/150/500/1000.
- **HV milestone** in HV FVG GZ1 OG: `volume[1] equals ta.highest(volume[1], N)` for N=5000/252/63 (formation-bar volume = lookback high).
- **HEV** (Highest-Ever-Volume) in Heavy Pentagon: `volume > maxVol` since `bar_index 0` — i.e. Nagasaki.

## Tier (T1/T2/T3/T4)

Two unrelated meanings:
1. **Bible tier**: depth from root. Tier-0 = root, tier-1 = composite-of-roots, tier-2 = composite-of-tier-1, etc.
2. **Squarify/TNT-OD tier-numbering**: T1 = single-engine fire, T2 = engine + enrichment, T3 = multi-engine + enrichment, T4 = aggregator.

These are independent numbering systems. The bible always uses meaning (1) when "tier" is unqualified.

## Provenance / canonical name

`<provenance>::<name>`. Provenance is the indicator study where the signal is canonically defined. When a signal is re-implemented in another indicator (cross-ref), the canonical name still points to the originating study, not the local copy. Example: B2B PUP locally re-implements PUP as `det_PUP`, but the canonical name stays `b2b-pup::PUP` (or `pocket-pivot::PUP` if a dedicated indicator owns it).

## Drift / redundancy

Two kinds:
- **Composition drift**: same name, different composition across indicators (e.g. `FLOOR` differs between Squarify and HVDPBJPPD).
- **Internal-implementation drift**: same name, same composition, different internal Pine math (e.g. PBJ's Supertrend changed in one indicator but not another). Detected by byte-diffing root function definitions across files.

Both kinds tracked in `docs/redundancy.md`.

## "Verbatim" claim

When a CHANGELOG states an indicator lifts code "verbatim" from another, the bible verifies via byte-diff. Example: `heavy-combo-toggles` lifts 5 base combos + 15 directional combo booleans verbatim from `heavy-pentagon` (verified 100% identical except whitespace).

## "Master gate" / "First Bar Only" / `masterFirstBar`

Top-level toggle in some indicators that requires `isFirstBar AND volume >= ta.highest(volume,50)[1]` on the appropriate plot bar. Disables most signals on every bar after the session-first-bar gap event. Default OFF in canonical HVDPBJPPD; default ON in some legacy versions.

## Aggregator alert

Bloomberg-style pipe-delimited alert payload that bundles all signals fired in a single bar: `BULL|<first_status>|<+joined_tags>` or detailed `T3_SIGNAL|TICKER:..|TF:..|SIGNAL:..|...|SLOPE:..`. Used in B2B PUP, TNT-OD, Squarify, VOB Asym T3×6.
