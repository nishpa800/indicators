# Reference: cross-condition validation (X and Y on same candle)

When the user asks "validate that X and Y fire on the same candle when they should" (or any variant), this is a CROSS-CONDITION check. Two targets, one question: how often do they co-occur?

The user's example (2026-05-10): "I want us to be looking at Nagasaki Plus and unified combo when they're both on the same candle."

## Procedure

### Step 1 — Per-target validation

Run a FULL validation skill invocation for X (Phases 1-3, skip Phase 4 reconcile until cross-condition is complete).
Run a FULL validation skill invocation for Y (same).

These can run in parallel as two separate skill invocations if the parent has the capacity to dispatch two `Agent(general-purpose)` calls.

### Step 2 — Bar-set intersection

After both validations have Phase 3 fire-bar sets, compute:

- **`X_only`** = bars where X fired but Y did not
- **`Y_only`** = bars where Y fired but X did not
- **`X_and_Y`** = bars where both fired (the INTERSECTION — the answer to the user's question)
- **`neither`** = bars where neither fired (not interesting, but include the count for completeness)

### Step 3 — Characterize the intersection

For each bar in `X_and_Y`:

- Timestamp + bar_index + symbol + timeframe
- Preceding bars (bar[-1] through bar[-5]): what fired? Were they leading into the X+Y co-occurrence?
- Following bars (bar[+1] through bar[+5]): what happened after? Was it a continuation, reversal, or noise?

### Step 4 — Frequency analysis

- `|X_and_Y| / |X|` — when X fires, what fraction of the time does Y also fire?
- `|X_and_Y| / |Y|` — when Y fires, what fraction of the time does X also fire?
- `|X_and_Y| / total_bars` — overall co-occurrence rate

### Step 5 — Edge-case classification

Three possible outcomes:

1. **`|X_and_Y| == 0`** — They never co-occur. Could be:
   - **Impossible by definition** (X and Y are mutually exclusive — e.g. SUPER bull and SUPER bear)
   - **Bug** (they SHOULD co-occur but never do — drift in one of them suppressing the other)
   - **Rare** (real but rare; might just need a longer history window)
   - **ESCALATE TO USER** to disambiguate

2. **`|X_and_Y|` is non-zero but `|X_and_Y| / max(|X|, |Y|) < 0.05`** — They rarely co-occur. Likely real but rare. Document the co-occurrence bars and move on.

3. **`|X_and_Y|` is non-zero and substantial** — They co-occur regularly. Document the pattern and check if it's expected (per Anish's domain knowledge).

### Step 6 — Report

Emit a cross-condition report per `templates/cross-condition-check.md`. Include:

- Both per-target validation reports as appendices
- The bar-set algebra
- The intersection bars with characterization
- The frequency table
- The edge-case classification
- ESCALATE flags if Step 5 outcome 1 (zero co-occurrences) needs disambiguation

## Anti-pattern: don't compute intersection from Phase-1 enumeration

The intersection is over FIRE BARS (Phase 3 runtime check), not DEFINITION LOCATIONS (Phase 1 source occurrences).

A common mistake: "X is defined in 3 indicators, Y is defined in 2 indicators, intersection is 0 because no indicator defines both". This is meaningless — what the user wants is bars where both BOOLEANS evaluated true on real data.

Always intersect Phase 3 outputs.

## When user wants OR (X or Y)

Different question. The OR is the UNION of fire-bar sets (X ∪ Y). Easier to compute (no agreement check) but rarely the user's actual question.

## When user wants timed co-occurrence ("X within N bars of Y")

Generalize the intersection: `for each bar where X fired, check if Y fired within ±N bars`. This is a windowed intersection. Treat as a parameterized cross-condition (`N=0` collapses to standard same-bar intersection).

If the user asks for this variant, follow the same procedure but use a windowed intersection in Step 2 instead of strict equality.

## Output schema

```yaml
cross_condition:
  target_x: <canonical-name-X>
  target_y: <canonical-name-Y>
  window: 0   # 0 = same-bar; N = within ±N bars
  per_target_validation_reports:
    x: docs/validation/<date>-<x-slug>.md
    y: docs/validation/<date>-<y-slug>.md
  bar_set_algebra:
    x_only_count: <int>
    y_only_count: <int>
    x_and_y_count: <int>
    neither_count: <int>
    total_bars_scanned: <int>
  intersection_bars:
    - timestamp: <ISO>
      bar_index: <int>
      symbol: <e.g. ES1!>
      timeframe: <e.g. 5m>
      preceding_5_bars: [<what-fired-on-each>]
      following_5_bars: [<what-fired-on-each>]
  frequency:
    x_and_y_over_x: <fraction>
    x_and_y_over_y: <fraction>
    x_and_y_over_total: <fraction>
  edge_case: zero | rare | regular
  escalate_to_user: <bool>
  escalation_reason: <if escalating>
```
