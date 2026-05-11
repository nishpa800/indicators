# Static Audit — hv-ladder-50-to-1k — 2026-05-10

## Summary
- Composites audited: 7 roots (HV50, HV150, HV250, HV500, HV1000, HEV, HotSpot) + 1 composite (VolumeHierarchy)
- ✅ matched: 5
- ⚠️ drift: 2 (HV50 and HV150 location field)
- ❓ unclear: 0

---

## Per-composite findings

### hv-ladder-50-to-1k::HEV
- YAML: `volume[1] > maxVolEver`; plot diamond/top/purple/normal/"HEV"/purple textcolor; offset=-1
- Pine L144: `plotshape(plot_HEV, "HEV", shape.diamond, location.top, color.new(color.purple, 0), size=size.normal, text="HEV", textcolor=color.purple, offset=-1)` — exact match
- Verdict: ✅ MATCH

### hv-ladder-50-to-1k::HV1000
- YAML: `volume[1] == ta.highest(volume, 1000)[1]`; plot circle/top/blue/normal/"1K"/yellow; offset=-1
- Pine L147: `plotshape(plot_1000, "1000-Bar High", shape.circle, location.top, color.new(color.blue, 0), size=size.normal, text="1K", textcolor=color.yellow, offset=-1)` — MATCH
- Verdict: ✅ MATCH

### hv-ladder-50-to-1k::HV500
- YAML: plot circle/top/red/normal/"500"/silver; offset=-1
- Pine L150: `plotshape(plot_500, "500-Bar High", shape.circle, location.top, color.new(color.red, 0), size=size.normal, text="500", textcolor=color.silver, offset=-1)` — MATCH
- Verdict: ✅ MATCH

### hv-ladder-50-to-1k::HV250
- YAML: plot circle/top/yellow/small/"250"/teal; offset=-1
- Pine L153: `plotshape(plot_250, "250-Bar High", shape.circle, location.top, color.new(color.yellow, 0), size=size.small, text="250", textcolor=color.teal, offset=-1)` — MATCH
- Verdict: ✅ MATCH

### hv-ladder-50-to-1k::HV150
- YAML: `plot: { shape: triangledown, location: belowbar, color: aqua, size: small, text: "150", textcolor: orange, offset: -1 }`
- Pine L156: `plotshape(plot_150, "150-Bar High", shape.triangledown, location.bottom, color.new(color.aqua, 0), size=size.small, text="150", textcolor=color.orange, offset=-1)`
- **DRIFT**: YAML says `location: belowbar` but Pine uses `location.bottom` (not `location.belowbar`)
- Verdict: ⚠️ DRIFT — YAML location field is wrong. Pine uses `location.bottom` (below the chart area, not adjacent to bars). **Recommend: update YAML** `location: belowbar` → `location: bottom` for HV150.

### hv-ladder-50-to-1k::HV50
- YAML: `plot: { shape: triangledown, location: belowbar, color: purple, size: small, text: "50", textcolor: yellow, offset: -1 }`
- Pine L159: `plotshape(plot_50, "50-Bar High", shape.triangledown, location.bottom, color.new(color.purple, 0), size=size.small, text="50", textcolor=color.yellow, offset=-1)`
- **DRIFT**: YAML says `location: belowbar` but Pine uses `location.bottom`
- Verdict: ⚠️ DRIFT — same issue as HV150. **Recommend: update YAML** `location: belowbar` → `location: bottom` for HV50.

### hv-ladder-50-to-1k::HotSpot
- YAML: `opExWindow OR qtrEndWindow OR ...`; plot cross/belowbar/red/tiny; offset=-1
- Pine L162: `plotshape(plot_HS, "Hot Spot", shape.cross, location.bottom, color.new(color.red, 0), size=size.tiny, offset=-1)`
- **Note**: YAML says `location: belowbar` but Pine also uses `location.bottom` here — same pattern as HV50/HV150
- Verdict: ⚠️ DRIFT — HotSpot YAML `location: belowbar` should be `location: bottom` to match Pine L162.

### hv-ladder-50-to-1k::VolumeHierarchy (composite)
- YAML: implicit priority filtering, only one signal per bar, HEV > 1000 > 500 > 250 > (150 bottom) > (50 bottom)
- Pine L131-L137: priority logic using `not isHEV`, `not is1000Bar` etc. — confirmed
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

1. **HV150 location** — YAML says `location: belowbar`; Pine uses `location.bottom`. **Recommend: update YAML**. No Pine change.
2. **HV50 location** — YAML says `location: belowbar`; Pine uses `location.bottom`. **Recommend: update YAML**. No Pine change.
3. **HotSpot location** — YAML says `location: belowbar`; Pine uses `location.bottom`. **Recommend: update YAML**. No Pine change.

Note: In TradingView Pine v5, `location.bottom` places markers in a separate pane area below the chart body (distinct from `location.belowbar` which places markers just below each bar). The YAML incorrectly conflates the two.
