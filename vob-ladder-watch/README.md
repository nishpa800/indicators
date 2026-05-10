# VOB Ladder Watch

Staged `zF → zE → zD → zC → zB → zA` ascending-ladder detector. Pine v5,
overlay.

## Files

- `versions/VOB_LADDER_WATCH_v1.pine` (12.2 KB)

## Roots (6)

Six ladder zones (`p_a..p_f` from `f_top_active` over per-tier bull-VOB
arrays).

## Composites (8)

`ladder_depth` (rolling depth 0-6), `escalated` edge event, 5 named
escalation signals (WATCH / TIER3 / TIER4 / TIER5 / FULL), pipe-delimited
`alert()` payload, top-right `depth_gauge_table` dashboard.

## Bible

- `bible-input/extract-vob-ladder-watch.yaml` — full extraction
- `docs/lineage/vob-ladder-watch__*.md` — lineage cards

## Sibling

`vob-asym/` — VOB asymmetric T3×6 (different concept, shares the bull-VOB
engine pattern).

## Stage 6 — folder split

Previously lived at `vob/versions/`. Stage 6.5 split it out so VOB Asym
and VOB Ladder Watch each have their own top-level directory. The
`CHANGELOG.md` here is the original VOB CHANGELOG (which was largely
LADDER WATCH-focused).

## Branch provenance

Available on both `main` and `claude/add-txt-indicator-format-b4FUu`.
