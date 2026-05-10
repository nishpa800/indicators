# TNT-OD v3 (2026-05-04) — extraction report (compact)

Source: `tnt-od/versions/TNT_Opening_Drive_OD_v3_2026-05-04.pine` · 1802 lines · Pine v5 · internal title `"TNT Opening Drive OD v2"` (filename says v3, internal says v2 — drift)

**Filename/title mismatch**: per CHANGELOG.md the v2 build is dated 2026-05-04 (THIS file) and v3 build (HCT/UC/T1 RELAY/T1 STACK/en_newGate) is in `TNT_OD_v3.pine` dated 2026-05-08. So the date-stamped file is internally v2; `TNT_OD_v3.pine` is newer with v3 features. Bible treats `TNT_OD_v3.pine` as canonical for full TNT-OD feature set.

## Summary

Three confluence engines (VOB ema-cross OB, ANISH swing-OB cross, FLUX swing-pullback) feed a TNT 1.0 zone array. Zones drive Napalm/Charge/Return/CONT, plus a TNT 2.0 super-zone aggregator. A parallel "USE V5" pipeline produces RVOL/WMD/FAUNA/PBJ/CS1/PUP/PPD/HV1000/DISP atoms. Final layer: Tier 1 / Tier 2 / Density / UU / WBUSH plots + per-bar Bloomberg-format alerts.

Counts: 45 plotshapes (49 in v3), 0 alertcondition, runtime alert() calls everywhere.

## Roots (canonical)

| Canonical | Source | Plain-English |
|---|---|---|
| `tnt-od::TNT_RAW_BULL` / `TNT_RAW_BEAR` | 246-479 | VOB ema-cross OB + ANISH swing-OB cross + FLUX pullback all confirm in same window AND zones overlap AND volume/EMA-slope/RSI synergy gate AND min-bar-gap cooldown elapsed. Defaults: `SENS=100`, `SWING_LEN=10`, `EMA_FAST=SENS`, `EMA_SLOW=SENS+13`, `ATR_VAL=ATR(200)`, `ATR_MULT=3.5`, `ATR_MIN=0.5`, `MIN_SIG_GAP=EMA_SLOW`, `CONF_WINDOW=EMA_SLOW*2`. |
| `tnt-od::OD` (Opening Drive shell) | 241, 251-254, 1384-1395 | Session-first-bar gate; `u5_od_max_bars=1` input. Roots only as gating boolean. |
| `tnt-od::NAPALM_BULL` / `NAPALM_BEAR` | 514-529 | Directional displacement bar that pierces an active opposing TNT zone level. |
| `tnt-od::CHARGE_BULL` / `CHARGE_BEAR` | 530-548 | Displacement bar violating stored ChargeLevel; pushes new same-direction ChargeLevel to maintain alternating ladder. |
| `tnt-od::RET_BULL_TNT` / `RET_BEAR_TNT` | 481-504 | First retrace into still-active TNT zone after breakout, hits programmable retracement (RET_TNT_PCT=100). Single-fire per zone. |
| `tnt-od::TNT2_BULL` / `TNT2_BEAR` (Super TNT) | 550-578 | ≥2 same-direction TNT-family events (TNT/NPM/effective-Charge) accumulate plus fresh same-direction event, with cooldown. |
| `tnt-od::SUPER_TNT_BULL` (raw_superTNTBull) | 550 | `raw_bullTNT AND raw_bearCharge` (and bear mirror). |
| `tnt-od::CONT_BULL` / `CONT_BEAR` | 593-624 | Rapid-fire proximity event: Charge after Return, OR TNT/TNT2 after recent Charge, OR Charge after recent TNT/TNT2. `SUDDEN_PROX=3`. |
| `tnt-od::DISP_BULL` / `DISP_BEAR` (Engine #1) | 506-512 | bar[1] body/range > DISP_STD_X * stdev(range, DISP_STD_LEN); bar[0] FVG confirms. Defaults: `DISP_STD_LEN=100`, `DISP_STD_X=5`. |

USE V5 inline ports (cross-refs):

| Local | Cross-ref to | Source |
|---|---|---|
| `u5_PBJBull` / `u5_PBJBear` | `hvdpbjppd::PBJ` | 725-823 (VWMA(5)±2*ATR(10) supertrend + PBJ pre-arm) |
| `u5_FAUNABull` / `u5_FAUNABear` | `squarify::FAUNA` | 683-710 |
| `u5_SAAB`, `u5_KRATOS`, `u5_RVOL1xB`, `u5_RVOL1xR`, `u5_GS`, `u5_MOAB`, `u5_PENTAGON`, `u5_WTC`, `u5_HIROSHIMA`, `u5_NAGASAKI` | `heavy-pentagon::*` | 636-678 |
| `u5_PUP` / `u5_PPD` | `b2b-pup::PUP` / `PPD` | 719-723 |
| `u5_CS1_BULL` / `u5_CS1_BEAR` | `squarify::COMBOSET1` | 825-873 |
| `u5_HV1000` | HV-rank primitive | 681 |
| `u5_DISPBull` / `u5_DISPBear` | (separate from Engine #1 disp) | (within USE V5 block) |

## Composites

Tier-1: B2B Napalm (`p_b2bBull`/`p_b2bBear`, offset=-1), RC NPM+TNT (`sig_rcNTBull`, offset=-1), FUSE (`p_fuseBull`, offset=0 — sequential cascade NPM→TNT→CONT within SUDDEN_PROX), CATALYST (`p_catBull`, offset=-1 — Napalm + CS1), PBJ+NPM (offset=-1), PBJ+TNT (offset=0), IGNITE T+C (offset=0), IGNITE N+C (offset=-1), DYNAMITE (offset=-1 — bespoke 5σ bar[1]+bar[2] + FAUNA + FVG).

Tier-2 ENRICHED variants: TNT ENRICHED (offset=0), NPM ENRICHED (offset=-1), CONT ENRICHED (offset=0), RC TNT+RET ENR (offset=0), RC RET+NPM ENR (offset=-1), PBJ+RET ENR (offset=0).

Density 1/2/3 (`p_d1b/p_d2b/p_d3b`, all offset=-1) — counts of denVisBull events in rolling Y-bar window.

UU+TNT-ANY / UUU+TNT-ANY / UUUU+TNT-ANY (all offset=-1) — paths pA-pG over PBJ/DISP/FAUNA/SAAB/RVOL1x/GS plus TNT-detection-in-window.

WBUSH+TNTOD-ANY Bull/Bear/Neutral (offset=0) — Heavy Pentagon family × USE V5 displacement classifier × any TNTOD plot fired same bar.

## Caveats

- File internally titled v2; v3 features (T1 RELAY, T1 STACK, HCT engine, UC placeholder, en_newGate, gateStdMult) are in `TNT_OD_v3.pine` (not this file).
- No alertcondition() — all alerts via runtime `alert()` in DIRECTION | FIRST_STATUS | NAME format with `freq_once_per_bar_close`.
- Aggregation toggle `masterAggregate` (default ON) bundles non-Nagasaki alerts into one combined message.
- Apex break / Failed-Apex flip / Long1/Long2/Short1/Short2 / Boom Hunter Omega names from earlier briefs DO NOT appear in this file.
- "OD" primitive is anemic — only session-first-bar boolean + unused `u5_od_max_bars` input.
- "Pentagon" in this file = WMD tier (relativeVolume bin), NOT geometric pentagon shape.
