# Anish's Indicator Suite

Pine Script indicators for the fund. Each indicator lives in its own folder with version history and a changelog.

## Folder layout

```
indicators/
├── b2b-pup/                  ← B2B PUP Combined (aggregator with S1-S20+ plots)
│   ├── README.md
│   ├── CHANGELOG.md
│   └── versions/
│       └── B2B_PUP_vX.YZ.pine
└── tnt-od/                   ← TNT Opening Drive (reference for Napalm/TNT/CONT)
    ├── README.md
    ├── CHANGELOG.md
    └── versions/
        └── TNT_OD_vN.pine
```

## How Anish recalls what we did

**Plain-English questions Claude can answer from this folder:**
- "What did we change in B2B PUP last time?" → read `b2b-pup/CHANGELOG.md`
- "Which version is on my chart?" → look at `versions/` for the highest version number
- "Show me what B2B PUP looked like before we fixed Napalm" → diff older vs newer versions in `versions/`
- "When did we add S19?" → grep CHANGELOG for "S19"

## Conventions

- **Versions are kept**, never overwritten. Each meaningful change = new file `INDICATOR_vX.YZ.pine`.
- **Latest version** is whichever has the highest number — also referenced as "current" in the indicator's README.
- **Every change has a CHANGELOG entry** with date, version, and bullet list of what changed and why.
- **Pine v5 only** — see `~/.claude/projects/-Users-anishpatel/memory/feedback_pine_v5_only.md`.
- **Signal labels are S-numbered** — see `feedback_signal_naming.md`. No "Plot A/B".

## Pine Editor workflow

1. `pbcopy < indicators/<name>/versions/<file>` to load latest into clipboard
2. TradingView Desktop → Pine Editor → Cmd+A → Cmd+V → Cmd+S → Add to Chart

## Git

This folder is git-tracked locally. Push to GitHub when Anish authorizes it.
