# detection-plot-validation — CHANGELOG

Skill version history. Bump on any procedural change. Re-run in-flight validations under the new version if the change is procedural (not cosmetic).

## v1.1.0 — 2026-05-10

Anish-directive update: TV-firing autonomy + standing approval embedded.

- **Phase 3 Path A removed from this skill.** Path A (chart-side TV MCP queries) required Anish at his desk — incompatible with the "never block on Anish while he's at work" directive. Moved to the new `detection-plot-tv-firing` skill in `.claude/skills/detection-plot-tv-firing/`.
- **Phase 3 in this skill is now Path B only**. If Path B is unavailable (target not in any Python port pack) OR stateful-blocked (returns zero), mark Phase 3 `BLOCKED-NEEDS-TV-FIRING-SKILL` and CONTINUE to Phase 4 with Phase-2 static findings only. Never pause.
- **`STANDING_APPROVAL.md` added inside the skill.** Embeds Anish's unlimited approval verbatim. Every agent invocation of the skill loads it. Hard guardrails reduced to 4: file deletion, DB drop, rate-limited APIs >100/5min, mass Pine renames.
- **Phase 4 reconcile is now autonomous for `semantic-drift` too**: instead of pausing for canonical decision, the skill creates a NEW versioned file in the affected indicator's `versions/` directory documenting both implementations; updates `extract-*.yaml` with `variant_of:` relationships; commits + pushes. Anish reviews the documented finding later. **No more validation pauses**.
- **Version-control mantra enforced**: never rename, never delete; always add a new versioned file. CHANGELOG documents what changed.

## v1.0.0 — 2026-05-10

Initial release.

- Four-phase procedure (`ENUMERATE → STATIC-DIFF → TV-FIRING → RECONCILE`) with explicit EXIT CHECKS per phase.
- Multi-agent orchestration pattern: one subagent per Pine file (Phase 1), one per diff pair (Phase 2), one per location for Path A logger queries (Phase 3). Reconcile is single-threaded.
- IPSF vs TRUE DRIFT classification taxonomy (`identical / cosmetic-drift / IPSF default variation / IPSF asymmetry / semantic drift`).
- Two TV-firing paths: Path A (logger Pines on TradingView) primary; Path B (Python ports / Phase M pipeline) secondary with stateful-composite caveat.
- Cross-condition check (two targets on same candle) supported via `references/cross-condition.md`.
- Hard guardrail: never modify Pine source without explicit user approval; always preserve prior versions.
- Reconcile path: `bible-input/extract-*.yaml` → `merge_extracts.py` → `build_lineage_cards.py` → `build_docs.py`. Never edit `data/indicators.yaml` directly.
- Fixed output shape: `docs/validation/<date>-<target>.md` per run.

## Future change candidates (not yet shipped)

- v1.1: integrate hooks (PostToolUse on extract-*.yaml writes auto-regen; PreToolUse on commit YAML==JSON guard) — see `docs/HOOKS_PROPOSAL.md` (INFRA 5).
- v1.2: native MCP tool for Path A logger queries (currently described in references; not codified).
- v1.3: per-target validation cache (re-running validation on an unchanged target uses cached report unless YAML hash changed).
- v1.4: report aggregator (`tools/validation_aggregate.py`) — produces a "rolled-up" report across many `docs/validation/*.md` files for periodic suite-wide audits.
