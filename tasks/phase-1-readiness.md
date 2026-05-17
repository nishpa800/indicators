# Phase 1 readiness gate

Phase 1 (live data pulls from massive.com into the warehouse) cannot begin until every box below is checked. Each box must be verified by the named owner with a linked artifact (log, test output, sample record).

## Foundation

- [ ] `CLAUDE.md` exists and is current
- [ ] `.gitignore`, `.mcp.json`, `.claude/settings.json` committed
- [ ] All four hooks executable and wired in `.claude/settings.json`
- [ ] `.claude/settings.local.json` exists (gitignored) with `MASSIVE_API_KEY`, `S3_ACCESS_KEY`, `S3_SECRET`, `S3_ENDPOINT`
- [ ] Auto-commit hook tested: produces one commit per file written

## Sub-agents (`.claude/agents/`)

- [ ] All Rig Operator agents (REST × all sub-sections, WebSocket × 6 asset classes, Flat-files × 5 buckets) — file present, no stubs
- [ ] Pipeline Engineer, Strategic Alignment Steward, Daily Monitor, Traceability Auditor, Breakage SOP Owner, Vendor-Change Watcher
- [ ] Reconstruction Engineer, Multi-Timeframe Resampler, Footprint Builder, TPO Builder, VSP Builder
- [ ] Options Chain Builder, ETF Prep, Stock Prep, Pine→Python Converter, Parity Tester, Granularity Switcher
- [ ] code-reviewer, debugger, security-auditor, data-trace-auditor

## Slash commands (`.claude/commands/`)

- [ ] `/commit`, `/pull-massive-com`, `/inventory-massive-com`
- [ ] `/recreate-candle`, `/switch-granularity`
- [ ] `/build-footprint`, `/build-tpo`, `/build-vsp`
- [ ] `/port-pine`, `/parity-check`

## Skill (`.claude/skills/massive-com-download/`)

- [ ] `SKILL.md` with frontmatter (`name`, `description`) and body
- [ ] `client/rest_client.py` — auth, retry, rate-limit, pagination — passes DRY_RUN smoke
- [ ] `client/websocket_client.py` — auth, reconnect, backpressure — passes DRY_RUN smoke
- [ ] `client/s3_client.py` — boto3 wrapper for `files.polygon.io` — passes DRY_RUN smoke
- [ ] Per asset-class modules for stocks/options/futures/indices/forex/crypto/economy/alternative/partners — all have at least one passing DRY_RUN unit test
- [ ] `inventory_probe.py` runs against the local llms.txt cache and produces an updated INVENTORY table
- [ ] `DRY_RUN.md` explains the default and how to disable

## Per-product artifacts (`data-sources/massive-dot-com/<product>/`)

- [ ] `_template/` skeleton committed; every product folder stamped from it
- [ ] Every product has README, ROLES, STRATEGIC-ALIGNMENT, rig-operator/, pipeline/, monitor/, traceability/, sop/, vendor-change-watcher/
- [ ] Every `sop/BREAKAGE.md` documents at least 3 failure modes with recovery procedures
- [ ] Every `monitor/daily-check.sh` is executable and runs under DRY_RUN
- [ ] Every `traceability/nightly-trace.sh` is executable and runs under DRY_RUN

## Downstream consumers (`downstream/`)

- [ ] `pine-to-python/` — converter, AST mapper, runtime shim, parity harness; at least one ported indicator passes parity
- [ ] `footprints/`, `tpo/`, `vsp/` — builder + SPEC + unit tests on synthetic data
- [ ] `options-chains/` — greeks, IV surface, term structure modules + SPEC
- [ ] `etf-prep/`, `stock-prep/` — modules + SPEC
- [ ] `multi-timeframe/` — resampler with 30+ timeframe configs
- [ ] `reconstruction/` — tick→candle with time / tick / volume / dollar / range / renko / kagi bar definitions

## Data lake (`data/`)

- [ ] `raw/`, `normalized/`, `derived/`, `manifests/` folder skeleton exists
- [ ] `config/granularity-per-asset-class.yml` exists with user-confirmed defaults
- [ ] `config/timeframes.yml` lists the 30+ timeframes
- [ ] `config/bar-types.yml` lists time/tick/volume/dollar/range/renko/kagi
- [ ] `config/derived-products-per-asset-class.yml` exists with defaults

## Open items resolved

- [ ] **NYSE order-imbalance feed** — confirmed source (WebSocket channel? flat-file prefix? add-on endpoint?) and Rig Operator wired
- [ ] **Account subscription scope** — `inventory_probe.py` has run successfully (DRY_RUN) and any products not on the subscription are flagged in `data-sources/massive-dot-com/INVENTORY.md`
- [ ] **Hardware** — 8×26 TB drives installed, RAID configured, warehouse path mounted (or path-aliased to the 4 TB hot drive until install)

## Phase 1 kickoff criteria

When every box above is checked, the user runs `/switch-granularity all <default>` to confirm the granularity-per-asset-class config, then `/pull-massive-com --dry-run` for a final no-op pass, then `/pull-massive-com` to start live ingestion. The Daily Monitor and Traceability Auditor fire immediately and continue forever.
