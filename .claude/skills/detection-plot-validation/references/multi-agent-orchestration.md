# Reference: multi-agent orchestration

How to dispatch subagents so validation parallelizes cleanly and consistently. The skill's value scales with this — one Claude validating one target is fine; ten Claudes validating ten targets only beats one Claude if each subagent has a NARROW BRIEF and a FIXED OUTPUT SCHEMA.

## Principles

1. **Subagents are read-only.** They never edit files. They return structured data; the parent agent applies it.
2. **One agent, one input.** Each subagent gets ONE Pine file, OR ONE diff pair, OR ONE location's logger query. Never a "do everything for this indicator" brief.
3. **Schema-first.** Every subagent's return shape is defined here. The parent expects this shape and fails fast on deviation.
4. **No improvisation.** If a subagent can't fulfill its brief, it returns a structured `BLOCKED` payload with the reason — it does NOT take initiative.
5. **Cap parallelism at 12.** Past 12 subagents in one message, the harness shows diminishing returns and merge cost climbs. Batch if needed.

## Phase 1 — ENUMERATE subagent

**When to dispatch**: if ≥4 distinct Pine files contain the target.

**Subagent type**: `Explore` (read-only).

**Brief template** (parent uses this verbatim, filling in the bracketed slots):

```
Search ONE Pine file for occurrences of a detection plot.

TARGET: <canonical-name> (e.g. UNIFIED_COMBO_BULL)
ALIASES: <comma-separated-alias-list> (e.g. UNIFIED_COMBO_BULL, csNew3_Bull, unified_combo, UC)
FILE: <absolute-path-to-pine-file>
LINE_RANGE_HINT: <optional-line-range-from-YAML-if-known>

Find every occurrence of any alias in the file. Classify each as DEFINITION,
REFERENCE, INPUT, PLOT, ALERT, or COMMENT (definitions per references/pine-grep-patterns.md).

Return ONLY this YAML (no preamble, no postamble):

```yaml
file: <absolute-path>
indicator_family: <inferred from path, e.g. squarify>
occurrences:
  - line: <line-number>
    classification: DEFINITION | REFERENCE | INPUT | PLOT | ALERT | COMMENT
    pine_variable: <exact variable name at this location>
    raw_line: |
      <the Pine line verbatim, including indentation>
    helper_refs: [<helper variable names referenced on the RHS>]
    ipsf_inputs: [<input.* parameter names referenced>]
status: COMPLETE | BLOCKED
blocked_reason: <if BLOCKED, why; else null>
```

Do NOT edit the file. Do NOT search files other than the one specified.
```

**Parent merges** all subagent outputs into the Phase-1 enumeration table.

## Phase 2 — STATIC-DIFF subagent

**When to dispatch**: if ≥6 DEFINITION pairs need diffing (i.e. ≥4 DEFINITIONs).

**Subagent type**: `Explore` (read-only — it only reads Pine files).

**Brief template**:

```
Diff two Pine boolean definitions of a detection plot.

TARGET: <canonical-name>

LOCATION_A:
  file: <path>
  line_range: <e.g. L78-L82>
LOCATION_B:
  file: <path>
  line_range: <e.g. L626-L628>

Read both line ranges, extract the boolean assignment + immediate helpers + IPSF inputs.
Normalize per references/4-phase-procedure.md § Phase 2 step 2.

Return ONLY this YAML:

```yaml
location_a:
  file: <path>
  line_range: <range>
  normalized_boolean: |
    <the normalized boolean>
  helpers_used: [<list>]
  ipsf_used: [<list with defaults>]
location_b:
  file: <path>
  line_range: <range>
  normalized_boolean: |
    <the normalized boolean>
  helpers_used: [<list>]
  ipsf_used: [<list with defaults>]
verdict: identical | cosmetic-drift | ipsf-default-variation | ipsf-asymmetry | semantic-drift | UNCLASSIFIABLE
verdict_evidence: |
  <one paragraph explaining the classification with line citations>
status: COMPLETE | BLOCKED
blocked_reason: <if BLOCKED>
```

Do NOT edit any file. Do NOT classify as identical unless the normalized booleans match byte-for-byte.
If you can't classify, return UNCLASSIFIABLE — the parent will escalate.
```

**Batching**: if ≥12 pairs need diffing, batch 3 pairs per subagent. Each subagent returns an array of 3 verdicts. Don't exceed 4 pairs per subagent (signal drops).

## Phase 3 — TV-FIRING subagent

**When to dispatch**: if ≥4 DEFINITION locations AND TV MCP is connected.

**Subagent type**: `general-purpose` (needs MCP tool access).

**Brief template**:

```
Query the Path A logger labels for ONE detection-plot location.

TARGET: <canonical-name>
LOCATION:
  indicator: <e.g. heavy-pentagon>
  file: <path-to-canonical-pine>
  pine_variable: <e.g. sigSAAB>
  expected_offset: <e.g. 0 or -1>

LOGGER:
  pine: <path-to-Path-A-logger-pine>
  input_source_target: <which "Source N: ..." input to point at>

Use mcp__tradingview__data_get_pine_labels (or the connected TradingView MCP equivalent) to query
labels on the chart. Filter for labels emitted by the logger for THIS variable.

Return ONLY this YAML:

```yaml
target: <canonical-name>
location_indicator: <indicator>
location_variable: <variable>
fire_bars:
  - timestamp: <ISO-8601>
    bar_index: <integer>
    symbol: <e.g. ES1!>
    timeframe: <e.g. 5m>
  - ...
fire_count: <integer>
query_range: <bars searched, e.g. last 5000>
status: COMPLETE | BLOCKED
blocked_reason: <if BLOCKED — e.g. "MCP not connected", "Logger not loaded on chart", "input.source unset">
```

Do NOT modify the chart. Do NOT load indicators. Read-only query.
```

**Parent merges** fire-bar sets across locations; computes agreement + drift sets.

## Phase 4 — RECONCILE (no subagents)

Reconcile is single-threaded by design. The parent agent:

1. Builds the proposal
2. Presents to user
3. Edits `bible-input/extract-*.yaml` files sequentially
4. Runs the three regenerators in order
5. Verifies YAML==JSON
6. Commits

Subagents in Phase 4 would conflict on YAML edits. Don't dispatch.

## Cross-condition variant

If the user request is "X and Y on same candle":

1. Run a full validation skill invocation for X (Phases 1-3, skip Phase 4 reconcile)
2. Run a full validation skill invocation for Y (same)
3. Intersect the fire-bar sets in the parent agent (not a subagent — needs both reports)
4. Write the cross-condition section per `templates/cross-condition-check.md`

The two per-target validations CAN run in parallel as two separate skill invocations if you have two parent agents available (e.g. `Agent(general-purpose)` × 2). Both must complete before the intersection is computed.

## Subagent prompt anti-patterns (DON'T DO THESE)

- **"Validate everything about X"** — too broad; subagent will improvise
- **"Find drift"** — what's drift? Subagent's judgment varies; use the explicit classification taxonomy
- **"Be thorough"** — meaningless to a subagent; specify which fields are required
- **"Use your best judgment"** — never. The skill is the judgment; the subagent executes.
- **"Modify the file if needed"** — subagents are read-only. Period.

## When parallelism HURTS

- 1-3 Pine files in scope → single agent is faster (no merge overhead)
- Stateful composite needing multi-step Phase M run → Path A path is single-threaded by chart
- Reconcile phase (4) → always single-threaded
- User-interaction loops → can't parallelize across user
