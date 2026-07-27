# HVD-PBJ-PPD — Combo + Displacement/FVG Offset Audit (2026-06-28)

Audit of the bull/bear split for: the **Combo Chain (CC)**, **FVG Combo (CS1)**,
**Matrix Combo (CS2)**, **Unified Combo (CS3)**, and every **displacement / FVG**
detection's **offset & visual-plot** correctness. Companion to
[`DETECTION_PLOT_VS_VISUAL_PLOT_FRAMEWORK.md`](../DETECTION_PLOT_VS_VISUAL_PLOT_FRAMEWORK.md).

**Files under audit**
- User's working bull: `june7-conversion/tick_friendly_pine/hvd_pbj_pup_bull_tickfriendly.pine` (shorttitle `HVD PBJ BULL`)
- Canonical tick-friendly bull: `hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BULLISH_v1_tick_friendly.pine`
- Canonical tick-friendly bear: `hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine`

Line numbers below are from the canonical **bear** file unless noted.

---

## TL;DR

1. **A correct tick-friendly bear already existed** and is a complete, faithful,
   byte-identical-engine mirror of the bull (36 bear plotshapes vs 38 bull; the 2
   bull-only plots — Omega-A and NAG+ — are bull-only **by design**). It is tick-safe
   and carries the canonical combo-chain fix. It is the recommended bear.
2. **The bull you pasted had a real bug:** it still carried the **retired** combo-chain
   logic (`comboSet1_Bull[i-1]` cross-bar shift). Every other file in the repo already
   had the binary fix. **Fixed** in this change.
3. **All displacement/FVG offsets are correct** — prior-bar/FVG/HV detections plot
   `offset=-1`, current-bar detections plot `offset=0`. **No blockers.** Two symmetric
   design notes (Golf, Alpha-Strike) are recorded below for your call.
4. **Hardening applied:** the canonical bull+bear `tfSec` tick-fallback now also detects
   the `"T"` suffix (was `na`/`<=0` only), matching the bull's NINE-NINES guard.

---

## Part A — Combo Rules

> "Which bar goes in the CSV" is governed entirely by the plot **offset** (there is no
> CSV writer in these files; the consumer stamps the row at the offset-adjusted bar).
> All alerts fire on `barstate.isconfirmed` with `alert.freq_once_per_bar_close`.

### A1. FVG Combo — CS1 / `csNew1 = comboSet1 OR comboSet2`  → **offset −1**

```pine
cs_bp1 = |close[1]-open[1]| / (high[1]-low[1])          // body of bar[1]
cs_vb  = cs_bp1 >= cs_bodyPct_FVG                        // default 0.74
comboSet1_Bear = conf and cs_vb and (gz_bearHV or gz_bearGZI) and (sigKratos[1] or sigBearRVOL1x[1] or sigMOAB[1])
comboSet2_Bear = conf and cs_vb and (gz_bearHV or gz_bearGZI) and ((cs_inc_pentagon_FVG and sigPentagon[1]) or sigWTC[1] or sigHiroshima[1] or sigNagasaki[1])
```
Fires when, on the FVG-completing bar: (1) **bar[1]'s** body ≥ 0.74; (2) a fresh
directional FVG exists whose middle candle is bar[1], either HV (`gz_*HV`, middle-bar
volume is a volume-high) or overlapping a same-direction FVG within 12 bars (`gz_*GZI`);
(3) an RVOL tier from **bar[1]** (`[1]`-shifted). **Set1** = trend tiers
(SAAB/RVOL1x/GrandSlam → Kratos/RVOL1x/MOAB), **Set2** = ratio tiers
(Pentagon/WTC/Hiroshima/Nagasaki).
**Offset −1** because every term is anchored to the FVG middle candle = bar[1]; the mark
sits on the candle it describes. CSV bar = `bar_index − 1`. Aggregate tag `FVG`.

### A2. Matrix Combo — CS2 / `csNew2 = comboSet3 OR comboSet4`  → **offset 0**

```pine
is_matrix_number = volume == ta.highest(volume, neo_len)         // current bar, neo_len=67
cs_vm  = ls_bodyRat >= cs_bodyPct_MAT                            // CURRENT bar body, 0.74
matrix_any_bear = sigNeoBear or sigTrinityBear or neo_bear_aligned or trinity_bear_aligned
comboSet3_Bear = cs_vm and matrix_any_bear and (sigKratos or sigBearRVOL1x or sigMOAB)
comboSet4_Bear = cs_vm and matrix_any_bear and ((cs_inc_pentagon_MAT and sigPentagon) or sigWTC or sigHiroshima or sigNagasaki)
```
Every input — Matrix Number (current volume rank), Neo/Trinity, body `cs_vm`, RVOL — is
**current-bar, no `[1]`**. **Offset 0** (belongs to its own bar). CSV bar = `bar_index`.
Tag `MAT`. This is the **only** combo with no offset; do not blindly copy `-1` onto it.

### A3. Unified Combo — CS3 / `csNew3 = csNew1 AND nz(csNew2[1])`  → **offset −1**

The ordered sequence **Matrix on bar N−1, FVG on bar N**: FVG combo fires **this** bar
AND matrix combo fired the **prior** bar. The FVG leg is bar[1]-anchored and the matrix
leg is explicitly `[1]`-shifted, so **both legs describe bar[1]** → **offset −1**.
CSV bar = `bar_index − 1`. Tag `COMBO`. (The `[1]` is on `csNew2` only — `csNew1` is this
bar. `nz()` makes the early-history prior-matrix false.)

### A4. Combo Chain — CC / `sigCCBull` / `sigCCBear`  → **offset −1**

Rolling window `cc_window` (2), `cc_min_hits` (2). The **binary law** (canonical fix):
```pine
for i = 0 to cc_window-1
    hv2 = comboSet3[i] or comboSet4[i] or comboSet1[i] or comboSet2[i]   // Matrix ∪ FVG, SAME bar → max 1
    if hv2: cc_win += 1
    if sigPBJ[i] or sigPB[i]: cc_pbj := true
```
Plus a PBJ/PB anywhere in the window, plus a **rising-edge latch** (`cc_*_active` clears
on a combo-free bar, sets once when `cc_win ≥ cc_min_hits and cc_pbj`). So **one physical
bar contributes at most 1**, and a 2-hit chain **requires two distinct bars**.

**Retired vs fixed:**
| | per-bar hit | one mixed bar (Matrix+FVG+PBJ) |
|---|---|---|
| **OLD (retired)** | `comboSet3/4[i] or comboSet1/2[i-1]` | `cc_win=2` → **fires off one candle** ❌ |
| **FIXED (canonical)** | `comboSet3/4[i] or comboSet1/2[i]` | `cc_win=1` → does **not** fire ✓ |

**Your pasted bull had the OLD form** → it emits **extra, false `CC Bull` alerts / CSV
rows** on any single candle carrying both a Matrix combo and an FVG combo (with a PBJ in
window). The bear (and every other file) never did. Now fixed on the bull too.

---

## Part B — Displacement & FVG Offset Audit

Decision rule (from the framework): prior-bar/FVG-middle/HV-on-`volume[1]` calc ⇒
`offset=-1`; current-closing-bar calc ⇒ `offset=0`.

| Detection | Calc anchor | Plot offset | Correct? |
|---|---|---|---|
| HV+D (`hvd_fire_bear`: `d1_prevDisp`[1] + `d1_bearFVG` middle=bar[1] + HV on `volume[1]`) | bar 1 | −1 | ✅ |
| HV+D+PB / HV+D+PBJ (`hvd_pb_bear` / `hvd_pbj_bear`, gates `[1]`) | bar 1 | −1 | ✅ |
| USE Displacement (`sigDISPBear`, default `i_req_fvg` → `disp_prevDisp`[1] + bear FVG) | bar 1 | (consumed by composites) | ✅ |
| OD Bear (`sigODBear`: `disp_prevDisp`[1] + `od_fvg_bear` + PPD + PBJ) | bar 1 | −1 | ✅ |
| Disp 2+ / 3+ (`sigDispConsBear2/3`: `disp2/3_rng[1]` + FVG middle bar[1]) | bar 1 | −1 | ✅ |
| disp5 / HW Bear (`disp5_bear` = `disp_rng>thresh` on bar[0], `close<open`) | bar 0 | 0 | ✅ |
| CS1 FVG combo (`csNew1_Bear`) | bar 1 | −1 | ✅ |
| CS2 Matrix combo (`csNew2_Bear`) | bar 0 | 0 | ✅ |
| CS3 Unified combo (`csNew3_Bear`) | bar 1 | −1 | ✅ |
| HV+D MOMENTUM CO-OCC (8 plots, all gated by `hvd_fire_bear` + `[1]` momentum) | bar 1 | −1 | ✅ |
| B2B HV+D ×3 (`b2b_bear_raw = hvd_fire_bear and nz(hvd_fire_bear[1])`) | bars 1 & 2 | −1 | ✅ (two adjacent visual HV+D plots) |
| CO HV+D+PBJ/PB+USE ×2 (gated by `hvd_fire_bear` + `[1]`) | bar 1 | −1 | ✅ |
| Golf Bear (`sigGolfBear`: current `sigDISPBear` + `[1]/[2]` confirmation) | bar 1 (displacement candle) | −1 | ⚠ note B1 |
| Alpha Strike Bear (`sigAlphaStrikeBear`: current-bar pp/RVOL/PBJ) | bar 0 | −1 | ⚠ note B2 |
| Foxtrot Bear (`sigFoxtrotBear`: 4× FAUNA streak, current trigger; no displacement/FVG) | bar 0 | 0 | ✅ |

**No blockers.** Two notes (both symmetric with the bull — not bear-specific bugs):

- **B1 — Golf (`-1`):** fires on the **current-bar** `sigDISPBear` (the `[1]/[2]` terms
  are streak confirmation). Because `sigDISPBear` defaults to the FVG path whose
  displacement/middle candle is bar[1], `offset=-1` **does** land on the displacement
  candle — defensible under the offset law. The only asymmetry is vs its sibling
  current-bar displacement detection `hwBear`/`disp5` (offset 0). **Recommendation:**
  keep `-1` and document Golf as "anchored to the displacement candle"; do not change
  one side without the other (bull `sigGolfBull` is also `-1`).
- **B2 — Alpha Strike (`-1`):** has **no** prior-bar displacement/FVG term; its
  load-bearing legs are current-bar. Strictly, `offset=0` would match the law. Low
  impact: **disabled by default** (`show_AlphaStrikeR=false`) and per `CLAUDE.md` Alpha
  Strike is only trusted from SQUARIFY 64. **Recommendation:** either set `offset=0` on
  both bull & bear for strict compliance, or leave `-1` and document the deliberate
  back-shift. Your call — flagged, not auto-changed, to keep bull/bear in lockstep.

---

## Part C — Bear-mirror & tick-safety verdict

- **Faithful mirror:** ✅ Engines 1–7 (RVOL, FAUNA, GZ1/HV FVG, Displacement, PUP/PPD,
  PBJ/Ping-Pong, Ping-Pong SR) are byte-identical to the bull; only logic delta is the
  (correct) binary combo fix.
- **Plot count 38→36:** fully explained — **Omega-A** (Boom-Hunter long-only) and
  **NAG+ Bull** (bull-suite plot per repo law) are bull-only by design; no real omission.
- **Tick-safe:** ✅ no `relativeVolume(…, "")` blank anchor; `reg_anchorSafe` coerces to
  `"D"` only on tick; `tfSec` fallback present. **Hardened** in this change so the
  `tfSec` fallback also fires on a `"T"`-suffixed period (previously only `na`/`<=0`).
- **Offsets:** ✅ all 36 mirror the bull's offset law.

---

## Changes applied in this commit

1. `june7-conversion/.../hvd_pbj_pup_bull_tickfriendly.pine` — combo chain: retired
   `comboSet1/2_*[i-1]` cross-bar form → canonical same-bar OR-collapse (bull + bear loops).
2. `hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BULLISH_v1_tick_friendly.pine` — `tfSec` guard
   hardened (`"T"`-suffix detection + `TICK_FALLBACK_SEC` input).
3. `hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine` — same `tfSec`
   hardening.

Gates after change: blank-anchor grep CLEAN ×3; `check_no_fixed_windows.sh` PASS; no
`[i-1]` cross-bar combo chain remaining.
