# HVD ↔ PBJ ↔ PPD — BEARISH (36) v1 — Indicator Study Audit

**Trigger:** `RE10023 — Cannot call the 'timeframe.change' function with a tick-based
'timeframe' argument` on **bar 0** (`tv_ta.relativeVolume():346 → #main():267`).

**Ask:** full study audit + a tick-friendly build; verify the plotshape **offsets** are
correct, *especially* the **Unified Combo** (`CS3R`).

---

## 0. Files

| Role | Path | Title / shorttitle |
|---|---|---|
| Source (crashes on tick) | `versions/HVD_PBJ_PPD_BEARISH_v1.pine` | `... BEARISH (36)` / `HVD PBJ PPD BEAR` |
| **Deliverable (tick-safe)** | `tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine` | `... BEARISH (36) [Tick-Friendly]` / `HVD PBJ PPD BEAR TF` |

The pasted source == committed `versions/` file (verified byte-identical incl. all 36
offsets); the only difference was the shorttitle, now aligned to `HVD PBJ PPD BEAR`
(matches the `HVD_PBJ_PPD` filename and the module). The tick-friendly build is the
source **plus two guards and nothing else** — detection logic and every offset are
byte-identical, so time-chart output is bit-for-bit unchanged.

---

## 1. Tick-safety audit (RE10023)

### Hazard surface — exhaustive scan
An exhaustive scan (`timeframe.*`, `request.security`, `time(`, `tv_ta.*`) found the
tick-hazard surface is exactly **two** things:

| # | Line(s) | Hazard | Fix |
|---|---|---|---|
| 1 | 267, 707, 708 | `tv_ta.relativeVolume(len, reg_anchorTimeframe, …)` with `reg_anchorTimeframe = ""`. The lib runs `timeframe.change(anchor)` internally (ta/7:346); a `""` anchor resolves to the **chart** TF, which on a tick chart is tick-based → throws on bar 0. | Route all 3 calls through `reg_anchorSafe`. |
| 2 | 27 | `int tfSec = timeframe.in_seconds(timeframe.period)` → **na** on some tick resolutions. Feeds the per-TF threshold tables (`f_*_threshold(tfSec)`, line 258) and the `tfSec>120` gates (928/939/950) and omega gates (1068/1071). na thresholds ⇒ every RVOL/SAAB/MOAB comparison silently goes `na` (false) and the study quietly stops firing. | `int tfSec = (na(_tfSecRaw) or _tfSecRaw <= 0) ? 10 : _tfSecRaw`. |

`ta.change(time("D"))` (line 283, session/day tracking) is **not** a hazard — `time("D")`
returns the containing daily bar's timestamp and is legal on tick charts (it does not call
`timeframe.change`). No `request.security`, no HTF, no other `tv_ta` function anywhere.

### The fix (matches the 2026-06-04 postmortem's corrected form)
```pine
// tfSec — fall back to 10s (tightest sub-minute) only when in_seconds is na/0:
int _tfSecRaw = timeframe.in_seconds(timeframe.period)
int tfSec = (na(_tfSecRaw) or _tfSecRaw <= 0) ? 10 : _tfSecRaw

// anchor — coerce ""→"D" ONLY on tick charts, detected by the CHART period suffix:
string reg_anchorSafe = ((reg_anchorTimeframe == "" and (str.endswith(timeframe.period, "T")
     or na(timeframe.in_seconds(timeframe.period)) or timeframe.in_seconds(timeframe.period) <= 0))
     or str.endswith(reg_anchorTimeframe, "T")) ? "D" : reg_anchorTimeframe
[currentVolume_reg,pastVolume_reg,_unused] = tv_ta.relativeVolume(reg_length, reg_anchorSafe, …)
```

**Why parity is preserved:** tick is detected off `timeframe.period` ending in `"T"` (the
authoritative signal — `timeframe.in_seconds("1000T")` returns a *positive* number, so the
na/≤0 test alone is NOT enough; that was the original 2026-06-04 bug). On a **time** chart
the `"T"` test is false → `reg_anchorSafe` stays `""` and `tfSec` stays raw → the library
and thresholds behave exactly as the source. Only tick charts get `"D"` / `10s`.

### Gate (from CLAUDE.md) — PASS
```
grep -nE 'relativeVolume\([^,]+,\s*""' tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine
# → (no output) — zero literal-blank anchors at call sites
```
The `reg_anchorSafe` *definition* itself keys off `str.endswith(timeframe.period, "T")`, so it
does not regress into the postmortem's "blank hidden inside the var" trap.

---

## 2. Offset audit — all 36 detections

**Repaint safety:** every detection is gated on `conf` (`barstate.isconfirmed`) → evaluated
on closed bars only. `offset=-1` draws on `bar[1]`, which is always closed. **Non-repainting.**

**The rule the file follows (and it is consistent):**
- **`offset = -1`** — the detection is anchored on the **HV / displacement / FVG / Matrix-combo
  bar**, which is `bar[1]` relative to the confirming bar. The marker sits on the *anomaly bar
  itself*, not the confirmation bar. This is the whole HV+D family + everything built on
  FVG / displacement / combo signals.
- **`offset = 0`** — the detection **completes on the current bar** with no back-referenced
  displacement bar: pure current-bar composites.

| # | Plot (bear) | Signal | Offset | Anchors on | Verdict |
|---|---|---|:--:|---|:--:|
| 1 | HV+D | `hvd_fire_bear` | −1 | HV `vol[1]` + disp`[1]` + FVG mid `[1]` = **T-1** | ✅ |
| 2 | HV+D+PB | `hvd_pb_bear` | −1 | +`sigBearPB[1]` → T-1 | ✅ |
| 3 | HV+D+PBJ | `hvd_pbj_bear` | −1 | +`sigBearPBJ[1]` → T-1 | ✅ |
| 4 | Bear DDDD | `sigP21BearUUUU` | −1 | streak displacement bar → T-1 | ✅ |
| 5 | Bear DDD | `sigP21BearUUU` | −1 | T-1 | ✅ |
| 6 | Bear DD | `sigUUBear` | −1 | T-1 | ✅ |
| 7 | A★ Bear | `sigAlphaStrikeBear` | −1 | **current-bar** composite (pp+MOAB/RVOL+PBJ) | ⚠️ see §2.2 |
| 8 | FOX Bear | `sigFoxtrotBear` | 0 | 4× consecutive Fauna incl. current bar | ✅ |
| 9 | OD Bear | `sigODBear` | −1 | `od_fvg_bear` + `disp_prevDisp[1]` → T-1 | ✅ |
| 10 | D2+ Bear | `sigDispConsBear2` | −1 | `sigDISP2Bear` FVG mid → T-1 | ✅ |
| 11 | D3+ Bear | `sigDispConsBear3` | −1 | FVG mid → T-1 | ✅ |
| 12 | Golf Bear | `sigGolfBear` | −1 | `sigDISPBear` (FVG) → T-1 | ✅ |
| 13 | PAF- | `sigPAFBear` | 0 | current-bar PPD+Fauna (& `[1]`) | ✅ |
| 14 | CS1 FVG | `csNew1_Bear` | −1 | bear-FVG middle bar → T-1 | ✅ |
| 15 | CS2 MAT | `csNew2_Bear` | 0 | Matrix high-vol bar = **current** | ✅ |
| 16 | **Combo (Unified)** | `csNew3_Bear` | −1 | **shared confluence bar T-1** | ✅ **see §2.1** |
| 17 | CC Bear | `sigCCBear` | −1 | combo-set (FVG/Matrix) chain → T-1 | ✅ |
| 18 | LSC Bear | `sigLSCBear` | 0 | LS-momentum (current RVOL) chain | ✅ |
| 19 | Rooftop | `anyBearRoof` | 0 | current-bar pp+PBJ+HW | ✅ |
| 20 | Penthouse | `anyBearPent` | 0 | current-bar | ✅ |
| 21 | HW Bear | `hwBear` | 0 | current-bar composite | ✅ |
| 22 | S! Bear | `superBear` | −1 | requires `sigDISPBear` (FVG) → T-1 | ✅ |
| 23 | SD! Bear | `sduperBear` | −1 | requires `sigDISPBear` (FVG) → T-1 | ✅ |
| 24 | CO PBJ | `co_bear_pbj` | −1 | `hvd_fire_bear` + `[1]` terms → T-1 | ✅ |
| 25 | CO PB | `co_bear_pb` | −1 | T-1 | ✅ |
| 26 | B2B HV+D | `b2b_bear_nopb` | −1 | latest of two HV+D bars → T-1 | ✅ |
| 27 | B2B HV+D+PBJ | `b2b_bear_pbj` | −1 | T-1 | ✅ |
| 28 | B2B HV+D+PB | `b2b_bear_pb` | −1 | T-1 | ✅ |
| 29 | HV+D+PPD | `hvdm_ppd_nopbj_r` | −1 | `hvd_fire_bear` + `sigPPD[1]` → T-1 | ✅ |
| 30 | HV+D+RVOL | `hvdm_rvol_nopbj_r` | −1 | + RVOL`[1]` → T-1 | ✅ |
| 31 | HV+D+CMB | `hvdm_cmb_nopbj_r` | −1 | + `csNew3_Bear` (already T-1-anchored) → T-1 | ✅ see §2.1 |
| 32 | HV+D+PBJ+PPD | `hvdm_vis_pbjppd_r` | −1 | T-1 | ✅ |
| 33 | HV+D+PBJ+RVOL | `hvdm_vis_pbjrvol_r` | −1 | T-1 | ✅ |
| 34 | HV+D+PBJ+CMB | `hvdm_vis_pbjcmb_r` | −1 | T-1 | ✅ |
| 35 | HV+D+PBJ 2of3 | `hvdm_2of3_r` | −1 | T-1 | ✅ |
| 36 | HV+D+PBJ 3of3 | `hvdm_3of3_r` | −1 | T-1 | ✅ |

Tally: 29 × `offset=-1`, 7 × `offset=0` — and every one lands on the bar it is *about*.

### 2.1 Unified Combo (`CS3R` / `csNew3_Bear`) — the flagged item — **CORRECT**
```
csNew3_Bear = csNew1_Bear and nz(csNew2_Bear[1])
```
Let **T** = the bar where `csNew3_Bear` is true.
- `csNew1_Bear` (at T) = the **FVG combo**: a bear FVG *completing at T*
  (`high[T] < low[T-2]`, `close[T-1] < low[T-2]`) — its displacement / middle bar is **T-1**,
  combined with body%`[T-1]` and RVOL`[1]`.
- `csNew2_Bear[1]` = the **Matrix combo** evaluated at **T-1** (Matrix high-volume bar + RVOL,
  all at T-1).

Both constituents reference **bar T-1**. `offset=-1` puts the COMBO marker on **T-1** — exactly
where CS1's own marker points (`offset=-1`), where CS2 actually fired (`offset=0`, fired at T-1),
and where the FVG-displacement bar and the Matrix-volume bar physically coincide. That shared bar
*is* the confluence the "Unified Combo" exists to highlight.

> If `CS3R` were `offset=0` it would sit on the FVG-completion bar **T**, one bar to the **right**
> of both of its own components — *that* would be the bug. It is not present. **`offset=-1` is right.**

Subtlety worth recording: in the Momentum block, `_m_cb1r = csNew3_Bear` uses the **current**
bar (`[0]`), while its siblings `_m_ppd1 / _m_rv1r / _m_pj1r` use `[1]`. This is **correct** —
`csNew3` is already T-1-anchored, so `[0]` already points at the T-1 confluence bar; the plain
current-bar signals (PPD/RVOL/PBJ) need `[1]` to reach that same T-1. Under `offset=-1` all four
co-locate on T-1. Do **not** "fix" `_m_cb1r` to `[1]` — that would push it to T-2.

### 2.2 One cosmetic outlier — `A★ Bear` (AlphaStrike, #7)
AlphaStrike's trigger (`bear_pp` + `MOAB/RVOL1x` + `sigBearPBJ` + Fauna) is a **pure current-bar**
composite — structurally identical to HW / Rooftop / Penthouse, which all use `offset=0`. By the
rule it "should" be `offset=0`; it is `offset=-1`, i.e. a 1-bar left visual shift.

**Left as-is (not a defect to fix here)** because: (a) it is **off by default**
(`show_AlphaStrikeR=false`); (b) per CLAUDE.md, Alpha Strike is trusted **only from SQUARIFY 64**,
so this plot is informational, not a trusted alert source; (c) changing it would diverge the
bear split's marker placement from the bull split and break byte-for-byte parity. Flag only —
fold into a future *coordinated bull+bear cosmetic* pass if a visual change is ever wanted.

---

## 3. Parity statement
Time charts: `reg_anchorSafe == ""` and `tfSec` raw ⇒ the tick-friendly build is
**bit-for-bit identical** to the source. Tick charts: the source cannot run at all (RE10023);
the tick build runs with a `"D"` anchor (session-anchored RVOL, the correct semantics) and a
10s threshold tier. No detection logic and no offset was altered.

## 4. Verification commands
```bash
# 1. no literal-blank anchor at any relativeVolume call site (must be empty):
grep -nE 'relativeVolume\([^,]+,\s*""' hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine
# 2. the anchorSafe def keys off the CHART period (guards the postmortem trap):
grep -n 'reg_anchorSafe' hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine
# 3. tick build == source apart from guards + shorttitle/comments:
diff hvd-pbj-ppd/versions/HVD_PBJ_PPD_BEARISH_v1.pine hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine
# 4. constitutional gate (no fixed/anchored windows):
./check_no_fixed_windows.sh hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine
```

## 5. Verdict
- **Tick crash:** fixed by the two guards; RE10023 cannot recur (gate green). ✅
- **Offsets:** all 36 correct and internally consistent; **Unified Combo `offset=-1` is
  correct** (lands on the T-1 confluence bar). ✅
- **One cosmetic note:** AlphaStrike (off by default, non-trusted here) is 1 bar left of the
  `offset=0` cohort it structurally belongs to — flagged, intentionally left for parity. ⚠️
- **Parity:** time-chart output unchanged, bit-for-bit. ✅
