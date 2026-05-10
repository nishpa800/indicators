# Standard Operating Procedures — Index

The repeatable assembly line for using and maintaining the indicator bible.
Each SOP describes a recurring procedure, when to use it, and the inputs /
outputs / failure modes.

## SOPs

| SOP | When to use it |
|---|---|
| [`root-validation.md`](./root-validation.md) | Every time a root is added, edited, or imported into a new chart. Confirms the root fires when expected and only when expected. |
| [`composite-validation.md`](./composite-validation.md) | Every time a composite is added, edited, or implicated in an unexpected firing. Walks the lineage card top-down to find the failing level. |
| [`drift-triage.md`](./drift-triage.md) | When the same root fires differently in two indicators or a composite that should fire doesn't. |
| [`offset-triage.md`](./offset-triage.md) | When a composite fires "one bar off" or fails to align with its dependencies. |
| [`icloud-mirror.md`](./icloud-mirror.md) | When syncing the bible to local + iCloud Drive for offline access. |

## Operating principle

The bible is the single source of truth. Every SOP starts from the bible:

1. **Open `INDICATORS_INDEX.md`** at the repo root.
2. **Drill into the relevant artifact**: a root in `docs/roots.md`, a
   composite in `docs/composites.md` or its lineage card in
   `docs/lineage/`, a drift question in `docs/redundancy.md`, a glossary
   term in `docs/glossary.md`.
3. **Walk top-down** for composites; **walk family-by-family** for roots.
4. **Use the offset ledger** in lineage cards to triage offset bugs.
5. **Update the bible**: edit `data/indicators.yaml`, re-run
   `tools/merge_extracts.py` then `tools/build_lineage_cards.py` then
   `tools/build_docs.py`. Commit with a clear "what changed and why".

## Daily-use snippet

For an "is this firing correctly?" check:

```
1. Open INDICATORS_INDEX.md.
2. Click the indicator family.
3. Find the named root or composite.
4. Open its lineage card (composites) or its row in docs/roots.md.
5. Read the OFFSET LEDGER (composites) or `offset:` field (roots).
6. Compare against the actual chart bar where the plot rendered.
7. If misaligned → offset-triage.md. If missing → drift-triage.md.
   If wrong threshold → root-validation.md (parameter check).
```

## Editing the bible

Never edit `docs/roots.md`, `docs/composites.md`, `docs/redundancy.md`,
`docs/visual-trees/*`, `docs/lineage/*`, or `INDICATORS_INDEX.md` by
hand — they are auto-generated from `data/indicators.yaml`. Edit the YAML
(or one of the `bible-input/extract-*.yaml` chunks if the change is
indicator-specific), then re-run the generators:

```bash
cd /home/user/indicators
python3 tools/merge_extracts.py    # YAML + JSON
python3 tools/build_lineage_cards.py   # docs/lineage/*
python3 tools/build_docs.py        # roots.md, composites.md, redundancy.md, visual-trees/*, INDICATORS_INDEX.md
```

`docs/glossary.md` and `docs/version-control-diagnosis.md` are
hand-authored; edit them directly.
