# Squarify

**Current version:** `v2` → `versions/SQUARIFY_v2.pine`

## What it is

Aggregator Pine indicator. Originally 64 numbered signals; v2 trimmed to 46 contiguous after removing B2B PUP overlaps, reserved slots, CONT, and replacing WMD with WBUSH.

## Signal taxonomy (v2 = 46 plots)

**1-13 USE Standalone:** SD!, SUPER, HW, FLOOR, 2F, UUUU, UUU, UU, A★, ΩA, FOX, OD, GOLF
**14-21 ULTRA 57 (Foster / Cluster / Exhaustion):** PBJ+F2/E3, PBJ+CL, F2CL→E3, E3⅔PP, F2×2D, E3×2D, F2E3seq, CL×2D
**22-26 NPM:** NPM+, NPM12, NPM3, B2BNPM, NPM+TNT
**27-31 HV+D:** CO, HVD+PBJ, B2BHVD+PBJ, B2BHVD, UU+UC
**32-39 Fusions:** GRAIL, FLR+NPM, NPM+PBJ+PUP, NAG+, UU+HVD, UU+NPM, FLR+UU, FOS+PUP+1x
**40 NPM+UC**
**41-43 WBUSH:** Bull, Bear, Neutral
**44 NPM+UC+PBJ**
**45-46 UC NAGASAKI:** Bull, Bear

## Cross-indicator relationship

- **B2B PUP** owns all `det_b2bPUP` combinations. Squarify v2 does NOT duplicate those (kept GOLF only — distinct 3-bar pattern).
- **TNT OD** is canonical for Napalm / TNT / CONT. Squarify v2 ports the same Napalm definition (consolidated NPM = raw OR Charge) and U-streak pG path.
- **HEAVY PENTAGON** is canonical for the 5 Heavy Combos (Yin-Yang, Nagasaki, Nagasaki Vol, Trident, Neutral Heavy x2). Squarify v2 ports them and aggregates as WBUSH.

## Deploy

```bash
pbcopy < ~/code/anish/indicators/squarify/versions/SQUARIFY_v2.pine
# TradingView Desktop → Pine Editor → Cmd+A → Cmd+V → Cmd+S → Add to Chart
```
