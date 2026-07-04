# HV ROLLING CLUSTERS NRA — CHANGELOG

Generated indicator. Source of truth is `build_hv_rolling_clusters.py`; the
`.pine` under `versions/` is its output. Edit the generator (the ladder is a
single `LADDER` list) and re-run — never hand-edit the `.pine`.

    python3 build_hv_rolling_clusters.py

## v1 — clean "N and above" ladder to 4000 — 2026-07-04
- First canonical version. Rolling-window high-volume **cluster** detectors: each
  window fires when at least `COUNT` events of its class occur within the last
  `BARS` bars (both per-window user inputs), on the leading edge of the count
  crossing the threshold. Non-repainting: `volume[1]` + `ta.highest(volume,N)[1]`,
  events gated on `barstate.isconfirmed`, markers `offset=-1`, plot==alert 1:1.
- **Design change vs the prior rolling-clusters build:** eliminated the arbitrary
  "only" and "A-or-B band" window classes (500-only, 250-only, 150-only, 50-only,
  250-or-500, 150-or-250). Every window is now a pure ladder rung — **"N-bar high
  and above."** Because the tier flags are nested (`is1000Bar` ⟹ `is500Bar` ⟹ …),
  the raw `is{N}Bar` flag already means "N or rarer," so no subtraction is needed.
- **Ladder extended to 4000** to match the expanded HV detection set. 11 windows,
  rarest first:

  | # | Class | default count / window |
  |---|---|---|
  | W1 | Nagasaki (all-time-high vol = HEV) | 2 / 250 |
  | W2 | 4000-bar high and above | 2 / 250 |
  | W3 | 3000+ | 2 / 200 |
  | W4 | 2500+ | 2 / 200 |
  | W5 | 2000+ | 2 / 175 |
  | W6 | 1500+ | 2 / 150 |
  | W7 | 1000+ | 2 / 150 |
  | W8 | 500+ | 2 / 100 |
  | W9 | 250+ | 3 / 75 |
  | W10 | 150+ | 3 / 50 |
  | W11 | 50+ (any HV tier) | 4 / 30 |

  Defaults are tunable starting points (rarer rung → smaller count / longer
  window). Nagasaki kept as the top rung (rarest "and above").
- **Hot Spot removed** — it was computed-but-never-plotted dead weight in the
  prior build and is not wanted.
- Alerts: one `alertcondition` per window (11), one `ANY` alertcondition, and one
  `alert()` any-call whose payload names which windows fired. Off-chart
  data-window plots (`n1..n11`, `activeWindows`) for tuning.
- Buffer: `max_bars_back=5000` covers the 4000-bar `ta.highest` and the sliding
  `f_sum_true` window (≤5000). These don't compound — `is{N}Bar` is a stored
  series, so `f_sum_true` reads history rather than re-deriving `ta.highest` at an
  offset. 23 plot outputs, under the 64-plot limit.
