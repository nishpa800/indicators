# Static Audit — hv-fvg-gz1-og — 2026-05-10

## Summary
- Composites audited: 6 roots (GZI_BULL, GZI_BEAR, HV_BULL, HV_BEAR, FVG_BULL_RAW, FVG_BEAR_RAW); 0 composites
- ✅ matched: 6
- ⚠️ drift: 0
- ❓ unclear: 0

---

## Per-composite findings

### hv-fvg-gz1-og::GZI_BULL
- YAML: `bull_fvg AND fvg_time != lastTime AND showGZI AND overlap detection`; offset=-1; `plotshape(bullGZI_trigger, title="Bullish GZI", style=shape.flag, location=location.top, color=gziBullCss, size=size.normal, offset=-1)`
- Pine L225-L226: `plotshape(bullGZI_trigger, title="Bullish GZI", style=shape.flag, location=location.top, color=gziBullCss, size=size.normal, offset=-1)` — exact match
- Verdict: ✅ MATCH

### hv-fvg-gz1-og::GZI_BEAR
- YAML: mirror of GZI_BULL (bearish polarity); offset=-1; `plotshape(bearGZI_trigger, title="Bearish GZI", style=shape.flag, location=location.top, color=gziBearCss, size=size.normal, offset=-1)`
- Pine L228-L229: exact match
- Verdict: ✅ MATCH

### hv-fvg-gz1-og::HV_BULL
- YAML: `bull_fvg AND showHV AND (volume[1] == highest(volume,5000)[1] OR ... OR volume[1] == highest(volume,63)[1])`; offset=-1; `plotshape(bullHV_trigger, title="Bullish HV", style=shape.flag, location=location.belowbar, color=hvBullCss, size=size.normal, offset=-1)`
- Pine L231-L232: exact match
- Verdict: ✅ MATCH

### hv-fvg-gz1-og::HV_BEAR
- YAML: mirror of HV_BULL; offset=-1; `plotshape(bearHV_trigger, title="Bearish HV", style=shape.flag, location=location.belowbar, color=hvBearCss, size=size.normal, offset=-1)`
- Pine L234-L235: exact match
- Verdict: ✅ MATCH

### hv-fvg-gz1-og::FVG_BULL_RAW
- YAML: no dedicated plotshape; visualized as FVG box; `alertcondition_id: "Bullish FVG"`
- Pine: no standalone plotshape for FVG_BULL_RAW; surfaced via box draws and bull_count increment alert (L240)
- Verdict: ✅ MATCH

### hv-fvg-gz1-og::FVG_BEAR_RAW
- YAML: mirror; no dedicated plotshape; `alertcondition_id: "Bearish FVG"`
- Pine L241: `alertcondition(bear_count > bear_count[1], "Bearish FVG", ...)` — confirmed
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

None. All 4 plotshape roots (GZI_BULL, GZI_BEAR, HV_BULL, HV_BEAR) match YAML exactly on title, shape, location, offset=-1. FVG_RAW roots correctly documented as box-only. YAML is current.
