# CARPATHI AUTO-RESEARCH — R&D Innovation Hub Primer

Operating manual for the LLM agent(s) sweeping input-parameter defaults across every Pine v5 indicator study in `~/code/anish/indicators/`.

## Mission

Maximize hit-rate of every detection plot on **potential→kinetic energy transfer** setups: heavy-volume bear-displacement BLOCKS at supply ceilings that absorb supply and ignite large bullish moves (and the demand-floor mirror for bear). Achieve this exclusively by tuning input defaults — never by editing detection logic, plot structure, alerts, or pipeline architecture.

## Mandatory Read Order Before Any Sweep

1. `~/.claude/projects/-Users-anishpatel/memory/ANISH_HAS.md` § PINE INDICATOR SUITE
2. `~/.claude/projects/-Users-anishpatel/memory/verification_protocol.md` v3.2
3. The target indicator file's 5-line CARPATHI header (top of every .pine file, immediately under `indicator(...)`)
4. The target indicator's `CHANGELOG.md` (do not reintroduce a reverted regression)

## Tunable Surface — TOUCH ONLY THESE

For every Pine file, the optimizer may modify the **default value** inside:

- `input.float(...)` — vol-ratio floors (`ls_reg*`, `ls_cum*`), std-dev multipliers (`d1_mult`), body ratios (`ls_body*`, `cs_bodyPct_*`), ATR multipliers, threshold floors
- `input.int(...)` — HV lookback windows, ATR lengths, std-dev lengths, bar counts
- `input.bool(...)` — HV-tier enables (`ub50`..`ub1000`, `useHEV`), engine toggles

Optionally, the optimizer may widen `minval` / `maxval` / `step` if a sweep requires finer granularity — but only when a candidate falls outside the current bounds AND the widening is justified in the PR body.

## Untouchable — HARD READ-ONLY

- Plot offsets, plot colors, plot text, plotshape locations, plotshape sizes
- `indicator(...)` title, shorttitle, max_*
- masterGate, _anyHV_bar0, base-pipeline structure (Pipeline A/B/C/D boundaries)
- Detection-plot formulas — the AND/OR composition of any `sig*` / `*_combo_*` / `as_*` / `co_*` / etc.
- Alert names, alertcondition messages, alert frequency
- Variable identifiers, function signatures, import statements

If a sweep proposes touching any of the above — STOP. Escalate to human review.

## Objective Function

For each candidate configuration `C`:

```
detect_bars(C) = { bar b | any target detection fires on b under C }

reward(C)  = mean_{b ∈ detect_bars(C)} [ fwd_MFE(b, 5) / ATR(b, 20) ]
penalty(C) = mean_{b ∈ detect_bars(C)} [ fwd_MAE(b, 5) / ATR(b, 20) ]

score(C) = reward(C) - 2.0 * penalty(C)
         - 0.5 * max(0, baseline_precision - precision(C))
         - 0.1 * max(0, baseline_recall    - recall(C))
```

- `fwd_MFE(b, k)` = max forward favorable excursion (high - close[b] for bull; close[b] - low for bear) within bars `b+1..b+k`
- `fwd_MAE(b, k)` = max forward adverse excursion within bars `b+1..b+k`
- Baseline = current committed defaults

Reward bars where a bear block transfers to a bull breakout (or floor mirror to bear breakdown). Penalize sustained continuations in the wrong direction.

## Search Strategy

1. **No gradient descent.** The parameter surface is non-monotone; local optima trap.
2. Phase 1 — Coverage: Sobol or Latin-hypercube sampling, ≥ 200 candidates per study.
3. Phase 2 — Refine: Bayesian optimization (Optuna / scikit-optimize) on the top decile from Phase 1.
4. Track the Pareto front across `score × hit-rate × precision`.
5. Validation: a winner must hold across ≥ 3 symbols (e.g., NQ1!, ES1!, BTCUSD) and ≥ 2 regimes (trending, choppy) before lock.

## Anti-Patterns — HARD BANS

- Optimizing on a single symbol or single regime.
- Lowering body-ratio floors below 0.5 — destroys the displacement requirement.
- Enabling HV ranks below 50-bar (`ub20`, `ub25`, `ub30`, `ub40`) — too noisy at base tier.
- Setting `input.*` defaults outside their declared `minval` / `maxval`.
- Reintroducing HTF references into any BASE study.
- Editing detection-plot formulas — only defaults change.
- Disabling all HV tiers simultaneously (would dead-strip Pipeline A).

## Workflow Loop

1. Choose target study (e.g., `base-hvd-pbj-ppd/versions/BASE_HVDPBJPPD_v1.pine`).
2. Enumerate `input.*` declarations into a parameter table:
   | name | type | default | minval | maxval | step | group |
3. Construct sweep grid (Sobol or LHS).
4. For each candidate `C`: write to temp branch, run backtest harness across reference symbols × timeframes.
5. Compute `score(C)` per the objective function.
6. Rank → pick winner → open **draft** PR titled `[CARPATHI] <study> sweep — Δscore=<n>`.
7. PR body MUST include the Output Contract (below).
8. Human approval required for merge. Optimizer never self-merges.

## Output Contract — every Carpathi PR

- Baseline defaults vs. proposed defaults table (full diff).
- Per-symbol score breakdown.
- Confusion matrix (TP / FP / FN) for the tuned detection plot(s).
- Hit-rate, precision, recall deltas vs. baseline.
- MFE / MAE distribution histograms (link or attach).
- One example chart per regime showing the new fires (TradingView snapshot URL or local PNG path).
- Sweep methodology summary: sampler used, candidate count, runtime.

## Boundaries Recap

- READ-ONLY: detection logic, plot structure, alert structure, pipeline architecture, indicator titles, variable identifiers.
- EDITABLE: `input.*` defaults; `minval`/`maxval`/`step` (within justification); toggle states.
- If a sweep wants to add a NEW `input.*`, a NEW detection plot, or modify any AND/OR composition — STOP. Escalate.

## Per-File Carpathi Header Format

Every Pine file gets exactly this 5-line block immediately under its `indicator(...)` declaration, tuned per-file with that file's actual tunable variable names:

```
// ╔ CARPATHI AUTO-RESEARCH — tune ONLY input.* defaults (float/int/bool). No flowery edits. ╗
// Targets: <comma-separated list of tunable variable names in this file>. Goal: maximize hit-rate
// on bar[N-1] heavy-vol bear-displacement BLOCKS at supply ceilings that transfer potential→
// kinetic energy into large bull moves within bar[N..N+5] (mirror at demand floors for bear).
// Score = fwd-MFE/ATR(20) minus 2·fwd-MAE-penalty. Sweep grid, non-monotone — no gradient descent.
```

## Roadmap (informational, not binding)

- v1.0 — manual Carpathi PRs reviewed by human (current).
- v1.1 — agent autorun on schedule, daily candidate sweeps committed to research branch.
- v1.2 — multi-objective optimization across detection-plot families simultaneously.
- v2.0 — cross-indicator coupling: tune one study's defaults conditional on another study's defaults (e.g., HVD PBJ ↔ Squarify joint sweep).
