# 1st PUP FAUNA → **LTF** — Detection Plots: Current vs. Additional Conditions

**Base study:** `Jumbo CIA ★ FIRST BAR ONLY FAUNA FIXED★` (shorttitle `1st PUP FAUNA`)
**New study:** `Jumbo CIA ★ FIRST BAR ONLY FAUNA FIXED★ LTF` (shorttitle `1st PUP FAUNA LTF`)
**File:** `first-pup-fauna/versions/FIRST_PUP_FAUNA_LTF_v1.pine`

> This is a **separate Long-Timeframe (LTF) build**. The original is untouched. Every *underlying*
> `sig*` definition is kept **verbatim** — the LTF conditions are appended at the plot/alert layer
> only (via gated `g_*` booleans), so combos that internally reuse a raw signal are not disturbed.

---

## The two overarching additional conditions (applied to **every** detection plot)

1. **Require `1k` OR `Nagasaki`.**
   - **`1k`** = a **1000-bar volume high**: `volume == ta.highest(volume, 1000)` — the bar's volume is
     the single highest across the last 1000 bars. (Suite-canonical "HV 1000 / 1K" tier — see
     `nova-volume/DEFINITIONS_HV_NAGASAKI.md` and `hv to 1k`.)
   - **`Nagasaki`** = **HEV / all-time-high volume**: `volume > maxVolEver` (the file's existing
     `sigNagasaki` trigger). Per the suite definition, **Nagasaki ≡ HEV**.
   - Implemented as `ltf_volGate = ltf_1k or sigNagasaki`, where `ltf_1k = conf and (volume == ta.highest(volume, 1000))`.
2. **Require displacement** — but **only if the detection did not already require it.** Detections that
   already require displacement keep their existing definition unchanged and only get the volume gate.
   Direction-matched: bullish plots add `sigDISPBull`, bearish plots add `sigDISPBear`.

**Gate evaluation bar** matches how each signal already treats its own timing:
`offset 0` (current bar) for current-bar detections, `[1]` for the FAUNA+ family + Katana (they describe
the prior bar / plot at `offset=-1`), `[yy_rightBars]` for Typhoon (swing / first-bar offset).

---

## Comparison Table

| # | Detection Plot | Current definition (kept **as-is**) | Already req. DISP? | **Additional LTF conditions** | Gate bar |
|---|----------------|-------------------------------------|:--:|-------------------------------|:--:|
| 1 | **Super** (Bull/Bear) | DISP + anyPBJ (or PB if enabled) + FAUNA + anyRVOL (1x / Grand Slam / MOAB) | ✅ | `+ (1k OR Nagasaki)` | 0 |
| 2 | **Grand Slam** | Bull bar + RVOL relative-spike ≥ Grand-Slam/MOAB threshold | ❌ | `+ DISP` (bull) `+ (1k OR Nagasaki)` | 0 |
| 3 | **MOAB** | Bear mirror of Grand Slam | ❌ | `+ DISP` (bear) `+ (1k OR Nagasaki)` | 0 |
| 4 | **Whale+PUP** | Whale pivot (reclaim SMA on vol > max down-vol) + HV milestone (Q/Y/ATH) + PUP + anyPBJ | ❌ | `+ DISP` (bull) `+ (1k OR Nagasaki)` | 0 |
| 5 | **Whale+PPD** | Bear mirror | ❌ | `+ DISP` (bear) `+ (1k OR Nagasaki)` | 0 |
| 6 | **SAAB²** | Back-to-back bull RVOL (SAAB/1x/GS on bar[1] & bar[0]) + (PUP or anyPBJ on either bar) | ❌ | `+ DISP` (bull) `+ (1k OR Nagasaki)` | 0 |
| 7 | **KRATOS²** | Bear mirror | ❌ | `+ DISP` (bear) `+ (1k OR Nagasaki)` | 0 |
| 8 | **Typhoon Bull** | Valid swing **low** + first bar of session + FAUNA + (PUP or Whale+PBJ) | ❌ | `+ DISP` (bull) `+ (1k OR Nagasaki)` | `[yy_rightBars]` |
| 9 | **Typhoon Bear** | Valid swing **high** + first bar + FAUNA + (PPD or Whale+PBJ) | ❌ | `+ DISP` (bear) `+ (1k OR Nagasaki)` | `[yy_rightBars]` |
| 10 | **Tomcat Bull** | First bar + FAUNA + **DISP** + ≥2 of {PUP, Whale, anyPBJ} | ✅ | `+ (1k OR Nagasaki)` | 0 |
| 11 | **Tomcat Bear** | Bear mirror | ✅ | `+ (1k OR Nagasaki)` | 0 |
| 12 | **Nagasaki Bull** | Highest-Ever-Volume bar + any bull directional signal | ❌ | `+ DISP` (bull) · *1k/Nagasaki already inherent (HEV)* | 0 |
| 13 | **Nagasaki Bear** | Bear mirror | ❌ | `+ DISP` (bear) · *1k/Nagasaki already inherent (HEV)* | 0 |
| 14 | **PAF PUP B2B** | PUP + FAUNA **back-to-back** — *by design **no** displacement* | ❌ | `+ DISP` (bull) `+ (1k OR Nagasaki)` ⚠️ changes its no-disp identity | 0 |
| 15 | **PAF PPD B2B** | Bear mirror — *by design no displacement* | ❌ | `+ DISP` (bear) `+ (1k OR Nagasaki)` ⚠️ | 0 |
| 16 | **FAUNA+ Alpha** | ≥`req` displacement-FVG hits within `win` bars (Set 1) | ✅ (density) | `+ (1k OR Nagasaki)` | `[1]` |
| 17 | **FAUNA+ Bravo** | …Set 2 thresholds | ✅ (density) | `+ (1k OR Nagasaki)` | `[1]` |
| 18 | **FAUNA+ Charlie** | …Set 3 thresholds | ✅ (density) | `+ (1k OR Nagasaki)` | `[1]` |
| 19 | **FAUNA+ Delta** | …Set 4 thresholds | ✅ (density) | `+ (1k OR Nagasaki)` | `[1]` |
| 20 | **FAUNA+ Echo** | …Set 5 thresholds | ✅ (density) | `+ (1k OR Nagasaki)` | `[1]` |
| 21 | **Foxtrot** (Fauna 4-in-4) | FAUNA on 4 consecutive bars | ❌ | `+ DISP` (dir.) `+ (1k OR Nagasaki)` | `[1]` |
| 22 | **Golf** (PUP²/PPD²) | Any density-disp raw + FAUNA + PUP/PPD, back-to-back | ✅ (density) | `+ (1k OR Nagasaki)` | `[1]` |
| 23 | **Opening Drive** | ≤ `od_max` bars into session + disp-FVG + prev DISP + PUP/price-up + vol | ✅ | `+ (1k OR Nagasaki)` | `[1]` |
| 24 | **Katana** (Bull/Bear) | Session-gap continuation: prior-day HV/GZI/FAUNA + today GZI/HV + FAUNA[1] + direction; req anyPBJ or PUP | ❌ | `+ DISP` (dir.) `+ (1k OR Nagasaki)` | `[1]` |
| 25 | **Musashi** (Bull/Bear) | (GZI or HV FVG) + PUP/PPD + Whale + anyPBJ | ❌ | `+ DISP` (dir.) `+ (1k OR Nagasaki)` | 0 |
| 26 | **Double Disp** (Bull/Bear) | **DISP** + FAUNA back-to-back + (PUP or anyPBJ) | ✅ | `+ (1k OR Nagasaki)` | 0 |
| 27 | **PUP Combo** | Low-threshold **DISP** + FAUNA + PUP, back-to-back | ✅ (low-thr) | `+ (1k OR Nagasaki)` | 0 |
| 28 | **PPD Combo** | Bear mirror | ✅ (low-thr) | `+ (1k OR Nagasaki)` | 0 |
| 29 | **Full Stack** (Bull/Bear) | anyRVOL + FAUNA + **DISP** + anyPBJ | ✅ | `+ (1k OR Nagasaki)` | 0 |
| 30 | **FVG Stack** (Bull/Bear) | anyRVOL + FAUNA + **DISP** + HV FVG + GZI | ✅ | `+ (1k OR Nagasaki)` | 0 |

**Legend:** ✅ = displacement already required (no DISP added, only the volume gate). ❌ = displacement
was **not** required, so direction-matched `sigDISPBull`/`sigDISPBear` is added. ⚠️ = the addition changes
the plot's defining character (flagged for your review).

---

## Notes & decisions to confirm

- **`1k` interpretation.** Resolved from the suite's own docs (`DEFINITIONS_HV_NAGASAKI.md`,
  `hv to 1k`, `heavy with 2x detection plots` which plots the 1000-bar tier literally as `text="1K"`):
  `1k` = **1000-bar volume high**. If you meant a different "1k" (e.g. a fixed RVOL multiple), say so and
  it's a one-line change in `ltf_1k`.
- **Nagasaki is inherent for the Nagasaki plot.** Items 12–13 already satisfy "1k OR Nagasaki" because the
  plot *is* an HEV event; for those only displacement is genuinely new.
- **PUP Combo / PPD Combo (27–28)** already require displacement, but at the design's **lower** std-dev
  threshold (mult = 2 vs the standard mult = 5). They were treated as "already requires displacement," so
  the standard `sigDISPBull/Bear` was **not** stacked on top. Tell me if the LTF build should instead
  force the *standard* displacement here.
- **PAF (14–15)** is defined by being a *no-displacement* back-to-back. Adding displacement (per the
  blanket rule) materially narrows it — flagged ⚠️. Say the word if PAF should be exempt ("doesn't make
  sense") instead.
- **`PUP+ANY` / `PPD+ANY` are alert-only** (no plotshape), so they are **not** "detection plots" and were
  left unchanged. Easy to gate them too if you want.
- **Toggles, offsets, colors, alert payloads** are all unchanged — only the fire conditions tightened.
