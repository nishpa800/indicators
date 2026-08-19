# VOB Indicator Suite — Changelog

## VOB ASYM HVPROX v1.3 — 2026-08-19 (Volume Order Blocks + Asymmetric Signals + HV Proximity v1.3) — SUPERSEDES v1.2
- **Operator orders 2026-08-19 (after v1.2):** (1) COLOR CHOICE — his TV shows no color control for bare-const plotshape colors (P-017 "bare literal shows the picker" REFUTED on his screen, PROBLEM_LOG P-044): every one of the 18 markers now has an **input.color swatch next to its plot checkbox** (Inputs → VISUAL PLOTS, E5). (2) **ALERT LINE = `BULL/BEAR, HV#, Disp #.#, RVOL #.#` — nothing else**: side = tier side; HV token HV500…HV4000 / NAGA; Disp = the HV candle ACHIEVED displacement sigma (one decimal, `0.0` format; Open-to-Close body / stdev 100, editable); RVOL = the HV candle Reg@Time relative-volume ratio (`import TradingView/ta/12`, relativeVolume 30 periods, cumulative, adjust realtime, tick-safe anchor remap to D). Tier name / gap / close / vol / bar → log.info only. (3) L-70 LAW-COPY-URL enacted the same wave.
- Files: `versions/VOB_ASYM_HVPROX_v1.3.pine` (TIME, shorttitle `VOB HVP1.3`) + `tick_friendly/VOB_ASYM_HVPROX_TICKFRIENDLY_v1.3.pine` (TICK, `HVP1.3TICK`) — byte-identical below the indicator() line except the shorttitle tag inside the 12 log.info metadata lines. Base = the operator's `vob asymmetric signals.txt` (sha256 `5a1f0ced07dd…`, hosted in `vob/sources/`).
- Unchanged from v1.2: HV tiers FIXED (500/1000/1500/3000/4000, Nagasaki all-time high); the only proximity inputs are the bars-from-T1/T2/T3 distances (3/5/5/5/5/15); print-highest toggle; 12 lanes × sig_/fire_/alf_; all 18 marker shape+location = his Style-tab defaults; base edits E1–E4.
- Budget: 39/64 under the proven 2026-08-12 law (18 plotshapes × (1 + 1 input.color) + 2 fill-anchor plot() + 1 series-color fill); ≤ 57/64 under the older text-×2 reading. 0 alertcondition. NOT TV-compiled (ban) — first paste settles the input-color unit cost and the tick-chart RVOL behavior (disclosed in the tick header).
- Rigor R2: every numeric default is operator-dictated or estate-canonical (RVOL 30 / Reg@Time / cumulative; Disp len 100 body).

## VOB ASYM HVPROX v1.2 — 2026-08-18 (Volume Order Blocks + Asymmetric Signals + HV Proximity v1.2) — SUPERSEDES v1.1
- **Operator clarification (same day, minutes after v1.1): "there are no rolling windows, just the number of bars away from T1/T2/T3."** v1.2 = v1.1 with the five HV-lookback INPUT rows removed (HV tiers FIXED as constants 500/1000/1500/3000/4000; Nagasaki = all-time high) and the distance rows relabeled **"HV N — bars from T1/T2/T3"** (defaults 3/5/5/5/5/15, still adjustable). Lane logic, plots, alerts, checkboxes: unchanged bytes apart from the input block and the header text. v1.1 stays on disk as history; **use v1.2**.
- `versions/VOB_ASYM_HVPROX_v1.2.pine` (TIME, shorttitle `VOB HVP1.2`) + `tick_friendly/VOB_ASYM_HVPROX_TICKFRIENDLY_v1.2.pine` (TICK, `HVP1.2TICK`) — byte-identical below the indicator() line except the shorttitle tag inside the 12 log.info metadata lines. Base = the operator's `vob asymmetric signals.txt` (sha256 `5a1f0ced07dd…`).
- Operator goal 2026-08-18: **IFF** an HV candle (500/1000/1500/3000/4000-bar high, or Nagasaki) sits within K bars of a T1/T2/T3 fire (either tier), then and only then the VP fires; K = **3/5/5/5/5/15 bars**, adjustable.
- 12 lanes = {HV 500, HV 1000, HV 1500, HV 3000, HV 4000, NAGASAKI} × {Bull (T1/T2/T3 BUY), Bear (T1/T2/T3 SELL)}; each a sig_/fire_/alf_ chain: real plotshape VP + plot checkbox + 🔔 alert checkbox + alert() (grammar v1.3 plain names) + log.info metadata. Print-highest-tier rule default ON (toggle).
- HV(N) = `volume >= ta.highest(volume, N)` with N fixed (ties count); NAGASAKI = running all-time max over confirmed candles, strict >; proximity = later-of-the-two candle, distance ≤ K (0 = same candle); everything evaluated on the confirmed bar (non-repainting, same as the base engine).
- Base edits (behavior of T1/T2/T3 unchanged at defaults): E1 indicator title/shorttitle stamped; E2 tier plot keys side-typed "(Bull)/(Bear)", bare const colors, white text, T3 SUPER Buy yellow→green #64DD17 (yellow banned); E3 math.min clamps on the OB scan-loop offsets; E4 tier lanes get plot + 🔔 alert checkboxes (default ON).
- Budget: 21/64 TV units (6 base tier + 2 fill-anchor plot() + 1 series-color fill + 12 new, plot colors all bare const); 0 alertcondition; graphic objects = the base's order-block lines/labels only.
- Base hosted verbatim in `vob/sources/VOB_ASYM_SIGNALS_operator-base_2026-08-18.txt` (sha256 `5a1f0ced07dd…`, T-INDSTUDY C12).
- Rigor R2: every numeric default is operator-dictated; base carried verbatim (sha-pinned).

## VOB ASYM HVPROX v1.1 — 2026-08-18 (Volume Order Blocks + Asymmetric Signals + HV Proximity v1.1)
- **NEW STUDY PAIR (create lane) on the operator's `vob asymmetric signals.txt` base (sha256 `5a1f0ced07dd…`).** `versions/VOB_ASYM_HVPROX_v1.1.pine` (TIME, shorttitle `VOB HVP1.1`) + `tick_friendly/VOB_ASYM_HVPROX_TICKFRIENDLY_v1.1.pine` (TICK, `HVP1.1TICK`) — byte-identical below the indicator() line except the shorttitle tag inside the 12 log.info metadata lines.
- Operator goal 2026-08-18: HV proximity VPs, adjustable rolling windows + adjustable bar distances; **IFF** an HV candle sits within K bars of a T1/T2/T3 fire (either tier), then and only then the VP fires. Defaults **500/1000/1500/3000/4000/Nagasaki** with **3/5/5/5/5/15 bars**.
- 12 lanes = {HV 500, HV 1000, HV 1500, HV 3000, HV 4000, NAGASAKI} × {Bull (T1/T2/T3 BUY), Bear (T1/T2/T3 SELL)}; each a sig_/fire_/alf_ chain: real plotshape VP + plot checkbox + 🔔 alert checkbox + alert() (grammar v1.3 plain names) + log.info metadata. Print-highest-tier rule default ON (toggle).
- HV(N) = `volume >= ta.highest(volume, N)` (rolling; ties count); NAGASAKI = running all-time max over confirmed candles, strict >; proximity = later-of-the-two candle, distance ≤ K (0 = same candle); everything evaluated on the confirmed bar (non-repainting, same as the base engine).
- Base edits (behavior of T1/T2/T3 unchanged at defaults): E1 indicator title/shorttitle stamped; E2 tier plot keys side-typed "(Bull)/(Bear)", bare const colors, white text, T3 SUPER Buy yellow→green #64DD17 (yellow banned); E3 math.min clamps on the OB scan-loop offsets; E4 tier lanes get plot + 🔔 alert checkboxes (default ON).
- Budget: 21/64 TV units (6 base tier + 2 fill-anchor plot() + 1 series-color fill + 12 new, plot colors all bare const); 0 alertcondition; graphic objects = the base's order-block lines/labels only.
- Base hosted verbatim in `vob/sources/VOB_ASYM_SIGNALS_operator-base_2026-08-18.txt` (sha256 `5a1f0ced07dd…`, T-INDSTUDY C12).
- Rigor R2: every numeric default is operator-dictated; base carried verbatim (sha-pinned).

## VOB v11.9 — KEEPER CUT + v11.9 PACK — 2026-08-11

Base: operator Desktop live copy `vob v11.8.txt`
(sha256 `a68809d1a5d986b07c8f9213fa153cf8495d386ca968e3f9c4c5cae6e99b4ae0`).
Operator .rtfd order 2026-08-11.

- **KEEPERS (only lanes with checkbox + vp + alert; all 26 🔔 default ON):**
  Nagasaki · VLB Bull/Bear · Multi-Zone Bull2/Bull3+/Bear2/Bear3+ · T3 Cluster
  Bull/Bear · VOB × HW-Single Bull/Bear · Nagasaki + ANY vob v11.9 (renamed) ·
  Tier Level X3 Bull/Bear · X3 Failed Overlap Bull/Bear · Birth Bar Proximity Bull/Bear.
- **CALCULATORS (compute-only; checkbox/vp/alert REMOVED):** T3 a–f Buy/Sell ×12,
  zone-formation alerts ×12 + aggregate, Zone Lines toggles ×6 (zone LINES now
  always-on), "Any T3"/"Any Zone Formation" alertconditions. Calculators still
  compute and count as companions in every +ANY lane.
- **NEW (8):** Pack Co-Fire Bull/Bear (exactly 2 of TC/X3/FO/BBP; X3⊥FO ⇒ 4-of-4
  impossible) · Pack 3-of-4 Bull/Bear (the max) · 4K/3K/2K/1K HV + ANY vob v11.9
  (rolling highest-vol windows, NAG+ANY construction, REFBAR:-1, exclusivity
  ladder NAG > 4K > 3K > 2K > 1K).
- **DEFAULTS BAKED (operator screenshots):** sens 1900/1800/1700/1600/1500/1400 ·
  asym 50 · super 0.5 · cooldown 30 · X3 buffer $0 · fill 75 · midline 1 · tag
  col 100 · stacking 1% · history 30 · HWS floors 62/62, body 80, seq lowers
  2/2/2, standalone σ7, HCT σ5.
- **CENSUS:** 26 lanes = 26 plotshapes (52/64 TV units) + 24 alertconditions +
  26 show + 26 🔔 checkboxes; alert-iff law intact. Acceptance gate D=0
  (census/banned-surface/iff/defaults/twin-parity axes).
- Files: `versions/VOB_v11.9.pine` (TIME) + `tick_friendly/VOB_TICKFRIENDLY_v11.9.pine` (TICK twin).

## VOB Asym COMBO v10.6 — Birth Confluence + BB1 Continuation — 2026-08-07

`versions/VOB_ASYM_COMBO_v10.6.pine` — TIME chart original. Supersedes v10.5
(same day). Operator dictation #2: births were never deleted (per-birth markers
went in v10.1 combo-only; v10.5 removed births from TIER alert member lists per
the tiers-are-not-zones order) — v10.6 adds the lanes the operator wants ON TOP:

- **WILD Confluence Bull/Bear**: ≥1 zone birth AND (Tiers 3+ OR exact-price
  Level count ≥2) on the SAME candle. The one lane family where births and
  tiers meet on purpose; the alert names BOTH classes.
- **Continuation Bull/Bear (VOB BB1 line doctrine, native port)**: BB1's
  "line drawn" event IS a zone birth (birth = line at EMA-crossover confirm).
  Bull: most recent BEAR birth ≤ cont_window (500) bars ago is the reference
  (newer bear birth resets it; A→F processing → F kept on multi-birth candles);
  firing close ABOVE that bear zone's top AND above the birth bar's close;
  THIS candle a BULL birth draws its green line. Bear mirror. Alert reports
  level distance in ATR units; ≤1 ATR = SAME-LEVEL (the BB echo band).
  Same-candle opposite births never fire (sequence ≥1 bar).
- Census: 32 lanes = 24 plotshapes (text) + 6 plotchars (text) + 2 plotchars
  (no text) = 62/64 units; 32 alertconditions; 72 input.bools, 0 dead;
  checkbox law maintained (32 Plot + 32 Alert rows). Census gate D=0
  (12 axes, anti-fixture pass; WILD family exempted by operator order from
  the tier-purity member rule — both classes lawfully named there).
  NOT TV-compiled (TV ban) — paste settles. Tick twin owed (dated debt).

## VOB Asym COMBO v10.5 — Checkbox Law · Tier Purity · Stepwise HV — 2026-08-07

`versions/VOB_ASYM_COMBO_v10.5.pine` — TIME chart original. Supersedes v10.4.
Repairs the operator's v10.2 Desktop working file per dictation 2026-08-07.

- **CHECKBOX LAW**: every detection lane has TWO checkboxes in two mirrored
  groups — "VISUAL PLOTS (chart markers only)" and "ALERTS (inbox only)".
  A Plot box never touches alerts; an Alert box never touches the chart.
  The 13 dead v10.1 toggles (12 T3x Buy/Sell + Nagasaki) are deleted.
  Zone Lines boxes gate line drawing ONLY (were silently gating Multi-Zone
  counts / ANY unions / histories). Detection booleans are checkbox-free;
  cooldown stamps on the detection itself.
- **TIER PURITY**: zone births removed from every tier surface. TIERS and
  LEVEL alerts name tier members only (new f_tier_members_bull/bear, zero
  zone terms). Zone births count ONLY in 4K + ANY and Nagasaki + ANY, whose
  labels say "(tier OR zone birth)".
- **STEPWISE HV (6 new lanes, bull + bear)**: three consecutive stepwise
  closes; strict 2K→3K→4K high-volume-record ladder / any-depth ×3 /
  +Nagasaki (≥1 of the three candles is the all-time-high volume event).
  New windows n_2k (2000) / n_3k (3000); plotchar glyphs L / Y / N.
- **v10.4 LEVEL-DISTINCTNESS ported**: level entries are DISTINCT
  (tier-class, sensitivity) pairs at an exact price (f_push_lvl verbatim).
- Census: 28 lanes = 22 plotshapes + 6 plotchars (all with text) = 56/64
  units; 28 alertconditions; 64 input.bools, 0 dead. Gates: census D=0
  (12 axes, anti-fixture 5/5) + pane-label D_cs1=0; 168 examples
  adversarially verified. NOT TV-compiled (TV ban) — paste settles.
- DEBT (dated 2026-08-07): tick_friendly twin owed (L-49.1). Latent lineage:
  zone-birth size-delta misses a birth on a full 15-zone array (all v10.x).

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

## VOB Asym COMBO v10.1 — 2026-08-05
- COMBO-ONLY wave (operator order): individual T3/Nagasaki/zone-marker plots and individual alerts REMOVED; combination dp+vp only.
- ADDED: `4K + ANY Bull/Bear (same candle)` (volume == ta.highest(volume, N), N≥4000) and `Nagasaki + ANY Bull/Bear (same candle)` (live-bar all-time-high volume), member-naming alert() payloads; VLB alertcondition split per side.
- Census: 10 plots + 10 alertconditions = 20/64. Files: VOB_ASYM_COMBO_v10.1.pine (TIME), VOB_ASYM_COMBO_TICKFRIENDLY_v10.1.pine (TICK).

## VOB Asym COMBO v10.2 — 2026-08-05
- TIER/LEVEL/DIAGONAL wave (operator dictation; supersedes v10.1 same day). T1 Asymmetric / T2 Pure / T3 Super now LIVE per sensitivity (operator live-study predicates, exclusivity ladder). NEW: Tiers 3+/4+ per candle per side; Level 2/3+/4+ on the EXACT same price (zero buffer); Institutional Diagonal contrarian lanes (diag buy => SELL, diag sell => BUY). ANY now includes tier events. asym_threshold activated (99->50, live-study default).
- Census: 22 plots + 22 alertconditions = 44/64. Files: VOB_ASYM_COMBO_v10.2.pine (TIME), VOB_ASYM_COMBO_TICKFRIENDLY_v10.2.pine (TICK).

## VOB Asym COMBO v10.3 — 2026-08-05
- DEDICATED-ALERT-BOX wave (operator order; supersedes v10.2 same day). Three-lane law on all
  22 lanes incl. VLB + Multi-Zone: sig (detection, owns cooldown) / plot (show box only) /
  alf (dedicated 🔔 box only). A lane alerts IFF its 🔔 box is checked. Machine zone payload
  got its own box. Files: VOB_ASYM_COMBO_v10.3.pine (TIME), VOB_ASYM_COMBO_TICKFRIENDLY_v10.3.pine (TICK).

## VOB Asym COMBO v10.4 — 2026-08-05
- LEVEL-DISTINCTNESS wave (operator catch; supersedes v10.3 same day). A LEVEL counts only DISTINCT
  (tier-class, sensitivity) pairs at the EXACT price — a repeating tier adds nothing; zones never
  counted in levels. Carries the v10.3 dedicated-🔔-box three-lane law in full on all
  22 lanes incl. VLB + Multi-Zone: sig (detection, owns cooldown) / plot (show box only) /
  alf (dedicated 🔔 box only). A lane alerts IFF its 🔔 box is checked. Machine zone payload
  got its own box. Files: VOB_ASYM_COMBO_v10.4.pine (TIME), VOB_ASYM_COMBO_TICKFRIENDLY_v10.4.pine (TICK).
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

## VOB ASYM + HV·DISP·TIER PROXIMITY v1 — 2026-08-19
- **NEW STUDY PAIR (create lane, operator goal 2026-08-19 "another indicator study").** `versions/VOB_ASYM_HDTPROX_v1.pine` (TIME, shorttitle `VOB HDT1`) + `tick_friendly/VOB_ASYM_HDTPROX_TICKFRIENDLY_v1.pine` (TICK, `HDT1 TICK`) — byte-identical below indicator() except the log.info tag. Base = `VOB_ASYM_HVPROX_v1.3.pine` @ d8970ab (T1/T2/T3 engine, cooldown, OB lines, tier markers/alerts, Disp/RVOL readouts UNCHANGED); the v1.3 two-way HV-proximity section is REPLACED by the three-way section (v1.3 stays the two-way study).
- 10 lanes (HV 1K/2K/3K/4K/NAGASAKI · DISP · TIER × Bull/Bear): fires when the latest HV-tier candle, the latest displaced candle (sigma 9 + FVG, same side) and the latest T1/T2/T3 fire (same side) all lie within **W bars** of each other (W input, default 5 — operator answer 2026-08-19), the moment the last of the three becomes known; marker on that bar; print-highest ON; no first-bar gate; lookbacks 1000/2000/3000/4000 editable, Nagasaki = all-time high.
- Alert line (0 units) = the v1.3 operator line: `BULL/BEAR, HV#/NAGA, Disp #.#, RVOL #.#` (HV candle values); tier/bars ride log.info.
- Budget 16 plotshapes × 2 (input.color) + 2 base plot() + 1 fill = 35/64; 0 alertcondition; graphic objects = the base's order-block drawing only.

## VOB ASYM + HV·DISP·TIER PROXIMITY v1.1 — 2026-08-19
- **Operator ruling (conflict row 5, same day):** when the DISPLACED candle is the last of the three events, the VP sits ON the displaced candle. Construction: two constant-offset plotshapes per lane — `…` (offset 0: HV candle / tier fire completed the triple) and `… (disp last)` (offset −1: displacement completed it); same glyph/colour/checkbox. Same-candle dedup: a lane never marks/alerts one candle twice (`sig_<lane>D` suppressed when `sig_<lane>N[1]`). Alert timing/text unchanged. Budget 26×2+3 = 55/64. Supersedes v1 (4118451).
- (same day) v1.1 lane identifiers renamed sig_/fire_/alf_<lane>_N / _D (1:1:1 gate matcher); logic byte-identical.
- (same day, 2nd fix) plot+alert references aligned to the _N/_D ids — commit 2f953e6 referenced undeclared identifiers (would not compile); fbf_111 D_111=0 x2.
