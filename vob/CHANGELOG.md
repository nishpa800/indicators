# VOB Indicator Suite — Changelog

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
