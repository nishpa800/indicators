---
name: pareto-leverage
description: 80/20 ranking. Score every plot × symbol × TF × axis-cell on its contribution to realized alpha. Identify the 20% that produces 80% of value. Drive promotion / demotion / retirement decisions. Owner-tier skill. Runs nightly across the portfolio, weekly per Plot Owner, monthly for the strategy book.
when_to_use: Nightly hook at 22:00 UTC after long-run-calibration has rolled up the day's outcomes. Weekly per Plot Owner during strategy review. Monthly when deciding whether to retire low-Pareto plots or hire new Plot Owners for novel high-Pareto candidates. Also invoke whenever a strategy review chain reaches the Pareto step.
tier: owner
---

# Pareto Leverage

**Tier**: owner (strategic stewardship; allocation of compute, capital, and attention).

**Purpose**: Identify the 20% of plots × conditions × symbols × TFs that produce 80% of the realized alpha. Concentrate the system's resources — compute, capital, attention — on the top 20%. Demote or retire the bottom 80%.

## Why Pareto, not "every plot is sacred"

Anish's alpha-max philosophy: hyper-aggressive, maximize return. Every resource has a marginal cost. Spending Opus tokens on a plot that historically contributes 0.02% to realized alpha is a leak. Pareto scoring makes the leak visible and the trim mechanical.

## Input

```yaml
target:
  type: portfolio | plot | data_source | symbol
  scope: <e.g. "all plots in the book" or "PBJ Bull across all symbols">
  window: <e.g. "trailing 30 days" or "since inception">
  calibration_log: <path to per-fire payload directory>
```

## Output

```yaml
pareto_ranking:
  ranking:
    - rank: 1
      cell: <plot × symbol × TF × axis-slice>
      contribution_bps: <realized alpha contribution in basis points>
      n_fires: <int>
      bps_per_fire: <number>
      cumulative_pct_of_total: <e.g. "32.4%">
    - rank: 2
      ...
  frontier:
    top_20_pct_cells: [<list>]
    top_20_pct_cumulative_alpha: <e.g. "81.7%">  # the actual 80/20 verification
  trim_candidates:
    - cell: <bottom-tier cell>
      cumulative_contribution_bps: <small number>
      recommendation: <"automate" | "demote" | "retire">
      shiva_redteam_score_if_available: <reference>
  promote_candidates:
    - cell: <novel high-Pareto cell>
      recommendation: <"hire dedicated Plot Owner" | "increase capital allocation" | "council-mode verify">
```

## Procedure

1. **Read the calibration log.** Filter to the target scope and window. Each per-fire payload contributes one row (fire id, plot, symbol, TF, axis-card, matrix confidences, outcome stamp, realized alpha in bps).
2. **Group by cell.** Default cell: (plot × symbol × TF). For deeper analysis: (plot × symbol × TF × axis-slice). Sum realized alpha per cell. Count n_fires per cell.
3. **Sort by total contribution descending.**
4. **Compute cumulative percentage.** Walk down the sorted list; cumulative pct of total alpha. Mark the row where cumulative first crosses 80% — everything above is the top 20% by impact.
5. **Verify the 80/20.** If the actual breakpoint is at, say, 35% of cells producing 80% of alpha, report that — Pareto is empirical, not dogmatic. Sometimes the curve is steeper (10/90), sometimes flatter (35/65). Report what's there.
6. **Identify trim candidates.** Cells in the bottom 80% with low bps-per-fire AND low n_fires (no signal AND no volume). Cross-reference with `shiva-redteam` outputs if available. Recommend automate / demote / retire.
7. **Identify promote candidates.** Cells in the top 20% with high bps-per-fire that don't yet have a dedicated Plot Owner. Recommend hiring.

## Hard rules

- Pareto runs against the ACTUAL calibration log, not against priors. If we don't have enough fires to compute a Pareto ranking (n < 30 per cell), say so explicitly — don't invent.
- Pareto does NOT override `inversion`. A high-Pareto cell that would violate a never-do rule STILL doesn't fire. Inversion is unconditional; Pareto is conditional on inversion compliance.
- Pareto does NOT override per-fire calibration. A high-Pareto cell that triggers a low-confidence matrix row STILL doesn't fire at that confidence. Pareto allocates attention; the matrix decides individual fires.
- Trim recommendations require Anish sign-off (today). Future: when calibration accumulates >180 days of outcomes, Plot Owners may be granted retirement authority via SD-N. Open question §13 #6 of the master spec.

## Output destination

- Nightly portfolio rollup: `docs/agentic-os/pareto-rollups/<date>-portfolio.md`
- Weekly per-plot: `docs/agentic-os/pareto-rollups/<date>-<plot>.md`
- Monthly book review: `docs/agentic-os/pareto-rollups/<date>-monthly-book.md`

## Cross-references

- Pillar definition: `docs/agentic-os/strategy/2026-05-11-agentic-os-full-build-spec.html` §2 Pillar 6 + §12 (Pareto applied to the build queue itself).
- Reads from: per-fire payloads (calibration log).
- Informs: hiring decisions (new Plot Owners), retirement decisions (deprecating plots), capital allocation.
- Constrained by: `inversion` (never-do rules are unconditional).
- Distinct from: `long-run-calibration` (which is the prerequisite that builds the calibration log Pareto reads).
