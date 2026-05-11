# detection-plot-validation — CHANGELOG

Skill version history. Bump on any procedural change. Re-run in-flight validations under the new version if the change is procedural (not cosmetic).

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
