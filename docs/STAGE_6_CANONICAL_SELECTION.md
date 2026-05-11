# Stage 6 — Canonical Selection + Archive Reconciliation

Stage 6 turns the "pending vetting" sibling variants (created during
the 2026-05-10 Master Directory ingest) into a clean per-family
`LATEST.txt` pointer and a tidied `versions/` directory.

Per Anish's hard rule (2026-05-10):
> Never label a variant "canonical" without empirical verification.
> Canonical determination is the OUTPUT of TV verification + the
> realtime-indicators Python ports, not the input.

So Stage 6 happens **after** Stage 4 (composite firing validation)
produces a verdict per (family, variant). Variants that fail Stage 4
are archived but never deleted (`do NOT delete anything` is also a hard
rule).

## Pending decisions Stage 6 must resolve

Per `bible-input/MANIFEST.md` pending-vetting section + the YAML drift
fix runs of 2026-05-10:

| Family | Sibling variants in repo | Stage 6 task |
|---|---|---|
| `hvd-pbj-ppd` | THE_ONLY_ONE (1767 lines, "USE THIS IS THE ONLY FUCKING ONE" on chart), HVDPBJPPD_2246_FROM_MASTERDIR (133 KB — bigger), HVDPBJPPD_1939_FROM_MASTERDIR (Tier-1 input defaults flipped), HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05 (1939-line predecessor) | Pick which is canonical for `LATEST.txt`; archive the others under `_legacy/<date>/`. |
| `vob-asym` | T3x6_MutEx_Claude_v8_2026-05-02 (current canonical per LATEST.txt), T3x6_FROM_MASTERDIR_ummmm (identical logic, plotshape locations differ) | If Stage 4 shows the plotshape differences don't affect fire timing, keep v8 canonical and archive ummmm. |
| `tnt-od` | TNT_Opening_Drive_OD_v3_2026-05-04 (current canonical per LATEST.txt), TNT_OD_v3 (148 KB, internally v3 with T1 RELAY/STACK/HCT/UC — "pending vetting"), TNT_OD_v2, TNT_OD_v1 | If Stage 4 shows TNT_OD_v3 fires match what Anish expects on his chart, flip LATEST.txt to v3 (per `tnt-od/VETTING.md`). |
| `squarify` | SQUARIFY_46_v2_2026-05-04 (canonical per LATEST.txt), SQUARIFY_v1, SQUARIFY_v2, SQUARIFY_ATOMS_v1 | v1/v2 are legacy. ATOMS is a sibling for atom-exposure (see SKU_VERIFICATION_AUTOMATION memory). Confirm 46_v2 stays canonical after Stage 4. |
| `vob-single-sens` | VOB_SINGLE_SENS_WITH_TABLES_v1, VOB_SINGLE_SENS_NO_TABLES_NO_EMISSION_v1 | The two files are byte-identical (audit finding). Pick one as canonical; archive the other with a "duplicate" marker. Filename "WITH_TABLES" misleading — neither file has `table.new()` calls. |
| `b2b-pup` | B2B_PUP_Combined_v4.32_2026-05-04 (canonical) | Only one — no Stage 6 action. |
| `heavy-pentagon`, `heavy-combo-toggles`, `hv-fvg-gz1-og`, `pb-pbj`, `proximity-gzi-hv`, `disp-4x`, `heavy-uncap`, `anish-50-1st-combo`, `vob-ladder-watch` | Single canonical each | No Stage 6 action. |
| NEW 7 families from Master Directory ingest (`hv-ladder`, `anish-tb-foster`, `heavy-weapons`, `fauna-shifu`, `vob-single-sens`, `yin-yang`, `e3-f2-cluster`) | Multi-variant siblings | After Stage 4 verdicts: pick canonical per family, archive predecessors. **NEVER DELETE** — move to `_legacy/<date>/` if needed. |

## Procedure

For each family with ≥2 sibling variants:

1. Read the Stage 4 validation log for every variant in that family.
   The log lists (composite, TF, match-rate, drift-summary) per variant.
2. The variant with the highest **average match-rate across composites**
   AND that fires on **Anish's actual chart** (per Path A TV labels)
   wins canonical.
3. Update the family's `LATEST.txt` to point at that variant's filename.
4. For each loser variant, **do not delete**. Move to `<family>/versions/_legacy/2026-MM-DD/<filename>` with a one-line note in
   `<family>/CHANGELOG.md` describing why it was demoted.
5. Update `bible-input/MANIFEST.md` to reflect the canonical pick + the
   archived siblings.
6. Re-run `tools/merge_extracts.py`, `tools/build_lineage_cards.py`,
   `tools/build_docs.py`, and `tools/build_commonality_table.py` so the
   bible reflects the new canonical state.
7. Commit + push.

## What "fires on Anish's actual chart" means

Anish's TradingView chart is the **runtime ground truth**. If Stage 4
validates a variant in pure Python but the Pine source on Anish's chart
doesn't match, the chart wins for canonical purposes (because the chart
is what Anish actually uses to trade).

Path A loggers (`path-a-loggers/versions/LOGGER_*.pine`) provide this
ground truth in bulk — each logger emits one `label.new()` per fire,
readable via `mcp__tradingview__data_get_pine_labels(study_filter=...)`.
For Stage 6, the chart-side label history is authoritative.

## What "archive don't delete" looks like

```
hvd-pbj-ppd/
  versions/
    LATEST.txt                                                 → "HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine"
    HVDPBJPPD_2026-05-10_THE_ONLY_ONE.pine                     (canonical)
    _legacy/
      2026-05-10/
        HVDPBJPPD_2246_FROM_MASTERDIR.pine                     (Stage 4 result: under-fired vs canonical)
        HVDPBJPPD_1939_FROM_MASTERDIR.pine                     (Stage 4 result: too-restrictive Tier-1 defaults)
        HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine      (predecessor, kept for diff)
  CHANGELOG.md
```

The `CHANGELOG.md` records WHY each variant was demoted:
```
## 2026-05-10 — Stage 6 canonical selection
- THE_ONLY_ONE (1767 lines) selected as canonical.
- 2246_FROM_MASTERDIR demoted to _legacy/2026-05-10/ — Stage 4 showed
  under-firing on 3 of 5 priority composites (CC Bull, LSC Bull, Floor)
  vs Anish's chart-side label history.
- 1939_FROM_MASTERDIR demoted to _legacy/2026-05-10/ — Tier-1 input
  defaults are flipped vs Anish's confirmed chart state (Anish has
  show_BullUUUU=true etc.).
- 4.26.1244am predecessor retained in _legacy/2026-05-10/ as a 2-byte
  whitespace-diff sibling.
```

## When Stage 6 is "done"

Every family in `bible-input/MANIFEST.md` has exactly ONE row in its
canonical column. The "pending-vetting" section is empty.
`docs/master-directory-delta-2026-05-10.md` and the
`docs/cross-variant-audit-2026-05-10.md` reports get a "RESOLVED on
<date>" footer pointing at the Stage 6 commit. PR #2 can then be
flipped to "ready for review."
