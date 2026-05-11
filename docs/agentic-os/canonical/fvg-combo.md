# Canonical — FVG Combo (PO::fvg-combo)

_Owned by `PO::fvg-combo`. Authored 2026-05-11. Source enumeration:
`bible-input/agent-reports/uc-fvg-matrix-combo-enumeration.md`._

## What FVG Combo IS

A composite that fires when EITHER comboSet3 OR comboSet4 fires:

```
csNew2_Bull = comboSet3_Bull OR comboSet4_Bull
csNew2_Bear = comboSet3_Bear OR comboSet4_Bear
```

`comboSet3` = the FVG Combo "lower" operand (no Pentagon).
`comboSet4` = the FVG Combo "upper" operand (= comboSet3 AND Pentagon[1]).

Identifier in Pine source: `csNew2_Bull`, `csNew2_Bear`. 10 sites across
all .pine files; ALL share the same csNew2-level OR pattern. Variation
lives INSIDE comboSet4 (Pentagon inclusion gate).

## Canonical decisions applied

| SD | Decision | Effect on canonical FVG Combo |
|---|---|---|
| SD-001 | Always include Pentagon | `cs_inc_pentagon_FVG` IPSF flag REMOVED. comboSet4 unconditionally includes `sigPentagon[1]`. |
| SD-002 | Never modify, always new-version | Canonical port at `python_ports/<family>/fvg_combo_canonical_pentagon_included.py`. Source .pine untouched. |
| SD-003 | IPSF defaults are not drift | DISP σ-mult, FAUNA lookback, RVOL thresholds preserved as DEFAULTS. |

## Canonical Python

```python
# python_ports/squarify/fvg_combo_canonical_pentagon_included.py
"""
FVG Combo BULL/BEAR canonical port. SD-001 applied: Pentagon always
included in comboSet4. SD-003: IPSF defaults preserved.
"""

DEFAULTS = {
    "disp_sigma_mult": 6.0,       # input.float from Pine
    "fauna_lookback": 20,         # input.int
    "rvol_1x_mult": 1.0,          # input.float
    # ... full IPSF table from squarify 46_v2 ...
}

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
    """FVG Combo upper: comboSet3 AND Pentagon[1].

    SD-001: Pentagon ALWAYS included (cs_inc_pentagon_FVG gate removed).
    Structural [1] lag preserved (it's an offset, not an IPSF default).
    """
    return comboset3_bull(df, params) & df["sig_pentagon"].shift(1).fillna(False)

def csnew2_bull(df, params):
    """FVG Combo: comboSet3 OR comboSet4."""
    return comboset3_bull(df, params) | comboset4_bull(df, params)

# Bear mirrors omitted for brevity.

DETECTIONS = {
    "comboset3_bull": comboset3_bull,
    "comboset4_bull": comboset4_bull,
    "csnew2_bull": csnew2_bull,
    # ... bear mirrors ...
}
STATE_MACHINES = {}
STUBBED = {}
```

## Per-file recognized variances

| File | Variance from canonical | Variant Python port |
|---|---|---|
| All squarify, all hvd-pbj-ppd, b2b-pup combined, ultra-combo | gated Pentagon (`cs_inc_pentagon_FVG` IPSF) | (canonical removes the gate; original Pine untouched) |
| Heavy Weapons NO_PENTAGON | Pentagon explicitly excluded at boolean level | `python_ports/heavy_weapons/fvg_combo_no_pentagon.py` (NOT canonical) |

## Notes for downstream Plot Owners

- `csNew2` (this) is the second operand of `csNew3` (Unified Combo). When
  PO::unified-combo arbitrates same-bar vs lagged for csNew3, that
  decision affects how this csNew2 enters UC, not how this csNew2 itself
  is computed.
- `comboSet4`'s Pentagon `[1]` lag is DIFFERENT from `comboSet2`'s
  Pentagon (current bar) — see `matrix-combo.md`. This is structural,
  preserved across all canonical and variant ports.

## Bull-vs-Hell debate hooks

PO::fvg-combo runs the debate on every csNew2 fire. Operand-level
breakdown is the heart of the debate evidence:

- Was it comboSet3 alone (Pentagon NOT firing) or comboSet4 (Pentagon also
  firing)? Pentagon-firing fires should produce higher P_true_angel by
  hypothesis — confirm via TV firing data.
- Which of the 5 OR-confluence operands (RVOL1x / GS / WTC / Hiroshima /
  Nagasaki) was the trigger? The "tier" of the volume signal weights the
  angel case.
- Concurrent: if csNew1 (Matrix Combo) is also firing, the next-tier
  composite (csNew3 = Unified Combo) handles it via PO::unified-combo. Hand
  off the debate.

## Stage-7 followups owned by PO::fvg-combo

- [ ] TV-firing comparison: comboSet3-only fires vs comboSet4 fires —
      predictive-value delta
- [ ] Backtest: under SD-001 (Pentagon always included), how much does
      comboSet4 fire-rate increase vs gated-Pentagon baseline?
- [ ] Calibrate: per-OR-operand (RVOL1x / GS / WTC / Hiroshima / Nagasaki)
      angel-confidence prior
- [ ] Cross-condition with PO::matrix-combo: when csNew1 AND csNew2 fire on
      the same bar (= csNew3 same-bar), is fire-rate higher than expected
      under independence? If so, csNew2 might predict csNew1 (or vice
      versa) — informational insight for the Heaven-vs-Hell debate
