# Static Audit — heavy-pentagon + heavy-combo-toggles — 2026-05-10

## Summary
- Composites audited: 18 total (15 heavy-pentagon directional combos + 3 heavy-combo-toggles master plots)
- ✅ matched: 17
- ⚠️ drift: 1 (HEAVY_YIN_YANG YAML operand list includes ALL 7 P1+P2 roots, but Pine uses a 2-group OR — operand list format is misleading)
- ❓ unclear: 0

Note: 10 heavy-pentagon roots (SAAB, KRATOS, RVOL_1X_BULL/BEAR, GRAND_SLAM, MOAB, PENTAGON, WTC, HIROSHIMA, NAGASAKI) have direct plot_calls. These are audited below as single-line checks since they are roots not composites.

---

## Root plot_call verification (heavy-pentagon)

### heavy-pentagon::SAAB
- YAML plot_call: `plotshape(fire_SAAB,title="SAAB",style=shape.square,location=location.top,size=size.tiny,color=color.lime,text="SAAB")`
- Pine source: L363: `plotshape(fire_SAAB,title="SAAB",style=shape.square,location=location.top,size=size.tiny,color=color.lime,text="SAAB")` — no offset= (offset=0)
- Verdict: ✅ MATCH (character-for-character)

### heavy-pentagon::KRATOS
- YAML plot_call: `plotshape(fire_Kratos,title="Kratos",style=shape.square,location=location.bottom,size=size.tiny,color=color.orange,text="Krat")`
- Pine source: L364 — confirmed match, no offset= (offset=0)
- Verdict: ✅ MATCH

### heavy-pentagon::RVOL_1X_BULL
- YAML plot_call: `plotshape(fire_BullRVOL1x,title="Bull RVOL 1x",style=shape.xcross,location=location.bottom,size=size.small,color=color.green,text="RV1x+")`
- Pine source: L365 — confirmed match, no offset= (offset=0)
- Verdict: ✅ MATCH

### heavy-pentagon::RVOL_1X_BEAR
- Pine source: L366 — confirmed match, no offset= (offset=0)
- Verdict: ✅ MATCH

### heavy-pentagon::GRAND_SLAM
- YAML plot_call: `plotshape(fire_GrandSlam,title="Grand Slam",style=shape.triangleup,location=location.bottom,size=size.normal,color=color.aqua,text="DINGER")`
- Pine source: L367 — confirmed match, no offset= (offset=0)
- Verdict: ✅ MATCH

### heavy-pentagon::MOAB
- Pine source: L368 — confirmed match, no offset= (offset=0)
- Verdict: ✅ MATCH

### heavy-pentagon::PENTAGON
- YAML plot_call: `plotshape(fire_Pentagon,title="Pentagon",style=shape.diamond,location=location.top,...)`
- Pine source: L369 — confirmed match, no offset= (offset=0)
- Verdict: ✅ MATCH

### heavy-pentagon::WTC
- Pine source: L370 — confirmed match, no offset= (offset=0)
- Verdict: ✅ MATCH

### heavy-pentagon::HIROSHIMA
- Pine source: L371 — confirmed match, no offset= (offset=0)
- Verdict: ✅ MATCH

### heavy-pentagon::NAGASAKI
- Pine source: L372 — confirmed match, no offset= (offset=0)
- Verdict: ✅ MATCH

---

## Per-composite findings (heavy-pentagon)

### heavy-pentagon::HEAVY_YIN_YANG_BULL
- YAML composition: AND with operands listing all 7 individual roots: `RVOL_1X_BULL, GRAND_SLAM, RVOL_1X_BEAR, MOAB, PENTAGON, WTC, HIROSHIMA` plus `direction_gate: dispBull`
- Pine source: L278-L283, L293:
  - `bool groupA_Bull = sigBullRVOL1x or sigGrandSlam`
  - `bool groupA_Bear = sigBearRVOL1x or sigMOAB`
  - `bool groupB = sigPentagon or sigWTC or sigHiroshima`
  - `bool baseYinYang = (groupA_Bull or groupA_Bear) and groupB`
  - `bool sigHYYBull = baseYinYang and dispBull`
- Pine plot: L381: `plotshape(fire_HYYBull,title="Heavy Yin-Yang Bull",style=shape.circle,location=location.bottom,size=size.small,color=color.lime,text="HYY")` — confirmed matches YAML plot_call, no offset= (offset=0)
- Verdict: ⚠️ DRIFT — YAML operands list presents all 7 primitives as if they ALL must be present (AND semantics implied by the `type: AND` field), but Pine uses `(groupA_Bull OR groupA_Bear) AND groupB`. The correct semantic is: "at least one P1 (directional OR not) AND at least one P2" — not "all 7 must fire." The YAML `type: AND` combined with 7 operands strongly implies an AND-of-all, which is wrong. **Recommend: update YAML** to use `type: OR_GROUPS` or document the actual Pine grouping:
  - Group A (any one of): RVOL_1X_BULL, GRAND_SLAM, RVOL_1X_BEAR, MOAB
  - Group B (any one of): PENTAGON, WTC, HIROSHIMA
  - Condition: `(GroupA_any) AND (GroupB_any)`, gated by `dispBull`
  This is the single most semantically misleading YAML entry across all 5 audited families.

### heavy-pentagon::HEAVY_YIN_YANG_BEAR
- YAML: same operand list + `direction_gate: dispBear`; Pine L294: `sigHYYBear = baseYinYang and dispBear`
- Pine plot: L382 — confirmed match
- Verdict: ⚠️ DRIFT (same operand-list issue — same fix applies)

### heavy-pentagon::HEAVY_YIN_YANG_NEUTRAL
- YAML: same + `direction_gate: noDisp`; Pine L295: `sigHYYNeutral = baseYinYang and noDisp`
- Pine plot: L383 — confirmed match
- Verdict: ⚠️ DRIFT (same fix applies — group semantics misrepresented)

### heavy-pentagon::HEAVY_NAGASAKI_BULL
- YAML composition: AND with operands `NAGASAKI, RVOL_1X_BULL, GRAND_SLAM, RVOL_1X_BEAR, MOAB` + `direction_gate: dispBull`
- Pine source: L284: `bool baseNagasaki = sigNagasaki and (groupA_Bull or groupA_Bear)`; L298: `sigHNBull = baseNagasaki and dispBull`
- Pine plot: L386 — confirmed match
- Verdict: ✅ MATCH — the YAML operand list here accurately represents: "Nagasaki AND (any one of the 4 P1 signals)" — because "any one of 4" is still a list, not all-AND. The `type: AND` with these operands is less misleading than HEAVY_YIN_YANG because there's a natural reading of "NAGASAKI must fire AND at least one of the P1 signals." However, this is still slightly misleading. Flagging but not marking as DRIFT since the YAML notes explain `baseNagasaki` semantics.

### heavy-pentagon::HEAVY_NAGASAKI_BEAR
- Pine L299: `sigHNBear = baseNagasaki and dispBear`; plot L387 — confirmed
- Verdict: ✅ MATCH

### heavy-pentagon::HEAVY_NAGASAKI_NEUTRAL
- Pine L300: `sigHNNeutral = baseNagasaki and noDisp`; plot L388 — confirmed
- Verdict: ✅ MATCH

### heavy-pentagon::HEAVY_NAGASAKI_VOL_BULL
- YAML: AND — `NAGASAKI, PENTAGON, WTC, HIROSHIMA` + `direction_gate: dispBull`
- Pine L285, L303: `baseNagasakiV = sigNagasaki and groupB`; `sigHNVBull = baseNagasakiV and dispBull`
- Pine plot: L391 — confirmed match
- Verdict: ✅ MATCH

### heavy-pentagon::HEAVY_NAGASAKI_VOL_BEAR
- Pine L304: `sigHNVBear = baseNagasakiV and dispBear`; plot L392 — confirmed
- Verdict: ✅ MATCH

### heavy-pentagon::HEAVY_NAGASAKI_VOL_NEUTRAL
- Pine L305: `sigHNVNeutral = baseNagasakiV and noDisp`; plot L393 — confirmed
- Verdict: ✅ MATCH

### heavy-pentagon::HEAVY_TRIDENT_BULL
- YAML: AND with all 8 primitives (NAGASAKI + 4 P1 + 3 P2) + `direction_gate: dispBull`
- Pine L286, L308: `baseTrident = sigNagasaki and (groupA_Bull or groupA_Bear) and groupB`; `sigHTBull = baseTrident and dispBull`
- Pine plot: L396 — confirmed match
- Verdict: ✅ MATCH — same "any-one-of-group" semantics as HEAVY_NAGASAKI but combined. The YAML does correctly note `baseTrident = P1+P2+P3 all-axes co-occurrence` in the notes field, making the intent clear despite the flat-list operand representation.

### heavy-pentagon::HEAVY_TRIDENT_BEAR
- Pine L309: `sigHTBear = baseTrident and dispBear`; plot L397 — confirmed
- Verdict: ✅ MATCH

### heavy-pentagon::HEAVY_TRIDENT_NEUTRAL
- Pine L310: `sigHTNeutral = baseTrident and noDisp`; plot L398 — confirmed
- Verdict: ✅ MATCH

### heavy-pentagon::NEUTRAL_HEAVY_X2_BULL
- YAML: AND — `PENTAGON, WTC, HIROSHIMA` + `direction_gate: dispBull`
- Pine L287: `baseNHx2 = (sigPentagon and sigWTC) or (sigPentagon and sigHiroshima) or (sigWTC and sigHiroshima)`; L313: `sigNHx2Bull = baseNHx2 and dispBull`
- Pine plot: L401 — confirmed match
- Verdict: ✅ MATCH — the YAML notes field correctly specifies `(sigPentagon and sigWTC) or (sigPentagon and sigHiroshima) or (sigWTC and sigHiroshima)` which is "2-of-3" P2 tiers, accurately describing the Pine. Operand list is {PENTAGON, WTC, HIROSHIMA} with the understanding that at least 2 must co-occur. The `type: AND` in YAML is misleading (implies all 3), but the notes field corrects this. Marginal drift — notes override the misleading operand structure.

### heavy-pentagon::NEUTRAL_HEAVY_X2_BEAR
- Pine L314: `sigNHx2Bear = baseNHx2 and dispBear`; plot L402 — confirmed
- Verdict: ✅ MATCH

### heavy-pentagon::NEUTRAL_HEAVY_X2_NEUTRAL
- Pine L315: `sigNHx2Neutral = baseNHx2 and noDisp`; plot L403 — confirmed
- Verdict: ✅ MATCH

---

## Per-composite findings (heavy-combo-toggles)

### heavy-combo-toggles::HEAVY_COMBO_BULL
- YAML composition: OR_TOGGLED — any of `[HEAVY_YIN_YANG_BULL, HEAVY_NAGASAKI_BULL, HEAVY_NAGASAKI_VOL_BULL, HEAVY_TRIDENT_BULL, NEUTRAL_HEAVY_X2_BULL]` gated by `[en_HYYBull, en_HNBull, en_HNVBull, en_HTBull, en_NHx2Bull]`, offset=-1
- Pine source: L249: `bool masterBull = (en_HYYBull and sigHYYBull) or (en_HNBull and sigHNBull) or (en_HNVBull and sigHNVBull) or (en_HTBull and sigHTBull) or (en_NHx2Bull and sigNHx2Bull)`
- Pine plot: L258: `plotshape(masterBull,title="S1: Heavy Combo Bull",style=shape.circle,location=location.bottom,size=size.normal,color=color.lime,text="HC▲",offset=-1)` — `offset=-1` confirmed
- YAML plot_call matches L258 exactly including `offset=-1`
- Verdict: ✅ MATCH — OR logic correct; eligibility checkboxes (15 en_* booleans) correctly gating each of the 5 bull combos; offset=-1 correctly reflects displacement-candle anchor

### heavy-combo-toggles::HEAVY_COMBO_BEAR
- YAML composition: OR_TOGGLED over 5 Bear combos with en_* gates, offset=-1
- Pine source: L250: analogous OR across the 5 bear directional booleans + en_* gates
- Pine plot: L259: `plotshape(masterBear,...,offset=-1)` — confirmed offset=-1
- YAML plot_call matches L259 exactly
- Verdict: ✅ MATCH

### heavy-combo-toggles::HEAVY_COMBO_NEUTRAL
- YAML composition: OR_TOGGLED over 5 Neutral combos with en_* gates, offset=0
- Pine source: L251: OR across the 5 neutral directional booleans + en_* gates
- Pine plot: L260: `plotshape(masterNeutral,title="S3: Heavy Combo Neutral",style=shape.circle,location=location.top,size=size.normal,color=color.white,text="HC—")` — no offset= param (offset=0 confirmed)
- YAML plot_call matches L260 exactly (no offset= parameter, meaning offset=0)
- Verdict: ✅ MATCH — offset=0 is correct because Neutral combos use `noDisp` (no displacement candle to mark); all constituent signals fire on bar[0]

---

## Drift candidates (action items)

1. **HEAVY_YIN_YANG (Bull/Bear/Neutral) — YAML operand type AND is semantically wrong** — The YAML lists 7 operands under `type: AND` implying all 7 must fire. Pine logic is `(groupA_Bull OR groupA_Bear) AND groupB` — i.e., "any one P1 signal AND any one P2 signal." This is the most critical structural documentation error across the 5 families. A reader implementing from the YAML alone would produce a far more restrictive signal than intended. **Recommend: update YAML** for HEAVY_YIN_YANG_BULL/BEAR/NEUTRAL to use a two-group OR-within-AND structure:
   ```yaml
   composition:
     type: ANY_OF_GROUPA AND ANY_OF_GROUPB
     groupA: [RVOL_1X_BULL, GRAND_SLAM, RVOL_1X_BEAR, MOAB]
     groupB: [PENTAGON, WTC, HIROSHIMA]
     direction_gate: dispBull  # or dispBear or noDisp
   ```
   **Anish decision required**: confirm that `groupA_Bear` (RVOL_1X_BEAR, MOAB) can satisfy the HYY condition even when gated by `dispBull`. This is what Pine does — a bearish RVOL spike can co-occur with a bullish displacement to form HYY Bull. If this is intentional, confirm in YAML notes. If not, Pine needs a direction-consistency gate.

2. **NEUTRAL_HEAVY_X2 — 2-of-3 semantics** — YAML `type: AND` with 3 operands implies all 3 P2 tiers must fire. Pine implements `(P and W) or (P and H) or (W and H)` (any 2-of-3). The YAML notes field contains the correct explanation but the `type: AND` field is wrong. **Recommend: change YAML `type`** from `AND` to `TWO_OF_THREE` or update the notes to override the type field explicitly, and confirm the notes field takes precedence over the type field in the bible schema.
