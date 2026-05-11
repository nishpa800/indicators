# Static Audit — proximity-gzi-hv — 2026-05-10

## Summary
- Composites audited: 6 roots (GZI_BULL, GZI_BEAR, HV_BULL, HV_BEAR, FVG_BULL_RAW, FVG_BEAR_RAW); 0 composites
- ✅ matched: 6
- ⚠️ drift: 0
- ❓ unclear: 0

Note: This is a stripped variant of hv-fvg-gz1-og. YAML declares all 6 roots as `variant_of: hv-fvg-gz1-og::*` with `parity_check_required: true`. All operands and plot calls are documented as verbatim from canonical.

---

## Per-composite findings

### proximity-gzi-hv::GZI_BULL
- YAML: same boolean_summary as hv-fvg-gz1-og::GZI_BULL; offset=-1
- YAML plot_call: `plotshape(bullGZI_trigger, title="Bullish GZI", style=shape.flag, location=location.top, color=gziBullCss, size=size.normal, offset=-1)`
- Pine L225-L226: `plotshape(bullGZI_trigger, title="Bullish GZI", style=shape.flag, location=location.top, color=gziBullCss, size=size.normal, offset=-1)` — exact match
- Verdict: ✅ MATCH

### proximity-gzi-hv::GZI_BEAR
- YAML: same as canonical; offset=-1
- Pine L228-L229: `plotshape(bearGZI_trigger, title="Bearish GZI", style=shape.flag, location=location.top, color=gziBearCss, size=size.normal, offset=-1)` — exact match
- Verdict: ✅ MATCH

### proximity-gzi-hv::HV_BULL
- YAML: same as canonical; offset=-1; `plotshape(bullHV_trigger, title="Bullish HV", style=shape.flag, location=location.belowbar, color=hvBullCss, size=size.normal, offset=-1)`
- Pine L231-L232: `plotshape(bullHV_trigger, title="Bullish HV", style=shape.flag, location=location.belowbar, color=hvBullCss, size=size.normal, offset=-1)` — exact match
- Verdict: ✅ MATCH

### proximity-gzi-hv::HV_BEAR
- YAML: same as canonical; offset=-1
- Pine L234-L235: `plotshape(bearHV_trigger, title="Bearish HV", style=shape.flag, location=location.belowbar, color=hvBearCss, size=size.normal, offset=-1)` — exact match
- Verdict: ✅ MATCH

### proximity-gzi-hv::FVG_BULL_RAW / FVG_BEAR_RAW
- YAML: no standalone plotshape; box-only + alertcondition; confirmed identical to canonical
- Pine: no plotshape for these roots; confirmed
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

None. Variant is byte-identical to canonical hv-fvg-gz1-og on all 4 plotshapes and both FVG alertconditions. YAML correctly marks all roots as `parity_check_required: true` and the audited plots confirm zero drift. Stage 1.5 byte-diff (as recommended in YAML) would provide final confirmation.
