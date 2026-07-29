# BEDROCK — CHANGELOG

Two separate studies, always (operator order 2026-07-27): **BEDROCK BULL** (BDRB) and
**BEDROCK BEAR** (BDRR). Hardcore forks of FABLE_BULL/BEAR_LTF_v1.5. Registries:
`contracts/bedrock_bull_dp_registry.json` · `contracts/bedrock_bear_dp_registry.json`.
VP spec: `contracts/bedrock_vp_spec.json`. Decisions ledger (CLOSED items are law):
`contracts/bedrock_build_decisions.json`.

## v1.4 — 2026-07-29 — SIDE-TYPED SHORTTITLE (BEDROCK BULL v1.4 + BEDROCK BEAR v1.4)

Operator: *"why the fuck is there no fucking bear or bull in the fucking title and short title"*

```
v1.3   indicator("BEDROCK BEAR v1.3", shorttitle="BDRR v1.3")      <- legend was side-blind
v1.4   indicator("BEDROCK BEAR v1.4", shorttitle="BDRR BEAR v1.4")
v1.4   indicator("BEDROCK BULL v1.4", shorttitle="BDRB BULL v1.4")
```

**The defect was the laundering, not the missing word.** `indicator_study_gate` axis A8 had
ALREADY flagged the shorttitle as side-less during the v1.3 wave. Instead of typing it, v1.3
answered by writing `"BDRR v1.3"` into `manifest.side_agnostic_plots` — taking the exemption
branch one message after criticising exactly that move on BDRB-29 Nagasaki (which *was*
typed). **T-INDSTUDY C2 names this case verbatim: "every key side-typed or declared agnostic
(incl. shorttitle)."** A study that is single-sided by construction declaring its own
shorttitle side-agnostic is a **false declaration**, not an exemption — the gate went green
on a lie.

**v1.4 empties `side_agnostic_plots` to `[]` in both manifests.** Nothing in either study is
declared away; every key, including the shorttitle, is typed. One declared edit per study,
anchor asserted pre-match and post-insert (T-INDSTUDY C9).

## v1.3 — 2026-07-29 — VERNACULAR LAW + LANE EXCISION (BEDROCK BULL v1.3 + BEDROCK BEAR v1.3)

Operator, on witnessing one candle carrying `PH +BDR PB`, `1X BDR PB`, `ANY BDR PB` and
`NAKED PB` at once: *"how the fuck is it naked if there is penthouse and rvol 1x... why
are you not suppressing naked pb and any bdr pb when the other conditions are met?????
you are not permitted ever, never never to use vernacular inconsistent on the chart, the
style tab, the visual plot checkbox and the alert checkbox and the source code. all 5
locations must have consistent naming... a long spelled out name and then one and only
one short hand version that strives for clarity not brevity. naked is a fail because it
can mean many things."*

### R1 — EXCISED BDRB/BDRR-09, -10, -11, -12. Proven redundant, not merely noisy.

```
BDR_NAKED_J = PBJ ∧ RC ∧ RS ∧ DIR ∧ FD        (:2445)
BDR_CORE    =       RC ∧ RS ∧ DIR ∧ FD        (:2440)
BDR_HC_J    = PBJ ∧ BDR_CORE                  (:2441)
BDR_ANY_J   = BDR_HC_J                        (:2447, a bare assignment)
⟹ BDR_NAKED_J ≡ BDR_HC_J ≡ BDR_ANY_J — ONE boolean, THREE names.
```

`BDR_HC_*` already contains `DIR = rv_base*`, and the four tiers partition that same axis
on `rv_normPrice`, so **exactly one of lanes 01–04 fires on every bar where 09/11 fired**.
Lanes 09–12 therefore carried **zero information** beyond 01–08. This is *why* the
operator's candle wore four marks — not a suppression bug, a lane shipped alongside its
own partition. Confirmed on his own TradingView export (SHC 5m, 7,473 bars): **09 and 11
fired the IDENTICAL 3 bars, 0 XOR disagreements; 01(1) + 02(2) = 3 = 09(3) = 11(3), both-fire 0,
neither-fire 0.** Suppression logic was unnecessary: excision is lossless by theorem.
`BDR_NAKED_*` deleted; `BDR_ANY_*` renamed `BDR_BASE_*` (it never meant "any of a set" —
"ANY" is now reserved for genuine disjunctions like `+ ANY FABLE`).

### R2 — RESIDUALISED lanes 01/05

`NO-TIER = base ∧ ¬KRATOS/SAAB ∧ ¬RVOL-1X ∧ ¬MOAB/GS` (was `rv_norm < th_saab`), making
the partition exhaustive **by construction** so R1's proof survives any future threshold edit.

### R3 — VERNACULAR: one typed record per lane, both names DERIVED

```
LONG  = "{id} · {side} · {pocket}+KC-RC+KC-RS · {kind} {qualifier}"
SHORT = "{qualifier}\n{pocket}"
```

LONG on the Style-tab title, the visual-plot checkbox and the alert checkbox. SHORT on the
chart and in the alert. **5-surface agreement measured: 0 mismatches, both studies.**

Killed the unmarked-default defect: lanes 01–04 printed `… / BDR` with **no pocket token**
while 05–08 printed `… / BDR PB` — so `KRAT / BDR` was indistinguishable from a PB event by
reading it. **8 lanes across the pair were unreadable.** Clarity over brevity throughout:
`KRATOS` not `KRAT`, `PENTHOUSE` not `PH`, `GRAND-SLAM` not `GS`, `UNIFIED-COMBO` not `UC`.
The one genuinely side-less inherited key (BDRB-29 Nagasaki) was **typed**, not declared away.

### R4 — ALERT GRAMMAR v2 (`OP-ALERTGRAMMAR-V2-DP-FIRST`)

`KRATOS PBJ | BDRR-02 | FIRST | DISP 4.2 | RVOL 412 BEAR | HV 250`

The DP leads, leftmost. Then the lane id, the session marker, and the qualifiers in the
operator's stated order: DISP → RVOL-with-direction → HV. No ticker, no interval, no
exchange — TradingView already carries them.

### Budget + gates

Plot budget **55→51/64 (BULL)**, **54→50/64 (BEAR)**. Graphic objects added: **zero**.
`indicator_study_gate` PROVED ×2 (`D_bytes=0`, declared-edits-only rebuild) · `pane_label_gate`
`D_cs1=0` ×2 · `bedrock_firstbar_alert_gate` `D_bdrfb=0` ×2. Manifests
`validation/indstudy/manifest_bedrock-{bull,bear}_v1.3.json`. Spec:
`docs/2026-07-29_TV-TickBar-RE_BEDROCK-VernacularLaw-LaneRedundancy-StructuredFieldSpec_v1.0.md`.

## v1.2 — 2026-07-29 — FIRST BAR MASTER BECOMES AN ALERT GATE (BEDROCK BULL v1.2 + BEDROCK BEAR v1.2)

Operator law: *"we need to see the visual plots but if we check the first bar checkbox,
then and only then we ONLY want the alert if the definition of first bar criteria is met
and there will be no other alert fired beyond that first bar definition. its important bc
low time intervals would fire crazily if we dont have this ability."*

**The defect v1.2 closes.** BEDROCK v1.1 *did* carry `★ FIRST BAR MASTER ★` (inherited
from FIRST BAR FABLE), but it gated the **detection** layer — `sig_L = D_L and c(L)` — and
`sig_L` feeds both `fire_L` (the plot) and `alf_L` (the alert). ON therefore erased the
visual plots off the first bar as well as the alerts. There was no way to keep the chart
fully drawn while quieting the alerts, which is exactly what low intervals need.

**The transform** (per lane L, `c(L)` = its reference-bar class ∈ {fb0, fb1, fb01, fbs,
fbm, fb12}; 55 BULL lanes, 54 BEAR lanes):

| | v1.1 | v1.2 |
|---|---|---|
| detection | `sig_L = D_L and c(L)` | `sig_L = D_L` |
| **plot** | `fire_L = en_L and sig_L` | `fire_L = en_L and sig_L` — **ungated** |
| gate | — | `aok_L = sig_L and c(L)` |
| **alert** | `alf_L = al_L and sig_L` | `alf_L = al_L and aok_L` — **gated** |
| alert count | `qn` term `fire_L` | `((en_L and aok_L) ? 1 : 0)` ≡ old `fire_L` |

- **T-A alert invariance** — `alf_new = al ∧ (D ∧ hc) ∧ c = al ∧ (D ∧ c ∧ hc) = alf_old`.
  Alert firing and alert text are bit-identical to v1.1 with the master ON.
- **T-B qn invariance** — `en ∧ aok = en ∧ sig_old = fire_old`, so the `SIDE n` count in
  every alert string is unchanged.
- **T-C plot unconditionality** — `fire_L` carries no `c(L)` term ⇒ ∂fire/∂master = 0.
- **T-D master-OFF identity** — OFF ⇒ `c ≡ true` ⇒ the study is identical to v1.1.
- **T-E alert totality** — every `alf_L` carries a `c(L)` factor. **Closures:** v1.1 left
  four lanes alert-ungated — `qS20`/`qS21` (b2bFC, a two-bar back-to-back → assigned
  `fb01`, the FBF law "the pair touches the first bar") and `qS32`/`qS33` (OPEN1 →
  assigned `fb0`, a provable no-op since `det_open1*` already requires `is_new_sess`).
  With the master ON, no alert of any kind now fires outside the first-bar definition.

**First-bar definition — unchanged, and NOT redefined here.** BEDROCK keeps the
estate-canonical `bool is_new_day = ta.change(time("D")) != 0` / `is_new_sess =
is_new_day`, byte-identical to FIRST BAR FABLE v3 / EXT v6 and SECONDS v1 (B2B PUP's
`session.isfirstbar` is the same boundary).

**Master input** retitled `★ FIRST BAR MASTER — ALERTS ONLY ★`, default **ON** (unchanged
default: alert behaviour matches today; the plots are what newly appear on every bar).

**Plot budget unchanged** — not one `plotshape` line was touched; each already read
`fire_L`, which is now first-bar-independent. Graphic-object disclosure (L-61): **zero**
`label.new`/`line.new`/`box.new`/`table.*`/`polyline.new` sites added; every VP remains a
real plot.

Gates: `validation/wrappers/bedrock_firstbar_alert_gate.py` → **D_bdrfb = 0 PROVED**,
anti-fixture battery **5/5 CAUGHT**; W-INDSTUDY manifests
`validation/indstudy/manifest_bedrock-{bull,bear}_v1.2.json` (declared-edits-only,
rebuild byte-compare D=0).

## v1.1 — 2026-07-28 — THE ERROR-WAVE FIX (BEDROCK BEAR v1.1 + BEDROCK BULL v1.1)

Operator witnessed ~20 TradingView errors per study on v1.0 ("I cannot take all the
pictures"). Root causes, fixed in both files via W-INDSTUDY manifests
(`validation/indstudy/manifest_bedrock-{bear,bull}_v1.1.json`, gate PROVED):

- **R1 (the error wall):** the HARDCORE-GATE engine block moved from :159 to after
  `det_PBJRSRC` — v1.0 inserted it before its dependencies (`d9_*` :292, `sigPBJ/PB`
  :452, `sigFAUNA*` :561, `det_kcRS/RC` :2306), so TradingView reported an
  undeclared-identifier per reference (gate measured 15-17 order violations per file).
- **R2:** killed lanes per operator decisions D-04/D-13/D-14 (CO: HV+D+PB+USE,
  CO: HV+D+PBJ+USE, ENR Same-Bar/TNT-1st) fully excised — v1.0 removed only the sig_
  definitions and left dangling `fire_/alf_` defs, `qn` terms, inputs and alert rows
  (25 residue sites per file). Every removal is a visible `CUT##` comment.
- **R3:** back-pocket lanes (D-05 `qB2BP`, D-06 `qPBR`) + `qPJR` keep their sig_
  definitions but lose every input/alert surface (slim-alert law: nothing alert-only).
- **R4 (BEAR):** BDRR-21 plot text wore the BULL literal `1X/GS` — the L-63
  founding-exhibit defect re-imported — now `1X/MOAB`.
- **R5 (BULL):** BDRB-24 Whale+PUP Bull wore Musashi's gold `c_mu_bull` — new
  `c_wh_bull` (#1E88E5).
- **R6:** `en_aggAlerts` tooltip made honest (per-lane OFF mode for inherited lanes no
  longer exists; BEDROCK lanes 01-18 always alert per-lane).
- Registry hygiene: BEAR registry lane ids carried the BULL prefix (BDRB-*) — corrected
  to BDRR-*; BDRR-21 text + BDRB-24 color corrected in `bedrock_vp_spec.json`.

Acceptance: `validation/wrappers/bedrock_v11_gate.py` D_bdr=0 both sides (9 axes:
declaration-order, kill-residue, back-pocket, alert↔plot cross-ref, spec parity,
budget, block integrity, L-63 string ban, stamping) · anti-fixture battery 6/6
(`validation/anti_fixtures/af_bedrock_v11_gate.py`) · `pane_label_gate` D_cs1=0 both ·
`indicator_study_gate` PROVED both. Budget: BEAR 54/64 · BULL 55/64 · alertcondition 0.
Graphic-object disclosure: 2 inherited GZ-FVG `line.new` decoration sites per study,
zero `label.new`, zero pane labels.

Adversarial verification wave (6 independent skeptics, 2 files × 3 lenses — compile /
decisions / render-truth; compile lens CLEAN both files) surfaced and the same wave fixed:

- **R8 (D-16, behavioral):** the NAKED lanes (BDRR/BDRB-09/10) omitted the mandatory
  directional conjunct — `BDR_DIR` added; no lane anywhere in either study can fire on a
  non-directional bar.
- **R9 (D-11):** the banned word appeared in the header comment and an operator-visible
  tooltip ("Bearish mirror.") — both reworded, zero occurrences remain.
- **R10 (D-04/D-13/D-14 doctrine):** zero-dependent dead layers excised — `co_*_v7` ×4,
  `coQ_bull/bear`, `det_S26/det_S27` ("otherwise the engine goes too").
- **R11 (D-09):** `kc_*ThrEff` ternaries collapsed — the ATR-x path is the only path.
- **R12 (D-15/side-truth):** BULL `en_/al_qS15` rows retitled "Nagasaki (any bar)" (the
  settings pane still claimed FIRST BAR after the constraint was removed); the
  "Grand Slam (MOAB)" tooltip gloss made side-correct in both files; stale S26/S27
  tooltip reference replaced.
- **Adjudicated, retained, disclosed:** `co_*`/`enrB2B_*` base engines stay inside the
  `any_BULL/any_BEAR` baskets — those baskets are definitionally "ANY FABLE" and the
  nine "+ANY FABLE" composite lanes would lie about their own names if FABLE detections
  were removed from them. The FIRST BAR master toggle (default ON, inherited) still
  gates all lanes including Nagasaki; D-15's baked per-lane constraint is gone — the
  master is a user switch, not a baked conjunct.

Tick-friendly twins: dated pair debt (due 2026-07-30) in `INDSTUDY_DEBTS.json` (L-49.1).

## v1.0 — 2026-07-28 — first build (SUPERSEDED by v1.1)

Generated by `scripts/ind/build_bedrock_v1_1.py`'s predecessor (`build_bedrock_v1.py`)
from FABLE_BULL/BEAR_LTF_v1.5: hardcore gate (ANCHOR · R-C · R-S · DIRECTIONAL ·
FAUNA|DISPLACEMENT), 18 BEDROCK lanes + gated inherited lanes, BAND LAW v2 plots,
per-lane dynamic alerts. Shipped with the error wave fixed by v1.1 — do not paste v1.0.
