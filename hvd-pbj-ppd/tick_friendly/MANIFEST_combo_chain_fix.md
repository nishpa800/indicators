# Combo Chain Fix — Conversion Manifest

**Date:** 2026-06-04
**Source indicator:** `BASE HV+D ↔ PBJ ↔ PPD v1 (no HTF)` (shorttitle `BASE HVD PBJ`)
**Trigger:** Anish reported combo chain compromised; demanded binary-law fix across three outputs.

## The defect (proven from pasted source)

Original Pine (`grp_cc` block):
```
for i = 0 to cc_window-1
    hv2 = comboSet3_Bull[i] or comboSet4_Bull[i]          // Matrix at bar N-i
    if i >= 1 and (comboSet1_Bull[i-1] or comboSet2_Bull[i-1])  // FVG at bar N-(i-1)
        hv2 := true
    if hv2: cc_win_bull += 1
```
The `[i-1]` cross-bar shift lets a SINGLE firing bar carrying both Matrix and
FVG fill two slots — `matrix(N)` in slot i=0 and `fvg(N)` in slot i=1 — so
`cc_win = 2` off one bar. With `cc_min_hits=2`, the chain fires off ONE candle.

## The law (Anish, 2026-06-04)

- Matrix combo counts. Offset **0** (belongs to its own bar).
- FVG combo counts. Offset **−1** (belongs to the bar one before it fires).
- One physical bar = **1 or 0**. Never more.
- Matrix AND FVG on the **same physical bar = one hit**, not two.
- A 2-hit chain requires **two different bars**.

## The fix

```
per_bar_hit[t] = matrix[t] OR fvg[t]   # same physical bar, OR-collapsed → max 1
count = sum over distinct bars t in window of per_bar_hit[t]
fire  = count >= min_hits AND (pbj in window)   # + original latch
```

Proven (signals_time/combo_chain_fixed.py replay):
- One bar with both Matrix+FVG+PBJ → `[False]` (1 hit, no fire). ✅
- Two distinct bars each with a combo + PBJ → fires on bar 2. ✅

## Outputs on disk

| # | Output | Path |
|---|--------|------|
| 1 | Pine tick-friendly | `indicators/hvd-pbj-ppd/tick_friendly/COMBO_CHAIN_FIXED_tick_friendly.pine` |
| 2 | Python tick-based | `realtime-indicators/rti/signals_tick/combo_chain_fixed.py` |
| 3 | Python time-based | `realtime-indicators/rti/signals_time/combo_chain_fixed.py` |
| 4 | Manifest | this file |

## Scope / honesty notes

- This conversion targets the **combo-chain subsystem** (the compromised part),
  the named focus. It consumes the terminal booleans Matrix Combo (`csNew2` /
  `CS2 MAT`), FVG Combo (`csNew1` / `CS1 FVG`), and PBJ/PB — exactly as the
  parent indicator already produces them. Upstream engine ports (FAUNA, GZ1 FVG,
  RVOL, Ping Pong, Boom Hunter, etc.) are NOT re-ported here.
- Tick-friendly Pine feeds Matrix/FVG/PBJ via `input.source()` so it runs on any
  tick chart against the parent indicator's plots — no time-based session math.
- **Parity NOT claimed.** This prepares parity handoff; the binary fix
  intentionally diverges from the original (buggy) TradingView output on the
  single-mixed-bar case.

## Pending

- **Bullish split version** (`HVD_PBJ_PPD_BULLISH_v1.pine`) has the SAME chain
  defect per Anish. Same fix (same-bar OR-collapse) applies. Awaiting paste —
  will be corrected in this same thread for consistency.
- Full combined `BASE` source intake should be saved as a versioned `.pine` once
  the bullish/bearish reconciliation is settled.
