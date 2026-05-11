# Static Audit — vob-single-sens-with-tables — 2026-05-10

## Summary
- Composites audited: 6 roots (T1-buy, T1-sell, T2-buy, T2-sell, T3-buy, T3-sell) + composites (pool totals, raw tier flags, alert payloads, zone drawings)
- ✅ matched: 6
- ⚠️ drift: 0
- ❓ unclear: 1 (pre-existing: "WITH_TABLES" filename vs no table.new() in code — already flagged in YAML)

---

## Per-composite findings

### vob-single-sens::T1-buy
- YAML: `sig_t1_buy`; asym_threshold % dominance + price_at_bull; plotshape diamond/belowbar/#26ba9f/small/"T1"
- Pine L324-L331:
  ```
  plotshape(sig_t1_buy,
       title     = "T1 Buy",
       style     = shape.diamond,
       location  = location.belowbar,
       color     = color.new(#26ba9f, 0),
       size      = size.small,
       text      = "T1", ...)
  ```
  Exact match including color hex, no offset= (offset=0 confirmed)
- Verdict: ✅ MATCH

### vob-single-sens::T1-sell
- YAML: sig_t1_sell; diamond/abovebar/#6626ba/small/"T1"
- Pine L333-L340: `style=shape.diamond, location=location.abovebar, color=color.new(#6626ba, 0), size=size.small, text="T1"` — exact match
- Verdict: ✅ MATCH

### vob-single-sens::T2-buy
- YAML: sig_t2_buy; exactly one valid bull OB + price inside; triangleup/belowbar/#00e5ff/normal/"T2"
- Pine L343-L350: `style=shape.triangleup, location=location.belowbar, color=color.new(#00e5ff, 0), size=size.normal, text="T2"` — exact match
- Verdict: ✅ MATCH

### vob-single-sens::T2-sell
- YAML: sig_t2_sell; triangledown/abovebar/#ff00e5/normal/"T2"
- Pine L352-L359: `style=shape.triangledown, location=location.abovebar, color=color.new(#ff00e5, 0), size=size.normal, text="T2"` — exact match
- Verdict: ✅ MATCH

### vob-single-sens::T3-buy
- YAML: sig_t3_buy; one OB + raw vol > bear pool * super_mult; circle/belowbar/#ffff00/large/"T3"
- Pine L362-L369: `style=shape.circle, location=location.belowbar, color=color.new(#ffff00, 0), size=size.large, text="T3"` — exact match
- Verdict: ✅ MATCH

### vob-single-sens::T3-sell
- YAML: sig_t3_sell; circle/abovebar/#ff4400/large/"T3"
- Pine L371-L378: `style=shape.circle, location=location.abovebar, color=color.new(#ff4400, 0), size=size.large, text="T3"` — exact match
- Verdict: ✅ MATCH

### vob-single-sens composites (pool_total, dom_vol, raw_tier_flags, alert payloads, zone drawings)
- All are derived-scalar or alert/drawing composites with no plotshape. Operand existence confirmed at documented line ranges.
- Verdict: ✅ MATCH

---

## Pre-existing flag (not new drift)

**Filename says "WITH_TABLES"** but Pine has no `table.new()` calls — only zone line/fill drawing. YAML already flags this at severity: high. Anish decision required on whether to add tables or rename file. Not a new finding.

---

## Drift candidates (action items)

None. All 6 T1/T2/T3 signal plotshapes match YAML exactly on shape, location, color_hex, size, text, and offset=0. YAML is current.
