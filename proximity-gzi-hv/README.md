# Proximity GZI HV

**Stripped variant of `hv-fvg-gz1-og` (canonical).** Same FVG / HV / GZI
detection core; dashboard, acceleration metrics, and table outputs removed.

Stage-1 parity check (extraction agent + spot byte-diff): identical fields,
parameters, predicates, and plotshape declarations. The differences are
limited to:
- Indicator title / shorttitle ("Proximity GZI HV" vs "HV FVG GZ1 OG")
- Some color-input defaults
- Removed dashboard / acceleration code

## Removed vs canonical

- Dashboard group (Show Dashboard / Location / Size inputs)
- Acceleration Periods group (Period 1 / 2 / 3 inputs)
- `table.new` declaration + every `table.cell` call
- `countSignalsInPeriod` helper, all `*_p1`/`*_p2`/`*_p3` and `*_total_*` vars
- Signal-bar tracking arrays + signal counters
- `tosolid` color method
- Unused `dynamic = false` constant

## Files

- `versions/PROXIMITY_GZI_HV_v1.pine` — variant (10.8 KB, Pine v5)

## Bible

- `bible-input/extract-proximity-gzi-hv.yaml` — full extraction with
  `variant_of: hv-fvg-gz1-og` annotations and `parity_check_required: true`
  for Stage 1.5 byte-diff
- See `hv-fvg-gz1-og/README.md` for canonical reference

## Branch provenance

Available on both `main` and `claude/add-txt-indicator-format-b4FUu`.
