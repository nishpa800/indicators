# VOB — Volume Order Block (umbrella folder for two indicators)

This folder currently holds **two distinct indicators** sharing one
directory. Stage 6.5 splits them into `vob-asym/` and `vob-ladder-watch/`.

## VOB Asym T3×6 MutEx

`versions/VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine` (112.7 KB, Pine v6)

VOB asymmetric T3×6 with mutually-exclusive state markers. 25 zone-creation
+ T3 SUPER + Nagasaki ATH-volume roots; 15 composites at tiers 1-4 including
any-T3 / any-zone aggregators, the MutEx priority-line engine, per-tier
bull/bear pools, and the pancake-bull/pancake-bear confluence flag.

Bible: `bible-input/extract-vob-asym.yaml`.

## VOB Ladder Watch v1

`versions/VOB_LADDER_WATCH_v1.pine` (12.2 KB, Pine v5)

Staged zF → zA escalation detector. 6 ladder roots (zA..zF as `p_a..p_f`)
and 8 composites including ladder_depth, escalated edge event, the 5 named
escalation signals (WATCH/TIER3/TIER4/TIER5/FULL), the pipe-delimited
`alert()` payload, and the depth-gauge dashboard table.

Bible: `bible-input/extract-vob-ladder-watch.yaml`.

## Why they share a folder

Historical accident — both started as VOB-related experiments before
diverging into distinct indicators. The shared `CHANGELOG.md` covers only
the LADDER WATCH addition (the VOB Asym entry is missing).

## Stage 6.5 plan

Split into two top-level directories:

```
vob-asym/
├── CHANGELOG.md  (VOB Asym history extracted from current shared CHANGELOG)
├── README.md
└── versions/
    └── VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine

vob-ladder-watch/
├── CHANGELOG.md  (LADDER WATCH history)
├── README.md
└── versions/
    └── VOB_LADDER_WATCH_v1.pine
```

Then update `bible-input/MANIFEST.md`, `bible-input/extract-vob-*.yaml`
file paths, and re-run `tools/merge_extracts.py` + `tools/build_docs.py`.

## Branch provenance

Available on both `main` and `claude/add-txt-indicator-format-b4FUu`.
