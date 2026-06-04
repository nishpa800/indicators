# Pine Conversion — Three Outputs Manifest
indicator: heavy-weapons-nra
title: "Heavy Weapons NRA + GZI/FVG + Matrix Combos 2 bodies not 1 NRAFR"
shorttitle: "RVOL NRAFR x2"
date: 2026-06-04
command: /pine-conversion-three-outputs

## Source intake & repo comparison
- pasted_source_sha256:        cc625933172c6994f2fa3e4be793be05992c61cfed8bf540be9b8e09d5cb4284
- canonical_version_sha256:    cc625933172c6994f2fa3e4be793be05992c61cfed8bf540be9b8e09d5cb4284   (== pasted; saved verbatim)
- prior_import_sha256:         d89c82d48c3bef0d4380658835ae74d0c4d53710f8b4cac86e87040b6a69cbbf
- repo_comparison: pasted vs prior import = FUNCTIONALLY IDENTICAL
  (diff = 3 removed comment lines only; zero logic/plot/alert change).
- repo_updated: YES — new canonical home created at
  indicators/heavy-weapons-nra/ (versions/ + tick_friendly/). Prior copy lived
  only under imports/; this is the first real version home.

## Output 1 — Pine is a Pine Editor tick-friendly
- path: indicators/heavy-weapons-nra/tick_friendly/HEAVY_WEAPONS_NRA_v1_tick_friendly.pine
- sha256: 466c5bf521cd7ace46632c11154e49ac4dd2e70108f7022655b0ddef4fbf932f
- label: "Pine is a Pine Editor tick-friendly"
- changed constructs vs canonical (the ONLY diffs):
  * tfSec: was `timeframe.in_seconds(timeframe.period)` (=0/na on tick charts).
    Now guarded: new input `tickTfSecOverride` (0=auto) + `TICK_FALLBACK_SEC=10`
    fallback when tfSecRaw<=0/na. Pins/keeps the per-TF threshold bucket defined.
  * Affects BOTH threshold tables: f_rvol_1x_threshold, f_gs_moab_threshold.
- detection plots preserved: YES (all 22 fire_* plotshape calls unchanged).
- alertconditions preserved: YES (all 22 alertcondition names unchanged).
- Pine v5: YES (//@version=5 retained).

## Output 2 — Python is a Python tick
- path: realtime-indicators/rti/signals_tick/heavy_weapons_nra.py
- sha256: 7b46c13648a59417656910c793b30244f89bb3706e6eb2485aa37f469acbca1b
- class HeavyWeaponsNRATick.update(TickBar) -> dict{fires:{<PLOT_KEYS>}}
- tf_sec supplied explicitly (default 10 = tick-friendly fallback bucket).
- relativeVolume via canonical rti.tv_ta_shim.relative_volume (NOT re-implemented).
- smoke test: 180 synthetic 1m bars, ran clean, Nagasaki fired (running-max path).

## Output 3 — Python is a Python time-based
- path: realtime-indicators/rti/signals_time/heavy_weapons_nra.py
- sha256: a0cc56d773c07a0975fcc76d93707eb3f958e8ea2fdd22bd80f7f885f994b12a
- class HeavyWeaponsNRATime(HeavyWeaponsNRATick) — REUSES the single tick core,
  only rebinds tf_sec to wall-clock seconds via tf_seconds(timeframe).
- smoke test: 180 synthetic 1m bars, ran clean, tf_sec=60.

## Unsupported / parity-risk constructs (handoff items — parity NOT accepted)
- line.new mitigation drawings (mitLvl): visual-only in Pine; omitted from Python
  (no plotting), removal logic preserved. No effect on fire_* booleans.
- R1 ta.sma na-handling for bb_smaDiff (bb_positiveDiff has na entries): Python
  averages non-na entries only; MUST be pinned vs TV plotted value.
- R2 ta.atr seeding (SMA seed + Wilder RMA): verify vs TV.
- R3 auto threshold = ta.cum((h-l)/l)/bar_index is na on bar 0: handled as None.

## Binary-law note
Matrix combos offset 0, FVG combos offset -1 — preserved as native plot offsets
in PLOT_KEYS. This command preserves all detection plots 1:1 and does NOT collapse
them; the 1-or-0-per-physical-bar collapse is the downstream combo-chain's job.

## Parity
NOT ACCEPTED. This command prepares a parity handoff only.
