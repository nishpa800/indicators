# Static Audit — e3-f2-cluster — 2026-05-10

## Summary
- Composites audited: 8 (BullFC, BullE3, BullF2, BearFC, BearE3, BearF2, AnyBull, AnyBear) + 6 atomic roots (bull_MB/RE/TA, bear_MB/RE/TA)
- ✅ matched: 8 composites
- ⚠️ drift: 0 (plot-level matches confirmed)
- ❓ unclear: 2 (pre-existing YAML flags re compression artifacts — not new drift)

---

## Per-composite findings

### e3-f2-cluster::BullFC
- YAML: `b1_2of3 AND b1_ovlp`; plot labeldown/belowbar/yellow 60%/huge/text="CLUSTER"
- Pine L300: `plotshape(sBullFC and show_bull_fc, title="Bull FC Cluster", location=location.belowbar, style=shape.labeldown, size=size.huge, color=col_bull_fc, text="CLUSTER")`
- Location, shape, size, text all match. `col_bull_fc` is defined from color input (yellow-based) — consistent with YAML.
- Verdict: ✅ MATCH

### e3-f2-cluster::BullE3
- YAML: `sessBar == 3 AND (bull_MB OR bull_RE OR bull_TA) on bar[0] AND bar[1] AND bar[2]`; plot circle/top/white 60%/huge/"E3"
- Pine L301: `plotshape(sBullE3 and show_bull_e3, title="Bull E3", location=location.top, style=shape.circle, size=size.huge, color=col_bull_e3, text="E3")`
- Verdict: ✅ MATCH

### e3-f2-cluster::BullF2
- YAML: `sessBar == 2 AND bull_MB AND bull_MB[1]`; plot triangleup/top/aqua 0%/huge/"F2"
- Pine L302: `plotshape(sBullF2 and show_bull_f2, title="Bull First Two", location=location.top, style=shape.triangleup, size=size.huge, color=col_bull_f2, text="F2")`
- Verdict: ✅ MATCH

### e3-f2-cluster::BearFC
- YAML: `b4_2of3 AND b4_ovlp`; plot labelup/abovebar/red 60%/huge/"BEAR\nCLUSTER"
- Pine L303: `plotshape(sBearFC and show_bear_fc, title="Bear FC Cluster", location=location.abovebar, style=shape.labelup, size=size.huge, color=col_bear_fc, text="BEAR\nCLUSTER")`
- Verdict: ✅ MATCH

### e3-f2-cluster::BearE3
- YAML: mirror of BullE3; plot circle/top/red 60%/huge/"Bear E3"
- Pine L304: `plotshape(sBearE3 and show_bear_e3, title="Bear E3", location=location.top, style=shape.circle, size=size.huge, color=col_bear_e3, text="Bear E3")`
- Verdict: ✅ MATCH

### e3-f2-cluster::BearF2
- YAML: `sessBar == 2 AND bear_MB AND bear_MB[1]`; plot triangledown/top/red 0%/huge/"Bear F2"
- Pine L305: `plotshape(sBearF2 and show_bear_f2, title="Bear First Two", location=location.top, style=shape.triangledown, size=size.huge, color=col_bear_f2, text="Bear F2")`
- Verdict: ✅ MATCH

### e3-f2-cluster::AnyBull
- YAML: `sBullFC OR sBullE3 OR sBullF2`; plot diamond/belowbar/lime 0%/huge/"ANY\nBULL"
- Pine L306: `plotshape(sAnyBull and show_any_bull, title="Any Bull", location=location.belowbar, style=shape.diamond, size=size.huge, color=col_any_bull, text="ANY\nBULL")`
- Verdict: ✅ MATCH

### e3-f2-cluster::AnyBear
- YAML: `sBearFC OR sBearE3 OR sBearF2`; plot diamond/abovebar/fuchsia 0%/huge/"ANY\nBEAR"
- Pine L307: `plotshape(sAnyBear and show_any_bear, title="Any Bear", location=location.abovebar, style=shape.diamond, size=size.huge, color=col_any_bear, text="ANY\nBEAR")`
- Verdict: ✅ MATCH

---

## Pre-existing flags (from YAML — not new drift)

1. **Asymmetric RVOL thresholds** — Bull FC uses `b1_sum >= 0.1`; Bear FC uses `b4_sum >= 0.5` (5x difference). YAML already documents this as `corruption_flag: true` on the bear side. Not a new finding; no Pine change without Anish verification.

2. **Bear double-gate** — `b4_base` re-applies `bodyDn` check when `b4_neg` already gates on it. YAML already flags `corruption_flag: true`. Not a new finding.

Both flags require Anish decision before any Pine change. YAML accurately describes the current (possibly corrupted) Pine implementation.

---

## Drift candidates (action items)

None at the plot-call level. All 8 composite plotshapes match YAML on shape, location, size, and text. Pre-existing asymmetry/corruption flags already cataloged in YAML.
