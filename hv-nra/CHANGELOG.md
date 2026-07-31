# HV NRA — CHANGELOG

Generated indicator. Source of truth is `build_hv_ladder.py`; the `.pine` under
`versions/` is its output. Edit the generator and re-run — never hand-edit the
`.pine` (it will be overwritten).

    python3 build_hv_ladder.py

## 50-step ladder v2 — 2026-06-13
- Densified the volume-high lookback ladder to a full 50-bar step:
  50, 100, 150, ... 950, 1000 (20 tiers), replacing the original sparse
  50/150/250/500/1000.
- Kept verbatim: non-repainting architecture (`volume[1]` + `ta.highest(...)[1]`
  + `offset=-1`, plot==alert 1:1), HEV running-max, Hot-Spot calendar.
- Tiers NESTED via a `not is{N+50}Bar` priority chain -> exactly one marker per
  bar (highest tier reached).

## +1.5k-4k mega-tiers — 2026-07-04
- Added FIVE ADDITIONAL detection tiers above 1000: **1500, 2000, 2500, 3000,
  4000** (irregular steps, no 3500). Ladder is now 25 tiers + HEV + Hot Spot.
- Each new tier gets the full treatment, 1:1 with the existing tiers: an
  `input.bool` toggle (`use1500`..`use4000`), a confirmed-bar calc
  (`is{N}Bar = volume[1] == ta.highest(volume, {N})[1]`), a `plot_{N}` nesting
  condition, a `plotshape`, and an `alertcondition`.
- Nesting chain generalized to the ascending tier list so it stays correct
  across the irregular mega-steps. New priority:
  `HEV > 4000 > 3000 > 2500 > 2000 > 1500 > 1000 > 950 > ... > 50`.
  The one existing line that changed: `plot_1000` now defers to `is1500Bar`
  instead of `isHEV`. (`is{big}Bar` implies `is{small}Bar`, so one marker per
  bar still holds.)
- Colors: existing 20 tiers UNCHANGED (blue->red ramp, denominator preserved).
  Mega-tiers continue the same formula (R=255, G=45, blue channel ramped back up
  80->240) so 1000's red sweeps on through pink into bright magenta — stays
  legible with white text and pops on light and dark chart themes.
- Sizes: mega-tiers escalate above the ladder max (`size.normal`) —
  `size.large` for 1500-3000, `size.huge` for 4000 — since they mark rarer,
  bigger events.
- Exports updated: `activeVolSignals` now 0..26 (25 tiers + HEV), `signalStates`
  is a 27-slot array ([0..24]=tiers, [25]=HEV, [26]=HotSpot).
- Max lookback is now 4000 (4001 bars with the `[1]` offset), under the 5000
  historical-buffer cap. `ta.highest` auto-sizes the buffer from its constant
  length — same mechanism the 1000-tier already relied on — so no `max_bars_back`
  is needed. 27 plot outputs total, under the 64-plot limit.

## remove Hot Spot — 2026-07-04
- Removed the Hot Spot (HS) calendar feature entirely: `useHS` input, the
  calendar-window calcs + `isHotSpot`, `plot_HS`, its plotshape and
  alertcondition, and its `signalStates` slot. Title is now
  `HV(50-1000 step50 +1.5k-4k / HEV)`.
- Ladder is now 25 tiers + HEV (no HS). Exports: `activeVolSignals` unchanged
  at 0..26 (25 tiers + HEV); `signalStates` is now a 26-slot array
  ([0..24]=tiers, [25]=HEV). 26 plot outputs / 26 alerts.
