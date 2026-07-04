# TNT OD v3 — Unit Building Blocks of Every Detection Plot

**Purpose:** answer one question for every plot in this study — *what atoms is it made of?*
("RC NPM+TNT" → **Napalm + TNT**), and pin down the two things that read as vague today:
**offset** and the **RELAY / STACK** definitions.

**Source of truth (read 2026-07-04):**
- `versions/TNT_OD_v3.pine`
- `tick_friendly/TNT_OD_v3_tick_friendly.pine` — *detection logic, plots and alerts are byte-identical
  to the version build*; the tick build only swaps the rel-vol anchor (`"" → "D"`) and guards
  `timeframe.in_seconds` on tick charts. Nothing in this document differs between the two files.

**What this is NOT:** this is not the Pine source of each atom. When you ask "what is Napalm?" the
answer here is **one plain line** ("a displacement candle that punches an opposing TNT zone"), not the
`disp_range[1] > threshold and isBullishFVG and low[1] > z.level …` code. The code lives in the `.pine`
file; this document is the block diagram above it.

---

## How to read a formula

| Notation | Means |
|---|---|
| `A + B` | atom A **and** atom B resolve to the **same visual bar** (after the code's internal `[1]` shifts) |
| `A → B → C` | A then B then C, in that **order**, inside a proximity window (sequential cascade) |
| `A ×2` | atom A on **two consecutive** bars (bar[1] **and** bar[2]) |
| `A (bar[1])` | atom A taken **one bar back** from the fire bar |
| **gate** | the v3 OR-of-6 conditional gate (see §3) |
| **enrich** | any one USE-V5 co-signal (see §3) |

A "visual bar" is the bar the shape paints on. The **fire bar** is bar[0] (where the boolean turns
true). Offset is only ever `0` or `-1`, i.e. the visual paints on the fire bar or one bar behind it.

---

## §1 — The atoms (unit building blocks)

Every plot below is assembled from these. Definitions are conceptual on purpose (per the ask).

### Structural / zone family
| Atom | What it is (one line) |
|---|---|
| **TNT** | A structural confluence **zone**: three independent zone engines mark the same price area within a short window and a synergy filter confirms it. `TNT = VOB + ANISH + FLUX` (+ synergy). Also fires as **TNT 2.0** (2+ recent bull/bear zone events) and **Super TNT** (TNT coinciding with an opposing charge). |
| ├ **VOB** | Volume order-block off an EMA fast/slow cross. |
| ├ **ANISH** | Order block printed when a swing high/low breaks, requiring overlap with the prior order block. |
| └ **FLUX** | A pullback into a still-active prior order block. |
| **RET** | **Return** — after a zone breaks, price retraces back into that TNT zone (1.0 or 2.0). |

### Displacement family (contains an FVG → drives offset −1)
| Atom | What it is (one line) |
|---|---|
| **DISP** | **Displacement** — one bar's range exceeds a σ-multiple of its recent stdev **and** the next bar leaves a fair-value gap (FVG) past it. The σ candle is bar[1]; the FVG confirms on bar[0]. |
| **FVG** | Fair-Value Gap — a 3-bar gap where the middle bar jumps clear of the outer two. **Mandatory** in every DISP. |
| **NPM** | **Napalm** — a DISP that punches through an opposing, still-active **TNT zone** level, **or** clears a stored **charge** level. `NPM = DISP + (opposing zone OR charge cleared)`. Because it contains a DISP, its meaningful candle is bar[1]. |
| └ **Charge** | A DISP that violates a stored opposing charge level (folded into NPM at the detection level). |

> **Five independent DISP engines.** DISP is one *idea* with five *threshold instances* that never share
> knobs: **#1 Main** (`DISP_STD_LEN/DISP_STD_X`, 5σ) feeds NPM/Charge/B2B/Catalyst/RC-NPM+TNT/Sudden-change/CONT/Ignite-N+C;
> **#2 DYNAMITE** (`dynStdMult`, 5σ, dedicated); **#3 USE-V5** (`u5_std_*`, 3σ) feeds enrichment + WBUSH direction;
> **#4 HCT** (`hct_disp_*`, 6σ); **#5 Gate** (`gateStdMult`, 6.5σ). Same shape, five separate throttles.

### Event-flow family
| Atom | What it is (one line) |
|---|---|
| **CONT** | **Continuous** — two zone/charge/return events fire within `SUDDEN_PROX` bars of each other (a rapid-fire burst). Has **no FVG of its own**. |

### Volume / anatomy enrichment atoms (USE-V5 pipeline)
| Atom | What it is (one line) |
|---|---|
| **RVOL tiers** | Price-spike rank (body move vs its own recent average): **SAAB < RVOL 1x < Grand Slam** (bull) / **Kratos < RVOL1xR < MOAB** (bear). |
| **WMD tiers** | Relative-volume-at-time rank: **Pentagon < WTC < Hiroshima**, plus **Nagasaki**. `WMD = any of those four`. |
| **Nagasaki** | All-time-high volume bar (running max). Also used standalone by the gate, CS1 and WBUSH. |
| **HV1000** | Volume is the highest in the last 1000 bars. |
| **FAUNA** | Candle-anatomy qualifier — the bar is a Momentum Bar, Range Expansion, Trend Acceleration, or Gap-&-Go (on volume). |
| **CS1** | FVG Combo — consecutive or HV-backed fair-value gaps, confirmed by an RVOL/WMD tier. |
| **PUP / PPD** | A >3 % body move on volume exceeding the recent opposing-colour high (PUP = up, PPD = down). |
| **PBJ** | A supertrend-style reversal entry (VWMA ± ATR trailing stop) firing on the trail crossover after a pullback/re-accel into a level. |

### Meta-combos that are themselves used as atoms
| Atom | What it is (one line) | Has its own plot in TNT OD? |
|---|---|---|
| **HCT** | Inline Heavy-Combo-Toggles, using **HCT's own thresholds**: a heavy RVOL/WMD combo base **AND** HCT displacement → `hct_bull / hct_bear / hct_neutral`. | **No** — used only inside the gate and RELAY/STACK. |
| **UC** | **Unified Combo (placeholder)** — ≥ 2 distinct streams from {FAUNA, RVOL tier, WMD, PUP/PPD, CS1}. Explicitly marked replaceable in code. | **No** — gate + RELAY/STACK only. |
| **WBUSH** | HEAVY PENTAGON's 5 heavy-volume combos (Yin-Yang, Nagasaki, Nagasaki-Vol, Trident, Neutral-Heavy-×2), direction-classified by USE-V5 displacement. | **Yes** — 3 plots. |

---

## §2 — Every detection plot as an atom formula

This is the core table. Read it as "this plot = these blocks." `Gated?` = whether the v3 gate (§3) is
applied on top.

### Tier 1
| Plot | Building blocks | Alignment | Offset | Gated? |
|---|---|---|---|---|
| **B2B NAPALM** | `NPM ×2` | Napalm on bar[1] **and** bar[2] (two in a row), same direction | **−1** | ✅ |
| **RC NPM+TNT** | `NPM + TNT` | both on the same visual bar | **−1** | ✅ |
| **FUSE** | `NPM → TNT → CONT` | sequential cascade inside `SUDDEN_PROX`, terminates on the CONT bar | **0** | ❌ |
| **CATALYST** | `NPM + CS1` | same visual bar | **−1** | ✅ |
| **PBJ+NPM** | `PBJ + NPM` | same visual bar | **−1** | ✅ |
| **PBJ+TNT** | `PBJ + TNT` | same visual bar | **0** | ❌ |
| **IGNITE T+C** | `TNT + CONT` | same visual bar | **0** | ❌ |
| **IGNITE N+C** | `NPM + CONT` | same visual bar | **−1** | ❌ |
| **DYNAMITE** | `DISP ×2 + FAUNA ×2 + FVG` | two consecutive σ-candles, FAUNA on each, FVG confirm on bar[0] | **−1** | ❌ |

> IGNITE is **one enable / two plots** (`IGNITE T+C`, `IGNITE N+C`) with **different offsets**. That's
> correct, but it is the single most misread item in the study — one checkbox drives two markers that
> land on different bars.

### Tier 2 — each is `raw atom + enrich (+ gate)`, hard-gated (never fires without enrichment)
| Plot | Building blocks | Offset | Gated? |
|---|---|---|---|
| **TNT ENRICHED** | `TNT + enrich` | **0** | ✅ |
| **NPM ENRICHED** | `NPM + enrich` | **−1** | ✅ |
| **CONT ENRICHED** | `CONT + enrich` | **0** | ✅ |
| **RC TNT+RET ENR** | `(TNT + RET) + enrich` | **0** | ✅ |
| **RC RET+NPM ENR** | `(RET + NPM) + enrich` | **−1** | ✅ |
| **PBJ+RET ENR** | `(PBJ + RET) + enrich` | **0** | ✅ |

### Density — temporal count of Tier-1/2 visual events
| Plot | Building blocks | Offset | Gated? |
|---|---|---|---|
| **DENSITY 1** | `≥ 2 TNTOD visual events within 2 bars` | **−1** | ❌ |
| **DENSITY 2** | `≥ 3 within 3 bars` | **−1** | ❌ |
| **DENSITY 3** | `≥ 2 within 6 bars` | **−1** | ❌ |

> The "event" counted is `denVis` = **any** of {TNT, CONT, RC-TNT+RET, PBJ+TNT, PBJ+RET (all bar[1]),
> NPM, RC-NPM+TNT, RC-RET+NPM, PBJ+NPM (all current)} on the same direction. **Note it does not require
> Napalm** — a cluster of three TNT-only bars fires density (relevant to the offset note in §4).

### UU / UUU / UUUU + TNT ANY
| Plot | Building blocks | Offset | Gated? |
|---|---|---|---|
| **UU + TNT ANY** | `2-bar RVOL streak (qualified) + any TNTOD signal in window` | **−1** | ❌ |
| **UUU + TNT ANY** | `3-bar streak (≥ 3 distinct qualifiers) + any TNTOD signal` | **−1** | ❌ |
| **UUUU + TNT ANY** | `4-bar streak (≥ 4 distinct qualifiers) + any TNTOD signal` | **−1** | ❌ |

> "Streak qualified" = the streak passes path pA/pB/pC/pE/pF **or** pG (≥ k distinct qualifiers from
> {PBJ, DISP, FAUNA, SAAB, RVOL1x, GrandSlam}, k = streak length). "TNT ANY" = any TNTOD detection in
> the streak window.

### WBUSH — HEAVY PENTAGON state × any TNTOD plot
| Plot | Building blocks | Offset | Gated? |
|---|---|---|---|
| **WBUSH+TNTOD ANY Bull** | `WBUSH-bull state + any TNTOD bull plot` | **0** | ❌ |
| **WBUSH+TNTOD ANY Bear** | `WBUSH-bear state + any TNTOD bear plot` | **0** | ❌ |
| **WBUSH Neutral** | `WBUSH-neutral state` (standalone, no TNTOD pairing) | **0** | ❌ |

### T1 RELAY / T1 STACK — see §5 (this is where "vague" lives)
| Plot | Building blocks | Offset | Gated? |
|---|---|---|---|
| **T1 RELAY** | `any Tier-1 visual on bar[2] + any Tier-1 visual on bar[1]` (same direction) | **−1** | ❌ (inherited only) |
| **T1 STACK** | `≥ 2 distinct Tier-1 visuals on bar[1]` (same direction) | **−1** | ❌ (inherited only) |

---

## §3 — The v3 gate and "enrich" (the two shared modifiers)

Both are **OR-nets** (any-one-of), which is *why* the plots that use them read as loose. Spelling them out:

**gate** (`en_newGate`, default ON) — a plot passes if **any one** of these 6 is true on its visual bar:
`RVOL 1x` · `Grand Slam` (bear: `MOAB`) · `UC` · `Nagasaki + any tier` · `HCT` · `DISP ≥ 6.5σ (Engine #5)`.
When `en_newGate` is OFF the gate is a constant pass-through (legacy v2 behaviour).

**enrich** — a Tier-2 plot passes if **any one** USE-V5 co-signal is present:
`RVOL 1x` · `Grand Slam/MOAB` · `PUP/PPD` · `CS1` · `FAUNA` · `WMD` · `HV1000` (offset-−1 variants also
accept `Pentagon/WTC/Hiroshima/Nagasaki` individually and `DYNAMITE`).

**Who is gated** (verified line-by-line):
- **Gated:** the 4 NPM-family Tier-1 (B2B, RC NPM+TNT, CATALYST, PBJ+NPM) + **all 12** Tier-2.
- **Not gated:** FUSE, PBJ+TNT, IGNITE (both), DYNAMITE, Density, UU-family, WBUSH, RELAY, STACK.
- RELAY/STACK inherit the gate **only** through the 4 already-gated candidates in their pool — the other
  7 candidates enter ungated. So the gate is applied **heterogeneously** inside RELAY/STACK, not as one
  clean filter.

---

## §4 — Offset: the real rule, and where the prose misleads

### The operative rule (what the code actually does)
> A plot is **`offset = −1`** ⟺ **its defining displacement candle sits on bar[1] of the fire bar** —
> the boolean turns true on bar[0], but the candle that *matters* (the σ-range candle whose FVG confirms
> on bar[0]) is one bar back. Everything whose defining event is **on** the fire bar is **`offset = 0`**.

### Mechanical consistency — PASS
For every plot, three things must agree: the `offset=` param on the plotshape, the alert gate
(`alertOK_N` vs `alertOK_N1`, `firstStatus_N` vs `_N1`), and the gate index (`gate_bull` vs
`gate_bull[1]`). **All three agree on every plot** — audited across all 49 plotshapes and their alert
blocks. There is **no desync**: nothing paints on one bar while alerting for another. (The v2/v3 audits
appear to have already closed the historical mismatches.)

| Offset | Plots | `offset=` | Alert gate | Gate index |
|---|---|---|---|---|
| **−1** | B2B, RC NPM+TNT, CATALYST, PBJ+NPM, IGNITE N+C, DYNAMITE, NPM-ENR, RC RET+NPM-ENR, Density 1/2/3, UU/UUU/UUUU, T1 RELAY, T1 STACK | `-1` | `_N1` | `gate_bull[1]` |
| **0** | FUSE, PBJ+TNT, IGNITE T+C, TNT-ENR, CONT-ENR, RC TNT+RET-ENR, PBJ+RET-ENR, WBUSH ×3 | *(none)* | `_N` | `gate_bull` |

### Where the *prose* misleads (the real source of "offset is unclear")
The header comment justifies offsets with the shorthand *"the chain contains a displacement+FVG → −1."*
That shorthand is **looser than the real rule** and mis-describes two families:

1. **FUSE, IGNITE T+C, PBJ+TNT are offset 0 even though a displacement can be in the picture.**
   FUSE's cascade literally contains an NPM (a DISP+FVG) — so the shorthand predicts −1, but the plot is
   **0 and that is correct**: FUSE fires on the terminal **CONT** bar, and the NPM leg is ≥ 2 bars back,
   **not** on bar[1] of the fire. The header line *"CONT has no displacement+FVG in its chain"* is the
   misleading part — the chain does contain one; it just isn't the defining candle. Under the operative
   rule (bar[1] test) the 0 is right.

2. **Density / UU are offset −1 justified as "chain touches Napalm w/ FVG" — but they can fire with no
   Napalm at all.** `denVis` and the U-streak include TNT/CONT/RET-only events. The **offset −1 is still
   correct**, but for a *different* reason than stated: `denVis`/streak booleans are already defined on
   **visual bar 1** (they read `[1]` on the offset-0 atoms), so the marker belongs on bar[1] regardless
   of whether displacement was involved. Right answer, wrong stated reason.

**Bottom line for the offset question:** mechanically it is fully consistent; the confusion is entirely
in the header's prose, which should read *"offset −1 ⟺ the defining candle is on bar[1] of the fire
bar"* and drop the "chain contains a displacement" shorthand.

---

## §5 — RELAY & STACK, de-vagued

Both draw from one **11-candidate Tier-1 pool**, and for each candidate the code knows exactly what
"its visual landed on bar[1]" means (offset-−1 candidates use the **bare** current-bar boolean;
offset-0 candidates use `[1]`). That per-candidate mapping is **internally consistent** — this part is
*not* sloppy. What is loose is the **combination rule**.

### The pool (11) and their "visual on bar[1]" source
| # | Candidate | Own offset | "visual on bar[1]" is… |
|---|---|---|---|
| 1 | B2B NAPALM | −1 | `p_b2bBull` (current) |
| 2 | RC NPM+TNT | −1 | `sig_rcNTBull` (current) |
| 3 | CATALYST | −1 | `p_catBull` (current) |
| 4 | PBJ+NPM | −1 | `p_pnBull` (current) |
| 5 | IGNITE N+C | −1 | `p_ignBull and ign_nc_bull` (current) |
| 6 | DYNAMITE | −1 | `p_dynBull` (current) |
| 7 | FUSE | 0 | `p_fuseBull[1]` |
| 8 | PBJ+TNT | 0 | `p_ptBull[1]` |
| 9 | IGNITE T+C | 0 | `p_ignBull[1] and ign_tc_bull[1]` |
| 10 | HCT | −1 (declared) | `hct_bull` (current) |
| 11 | UC | 0 (declared) | `uc_bull[1]` |

*(HCT and UC have no standalone plot in TNT OD, so their "offset" is a declared alignment assumption:
HCT = −1 because its chain has a DISP+FVG; UC = 0 because it's current-bar atoms only.)*

### T1 RELAY = `(any of the 11 on bar[2]) AND (any of the 11 on bar[1])`, same direction
- **Offset −1** → paints on bar[1] (the second of the two bars).
- **Why it reads vague, precisely:**
  - It is **"any AND any"** — the bar[2] signal and the bar[1] signal need **nothing in common**. Bar[2]
    could be a UC and bar[1] a FUSE. It only asserts *"two consecutive bars each had ≥ 1 Tier-1-ish
    visual."*
  - **Same type counts** (by design): CATALYST→CATALYST is a valid RELAY. So it can be one repeating
    signal, not an escalation.
  - The pool includes **HCT, UC, FUSE, IGNITE** — themselves OR-combos — so "any Tier-1" is a wide net.

### T1 STACK = `≥ 2 distinct of the 11 on bar[1]`, same direction
- **Offset −1** → paints on bar[1].
- **Why it reads vague, precisely:** "distinct" counts **distinct booleans**, not **independent
  events**. Several candidates share the same underlying atom, so one strong bar double/triple-counts:
  - `B2B`, `RC NPM+TNT`, `PBJ+NPM`, `CATALYST`, `IGNITE N+C` **all contain NPM** — a single Napalm bar
    that also has a TNT and a PBJ can light up RC NPM+TNT **and** PBJ+NPM **and** (if the prior bar was
    Napalm) B2B simultaneously → STACK reports **"3 distinct"** off essentially **one** displacement.
  - `IGNITE N+C` ⊂ `NPM + CONT`; `IGNITE T+C` ⊂ `TNT + CONT` — the IGNITE variants overlap the CONT-based
    candidates.
  - So **STACK's count is an upper bound on genuine confluence, not a measure of it.**

### If you want these tightened (behaviour change — not done here)
These are documentation notes; the code is unchanged. If desired, say the word and I can:
- make **RELAY** require the two bars to be **different** candidate types (real escalation), and/or
- make **STACK** count **independent atom families** (NPM / TNT / CONT / RET / PBJ / volume) instead of
  raw booleans, so overlapping combos can't inflate the count.

---

## §6 — The honest "still fuzzy" list

Everything below is an **OR-of-N** ("fires if any one of…"), which is exactly the pattern the ask flags.
None are bugs; they are breadth choices. Listed so the breadth is explicit, not hidden:

| Where | The OR-net | Practical effect |
|---|---|---|
| **gate** (§3) | any 1 of 6 | one weak co-signal (e.g. a single RVOL 1x) satisfies the gate for the whole NPM-family + Tier 2 |
| **enrich** (§3) | any 1 of 7–11 | Tier-2 "hard-gate" is wide; almost any volume/anatomy blip enriches |
| **UC** | ≥ 2 of 5 | placeholder — not the real Squarify v2 UC; currently a 2-of-5 net |
| **Nagasaki + Any** | Nagasaki AND (any tier) | the "Any" is itself an OR of 6 |
| **denVis / TNT-ANY** | any TNTOD event | density and UU treat *all* detections as interchangeable |
| **WBUSH × ANY** | any TNTOD plot | direction/volume state × the same "any TNTOD" net |
| **RELAY / STACK** | any + any / ≥2 distinct | see §5 — no diversity or independence requirement |

**One-line summary of the whole study's shape:** a set of **displacement/zone atoms** (NPM, TNT, CONT,
RET, DISP) combined pairwise or in short cascades into Tier-1 plots, each optionally **AND-ed with a wide
OR-net of volume/anatomy co-signals** (gate, enrich) — and RELAY/STACK/Density/UU/WBUSH sitting on top as
**meta-detectors over the Tier-1/2 outputs.** Offset is mechanically clean; the only genuine clarity debt
is the header's loose prose (§4) and the un-diversified "any/distinct" nets (§5, §6).
