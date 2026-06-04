# Squarify

**Current lower-timeframe version:** `SQUARIFY LTF v1` → `tick_friendly/SQUARIFY_LTF_v1_tick_friendly.pine`

**High-timeframe legacy version:** `SQUARIFY HTF` → `versions/SQUARIFY_HTF_v1.pine`

## What it is

Aggregator Pine indicator. The old production study is now named **Squarify HTF**. The prevailing lower-timeframe/tick build is **Squarify LTF v1**.

SQUARIFY LTF is intended for 5/10-tick style charts and lower timeframes such as 10s, 15s, 30s, and 45s. It can still be used on daily if desired, but it is not tuned to over-limit signals on multi-day/week charts.

## LTF v1 Rule Changes

- `SUPER` = UC + one of Napalm, RVOL1x, or Grand Slam.
- `SD!` = UC + one of Napalm, RVOL1x, or Grand Slam + PUP.
- Optional checkbox: if checked, every detection plot requires Unified Combo on the same visual candle. If unchecked, UC is not required.
- Optional checkbox: if checked, U2/U3/U4 require high-volume rank >= 100 somewhere in the U window.
- S22-S24 replace Napalm with RVOL1x or Grand Slam.
- CO requires UC. FVG Combo Set alone no longer qualifies.
- HCT v2 uses bull-side WBUSH only; bear combos are not HCT v2.
- Pentagon-family means Pentagon, WTC, Hiroshima, or Nagasaki.
- S47/S48/S49 all require displacement and alert details name the `ANY` component.
- Omega-A alert details name the co-signal.

## Signal taxonomy (LTF v1 = 49 plots)

**1-13 USE Standalone:** SD!, SUPER, HW, FLOOR, 2F, UUUU, UUU, UU, A★, ΩA, FOX, OD, GOLF
**14-21 ULTRA 57 (Foster / Cluster / Exhaustion):** PBJ+F2/E3, PBJ+CL, F2CL→E3, E3⅔PP, F2×2D, E3×2D, F2E3seq, CL×2D
**22-26 NPM:** NPM+, NPM12, NPM3, B2BNPM, NPM+TNT
**27-31 HV+D:** CO, HVD+PBJ, B2BHVD+PBJ, B2BHVD, UU+UC
**32-39 Fusions:** GRAIL, FLR+NPM, NPM+PBJ+PUP, NAG+, UU+HVD, UU+NPM, FLR+UU, FOS+PUP+1x
**40 NPM+UC**
**41-43 WBUSH:** Bull, Bear, Neutral
**44 NPM+UC+PBJ**
**45-46 UC NAGASAKI:** Bull, Bear
**47-49 HV + ANY:** 1K+ANY, PENT+500+ANY, PENT+1K+ANY

## Cross-indicator relationship

- **B2B PUP** owns all `det_b2bPUP` combinations. Squarify v2 does NOT duplicate those (kept GOLF only — distinct 3-bar pattern).
- **TNT OD** is canonical for Napalm / TNT / CONT. Squarify v2 ports the same Napalm definition (consolidated NPM = raw OR Charge) and U-streak pG path.
- **HEAVY PENTAGON** is canonical for the 5 Heavy Combos (Yin-Yang, Nagasaki, Nagasaki Vol, Trident, Neutral Heavy x2). Squarify v2 ports them and aggregates as WBUSH.

## Deploy

```bash
pbcopy < ~/code/anish/indicators/squarify/tick_friendly/SQUARIFY_LTF_v1_tick_friendly.pine
# TradingView Desktop → Pine Editor → Cmd+A → Cmd+V → Cmd+S → Add to Chart
```
