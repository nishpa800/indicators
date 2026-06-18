# ULTRA COMBO v57 — Changelog

Newest first.

---

## v57 tick-friendly — 2026-06-12 (permanent home established)
**File:** `tick_friendly/ULTRA_COMBO_v57_tick_friendly.pine`
**Trigger:** RE10023 (`Cannot call timeframe.change with a tick-based 'timeframe'`) on
**bar 0** of a tick chart. Error trace `tv_ta.relativeVolume():346 → #main():366` resolved
to the **raw verbatim import**
`imports/20260531T103840_indicator_studies/pine_v5/ultra_combo_v57_shorttitle_ultra_v57.pine:366`
— `tv_ta.relativeVolume(30, "", false, true)` (literal blank = chart-TF anchor). The import
is a pre-conversion original and was never a tick-safe build.

**Root cause of the mis-load:** every other study in the suite (b2b-pup, tnt-od, squarify,
vob, hvd-pbj-ppd, heavy-weapons-nra) has a permanent, discoverable `<study>/tick_friendly/`
home. ULTRA 57 was the only study never promoted out of the `june7-conversion/` batch
staging folder, so the only ULTRA 57 in a normal study location was the raw import.

**Change:** promoted the verified tick-safe build from
`june7-conversion/tick_friendly_pine/ultra_57_tickfriendly.pine` (byte-identical) into this
permanent home. The RVOL engine routes through `u_regAnchorSafe`:

```pine
bool   u_isTickChart   = str.endswith(timeframe.period, "T") or na(timeframe.in_seconds(timeframe.period)) or timeframe.in_seconds(timeframe.period) <= 0
string u_regAnchorSafe = u_isTickChart ? "D" : ""          // "" on time charts (parity), "D" on tick
[currentVolume_reg, pastVolume_reg, _] = tv_ta.relativeVolume(30, u_regAnchorSafe, false, true)
```

Tick detection keys off `str.endswith(timeframe.period, "T")` — the authoritative tick
signal per the postmortem (`timeframe.in_seconds("1000T")` returns a positive number, so
the na/<=0 branch alone never fires). `tfSec` for the per-TF RVOL threshold table is guarded
with the same tick fallback so thresholds do not silently die on tick charts.

**Verification:**
- Strict call-site gate (comments excluded) returns nothing:
  `grep -nE 'relativeVolume\([^,]+,\s*""' <file> | grep -vE '^\s*[0-9]+://'` → empty.
- Time charts unchanged → parity preserved; only tick charts coerce the anchor to `"D"`.
- Drop-in superset of the import: `//@version=5`, 72 plot objects (35 original visuals +
  appended numeric data-window matrix), clean ending, no `label.new`.

**Load this file on tick charts — NOT the raw import.**
