# Heavy Weapons ULTRA — VARIANTS (read this to tell the two builds apart)

There are **two intentionally-separate ULTRA builds**. They are NOT merged. Pick by chart type.

| | **TIME build** | **TICK build** |
|--|--|--|
| File | `versions/HEAVY_WEAPONS_ULTRA_v1.pine` | `tick_friendly/HEAVY_WEAPONS_ULTRA_tickfriendly_b2b1.pine` |
| `shorttitle` | `HW ULTRA` | `HW ULTRA b2b1` |
| Use on | time charts (1m, 5m, 1h, …) | tick charts (e.g. 1000T) **and** time charts |
| Tick-safe | ❌ crashes on tick (`relativeVolume(.., "")` → RE10023) | ✅ `reg_anchorSafe` coerces blank/tick anchor → `"D"` on tick only; `chartSec` tick fallback |
| Long/Short floors | **Hiroshima-derived** (`hybAutoReg1 = th_hiroshima×2.85`, ~100 Reg @1m) | **hard-coded** `hyb_addReg1 = 5.0` / Cum `3.0` / Body `0.65` (per tier) |
| → effect | Long/Short fire **rarely** (high bar) | Long/Short fire **far more often** (low bar) |
| Alert | **queryable per-atom** records (`f_q`, `HWULTRA\|...`) — see `ATOM_REGISTRY.md` | old **OR-collapsed** tier text (`{{ticker}} {{interval}} — …`) |
| FAUNA (F1–F14) | **emitted** (queryable) | computed internally, **never emitted** |

## What is IDENTICAL between the two
Every other atomic gate formula is the same. The shared gate definitions live in:
- `GATES_REFERENCE.md` — every spot + alert gate, fully expanded
- `ATOM_REGISTRY.md` — the atom catalog + queryable wire format (time build)

Identical engines: **R** (RVOL 0.56: SAAB/Kratos/Bull1x/Bear1x/GrandSlam/MOAB), **T** (Reg@Time:
Pentagon/WTC/Hiroshima), **N** (Nagasaki), **Q** (sequences UU…DDDD), **B** (back-to-back 2x/Mid),
**D** (displacement + consecutive), **V** (HV rank tiers 75–1000), **P** (PBJ bull/bear), **H** (HV+D
bull/bear), **K** (HVD+PBJ), **G** (GZI/HV-FVG), **C** (CS1/CS2/CS1+CS2), **U** (PUP). Same thresholds
(`th_1x`, `th_saab_kratos`=0.56×, `th_gs_moab`=`th_hiroshima`, `th_wtc`=2×).

## The ONLY material differences (4)
1. **Tick safety** — tick build has the RE10023 guard + `chartSec` fallback; time build does not.
2. **Hybrid Long/Short floors** — Hiroshima-derived (time) vs hard-coded 5.0/3.0/0.65 (tick). This
   changes *how often* LONG/SHORT 1–5 fire, nothing else.
3. **Alert layer** — queryable per-atom (time) vs OR-collapsed tier text (tick).
4. **FAUNA** — emitted/queryable (time) vs computed-only (tick).

## Decision (do not auto-merge)
User has chosen to **keep both separate**. If you ever want them reconciled, that is a new explicit task.

## Quick identify (grep)
```
grep -l reg_anchorSafe  → the TICK build
grep -l hybAutoReg1     → the TIME build (Hiroshima floors)
grep -l 'f_q('          → the TIME build (queryable alert)
grep -l hyb_addReg1     → the TICK build (hard-coded floors)
```
