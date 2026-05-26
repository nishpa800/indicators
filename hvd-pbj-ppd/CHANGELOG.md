# HVD-PBJ-PPD — Changelog

Newest first. Each version = one file in `versions/`.

---

## v1.1 — 2026-05-26 — Combo Chain Off-by-One Fix
**File:** `versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine`
**Lines modified:** 1011–1046

### Problem observed

Combo chain does not fire when two unified combos (csNew3) are visible on the chart within 3–4 bars, even with settings `cc_min_hits=2`, `cc_window=5`.

### Root cause

The combo chain counting algorithm in HVD-PBJ-PPD diverged from the SQUARIFY reference implementation. The HVD-PBJ-PPD version attempted to align FVG combo events to their visual bars by shifting array lookups, but introduced a systematic off-by-one that shrank the effective FVG-combo scanning window by 1 bar.

### What was there BEFORE (broken — lines 1011–1046)

```pine
// Combo Chain
int cc_win_bull=0
bool cc_pbj_bull=false
for i=0 to cc_window-1
    bool hv2=nz(comboSet3_Bull[i]) or nz(comboSet4_Bull[i])
    if i>=1
        if nz(comboSet1_Bull[i-1]) or nz(comboSet2_Bull[i-1])
            hv2:=true
    if hv2
        cc_win_bull+=1
    if nz(sigBullPBJ[i]) or nz(sigBullPB[i])
        cc_pbj_bull:=true
int cc_win_bear=0
bool cc_pbj_bear=false
for i=0 to cc_window-1
    bool hv2=nz(comboSet3_Bear[i]) or nz(comboSet4_Bear[i])
    if i>=1
        if nz(comboSet1_Bear[i-1]) or nz(comboSet2_Bear[i-1])
            hv2:=true
    if hv2
        cc_win_bear+=1
    if nz(sigBearPBJ[i]) or nz(sigBearPB[i])
        cc_pbj_bear:=true

var bool cc_bull_active=false, var bool cc_bear_active=false
if conf
    if not (comboSet1_Bull or comboSet2_Bull or comboSet3_Bull or comboSet4_Bull)
        cc_bull_active:=false
    else if not cc_bull_active and cc_win_bull>=cc_min_hits and cc_pbj_bull
        cc_bull_active:=true
if conf
    if not (comboSet1_Bear or comboSet2_Bear or comboSet3_Bear or comboSet4_Bear)
        cc_bear_active:=false
    else if not cc_bear_active and cc_win_bear>=cc_min_hits and cc_pbj_bear
        cc_bear_active:=true
```

### Three specific defects in the old code

**Defect 1: `if i>=1` guard skips FVG combos at i=0.**
At iteration i=0 (current bar), only matrix combos (`comboSet3/4`) are checked. FVG combos (`comboSet1/2`) on the current computational bar are skipped entirely. They are not counted until i=1 via `comboSet1/2[i-1]`. This shifts the effective start of the FVG scanning window forward by 1 bar.

**Defect 2: Oldest FVG event falls outside the loop.**
At the last iteration (i=cc_window-1), the code checks `comboSet1/2[cc_window-2]`. The FVG event at computational position cc_window-1 is never reached — it would require `comboSet1/2[cc_window-1]` checked at i=cc_window, which is outside the loop boundary. Net effect: FVG combo events have an effective window of `cc_window - 1` bars instead of `cc_window` bars.

**Defect 3: No csNew3 overlap subtraction.**
When a unified combo fires (csNew3 = csNew1 AND csNew2[1]), both the FVG component (csNew1) and the matrix component (csNew2) are counted in the window. SQUARIFY subtracts 1 for each csNew3 to avoid double-counting adjacent FVG+matrix as two separate events. HVD-PBJ-PPD had no subtraction loop. While the alignment trick partially compensated (both components could land in the same iteration), it relied on the alignment being correct — which it wasn't due to defects 1 and 2.

### Proof: concrete scenario where the bug causes a miss

Two FVG combos (csNew1) at computational bars V+1 and V-3 (4 bars apart). Settings: cc_min_hits=2, cc_window=5.

**SQUARIFY (reference):** i=0 captures csNew1[0] (bar V+1). i=4 captures csNew1[4] (bar V-3). Count=2. Fires.

**HVD-PBJ-PPD (broken):** i=0 skips FVG (i>=1 guard). i=1 captures comboSet1/2[0] (bar V+1). i=4 checks comboSet1/2[3] which is bar V-2, NOT bar V-3. The event at V-3 needs comboSet1/2[4] at i=5, but loop stops at i=4. Count=1. Does not fire.

### What it looks like NOW (fixed — lines 1011–1046)

```pine
// Combo Chain — aligned with SQUARIFY reference (fixes off-by-one on FVG combo events)
int cc_win_bull=0, bool cc_pbj_bull=false
for i=0 to cc_window-1
    if nz(csNew1_Bull[i]) or nz(csNew2_Bull[i])
        cc_win_bull+=1
    if nz(sigBullPBJ[i]) or nz(sigBullPB[i])
        cc_pbj_bull:=true
for i=0 to math.max(cc_window-2, 0)
    if i+1 <= cc_window-1 and nz(csNew3_Bull[i])
        cc_win_bull-=1
int cc_win_bear=0, bool cc_pbj_bear=false
for i=0 to cc_window-1
    if nz(csNew1_Bear[i]) or nz(csNew2_Bear[i])
        cc_win_bear+=1
    if nz(sigBearPBJ[i]) or nz(sigBearPB[i])
        cc_pbj_bear:=true
for i=0 to math.max(cc_window-2, 0)
    if i+1 <= cc_window-1 and nz(csNew3_Bear[i])
        cc_win_bear-=1

var bool cc_bull_active=false, var bool cc_bear_active=false
if conf
    if not (csNew1_Bull or csNew2_Bull)
        cc_bull_active:=false
    else if not cc_bull_active and cc_win_bull>=cc_min_hits and cc_pbj_bull
        cc_bull_active:=true
if conf
    if not (csNew1_Bear or csNew2_Bear)
        cc_bear_active:=false
    else if not cc_bear_active and cc_win_bear>=cc_min_hits and cc_pbj_bear
        cc_bear_active:=true
```

### What changed and why — line by line

| Old | New | Why |
|---|---|---|
| `bool hv2=nz(comboSet3_Bull[i]) or nz(comboSet4_Bull[i])` + shifted FVG lookup | `if nz(csNew1_Bull[i]) or nz(csNew2_Bull[i])` | Counts unified combo sets (csNew1 = FVG combo, csNew2 = Matrix combo) directly at their computational positions. Eliminates the shifted lookup that caused the off-by-one. Matches SQUARIFY reference exactly. |
| `if i>=1` guard on FVG lookup | Removed | FVG combos are now counted at i=0 like matrix combos. No special casing. |
| No overlap subtraction | `for i=0 to math.max(cc_window-2, 0)` loop subtracting csNew3 | When csNew3 fires (= csNew1 + csNew2 on adjacent bars), both components were already counted. Subtracting 1 prevents double-counting the same visual event. Matches SQUARIFY reference. |
| `if not (comboSet1_Bull or comboSet2_Bull or comboSet3_Bull or comboSet4_Bull)` | `if not (csNew1_Bull or csNew2_Bull)` | Functionally identical (csNew1 = comboSet1 OR comboSet2; csNew2 = comboSet3 OR comboSet4). Using csNew1/csNew2 is cleaner and matches the reference. |

### What was NOT changed

- **comboSet1–4 definitions** (lines 954–964): identical to SQUARIFY, untouched.
- **csNew1, csNew2, csNew3 definitions** (lines 966–968): identical to SQUARIFY, untouched.
- **cc_has_fvg_bull/bear** (line 1047): HVD-PBJ-PPD-specific output, preserved.
- **sigCCBull/sigCCBear** (line 1046): same structure, untouched.
- **All other pipelines** (HV+D, PBJ, USE, Floor/2F/Roof/Pent, etc.): untouched.

### Cross-file consistency check

| Component | SQUARIFY v2 | HVD-PBJ-PPD (after fix) | B2B PUP v4.32 | Match? |
|---|---|---|---|---|
| comboSet1_Bull | `conf and cs_vb and (gz_bullHV or gz_bullGZI) and (sigSAAB[1] or sigBullRVOL1x[1] or sigGrandSlam[1])` | Identical | Identical | YES |
| comboSet2_Bull | `conf and cs_vb and (gz_bullHV or gz_bullGZI) and ((cs_inc_pentagon_FVG and sigPentagon[1]) or sigWTC[1] or sigHiroshima[1] or sigNagasaki[1])` | Identical | Identical | YES |
| comboSet3_Bull | `cs_vm and matrix_any_bull and (sigSAAB or sigBullRVOL1x or sigGrandSlam)` | Identical | Identical | YES |
| comboSet4_Bull | `cs_vm and matrix_any_bull and ((cs_inc_pentagon_MAT and sigPentagon) or sigWTC or sigHiroshima or sigNagasaki)` | Identical | Identical | YES |
| csNew1 | `comboSet1_Bull or comboSet2_Bull` | Identical | Identical | YES |
| csNew2 | `comboSet3_Bull or comboSet4_Bull` | Identical | Identical | YES |
| csNew3 | `csNew1_Bull and nz(csNew2_Bull[1])` | Identical | Identical | YES |
| Combo chain counting | csNew1/csNew2 direct + csNew3 subtraction | **NOW matches** | N/A (no combo chain) | YES |

### Verification steps

1. Paste the fixed source into TradingView on the same chart as SQUARIFY v2.
2. Set both to `cc_min_hits=2`, `cc_window=5`.
3. Combo chain markers should fire on the same bars in both indicators.
4. Edge case: two FVG-only combos (csNew1) separated by exactly `cc_window - 1` bars — should now fire (previously missed due to the off-by-one).

---

## v1 — 2026-05-05 (initial commit)
**File:** `versions/HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine`

Initial cleanup pass from TradingView source (entity 8A6Sm9).

**Removed:** Dashboard, Acceleration Periods, Tables, signal-bar tracking.
**Kept untouched:** FVG, HV, GZI, mitigations, all 4 pipelines (HV+D, PBJ, USE, Triple Co-occurrence).
