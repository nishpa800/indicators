# HV+D ↔ PBJ ↔ USE — CHANGELOG

## 2026-05-10 — `HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine`

Anish-declared canonical version. Title: `HV+D ↔ PBJ ↔ USE THIS IS THE
ONLY FUCKING ONE` (shorttitle `HV+D↔PBJ ONLY`). Pine v5.

The decoupled-pipeline architecture is now formalized in the file header
with mandatory rules:

- **Pipeline A (HV+D)** — volume rank + stdev candle range + FVG only.
  Emits `hvd_fire_bull` / `hvd_fire_bear`. Fires bar N, describes N-1,
  plots `offset=-1`.
- **Pipeline B (PBJ/PB)** — Zoo MA + Supertrend + PB&J filter only.
  Emits `sigBullPBJ`, `sigBullPB`, `sigBearPBJ`, `sigBearPB`. Fires N,
  describes N, `offset=0`.
- **Pipeline C (USE Alarm)** — RVOL, FAUNA, Disp, PBJ, PP, Combo Sets,
  Boom Hunter, etc. Emits all `fire_*` booleans (45 signals). Fires N,
  describes N, `offset=0` (most signals).
- **Pipeline D (Triple Co-occurrence)** — pure AND gate over
  `hvd_fire_*` ∧ `sigBullPBJ[1]/sigBullPB[1]` ∧ `use_any_*[1]`. Plot
  `offset=-1`. Touches zero pipeline internals.

Plus a new **Back-to-Back HV+D** section: detects two consecutive HV+D
candles, with PBJ-or-PB qualifiers, with three-way mutually exclusive
plot variants (`b2b_bull_nopb` / `b2b_bull_pb` / `b2b_bull_pbj` and
bear mirrors). Six toggleable plotshape + alert pairs.

USE plotshapes: 22 bull, 21 bear (Tier 0 SUPER/SD, Tier 1 streaks/
patterns, Tier 1B Combo Sets, Tier 1C Chains, Tier 2 Floor/Roof/2F/PH,
Tier 3 HW). Pipeline D plots 4 more co-occurrence shapes. Pipeline A
plots 2 standalone HV+D shapes plus 4 HV+D↔PBJ co-shapes.

Imports `TradingView/ta/7` (Pine v6 lib — TV accepts cross-version lib
imports as long as the script's own version is compatible). Library is
used by both Pipeline C engines (RVOL, Long/Short).

## 2026-05-05 — `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine`

Earlier 4.26 source variant (1939 lines). Retained for version history.

## v1 — 2026-05-05 — `HVDPBJPPD_v1.pine`

Audit stub (10 lines). Placeholder pointing to TradingView chart entity
8A6Sm9 and `HVDPBJPPD_v1_AUDIT.md`. The full source body was not saved
in this file at the time. The 2026-05-10 file above supersedes it.
