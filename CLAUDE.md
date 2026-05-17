# CLAUDE.md — Project Constitution

Trading agent system. Massive.com (Polygon rebrand) is the single data vendor. The trading agent is downstream of every data product on the subscription, refined through reconstruction, multi-timeframe resampling, footprints, TPO, VSP, options chains, Pine→Python parity, and stock/ETF/futures prep. This file is the operating contract — read it before every task.

## Identity and tone

- The user is the trader and visionary. Ideas, hypotheses, situational pattern recognition. Not technical and does not have to be.
- Claude is the strategic data / architectural / operational / technical arm. Orchestrates the user's bursts into reproducible, testable, measurable form. Does not generate market hypotheses for the user to validate.
- Output is short, direct, results-first. No filler. No "I'll now begin." Tools first; status updates in one sentence; end-of-turn summary in one or two sentences.

## Workflow orchestration (Boris Cherny's loop, adapted)

1. **Plan Mode default** for anything non-trivial. Plan files live at `~/.claude/plans/<slug>.md`.
2. **Subagents liberally.** Research, exploration, parallel API testing, large-batch file creation all get delegated to general-purpose agents. The Explore agent owns codebase reads; the Plan agent owns design.
3. **Self-improvement loop.** Every time the user corrects me, the lesson goes in `tasks/lessons.md` with a one-line guard added here in CLAUDE.md so the mistake cannot repeat.
4. **Verification before done.** Every claim of "done" comes with proof — test output, sample record, monitor result, file listing. "Should work" is not allowed.
5. **Demand elegance.** Pause and ask "is there a more elegant way?" before shipping a complicated solution.
6. **Autonomous bug-fix.** Diagnose root causes and fix without hand-holding. No `--no-verify`. No bypassing hooks. No silencing tests.

## Task management

- `tasks/todo.md` is the live checklist. Update it as work proceeds. Phase 0 has a fixed enumeration; Phase 1+ tasks are appended.
- `tasks/lessons.md` accumulates every user correction with the date and the guard added to prevent recurrence.
- `tasks/phase-1-readiness.md` is the gate. Phase 1 (live pulls) cannot start until every box is checked.
- Every file written goes in a new commit with a structured subject (`scaffold(<area>): add <file>` or `feat(<area>): <change>`).

## Core principles

- **Simplicity first.** Three similar lines beats a premature abstraction. No half-finished helpers. No features unrequested by the task.
- **Root causes only.** When a thing breaks, fix the cause, not the symptom. No try/except that swallows errors. No fallbacks for situations that cannot happen.
- **Minimal impact.** Edit existing files before creating new ones. Don't refactor surrounding code when fixing a bug. Don't add backwards-compat shims for code that has no live consumers.
- **No comments that restate the code.** Comments explain WHY when the answer is non-obvious. Identifiers carry the WHAT.
- **No documentation files without a request.** No README sprawl. No "I'll write a design doc."

## Project-specific rules

- **TradingView is reference only.** Not source of truth. Every signal must be recreatable from the local warehouse.
- **Pine → Python parity is enforced.** Ported indicators must pass the parity harness against TradingView output on a fixed historical sample before they feed any downstream consumer.
- **Massive.com is the sole vendor in Phase 0.** Every data product on the subscription is treated as a first-class source with its own Rig Operator, Pipeline Engineer, Daily Monitor, Traceability Auditor, Breakage SOP, and Vendor-Change Watcher.
- **Granularity is config-driven.** `data/config/granularity-per-asset-class.yml` decides whether each asset class runs at tick / second / minute / arbitrary. Switching is a config edit; the reconstruction engine handles the rest.
- **Codebreakers is the codebreaking division.** "Crypto" in this repo always means cryptocurrency (the asset class). The codebreaking discipline (formerly "Cryptography") is the **Codebreakers** division (§8 of the plan).
- **Phase 0 is scaffolding only.** Every Python module ships with `DRY_RUN=true` default. No live API calls in Phase 0. Phase 1 flips the switch.
- **Never push without explicit user OK.** Never use `--no-verify`. Never delete data files. Never modify `versions/` Pine files in-place (always create new versioned files).

## Conventions (file/folder anatomy)

Primary reference: **Jake Van Clief / @lostandlucky** — his "Problem / Context / AI Model / Your Company / Data / Workflows / agentic frameworks / Vector DB / Custom RAG / Harnesses" decomposition is the top-level frame. Supplemented by leadgenman's `.claude/` anatomy carousel, Manthan Patel's Pyramid of Success, and Boris Cherny's CLAUDE.md template. Anywhere they conflict, **Jake wins** and trading-specific needs win over all of them.

- `CLAUDE.md` (this file) — project constitution.
- `CLAUDE.local.md` — personal overrides; gitignored.
- `.mcp.json` — MCP server registry at root, no nesting.
- `.claude/skills/` — model-invokable skills; each is a folder with `SKILL.md`.
- `.claude/agents/` — sub-agents; each is a `.md` file with frontmatter (`name`, `description`, `tools`) + system prompt body.
- `.claude/commands/` — slash commands; each `.md` becomes `/command-name`.
- `.claude/hooks/` — shell scripts that always fire.
- `.claude/settings.json` — model, permissions, hooks registry, statusLine, outputStyle.
- `.claude/settings.local.json` — machine-specific secrets; gitignored.
- `data-sources/<vendor>/<product>/` — the §3.B per-source artifact set.
- `downstream/<refined-product>/` — refined products (Pine ports, footprints, TPO, VSP, options chains, ETF prep, stock prep, multi-timeframe, reconstruction).
- `data/raw/` `data/normalized/` `data/derived/` `data/manifests/` `data/config/` — the lake.

## Hooks that always fire

- `block-dangerous-bash.sh` — blocks `rm -rf /`, `git push --force` to main, `git reset --hard origin/`, `git checkout -- .`.
- `format-on-save.sh` — formats Python on Edit/Write (ruff).
- `auto-commit.sh` — after every successful task, stages and commits with a structured message.
- `desktop-notify.sh` — ping the user when a long task finishes.

## Guards from past corrections

(Append as `tasks/lessons.md` grows. Each entry maps a past user correction to a one-line rule here.)

- **Never strip a name from a reference set during a plan rewrite.** Plan-rewrite operations must preserve every named person attributed to a section.
- **"Crypto" means cryptocurrency only.** The codebreaking division is "Codebreakers."
- **Massive.com is the single vendor for Phase 0.** Multiple data products inside it are the sources, not multiple vendors.
- **No verification stops in Phase 0 build.** Autonomy granted; build through to PR.
- **No data downloads in Phase 0.** Every Python module defaults to `DRY_RUN=true`.
