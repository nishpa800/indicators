# Phase 1 enumeration table — template

The exact shape every Phase-1 output uses. Embed this as a section in `templates/validation-report.md § Phase 1 — Enumeration`.

## DEFINITIONS

One row per DEFINITION occurrence (a Pine line that ASSIGNS the boolean / value for the target).

| # | Indicator | File | Line range | Pine variable | Boolean (one-line excerpt) | YAML record? |
|---|---|---|---|---|---|---|
| 1 | <e.g. squarify> | <path> | L1217-L1218 | `sigUNIFIED_COMBO_BULL` | `csNew3 = csNew1 and csNew2[1]` | ✓ (`squarify::UNIFIED_COMBO_BULL`) |
| 2 | <e.g. hvd-pbj-ppd> | <path> | L1052 | `csNew3` | `csNew3 = csNew1 and csNew2` | ✓ (`hvdpbjppd::CS3_BULL`) — note same-bar AND |
| 3 | ... | ... | ... | ... | ... | ✗ MISSING from YAML — add in Phase 4 |

## OTHER OCCURRENCES

Count by classification (no row-level detail unless investigating a specific occurrence):

| Indicator | DEFINITION | REFERENCE | INPUT | PLOT | ALERT | COMMENT |
|---|---:|---:|---:|---:|---:|---:|
| squarify | 1 | 5 | 1 | 1 | 1 | 3 |
| hvd-pbj-ppd | 1 | 12 | 0 | 1 | 1 | 7 |
| ... | ... | ... | ... | ... | ... | ... |

## Orphans in YAML

YAML records pointing at line ranges where no Pine occurrence exists. Each row needs investigation in Phase 4.

| Canonical (YAML) | File (YAML claim) | Line range (YAML claim) | Actual file content at that range |
|---|---|---|---|
| <if any> | <path> | <range> | <what's actually there> |

If none: write "_(none)_" in the table.

## Missings (in Pine, not in YAML)

Pine DEFINITIONs that have no corresponding YAML record. Add to `bible-input/extract-*.yaml` in Phase 4.

| Pine variable | Indicator | File | Line range |
|---|---|---|---|
| <if any> | <e.g. squarify> | <path> | <range> |

If none: write "_(none)_" in the table.

## Aliases resolved

The full alias set the skill matched against. Document this so future runs can match the same set.

```
- <ALIAS_1>          # primary canonical
- <ALIAS_2>          # variation 1
- <ALIAS_3>          # colloquial name (e.g. "UC")
- ...
```

Source of each alias (e.g. `docs/glossary.md`, `docs/redundancy.md`, user request).
