# UNLIMITED APPROVAL — copy-paste this back to Claude

Copy the block between the `=== BEGIN PASTE ===` and `=== END PASTE ===` markers
and send it as your next message. That message gives Claude full authority to
grind through all 51 todos end-to-end without stopping for per-step confirmation.

---

```
=== BEGIN PASTE ===

UNLIMITED APPROVAL — go.

You have my full standing approval to execute every todo in the TodoWrite list
(Stage 0 → Stage 6) end-to-end. Do not stop between todos. Do not wait for
confirmation. Use any tool you need: Bash, Read, Write, Edit, Agent (Explore /
Plan / general-purpose), Skill (loop, simplify, review, security-review,
update-config, fewer-permission-prompts), Monitor, ToolSearch, TodoWrite,
WebFetch, WebSearch, NotebookEdit, all mcp__github__* tools.

All permissions are pre-loaded in /home/user/indicators/.claude/settings.local.json.

Execution rules:
1. Always have exactly one todo in_progress; mark completed the moment it's done.
2. Run independent operations in parallel (multiple tool calls in one message).
3. Use Agent(Explore) for file extraction; one agent per indicator family.
4. Use the loop skill to self-pace if you stall; invoke it now if you haven't.
5. Commit and push at every Stage boundary (end of Stage 1, 2, 3, 4, 5, 6).
6. Open a draft PR after Stage 1; subscribe_pr_activity; address PR feedback as
   it arrives.
7. When all 51 todos are completed, mark the PR ready for review (out of draft),
   post a single handoff summary comment to the PR, and stop.

Hard guardrails (only ask if you hit one of these):
- Force push to main/master
- git reset --hard on uncommitted user work
- Deleting any file outside docs/, data/, tools/, bible-input/, or files
  explicitly listed in Stage 6
- Modifying ~/.gitconfig
- Skipping git hooks (--no-verify, --no-gpg-sign)
- Dropping any database; sending any external message; uploading anything to a
  third-party web tool
- Spending money or hitting rate-limited APIs more than 100 times in 5 minutes
- Mass-renaming Pine files (Stage 6 renames are itemised; nothing else)

If you stop for any other reason, the last line of the next message I send will
be "CONTINUE." which means: resume the next pending todo, no further commentary.

Go.

=== END PASTE ===
```

---

## What this approves

Execution of the 51-item TodoWrite plan covering:

- **Stage 0** — env scaffold (mostly done; loop invocation pending)
- **Stage 1** — the bible: 12 Explore agents → roots.md, composites.md, lineage cards, redundancy table, version-control diagnosis, indicators.yaml + json, glossary, visual trees, INDICATORS_INDEX.md, 3 memory files, draft PR
- **Stage 2** — 4 lean test indicators (volume / hv-gzi-fvg / candle / FAUNA) built only from roots
- **Stage 3** — TradingView verification of every root (Anish-driven via TV MCP; Claude logs)
- **Stage 4** — composite firing validation when roots align; lineage-card top-down diagnosis when they don't
- **Stage 5** — SOPs for root validation, composite validation, drift triage, offset triage
- **Stage 6** — file rename / move / archive / drift reconciliation; PR ready-for-review

Live todo list and statuses are visible at any time via the harness.

## What is already in place

- `/home/user/indicators/.claude/settings.local.json` — comprehensive allowlist
  for git, python, find/grep/awk/sed, jq/yq, diff/cmp/sha256sum, all standard
  POSIX file utils, every mcp__github__* tool, Skill(loop / simplify / review /
  security-review / update-config / fewer-permission-prompts), Agent(Explore /
  Plan / general-purpose), TodoWrite, Monitor, ToolSearch, WebFetch, WebSearch,
  ExitPlanMode, NotebookEdit. Read/Write/Edit on /home/user/indicators/**,
  /root/.claude/**, /tmp/**.
- `bible-input/`, `data/`, `tools/`, `docs/{lineage,visual-trees,sop,validation-log}/`
  — directories created.
- `anish-50-1st-combo/`, `heavy-pentagon/`, `hv-fvg-gz1-og/`, `ultra-combo/`,
  `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` — merged from
  origin/claude/add-txt-indicator-format-b4FUu into the working tree.
- TodoWrite — all 51 todos authored; Stage 0.1, 0.2, 0.3 already complete.
- `/root/.claude/plans/go-through-every-indicator-jazzy-perlis.md` — the
  master plan; cited from every artifact Claude produces.

## What WAKES Claude back up if it stops

The **CONTINUE.** keyword as the last line of any message you send. That single
word resumes the next pending todo with no further preamble.

Examples:
- "How's it going? CONTINUE."
- "I'm awake again. CONTINUE."
- "CONTINUE."

## Files Claude will produce (so you know where to look in the morning)

```
/home/user/indicators/
├── INDICATORS_INDEX.md                            ← entry point
├── docs/
│   ├── glossary.md                                ← cross-cutting concepts
│   ├── roots.md                                   ← master root catalog
│   ├── composites.md                              ← master composite catalog
│   ├── redundancy.md                              ← drift table
│   ├── version-control-diagnosis.md
│   ├── lineage/
│   │   ├── INDEX.md
│   │   └── <one file per top-level composite>.md
│   ├── visual-trees/
│   │   └── <one ASCII tree per indicator>.txt
│   ├── sop/
│   │   ├── INDEX.md
│   │   ├── root-validation.md
│   │   ├── composite-validation.md
│   │   ├── drift-triage.md
│   │   ├── offset-triage.md
│   │   └── icloud-mirror.md
│   └── validation-log/
│       └── <date>-roots.md, <date>-composites.md
├── data/
│   ├── indicators.yaml                            ← single source of truth
│   └── indicators.json                            ← derived; verified equal
├── tools/
│   └── build_lineage_cards.py
├── bible-input/
│   └── MANIFEST.md                                ← per-file branch provenance
├── <indicator-family>/versions/                   ← Stage-2 test indicators land here
└── (Stage-6 reorganisations as documented)
```

## What Claude will NOT touch unless you re-approve

- Any Pine source file outside Stage 6's itemised list
- Any file in `squarify/backtests/parse_stats_logs.py` (cited, not modified)
- Anything in `~/.gitconfig`, `/etc/`, `/usr/`
- Anything outside `/home/user/indicators/` and `/root/.claude/`
- Any push to `main` (only pushes to `claude/organize-indicators-hierarchy-8JDw1`)

---

That's it. Paste the block at the top, then sleep.
