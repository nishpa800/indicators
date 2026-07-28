# FABLE QUAD — CHANGELOG

## v1.5 (2026-07-27) — Fable Bull LTF v1.5 · Fable Bull HTF v1.5 · Fable Bear LTF v1.5 · Fable Bear HTF v1.5
ROOF / PENTHOUSE / FLOOR / 2nd FLOOR TAKEN FROM HVD PBJ PPD. Operator goal: *"take roof and floor
from hvd pbj ppd bear and bull, then add them to fbear/bull ltf/htf v1.4. create 2 new dp/vp for
each bull/bear indicator study. ROOF + any fable (bear), PH + any fable (bear); Floor + any fable
(bull), 2F + any fable (bull)."* Two new dp/vp/alert rows per study, 8 rows across the QUAD.

**New rows (1:1:1 — real-plot VP + 🔔 checkbox + alert emission, CS-1 clean):**

- `ROOF + ANY FABLE Bear` — circle / abovebar / `#FF1744` / "ROOF\n+ANY" — the HVD *Rooftop* identity
- `PH + ANY FABLE Bear` — cross / belowbar / `#D50000` / "PH\n+ANY" — the HVD *Penthouse* identity
- `FLOOR + ANY FABLE Bull` — circle / top / `#00E5FF` / "FLOOR\n+ANY" — the HVD *Floor* identity
- `2F + ANY FABLE Bull` — cross / abovebar / `#80DEEA` / "2F\n+ANY" — the HVD *2nd Floor* identity

**Engine ported: "ENGINE 7: PING PONG SR"** (HVD_PBJ_PPD_{BEARISH,BULLISH}_v1.pine L558-693) under the
`rf_` prefix — flat-body + swing-pivot S/R level array, break / reject / bounce / pivot-bounce state
machine, regime latch, and the 6-member structural gravity count (`rf_bull_pp` / `rf_bear_pp`,
min count 3). Every constant is the source's own default, exposed as an input, rolling-window only.

**ONE DECLARED DEVIATION (T-INERT).** The source's `srLevel` carries a `line` field and 7 `line.*`
call sites that draw 100%-transparent bookkeeping lines. Those are REMOVED. No detection boolean
reads `lnID` — it is only ever the receiver of `line.set_*` / `line.delete` — so every ported
boolean is bit-identical to the source, while the study adds **ZERO graphic objects** (CARDINAL
SIN #1 / L-61) and cannot exhaust TradingView's line-object cap.

**Root atoms are the source's own side-symmetric 4-term definitions** (HVD L742-745):
`conf ∧ <side>_pp ∧ <side>PBJ ∧ <side>_hw_slot` for ROOF/FLOOR, with `PB` in place of `PBJ` for
PH/2F. The HVD bull side additionally ran `floor_gated = anyBullFloor ∧ oneOfThese ∧ cb1_pass_floor`;
those two extra gates are **deliberately not ported**. Their job was to demand a co-occurring
qualifier — which the `+ ANY FABLE` conjunct does natively here — and porting them would have broken
bull/bear symmetry (the HVD bear plots use the raw atom, the bull plots use the gated one) and pulled
in ~15 bull-only engines with no bear mirror. Deviation is declared, not silent.

**Plot budget:** 41 → 43 / 64 (bear), 42 → 44 / 64 (bull). No `display.data_window` plots,
no alertconditions, no dynamic-color args. Detection counter `qn` extended by both new lanes.

**Shape+location collision disclosure (honest, not clean):** the QUAD's 9 bear shapes × 4 locations
= 36 slots were already fully consumed at 41 plots in v1.4, so no free pair exists. The operator's
own HVD identity was preserved instead of inventing a new one: ROOF collides with S8 Whale+PPD
(circle/abovebar), PH with S31 NAG+ANY (cross/belowbar), FLOOR with S7 (circle/top), 2F with S32
(cross/abovebar). Colour, text and size differ in every case. The 5 (bear) / 6 (bull) PRE-EXISTING
v1.4 collisions are recorded as a dated debt row, not silently inherited.

Build + declared edits: `lake/scripts/ind/build_fable_quad_v15.py` (9 edits per study, E7 double-run
byte-identical). Manifests: `validation/indstudy/manifest_fable-quad-fable_*_v1.5_v1.json`.

## v1.4 (2026-07-26) — Fable Bull LTF v1.4 · Fable Bull HTF v1.4 · Fable Bear LTF v1.4 · Fable Bear HTF v1.4
COMPILE-RISK REMOVAL. The v1.2 KC scale fix introduced a dropdown whose option value contained a
non-ASCII character ("ATR ×"). A repo-wide scan of every pre-existing .pine found **ZERO** studies
using non-ASCII inside an `options=[]` list — no precedent anywhere in this estate. Non-ASCII string
LITERALS are proven safe (70 of them sit in v1.1 input labels and compile today), but `options=[]`
specifically was unwitnessed, and the lake's gates are static text checks that cannot type-check
Pine — only a TV paste settles it. Rather than let an unproven construct be the thing that breaks
the operator's chart, it is now ASCII **"ATR x"** at every site including the tooltip prose.

Builder asserts, per file: the `options=[]` list contains no non-ASCII; the input DEFAULT, the
options VALUE and BOTH ternary comparison literals are byte-equal. That last one matters — if the
comparison literal ever drifts from the option value, `kc_slopeUnit == "..."` is simply always false
and ATR mode silently does nothing while appearing selected. Asserted, not assumed.

No behaviour change from v1.3. Displacement σ=5.0 and the bear 1X/MOAB label fix carry through.


## v1.3 (2026-07-26) — Fable Bull LTF v1.3 · Fable Bull HTF v1.3 · Fable Bear LTF v1.3 · Fable Bear HTF v1.3
BEAR LABEL FIX — pays the dated quarantine debt due 2026-07-27 (DOORMAN founding exhibit of
LAW-ZERO-DEFECT L-63, operator-witnessed on his own chart). The Bear S2 lane fires the BEAR
boolean `(det_RVOL1xR or det_MOAB) and d9_bear and sigBearPBJ` but rendered the BULL text
literal **"1X/GS"** — GS = Grand Slam, a bull RVOL tier; the bear-side tier is MOAB. The plot
TITLE was always correct ("S2: Bear RVOL 1X/MOAB + Disp9 + PBJ"); only the on-chart glyph lied,
which is exactly why it survived every static check and had to be caught by the operator's eye.
Now renders **"1X/MOAB"**. Blast radius exactly 2 sites (BEAR LTF + BEAR HTF); the BULL files
legitimately use 1X/GS on their S1 lane and are asserted UNTOUCHED by the builder.

**Why v1.3 and not a v1.2 amendment:** this defect was carried FORWARD into v1.2 earlier the same
session, because v1.2 was built from the v1.1 base without re-checking the open debt list. A
shipped version is immutable (L-60 ES-0), so the fix takes its own number. BULL members are
version-stamp-only — byte-identical to v1.2 otherwise — purely to keep the QUAD in lockstep, since
P-021 proved that mixed version numbers inside one family are themselves an operator-facing defect.

Diff vs v1.2: 3 lines per bear file (2 stamp + 1 literal), 2 lines per bull file (stamp only).
IPSF values inherited unchanged from v1.2; its calibration cert remains valid.


## v1.2 (2026-07-26) — Fable Bull LTF v1.2 · Fable Bull HTF v1.2 · Fable Bear LTF v1.2 · Fable Bear HTF v1.2
IPSF RECALIBRATION — two declared edits on a sha256-pinned v1.1 base, 23 diff lines per file,
nothing else touched. Both values are MEASURED, not chosen: 162-cell census over 210,686 bars /
9,957 sessions / 11 symbols × 6 intervals (docs/2026-07-26_TV-TickBar-RE_FableQuadBearRSRC-
DisplacementIPSFAudit_v1.0.md). Instrument = scripts/ind/ports/fable_quad_audit_engine.py,
accepted only at D_parity=0 byte-identity vs the proven port with 2 anti-fixtures CAUGHT.

**E1 — displacement σ 9.0 → 5.0 on ALL THREE dedicated engines** (i_d9_mult, hq_dmult, and
ltf_dmult on the LTF builds). At σ=9 a displacement event fired **2.13 times per 10,000 bars**,
which structurally disabled ten Disp9-gated lanes (S1/S2, S9/S10, S18/S19, S22/S23, S24/S25);
the dedicated LTF engine fired **0 times on 1h and 15m in 10 of 12 measured cells**, meaning
Typhoon / Musashi / Whale **could not fire at all in any LTF build** — that was the entire
LTF-vs-HTF gap the operator reported. Measured ladder, events per 10k bars:
σ9=2.13 · σ8=7.20 · σ7=20.54 · σ6=43.92 · σ5=88.20 (41.5× across the range). The ladder now
ships inside each tooltip so every intermediate σ is reachable with its known rate.

**E2 — KC slope threshold made SCALE-FREE** (new `KC Slope Threshold Unit` dropdown; default
"ATR ×" with thresholds 0.05 → 0.02; "Absolute $" retained so v1.1 behaviour is never removed).
The v1.1 threshold was denominated in absolute dollars per bar, so the R-S lane was dead on
every low-priced symbol while looking healthy on megacaps: Ford R-S 2/1 and PBJ+RS+RC **0/0**.
Calibrated by a 5-symbol × 6-multiplier sweep at 1h — 0.02 × ATR holds megacap counts within one
event (AAPL 7/4→7/4, TSLA 5/5→5/5, NVDA 3/3→4/3) and revives the low-priced names
(F 0/0→**5/3**, SOFI 0/0→**3/1**). Inputs cost zero plot units (P-019), so budgets are unchanged.

**NOT changed, deliberately:** FIRST BAR MASTER stays ON — it discards 52% of PBJ+RS+RC events
and asymmetrically (bull −44% / bear −60%), but it is a declared operator semantic, not a defect,
and it is one checkbox. **Bear RS/RC was investigated and is NOT broken**: plotted PBJ+RS+RC
measured bear 198 vs bull 195 (1.02×) — the apparent silence is a base rate of ~1 print per
50–100 sessions, not a logic fault.

**DEFECTS CARRIED FORWARD, recorded not hidden (L-63):** (a) `fbf_111_gate` D_111=**8** on all
four — IDENTICAL to v1.1, inherited, on lanes rcNTBull/rcNTBear (the RC NPM+TNT suppressor
toggles, which have no plot of their own); v1.2 introduces zero new 1:1:1 defects but does not
close these. (b) residual 10 (shape, location) plot collisions from v1.1 are untouched.
(c) dedicated tick_friendly siblings for the QUAD family are still owed (L-49.1), debt due
2026-07-29. Gates green this wave: pane_label_gate D_cs1=0 ×4.


## v1 (2026-07-24) — Fable Bull LTF v1 · Fable Bull HTF v1 · Fable Bear LTF v1 · Fable Bear HTF v1
Operator GO ("build all 4"). Single-side studies from the FIRST_BAR_FABLE_v5 engine base
(sha 5635be9b, commit 19cbab4): bull 42 rows / bear 41 rows, ALL real plotshapes (CS-1/L-61),
per-row 🔔 lanes (1:1:1, D_111=0 ×4). UC_core MAJOR REDEF ([(FVG-1∨FVG-2)∧MAT prior] ∨
[FVG-1∧FVG-2 same candle]) inherited by S24/S25, CO v7 (13-term qualifier menu), HVD CMB
member (q_ family), chain constituent. Combo Chain back-to-back binary law (det_CC =
conf ∧ hit ∧ hit[1]; 8-case battery PROVED). HVD 2of3/3of3 (no PBJ); HV+PBJ+DISP (dedicated
engine + HV-ladder rung dropdown 50…4000/HEV); PBJ+RS+RC; PB+RS+RC; GS+ANY / MOAB+ANY; raw
R-S/R-C rows removed (KC engine internal). LTF fork: dedicated LTF displacement REQUIRED on
Typhoon/Musashi/Whale reference bars (HTF builds exclude the engine — no dead knobs).
Alert grammar T-ALERTMSG v1.2 (SIDE n | FIRST/G>R gap%/ratio | tokens+achieved numbers | RVr;
per-dp messages; achieved-depth reporter capped 2400 by Pine history physics — disclosed).
Renames carried: Ignite TNT / Ignite Napalm · ENR Same-Bar / ENR TNT-1st. ⓘ info law: every
tooltip enumerates gates + displacement tether (D-REQ column). 135 dead legacy inputs stripped
per study. Heritage shape×location collisions disclosed (inherited v2 visual language; all NEW
rows collision-free). Specs: docs/2026-07-24_*FableBullBear*_v1.0–v1.3 + BudgetSpec v1.1/v1.2.
1FABLE v6 pair remains untouched.

## CCC v1 (2026-07-24) — Combo Chain Constituents v1
Diagnostic/parity harness (operator chain-flaw suspicion): 10 rows only — FVG CS1, FVG CS2,
MAT (set3∨set4), UC (UC_core NEW def), Combo Chain — bull + bear. EVERY row marks its
DETECTION candle (offset 0): chart == chain census 1:1. No First Bar Master. Engines = v5
base verbatim (RVOL/FVG/matrix settings feed CS1–CS4 — load-bearing). Built for the
operator's CSV parity check of the back-to-back chain law.

## v1.1 (2026-07-24) — Fable Bull LTF v1.1 · Fable Bull HTF v1.1 · Fable Bear LTF v1.1 · Fable Bear HTF v1.1
Operator visual-law + chain-v2 wave (v1 SUPERSEDED — stacked locations + chain flaw charge).
VISUAL LAW: all four locations used (below bar / bottom / top / above bar) in family blocks;
distinct shapes per location; same-location overlaps differentiated by translucency (8-digit
hex const literals — P-017-legal, Style picker intact); bull palette greens/cyans/blues/
yellows/white ONLY, bear palette reds/oranges/pinks/purples ONLY. CHAIN v2: UC same-candle =
(CS1∧CS2) ∨ ((CS1∨CS2)∧MAT); fire iff [two consecutive constituent candles with ≥1 UC candle]
OR [≥2 UC candles within any 3 consecutive] — battery 10/10 PROVED (MAT→FVG no longer fires
without a UC). Frozen defaults: chain uses same-candle UC; S24/CO keep UC_core pending
operator ruling; 2-of-3 middle candle may be empty.
