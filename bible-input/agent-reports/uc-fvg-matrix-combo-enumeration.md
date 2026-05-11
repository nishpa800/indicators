# UC / FVG / Matrix Combo enumeration — every definition site

Generated 2026-05-11 from the cross-bible Explore agent's findings.

## Counts

- Unified Combo definitions (csNew3 + uc_bull/bear): **12 sites**
- FVG Combo definitions (csNew2): **10 sites**
- Matrix Combo definitions (csNew1): **10 sites**
- FVG Combo CONSTITUENTS (comboSet3/4_Bull/Bear): 40+ sites across 5 indicator families
- Matrix Combo CONSTITUENTS (comboSet1/2_Bull/Bear, sigNeo, sigTrinity): 40+ sites across 3 families
- .pine files scanned: 38
- Indicator families containing at least one of the 3 main combos: **6** (squarify, hvd-pbj-ppd, tnt-od, b2b-pup, heavy-weapons, ultra-combo)

---

## Distinct semantic groups

### Unified Combo (csNew3) — 3 semantic groups

| Group | Operands (canonical form) | Files in group | Count |
|---|---|---|---|
| **A — LAGGED** | `csNew1_Bull and nz(csNew2_Bull[1])` | 9 .pine files (HVDPBJPPD predecessors, Squarify variants, b2b-pup combined, others) | 9 |
| **B — SAME-BAR** | `csNew1_Bull and csNew2_Bull` | `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` only | 1 |
| **C — TNT counting** | count-based: ≥2 of {csNew1, csNew2, others} | `tnt-od/versions/TNT_OD_v3.pine` (uc_bull / uc_bear) | 1 |

This 7-vs-1 majority for LAGGED is the same finding as VALIDATE 1
(`docs/validation/2026-05-10-unified-combo.md`). Resolution requires TV
firing — owned by `PO::unified-combo`.

### FVG Combo (csNew2) — 1 universal semantic group

| Group | Operands | Files in group |
|---|---|---|
| **Universal** | `comboSet3_Bull or comboSet4_Bull` | All 10 csNew2 sites |

The variation lives **inside** `comboSet4_Bull` (the constituent), specifically
in whether Pentagon is gated in. See "Pentagon inclusion table" below.

### Matrix Combo (csNew1) — 1 universal semantic group

| Group | Operands | Files in group |
|---|---|---|
| **Universal** | `comboSet1_Bull or comboSet2_Bull` | All 10 csNew1 sites |

Variation lives inside `comboSet2_Bull` (Pentagon inclusion via
`cs_inc_pentagon_MAT` gate flag).

---

## Pentagon inclusion table (the canonical-decision input)

| File / family | UC includes Pentagon? | FVG comboSet4 Pentagon? | Matrix comboSet2 Pentagon? | Mechanism |
|---|---|---|---|---|
| `squarify/versions/SQUARIFY_46_v2_2026-05-04.pine` | gated | gated | gated | `cs_inc_pentagon_FVG` + `cs_inc_pentagon_MAT` IPSF flags |
| Squarify v1, v2 (legacy) | gated | gated | gated | same flags |
| `hvd-pbj-ppd/versions/HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine` | gated (same-bar AND) | gated | gated | same flags |
| HVDPBJPPD 4.26.1244am, 1939 masterdir, 2246 masterdir | gated (lagged AND) | gated | gated | same flags |
| `b2b-pup/versions/B2B_PUP_Combined_v4.32_2026-05-04.pine` | gated | gated | gated | same flags |
| `ultra-combo/versions/ULTRA_COMBO_v57_pine6.pine` (and pine5) | gated | gated | gated | same flags |
| `tnt-od/versions/TNT_OD_v3.pine` | **NO** (uc_bull/uc_bear are confluence-style) | n/a | n/a | Pentagon is not an operand of TNT's UC at all |
| `heavy-weapons/.../*NO_PENTAGON*.pine` | **NO (explicit exclude)** | **NO** (NO_PENTAGON variant) | **NO** | hardcoded — the NO_PENTAGON variant exists deliberately |

### Canonical decision (per Anish 2026-05-11)

**Always include Pentagon.** The canonical Python ports use Pentagon as an
included operand (no IPSF flag, no opt-out). See SD-001 in
`docs/agentic-os/STANDING_DECISIONS.md`.

The 2 files that exclude Pentagon (TNT_OD_v3 and Heavy Weapons NO_PENTAGON
variant) are NOT modified. Their .pine source stays as-is. The Python ports
for these files document the variance and produce a separate variant module
(e.g. `python_ports/tnt_od/v3_no_pentagon.py`); the canonical port lives at
`python_ports/<family>/<family>_canonical_pentagon_included.py`.

---

## FVG Combo constituents — comboSet3 / comboSet4

`comboSet3_Bull` and `comboSet4_Bull` are the two operands of csNew2_Bull.
They're defined in each of the 6 indicator families separately. The
canonical pattern (extracted from squarify 46_v2):

```
comboSet3_Bull = sigBullPBJ and sigDISPBull and sigFAUNABull and (sigBullRVOL1x or sigGrandSlam or sigWTC or sigHiroshima or sigNagasaki)
comboSet4_Bull = comboSet3_Bull and (cs_inc_pentagon_FVG and sigPentagon[1])
```

Pentagon enters the bible at `comboSet4` via the IPSF gate. With SD-001
applied, the canonical Python form is:

```python
comboset3_bull = sig_bull_pbj & sig_disp_bull & sig_fauna_bull & (
    sig_bull_rvol_1x | sig_grand_slam | sig_wtc | sig_hiroshima | sig_nagasaki
)
comboset4_bull = comboset3_bull & sig_pentagon.shift(1)   # Pentagon ALWAYS included per SD-001
```

(Pentagon's `[1]` lag is preserved — that's a structural offset, not an IPSF
default.)

---

## Matrix Combo constituents — comboSet1 / comboSet2

`comboSet1_Bull` and `comboSet2_Bull` are the two operands of csNew1_Bull.
Canonical pattern (extracted from squarify 46_v2):

```
comboSet1_Bull = sigBullPBJ and sigBullRVOL1x and (sigFAUNABull or sigDISPBull)
comboSet2_Bull = comboSet1_Bull and (cs_inc_pentagon_MAT and sigPentagon)
```

Note: comboSet2 uses `sigPentagon` (current bar), not `sigPentagon[1]`.
Different lag than comboSet4. Both lags are PRESERVED in the canonical
Python; SD-001 only removes the IPSF GATE flag, not the structural offset.

```python
comboset1_bull = sig_bull_pbj & sig_bull_rvol_1x & (sig_fauna_bull | sig_disp_bull)
comboset2_bull = comboset1_bull & sig_pentagon   # Pentagon ALWAYS included per SD-001
```

---

## Suspect / outlier definitions

1. **`tnt-od/versions/TNT_OD_v3.pine` `uc_bull` / `uc_bear`** — TNT's
   "Unified Combo" is a count-style confluence (≥2 of multiple operand
   streams) that does NOT participate in the csNew1/csNew2/csNew3 family.
   It happens to share the name "UC" but is a different concept. Document
   as a separate canonical (PO::unified-combo TNT-flavor) or rename in the
   bible to `tnt_od::TNT_CONFLUENCE_BULL` to disambiguate. Anish to choose
   later; not blocking SD-001.
2. **Heavy Weapons NO_PENTAGON variant** — deliberate exclusion. Stays
   as-is per "never modify Pine"; Python port documents the variance.

---

## Notes for the canonical-definition compiler

- **csNew3 same-bar-vs-lagged remains UNRESOLVED** — SD-001 does NOT touch
  this. PO::unified-combo arbitrates after TV firing. Until then, the
  canonical Python emits BOTH variants:
  `unified_combo_bull_lagged.py` (matches 9 .pine files) and
  `unified_combo_bull_same_bar.py` (matches THE_ONLY_ONE).
- **Pentagon is always included** in the canonical Python
  (`unified_combo_bull_canonical_pentagon_included.py`) regardless of
  same-bar vs lagged.
- **Heavy Weapons NO_PENTAGON and TNT uc_bull/bear** are recognized variants
  but NOT canonical. They get their own variant Python modules tagged
  `_no_pentagon` or `_tnt_confluence`.
