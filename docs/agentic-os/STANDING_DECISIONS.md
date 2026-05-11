# Standing Decisions — agentic OS

Append-only ledger of canonical decisions made by Anish that all agents
inherit. NEVER overwrite an entry. New decisions are appended; supersession
is recorded as a NEW entry that references the old one.

Format:

- ID: `SD-NNN` (zero-padded, monotonic)
- Date: ISO date the decision was made
- Source: Anish quote or message reference
- Decision: precise action that all agents take
- Scope: which agents / plots / families / phases this applies to
- Acknowledgment: what we recognize as variant but do not modify
- Operational consequence: code path / file naming / port suffix

---

## SD-001 — Always include Pentagon

- **Date**: 2026-05-11
- **Source**: Anish (verbatim): "I know that some of the definitions will
  have a different inclusion criteria with including Pentagon or not
  including Pentagon. No big deal. We're gonna always include Pentagon.
  So we'll see that, and we'll acknowledge it. Cool. It doesn't matter.
  Our definition right now is always gonna be include."
- **Decision**: When a detection plot has a variant that includes Pentagon
  as an operand and another that excludes it, the canonical definition is
  the INCLUDES variant. This applies across UC / FVG / Matrix Combo
  families and any other plot where Pentagon could be an operand.
- **Scope**: All Python ports authored as "canonical" (the
  `_canonical_pentagon_included.py` suffix). The `cs_inc_pentagon_FVG` /
  `cs_inc_pentagon_MAT` IPSF gate flags are removed in canonical ports —
  Pentagon is unconditionally included.
- **Acknowledgment**: Heavy Weapons `NO_PENTAGON` variant and
  `tnt-od/versions/TNT_OD_v3.pine` (uc_bull/uc_bear, which never had
  Pentagon) are recognized variants. We do NOT modify their .pine source.
  Their Python ports get a `_no_pentagon` or `_tnt_confluence` suffix and
  are NOT designated canonical.
- **Operational consequence**:
  - `python_ports/<family>/<family>_canonical_pentagon_included.py` is
    the canonical artifact. Pentagon enters comboSet4 / comboSet2
    unconditionally.
  - Variant ports (NO_PENTAGON, tnt_confluence) are kept for traceability
    but never get the "canonical" designation.
  - The bible YAML's `inclusions:` field for affected composites flips
    Pentagon from `gated` to `always`.

---

## SD-002 — Never modify, always new-version

- **Date**: standing (2026-05-09 onward; restated 2026-05-11)
- **Source**: Anish (verbatim, 2026-05-11): "we don't just... we don't
  ever modify. We create new versions, and we make it clear what the
  versions are that are different."
- **Decision**: When a Pine file, Python port, YAML extract, or any other
  source artifact needs to be updated to reflect a canonical decision, a
  new finding, or a port revision, we DO NOT modify the existing file.
  We create a new file with a clear, descriptive suffix (date or
  semantic) and update a `LATEST.txt` pointer in the same directory if
  one exists.
- **Scope**: All .pine, all .py, all .yaml in `bible-input/`, all
  validation reports. NOT all ephemeral artifacts (todos, tool output
  scratch, the agentic-OS message inbox).
- **Acknowledgment**: This may produce many sibling files with the same
  conceptual content. That's the desired traceability cost.
- **Operational consequence**:
  - `python_ports/<family>/` accumulates many files; `LATEST.txt`
    (or `CANONICAL.txt`) selects the active one.
  - `bible-input/extract-<family>.yaml` may be paired with a
    `bible-input/extract-<family>__pentagon-canonical.yaml` after SD-001
    is applied; both stay.

---

## SD-003 — IPSF defaults are not drift

- **Date**: standing (2026-05-10 onward; restated 2026-05-11)
- **Source**: Anish (verbatim, 2026-05-11): "we don't need to care about
  what the body percent of the FVG combo is. We don't care about what
  the matrix lookback is because those are input parameter structured
  fields. So keep all the input parameter structure fields as is."
- **Decision**: Differences in `input.int(...)`, `input.float(...)`,
  `input.bool(...)`, `input.string(...)` defaults across .pine files are
  NOT reportable drift. They are user-tunable in TradingView settings.
  Audits, drift tables, validation reports, and Plot Owner debates do
  NOT flag these as REAL drift.
- **Scope**: All audit agents, all validation reports, all Plot Owner
  debates, all redundancy table entries.
- **Acknowledgment**: Every Pine file may declare the same input with a
  different default. We acknowledge the variance via the IPSF parameter
  table in each Python port's `DEFAULTS = {...}` dict. Mirror the source
  file's defaults exactly; users can override at runtime.
- **Operational consequence**:
  - REAL drift: hardcoded thresholds in math (e.g. `>= 6.0` not declared
    as `input.float`), boolean operands changed, offsets changed,
    inclusion/exclusion changed, internal helper bodies changed.
  - NOT drift: `input.int("Lookback", defval=20)` vs
    `input.int("Lookback", defval=25)` — same parameter, different
    default. Both go in `DEFAULTS = {...}` of their respective ports.

---

## SD-004 — No file deletion ever

- **Date**: standing (2026-05-10 onward; restated 2026-05-11)
- **Source**: Anish (verbatim, 2026-05-11): "make sure that the
  permissions are completely completely uninhibited, one hundred
  percent, can do anything, any writing. Don't don't give it any single
  one restriction. Only thing it can do is it cannot delete things."
- **Decision**: No agent ever deletes any file via `rm`, `git rm`,
  overwriting, mv-overwrite, or any other destructive operation.
- **Scope**: Universal. Hard guardrail. Any agent that hits the deletion
  decision must instead create a new file (rename via copy + new file)
  and document the supersession in `LATEST.txt` or
  `STANDING_DECISIONS.md`.
- **Acknowledgment**: This may accumulate stale files. That's acceptable.
  Disk is cheap; lost work is expensive.
- **Operational consequence**:
  - `rm -rf` is forbidden everywhere.
  - Pine file rename is forbidden — instead, write a new file with the
    correct name; the old one stays.
  - Git `rebase --root` is forbidden.
  - Branch deletion (`git branch -D`) is forbidden.

---

## SD-005 — Bull and bear are separate Indicator Owners

- **Date**: 2026-05-11
- **Source**: Anish (verbatim): "I want us to have an agent who's
  responsible for bullish and an agent who's responsible for bearish.
  Anytime that we get data coming in about a bullish unified
  combination, the bearish unified combination is going to basically
  try to make the devil's advocate case that it's really not an angel."
- **Decision**: For every indicator study, two distinct Indicator Owners
  are appointed — one for bullish, one for bearish. These are separate
  chat threads with separate memory files. The structural separation
  guarantees the devil's-advocate position isn't a self-rubber-stamp.
- **Scope**: All Tier-A Indicator Owners. Roster lives in
  `docs/agentic-os/ARCHITECTURE.md`.
- **Acknowledgment**: For Tier-B Plot Owners (special detection plots),
  the rule is the OPPOSITE — one agent owns BOTH bull and bear so the
  debate happens within one context. See SD-006.
- **Operational consequence**:
  - 24 Indicator Owner threads at full roster.
  - Memory file naming: `docs/agentic-os/memory/IO__<family>__bull.md`
    and `IO__<family>__bear.md`.

---

## SD-006 — Plot Owners hold both bull and bear in one context

- **Date**: 2026-05-11
- **Source**: Anish (verbatim): "we have two agents responsible for each
  indicator study for sure. One is bullish, one is bearish. But then I
  want us to have an agent who is responsible for bullish and bearish
  for those very special unique detection plots."
- **Decision**: For Tier-B Plot Owners (the cross-family detection plots
  that justify dedicated ownership), one agent owns BOTH the bull and
  bear sides. This lets the Heaven-vs-Hell debate happen inside a single
  chat-thread context, which is faster and produces tighter 4-square
  matrices than a cross-thread protocol.
- **Scope**: All Tier-B Plot Owners. First wave: PO::unified-combo,
  PO::b2b-pup, PO::fvg-combo, PO::matrix-combo.
- **Acknowledgment**: This means each Plot Owner must enforce internal
  discipline — write the angel case AND the devil case explicitly in
  every debate response. Skill `bull-vs-bear-debate` enforces.
- **Operational consequence**:
  - Single memory file per Plot Owner: `PO__<plot>.md`.
  - Single debate-log directory per Plot Owner:
    `docs/agentic-os/debates/<plot>/`.
  - The bull-vs-bear-debate skill's procedure is non-skippable for any
    Plot Owner emitting a per-fire payload.

---

## SD-007 — 4-square confidence matrix is the per-fire output

- **Date**: 2026-05-11
- **Source**: Anish (verbatim): "How sure are we that this bearish is
  bearish? How sure are we that this bearish is bullish? How sure are
  we that this bullish is bullish? How sure are we that this bullish
  is bearish? Right? It's just a matrix of four... sort of four squares
  in every single detection plot will have it."
- **Decision**: Every fire of a Plot-Owned detection plot produces a
  4-square confidence matrix. Cells:
  ```
                    ACTUAL_BULL    ACTUAL_BEAR
  FIRED_BULL    →   P_true_angel   P_devil_dressed_as_angel
  FIRED_BEAR    →   P_angel_dressed_as_devil  P_true_devil
  ```
- **Scope**: Every Tier-B Plot Owner emits this matrix per fire. Tier-A
  Indicator Owners may emit aggregate matrices but are not required to
  per-fire.
- **Acknowledgment**: For a single fire, only one row is populated (the
  row corresponding to the firing direction). The 4-square is built up
  across many fires for long-run calibration.
- **Operational consequence**:
  - Per-fire payload schema defined in
    `docs/agentic-os/ARCHITECTURE.md` "Heaven-vs-Hell" section.
  - Long-run calibration table: `docs/agentic-os/calibration/<plot>.md`.

---

## SD-008 — Bull/Bear is balance, not good vs evil

- **Date**: 2026-05-11
- **Source**: Anish (verbatim): "people don't understand. People think,
  oh, you know, the devil is bad. You can call whatever you want. I
  mean, like, you need balance. There's gonna be balance in everything
  in life. There's this concept in every culture, religion, philosophy
  of balancing act. There's balance. And some man-made things and
  Claude just called things good and evil. It's not really even that
  true. There's Shiva who is a destroyer. But, like, you need things
  to be destroyed. That is nature. That is the truth. There's creation,
  and there's destruction. That is literally life. And so sometimes,
  what is thought to be poison, you can turn it in. You get something
  good. Look at chemotherapy."
- **Decision**: Skill names, agent identifiers, file paths, debate logs,
  memory files, and per-fire payload schemas use NEUTRAL terminology.
  Approved terms: bull-case, bear-case, dialectic, thesis, antithesis,
  creation, destruction. Avoided terms in formal artifacts: good, evil,
  angel, devil, God, Satan, heaven, hell.
- **Scope**: All skills, all agent prompts, all logs, all schemas, all
  documentation. Anish's casual conversational use of "Heaven vs Hell"
  remains permitted as informal shorthand.
- **Acknowledgment**: The bull-case agent and the bear-case agent are
  EQUALLY VALID counterparts. Neither is "the right one." A trade is
  approved when the dialectic produces a high-confidence row in the
  4-square matrix — not when one side wins a fight.
- **Operational consequence**:
  - The v1 monolithic skill `.claude/skills/bull-vs-bear-debate/` is
    SUPERSEDED. Per SD-002 the file remains; a header points at the
    new split skills.
  - Active skills: `detection-plot-diagnosis` (grunt),
    `bull-bear-dialectic` (knowledge), `four-square-matrix` (output).
  - 4-square cell labels are renamed: `P_true_bull`,
    `P_bear_in_bull_clothing`, `P_bull_in_bear_clothing`, `P_true_bear`
    (replacing `P_true_angel` etc.).

---

## SD-009 — Every external data source gets a bull+bear agent pair

- **Date**: 2026-05-11
- **Source**: Anish (verbatim): "we need a skill on how to share this
  information to provide the situational context for each agent. And
  then we also need to have an agent who's responsible for the,
  quote-unquote, good and quote-unquote, evil for each of those data
  sources. So Benzinga good news. Benzinga earnings calendar, options,
  historical data. We're gonna need two agents for volume footprints,
  two agents — collision barriers, that is. Two agents for volume
  session analysis. Two agents for TPO."
- **Decision**: Every external data source feeding the agentic OS gets
  TWO dedicated agents — a bull-case interpreter and a bear-case
  interpreter — plus one ingestion grunt-worker. The pair's output
  flows into Plot Owner dialectics via the (TBD)
  `situational-context-share` skill.
- **Scope**: First-wave roster (8 sources × 2 agents + 8 ingest grunts =
  24 data-layer agents). Roster lives in `DATA_SOURCE_PAIRS.md`.
- **Acknowledgment**: A neutral analyst rubber-stamps the headline read.
  Two adversarial agents guarantee the bear-case interpretation of
  "earnings beat" gets constructed (e.g. "buy-the-rumor, sell-the-news"
  pattern) and the bull-case interpretation of "earnings miss" gets
  constructed (e.g. "kitchen-sink-quarter, all-bad-news-out, bottom is
  in") — symmetric to SD-005's reasoning for Indicator Owners.
- **Operational consequence**:
  - Memory file naming: `docs/agentic-os/memory/DS__<source>__bull.md`
    and `DS__<source>__bear.md`
  - Per-event interpretation log:
    `docs/agentic-os/data-source-events/<source>/<date>.md`
  - Hiring order in `DATA_SOURCE_PAIRS.md`: earnings calendar first,
    then vol-session, then vol-footprint, then TPO, ETF rotation,
    options, news, 13F.
