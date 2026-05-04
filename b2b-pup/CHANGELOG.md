# B2B PUP — Changelog

Newest first. Each version = one file in `versions/`.

---

## v4.31 — 2026-05-04 (current)
**File:** `versions/B2B_PUP_v4.31.pine` (1247 lines)
**Compiled clean in TradingView:** yes (v4.30 compiled, v4.31 follow-up was UI/naming-only — same compile path).

**Changes from v4.30:**
- **S9 source dropdown removed.** S9 now fires when EITHER `S19` (Unified Combo ×2) OR `S20` (FVG/MAT/Uni Combo ×2) lands alongside B2B PUP. Was: `input.string` dropdown forcing the user to pick one path.
- **Plot A / Plot B renamed → S19 / S20** to fit the numbered-signal scheme. Letter abbreviations confused across the 6-indicator suite.
  - `S19: Unified Combo ×2` (standalone — back-to-back Unified Combo only)
  - `S20: FVG/MAT/Uni Combo ×2` (standalone — any combo type counts)
- **Sudden Change Max Bars default:** 10 → **3**.

---

## v4.30 — 2026-05-04 (compiled, then superseded by v4.31 same session)
**File:** not preserved as separate file; v4.31 is a UI/naming refinement on top.
**Compiled clean in TradingView:** yes — Anish confirmed.

**Changes from v4.29 (the big rewrite):**
1. **Napalm now scans ALL active opposing TNT zones** (was: last bear-TNT level only).
   New input `Max TNT Zones` (default 30, range 1-200) controls how many active zones are kept tracked. Higher = more historical zones considered.
2. **Cont engine matched to TNT OD definition.** v4.29's CONT had only 2 of TNT OD's 3 trigger paths — the Return-to-TNT leg and TNT 2.0 leg were missing. v4.30 ports the full architecture:
   - Added `Zone` type + active zone arrays (bull + bear)
   - Added `ChargeLvl` type + array (replaces single-variable charge tracking)
   - Added `BBEvent` type + event log → 2+ events trigger TNT 2.0 (super) detection
   - Added Return-to-TNT detection (with `tnt_RET_PCT` input, default 100%)
   - Cont now uses the 3-clause OR logic from TNT OD verbatim
   - Super-TNT path (`raw_bullTNT AND raw_bearCharge`) added to consolidated TNT
3. **FAUNA family checkboxes deleted from UI** (MB/RE/GG/TA/TR/ES/GDR). All 7 hardcoded ON. Behavior unchanged from prior all-on default — just removes UI clutter.
4. **Combo Chain (CC) engine ripped out** and replaced with two new standalone plots (Plot A / Plot B in v4.30; renamed to S19 / S20 in v4.31).
5. **S9 rewired** from CC + B2B PUP → "Uni Combo + B2B PUP" using the new plots.
6. **Offset bugs fixed.** S6, S9, S11, S16 plotshapes had no offset but tooltips said `Offset=-1` — fixed all 4. S17 and S18 anchored to bar[0] but underlying B2B HV+D event finishes on bar[1] — both moved to `offset=-1`.

**Definition discrepancies that motivated this rewrite (audit done 2026-05-04):**
- B2B PUP v4.29's Napalm: only checked `tnt_lastBearLvl` (single var). Misses fires when older active zones are still in play.
- B2B PUP v4.29's CONT: missing Return-leg + TNT 2.0-leg. Strict subset of TNT OD's CONT.
- TNT raw definition: matched ✓
- Pentagon definition: matched ✓
- FVG/Matrix/Unified combo definitions: matched ✓
- TNT OD is the canonical reference for Napalm/TNT/CONT; B2B PUP must mirror it.

---

## v4.29 — pre-2026-05-04 (baseline pasted by Anish at session start)
**Source:** Pasted inline in chat; not preserved as a file in this repo.

**State at v4.29:**
- 17 detection plots (S1-S6, S8-S18; S7 missing in original).
- "Combo Chain" (CC) was the back-to-back combo detector — confusingly named, bundled 3 cases into 1 plot, gated on PBJ.
- FAUNA had 7 family checkboxes in UI.
- TNT engine used minimal level tracking — single-var `tnt_lastBullLvl` / `tnt_lastBearLvl` for Napalm.
- CONT had 2 of 3 trigger paths (missing Return-leg + TNT 2.0-leg).
- Multiple plotshape offset/tooltip mismatches (S6, S9, S11, S16, S17, S18).

---

## How to read this changelog
- **Plain English recall:** "Hey, did we change Napalm in B2B PUP?" → grep this file for "Napalm" and read the matching version's notes.
- **Diff between versions:** `diff versions/B2B_PUP_vA.pine versions/B2B_PUP_vB.pine`
- **Roll back:** `pbcopy < versions/B2B_PUP_vX.pine` then paste into Pine Editor.
