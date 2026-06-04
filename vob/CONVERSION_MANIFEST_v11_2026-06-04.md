# VOB v11 — Conversion Manifest (Pine Conversion Three Outputs)

Date: 2026-06-04 · Author: Claude Code · Mode: full-send (Anish "everything now")

## What changed vs v10 (the new feature)
Two NEW detection plots added on top of the v10 body:
1. **T3 Cluster** — fires when **2+ of the six T3 tiers** (T3a..T3f, buy OR sell)
   fire on the SAME candle. Direction-agnostic (two bulls / two bears / mixed).
2. **VOB × HW-Single Coincidence** — fires when ANY VOB T3 or ANY VOB zone marker
   (either direction) coincides on the SAME candle with ANY Heavy Weapons Single
   v3 detection. HW Single v3 is **NOT modified** — its detection math is embedded
   READ-ONLY and collapsed to a single `hws_any` boolean.

Two Pine variants were produced from this:
- **FULL** — keeps all individual T3 + zone markers + composites + the 2 new plots.
- **MULTIPLES-ONLY** — individual T3 circles + individual zone crosses removed
  (24 plotshapes commented `// [v11 MULTIPLES-ONLY removed]`); zone lines/fills,
  Nagasaki, VLB, MZ2/MZ3, and the 2 new plots kept.

## Source hashes (sha256)
| file | sha256 |
|---|---|
| v10 base (on-disk) | `f8c06ed6…87efd` |
| v11 FULL | `d5d2dc90…36210` |
| v11 MULTIPLES | `13912c6b…1b1d46` |

## Repo comparison
- Pasted chat source = on-disk v10 body + `//@version=6` header bump + `max_bars_back 5000→3000`.
  Body is byte-identical to the on-disk v10; only the header differed. The pasted
  version was NOT newer in logic, so v10 was NOT overwritten — v11 saved as new files.
- **Host version = v6** by EXPLICIT in-session instruction from Anish (suite default
  is "v5 only"; waived for this build after a smoke test proved `import
  TradingView/ta/7` + `relativeVolume()` compiles clean under v6).

## Outputs on disk
| output | label | path | repo updated |
|---|---|---|---|
| Pine v6 FULL | source indicator | `indicators/vob/versions/VOB_v11_FULL_HWcoincidence_2026-06-04.pine` | yes (committed+pushed) |
| Pine v6 MULTIPLES | source indicator | `indicators/vob/versions/VOB_v11_MULTIPLES_HWcoincidence_2026-06-04.pine` | yes (committed+pushed) |
| Pine v5 tick-friendly FULL | "Pine is a Pine Editor tick-friendly" | `indicators/vob/tick_friendly/VOB_v11_FULL_TICKFRIENDLY_2026-06-04.pine` | yes |
| Pine v5 tick-friendly MULTIPLES | "Pine is a Pine Editor tick-friendly" | `indicators/vob/tick_friendly/VOB_v11_MULTIPLES_TICKFRIENDLY_2026-06-04.pine` | yes |
| Python engine (shared) | core | `realtime-indicators/rti/vob_v11_engine.py` | yes |
| Python tick | "Python is a Python tick" | `realtime-indicators/rti/signals_tick/vob_v11_tick.py` | yes |
| Python time | "Python is a Python time-based" | `realtime-indicators/rti/signals_time/vob_v11_time.py` | yes |

The Python tick + time wrappers share ONE engine; FULL/MULTIPLES is a `mode=`
output selector (so all 4 logical Python ports = engine × {tick,time} × {FULL,MULTIPLES}).

## Tick-friendly change (only one, surgical)
`timeframe.in_seconds(timeframe.period)` returns `na` on tick resolutions (e.g.
`"10T"`), which would poison the entire HW-Single threshold ladder. Guarded with
a fallback input `tick_assumed_tfsec` (default 60). All detection plots +
alertcondition titles preserved verbatim.

## Verification performed
- v6 + `tv_ta` smoke test: **0 errors**.
- v6 append block (HWS engine + both new detections) via `pine_check`: **0 errors**, 3
  advisory warnings (pre-existing HWS `ta.*`-in-conditional patterns, faithful to source).
- v5 tick-friendly guarded append via `pine_check`: **0 errors, 0 warnings**.
- v10 body scanned for v5→v6 breaking constructs: **none present**.
- Python engine + both wrappers: import + run clean on synthetic bars (zones +
  nagasaki fire; FULL 38 keys, MULTIPLES 14 keys).
- NOTE: full 132KB single-file `pine_check` was not run (toolset can't ingest a
  local file into the compiler in one call); verified via append-isolation compile
  + targeted v6-construct scan instead.

## Unsupported / deferred constructs (for the parity stage)
- **Parity NOT claimed.** This command only PREPARES the parity handoff.
- EMA/ATR seeding in the Python engine uses first-value seeding — must be
  reconciled vs TradingView before any signal is trusted.
- `relativeVolume` delegated to the canonical `rti/tv_ta_shim.py` (never re-implemented).
- **VLB strict-ladder** is present in the Pine but NOT yet ported to Python —
  flagged for parity follow-up. MZ2/MZ3 derived in the Python wrappers from
  per-bar zone-formation fires (same rule as Pine).
- The HWS `bb_smaDiff` positive-diff SMA filter is approximated by `bdiff>0` in
  the Python engine pending parity reconciliation.
