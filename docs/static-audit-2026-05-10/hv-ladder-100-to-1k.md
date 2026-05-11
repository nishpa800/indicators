# Static Audit — hv-ladder-100-to-1k — 2026-05-10

## Summary
- Composites audited: 12 roots (HV100, HV200, HV300, HV400, HV500, HV600, HV700, HV800, HV900, HV1000, HEV, HotSpot) + 1 composite (VolumeHierarchy)
- ✅ matched: 10
- ⚠️ drift: 3 (HV100, HV200, HotSpot location field)
- ❓ unclear: 0

---

## Per-composite findings

### hv-ladder-100-to-1k::HEV
- YAML: plot diamond/top/purple/normal/"HEV"/red textcolor; offset=-1
- Pine L150: `plotshape(plot_HEV, "HEV", shape.diamond, location.top, color.new(color.purple, 0), size=size.normal, text="HEV", textcolor=color.red, offset=-1)` — MATCH
- Verdict: ✅ MATCH

### hv-ladder-100-to-1k::HV1000 through HV300
- YAML: all at `location: top`; Pine L153-L174: all use `location.top` — confirmed
- Verdict: ✅ MATCH (HV1000, HV900, HV800, HV700, HV600, HV500, HV400, HV300 all match)

### hv-ladder-100-to-1k::HV200
- YAML: `plot: { shape: triangledown, location: belowbar, color: aqua, size: small, text: "200", textcolor: orange, offset: -1 }`
- Pine L177: `plotshape(plot_200, "200-Bar High", shape.triangledown, location.bottom, color.new(color.aqua, 0), size=size.small, text="200", textcolor=color.orange, offset=-1)`
- **DRIFT**: YAML says `location: belowbar`; Pine uses `location.bottom`
- Verdict: ⚠️ DRIFT — same issue as hv-ladder-50 HV150. **Recommend: update YAML** to `location: bottom`.

### hv-ladder-100-to-1k::HV100
- YAML: `plot: { shape: triangledown, location: belowbar, color: purple, size: small, text: "100", textcolor: yellow, offset: -1 }`
- Pine L180: `plotshape(plot_100, "100-Bar High", shape.triangledown, location.bottom, color.new(color.purple, 0), size=size.small, text="100", textcolor=color.yellow, offset=-1)`
- **DRIFT**: YAML says `location: belowbar`; Pine uses `location.bottom`
- Verdict: ⚠️ DRIFT — **Recommend: update YAML** to `location: bottom`.

### hv-ladder-100-to-1k::HotSpot
- YAML: `plot: { shape: cross, location: belowbar, color: red, size: tiny, offset: -1 }`
- Pine L183: `plotshape(plot_HS, "Hot Spot", shape.cross, location.bottom, color.new(color.red, 0), size=size.tiny, offset=-1)`
- **DRIFT**: YAML says `location: belowbar`; Pine uses `location.bottom`
- Verdict: ⚠️ DRIFT — **Recommend: update YAML** to `location: bottom`.

### hv-ladder-100-to-1k::VolumeHierarchy (composite)
- YAML: implicit priority filtering, one signal per bar, HEV > 1000 > 900 > ... > 100
- Pine L132-L143: 10-level exclusion chain — confirmed
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

1. **HV200 location** — YAML `location: belowbar`; Pine `location.bottom`. **Recommend: update YAML**.
2. **HV100 location** — YAML `location: belowbar`; Pine `location.bottom`. **Recommend: update YAML**.
3. **HotSpot location** — YAML `location: belowbar`; Pine `location.bottom`. **Recommend: update YAML**.

These are the same `belowbar` vs `bottom` drift found in hv-ladder-50-to-1k. Both YAML files were likely written with the same incorrect assumption. Both need the same fix.
