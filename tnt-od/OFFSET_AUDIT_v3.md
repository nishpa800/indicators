# TNT OD v3 — Detection-Plot Offset Audit

**File audited:** `tnt-od/versions/TNT_OD_v3.pine`
**Date:** 2026-07-13
**Trigger:** FUSE `offset = 0` challenged as nonsensical.
**Vocabulary:** `bar[N]` only. "Detection bar" = the bar on which the boolean
goes `true` (= `bar[0]` at evaluation time). "Visual bar" = the bar the marker
is drawn on after `offset` is applied.

---

## 0. What "offset" actually is (visual-plot semantics)

An offset is **not** part of detection. It is applied **only after** a detection
boolean is already `true`. Sequence per bar:

1. Calculate the combo's conditions.
2. If — and only if — they are **met**, a marker exists. A `false` boolean
   produces **no marker**; there is no offset to speak of, because there is no
   particle to place.
3. `offset` then *relocates* that already-existing marker from the detection bar
   to the bar where the price event the marker refers to actually happened.

So offset answers exactly one question: **"the condition fired on `bar[0]`; on
which bar does the human eye see the thing this marker is about?"**

### The one line that defines every atom's visual bar

`TNT_OD_v3.pine:630`

```pine
int evtBar = raw_bullTNT ? bar_index : bar_index - 1
```

| Atom | Real price event lives on | Natural offset |
|------|---------------------------|----------------|
| **TNT** (structural break, confirmed on the bar) | `bar[0]` = detection bar | **0** |
| **CONT** (proximity/sudden-change trigger) | `bar[0]` = detection bar | **0** |
| **RET** (return into zone) | `bar[0]` = detection bar | **0** |
| **PBJ** (supertrend flip) | `bar[0]` = detection bar | **0** |
| **NPM / Charge** (displacement + FVG) | `bar[1]` = the displaced candle (`bar[0]` is only the FVG-confirm candle) | **−1** |

### The combo rule (how per-atom offsets become a combo offset)

> Choose the offset that lands **all** of the combo's atoms on **one** visual
> bar. This is solvable **only when the atoms are a same-visual-bar
> coincidence** — i.e. they co-locate once the offset is applied.
>
> - If the chain contains an NPM/Charge (displacement + FVG) atom, that atom's
>   real candle is at `bar[1]`, so the combo shifts to **offset −1** and the
>   non-displacement partner is read at `[1]` so it lands on the same `bar[0]−1`.
> - If every atom is a `bar[0]` atom (TNT/CONT/RET/PBJ), the combo stays at
>   **offset 0**.

---

## 1. The table — every detection plot, its offset, and my verdict

`d` = detection bar (`bar[0]`). ✅ = offset is internally consistent with the
rule above. ⚠️ = flagged.

### Tier 1

| # | Plot | Code offset | Atom chain (visual bars) | Rule-implied | Verdict |
|---|------|:----------:|--------------------------|:-----------:|:------:|
| 1 | B2B Napalm | −1 | NPM@`d−1` **and** NPM@`d−2` → anchor most-recent displaced candle `d−1` | −1 | ✅ |
| 2 | RC NPM+TNT | −1 | NPM@`d−1` + TNT read `[1]`@`d−1` → both `d−1` | −1 | ✅ |
| 3 | **FUSE** | **0** | NPM@`N` → TNT@`T` → CONT@`d`, with `N < T < d` (three **different** bars, span up to `2·SUDDEN_PROX`) | **no single bar exists** | ⚠️ **flagged** |
| 4 | CATALYST | −1 | NPM@`d−1` + CS1@`d−1` (both displacement+FVG) | −1 | ✅ |
| 5 | PBJ+NPM | −1 | NPM@`d−1` + PBJ read `[1]`@`d−1` | −1 | ✅ |
| 6 | PBJ+TNT | 0 | TNT@`d` + PBJ@`d` | 0 | ✅ |
| 7 | IGNITE TNT+CONT | 0 | TNT@`d` + CONT@`d` | 0 | ✅ |
| 8 | IGNITE NPM+CONT | −1 | NPM@`d−1` + CONT read `[1]`@`d−1` | −1 | ✅ |
| 9 | DYNAMITE | −1 | displaced `bar[1]`+`bar[2]`, FVG `bar[0]` → anchor `d−1` | −1 | ✅ |

### Tier 2 (enrichment-gated)

| # | Plot | Code offset | Atom chain | Rule-implied | Verdict |
|---|------|:----------:|-----------|:-----------:|:------:|
| 10 | TNT Enriched | 0 | TNT@`d` | 0 | ✅ |
| 11 | NPM Enriched | −1 | NPM@`d−1` | −1 | ✅ |
| 12 | CONT Enriched | 0 | CONT@`d` | 0 | ✅ (see §3 caveat) |
| 13 | RC TNT+RET Enriched | 0 | TNT@`d` + RET@`d` | 0 | ✅ |
| 14 | RC RET+NPM Enriched | −1 | NPM@`d−1` + RET read `[1]`@`d−1` | −1 | ✅ |
| 15 | PBJ+RET Enriched | 0 | PBJ@`d` + RET@`d` | 0 | ✅ |

### Other

| # | Plot | Code offset | Atom chain | Rule-implied | Verdict |
|---|------|:----------:|-----------|:-----------:|:------:|
| 16–18 | Density 1/2/3 | −1 | rolling window over `denVis` events, which include NPM@`d−1` | −1 | ✅ |
| 19–21 | UU/UUU/UUUU+TNT | −1 | U-streak whose chain touches Napalm (FVG) | −1 | ✅ |
| 22 | WBUSH (+Neutral) | 0 | Heavy-Pentagon current-bar atoms | 0 | ✅ |
| 23 | T1 RELAY | −1 | fires `d`, marks the 2nd of two consecutive visual bars = `d−1` | −1 | ✅ |
| 24 | T1 STACK | −1 | fires `d`, marks the stack bar = `d−1` | −1 | ✅ |

**Result: 23 of 24 plot families are internally consistent. FUSE is the sole
anomaly.**

---

## 2. FUSE — the deep dive (why the flag is correct)

### 2.1 What FUSE actually detects (`TNT_OD_v3.pine:1188-1199`)

```pine
if det_bullNapalm
    lastBullNPMVis := bar_index - 1     // NPM visual bar (honors NPM offset −1)
if det_bullTNT
    lastBullTNTVis := bar_index          // TNT visual bar (offset 0)
...
det_fuseBull = det_contBull                          // CONT fires NOW, on bar[0]
   and lastBullNPMVis < lastBullTNTVis               // NPM before TNT
   and lastBullTNTVis < bar_index                    // TNT strictly before now
   and (bar_index - lastBullTNTVis) <= SUDDEN_PROX   // TNT recent
   and (lastBullTNTVis - lastBullNPMVis) <= SUDDEN_PROX  // NPM→TNT tight
   and lastBullNPMVis >= sessionFirstBarIdx
```

Note the detection logic is **correct and careful**: it stores each atom's
*visual* bar (NPM at `bar_index − 1`, honoring its −1 offset; TNT at
`bar_index`). The bug is not in detection. It is in the **plot offset**.

### 2.2 Why offset 0's stated justification is nonsensical (user is right)

The three places that document FUSE offset all say the same thing:

- `:118` — `Offset: 0 (CONT has no displacement+FVG in its chain).`
- `:227` — tooltip `... Offset = 0.`
- `:1594` — alert-table `FUSE 0 p_fuseBull[1]`

The `:118` justification cherry-picks the **terminal** atom (CONT) and pretends
the chain is CONT-only. But **FUSE's chain literally is NPM → TNT → CONT.** The
**first** atom is a Napalm — displacement + FVG — the exact structure the offset
rule says forces −1. Judging the combo's offset by looking only at CONT, while
an NPM sits at the head of the chain, is internally inconsistent with the
project's own doctrine. **This is exactly the "the detection plot includes the
napalm as a confirmatory candle" objection, and it is valid.**

### 2.3 …but flipping to −1 does **not** fix it

Here is the subtlety that makes FUSE unique. Every other NPM-bearing combo
(rows 2, 4, 5, 8, 14) is a **same-visual-bar coincidence**: the NPM and its
partner land on the *same* bar once offset −1 is applied. FUSE is **not**. Its
three atoms sit on **three different bars**:

```
   bar N ........ bar T ........ bar d (=now)
   ▲NPM           ▲TNT          ▲CONT + FUSE fires
   └── ≤ SUDDEN_PROX ┘ └ ≤ SUDDEN_PROX ┘         (default 3 → span up to 6 bars)
```

- **offset 0** → marker on `bar[d]` (the CONT / culmination bar).
- **offset −1** → marker on `bar[d−1]` — one bar *before* CONT. That bar is
  **neither** the NPM bar, **nor** the TNT bar, **nor** the CONT bar. It is a
  meaningless bar. So −1 is *more* wrong, not less.
- The NPM bar is `lastBullNPMVis`, a **runtime-variable** distance back (1 to 6
  bars). `plotshape(..., offset=)` requires a **compile-time constant**. **No
  scalar offset can ever reach the NPM (or TNT) bar.**

**Conclusion:** FUSE is a variable-width cascade. A single scalar offset cannot
faithfully represent it. `0` is the *least-bad* scalar (it at least lands on a
**real** cascade bar — the CONT bar — and never repaints), but its **written
justification is wrong**, and if the design intent is "point at the candle that
lit the fuse," then `offset` is the wrong tool entirely.

### 2.4 The three honest resolutions

| Option | What it does | Behavior change | Cost |
|--------|--------------|:---------------:|------|
| **A. Keep 0, fix the comment** | Marker stays on the CONT/culmination bar. Replace the false "CONT has no displacement+FVG" note with the honest one: *"anchored at the cascade culmination (CONT bar); the NPM and TNT legs are a runtime-variable distance back and cannot be expressed as a scalar `plotshape` offset."* | none | 1-line comment |
| **B. Re-anchor to the ignition candle** | Draw FUSE on the NPM bar (`lastBullNPMVis`) — the displaced candle that lit the fuse — via `label.new(lastBullNPMVis, …)` instead of `plotshape`. Honors the "napalm is in the chain" intent literally. | marker moves back 1–6 bars | new label logic + alert-bar rework |
| **C. Re-anchor to the TNT bar** | Same as B but anchor `lastBullTNTVis` (structural-confirmation bar, the middle of the cascade). | marker moves back 0–3 bars | same as B |

Only **A** is a pure documentation fix. **B/C** change what the trader sees and
must also move the alert reference off `p_fuseBull[1]`, so they are a design
decision, not a mechanical correction.

---

## 3. Secondary note (not a FUSE issue) — CONT-via-Charge

`raw_contBull` (`:670`) can fire through a `raw_bullCharge` leg. Charge's real
candle is `bar[1]` (offset −1), yet CONT is treated as offset 0 everywhere
(rows 7, 12, and the CONT leg of FUSE). This is a pre-existing, **uniform**
simplification applied consistently to every CONT consumer, so it does not
create an inconsistency *between* plots. Logged here for completeness only; out
of scope for the FUSE question.

---

## 4. Bottom line

- The user's instinct is **correct**: FUSE's `offset = 0` **justification is
  nonsensical** — it ignores the Napalm sitting at the head of its own chain.
- The user's implied fix (offset should honor the napalm → −1) is **directionally
  right but mechanically impossible**: −1 lands on an unrelated bar, and no
  scalar offset can reach the napalm bar because it is a variable distance back.
- FUSE is the **only** one of the 24 detection-plot families that is a
  variable-width, multi-bar cascade; it is the one place the "co-locate all
  atoms on one visual bar" model has no scalar solution.
- Recommended: **Option A** (keep `0` as the culmination anchor, correct the
  false comment) unless the desired UX is "mark the igniting candle," in which
  case **Option B** (dynamic `label.new` on the NPM bar) is the only faithful
  implementation.
