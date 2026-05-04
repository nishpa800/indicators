# TNT Opening Drive (OD)

**Current version:** `v2` → `versions/TNT_OD_v2.pine`
**Source pasted by Anish:** 2026-05-04 (v1 baseline). v2 produced same session — see CHANGELOG.

## What it is

Extreme-anomaly detection focused on the opening drive. Tier-1 / Tier-2 fire-control with hard-gated enrichment. Includes DYNAMITE auto-promote (B2B displacement + FAUNA on both bars), UU/UUU/UUUU + TNT-any-signal fusion, and density signals.

## Reference role

**TNT OD is the canonical source-of-truth for Napalm / TNT / CONT definitions across the suite.** Any other indicator (B2B PUP, etc.) that includes these engines must mirror TNT OD's logic exactly.

When TNT OD is updated, audit downstream indicators for drift:
- B2B PUP — Engine G (TNT / Napalm / Cont) — see `../b2b-pup/`

## Key Tier-1 signals
- B2B Napalm Bull/Bear
- RC NPM+TNT
- FUSE
- CATALYST
- PBJ+NPM, PBJ+TNT, NPM+PBJ Unsup
- IGNITE (TNT+CONT or NPM+CONT)
- DYNAMITE (B2B disp + FAUNA on both bars)

## Key Tier-2 signals (require enrichment)
- TNT Raw + Enriched
- Napalm Raw + Enriched
- Continuous Raw + Enriched
- RC TNT+RET, RC RET+NPM, PBJ+RET

## Architecture

- **VOB engine** (volume-block via EMA fast/slow cross)
- **Anish swing engine** (order-block on swing break with previous-OB overlap requirement)
- **Flux engine** (pullback into prior OB)
- **Confluence**: temporal-OK across all 3 + zone overlap → TNT raw
- **Zone tracking** (full Zone type with active flag + returnFired flag)
- **TNT 2.0** (event-log path: 2+ Bull or Bear events recently)
- **CONT 3-clause logic** (Return-leg / TNT-leg / TNT 2.0-leg)
