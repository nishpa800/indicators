# HV FVG GZ1 OG — CHANGELOG

## v1 — 2026-05-10

Initial drop. Pine v5. Title: `HV FVG GZ1 OG THIS No tables` (shorttitle
`HV FVG GZ1 OG`). The OG variant of the HV/GZI FVG engine — no
dashboard, no acceleration metrics, no tables.

Sibling of `proximity-gzi-hv/` (which is a stripped variant). Same FVG
detection core (`bull_fvg_raw` / `bear_fvg_raw`, auto threshold from
cumulative avg range, MTF via `request.security`, HV detection over
5000/252/63 lookbacks). Differences:

- GZI overlap uses bar-distance proximity (`gziProximity`, default 6)
  instead of fixed bar-index window — same-polarity FVGs within the
  bar-distance count when prices overlap, or are adjacent if both are
  HV.
- Plots: 4 plotshape flags (Bull/Bear GZI on top, Bull/Bear HV below
  bar, all `offset=-1`).
- Alerts: 10 alertconditions (FVG creation, mitigation, GZI
  Bull/Bear/Any, HV Bull/Bear/Any).
- FVG box draw extends `n+480` bars; mitigation draws optional dashed
  line on close-through.
