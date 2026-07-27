# Detection Plot vs Visual Plot — the suite's offset & rolling-window law

> **Status:** canonical framework for every Pine study in this repo.
> **Scope:** how a detection becomes a mark on a candle, where that mark lands, and
> what may be counted in a window. Read this before adding/auditing any `plotshape`.
> **One-line test of understanding:** *"Which bar?" is ALWAYS a question about the
> visual plot — never about the detection plot.*

---

## 1. Purpose

Every study here is a stack of **detections** that become **marks on candles**. Two
different things get conflated all the time, and the conflation causes real bugs
(wrong-bar plots, double-counted windows, off-by-one CSV rows). This document
separates them into one strict pipeline and a short list of invariants so that
every detection, in every study, is reasoned about the same way.

The model is deliberately literal:

- A **detection plot** answers *what / whether* — "are the conditions met?"
- It says **nothing** about *where*.
- *Where* is a **separate, second step** called **offset**, and it is considered
  **only after** the conditions are met.
- The mark that finally lands on a candle is the **visual plot**.
- **Only visual plots** are counted — on the chart, in a CSV, in any rolling window.

---

## 2. Glossary

| Term | Definition |
|---|---|
| **Detection plot** | A boolean produced by **calculations + conditions**. Its only job: *are the conditions met on this evaluation?* It has **no location**. Do **not** say a detection plot "is on bar X." |
| **Calculation** | The raw math a detection runs (std-dev of range, volume rank, RVOL ratio, FVG geometry, body ratio, streak counters…). May reference the current bar `[0]` and/or prior bars `[1]`, `[2]`. |
| **Condition** | The boolean test over the calculations (`disp_rng[1] > thresh[1]`, `volume[1] == highest(...)[1]`, `low > high[2] and close[1] > open[1]`…). When the condition is **met**, and only then, we proceed to offset. |
| **Offset** | The **second step**, applied **only after** conditions are met. It decides *where the mark goes*. `offset = -1` ⇒ the mark lands on the **candle before** the firing bar (bar `[1]`). `offset = 0` (the default, no `offset=` argument) ⇒ the mark lands on the **current/closing** bar (bar `[0]`). |
| **Visual plot** | The mark actually rendered on a candle **after** offset is applied. This is the *only* observable: it is what you see on the TradingView chart **and** the bar recorded in any CSV / spreadsheet ("which bar did it land on?"). |
| **Rolling window** | A trailing window of length *N*, evaluated at its **leading edge** on every confirmed bar, counting **visual plots only**. Slides forward one bar at a time. |
| **Back-to-back (B2B)** | Our nickname for the smallest rolling window: **two visual plots on two adjacent bars**. Nothing more. |
| **Fixed / anchored window** | **BANNED.** A window that pins a start bar and waits *N* bars (`var int xStartBar … if bar_index - xStartBar >= N`). Enforced by `check_no_fixed_windows.sh`. |

---

## 3. The Pipeline (the canonical chain — in order, no skipping)

This is the law. Each step happens **only if** the previous one did.

1. **Calculate.** Compute the detection's math. It may look at `[0]`, `[1]`, `[2]`.
2. **Evaluate the condition.** "Are the conditions met?" → yes / no. *This is the
   entire job of the detection plot.* If **no**, stop: nothing is placed, nothing
   is counted.
3. **(Only if met) Consider offset.** Now — and not before — ask *where*. Offset is
   determined by **which bar the calculation actually describes**:
   - calc anchored to the **prior bar** (`[1]` / the FVG middle candle / HV on
     `volume[1]`) ⇒ `offset = -1`.
   - calc describes the **current closing bar** ⇒ `offset = 0`.
4. **Place the visual plot.** The mark lands on `firing_bar + offset`. *This* is the
   visual plot — the thing on the chart and in the CSV.
5. **(Only this) Count it.** Rolling windows, B2B, CSV rows — everything that asks
   "which bar / how many" counts **visual plots only**, never detection evaluations.

```
 calc ──▶ condition met? ──no──▶ (nothing: no offset, no plot, no count)
                 │ yes
                 ▼
            consider offset (where?)  ──▶  place VISUAL PLOT at firing_bar + offset
                                                       │
                                                       ▼
                                          counted in chart / CSV / rolling windows
```

---

## 4. Invariants (MUST / MUST-NOT)

1. **MUST** treat the detection plot as *whether*, never *where*. Never write or say
   "the detection plot is on this bar." A detection plot detects; it does not locate.
2. **MUST** decide offset **only after** the condition is met. Offset is step 3, never
   step 1.
3. **Offset law:** a detection whose firing calculation is anchored to the **prior
   bar** (`[1]`, the FVG/displacement middle candle, HV measured on `volume[1]`)
   **MUST** plot at `offset = -1`. A detection that describes the **current closing
   bar** **MUST** plot at `offset = 0` (omit the `offset=` arg).
4. **Single source of "where":** the visual plot's bar = `firing_bar + offset`. The
   CSV row's bar **MUST** equal the visual plot's bar. If a plot is `offset=-1`, its
   CSV/event timestamp is `bar_index - 1`.
5. **Count visual plots only.** Rolling windows, B2B, and any "how many in N bars"
   count **visual plots**, never raw detection evaluations.
6. **Rolling, never fixed.** Every window/lookback **MUST** be a sliding trailing-N
   evaluated at the leading edge on `barstate.isconfirmed`. Fixed/anchored windows
   are **MUST-NOT** (gated by `check_no_fixed_windows.sh`).
7. **B2B = two adjacent visual plots.** "Back-to-back" is exactly a 2-bar rolling
   window of visual plots. It is **not** "every two bars" and **not** a fixed pair.
8. **Binary-bar law (counting).** When a rolling window counts combo hits, **one
   physical bar contributes at most 1** (`true`/`false`). Two distinct detections
   that land on the **same physical bar** OR-collapse to **one** hit. A 2-hit window
   therefore **requires two distinct bars**. (This is the combo-chain fix; see §6.)
9. **Confirmed bars only.** Detections gate on `conf = barstate.isconfirmed` so the
   visual plot and its window membership do not repaint intrabar.
10. **Tick safety is orthogonal to offset.** The RE10023 anchor guard and the `tfSec`
    tick fallback affect *whether* RVOL conditions compute — they never change *where*
    a visual plot lands. Keep them, but audit them separately (see §7).

---

## 5. Decision procedure — setting offset on any new detection

Ask, in order:

1. **What bar does the firing condition describe?** Trace every term in the condition
   to the bar it reads.
   - Pure `[0]` terms (this bar's `close>open`, current-bar volume rank, current-bar
     RVOL, current-bar body ratio) → the detection describes **bar 0**.
   - Any of: a displacement gate on `[1]` (`disp_rng[1] > …`), an ICT FVG whose
     **middle/displacement candle is `[1]`** (`low>high[2] and close[1]>open[1]`),
     HV measured on `volume[1]` → the detection describes **bar 1**.
2. **History gates don't move the anchor.** `nz(sig[1])`, `nz(sig[2])` used only to
   *confirm a streak/sequence* do **not** change where the mark goes. The anchor is the
   bar the **firing** term describes. (E.g. a Foxtrot that fires on the current
   FAUNA bar but checks 3 prior FAUNA bars is a **bar-0** detection.)
3. **Set the offset:** bar 1 → `offset=-1`; bar 0 → omit `offset` (=0).
4. **Mixed condition?** If the load-bearing/identifying term is a prior-bar
   displacement/FVG, anchor to bar 1 (`-1`) even if a confirming gate is current-bar.
   Document the choice in a comment.
5. **Mirror bull↔bear.** The bear plot's offset must equal its bull twin's offset.

---

## 6. Worked examples (from the real HVD-PBJ-PPD code)

All line numbers from `hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine`
(bull twin is symmetric).

### HV+D — `offset=-1` ✓
`hvd_fire_bear = base_hv_hit and d1_bear`, where `d1_prevDisp = d1_rng[1] > d1_thresh[1]`,
`d1_bearFVG = high < low[2] and close[1] < open[1]`, and every HV rank reads `volume[1]`.
**Every term is anchored to bar 1** (the displacement / FVG middle candle). → visual
plot must sit on bar 1 → `offset=-1` (L1115). Correct.

### Matrix Combo (CS2) — `offset=0` ✓
`comboSet3_Bear = cs_vm and matrix_any_bear and (sigKratos or sigBearRVOL1x or sigMOAB)`.
`is_matrix_number = volume==ta.highest(volume,neo_len)` (current bar), `cs_vm` is the
**current** bar's body ratio, RVOL tiers are current-bar (no `[1]`). **Everything is
bar 0** → `offset=0` (no `offset=` on L1131). Correct, and intentionally different from CS1.

### FVG Combo (CS1) — `offset=-1` ✓
`comboSet1_Bear = cs_vb and (gz_bearHV or gz_bearGZI) and (sigKratos[1] or …[1])`. The
body gate `cs_vb` reads bar 1's body (`cs_bp1` from `close[1]/open[1]/…`), the FVG
middle candle is bar 1 (`close[1]<low[2]`), and the RVOL tiers are `[1]`-shifted.
**Anchor = bar 1** → `offset=-1` (L1130). Correct.

### Unified Combo (CS3) — `offset=-1` ✓
`csNew3_Bear = csNew1_Bear and nz(csNew2_Bear[1])` — FVG combo **this** bar AND matrix
combo the **prior** bar. The FVG leg is bar-1-anchored and the matrix leg is explicitly
shifted to `[1]`, so **both legs describe bar 1** → `offset=-1` (L1132). Correct.

### Back-to-Back HV+D — two visual plots on two adjacent bars ✓
`b2b_bear_raw = hvd_fire_bear and nz(hvd_fire_bear[1])`, plotted `offset=-1` (L1170). On
the B2B bar, today's HV+D visual sits on bar 1 (offset −1) and yesterday's HV+D visual
sat on bar 2 (its own offset −1). **Two HV+D visual plots on two adjacent candles** =
the definition of back-to-back. This is a 2-bar **rolling** window at its leading edge —
not "every two bars."

### Combo Chain (CC) — the binary-bar law, `offset=-1` ✓
Rolling window `cc_window` (default 2), `cc_min_hits` (default 2). Per bar:
`hv2 = comboSet3[i] or comboSet4[i] or comboSet1[i] or comboSet2[i]` — Matrix **and**
FVG on the **same physical bar** OR-collapse to **one** hit (max +1 per bar). So a 2-hit
chain **requires two distinct bars**. Plotted `offset=-1` (L1133).
**Retired (buggy) form:** `… ; if i>=1 and (comboSet1[i-1] or comboSet2[i-1]): hv2:=true`
— the `[i-1]` cross-bar shift let one candle carrying both Matrix and FVG self-count to 2
and fire a chain off **one** bar. That violates invariant #8 and is **banned**.

---

## 7. Gates — how to verify before calling a file "done"

```bash
# (a) Offset audit: every displacement/FVG/HV detection that reads [1] must plot offset=-1.
#     Eyeball each plotshape against §5; bull and bear offsets must match.

# (b) No retired cross-bar combo chain:
grep -nE 'comboSet[12]_(Bull|Bear)\[i-1\]' <file>      # must return nothing

# (c) RE10023 tick anchor (never a blank anchor that throws on tick):
grep -nE 'relativeVolume\([^,]+,\s*""' <file>          # must return nothing

# (d) tfSec tick fallback present AND detects the "T" suffix (not just na/<=0):
grep -nE 'str.endswith\(timeframe.period, "T"\)' <file>   # must be present in the tfSec guard

# (e) No fixed/anchored windows (rolling only):
bash check_no_fixed_windows.sh <file>                  # must print PASS
```

---

## 8. Vocabulary discipline

**Say:**
- "The **visual plot** is on bar N." / "Which bar is the **visual plot** on?"
- "The **detection's conditions are met** (or not)."
- "After conditions are met, **offset** places the visual plot on bar N−1."
- "Two **visual plots** on two adjacent bars → back-to-back (a 2-bar rolling window)."

**Never say:**
- ❌ "The detection plot is on this/that bar." (A detection has no location.)
- ❌ "It fired on bar N, so the mark is on bar N." (Only true when `offset=0`.)
- ❌ "Every two bars" / "fixed window" / "anchored window." (All windows are rolling.)
- ❌ "Detection plot" and "visual plot" as synonyms.

---

### Appendix — suite-wide consistency (surveyed)

The offset law and rolling-window discipline hold across the suite, e.g. B2B PUP v5.4
(CS1 FVG `offset=-1`, body% gate on bar 1; non-displacement S5/S10/S12–15 `offset=0`),
TNT OD v3 ("boolean true on bar 0; visual offset −1 → lands on bar 1"), SQUARIFY v3.1
(23 displacement/FVG plots `-1`, the rest `0`), and Heavy Combo Toggles v2 ("Bull combos
AND-gate with displacement → −1; Neutral with noDisp → 0"). All pass
`check_no_fixed_windows.sh`. Known cosmetic deviations to clean up over time: TNT OD v3
uses descriptive plot names instead of `S<N>:` (CLAUDE.md plot-naming rule), and SQUARIFY
uses `<N>` without the `S` prefix.
