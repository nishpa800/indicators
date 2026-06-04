# HVD-PBJ-PPD — CHANGELOG

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
