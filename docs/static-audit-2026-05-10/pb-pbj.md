# Static Audit — pb-pbj — 2026-05-10

## Summary
- Composites audited: 4 roots (PB_BULL, PBJ_BULL, PB_BEAR, PBJ_BEAR); 0 composites
- ✅ matched: 4
- ⚠️ drift: 0
- ❓ unclear: 0

---

## Per-composite findings

### pb-pbj::PB_BULL
- YAML boolean_summary: `barstate.isconfirmed AND buy_cross AND wait_buy AND NOT (buy_cross AND wait_pbj_buy)`; offset=0
- YAML plot_call: `plotshape(show_BullPB and sigBullPB, title="Sig#1 Bull PB", style=shape.labelup, location=location.bottom, color=color.new(color.aqua, 75), size=size.small, text="PB", textcolor=color.white, offset=0)`
- Pine L315: `plotshape(show_BullPB and sigBullPB, title="Sig#1 Bull PB", style=shape.labelup, location=location.bottom, color=color.new(color.aqua, 75), size=size.small, text="PB", textcolor=color.white, offset=0)` — exact match
- Verdict: ✅ MATCH

### pb-pbj::PBJ_BULL
- YAML boolean_summary: `barstate.isconfirmed AND buy_cross AND wait_pbj_buy`; offset=0
- YAML plot_call: `plotshape(show_BullPBJ and sigBullPBJ, title="Sig#2 Bull PBJ", style=shape.diamond, location=location.bottom, color=color.new(color.yellow, 25), size=size.normal, text="PBJ", textcolor=color.white, offset=0)`
- Pine L318: `plotshape(show_BullPBJ and sigBullPBJ, title="Sig#2 Bull PBJ", style=shape.diamond, location=location.bottom, color=color.new(color.yellow, 25), size=size.normal, text="PBJ", textcolor=color.white, offset=0)` — exact match
- Verdict: ✅ MATCH

### pb-pbj::PB_BEAR
- YAML boolean_summary: `barstate.isconfirmed AND sell_cross AND wait_sell AND NOT (sell_cross AND wait_pbj_sell)`; offset=0
- YAML plot_call: `plotshape(show_BearPB and sigBearPB, title="Sig#3 Bear PB", style=shape.labeldown, location=location.top, color=color.new(color.orange, 75), size=size.small, text="PB", textcolor=color.white, offset=0)`
- Pine L321: `plotshape(show_BearPB and sigBearPB, title="Sig#3 Bear PB", style=shape.labeldown, location=location.top, color=color.new(color.orange, 75), size=size.small, text="PB", textcolor=color.white, offset=0)` — exact match
- Verdict: ✅ MATCH

### pb-pbj::PBJ_BEAR
- YAML boolean_summary: `barstate.isconfirmed AND sell_cross AND wait_pbj_sell`; offset=0
- YAML plot_call: `plotshape(show_BearPBJ and sigBearPBJ, title="Sig#4 Bear PBJ", style=shape.diamond, location=location.top, color=color.new(color.red, 25), size=size.normal, text="PBJ", textcolor=color.white, offset=0)`
- Pine L324: `plotshape(show_BearPBJ and sigBearPBJ, title="Sig#4 Bear PBJ", style=shape.diamond, location=location.top, color=color.new(color.red, 25), size=size.normal, text="PBJ", textcolor=color.white, offset=0)` — exact match
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

None. All 4 PB/PBJ roots match YAML exactly on boolean_summary, plot_call, and offset=0. This is the cleanest indicator in the audit batch. YAML is current.
