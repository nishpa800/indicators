# VOB Asym T3×6 MutEx

VOB asymmetric T3×6 ladder with mutually-exclusive state markers. Pine v6,
overlay.

## Files

- `versions/VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine` (112.7 KB)

## Roots (25)

- 12 zone-creation markers (zA..zF bull/bear)
- 12 T3 SUPER signals (T3a-T3f buy/sell)
- 1 Nagasaki ATH-volume marker

## Composites (15)

Tiers 1-4: any-T3 / any-zone aggregators, MutEx priority-line engine,
per-tier bull/bear pools, aggregate metrics, pancake_bull/pancake_bear
confluence flag, alertconditions, Bloomberg-format alert payloads,
zone-formation labels, log.info stream, on-chart tables.

## Bible

- `bible-input/extract-vob-asym.yaml` — full extraction
- `docs/lineage/vob-asym__*.md` — lineage cards

## Sibling

`vob-ladder-watch/` — distinct indicator (staged zF → zA escalation
detector). Shares the bull-VOB engine pattern but no live data dependency.

## Stage 6 — folder split

Previously lived at `vob/versions/`. Stage 6.5 split it out so VOB Asym
and VOB Ladder Watch each have their own top-level directory.

## Branch provenance

Available on both `main` and `claude/add-txt-indicator-format-b4FUu`.
