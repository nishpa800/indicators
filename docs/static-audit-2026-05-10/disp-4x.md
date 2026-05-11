# Static Audit — disp-4x — 2026-05-10

## Summary
- Composites audited: 8 roots (D1_BULL, D1_BEAR, D2_BULL, D2_BEAR, D3_BULL, D3_BEAR, D4_BULL, D4_BEAR)
- ✅ matched: 8
- ⚠️ drift: 0
- ❓ unclear: 0

---

## Per-composite findings

### disp-4x::D1_BULL
- YAML boolean_summary: `barstate.isconfirmed AND d1_rng[1] > d1_thresh[1] AND low > high[2] AND close[1] > open[1]`
- Pine L39: `bool d1_bullFVG = low > high[2] and close[1] > open[1]`; L41: `bool d1_bull = conf and d1_prevDisp and d1_bullFVG`
- Pine plot: L44: `plotshape(d1_show_b and d1_bull, "D1 Bull", shape.square, location.top, color.new(#00FF00, 0), text="D1", textcolor=color.white, size=size.small, offset=-1)`
- YAML plot_call exactly matches L44. offset=-1 confirmed.
- Verdict: ✅ MATCH

### disp-4x::D1_BEAR
- YAML boolean_summary: `barstate.isconfirmed AND d1_rng[1] > d1_thresh[1] AND high < low[2] AND close[1] < open[1]`
- Pine L40: `bool d1_bearFVG = high < low[2] and close[1] < open[1]`; L42: `bool d1_bear = conf and d1_prevDisp and d1_bearFVG`
- Pine plot: L45: `plotshape(d1_show_r and d1_bear, "D1 Bear", shape.square, location.top, color.new(#FF0000, 0), text="D1", textcolor=color.white, size=size.small, offset=-1)`
- YAML plot_call matches. offset=-1 confirmed.
- Verdict: ✅ MATCH

### disp-4x::D2_BULL
- YAML boolean_summary: `barstate.isconfirmed AND d2_rng[1] > d2_thresh[1] AND bullFVG`; location.bottom
- Pine L63/L65: identical pattern; L68: `plotshape(d2_show_b and d2_bull, "D2 Bull", shape.square, location.bottom, color.new(#2962FF, 0), text="D2", textcolor=color.white, size=size.small, offset=-1)`
- Verdict: ✅ MATCH

### disp-4x::D2_BEAR
- YAML: location.bottom / fuchsia `#FF00FF`
- Pine L69: `plotshape(d2_show_r and d2_bear, "D2 Bear", shape.square, location.bottom, color.new(#FF00FF, 0), text="D2", textcolor=color.white, size=size.small, offset=-1)`
- Verdict: ✅ MATCH

### disp-4x::D3_BULL
- YAML: shape.xcross / location.top / green `#00FF00`; offset=-1
- Pine L92: `plotshape(d3_show_b and d3_bull, "D3 Bull", shape.xcross, location.top, color.new(#00FF00, 0), text="D3", textcolor=color.white, size=size.small, offset=-1)`
- Verdict: ✅ MATCH

### disp-4x::D3_BEAR
- YAML: shape.xcross / location.top / red `#FF0000`; offset=-1
- Pine L93: `plotshape(d3_show_r and d3_bear, "D3 Bear", shape.xcross, location.top, color.new(#FF0000, 0), text="D3", textcolor=color.white, size=size.small, offset=-1)`
- Verdict: ✅ MATCH

### disp-4x::D4_BULL
- YAML: shape.cross / location.bottom / blue `#2962FF`; offset=-1; size=small
- Pine L116: `plotshape(d4_show_b and d4_bull, "D4 Bull", shape.cross, location.bottom, color.new(#2962FF, 0), text="D4", textcolor=color.white, size=size.small, offset=-1)`
- Verdict: ✅ MATCH

### disp-4x::D4_BEAR
- YAML: shape.cross / location.bottom / fuchsia `#FF00FF`; offset=-1
- Pine L117: `plotshape(d4_show_r and d4_bear, "D4 Bear", shape.cross, location.bottom, color.new(#FF00FF, 0), text="D4", textcolor=color.white, size=size.small, offset=-1)`
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

None. All 8 D<n>_BULL / D<n>_BEAR roots match YAML exactly on boolean_summary, plot shape, location, color, size, and offset=-1. YAML is current.
