# HVD-PBJ-PPD — CHANGELOG

## 2026-07-17 — Combo Chain VISUAL-OFFSET correction (CANONICAL — supersedes 2026-06-04)

**The 2026-06-04 "fix" below was itself the defect. It is now reversed.** The
combo chain counts EVENTS, and an **event is a VISUAL plot (post-offset)** — never
a raw detection. Offset is applied *after* the combo condition is met, then you
count. The three combo visual plots carry different offsets:

- **Matrix combo** (CS2 = comboSet3/4) — offset **0**  → visual bar = detection bar → `[i]`
- **FVG combo** (CS1 = comboSet1/2) — offset **−1** → visual bar = detection bar−1 → `[i-1]`
- **Unified combo** (CS3 = csNew3)  — offset **−1** → visual bar = detection bar−1 → `[i-1]`

**Law (Anish):** on any single VISUAL bar the combo chain signs **1 or 0** — never
more. Matrix, FVG and Unified visual plots on the **same visual bar** OR-collapse to
**one** hit. A "**Unified combo**" is precisely the bar where all three visual plots
coincide (Matrix detected at N−1, FVG detected at N → all three drawn on visual bar
N−1); it is **one** hit, not two/three. A 2-hit chain therefore **requires two
distinct visual bars**.

- **What was wrong:** the 2026-06-04 counter used `hv2 = matrix[i] OR fvg[i]` — FVG
  read on the SAME slot as Matrix, i.e. the detection bar, **discarding FVG's −1
  offset**. On a Unified-combo setup (Matrix@N−1, FVG@N) that scored Matrix in slot
  `i=1` and FVG in slot `i=0` = **2 hits off one visual bar** → the chain fired off a
  single candle. That is the "big fuck up."
- **Fix:** restore the offset-aware, per-visual-bar OR-collapse and make the Unified
  term explicit:
  ```
  hv2 = comboSet3[i] or comboSet4[i]                       // Matrix, offset 0  -> [i]
  if i>=1 and (comboSet1[i-1] or comboSet2[i-1]            // FVG,     offset -1 -> [i-1]
               or csNew3[i-1])                             // Unified, offset -1 -> [i-1]
      hv2 := true                                          // OR-collapsed -> one binary hit
  ```
  Applied to both the bull and bear chain loops in all HVD-PBJ-PPD studies:
  `versions/HVD_PBJ_PPD_BULLISH_v1.pine`, `versions/HVD_PBJ_PPD_BEARISH_v1.pine`,
  `versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine`, both
  `tick_friendly/HVD_PBJ_PPD_*_v1_tick_friendly.pine`, and the two matching
  `june7-conversion/tick_friendly_pine/hvd pbj *` builds.
- **Proven (Python replay, `scratchpad/replay.py` logic):** Unified combo (Matrix@N−1,
  FVG@N) → count **1**, no fire ✓. Two distinct combo visual bars → fire ✓. FVG-only
  on one bar → no fire ✓.
- **Follow-up owed:** the companion Python ports
  `realtime-indicators/rti/signals_{tick,time}/combo_chain_fixed.py` and the standalone
  are regenerated against this corrected law; the ports live in the other repo and
  must be re-synced there.

## 2026-06-04 — Combo Chain BINARY-LAW fix (SUPERSEDED 2026-07-17 — see above)

**Retracted:** this entry misread FVG's −1 offset as a bug and collapsed the count
onto the detection bar. Kept for history only.

**This is now the real version. The prior combo-chain logic is retired as incorrect.**

- **Defect:** the combo-chain counter read FVG combo with a cross-bar shift
  (`comboSet1_*[i-1]`). At `i=1` that resolved to the CURRENT bar, so a single
  candle carrying BOTH Matrix combo and FVG combo filled two window slots and
  self-counted to **2** — illegally firing a chain off one bar.
- **Law (Anish):** one physical bar = **1 or 0**. Matrix combo (CS2 =
  comboSet3/4, offset 0) and FVG combo (CS1 = comboSet1/2) on the SAME physical
  bar OR-collapse to a single hit. A 2-hit chain requires **two different bars**.
- **Fix:** `hv2 = matrix[i] OR fvg[i]` (same offset, OR-collapsed) in both the
  bull and bear chain loops. Applied to:
  - `versions/HVD_PBJ_PPD_BULLISH_v1.pine` (commit f36e7c6)
  - `versions/HVD_PBJ_PPD_BEARISH_v1.pine` (commit 069550e)
  - merged to `main` as 98e56a0.
- **Proven:** Python replay — one bar with Matrix+FVG+PBJ does NOT fire; two
  distinct bars chain. See `realtime-indicators/rti/signals_{tick,time}/combo_chain_fixed.py`.
- **Parity note:** intentionally diverges from the old TradingView output on the
  single-mixed-bar case. That divergence is the fix.
