# Reference: IPSF vs TRUE DRIFT classification taxonomy

The five-class taxonomy used by Phase 2 STATIC-DIFF to classify every pair of DEFINITIONs. Adapted from `docs/glossary.md § "IPSF (Input Structured Field) vs TRUE DRIFT"` — the canonical bible-wide definition.

## The five classes

### `identical`

Both DEFINITIONs produce a bit-for-bit identical boolean after normalization.

**Test**: normalized boolean (post alpha-rename + whitespace collapse + lowercase) is `==` byte-for-byte.

**Action**: report and move on. No reconcile.

**Example**:

```
Location A: bool sigPUP = conf and pp_priceUp and volume > pp_hiRedVol
Location B: bool det_PUP = barstate.isconfirmed and ((close-open)/open)*100 > pp_barSize and volume > pp_hiRedVol
```

After normalization (where `pp_priceUp` expands to `((close-open)/open)*100 > pp_barSize`):

```
b1 = i1 and h1 > h2 and h3 > h4
b1 = i1 and h1 > h2 and h3 > h4
```

Verdict: `identical`.

---

### `cosmetic-drift`

Variable names differ but the expression structure (operators, operand types, shift indices) is identical.

**Test**: normalized booleans differ ONLY in variable names; operator/operand/shift sequence matches.

**Action**: optional Stage-7 cleanup — unify the variable name across files. No urgency.

**Example**:

```
Location A: bool sigSAAB = conf and bb_baseBullish and bb_normalizedPrice >= th_saab_kratos and bb_normalizedPrice < th_1x
Location B: bool det_SAAB = conf and base_bull and norm_price >= saab_kratos_thresh and norm_price < x1_thresh
```

After alpha-rename:

```
b1 = i1 and b2 and h1 >= h2 and h1 < h3
b1 = i1 and b2 and h1 >= h2 and h1 < h3
```

Verdict: `cosmetic-drift` (same structure, names differ).

---

### `ipsf-default-variation`

Both DEFINITIONs use `input.*` for the relevant parameter, but the default values differ.

**Test**: structure identical; both parameters are `input.*`; numeric defaults differ.

**Action**: NONE required. The user tunes either default in TradingView settings; the difference is a packaging choice, not corruption.

**Example**:

```
Location A: gziProximity = input.int(6, "Max Bar Distance", ...)
Location B: gz1_dist   = input.int(7, "GZ1 Max Bar Distance", ...)
```

Verdict: `ipsf-default-variation`. Both `input.int(...)`; only defaults 6 vs 7 differ. User tunes.

---

### `ipsf-asymmetry`

The same parameter is exposed as `input.*` in some locations but HARDCODED as a constant in others. The numeric values may currently match, but tuning is asymmetric.

**Test**: at least one location has `input.*`; at least one has a hardcoded constant; values may or may not match.

**Action**: PROMOTE the hardcoded copy to `input.*` (matching the IPSF version). This is real corruption risk over time — without action, the two will silently diverge as the user tunes the IPSF one and forgets about the hardcoded one.

**Example**:

```
Location A: pp_barSize = input.float(3.0, "% Change", minval=0.1, step=0.1, group=grpPP)
Location B: pp_barSize = 3.0   // hardcoded
```

Verdict: `ipsf-asymmetry`. Values match TODAY (3.0); tuning surfaces diverge.

---

### `semantic drift`

Operators, operand sets, or shift indices differ. This is REAL drift — the two locations compute different booleans even after normalization.

**Test**: normalized booleans differ in operators or operand structure.

**Action**: ESCALATE TO USER. Present diff side-by-side. User designates canonical; mark the other as a variant or deprecate it.

**Example**:

```
Location A: csNew3_Bull = csNew1 and csNew2[1]     // lagged AND (Squarify)
Location B: csNew3_Bull = csNew1 and csNew2        // same-bar AND (HVDPBJPPD)
```

Verdict: `semantic drift`. Same name, different math. One of them is the "true" Unified Combo; the other is a drift.

---

## Decision tree

```
Both normalized booleans identical byte-for-byte?
├── YES → identical
└── NO
    │
    │ Differ ONLY in variable names (alpha-rename produces equality)?
    ├── YES → cosmetic-drift
    └── NO
        │
        │ Both locations use input.* for the differing parameter?
        ├── YES → ipsf-default-variation
        └── NO
            │
            │ At least one uses input.* and at least one is hardcoded?
            ├── YES → ipsf-asymmetry
            └── NO
                │
                │ Operators / operand structure differ
                └── YES → semantic-drift
```

## Why this taxonomy matters

The earlier bible work made a mistake: I called GZI proximity `6 vs 7` "real drift" when it was IPSF default variation. Anish corrected the framing, and we now have the five-class taxonomy to prevent false alarms.

False positives (calling IPSF variation "drift") flood the redundancy table with non-issues. The user loses trust in the table; real drift gets buried.

The taxonomy keeps the redundancy table tight: only `semantic-drift` and `ipsf-asymmetry` warrant action. The other three classes are informational only.

## Edge cases

### Shift indices

`b[1] AND b` and `b AND b[1]` are NOT semantic drift — both express "back-to-back" (boolean AND across two consecutive bars). The operator structure is commutative under AND.

But `b[1] AND b[0]` (B2B) vs `b[2] AND b[0]` (skip-one B2B) IS semantic drift — different bar indices have different meanings.

### NOT-gates

`a AND NOT b` vs `a AND (NOT b)` — identical after normalization (parentheses don't matter).

`a AND NOT b` vs `a AND b == false` — identical after normalization (semantic equality).

`(a OR b) AND NOT c` vs `a AND NOT c OR b AND NOT c` — these are DIFFERENT (the second one parses as `(a AND NOT c) OR (b AND NOT c)` per Pine operator precedence, equal to the first only by distributive law). Normalization should explicitly parenthesize per Pine's precedence; if the structure post-parenthesization differs, it's semantic drift.

### Helper variables

If both locations call a helper named `f_displacement_check(...)` with the same args, that's `identical` (the helper is the source of truth).

If they call helpers with the SAME NAME but different bodies, that's a HIDDEN semantic drift. Phase 2 must read the helper definitions at both locations and include them in the normalization. Failing to do so produces false `identical` verdicts that mask real bugs.

### IPSF with the same default and different titles/tooltips

```
Location A: gziProximity = input.int(6, "Max Bar Distance", group=group_gzi)
Location B: gziProximity = input.int(6, "GZI Proximity Bars", group=group_main)
```

Verdict: `cosmetic-drift` (title/group differ; default and numeric semantics match). User probably wants both titled the same; not blocking.
