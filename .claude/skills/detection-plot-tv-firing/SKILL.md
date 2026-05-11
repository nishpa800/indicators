---
name: detection-plot-tv-firing
description: Use ONLY when Anish is at his desk with TradingView open AND the Path A logger Pines loaded on the chart. Captures fire bars via TradingView MCP (`data_get_pine_labels`) for one or more detection plots that have been flagged `BLOCKED-NEEDS-TV-FIRING-SKILL` by the main `detection-plot-validation` skill. Phase 3 Path A only — does not duplicate Phases 1, 2, 4 of the main skill. INVOKE ONLY when explicitly asked or when Anish confirms he's at the chart; never as part of autonomous validation runs.
---

# Detection-plot TV firing

You are the chart-side firing verifier. This skill is the spinout from `detection-plot-validation` that handles Phase 3 Path A — the part that needs Anish + TradingView + a connected MCP server.

**This skill is gated behind explicit human readiness.** It does NOT run as part of autonomous validation. The main `detection-plot-validation` skill flags targets as `BLOCKED-NEEDS-TV-FIRING-SKILL` and keeps going; this skill picks up those targets later when Anish is at his desk.

## When to invoke

YES if any of:

- Anish says "let's do the TV firing now" / "I'm at the chart"
- A validation report has `BLOCKED-NEEDS-TV-FIRING-SKILL` entries AND Anish has acknowledged he's ready
- Anish asks "run TV firing on X" with X being a validated target

NO if:

- Running an autonomous validation pass (Anish at work)
- The TV MCP is not connected (check `/mcp` output first)
- Path A logger Pines are not loaded on the chart (the MCP can list active indicators)

## Preconditions

Before invoking this skill, verify:

1. **TV MCP connected**. Run `/mcp` and confirm the TradingView MCP is in the active server list.
2. **Path A logger loaded for the target's indicator family**. The 5 logger Pines are in `path-a-loggers/versions/`:
   - `LOGGER_HCT.pine`
   - `LOGGER_B2B_PUP.pine`
   - `LOGGER_HVDPBJPPD.pine`
   - `LOGGER_TNT_OD.pine`
   - `LOGGER_SQUARIFY.pine`
3. **Chart is on a reasonable history window**. The logger only captures fires within the chart's loaded bar count (typically 5000-20000 bars).
4. **Each logger's `input.source(...)` is pointing at the right plot** of the source indicator on the same chart.

If any precondition fails, STOP and tell Anish what's missing. Don't proceed.

## Procedure

### Step 1 — Pull list of BLOCKED targets

Read recent validation reports under `docs/validation/*.md`. Find every report whose verdict includes `BLOCKED-NEEDS-TV-FIRING-SKILL`. Build a list:

```
target: <canonical-name>
indicator_family: <family>
location_in_pine: <file:line>
expected_offset: <0 or -1>
last_validated_at: <timestamp from report>
```

### Step 2 — Group by indicator family

Some chart layouts will have multiple loggers loaded; group targets so a single logger query can capture multiple targets at once.

### Step 3 — Per-target: query the logger

For each target, invoke the TV MCP's `data_get_pine_labels` (exact tool name depends on which TradingView MCP server is installed):

```yaml
mcp_tool: mcp__tradingview__data_get_pine_labels  # or whichever MCP is configured
parameters:
  indicator_id_or_title: "Logger <Family>"
  symbol: <current chart symbol>
  timeframe: <current chart timeframe>
  limit: 500
```

Parse the returned labels. Logger label text follows the convention `<canonical-name> | <indicator> | <bar_index> | <timestamp>` per `path-a-loggers/README.md`. Extract fire bars per target.

### Step 4 — Update the validation report

For each target that was `BLOCKED-NEEDS-TV-FIRING-SKILL`, append a new section to its report at `docs/validation/<date>-<target-slug>.md`:

```markdown
## Phase 3 — TV firing (chart-side path A) — completed YYYY-MM-DD

| Location | Fire-bar count | Query window | Status |
|---|---|---|---|
| <indicator>::<variable> | <int> | <symbol + tf + bars> | COMPLETE |

### Fire bars

<list of timestamps + bar_indices>

### Update to final verdict

Previously: BLOCKED-NEEDS-TV-FIRING-SKILL
Now: <OK | DRIFT-RECONCILED | DRIFT-PENDING-USER>
```

### Step 5 — If new drift discovered

If the Path A fire bars reveal a drift that Phase 2 static-diff missed (e.g. fire bars differ across locations despite static-diff saying `identical`), CREATE A NEW DRIFT FINDING per `templates/drift-finding.md` (in the main skill's templates) and tag as `runtime-drift`.

Apply Phase 4 RECONCILE per the main skill's procedure — autonomously per Anish's standing approval, treating new findings the same as static ones (versioned new file, not rename/delete).

### Step 6 — Commit + push

After all queued targets are processed:

```bash
git add docs/validation/ bible-input/extract-*.yaml data/indicators.{yaml,json} docs/{roots,composites,redundancy,lineage,visual-trees}.md
git commit -m "tv-firing: Path A complete for <N> targets — see report updates"
git push
```

## Hard guardrails (this skill specifically)

- **Never load indicators on the chart from this skill.** Anish does the chart setup. This skill only QUERIES labels.
- **Never modify the source Pine file in response to TV-firing data.** If you find Pine source needs changing, create a new versioned file per the standing approval (`STANDING_APPROVAL.md` in the main skill).
- **Don't block on chart state.** If the logger returns zero labels, status `BLOCKED-LOGGER-EMPTY` and move on; don't wait for Anish to refresh the chart.
- **Never spam the MCP.** Cap at 100 queries per 5-minute window per the standing approval's rate-limit guardrail.

## Output

This skill updates existing validation reports — it doesn't author new ones. The main `detection-plot-validation` skill owns report creation. This skill appends a "Phase 3 chart-side" section to each report it processes.

If a target was previously verdict=`OK` or `DRIFT-RECONCILED` and the TV firing reveals new drift, this skill DOWNGRADES the verdict to `DRIFT-PENDING-USER` and creates a new drift-finding artifact. Anish reviews next time he's at his desk.

## Standing approval

Inherits from `detection-plot-validation/STANDING_APPROVAL.md`. Same rules: don't pause; parallel where possible; minimal escalation; version-control instead of rename/delete.

## Why this is a separate skill (Anish's reasoning, 2026-05-10)

> "I don't want it to get held up if it can't do some things... if the TV firing can't be done without me, then you gotta remove that from the skill. We need to have a separate skill just for the TV firing... I can't have fifteen different agents bugging me that, hey, I need you to do the TV firing while I'm at work."

The main `detection-plot-validation` skill must be FULLY autonomous. Path A requires Anish; Path A goes here. The main skill flags + continues; this skill catches up later.
