# Heavy Weapons Single — CHANGELOG

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
