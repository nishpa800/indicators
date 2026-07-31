# INDICATOR STUDY AUDIT — BASE HV+D ↔ PBJ v1 (Bull 38 / Bear 36)

**Date:** 2026-07-04
**Scope:** RE10023 tick-safety + offset correctness (esp. Unified Combo) for the
HV+D ↔ PBJ ↔ PPD bull/bear split pair.
**Verdict:** ✅ The canonical tick-friendly files are correct and paste-ready. The
snapshot that threw RE10023 is an **obsolete pre-fix copy** missing *two* fixes — no
new conversion is required, only load the current tick-friendly file.

**Deliverable (load these):**
- `hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BULLISH_v1_tick_friendly.pine`  → `HVD PBJ BULL TF`
- `hvd-pbj-ppd/tick_friendly/HVD_PBJ_PPD_BEARISH_v1_tick_friendly.pine`  → `HVD PBJ BEAR TF`

---

## 1. The crash

```
RE10023 — Error on bar 0: Cannot call the `timeframe.change` function with a
tick-based 'timeframe' argument.   at tv_ta.relativeVolume():346   at #main():270
```

`TradingView/ta/7 relativeVolume()` runs `timeframe.change(anchor)` internally. The
study passes a blank anchor `reg_anchorTimeframe = ""`, which resolves to the **chart**
timeframe. On a tick chart (e.g. `1000T`) that anchor is tick-based → `timeframe.change`
throws on `bar[0]`. `#main():270` is the first of the three `relativeVolume()` call sites.

## 2. The snapshot that crashed is obsolete — it carries TWO defects

The pasted source is the bull split at its **initial** commit (`4b81122`), *before* two
subsequent fixes. Both defects are already retired on the current tree:

| # | Defect in the pasted snapshot | Status on current tree |
|---|---|---|
| D1 | 3× `relativeVolume(reg_length, reg_anchorTimeframe, …)` with raw `""` → **RE10023** on tick | Fixed in `tick_friendly/` via `reg_anchorSafe` |
| D2 | Combo-Chain loop uses cross-bar `comboSet1_Bull[i-1]` → a single bar carrying Matrix+FVG self-counts to 2 and fires a chain off one candle (binary-law violation; see `hvd-pbj-ppd/CHANGELOG.md`) | Fixed in **both** `versions/` and `tick_friendly/` via same-offset OR-collapse |

> **Do not re-tick-friendly the pasted text.** It would re-import D2. The current
> `tick_friendly/` file already contains D2's fix **plus** the RE10023 fix.

## 3. The fix (already present in `tick_friendly/`)

Engine is **byte-identical** to `versions/` except three guard blocks:

**(a) RE10023 anchor gate** — force a time-based `"D"` anchor **only on tick charts**;
time charts keep `""` → bit-for-bit RVOL parity preserved (this is the postmortem-verified
form; detect tick by the **chart period**, never the anchor var):

```pine
string reg_anchorSafe = ((reg_anchorTimeframe == "" and (str.endswith(timeframe.period, "T")
     or na(timeframe.in_seconds(timeframe.period)) or timeframe.in_seconds(timeframe.period) <= 0))
     or str.endswith(reg_anchorTimeframe, "T")) ? "D" : reg_anchorTimeframe
```
…applied at all **3** call sites (reg / regular / cumulative).

**(b) `tfSec` fallback** — `timeframe.in_seconds()` can go na/≤0 on tick; the per-TF
threshold tables (`f_*_threshold(tfSec)`) would silently go na and stop firing:

```pine
int _tfSecRaw = timeframe.in_seconds(timeframe.period)
int tfSec = (na(_tfSecRaw) or _tfSecRaw <= 0) ? 10 : _tfSecRaw   // 10s = tightest sub-minute tier
```

**(c) Combo-Chain binary law** — `hv2 = matrix[i] OR fvg[i]` at the **same** offset (no
`[i-1]` cross-bar shift). One physical bar = 1 or 0; a 2-hit chain requires two bars.

## 4. Offset audit — the main ask

### 4a. Convention (two families)
Every detection fires on the confirmed `bar[0]` (`barstate.isconfirmed`). The plot offset
places the marker on the candle the detection is *about*:

- **`offset=-1` family** — detections whose defining content lives on `bar[1]` (the prior
  candle): the HV+D / displacement lineage, the streak (UU/UUU/UUUU) family, the co-occurrence
  and combo family (CS1, **Unified Combo**, CC, B2B, HV+D momentum). The marker back-shifts one
  bar to sit on the originating candle.
- **`offset=0` family** — detections that complete purely on `bar[0]`: FOX (4 consecutive
  incl. `bar[0]`), Omega, PAF, **CS2 MAT**, LSC, Floor, 2F, HW, NAG+.

### 4b. Faithfulness — 38/38 match the canonical combined source
Extracted every plotshape offset from the canonical combined study
(`versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine`) and diffed against the bull
split and the tick-friendly file. **All 38 offsets match exactly.** The split and the
tick-friendly conversion introduced **zero** offset drift. Bear side likewise (36/36).

### 4c. Unified Combo (CS3B) — deep-dive proof that `offset=-1` is correct
```pine
csNew1_Bull = comboSet1_Bull or comboSet2_Bull          // FVG combo  (content on bar[1])
csNew2_Bull = comboSet3_Bull or comboSet4_Bull          // Matrix combo (content on bar[0])
csNew3_Bull = csNew1_Bull and nz(csNew2_Bull[1])        // Unified: FVG on bar[0] AFTER Matrix on bar[1]
plotshape(fire_CS3B, "Combo Bull", …, offset=-1)
```
Trace one firing (Matrix combo on the earlier candle `E`, FVG combo on the next candle `F`):

| Marker | Fires on | Own offset | Lands on |
|---|---|---|---|
| CS2 MAT (`csNew2`) | `E` | `0` | **`E`** |
| CS1 FVG (`csNew1`) — its momentum (`cs_vb`, `sig*[1]`) is on `E` | `F` | `-1` | **`E`** |
| **Unified Combo (`csNew3`)** | `F` | `-1` | **`E`** |

`csNew1` is built from `bar[1]` body/momentum (`cs_vb`, `sigSAAB[1]`, …) gated by a `bar[0]`
FVG, so its own marker already back-shifts to `E`. `csNew2` fired one bar earlier on `E`.
`offset=-1` therefore **co-locates** the COMBO marker with *both* of its constituents (CS1
FVG + CS2 MAT) on the shared originating candle `E`. Any other offset would split the trio.
**Correct — and consistent with CS1 (`-1`) / CS2 (`0`).**

No repaint: `csNew3` is `conf`-gated end-to-end (via `comboSet*`), drawn on a closed bar; the
`alert()` fires at bar-close of `F`. Standard suite behavior (plot back-dated to the
originating candle; alert at confirmation).

## 5. Verification gates (all PASS)

| Gate | Bull TF | Bear TF |
|---|---|---|
| `//@version=5` (Pine v5 only) | ✓ | ✓ |
| Engine == `versions/` except guard blocks (`diff`) | ✓ | ✓ |
| RE10023 literal-blank-anchor gate `grep -nE 'relativeVolume\([^,]+,\s*""'` → empty | ✓ CLEAN | ✓ CLEAN |
| 3/3 `relativeVolume` call sites via `reg_anchorSafe` | ✓ | ✓ |
| `tfSec` na/≤0 → 10 fallback present | ✓ | ✓ |
| Combo-Chain binary law (no `[i-1]`) | ✓ | ✓ |
| `check_no_fixed_windows.sh` (constitutional) | ✓ PASS | ✓ PASS |
| Plotshapes (all real, 0 labels) | 38 | 36 |
| Offsets match canonical combined source | 38/38 | 36/36 |

## 6. Not live-compiled
No TradingView compile was run (headless environment; Anish's 1000T chart is an immutable
curated stack). All checks above are static. The RE10023 fix is the exact
postmortem-verified form proven live on `1000T` AMEX:BRF (`anchor "D"` → relVol 4.11 clean).
