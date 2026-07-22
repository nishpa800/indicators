# VOB Indicator Suite — Changelog

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
