# VOB Asym T3×6 MutEx — CHANGELOG

## v8 — 2026-05-02

`VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine` (112,709 bytes, Pine v6).

Asymmetric T3×6 ladder with mutually-exclusive state markers. Per Stage-1
extraction (see `bible-input/extract-vob-asym.yaml`):

- 25 zone-creation roots: 12 zA-bull/bear … zF-bull/bear plotshape markers
  driven by cooldown-gated booleans, 12 T3a-buy/sell … T3f-buy/sell SUPER
  signals, 1 Nagasaki ATH-volume marker.
- 15 composites at tiers 1-4: any-T3 / any-zone aggregator flags, the MutEx
  priority-line drawing engine, per-tier bull/bear pools, aggregate
  counts/distances/stack/gap metrics, the pancake_bull / pancake_bear
  confluence flag, two consolidated alertconditions, two Bloomberg-format
  alert payloads, the zone-formation label emission, log.info per-bar
  stream, and three on-chart tables.

## Stage-6 history

Previously co-located with `VOB_LADDER_WATCH_v1.pine` under a shared `vob/`
directory. Stage-6 split (commit on this branch) moved both indicators to
their own top-level directories. The Stage-1 extraction agent already
treated them as distinct families; this folder split makes the file
organisation match.
