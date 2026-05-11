# Stage 4 — Composite Firing Validation Methodology

This is the methodology document for **Bible Stage 4** (composite firing
validation when roots align). It is written so the next person who picks
up the work (or future-Anish) can execute Stage 4 mechanically.

Stage 4 is the **first stage that actually decides correct vs incorrect**
for a composite. Earlier stages (1–3) ingested, catalogued, and verified
roots. Stage 4 turns the Phase M / Phase A outputs into a verdict per
composite.

## ⭐ CANONICAL PROCEDURE: use the `detection-plot-validation` skill ⭐

As of 2026-05-10, the Stage 4 procedure is **codified as a Claude Code skill** at
`.claude/skills/detection-plot-validation/`. The skill enforces:

- The 4-phase procedure (ENUMERATE → STATIC-DIFF → TV-FIRING → RECONCILE)
- Multi-agent orchestration (one subagent per Pine file / diff pair / TV-firing location)
- Fixed output shape (`docs/validation/<date>-<target>.md`)
- Hard guardrails (no Pine modification without approval, no version deletion, never bypass extract-*.yaml, never commit without YAML==JSON)
- Standing approval embedded (`STANDING_APPROVAL.md` in the skill dir)

Phase 3 (TV firing chart-side) is the spinout skill at `.claude/skills/detection-plot-tv-firing/` — only invoke when Anish is at his desk with the Path A loggers loaded. The main skill flags `BLOCKED-NEEDS-TV-FIRING-SKILL` and continues; never blocks on Anish.

**Run the skill** (any agent reading this can do it):

```
Validate <target>
```

Where `<target>` is any detection plot's canonical name (e.g. `UNIFIED_COMBO_BULL`, `csNew3_Bull`, `superBull`). The skill loads its own context, runs all 4 phases, produces the report.

Or via the harness directly for Phase 1 only:

```bash
python3 tools/validate_detection_plot.py --target=<canonical> --aliases=<comma-list>
```

The methodology below is the LEGACY pre-skill description, retained for posterity.

---

## Inputs

1. **Path B static audit** — `docs/static-audit-2026-05-10/*.md`. Tells
   you which composites have YAML-vs-Pine drift on paper.
2. **Path A TV labels** — `data_get_pine_labels(study_filter="LOGGER ...")`
   returns every fire recorded by the logger Pines on Anish's chart.
3. **Phase M Python compute** —
   `~/data/massive/_phase_m/<date>_detections.csv` produced by
   `realtime-indicators/run_ports_against_bars.py`. Every fire the
   Python ports computed on Massive historical bars.
4. **Bible YAML** — `data/indicators.yaml` and the per-family
   `bible-input/extract-*.yaml`. The composition spec.

## The decision matrix

For each composite, on each (ticker, TF, bar) tuple:

| Pine logger fired? | Python port fired? | Verdict |
|---|---|---|
| ✅ | ✅ | **MATCH** — Composite is internally consistent. Roots co-firing → composite firing in both implementations. |
| ✅ | ❌ | **PORT MISS** — Python port has a bug or is missing state. Fix the port. |
| ❌ | ✅ | **PORT OVER-FIRE** — Python port is too permissive. Tighten the port. |
| ❌ | ❌ | (no datum — composite simply didn't fire here) |

Run this matrix across ≥100 fires per (composite, TF). The composite
**passes Stage 4** when:
- ≥95% of Pine fires are matched by Python fires within ±1 bar offset.
- ≥95% of Python fires are matched by Pine fires within ±1 bar offset.
- No more than 5% mismatch on any (composite, TF) row of the table.

Composites that pass Stage 4 are "behaviorally validated." They can
be promoted into the canonical-selection process for Stage 6.

Composites that fail get their **lineage card** (`docs/lineage/<family>__<COMPOSITE>.md`)
opened up. Walk it top-down: which operand is the first one whose roots
don't agree between Pine and Python? Fix that root or composite. Re-run
Stage 4. Repeat until pass.

## Procedure (per composite)

```
1. Pull TV logger labels:
     mcp__tradingview__data_get_pine_labels(study_filter="LOGGER <family>", max_labels=500, verbose=true)
   → bucket by text tag → per-composite list of {bar_index, time, price}.

2. Pull Phase M Python fires:
     pandas.read_csv("~/data/massive/_phase_m/<date>_detections.csv")
       .query("name == '<composite>'")
   → list of {ticker, tf, detection_ts, plot_ts}.

3. Inner-join the two on (ticker, tf, time) with ±1 bar tolerance.
4. Compute the matrix counts. Compute the pass thresholds.
5. If pass → mark composite "Stage-4 validated" in lineage card.
   If fail → drift triage (docs/sop/drift-triage.md), open lineage card.
```

## Common failure modes (and where to look first)

| Failure pattern | Most likely cause | Where to look |
|---|---|---|
| Python fires never, Pine fires always | State machine port missing | check the pack's docstring for "STUBBED" or "TODO: stateful" |
| Python fires constantly, Pine fires rarely | Threshold off, or required gate missing | compare `composition.operands` between extract YAML and the Python implementation |
| Offset disagreement (always ±1 bar) | Pine `offset=-1` not mirrored in Detection.offset | check the `offset` argument in the `yield Detection(...)` call |
| Pine fires only on certain TFs | TF-keyed threshold table | check Pine source for `timeframe.in_seconds()` switch |
| Sub-5min TFs show 0 Pine fires | Same TF-keyed threshold table — bands collapse | `pine_port_findings_2026-05-10.md` Finding #2 (WTC) |

## How Phase M's Python ports relate to Pine source canonicality

Phase M's Python output is the **reference implementation against
which Pine is validated**, not the other way around. The Path B audit
already aligned the bible YAML with Pine. The Python ports were
written from those bible YAMLs. So the chain of truth is:

```
Pine source ← (Path B static audit) → bible YAML → (Phase C port) → Python pack
                                                    ↓ (Phase M run)
                                                   detections
TV chart ← (Path A logger) ← (input.source) ← Pine source → TV labels
```

Stage 4 closes the loop: TV labels (Pine runtime truth) cross-referenced
against Python detections (bible runtime truth). Disagreement = a bug
somewhere in the chain, and the procedure above narrows it down.

## When to STOP and ask Anish

- A composite has structural drift the audit already flagged "requires
  Anish's decision" (e.g. `e3-f2-cluster` bull/bear threshold asymmetry).
  Stage 4 cannot decide canonicality here — it's a design choice.
- A composite is named identically in 2+ families but the implementations
  obviously differ (e.g. `HEV` in `hv-ladder` vs in `hvd-pbj-ppd`).
  Stage 4 verifies each separately; canonical-selection (Stage 6)
  decides which name "wins."
- A composite has ≥10 successive failures even after the lineage card
  walk surfaces no obvious culprit. Likely the Pine source itself has
  a bug Anish wasn't aware of (e.g. `pine_port_findings_2026-05-10.md`
  Finding #1 — `NEUTRAL_HEAVY_X2` always False).

All other cases — automatic.
