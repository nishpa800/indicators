# HV FVG GZ1 OG ⭐

**Canonical HV / GZI / FVG engine for the entire indicator suite.** Every
other indicator that references HV+FVG, GZI, or FVG bull/bear traces back
to this file.

`proximity-gzi-hv/` is a parity-checked stripped variant — same FVG / HV /
GZI core; dashboard + acceleration metrics removed. Stage-1 byte-diff
verified: identical input names/defaults, identical FVG predicate, identical
GZI overlap rule with adjacent-HV branch, identical plotshape titles /
styles / locations / colors / offsets, identical alertcondition IDs.

## Roots (6)

- **GZI bull/bear** — gap-zone-intersection of two same-polarity FVGs within
  bar-distance proximity (default 6 bars), with adjacent-HV rule allowing
  overlap when both FVGs are HV-confirmed
- **HV bull/bear** — high-volume FVG: bar volume hits the 5,000 / 252 / 63
  bar lookback maximum
- **FVG bull/bear raw** — 3-bar fair-value-gap creation event (bull: low >
  high[2]; bear: high < low[2]; with auto/manual threshold gate)

## Files

- `versions/HV_FVG_GZ1_OG_v1.pine` — canonical (10.8 KB, Pine v5)

## Bible

- `bible-input/extract-hv-fvg-gz1-og.yaml` — full extraction (6 roots)
- `test-indicators/versions/ROOTS_HVGZIFVG_TEST_v1.pine` — Stage-2 test rig

## Branch provenance

Lives on `claude/add-txt-indicator-format-b4FUu` — not on `main` as of bible
Stage 1.
