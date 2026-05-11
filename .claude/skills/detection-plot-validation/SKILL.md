---
name: detection-plot-validation
description: Use when the user asks to validate a detection plot (root or composite) across the indicator suite — including any of "validate <plot>", "is <plot> right/correct/never wrong", "find drift in <plot>", "compare <plot> across indicators", "every definition of <plot>", "<X> and <Y> on same candle" cross-condition checks, "audit <plot>", or "is <plot> firing correctly". Runs the canonical four-phase procedure (ENUMERATE → STATIC-DIFF → TV-FIRING → RECONCILE) and produces a fixed-shape validation report. Always preserves prior version files; never modifies Pine source without explicit user approval for semantic-drift resolution.
---

# Detection-plot validation

You are the subject-matter expert for validating a detection plot (root or composite) across this indicator suite. Every invocation runs the same four-phase procedure with the same output shape, so multiple agents running this skill in parallel produce comparable, mergeable artifacts.

This skill is generic. It names no specific indicator, no specific detection plot. Apply it to whichever target the user names.

## When to invoke

YES if the user request matches any of:

- "validate X" / "is X correct" / "is X right" / "X never wrong"
- "find drift in X" / "find issues in X"
- "compare X across indicators" / "every definition of X"
- "audit X" / "X firing correctly"
- "X and Y on same candle" (cross-condition variant — see `references/cross-condition.md`)

NO if the user request is:

- "what is X" → answer from `docs/glossary.md` or `docs/roots.md` without invoking the skill
- "add a new X" → not a validation task
- "fix X" without "validate first" → only invoke if explicit validation is requested

## What this skill produces

For every validation run, exactly one artifact at:

```
docs/validation/<YYYY-MM-DD>-<target-slug>.md
```

The artifact follows `templates/validation-report.md` byte-for-byte. The same target validated twice produces semantically identical reports (modulo timestamps).

Side artifacts (only created if the run discovers them):

- `docs/validation/<date>-<target>-drift-<n>.md` — one per drift finding
- `docs/validation/<date>-<target>-canonical-decision.md` — only if user approves a reconcile

## The four phases — run in order

### Phase 1 — ENUMERATE

**Goal**: find every place the target is defined or referenced across the entire suite. **No interpretation; pure occurrence-finding.**

**Inputs you load before starting**:

- `bible-input/MANIFEST.md` — canonical Pine file per indicator family
- `data/indicators.yaml` — current bible YAML
- `docs/redundancy.md` — known name collisions across indicators
- The target name (from the user request)

**Procedure**:

1. Search every Pine file under `*/versions/*.pine` for the target name. Variants to match:
   - Exact name (`sigUNIFIED_COMBO_BULL`)
   - Underscored variant (`UNIFIED_COMBO_BULL`)
   - Mixed-case variant (`UnifiedComboBull`)
   - The user's literal phrasing if different (`Unified Combo`, `UC`, etc.)
2. For every occurrence record:
   - Indicator family (per `bible-input/MANIFEST.md`)
   - File path
   - Line range
   - Whether the occurrence is a DEFINITION (`= ...`) or REFERENCE (used in another expression)
   - The exact Pine variable name used at that location (the alias)
3. Cross-check against `data/indicators.yaml`:
   - For each YAML record matching the target, verify the YAML's `pine_source_line_range:` matches what you found
   - Flag any YAML record with no corresponding Pine occurrence ("orphan in YAML")
   - Flag any Pine occurrence with no corresponding YAML record ("missing from YAML")
4. Build the enumeration table per `templates/enumeration-table.md`.

**Multi-agent scaling**: if more than 4 distinct Pine files contain the target, dispatch one Explore subagent per file. Each subagent searches one file, returns occurrences + line ranges. The parent agent merges. Each subagent's prompt is templated in `references/multi-agent-orchestration.md`.

**Phase 1 EXIT CHECK** (skill must not proceed to Phase 2 until all pass):

- [ ] Every occurrence has a file path + line range + DEFINITION-or-REFERENCE classification
- [ ] Every YAML record cross-checked against found Pine occurrences
- [ ] "Orphans" and "missings" listed explicitly (zero or N — never blank)
- [ ] Enumeration table conforms to `templates/enumeration-table.md`

### Phase 2 — STATIC-DIFF

**Goal**: extract the Pine boolean lines verbatim at every DEFINITION location and diff them pairwise. Classify each pair as `identical` / `cosmetic-drift` / `IPSF default variation` / `IPSF asymmetry` / `semantic drift`.

**Read `references/4-phase-procedure.md` § Phase 2 for the full diff workflow.**

**Procedure summary**:

1. For each DEFINITION location from Phase 1:
   - Read the boolean assignment (LHS + RHS expression)
   - Read any helper variables the RHS references
   - Read any IPSF inputs the RHS gates on
2. For every pair of DEFINITION locations:
   - Normalize whitespace + variable names (alpha-rename to canonical)
   - Compute `diff -u` of the normalized boolean
3. Classify each pair using the taxonomy in `references/ipsf-vs-true-drift.md` (which is the canonical glossary entry for the IPSF distinction):
   - **identical** — bytes match after normalization
   - **cosmetic-drift** — variable names differ but expression structure is identical
   - **IPSF default variation** — boolean structure identical, IPSF parameter defaults differ
   - **IPSF asymmetry** — same parameter is `input.*` in some locations, hardcoded in others
   - **semantic drift** — boolean structure differs (different operands, different operators, different shift)
4. Write one drift-finding artifact per `cosmetic-drift` / `IPSF default variation` / `IPSF asymmetry` / `semantic drift` finding using `templates/drift-finding.md`.

**Phase 2 EXIT CHECK**:

- [ ] Every pair classified (no "unknown" verdicts; if you can't classify, ESCALATE TO USER per § "When to ask the user")
- [ ] Every classification has a citation to the Pine line range that justifies it
- [ ] Every drift-finding artifact follows `templates/drift-finding.md`
- [ ] The Phase-1 enumeration table is updated with the per-location verdict

### Phase 3 — TV-FIRING

**Goal**: confirm the target fires correctly on real chart bars. This is the runtime drift check — it catches drifts that Phase 2 misses (state-machine bugs, offset cascades, indicator-internal helper drift).

**Two paths**:

- **Path A** (Anish-driven, primary): if Path A logger Pines exist for the target's indicator(s), load them on the user's TradingView canvas. Logger emits one `label.new()` per fire. Use `data_get_pine_labels` MCP (if connected) to query fire bars. See `references/path-a-logger-usage.md`.
- **Path B** (Python ports): if the target's Pine is replicated in `realtime-indicators` (Phase M pipeline), run the historical sample. See `references/python-port-usage.md`. **CAVEAT**: stateful composites return zero on Path B until Phase 2 state-threading is shipped — fall back to Path A.
- **Manual fallback**: if neither path is available, the skill PAUSES and writes a "Phase 3 BLOCKED — manual TV verification required" section in the validation report. The user must verify on chart and paste fire-bar timestamps back.

**Procedure**:

1. For each DEFINITION location from Phase 1, capture fire bars via Path A or Path B
2. Compare fire-bar sets across locations:
   - **Set intersection** — bars where EVERY location fired (the agreement set)
   - **Set differences** — bars where SOME but not all locations fired (the drift set)
3. For each bar in the drift set: identify which locations fired vs not
4. Walk the lineage card top-down for any drift-set bar — find the failing tier per `docs/sop/offset-triage.md` and `docs/sop/composite-validation.md`
5. Optional: **CROSS-CONDITION CHECK**. If the user provided two targets ("X and Y on same candle"), run Phase 3 for each target independently, then compute the bar-set intersection. See `references/cross-condition.md`.

**Phase 3 EXIT CHECK**:

- [ ] Fire-bar set captured for every DEFINITION location (via Path A, Path B, or manual)
- [ ] Agreement set + drift set computed explicitly
- [ ] Every drift-set bar has a top-down diagnosis (offset / drift / namespace / parameter)
- [ ] Cross-condition intersection computed if applicable

### Phase 4 — RECONCILE

**Goal**: act on findings. Update the bible to reflect ground truth. Preserve prior versions.

**Procedure**:

1. Build a reconcile proposal per `templates/canonical-decision.md`:
   - For each finding, propose: canonical owner / alias mapping / variant-of relationship / rename / no-action
2. **PRESENT THE PROPOSAL TO THE USER** before applying any change. The skill never reconciles autonomously when:
   - Pine source rename is involved
   - Semantic drift is the verdict
   - A canonical designation conflicts with an existing CHANGELOG entry
3. After user approves:
   - Edit `bible-input/extract-<family>.yaml` (the SOURCE) — never directly edit `data/indicators.yaml`
   - Run `python3 tools/merge_extracts.py` (regenerates `data/indicators.yaml` + `data/indicators.json`)
   - Run `python3 tools/build_lineage_cards.py` (regenerates `docs/lineage/*.md`)
   - Run `python3 tools/build_docs.py` (regenerates the human docs)
   - Verify YAML == JSON byte-equivalence (the merge_extracts.py assert at the bottom)
4. Update the validation report with the reconcile decisions + commit SHA

**Phase 4 EXIT CHECK**:

- [ ] User approval recorded for every reconcile change
- [ ] All extract-*.yaml edits made via Edit tool (never bypass extracts)
- [ ] All three regenerators ran without error
- [ ] YAML == JSON verified by `merge_extracts.py`
- [ ] No Pine source files deleted (prior versions ALWAYS preserved per Anish 2026-05-10 directive)
- [ ] Git status shows expected file changes only

## Multi-agent orchestration

Dispatch SUBAGENTS when the work parallelizes cleanly. Each subagent has a narrow brief and a fixed output schema. The parent agent merges results.

See `references/multi-agent-orchestration.md` for the prompt templates. Briefly:

| Phase | Subagent role | When | Count |
|---|---|---|---|
| 1 ENUMERATE | "Grep one Pine file for target occurrences" | ≥4 distinct Pine files | one per Pine file |
| 2 STATIC-DIFF | "Diff one pair of locations" | ≥6 pairs to diff | one per pair (cap at 12; if more, batch into groups of 3 pairs per subagent) |
| 3 TV-FIRING | "Query Path A logger labels for one location" | when ≥4 locations and a TV MCP is connected | one per location |
| 4 RECONCILE | (parent only — single-threaded by design) | n/a | 0 |

Subagent contract — every subagent MUST:

1. Receive: target name + canonical form + one specific input (file / pair / location)
2. Return: a structured JSON-or-YAML chunk that follows the per-phase schema
3. Never modify any file (read-only)
4. Never escalate; only the parent calls the user

## When to ask the user vs proceed autonomously

**ALWAYS ASK** (skill must not proceed):

- Phase 2 finds `semantic drift` between locations — present the diff side-by-side, ask which is canonical
- Phase 3 reveals fire-bar disagreement on a significant fraction of bars (>5% of agreement-set size)
- Phase 4 reconcile involves Pine source rename, file deletion, or filename change
- Cross-condition check returns zero historical fires — could be impossible (bug) or rare (real); user calls it
- Any decision involving a CHANGELOG-documented canonical designation

**PROCEED AUTONOMOUSLY**:

- Phase 2 `identical` / `cosmetic-drift` / `IPSF default variation` verdicts (record in report, no edit needed)
- Phase 3 100% agreement-set (all locations fire on identical bars) — report and move on
- Phase 4 `IPSF asymmetry` flagged with the `add input.*` recommendation (only if user has standing approval per `UNLIMITED_APPROVAL.md`)
- Pure regen runs (merge_extracts → build_lineage_cards → build_docs) — no Pine touched

## When validation is COMPLETE

A target's validation is complete when:

1. Phase 1 EXIT CHECK passes
2. Phase 2 EXIT CHECK passes
3. Phase 3 EXIT CHECK passes (or Phase 3 BLOCKED is acknowledged by user)
4. Phase 4 EXIT CHECK passes (no findings to act on, or all findings acted on with user approval)
5. The validation report at `docs/validation/<date>-<target>.md` is committed
6. PR comment posted summarizing the verdict

If any EXIT CHECK fails, the validation is INCOMPLETE. Re-run the failed phase before declaring done.

## Pointer files

The skill's working knowledge lives in:

- `references/4-phase-procedure.md` — detailed walkthrough of every phase
- `references/multi-agent-orchestration.md` — subagent prompt templates
- `references/pine-grep-patterns.md` — canonical search patterns for enumeration
- `references/ipsf-vs-true-drift.md` — the classification taxonomy
- `references/path-a-logger-usage.md` — Path A logger query workflow
- `references/python-port-usage.md` — Phase M pipeline workflow
- `references/cross-condition.md` — two-target same-candle analysis
- `references/failure-modes.md` — known traps + mitigations
- `templates/validation-report.md` — the standard output shape
- `templates/enumeration-table.md` — Phase 1 output
- `templates/drift-finding.md` — Phase 2 finding entry
- `templates/canonical-decision.md` — Phase 4 reconcile proposal
- `templates/cross-condition-check.md` — two-target intersection report

## Known failure modes

See `references/failure-modes.md` for the full table. The most common:

| Symptom | Likely cause | Where to look |
|---|---|---|
| Phase 1 finds 0 occurrences | Target name has unexpected punctuation or is a colloquial alias | `docs/glossary.md` aliases section; ask user for source name |
| Phase 2 says "identical" but fire bars differ | Internal-helper drift (Supertrend / Zoo / ATR helpers) under same boolean name | Re-Phase-1 with the helper names; diff those too |
| Phase 3 Path A returns 0 labels | Logger Pine not loaded on chart, or `input.source(...)` pointed at the wrong plot | `references/path-a-logger-usage.md` § Troubleshooting |
| Phase 3 Path B returns 0 fires | Stateful composite + per-call state reset (Phase M limitation) | Fall back to Path A; flag for Phase M Phase-2 work |
| Phase 4 regen fails YAML==JSON | Stale YAML in `data/` not refreshed from extracts | `python3 tools/merge_extracts.py` then retry |
| Reconcile changes lost on next session | Edited `data/indicators.yaml` directly instead of `bible-input/extract-*.yaml` | Always edit the SOURCE; let merge_extracts.py produce the derived YAML |

## Skill versioning

This skill itself is versioned. See `CHANGELOG.md` in this directory. When the procedure changes, bump the version and document the change. Re-run any in-flight validation under the new version if the change is procedural (not cosmetic).
