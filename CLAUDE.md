# ~/code/anish/indicators/ — Pine Script v5 indicator suite

Public repo: **github.com/nishpa800/indicators**

## Before doing anything

**Read the master registry first:**
`/Users/anishpatel/.claude/projects/-Users-anishpatel/memory/ANISH_HAS.md` section "PINE INDICATOR SUITE."

Then read:
- `~/.claude/projects/-Users-anishpatel/memory/indicator_trust_rules.md`
- `~/.claude/projects/-Users-anishpatel/memory/wmd_deprecated_use_hct.md`
- `~/.claude/projects/-Users-anishpatel/memory/verification_protocol.md` (v3.2)
- `~/.claude/projects/-Users-anishpatel/memory/verification_protocol_supplement.md`
- Indicator-specific deep doc (e.g., `b2b_pup_indicator.md`)

## Structure

```
indicators/
├── b2b-pup/                  # B2B PUP — aggregator with S1-S20+ plots
│   ├── versions/
│   │   └── B2B_PUP_v4.32.pine
│   └── CHANGELOG.md
├── tnt-od/                   # TNT OD v2 — canonical Napalm/TNT/CONT/Charge ladder
│   ├── versions/
│   │   └── TNT_OD_v2.pine
│   └── CHANGELOG.md
├── squarify/                 # SQUARIFY v2 — 46-plot aggregator
│   ├── versions/
│   │   └── SQUARIFY_v2.pine
│   └── CHANGELOG.md
├── hvd-pbj-ppd/              # Floor/2F/Rooftop/Penthouse composites — engine = Ping Pong
├── vob/                      # Volume Order Block — Holy Grail / Nightmare confluence
├── heavy-combo-toggles/      # HCT — S1 Heavy Combo Bull/Bear/Neutral (REPLACES deprecated WMD)
├── proximity-gzi-hv/         # Proximity-based GZI for HV
├── sync_from_tradingview.sh  # pulls source from TV
└── CHANGELOG.md
```

## Hard rules

- **Pine v5 ONLY.** `//@version=5` at top of every file. AVOID v6-only MCPs/docs (iamrichardD, 9Mirrors-Lab, GoldenPine, paulieb89, etc).
- **Fast Calculation OFF** in TradingView always. Truncates history → breaks long-lookback state.
- **Alpha Strike trusted ONLY from SQUARIFY 64.** Always filter alerts by source indicator.
- **WMD is DEPRECATED** → use Heavy Combo Toggles. Squarify's `35 NAG+` (Nagasaki Plus) still valid.
- **Plot naming:** every plot is `S<N>: <descriptor>`. Never letter abbreviations.
- **Never label "canonical" prematurely.** Ingest all variants verbatim. "Which is canonical?" is the OUTPUT of root extraction + TV verification, never the input.
- **Always commit + push every change in the same turn.** Paste the GitHub URL.

## Verification

Use [Verification Protocol v3.2](~/.claude/projects/-Users-anishpatel/memory/verification_protocol.md) for ALL audit/translation/delivery work. Vocabulary: `bar[N]` only — no "signal" / "current bar."
