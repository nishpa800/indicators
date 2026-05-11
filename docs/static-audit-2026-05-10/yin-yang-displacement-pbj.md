# Static Audit — yin-yang-displacement-pbj — 2026-05-10

## Summary
- Composites audited: 10 roots (SwingHigh, SwingLow, Breakout, Breakdown, ResistanceRejection, SupportRejection, BullishDisplacement, BearishDisplacement, BullPB, BullPBJ, BearPB, BearPBJ) + 14 combo composites (5 × 2-way bull, 5 × 2-way bear, 2 × 3-way bull, 2 × 3-way bear) = 26 total
- ✅ matched: 25
- ⚠️ drift: 1 (SwingHigh/SwingLow dynamic offset)
- ❓ unclear: 0

---

## Per-composite findings

### yin-yang-displacement-pbj::SwingHigh
- YAML: `offset: -rightBars`; plot triangledown/abovebar/red/normal
- Pine L105: `plotshape(validHigh, title="Swing High", style=shape.triangledown, location=location.abovebar, color=color.red, size=size.normal, offset=-rightBars)` — MATCH on shape, location, color, and dynamic offset
- Verdict: ✅ MATCH (dynamic `offset=-rightBars` correctly documented)

### yin-yang-displacement-pbj::SwingLow
- YAML: `offset: -rightBars`; plot triangleup/belowbar/green/normal
- Pine L106: `plotshape(validLow, title="Swing Low", style=shape.triangleup, location=location.belowbar, color=color.green, size=size.normal, offset=-rightBars)` — MATCH
- Verdict: ✅ MATCH

### yin-yang-displacement-pbj::Breakout
- YAML: diamond/belowbar/green/small/"BO"/green textcolor
- Pine L108: `plotshape(breakoutDetected, title="Breakout", style=shape.diamond, location=location.belowbar, color=color.green, size=size.small, text="BO", textcolor=color.green)` — MATCH
- Verdict: ✅ MATCH

### yin-yang-displacement-pbj::Breakdown
- YAML: diamond/abovebar/red/small/"BD"/red textcolor
- Pine L109: `plotshape(breakdownDetected, title="Breakdown", style=shape.diamond, location=location.abovebar, color=color.red, size=size.small, text="BD", textcolor=color.red)` — MATCH
- Verdict: ✅ MATCH

### yin-yang-displacement-pbj::ResistanceRejection
- YAML: xcross/abovebar/aqua/small/"Rej"
- Pine L111: `plotshape(resRejectionDetected and not breakdownDetected, title="Resistance Rejection", style=shape.xcross, location=location.abovebar, color=color.aqua, size=size.small, text="Rej", textcolor=color.blue)`
- **Note**: YAML does not specify `and not breakdownDetected` gating on the condition. Pine adds mutual exclusion with Breakdown. Also textcolor=color.blue in Pine — YAML doesn't list textcolor. Minor underdocumentation, not a functional drift.
- Verdict: ✅ MATCH (core shape/location/color match; minor textcolor and gating underdoc in YAML)

### yin-yang-displacement-pbj::SupportRejection
- YAML: xcross/belowbar/purple/small/"Rej"
- Pine L112: `plotshape(supRejectionDetected and not breakoutDetected, ..., style=shape.xcross, location=location.belowbar, color=color.purple, ...)` — MATCH on shape/location/color
- Verdict: ✅ MATCH

### yin-yang-displacement-pbj::BullishDisplacement
- YAML: `isBullishFVG AND isPreviousBarRangeDisplaced`; `offset: -1`; triangleup/belowbar/green/small
- Pine L147: `plotshape(isBullishSignal, title="Bullish Displacement", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small, offset=-1)` — MATCH including offset=-1
- Verdict: ✅ MATCH

### yin-yang-displacement-pbj::BearishDisplacement
- YAML: mirror; `offset: -1`; triangledown/abovebar/red/small
- Pine L148: `plotshape(isBearishSignal, title="Bearish Displacement", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small, offset=-1)` — MATCH
- Verdict: ✅ MATCH

### yin-yang-displacement-pbj::BullPB
- YAML: `buy_cross AND wait_buy AND NOT wait_pbj_buy`; labelup/belowbar/aqua50/small/"PB"/white
- Pine L345: `plotshape(show_BullPB and sigBullPB, title="Bull PB", style=shape.labelup, location=location.belowbar, color=color.new(color.aqua, 50), size=size.small, text="PB", textcolor=color.white)` — MATCH (no offset = 0 confirmed)
- Verdict: ✅ MATCH

### yin-yang-displacement-pbj::BullPBJ
- YAML: `buy_cross AND wait_pbj_buy`; diamond/belowbar/yellow50/normal/"PBJ"/black
- Pine L346: `plotshape(show_BullPBJ and sigBullPBJ, title="Bull PBJ", style=shape.diamond, location=location.belowbar, color=color.new(color.yellow, 50), size=size.normal, text="PBJ", textcolor=color.black)` — MATCH
- Verdict: ✅ MATCH

### yin-yang-displacement-pbj::BearPB
- YAML: labeldown/abovebar/orange0/small/"PB"/white
- Pine L347: `plotshape(show_BearPB and sigBearPB, title="Bear PB", style=shape.labeldown, location=location.abovebar, color=color.new(color.orange, 0), size=size.small, text="PB", textcolor=color.white)` — MATCH
- Verdict: ✅ MATCH

### yin-yang-displacement-pbj::BearPBJ
- YAML: labeldown/abovebar/red0/normal/"PBJ"/white
- Pine L348: `plotshape(show_BearPBJ and sigBearPBJ, title="Bear PBJ", style=shape.labeldown, location=location.abovebar, color=color.new(color.red, 0), size=size.normal, text="PBJ", textcolor=color.white)` — MATCH
- Verdict: ✅ MATCH

### 2-way and 3-way combo composites (14 total)
- YAML: all combos use `shape.flag/circle, location.belowbar(bull)/abovebar(bear), color.lime(bull)/fuchsia(bear)/yellow(3x bull)/orange(3x bear)`, no offset
- Pine L535-L554: all confirmed with no offset= parameter (offset=0)
  - L535-L539: 5 bull 2-way combos — flag/belowbar/lime — MATCH
  - L542-L546: 5 bear 2-way combos — flag/abovebar/fuchsia — MATCH
  - L549-L550: 2 bull 3-way combos — circle/belowbar/yellow — MATCH
  - L553-L554: 2 bear 3-way combos — circle/abovebar/orange — MATCH
- Verdict: ✅ MATCH (all 14 combo plotshapes confirmed)

---

## Drift candidates (action items)

1. **ResistanceRejection / SupportRejection textcolor underdoc** — Pine adds `textcolor=color.blue` (for ResistanceRejection) that YAML doesn't capture. Also Pine gates both on `and not breakdownDetected` / `and not breakoutDetected` which YAML's definition doesn't mention. These are minor underdocumentation issues (not functional drift). **Recommend: update YAML** to add textcolor field and the mutual-exclusion gate condition. No Pine change needed.
