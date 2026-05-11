---
name: inversion
description: Munger's "invert, always invert." Instead of asking how to succeed, ask what guarantees failure — then systematically avoid those things. Produces a list of "never do" rules that override every other consideration. Owner-tier skill. Outputs are appended to STANDING_DECISIONS.md when canonicalized as SD-N inversion rules.
when_to_use: Invoke at strategy review time after krishna-steelman + shiva-redteam + premortem have run. Also invoke when a premortem identifies a recurring failure mode (across multiple premortems) — that's a candidate for an inversion rule. The inversion skill is the formalization step.
tier: owner
---

# Inversion

**Tier**: owner (strategic stewardship; codifies "never do" rules into the SD ledger).

**Purpose**: Charlie Munger's discipline. Invert always invert. The skill that takes "what guarantees failure?" and produces a clean, scoped, enforceable "never do" rule. Each rule has a violation detector and an escalation path.

## Existing inversion rules in the SD ledger

These already exist in `docs/agentic-os/STANDING_DECISIONS.md`. The inversion skill is the discipline that produces more of them.

- **SD-002 inversion**: Never modify a Pine source file. Always new-version.
- **SD-004 inversion**: Never delete a file. Renames, moves, overwrites also forbidden.
- **SD-001 inversion**: Never include phantom-toggle plots in canonical scope.
- **SD-011 inversion (pending)**: Never tabulate concurrent fires on the alert bar. Always use the visual bar.

## Input

```yaml
target:
  type: strategy_review | recurring_premortem_fm | standing_decision_authoring
  identifier: <e.g. "PBJ Bull adoption" or "FM-7 from 2026-05-11 premortem">
  context:
    krishna_output: <ref>
    shiva_output: <ref>
    premortem_output: <ref>
    recurring_failure_modes: <list of FMs seen across N premortems>
```

## Output

```yaml
inversion:
  rule_id: SD-NNN  # the next SD number to claim
  rule_statement: "Never <do X> when <conditions>."
  scope:
    - applies_to: <list of plots, families, or contexts>
    - excludes: <explicit exclusions if any>
  rationale: <one-paragraph why this rule reduces ruin>
  violation_detector:
    - <concrete check that fires if rule is violated>
    - <e.g. "If a Plot Owner emits a fire when bar.session_position == 'pre_market' AND plot ∈ {PBJ Bull, RVOL 1x} → violation">
  escalation_path:
    - on_violation: <who is paged, what is logged>
  empirical_evidence:
    - <links to failure cases observed; or "novel — no observed cases yet">
  override_conditions: <list — typically empty; inversions are unconditional by design>
```

## Procedure

1. **Identify the failure-guarantor.** From Shiva + premortem + recurring patterns, find the specific behavior that — if performed — guarantees failure with high probability. The rule will codify "do not do this."
2. **Phrase as "never X when Y."** Concrete, scoped, enforceable. Bad: "be careful in volatile markets." Good: "Never enter PBJ Bull at session_position=open_30 when 5-bar realized volatility > 3x trailing 30-day average."
3. **Define the violation detector.** A boolean check the system can run automatically. If it's not automatable, the rule isn't enforceable — sharpen until it is.
4. **Define the escalation path.** What happens on violation. Typically: log to `docs/agentic-os/violations/<date>.md`, page Anish if severity-critical, halt the offending agent until human review.
5. **Cite empirical evidence if available.** A list of past failure cases the rule would have prevented. If novel, say so.
6. **Override conditions are by default EMPTY.** Inversions are unconditional. If you find yourself listing exceptions, the rule isn't fundamental enough — rethink.
7. **Claim the next SD number.** Append to `docs/agentic-os/STANDING_DECISIONS.md` per the existing format. Cross-reference SD-002 (always-new-version) for the inversion's own meta-discipline.

## Hard rules

- Inversions are UNCONDITIONAL. If a rule has exceptions, it isn't an inversion — it's guidance.
- Inversions are AUTOMATABLE. If the violation can't be detected by code, the rule isn't enforceable.
- Inversions are APPEND-ONLY. SD entries never get edited (per SD-002).
- Inversions override every other consideration including Pareto leverage. A plot that scores in the top 20% Pareto STILL doesn't fire if it would violate an inversion rule.

## Cross-references

- Pillar definition: `docs/agentic-os/strategy/2026-05-11-agentic-os-full-build-spec.html` §2 Pillar 5.
- Reads from: `shiva-redteam`, `premortem`, the SD ledger.
- Writes to: `docs/agentic-os/STANDING_DECISIONS.md` (append-only).
- Enforced at: pre-fire gate in the per-fire chain — before `detection-plot-diagnosis` is invoked.
- Munger source: "Invert, always invert" — Berkshire Hathaway letters and lectures.
