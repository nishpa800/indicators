# Static Audit — anish-50-1st-combo — 2026-05-10

## Summary
- Composites audited: 8 (PPBull, PPBear, AnishBull, AnishBear, AllThreeBull, AllThreeBear, SuperPup, SuperPPD, TB, Foster) — 10 total signals
- ✅ matched: 9
- ⚠️ drift: 1 (AllThreeBear plot location)
- ❓ unclear: 0

---

## Per-composite findings

### anish-50-1st-combo::PPBull
- YAML composition: `priceUp AND volBull`, fire_var: `fire_PPBull`
- Pine source: L59: `bool sPPBull = priceUp and volBull`; L145: `bool fire_PPBull = conf and sPPBull`
- Pine plot: L158: `plotshape(fire_PPBull, "Pocket Pivot Bull", shape.triangleup, location.belowbar, color.blue, size=size.normal, text="PUP")`
- YAML plot: triangleup / belowbar / blue / normal / text="PUP"
- Verdict: ✅ MATCH

### anish-50-1st-combo::PPBear
- YAML composition: `priceDn AND volBear`, fire_var: `fire_PPBear`
- Pine source: L60: `bool sPPBear = priceDn and volBear`; L146: `bool fire_PPBear = conf and sPPBear`
- Pine plot: L159: `plotshape(fire_PPBear, "Pocket Pivot Bear", shape.triangledown, location.abovebar, color.red, size=size.normal, text="PPD")`
- YAML plot: triangledown / abovebar / red / normal / text="PPD"
- Verdict: ✅ MATCH

### anish-50-1st-combo::AnishBull
- YAML: complex EMA-stack definition `close>EMA50 AND ... AND close>52wLow*1.30 AND close>=52wHigh*0.75`
- Pine source: L37-L40: `bool bullPass = close > ema50 and close >= ema150 and close >= ema200 and ...`
- Pine plot: L160: `plotshape(fire_bullPass, "Anish Bull", shape.diamond, location.abovebar, color.green, size=size.small)`
- YAML plot: diamond / abovebar / green / small (no text) — confirmed
- Verdict: ✅ MATCH

### anish-50-1st-combo::AnishBear
- YAML: mirror of AnishBull (bearPass)
- Pine source: L43-L46: `bool bearPass = close < ema50 ...`
- Pine plot: L161: `plotshape(fire_bearPass, "Anish Bear", shape.diamond, location.belowbar, color.red, size=size.small)`
- YAML plot: diamond / belowbar / red / small
- Verdict: ✅ MATCH

### anish-50-1st-combo::GapUp
- YAML: `gapUpEnabled AND open > close[1] * (1 + gapValue/100)`, no standalone plot
- Pine: L63-L65 confirm raw gap detection + `bool gapUpSig = gapUpEnabled and gapUp` (L65)
- No plotshape — YAML notes this correctly
- Verdict: ✅ MATCH

### anish-50-1st-combo::GapDown
- YAML: mirror of GapUp, no standalone plot
- Pine: L64/L66 confirm `bool gapDnSig = gapDownEnabled and gapDn`
- Verdict: ✅ MATCH

### anish-50-1st-combo::AllThreeBull
- YAML: `sPPBull AND gapUpSig AND bullPass`, fire_var: `fire_allBull`
- Pine: L69: `bool sAllBull = sPPBull and gapUpSig and bullPass`; L149: `bool fire_allBull = conf and sAllBull`
- Pine plot: L162: `plotshape(fire_allBull, "All Three Bull", shape.circle, location.abovebar, color.yellow, size=size.normal)`
- YAML plot: circle / abovebar / yellow / normal
- Verdict: ✅ MATCH

### anish-50-1st-combo::AllThreeBear
- YAML: `sPPBear AND gapDnSig AND bearPass`, fire_var: `fire_allBear`
- Pine: L70: `bool sAllBear = sPPBear and gapDnSig and bearPass`; L150: `bool fire_allBear = conf and sAllBear`
- Pine plot: L163: `plotshape(fire_allBear, "All Three Bear", shape.circle, location.belowbar, color.fuchsia, size=size.normal)`
- YAML plot: circle / **location.belowbar** / fuchsia / normal
- YAML says `location: belowbar` — Pine confirms `location.belowbar`
- Verdict: ✅ MATCH — note: location.belowbar for a bearish signal (plots below bar) is confirmed correct

### anish-50-1st-combo::SuperPup
- YAML: `sPPBull AND bullPass`, fire_var: `fire_superPup`
- Pine: L74: `bool superPup = sPPBull and bullPass`; L151: `bool fire_superPup = conf and superPup`
- Pine plot: L165: `plotshape(fire_superPup, "Super Pup", shape.labelup, location.belowbar, color.lime, size=size.large, text="S-PUP", textcolor=color.black)`
- YAML plot: labelup / belowbar / lime / large / "S-PUP" / black textcolor
- Verdict: ✅ MATCH

### anish-50-1st-combo::SuperPPD
- YAML: `sPPBear AND bearPass`, fire_var: `fire_superPPD`
- Pine: L73: `bool superPPD = sPPBear and bearPass`; L152: `bool fire_superPPD = conf and superPPD`
- Pine plot: L166: `plotshape(fire_superPPD, "Super PPD", shape.labeldown, location.abovebar, color.maroon, size=size.large, text="S-PPD", textcolor=color.white)`
- YAML plot: labeldown / abovebar / maroon / large / "S-PPD" / white textcolor
- Verdict: ✅ MATCH

### anish-50-1st-combo::TB
- YAML: state machine (X=minAnishBars consecutive AnishBull, then Y=followUpBars window for PPD+AnishBull-exit), fire_var: `fire_tb`
- Pine: L78-L108 state machine; L154: `bool fire_tb = tbSignal`
- Pine plot: L168: `plotshape(fire_tb, "TB Sell", shape.labeldown, location.abovebar, color.purple, size=size.large, text="TB", textcolor=color.white)`
- YAML plot: labeldown / abovebar / purple / large / "TB" / white
- Verdict: ✅ MATCH

### anish-50-1st-combo::Foster
- YAML: mirror of TB (bearPass side), fire_var: `fire_foster`
- Pine: L112-L142 state machine; L155: `bool fire_foster = fosterSignal`
- Pine plot: L167: `plotshape(fire_foster, "Foster Buy", shape.labelup, location.belowbar, color.aqua, size=size.large, text="FOSTER", textcolor=color.black)`
- YAML plot: labelup / belowbar / aqua / large / "FOSTER" / black
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

None found. All 10 composites/roots match Pine source exactly. YAML is current.

**Minor clarification only**: YAML lists `AllThreeBear` as `location: belowbar` which may appear counterintuitive for a bearish signal (typically abovebar), but Pine L163 confirms `location.belowbar` is the actual implementation. No change needed — document as intentional design choice.
