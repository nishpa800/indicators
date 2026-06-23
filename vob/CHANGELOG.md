# VOB Indicator Suite — Changelog

## VOB v10 — +T3 Cluster, −zone markers/labels — 2026-06-23

New file (does NOT replace any existing v10): `versions/VOB_v10_T3cluster_noZoneMarkers_2026-06-23.pine`.
Built from Anish's working `//@version=6` "VOB v10" body by explicit request.

### Added
- **T3 Cluster** detection (`T3x`, yellow flag, top) — ported verbatim from VOB
  v11. Fires when **2+ of the six T3 tiers** (T3a..T3f, buy OR sell) paint on the
  SAME candle. Direction-agnostic. One plotshape + alertcondition + Bloomberg
  `alert()`. Non-repainting (`barstate.isconfirmed`), cooldown-gated. Counts off
  the gated `plot_t3_*` booleans.

### Removed
- The **12 zone-formation marker plotshapes** (zA..zF Bull + Bear cross markers).
- Their alerts: the `Any Zone Formation` alertcondition **and** the
  `ZONE_FORMATION` `alert()` payload (`any_zone` is now unreferenced and gone).
- The **zone-formation labels** (`f_emit_label` + the `en_emission_labels` input).

### Kept (unchanged)
- Individual T3a..f Buy/Sell circles + their per-tier Bloomberg alerts.
- Nagasaki (`offset = -1`), VLB Bull/Bear, Multi-Zone Bull/Bear 2 & 3+.
- The shaded **order-block zone boxes/midlines** (MutEx line engine) and per-bar
  `log.info` console stream. `en_zone_*` toggles retained (default true) — they
  still gate the boxes AND the `fire_zb_*/fire_zs_*` booleans the Multi-Zone
  detection counts.

### Tally
- Plotshapes 31 → **20** (−12 zone markers, +1 T3 Cluster).
- Alertconditions 7 → **7** (−`Any Zone Formation`, +`T3 Cluster`).
- `alert()` payloads 20 → **20** (−`ZONE_FORMATION`, +`T3_CLUSTER`).

### Note
- `f_vob`'s neighbor-dedup reads `get(i - 1)` unconditionally (no `if i > 0`
  guard) — **preserved verbatim** from Anish's pasted v10; only the five
  requested changes were made.

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
