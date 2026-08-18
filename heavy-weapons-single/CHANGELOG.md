# Heavy Weapons Single — CHANGELOG

## v3.2 DISP 9 — 2026-08-18 (W-INDSTUDY transform; operator order 2026-08-18 /goal)

**Heavy Weapons Single v3.2 DISP 9** (time, `HW3.2 D9`) + **Heavy Weapons Single v3.2 [tick-friendly] DISP 9**
(tick twin, `HW3.2TF D9`, same wave). Base = the operator's LIVE "HW v3 TF 9" export
(`sources/HW_v3_TF9_DISP9_operator-live_2026-07-23.txt`, CRLF sha256 16b547d9…, LF-normalized at intake) —
the DISP-9 lineage (D9 studies + Pent+D), NOT the june7-based v3.1; v3.1's master 4K/NAGA VP gate is
NOT carried (not requested). Generator: lake `scripts/ind/build_hw_v3_2.py` (one edit list → both twins).

- **ALERT IFF CHECKBOX (the headline law):** an alert line is emitted IFF its lane checkbox is ON.
  Base defect: four alert branches carried NO checkbox term — `HCT BULL`, `HCT BEAR`,
  `PENT+HV1K+DISP`, `PENT+HV500+DISP` (the operator received Pentagon alerts with both boxes
  unchecked). Every alert branch now carries the IDENTICAL boolean as its plotshape (chart == alert,
  L-63). Gate: `validation/wrappers/hw_alert_iff_gate.py` — base REFUTED D=10, v3.2 PROVED D=0 per twin,
  anti-fixture 3/3.
- **Pent+HV1K+D → Pent+4K+D:** `is4KNow = volume == ta.highest(volume, hv4k_len)` (input "4K Lookback
  (bars)" default 4000, editable 1..5000); lane = Pentagon AND 4K AND same-candle 5σ displacement.
- **Pent+HV500+D → Pent+NAGA+D:** Pentagon AND Nagasaki (all-time-high volume, bar[0]) AND same-candle
  5σ displacement.
- **NEW Naga + ANY Bull / Naga + ANY Bear** (global toggles, under Nagasaki; default ON; own input.color):
  Nagasaki + ≥1 same-candle bullish/bearish HW detection, partners read at the DETECTION level
  (checkbox-independent); the alert line NAMES every partner:
  `NAGASAKI + ANY BULL (SAAB, LONG 1, D9 BULL STUDY)`. Partners = singles (+LONG/+SHORT gated as they
  plot), WTC/Hiroshima routed by the coincident momentum side, LONG 1-5 / SHORT 1-2, sequences, B2B,
  FAUNA, D9 studies. NOT partners: HCT composites, Pentagon specials, offset −1 lanes (HV, Disp, Consec Disp).
- **DEFAULTS = the operator's Inputs-dialog screenshots (2026-08-18 10:07/10:08):** 51 checkboxes
  flipped true→false, 12 numeric defaults changed (Reg/Cum/Body floors 85, sequence lower thresholds 7,
  Disp σ 9/8/7/9, D9 σ 9.9 (step 0.1), HCT disp σ 9, Info Panel OFF). Census gate:
  `validation/wrappers/study_defaults_gate.py` + `validation/indstudy/hw_v32_defaults_expected.json`
  (98/98, anti 2/2).
- **A8 side-typing:** sequence plot keys typed — UU/UUU/UUUU titled Bull, DD/DDD/DDDD titled Bear (chart text= unchanged; v3.1 precedent).
- Info-panel header → "HW SINGLES v3.2 DISP 9"; GATES footer documents P+4K / P+NAGA / N+ANY / iff law.
- TV plot units: 53/64 (49 plotshapes + 4 dynamic input-color args); 0 alertconditions; 0 plain plot();
  graphic objects: 1 site (`table.new`, the info panel, default OFF; no label/line/box).


## v3.1 — 2026-08-10 (W-INDSTUDY transform; operator order 2026-08-10)

**Heavy Weapons Single v3.1** (time) + **Heavy Weapons Single v3.1 [tick-friendly]** (tick twin, same wave).
Base: the v3 imports (time) / june7-conversion tick-friendly build (tick), sha-pinned at 57fc926.

- **MASTER VP GATE (the headline law):** every VP in the study now fires IFF **4K** or
  **Nagasaki** fires on the candle the VP marks. Offset −1 lanes (HV ladder, Disp) test the
  marked bar[1] via vpGatePrev; all bar[0] lanes test vpGateNow. The aggregated alert carries
  the identical gate term per lane — chart and alert can never disagree (L-63). Master toggle
  defaults ON; OFF restores v3.0 ungated behavior.
- **4K engine added:** `det_HV4K = conf and volume >= ta.highest(volume, i_4k_len)[1]`,
  lookback input floor 4000 (HV-ladder 4K rung; canonical FBF/BEDROCK construction).
- **Three dedicated Nagasaki combo lanes** (sig_/fire_/alf_ chains, 111 law; real plotshape
  VPs per CS-1/L-61; each with its own input.color per the visual-identity law):
  - **Nagasaki + ANY HW** — Nagasaki + ANY other same-candle HW v3 detection (side-agnostic;
    flag @ bottom). FAUNA ⊂ LONG/SHORT; offset −1 lanes excluded from the same-candle basket.
  - **Nagasaki + ANY LONG (1-5)** — arrowup below bar.
  - **Nagasaki + ANY SHORT (1-2)** — arrowdown above bar (this study's short tiers are 1-2).
  - Alert texts: `NAGASAKI + ANY HW` / `NAGASAKI + ANY LONG` / `NAGASAKI + ANY SHORT`.
- **A8 side-typing:** sequence plot keys side-typed — UU/UUU/UUUU now titled Bull,
  DD/DDD/DDDD titled Bear (chart text= unchanged).
- **A13:** shorttitles cut to ≤10 chars: `HW3.1` (time), `HW3.1 TF` (tick).
- Info-panel header corrected (base said "HW SINGLES v2"); GATES footer documents the master gate.
- TV plot units: 53/64 (45 base plots + 3 new + 5 dynamic input-color args); 0 alertconditions.

---


Newest first.

---

## v3 tick-friendly — 2026-06-13
**Files:**
- `versions/HEAVY_WEAPONS_SINGLE_v3.pine` — as-received (verbatim, = the pasted v3 / repo import).
- `tick_friendly/HEAVY_WEAPONS_SINGLE_v3_tick_friendly.pine` — **load this on tick charts.**
- (DR copy: `dateroll/HEAVY_WEAPONS_SINGLE_v3_DR.pine`, shorttitle `HW Single v3 DR`.)

**Two tick-safety fixes (logic otherwise untouched; 45 plots, 0 data-window — gate PASS):**
1. **RE10023 anchor.** All 3 `tv_ta.relativeVolume(...)` calls used `reg_anchorTimeframe`
   (`input.timeframe("")` → blank = chart TF → `timeframe.change()` throws on tick bar 0). Now
   routed through `reg_anchorSafe` (`"D"` on tick, `""` on time = parity).
2. **`tfSec` guard.** `tfSec = timeframe.in_seconds(timeframe.period)` is na/0/unreliable on tick,
   which kills the per-TF RVOL threshold table. Guarded via `str.endswith(timeframe.period,"T")`
   with a 10s fallback.

**Not present (checked):** no `time(timeframe.period, …)` session calls (RE10023 #2), no bar-scan
"yesterday" loop (RE10008), plot count 45 ≤ 64. Live TradingView compile not performed here —
status is 🟡 (fixed in code, awaiting your load) in TICK_FRIENDLY_INDEX.md.
