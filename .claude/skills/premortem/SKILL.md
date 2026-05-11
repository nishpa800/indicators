---
name: premortem
description: Assume the strategy / trade / setup HAS FAILED. Enumerate the causes in past-tense-of-failure. Pre-author the mitigation for each. The discipline of writing in past tense surfaces causes that future-tense risk talk misses. Owner-tier skill. Runs before adopting a strategy and daily before market open against today's calendar.
when_to_use: Invoke before formally adopting a new detection plot, before committing to a trade plan, and as a daily 04:00 UTC hook against the day's calendar (earnings, FOMC, jobs, CPI). NOT a "what might go wrong" hand-wave — it's "this DID go wrong; why?" The past-tense framing is non-negotiable.
tier: owner
---

# Premortem

**Tier**: owner (orchestration; persistent memory; strategic stewardship).

**Purpose**: Surface failure causes BEFORE they happen. The discipline: write as if the failure has already occurred. Past tense. "On 2026-05-12 the PBJ Bull setup failed. The cause was…" Then enumerate. The past-tense framing forces concreteness that future-tense ("what might go wrong") evades.

## Origin

Behavioral discipline borrowed from Gary Klein. The premortem outperforms the postmortem because the agent is psychologically free to imagine failure without admitting it — and the imagined failure surfaces causes the agent's confirmation bias would suppress in retrospect.

## Input

```yaml
target:
  type: trade_plan | new_plot_adoption | daily_session | strategy_change
  identifier: <e.g. "PBJ Bull adoption" or "2026-05-12 trading session">
  date: <iso>
  context:
    krishna_output: <ref to krishna-steelman.yaml if available>
    shiva_output: <ref to shiva-redteam.yaml if available>
    axis_card: <ref to axis-card>
    calendar_events: <list of catalyst events in the window — earnings, FOMC, jobs, CPI>
    open_positions: <if applicable>
```

## Output

```yaml
premortem:
  scenario: "On <date>, the <target> failed. The cause was..."
  failure_modes:
    - id: FM-1
      description: <past-tense narrative of one specific failure mode>
      severity: critical | high | medium | low
      probability: <subjective number in [0,1]>
      detection_lag: <how many bars before the cause became observable>
      mitigation: <concrete action that would prevent or limit this failure>
      early_warning_indicator: <observable signal that would trigger the mitigation>
    - id: FM-2
      ...
  ranked_priority:
    - FM-3   # highest priority — high severity AND high probability
    - FM-1
    - FM-7
    ...
  do_not_act_unless:
    - <condition that must be true to enter at all — derived from the most severe FMs>
  inversion_candidates:
    - <items that should escalate to the inversion skill for codification as "never do" rules>
```

## Procedure

1. **Read Krishna + Shiva if available.** Shiva's failure_regimes are seed candidates for premortem FMs. Krishna's required_conditions help identify FMs (failure of required conditions).
2. **Imagine the specific failure scene.** Don't generalize ("the trade might lose money"). Be specific ("at 09:42 ET the position was stopped out because LUNR gapped down 4% on a 13F sell from Renaissance Tech that hit headlines at 09:35"). Specific scenes surface specific causes.
3. **Enumerate at least 5 failure modes.** Range from operational (data feed lag, missed alert) to structural (regime change, edge decay) to behavioral (over-sizing, FOMO entry late).
4. **Score severity × probability for each.** Severity ∈ {critical, high, medium, low}. Probability ∈ [0,1] subjective. The ranked_priority is sorted by severity × probability.
5. **Author a concrete mitigation for each.** Not "be careful" — a specific action. "If 09:30–09:35 sees gap-down > 2% on volume > 3x average, do NOT enter PBJ Bull on this symbol today, period."
6. **Author an early-warning indicator for each mitigation.** The signal that triggers the mitigation. "Gap-down 2% on volume 3x — check at 09:35:00 ET sharp."
7. **Flag inversion candidates.** Failure modes that recur across multiple premortems should escalate to the `inversion` skill for codification as standing "never do" rules.

## Hard rules

- Past tense. Always. "The trade failed because…" not "the trade might fail if…"
- Specific scenes. No generalities.
- At least 5 failure modes. Even if the first 5 feel forced — the forcing function is the point. The forced 6th and 7th are often the real ones.
- Mitigations must be CONCRETE actions, not posture statements.
- Every premortem writes to disk. Append-only. Forever-logged. Even the ones that turned out wrong.

## Output destination

- Adoption / strategy: `docs/agentic-os/premortems/adoption/<date>-<setup-slug>.md`
- Daily session: `docs/agentic-os/premortems/<date>.md` — posted to Slack #premortem at 04:00 UTC daily

## Cross-references

- Pillar definition: `docs/agentic-os/strategy/2026-05-11-agentic-os-full-build-spec.html` §2 Pillar 4.
- Reads from: `krishna-steelman`, `shiva-redteam`, `axis-decomposition`.
- Escalates to: `inversion` (when FMs recur).
- Distinct from: postmortem (which runs AFTER an outcome — not yet a skill; future work).
