# HVD-PBJ-PPD — CHANGELOG

## 2026-07-04 — BEARISH v1 Indicator Study Audit + tick-friendly RE10023 fix

- **Trigger:** `RE10023 — Cannot call timeframe.change with a tick-based timeframe`
  on bar 0 (`tv_ta.relativeVolume():346 → #main():267`) when the BEARISH (36) study
  is loaded on a tick chart.
- **Audit:** full study audit written to
  `HVD_PBJ_PPD_BEARISH_v1_STUDY_AUDIT.md` — tick-hazard surface (exhaustive scan:
  3 `relativeVolume()` calls + `tfSec`, nothing else) and a full **offset audit of
  all 36 plotshapes**.
- **Offsets:** all 36 correct and internally consistent (rule: HV/displacement/FVG/
  Matrix-anchored → `offset=-1` on bar T-1; pure current-bar composites → `offset=0`).
  The flagged **Unified Combo (`CS3R`/`csNew3_Bear`) `offset=-1` is CORRECT** — it lands
  on the shared T-1 confluence bar (FVG middle bar == Matrix volume bar), matching CS1's
  marker and CS2's fire bar. One cosmetic note: `A★ Bear` (AlphaStrike, off by default,
  non-trusted here) is a current-bar composite plotted `offset=-1`; left as-is for parity.
- **Fix:** `tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine` already carried the
  correct `reg_anchorSafe` + `tfSec` guards (postmortem 2026-06-04 form); aligned its
  shorttitle to the source lineage → **`HVD PBJ PPD BEAR TF`**. Detection logic and every
  offset are byte-identical to the source → time-chart parity is bit-for-bit.
- **Housekeeping:** `versions/HVD_PBJ_PPD_BEARISH_v1.pine` shorttitle `HVD PBJ BEAR` →
  `HVD PBJ PPD BEAR` (matches the `HVD_PBJ_PPD` filename, the module, and the user's file;
  display-string only, no logic change).

## 2026-06-04 — Combo Chain BINARY-LAW fix (CANONICAL)

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
