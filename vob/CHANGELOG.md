# VOB Indicator Suite — Changelog

## VOB ASYM HVPROX v1.1 — 2026-08-18 (Volume Order Blocks + Asymmetric Signals + HV Proximity v1.1)
- **NEW STUDY PAIR (create lane) on the operator's `vob asymmetric signals.txt` base (sha256 `5a1f0ced07dd…`).** `versions/VOB_ASYM_HVPROX_v1.1.pine` (TIME, shorttitle `VOB HVP1.1`) + `tick_friendly/VOB_ASYM_HVPROX_TICKFRIENDLY_v1.1.pine` (TICK, `HVP1.1TICK`) — byte-identical below the indicator() line except the shorttitle tag inside the 12 log.info metadata lines.
- Operator goal 2026-08-18: HV proximity VPs, adjustable rolling windows + adjustable bar distances; **IFF** an HV candle sits within K bars of a T1/T2/T3 fire (either tier), then and only then the VP fires. Defaults **500/1000/1500/3000/4000/Nagasaki** with **3/5/5/5/5/15 bars**.
- 12 lanes = {HV 500, HV 1000, HV 1500, HV 3000, HV 4000, NAGASAKI} × {Bull (T1/T2/T3 BUY), Bear (T1/T2/T3 SELL)}; each a sig_/fire_/alf_ chain: real plotshape VP + plot checkbox + 🔔 alert checkbox + alert() (grammar v1.3 plain names) + log.info metadata. Print-highest-tier rule default ON (toggle).
- HV(N) = `volume >= ta.highest(volume, N)` (rolling; ties count); NAGASAKI = running all-time max over confirmed candles, strict >; proximity = later-of-the-two candle, distance ≤ K (0 = same candle); everything evaluated on the confirmed bar (non-repainting, same as the base engine).
- Base edits (behavior of T1/T2/T3 unchanged at defaults): E1 indicator title/shorttitle stamped; E2 tier plot keys side-typed "(Bull)/(Bear)", bare const colors, white text, T3 SUPER Buy yellow→green #64DD17 (yellow banned); E3 math.min clamps on the OB scan-loop offsets; E4 tier lanes get plot + 🔔 alert checkboxes (default ON).
- Budget: 21/64 TV units (6 base tier + 2 fill-anchor plot() + 1 series-color fill + 12 new, plot colors all bare const); 0 alertcondition; graphic objects = the base's order-block lines/labels only.
- Base hosted verbatim in `vob/sources/VOB_ASYM_SIGNALS_operator-base_2026-08-18.txt` (sha256 `5a1f0ced07dd…`, T-INDSTUDY C12).
- Rigor R2: every numeric default is operator-dictated; base carried verbatim (sha-pinned).

## v10.5 + v11.8 — 2026-07-24 — RE10140 FIX (input colors on plots = runtime series; the plot budget truth)

W-INDSTUDY lane (manifests `manifest_vob-v10.5-*` / `manifest_vob-v11.8-*`). Bases:
`VOB_v10.4.pine` / `VOB_v11.7.pine` @ `744637b`. **Impetus (operator screenshot
2026-07-24 00:53):** TV runtime error RE10140 — "The script creates too many plots (100).
The limit is 64" on the v10.4 paste.

### P-017 — THE DYNAMIC-COLOR PLOT-COST LAW (extends P-011)
- An `input.color`-driven `color`/`textcolor` arg on plotshape/plotchar is a runtime
  color SERIES: each one consumes a plot slot. The 28-input group pushed 56 -> 100+.
- Colors on plot*() calls must be BARE compile-time const literals (`#hex` /
  `color.name`) — zero plot cost.
- A bare const color is also exactly what makes the TV **Style-tab color picker**
  appear on a plot row; `color.new(...)` wrapping hides it. That hidden picker WAS
  the "no color choice" defect — the const fix delivers the choice natively.
- `input.color` on plot arguments is BANNED estate-wide (proposed gate axis A11).

### Files
- `versions/VOB_v10.5.pine` + `tick_friendly/VOB_TICKFRIENDLY_v10.5.pine`
- `versions/VOB_v11.8.pine` + `tick_friendly/VOB_TICKFRIENDLY_v11.8.pine`

### Changes
1. Detection Marker Colors input group REMOVED (both lineages).
2. Every plotshape color/textcolor -> bare const literal (the original palette:
   T3 tier hexes, lime/red composites, purple NAG, fuchsia NAG+ANY, etc.).
3. Operator's shape x location marker table (v10.4/v11.7 wave) preserved verbatim.
4. **Color choice = Settings -> Style -> swatch per plot row** (now visible).
5. v10.5 supersedes v10.4 (REFUTED by TV RE10140); v11.8 supersedes v11.7
   (same input-color pattern, fixed preemptively — it was never pasted).

## v10.4 + v11.7 — 2026-07-24 — VISUAL-IDENTITY FIX (operator screenshot = the standard)

W-INDSTUDY lane (manifests `manifest_vob-v10.4-*` / `manifest_vob-v11.7-*`). Bases:
`VOB_v10.3.pine` / `VOB_v11.6.pine` @ `2587859`. **Impetus (operator order
2026-07-24, screenshot-anchored):** the T3 12-pack painted identical circles
below/above bar — "visual information-free architecture" — and no detection plot
offered a color choice.

### THE VISUAL-IDENTITY LAW (vaulted; memory + lessons ledger)
- Distinct detection lanes may NEVER share (shape + location) such that
  same-candle fires stack indistinguishably.
- EVERY visual detection plot ships with its own `input.color`.
- The operator's Style-tab fix (screenshot 2026-07-24 00:17) is the canonical
  marker table — shipped as code defaults so it never needs hand-editing again.

### Files
- `versions/VOB_v10.4.pine` + `tick_friendly/VOB_TICKFRIENDLY_v10.4.pine` (28 color inputs)
- `versions/VOB_v11.7.pine` + `tick_friendly/VOB_TICKFRIENDLY_v11.7.pine` (18 color inputs)

### Changes
1. **v10 T3 spread (operator table, verbatim):**
   - Buy: a ○ top
   - Buy: b ○ bottom
   - Buy: c ○ abovebar
   - Buy: d ○ belowbar
   - Buy: e ▽ top
   - Buy: f △ bottom
   - Sell: a + top
   - Sell: b + bottom
   - Sell: c ✕ top
   - Sell: d ✕ bottom
   - Sell: e ✕ abovebar
   - Sell: f ✕ belowbar
   (v11 lineage carries no individual T3 markers — MULTIPLES host — table N/A there.)
2. **Nagasaki diamond → flag** (both lineages): kills the NAG / NAG+ANY
   same-glyph diamond/top collision.
3. **Multi-Zone 3+ spread** (both lineages): Bull 3+ → abovebar, Bear 3+ → belowbar.
4. **`Detection Marker Colors` input group** (both lineages): one `input.color` per plotshape,
   defaults = previous hardcoded colors; textcolor follows the marker input where
   it previously matched. Titles, texts, sizes, offsets, alert lanes untouched;
   TV unit budgets unchanged (56/64 and 36/64).

## v11.6 — 2026-07-24 — AGNOSTIC-LANE KILL (redundant direction-agnostic composites removed)

W-INDSTUDY lane (manifests `manifest_vob-v11.6-*`, gate exit 0 ×2). Base: `VOB_v11.5.pine`
@ `47b2446` (e4ed41c93025c2e7…). **Impetus (operator order 2026-07-24):** an agnostic
dp/vp/alert whose every fire candle ALWAYS carries a directional dp/vp is redundant
architecture — "how is that allowed."

### Files
- `versions/VOB_v11.6.pine` + `tick_friendly/VOB_TICKFRIENDLY_v11.6.pine`

### Changes (7 declared edits per variant)
1. **REMOVED: "T3 Cluster (2+ same candle)" (direction-agnostic)** — dp, vp,
   alertcondition, alert(), `show_tc_cluster`, `al_tc_cluster`, `last_tc_cluster`,
   `tc_fire_cnt`. Redundancy theorem: fired iff >=2 sided T3 sig lanes true on the
   same candle — each already a directional dp/vp. `tc_bull_cnt`/`tc_bear_cnt` kept
   (feed the side-typed clusters). Mixed 1+1 candles remain visible as their two
   sided T3 markers + `T3_CLUSTER_MIXED` in the NAG+ANY payload.
2. **REMOVED: "VOB × HW-Single Coincidence" (direction-agnostic)** — dp, vp,
   alertcondition, alert(), `show_vobhws`, `al_vobhws`, `last_vobhws`, `vob_tc_any`,
   `vob_left_side`. Redundancy theorem: sig == (bull OR bear constituents) AND
   hws_any == V×HW Bull OR V×HW Bear (side carried by the VOB constituent, E-1).
3. `any_sig_fired` / `bbp_armed` drop the dead terms — provable no-op for arming
   (`sig_tc_cluster ⟹ any_t3`, same disjunction); `TC,`/payload token now emitted
   only by the sided clusters (disclosed payload delta).
4. Budget: −2 text plotshapes (−4 TV units, P-011) · −2 alertconditions · −2 🔔
   checkboxes. Doctrine tightened (L-49.3): side_agnostic declarations are lawful
   for ATOMS only (Nagasaki, NAG+ANY) — never for composites of sided constituents.

## v10.3 + v11.5 — 2026-07-23 — ZONE LIFECYCLE telemetry + sensitivity tags (reticular-net session)

W-INDSTUDY lane under T-VOBPACK/T-INDSTUDY (manifests `manifest_vob-v10.3-*` / `manifest_vob-v11.5-*`,
gate v1.4 exit 0 ×4). Bases: `VOB_v10.2.pine` @ `b1e144a` and `VOB_v11.4.pine` @ `700b43e`.
**Impetus (operator reticular-net dictation, 2026-07-23):** (a) "Survivorship bias: I have no
idea when a line was drawn and when it was killed"; (b) "I have no idea which line is 100
sensitivity and which is 1,400 — there's just no graceful way to see this."

### Files
- `versions/VOB_v10.3.pine` + `tick_friendly/VOB_TICKFRIENDLY_v10.3.pine` (56/64 TV units)
- `versions/VOB_v11.5.pine` + `tick_friendly/VOB_TICKFRIENDLY_v11.5.pine` (40/64 TV units)

### Changes (9 declared edits per variant; identical intent across lineages)
1. **VOB_ZONEKILL emission — the survivorship fix.** Every zone death now emits
   (`T|SIDE|SENS|ZLO|ZHI|MID|ZVOL|BIRTH_T|AGE_MS|REASON|CLOSE`) at all three death
   paths inside f_vob: **BREACH** (close through boundary), **DEDUP** (newer zone
   within 3×ATR replaces older), **EVICT** (>15-zone FIFO drop). Confirmed-bar gated
   (intrabar provisional kills never emit). Paired with VOB_ZONEFORM births, zone
   LIFETIMES are complete on the log stream → survival analysis (Kaplan–Meier per
   sensitivity, hazard by age/distance) is computable with no chart access.
2. **Sensitivity tags — the line-identification fix.** Each drawn zone gets a boxless,
   zone-colored number tag (`label.style_none`, text = its sensitivity) at the zone
   midline, `sens_tag_off` bars right of the last bar. Toggle `show_sens_tags` (ON).
   Multiple stacked instances set different Tag Column offsets (e.g. 3/6/9/12) so a
   4-study reticular net reads as four clean columns. These are the operator-ordered
   tags ("that might be a time where a pane label would be helpful") — 4-character
   axis-style marks, NOT the killed metadata walls. Labels cost 0 TV plot units.

Verifiers: gate v1.4 PROVED ×4 (D_bytes=0; A10=0) · alert_iff_verifier PROVED ×4
(no alert-surface change) · anti-tamper 1→0 per lineage.
CORRECTION (LAW-CANDOR): earlier reports said v11.3/v11.4 = "62/64" — that figure was
call-site arithmetic; the measured TV-unit integer is **40/64** (cert A4_tv_plot_units).

## v11.4 — 2026-07-23 — P-012 FIX: the line-continuation refusal (supersedes v11.3)

W-INDSTUDY lane (manifests `manifest_vob-v11.4-{time,tick}_v11.4.json`, gate v1.4 exit 0).
Base = `versions/VOB_v11.2.pine` @ `5ba4cf5` (same base and same pack as v11.3). **Impetus
(operator screenshot 2026-07-23):** TradingView refused v11.3 — "Syntax error at input
'end of line without line continuation'" at the VOB_EMISSION statement. **Root cause
(P-012):** the v11 lineage wraps that statement with 6-space continuation lines; the
v11.3 edit appended `str.tostring(time)` as a NEW 8-space line — Pine refuses a wrapped
statement with MIXED continuation indents. (The v10 lineage is uniformly 8-space, which
is why v10.2 compiles-by-wrap and needed no fix.)

### Files (L-49.1 twin pair)
- `versions/VOB_v11.4.pine` — "VOB v11.4" (time build).
- `tick_friendly/VOB_TICKFRIENDLY_v11.4.pine` — "VOB v11.4 TICK-FRIENDLY", "V11.4 TICK".

### Change vs v11.3 (single defect fix; everything else byte-identical in intent)
- The `T:{34}` argument is appended ON THE SAME final continuation line
  (`..., str.tostring(time))`) — zero new continuation lines, wrap stays uniform 6-space.
- Enforcement: gate v1.4 axis **A10 WRAP-CONSISTENCY** (string-aware paren balance; a
  wrapped statement with mixed continuation indents is REFUSED). Founding refusal
  reproduced: v11.3 REFUTED at line 1345, indents [6, 8]; v10.2 and the live bases PASS.

Verifiers: gate v1.4 PROVED ×2 (D_bytes=0, 62/64 TV units, A10=0) · alert_iff_verifier
PROVED ×2 (45/45) · anti-tamper 1→0. v11.3 manifests remain as the honest REFUTED record.

## v10.2 — 2026-07-23 — P-011 BUDGET FIX + THE ALERT LAW ported from v11.2 (HW/HCT excluded)

W-INDSTUDY lane (manifests `manifest_vob-v10.2-{time,tick}_v10.2.json`, gate v1.3 exit 0).
Base = `versions/VOB_v10.1.pine` @ `9950c33` (sha256 `f7c998fa...`). **Impetus (operator
2026-07-23):** v10.1 REFUSED by TradingView at "78 plots > 64" — the P-011 counting law
(a plotshape with text = 2 TV units; alertconditions free; v10.1 = 39 text-shapes = 78;
gate v1.2's call-site counter said 54 = a false PASS, fixed in gate v1.3 which now
reproduces TV's 78 exactly) — plus "take the alert approach and the plot count approach
from v11.2; everything from v11.2 except the HCT thing."

### Files (L-49.1 twin pair, same base, same pack)
- `versions/VOB_v10.2.pine` — "VOB v10.2", shorttitle "VOB10.2" (time build).
- `tick_friendly/VOB_TICKFRIENDLY_v10.2.pine` — "VOB v10.2 TICK-FRIENDLY",
  shorttitle "V10.2 TICK" (A9 marker).

### v10.2 changes (25 declared edits, diff-derived; both variants share the pack)
1. **P-011 BUDGET FIX** — the 12 zone-marker plotshapes REMOVED (v11.2 plot-count
   approach; −24 TV units). Zones still draw as lines/fills; per-tier ZONE_FORM_X_BULL/
   BEAR alerts (12, each with its own 🔔) replace both the markers' info and the
   aggregate ZONE_FORMATION payload. **TV units: 28 text-plotshapes = 56/64** (was 78).
2. **THE ALERT LAW (v11.2) ported** — sig/show/al three-lane split for EVERY detection
   (13 T3/NAG + 12 zones + 2 VLB + 4 MZ + 8 pack + NAG+ANY): sig_X = criteria +
   confirmed + cooldown (stamps itself); plot_X = show_X and sig_X; **alert fires IFF
   its 🔔 checkbox is checked — display-independent**. 40 new al_ inputs (singles OFF,
   composites ON). alertconditions ride sig lanes.
3. **Composites re-based on SIG lanes** (v11.2 rule, display-independent): MZ counts,
   T3 Cluster counts, X3 pushes/prints, Failed Overlap, Birth-Bar-Proximity arming,
   VOB_TC/VOB_BBP log conditions, history pushes, cooldown stamps. Behavior delta vs
   v10.1: display toggles no longer suppress detection counting.
4. **NAGASAKI + ANY ported from v11.2 WITHOUT the HW/HCT apparatus** (operator
   exclusion: no HW-Single curves, no HCT displacement, no tv_ta import). Fires iff
   the ATH-volume candle carries ≥1 raw companion (T3/zone [1]); ANY: list names all;
   slim alert + BB block; offset −1 marker.
5. Slim alerts + BB block + emission lanes (ZONEFORM/X3_TEST/BBP/EMISSION2, T: keys)
   preserved from v10.1 unchanged.

Verifiers: indicator_study_gate v1.3 PROVED ×2 (D_bytes=0, tv_units 56/64) ·
alert_iff_verifier PROVED ×2 · anti-tamper 1→0. Supersedes v10.1 (REFUTED at 78).

## v11.3 — 2026-07-23 — v10.1 wave ported: pane-label kill + 6 pairs complete the 8-pack + T-ALERTMSG + birth-bar engine

W-INDSTUDY lane (manifests `manifest_vob-v11.3-{time,tick}_v11.3.json`, gate exit 0).
Base = `versions/VOB_v11.2.pine` @ `5ba4cf5` (sha256 `63377660...`; == the operator's
Desktop `vob v11.2.txt` after CRLF->LF + trailing-newline normalization — verified,
1-line diff). **Impetus (operator /goal 2026-07-23):** port the v10.1 wave onto v11.2.

### Files (L-49.1 twin pair, same base, same pack)
- `versions/VOB_v11.3.pine` — "VOB v11.3" (time build).
- `tick_friendly/VOB_TICKFRIENDLY_v11.3.pine` — "VOB v11.3 TICK-FRIENDLY", shorttitle
  "V11.3 TICK" (A9 marker).

### v11.3 changes (37 declared edits; both variants share the pack)
1. **PANE LABELS KILLED IN TOTALITY** — `f_emit_label` + 12 call sites and
   `en_emission_labels` REMOVED; `max_labels_count` arg dropped. Payload preserved as
   `VOB_ZONEFORM` log lines (+ ZLO/ZHI/BIRTH_T). Zero graphic-object labels remain.
2. **8-pack COMPLETE** — T3 Cluster Bull/Bear existed (v11.1); added the missing six:
   Tier Level X3 Bull/Bear (rolling last-3 common band, `x3_buffer` $0.05, no
   exclusion, `x3_cooldown` default 0), X3 Failed Overlap Bull/Bear (band empty =
   staircase read), Birth Bar Proximity Bull/Bear (`bbp_pct` 1.0%). All wired
   **sig/show/al** per THE ALERT LAW (alertcondition on sig; alert IFF checkbox;
   composites' checkboxes default ON). X3 pushes + BBP arming count SIG lanes
   (display-independent — v11.2 composite rule; note: v10.1 counts display-gated
   booleans — divergence recorded for the flagged v10 three-lane replication).
3. **T-ALERTMSG applied** — every alert() slimmed to the operator lane + the birth
   block `BB_BULL:price(pct%)|BB_BEAR:price(pct%)|CLOSER|EMANATE`; EXCHANGE dropped
   everywhere (22-line mechanical sweep); fat payloads (T3 Bloomberg wall, VLB
   per-tier OHLCV, MZ context, legacy T3_CLUSTER context, NAG_ATH RSI/SESS) moved to
   log mirrors (`VLB_*_DATA`, `MZ_*_DATA`). NOTHING IS ALERT-ONLY (join key `T:`
   epoch-ms added to `VOB_EMISSION` + every event line). Three-lane iff law PRESERVED.
4. **Birth-bar engine** — nearest-active reference per side (bull=z.lower,
   bear=z.upper, D4 birth law); EMANATE = latest-birth side (tie -> BULL).
5. **T-METALEARN emission** — `VOB_X3_TEST` (M_ZONE/M_CANDLE/M_ORIGIN margins per
   test: the range-definition race dataset), `VOB_BBP`, `VOB_EMISSION2` per bar.

Output budget: **40/64** (was 28/64; +6 plotshapes +6 alertconditions).
Non-repaint: all new sigs barstate.isconfirmed-gated; parity via single sig boolean.

## v11.2 — 2026-07-22 — THE ALERT LAW: alert-display decoupling + 🔔 ALERTS section

**Impetus (operator dictation 2026-07-22):** "I cannot understand when I will get an
alert and when I will not get an alert… I want separate checkboxes for each dp/vp
with a clear alert checkbox section… iff checked → alert fires, independent of the
visual." Charge CONFIRMED: pre-v11.2, display checkboxes were silently welded to the
alert stream (a hidden T3 tier could never alert; composites counted only displayed
constituents).

### THE ARCHITECTURE (the how — transferable to VOB v10 / VOB Asymmetric)
One signal lane per dp/vp, two independent taps:
```
sig_X  = dp criteria + confirmed bar + shared cooldown   // stamps its OWN cooldown, always
plot_X = show_X and sig_X                                // chart tap  (display checkboxes)
alert fires iff:  al_X and sig_X                         // inbox tap  (🔔 ALERTS section)
```
**Recipe to replicate in any VOB study:** per dp/vp, (1) declare `al_X` in the 🔔
group, (2) split `sig_X` out of the old `plot_X` definition, (3) gate every
`alert()` with `al_X and sig_X`, (4) run
`python3 validation/wrappers/alert_iff_verifier.py <file>` — exit 0 proves the law
structurally (T1–T6: every alert al-gated, no display token in any alert gate, no
alert token in any plot, pure signal lanes, no dead checkboxes, default census).

### Files (L-49.1 twin pair, base = VOB_OPERATOR_HOST_v11.pine @ 58ccd59)
- `tick_friendly/VOB_TICKFRIENDLY_v11.2.pine` — "VOB v11.2 TICK-FRIENDLY" / "V11.2 TICK"
- `versions/VOB_v11.2.pine` — "VOB v11.2" / "VOB v11.2"

### 🔔 ALERTS section census — 39 checkboxes (one per alert-bearing dp/vp)
| family | checkboxes | default |
|---|---|---|
| T3a–f Buy/Sell (12) · Nagasaki (1) · Zone A–F Bull/Bear formation (12, NEW individual alerts) · Zone aggregate (1) | 26 singles | **OFF** |
| VLB Bull/Bear (2) · Multi-Zone 2/3+ ×2 sides (4) · T3 Cluster agnostic/Bull/Bear (3) · V×HW agnostic/Bull/Bear (3) · NAG+ANY (1) | 13 composites | **ON** |

### Behavior changes vs v11.1 (each deliberate, all disclosed)
| surface | before (v11/v11.1) | after (v11.2) |
|---|---|---|
| T3/zone/NAG/VLB/MZ alerts | fired only if the DISPLAY toggle was on | fire iff the 🔔 checkbox is on — display irrelevant |
| Individual zone alerts | did not exist (aggregate only) | 12 per-tier `ZONE_FORM_<T>_<SIDE>` alerts (alert-tap only, no new plots) |
| Composites (clusters, MZ, V×HW) | counted DISPLAY-gated constituents | count SIG lanes — hiding singles can't starve composites |
| Cooldown stamping | stamped only when displayed | stamps on every raw signal (consistent lanes) |
| alertcondition() channel | read display-gated booleans | reads sig lanes (TV-native, opt-in per dialog) |

Output census unchanged: 14 plotshapes + 14 alertconditions = 28/64 (alert() calls
and inputs don't count). Proof artifacts: `alert_iff_verifier.py` PROVED ×2 + anti
2/2 CAUGHT · W-INDSTUDY manifests `manifest_vob-v11.2-{tick,time}_v11.2.json`.
Both v11.2 files include VOB_TICKFRIENDLY_v11.2.pine and VOB_v11.2.pine names here
for the A5 markers.

## v10.1 — 2026-07-22 — Pane-label kill + 8 sided dp/vp pairs + slim-alert law + birth-bar engine

W-INDSTUDY lane (L-49; manifests `manifest_vob-v10.1-{time,tick}_v10.1.json`, gate
`indicator_study_gate.py` exit 0). Base = the operator's live Desktop host copy
(`vob v10.txt`, CRLF sha256 `7f67e252...efe55d46`), intaken CRLF->LF as
`versions/VOB_OPERATOR_HOST_v10.pine` (LF sha256 `79873843...1db94011`, commit `d743184`). **Impetus (operator dictation
2026-07-22, five-questions session):** the BULL/BEAR pane labels obstruct the
chart in totality ("I don't want it — get rid of it"); v10 lacked sided T3
clusters; and three new detection families were dictated (Tier Level X3,
X3 Failed Overlap, Birth Bar Proximity) plus a slim human-alert law with a
birth-bar distance block.

### Files (L-49.1 twin pair, same base, same pack)
- `versions/VOB_v10.1.pine` — title "VOB v10.1", shorttitle "VOB10.1" (time build).
- `tick_friendly/VOB_TICKFRIENDLY_v10.1.pine` — title "VOB v10.1 TICK-FRIENDLY",
  shorttitle "V10.1 TICK" (A9 tick marker; base is rolling-window tick-safe).

### v10.1 changes (17 declared edits vs base; both variants share the pack)
1. **PANE LABELS KILLED IN TOTALITY** — the single `label.new()` constructor
   (`f_emit_label`, base L1047-1053) and all 12 call sites REMOVED; the
   `en_emission_labels` input and `max_labels_count` declaration arg removed.
   Zero graphic-object labels remain: the TV graphic-objects toggle has nothing
   left to show for this study. Payload PRESERVED as `VOB_ZONEFORM` log.info
   lines (same fields + ZLO/ZHI/BIRTH_T zone geometry), gated by
   `en_emission_logs` — emission data, not graphic objects (operator order).
2. **T3 Cluster Bull / Bear** — 2+ same-side T3 prints on one candle (the {T1,T2,T3}
   tier family degenerates to T3a-F in v10.1; alert lists each member with its
   class: `TIERS:T3-A(2500),T3-C(2000),`). Shared `cooldown_bars`.
3. **Tier Level X3 Bull / Bear** — TRUE rolling window over the last 3 same-side
   tier prints (unbounded age, NO exclusion after a fire: the 4th/5th/6th print
   at the level re-fires). Overlap = COMMON BAND: max(lows) <= min(highs) + buffer
   (`x3_buffer`, default $0.05; touching counts). Binding range = dominant-zone
   bounds; fire-candle and origin-swing-bar ranges were considered, rejected, and
   are EMITTED per test (M_ZONE/M_CANDLE/M_ORIGIN in `VOB_X3_TEST`) so the
   binding definition is empirically re-decidable (T-METALEARN loop).
4. **X3 Failed Overlap Bull / Bear** — the test RAN (3 prints in memory, new print
   landed) and the common band is EMPTY: the staircase/diagonal formation
   (institutional one-way-flow read). `GAP:` in the alert = shortfall dollars.
5. **Birth Bar Proximity Bull / Bear** — any vp fired while close is within
   `bbp_pct` (default 1.0%) of the nearest ACTIVE birth level on that side.
6. **Birth-bar reference engine** — birth level law (D4, ProofTEMVOB10BirthBars):
   bullish zone birth = zone.lower, bearish = zone.upper; per side THE reference =
   nearest active (actionability law); EMANATE = side of the latest active birth
   (flips only on opposite-side birth or full invalidation; tie -> BULL).
7. **SLIM-ALERT LAW (operator 2026-07-22)** — every alert() is the OPERATOR lane:
   event id, DIR/TIER/SENS, VOL/POOL where relevant, CLOSE, plus the birth block
   `BB_BULL:price(pct%)|BB_BEAR:price(pct%)|CLOSER:x|EMANATE:y`. RSI/SESS/SLOPE/
   VOLRANK/stacks/gaps/EXCHANGE and the VLB per-tier OHLCV wall moved to log.info
   mirrors (`VLB_*_DATA`, `MZ_*_DATA`). NOTHING IS ALERT-ONLY: every dropped field
   lives on the log stream, joined by `T:` (epoch-ms bar time, added to
   `VOB_EMISSION` and every event line).
8. **Emission layer v2** — `VOB_EMISSION2` per-bar line (birth geometry, X3 memory
   state, cluster counts); `VOB_TC`/`VOB_BBP` event lines.

Output budget: 39 plotshapes + 15 alertconditions = **54/64** (was 38/64).
Non-repaint law: every new dp is barstate.isconfirmed-gated with 1:1 plot/alert
parity off a single boolean. X3/FO cooldown = `x3_cooldown` (default 0 by
operator rolling-window law); TC/BBP share `cooldown_bars`.

## v11.1 — 2026-07-22 — Bull/Bear T3 Cluster + Bull/Bear V×HW + NAGASAKI+ANY

> **NAMING LAW (operator-dictated 2026-07-22, same session):** the VOB family names are
> FROZEN — **VOB v10, VOB v11, VOB Asymmetric** — until the operator declares better
> nomenclature. New versions bump the MINOR number only (v11.1, v11.2, …); a major bump
> is REFUSED. This release first shipped mis-named "v12"; the operator revoked that name
> within the hour and it was renamed v11.1 (the v12 files/manifests were removed; dated
> rows in INDSTUDY_DEBTS.json are the record).

W-INDSTUDY lane (L-49; manifests `manifest_vob-v11.1-{tick,time}_v11.1.json`, gate
`indicator_study_gate.py` exit 0). Base = the operator's live Desktop host copy
(`vob v11.txt`), intaken CRLF→LF as `versions/VOB_OPERATOR_HOST_v11.pine`
(sha256 `f35668a0…121c4756`, commit `58ccd59`) — chosen over the stripped
mirror MULTIPLES because it carries the individual T3/zone/Nagasaki VPs and
toggles the operator's asks reference. **Impetus (operator dictation
2026-07-22):** the study had no bullish/bearish T3 cluster and no dedicated
bull/bear V×HW coincidence VPs, and no Nagasaki-plus-companion detection whose
alert states what the companion is.

### Files (L-49.1 twin pair, same base, same pack)
- `tick_friendly/VOB_TICKFRIENDLY_v11.1.pine` — title "VOB v11.1 TICK-FRIENDLY",
  shorttitle "V11.1 TICK" (A9 tick marker; TV shorttitle law ≤10 chars).
- `versions/VOB_v11.1.pine` — title "VOB v11.1", shorttitle "VOB v11.1" (time build;
  v11 tick guards remain — semantic no-ops on time charts).

### New in v11.1 (appended pack; exactly 2 declared edits vs base)
1. **T3 Cluster Bull / T3 Cluster Bear** — dedicated sided VPs: 2+ same-side T3
   tiers on one candle (flag below/above bar, lime/red, `T3x↑`/`T3x↓`), each with
   its own cooldown, alertcondition, and Bloomberg `alert()` naming the tiers.
   The v11 direction-agnostic T3 Cluster is unchanged and can co-fire.
2. **VOB × HW-Single Coincidence Bull / Bear** — side carried by the VOB
   constituent (bull vs bear T3/zone leg); HWS side disclosed in the payload
   (`HWS:` field). v11 agnostic coincidence unchanged.
3. **NAGASAKI + ANY** (`NAG+`, fuchsia diamond, offset −1 onto the NAG candle) —
   fires iff the all-time-high-volume candle also carries ≥1 companion dp/vp.
   RAW-signal counting law (operator-dictated): visibility toggles and cooldowns
   never affect counting — an untoggled T3/zone still COUNTS iff it is on the NAG
   candle. The `alert()` payload's `ANY:` field names every companion
   (T3A_BUY…T3F_SELL, ZONE_A_BULL…ZONE_F_BEAR, VLB_BULL/BEAR, MZ_BULL/BEAR_2/3PLUS,
   T3_CLUSTER_BULL/BEAR/MIXED, VOBXHWS_BULL/BEAR) + `HWS_CTX:` context + `REFBAR:-1`.
   Fire-condition reduction theorem: every composite companion implies a raw T3 or
   zone signal, so fire ⟺ NAG ∧ (raw T3[1] ∨ raw zone[1]).

Output census v11.1: 14 plotshapes + 14 alertconditions = 28/64.

## VOB v11 — HW-Single Coincidence + T3 Cluster — 2026-06-04

Two new files (NOT replacing v10). Built on the v10 body. **Host bumped to
`//@version=6` by explicit in-session instruction from Anish** (the suite-wide
"v5 only" default was waived for this build after a smoke test proved
`import TradingView/ta/7` + `relativeVolume()` compiles clean under v6).

### Files
- `versions/VOB_v11_FULL_HWcoincidence_2026-06-04.pine` — keeps ALL v10 visuals
  (individual T3 circles + zA..zF zone crosses + zone lines/fills + VLB + MZ),
  PLUS the two new detections.
- `versions/VOB_v11_MULTIPLES_HWcoincidence_2026-06-04.pine` — "multiples only":
  the 12 individual T3 circles and the 12 individual zone-formation crosses are
  commented out (`// [v11 MULTIPLES-ONLY removed]`). KEEPS the drawn zone
  lines/fills, Nagasaki, VLB, MZ2/MZ3, and both new detections. Chart shows only
  confluence/composite events.

### New detection #1 — T3 Cluster (`T3x`, yellow flag, top)
Fires when **2+ of the six T3 tiers** (T3a..T3f, buy OR sell) paint on the SAME
candle. Direction-agnostic — two bulls, two bears, or a bull+bear mix all count.
One plot + alertcondition + Bloomberg `alert()`. Non-repainting, cooldown-gated.

### New detection #2 — VOB × HW-Single Coincidence (`V×HW`, magenta label, top)
Fires when ANY VOB T3 or ANY VOB zone-formation marker (either direction)
coincides on the SAME candle with ANY Heavy Weapons Single v3 detection (high
volume, displacement, RVOL, sequence, B2B, FAUNA, HCT, Pentagon, HV).
**HW Single v3 itself is NOT modified** — its detection math is embedded
READ-ONLY (group "HW Single v3 Engine (embedded — read-only)"), visuals stripped,
collapsed to a single `hws_any` boolean. One plot + alertcondition + Bloomberg
`alert()`. Non-repainting, cooldown-gated.

### Verification
- Append block (HWS engine + both detections) compiles under v6: 0 errors,
  3 advisory warnings (pre-existing HWS `ta.*`-in-conditional patterns).
- v10 body scanned for v5→v6 breaking constructs: none present.

# VOB Indicator Suite — Changelog

## VOB_Asym_T3x6_MutEx_Claude_v9_2026-05-12.pine — v9.1 patch — 2026-05-12

Adds the "Wrong-Way 3" family + makes every v9 detection non-repainting
with 1:1 alert parity. Same file as v9, indicator() title bumped to v9.1
to mark the patch.

New Wrong-Way 3 detection:
- **Wrong-Way 3 Bear** (`WW↑` yellow xcross below bar) — Three consecutive
  bear-zone tiers ASCENDING against the expected descent. Slides any
  window of 3 (F-E-D / E-D-C / D-C-B / C-B-A); if any window shows
  three bear zones rising in price beyond the tolerance percent,
  fire. Bears are losing structure → potential reversal.
- **Wrong-Way 3 Bull** (`WW↓` orange xcross above bar) — Three
  consecutive bull-zone tiers DESCENDING against the expected ascent.
  Same window logic. Bulls are losing structure → potential reversal.
- Tolerance reused from Ladder Tolerance %; deviation must EXCEED
  tolerance to count, so noise doesn't trigger.

Non-repainting + 1:1 parity:
- Every v9 plot_* boolean (Ladder, Ladder+Gap, Adjacent, Wrong-Way) is
  now gated by `barstate.isconfirmed` — visual paint only on confirmed
  bar close.
- All `alert()` calls use `alert.freq_once_per_bar_close` — alert fires
  on the same boundary as the plot.
- The visual plotshape and the alert fire on the SAME boolean, so what
  you see on the chart matches what you get in the inbox.

The new "Any Checked Detection" alertcondition is renamed to "Any
Checked Detection (v9.1)" and now includes plot_ww_bull / plot_ww_bear.

## VOB_Asym_T3x6_MutEx_Claude_v9_2026-05-12.pine — v9 — 2026-05-12

Three new detection plots + one consolidated "any checked detection"
alertcondition. Defaults rebased to Anish's current per-screenshot
preference set.

New detections (Layer 3):
- **Bull Ladder** — all 6 tier wick lows ascending F→A within a
  tolerance percent (default 0.3%). Plots an `L↑` flag below bar.
- **Bear Ladder** — all 6 tier wick highs descending F→A within
  tolerance. Plots `L↓` flag above bar.
- **Bull Ladder + Gap Up** — bull ladder valid AND current bar opens
  ≥ gap-threshold percent above prior close. Plots `LG↑` triangle.
- **Bear Ladder + Gap Down** — bear ladder valid AND current bar
  opens ≥ gap-threshold percent below prior close. Plots `LG↓`.
- **Adjacent Bull/Bear** — same-tier bull AND bear zones formed
  within a bar window (default 25). Plots `ADJ` diamond on the bar
  the second one fires. Aggregates across all six tiers.

Structured inputs (all editable in the UI):
- Ladder Tolerance % (default 0.3)
- Ladder Gap Threshold % (default 0.5)
- Adjacent Bar Window (default 25)
- Per-detection show/hide checkboxes

Alert behavior:
- New `alertcondition("Any Checked Detection (v9)", ...)` fires when
  ANY checkbox-enabled detection (existing T3a-T3f + Nagasaki + new
  ladder/gap/adjacent) fires this bar. Unchecking a detection in the
  UI silences it in this alert.
- Per-detection `alert()` payloads are pipe-delimited Bloomberg-style
  with all six sensitivity values stamped in every message, plus
  per-tier zone prices, gap %, stack counts, RSI, vol rank, session
  bar, and the actual tolerance/window settings — usable for
  database cataloging and downstream ML.

Defaults updated:
- sens_a 2500→850, sens_b 2250→750, sens_c 2000→650,
  sens_d 1500→550, sens_e 1250→450, sens_f 1000→350
- asym_threshold 99→100, super_mult 1.5→1.0

Plot budget: 25 plotshapes + 5 new plotshapes + 3 alertconditions = 33
outputs (well under the 64 limit). Existing alerts ("Any T3 Signal or
Nagasaki", "Any Zone Formation") preserved so TV alerts already set up
do not break.

## VOB_LADDER_WATCH_v1.pine — 2026-05-04

Initial. Companion indicator to VOB Asym T3 ×6.

Implements Anish's "zF then zE then zD..." ascending-ladder thesis as
running code. Six-tier bull-zone engine (mirrors VOB Asym T3 logic but
bull-only, no T3/MutEx). Tracks the most recent active bull zone per
tier, then evaluates the strict ascending sequence F→E→D→C→B→A.

Output:
- Ladder depth (0-6) gauge in top-right table
- Per-tier zone price in same table
- Plotshape labels on each escalation: WATCH (depth 2), TIER3, TIER4,
  TIER5, FULL (depth 6 = all 6 ascending)
- alertcondition + alert() per escalation tier — for tomorrow's session,
  set TV alerts using "Any alert() function call" so each escalation
  pushes a notification

Rationale: per Anish's screenshot review of DDOG run from $110 on
Apr 14, the staged ladder formation is itself the trend confirmation;
question is entry timing. Watch state at depth 2 is "put it on radar";
depth ≥3 with PBJ/RVOL confirmation = consider entry.
## v10.7 — 2026-08-10 (machine-feed checkbox wave; operator defect report, W-INDSTUDY transform)

**VOB Asym COMBO v10.7** (time; base = v10.5 @ 3228671, the build the operator runs).

- **DEFECT (operator screenshots 2026-08-10):** v10.5 carried exactly ONE alert() emitter
  with no checkbox — the aggregate Bloomberg-format **ZONE_FORMATION** machine alert
  (`if any_zone`). An operator alert armed on **"Any alert() function call"** received every
  zone birth (tiers A-F, both sides, post-cooldown) regardless of every ALERTS checkbox —
  the checkboxes were never wrong; the emitter had no checkbox.
- **FIX:** new ALERTS-group row `al_zone_machine` — "Alert: Machine Zone Feed (ZONE_FORMATION)",
  **DEFAULT OFF** — gating that emitter. The checkbox law now covers 21/21 alert() emitters.
- v10.6 (parallel WILD wave) carries the same orphan emitter — same fix owed on that line.
- Reminder shipped with delivery: TV alerts are frozen snapshots — delete the old alert and
  re-create it on v10.7 or the old spam keeps firing.
