# Version-control diagnosis (Stage-1 read-only)

Every file-system / version-control issue identified in the indicator suite. **No fixes inline** — Stage 6 ("Treatment") will reorganise.

## Working-tree state

- Local working tree at `/home/user/indicators` is on branch `claude/organize-indicators-hierarchy-8JDw1` (derived from `origin/main`).
- The `claude/add-txt-indicator-format-b4FUu` branch on remote contains 4 indicators NOT on main and a new HVDPBJPPD canonical file. Stage 1 ingestion procedure: pull these into the working branch via `git checkout origin/claude/add-txt-indicator-format-b4FUu -- <paths>` (already executed; staged for commit).
- Indicators discovered on `b4FUu` only: `anish-50-1st-combo`, `heavy-pentagon`, `hv-fvg-gz1-og`, `ultra-combo`, plus the file `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine`.

## Stub files

- `hvd-pbj-ppd/versions/HVDPBJPPD_v1.pine` — 10-line placeholder. Real source is `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` (predecessor) and now `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` (canonical, b4FUu only).

## Duplicate version labels

- `b2b-pup/versions/B2B_PUP_v4.32.pine` (LF line endings, 77.3 KB, md5 `9151c531...`) and `b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine` (CRLF line endings, 78.5 KB, md5 `9327c895...`) are both labelled `v4.32`. Normalised diff (`tr -d '\r'`) is empty — content is byte-identical. Only difference: line endings. Stage 6 should delete one and keep one with consistent line endings.

## Title / filename mismatch

- `tnt-od/versions/TNT_OD_v3.pine` (148.4 KB, internally titled `TNT Opening Drive OD v3`, dated 2026-05-08) is **newer and has more features** (HCT engine, UC placeholder, T1 RELAY, T1 STACK, en_newGate/gateStdMult).
- `tnt-od/versions/TNT_Opening_Drive_OD_v3_2026-05-04.pine` (123.0 KB, internally titled `TNT Opening Drive OD v2`, dated 2026-05-04) is older despite the v3-style filename.
- Per `tnt-od/CHANGELOG.md`, the v3 build is the canonical one. Stage 6 should either rename the older file to `TNT_OD_v2_2026-05-04.pine` for clarity, or merge their version histories.

## TNT-OD version chain (4 versions)

- `TNT_OD_v1.pine` (99.9 KB) — legacy.
- `TNT_OD_v2.pine` (123.0 KB) — internally consistent v2; same SHA as the date-stamped 05-04 file.
- `TNT_OD_v3.pine` (148.4 KB) — internally v3 (newer despite v3 filename).
- `TNT_Opening_Drive_OD_v3_2026-05-04.pine` (123.0 KB) — date-stamped 05-04 but internally v2.

The duplicate-named files (`TNT_OD_v2.pine` and `TNT_Opening_Drive_OD_v3_2026-05-04.pine` are byte-identical per `git log`).

## Mixed-indicators in one folder

- `vob/versions/` contains TWO distinct indicators:
  - `VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine` (113 KB) — VOB asymmetric T3×6 ladder.
  - `VOB_LADDER_WATCH_v1.pine` (12 KB) — staged zF→zA escalation detector. Distinct concept, distinct canonical role.
- Stage 6 should split into `vob/zone_engine/` and `vob/ladder_watch/`, or hoist the shared `f_bull_vob` engine to `vob/_shared/`.

## No "current" pointer per indicator

- No `LATEST.pine` symlink, no `current.pine` manifest, no per-indicator pointer file. Finding the current canonical version requires grepping filenames, reading `CHANGELOG.md`, and cross-referencing dates.
- Stage 6 should add `<indicator-dir>/CURRENT.pine` symlink (or manifest entry) per family.

## Inconsistent per-indicator metadata

| Dir | CHANGELOG.md | README.md | versions/ |
|---|---|---|---|
| `b2b-pup/` | ✓ | ✓ | ✓ |
| `heavy-combo-toggles/` | ✓ | ✗ | ✓ |
| `hvd-pbj-ppd/` | ✓ (b4FUu only) | ✗ | ✓ |
| `proximity-gzi-hv/` | ✓ | ✗ | ✓ |
| `squarify/` | ✓ | ✓ | ✓ + `backtests/` |
| `tnt-od/` | ✓ | ✓ | ✓ |
| `vob/` | ✓ | ✗ | ✓ |
| `anish-50-1st-combo/` | ✓ (b4FUu only) | ✗ | ✓ (b4FUu only) |
| `heavy-pentagon/` | ✓ (b4FUu only) | ✗ | ✓ (b4FUu only) |
| `hv-fvg-gz1-og/` | ✓ (b4FUu only) | ✗ | ✓ (b4FUu only) |
| `ultra-combo/` | ✓ (b4FUu only) | ✗ | ✓ (b4FUu only) |

Stage 6 should add `README.md` to every indicator family with at minimum: title, current canonical file path, key signals owned, downstream consumers.

## Squarify backtest siblings with unclear status

- `squarify/backtests/SQUARIFY_v2_BT.pine` (143.9 KB) — backtest variant, distinct from main.
- `squarify/backtests/SQUARIFY_v2_STATS.pine` (153.4 KB) — same SHA as `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine`, suggesting it's a stats-instrumented mirror of canonical.
- `squarify/backtests/parse_stats_logs.py` (7.8 KB) — Python tool, not Pine. Cite, don't touch.

## ATOMS-exposed sibling

- `squarify/versions/SQUARIFY_ATOMS_v1.pine` (151.2 KB) — companion to canonical `SQUARIFY_46_v2_2026-05-04.pine`. Per repo CHANGELOG, this exposes the ~60 atoms as separate plots for verification. Stage 6 should clarify whether it's a maintenance burden (must mirror v2 changes) or a one-shot snapshot.

## Squarify v3 retraction

- Per repo CHANGELOG.md: `squarify v3` was retracted ("over Pine 64-plot limit"); v2 is current. No `SQUARIFY_v3.pine` file in repo.

## Dead-state declarations

- `proximity-gzi-hv/versions/PROXIMITY_GZI_HV_v1.pine` and `hv-fvg-gz1-og/versions/HV_FVG_GZ1_OG_v1.pine` both declare `var float max_bull_fvg`/`min_bull_fvg`/`max_bear_fvg`/`min_bear_fvg` (lines 78-83) but never assign or read them. Janitorial flag for Stage 6.
- TNT-OD v2 declares `u5_od_max_bars` input but never references it.
- VOB Asym T3×6 declares `asym_threshold=99.0` input "Reserved for future Tier 1 asymmetric signals" — declared but unused.
- VOB Ladder Watch computes `de_escalated` (line 140) but never consumes it — dead transition flag.

## Phantom toggles

- `heavy-pentagon/versions/HEAVY_PENTAGON_v1.pine` lines 61-83: FAUNA Bull/Bear, DISP A/B/C Bull/Bear, LONG 1/2, SHORT 1/2, HV 75/150/250/500/1000, Hot Spot — all input checkboxes with NO engine wired. File header explicitly says "PHANTOM TOGGLES (reserved — no engine connected)". Stage 6 should either remove or wire engines.

## Cross-indicator drift candidates flagged for byte-diff

- B2B PUP's RVOL block has comment "Pre Mythos thresholds" (L276) — drift candidate vs Heavy Pentagon canonical thresholds.
- Squarify's `csNew3 = csNew1 AND csNew2[1]` (1-bar lagged) vs HVDPBJPPD canonical `csNew3 = csNew1 AND csNew2` (same-bar) — **CRITICAL semantic drift to reconcile**.
- B2B PUP's `gz1_dist=7` vs HV FVG GZ1 OG's `gziProximity=6` — drift candidate.
- HVDPBJPPD predecessor vs canonical: HV+D HTF mults, USE Disp `i_std_min`, GZI proximity, Long1/Long2 thresholds, ComboSet body% — all changed.
- "EXACT COPY FROM ANISH TB FOSTER v6" comment in TNT-OD line 367 implies a separate `anish-tb-foster` indicator may exist (not in this repo).

## Recommendation summary for Stage 6

1. Delete `hvd-pbj-ppd/versions/HVDPBJPPD_v1.pine` stub.
2. Delete one of the v4.32 line-ending duplicates in `b2b-pup/versions/`.
3. Rename `tnt-od/versions/TNT_Opening_Drive_OD_v3_2026-05-04.pine` → `TNT_OD_v2_2026-05-04.pine` to match its internal title.
4. Split `vob/versions/` into `vob/zone_engine/` and `vob/ladder_watch/` (or share `_shared/`).
5. Add `CURRENT.pine` symlink (or manifest pointer) per indicator family.
6. Add `README.md` to every indicator family.
7. Reconcile `csNew3` lag in Squarify vs HVDPBJPPD.
8. Byte-diff RVOL ladder across HVDPBJPPD / B2B PUP / Squarify / Ultra Combo / Heavy Pentagon / TNT-OD; pick canonical, mirror everywhere.
9. Decide fate of `SQUARIFY_ATOMS_v1.pine` (mirror or snapshot).
10. Clean up phantom toggles in Heavy Pentagon.
