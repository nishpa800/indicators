# Path-A Logger Coverage Audit — 2026-05-11

Author: agent
Branch: `claude/organize-indicators-hierarchy-8JDw1`
Scope: priority detection plots Anish wants to verify in TradingView's Pine
editor TODAY.

## Existing loggers (DO NOT MODIFY per SD-002 / SD-004)

| File | Covers |
|---|---|
| `path-a-loggers/versions/LOGGER_B2B_PUP_v1.pine` | 37 B2B PUP S-plots + roots |
| `path-a-loggers/versions/LOGGER_HEAVY_COMBO_TOGGLES_v1.pine` | S1 Heavy Combo Bull / S2 Heavy Combo Bear / S3 Heavy Combo Neutral (master OR-gates only) |
| `path-a-loggers/versions/LOGGER_HVDPBJPPD_v1.pine` | Floor / 2F / Rooftop / Penthouse, Combo Bull/Bear (CS3), CC, LSC, UU family (UU/UUU/UUUU), A★ Bull/Bear, FOX |
| `path-a-loggers/versions/LOGGER_SQUARIFY_v1.pine` | Squarify 46 S-plots + T1/T2 OC |
| `path-a-loggers/versions/LOGGER_TNT_OD_v1.pine` | 48 TNT-OD composite plots |

## Coverage table (priority plot × logger)

Legend: ✅ covered • ➕ partial • ❌ gap • — N/A

| # | Priority plot | LOGGER_HVDPBJPPD | LOGGER_SQUARIFY | LOGGER_B2B_PUP | LOGGER_HEAVY_COMBO_TOGGLES | LOGGER_TNT_OD | Status |
|---|---|---|---|---|---|---|---|
| 1 | csNew3_Bull | ✅ "Combo Bull" L27 | ➕ S2/S3 inherited | — | — | — | COVERED |
| 1 | csNew3_Bear | ✅ "Combo Bear" L28 | ➕ inherited | — | — | — | COVERED |
| 2 | det_b2bPUP (root) | — | — | ✅ via "B2B Bull" | — | — | COVERED |
| 2 | det_b2bPPD (root) | — | — | ✅ via "B2B Bear" | — | — | COVERED |
| 3 | sigNagPlusBull | ✅ "NAG+ Bull" (HVDPBJPPD L1522) | ➕ via "35 NAG+" (`nag_any_bull`) | — | — | — | COVERED (but indirect on Squarify) |
| 3 | sigNagPlusBear | ❌ NOT plotted in HVDPBJPPD | ❌ NOT plotted (S35 is bull-only) | — | — | — | **GAP — needs new logger w/ manual wiring** |
| 4 | superBull | ✅ "S! Bull" L1451 | ✅ "2 SUPER" L2228 (`superBull and not sduperBull`) | — | — | — | COVERED (two emitters, definitions differ slightly) |
| 4 | superBear | ✅ "S! Bear" L1475 | ❌ no bear "SUPER" plot in Squarify | — | — | — | COVERED via HVDPBJPPD only |
| 4 | sduperBull | ✅ "SD! Bull" L1452 | ✅ "1 SD!" L2227 | — | — | — | COVERED |
| 4 | sduperBear | ✅ "SD! Bear" L1476 | ❌ no bear "SD!" plot | — | — | — | COVERED via HVDPBJPPD only |
| 5 | sigSuperBullPBJ (Ultra-Combo decomp) | — | — | — | — | — | ❌ NOT plotted ANYWHERE — only combined "Super" in Fauna-Shifu L1476 |
| 5 | sigSuperBullPB | — | — | — | — | — | ❌ same gap |
| 5 | sigSuperBearPBJ | — | — | — | — | — | ❌ same gap |
| 5 | sigSuperBearPB | — | — | — | — | — | ❌ same gap |
| 6 | sigAlphaStrikeBull | ✅ "A★ Bull" L1435 | ✅ "9 A★" L2235 (gated) | — | — | — | COVERED |
| 6 | sigAlphaStrikeBear | ✅ "A★ Bear" L1460 | ➕ "9 A★" gates bull only; bear path elsewhere | — | — | — | COVERED via HVDPBJPPD |
| 7 | anyBullFloor | ✅ "Floor" L1448 | ✅ "4 FLOOR" L2230 (gated `floor_sq`) | — | — | — | COVERED |
| 7 | anyBull2nd | ✅ "2F" L1449 | ✅ "5 2F" L2231 | — | — | — | COVERED |
| 7 | anyBearRoof | ✅ "Rooftop" L1472 | ❌ not in Squarify 46 | — | — | — | COVERED via HVDPBJPPD |
| 7 | anyBearPent | ✅ "Penthouse" L1473 | ❌ not in Squarify 46 | — | — | — | COVERED via HVDPBJPPD |
| 8 | NEUTRAL_HEAVY_X2 Bull/Bear/Neutral | — | — | — | ❌ LOGGER_HEAVY_COMBO_TOGGLES only logs the 3 MASTER gates; NHx2 is a *member* | — | **GAP — need Heavy-Pentagon-member logger** |
| 9 | sigUUBull / sigP21BullUUU / sigP21BullUUUU | ✅ "Bull UU/UUU/UUUU" L1432-4 | ✅ "6 UUUU" / "7 UUU" / "8 UU" L2232-4 | — | — | — | COVERED |
| 9 | sigUUBear / sigP21BearUUU / sigP21BearUUUU | ✅ "Bear UU/UUU/UUUU" L1457-9 | ➕ bear via Squarify if present | — | — | — | COVERED |

## Gap summary → new loggers to add

1. **`LOGGER_NAGASAKI_PLUS_v1.pine`** — covers `sigNagPlusBull` (via HVDPBJPPD
   "NAG+ Bull" plot) and exposes a placeholder source for `sigNagPlusBear`
   (currently unplotted; user can wire to whatever future bear plot emerges,
   or use a Squarify scratch plot once exposed).

2. **`LOGGER_SUPER_FAMILY_v1.pine`** — covers `superBull/Bear` and
   `sduperBull/Bear` from BOTH HVDPBJPPD ("S! Bull/Bear", "SD! Bull/Bear")
   AND Squarify ("1 SD!", "2 SUPER"), with distinguishable tags so we can
   cross-check that both indicators agree.

3. **`LOGGER_HEAVY_PENTAGON_v1.pine`** — covers ALL 15 individual Heavy-Pentagon
   members (HYY / HN / HNV / HT / NHx2) × {Bull, Bear, Neutral}. This is the
   only way to verify NEUTRAL_HEAVY_X2 in isolation (the existing Heavy Combo
   Toggles logger only catches the master OR-gate).

4. **`LOGGER_ULTRA_COMBO_SUPER_v1.pine`** — covers Ultra-Combo's
   `sigSuperBullPBJ/PB` and `sigSuperBearPBJ/PB` via the combined Fauna-Shifu
   "Super" plotshape, then decomposes by reading concurrent root PBJ/PB
   bull/bear plot sources. Known structural limitation: if no root variant
   plot fires concurrently, the logger emits "SUP+?" / "SUP-?" for manual
   triage.

## Loggers we did NOT create (because existing coverage suffices)

- ❌ `LOGGER_FAUNA_SHIFU_v1.pine` — Fauna-Shifu's decomposed signals
  (`sigSuperBullPBJ/PB`) overlap entirely with Ultra-Combo's; one
  cross-indicator logger (`LOGGER_ULTRA_COMBO_SUPER_v1.pine`) handles both.
- ❌ `LOGGER_ALPHA_STRIKE_v1.pine` — `sigAlphaStrikeBull/Bear` are already
  plotted as "A★ Bull"/"A★ Bear" in HVDPBJPPD and "9 A★" in Squarify, both
  covered by existing loggers (`LOGGER_HVDPBJPPD_v1`, `LOGGER_SQUARIFY_v1`).
- ❌ `LOGGER_ULTRA_COMBO_v1.pine` — the 35 Ultra-Combo plots (PBJ+F2, PBJ+E3,
  HW+Bull, etc.) are NOT on the priority list TODAY; Anish can ask for this
  in a follow-up if needed.

## Hand-off — TV Pine editor load order for TODAY

To verify ALL priority plots in one sitting, Anish loads on the active chart:

**Base indicators (existing, unmodified):**
- "B2B PUP Combined 5.4.439am"
- "Heavy Combo Toggles"
- "Heavy PENTAGON"
- "HV+D ↔ PBJ ↔ USE THIS IS THE ONLY FUCKING ONE" (HVDPBJPPD)
- "SQUARIFY 46 v2"
- "TNT Opening Drive OD v3"
- "ULTRA COMBO v57" (Pine 6)
- "FAUNA SHIFU JUMBO CIA 1ST PUP v1"

**Loggers (load AFTER base indicators so input.source() targets are
discoverable):**
- `path-a-loggers/versions/LOGGER_B2B_PUP_v1.pine`            (priorities 2)
- `path-a-loggers/versions/LOGGER_HEAVY_COMBO_TOGGLES_v1.pine`(priority 8 — master gates only)
- `path-a-loggers/versions/LOGGER_HEAVY_PENTAGON_v1.pine`     (priority 8 — NHx2 individual)  *NEW*
- `path-a-loggers/versions/LOGGER_HVDPBJPPD_v1.pine`          (priorities 1, 4, 6, 7, 9)
- `path-a-loggers/versions/LOGGER_SQUARIFY_v1.pine`           (priorities 1, 4, 6, 7 cross-check)
- `path-a-loggers/versions/LOGGER_NAGASAKI_PLUS_v1.pine`      (priority 3)  *NEW*
- `path-a-loggers/versions/LOGGER_SUPER_FAMILY_v1.pine`       (priority 4 cross-check)  *NEW*
- `path-a-loggers/versions/LOGGER_ULTRA_COMBO_SUPER_v1.pine`  (priority 5)  *NEW*

**Per-logger wiring quick-ref (most common gotcha):**

- LOGGER_NAGASAKI_PLUS — wire `NAG+ Bull` to HVDPBJPPD plot "NAG+ Bull"; leave
  `NAG+ Bear` at `close` until a bear plot is exposed somewhere.
- LOGGER_HEAVY_PENTAGON — wire 15 inputs to the 15 plots in Heavy-PENTAGON
  L381–403 (titles match 1:1).
- LOGGER_SUPER_FAMILY — wire 4 HVD inputs to "S! Bull/Bear" + "SD! Bull/Bear"
  in HVDPBJPPD; wire 2 SQ inputs to "1 SD!" + "2 SUPER" in Squarify 46.
- LOGGER_ULTRA_COMBO_SUPER — wire `Super (Fauna-Shifu combined plot)` to the
  Fauna-Shifu "Super" plotshape (L1476); wire 4 root inputs to your preferred
  PBJ/PB Bull/Bear source plots.

After loading, scrape with:

```
mcp__tradingview__data_get_pine_labels(study_filter="LOGGER ...")
```

substituting each logger's display title (e.g. `"LOGGER Nagasaki Plus"`,
`"LOGGER Heavy Pentagon Members"`, `"LOGGER SUPER Family"`,
`"LOGGER Ultra-Combo SUPER Decomp"`).

## Compliance

- SD-002: zero modifications to the 5 existing loggers. New files only.
- SD-004: zero deletions. The 4 new logger files are additive.
