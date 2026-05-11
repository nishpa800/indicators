# Static Audit — vob-ladder-watch — 2026-05-10

## Summary
- Composites audited: 6 roots (zF, zE, zD, zC, zB, zA) + 6 composites (ladder_depth, escalated, WATCH, TIER3, TIER4, TIER5, FULL)
- ✅ matched: 12
- ⚠️ drift: 0
- ❓ unclear: 0

---

## Per-composite findings

### vob-ladder-watch roots zA through zF
- YAML: all roots are `kind: scalar_price`, fire via `f_top_active` helper; no standalone plotshapes (rendered only in depth_gauge_table via f_zone_cell)
- Pine: p_a through p_f defined at L106-L111 as `float p_a = f_top_active(bull_a)` etc. — no plotshape calls for individual roots; rendered in table at L210-L215
- YAML `output.kind: scalar_price` correctly describes this — these are not event booleans, they are continuous price values
- Verdict: ✅ MATCH

### vob-ladder-watch::ladder_depth (composite)
- YAML: `Counts consecutive strictly-ascending non-na tier mids walking F->E->D->C->B->A. Range 0..6.`
- Pine L117-L135: `var int ladder_depth = 0` incremented by sequential F→A checks — confirmed
- Verdict: ✅ MATCH

### vob-ladder-watch::WATCH (depth 2)
- YAML: `fire_watch = escalated AND ladder_depth == 2`; plotshape labelup/belowbar/#FFFF00/small/"WATCH\nF+E"
- Pine L151: `bool fire_watch = escalated and ladder_depth == 2`
- Pine L157-L158: `plotshape(fire_watch and show_labels, "WATCH (zF+zE)", shape.labelup, location.belowbar, color.new(#FFFF00, 0), size=size.small, text="WATCH\nF+E", ...)` — MATCH
- Verdict: ✅ MATCH

### vob-ladder-watch::TIER3 (depth 3)
- YAML: `fire_tier3 = escalated AND ladder_depth == 3`; labelup/belowbar/#FF9800/normal/"LDR3\n+D"
- Pine L152/L159-L160: confirmed — `shape.labelup, location.belowbar, color.new(#FF9800, 0), size=size.normal, text="LDR3\n+D"`
- Verdict: ✅ MATCH

### vob-ladder-watch::TIER4 (depth 4)
- YAML: `fire_tier4`; labelup/belowbar/#FF6D00/normal/"LDR4\n+C"
- Pine L153/L161-L162: confirmed
- Verdict: ✅ MATCH

### vob-ladder-watch::TIER5 (depth 5)
- YAML: `fire_tier5`; labelup/belowbar/#E91E63/large/"LDR5\n+B"
- Pine L154/L163-L164: confirmed
- Verdict: ✅ MATCH

### vob-ladder-watch::FULL (depth 6)
- YAML: `fire_full`; flag/location.bottom/#FFD700/huge/"FULL\nLDR"
- Pine L155/L165-L166: `plotshape(fire_full and show_labels, "FULL LADDER (+zA)", shape.flag, location.bottom, color.new(#FFD700, 0), size=size.huge, text="FULL\nLDR", ...)` — MATCH
- Verdict: ✅ MATCH

### vob-ladder-watch::escalation_alert_message / depth_gauge_table
- YAML: pipe-delimited alert() at L180-L191; depth_gauge_table at L203-L215
- Pine: confirmed at documented line ranges
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

None. All 5 escalation plotshapes (WATCH/TIER3/TIER4/TIER5/FULL) match YAML exactly on shape, location, color_hex, size, and text. Ladder depth logic and root scalar structure confirmed. YAML is current.
