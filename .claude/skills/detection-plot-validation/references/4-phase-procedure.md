# Reference: the four-phase procedure (detailed)

Companion to `SKILL.md`. Open whichever phase you're working on; do not skip steps; do not invent steps not listed here. If you find the procedure doesn't fit a specific target, **stop, document the gap in the validation report, and ask the user** — do not improvise. Improvisation across multiple agents produces incomparable reports.

---

## Phase 1 — ENUMERATE

### Inputs (load before you start)

- `bible-input/MANIFEST.md` — canonical Pine file per indicator family
- `data/indicators.yaml` — current bible YAML (read as a flat record set; ignore the `indicators:` nesting and walk the flat `roots:` + `composites:` arrays at the top)
- `docs/redundancy.md` — known name collisions
- The target's name AND any aliases the user mentioned

### Steps

1. **Resolve aliases.** If the user said "Unified Combo" find every canonical form: `UNIFIED_COMBO_BULL`, `UNIFIED_COMBO_BEAR`, `csNew3_Bull`, `csNew3_Bear`, `UC`, `unified_combo`. Build the full alias set BEFORE you start grepping.

2. **Grep every canonical Pine file** for every alias. Use `references/pine-grep-patterns.md` — it has the canonical search patterns for: definition lines (`= <expr>`), reference lines (`<name>` as operand), input declarations (`input.bool("Show <name>", ...)`), alertconditions, plotshapes, comments. Capture ALL six kinds.

3. **Classify each occurrence** as one of:
   - `DEFINITION` — boolean / state assignment (`var sigX = ...` or `bool sigX = ...`)
   - `REFERENCE` — used in another expression (`anyBull = sigX or sigY`)
   - `INPUT` — exposed as Pine input (`show_X = input.bool(...)`)
   - `PLOT` — plotshape / plot / plotchar
   - `ALERT` — alertcondition / alert()
   - `COMMENT` — mentioned in a `//` comment only (no logic)

4. **Cross-check against `data/indicators.yaml`**:
   - For each YAML record matching the target (across both `roots:` and `composites:`), verify the YAML's `pine_source_line_range:` is within ±5 lines of the Pine occurrence
   - List orphans (YAML records with no Pine match)
   - List missings (Pine occurrences with no YAML match)

5. **Emit the enumeration table** per `templates/enumeration-table.md`. One row per DEFINITION occurrence. Include all 6 classification types in a separate "other occurrences" section.

### Cross-checks before exiting Phase 1

- Every alias resolved
- Every Pine file under `*/versions/*.pine` searched
- Every occurrence classified
- Orphans / missings explicitly listed (zero or N — never blank)

### Exit artifact

The Phase-1 enumeration table embedded in the validation report under `## Phase 1 — Enumeration`.

---

## Phase 2 — STATIC-DIFF

### Inputs

- Phase 1 enumeration table
- The Pine source at every DEFINITION location

### Steps

1. **For each DEFINITION**, extract:
   - The full boolean assignment line (LHS + `=` + RHS)
   - Any helper variables the RHS references (recurse one level deep into the immediate helpers — do not recurse further; you'll lose signal in noise)
   - Any IPSF inputs the RHS gates on (`input.bool / input.int / input.float / input.string / input.source`)

2. **Normalize** each captured boolean:
   - Strip Pine line continuations / multi-line breaks
   - Alpha-rename variables to a canonical scheme: `b1` = first bool operand, `b2` = second, `i1` = first input, `h1` = first helper
   - Collapse whitespace
   - Lowercase identifiers (Pine is case-insensitive for compiler purposes but humans mix cases)

3. **Diff pairwise.** For N DEFINITION locations, run `N*(N-1)/2` diffs. If N > 4, the count grows (N=5 → 10 diffs; N=6 → 15). Use multi-agent orchestration (one subagent per pair or per batch of 3 pairs).

4. **Classify each pair** using `references/ipsf-vs-true-drift.md`:
   - `identical` — diff is empty after normalization
   - `cosmetic-drift` — variable names differ but expression structure (operators + operand types + shift indices) is identical
   - `IPSF default variation` — both operands are `input.*`; only the numeric defaults differ
   - `IPSF asymmetry` — same parameter is `input.*` in one location, hardcoded in another
   - `semantic drift` — operators, operand sets, or shift indices differ

5. **For every classification that isn't `identical`**, emit a drift-finding artifact per `templates/drift-finding.md`.

### Cross-checks before exiting Phase 2

- Every pair classified (no blank verdicts; if you can't classify, ESCALATE TO USER)
- Every classification cites Pine line ranges
- Every non-`identical` finding has a drift-finding artifact

### Exit artifact

The Phase-2 pairwise classification table in the validation report under `## Phase 2 — Static diff`.

---

## Phase 3 — TV-FIRING

### Inputs

- Phase 1 enumeration table (DEFINITION locations)
- The target's plot offset (from `data/indicators.yaml`)
- Either: TradingView MCP connection + Path A logger Pines, OR: realtime-indicators repo + Phase M pipeline, OR: nothing (manual fallback)

### Path selection

- **Path A** preferred if: TV MCP connected AND Path A logger Pines exist for the target's indicator(s). See `references/path-a-logger-usage.md`.
- **Path B** if: Path A unavailable AND the target's Pine is replicated in `realtime-indicators/rti/signals/`. See `references/python-port-usage.md`. **Skip Path B for stateful composites** — Phase M pipeline currently re-instantiates state per `detect()` call.
- **Manual** if: neither available. Write a "Phase 3 BLOCKED" section in the report; user runs the chart-side check and pastes timestamps back.

### Steps (Path A)

1. For each DEFINITION location, identify the Path A logger that captures it
2. Query the logger via `data_get_pine_labels` (MCP)
3. Collect the fire-bar set (list of `{timestamp, bar_index, symbol, timeframe}` tuples) per DEFINITION

### Steps (Path B)

1. Run `realtime-indicators/scripts/phase_m_run.py --target=<canonical-name> --pack=<pack-name>` (or equivalent — see `references/python-port-usage.md`)
2. Output is fire bars per location

### Compute the bar-set algebra

1. **Agreement set** = bars where EVERY DEFINITION location fired
2. **Drift set** = bars where SOME but not all locations fired
3. For each drift bar: identify which locations fired vs not; mark which is "incorrect" per the canonical (if Phase 4 has been pre-decided) or flag for user

### Top-down diagnosis for every drift bar

Walk the lineage card at `docs/lineage/<target-slug>.md` from top to bottom:

1. Top-level composite — did it fire? If not, walk to children
2. Each tier-N child — did it fire? Check its offset cascade
3. Eventually reach the root that didn't fire — that's the failing leaf
4. Diagnose: `offset cascade` / `parameter drift` / `internal helper drift` / `namespace collision`

See `docs/sop/composite-validation.md` and `docs/sop/offset-triage.md` for the canonical procedures.

### Cross-checks before exiting Phase 3

- Fire-bar set captured per location (or Phase 3 BLOCKED documented + user notified)
- Agreement + drift sets computed
- Every drift bar diagnosed

### Exit artifact

Phase-3 firing comparison table in validation report under `## Phase 3 — TV firing`.

---

## Phase 4 — RECONCILE

### Inputs

- Phase 2 drift findings
- Phase 3 drift bars
- User's standing approval status (per `UNLIMITED_APPROVAL.md` if applicable)

### Steps

1. **Build a reconcile proposal** per `templates/canonical-decision.md`. For each finding, propose ONE of:
   - `canonical: <provenance>` — designate this implementation as canonical
   - `alias-of: <canonical>` — mark as alias in YAML
   - `variant-of: <canonical>` — mark as variant (e.g. stripped variant)
   - `rename: <from> → <to>` — Pine source rename (requires user)
   - `add-input: <param>` — promote hardcoded to `input.*` (requires user)
   - `no-action` — document and move on

2. **Present the proposal to the user** unless every proposed change is in the "PROCEED AUTONOMOUSLY" set per `SKILL.md` § "When to ask the user".

3. **After user approves**:
   - Edit `bible-input/extract-<family>.yaml` (THE SOURCE) — never `data/indicators.yaml` directly
   - Run `python3 tools/merge_extracts.py` (regen YAML + JSON)
   - Run `python3 tools/build_lineage_cards.py` (regen lineage cards)
   - Run `python3 tools/build_docs.py` (regen the human docs)
   - Verify YAML == JSON byte-equivalence (the assert at the bottom of `merge_extracts.py`)

4. **Update the validation report** with the reconcile decisions + git commit SHA after pushing.

### Hard guardrails (never violate)

- Never delete a Pine version file. All prior versions stay (Anish 2026-05-10 directive).
- Never modify Pine source without explicit user approval per request.
- Never bypass `bible-input/extract-*.yaml` and edit `data/indicators.yaml` directly.
- Never commit without verifying YAML == JSON.

### Exit artifact

Phase-4 reconcile section in validation report under `## Phase 4 — Reconcile`. Includes: proposal table + user approval timestamps + commit SHA.

---

## Cross-condition variant (when user asks "X and Y on same candle")

Run Phase 1 + Phase 2 + Phase 3 for X and for Y INDEPENDENTLY first. Then in a separate "Cross-condition" section of the validation report:

1. Compute fire-bar intersection (X-fire-set ∩ Y-fire-set)
2. List the intersection bars with timestamp + symbol + timeframe
3. For each intersection bar: characterize what happened (which preceding bars led into both X and Y firing; was it a rare event or a regularly co-occurring pair?)
4. If the intersection is empty: confirm with user whether that's expected (impossible by definition) or a bug (should fire but never does)

See `references/cross-condition.md` for the full workflow.
