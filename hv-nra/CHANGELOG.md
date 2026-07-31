# CHANGELOG — hv-nra

## 2026-07-09 — HV ROLL v2: 15 CUMULATIVE rolling windows (50→4K ladder)

New file: `versions/HV_ROLL_15_cumulative_50-4K_v1_2026-07-09.pine`
Generator: `build_hv_roll_15.py` (one source of truth, like `build_hv_ladder.py`).

**Why.** The prior "HV ROLLING CLUSTERS" study detected *"only"* bands — `500 only
(not 1000+)`, `250-or-500`, `150 only`, etc. Those go **quiet exactly when a stock
gets stronger** and its highs graduate to a rarer tier, which is the wrong signal.
This rebuild replaces every band with a **cumulative `>=` class**.

**What changed.**
- Raw tier material is now the **full 50-step → 4K mega ladder** (50,100,…,1000,
  then 1500/2000/3000/4000, plus HEV all-time) — not the old sparse 50/150/250/500/1000.
- **15 windows, all cumulative `>=`** (rarest→common): HEV, 4000+, 3000+, 2000+,
  1500+, 1000+, 750+, 500+, 400+, 300+, 250+, 200+, 150+, 100+, 50+.
  A `1000+` window counts every 1000-bar high **or rarer** (up to all-time), so
  strength never leaks out of a bucket. No `not is{bigger}Bar` subtraction anywhere
  — that subtraction is precisely what created the old "only" bands.
- Each window still has live **Count (events)** and **within Bars** inputs.

**Calculus for the default window sizes.** Model each `>= N` class as ~Poisson:
P(a closed bar is a new N-bar high) ≈ 1/N, so it fires ≈ once per N bars. The rolling
count is the moving **sum** (discrete integral) of that event stream; its 1st/2nd
differences are clustering **velocity/acceleration**. Random baseline over a W-bar
window is `E[n] = W/N`. Requiring a fire to mean "events D× denser than random" gives

    W_default = round(COUNT · N / D),   shipped D = 2  (every fire ≈ 2× random density).

The generator prints the derived schedule; every window lands at a uniform **2.0×**
density bar. Tighter window / higher COUNT → sharper derivative → more motion.
Data-window `clusterLoad`, `motionVel` (velocity) and `motionAcc` (acceleration)
expose that motion directly.

**Architecture kept verbatim (NRA + constitutional rolling windows).**
- Tiers compare the prior closed bar (`volume[1] == ta.highest(volume,N)[1]`) → non-repainting.
- Counting gated on `barstate.isconfirmed`; each window is a TRUE sliding trailing-N
  moving sum (`math.sum`, O(1)/bar — not an anchored wait-N-then-reset window; passes
  `check_no_fixed_windows.sh`). `math.sum` (vs a manual loop) matters here because the
  big windows reach 4000 bars.
- Fire = leading edge of `n >= COUNT` (`cond and not cond[1]`), re-arms automatically.
- Plot and alert per window share ONE boolean (1:1, can't desync); markers `offset=-1`.
- Per-window alertconditions (15) + an ANY alertcondition + one `alert()` any-call
  whose payload names which windows fired.

ASCII-only source (TradingView's Pine lexer rejects non-ASCII punctuation).
