# Canonical — Unified Combo (PO::unified-combo)

_Owned by `PO::unified-combo`. Authored 2026-05-11. Source enumeration:
`bible-input/agent-reports/uc-fvg-matrix-combo-enumeration.md`._

## What Unified Combo IS

A composite that fires when Matrix Combo (`csNew1_Bull/Bear`) AND FVG Combo
(`csNew2_Bull/Bear`) are both true on the same bar (or with FVG lagged by
one bar — semantic-group decision pending).

Identifier in Pine source: `csNew3_Bull`, `csNew3_Bear` (also `uc_bull` /
`uc_bear` in TNT-OD, but TNT's UC is a different count-style confluence
and is documented separately as `tnt_od::TNT_CONFLUENCE_BULL/BEAR`).

## Canonical decisions applied

| SD | Decision | Effect on canonical UC |
|---|---|---|
| SD-001 | Always include Pentagon | `cs_inc_pentagon_FVG` and `cs_inc_pentagon_MAT` IPSF flags are REMOVED in the canonical Python port. Pentagon is an unconditional operand of comboSet4 (FVG side) and comboSet2 (Matrix side). |
| SD-002 | Never modify, always new-version | The canonical Python port lives at `python_ports/squarify/unified_combo_canonical_pentagon_included.py` (and per-family equivalents). Source .pine files are NOT touched. |
| SD-003 | IPSF defaults are not drift | Body-percent defaults, lookback defaults, RVOL thresholds — all stay as `DEFAULTS = {...}` per-port. Anish tunes at TV runtime. |

## Open semantic-group question (NOT decided today)

`csNew3_Bull` operand 2 is `csNew2_Bull` in 1 file (THE_ONLY_ONE) and
`nz(csNew2_Bull[1])` in 9 files. Same-bar-AND vs lagged-AND.

| Group | Operands | Files |
|---|---|---|
| A — LAGGED | `csNew1_Bull AND nz(csNew2_Bull[1])` | 9 .pine files (majority) |
| B — SAME-BAR | `csNew1_Bull AND csNew2_Bull` | THE_ONLY_ONE.pine only |
| C — TNT counting | ≥2 of confluence streams | TNT_OD_v3.pine (`uc_bull`/`uc_bear`) — semantically a different signal |

PO::unified-combo arbitrates after TV firing reveals which fires more
predictively. Until then, BOTH variants are emitted as separate Python
ports:
- `unified_combo_canonical_lagged_pentagon_included.py` (matches Group A,
  preserves SD-001)
- `unified_combo_canonical_same_bar_pentagon_included.py` (matches Group B,
  preserves SD-001)

The TNT confluence variant is its own thing and doesn't belong under
PO::unified-combo's canonical — it goes to PO::tnt-confluence (deferred).

## Canonical Python (Group A — LAGGED, with SD-001 applied)

```python
# python_ports/squarify/unified_combo_canonical_lagged_pentagon_included.py
"""
Unified Combo BULL/BEAR canonical port, Group A (LAGGED), with SD-001
(Pentagon always included).

Source Pine: 9 .pine files (squarify 46_v2 + variants, hvd-pbj-ppd 4.26 +
1939 masterdir + 2246 masterdir, b2b-pup combined v4.32, ultra-combo v57).

Standing decisions applied:
- SD-001: Pentagon included unconditionally (cs_inc_pentagon flags removed)
- SD-002: This file is NEW; siblings preserved
- SD-003: IPSF defaults from squarify 46_v2 mirrored in DEFAULTS dict
"""

DEFAULTS = {
    # comboSet1 (Matrix lower) — IPSF, mirror of squarify 46_v2 defaults
    "matrix_lookback": 67,        # input.int from Pine
    "rvol_1x_mult": 1.0,          # input.float
    # comboSet3 (FVG lower) — IPSF
    "disp_sigma_mult": 6.0,       # input.float
    "fauna_lookback": 20,         # input.int
    # ... (full IPSF table mirrored from each Pine source)
}

def comboset1_bull(df, params):
    """Matrix Combo lower: PBJ + RVOL1x + (FAUNA or DISP)."""
    return (
        df["sig_bull_pbj"] & df["sig_bull_rvol_1x"]
        & (df["sig_fauna_bull"] | df["sig_disp_bull"])
    )

def comboset2_bull(df, params):
    """Matrix Combo upper: comboSet1 AND Pentagon (SD-001: Pentagon always in)."""
    return comboset1_bull(df, params) & df["sig_pentagon"]

def csnew1_bull(df, params):
    """Matrix Combo: comboSet1 OR comboSet2."""
    return comboset1_bull(df, params) | comboset2_bull(df, params)

def comboset3_bull(df, params):
    """FVG Combo lower: PBJ + DISP + FAUNA + (RVOL1x or GS or WTC or Hiroshima or Nagasaki)."""
    return (
        df["sig_bull_pbj"] & df["sig_disp_bull"] & df["sig_fauna_bull"]
        & (
            df["sig_bull_rvol_1x"] | df["sig_grand_slam"] | df["sig_wtc"]
            | df["sig_hiroshima"] | df["sig_nagasaki"]
        )
    )

def comboset4_bull(df, params):
    """FVG Combo upper: comboSet3 AND Pentagon[1] (SD-001: Pentagon always in,
    [1] lag preserved)."""
    return comboset3_bull(df, params) & df["sig_pentagon"].shift(1)

def csnew2_bull(df, params):
    """FVG Combo: comboSet3 OR comboSet4."""
    return comboset3_bull(df, params) | comboset4_bull(df, params)

def csnew3_bull(df, params):
    """Unified Combo (Group A, LAGGED): csNew1 AND nz(csNew2[1])."""
    return csnew1_bull(df, params) & csnew2_bull(df, params).shift(1).fillna(False)

# Bear mirrors omitted for brevity; structurally identical with bear operands.

DETECTIONS = {
    "comboset1_bull": comboset1_bull,
    "comboset2_bull": comboset2_bull,
    "csnew1_bull": csnew1_bull,
    "comboset3_bull": comboset3_bull,
    "comboset4_bull": comboset4_bull,
    "csnew2_bull": csnew2_bull,
    "csnew3_bull": csnew3_bull,
    # ... bear mirrors ...
}
STATE_MACHINES = {}
STUBBED = {}
```

(The same-bar variant is structurally identical except `csnew3_bull` drops
the `.shift(1)`. Both files coexist; `LATEST.txt` selects the active one
per family after PO::unified-combo arbitrates.)

## Per-file recognized variances

| File | Variance from canonical | Variant Python port |
|---|---|---|
| HVDPBJPPD THE_ONLY_ONE | csNew3 same-bar AND | `unified_combo_canonical_same_bar_pentagon_included.py` |
| HVDPBJPPD 4.26 / 1939 / 2246 | csNew3 lagged AND (matches canonical Group A) | (canonical, no variant needed) |
| Squarify 46_v2 + variants | csNew3 lagged AND (matches canonical Group A) | (canonical) |
| TNT_OD_v3 | uc_bull is count-style ≥2 confluence; not csNew3 | `python_ports/tnt_od/uc_tnt_confluence.py` (separate concept) |
| Heavy Weapons NO_PENTAGON | Pentagon explicitly excluded | `python_ports/heavy_weapons/unified_combo_no_pentagon.py` (NOT canonical) |

## Bull-vs-Hell debate hooks

PO::unified-combo runs the Heaven-vs-Hell debate (per `.claude/skills/bull-vs-bear-debate/`)
on every csNew3 fire. Inputs:

- Bar context (preceding 5 bars + concurrent plot fires)
- Which sub-operands actually fired (PBJ, RVOL1x, FAUNA, DISP, Pentagon,
  WTC/Hiroshima/Nagasaki/GS — broken down)
- Whether Group A vs Group B variant fired (these have different
  predictive signatures)
- Historical analogues: prior csNew3 fires on the same symbol/TF with
  same operand mix → outcome distribution

Output: 4-square matrix per SD-007. Logged to
`docs/agentic-os/debates/unified-combo/<date>-<fire-id>.md`.

## Stage-7 followups owned by PO::unified-combo

- [ ] Run TV firing on Group A vs Group B variants on the same chart;
      compare bar-set agreement
- [ ] Run TV firing on Pentagon-included vs Pentagon-excluded variants;
      measure predictive-value delta
- [ ] Backtest: under SD-001 (Pentagon always included), what's the
      change in fire count and predictive value vs the gated-Pentagon
      historical baseline?
- [ ] Decide: when Group A and Group B both fire on the same bar, treat
      as confirmation (bonus confidence) or treat each independently?
- [ ] Wire the bull-vs-bear-debate skill into the realtime Path-M
      pipeline so per-fire payloads land in `docs/agentic-os/debates/
      unified-combo/` automatically
