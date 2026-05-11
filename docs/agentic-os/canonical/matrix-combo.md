# Canonical — Matrix Combo (PO::matrix-combo)

_Owned by `PO::matrix-combo`. Authored 2026-05-11. Source enumeration:
`bible-input/agent-reports/uc-fvg-matrix-combo-enumeration.md`._

## What Matrix Combo IS

A composite that fires when EITHER comboSet1 OR comboSet2 fires:

```
csNew1_Bull = comboSet1_Bull OR comboSet2_Bull
csNew1_Bear = comboSet1_Bear OR comboSet2_Bear
```

`comboSet1` = the Matrix Combo "lower" operand (no Pentagon).
`comboSet2` = the Matrix Combo "upper" operand (= comboSet1 AND Pentagon).

Identifier in Pine source: `csNew1_Bull`, `csNew1_Bear`. 10 sites across
all .pine files; all share the same csNew1-level OR pattern. Variation
lives INSIDE comboSet2 (Pentagon inclusion gate).

## Trinity vs Neo (legacy ambiguity — RESOLVED here)

The Stage-1 plan flagged: "in the matrix one, I don't even know if Trinity
is part of it or if it's just neo for the unified combo." Per the
enumeration agent's read of all .pine sources:

- **Neo** (`sigNeo`) feeds `comboSet1_Bull` directly — Neo IS the matrix
  primitive that drives Matrix Combo.
- **Trinity** (`sigTrinity`) is a SEPARATE composite that does NOT feed
  csNew1 — it's used in Squarify's S25/S35/S45 numbered atoms but NOT in
  Matrix Combo. Trinity is its own thing.
- **Conclusion**: Matrix Combo = comboSet1 OR comboSet2, both of which
  derive from Neo + RVOL1x + (FAUNA or DISP). Trinity is downstream of
  csNew1 in some atoms but not an operand of csNew1.

(If Anish disagrees, this is the place to overwrite. PO::matrix-combo owns
this canonical statement.)

## Canonical decisions applied

| SD | Decision | Effect on canonical Matrix Combo |
|---|---|---|
| SD-001 | Always include Pentagon | `cs_inc_pentagon_MAT` IPSF flag REMOVED. comboSet2 unconditionally includes `sigPentagon`. |
| SD-002 | Never modify, always new-version | Canonical port at `python_ports/<family>/matrix_combo_canonical_pentagon_included.py`. Source .pine untouched. |
| SD-003 | IPSF defaults are not drift | Matrix lookback (67), RVOL thresholds, FAUNA lookback all preserved as DEFAULTS. |

## Canonical Python

```python
# python_ports/squarify/matrix_combo_canonical_pentagon_included.py
"""
Matrix Combo BULL/BEAR canonical port. SD-001 applied: Pentagon always
included in comboSet2. SD-003: IPSF defaults preserved.
"""

DEFAULTS = {
    "matrix_lookback": 67,        # input.int — sigNeo's volume lookback
    "rvol_1x_mult": 1.0,          # input.float
    "fauna_lookback": 20,         # input.int
    "disp_sigma_mult": 6.0,       # input.float
    # ... full IPSF table from squarify 46_v2 ...
}

def comboset1_bull(df, params):
    """Matrix Combo lower: PBJ + RVOL1x + (FAUNA or DISP). Driven by sigNeo
    upstream (sigNeo == matrix-volume primitive)."""
    return (
        df["sig_bull_pbj"] & df["sig_bull_rvol_1x"]
        & (df["sig_fauna_bull"] | df["sig_disp_bull"])
    )

def comboset2_bull(df, params):
    """Matrix Combo upper: comboSet1 AND Pentagon (current bar).

    SD-001: Pentagon ALWAYS included (cs_inc_pentagon_MAT gate removed).
    Note current-bar (no [1] lag) — different from FVG comboSet4 which uses
    Pentagon[1]. Structural offset, preserved.
    """
    return comboset1_bull(df, params) & df["sig_pentagon"]

def csnew1_bull(df, params):
    """Matrix Combo: comboSet1 OR comboSet2."""
    return comboset1_bull(df, params) | comboset2_bull(df, params)

# Bear mirrors omitted for brevity.

DETECTIONS = {
    "comboset1_bull": comboset1_bull,
    "comboset2_bull": comboset2_bull,
    "csnew1_bull": csnew1_bull,
    # ... bear mirrors ...
}
STATE_MACHINES = {}
STUBBED = {}
```

## Per-file recognized variances

| File | Variance from canonical | Variant Python port |
|---|---|---|
| All squarify, all hvd-pbj-ppd, b2b-pup combined, ultra-combo | gated Pentagon (`cs_inc_pentagon_MAT` IPSF) | (canonical removes the gate; original Pine untouched) |
| Heavy Weapons NO_PENTAGON | Pentagon explicitly excluded at boolean level | `python_ports/heavy_weapons/matrix_combo_no_pentagon.py` (NOT canonical) |

## Notes for downstream Plot Owners

- `csNew1` is the FIRST operand of `csNew3` (Unified Combo). PO::unified-combo
  consumes this canonical. The same-bar-vs-lagged decision for UC is
  about WHEN csNew2 enters UC — it does NOT change how csNew1 itself is
  computed.
- The Pentagon LAG asymmetry: comboSet2 uses `sigPentagon` (current bar);
  comboSet4 (FVG side) uses `sigPentagon[1]`. This is intentional in the
  Pine source — preserved in canonical Python.

## Bull-vs-Hell debate hooks

PO::matrix-combo runs the debate on every csNew1 fire:

- Was it comboSet1 alone (Pentagon NOT firing this bar) or comboSet2
  (Pentagon also firing this bar)? Pentagon-firing should boost
  angel-confidence.
- Was Neo (the underlying matrix primitive) ALSO firing 1-3 bars prior?
  Persistence of matrix volume is bullish-confirming (or bearish-confirming
  depending on direction).
- If Trinity (separate composite) is ALSO firing concurrently, that's a
  multi-confluence event — note in debate evidence even though Trinity
  isn't operand-of-csNew1.

## Stage-7 followups owned by PO::matrix-combo

- [ ] TV-firing comparison: comboSet1-only fires vs comboSet2 fires —
      predictive-value delta
- [ ] Backtest: under SD-001 (Pentagon always included), how much does
      comboSet2 fire-rate increase vs gated-Pentagon baseline?
- [ ] Cross-condition with PO::fvg-combo: when csNew1 AND csNew2 fire on
      the same bar (= csNew3 same-bar variant), is the predictive value
      multiplicative or sub-multiplicative?
- [ ] Trinity-vs-Neo confirmation: is Trinity actually downstream-only, or
      does it ever feed csNew1 in a Pine file the enumeration missed?
- [ ] Calibrate: prior for Pentagon current-bar firing (comboSet2 trigger)
      vs Pentagon-1-bar-prior firing (comboSet4 trigger) — these are
      different events even with the same Pentagon root
