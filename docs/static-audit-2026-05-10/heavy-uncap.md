# Static Audit — heavy-uncap — 2026-05-10

## Summary
- Composites audited: 19 roots + composites (LONG_1-5, SHORT_1-2, UU/UUU/UUUU, DD/DDD/DDDD, HOT_SPOT, B2B_2X_SAAB/KRATOS/BULL1X/BEAR1X, B2B_MID_BULL/BEAR, CONSEC_DISP_BULL/BEAR_2/3, FAUNA_BULL/BEAR)
- ✅ matched: 18
- ⚠️ drift: 1 (HOT_SPOT line number mismatch in YAML)
- ❓ unclear: 0

---

## Per-composite findings

### heavy-uncap::LONG_1 through LONG_5 / SHORT_1 / SHORT_2
- YAML boolean_summary (LONG_1): `barstate.isconfirmed AND hybRegRatio > hyb_addReg1 AND hybCumRatio > hyb_addCum1 AND (close > open) AND hybBodyRat ≥ hyb_bodyRat1`; offset=0
- Pine: L226-L228 for LONG_1 (sigAddLong1), L722-L723: `plotshape(show_Long1 and sigAddLong1, title="LONG 1", style=shape.labelup, location=location.belowbar, size=size.tiny, color=color.new(color.blue, 10), text="LONG 1", textcolor=color.yellow)` and `plotshape(show_Short1 and sigAddShort1, title="SHORT 1", style=shape.labeldown, ...)` — no offset parameter = offset 0 confirmed
- YAML LONG_1 plot_call: `plotshape(show_Long1 and sigAddLong1, title="LONG 1", ...)` — matches Pine L722
- Verdict: ✅ MATCH (all 7 hybrid momentum roots follow same pattern)

### heavy-uncap::UU / UUU / UUUU / DD / DDD / DDDD
- YAML: sequence-counter roots, offset=0; plots at L683-L688
- Pine L683-L688 all use no offset= parameter (offset=0 implied), `location.belowbar` for bull variants, `location.abovebar` for bear variants, `shape.triangleup` / `shape.triangledown`
- YAML does not specify plot_call text for these (marked `pine_source_line_range: "L389"` etc.) — plot calls confirmed in Pine match expected pattern
- Verdict: ✅ MATCH

### heavy-uncap::HOT_SPOT
- YAML: `offset=-1`, `pine_source_line_range: "L590-L601"`, `plot_call: 'plotshape(plot_HS, title="Hot Spot", style=shape.cross, location=location.bottom, color=color.new(color.red, 0), size=size.tiny, offset=-1)'`
- Pine: `plot_HS` is defined at L665, plotshape at **L746** (not L590-L601 as YAML says)
- Pine L746: `plotshape(plot_HS, title="Hot Spot", style=shape.cross, location=location.bottom, color=color.new(color.red, 0), size=size.tiny, offset=-1)` — shape, location, color, offset all MATCH YAML
- **Drift**: YAML `pine_source_line_range: "L590-L601"` is wrong; actual plotshape is at L746. The boolean logic may be around L590-L601 but the plotshape cited in the `plot_call` field is at L746.
- Verdict: ⚠️ DRIFT — `pine_source_line_range` should include L746 for the plotshape. Update YAML to `"L590-L601 (def), L665 (fire var), L746 (plotshape)"`.

### heavy-uncap::B2B_2X_SAAB / B2B_2X_KRATOS / B2B_2X_BULL_1X / B2B_2X_BEAR_1X
- YAML: `sigSAAB[1] AND sigSAAB`; offset=0; `pine_source_line_range: "L406"` etc.
- Pine L693: `plotshape(show_B2B_2xSAAB and sig_B2B_2xSAAB, title="2x SAAB", location=location.belowbar, style=shape.labelup, size=size.small, ...)` — no offset = offset 0 confirmed
- YAML offset=0 confirmed
- Verdict: ✅ MATCH

### heavy-uncap::B2B_MID_BULL / B2B_MID_BEAR
- YAML: mixed B2B (SAAB×1x or 1x×SAAB) with NOT gates; offset=0
- Pine L697-L698: plotshapes without offset= — offset 0 confirmed
- Verdict: ✅ MATCH

### heavy-uncap::CONSEC_DISP_BULL_2 / CONSEC_DISP_BEAR_2 / CONSEC_DISP_BULL_3 / CONSEC_DISP_BEAR_3
- YAML: `sigDispBull AND disp_bullStreak ≥ N`; **offset=-1**
- Pine L714-L717: all use `offset=-1` explicitly — confirmed
- Verdict: ✅ MATCH

### heavy-uncap::FAUNA_BULL / FAUNA_BEAR
- YAML: HIERARCHICAL_OR over MB/RE/TA/GG/TR/ES/GDR; label-based composite at L457-L502/L505-L550; offset=0
- Pine L457-L502: FAUNA bull label logic confirmed. Pine L722+ plots are for LONG/SHORT not FAUNA separately (FAUNA is label-embedded)
- Verdict: ✅ MATCH (label-based composite, no standalone plotshape, consistent with YAML notes)

---

## Drift candidates (action items)

1. **HOT_SPOT pine_source_line_range** — YAML says `"L590-L601"` but Pine plotshape is at L746. The plot_call content itself is correct. **Recommend: update YAML** `pine_source_line_range` to `"L590-L601 (calendar logic), L665 (fire var), L746 (plotshape)"`. No Pine change needed.
