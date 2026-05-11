# Reference: Python port usage (Phase M pipeline)

Path B is the fallback for TV-firing verification when Path A is unavailable. The Python ports live in the separate `realtime-indicators` repo (`~/code/anish/realtime-indicators/` on Anish's Mac, not pushed to GitHub at time of writing).

## When Path B works

- Stateless composites (no `var` variables tracking session state)
- Single-bar booleans
- Composites that depend on already-fired primitives via `[1]`, `[2]` etc.

## When Path B does NOT work

**Known limitation** (per `docs/sop/phase-m-runner.md`): the runner instantiates fresh detection-class state per `detect()` call. Stateful composites silently return zero.

Stateful composites include:
- Combo Chain (4-bar rolling window with min-hits + PBJ co-presence)
- B2B PUP S-plots that track session state (e.g. `pp_sessionFirstBarIdx`)
- VOB Ladder Watch (zF → zA escalation tracking)
- Squarify session-tied detections (`sessionBarCount`, `od_max_bars` gates)
- TNT-OD T1 RELAY / T1 STACK (visual-bar-aligned cross-bar tracking)
- Any composite using `var ...` initialization

For these, FALL BACK TO PATH A.

## Running the pipeline

From the `realtime-indicators` repo root:

```bash
cd ~/code/anish/realtime-indicators
python3 scripts/phase_m_run.py --target=<canonical> --pack=<pack> --symbol=<symbol> --timeframe=<tf> --window=<bars>
```

Args:

- `--target` — canonical detection-plot name (e.g. `heavy-pentagon::SAAB`)
- `--pack` — Python pack the detection lives in (e.g. `heavy_combo`, `primitives`, `tnt_od`)
- `--symbol` — e.g. `ES1!`
- `--timeframe` — e.g. `5m`
- `--window` — lookback in bars (default 5000)

Output: a JSON list of `{bar_index, timestamp, ohlcv, fired}` records.

## Pack-to-canonical mapping

Anish's ports (per the Stage 7.5-7.8c handoff comment):

| Pack | Canonicals covered |
|---|---|
| `offset_rules` | offset-rule primitives (not validation targets) |
| `anish_stack` | anish-50-1st-combo + anish-tb-foster |
| `primitives` | disp-4x, hv-fvg-gz1-og, proximity-gzi-hv, pb-pbj, hv-ladder × 2 |
| `heavy_combo` | heavy-pentagon + heavy-combo-toggles (15 Heavy Combos) |
| `heavy_rvol` | heavy-uncap + heavy-weapons |
| `vob` | vob-asym + vob-ladder-watch + vob-single-sens |
| `swings` | yin-yang × 2 + e3-f2-cluster |
| `ultra_combo` | Unified Combo + Combo Chain |
| `hvd_pbj_ppd` | Floor / 2F / Rooftop / Penthouse + Combo + CC + LSC |
| `b2b_pup` | All 37 S-plots (stateful ones stubbed) |
| `fauna_shifu` | Jumbo CIA + SHIFU + FAUNA+ |
| `tnt_od` | TNT-OD all tiers (3 WBUSH stubbed) |
| `squarify` | 35 detections (15 stubbed for state) |

If your validation target is in this table AND it's not stateful, Path B is feasible. Otherwise Path A.

## Subagent contract (Phase 3 via Path B)

Same shape as Path A — a fire-bar list per location. The subagent runs `phase_m_run.py` and returns:

```yaml
target: <canonical>
location:
  pack: <e.g. ultra_combo>
  pine_indicator: <e.g. ultra-combo>
fire_bars:
  - timestamp: <ISO>
    bar_index: <int>
    symbol: <e.g. ES1!>
    timeframe: <e.g. 5m>
fire_count: <int>
status: COMPLETE | BLOCKED
blocked_reason: <if BLOCKED — likely "stateful composite returns zero">
```

## Comparing Path A vs Path B fire bars

When both Path A AND Path B are available, run BOTH and intersect:

- Bars where Path A AND Path B fire — high confidence
- Bars where ONLY Path A fires — could be Path B bug (stateful state-threading) OR Pine bug Path A captures
- Bars where ONLY Path B fires — likely Pine source the logger isn't reading correctly (check `input.source()` mapping)

Path A is the chart-truth. Path B is the Pine-source-truth. They should agree; when they don't, drill down.

## Phase M state-threading status

Per Anish's 2026-05-10 PR handoff comment:

> Known limitation: the runner instantiates fresh state per `detect()` call, so stateful packs (most heavy composites) silently return zero on real data. Path A TV loggers stay primary for Stage 4 verification until Phase 2 state-threading lands.

For now: Path A is primary. Path B is opportunistic. Document the path used in the validation report.
