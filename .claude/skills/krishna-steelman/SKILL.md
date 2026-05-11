---
name: krishna-steelman
description: Build the strongest, most generous, most strategically-coherent case FOR adopting (or keeping) a setup type, plot, or strategy. Knowledge-tier skill at the META scale — operates on setup TYPES (not single fires). Krishna is the Preserver (Hindu cosmology — eighth avatar of Vishnu); the strategist who sees through illusion to the long game. Pairs structurally with shiva-redteam. Output is a steelman argument with cited supporting facts and a confidence score in [0,1].
when_to_use: Invoke at strategy review time — when adopting a new detection plot into the book, when deciding whether to keep an existing plot, when canonicalizing a setup type, when responding to a drift finding that calls a plot's existence into question. NEVER use per-fire; the per-fire bull-case is `bull-bear-dialectic`. Krishna operates above the fire — at the strategy-type level.
tier: knowledge
---

# Krishna Steelman

**Tier**: knowledge worker (strategic reasoning; free-form text in dialectic only).

**Purpose**: The strongest possible case FOR adoption / retention of a setup type, plot, or strategy. The Krishna pillar at strategy scale. Pairs always with `shiva-redteam`; one without the other is invalid.

## Why "Krishna" (not just "steelman")

Per `docs/agentic-os/THESIS.md` §"Balance, not morality" — and Anish's directive 2026-05-11 to use the Krishna / Shiva framing for the META-dialectic (above per-fire bull/bear). Krishna in Hindu cosmology is the Preserver (eighth avatar of Vishnu), the strategist who delivered the Bhagavad Gita on the battlefield of Kurukshetra. He is the long-game player, the seer-through-illusion. The naming is functional, not moralistic — same as Shiva. Per SD-008, the formal per-fire payload schema still uses neutral `bull-case` / `bear-case`. Krishna / Shiva is reserved for skill names + strategy-scale artifacts + informal logs.

## Input

```yaml
target:
  type: new_plot | existing_plot | setup_type | strategy_change
  identifier: <e.g. "PBJ Bull on equities at open" or "deprecate B2B PUP S-7 variant">
  axis_card: <output of axis-decomposition skill>
  history:
    n_fires_observed: <int>
    realized_alpha_summary: <statistics from calibration log if available>
    calibration_table: <past 4-square distribution if available>
```

## Output

```yaml
krishna_steelman:
  thesis: <one-paragraph statement of the strongest case for adoption>
  supporting_facts:
    - <fact 1, cite source>
    - <fact 2, cite source>
    - <fact 3, cite source>
  long_run_analogues:
    - <historical example where this setup type produced alpha>
    - <another>
  structural_argument: <why the setup type EXISTS structurally — what market microstructure, behavioral, or arbitrage logic underlies it>
  required_conditions: <list of axis values that must be present for this setup to have edge>
  expected_alpha_per_fire: <number in basis points if calibration data exists; "unknown" if not>
  confidence: <number in [0,1]>
  caveats: <list — but framed as "this case still holds IF X is true">
```

## Procedure

1. **Read the axis-card.** This anchors the steelman to the actual conditions under which the setup operates. Do not handwave.
2. **Cite calibration data first.** If the setup has fired N times with logged outcomes, lead with that. The strongest case is empirical. If N is small, say so and weight accordingly.
3. **Articulate the structural reason for edge.** Market microstructure (order book imbalance), behavioral (FOMO at HV1000), arbitrage (cross-venue lag) — what is the WHY the setup has edge? Hand-waving here forfeits the steelman; we want the real structural argument.
4. **Find long-run analogues.** Pre-2026 examples. If no analogue exists, say so — that's a Shiva point, not a Krishna point, but acknowledging it strengthens the steelman.
5. **State required conditions.** "This setup has edge IFF (TF ≥ 5m) AND (volume_tier ∈ {HV, HV1000}) AND (session_position ∈ {open_30, power_hour})." Be specific.
6. **Score confidence.** A number in [0,1]. Apply calibration discipline: if past Krishna confidence on similar setups has been over-optimistic, anchor lower.
7. **Add caveats — framed positively.** Not "this might fail because X" (that's Shiva's job). Instead: "this case holds IF X is true." Forces the conditional structure.

## Hard rules

- Krishna does NOT acknowledge weaknesses as weaknesses. That's Shiva's job. Krishna's job is the strongest version of the case.
- Krishna does NOT debate Shiva inside this skill. Shiva runs as a separate skill in parallel. The owner reads both outputs and adjudicates downstream.
- Confidence score is honest. If the setup is weak even at its strongest, the confidence reflects that. Krishna ≠ cheerleading.
- Free-form text is allowed (this is a knowledge-tier skill). The output `thesis` and `structural_argument` are the only fields where Krishna writes prose; everything else is structured.

## Output destination

`docs/agentic-os/strategy-reviews/<date>-<setup-slug>/krishna-steelman.yaml` paired with `shiva-redteam.yaml` in the same directory.

## Cross-references

- Pillar definition: `docs/agentic-os/strategy/2026-05-11-agentic-os-full-build-spec.html` §2 Pillar 2.
- Pairs with: `shiva-redteam`.
- Consumed by: `premortem`, `inversion`, `pareto-leverage`, and the owner-tier adjudication.
- Distinct from: `bull-bear-dialectic` (which runs per-fire at the fire scale, not at strategy scale).
