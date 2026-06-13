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
- **🚫 64-PLOT CEILING — NO `display.data_window` PLOT MATRICES.** TradingView caps a
  script at **64 plot-objects**; EVERY `plot*()`/`alertcondition()` counts, including
  `plot(..., display=display.data_window)` (draws nothing, still burns budget, litters the
  Style tab with junk blue lines). Shipping a "numeric data-window fire matrix" blew ULTRA 57
  past 64 → **RE10140** (2026-06-13). NEVER add `display.data_window` plots. If a
  machine-readable fire matrix is needed, emit it via **`log.info()`** (does NOT count).
  Gate before "done": `tools/check_plot_budget.sh` must exit 0 (≤64 plot-objects, zero
  `display.data_window` plots) for every tick-friendly build.
- **🚫 RE10008 — NEVER scan bars for "yesterday" / multi-day lookback.** A loop like
  `for i = 1 to barsPerDay*2` or `... to bar_index` that reads `sig[i]` forces Pine to
  reserve a history buffer as deep as the bound; on fine intraday/tick sessions that
  exceeds Pine's hard **5000-bar** history limit → **RE10008** (blew up ULTRA 57's
  `f_hadSignalYesterday`, 2026-06-13). Track days with **date-rolled `var` state**, never
  bar offsets — reference impl `f_firedPrevDay()` in
  `ultra-combo/tick_friendly/ULTRA_COMBO_v57_tick_friendly.pine` (O(1), zero history
  references, correct on every timeframe). A small fixed cap (e.g. `to 500`) dodges the
  crash but silently fails to reach "yesterday" on tick — still wrong, just quieter.
- **🚫 RE10023 #2 — `time(timeframe.period, …)` ALSO crashes on tick.** It is NOT only
  `relativeVolume`/`timeframe.change`: calling `time()`/`time_close()` with the chart's tick
  `timeframe.period` as the resolution arg — e.g. session checks like
  `not na(time(timeframe.period, "0930-1600", tz))` — throws **RE10023 on bar 0** of a tick chart
  (blew up SQUARIFY v2 + HUB, 2026-06-13). Route the resolution through a tick-safe value:
  `time(str.endswith(timeframe.period,"T") ? "1" : timeframe.period, session, tz)` ("1" = 1-min
  session eval on tick; time charts keep `timeframe.period` for parity). `tools/check_plot_budget.sh`
  now hard-fails on `time(timeframe.period,` and on any blank `relativeVolume(..., "")` anchor.
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
