# ~/code/anish/indicators/ — Pine Script v5 indicator suite

Public repo: **github.com/nishpa800/indicators**

> ## ⭐ `tv_ta.relativeVolume()` — the suite's ONE shared library function
> Every Pine study here shares exactly one external library function:
> `tv_ta.relativeVolume()` (`import TradingView/ta/7`, 90 call sites suite-wide,
> zero other `tv_ta` functions). Its CANONICAL Python port lives in the companion
> repo: **`~/code/anish/realtime-indicators/rti/tv_ta_shim.py`** (verified in
> `rti/SHIM_PARITY.md`). It is "Relative Volume **at Time**" — a session-anchored,
> intraday-offset average. **Never re-implement it, and never approximate it as
> `volume / ta.sma(volume, N)`** (that guess diverged up to ~162% from TradingView
> on real opening bars and silently broke parity). Any Python port of any study in
> this repo must import that one shim.
>
> ### 🚨 TICK CHARTS: `relativeVolume()` crashes with RE10023 unless you force a "D" anchor
> `TradingView/ta/7` line 346 runs `timeframe.change(anchorTimeframe)`. The suite passes
> `""` (chart TF) → on a **tick** interval that's tick-based → `timeframe.change` throws
> **RE10023 on bar 0**: *"Cannot call `timeframe.change` with a tick-based 'timeframe' argument."*
> EVERY tick-friendly build MUST route relativeVolume through a forced time-based anchor:
> ```pine
> string reg_anchorSafe = (reg_anchorTimeframe == "" or str.endswith(timeframe.period, "T")
>      or na(timeframe.in_seconds(timeframe.period)) or timeframe.in_seconds(timeframe.period) <= 0)
>      ? "D" : reg_anchorTimeframe
> [c,p,r] = tv_ta.relativeVolume(len, reg_anchorSafe, cumul, adjust)
> ```
> Time charts keep their anchor (parity preserved); only tick charts get `"D"`. PROVEN live on
> 1000T (AMEX:BRF): anchor `"D"` → relVol 4.11 clean; `""` → RE10023. Gate before "done":
> `grep -nE 'relativeVolume\([^,]+,\s*""' <file>` must return nothing. Also guard `tfSec` —
> `timeframe.in_seconds()` is na/0 on tick → thresholds silently die without a fallback.
> Full doctrine: `~/.claude/projects/-Users-anishpatel/memory/pine_tick_relativevolume_re10023.md`
> + skill `pine-editor-to-pine-tick-friendly`.

> ## ⭐ MANDATE — NO unrequested `plot()` lines (numeric / count / debug / aggregate)
> A detection study emits ONLY the exact `plotshape()` markers the user asked for.
> **NEVER** add a `plot()` of a count, sum, ratio, score, distance, or any aggregate
> — **not even `display=display.data_window`** — unless the user EXPLICITLY asks for
> that exact series. Every `plot()` adds its own row to the Style/Settings tab; a
> wall of "tuning helper" count lines is junk the user did not order. Internal
> aggregates stay as **UNPLOTTED export variables only**. Default = ZERO extra plots.
> (Origin: a build shipped 11 `display.data_window` count lines nobody requested.)
>
> **HOW IT IS ENFORCED (mechanical, not honor-system):**
> 1. Every detection-only `.pine` carries the marker `// NO-DEBUG-PLOTS` near the top.
> 2. `check_no_debug_plots.sh` HARD-FAILS any marked file that contains a `plot(` call
>    (legacy files that legitimately export to the fire-matrix simply omit the marker).
> 3. `hooks/pre-commit` runs that gate (+ `check_no_fixed_windows.sh`) on every staged
>    `.pine` and BLOCKS the commit on any violation.
> 4. `.claude/settings.json` runs `git config core.hooksPath hooks` on SessionStart, so
>    the pre-commit block is auto-armed for EVERY Claude agent / session / fresh clone.
> Gate before "done": `bash check_no_debug_plots.sh <file>` must print PASS.

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
- **🚫 NO unrequested `plot()` lines (numeric / count / debug / aggregate) — see the ⭐ MANDATE at the top.** Detection studies = only the `plotshape()` markers the user asked for. Mark such files `// NO-DEBUG-PLOTS`; `check_no_debug_plots.sh` + the `hooks/pre-commit` gate will BLOCK any commit that puts a `plot()` in a marked file. Internal aggregates stay UNPLOTTED.
- **Never label "canonical" prematurely.** Ingest all variants verbatim. "Which is canonical?" is the OUTPUT of root extraction + TV verification, never the input.
- **Always commit + push every change in the same turn.** Paste the GitHub URL.

## Verification

Use [Verification Protocol v3.2](~/.claude/projects/-Users-anishpatel/memory/verification_protocol.md) for ALL audit/translation/delivery work. Vocabulary: `bar[N]` only — no "signal" / "current bar."

---

## 📄 PDF / Office / Audio → Markdown — ALWAYS use `markitdown` FIRST

For ANY non-text document (PDF, DOCX, PPTX, XLSX, HTML, image, audio file, YouTube URL),
convert to Markdown with `markitdown` BEFORE reading. Do NOT `Read` a PDF/DOCX/PPTX directly —
binary Read produces noise or fails.

    markitdown <path-or-url> > /tmp/<name>.md     # then Read /tmp/<name>.md

**MCP also available** in BOTH Claude Code and Codex CLI: server name `markitdown`,
tool `convert_to_markdown`, pass `uri="file:///abs/path"` or `uri="https://..."`.

Covers ~99% of vendor PDFs, hedge-fund letters, protocol PDFs, earnings transcripts,
papers, slide decks, transcripts.

**EXCEPTIONS — do NOT use markitdown for:**
- 13F native EDGAR XML → use `sec-edgar-13f` skill + `edgartools`
- Massive REST/WS JSON or S3 parquet → use Massive MCP / DuckDB directly
- Heavy-table PDFs where row/column alignment matters → use `pdfplumber` or `camelot`

Full doctrine + install state + failure modes:
`~/.claude/projects/-Users-anishpatel/memory/pdf_conversion_markitdown.md`
