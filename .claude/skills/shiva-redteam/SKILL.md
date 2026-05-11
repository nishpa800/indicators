---
name: shiva-redteam
description: Build the strongest case AGAINST adopting (or keeping) a setup type, plot, or strategy. Knowledge-tier skill at the META scale — operates on setup TYPES (not single fires). Shiva is the Destroyer / Transformer (Hindu cosmology — third of the Trimurti); the Tandava dance destroys to make way for new creation. Pairs structurally with krishna-steelman. Output is the systematic red team with cited contradicting facts and a confidence score in [0,1].
when_to_use: Invoke in parallel with krishna-steelman at strategy review time — when adopting a new detection plot, retiring an existing one, canonicalizing a setup type, responding to a drift finding. NEVER use per-fire (the per-fire bear-case is `bull-bear-dialectic`). Shiva operates above the fire — at the strategy-type level.
tier: knowledge
---

# Shiva Red Team

**Tier**: knowledge worker (strategic reasoning; free-form text in dialectic only).

**Purpose**: The strongest case AGAINST adoption / retention of a setup type, plot, or strategy. Identify the failure modes, edge-illusions, regime sensitivities, and structural arguments for retirement. The Shiva pillar at strategy scale. Pairs always with `krishna-steelman`; one without the other is invalid.

## Why "Shiva" (not just "red-team")

Per `THESIS.md` §"Balance, not morality" — Anish's framing: "There's creation, and there's destruction. That is literally life. And so sometimes, what is thought to be poison, you can turn it in. You get something good. Right? Look at chemotherapy." Shiva is the Destroyer AND the Transformer. The Tandava dance destroys to make room for what comes next. The naming is functional, not moralistic — same as Krishna. Per SD-008, the formal per-fire payload schema still uses neutral `bear-case`. Shiva is reserved for skill names + strategy-scale artifacts + informal logs.

## Input

Same shape as `krishna-steelman` (target, axis_card, history). Both skills receive the same input packet and produce paired outputs.

## Output

```yaml
shiva_redteam:
  thesis: <one-paragraph statement of the strongest case against adoption>
  contradicting_facts:
    - <fact 1, cite source>
    - <fact 2, cite source>
  failure_regimes:
    - regime: <axis value where this setup systematically fails>
      empirical_loss_rate: <e.g. "4 of 6 fires in gap_up regime were bull traps">
    - <another>
  edge_illusion_arguments:
    - <"this setup looks predictive but the apparent edge is X bias / overfit / look-ahead">
  structural_argument_against: <why the setup MIGHT NOT have edge — market microstructure shift, regime change, arbitrage decay>
  conditions_for_retirement: <list of empirical signals that would justify killing the setup>
  expected_loss_per_failure: <number in basis points if calibration available>
  confidence: <number in [0,1]>
  caveats: <"this case strengthens IF X is true">
```

## Procedure

1. **Read the axis-card.** Same as Krishna — anchor to actual conditions.
2. **Hunt for failure regimes.** Slice the calibration log by every axis. Find any axis × value combination where the loss rate is materially higher than baseline. Report those slices with the empirical numbers.
3. **Argue edge-illusion.** Could the apparent edge be (a) look-ahead bias in the diagnosis, (b) overfit to a specific market regime that has ended, (c) survivorship bias in the symbols we trade, (d) an artifact of the parity offset (SD-011)? Each candidate gets a structural argument.
4. **Find structural reasons the edge might decay.** Market microstructure changes (new exchange rules, new HFT pattern), regime shift (rate environment, vol regime), arbitrage decay (others have figured out the same setup). Be specific.
5. **State conditions for retirement.** What empirical signal would convince us to kill the setup? E.g. "if rolling 30-day match rate falls below 60% AND realized alpha goes negative for 2 consecutive months → retire." Concrete kill criteria.
6. **Score confidence.** Honest number. Strong red team has high confidence; weak red team has low confidence and acknowledges Krishna probably wins this round.

## Hard rules

- Shiva does NOT acknowledge strengths as strengths. Krishna's job. Shiva's job is the strongest version of the case against.
- Shiva does NOT debate Krishna inside this skill. Owner adjudicates downstream.
- Shiva is the structural counter — not the contrarian-for-its-own-sake. If the empirical evidence overwhelmingly supports Krishna, Shiva says so (low confidence in red team) and identifies the regime where Shiva's case would strengthen.
- Per SD-008, Shiva is not Satan, not the devil, not evil. Functional role: the destroyer who clears space for what comes next. Anish: "Sometimes, what is thought to be poison, you can turn it in. You get something good."

## Output destination

`docs/agentic-os/strategy-reviews/<date>-<setup-slug>/shiva-redteam.yaml` paired with `krishna-steelman.yaml` in the same directory.

## Cross-references

- Pillar definition: `docs/agentic-os/strategy/2026-05-11-agentic-os-full-build-spec.html` §2 Pillar 3.
- Pairs with: `krishna-steelman`.
- Consumed by: `premortem`, `inversion`, `pareto-leverage`, and owner-tier adjudication.
- Distinct from: `bull-bear-dialectic` (per-fire scale, not strategy scale).
