# Reference: known failure modes

Things that have actually gone wrong (or could go wrong) during validation. Read this BEFORE invoking the skill so you don't repeat the mistakes.

## Phase 1 — ENUMERATE failures

### F1.1 — Zero occurrences found, but the target obviously exists

**Symptom**: grep returns nothing. User insists the target is real.

**Causes**:
- Target name is a colloquial alias (e.g. "UC" for `UNIFIED_COMBO_BULL`)
- Punctuation difference (`SUPER_DUPER` vs `SDUPER` vs `SUPERDUPER`)
- Target lives in a Pine file the bible doesn't know about (check Anish's iCloud "Master Directory")
- Target is only defined inside a multi-line expression (line continuation hides the assignment from a line-scoped grep)

**Mitigation**:
- Resolve aliases via `docs/glossary.md` and `docs/redundancy.md` BEFORE grepping
- Use `rg -A 5 -B 2` (ripgrep with context) when grep fails — line continuations may be a few lines above/below
- ASK THE USER for the exact Pine variable name if the alias set is empty

### F1.2 — Found in YAML but not in Pine

**Symptom**: `data/indicators.yaml` lists the target with a line range; Pine file at that line range has different content (or no occurrence at all).

**Causes**:
- Bible extraction is stale (a Pine source was updated after extraction)
- The line range YAML was hand-edited and is wrong
- Filename in the YAML doesn't match the actual file (e.g. before the Stage 6.4 rename revert)

**Mitigation**:
- Flag as "orphan in YAML" — Phase 1 EXIT CHECK includes this
- Trigger a Stage 8 re-extraction for the affected indicator
- Don't silently delete YAML rows; they may point at content that moved

### F1.3 — Found in Pine but not in YAML

**Symptom**: Pine file has DEFINITION; `data/indicators.yaml` has no record.

**Causes**:
- Pine source was added/updated post-Stage-1 extraction
- Bible extraction missed it (agent error)

**Mitigation**:
- Flag as "missing from YAML" — Phase 1 EXIT CHECK includes this
- Add the missing record during Phase 4 reconcile (after user confirms it's intentional)

---

## Phase 2 — STATIC-DIFF failures

### F2.1 — Verdict `identical` but fire bars differ (Phase 3 reveals)

**Symptom**: Phase 2 says two locations are identical; Phase 3 shows they fire on different bars.

**Cause**: Internal-helper drift hidden under same boolean name. E.g. both DEFINITIONs are `b1 = h1 AND h2`, but `h1` (Supertrend / Zoo / ATR) has diverged between the two indicators.

**Mitigation**:
- Phase 2 normalization MUST include immediate helper variables (per `references/4-phase-procedure.md § Phase 2 step 1`)
- If helpers diverge, the verdict should be `semantic-drift` not `identical`
- Re-Phase-1 the helper names and Phase-2 those too

### F2.2 — Multi-line boolean truncated

**Symptom**: Phase 2 extracts only the first line of a multi-line DEFINITION; diff is wrong because half the expression is missing.

**Cause**: Subagent grabbed only the line at the cited line number, not the full continuation.

**Mitigation**:
- The grep harness in `references/pine-grep-patterns.md` records FULL LINE RANGES (e.g. `L78-L82`), not single lines
- Phase 2 subagents read the full range, not just one line
- If line range is `L78` (single line) but the boolean continues, re-extract with `L78-<next-blank-or-non-continuation>`

### F2.3 — Pine operator precedence ambiguity

**Symptom**: Two locations LOOK the same but parse differently in Pine.

**Example**: `a and b or c` parses as `(a and b) or c` in Pine. If one location parenthesizes and the other doesn't, the normalized form should still be `(a and b) or c` — they're equal. But `a or b and c` parses as `a or (b and c)` — different!

**Mitigation**:
- Phase 2 normalization step 2 includes "fully parenthesize per Pine's precedence" before diff
- If the post-parenthesization differs, it's semantic drift

---

## Phase 3 — TV-FIRING failures

### F3.1 — Logger returns zero labels

**Symptom**: Path A query returns empty fire-bar list.

**Causes**: see `references/path-a-logger-usage.md § Troubleshooting`.

### F3.2 — Path B returns zero on stateful composite

**Symptom**: `phase_m_run.py` returns zero fires for a composite Anish swears fires regularly on chart.

**Cause**: Phase M state-threading limitation. Documented in the Stage 7.5-7.8c handoff comment.

**Mitigation**:
- Fall back to Path A
- If Path A is also unavailable, write "Phase 3 BLOCKED — stateful composite + Phase M limitation; manual TV verification required" in the report; user pastes timestamps back

### F3.3 — Fire bars between Path A and Path B disagree

**Symptom**: Path A shows N fires; Path B shows M fires; N ≠ M.

**Causes**:
- Stateful composite (Path B returns zero)
- Logger `input.source()` pointed at wrong plot
- Path B has a port bug (bench test against Path A)

**Mitigation**:
- Trust Path A as chart-truth
- If discrepancy is large, file a Path-B port bug in `realtime-indicators`
- For the validation report, log both counts and the discrepancy

---

## Phase 4 — RECONCILE failures

### F4.1 — User edits `data/indicators.yaml` directly; changes lost on next merge

**Symptom**: Reconcile changes applied to `data/indicators.yaml` are gone after the next `merge_extracts.py` run.

**Cause**: `data/indicators.yaml` is GENERATED from `bible-input/extract-*.yaml`. Edits to the generated file are overwritten.

**Mitigation**:
- Phase 4 procedure MUST edit `bible-input/extract-<family>.yaml` (the source)
- Then run `merge_extracts.py` to regenerate `data/indicators.yaml`
- This is enforced by the procedure; subagents only return proposals, parent applies them via Edit to the SOURCE

### F4.2 — Regen succeeds but YAML != JSON

**Symptom**: After `merge_extracts.py`, the JSON and YAML don't match.

**Cause**: shouldn't happen — `merge_extracts.py` includes the byte-equivalence assert. If it does, there's a bug in `merge_extracts.py` (e.g. non-deterministic key ordering).

**Mitigation**:
- The assert at the bottom of `merge_extracts.py` blocks the script from completing on mismatch
- If it ever does mismatch, file a bug; rollback the extract edit

### F4.3 — Pine source rename breaks downstream consumers

**Symptom**: User approves renaming a Pine variable (e.g. `anyBearPent` → `anyBearPenthouse`); downstream consumers in other indicators that grep'd the old name break.

**Cause**: Pine source is essentially copy-paste-coupled across indicators. Renaming one without updating all consumers leaves the consumers referencing an undefined symbol.

**Mitigation**:
- Before approving a Pine rename: ENUMERATE all REFERENCE occurrences (Pattern 2 in `references/pine-grep-patterns.md`)
- Update consumers in the SAME commit as the rename
- Test compile on TradingView before promoting

### F4.4 — Pre-existing file deleted

**Symptom**: A Pine version file is gone after Phase 4.

**Cause**: violated the "prior versions stay" guardrail.

**Mitigation**:
- Phase 4 EXIT CHECK includes "No Pine source files deleted"
- Recovery: `git log --diff-filter=D` to find the deletion commit; `git revert` or restore from history
- This is a HARD guardrail per Anish 2026-05-10. Never delete prior versions.

---

## Procedural failures

### P1 — Two subagents return inconsistent verdicts on the "same" pair

**Symptom**: subagent A says `cosmetic-drift`; subagent B (re-run on the same pair) says `identical`.

**Cause**: subagent improvised; didn't follow `references/ipsf-vs-true-drift.md`.

**Mitigation**:
- The decision tree in `references/ipsf-vs-true-drift.md` is deterministic; if applied correctly, two subagents on the same input give the same verdict
- If they don't, file a procedural issue against the skill (CHANGELOG.md bump)
- Investigate which subagent deviated; the parent retains the deterministic-per-procedure verdict

### P2 — Skill invoked for non-validation task

**Symptom**: User says "tell me about X"; skill kicks off a full 4-phase validation.

**Cause**: skill description in SKILL.md frontmatter matches too broadly.

**Mitigation**:
- The "When to invoke" section in `SKILL.md` includes counter-examples
- If you find yourself running the procedure on a non-validation request, stop and ask the user "do you want a validation run or just information?"

### P3 — Cross-condition check requested without per-target validations

**Symptom**: User says "X and Y on same candle"; parent agent jumps straight to intersection without running per-target validations.

**Cause**: skipping Phase 1 + 2 + 3 for X and Y before intersecting.

**Mitigation**:
- `references/cross-condition.md` Step 1 is non-negotiable: per-target validation FIRST
- The intersection is meaningless without confidence in each side's fire-bar set
