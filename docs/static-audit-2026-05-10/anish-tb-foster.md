# Static Audit — anish-tb-foster — 2026-05-10

## Summary
- Composites audited: 19 (PPBull, PPBear, AnishBull, AnishBear, RVOLBull, RVOLBear, BullPB, BullPBJ, BearPB, BearPBJ, SuperPup, SuperPPD, TB, TBPBJSignal, TBPBSignal, Foster, FosterPBJSignal, FosterPBSignal, B2BPUP, B2BPPD, AirBud, Leprosy, FirstPUPPass, FirstPPDPass) — 23 total
- ✅ matched: 22
- ⚠️ drift: 1 (FirstPUPPass plot location)
- ❓ unclear: 0

---

## Per-composite findings

### anish-tb-foster::PPBull / PPBear
- YAML: `sPPBull = priceUp AND volBull`; plot square/belowbar/blue/tiny/"PUP"
- Pine L133: `sPPBull = priceUp and volBull`; L513: `plotshape(sPPBull and show_pup, "PUP", shape.square, location.belowbar, color.blue, size=size.tiny, text="PUP")`
- Verdict: ✅ MATCH

### anish-tb-foster::AnishBull / AnishBear
- YAML: EMA-stack definitions `bullPass`/`bearPass`; no standalone plot
- Pine L117/L120: `bullPass` and `bearPass` defined; no plotshape for standalone roots (YAML: `plot: null`)
- Verdict: ✅ MATCH

### anish-tb-foster::RVOLBull / RVOLBear
- YAML: `bull_candle AND rv_d > rv_m AND rv_p >= i_rv_b_th`; plot arrowup/belowbar/cyan/"RV+"
- Pine L154/L155: `sRVOLBull/sRVOLBear` defined; L549/L550: `plotshape(sRVOLBull and show_rv_bull, "RVOL Bull", shape.arrowup, location.belowbar, color.new(#00FFFF, 0), size=size.small, text="RV+")` / `plotshape(sRVOLBear and show_rv_bear, "RVOL Bear", shape.arrowdown, location.abovebar, color.new(#FFA500, 0), size=size.small, text="RV-")`
- Verdict: ✅ MATCH

### anish-tb-foster::BullPB / BearPB
- YAML: `sig_pb_buy (buy_cross AND wait_buy)`; plot labelup/belowbar/aqua50/tiny/"PB"
- Pine L543: `plotshape(sBullPB and show_bull_pb, "Bull PB", shape.labelup, location.belowbar, color.new(color.aqua, 50), size=size.tiny, text="PB", textcolor=color.white)` — MATCH
- Pine L545: `plotshape(sBearPB and show_bear_pb, "Bear PB", shape.labeldown, location.abovebar, color.new(color.orange, 0), size=size.tiny, text="PB", textcolor=color.white)` — MATCH
- Verdict: ✅ MATCH

### anish-tb-foster::BullPBJ / BearPBJ
- YAML BullPBJ: `buy_cross AND wait_pbj_buy`; plot diamond/belowbar/yellow50/small/"PB+J"
- Pine L544: `plotshape(sBullPBJ and show_bull_pbj, "Bull PBJ", shape.diamond, location.belowbar, color.new(color.yellow, 50), size=size.small, text="PB+J", textcolor=color.black)` — MATCH
- YAML BearPBJ: diamond/abovebar/red/small/"PBJ"/textcolor=white
- Pine L546: `plotshape(sBearPBJ and show_bear_pbj, "Bear PBJ", shape.labeldown, location.abovebar, color.new(color.red, 0), size=size.small, text="PBJ", textcolor=color.white)`
- **Note**: YAML says `shape: diamond` but Pine uses `shape.labeldown`. Minor shape drift.
- Verdict: ⚠️ DRIFT — BearPBJ YAML says `shape: diamond` but Pine implements `shape.labeldown`. The label text "PBJ" and other parameters match. Update YAML to `shape: labeldown`.

### anish-tb-foster::SuperPup / SuperPPD
- YAML SuperPup: `sPPBull AND bullPass`; labelup/belowbar/lime/normal/"S-PUP"/black
- Pine L517: `plotshape(superPup and show_super_pup, "Super PUP", shape.labelup, location.belowbar, color.lime, size=size.normal, text="S-PUP", textcolor=color.black)` — MATCH
- YAML SuperPPD: `sPPBear AND bearPass`; labeldown/abovebar/maroon/large/"S-PPD"/white
- Pine L518: `plotshape(superPPD and show_super_ppd, "Super PPD", shape.labeldown, location.abovebar, color.maroon, size=size.large, text="S-PPD", textcolor=color.white)` — MATCH
- Verdict: ✅ MATCH

### anish-tb-foster::TB / TBPBJSignal / TBPBSignal
- YAML TB: after X AnishBull bars, window for sPPBear OR sBearPBJ OR sBearPB; labeldown/abovebar/purple/normal/"TB"/white
- Pine L522: `plotshape(tbSignal and show_tb, "TB", shape.labeldown, location.abovebar, color.purple, size=size.normal, text="TB", textcolor=color.white)` — MATCH
- YAML TBPBJSignal: labeldown/location.top/rgb(128,0,128)/large/"TB-PBJ"/white
- Pine L527: `plotshape(tbPBJSignal and show_tb_pbj, "TB PBJ", shape.labeldown, location.top, color.rgb(128, 0, 128), size=size.large, text="TB-PBJ", textcolor=color.white)` — MATCH
- YAML TBPBSignal: labeldown/abovebar/rgb(180,0,180)/large/"TB-PB"/white
- Pine L528: `plotshape(tbPBSignal and show_tb_pb, "TB PB", shape.labeldown, location.abovebar, color.rgb(180, 0, 180), size=size.large, text="TB-PB", textcolor=color.white)` — MATCH
- Verdict: ✅ MATCH

### anish-tb-foster::Foster / FosterPBJSignal / FosterPBSignal
- YAML Foster: after X AnishBear bars, window for sPPBull OR sBullPBJ OR sBullPB; labelup/belowbar/aqua/normal/"FOSTER"/black
- Pine L521: `plotshape(fosterSignal and show_foster, "Foster", shape.labelup, location.belowbar, color.aqua, size=size.normal, text="FOSTER", textcolor=color.black)` — MATCH
- YAML FosterPBJSignal: labelup/belowbar/rgb(0,255,200)/large/"FOSTER-PBJ"/black
- Pine L525: `plotshape(fosterPBJSignal and show_foster_pbj, "Foster PBJ", shape.labelup, location.belowbar, color.rgb(0, 255, 200), size=size.large, text="FOSTER-PBJ", textcolor=color.black)` — MATCH
- YAML FosterPBSignal: labelup/location.bottom/rgb(100,255,200)/large/"FOSTER-PB"/black
- Pine L526: `plotshape(fosterPBSignal and show_foster_pb, "Foster PB", shape.labelup, location.bottom, color.rgb(100, 255, 200), size=size.large, text="FOSTER-PB", textcolor=color.black)` — MATCH
- Verdict: ✅ MATCH

### anish-tb-foster::B2BPUP / B2BPPD
- YAML B2BPUP: `sPPBull AND sPPBull[1]`; labelup/location.bottom/teal/large/"B2B PUP"/white
- Pine L421: `bool b2bPUP = sPPBull and sPPBull[1]`; L531: `plotshape(b2bPUP and show_b2b_pup, "B2B PUP", shape.labelup, location.bottom, color.teal, size=size.large, text="B2B PUP", textcolor=color.white)` — MATCH
- YAML B2BPPD: `sPPBear AND sPPBear[1]`; labeldown/location.top/orange/large/"B2B PPD"/black
- Pine L422: `bool b2bPPD = sPPBear and sPPBear[1]`; L532: `plotshape(b2bPPD and show_b2b_ppd, "B2B PPD", shape.labeldown, location.top, color.orange, size=size.large, text="B2B PPD", textcolor=color.black)` — MATCH
- Verdict: ✅ MATCH

### anish-tb-foster::AirBud
- YAML: `(airBudArmed by sPPBear OR sRVOLBear), detect sPPBull OR sRVOLBull within airBudWindow`; labelup/location.top/rgb(255,215,0)/normal/"AIR BUD"/black
- Pine L539: `plotshape(airBudSignal and show_air_bud, "Air Bud", shape.labelup, location.top, color.rgb(255, 215, 0), size=size.normal, text="AIR BUD", textcolor=color.black)` — MATCH
- Verdict: ✅ MATCH

### anish-tb-foster::Leprosy
- YAML: `(leprosyArmed by sPPBull OR sRVOLBull), detect sPPBear OR sRVOLBear`; labeldown/location.bottom/rgb(139,0,139)/normal/"LEPROSY"/white
- Pine L540: `plotshape(leprosySignal and show_leprosy, "Leprosy", shape.labeldown, location.bottom, color.rgb(139, 0, 139), size=size.normal, text="LEPROSY", textcolor=color.white)` — MATCH
- Verdict: ✅ MATCH

### anish-tb-foster::FirstPUPPass
- YAML: state machine (neutral bars → PUP armed → AnishBull entry fires once); **labeldown/location.top**/rgb(0,255,127)/large/"1st PUP"/black
- Pine L535: `plotshape(firstPUPPass and show_1st_pup, "1st PUP Pass", shape.labeldown, location.top, color.rgb(0, 255, 127), size=size.large, text="1st PUP", textcolor=color.black)`
- YAML says `shape: labeldown` and `location: top` — Pine confirms both
- Verdict: ✅ MATCH

### anish-tb-foster::FirstPPDPass
- YAML: mirror of FirstPUPPass; **labelup/location.bottom**/rgb(255,69,0)/large/"1st PPD"/white
- Pine L536: `plotshape(firstPPDPass and show_1st_ppd, "1st PPD Pass", shape.labelup, location.bottom, color.rgb(255, 69, 0), size=size.large, text="1st PPD", textcolor=color.white)` — MATCH
- Verdict: ✅ MATCH

---

## Drift candidates (action items)

1. **BearPBJ shape mismatch** — YAML says `shape: diamond` but Pine L546 uses `shape.labeldown`. All other BearPBJ attributes (location, color, size, text, textcolor) match. **Recommend: update YAML** to `shape: labeldown`. No Pine change needed.
